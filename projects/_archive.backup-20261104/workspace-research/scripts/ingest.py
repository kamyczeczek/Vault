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
import os
import re
import shutil
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
CORPUS = ROOT / "knowledge" / "corpus"
RAW = ROOT / "knowledge" / "raw"

CHUNK_CHARS = 3000
SLUG_RE = re.compile(r"[^a-z0-9]+")

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
    s = re.sub(r"\.pdf$|\.md$|\.txt$", "", s)
    s = SLUG_RE.sub("_", s).strip("_")
    return s[:maxlen].strip("_") or "doc"


def extract_text(path: Path) -> tuple[str, str]:
    """Return (title, body) for a pdf/md/txt file."""
    name = path.name
    if is_pdf(path):
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            chunks = []
            for pg in reader.pages:
                t = pg.extract_text() or ""
                chunks.append(t)
            body = "\n\n".join(chunks).strip()
            # crude title: first non-empty line, else filename
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


def write_chunk(idx: int, total: int, source: str, title: str, tags: list[str], body: str) -> str:
    slug = slugify(source)
    seq = f"{idx:02d}" if total > 1 else "00"
    cid = f"{seq}_{slug}"
    if total > 1:
        title_disp = f"{title} (part {idx+1}/{total})"
    else:
        title_disp = title
    head = "---\n"
    head += f"id: {cid}\n"
    head += f'title: "{title_disp.replace(chr(34), chr(39))}"\n'
    head += f"source: \"{source}\"\n"
    head += f"tags: [{', '.join(tags)}]\n"
    head += "---\n\n"
    # keep a clean leading anchor
    out = head + body.strip() + "\n"
    (CORPUS / f"{cid}.md").write_text(out, encoding="utf-8")
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
    written = []
    for i, sec in enumerate(sections):
        cid = write_chunk(i, len(sections), path.name, title, tags, sec)
        written.append(cid)
        if not dry:
            pass  # already written
    if dry:
        # remove the just-written files in dry mode
        for i in range(len(sections)):
            seq = f"{i:02d}" if len(sections) > 1 else "00"
            (CORPUS / f"{seq}_{slugify(path.name)}.md").unlink(missing_ok=True)
    return written


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--file", help="ingest a single INBOX file")
    args = ap.parse_args()

    if args.file:
        # resolve against INBOX, not CWD: a bare name is what callers pass
        cand = INBOX / args.file
        files = [cand if cand.is_file() else Path(args.file)]
    else:
        if not INBOX.exists():
            print("[ingest] no INBOX", file=sys.stderr)
            return 1
        files = sorted(p for p in INBOX.iterdir() if p.is_file() and (is_pdf(p) or p.suffix.lower() in {".md", ".txt"}))

    if not args.dry:
        CORPUS.mkdir(parents=True, exist_ok=True)
        RAW.mkdir(parents=True, exist_ok=True)

    total = 0
    plan = []
    for f in files:
        chunks = ingest_file(f, dry=args.dry)
        total += len(chunks)
        plan.append((f.name, chunks))
        if not args.dry:
            # archive original
            shutil.move(str(f), str(RAW / f.name))

    if not args.dry and total:
        # W5/W6 provenance: the manifest is a DERIVED index of the corpus, not an
        # append log. Appending rows here drifts whenever the corpus is re-chunked
        # (old rows keep ids that no longer exist). Rebuild it from the corpus
        # `source:` frontmatter so it is always exactly consistent.
        import check_manifest
        check_manifest.rebuild_after_ingest()

    for name, chunks in plan:
        print(f"{name}: {len(chunks)} chunk(s) -> {', '.join(chunks)}")
    print(f"\n{'[dry] ' if args.dry else ''}total chunks: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
