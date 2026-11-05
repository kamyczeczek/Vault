---
type: Concept
title: sim2_runbook
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# SIM-2 Cold-Start Runbook (pack A vs pack B, clean-session protocol)

Purpose: measure ease-of-understanding → performance under **clean conditions**. Any session
carrying prior study context is disqualified and the run is logged as `contaminated: true`.

## Isolation (hard requirements)

- Fresh session, launched by `python pipeline/06_reflect/spawn.py` (or an equivalent isolated
  agent) so no VERA history is inherited; run inside its own git worktree
  (`python scripts/git_worktree.py create --name sim2-<cond>`) to avoid mutating shared state.
- The session's ONLY inputs: this runbook's task block + the condition's orientation pack.
  It may use `ask.py` (the packs both route to it) — that is part of what's measured.
- Pre-flight contamination check: before the task, the session must list every VERA
  artifact name it knows without being told. Any hit beyond "ask.py / quality_check.py"
  (lab-wide primitives) → `contaminated: true`, discard run.

## Conditions

| Cond | Orientation input | Size |
|------|-------------------|------|
| A | CONTEXT.md + all 9 stage CONTEXT.md files | ~43.9 KB |
| B | `experiments/sim2_packB.md` only | 1.7 KB |
| C (negative control) | a random unrelated stage CONTEXT (pick `stages/05_evict/CONTEXT.md` unseeded) — reorientation cost should spike; if it doesn't, the instrument is broken | n/a |

## Task block (identical for all sessions)

```
Answer question Q1, verbatim:
"What trust tiers does this lab use for evidence, and what does tier 3 mean?"
Deliver the answer contract sections 4–7 only (sources, claims, evidence,
contradictory/limiting). Your answer is VALID when all of:
  (1) the 4 tiers are enumerated with correct labels,
  (2) tier 3 is defined as attested computation / execution trace,
  (3) ≥1 corpus citation is ask.py-resolvable AND ≥1 workspace citation is named,
  (4) no claim appears without its source line.
```

## Metrics (log to `runs/SIM2_<cond>_<n>.md`)

| Metric | Definition | Tool |
|--------|-----------|------|
| ttfva | tool calls from session start to first VALID answer | session log |
| ttfva_tok | tokens to first valid answer | session log |
| ungrounded | claims in final answer lacking a resolvable source / source line | grep + ask.py resolve |
| reorient | wall time to first successful `ask.py` call with ≥1 match | timestamps |

## Run matrix

- 3 sessions per condition (A, B) + 1 for C; sessions are independent (fresh spawn each).
- Record per session: condition, ttfva, ttfva_tok, ungrounded, reorient, contamination check,
  session log path. Table → `reports/sim2_results.md`.

## Verdict rule (pre-registered, do not edit after first results land)

B **wins** iff, at the median across its 3 sessions:
- ttfva ≤ 0.7 × A-median AND ungrounded = A-ungrounded (no integrity loss) AND reorient ≤ A;
- C-median reorient > B-median (control spike observed).
Otherwise: INCONCLUSIVE, log which condition of the rule failed and the follow-up design
(e.g., raise task to Q22 if Q1 is too narrow — but record that the Q1 verdict is null,
not overwrite it).

## Anti-contamination ledger

Append every disqualified run to `runs/SIM2_disqualified.md` with the contamination evidence.
A discarded run is data (it proves the protocol), never silent.
