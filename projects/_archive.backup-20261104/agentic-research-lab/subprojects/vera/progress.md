---
type: Concept
title: progress
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Progress: VERA (Verification-Enhanced Research Agents)

## 2026-09-25 23:15 — SIM-2b Q22 run: verdict PASS (B wins on Q22)
- Pre-registered protocol + harness committed (`4b40b7b` [sim2]); 5 pre-run refinements logged in protocol (R-rc seed-valid reorient_cum — v1-style "first rc=0" hollowed the C control; R-tt cumulative-union ttfva; R-c3 C = 3 evict-domain queries; R-ct two-tier contamination: trivialization auto-disqualify / lab-state logged-only; R-db graph.db hardlink into worktrees — 713 MB DB is gitignored, without attach every ask.py call exits "graph.db missing").
- Tooling fixes on the way: `git_worktree.py` used `--branch` (git 2.54 wants `-b`, `cae258d`); `.gitignore` v1 pattern `sim2-*` missed `sim2b-*` (main tree stayed dirty, blocked `create`; widened to `.worktrees/`, `199683e`).
- Run: 12 sessions interleaved 5A/5B/2C in worktrees `sim2b-{A,B,C}`; deterministic FTS — every session per-condition reproducible. A: verbatim Q22 rc=2 (B0 miss) → seed-valid at call 2, both seeds by call 3. B: seed-valid at call 1, both by call 2. C: never seed-valid (2 evict rc=0 non-seed + 1 rc=2) → full 3-call budget.
- Verdict: all 4 pre-registered rules pass at median (reorient_cum B=1≤A=2; ttfva B=2≤A=3; ungrounded B=1=A=1; C=3>B=1). 0 trivialization hits. Caveats logged in runs/sim2_q22_results.md: pack A carries VERA lab-state tokens (SIM-2×16, Q1×17, INCONCLUSIVE×2 in root CONTEXT.md) — tier-2 evidence, verdict robust; scripted-simulation class (fresh-LLM `spawn.py` run = next class).
- Logs survived on main tree (`runs/sim2_q22_s??_*.json` ×12 + summary) — v1 flaw (logs in deleted worktrees) closed. Worktrees + branches removed post-run.
- Next: commit results + docs; optional follow-ups in sim2_q22_results.md (blank-baseline A', spawn.py cold start, propagate pinned-terms finding to memory candidate).

## 2026-09-25 21:55 — Lab closeout: F meta-findings promoted, meta-learning propagated, report updated
- F pipeline run on last untested candidate: `vera-expf-final-001` pass_falsification (F1 partial, G=1.0 C=1.0 V=0.67; run EXPF_adversarial_falsification_20260925_215106.json). All 3 meta-candidates now F-clean.
- Review-gate before/after pairs logged for rev-001/rev-002/final-001 (F-run measured scores; audit drift tracked by W7 sidecar, not gate log).
- Actions rewritten chunk-keyword-grounded (auditor zero-keyword gotcha, 2nd recurrence — same class as 001/004 fix); all 3 promoted experimental→accepted, post-promotion audits PASS (score 1.0). memory.md now 12 accepted rules.
- apply_meta_learning.py: 3 new rules appended to stages/04_reflect/CONTEXT.md; 15/15 pre/post gates green; baseline updated.
- Reachability seeds for the 3 new rules: UNREACHABLE on frozen corpus (meta-concept not ingested) — documented, seeds not added (12-seed gate stays green; re-add after next corpus ingest + graph rebuild).
- Standing gates: check_promotion 7/7, continuous_calibration 12 rules 0 stale, evict_stale dry-run 0 evict, audit_workspace all PASS.
- Final lab report updated: Experiment F + meta-findings rows; 7-insight list; end-to-end conclusion.
- Next: commit closeout batch; after any future ingest+rebuild, re-add the 3 pending reachability seeds and rerun check_reachability.py.

## 2026-09-24 22:20 — check_manifest divergence closed + residue commit + Q5/Q6 parity row (Goose)
- check_manifest divergence ROOT CAUSE (not args/CWD): on-disk manifest still carried the freshness-probe's long-key row ("VERA DB-1 experiment...") while the probe chunk had been `git checkout`-restored to committed bytes (source `db1_freshness_probe.md`) → phantom + untraced rows → direct CLI exit 2; the earlier quality_check.py PASS was transient state. One `--write` healed the manifest to HEAD state; read-only PASSes; fix committed with residue batch.
- Graph re-pinned `44172cafee34` (10,364 nodes, 1,247,343 edges) via build_graph.py; 15/15 gates green; residue committed 126898a (09-23 Braintrust re-ingest, ts_discovery deletion, zero-state reflection + .gitkeep, CLAUDE.md jCodeMunch trim).
- ingest.py verdict one-liner landed and committed 0399afa: `[ingest] manifest: PASS (rebuilt + post-write re-verified)` / stderr FAIL line; probe-defect class from the freshness probe is structurally closed (post-write re-verification).
- **DB-1 parity row (item c) MEASURED** via new `db1_parity_row.py` (pinned pools through the fixed gateway, 0 full-file reads):
  - Q5 v3 pool: **3/4** pool-level recall (both modes; fast 2,246 est tok) → parity MET vs D0 ~2/4–3/4 @ 1.4K; miss = `00_reflection_reorientation_cost` (no pool query carries "reorientation" — pool ceiling).
  - Q6 v2 pool: **1/2 strict, 2/2 source-level** — pool returned `00_00_` (part 1/4) for seeded `02_00_` (part 3/4); new finding **DB1-F3 part-sibling displacement** (lexical ranking, not the gateway — ask.py alone ranks identically).
  - Verdict upgraded: **D1 ADOPTED for L1–L2 pinned-pool retrieval via the gateway**; NOT for multi-seed L3–L5 until D7 spec'd into E-suite + Q6 pin v3.
- E-suite candidate defects D6 (same-source double citation) + D7 (part-sibling displacement) added to injection_test.md.
- Q6 pin upgraded to v3 ("software factory machine gate proof receipt merge gate" — part-3/4-specific, verified 02_00 ranks #1 via ask.py); parity harness re-measured → Q6 pool now **2/2 strict** (both modes); DB-1 verdict line updated: D1 ADOPTED for L1–L2 pinned-pool retrieval, DB1-F3 closed at pin layer, D7 stays E-suite queue.
- Next: E-suite build (50 planted defects, 5×10 randomized positions, pre-registered D7 scoring policy); two-rater inter-rater log debt; L3–L5 parity rows; SIM-2 cold-start in a FRESH session (self-contamination rule blocks in-session execution).

## 2026-09-24 19:00 — Goose (this session)
- Created subprojects/vera/ structure: task_plan.md, gates.md, progress.md, findings.md
- Wrote benchmark spec (20 questions, 5 difficulty levels, seed/distractor placeholders to annotate)
- Wrote experiments/baseline.md (pinned B0 config + runbook + determinism rules)
- Wrote experiments/injection_test.md (5 defect types, 5 runner configs A–E, passing rule)
- Wrote metrics/scorecard.md (7 dimensions, negative controls, verdict format)
- Wrote metrics/claim_schema.md (canonical JSONL claim row + invariants)
- Added VERA V-N1 gate to root GATES.md
- Next: annotate benchmark seeds/distractors with real chunk IDs (V1 research ticket); first B0 run; pin fingerprint

## 2026-09-24 19:08 — V1 Annotation (Goose)
- V1 PASS: 20/20 questions annotated with 24 verified chunk IDs + workspace markers; log in reports/seed_annotation.md
- Gaps found: Q17 has no corpus-size-degradation chunk (coverage gap by design of L5); 01_new_markdown_file carries eval content under boilerplate title; 365_ vs 240_ Book of Why chunks suggest duplicate ingestion
- Next: first B0 run on stable subset (Q1, Q13–Q16); pin fingerprint 05bc79e4b41e into experiments/baseline.md

## 2026-09-24 20:10 — VERA Phase 1 complete (Goose)
- L1 set finished: Q2, Q3, Q4 B0.1 runs (+10 claims); costs.jsonl now 10 rows
- Scorecard instrumented: metrics/tools/score_b01.py → dims 1/3/7 table in reports/B0.1_phase1.md; distractor-only negative control green; invariant caught 2 invalid direct claims (fixed via workspace: namespace)
- Reproducibility: Q13 rerun → 3/3 direct+inferred claims hash-stable, novel claim drifted (expected); query layer found under-determined → B0.2 addendum (pin query terms in benchmark file)
- **VERA Phase 1 complete: V1–V5 + V-N1 all green**
- Next: B0.2 pinning pass; L2/L3 runs; Experiment A; eviction check on 00_/01_ duplicate pairs

- Gated commit `2c4dc2a` [pipeline-vera] closed the 09-23 pipeline batch + all VERA work; untracked remainder = 0
- **Hook repaired:** `.git/hooks/pre-commit` shebang (`env python3`) hit the Windows app-install alias → every commit failed; replaced with a sh wrapper invoking the venv interpreter explicitly (`pre-commit.py` holds the gate logic). Pre-commit gate re-armed and passed on 2c4dc2a
- Triage tickets owed: (1) `ingest.py` transient MANIFEST FAIL misreport — one-line verdict fix; (2) 10 root scratch scripts + `INBOX_archive/` now gitignored — delete-or-adopt decision is the researcher's; (3) two-rater inter-rater log for gate-ablation results
- Next: P2-2 SIM-2 pack B; P2-4 Q21–Q23 annotation; gateway per-kind limit fix

## 2026-09-24 22:05 — check_manifest divergence RESOLVED + graph re-pin + residue cleanup (Goose)
- Root cause of the 21:45 "PASS vs FAIL" divergence: NOT an args/CWD difference between quality_check.py and the CLI. Both invoke the identical read-only path. The on-disk manifest still carried a long-key row from the freshness-probe `--write` ("VERA DB-1 experiment, 2026-09-24 — ..." raw, which does not exist) while the probe chunk had been restored to committed bytes (`git checkout --`), which declares `source: "db1_freshness_probe.md"`. So read-only mode found: phantom long-key row + untraced committed row → exit 2. The earlier quality_check.py PASS was a transient state (manifest not yet in this split state).
- Fix confirmed end-to-end: `check_manifest.py --write` now regenerates + re-verifies against the post-write state and exits 0 when healed. After one `--write`, on-disk manifest == HEAD (194 rows, staleness []), read-only PASSes. The 21:45 fix is ready to commit.
- Graph was stale vs. corpus after the clobber/restore of the probe chunk: rebuilt via `build_graph.py` → fingerprint **44172cafee34** (10,364 nodes, 1,247,343 edges); GRAPH-DIGEST.md + generation.json updated; all 15 gates green.
- Residue review completed: "New Markdown File" re-ingest (SQL talk → Braintrust evals-maturity talk; raw + 00_/01_ part-split chunks) kept; ts_discovery subproject deletion kept (superseded, restorable from 93ede16); reflection candidates/digests at zero state (gates consistent); CLAUDE.md jCodeMunch mention trimmed (tooling not installed in this workspace), Goose Principle kept.
- Next: commit residue + fix (agent_commit.py); ingest.py verdict one-liner; Q5/Q6 parity row to close DB-1; SIM-2 cold-start in a FRESH session (self-contamination rule).

## 2026-09-24 21:45 — check_manifest verdict work (RESOLVED at 22:05, Goose)
- `--write` re-verification added to scripts/check_manifest.py (post-write load + re-verify; exit 0 when healed) — fix is in the file but NOT committed
- DIVERGENCE to investigate: `python scripts/check_manifest.py` (direct, no args) now exits 2 / verdict FAIL, while `quality_check.py`'s manifest gate PASSES (194 rows both sides, staleness []) — likely env/path/args difference between the two invocation paths; quality_check may pass `--json` or run from a different CWD
- Test residue: I clobbered + restored `00_db1_freshness_probe.md` during testing (content identical to committed version — verify with git diff); graph rebuilt to fingerprint c450a12a8572 (10,364 nodes)
- Next session: `git diff scripts/check_manifest.py` → reproduce both invocation paths → commit the fix only when both agree; then Q5/Q6 parity row, SIM-2 execution, E-suite

## 2026-09-24 21:40 — Gateway per-kind fix (DB1-F2) (Goose)
- context_gateway.py: selection loop now reserves 3 per-kind corpus slots before the shared token budget (verified: Q5 pool keeps all 3 corpus rows + lessons)
- Q5 pinned_query → v3 (3-query pool); "agent memory hierarchies" verified to surface the missing seed; Q5 recall floor now ≥2/4
- DB1_arms.md follow-up marked RESOLVED (a+b), parity row (c) owed in next L2-runs session; hybrid index deferred
- Next: commit; SIM-2 runbook execution in fresh session; ingest.py one-liner

## 2026-09-24 21:30 — SIM-2 runbook (Goose)
- Wrote experiments/sim2_runbook.md: clean-session protocol (spawn.py isolation + worktree), conditions A/B + negative control C, 4 pre-registered metrics (ttfva, ttfva_tok, ungrounded, reorient), 3+3+1 run matrix, verdict rule (B wins at ≤0.7× A-median ttfva with no integrity loss), anti-contamination ledger (discarded runs are data)
- Chose runbook over in-session pilot per researcher: prior context contaminates exactly the variable SIM-2 measures
- Next: execute runbook in a fresh session; gateway per-kind limit fix; ingest.py one-liner

## 2026-09-24 21:15 — Eviction pass: EVICTION NOT NEEDED (Goose)
- Ran metrics/tools/find_duplicate_chunks.py over all 10,364 chunks: 0 exact-hash duplicates; 85 multi-member suffix groups
- Title inspection RETRACTS the "duplicate-ingestion" finding: 00_06/01_06 = parts 1/2 + 2/2; 00_07/01_07 same; bend2 same; 240_/365_ Book of Why = parts 241/386 and 366/386 of one 386-part source — all legitimate part-splits
- Records corrected in place: seed_annotation.md (correction appended), Q4 claims (c04 superseding claim), Q4 answer (superseded marker); originals preserved per evidence-discipline
- Lesson logged: single-title reads without part numbers produced the false alarm; find_duplicate_chunks.py stays as the standing maintenance tool
- Next: SIM-2 cold-start run; gateway per-kind limit fix; ingest.py verdict one-liner

## 2026-09-24 21:10 — Commit + P2-2/P2-4 (Goose)
- Gated commit 2c4dc2a [pipeline-vera]: 09-23 pipeline batch + all VERA work + DB-1 probe chunk; untracked remainder 0
- Pre-commit hook repaired (was silently broken: `env python3` shebang → Windows app-install alias; all prior commits skipped the gate); sh wrapper + explicit venv interpreter; gate verified on 2c4dc2a
- Triage tickets: ingest.py transient MANIFEST FAIL misreport (one line); scratch scripts + INBOX_archive gitignored pending delete-or-adopt; two-rater inter-rater log owed
- P2-4: Q21–Q23 appended to benchmark (verified seeds, pinned queries; 3rd 00_/01_ duplicate pair — bend2 — confirmed)
- P2-2: SIM-2 orientation pack B written (experiments/sim2_packB.md, 1.7 KB; 96% smaller than pack A's 43.9 KB)
- All P2 spec tickets green; remaining: SIM-2 cold-start run, gateway per-kind limit fix, formal E-suite
- Next: SIM-2 cold-start (fresh session, pack B vs A on Q1); then gateway fix

## 2026-09-24 20:30 — DB-1 arms + freshness probe (Goose)
- D0 vs D1 measured on Q1/Q5 (runs/DB1_arms.md + db1_d1_harness.py): D1 saves ~35–45% tokens + 0 full-file reads; verbatim-question failure reproduced through gateway (DB1-F1); multi-seed recall parity NOT met (budget truncation, DB1-F2)
- Verdict: D1 conditional — adopted for single-seed L1 + session-fused context; follow-up gateway fix spec'd (per-kind limit, pinned-query pairing)
- Freshness probe executed through the real pipeline: INBOX → ingest → build (fingerprint re-pinned 679a4aa15608) → watch → ask.py visible in 1 call; 0 stale-read incidents; found a new probe-defect class: ingest.py misreports its own successful run as MANIFEST FAIL (self-heals; one-line fix ticket owed)
- Next: P2-2 SIM-2 pack B; P2-4 Q21–Q23 annotation; gateway limit fix; ingest.py verdict fix; gated commit

## 2026-09-24 20:20 — L4 Gate Ablation (Goose)
- Closed the S1-vs-S0 verdict: runs/GATE_ABLATION_Q13Q14.md — gate set is difficulty-tier dependent (S1 on L1–L2, S0 on L3–L5); P13 (D4) + P14 (D2) pre-planted defects both caught by grounding+spot-check, query-drift only by rerun diff
- Task plan decision log updated (5 new entries incl. two-rater debt)
- Next: P2-2 (SIM-2 pack B), P2-4 (Q21–Q23 annotation), DB-1 arms; then gated commit

## 2026-09-24 20:10 — SIM-1 first results + B0.2 pinning (Goose)
- B0.2 pinning pass: Q2 (v2 "session compaction"), Q4, Q5 (v2), Q6 pinned in QUESTIONS.md; B0.2 addendum in baseline.md. Pinning = biggest recall lift yet: Q2/Q4/Q5 0.00 → 0.33–1.00
- SIM-1 arms executed on 6-question task set (S0=B0.1 protocol, S1=B0.2+single grounding gate, S2=B0.2 no-gate): arm log in runs/SIM1_arms.md, S2 claims in runs/SIM1_S2_claims.jsonl, 9 new cost rows
- Verdicts: S1 beats S2 (integrity: 2 defects caught vs 0; cost +43%) — external grounding gate is load-bearing, confirming the memory.md rule with evidence. S1 vs S0 INCONCLUSIVE pending per-gate ablation
- P2-1 + P2-3 closed; remaining: P2-2 (distilled orientation pack for SIM-2), P2-4 (Q21–Q23 annotation)
- Next: gate-by-gate ablation on Q13/Q14 (where gates are most likely load-bearing); SIM-2 pack B; DB-1 D0/D1 arms

## 2026-09-24 19:43 — Phase 2 direction (Goose)
- Researcher set new direction: simplicity + understandability as performance drivers; merge workflow with the graph database
- Wrote experiments/phase2_simplicity_db.md: SIM-1 (simplicity ablation, S0/S1/S2 arms), SIM-2 (cold-start orientation pack A/B), DB-1 (single-graph read path via context_gateway, with freshness probe)
- Source map grounded in corpus: karpathy minimalism, bend2, 03_perf, 00_reflection_reorientation_cost, 00_graph_database_architectural_reflection
- Reordered task_plan phases (Phase 2 = simplicity, Phase 3 = DB, Phase 4 = retrieval/verification experiments); added gates P2-1…P2-4; Q21–Q23 benchmark seeds spec'd
- Note: lab already has knowledge/graph/context_gateway.py — DB-1 is about routing the workflow THROUGH it, not building it
- L1 set finished: Q2, Q3, Q4 B0.1 runs (+10 claims); costs.jsonl now 10 rows
- Scorecard instrumented: metrics/tools/score_b01.py → dims 1/3/7 table in reports/B0.1_phase1.md; distractor-only negative control green; invariant caught 2 invalid direct claims (fixed via workspace: namespace)
- Reproducibility: Q13 rerun → 3/3 direct+inferred claims hash-stable, novel claim drifted (expected); query layer found under-determined → B0.2 addendum (pin query terms in benchmark file)
- **VERA Phase 1 complete: V1–V5 + V-N1 all green**
- Next: B0.2 pinning pass; L2/L3 runs; Experiment A; eviction check on 00_/01_ duplicate pairs

- B0 verbatim queries returned 0 matches on long-form questions (also with --recall): and-term ranking requires overlapping vocabulary; kept as floor data in costs.jsonl
- Defined B0.1 (core-terms query_form, one decomposition step, no iteration) — config change logged per determinism rule; addendum in experiments/baseline.md
- Completed B0.1 runs on stable subset: Q1, Q13, Q14, Q15, Q16 → runs/Q*_B0.1.md + claims jsonl (17 claims) + 7 cost rows
- V2 and V4 marked done in gates.md (V4 addendum: `workspace:` source namespace added to claim schema)
- Study findings logged: B0 verbatim = zero coverage; systematic double-ingestion (00_06/01_06 pairs); ask.py has --recall/--expand options not used by B0.1
- Next: rerun stable subset for V-N1 diff; annotate distractor-only negative control; run cost curves for L1 set
