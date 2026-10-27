"""Reconstruct knowledge/raw/manifest.jsonl as a DERIVED index of the corpus.

The manifest is not an append-only ingestion log. Its source of truth is the
`source:` frontmatter field of every `knowledge/corpus/*.md` chunk: the corpus
declares where it came from, the manifest is the reverse index (source -> ids)
plus the sha256 of the originating raw file. Re-running is idempotent.

Read-only verification by default; pass --write to regenerate.

Exit code: 0 = consistent, 2 = provenance break (raw file maps to no chunks).
"""
import argparse
import collections
import glob
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "knowledge", "raw")
CORPUS = os.path.join(ROOT, "knowledge", "corpus")
MANIFEST = os.path.join(RAW, "manifest.jsonl")

FM_RE = re.compile(r"(?s)^---(.*?)---")
SOURCE_RE = re.compile(r"^source:\s*(.+?)\s*$", re.M)


def unquote(value):
    """Strip one layer of YAML double/single quoting."""
    value = value.strip()
    for wrapper in ('"', "'"):
        if len(value) >= 2 and value.startswith(wrapper) and value.endswith(wrapper):
            return value[1:-1].replace("\\" + wrapper, wrapper)
    return value


def sha256_of_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def corpus_index():
    """Map corpus chunk id -> declared source (from frontmatter)."""
    index = {}
    no_source = []
    for path in sorted(glob.glob(os.path.join(CORPUS, "*.md"))):
        cid = os.path.basename(path)[:-3]
        text = open(path, encoding="utf-8", errors="replace").read(4000)
        source = None
        fm = FM_RE.search(text)
        if fm:
            m = SOURCE_RE.search(fm.group(1))
            if m:
                source = unquote(m.group(1))
        index[cid] = source
        if not source:
            no_source.append(cid)
    return index, no_source


def raw_basenames():
    return {
        os.path.basename(p)
        for p in glob.glob(os.path.join(RAW, "*"))
        if os.path.isfile(p) and os.path.basename(p) != "manifest.jsonl"
    }

def load_manifest():
    """Read the on-disk manifest. Returns (rows, problem) — problem is set when
    the file is absent or unparseable, so verify mode never silently passes
    on a corrupt handoff artifact."""
    if not os.path.exists(MANIFEST):
        return None, "manifest.jsonl does not exist"
    rows, bad = [], []
    for lineno, line in enumerate(open(MANIFEST, encoding="utf-8"), 1):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if set(r) < {"raw", "sha256", "corpus_ids"}:
            bad.append(f"line {lineno}: missing raw/sha256/corpus_ids keys")
            continue
        rows.append(r)
    if bad:
        return None, "; ".join(bad)
    return rows, None


def manifest_problems(disk_rows, built_rows):
    """P6: judge the on-disk manifest against a freshly derived one.

    The corpus is the source of truth, so the correct row-key set is exactly
    what build_rows() produces: real raw filenames plus intentional
    composite/web-source keys. Any disk key absent from the built set is
    phantom provenance (a raw file that never existed, or one since deleted);
    any built key absent from disk is a chunk set the manifest fails to trace.
    Content hashes must also agree, else a raw file changed after chunking.
    """
    problems = []
    disk = {r["raw"]: r for r in disk_rows}
    built = {r["raw"]: r for r in built_rows}
    for key in sorted(set(disk) - set(built)):
        problems.append(f"phantom raw (not derivable from corpus): "
                        f"{key[:70]} -> {len(disk[key]['corpus_ids'])} chunks")
    for key in sorted(set(built) - set(disk)):
        problems.append(f"untraced corpus (manifest has no row): "
                        f"{key[:70]} -> {len(built[key]['corpus_ids'])} chunks")
    for key in sorted(set(disk) & set(built)):
        if disk[key]["sha256"] != built[key]["sha256"]:
            problems.append(f"content drift: {key[:70]} sha changed since chunking")
    claimed = collections.Counter()
    for r in disk_rows:
        claimed.update(r["corpus_ids"])
    dupes = sorted(c for c, n in claimed.items() if n > 1)
    if dupes:
        problems.append(f"{len(dupes)} chunks claimed by multiple rows: {dupes[:8]}")
    return problems
