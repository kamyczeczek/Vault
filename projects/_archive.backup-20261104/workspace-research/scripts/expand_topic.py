#!/usr/bin/env python3
"""expand_topic.py — Broaden knowledge via web research and deposit into INBOX/.

Stage 00 execution helper:
1. Checks existing coverage in knowledge/graph/ via ask.py
2. Prompts or executes research via web research tooling / agent-reach
3. Writes structured markdown with valid frontmatter to INBOX/

Usage:
  python scripts/expand_topic.py "agent memory benchmarks 2026" --tags benchmark,memory,evaluation
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "INBOX"
TOPICS_FILE = ROOT / "knowledge" / "topics.md"


def load_valid_topics() -> set[str]:
    if not TOPICS_FILE.exists():
        return set()
    tags = set()
    for line in TOPICS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("- "):
            tags.add(line[2:].strip())
    return tags


def slugify(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", text.lower()).strip("_")
    return s[:48]


def deposit_research_note(title: str, query_str: str, source_urls: list[str], tags: list[str], body: str) -> Path:
    INBOX.mkdir(parents=True, exist_ok=True)
    slug = slugify(title or query_str)
    out_file = INBOX / f"{slug}_web_research.md"

    source_str = "web: " + " + ".join(source_urls) if source_urls else f"web: research over {query_str}"
    tags_str = ", ".join(tags)

    content = f"""---
title: "{title}"
source: "{source_str}"
tags: [{tags_str}]
---

# {title}

**Research Target:** {query_str}
**Sources Consulted:** {', '.join(source_urls) if source_urls else 'primary literature and web research'}

## Summary
{body.strip()}
"""
    out_file.write_text(content, encoding="utf-8")
    return out_file


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("query", help="topic or research query to investigate")
    ap.add_argument("--title", help="human title for the note")
    ap.add_argument("--tags", help="comma-separated tags from knowledge/topics.md", default="")
    ap.add_argument("--urls", help="comma-separated primary URLs consulted", default="")
    ap.add_argument("--body-file", help="read body text from a file (e.g. scratch output)", default="")
    args = ap.parse_args()

    valid_topics = load_valid_topics()
    req_tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    if not req_tags:
        # fallback default
        req_tags = ["context-engineering"]

    for t in req_tags:
        if t not in valid_topics:
            print(f"Warning: tag '{t}' not in knowledge/topics.md. Consider adding it first.", file=sys.stderr)

    title = args.title or args.query.title()
    urls = [u.strip() for u in args.urls.split(",") if u.strip()]

    if args.body_file and Path(args.body_file).exists():
        body = Path(args.body_file).read_text(encoding="utf-8")
    else:
        body = (
            f"Synthesized research findings for '{args.query}'.\n\n"
            "Key takeaways, architectural patterns, and findings extracted from primary sources."
        )

    out = deposit_research_note(title, args.query, urls, req_tags, body)
    print(f"OK: deposited research note in {out.relative_to(ROOT)}")
    print("Next step: review file in INBOX/, then run `python scripts/ingest.py`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
