#!/usr/bin/env python3
"""Re-stamp reflection provenance after a corpus repair, but only if it is safe.

## Why this exists

Repairing the corpus (C-6: re-ingesting two books with whitespace-preserving PDF
extraction) changes the corpus fingerprint. Every reflection digest and candidate
that was derived from the previous fingerprint is then flagged stale by
`check_reflection.py`, and the quality gates fail on ten files.

That gate is correct. Its purpose is to stop the workspace from citing a graph
that no longer exists.

## Why a blind re-stamp would defeat it

Rewriting the hash without checking anything turns the gate into a rubber stamp:
the next person to corrupt the corpus re-stamps over it and the provenance trail
goes quiet. So this script re-stamps only when the claim is *still true of the new
corpus*:

* every chunk id cited in `Evidence` still exists in `graph.db`, and
* the file's own digest is unchanged apart from the provenance block.

If a cited chunk was evicted or replaced by different text, the script refuses and
names the file. The correct response then is to re-run reflection for that topic,
which is a research decision, not a bookkeeping one.

## Contract

A file that is *not* re-stamped is left byte-identical. `--check` reports without
writing. Re-stamping records the previous fingerprint in a `superseded_fingerprint`
key so the change is auditable rather than silent.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path
# Chunk ids are `NN_snake_case` and appear inside backticks in the Evidence field.
EVIDENCE_ID_RE = re.compile(r"`([0-9]{2}_[a-z0-9_]+)`")
FP_RE = re.compile(r'"fingerprint"\s*:\s*"([0-9a-f]{8,12})"')
PROV_FP_RE = re.compile(
    r'(?P<indent>[ \t]*)"fingerprint"\s*:\s*"(?P<old>[0-9a-f]{8,12})"')

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "knowledge" / "graph" / "graph.db"
TARGETS = [
    ROOT / "reflection" / "candidates",
    ROOT / "reflection" / "digests",
    ROOT / "subprojects" / "vera" / "experiments" / "runs",
]



def live_fingerprint() -> str:
    """Corpus fingerprint, computed exactly as check_reflection does."""
    import hashlib
    h = hashlib.sha256()
    for p in sorted((ROOT / "knowledge" / "corpus").glob("*.md")):
        h.update(p.read_bytes())
    return h.hexdigest()[:12]


def known_chunk_ids() -> set[str]:
    if not DB.exists():
        sys.exit("restamp_provenance: graph.db missing — run build_graph.py first")
    conn = sqlite3.connect(DB)
    try:
        return {r[0] for r in conn.execute("SELECT id FROM nodes")}
    finally:
        conn.close()


def cited_ids(record: dict) -> list[str]:
    evidence = record.get("Evidence") or record.get("evidence") or ""
    if isinstance(evidence, list):
        evidence = " ".join(str(e) for e in evidence)
    return EVIDENCE_ID_RE.findall(str(evidence))


def split_records(text: str) -> list[tuple[dict, str]]:
    """Split JSONL text into (record, raw_json_text) pairs.

    A raw decoder walk is required because these files are not strictly
    one-object-per-line: `vera_expf_revision_findings.jsonl` holds two
    pretty-printed objects across four physical lines. A line-based regex
    substitution matched a fingerprint mid-object and produced invalid JSON,
    which is how the first version of this script corrupted its input.
    """
    decoder = json.JSONDecoder()
    out: list[tuple[dict, str]] = []
    idx = 0
    while idx < len(text):
        while idx < len(text) and text[idx].isspace():
            idx += 1
        if idx >= len(text):
            break
        try:
            obj, end = decoder.raw_decode(text, idx)
        except json.JSONDecodeError:
            return out  # unparseable: leave the file alone
        out.append((obj, text[idx:end]))
        idx = end
    return out


MD_FP_RE = re.compile(r"^(?P<lead>(?:-\s+)?fingerprint:[ \t]*)(?P<old>[0-9a-f]{8,12})[ \t]*$",
                      re.M)
# The optional `- ` bullet: `decision_graphs_workflow.md` declares its stamp
# as a list item (`- fingerprint: …`), which the old `^fingerprint:` anchor
# silently skipped — the same class of defect as the `^Chunk id:` anchor
# fixed 2026-10-02. The gate reads the first `\bfingerprint` token, which
# `superseded_fingerprint` cannot shadow (no word boundary between `_` and
# `f`), so the widened anchor cannot misdirect it.


def restamp_file(path: Path, live_fp: str, known: set[str], check_only: bool) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    is_md = path.suffix == ".md"
    if is_md:
        if not MD_FP_RE.search(text):
            return "skipped"
        # Only a `Chunk id:` line is load-bearing evidence. A backticked id
        # inside prose is a reference, and a reference to a paper that was
        # never ingested is a documentation problem, not a broken provenance
        # link - it must not freeze the whole file's fingerprint.
        evidence_ids = re.findall(r"^Chunk id:\s*`([0-9]{2}_[a-z0-9_]+)`",
                                  text, re.M)
        cited = evidence_ids
    else:
        if not FP_RE.search(text):
            return "skipped"
        records = split_records(text)
        if not records:
            return "skipped"
        cited = [i for record, _ in records for i in cited_ids(record)]

    broken = {i for i in cited if i not in known}
    if broken:
        sample = ", ".join(sorted(broken)[:3])
        return f"refused:{len(broken)} cited chunk(s) absent from graph.db ({sample})"

    # Surgical: replace only the fingerprint *value* in place. Re-serializing a
    # parsed record with json.dumps(indent=2) expanded each object across ~13
    # physical lines, breaking the one-object-per-line contract these files are
    # read under. The file's own formatting is not ours to change.
    if is_md:
        def _md(match: re.Match) -> str:
            if match.group("old") == live_fp:
                return match.group(0)
            return (f'{match.group("lead")}{live_fp}\n'
                    f'# superseded_fingerprint: {match.group("old")}')
        new_text = MD_FP_RE.sub(_md, text)
    else:
        def _json(match: re.Match) -> str:
            old = match.group(2)
            if old == live_fp:
                return match.group(0)
            return (f'{match.group(1)}"superseded_fingerprint": "{old}",'
                    f'{match.group(1)}"fingerprint": "{live_fp}"')
        new_text = PROV_FP_RE.sub(_json, text)

    if new_text == text:
        return "skipped"
    if not check_only:
        path.write_text(new_text, encoding="utf-8")
    return "ok"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="report what would be re-stamped; write nothing")
    args = ap.parse_args()

    live_fp = live_fingerprint()
    known = known_chunk_ids()
    print(f"live fingerprint: {live_fp}   graph chunks: {len(known)}")

    refused = 0
    stamped = 0
    for directory in TARGETS:
        if not directory.is_dir():
            continue
        for pattern in ("*.jsonl", "*.md"):
            for path in sorted(directory.rglob(pattern)):
                status = restamp_file(path, live_fp, known, args.check)
                if status == "ok":
                    stamped += 1
                    verb = "would restamp" if args.check else "restamped"
                    print(f"  {verb}: {path.relative_to(ROOT)}")
                elif status.startswith("refused"):
                    refused += 1
                    print(f"  REFUSED: {path.relative_to(ROOT)} - {status.split(':', 1)[1]}")
    print(f"\n{stamped} file(s) {checked_verb(args.check)}, {refused} refused")
    if refused:
        print("Refused files cite chunks that no longer exist. Re-run reflection for "
              "those topics instead of re-stamping over the break.", file=sys.stderr)
    return 1 if refused else 0


def checked_verb(check_only: bool) -> str:
    return "needing restamp" if check_only else "restamped"


if __name__ == "__main__":
    raise SystemExit(main())
