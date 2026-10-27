---
type: Concept
title: 2026-09-12_spectral-predictability-omega
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# Spectral Predictability (Ω) — Research Findings

**Date:** 2026-09-12
**Paper:** Wang et al., *Spectral Predictability as a Fast Reliability Indicator for Time Series Forecasting Model Selection*, arXiv:2511.08884 (12 Nov 2025), AAAI AI4TS Workshop 2026 — [arXiv](https://arxiv.org/abs/2511.08884) · [ar5iv HTML](http://ar5iv.org/html/2511.08884v1)
**Benchmark:** GIFT-Eval — Aksu et al. arXiv:2410.10393 — [github.com/SalesforceAIResearch/GIFT-Eval](https://github.com/SalesforceAIResearch/GIFT-Eval)
**Code repo:** [github.com/nesl/Spectral-Predictability-TS](https://github.com/nesl/Spectral-Predictability-TS) (BSD-3-Clause)
**Method note:** Research conducted via `agent-reach` tooling — `doctor --json` confirmed `gh CLI` / `Jina Reader` / `B站搜索 API` / `V2EX API` active; arXiv and GitHub fetched via Jina Reader (`curl https://r.jina.ai/...`) and GitHub API; `mcporter` available but `exa_search` not validated (see § Backend note).

---

## 1. Paper Summary

- **Problem:** Practitioners face a model-selection dilemma — exhaustively training/validating dozens of forecasters is expensive, but picking the wrong one hurts accuracy. No lightweight signal explains *why* models differ across datasets.
- **Proposed indicator:** Spectral predictability **Ω** — a signal-processing metric that quantifies how concentrated a series' power spectrum is. High Ω = structured/periodic; low Ω = diffuse/noisy. Computing Ω is an **FFT-only** step that takes **seconds** on a laptop, vs. hours–days to train a model suite.
- **Two-stage empirical design:**
  1. **Controlled experiments** (4 domains): synthetic Fourier signals (Ω engineered 0.2–0.8) + CarbonCast (hourly energy), PEMS (hourly traffic), Fitbit (minute heart-rate). Models: TimeLLM (Llama3.2-1B frozen), same arch random-init, GPT2-130M, DLinear. Protocol: 512-step context, 96-step horizon, sMAPE/MSE.
  2. **Large-scale GIFT-Eval analysis:** 51 models × 28 datasets spanning energy, health, finance, nature. Dataset-level Ω computed on full series (train/test splits not public; see Limitations).
- **Key finding:** Model-family performance **stratifies by Ω**. Large **zero-shot TSFMs** (foundation models with original pretrained weights, no fine-tuning on GIFT-Eval — per GIFT-Eval taxonomy) systematically beat statistical/DL baselines when Ω is high; the gap **vanishes at low Ω**.
- **Contributions (paper §1):** interpretable fast metric; monotonic Ω–error relationship; 60% regime-specific gain for zero-shot; low-Ω frontier identified; actionable deployment guidance.

---

## 2. Ω Formula & Definition

> Source: paper §3, arXiv HTML lines ~90–130; repo `gift_eval/compute_metrics_fast.py:77–135` and `:spectral_entropy()` / `omega_from_arr()`.

### Signal model

Let \(\{x_t\}_{t=1}^{T}\) be a univariate series.

1. **Preprocess:** remove DC (subtract mean), apply **Hann taper** window (reduces spectral leakage when periodicities unknown — paper §A.4).
2. **One-sided power spectral density** via FFT (DC bin excluded):
   \[
   P_k = |\hat{x}_k|^2,\quad k=1,\dots,K,\quad K=\lfloor T/2 \rfloor
   \]
   where \(\hat{x}_k\) is the \(k\)-th FFT coefficient.
3. **Normalize** to a distribution \(p_k = P_k / \sum_j P_j\).
4. **Spectral entropy** \(H(x) = -\sum_{k=1}^K p_k \log p_k\), with maximum entropy \(H_{\max}=\log K\).
5. **Spectral predictability**
   \[
   \Omega(x) = 1 - \frac{H(x)}{H_{\max}},\qquad \Omega \in [0,1].
   \]
   - \(Ω→1\): energy in few bins (strong seasonality/periodicity).
   - \(Ω→0\): energy spread uniformly (white-noise-like, unpredictable).
   - **Range:** [0, 1] by construction; prior work calls \(H/H_{\max}\) normalized spectral entropy / wavelet entropy analogues (refs Guntu et al. 2020; Wang et al. 2025 in paper §2–3).

### Computational efficiency

- Single FFT pass, \(\mathcal{O}(T\log T)\). Paper reports "seconds per dataset" for thousands–millions of points ("orders of magnitude faster than training a single model" — §3). Controlled-experiment datasets and GIFT-Eval truncated at 4096 steps per stream for tractability (§A.2).

### Multivariate handling (GIFT-Eval)

- Per-covariate Ω computed, then **averaged** across variates for a dataset-level score (§A.2: "we calculated metrics such as Ω and LLE per each covariate, and averaged them together").

---

## 3. Thresholds & Decision Rule

> Source: paper §5.2–5.3, Fig. 4 caption, and abstract.

| Regime | Threshold | Action | Rationale |
|--------|-----------|--------|-----------|
| **High Ω** | **Ω > 0.5** | **Prefer zero-shot TSFMs** (e.g., Moirai, Chronos). Narrow search to zero-shot candidates; skip exhaustive validation of other families. | Largest win observed here — up to **~60% lower sMAPE** vs. statistical/DL baselines. TSFMs leverage strong periodic structure. |
| **Low Ω** | **Ω < 0.4** | **Prefer lightweight baselines** (ARIMA/ETS/Seasonal Naive or DLinear/PatchTST). Zero-shot offers no clear advantage; use cheaper models. | Performance **converges** — model-type gaps shrink; at **Ω < 0.2** minimal differentiation at all (paper §5.1: "At Ω<0.2, there is minimal differentiation"). |
| **Mid Ω** | **0.4 ≤ Ω ≤ 0.5** | **Ambiguous — use secondary criteria** (budget, latency, stationarity check, domain knowledge). | Gaps are noisy; Ω alone insufficient to recommend a family. |

**Efficiency claim (paper §5.2, §6.1):**
- Compute Ω (seconds, no training) → filter to ~1 family → validate only that family.
- Cuts validation cost substantially vs. training all 51 candidates. Paper frames Ω as a **first-pass filter** that *complements* validation, not replaces it.

**60% gain — precise context:**
- Paper abstract + §1 bullet: "zero-shot TSFMs outperform statistical and deep-learning baselines **by up to 60% in high-Ω regimes**" — on **sMAPE** across GIFT-Eval. Gain is **regime-specific max**, not average; vanishes at low Ω. See Fig. 4 (binned sMAPE vs Ω by model type) and `gift_eval/corr_out/figures/` in repo.

---

## 4. GIFT-Eval Results (51 Models, 28 Datasets)

> Source: paper §5, Appendix A.1–A.2; repo `gift_eval/merged_gift_results.csv` (51 models, 28–98 configs) + `metrics_summary_wide*.csv`.

### Benchmark snapshot

- GIFT-Eval (Aksu et al., arXiv:2410.10393): 23 base datasets, ~144k series, 177M points, 7 domains, 10 frequencies, secondly→yearly, uni/multi, short/long horizons; includes non-leaking pretrain split `GiftEvalPretrain`. Leaderboard at `SalesforceAIResearch/gift-eval` tracks `model_type ∈ {statistical, deep-learning, pretrained, fine-tuned, zero-shot, agentic}` and `testdata_leakage`/`replication_code_available` flags (added 2025-08).

### How the paper uses it

- Draws Oliver et al.'s **51 models** from the public **GIFT-Eval leaderboard** `all_results.csv` files, categorized per GIFT-Eval taxonomy (§5 intro, §A.1). Coverage:

| Category | Example models (paper §A.1) |
|----------|-----------------------------|
| **Zero-shot** (≥19) | TimesFM-2.5, FlowState-9.1M, Kairos 10/23/50m, Sundial 128m, YingLong 6/50/110/300m, Granite-FlowState-r1, TiRex, DeOSAlphaTimeGPT, Toto Open Base 1.0, TabPFN-TS, Moirai small/base/large, VisionTS |
| **Pretrained** (11) | Moirai2, Chronos bolt small/base, Chronos small/base/large, TimesFM, TimesFM 2.0 500m, TTM-R1/R2-Pretrained, Lag-Llama |
| **Deep learning** (9) | xLSTM-Mixer, PatchTST, TFT, N-BEATS, DLinear, TIDE, DeepAR, Crossformer, iTransformer |
| **Statistical** (5) | Auto-ARIMA, Seasonal Naive, Auto-Theta, Auto-ETS, Naive |
| **Fine-tuned** (3) | TSOrchestra-test, TTM-R2-Finetuned, TE… (+ small-n agentic) |

- 28 datasets selected (subset where spectral stats available; full GIFT-Eval has 97 configs / 98 leaderboard rows).
- Ω computed **per dataset** (full series, since splits not public) and correlated with per-model sMAPE.

### Statistical pattern

- Overall: **Spearman ρ = −0.65, p = 1.9×10⁻²¹** between Ω and mean sMAPE across datasets (monotonic: higher Ω → lower error). Paper Fig. 2 (all-models mean) and Fig. 3 (split by model type).
- **Interaction by family** (Fig. 4, binned into 6 quantile bins so each bin has similar dataset count):
  - **Zero-shot** sMAPE falls steeply with Ω; at high Ω it beats other families by the headline ~60% margin.
  - **Pretrained** (Fig. 7) shows **no systematic Ω-dependence** — advantage flat across Ω (paper §5.1).
  - All families **converge** below Ω≈0.2–0.3 (§5.1 "The Low-Ω Challenge").
- Controlled experiments replicate: error ↓ 20–40% from Ω=0.3 → 0.7 in synthetic/CarbonCast; Pearson r(MSE, Ω) ∈ [−0.377, −0.750] across domains (paper Table 2).

### Relation to chaos (LLE)

- Appendix: LLE computed via Rosenstein method (embedding m=4, τ=10, dataset-level). High LLE (chaotic, sensitive to initial conditions) tends to coincide with low Ω, further predicting poor forecastability — but Ω alone doesn't fully capture chaotic dynamics (§5.1).

---

## 5. Repo & Code Notes

### Availability

- **Public** at `github.com/nesl/Spectral-Predictability-TS`, BSD-3-Clause. Clonable without auth. Structure verified via GitHub API `GET /repos/.../contents`.

### Layout (per README and API listing)

```
.
├── TimeLLM/                        # modified TimeLLM clone
│   ├── datasets/                   # user-supplied (Time Series Library)
│   ├── scripts/testSpectralAll.sh  # launches all 4-domain controlled runs
│   └── results_automate/graph_spectral.py  # per-domain plots + stats, Ω vs sMAPE
├── gift_eval/
│   ├── git_repo/                   # user clones SalesforceAIResearch/gift-eval here
│   ├── series/                     # Arrow datasets from GiftEval HF
│   ├── merge_gift_results.py       # → merged_gift_results.csv
│   ├── compute_metrics_fast.py     # → metrics_summary_wide.csv  (Ω, spectral_entropy, …)
│   ├── compute_all_dataset_metrics.py
│   ├── visualize_modeltype_effects.py  # → gift_eval/corr_out/figures/
│   ├── merged_gift_results.csv / _cleaned.csv  (checked in)
│   └── metrics_summary_wide*.csv      (checked in)
└── README.md / LICENSE / AUTHORS
```

### How to compute Ω

**Fastest path — reuse `compute_metrics_fast.py`** (recommended for GIFT-Eval scale):

```bash
cd gift_eval
python compute_metrics_fast.py                          # defaults: --metrics omega,spectral_entropy --truncate 4096 --downsample 2
python compute_metrics_fast.py --metrics omega,spectral_entropy,permen,wavelet_entropy
python compute_metrics_fast.py --metrics apen,sampen,lle --max-series 200 --truncate 2048 --downsample 4
```

- Outputs: `metrics_summary_wide.csv` (dataset-level means) + optional `metrics_per_series_wide.csv` (`--write-series`).
- Heavy metrics (`apen/sampen/permen/wavelet_entropy/lle`) are optional and gated behind `antropy`, `nolds`, `pywt`.

**Minimal standalone (single series)** — function signature is `omega_from_arr(x: np.ndarray) -> float` where `spectral_entropy(x) -> float` is `H(x)/Hmax` (normalized 0–1). Canonical implementation (`gift_eval/compute_metrics_fast.py:77–135`, simplified):

```python
import numpy as np

def _safe_rfft_power(x: np.ndarray):
    x = np.asarray(x, float).ravel()
    if x.size < 4: return None
    if np.allclose(x.std(), 0): return np.array([1.0])  # constant → Ω=1
    x = x - x.mean()
    # Note: paper §A.4 specifies Hann taper; repo code uses plain rfft —
    # add Hann outside if you want paper-exact: x = x * np.hanning(len(x))
    spec = np.fft.rfft(x, n=x.size)
    power = spec.real**2 + spec.imag**2
    power = np.clip(power, 0, None)
    return None if power.sum() == 0 else power

def spectral_entropy(x: np.ndarray) -> float:
    pwr = _safe_rfft_power(x)
    if pwr is None: return np.nan
    if pwr.size == 1: return 0.0
    p = pwr / pwr.sum()
    p = np.clip(p, 1e-12, 1.0)
    H = -np.sum(p * np.log(p))
    return float(H / np.log(len(p)))

def omega_from_arr(x: np.ndarray) -> float:
    return 1.0 - spectral_entropy(x)   # gift_eval/compute_metrics_fast.py:133–134

# Usage: omega_from_arr(series)  # series: 1-D np.ndarray, T>~100 (see reliability rule)
```

- **Inputs:** 1-D float array (univariate). For multivariate, compute per channel and average (paper §A.2).
- **Edge handling:** length <4 → NaN; constant/variance≈0 → H=0 → Ω=1 (by convention); zero total power → NaN.
- **Paper-exact nuance:** §A.4 prescribes `Hann taper + DC removal + FFT excluding DC` with `Hmax=log K, K=floor(T/2)`. Repo's `_safe_rfft_power` implements DC removal via mean subtraction and NaN guards but does **not** apply the Hann window internally — apply `x * np.hanning(T)` before calling if strict paper fidelity is needed.

### Code-derived Ω definition alignment

| Aspect | Paper (§3, §A.4) | Repo (`compute_metrics_fast.py:77–135`) |
|--------|------------------|----------------------------------------|
| Window | Hann taper | Not applied inside `_safe_rfft_power` (caller-side Hann recommended) — minor deviation, noted above |
| DC handling | Remove DC, exclude k=0 | `x - mean()` + rfft (DC bin magnitude then contributes to power; near-DC leakage differs — see note) |
| Spectrum | one-sided PSD \(|\hat{x}_k|^2\), \(k=1..K\) | `rfft` power; DC not explicitly dropped from sum (constant edge-case special-cased) |
| Ω | \(1 - H/\log K\) | `1 - spectral_entropy(x)` where `spectral_entropy` returns `H/log(len(p))` |

Difference is small for \(T\gg1;\Omega\) ordering is preserved. For reproduction, follow the repo or add taper+DC-drop to match §A.4 exactly.

### Dependencies

- **Core:** `numpy`, `pandas`, `datasets` (HF `load_from_disk` for GIFT-Eval Arrow), `scipy` (optional, for CI/stats in `graph_spectral.py` / `visualize_modeltype_effects.py`).
- **Optional / heavy metrics:** `antropy` (ApEn/SampEn/PermEn), `nolds` (LLE), `pywt` (wavelet entropy).
- **Plotting:** `matplotlib`, `statsmodels`, `scikit-learn` (Isotonic Regression).
- **For TimeLLM pipeline:** TimeLLM deps + `scripts/testSpectralAll.sh` expectations (Llama3.2-1B, GPT-2 weights, Time Series Library datasets).
- See `gift_eval/compute_metrics_fast.py:1–50` header and paper `§A.3` (single H100, lr 0.01, batch 16, ≤10 epochs, early-stop patience 3, per-window normalization, stride 1).

### What ships precomputed

- `merged_gift_results.csv` / `_cleaned.csv` — 51-model GIFT-Eval sMAPE/MSE table.
- `metrics_summary_wide.csv` / `_cleaned.csv` / `metrics_summary_all.csv` — per-dataset Ω, LLE, spectral_entropy, etc.
- `gift_eval/corr_out/` — correlation tables + Fig. 2–4, 7 PDFs.

---

## 6. Decision Rule (Operator Playbook)

```text
INPUT: univariate (or per-channel) series x, length T
1. Check reliability preconditions (§5.3):
   - T > 1000 timesteps (FFT stability; paper recommendation)
   - Series is (approximately) stationary — no regime shifts / structural breaks
     (visual check or stationarity test; high LLE is a warning sign)
   - Intrinsic temporal structure dominates over exogenous shocks
     (if shocks dominate — e.g., traffic accidents, policy events — Ω is weak)
2. Compute Ω(x):
   Hann-taper, remove DC, FFT → PSD → normalized entropy → Ω = 1 - H/Hmax
   (use omega_from_arr() or compute_metrics_fast.py)
   For multivariate: mean Ω across channels.
3. Branch:
   Ω > 0.5  → deploy ZERO-SHOT TSFM (e.g., Chronos, Moirai); validate only that family.
   Ω < 0.4  → deploy LIGHTWEIGHT (ARIMA/ETS/Naive or DLinear/PatchTST); skip heavy TSFMs.
   0.4–0.5  → no strong recommendation; include cost/latency/domain knowledge.
4. Caveats:
   - Ω on FULL dataset when splits unavailable may bias upward; controlled per-series Ω is ideal.
   - Low-Ω failure zone (Ω<0.2): all families struggle — treat forecasts as low-reliability; invest in noise modeling / mixture-of-experts / sparse-pattern attention (paper §7 directions).
   - Empirical counterexample: one dataset at Ω=0.66 where statistical beat zero-shot by ~50% (paper §5.3, Fig. 6 outlier).
   - Re-validate the reduced candidate set; Ω is a first-pass filter, not a replacement for validation (§6.1).
```

---

## 7. Limitations & When to Distrust Ω

Source: paper §5.3, §6.2, Appendix B.

1. **Non-stationarity — strongest failure mode.** Ω assumes stable spectra. Series with regime shifts, structural breaks, or high LLE (chaotic) produce a misleading aggregate Ω.
2. **Short series.** FFT estimates unstable; paper: require **T > 1000**. Synthetic sweep used T-controlled signals; GIFT-Eval truncated at 4096 but many series exceed that natively.
3. **Exogenous-driven dynamics.** Ω measures *intrinsic* temporal concentration, not shock-driven predictability. PEMS (traffic) and Fitbit (wearable gaps from device removal, night-time zero-traffic stretches) show weaker Ω–error correlation for this reason (Appendix B).
4. **Aggregation bias.** GIFT-Eval Ω computed on full datasets (splits not public), not per-split/test-only — subtle upward bias possible; controlled experiments (per-series, test-only Ω) mitigate and replicate the pattern.
5. **Scope of validation.** Coverage is sMAPE/MSE + CRPS/MASE in GIFT-Eval; no systematic test of probabilistic scores (CRPS interval coverage) vs Ω (paper §4 "Consistency Across Metrics" notes sMAPE/MSE agree, but CRPS not stratified). Also: neural-ODE / certain probabilistic architectures not represented among the 51 models.
6. **Other correlates not isolated.** Pretraining corpus composition and LLE may confound the Ω effect; paper: "more work should be done to integrate these indicators into a more cohesive index" (§6.2).
7. **Instructive outlier.** Ω=0.66 dataset where statistical models beat zero-shot by ~50% (opposite to rule) — shows domain factors Ω doesn't capture.

---

## 8. Related Context (GIFT-Eval Benchmark)

- **Paper:** Aksu et al., *GIFT-Eval: A Benchmark for General Time Series Forecasting Model Evaluation*, arXiv:2410.10393 (Oct 2024, v2 Nov 2024).
- **Scale:** 23 datasets / 144k series / 177M points; 7 domains, 10 frequencies, uni/multi, short/long horizons.
- **Splits:** `training_dataset` / `validation_dataset` / `test_data` via `gift-eval` `Dataset` class (gluonts interface); HF at `Salesforce/GiftEval` + `GiftEvalPretrain` (non-leaking pretrain corpus).
- **Evaluation:** `evaluate_model(predictor, test_data, metrics, batch_size=512, axis=None, mask_invalid_label=True, allow_nan_forecast=False, seasonality=season_length)`; metrics include MSE/MAE/MAPE/sMAPE/RMSE/NRMSE/CRPS/MASE etc.; per-config `all_results.csv` → leaderboard (now tracks `testdata_leakage`, `model_type`, `replication_code_available`).
- **Relevance here:** Wang et al. *reuse* the leaderboard's sMAPE columns verbatim, joining them to their own Ω table via `merge_gift_results.py` + `compute_metrics_fast.py` → `visualize_modeltype_effects.py`.

---

## 9. Reproducibility Notes

- **To reproduce Ω figures end-to-end (per repo README):**
  ```bash
  git clone https://github.com/nesl/Spectral-Predictability-TS && cd Spectral-Predictability-TS
  # Controlled: supply Time Series Library datasets to TimeLLM/datasets/, then:
  bash TimeLLM/scripts/testSpectralAll.sh
  python TimeLLM/results_automate/graph_spectral.py   # → TimeLLM/results_automate/out/Omega/{base,mse}/
  # Large-scale: supply GIFT-Eval Arrow + git_repo clone to gift_eval/{series,git_repo}, then:
  cd gift_eval && python merge_gift_results.py         # → merged_gift_results.csv
  python compute_metrics_fast.py                       # → metrics_summary_wide.csv
  python visualize_modeltype_effects.py                # → gift_eval/corr_out/figures/
  ```
- Datasets are **not bundled** — user must download Time Series Library sets and GiftEval Arrow splits separately (README). Precomputed CSVs and `corr_out/` are already committed for inspection without running the full pipeline.
- **Citation (paper):**
  ```bibtex
  @inproceedings{wang2026spectralpredictability,
    title={Spectral Predictability as a Fast Reliability Indicator for Time Series Forecasting Model Selection},
    author={Wang, Oliver and Quan, Pengrui and Yang, Kang and Srivastava, Mani},
    booktitle={AAAI Workshop on AI for Time Series (AIforTS)},
    year={2026}
  }
  ```

---

## 10. Backend Note (Agent-Reach)

- Command inventory from `agent-reach --help` exposes only `setup/install/configure/doctor/uninstall/skill/format/transcribe/check-update/watch/version` — **no** `agent-reach search` / `agent-reach fetch` subcommands. Tasks 1–3 were satisfied via the backends `doctor --json` *does* expose:
  - **Jina Reader** (`curl https://r.jina.ai/<URL>`) for arXiv + GitHub Markdown (active backend per doctor).
  - **GitHub API** (`api.github.com/repos/.../contents`) for repo file enumeration and raw fetches (`raw.githubusercontent.com`).
  - **`mcporter` + `gh CLI`** available in PATH; `exa_search` backend present in config but not validated live, so web search was routed through Jina as the zero-config fallback consistent with `'C:\Users\Mateusz\.agents\skills\agent-reach'` routing.

---

### File & Line Provenance (anchor citations)

- Ω math + efficiency: paper §3, ar5iv lines ~100–135; repo `gift_eval/compute_metrics_fast.py:77–135`.
- Thresholds 0.5/0.4/0.2: paper §5.2–5.3, §7; mid-bin rule `0.4≤Ω≤0.5`; low-Ω convergence `Ω<0.2`.
- 60% gain: paper abstract + §1 bullet 3 + §5 narrative; Fig. 4 + `gift_eval/corr_out/figures/`.
- GIFT-Eval 51×28: paper §5 + §A.1–A.2; model list `gift_eval/merged_gift_results.csv:1`, metrics `gift_eval/metrics_summary_wide*.csv:1`.
- Hann taper + length>1000 + stationarity caveats: paper §A.4, §5.3, §6.2, Appendix B.
- Code signatures: `spectral_entropy(x)` / `omega_from_arr(x)` at `compute_metrics_fast.py:100–135`; pipelines at `compute_metrics_fast.py:1`, `merge_gift_results.py:1`, `visualize_modeltype_effects.py:1`, `TimeLLM/results_automate/graph_spectral.py:1`.
- GIFT-Eval benchmark details: `github.com/SalesforceAIResearch/GIFT-Eval` README + arXiv:2410.10393.
- License: BSD-3-Clause (`LICENSE`).