def resolve_source(source, raws):
    """Resolve a declared source to the raw file(s) it names.

    A chunk is either ingested from one raw file (source == raw basename) or
    synthesized from several (source is a composite string naming them).
    Returns (direct, contributors): the exact raw if ingested, plus any raws
    named inside a composite declaration.
    """
    direct = source if source in raws else None
    contributors = set()
    if not direct:
        for token in re.split(r"[+,()|/]", source):
            token = token.strip().strip('"\'').strip()
            if token in raws:
                contributors.add(token)
    return direct, contributors


def build_rows():
    """Deterministically derive manifest rows from the corpus."""
    index, no_source = corpus_index()
    raws = raw_basenames()

    by_source = collections.defaultdict(list)
    for cid, source in index.items():
        if source:
            by_source[source].append(cid)

    rows = []
    contrib = collections.defaultdict(set)
    for source in sorted(by_source):
        ids = sorted(by_source[source])
        direct, contributors = resolve_source(source, raws)
        if direct:
            sha = sha256_of(os.path.join(RAW, direct))
            rows.append({"raw": direct, "sha256": sha, "corpus_ids": ids})
        else:
            # Web/synthesis source: no raw file of its own, but it may name
            # raw files as contributors. Record both.
            if contributors:
                for c in sorted(contributors):
                    contrib[c].update(ids)
            sha = sha256_of_bytes(source.encode("utf-8"))
            rows.append({"raw": source, "sha256": sha, "corpus_ids": ids})

    unmapped = sorted(raws - set(r["raw"] for r in rows) - set(contrib))
    return rows, {"no_source": no_source, "unmapped_raw": unmapped,
                  "corpus_chunks": len(index)}

def rebuild_after_ingest():
    """Rebuild the manifest after ingest; warn loudly on a provenance break.

    Called from ingest.py so the manifest can never drift from the corpus it
    indexes. The manifest is derived from corpus frontmatter, so this is a
    full rebuild, not an append.

    Must pass --write: without it main() is read-only verification, which can
    report a drift it cannot repair, leaving the manifest stale and ingest's
    exit code meaningless (W5).
    """
    rc = main(["--write"])
    if rc != 0:
        print("[ingest] WARNING: manifest rebuild reported a provenance break",
              file=sys.stderr)
    return rc


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="regenerate the manifest")
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    args = ap.parse_args(argv)

    rows, meta = build_rows()
    covered = set()
    for r in rows:
        covered.update(r["corpus_ids"])
    report = {
        "manifest_rows": len(rows),
        "corpus_chunks": meta["corpus_chunks"],
        "covered_chunks": len(covered),
        "chunks_without_source_field": len(meta["no_source"]),
        "raw_files": len(raw_basenames()),
        "raw_files_mapped": len(raw_basenames()) - len(meta["unmapped_raw"]),
        "raw_files_with_no_chunks": len(meta["unmapped_raw"]),
        "unmapped_raw": meta["unmapped_raw"],
    }

    broken = bool(meta["unmapped_raw"] or meta["no_source"])
    # P6: the on-disk manifest is the phase-1 handoff artifact — verify it
    # against the corpus instead of trusting a reconstruction of itself.
    disk, problem = load_manifest()
    if problem:
        report["manifest_on_disk"] = f"UNREADABLE: {problem}"
        broken = True
    else:
        report["manifest_on_disk"] = f"{len(disk)} rows"
        staleness = manifest_problems(disk, rows)
        report["staleness"] = staleness
        if staleness:
            broken = True
    report["verdict"] = "FAIL" if broken else "PASS"

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for k, v in report.items():
            shown = v if not isinstance(v, list) or len(v) <= 10 else str(v[:10]) + " ..."
            print(f"{k}: {shown}")
        if meta["unmapped_raw"]:
            print(f"\nPROVENANCE BREAK: raw files present in knowledge/raw/ that map to "
                  f"zero corpus chunks (ingested but never chunked, or chunks lost):")
            for name in meta["unmapped_raw"]:
                print(f"  - {name}")
        if meta["no_source"]:
            print(f"\nPROVENANCE BREAK: corpus chunks with no `source` frontmatter "
                  f"(cannot be traced to any raw file): {meta['no_source'][:10]}")
    if report.get("staleness"):
        print("\nMANIFEST STALE — on-disk manifest does not trace the corpus:")
        for p in report["staleness"]:
            print(f"  - {p}")
    if args.write:
        tmp = MANIFEST + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        os.replace(tmp, MANIFEST)
        action = "REGENERATED" if not broken else "REGENERATED (with warnings)"
        print(f"\n{action}: {MANIFEST} — {len(rows)} rows, {len(covered)} corpus ids")

    return 2 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main())
