"""Whitespace-separated token counter.

A token is any maximal run of non-whitespace characters; runs of any
whitespace (spaces, tabs, newlines) separate tokens. Empty strings and
strings of only whitespace therefore yield zero.

CLI (sanctioned entry point for the dead-code gate):
    python scripts/word_count.py [FILE ...]   # per-file + total token counts
    echo "a b c" | python scripts/word_count.py -   # stdin
"""
from __future__ import annotations

import sys


def count_words(text: str) -> int:
    """Count whitespace-separated tokens in *text*.

    Uses ``str.split()`` with no arguments: leading, trailing, and
    repeated internal whitespace all act as a single separator, so
    ``""`` and ``"   "`` both return 0.

    Args:
        text: The string to tokenize.

    Returns:
        The number of whitespace-separated tokens.
    """
    return len(text.split())


def main(argv: list[str]) -> int:
    """Report whitespace-separated token counts for each FILE (- = stdin)."""
    paths = argv[1:] or ["-"]
    total = 0
    for name in paths:
        if name == "-":
            text: str = sys.stdin.read()
        else:
            with open(name, encoding="utf-8") as fh:
                text = fh.read()
        n = count_words(text)
        total += n
        print(f"{n:8d}  {name}")
    print(f"{total:8d}  <total>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
