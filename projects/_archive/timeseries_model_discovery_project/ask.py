#!/usr/bin/env python3
"""
ask.py — ROOT-level brain dispatcher.

Reads ROOT/brains/brain_router.md to find the right brain, then
calls that brain's ask.py. Plain keyword matching, no LLM in the
routing loop.

Usage:
    python ask.py "your question" --limit 5
    python ask.py --list-brains         # show known brains
    python ask.py --self-test           # test dispatcher
    python ask.py --brain icm_brain "your question"  # direct dispatch
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BRAINS_DIR = ROOT / "brains"
ROUTER = BRAINS_DIR / "brain_router.md"


def list_brains() -> list[str]:
    """Return the list of brain names from the routing table.

    Parses the markdown table in brain_router.md and returns the
    names of the brain folders (one per row).
    """
    if not ROUTER.exists():
        return []
    text = ROUTER.read_text(encoding="utf-8")
    out: list[str] = []
    # Match rows like: | ICM Knowledge Brain | `brains/icm_brain/` | ...
    for m in re.finditer(r"\|\s*`?brains/([a-z][a-z0-9_-]+)/?`?\s*\|", text):
        out.append(m.group(1))
    # Dedupe preserving order.
    seen: set[str] = set()
    uniq: list[str] = []
    for n in out:
        if n not in seen:
            seen.add(n)
            uniq.append(n)
    return uniq


def load_brain_keywords(brain_name: str) -> set[str]:
    """Read a brain's topics.md and return its keyword set.

    The topics.md format: `### Heading` followed by a list of
    `- keyword` lines. Anything after `## Excluded topics` is
    ignored.
    """
    topics = BRAINS_DIR / brain_name / "topics.md"
    if not topics.exists():
        return set()
    text = topics.read_text(encoding="utf-8", errors="replace")
    # Drop everything after "## Excluded topics"
    cut = text.find("## Excluded")
    if cut >= 0:
        text = text[:cut]
    # Match `  - keyword` (one or more spaces, dash, space, the keyword)
    keywords: set[str] = set()
    for m in re.finditer(r"^\s*-\s+([^\n]+)$", text, re.MULTILINE):
        kw = m.group(1).strip().lower()
        # Strip markdown formatting
        kw = re.sub(r"\*\*?|`", "", kw).strip()
        if kw:
            keywords.add(kw)
    return keywords


def match_brain(question: str) -> tuple[str, int]:
    """Return (brain_name, match_count) for the question.

    Match count = sum of occurrences of any keyword from the
    brain's topics.md in the question. The brain with the highest
    count wins. Ties go to the brain earlier in the routing
    table. If no brain has any match, returns the first brain
    (default) with match_count=0.
    """
    brains = list_brains()
    if not brains:
        return ("", 0)
    q = question.lower()
    best = (brains[0], 0)  # default = first brain (only used when no keyword matches)
    for name in brains:
        keywords = load_brain_keywords(name)
        score = 0
        for kw in keywords:
            # Count substring occurrences. We use a word-boundary
            # check for short keywords (<=4 chars) to avoid false
            # positives (e.g. "icm" matching inside "icm_knowledge").
            if len(kw) <= 4:
                # Word-boundary match for short keywords
                score += len(re.findall(rf"\b{re.escape(kw)}\b", q))
            else:
                # Substring match for longer keywords
                score += q.count(kw)
        if score > best[1]:
            best = (name, score)
    return best


def dispatch(brain_name: str, question: str, limit: int) -> int:
    """Call the brain's ask.py. Returns its exit code."""
    brain_ask = BRAINS_DIR / brain_name / "ask.py"
    if not brain_ask.exists():
        print(f"FAIL: brain '{brain_name}' has no ask.py at {brain_ask}",
              file=sys.stderr)
        return 1
    cmd = [sys.executable, str(brain_ask), question, "--limit", str(limit)]
    print(f"[router] dispatching to {brain_name}: {question!r}")
    result = subprocess.run(cmd, cwd=str(brain_ask.parent))
    return result.returncode


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if args[0] == "--list-brains":
        for n in list_brains():
            print(n)
        return 0
    if args[0] == "--self-test":
        return self_test()

    # Direct dispatch: --brain <name> ...
    if args[0] == "--brain":
        if len(args) < 3:
            print("usage: --brain <name> <question> [--limit N]",
                  file=sys.stderr)
            return 2
        brain_name = args[1]
        question = args[2]
        limit = 5
        if "--limit" in args:
            i = args.index("--limit")
            if i + 1 < len(args):
                limit = int(args[i + 1])
        return dispatch(brain_name, question, limit)

    # Otherwise: parse question + optional --limit
    limit = 5
    if "--limit" in args:
        i = args.index("--limit")
        if i + 1 < len(args):
            limit = int(args[i + 1])
        question = " ".join(a for a in args[:i] + args[i + 2:])
    else:
        question = " ".join(args)

    # Optional brain hint: @<brain_name> ...
    if question.startswith("@"):
        m = re.match(r"@(\S+)\s+(.*)$", question)
        if m:
            return dispatch(m.group(1), m.group(2), limit)

    brain_name, score = match_brain(question)
    if not brain_name:
        print("FAIL: no brains registered in brain_router.md",
              file=sys.stderr)
        return 1
    if score == 0:
        # No brain's topics matched. We fall back to the first brain in
        # the routing table rather than guessing silently: say so, so a
        # bad default is visible instead of returning wrong-but-plausible
        # answers. Use @<brain> to override.
        print(f"[router] WARNING: no topic match for {question!r} — "
              f"defaulting to {brain_name} (first in brain_router.md). "
              f"Use @{brain_name or ''} <question> to pick a brain.",
              file=sys.stderr)
    return dispatch(brain_name, question, limit)


def self_test() -> int:
    """Test the router + dispatch.

    1. list_brains() returns at least one brain.
    2. match_brain("common AI workflow mistakes") -> icm_brain.
    3. match_brain("what is the rule of scars") -> icm_brain.
    4. Dispatch to icm_brain returns exit 0.
    """
    brains = list_brains()
    if not brains:
        print("self-test FAIL: no brains in routing table")
        return 1
    print(f"  brains: {brains}")

    expected_brain = "skills_brain"
    for q in ["which skill for X",
              "workflow stages"]:
        matched, score = match_brain(q)
        if matched != expected_brain:
            print(f"  self-test FAIL: {q!r} matched {matched!r} (expected {expected_brain!r})")
            return 1
        print(f"  ok: {q!r} -> {matched} (score={score})")

    # Real dispatch test
    rc = dispatch("skills_brain", "which skill for X", 3)
    if rc != 0:
        print(f"  self-test FAIL: dispatch exit={rc}")
        return rc
    print("  self-test PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
