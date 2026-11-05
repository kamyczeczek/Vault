---
type: Concept
title: findings
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# H=720 ETTh1 Forecasting — Research Findings & Future Experiment Directions

**Project**: `.` (univariate OT, H=720, ETTh1)
**Stage**: 02_research (read-only commission; findings only — no design commitments)
**Date**: 2026-09-02. All URLs fetched this session. All project numbers verified against files on disk this session.

---

## Current-State Grounding

### Protocol (the locked evaluation surface)

- **Task**: univariate forecasting of the OT (oil temperature) column of ETTh1, horizon H=720 (30 days ahead), direct multi-step (one `predict()` emits all 720 values). Source: `./CONTEXT.md` (leaderboard header), `./config.json` (`"features": "S"`, `"mode": "univariate"`, `"horizons": [720]`, `"input_length": 96`).
- **Data**: raw `ETTh1.csv`, 17,420 hourly rows (2016-07-01 → 2018-06-26), gapless. Source: `./CONTEXT.md` §Data processing pipeline, `./data.py` (`EXPECTED_ROWS = 17_420`).
- **Split** (`./data.py`, constants `TRAIN_ROWS=8_545`, `VALIDATION_ROWS=2_880`, `TEST_ROWS=2_880`): `train.csv` = raw rows 0–11,424 (8,545 train + 2,880 validation rows **merged into one fit history**); `test.csv` = raw rows 11,425–14,224; raw rows 14,225–17,419 (3,195 rows) are unused reserve. Fit on **all** of `train.csv` (11,425 rows), forecast 720 steps, score against **only the first 720 rows of `test.csv`** — a **single forecast origin** (raw rows 11,425–12,144 = 2017-10-20 01:00 → 2017-11-19 00:00, verified this session against `ETTh1.csv` date column).
- **Anti-leakage**: verified API-level (`ProtocolData` name-mangled privates; test only via `forecast_views()`/`test_scores()`) and model-level (`methods/` is I/O-blind; every `predict()` derives from `self.history_` = the fit array). Source: `./CONTEXT.md` §Anti-leakage guarantees.
- **Not comparable to the multivariate benchmark** — stated explicitly in `./config.json`: `"description": "Project univariate OT high-horizon (H=720) evaluation. NOT comparable to the multivariate benchmark."` See "Honest SOTA comparison" below for the full list of protocol caveats.

### Leaderboard (exact numbers, from the `LEADERBOARD_START/END` markers in `./CONTEXT.md`)

Top-3 (all H=720, raw units):

| Rank | Model | MAE | RMSE | Status |
|---|---|---|---|---|
| 1 | HeuristicLagELM (fast lags, 64 neurons, full history) | **1.5923** | **1.9823** | ok (sobol sweep) |
| 2 | HeuristicLagELM (fast lags, 256n, sobol_iid, full) | 1.6330 | 2.0550 | ok (sobol sweep) |
| 3 | HeuristicLagELM (fast lags, 256n, recent 50%) | 1.6344 | 2.1715 | ok (sweep) |

Reference rows on the same protocol (raw units): daily seasonal-naive (lag 24) **1.6720**/2.1719; tuned HeuristicLagKNN (k=32, q=3, recent 10%) **1.7204**/2.1405; persistence 1.7952/2.2503; nlinear 2.3507/2.8173; dlinear 16.6890/16.8130; recursive kNN 2.4308/3.1944; single tree 3.3488/4.0927; RF 2.7354/3.1826.

Two structural facts from the leaderboard:
1. **The best model beats the seasonal-naive baseline by only 0.0797 MAE (4.8%)** (1.5923 vs 1.6720, `./CONTEXT.md` leaderboard rows 1 and 4). Every learned model on the board is within ~±10% of "copy yesterday".
2. **Direct vs recursive is already settled in-project**: `heuristic_lag_knn_recursive` scores 2.4308 MAE vs 1.7204 for the direct variant of the same family — error compounding at H=720 costs +41% MAE (`./CONTEXT.md` leaderboard).

### Unit conversion (computed this session from `train.csv`/`test.csv` on disk)

Published ETT numbers are computed on data standardized by the **benchmark train-split** statistics (raw rows 0–8,544). That split's OT std = **9.2206**, mean = 17.0964 (computed from `./train.csv` rows 0–8,544). Conversions:

| Project number (raw) | Standardized (÷ 9.2206) |
|---|---|
| Best MAE 1.5923 (HeuristicLagELM) | **0.1727** |
| Best RMSE 1.9823 | 0.2150 (→ MSE ≈ 0.0462) |
| daily seasonal-naive MAE 1.6720 | 0.1813 |
| tuned kNN MAE 1.7204 | 0.1866 |
| nlinear MAE 2.3507 | 0.2549 |
| persistence MAE 1.7952 | 0.1947 |

