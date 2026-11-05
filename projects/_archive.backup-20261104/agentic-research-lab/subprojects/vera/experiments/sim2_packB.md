---
type: Concept
title: sim2_packB
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Orientation Pack B (SIM-2, "simple" variant)

> One page. If a fresh session can't answer Q1 from this + one `ask.py` call, the pack failed.
> Size target: < 2 KB (pack A = CONTEXT.md + 9 stage CONTEXTs ≈ 55 KB).

## What this lab is
A graph-backed research lab studying **how to do agentic research well**. Knowledge lives in
markdown files (`knowledge/corpus/`); the graph is a derived, rebuildable index.

## The 5 rules that matter

1. **Read:** `python knowledge/graph/ask.py "<core terms>"` (pinned-query terms, not long
   sentences — long verbatim queries return 0 matches; see VERA B0 finding).
2. **Write:** new knowledge enters via `INBOX/` → `python scripts/ingest.py` → corpus. Never
   hand-edit `knowledge/graph/graph.db`.
3. **After corpus changes:** `python knowledge/graph/build_graph.py` (fingerprint restamps).
4. **Never claim without a resolvable chunk ID.** Every research claim cites IDs you can
   resolve with `ask.py`; self-critique alone is not evidence.
5. **Persist after every 2 tool ops** (2-Action Rule): findings → disk before context rots.

## 3 commands

```
python knowledge/graph/ask.py "topic terms"     # retrieve
python scripts/quality_check.py                  # 15-gate health (must pass before commit)
python scripts/agent_commit.py --scope <name> --message "..." --stage <files>   # commit (gated)
```

## Where depth lives (query, don't memorize)
- Rules & rationale → `reflection/memory.md`, `stages/*/CONTEXT.md`
- Current state & next actions → `CONTEXT.md` daily handoff (newest first)
- Ongoing experiments → `subprojects/<name>/` (current: `subprojects/vera/`)
- If unsure what changed: `git log --oneline -5` + the handoff above it

**Pack end.**
