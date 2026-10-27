#!/usr/bin/env python3
"""check_stage_contracts.py — stage CONTEXT.md must not hardcode moving values.

The corpus fingerprint and the WORKFLOW.md plan_version are live values: they change on
every corpus edit and every plan edit. The stage contracts are prose documents that
agents read as the Inputs Table, so a hardcoded value there silently becomes a lie the
day after a rebuild — and the project has already fought exactly this failure
(three digests carried a pre-repair fingerprint after a corpus tag repair, caught only
by the P5 gate, not by the docs that claimed to describe the current graph).

Contract: a CONTEXT.md under stages/ MAY name the current fingerprint inline for a human
reader, but only inside the de-hardcoding caveat (it must also name
`knowledge/graph/.graph_fingerprint` as the live source). A bare 12-hex literal with no
caveat is a violation, because nothing in the surrounding text points the reader at the
value that actually moves.

Exit code: 0 = clean, 1 = violation.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGES = ROOT / "stages"

FP_LITERAL = re.compile(r"[^0-9a-f]([0-9a-f]{12})[^0-9a-f]")
LIVE_SOURCE = "knowledge/graph/.graph_fingerprint"
def violations(text: str, window: int = 400) -> list[str]:
    """A 12-hex literal is allowed only near the live-source pointer.

    `window` is the number of characters of surrounding context that must name
    knowledge/graph/.graph_fingerprint for the literal to count as annotated.
    """
    found = []
    for m in FP_LITERAL.finditer("\n" + text + "\n"):
        start = max(0, m.start() - window)
        end = min(len(text), m.end() + window)
        if LIVE_SOURCE not in text[start:end]:
            line = text[:m.start()].count("\n") + 1
            found.append((line, m.group(1)))
    return found



def main() -> int:
    problems = []
    contexts = sorted(STAGES.rglob("CONTEXT.md"))
    if not contexts:
        print("FAIL: no stages/*/CONTEXT.md found", file=sys.stderr)
        return 1
    for path in contexts:
        text = path.read_text(encoding="utf-8", errors="replace")
        for line, literal in violations(text):
            problems.append(f"{path.relative_to(ROOT)}:{line}: bare fingerprint "
                            f"literal `{literal}` with no live-source caveat "
                            f"(`{LIVE_SOURCE}`) — value moves on every corpus edit")
    if problems:
        for p in problems:
            print(f"FAIL: {p}", file=sys.stderr)
        return 1
    print(f"OK: checked {len(contexts)} stage contracts — no hardcoded moving values.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
