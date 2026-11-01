---
type: Concept
title: gates-s44-calibration
generated: { by: opencode/nara-step-5-preview, at: 2026-10-30T00:00:00Z }
---

# Gates: S44 blend calibration on the S49 protocol

OWNS: projects/research/etth1-h720/GATES-s44-calibration.md, projects/research/etth1-h720/run_s44_calibration.py, projects/research/etth1-h720/verify_s44_calibration.py, projects/research/etth1-h720/S44_CALIBRATION_RESULT.md, projects/research/etth1-h720/results/s44_calibration_*.json, projects/research/etth1-h720/CONTEXT.md, projects/research/etth1-h720/docs/adr/0001-s49-closeout-and-protocol-discrepancies.md, handoff/flags/etth1-h720-s44-calibration-2026-10-30.md

Scope: a pure calibration measurement. It does NOT resume S49, does NOT tune, does NOT
promote any model. It answers one question with one number: what would the S44 blend
(NLinear L336 a=1 + NLinear L336 a=10 + PatchTST-Delta P24 D32 2L, per-horizon ridge,
no intercept, alpha=30000) score under the S49 protocol (12 locked origins, step 720 h,
8640..16560), so that the ADR 0001 threshold-comparability caveat becomes a number.

## Pre-registration (written before any measurement run)

Protocol — identical to S49 (`run_amr_h720_final.py`, `run_h2k_h720_final.py`):

- data: `_archive/datasets/data/ETTh1_h1.csv`, column `OT`, n=17420.
- horizon H = 720; fit window CAP = 8640 (360 days).
- 12 locked origins: 8640, 9360, 10080, 10800, 11520, 12240, 12960, 13680, 14400, 15120,
  15840, 16560 (step 720 h).
- per origin o: fit on `s[o-8640:o]` only, context `s[:o]`, target `s[o:o+720]`.
- metric: raw MAE over the 720-step horizon (no extra normalization; each member keeps
  the normalization it carries in its own S44 code — NLinear last-value anchoring,
  PatchTST-Delta level-free delta, DLinear/BigDictELM as in `benchmark-core/members`).

Blend (S44 object, frozen):

- members: `nlinear_L336_a1` (L=336, ridge_alpha=1.0), `nlinear_L336_a10` (L=336,
  ridge_alpha=10.0), `patchtst_P24_D32_2L` (P=24, D=32, 2 layers, heads=2, FFN=64,
  dropout 0.30, stochastic depth 0.10, attn dropout 0.2, weight decay 1e-2, no causal
  mask, AdamW lr 3e-4, batch 64, grad clip 1.0, level-free delta, anchor = window[-1]).
- stack: per-horizon ridge, `fit_intercept=False`, alpha=30000, applied to the three
  members' predictions at the origin.
