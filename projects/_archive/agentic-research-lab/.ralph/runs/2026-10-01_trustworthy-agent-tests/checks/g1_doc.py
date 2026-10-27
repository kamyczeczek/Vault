#!/usr/bin/env python3
"""G1 check: research doc exists and cites >= MIN_SOURCES distinct external primary-source URLs.

Run from the project root. Exit 0 + "G1 OK ..." when the gate is honestly met.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

DOC = Path("docs/research/trustworthy-agent-tests.md")
MIN_SOURCES = 5
# A "primary source" here = a real, reachable external URL (not an in-repo link).
URL_RE = re.compile(r"https?://[^\s)\]<>\"'`]+")
SKIP_HOSTS = ("localhost", "127.0.0.1", "example.com")


def main() -> int:
    if not DOC.exists():
        print(f"G1 FAIL: missing {DOC}")
        return 1
    text = DOC.read_text(encoding="utf-8")
    urls = set()
    for raw in URL_RE.findall(text):
        host = raw.split("//", 1)[-1].split("/", 1)[0].lower()
        if any(host == s or host.endswith("." + s) for s in SKIP_HOSTS):
            continue
        urls.add(raw.rstrip(".,;:"))
    if len(urls) < MIN_SOURCES:
        print(f"G1 FAIL: {len(urls)} external source URL(s), need >= {MIN_SOURCES}")
        for u in sorted(urls):
            print(f"  {u}")
        return 1
    print(f"G1 OK: {DOC} cites {len(urls)} distinct external source URLs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
