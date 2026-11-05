---
type: Concept
id: 00_measured_closed_families_need_frontier_state
title: "Measured Lesson — Closed Families Need Machine-Readable Frontier State (h720 S-43 P4) (part 1/2)"
source: "measured_closed_families_need_frontier_state.md"
tags: [agentic, agents, forecasting, frontier-state, negative-results, planning, reflection]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---
taxonomy: #frontier-state #negative-results #forecasting
# Measured Lesson — Closed Families Need Machine-Readable Frontier State (h720 S-43 P4)

## What was measured

Four model families were closed on the h720 benchmark, each closed by its own spec text in a
different document. **There was no single place a planner could read "these four are shut and
the next admissible move is X."**

The closures, with their numbers:

| Family | Closure evidence | Number |
|---|---|---|
| Zero-shot TSFM | Phase 2, sampled | 2.1218 |
| PEFT / foundation adaptation | Bet 1, full | 2.0062 |
| Linear multivariate | Bet 2, val_full / sparsity | 2.8638 / 0 |
| Patch-attention non-linear | Bet 3, singleton val | 3.0267 |

## Why this is a real failure, not tidiness

Closures accumulate **section-by-section as experiments run**. The routing is implicit in prose:
each close is recorded in the section of the experiment that produced it, in the document that
experiment happened to touch. Nothing indexes the set.

A planner asking "what is still open?" must read four different documents and reconstruct the
frontier by hand. The failure mode that follows is direct: **the next proposal can re-enter a
closed family** because nothing machine-visible says it is closed. The cost of that is not
embarrassment — it is a full harness run (Bet 3 cost 488.3 s) plus the family-close reasoning,
re-done from scratch.

The workspace had already recorded the sibling failure at a different granularity:
`reflection_brain` scar `2026-09-12_0435_S-h2-wavelet-terminal-close P2` — a pre-terminal
frontier state with an unverifiable artifact. **Same class, portfolio granularity instead of
artifact granularity.** A recurrence across granularities is a sign the mechanism is missing,
not that two people were careless.

## The transferable rule

**Negative results need a queryable index, not just a record.** A closed family written only in
prose is closed to a careful reader and open to everyone else — including a future agent that
does not know which sections to read.

Concretely, for any portfolio of explored options:

- Maintain one place listing the frontier state: what is closed, with the number and the reason.
- Each entry must carry the **magnitude of what was demonstrated**, not just the verdict.
  "REJECT" is not a finding; "rejected at 3.0267 vs 2.90 screen, held-out gain +0.0204 on the
  legitimate selector" is a finding. Without magnitude, the cheapest-looking re-open is always
  "try again with a different member", which re-pays the full cost of the original experiment.
- The index must be readable by whatever proposes the next step — a planner, a router, or an
  agent — or it does not close the loop.

Recording a verdict records that a thing was tried. Recording the frontier state is what makes
the next proposal different from the last one.

## Provenance
