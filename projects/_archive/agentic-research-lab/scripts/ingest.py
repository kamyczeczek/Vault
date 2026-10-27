#!/usr/bin/env python3
"""
ingest.py — Turn raw INBOX material into knowledge/corpus/ front-matter chunks.

Design (faithful to proven ts-research corpus contract):
- Each output chunk is a markdown file with YAML-ish front matter:
      ---
      id: NN_slug
      title: "Human Title"
      source: "original filename"
      tags: [tag1, tag2]
      ---
      # Body ...
- A short auto-generated summary header (first sentence(s)) is kept to aid the
  graph digest readability, but full body is indexed for FTS.

Run:
    python scripts/ingest.py            # ingest everything in INBOX
    python scripts/ingest.py --dry      # show plan, write nothing
    python scripts/ingest.py --file INBOX/foo.pdf
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def is_pdf(path: Path) -> bool:
    if path.suffix.lower() == ".pdf":
        return True
    try:
        return path.read_bytes()[:5] == b"%PDF-"
    except Exception:
        return False


ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "INBOX"
# INBOX/ideas/ holds arguments (scripts/discuss.py), not papers. A discussion
# file is never a research source: ingesting one would cut the lab's own
# argument into the corpus and let the brain cite the skeptic as evidence.
IDEAS = INBOX / "ideas"


def is_idea_file(path: Path) -> bool:
    """True for discussion files, which intake must never consume."""
    try:
        return path.resolve().is_relative_to(IDEAS.resolve())
    except OSError:
        return False
CORPUS = ROOT / "knowledge" / "corpus"
RAW = ROOT / "knowledge" / "raw"

CHUNK_CHARS = 3000
SLUG_RE = re.compile(r"[^a-z0-9]+")

# The corpus-health detector defines what "run-together words" means, so the
# extractor and the gate that judges it can never disagree about the threshold.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_corpus_health import suspicious_runs

# Per-source tag hints (keyword -> extra tags). Conservative; real tags come
# from the ingestor's heading/keyword scan below.
DOMAIN_TAGS = {
    "context": ["context-engineering"],
    "agent": ["agents", "agentic"],
    "plan": ["planning"],
    "memory": ["memory"],
    "icm": ["icm"],
    "leak": ["anti-leakage"],
    "reflect": ["reflection"],
    "prompt": ["prompt-engineering"],
}


def slugify(s: str, maxlen: int = 48) -> str:
    s = s.lower()
    s = re.sub(r"\.pdf$|\.md$|\.txt$|\.epub$", "", s)
    s = SLUG_RE.sub("_", s).strip("_")
    return s[:maxlen].strip("_") or "doc"


def extract_epub_text(path: Path) -> tuple[str, str]:
    import zipfile
    from html.parser import HTMLParser

    class HTMLFilter(HTMLParser):
        def __init__(self):
            super().__init__()
            self.text = []
        def handle_data(self, data):
            self.text.append(data)

    title = path.stem
    body_chunks = []
    try:
        with zipfile.ZipFile(path, 'r') as z:
            for name in z.namelist():
                if name.lower().endswith(('.html', '.xhtml', '.htm')):
                    try:
                        html_bytes = z.read(name)
                        f = HTMLFilter()
                        f.feed(html_bytes.decode('utf-8', errors='ignore'))
                        text = "".join(f.text)
                        if len(text.strip()) > 50:
                            body_chunks.append(text)
                    except Exception:
                        pass
    except Exception as e:
        return path.stem, f"[epub extraction failed: {e}]"

    body = "\n\n".join(body_chunks).strip()
    return title[:120], body



def _pdf_page_text(page) -> str:
    """Extract one page, preferring the mode that preserves intra-word spacing.

    pypdf's default mode discards glyph positioning and emits run-together words
    ("ofthecausalinferenceengine"). `extraction_mode="layout"` reconstructs the
    spacing from the text matrix. Verified on the two INBOX PDFs: the default
    mode produced 31 glue runs across seven sampled pages, layout mode produced
    0. The mode is chosen per page by measuring it rather than hardcoded, so a
    PDF with no usable layout pass still extracts - the page falls back to the
    default mode instead of losing its text.
    """
    best, best_glue = "", None
    for kwargs in ({"extraction_mode": "layout"}, {}):
        try:
            text = page.extract_text(**kwargs) or ""
        except Exception:  # noqa: BLE001 - one bad mode must not abort the book
            continue
        text = _normalize_layout(text)
        glue = len(suspicious_runs(text))
        if best_glue is None or glue < best_glue:
            best, best_glue = text, glue
        if not glue:
            break
    return best


def _normalize_layout(text: str) -> str:
    """Remove the artifacts that layout-mode extraction introduces.

    Layout mode reconstructs columns, so it emits runs of padding spaces and
    keeps the printed hyphenation ("Sys-\\ntem/360"). Left alone, FTS5 indexes
    "Sys tem" as two tokens and "man-monthmythical" as one - it reintroduces,
    in a different shape, the very run-together words this mode was chosen to fix.
    """
    text = text.replace("\u00ad", "")          # soft hyphen
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)  # de-hyphenate across the line break
    text = re.sub(r"[ \t]{2,}", " ", text)     # layout padding
    text = re.sub(r"^ *", "", text, flags=re.M)  # per-line leading padding
    return text


def extract_text(path: Path) -> tuple[str, str]:
    """Return (title, body) for a pdf/md/txt/epub file."""
    name = path.name
    if path.suffix.lower() == ".epub":
        return extract_epub_text(path)
    if is_pdf(path):
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            num_pages = len(reader.pages)
            sample_indices = {0, num_pages - 1}
            if num_pages > 2:
                step = max(1, num_pages // 7)
                for i in range(1, num_pages - 1, step):
                    sample_indices.add(i)
            sampled_text_chars = 0
            for idx in sorted(sample_indices):
                if idx < num_pages:
                    sampled_text_chars += len(_pdf_page_text(reader.pages[idx]).strip())
            body = _normalize_layout(
                "\n\n".join(_pdf_page_text(pg) for pg in reader.pages).strip())
            if sampled_text_chars < 50 and num_pages > 1:
                body = f"[Warning: PDF appears to be scanned or image-based with low native text density]\n\n" + body
            first = next((l.strip() for l in body.splitlines() if l.strip()), name)
            title = first[:120]
            return title, body
        except Exception as e:  # noqa
            return name, f"[pdf extraction failed: {e}]"
    text = path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix.lower() == ".md":
        # front matter already? keep title from first heading
        fm = re.match(r"^---\n.*?\n---\n", text, re.DOTALL)
        if fm:
            body = text[fm.end():]
        else:
            body = text
        m = re.search(r"^#{1,2}\s+(.+)$", body, re.MULTILINE)
        title = m.group(1).strip() if m else name
        return title, body
    # txt
    first = next((l.strip() for l in text.splitlines() if l.strip()), name)
    return first[:120], text


def infer_tags(title: str, body: str) -> list[str]:
    text = (title + "\n" + body).lower()
    tags: set[str] = set()
    for kw, t in DOMAIN_TAGS.items():
        if kw in text:
            tags.update(t)
    # extract #hashtags from body
    for h in re.findall(r"#(\w[\w\-]*)", body):
        tags.add(h)
    return sorted(tags)


def split_sections(body: str, size: int = CHUNK_CHARS) -> list[str]:
    """Split at paragraph boundaries into ~size-char sections."""
    paras = re.split(r"\n\s*\n", body)
    sections: list[str] = []
    cur: list[str] = []
    n = 0
    for p in paras:
        p = p.strip()
        if not p:
            continue
        if n + len(p) > size and cur:
            sections.append("\n\n".join(cur))
            cur = []
            n = 0
        cur.append(p)
        n += len(p) + 2
    if cur:
        sections.append("\n\n".join(cur))
    return sections or [body]


def record_failure(condition: str, reason: str, correction: str) -> None:
    event = {"event": "FAILURE_TRIPLE", "condition": condition, "reason": reason, "correction": correction}
    try:
        with (ROOT / "reflection" / "events.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except OSError:
        pass


def validate_chunk_write(path: Path, content: str) -> None:
    resolved = path.resolve()
    corpus_root = CORPUS.resolve()
    if resolved.parent != corpus_root:
        raise ValueError(f"chunk path escapes corpus sandbox: {resolved}")
    if not content.startswith("---\n") or "\nid: " not in content or "\nsource: " not in content:
        raise ValueError("chunk failed frontmatter prevalidation")
    if not content.rstrip().endswith("---") and "\n---\n\n" not in content:
        raise ValueError("chunk failed body delimiter prevalidation")


def chunk_id(idx: int, total: int, source: str) -> str:
    """The single definition of a chunk id.

    --dry used to recompute this separately and got it wrong, so a preview could
    overwrite and delete live corpus files. One function, one answer.
    """
    seq = f"{idx:02d}" if total > 1 else "00"
    return f"{seq}_{slugify(source)}"


def write_chunk(idx: int, total: int, source: str, title: str, tags: list[str], body: str) -> str:
    cid = chunk_id(idx, total, source)
    title_disp = f"{title} (part {idx+1}/{total})" if total > 1 else title
    head = "---\n"
    head += f"id: {cid}\n"
    head += f'title: "{title_disp.replace(chr(34), chr(39))}"\n'
    head += f"source: \"{source}\"\n"
    head += "trust_tier: 1\n"
    head += "derives_from: []\n"
    head += "supports: []\n"
    head += "refutes: []\n"
    head += "contradicts: []\n"
    head += "extends: []\n"
    head += f"tags: [{', '.join(tags)}]\n"
    head += "---\n\n"
    out = head + body.strip() + "\n"
    target = CORPUS / f"{cid}.md"
    try:
        validate_chunk_write(target, out)
        target.write_text(out, encoding="utf-8")
    except (OSError, ValueError) as exc:
        record_failure("chunk_write", str(exc), "repair frontmatter or sandbox path, then retry")
        raise
    return cid


def ingest_file(path: Path, dry: bool = False) -> list[str]:
    title, body = extract_text(path)
    if len(body) < CHUNK_CHARS:
        sections = [body]
    else:
        sections = split_sections(body)
    tags = infer_tags(title, body)
    if not tags:
        tags = ["seed", slugify(path.stem, 16)]
    written = [chunk_id(i, len(sections), path.name) for i in range(len(sections))]
    if dry:
        # --dry must not touch the corpus. It previously wrote every chunk and
        # then tried to delete them by recomputing their ids, which produced a
        # different slug than write_chunk used (48 vs 55 chars). When the new
        # id collided with an existing chunk, --dry overwrote a live corpus file
        # and then deleted it: 369 chunks of The Book of Why destroyed by a
        # preview. Only the extraction and split are previewed now.
        return written
    for i, sec in enumerate(sections):
        written[i] = write_chunk(i, len(sections), path.name, title, tags, sec)
    return written


def find_family_chunks(needle: str) -> list[Path]:
    """Corpus chunks whose declared source matches `needle` (case-insensitive).

    The needle is matched against the whole `source:` value, not a slug, so
    "book of why" finds all 386 chunks even though the filename is truncated in
    the chunk id. Quotes are stripped before matching: the frontmatter stores
    `source: "Name.pdf"`, and matching the raw value returned only 17 of 386.
    """
    needle = needle.lower().strip()
    hits = []
    for path in sorted(CORPUS.glob("*.md")):
        head = path.read_text(encoding="utf-8", errors="replace")[:4000]
        m = re.search(r"^source:\s*(.+?)\s*$", head, re.M)
        if not m:
            continue
        if needle in m.group(1).strip().strip('"').lower():
            hits.append(path)
    return hits


def evict_family(needle: str, dry: bool = False) -> list[str]:
    """Delete superseded chunks for one source family.

    Re-ingesting a book under a different filename produces different chunk ids,
    so the damaged chunks would survive alongside their clean replacements and
    the corpus would hold two copies of the same book. Eviction is explicit
    because it removes hundreds of files: it is only ever called with a
    caller-supplied needle, never inferred.
    """
    removed = []
    for path in find_family_chunks(needle):
        removed.append(path.stem)
        if not dry:
            path.unlink()
    return removed

def _stage(path: Path) -> bool:
    """Stage an ingested source so git records that it exists.

    Staging is enough; committing is the user's call. A file that is staged
    cannot be lost to an inbox cleanup, and `git status` names it as new rather
    than as debris to be swept.
    """
    try:
        subprocess.run(
            ["git", "add", "--", str(path)], cwd=ROOT, check=True,
            capture_output=True, text=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        detail = getattr(exc, "stderr", "") or exc
        print(f"[ingest] warning: could not stage {path.name} ({detail.strip()}); "
              f"add it by hand or the source is at risk", file=sys.stderr)
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry", "--dry-run", dest="dry", action="store_true", help="preview ingestion without changing files")
    ap.add_argument("--file", help="ingest a single INBOX file")
    ap.add_argument("--replace", metavar="NEEDLE",
                    help="evict existing corpus chunks whose source matches NEEDLE "
                         "before ingesting; use when re-ingesting a book under a new "
                         "filename so the corpus does not hold two copies")
    args = ap.parse_args()

    if args.file:
        # resolve against INBOX, not CWD: a bare name is what callers pass
        cand = INBOX / args.file
        chosen = cand if cand.is_file() else Path(args.file)
        # --file is a bypass for everything else that calls it, so the
        # discussion exemption has to be checked here too.
        if is_idea_file(chosen):
            print(
                f"[ingest] refused: {chosen} is a discussion under "
                "INBOX/ideas/, not a research source. Arguments are not "
                "evidence; only an `unresolved` discussion that is `staged` "
                "becomes a candidate (scripts/discuss.py stage).",
                file=sys.stderr,
            )
            return 1
        files = [chosen]
    else:
        if not INBOX.exists():
            print("[ingest] no INBOX", file=sys.stderr)
            return 1
        files = sorted(
            p for p in INBOX.iterdir()
            if p.is_file()
            and not is_idea_file(p)
            and (is_pdf(p) or p.suffix.lower() in {".md", ".txt", ".epub"})
        )

    if not args.dry:
        CORPUS.mkdir(parents=True, exist_ok=True)
        RAW.mkdir(parents=True, exist_ok=True)

    # Optional PDF inspection report for intake visibility
    pdfs = [f for f in files if is_pdf(f)]
    if pdfs:
        try:
            from inspect_pdf import inspect_pdf
            for f in pdfs:
                info = inspect_pdf(f)
                if "error" not in info:
                    native = "native" if info.get("native_extractable") else "image/scanned"
                    print(f"[inspect_pdf] {info['path']} -> {info.get('pages',0)} pages, {native}")
                else:
                    print(f"[inspect_pdf] {info['path']} -> ERROR: {info['error']}", file=sys.stderr)
        except Exception as e:
            print(f"[inspect_pdf] optional inspection unavailable: {e}", file=sys.stderr)

    total = 0
    plan = []
    if args.replace:
        evicted = evict_family(args.replace, dry=args.dry)
        verb = "would evict" if args.dry else "evicted"
        print(f"[ingest] {verb} {len(evicted)} superseded chunk(s) matching "
              f"{args.replace!r}", file=sys.stderr)
    for f in files:
        chunks = ingest_file(f, dry=args.dry)
        total += len(chunks)
        plan.append((f.name, chunks))
        if not args.dry:
            # Archive the original. `shutil.move` is invisible to git: the file
            # reappears under knowledge/raw/ looking like untracked debris, and
            # the next inbox cleanup deletes it as such. Six .md sources were
            # lost exactly this way — their chunks survive, the source does not.
            # Staging on move is what makes a source durable the moment it is
            # ingested. PDFs stay unstaged: .gitignore:14 excludes them by
            # policy, and the workspace library is where binaries live now.
            shutil.move(str(f), str(RAW / f.name))
            if f.suffix.lower() != ".pdf":
                _stage(RAW / f.name)

    if not args.dry and total:
        # W5/W6 provenance: the manifest is a DERIVED index of the corpus, not an
        # append log. Appending rows here drifts whenever the corpus is re-chunked
        # (old rows keep ids that no longer exist). Rebuild it from the corpus
        # `source:` frontmatter so it is always exactly consistent.
        import check_manifest
        rc = check_manifest.rebuild_after_ingest()
        # One-line manifest verdict: reflects the POST-write re-verified state
        # (check_manifest --write re-verifies, so a successful regeneration
        # heals any pre-run staleness instead of misreporting it).
        if rc == 0:
            print("[ingest] manifest: PASS (rebuilt + post-write re-verified)")
        else:
            print("[ingest] manifest: FAIL (provenance break persists; run scripts/check_manifest.py for details)", file=sys.stderr)

    for name, chunks in plan:
        print(f"{name}: {len(chunks)} chunk(s) -> {', '.join(chunks)}")
    print(f"\n{'[dry] ' if args.dry else ''}total chunks: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
