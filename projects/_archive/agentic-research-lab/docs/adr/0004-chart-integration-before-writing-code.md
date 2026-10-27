---
type: Concept
title: 0004-chart-integration-before-writing-code
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Chart the integration as decision tickets before writing code

`docs/wayfinder/research-graph-reflection-execution.md` exists because four
layers of this repo — research intake, the FTS5 knowledge graph, reflection,
and execution — are each individually specified and individually gated, and the
*seams* between them are not. The 18 gates assert local properties; `CONTEXT.md`
C-7 records that 15 of them passed continuously through six defects whose
failures were all relational. Charting is how the seams get named before code
freezes an unchosen answer into them.

## Considered Options

- **Write the integration directly.** The most tempting option and the wrong one.
  The single largest ambiguity right now is that phase 04 has two runners
  (`spawn.py`, the `omp` agent loop, and `reflect.py`, one LLM call over a
  presearched packet) and `CLAUDE.md` routes to the slower one. Building an
  integration layer first means picking a runner for structural reasons, and the
  choice then becomes a precondition nobody re-examines — which is how
  `03_graph` ended up carrying a hardcoded fingerprint in the first place.
- **Chart it, and resolve tickets in the same session.** Rejected: wayfinder's
  premise is that charting hand-resolves nothing. A session that charts and
  resolves has already made the decisions by the time a human reads the map, so
  the confirmation boundary is decorative.
- **Chart it (chosen).** Destination plus frontier tickets, each ticket a
  question sized to one session, and an explicit `Not yet specified` section for
  fog too coarse to ticket yet. Zero tickets resolved in the charting pass.

## Consequences

The map is marked `CONFIRMED 2026-10-01`: a human accepted option A as the
destination. Confirmation happened *after* charting, which is the ordering this
ADR argues for — the destination fixes the scope, so charting first and asking
second inverts the method. The map does not read as settled, though, and that
distinction is load-bearing: `CONFIRMED` records the decision, while the five
frontier tickets stay open and T1 remains the frontier. A confirmed destination
authorises T1 to start, not T1 through T5.

`check_wayfinder_map.py` gate G6 enforces that the status marker is present and
well-formed. It did not survive the confirmation unchanged: it required the
words `PROPOSED`, which had encoded *charting precedes confirmation* as *this
text is permanent*, so the first correct update to the map failed a gate written
for the previous state. It now accepts either state and demands an ISO date on a
confirmation.

The destination is written with four checkable conditions rather than a topic,
because "integrate research and knowledge" is not a thing that can be reached —
it is a thing that can be half-built indefinitely. Each condition is the kind of
claim this repo has been burned by before: one canonical runner, a measurement
for the execution seam, one gate per seam, and a cold walk test.

Three things this map deliberately does not do. It does not touch corpus
content, chunking, or the graph schema — those are recorded in `CONTEXT.md` C-4
as measured flat, with a negative control proving the metric was saturated, so
re-proposing them spends budget for a known-zero result. It does not modify
sibling projects, because the workspace rule is one project per session. And it
does not delete stale reflection artifacts, because the workspace rule is that a
gate-flagged artifact is evidence.

`check_wayfinder_map.py` was written before it was trusted, and the negative
control found two of its own gates green against deliberately broken maps: G2
matched a bullet shape the map never used, and G3 searched for `- T1` while
Decisions entries are written `- **[T1 — title]**`. Both were the same defect
class as `check_graph_determinism`, which asserted a safety property and
restored only one of the five files its own check wrote. The control is recorded
in the gates ledger rather than discarded, because the two near-misses are more
useful to the next session than a clean run would be.

It paid for itself twice. The third time was at the confirmation boundary: the
old `unmarked-provisional` mutation was pinned to the literal text `PROPOSED`,
which stops existing the moment a map is confirmed, so the mutation became a
no-op that reported success while testing nothing. Only the control's refusal to
treat a no-op as a pass exposed it. Two mutations now cover both states, and the
run is 8/8.