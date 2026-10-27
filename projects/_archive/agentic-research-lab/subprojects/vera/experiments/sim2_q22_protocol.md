---
type: Concept
title: sim2_q22_protocol
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# SIM-2b Protocol — Q22 Cold-Start Follow-up (PRE-REGISTERED)

Date: 2026-09-25
Supersedes: none. SIM-2 v1 (Q1) verdict **INCONCLUSIVE stands as null** — Q1 was too
narrow; this run does NOT overwrite it (runbook rule). Q22 is a new pre-registered run.

## Why Q22

Q1 failed rules 3+4 because the task was too narrow for orientation packs to
differentiate on reorient time. Q22 is an L4 causal-synthesis question:

> "Causal chain: how does reorientation cost convert into performance loss for a
> fresh agent session?"

Target structure (all 4 items required for a VALID answer):
1. chain steps (reorientation → re-query overhead → degraded first-answer latency/tokens)
2. measurable proxies (reorient, ttfva, ttfva_tok)
3. intervention point (orientation pack / bounded-state layer)
4. falsification probe (irrelevant orientation should spike reorient)

Plus: each of items 1–3 must cite a resolvable chunk ID (item 4 cites the pack itself).

## Required seeds (verified pre-run)

| Seed | Pinned query that resolves it | Verified |
|---|---|---|
| `00_reflection_reorientation_cost` | `ask.py "reorientation cost"` | top match, tags incl. `reorientation-cost` |
| `01_workspace_rapid_understanding` | `ask.py "rapid understanding"` | match |
| Distractor `00_session_compaction_for_ai_agents` | `ask.py "session compaction"` | adjacent lever, different mechanism — appearance = no credit |

Verified pre-run property that the whole experiment hinges on:
**the verbatim Q22 question returns 0 FTS matches.** Pinned terms, not sentences (VERA B0).

## Conditions (same as SIM-2 v1)

| Cond | Orientation input |
|---|---|
| A | CONTEXT.md + 9 stage CONTEXTs (~43.9 KB) |
| B | `experiments/sim2_packB.md` only (1.7 KB) |
| C | `stages/05_evict/CONTEXT.md` (unrelated domain — negative control) |

## Query policies (frozen; these ARE the under-test variable)

| Cond | Query sequence (ask.py calls, in order) |
|---|---|
| A | 1. verbatim Q22 question → 2. `reorientation cost` → 3. `rapid understanding` |
| B | 1. `reorientation cost` → 2. `rapid understanding` |
| C | 1. `eviction stale memory` → 2. `memory rule evict gate` → 3. `promote candidate gate` |

A simulates an un-oriented agent (long verbatim first — the B0 failure mode B's pack
prevents). B simulates the pack's pinned-terms rule. C simulates an orientation to the
wrong domain: all three evict-domain queries are seed-free, so C never reaches a valid
answer — that is the spike. Pre-run probe (2026-09-25): C queries return
`rc=0`/`rc=2` with 0 required-seed matches (non-seed matches do not count valid).

## Metrics (refined pre-run 2026-09-25 — logged below; verdict rule stays frozen)

- **reorient_cum** (calls): number of `ask.py` calls up to and including the first
  SEED-VALID call — the first call whose results contain ≥1 required seed
  (`00_reflection_reorientation_cost` or `01_workspace_rapid_understanding`).
  If no call ever retrieves a required seed, reorient_cum = all calls.
  (Pre-run refinement R-rc: v1's "first ≥1 rc-match" definition hollowed the
  C control — C's `eviction stale memory` returns rc=0 with non-seed matches,
  making C cum = 1 and killing the rule-4 spike by construction. "≥1 required
  seed" is the pre-registered fix; C never succeeds, so C cum = 3 > B cum = 1.)
- **ttfva** (calls): first call index k where the cumulative union of ids
  retrieved across calls[0..k] contains BOTH required seeds; "NA" if never
  (pre-run refinement R-tt: single-call ttfva mis-measured — B's union
  reaches both seeds by call 2, not 1; cumulative union is the faithful
  "time to first valid answer").
- **ungrounded**: target items 1–3 lacking their required seed in the
  cumulative retrieved set (item 1 ← seed1, item 2 ← seed1, item 3 ← seed2).
- **contaminated**: pre-flight — pack text may not carry **task-trivializing**
  content: reproduced seed-chunk content or the stated causal-chain answer to
  Q22. Lab-state pointers (SIM-2/Q1/Q22 mentions, verdict metadata, routing)
  are the under-test orientation input, NOT contamination — voiding pack A on
  them would also void pack B (the treatment arm), which is incoherent.
  Two-tier check (pre-run refinement R-ct): trivialization probes hit =
  auto-disqualify session; lab-state token hits = logged evidence, judged
  clean. All trivialization probes verified CLEAN against pack sets A/B/C
  pre-run (2026-09-25): pack A's stage CONTEXTs are workspace routing,
  pack B is the 1.7 KB treatment, pack C is evict-domain only.

## Run matrix (v1 follow-up #2: increase sample size)

5 sessions per condition A and B, 2 for C; sessions interleaved
(A1 B1 A2 B2 C1 A3 B3 C2 A4 B4 A5 B5) to spread machine warm-state across
conditions. Isolation: one git worktree per **condition**
(`sim2b-A`, `sim2b-B`, `sim2b-C`); per-session JSON logs written to the main
tree `subprojects/vera/experiments/runs/SIM2b_q22_<cond>_<n>.json` (v1 flaw:
its logs lived in deleted worktrees and were lost).

Pre-run refinement R-db: `knowledge/graph/graph.db` (713 MB) is gitignored, so
`git worktree add` leaves each worktree without it and every `ask.py` call
exits "graph.db missing". After worktree creation the harness hardlinks
(`os.link`) the main-tree DB into each worktree (zero extra space; read-only,
sequential calls). Without this step the run is void.

## Verdict rule (PRE-REGISTERED — do not edit after first results land)

B wins on Q22 iff, at median across its 5 sessions:
1. **reorient_cum** B ≤ A
2. **ttfva** B ≤ A
3. **ungrounded** B = A
4. **reorient_cum** C > B (control spike observed — instrument alive)

Otherwise **INCONCLUSIVE**, log which rule(s) failed. Q1 verdict remains null.

## Method note

Same scripted-simulation class as SIM-2 v1 (real timed `ask.py` subprocess calls,
query policy = the orientation effect). v2 fixes: sample 3→5/condition, cumulative
reorient incl. failed calls, surviving logs, 1 worktree per condition. A true fresh-LLM
cold start would use `spawn.py`; that is the next-class follow-up, not this run.
