---
status: decided
recommendation: variant (b) now — 42-task legacy Lockbox kept as post-hoc diagnostics, no confirmatory claim; variant (c) before final promotion — fresh blind Lockbox built from data outside fev-bench-100; Phase 2 unblocks on Dev immediately
decided_at: 2026-11-07
owner: mateusz
---

# benchmark-core-a7-lockbox

How is the §8 Lockbox remedy resolved after the A6 contamination disclosure
(36/42 Lockbox tasks touched by the aborted 2026-10-30 legacy `--fev-full`
run; 6 clean: `task_id` 76, 92, 93, 94, 95, 99)?

Context: flag `benchmark-core-lockbox-a6-disclosure-2026-11-02` (commit
`01d0b4b`) ruled out mechanical re-partition under the §2 manifest
invariants and named three variants: (a) Lockbox = the 6 clean tasks,
consciously underpowered; (b) the 42 tasks stay as post-hoc diagnostics,
no confirmatory claim; (c) new data outside fev-bench-100 rebuilds a blind
Lockbox with real power. Phase 1b on Dev passed for NLinear
(`results/phase1b_dev_analysis.json`, commit `cd087c3`: NLinear +14.88% vs
SNaive, lower 98.33% CI +3.75% — passes; DLinear +12.08%, lower CI −0.63%
— does not pass; MDE 0.178; 20/20 tasks in 1359 s, all within the 20-min
budget).

Decision (owner, 2026-11-07): **(b) now, (c) before final promotion.**
Variant (a) is rejected: 6 tasks / 4 families / 2 domains cannot carry a
confirmatory Lockbox claim. The 42-task legacy Lockbox is re-designated
post-hoc diagnostics — it may inform debugging and hypothesis generation,
never a confirmatory statement, until (c) delivers a fresh blind Lockbox.
The Lockbox-use ban in PROTOCOL.md §15 (post-A6) stays in force until the
(c) Lockbox is registered; the budget (3 uses, α = 0.01667) applies to the
fresh Lockbox. Phase 2 starts on Dev: starting population N ≤ 8 with
Champion = NLinear, 20-min-per-method budget, dashboard, no generalization
claims.

Not checked: GIFT-Eval overlap with fev-bench (part of its datasets may
overlap fev-bench-100 — must be confirmed before any (c) data selection);
`bench.py --fev-full` guard verified only by the subprocess test
(`test_benchmark_protocol.py::test_fev_full_guard_exits_before_data_access`),
its flag prose not read line by line.

Registered as ledger amendment A7 (`ledger.jsonl` entry appended via
`projects/_archive/benchmark-core-apply-a7.py`, chain verified against the
frozen manifest SHA-256) and the §15 register row A7 in
`projects/research/benchmark-core/PROTOCOL.md`.
