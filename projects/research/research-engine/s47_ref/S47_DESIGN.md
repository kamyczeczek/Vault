---
type: Concept
title: S47_DESIGN
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:26Z }
---

# S47 — Diverse Mini Suite (6-task fast + cross-domain probe)

**Status:** Protocol amended before corrected rerun (2026-10-25); Q9-Q11 decided
2026-10-26. Rerun complete; diagnostic only because the five origins had already
been exposed.

## Goal
Test whether anchored-wavelet methods (S46-style) have *any* cross-domain signal when ETTh1 H720 is saturated, and provide a **diverse but extremely fast** harness for future frontier bets. ETTh1 alone filters every wavelet/ELM variant (H2, S35, S46 all REJECTED with singleton >2.90). A 6-task mini-suite (ETTh1 + 5 synthetic domains emulating FEv-bench-mini / fev/Monash coverage) gives a cheap `≈2–5 min` CPU probe vs S46's `6.5h` full ETTh1 rolling.

## Suite
6 tasks, each `train=2000, W=5 rolling origins stride H, H variable` (matches fev-bench `W≤20` small-dataset protocol). Metric: **per-task MAE**, aggregate **mean rank + mean MAE normalized by task std**. Runtime reported per-task.

| Task | Domain analogue | Generator | H | Freq |
|------|-----------------|-----------|---|------|
| 1 ETTh1-like | ETT (transformer temp) | real ETTh1 OT slice (reuse `data.py` OT) | 96 | hourly |
| 2 Seasonal | Electricity (strong daily/weekly) | `sin(2πt/24)+0.5 sin(2πt/168)+AR1 noise` | 48 | hourly |
| 3 Trending | ExchangeRate-like (random walk) | `cumsum N(0,1) + weak AR` | 48 | daily |
| 4 Spiky | Traffic/Weather exogenous | `AR(2) + sparse spikes + AR noise` | 48 | 10-min |
| 5 Mean-reverting | Illness weekly | `OU process + seasonal` | 24 | weekly |
| 6 Multi-scale | fev mixed | `sum of 3 sines (periods 12,48,168) + noise` | 96 | hourly |

Fallback: if `fev` datasets unreachable offline, use the 6 synthetic generators above with fixed seed 0. Synthetic is deterministic and proves harness plumbing; `fev` YAMLs can be swapped in later without harness change.

## Members
`M=5` pooled baseline (S44-style without PatchTST retrain cost) + 2 contrasts:

- `nlinear_L96_a1`, `nlinear_L336_a1`, `nlinear_L96_a10` (linear anchors)
- `rff_rbf_h64` (fast non-linear ELM-style, no training beyond ridge)
- `subband_expert` group = `4` SWT subband Ridge experts `cA3/d3/d2/d1` (S46-intelligent-merge idea, no pooling, per-horizon Ridge directly on subband)

Comparisons:
- `Pool A (baseline)`: 5 linear/RFF
- `Pool B (+subband-experts)`: 5 + 4 experts = 9
- `Pool C (+pooled-ELM S46-style)`: 5 + 1 pooled F=12 ELM-Ridge = 6  (sanity: should lose per S46)

Protocol amendment (2026-10-25, before the corrected run): use a fixed trailing
`train_window=2000` at every origin, fitting each member once per origin and
forecasting the full horizon. The stacker is per-horizon Ridge without an
intercept and with fixed `alpha=3000` (`SEARCH_ALPHA`); it is not tuned on the
confirmation origins. Fast path remains `W=5`, not 2161 origins.

## Open-question decisions (Q9-Q11)

**Q9 — fit window: fixed 2000 or expanding?** Decision rule, written before the
sensitivity numbers were read: the choice counts as robust only if both policies
agree on the locked candidate *and* on all three select gates. If they agree,
`fixed 2000` stands (sample size constant, only the target window moves) and
`expanding` is recorded as a sensitivity check. If they disagree, the gate verdict

