---
type: Concept
flag: decision-brief-hypothesis-D
since: 2026-10-08
owner: Mateusz
agent: goose
model: gemini-flash-lite-latest
title: decision-brief-hypothesis-D
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

2026-10-08: Closed session at D-002 implementation decision.

State:
- Hypothesis D defined: decision brief grounded in graph improves architectural decisions for weak models
- Wayfinder map created at `.wayfinder/MAP.md` with 6 tickets
- D-001 resolved: 4-section template, hard 8K limit, hybrid citation, context-only (no recommendation), file + auto-prepend delivery
- D-002 resolved: new `node_type = "precedent"` with `precedent_kind: adr|scar|pattern`, dedicated `ask.py` filters, hybrid ranking (BM25 * trust * recency), scars as separate output section, non-fatal missing precedents

Next step:
- Start next session with D-003 (decision quality metric) or go straight to implementation
- Implementation order: extend `build_graph.py` → extend `ask.py` → create `build_brief.py` → create run `.ralph/runs/2026-10-08_decision-brief/`
- Do NOT start before reviewing `.wayfinder/MAP.md` and ticket D-002
