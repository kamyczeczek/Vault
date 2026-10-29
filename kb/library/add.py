#!/usr/bin/env python3
"""add.py — file a raw source document into the workspace library.

Content-addressed: the file is stored under the first two hex characters of its
sha256 and the full digest, so re-adding identical content is a no-op rather
than a second copy. That property is the reason for the layout — a 40 MB book
pulled from a different mirror is byte-identical, and a title-keyed library
would let that duplicate in unnoticed.

Only `index.json` is committed. The bytes stay out of git: the material here
is mostly books, much of it z-library, and git history cannot be scrubbed. The
index is what makes the library reviewable — which sources exist, what they
hash to, which projects cite them.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.json"
BINARY_SUFFIXES = {".pdf", ".epub", ".txt", ".md", ".html", ".docx", ".mobi", ".azw3"}


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_index() -> dict:
    if not INDEX.is_file():
        return {}
    try:
        return json.loads(INDEX.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"error: {INDEX} is not valid JSON; refusing to overwrite it", file=sys.stderr)
        raise SystemExit(1)


def store(path: Path, digest: str) -> Path:
    dest_dir = ROOT / digest[:2]
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{digest}{path.suffix.lower()}"
    if not dest.exists():
        dest.write_bytes(path.read_bytes())
    return dest


def save_index(index: dict) -> None:
    """Persist the index. Every mutation path must go through here."""
    INDEX.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n",
                     encoding="utf-8")


def add_entry(path: Path, title: str, projects: list[str] | None = None) -> tuple[str, bool]:
    """File one source. Returns (sha256, already_present).

    Callers that build the index in a loop must use this rather than mutating
    a dict in place — an index that is never saved is an index of nothing, and
    the bytes on disk look like a successful filing either way.
    """
    digest = sha256_of(path)
    index = load_index()
    if digest in index:
        entry = index[digest]
        for name in projects or []:
            if name not in entry["cited_by"]:
                entry["cited_by"].append(name)
                entry["cited_by"].sort()
        save_index(index)
        return digest, True

    dest = store(path, digest)
    index[digest] = {
        "title": title or path.stem,
        "filename": path.name,
        "sha256": digest,
        "bytes": path.stat().st_size,
        "path": f"{digest[:2]}/{dest.name}",
        "cited_by": sorted(set(projects or [])),
    }
    save_index(index)
    return digest, False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", help="file to add")
    parser.add_argument("--title", default="", help="human title (defaults to the filename)")
    parser.add_argument("--project", action="append", default=[], help="project citing it; repeatable")
    args = parser.parse_args()

    path = Path(args.source).expanduser()
    if not path.is_file():
        print(f"error: no such file: {path}", file=sys.stderr)
        return 1
    if path.suffix.lower() not in BINARY_SUFFIXES:
        print(f"error: {path.suffix or 'no suffix'} is not a recognised source type",
              file=sys.stderr)
        return 1

    digest, existed = add_entry(path, args.title, args.project)
    index = load_index()
    if existed:
        print(f"[add] already present: {index[digest]['title']} ({digest[:12]})")
    else:
        print(f"[add] {index[digest]['title']} -> {index[digest]['path']} ({digest[:12]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
