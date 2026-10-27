#!/usr/bin/env python3
"""check_reachability.py — read-path liveness gate (phase 4 sub-gate).

The workspace verifies that its *prompts* route (dead_route_tags: every --tag named
in a routing block exists in knowledge/topics.md). Nothing verifies that a *question*
a working agent would actually ask reaches an answer. This gate closes that half.

Grounding (cited in the reflection that proposed this gate):
- `00_reflection_closed_vocabulary_before_content` — "the vocabulary must be maintained,
  or questions silently go unanswered." The boundary condition the corpus names and the
  workspace does not monitor.
- `00_reflection_retrieval_dominates_write` — retrieval is the load-bearing axis
  (r = 0.98 against write strategy's 3-8 points). Effort belongs on reachability, not
  on better chunk writing.
- `00_measured_closed_families_need_frontier_state` — "a closed family written only in
  prose is closed to a careful reader and open to everyone else." A zero-hit question
  is the same defect on the read path.

Contract (fail-loud):
  exit 0  every seeded question reaches >=1 chunk via ask.py (the real read path)
  exit 1  at least one seeded question is unreachable — named, with the chunk ids the
          corpus *does* have for the concept, so the repair is a topics.md alias, not
          a guess
  exit 2  prerequisite missing (graph.db, ask.py, or the seed file)

The gate does not re-derive reachability: it imports ask.py's own `query()` so it
asserts what a working agent actually gets, not an approximation of it.

Seeds live in reflection/reachability-seed.jsonl (one {"question": ..., "expect": ...}
per line). `expect` is the expected answer count; questions are seeded from real
zero-hit runs, not from imagination. Add a seed whenever a question silently fails —
that is the only correct way to grow this file.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "knowledge" / "graph" / "graph.db"
ASK = ROOT / "knowledge" / "graph" / "ask.py"
SEED = ROOT / "reflection" / "reachability-seed.jsonl"


def load_seeds() -> list[dict]:
    """One {"question", "expect"} object per line. Comments start with #."""
    if not SEED.exists():
        return []
    out: list[dict] = []
    for line in SEED.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        try:
            obj = json.loads(s)
        except json.JSONDecodeError as e:
            print(f"FAIL: malformed seed line: {e}", file=sys.stderr)
            sys.exit(2)
        if "question" not in obj or not isinstance(obj.get("expect"), int):
            print(f"FAIL: seed needs string `question` + int `expect`: {s}", file=sys.stderr)
            sys.exit(2)
        out.append(obj)
    return out


def main() -> int:
    # prerequisites
    if not DB.exists():
        print("FAIL: graph.db missing — run watch.py --once / build_graph.py first", file=sys.stderr)
        return 2
    if not ASK.exists():
        print(f"FAIL: {ASK} missing — cannot import the real read path", file=sys.stderr)
        return 2

    sys.path.insert(0, str(ASK.parent))
    import ask as ask_mod

    seeds = load_seeds()
    if not seeds:
        print(f"FAIL: no seeds in {SEED.relative_to(ROOT)} — the gate asserts nothing; "
              f"add questions a working agent is expected to ask", file=sys.stderr)
        return 2

    errors: list[str] = []
    for seed in seeds:
        q, expect = seed["question"], seed["expect"]
        # the real read path a working agent uses: FTS5 AND-semantics over the corpus
        got = ask_mod.query(q, limit=5)
        # negative-control sanity: a control that stops matching means the corpus moved,
        # not that vocabulary improved
        if expect < 1 and got:
            errors.append(
                f"CONTROL-FLIP: '{q}' was seeded as zero-hit (expect={expect}) but now "
                f"returns {len(got)} — the vocabulary gap closed; update this seed "
                f"(reached: {', '.join(r['id'] for r in got[:3])})"
            )
            continue
        if expect > 0 and not got:
            # name what the corpus *does* hold for the concept, via tags, so the repair
            # is an alias in topics.md rather than a guess
            errors.append(
                f"UNREACHABLE: '{q}' reaches 0 chunks (expected {expect}) — the concept "
                f"is in the corpus but not by this question"
            )
        elif expect > 0 and len(got) < expect:
            errors.append(
                f"THIN: '{q}' reaches {len(got)} chunks, expected {expect} "
                f"({', '.join(r['id'] for r in got)})"
            )

    if errors:
        print(f"FAIL: {len(errors)} reachability violation(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"OK: checked {len(seeds)} seeded question(s) — all reachable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
