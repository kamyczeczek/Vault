---
type: Concept
title: open_questions
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Open Questions — H=720 ETTh1 Research (2026-09-02)

Extracted from findings.md (commission by TsResearch subagent). Reason recorded per item: single-origin protocol limits, missing sources, or out-of-scope design decisions.

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