Note: the rule text, the expanding results and the comparison script landed in the same commit (0b08562), so the claim "rule written before reading the numbers" is an author assertion, not a git-verifiable fact.
is policy-dependent — G3 is then too fragile to lock anything and this suite
promotes nothing, which leaves the `benchmark-core` evaluation as the only path.

Run: `python s47_ref/rolling_arm.py --window expanding` writes
`results_s47_expanding.json` + `harness_expanding.log`; the default stays
`--window fixed`, so `results_s47.json` is untouched. Normalization uses the
initial 2000-point window std under both policies, so the policy moves the fit
sample (numerator) and not the task scale (denominator).

Result (2026-10-26, both policies complete): identical locked choice (B) and
identical G1/G2/G3; **0/6 per-task winners flipped**. Mean select normalized MAE
A=1.084936 / B=1.021247 fixed vs A=1.085858 / B=1.022560 expanding; mean rank
B=1.500 in both; B wins 4/6 in both; post-lock G4 diagnostic gap -0.077304 vs
-0.077315. Per-task deltas are at most 0.0076 normalized and dominated by ETTh1
(+0.0075 on B); the synthetic tasks move by <= 0.0004.
`python s47_ref/compare_window_policies.py` reproduces the comparison and exits
0. **Decision: fixed 2000 stands as the protocol; expanding is a recorded
sensitivity check, not the protocol.** The noise-level margins on `spiky_H48`
and `ou_H24` (~1e-5) survive this test unchanged, so they remain a separate
risk that only an unseen-task evaluation can settle.

**Q10 — reuse of the confirmation origins?** No. The pre-correction report scored
all five origins, so the last two cannot confirm anything in this run; the suite
is retired for confirmation purposes and a promotion decision needs new origins
or new tasks in `benchmark-core`.

**Q11 — the `<5 min` runtime target?** Measured per refit policy, reported, never
a gate: 26.7 s fixed / 26.2 s expanding on the 2026-10-26 run, 55.2 s for the
colder recorded rerun. The target holds.

## Gates (binding screening gates, candidate pool B vs pool A)
- Origins are `2000 + i*H`, `i=0..4`; the first three are selection origins and
  the last two are post-lock confirmation origins.
- For a selection-origin score, Ridge weights are fit on the other two
  selection origins only. For a confirmation-origin score, weights are fit on
  all three selection origins. Fit and score origins must be disjoint.
- Task scale is the population standard deviation of the initial 2000-point
  training window. No validation or confirmation targets enter normalization.
- **G1 (select)**: mean task-normalized MAE(B) improves on A by at least 0.005.
- **G2 (select)**: B's mean rank is better than A's mean rank across pools A/B/C,
  ranking each task by select-only normalized MAE and averaging ranks by task.
- **G3 (select)**: B beats A on at least 4/6 tasks using select-only normalized
  MAE.
- **G4 (post-lock diagnostic)**: B's mean task-normalized MAE is below A's and
  B beats A on at least 4/6 tasks on the two remaining origins.

G1-G3 use select origins only; the harness locks the aggregate A/B decision
before it computes G4. **This historical W=5 set is already exposed:** the
pre-correction report scored all five origins. Therefore this amendment's G4
cannot be described as untouched confirmation and no result from this rerun
advances a candidate. A new, unexposed evaluation in `benchmark-core` is
required before any promotion decision.

## Harness
`rolling_arm.py`: generates/loads 6 tasks and scores pools A/B/C. The result
stores select-only raw and normalized metrics separately from post-lock
diagnostics in `results_s47.json` and `harness.log`. ETTh1 uses its H96 slice
with W=5; S-47 remains a suite probe, not a promotion attempt on H720. Runtime
is reported, not a gate.

## If offline (fev unreachable)
S-47 keeps five fixed-seed synthetic tasks plus ETTh1, independent of FEV
availability. `benchmark-core` supplies the authoritative real-benchmark
evaluation before model promotion. The original `<5 min` target is measured, not
assumed: 26-56 s per window policy (Q11).
