"""Replace exact line ranges in a file (1-based, inclusive) — CRLF-safe.

Windows tooling scar: `edit` anchors copied from `read` output fail on CRLF
files when the editor expects the other line ending. Read the region with
`read`, then run this with those exact line numbers. Stdlib only.
"""
from __future__ import annotations

import sys
from pathlib import Path


def normalize(path: Path, *, dry_run: bool = False) -> int:
    """Rewrite a file with consistent CRLF (Windows) line endings.

    An `edit`/`replace` round trip can inject LF-only lines into a CRLF file.
    Mixed endings make line numbers disagree between tools and silently break
    `edit` anchors, so normalize before doing line-range work.
    """
    raw = path.read_bytes()
    crlf = raw.count(b"\r\n")
    total = raw.count(b"\n")
    lone = total - crlf
    if lone == 0:
        print(f"OK: {path.name} already consistent ({crlf} CRLF lines)")
        return 0
    if dry_run:
        print(f"DRY: {path.name} would convert {lone} lone LF -> CRLF ({crlf} already CRLF)")
        return 0
    body = raw.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    path.write_bytes(body)
    print(f"OK: {path.name} converted {lone} lone LF -> CRLF")
    return 0


def replace_lines(path: Path, start: int, end: int, new_text: str, *, dry_run: bool = False) -> int:
    """Replace lines start..end (1-based, inclusive) with new_text."""
    raw = path.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    lines = raw.split("\r\n") if crlf else raw.split("\n")
    # Only drop the final empty element if the file ends with a line break;
    # otherwise the last real line would be lost and every range shifts by 1.
    tail = ""
    if lines and lines[-1] == "":
        tail = "\r\n" if crlf else "\n"
        lines = lines[:-1]

    if not (1 <= start <= end <= len(lines)):
        raise SystemExit(f"range {start}..{end} out of bounds (file has {len(lines)} lines)")

    new_lines = new_text.rstrip("\r\n").split("\n")
    out = lines[: start - 1] + new_lines + lines[end:]
    body = ("\r\n" if crlf else "\n").join(out) + tail

    if dry_run:
        print(f"DRY: {path.name} lines {start}..{end} -> {len(new_lines)} lines ({len(lines)} total)")
        return 0
    path.write_bytes(body.encode("utf-8"))
    print(f"OK: {path.name} lines {start}..{end} -> {len(new_lines)} lines (crlf={crlf})")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[1] == "--normalize":
        dry = "--dry-run" in argv
        for target in argv[2:]:
            if target.startswith("--"):
                continue
            normalize(Path(target), dry_run=dry)
        return 0
    if len(argv) < 4:
        raise SystemExit(
            "usage: patch_lines.py <file> <start> <end> [new_file] [--dry-run]\n"
            "       patch_lines.py --normalize <file>..."
        )
    path = Path(argv[1])
    start, end = int(argv[2]), int(argv[3])
    dry = "--dry-run" in argv
    new_text = ""
    if len(argv) > 4 and not argv[4].startswith("--"):
        new_text = Path(argv[4]).read_text(encoding="utf-8")
    return replace_lines(path, start, end, new_text, dry_run=dry)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))