Scoring-window regime (computed from `test.csv`): the single scored 720-row window has OT mean 9.23, std **2.22** (min 0.0, max 14.77) — a low-amplitude autumn regime following the high-amplitude summer (benchmark train-split std 9.22). For contrast, the *second* 720-row window of `test.csv` (rows 720–1,440) gives daily-naive MAE **1.3332**, and daily-naive averaged over the full 2,880-row test region is **1.5205** (computed this session) — i.e., the project's scored window is ~10% *harder* than the test-region average for the seasonal-naive rule, and individual windows vary widely. Single-origin numbers are high-variance draws.

### Registry surface & sub-experiment map (what exists)

`REGISTRY` (10 forecasters, `./methods/__init__.py`): `persistence`, `heuristic_lag_knn`, `heuristic_lag_knn_recursive`, `heuristic_lag_rf`, `heuristic_lag_tree`, `temporal_lag_knn`, `dlinear`, `nlinear`, `heuristic_lag_elm_tree` (+`HeuristicLagELM`, `BalancedLagEnsembleKNN`, `seasonal_forecast` exported). Contract: `fit(y, *, horizon) -> self` / `predict() -> ndarray(H,)` (`./methods/base.py`).

Sub-experiments (each `sub_experiments/*/CONTEXT.md`):
- `heuristic_sweep` / `q3_k_sweep` / `recent10_sweep` — kNN (k, q, history) tuning; best kNN 1.7204 (k=32, q=3, recent 10%).
- `temporal_knn_sweep` — 70 configs of time-decayed kNN; **decay never beats the hard recent-10% window** (best decayed 1.7866 vs parent 1.7204).
- `ensemble_sweep` — `BalancedLagEnsembleKNN` (16-expert lag grid); best 1.7639 (q6_k8_recent50); weekly-168h lags hurt at H=720.
- `elm_sweep` — ELM (hidden_dim × history_fraction × lag set); best 1.6344 (256n, recent 50%, fast lags); 1024/4096 neurons over-fit; **dropping the 24h lag helped** ("fast" = 1,2,3,6,12 beats "default").
- `sobol_elm_sweep` — Sobol/quasi-random weight placement vs iid normal; hypothesis rejected; **current best 1.5923** = normal-init, 64 neurons, full history, fast lags (capacity, not placement).
- `fnn_mi_elm_tree` — **designed but not yet run** (`CONTEXT.md` says "Results (pending — run run_sweep.py)"): AMI/FNN lag selection (τ=14, m=5 → lags 14,28,42,56,70) + ELM layer + decision-tree readout vs ridge readout.

### Gap analysis — what the project has NOT tried (all verifiable from `methods/` + sweep docs)

1. **No rolling-origin evaluation** — every number is one origin (`data.py::forecast_views` scores `test.csv[:720]` only). No sub-experiment scores the remaining 2,160 test rows or the 3,195-row reserve.
2. **No validation-split model selection** — sweeps pick the best config **by the scored test window itself** (each sub-experiment `CONTEXT.md` ranks configurations by test-window MAE); the benchmark 2,880-row validation segment is folded into fit data instead.
3. **No scale normalization** — `methods/base.py::_lag_features` subtracts the q-step anchor mean but never divides by window std; DLinear fits closed-form OLS on **raw-scale** windows (its 16.6890 MAE, vs 0.490 MAE published multivariate — see SOTA section — points to raw-scale conditioning, not to DLinear being a bad model for this data).
4. **No lookback > 336 for any linear/window model** — DLinear uses `input_length=96` (`config.json`), NLinear 336 (`methods/neural_models.py` `NLinear.__init__`); nothing uses the 720-step lookback that the linear-family literature favors at H=720.
5. **No frequency-domain method** — nothing in `REGISTRY` touches FFT/spectral features (registry listing, `methods/__init__.py`).
6. **No multi-rate/multi-scale input features** — all lag sets are single-rate hourly (1–24h; the 16-expert grid varies lags, not sampling rate). No pooled/downsampled views.
7. **No cross-family ensembles** — `BalancedLagEnsembleKNN` mixes only kNN experts; the three strongest diverse families (ELM 1.5923, kNN 1.7204, seasonal-naive 1.6720) have never been blended.
8. **No nonlinear readout beyond ridge-on-random-features and trees** — no spline/adaptive activation models (KAN family), no gradient-trained heads at all.
9. **The one designed experiment on principled lag selection (MI+FNN) is unrun** (`sub_experiments/fnn_mi_elm_tree/CONTEXT.md`, results pending).

---

## External State of the Art

Every claim below is URL-cited. Numbers are as reported by each source; see "Contradictions" for cross-paper disagreements.

### Univariate ETTh1, H=720 (the closest published surface to this project)

The LTSF-Linear paper's univariate ETT benchmark (features=S, target = OT channel — the paper's Fig. 5 caption "ETTh1 channel6" confirms the univariate ETT target is OT), metrics on train-standardized data, lookback-96 protocol, evaluated over the standard test split:

