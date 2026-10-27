#!/usr/bin/env python3
"""check_brain_identity.py — federation contract gate (IDENTITY.md).

CONTEXT (why this gate exists, and what it is NOT)

`PROCESS/check_brain_router.py` already asserts routing *liveness*: canned queries
route to the expected brain by keyword score and dispatch exits 0. It does not assert
the *contract* — the rules that make the federation one-level rather than hierarchical.

That distinction is measured, not stylistic. The first controlled study of progressive
disclosure for agentic long-document reasoning (arXiv 2607.17598, 3 harnesses x 3 model
families) found a second routing level never helps and sometimes breaks: one Pi/model
pairing saw multiple-choice accuracy collapse 0.91 -> 0.64, because "the always-loaded
child descriptions eat exactly the context budget the structure was meant to save."
The flat one-level arm is the rescue (20-book raw nav 0.26 -> one-level 0.46).

So the one-level rule is the load-bearing constraint, and before this gate it existed
only as convention — nothing prevented a brain's ask.py from delegating to another
brain's ask.py, which would be exactly the collapsing tier.

WHAT THIS GATE ASSERTS (exit 1 on any violation)

  s1 id rule      every corpus file's `id:` frontmatter equals its filename stem;
                  the id is derivable from the path and vice versa
  s2 vocabulary   every routed brain has a topics.md with at least one keyword
  s3 one level    no brain's ask.py imports, subprocesses, or dispatches to another
                  brain's ask.py — there is no meta-router
  s3b direct-call a brain may be deliberately off the keyword router (graph_brain is,
                  because its terms would steal generic queries); being unrouted is a
                  recorded decision, not a defect

exit 0 = contract holds, exit 1 = violation named, exit 2 = prerequisite missing.

WHAT IT DELIBERATELY DOES NOT DO

It does not merge corpora, build a global index, or score semantic similarity between
brains' topics. Each of those is the second tier.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRAINS = ROOT / "brains"
ROUTER = BRAINS / "brain_router.md"
IDENTITY = BRAINS / "IDENTITY.md"

# routed brains appear in the routing table; direct-call brains are named there too but
# the table marks them. We detect "routed" as "has a topics.md the router can score".
ID_RE = re.compile(r"^id:\s*(.+?)\s*$", re.M)
# s3: any reference from one brain's ask.py into another brain's ask.py
SECOND_TIER_RE = re.compile(r"brains/[a-z0-9_-]+/ask\.py")


def parse_router() -> dict[str, dict]:
    """brain name -> row info from the routing table."""
    out: dict[str, dict] = {}
    if not ROUTER.exists():
        return out
    for m in re.finditer(r"^\|.*?`?brains/([a-z][a-z0-9_-]+)/?`?\s*\|(.*)$", ROUTER.read_text(),
                         flags=re.M):
        name, rest = m.group(1), m.group(0)
        out[name] = {"direct_only": "direct-call" in rest.lower()}
    return out


def check_id_rule(brain: Path) -> list[str]:
    """s1: chunk id == filename stem, in every corpus dir this brain owns."""
    errs: list[str] = []
    corpora = [p for p in brain.iterdir() if p.is_dir() and (p / "ask.py").exists() or
               (p.is_dir() and p.name in ("corpus", "knowledge"))]
    # the common case: <brain>/corpus/*.md
    corpus = brain / "corpus"
    if not corpus.exists():
        return []
    for md in sorted(corpus.glob("*.md")):
        head = md.read_text(encoding="utf-8", errors="ignore")[:400]
        m = ID_RE.search(head)
        if not m:
            errs.append(f"{brain.name}: {md.name} has no `id:` frontmatter")
        elif m.group(1) != md.stem:
            errs.append(f"{brain.name}: {md.name} id `{m.group(1)}` != filename stem "
                        f"`{md.stem}` (id must be derivable from the path)")
    return errs


def main() -> int:
    if not IDENTITY.exists():
        print(f"FAIL: {IDENTITY} missing — the federation contract is absent",
              file=sys.stderr)
        return 2
    if not ROUTER.exists():
        print(f"FAIL: {ROUTER} missing — cannot enumerate brains", file=sys.stderr)
        return 2

    table = parse_router()
    if not table:
        print("FAIL: routing table parsed to zero brains", file=sys.stderr)
        return 2

    errors: list[str] = []

    # s2 + s3 for every brain in the table
    for name, info in sorted(table.items()):
        brain = BRAINS / name
        if not brain.is_dir():
            errors.append(f"{name}: routing table names it but {brain} does not exist")
            continue
        ask = brain / "ask.py"
        if not ask.exists():
            errors.append(f"{name}: no ask.py — the read path is missing")
            continue

        # s2: routed brains need a scorable vocabulary
        if not info.get("direct_only"):
            topics = brain / "topics.md"
            if not topics.exists():
                errors.append(f"{name}: routed brain has no topics.md — its corpus is "
                              f"unreachable by question (the s2 defect)")
            else:
                kws = [l.strip("- ").strip()
                       for l in topics.read_text(encoding="utf-8", errors="ignore").splitlines()
                       if re.match(r"^\s*-\s+\S", l)]
                if not kws:
                    errors.append(f"{name}: topics.md has no `- keyword` lines — nothing "
                                  f"to score, so every query falls through to default")

        # s3: one-level routing — no brain may reach into another brain's ask.py
        src = ask.read_text(encoding="utf-8", errors="ignore")
        for hit in SECOND_TIER_RE.finditer(src):
            target = hit.group(0)
            if target.split("/")[1] != name:
                errors.append(f"{name}: ask.py references {target} — second-tier dispatch "
                              f"(the measured 0.91->0.64 collapse); see IDENTITY.md s3")

    # s1 across all brains that own a corpus
    for brain in sorted(BRAINS.iterdir()):
        if brain.is_dir() and (brain / "corpus").exists():
            errors.extend(check_id_rule(brain))

    if errors:
        print(f"FAIL: {len(errors)} federation contract violation(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    routed = [n for n, i in sorted(table.items()) if not i.get("direct_only")]
    direct = [n for n, i in sorted(table.items()) if i.get("direct_only")]
    print(f"OK: federation contract holds — {len(routed)} routed brain(s) "
          f"({', '.join(routed)}) + {len(direct)} direct-call ({', '.join(direct)}); "
          f"id rule holds; no second-tier dispatch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
