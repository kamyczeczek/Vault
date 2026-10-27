---
type: Concept
title: references
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# References — H=720 ETTh1 Research (2026-09-02)

Every URL fetched 2026-09-02 by the TsResearch subagent (transcript: history://TsResearch).

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

---