| Model | MSE | MAE |
|---|---|---|
| **NLinear** | **0.080** | **0.226** |
| FEDformer-f | 0.142 | 0.299 |
| Autoformer | 0.126 | 0.283 |
| Linear | 0.172 | 0.340 |
| Informer | 0.183 | 0.355 |
| DLinear | 0.189 | 0.359 |
| LogTrans | 0.475 | 0.629 |

Source: Table 9, https://ar5iv.labs.arxiv.org/html/2205.13504 . Same paper: NLinear's last-value subtraction is explicitly motivated by "serious distribution shifts between training and test sets" on ETTh1/ETTh2 (§C.1, same URL).

### Multivariate ETTh1, H=720 (context: the commonly cited "SOTA table")

TimesNet-protocol table (lookback 96, standardized), ETTh1 @ 720 — iTransformer 0.503/0.491 (MSE/MAE), RLinear 0.481/0.470, PatchTST 0.500/0.488, TiDE 0.594/0.558, TimesNet 0.521/0.500, DLinear 0.519/0.516, SCINet 0.836/0.699. Source: Table 10, https://arxiv.org/html/2310.06625v4 (iTransformer, ICLR 2024).

Original DLinear-paper protocol (lookback 96), ETTh1 @ 720 — NLinear 0.440/0.453, DLinear 0.472/0.490, FEDformer 0.506/0.507, Autoformer 0.514/0.512, Linear 0.624/0.592, Informer 1.181/0.865, **Repeat (persistence) 1.339/0.756**. Source: Table 2, https://ar5iv.labs.arxiv.org/html/2205.13504 .

FITS (frequency-interpolation linear model, lookback 720 for all horizons), ETTh1 @ 720: **MSE 0.427** vs DLinear 0.440 / PatchTST 0.447 / TimesNet 0.521 / FEDformer 0.506 — with ~10k parameters. Source: Table 2, https://arxiv.org/html/2307.03756v2 .

FAN (frequency-adaptive normalization, NeurIPS 2024) on SCINet backbone, ETTh1 @ 720: MAE 0.571 / MSE 0.572; ablation "pure backbone" (SCINet without FAN) 0.633/0.636 and "w/o predict" 0.632/0.789. Averaged over all horizons on ETTh1, FAN beats SAN/Dish-TS/RevIN on all four tested backbones (e.g., DLinear backbone: FAN 0.441 vs RevIN 0.477 avg MSE). FAN claims 7.76%–37.90% average MSE improvement across 8 datasets. Source: Tables 3–4, https://arxiv.org/html/2409.20371v1 and https://arxiv.org/abs/2409.20371 .

### Architecture families (2023–2025), with the claims their authors make

- **iTransformer** (ICLR 2024): inverts the Transformer — attention over *variate* tokens, FFN over each series. SOTA on multivariate benchmarks; also shows plain Transformer +Inverted gains 16.8%–38.9% MSE over five Transformer variants. https://arxiv.org/html/2310.06625v4
- **PatchTST** (ICLR 2023): patching + channel independence; prior SOTA Transformer; in the FITS table at ETTh1-720 MSE 0.447 (L=720). https://arxiv.org/abs/2211.14730 ; https://arxiv.org/html/2307.03756v2
- **TimesNet** (ICLR 2024): FFT-based multi-period 2D reshaping; task-general backbone; ETTh1-720 MSE 0.521 (as reproduced by iTransformer). https://arxiv.org/abs/2210.02186
- **N-HiTS** (AAAI 2023): multi-rate MaxPool input sampling + hierarchical interpolation on the N-BEATS skeleton; ~20% average accuracy improvement over latest Transformers and 50× compute reduction; long-horizon-specialized; univariate-native (its univariate appendix covers ETTm2/Exchange, not ETTh1). Its multi-step strategy discussion holds that the *joint/direct* strategy "strikes the perfect balance between variance and bias, avoiding error accumulation". https://ar5iv.labs.arxiv.org/html/2201.12886 (Table 1, Appendix F).
- **TimeMixer** (ICLR 2024): fully-MLP multiscale mixing (Past-Decomposable-Mixing + Future-Multipredictor-Mixing — i.e., an explicit multi-predictor ensemble over scales). https://arxiv.org/abs/2405.14616
- **FITS**: complex-linear interpolation on rFFT of the lookback + low-pass filter; ~10k params; ETTh1-720 MSE 0.427; DLinear is 50× its size, mainstream models ~10,000×. https://arxiv.org/html/2307.03756v2
- **KAN-based TS models**: KAN (spline-parametrized edge activations) proposed as an MLP alternative — https://arxiv.org/abs/2404.19756 (as cited by the T-KAN paper). T-KAN/MT-KAN apply it to univariate/multivariate forecasting with concept-drift detection; on financial OHLCV data a 2-layer, 5-neuron T-KAN (193 params) matches LSTM [84,50,21] (11,671 params); authors note KAN is "typically 10 times slower to train compared to MLPs with the same number of parameters" and compare only against MLP/RNN/LSTM (not TSF SOTA). https://arxiv.org/html/2406.02496v1 . TKAN (recurrent KAN layers) targets multi-step forecasting — https://arxiv.org/abs/2405.07344 . No ETTh1-720 numbers exist for any KAN variant in these sources.
- **ELM**: the project's own winning family. Modern ELM literature is mostly hybrid/metaheuristic (e.g., convolutional or ensemble ELMs — https://link.springer.com/article/10.1007/s00500-023-09499-6 , https://www.sciencedirect.com/science/article/pii/S0925231220316544 ); no ELM entry appears in any of the ETT-720 leaderboard tables cited above — i.e., **the project's HeuristicLagELM result is not represented in the published ETT-720 comparison tables**.

