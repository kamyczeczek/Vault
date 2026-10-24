---
flag: kr-0746-artifact-resolved-2026-10-16
since: 2026-10-16
owner: mateusz
agent: pi
model: nara/deepseek-v4.1-flash-free
origin: session-close
---

`kr-0746-artifact-resolved-2026-10-16` — 2026-10-16: knowledge-retrieval Open work resolved against the artifact — 0.746 retired, 0.654 stands; next step is the owner's brain/ + knowledge-retrieval merge decision (Opcja 2), deferred to a following session.

R10 WARN closed. `knowledge-retrieval/CONTEXT.md` claimed the standing table and
its artifact disagreed, and that the artifact read `mean_family_precision` 0.629 /
`mean_latency_ms` 112.601. The file on disk
(`_archive/agentic-research-lab/knowledge/graph/retrieval_benchmark_results.json`,
fingerprint `0a5b47437367`) reads 0.654 / 100.188. The unverified 0.746 lived
only in the C-6 commit message — no benchmark run was ever recorded behind it.

Done, committed in the project repo (nested, not root):
- `references/measurements.md`: the "Not yet measured" note 0.746 → 0.654.
- `CONTEXT.md`: the Open work entry marked RESOLVED, artifact numbers corrected.
- `MAP.md`: regenerated after the `_tmp_run_*` deletions (R7).
Project commit: `9b40ac5`.

Root gate after the change: EXIT=0; the two knowledge-retrieval WARNs (stale MAP,
live Open work) are gone. Remaining and not mine: R18 `D-2026-10-11-03` /
`-04` still PENDING_IMPLEMENTATION at 5d.

Also in this close: `handoff/state_description/exports.md` (a pre-existing
regeneration stray from the 06:06 export run, not authored here) is included so
the close is not blocked by it.

not checked: the benchmark was not re-run, so 0.654 is the last measured number
rather than a fresh one, and the within-family ranking gap stays unmeasured. The
brain/ + knowledge-retrieval merge was not attempted — owner decision, next
session.
