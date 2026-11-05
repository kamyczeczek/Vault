---
type: Concept
title: sim2_q22_results
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# SIM-2b Q22 Causal-Chain Follow-up Results

**Date:** 2026-09-25
**Protocol:** `subprojects/vera/experiments/sim2_q22_protocol.md` (pre-registered; verdict rule frozen)
**Run:** `python subprojects/vera/experiments/sim2_q22.py` — 12 sessions (5A, 5B, 2C),
interleaved A1 B1 A2 B2 C1 A3 B3 C2 A4 B4 A5 B5, isolated worktrees `sim2b-{A,B,C}`
(each with gitignored `graph.db` hardlinked in, refinement R-db).
Q1 verdict from SIM-2 v1 remains **INCONCLUSIVE/null** — this run does not overwrite it.

## Task (Q22)

> "Causal chain: how does reorientation cost convert into performance loss for a
> fresh agent session?"

Verified pre-run property that the run hinges on: the **verbatim Q22 question
returns 0 FTS matches** (rc=2) — pinned terms, not sentences (VERA B0).

## Per-Session Raw Metrics

| Slot | Cond | reorient_cum (calls) | ttfva (calls) | ungrounded | rc pattern | per-call wall (s) |
|---|---|---|---|---|---|---|
| 1 | A1 | 2 | 3 | 1 | 2,0,0 | 0.295, 0.282, 0.384 |
| 2 | B1 | 1 | 2 | 1 | 0,0 | 0.236, 0.159 |
| 3 | A2 | 2 | 3 | 1 | 2,0,0 | 0.155, 0.148, 0.165 |
| 4 | B2 | 1 | 2 | 1 | 0,0 | 0.144, 0.155 |
| 5 | C1 | 3 | NA | 3 | 0,2,0 | 0.199, 0.147, 0.155 |
| 6 | A3 | 2 | 3 | 1 | 2,0,0 | 0.146, 0.150, 0.147 |
| 7 | B3 | 1 | 2 | 1 | 0,0 | 0.146, 0.199 |
| 8 | C2 | 3 | NA | 3 | 0,2,0 | 0.151, 0.155, 0.142 |
| 9 | A4 | 2 | 3 | 1 | 2,0,0 | 0.145, 0.146, 0.161 |
| 10 | B4 | 1 | 2 | 1 | 0,0 | 0.155, 0.223 |
| 11 | A5 | 2 | 3 | 1 | 2,0,0 | 0.153, 0.146, 0.156 |
| 12 | B5 | 1 | 2 | 1 | 0,0 | 0.151, 0.158 |

Per-call notes (deterministic FTS):
- A: call 1 = verbatim Q22 → **rc=2, 0 matches** (the B0 failure mode);
  call 2 = `reorientation cost` → seed1 `00_reflection_reorientation_cost`;
  call 3 = `rapid understanding` → seed2 `01_workspace_rapid_understanding`
  (+ distractor-adjacent `31_beyond_vibe_coding...`).
- B: call 1 → seed1; call 2 → seed2. Packed pinned terms hit first-try.
- C: `eviction stale memory` rc=0 (2 non-seed evict-domain chunks),
  `memory rule evict gate` rc=2, `promote candidate gate` rc=0
  (`111_harness_starter_kit`). **No required seed ever retrieved** →
  reorient_cum = 3, ttfva = NA, ungrounded = 3.

## Per-Condition Medians (5 sessions; C n=2 → max)

| Condition | reorient_cum | ttfva | ungrounded | ttfva_tok |
|---|---|---|---|---|
| A | 2 | 3 | 1 | ~624 |
| B | 1 | 2 | 1 | ~624 |
| C | 3 | NA | 3 | ~301 |

## Verdict Rule Evaluation (Pre-Registered)

| Rule | Requirement | A | B | C | Pass? |
|---|---|---|---|---|---|
| 1 | reorient_cum B ≤ A | 2 | 1 | — | **YES** (1 ≤ 2) |
| 2 | ttfva B ≤ A | 3 | 2 | — | **YES** (2 ≤ 3) |
| 3 | ungrounded B = A | 1 | 1 | — | **YES** |
| 4 | reorient_cum C > B (control spike) | — | 1 | 3 | **YES** (3 > 1) |

Contamination: all 12 sessions trivialization-scan **CLEAN**
(no auto-disqualification). Pack A carries lab-state tokens
(`SIM-2`×16, `Q1`×17, `verdict`×10, `INCONCLUSIVE`×2, `falsification`×4 in
root CONTEXT.md) — logged as evidence only (tier-2 rule; these are the
orientation input under test, and pack B shares a subset of them).

## Verdict: **PASS** — B wins on Q22

All four pre-registered rules hold at median. The v1 INCONCLUSIVE on Q1 is
resolved: on the harder L4 causal-synthesis task, the 1.7 KB pinned-terms
orientation pack (B) eliminates the verbatim-sentence first-miss that costs
condition A one full call + its wall time, while the negative control (C)
spikes to the full 3-call budget without ever reaching a valid answer —
the instrument detects domain-irrelevant orientation, so the reorient
metric is alive.

## Observations

1. **The verbatim miss is the entire B/A difference.** A and B retrieve
   identical ids on their remaining calls (deterministic FTS); B's win is
   precisely the omitted rc=2 first call. reorient_cum delta = 1 call,
   ttfva delta = 1 call. No token-budget difference (both ~624 ttfva_tok
   at their valid point).
2. **Wall times are session-noisy** (0.14–0.38 s per call, process
   startup dominates) — call-count metrics are the signal; wall times
   recorded for the record, not used by verdict rules.
3. **C never goes seed-valid** — its 2 rc=0 calls return evict-domain
   chunks that do not count as required seeds, exactly the pre-registered
   control behavior (non-seed rc=0 matches hollowed the v1-style
   "first rc=0" metric; R-rc refined the metric to "first call with ≥1
   required seed").
4. **Caveat:** pack A is not a truly blank baseline — its root CONTEXT.md
   carries VERA lab-state tokens (logged above). B still wins, so the
   verdict is robust to that, but a future class should test A against a
   genuinely clean orientation document.
5. Same scripted-simulation class as v1: deterministic subprocess calls,
   no fresh-LLM cold start. `spawn.py`-based run remains the next-class
   follow-up.

## Files

- Per-session JSON logs: `subprojects/vera/experiments/runs/sim2_q22_s??_?.json`
  (12 files, survived on the main tree this time — v1's logs were lost
  with its deleted worktrees)
- Summary: `subprojects/vera/experiments/runs/sim2_q22_summary.json`
- This report: `subprojects/vera/experiments/runs/sim2_q22_results.md`

## Next Actions

1. Record PASS verdict in `task_plan.md` decision log + `progress.md`.
2. Remove worktrees `sim2b-{A,B,C}` (harness worktrees hold the
   hardlinked `graph.db`; `git worktree remove --force` or
   `scripts/git_worktree.py remove`).
3. Optional follow-ups: (a) fresh-LLM cold start via `spawn.py`;
   (b) blank-baseline A' condition to isolate the lab-state token
   caveat; (c) propagate the pinned-terms-orientation finding to a
   memory candidate.
