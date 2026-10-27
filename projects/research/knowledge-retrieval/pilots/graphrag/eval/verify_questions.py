#!/usr/bin/env python3
"""verify_questions.py — validate evaluation questions against quality rules.

Rules:
- Question cannot contain node IDs (e.g. digits followed by underscore and lowercase letters, like 621_artificial...).
- Question cannot contain forbidden metadata words: węzeł, rozdział, źródło, family, part.
- Question must end with '?'.
- Question must be between 15 and 140 characters long.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

NODE_ID_RX = re.compile(r"\b[0-9]+_[a-z_]+")
FORBIDDEN_WORDS = {"węzeł", "rozdział", "źródło", "family", "part", "wezel", "rozdzial", "zrodlo"}


def validate_question(q: str) -> list[str]:
    errors = []
    q_stripped = q.strip()
    if not q_stripped:
        return ["empty question"]
    if not q_stripped.endswith("?"):
        errors.append("must end with '?'")
    if not (15 <= len(q_stripped) <= 140):
        errors.append(f"length {len(q_stripped)} outside [15, 140]")
    if NODE_ID_RX.search(q_stripped):
        errors.append("contains node ID pattern (e.g. 123_abc)")
    lower_q = q_stripped.lower()
    for word in FORBIDDEN_WORDS:
        if re.search(r"\b" + word + r"\b", lower_q):
            errors.append(f"contains forbidden metadata word: '{word}'")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify evaluation questions.")
    ap.add_argument("path", type=Path, help="Path to questions file (markdown or txt)")
    a = ap.parse_args()

    if not a.path.is_file():
        print(f"Error: file not found: {a.path}", file=sys.stderr)
        return 1

    content = a.path.read_text(encoding="utf-8")
    lines = content.splitlines()
    questions = []
    for line in lines:
        line_s = line.strip()
        if not line_s or line_s.startswith("#"):
            continue
        # Check if markdown table row
        if line_s.startswith("|"):
            parts = [p.strip() for p in line_s.split("|")]
            # parts[0] is empty before first pipe, parts[1] is ID, parts[2] is Question
            if len(parts) >= 3:
                qid = parts[1]
                qtext = parts[2]
                if qid.lower() in ("id", "---") or "---" in qid:
                    continue
                if qtext and qtext != "Pytanie":
                    questions.append((line_s, qtext))
            continue

        # Non-table lines
        if line_s.startswith(("-", "*", "Q")) or re.match(r"^[0-9]+\.", line_s):
            cleaned = re.sub(r"^(-\s+|\*\s+|Q[0-9]*[a-z]*[\.:]?\s*|[0-9]+\.\s*)", "", line_s)
            if cleaned:
                questions.append((line_s, cleaned))

    if not questions:
        questions = [(l, l) for l in lines if l.strip() and not l.startswith("#")]

    total = 0
    failed = 0
    for raw, q in questions:
        total += 1
        errs = validate_question(q)
        if errs:
            failed += 1
            print(f"FAIL: {q}\n  Errors: {', '.join(errs)}")
        else:
            print(f"OK: {q}")

    print(f"\nTotal: {total}, Failed: {failed}")
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