### Linear-model analysis & normalization tricks (directly about this project's model class)

- **Toner & Darlow (ICML 2024)**: DLinear, NLinear, RLinear, and FITS are all mathematically equivalent to (unconstrained or weakly-constrained) **linear regression over augmented features**; closed-form OLS solutions are "superior forecasters across 72% of test settings"; the variants "learn nearly identical solutions". https://arxiv.org/abs/2403.14587 , https://arxiv.org/html/2403.14587v2
- **RLinear / Li et al. (2023)**: "affine mapping dominates forecasting performance across commonly utilized benchmarks"; reversible normalization "significantly enhances trend forecasting by transforming non-periodic trends into periodic-like patterns"; longer input horizon helps multi-channel data. https://arxiv.org/abs/2305.10721
- **RevIN (Kim et al., ICLR 2022)**: instance-wise standardize-then-reverse normalization against distribution shift; model-agnostic. https://openreview.net/forum?id=cGDAkQo1C0p (page fetched via search result listing; abstract at https://iclr.cc/virtual/2022/poster/6034 )
- **Dish-TS (2023)**: dual coefficient-nets for intra-space and inter-space (lookback→horizon) distribution shift; ">20% average improvement" when coupled with SOTA models. https://arxiv.org/abs/2302.14829
- **FAN (NeurIPS 2024)**: removes top-K instance-wise Fourier components and *predicts their future values* with an MLP rather than assuming they persist; improvements grow with horizon (Informer backbone, 96→720: 9.87%→20.05% MSE). https://arxiv.org/html/2409.20371v1
- **Lookback effect (DLinear paper)**: for *linear* models, performance improves monotonically with lookback up to 720 on hourly datasets, while most Transformers plateau or degrade; "the farther the forecasting horizon, the less impact the look-back window itself has" — long-horizon learnability is dominated by trend + periodicity capture. https://ar5iv.labs.arxiv.org/html/2205.13504 (§5.3, Fig. 4/6)

### Direct vs recursive at long horizons

- DLinear paper (§2): IMS/recursive "inevitably suffer from error accumulation"; DMS/direct is preferable "when it is hard to obtain an unbiased single-step forecasting model, or T is large". https://ar5iv.labs.arxiv.org/html/2205.13504
- N-HiTS (§2 Related Work, multi-step forecasting): the direct strategy has low bias/high variance avoiding error accumulation; the *joint* strategy (single model, all steps, shared parameters) balances bias/variance. https://ar5iv.labs.arxiv.org/html/2201.12886
- N-HiTS Appendix F: "recurrent based strategies like the one from ARIMA tend to degrade due to the concatenation of errors phenomenon". https://ar5iv.labs.arxiv.org/html/2201.12886
- Project-side confirmation at H=720: recursive kNN 2.4308 vs direct 1.7204 MAE (`./CONTEXT.md` leaderboard).

### Benchmark criticism (Transformers vs linear baselines)

- Zeng et al. 2023 (DLinear paper): LTSF-Linear beats the five tested Transformers "in all cases, and often by a large margin (20%∼50%)"; shuffling the input barely hurts Informer but devastates Linear; Transformers fail to exploit longer lookbacks. https://ar5iv.labs.arxiv.org/html/2205.13504
- iTransformer's rebuttal framing: "it is not that Transformer is ineffective for time series forecasting, but rather that it is improperly used" (inverted usage restores SOTA). https://arxiv.org/html/2310.06625v4
- Toner & Darlow: the linear-variant zoo is largely the same model class dressed differently; closed-form fits often beat the same architecture trained by SGD. https://arxiv.org/abs/2403.14587
- FITS: at ~10k parameters it matches/beats million-parameter models on ETT — an argument that ETT benchmarks under-constrain model complexity. https://arxiv.org/html/2307.03756v2

---

## Honest SOTA Comparison — how MAE 1.5923 relates to published ETTh1-720 results

