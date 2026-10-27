#!/usr/bin/env python3
"""bootstrap_project_brain.py — Bootstrap a portable Project Brain sidecar (.brain/)
in any external project workspace.

Extracts documentation, READMEs, benchmarks, and markdown notes into atomic corpus chunks,
builds a local SQLite FTS5 graph database, and provides query capability.
"""
from __future__ import annotations
import argparse
import sqlite3
import sys
from pathlib import Path
import re

def bootstrap_brain(target_dir: Path) -> None:
    target_dir = target_dir.resolve()
    brain_dir = target_dir / ".brain"
    corpus_dir = brain_dir / "corpus"
    graph_dir = brain_dir / "graph"
    corpus_dir.mkdir(parents=True, exist_ok=True)
    graph_dir.mkdir(parents=True, exist_ok=True)

    print(f"Bootstrapping Project Brain in {target_dir}...")

    # 1. Discover source files (README.md, docs/, python files with docstrings)
    sources = []
    readme = target_dir / "README.md"
    if readme.exists():
        sources.append(("readme", readme))

    docs_dir = target_dir / "docs"
    if docs_dir.exists():
        for doc in docs_dir.glob("**/*.md"):
            sources.append((doc.stem, doc))

    # Also scan python files for high-level docstrings
    for py in target_dir.glob("*.py"):
        if py.name.startswith("test_") or py.name.startswith("bench_"):
            continue
        sources.append((py.stem, py))

    # 2. Ingest into atomic corpus chunks
    manifest_rows = []
    for slug, path in sources:
        if path.suffix == ".py":
            content = path.read_text(encoding="utf-8", errors="ignore")
            # Extract module docstring if any
            match = re.search(r'^[\s]*"""(.*?)"""', content, re.DOTALL)
            text = match.group(1).strip() if match else f"Python module {path.name}"
        else:
            text = path.read_text(encoding="utf-8", errors="ignore")

        chunk_id = f"00_{slug.lower().replace('-', '_')}"
        chunk_path = corpus_dir / f"{chunk_id}.md"

        chunk_content = f"""---
id: {chunk_id}
title: "{slug.replace('_', ' ').title()}"
source: "{path.relative_to(target_dir)}"
tags: [project-brain, auto-extracted, {slug}]
---

# {slug.replace('_', ' ').title()}

{text[:3000]}
"""
        chunk_path.write_text(chunk_content, encoding="utf-8")
        manifest_rows.append({"id": chunk_id, "file": chunk_path.name, "source": str(path.relative_to(target_dir))})
        print(f"  [+] Ingested chunk {chunk_id} from {path.relative_to(target_dir)}")

    # 3. Build FTS5 graph database
    db_path = graph_dir / "graph.db"
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    conn.execute("CREATE VIRTUAL TABLE nodes USING fts5(id, title, content, tags, path)")

    for row in manifest_rows:
        chunk_path = corpus_dir / f"{row['id']}.md"
        text = chunk_path.read_text(encoding="utf-8")
        # Parse frontmatter and body
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm = parts[1]
            body = parts[2]
        else:
            fm = ""
            body = text

        title_match = re.search(r'title:\s*"(.*?)"', fm)
        title = title_match.group(1) if title_match else row['id']
        tags_match = re.search(r'tags:\s*\[(.*?)\]', fm)
        tags_str = tags_match.group(1) if tags_match else ""

        conn.execute(
            "INSERT INTO nodes(id, title, content, tags, path) VALUES (?, ?, ?, ?, ?)",
            (row['id'], title, body, tags_str, str(chunk_path))
        )
    conn.commit()
    conn.close()

    print(f"SUCCESS: Project Brain successfully created at {brain_dir}")
    print(f"  - Corpus chunks: {len(manifest_rows)}")
    print(f"  - FTS5 graph database: {db_path}")

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target_path", help="Path to external project directory")
    args = parser.parse_args()
    target = Path(args.target_path)
    if not target.exists():
        print(f"ERROR: Path {target} does not exist.", file=sys.stderr)
        return 1
    bootstrap_brain(target)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