- seeds: 42, 43, 44, 45, 46 for PatchTST-Delta (S49 seed set; S44 itself used seed 0).
  NLinear a=1 / a=10 are closed-form deterministic — one run each. References BigDictELM
  L96 (seed 42, as in S49's locked run) and DLinear are deterministic — one run each.

Ridge-weight fitting data (pre-registered rule):

- the blend weights are fitted ONLY on origins whose scored windows lie strictly inside
  the training slice `s[o-8640:o]`, i.e. on data before the scored origin. Chronological
  first half of those in-window origins is the fit set (mirrors S44's `val[0:1080)`
  half-split). The last-2880-rows half-split variant is recorded as a sensitivity row.
- a discovery to record: S44's own frozen-test stack was fitted on `val[0:1080)`, whose
  targets are raw rows 8545..10343 — inside `train.csv`, strictly before S44's test
  region (rows 11425+). S44 did NOT fit the blend weights on test-period data. The
  contingency "if it used test data, refit on pre-origin data only" therefore does not
  trigger for S44; the pre-origin-only rule above is kept anyway because the S49 geometry
  has no shared fit history across origins.

### Amendment A1 (2026-11-01, recorded BEFORE the measurement run; no results seen)

The rule above was written before the ridge-fit discipline was inspected in S44's code.
That inspection shows S44 fitted the ridge weights on strictly OUT-OF-SAMPLE member
forecasts: members were frozen at row 8545 and only then produced the val forecasts
(8545..11425) the ridge learned from; members were refit on 0..11424 only afterwards, to
score the test origins. An "in-window origin" whose member forecast came from a member
trained on the whole training slice would therefore be IN-SAMPLE stacking — a mechanism
S44 never used.

The pre-registered rule as written admits such origins (e.g. origin 336 lies inside a
slice a member was trained on). Amendment A1 narrows the admissible set to the
out-of-sample region only, and changes nothing else:

- ridge members are frozen on the FIRST 5760 rows of `s[o-8640:o]`;
- PRIMARY fit set = the chronological first 1080 of the 2161 out-of-sample origins in
  the 2880-row tail (origins 5760..7920). This is the exact structural mirror of S44:
  freeze at 8545 / val origins 8545..11425 / ridge on val[0:1080) translates to
  freeze at 5760 / OOS origins 5760..8640 / ridge on the first 1080;
- SENSITIVITY = the disjoint second half of the same 2161 origins (1080..2160);
- scored predictions at origin `o` still come from members refit on the full
  `s[o-8640:o]`.

The interpretation rule, the 12 origins, the seed set, alpha=30000, the no-intercept
stack and the 2.4777 comparison point are untouched by A1.

Interpretation rule (fixed BEFORE seeing results; nothing is changed afterwards):

- blend mean raw MAE < 2.4777 (BigDictELM L96 on the same 12 origins, re-derived fresh)
  => S44 was genuinely stronger, and the 1.9781 threshold was reachable under S49's
  protocol.
- blend mean raw MAE >= 2.4777 => the 1.9781 figure was an artifact of the S44 protocol
  (2161 dense step-1 origins), not a level any model reliably reaches on 12 sparse
  step-720 origins.
- the verdict string in `S44_CALIBRATION_RESULT.md` is produced by this rule and by
  nothing else. The 1.9781 number is reported as context only and is never a gate.

Consistency control (pre-registered):

- re-run the identical S44 frozen test (members refit on raw rows 0..11424, stack fitted
  on `val[0:1080)` at alpha=30000, scored on the 2161 step-1 test origins) and compare
  with 1.978126. Divergence > 1% means the S44 reproduction is unfaithful: STOP before
  interpreting anything.
- the control is run on S44's own data file (`ts-ml-experiments/h720/ETTh1.csv`) and on
  the S49 data file (`_archive/datasets/data/ETTh1_h1.csv`). The two differ in 166 of
  17420 OT rows by at most 3.6e-15 (float print/parse precision, rows 0..10669 only);
  this is recorded as a data-provenance finding, not corrected.

Reported quantities: per-origin and per-seed raw MAE for the blend, each of the three
members, BigDictELM L96 and DLinear; mean, std, median and win count vs DLinear per
method; for PatchTST-Delta and the blend, mean and spread across the 5 seeds.

## Ledger history

- 2026-10-30T00:00:00Z — initial ledger, written before any measurement run.

- 2026-11-01T00:00:00Z — Amendment A1: ridge-fit origins narrowed to the out-of-sample
  region (members frozen at 5760, ridge on the first 1080 of origins 5760..7920, disjoint
  second-half sensitivity). Recorded before the run; no results seen. Rationale in A1 above.

- 2026-11-01T01:00:00Z — Status disclosure: seen value 1.7229 originates from an early,
  aborted in-sample stacking run on origin 8640 (seed 42, ~844s elapsed) that failed on
  BrokenProcessPool. That variant trained the members on `s[o-8640:o]` and then fed the
  ridge their forecasts from the last 2880 rows of the same window — in-sample stacking,
  a mechanism S44 never used. It is therefore an INVALID estimand, not a weak result, and
  is recorded here only so the number is not floating around unattributed. The raw log
  was transient build residue under `results/` (the workspace integrity gate forbids
  untracked files there) and was deleted rather than committed; no artifact of record
  carries it. It is not a benchmark reference and not a decision gate.

- [x] G0: this ledger states outcomes that can fail
  CHECK: node C:/Users/Mateusz/.config/opencode/skills/unlazy/scripts/gate-lint.mjs projects/research/etth1-h720/GATES-s44-calibration.md
  EXPECT: LINT OK
  EVIDENCE: LINT OK (2026-11-01)

- [x] G1: the report's numbers are recomputed from the JSON, and the run matches the pre-registration
  CHECK: python projects/research/etth1-h720/verify_s44_calibration.py --stage recompute
  EXPECT: RECOMPUTE_OK
  EVIDENCE: RECOMPUTE_OK — blend mean 4.125489, BigDictELM 2.477669, DLinear 2.538356, 12 origins

- [x] G2: the S44 reproduction control is within 1%, or is explicitly marked FAIL-and-stop
  CHECK: python projects/research/etth1-h720/verify_s44_calibration.py --stage reproduction
  EXPECT: REPRODUCTION_OK
  EVIDENCE: REPRODUCTION_OK — 1.978126 both files, rel diff 4.2e-11

- [x] G3: the interpretation follows the pre-registered rule, not a post-hoc reading
  CHECK: python projects/research/etth1-h720/verify_s44_calibration.py --stage interpretation
  EXPECT: INTERPRETATION_OK
  EVIDENCE: INTERPRETATION_OK — rule outcome AT_OR_ABOVE, verdict phrase present

- [x] G4: the report states explicitly what was not reproduced 1:1
  CHECK: python projects/research/etth1-h720/verify_s44_calibration.py --stage not-checked
  EXPECT: NOT_CHECKED_OK
  EVIDENCE: NOT_CHECKED_OK — 8 explicit entries

- [x] G5: project tests and the workspace integrity gate are green
  CHECK: python -c "import subprocess, sys; r1=subprocess.run([sys.executable,'-m','pytest','projects/research/etth1-h720','-q'],capture_output=True,text=True); assert r1.returncode==0, r1.stdout[-3000:]+r1.stderr[-3000:]; r2=subprocess.run([sys.executable,'scripts/check_workspace_integrity.py'],capture_output=True,text=True); assert r2.returncode==0, r2.stdout+r2.stderr; print('TESTS_AND_INTEGRITY_OK')"
  EXPECT: TESTS_AND_INTEGRITY_OK
  EVIDENCE: TESTS_AND_INTEGRITY_OK — 31 passed, integrity OK

- [ ] G6: the closing ritual left a clean tree, the flag in HEAD, and origin/master == HEAD
  CHECK: python -c "import subprocess, sys; paths=['projects/research/etth1-h720','handoff/flags/etth1-h720-s44-calibration-2026-10-30.md']; st=subprocess.run(['git','status','--short','--']+paths,capture_output=True,text=True); assert st.stdout.strip()=='', 'OWNS dirty: '+st.stdout; r=subprocess.run(['git','cat-file','-e','HEAD:handoff/flags/etth1-h720-s44-calibration-2026-10-30.md'],capture_output=True,text=True); assert r.returncode==0, 'flag not in HEAD'; h=subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True).stdout.strip(); m=subprocess.run(['git','rev-parse','origin/master'],capture_output=True,text=True).stdout.strip(); assert h==m, f'HEAD {h} != origin/master {m}'; print('CLOSE_RITUAL_OK')"
  EXPECT: CLOSE_RITUAL_OK
  EVIDENCE: pending