**Answer to the implicit commission question.** The project's best model (HeuristicLagELM, fast lags, 64n, full history: MAE 1.5923 / RMSE 1.9823, raw units — `./CONTEXT.md` leaderboard) **cannot be placed on a published leaderboard as-is**, for four protocol reasons (each grounded):

1. **Single origin vs rolling windows.** The project scores one 720-step window (raw rows 11,425–12,144). Published ETT tables average over the entire 2,880-row test region via sliding windows (multiple forecast origins) — e.g., the iTransformer evaluation protocol (§4.1/Appendix F, https://arxiv.org/html/2310.06625v4 ) and the LTSF-Linear univariate benchmark ( https://ar5iv.labs.arxiv.org/html/2205.13504 ). This session's computation shows the choice of window matters a lot: daily-naive MAE is 1.6720 on the scored window, 1.3332 on the next window, 1.5205 averaged over the full test region.
2. **Fit data.** The project fits on 11,425 rows (train+validation merged, `./data.py` `VALIDATION_END = 11425`); the benchmark fits on 8,545 rows and uses the 2,880 validation rows for model selection (N-HiTS: "validation split is used to tune hyperparameters" — https://ar5iv.labs.arxiv.org/html/2201.12886 ).
3. **Selection surface.** Project sweeps rank configurations by the *scored test window* (each `sub_experiments/*/CONTEXT.md` results table is test-window MAE); published protocol selects on validation. The project's own `sub_experiments/elm_sweep/CONTEXT.md` caveat ("confirm on the validation split before promoting any default change") acknowledges this.
4. **Units.** Project metrics are raw-OT; published metrics are train-standardized. Using the benchmark train-split σ = 9.2206 (computed from `train.csv` rows 0–8,544): project best ≈ **0.1727 MAE / 0.0462 MSE** (standardized equivalents).

**With all four caveats stated, the numeric comparison is:**

| ETTh1, H=720 | Protocol | MAE (std) | MSE (std) |
|---|---|---|---|
| **Project best (HeuristicLagELM 64n)** | single origin, fit 11,425 rows, tuned on window | **0.173** | **0.046** |
| Project daily seasonal-naive | same | 0.181 | — |
| NLinear (best published univariate) | rolling, lookback 96, fit 8,545 | 0.226 | 0.080 |
| FEDformer-f (best Transformer, univariate) | rolling, lookback 96 | 0.299 | 0.142 |
| iTransformer (best multivariate, L=96) | rolling | 0.491 | 0.503 |
| FITS (multivariate, L=720) | rolling | — | 0.427 |

(Sources as cited in the External SOTA section.)

**Verdict (honest reading):** after unit conversion the project's number is *numerically below* the best published univariate ETTh1-720 result (NLinear 0.226 MAE, https://ar5iv.labs.arxiv.org/html/2205.13504 ) — roughly 24% lower MAE — but this is **not a SOTA claim**: it is one favorable draw from a high-variance single-origin protocol, on a low-amplitude autumn window (window OT σ 2.22 vs series σ 8.37 — computed this session), with 2,880 extra training rows and window-level hyperparameter selection. The three externally-valid facts are: (a) the project's *baseline* (seasonal-naive 0.181 std-MAE) is itself at the level of published univariate SOTA on the benchmark protocol, so **the honest external anchor is: the project's models beat strong simple baselines by ~5% on one window, and the published field sits within ~±25% of NLinear's 0.226 univariate MAE**; (b) no ELM-family or kNN-family model appears in any published ETTh1-720 table cited here, so the project is exploring genuinely under-reported territory; (c) the project's DLinear 16.6890 raw-MAE (≈1.81 std) is an outlier vs the same architecture's published 0.490 std-MAE ( https://ar5iv.labs.arxiv.org/html/2205.13504 Table 2) and almost certainly reflects the project's raw-scale, closed-form-OLS, lookback-96 implementation (`./methods/neural_models.py` `DLinear`, `ridge_alpha=0.0`, raw windows) rather than the method itself.

---

## Contradictions & Open Questions

**Recorded per stop-on-contradiction doctrine — both sides kept, not adjudicated here.**

1. **DLinear's ETTh1-720 number differs by source**: original paper 0.472 MSE (Table 2, https://ar5iv.labs.arxiv.org/html/2205.13504 ) vs iTransformer's reproduction 0.519 MSE (Table 10, https://arxiv.org/html/2310.06625v4 ). Same for FEDformer (0.506 vs 0.594) and others. Cross-paper reproducibility of these benchmarks is ±10–20% for the *same* method+dataset+horizon — directly relevant to how much weight to give any single leaderboard entry.
2. **"Transformers are ineffective" vs "Transformers were misused"**: Zeng et al. 2023 ( https://ar5iv.labs.arxiv.org/html/2205.13504 ) vs iTransformer ( https://arxiv.org/html/2310.06625v4 ) and PatchTST ( https://arxiv.org/abs/2211.14730 ). Unresolved at the community level; the project has no stake since it fields no attention-based model.
3. **Normalization-trick gains vs linear-equivalence results**: FAN reports up to 37.9% MSE improvements from normalization layers ( https://arxiv.org/html/2409.20371v1 ), while Toner & Darlow prove the underlying model classes equivalent and find closed-form fits dominate ( https://arxiv.org/abs/2403.14587 ). Both can be true (normalization changes the *feature augmentation*, not the class), but the *effective* gain from adding RevIN/Dish-TS/FAN-style machinery to a well-fit linear/ridge model is contested: FAN's own ETTh1 table shows single-digit avg-MSE differences among FAN/SAN/RevIN on DLinear and SCINet backbones (0.441–0.477) and large gains only on weak backbones (Informer: 0.465 vs RevIN 0.688).
4. **Project's DLinear 16.6890 vs published 0.490**: contradiction between project leaderboard (`./CONTEXT.md`) and the source paper ( https://ar5iv.labs.arxiv.org/html/2205.13504 ). Most plausible resolution (untested): raw-scale OLS conditioning + lookback-96 + full-history origins in the project's implementation; the published model is trained on standardized data. This deserves a re-implementation check before DLinear is used as any evidence in the project.
5. **Seasonal-naive is not in published ETT tables**: none of the cited tables includes a lag-24 seasonal-naive row (only Repeat/persistence: 0.756 std-MAE multivariate at 720, https://ar5iv.labs.arxiv.org/html/2205.13504 ), yet it is the project's near-best model (1.6720 raw). How the published univariate leaders (NLinear 0.226) compare to plain seasonal-naive on the *same* rolling protocol is not answerable from cited sources — an open external question, and the main reason the project's internal baselines are not externally anchored.
6. **KAN evidence is thin**: T-KAN/MT-KAN results are on financial OHLCV data against MLP/RNN/LSTM only, with a self-reported 10× training slowdown ( https://arxiv.org/html/2406.02496v1 ); no ETT numbers exist (TKAN, https://arxiv.org/abs/2405.07344 , reports no ETT-720 table either). Whether a KAN readout beats a random-feature ELM readout at H=720 is genuinely open.
7. **Univariate NLinear lookback**: the univariate Table 9 numbers ( https://ar5iv.labs.arxiv.org/html/2205.13504 ) do not state the lookback in the caption; the paper's lookback ablations (Fig. 6) show univariate linear results keep improving up to L=720. Exact L for Table 9 is an open question to verify from the LTSF-Linear repo before using 0.226 as a like-for-like anchor.
8. **Open questions (unresolved this session)**: (a) does the ELM/kNN advantage over seasonal-naive survive rolling-origin averaging? (computable from `test.csv` + reserve rows — protocol decision needed); (b) is the 1.5923 config's gain an artifact of window-level tuning? (needs validation-split re-selection); (c) do the 3,195 reserve rows ( `./CONTEXT.md` pipeline note) hold a second, unseen 720-window for a true holdout? (rows 14,225+ exist but are after the benchmark test region — usable as a sanity holdout, though not comparable to anything published); (d) what does the pending MI+FNN sub-experiment ( `sub_experiments/fnn_mi_elm_tree/CONTEXT.md` ) actually yield — it is designed but unrun.

---

## Directions to Evaluate

*Evaluation candidates for the user — not commitments. Each row cites one project fact (file path) + one external source (URL). Cost/effort marks are estimates only.*

| # | Direction | Project fact (path) | External anchor (URL) | Est. cost |
|---|---|---|---|---|
| 1 | **Rolling-origin evaluation** — extend scoring to all disjoint 720-windows of `test.csv` (and optionally the reserve), reporting mean±spread per model, before any further model work. First: re-rank the existing top-5 under rolling evaluation. | `data.py::forecast_views()` scores only `test.csv[:720]`; this session: daily-naive 1.672 vs 1.333 vs 1.520 across windows | Benchmark protocol evaluates the full test region via sliding windows: https://arxiv.org/html/2310.06625v4 (§4.1, App. A/F) | Low (hours; evaluation-only change) |
| 2 | **Validation-split model selection** — re-select the winning ELM/kNN configs on the 2,880-row validation segment (fit train-only, select on val, score once), to check the 1.5923–1.7204 band for tuning artifacts. | Sweeps rank by scored-window MAE (e.g., `sub_experiments/elm_sweep/CONTEXT.md` tables); validation rows are folded into fit (`data.py` `VALIDATION_END`) | N-HiTS: validation split is for hyperparameter tuning — https://ar5iv.labs.arxiv.org/html/2201.12886 ; DLinear paper's own caveat pattern | Low (re-run existing sweeps with train-only fit) |
| 3 | **Instance normalization (RevIN-style scale, not just anchor-shift)** — add window-std division (+ optional learnable affine) to the HeuristicLag* feature pipeline; the anchor currently removes only a mean. | `methods/base.py::_lag_features` subtracts the q-mean anchor, never divides by std; `methods/neural_models.py::HeuristicLagELM` inherits it | RevIN: https://iclr.cc/virtual/2022/poster/6034 ; FAN shows instance-wise normalization beats plain backbones at H=720 (Informer 96→720: gains grow to 20.05% MSE): https://arxiv.org/html/2409.20371v1 | Low (one feature-transform variant) |
| 4 | **Standardized-scale + long-lookback linear baselines (NLinear/RLinear/FITS-form at L=720)** — fix the project's DLinear (currently raw-scale OLS, 16.6890) and add the linear family at benchmark-standardized scale with L ∈ {336, 720}; per Toner-Darlow these are closed-form OLS on augmented features, i.e., cheap to implement exactly. | `DLinear` uses `ridge_alpha=0.0` on raw windows, `input_length=96` (`methods/neural_models.py`, `config.json`); project DLinear MAE 16.6890 (`CONTEXT.md` leaderboard) | Linear models improve monotonically with lookback to 720: https://ar5iv.labs.arxiv.org/html/2205.13504 §5.3/Fig.6 ; FITS at L=720: ETTh1-720 MSE 0.427, ~10k params: https://arxiv.org/html/2307.03756v2 ; equivalence/closed-form: https://arxiv.org/abs/2403.14587 | Low–medium |
| 5 | **Frequency-domain forecaster (FITS-style, closed-form)** — rFFT of the normalized lookback, complex ridge readout to the extended spectrum, low-pass cutoff by dominant-frequency harmonics; matches the project's numpy/ridge philosophy and gives the project its first spectral entry. | Nothing in `REGISTRY` uses spectral features (`methods/__init__.py`); lag sets are all hourly single-rate | FITS: frequency interpolation + LPF, SOTA-competitive at ~10k params: https://arxiv.org/html/2307.03756v2 | Low–medium |
| 6 | **Cross-family ensemble (ELM + kNN + seasonal-naive)** — blend the three strongest, structurally diverse members (1.5923 / 1.7204 / 1.6720); the existing ensemble mixes only kNN experts. | `sub_experiments/ensemble_sweep/CONTEXT.md` (BalancedLagEnsembleKNN best 1.7639 — kNN-only); top models from three families on the leaderboard (`CONTEXT.md`) | TimeMixer FMM — explicit multi-predictor mixing across scales: https://arxiv.org/abs/2405.14616 | Low |
| 7 | **Multi-rate/multi-scale lag features (N-HiTS-style pooling)** — MaxPool-downsampled views (e.g., 2h/4h/8h rates) feeding separate ELM/ridge experts summed hierarchically; complements the failed single-rate lag-grid ensemble. | All lag grids are hourly single-rate; weekly-168h lags already shown to hurt (`sub_experiments/ensemble_sweep/CONTEXT.md` finding 2) | N-HiTS multi-rate sampling + hierarchical interpolation, ~20% avg gain, univariate-native: https://ar5iv.labs.arxiv.org/html/2201.12886 | Medium |
| 8 | **Run the pending MI+FNN lag-selection sub-experiment** — it is fully designed; its ridge-reference arm directly tests whether data-driven lags beat hand-picked fast lags. | `sub_experiments/fnn_mi_elm_tree/CONTEXT.md`: "Results (pending — run run_sweep.py)" | FAN: instance-wise (data-driven) frequency selection beats fixed/global selection — https://arxiv.org/html/2409.20371v1 (§4.5) | Low (script exists) |
| 9 | **KAN/spline readout on the ELM hidden layer** — replace ridge-on-random-tanh with spline-edge activations; exploratory, given thin external evidence. | ELM readout is ridge on fixed random features (`methods/neural_models.py::HeuristicLagELM`) | T-KAN: 193 params matching 11,671-param LSTM (financial data only); 10× train slowdown: https://arxiv.org/html/2406.02496v1 | Medium (high risk, high interpretability payoff) |
| 10 | **Seasonal-naive-anchored residual learning** — model the *residual against daily seasonality* instead of the raw series (the ELM's anchor is only a 3-step mean); pairs naturally with direction 3. | Best models beat daily-naive by ≤4.8% (`CONTEXT.md` leaderboard rows 1 vs 4); current anchor is q∈{3..24}-mean (`methods/base.py::_anchor`) | DLinear trend/seasonal decomposition rationale: https://ar5iv.labs.arxiv.org/html/2205.13504 §4 | Low |

**Priority reading** (advisory): directions 1–2 are protocol hygiene and gate every other comparison — without them, any model-level gain (3–10) cannot be told apart from window luck or tuning artifacts. Directions 3–5 are the cheapest externally-anchored modeling upgrades; 6–7 are the natural next model-class steps; 8 is already built; 9 is exploratory. The single most informative cheap experiment is likely **1+2 combined**: re-rank the existing top-5 under rolling-origin, validation-selected evaluation — it converts the project's leaderboard from "one lucky window" to an externally comparable result, and every direction above depends on that conversion.

---

## References (all fetched 2026-09-02)

1. Zeng, Chen, Zhang, Xu — *Are Transformers Effective for Time Series Forecasting?* (LTSF-Linear/DLinear/NLinear). https://arxiv.org/abs/2205.13504 ; full tables: https://ar5iv.labs.arxiv.org/html/2205.13504 — multivariate Table 2, univariate Table 9, lookback/shuffle ablations §5.3, Repeat baseline.
2. Liu, Hu, Zhang, Wu, Wang, Ma, Long — *iTransformer* (ICLR 2024). https://arxiv.org/html/2310.06625v4 — ETTh1-720 multivariate numbers (Table 10), inverted-architecture argument, dataset split spec (App. A).
3. Xu, Zeng, Xu — *FITS: Modeling Time Series with 10k Parameters*. https://arxiv.org/abs/2307.03756 ; https://arxiv.org/html/2307.03756v2 — ETTh1-720 MSE 0.427 at L=720, parameter table.
4. Toner, Darlow — *An Analysis of Linear Time Series Forecasting Models* (ICML 2024). https://arxiv.org/abs/2403.14587 ; https://arxiv.org/html/2403.14587v2 — linear-variant equivalence, closed-form dominance.
5. Li, Qi, Li, Xu — *Revisiting Long-term Time Series Forecasting: An Investigation on Linear Mapping* (RLinear). https://arxiv.org/abs/2305.10721 — affine mapping, RevIN effects, input-horizon extension.
6. Nie, Nguyen, Sinthong, Kalagnanam — *PatchTST*. https://arxiv.org/abs/2211.14730 — patching + channel independence.
7. Wu, Hu, Liu, Zhou, Wang, Long — *TimesNet* (ICLR 2024). https://arxiv.org/abs/2210.02186 — multi-period 2D variation modeling.
8. Challu, Olivares, Oreshkin, Garza, Mergenthaler-Canseco, Dubrawski — *N-HiTS* (AAAI 2023). https://arxiv.org/abs/2201.12886 ; https://ar5iv.labs.arxiv.org/html/2201.12886 — multi-rate sampling, hierarchical interpolation, direct/joint multi-step rationale, univariate appendix.
9. Wang, Wu, Shi, Hu, Luo, Ma, Zhang, Zhou — *TimeMixer* (ICLR 2024). https://arxiv.org/abs/2405.14616 — multiscale mixing, multi-predictor ensembling.
10. Ye, Deng, Zou, Gui — *Frequency Adaptive Normalization (FAN)* (NeurIPS 2024). https://arxiv.org/abs/2409.20371 ; https://arxiv.org/html/2409.20371v1 — ETTh1-720 with SCINet, normalization-methods comparison, instance-wise frequency selection.
11. Fan, Wang, Wang, Wang, Zhou, Fu — *Dish-TS* (2023). https://arxiv.org/abs/2302.14829 — intra/inter-space distribution shift, dual CONET.
12. Kim, Jeong, Kim, Cho, Yoon — *RevIN* (ICLR 2022). https://iclr.cc/virtual/2022/poster/6034 (abstract page; OpenReview forum id cGDAkQo1C0p) — reversible instance normalization.
13. Xu, Chen, Wang — *Kolmogorov-Arnold Networks for Time Series* (T-KAN/MT-KAN). https://arxiv.org/html/2406.02496v1 — KAN TS application, param-efficiency vs LSTM, 10× slowdown note.
14. Genet, Inzirillo — *TKAN: Temporal Kolmogorov-Arnold Networks*. https://arxiv.org/abs/2405.07344 — recurrent KAN for multi-step forecasting.
15. ELM hybrid literature (context for the project's ELM family): https://link.springer.com/article/10.1007/s00500-023-09499-6 ; https://www.sciencedirect.com/science/article/pii/S0925231220316544 ; https://github.com/chickenbestlover/Online-Recurrent-Extreme-Learning-Machine — no ETT-720 leaderboard entries.

*Project sources: `./CONTEXT.md`, `data.py`, `config.json`, `methods/{__init__,base,neural_models}.py`, `sub_experiments/{heuristic_sweep,q3_k_sweep,recent10_sweep,temporal_knn_sweep,ensemble_sweep,elm_sweep,sobol_elm_sweep,fnn_mi_elm_tree}/CONTEXT.md` — all read from disk 2026-09-02. Numeric conversions (σ=9.2206 train-split std; window stats; rolling seasonal-naive) computed this session from `train.csv`/`test.csv`.*
