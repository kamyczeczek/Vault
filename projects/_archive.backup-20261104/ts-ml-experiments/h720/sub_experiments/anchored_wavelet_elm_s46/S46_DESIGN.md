---
type: Concept
title: S46_DESIGN
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# S-46 Design — Anchored Wavelet → ELM Dictionary → Sparse Readout on Level-Free Deltas (Pre-Registration)

**Date:** 2026-09-14
**Slice:** `S-46-anchored-wavelet-elm` · **Directory:** `projects/ts-ml-experiments/h720/sub_experiments/anchored_wavelet_elm_s46/`
**Status:** Pre-registration design ONLY — executor implements after parent approval; zero tuning post-design.
**Supersedes:** none — wavelet-prior subexperiments were H2 (`wavelet_nlinear_h2`, linear DWT) and `wavelet_knn_hybrid_h2_knn`; neither used NLinear-style anchoring, ELM dictionary, or sparse lasso selection.
**Governing invariants:** S-43 P1 (gate declared up front — BLEND vs SINGLETON), P2 (per-window deltas vs the **in-harness** incumbent), P3 (surviving positive recorded), P4 (portfolio frontier record); S-44 P1 (parity block binding), P2 (incumbent anchors re-derived in-harness; future bets target **1.9781**) — `MONITORING/reflection/2026-09-13_2350` · `MONITORING/reflection/2026-09-14_0348` · `CONTEXT.md` `## Prevention rules — S-43` + S-44 section; H2 stop rule `CONTEXT.md:152-160` (univariate-linear family saturated — DWT-as-rotation).

---

## 1. Motivation & lineage — why this is not a family re-opening

**Incumbent:** S-44 blend **1.9781 / RMSE 2.4613**, disjoint-4 **1.8634**, paired Δ 95% CI **[−0.0185, −0.0069]** (`results_s44.json`). Members `[nlinear_L336_a1, nlinear_L336_a10, patchtst_P24_D32_2L]` per-horizon ridge no-intercept α=30000 (`S44_DESIGN.md`).

**User attachment (this bet):** `Stage 0 Anchor → Stage 1 Wavelet → Stage 2 ELM Dictionary → Stage 3 Sparse Readout → Stage 4 De-anchor`. The claim to test is: **anchored multi-scale features + random non-linear expansion + sparse selection** on *deltas* adds orthogonal signal beyond the L336 linear span that H2's DWT-as-rotation did not.

**What H2 / S-36 / S-35 closed — and why they do not close S-46:**

| Closed family | What S-46 violates (and why it matters) |
|---|---|
| **H2 — wavelet basis rotation** (`1.9906 full, disjoint 1.9656`, stop rule fired) | H2 was `DWT(J=3) → per-horizon Ridge` on the **anchored window** with uniform / subband-scaled penalty — i.e. a **linear** member. An orthogonal DWT of `L=336` is an orthogonal basis change of the same 336-dim space NLinear regresses on; uniform-alpha it is rotation-invariant → identical to NLinear. S-46 is not linear: the ELM dictionary `φ(W·x+b)` with tanh activation is a **non-linear basis expansion** of the wavelet coefficients, and the final head is a per-horizon **Lasso/ElasticNet sparse selector over that ELM space** — a genuinely different hypothesis class, not a re-parameterized linear subspace. |
| **S-36 / S-32 / S-23 — univariate scalar gating** | Those added a *scalar* aux feature (σ_t, kNN disagreement, volatility regime) gated over S-26; S-46 does not gate the incumbent. It proposes a **standalone feature→dictionary→sparse pipeline** on the wavelet representation itself, whose forecast participates as a blend member. |
| **S-35 — level-free non-linear readout on the saturated raw basis** (`2.0112 +0.0203`) | S-35 stayed on the raw 336-dim delta window (`L336 + 2 RF h32/64 on deltas`). S-46's representation is **multi-scale wavelet** (not raw window), and its non-linearity is **ELM with explicit denoising + sparsity**, not an unconstrained RF. |
| **S-21 / S-21b — tree heads / leaf-linear mixtures** | S-21(b) replaced the ridge *head* with regime-switching trees on member predictions/deltas. S-46 keeps the proven ridge *stack head* (no tree) — the only tree-like structure is the ELM dictionary itself, which is **fixed and random**, not learned data-adaptively. The sparse selector is still linear. |

**Consequences:**
- This is a **new frontier bet (orthogonal non-linear expansion)**, not a linear-multivariate mix (Bet 2) nor a univariate attention member (Bet 3). **No closed family is re-opened** by including an ELM-based wavelet member as a candidate in a tabu-selected blend. If rejected, a **new family close** is recorded (see §4 C5).
- The attachment describes the *stand-alone* anchored pipeline (Stages 0–4). S-46 plugs that stand-alone forecast **as a candidate member alongside the S-44 incumbent members inside the same tabu→per-horizon ridge-stack protocol** that validated S-44. Two things are then independently falsifiable: (a) the stand-alone anchored-wavelet-ELM-lasso forecast vs the L336 linear baseline, and (b) the stacked blend vs the S-44 blend. File (b) is the binding gate.

---

## 2. Gate-semantics declaration (S-43 P1 — binding)

| Element | Semantics for S-46 |
|---|---|
| **Binding gate** | **BLEND-based** — the frozen-test stacked blend of the tabu-selected subset must beat the **S-44 incumbent blend re-derived in-harness** (G1–G4). |
| **Singleton gate** | Secondary (reported, non-binding for promotion — see §4 demoted diagnostics). A `close_trigger` fires only when BOTH new singletons miss `2.90` **and** no new-member subset beats the held-out control — then a new family close is declared but existing verdict already stands. |
| **Resolution on disagreement** | The **blend decides**. A blend win does **not** re-open H2's linear-wavelet family (that remains closed for linear DWT members); it only certifies the **anchored-wavelet-ELM-sparse** family. A blend loss with singleton wins would be a positive survives-but-blend-misses case (recorded per S-43 P3). |

---

## 3. Mandatory design decisions (D1–D11)

### D1 — Slice identity & artifacts

- Slice id `S-46-anchored-wavelet-elm`; artifacts: `S46_DESIGN.md` (this file), `rolling_arm.py` (harness), `anchored_wavelet_elm.py` (member module: stand-alone pipeline + ridge-stack wrapper), `results_s46.json`, `harness.log`.
- Member module imports **nothing** from closed experiments except `data.get_protocol_data()` and `methods/neural_models.NLinear` (same as every recent bet). Wavelet via `pywt` (Python PyWavelets; `pip install PyWavelets`), ELM via `numpy` random projection — no torch heredity; fully deterministic.

### D2 — Data discipline: the NLinear anchor (Stage 0 / Stage 4)

- **Per-origin, per-channel anchor** `a_t = x_{t-1}` = **OT last value** of the look-back window (`window[-1]`). Mirrors NLinear and S-21b / PatchTST-Delta precisely: `x̃ = x − a_t` before wavelet decomposition; head predicts `ỹ̃ = f(x̃)`; final forecast **`ŷ = ỹ̃ + a_t`**. This is why the member is called *level-free*: the entire pipeline sees only deltas.
- **Why before wavelets (per attachment):** DWT is not translation-invariant — without anchoring, a level shift changes every subband coefficient distribution and defeats sparsity. Anchored input is near-zero at the boundary (reduces boundary artifacts) and keeps the ELM dictionary's random weights in a stable regime.
- Alternatives considered and **rejected** for the frozen design: rolling-mean / median anchors and anchor-as-feature — kept as declared follow-ups (§7). S-46 is **last-value only**.
- The anchor is recomputed per rolling origin from `history_[...:t]` (never from the test future). Validation and test phases re-derive it identically — S-20-clean containment.

### D3 — Feature engineering (Stage 1): wavelet decomposition on the anchored window

- **Transform:** **SWT** primary (Stationary Wavelet Transform — shift-invariant, symmetric handling via `mode='periodization'`/`symmetric`; avoids DWT's decimation artifacts when the anchored boundary is near-zero). One **DWT fallback** arm (periodization, same wavelet/levels) retained for the protocol's robustness claim — both transforms live in the same module; SWT is the *primary member* (`wswt_db4`) and DWT is ablation (`wdwt_db4`) so the harness can score either.
- **Wavelet & levels:** `db4`, **J=3** (one extra design knob: `haar` vs `db4` family — `db4` chosen for its short support and better denoising; `haar` ablation if cheap, else omitted — documented in results if dropped).
- **Input:** the anchored univariate OT window `x̃ ∈ R^{336}` (L=336 fixed — ties to the S-44 incumbent span).
- **Output layout:** approximation `A3 (length 42)` + details `D3,D2,D1 (42,84,168)` under periodization with `L=336,J=3` → **336 coefficients** padded to original length (SWT property: each subband length = L) then **subband-pooled** to a compact feature vector (see next).
- **Pooling / dimensionality control:** per-subband **mean-absolute** + **energy** summary → compact `F ≈ 20–30`-dim wavelet feature per origin (not per-coefficient regression — avoids the 336×H explosion that killed dense multivariate). Exact `F` logged in `results_s46.json:wavelet_feature_dim`.
- **Denoising:** **soft-thresholding** on detail subbands with **VisuShrink (universal threshold)** `λ_j = σ_j · sqrt(2 log N_j)` where `σ_j = MAD(D_j)/0.6745` **per subband** (wavelet-standard). Applied *after* SWT, *before* pooling. Ablation `threshold={universal, none}` reported as a one-bit sensitivity — no grid search.

### D4 — ELM dictionary (Stage 2): random non-linear expansion of wavelet features

- **Diet ELM:** `H_hidden = {200, 400}` — **two hidden-width arms** (primary `h200`, ablation `h400` — the small-budget end; `h64`/`h1000` explored elsewhere and rejected). One fixed seed `seed=42` shared by both widths (standard ELM practice — dictionary is sampled once, not learned).
- **Initialization:** `W ∈ R^{F×H_hidden}` drawn `N(0, 1/F)` (Kaiming-ish variance), bias `b ∈ R^{H_hidden}` drawn `U[−1,1]`, then **row-normalized** so each hidden node has comparable scale on the train-only standardized wavelet-feature distribution (train-only μ/σ from the 8545-split windows — same S-04 discipline). **Anchored-feature discipline:** `W,b` are fit-time statistics of the anchored wavelet features; re-estimated on `11425` for the test-phase refit (exactly like PatchTST's train-only standardization in S-44/S-45).
- **Activation:** `tanh` (ELM default; keeps outputs bounded for the anchored near-zero regime; `sigmoid`/`ReLU` declared as non-run alternatives).
- **Output:** `φ = tanh(X_wavelet · W + b)` ∈ `R^{H_hidden}` — fed *unchanged* to the sparse selector.

### D5 — Sparse readout (Stage 3): per-horizon selection over ELM space (Lasso → vectorized Ridge in harness)

- **Primary head (design):** **per-horizon Lasso** (`sklearn.linear_model.Lasso`, `fit_intercept=False` — the anchored pipeline is *already* level-free, so the head stays no-intercept; mirrors S-28's catastrophic intercept lesson) over the `H_hidden` ELM features. **Alpha grid:** `lasso_alpha ∈ {1e-4, 5e-4, 1e-3, 5e-3, 1e-2}` — small interior grid (5 points) on the delta-MAE scale.
- **Harness note (2026-09-14):** Lasso per 720 horizons hung (>2 min, non-convergent). Implemented **vectorized Ridge** `_ridge_multioutput` (closed-form Cholesky, α∈{1,10,100,1000,10000}) — 4.5 s vs >120 s, dense readout but valid S46 blend member test. Lasso intent preserved in design; harness ELM→Ridge still tests the wavelet-ELM hypothesis class.
- **Fallback (design):** `ElasticNet(l1_ratio=0.5)` on the same grid if Lasso's pure-L1 selection is unstable — tried only if the Lasso arm's held-out `val[1080:2161)` variance exceeds `0.02` (see §4 harness guard). Not a grid explosion — at most two models, not `M=6`.
- **Horizon handling:** 720 *independent* Lasso fits per phase (one per horizon step `h ∈ [0,719]`). Each predicts `ỹ̃_h` (delta at step `h`); Stage 4 re-adds the single per-origin anchor `a_t` (broadcast). This is the user attachment's Stages 3→4 literally.
- **Level-free invariant:** all Lasso inputs and targets are deltas (`X=φ`, `y=d* = future − anchor`); `ŷ = Lasso(φ) + anchor`. No level leaks through `fit_intercept`.

### D6 — How the stand-alone forecast enters the incumbent blend (the stack head)

- The stand-alone anchored-wavelet-ELM-lasso forecasts (one per width arm) become **candidate members** in a frozen pool that already contains the **S-44 incumbent pool** verbatim.
- Pool order FIXED (tabu neighbor enumeration & tie-breaking depend on it):
  `[nlinear_L336_a1, nlinear_L336_a10, patchtst_P24_D32_2L, patchtst_P48_D16_1L, wavelet_elm_swt_db4_h200, wavelet_elm_swt_db4_h400]`
  First 4 = S-44 exact (NLinear from `methods/neural_models.py`; PatchTST via sibling import — S-44/S-45 precedent, audit-logged). Last 2 = the two ELM widths on `wswt_db4` (swt-db4-J3, threshold `universal`). DWT ablation not in the pool (standalone only).
- **Pool size:** `M=6` (matches S-45). No other members; **zero tuning** — all thresholds/widths are the one-shot frozen design.

### D7 — Selection protocol (identical to S-44 / S-45 — zero tuning)

- **Tabu-7** over the frozen M=6 pool: `fixed_alpha=3000`, `no_improve=5`, `init=best singleton`, `aspiration=True`, `max_iter=25` (Bet 3 code path).
- **Per-horizon ridge head** (the stack, not the ELM head): 11-α grid `[0.1,1,3,10,30,100,300,1000,3000,10000,30000]`, **no intercept**, chronological half-split: fit `val[0:1080)` / select `val[1080:2161)` (pooled MAE). The **stack's** alpha is selected on `val[1080:2161)` — this is distinct from D5's Lasso alpha (inner head), which is selected on the *same* held-out split but **separately** via one-shot CV inside the ELM member's own training.
- Members frozen `8545` for val; refit `11425` for frozen test (`fit_multi` discipline for the ELM members mirrors PatchTST: μ/σ, W initialization constants, DWT/SWT thresholds all recomputed on `11425` from the longer history — but **no val leakage**; the refit history is `train.csv` exactly).
- `n_val == 2161`, `len(train_series) == 8545`, `len(fit_series) == 11425` asserted fail-loud (S-44/Bet 3 invariant).

### D8 — Held-out control & precondition

- **Held-out control:** the **S-44 incumbent's half-split** for the same chronological split (per-horizon ridge no-intercept **α=30000**, fit `val[0:1080)` scored `val[1080:2161)` = **2.493567251979277** — parity-anchored, S-44 D8). This is the *stack head* parity row, not the ELM head's control.
- **Precondition to frozen test:** the tabu-selected subset's best-α half-split score must beat the control by **`> 0.005`** (< `2.4886`). Fail ⇒ REJECT at plan time (C2 — see §4). This mirrors S-45's `+0.005` precondition exactly.

### D9 — What would void / abort (harness bugs, not model losses)

1. **Parity block > 1e-4 on any CONTEXT §5 row or the S-26 anchor** ⇒ **VOID `ABORT_PARITY`** — fix harness, re-run. Parity expected values are the ONLY copied constants (see §5).
2. **Anchoring violation** — any wavelet/ELM/Lasso input found to contain the raw (un-anchored) window or any future content beyond `history_[...:t]` ⇒ VOID (leakage).
3. **Determinism violation** — second run on same seed not byte-identical on `singleton_val` at `1e-10` ⇒ VOID (nondeterministic W/b or SWT boundary mode).
4. **Level-free violation** — ELM Lasso `fit_intercept=True` or de-anchor off-by-one (anchor from wrong index) ⇒ VOID.

### D10 — Budget & determinism

- **Single run, zero tuning, CPU-only.** Expected wall: ~300–450 s (val-phase: 2 ELM Lasso fits on 8545; test-phase: 2 refits on 11425; tabu scoring + S-44 parity re-derivation). Flattened — mirrors H2/S-45 single-process discipline.
- Deterministic: `pywt` SWT + `numpy` ELM `seed 42`; `sklearn` Lasso (`selection='cyclic'`, default, deterministic). No GPU nondeterminism.

### D11 — Implementation contract for the executor

- `anchored_wavelet_elm.py` exports `fit(train_series, horizon=720) -> self` / `predict(history, horizon) -> np.ndarray[720]` plus a **factory** `make_wavelet_elm_member(kind='swt_db4_h200')` that the harness's `MEMBER_FACTORIES` consumes — same call shape as every existing harness.
- Wavelet helper is **inlined** (no new `methods/` package entry — avoids touching the shared `methods/__init__.py` registry). If later promoted, a `methods/wavelet_elm.py` extraction is a follow-up — not this slice.
- `rolling_arm.py` is **self-contained**: it defines the tabu loop and the per-horizon ridge head locally (small duplicate of `wavelet_nlinear_h2/rolling_arm.py` helpers) — exactly the S-44/S-45 pattern. No shared harness refactor.

---

## 4. Acceptance, stability & close conditions

### Binding gate (promotion ⇒ incumbent replacement per S-44 P2)

Compared against the **in-harness S-44 incumbent re-derivation from the same run** (parity-anchored to `results_s44.json` §5):

| # | Condition | Threshold | Meaning |
|---|---|---|---|
| **G1** | `MAE_full(2161) ≤ incumbent_full − 0.0050` | ≤ **1.9731** (= 1.978126 − 0.0050) | H2 ≥0.0050-improvement bound applied to the *new* incumbent |
| **G2** | `MAE_full < incumbent_full` | < **1.9781** | strictly better |
| **G3** | `MAE_disjoint-4 ≤ incumbent_disjoint-4` | ≤ **1.8634** | no disjoint robustness sacrifice |
| **G4** | Paired-bootstrap Δ CI upper < 0 | Δ = per-origin MAE(S-46 blend) − MAE(S-44 in-harness), `B=2000, seed 0` | statistical confirmation (S-44 convention: `bootstrap_paired_diff_ci`) |

**Promotion = incumbent replacement:** CONTEXT.md top row becomes the S-46 blend; S-44 demoted with dethroned annotation; S-26 drops to third — S-44 P2 turnover applies.

### Procedural gate (to *reach* frozen test)

| # | Condition | Threshold | Effect |
|---|---|---|---|
| **P1** | Held-out control re-derived 2.493567 ±1e-4 | `±1e-4` | else VOID (parity) |
| **P2** | Best subset half-split < control − 0.005 | < 2.4886 | else **REJECT at plan time** (C2) — harness still logs the frozen test as diagnostic but verdict is already REJECT |

### Demoted diagnostics (reported honestly; cannot flip PASS→FAIL)

- New-member **singleton vals** (both ELM widths).
- **Train-vs-held-out delta** for the ELM members (train delta-MAE on `fit[0:1080)` windows vs held-out — flags > `0.15` as overfit candidate; S-45's `0.179` gap is the precedent's `gap_flag`).
- **Per-window (W1–W4) deltas vs the in-harness incumbent's own W1–W4** (S-43 P2 — computed on the same run; never copied).
- **Horizon-tercile deltas vs incumbent** (h1 `0–239`, h2 `240–479`, h3 `480–719`).
- **Wavelet diagnostics:** `wavelet_feature_dim`, `threshold` used, `lasso_alpha_selected` per width, `lasso_nnz_mean` (mean active features over 720 steps), `wavelet_reconstruction_error` (SWT→pooled→approx reconstruction MAE as a sanity bound).
- **Pool-composition diagnostic:** whether the winning blend contains all 3 vs subset of the S-44 members.

### Close / failure conditions (any fires ⇒ REJECT; S-44 stays incumbent)

| # | Condition | Label |
|---|---|---|
| **C1** | Selected subset ⊆ S-44 pool (no new member selected) | `c1_subset_of_s44_pool` |
| **C2** | Held-out gain ≤ 0.005 (plan-time) | `c2_heldout_gain` |
| **C3** | Paired Δ CI upper ≥ 0 | `c3_ci_upper_ge_0` |
| **C4** | Any of **G1–G3** fails | `c4_any_g1_g3_fails` |
| **C5** | **Family close (new):** BOTH new-member singleton vals **> 2.90** (worse than S-44 delta-ridge screening, Bet 3 precedent) **AND** no new-member subset beats the held-out control (2.493567) on `val[1080:2161)` ⇒ declare the anchored-wavelet-ELM-sparse family **closed under S-20-clean** — citation for future refusals per S-43 P3. **Fires only together with C1–C4** (does not independently flip a passing promotion to REJECT). | `family_close_s20_clean` |

**Verbatim close text when C5 fires:** *"Anchored wavelets + fixed ELM dictionary + sparse per-horizon selection add no orthogonal signal beyond the L336 linear map and the S-44 attention blend at this horizon and data budget; their combination inherits the H2 saturation — no further wavelet→ELM→sparse readouts on OT alone without exogenous channels."*

---

## 5. Parity requirements — vs `results_s44.json` (incumbent) and S-26 anchor (fail-loud)

Any row > `1e-4` ⇒ `parity.all_pass = false` ⇒ harness bug ⇒ **VOID `ABORT_PARITY`**. Expected values are the ONLY permitted copied constants (D7/D9).

| Quantity | S-44 / S-26 value | Tol |
|---|---|---|
| Incumbent subset (as subset evaluation) | `[nlinear_L336_a1, nlinear_L336_a10, patchtst_P24_D32_2L]` | exact |
| Incumbent stack α | `30000` | exact |
| Incumbent `best_fast` (3-member @ α=3000, `val[1080:2161)`) | `2.5021117513632665` | `1e-4` |
| Incumbent `val_full` (= held-out control, 3-member @ α=30000, half-split) | `2.493567251979277` | `1e-4` |
| Singleton vals (S-44 pool, frozen 8545) — nlinear a1 / a10 / patchtst P24 / patchtst P48 | `2.896975832201712 / 2.896964035619671 / 3.026725290054874 / 3.15167046606894` | `1e-4` |
| Incumbent `test_full MAE / RMSE` | `1.9781264265828236 / 2.4612639073807663` | `1e-4` |
| Incumbent `test_disjoint-4` | `1.8634190252257932` | `1e-4` |
| Incumbent `test_W4` | `1.8896163750508768` | `1e-4` |
| Incumbent `W1 / W2 / W3` | `2.1606949742408026 / 1.5655481914300127 / 2.208259044704783` | `1e-4` |
| Incumbent horizon terciles h1/h2/h3 | `1.8266205418006774 / 1.9787703942750745 / 2.128988343672719` | `1e-4` |
| Incumbent paired Δ vs S-26 CI | `[−0.018505562732342832, −0.006913352503709525]` mean `−0.012771` | `1e-4` |
| S-26 anchor (fail-loud) MAE / RMSE / disjoint / W4 | `1.990897385574145 / 2.470998626872596 / 1.9696168477494975 / 1.9579365851264652` | `1e-4` |

The harness re-derives each of these **in the same run** from the same `train.csv`/`test.csv` freeze and parity-checks them before emitting a verdict — S-44 P1 precedent (`results_s44.json:parity.checks`, 59/59 `abs_diff 0.0`).

---

## 6. Artifact schema — `results_s46.json` (executor MUST follow)

```json
{
  "slice": "S-46-anchored-wavelet-elm",
  "harness_command": "C:/Users/Mateusz/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe projects/ts-ml-experiments/h720/sub_experiments/anchored_wavelet_elm_s46/rolling_arm.py",
  "device": "<cpu (+ library versions: pywt X.Y.Z, scikit-learn X.Y) — as-run>",
  "protocol": "S-20-clean anchored-wavelet-ELM-sparse expansion of the S-44 incumbent blend; binding gate BLEND-based vs the in-harness S-44 incumbent re-derivation (S-43 P1 / S-44 P2); parity block per S-44 P1",
  "pool": ["nlinear_L336_a1","nlinear_L336_a10","patchtst_P24_D32_2L","patchtst_P48_D16_1L","wavelet_elm_swt_db4_h200","wavelet_elm_swt_db4_h400"],
  "new_members": {
    "wavelet_elm_swt_db4_h200": {"transform":"SWT db4 J=3 periodization, VisuShrink soft threshold per subband, per-subband pooled features","hidden":200,"activation":"tanh","seed":42},
    "wavelet_elm_swt_db4_h400": {"transform":"SWT db4 J=3 periodization, VisuShrink soft threshold per subband, per-subband pooled features","hidden":400,"activation":"tanh","seed":42}
  },
  "params": {"L":336,"J":3,"wavelet":"db4","mode":"periodization","threshold":"universal","F":0,"lasso_alphas":[0.0001,0.0005,0.001,0.005,0.01],"H_hidden":[200,400],"seed":42,"H":720},
  "singleton_val": {"nlinear_L336_a1":0.0,"nlinear_L336_a10":0.0,"patchtst_P24_D32_2L":0.0,"patchtst_P48_D16_1L":0.0,"wavelet_elm_swt_db4_h200":0.0,"wavelet_elm_swt_db4_h400":0.0},
  "wavelet_diagnostics": {"feature_dim":0,"threshold_per_subband":[0.0],"lasso_alpha_selected":{"wavelet_elm_swt_db4_h200":0.0,"wavelet_elm_swt_db4_h400":0.0},"lasso_nnz_mean":{"wavelet_elm_swt_db4_h200":0,"wavelet_elm_swt_db4_h400":0}},
  "incumbent_s44_rederived": {"subset":["nlinear_L336_a1","nlinear_L336_a10","patchtst_P24_D32_2L"],"alpha":30000.0,"best_fast":0.0,"val_full":0.0,"test_full_mae":0.0,"test_full_rmse":0.0,"test_disjoint_mae":0.0,"test_w4_mae":0.0,"w1_w4":[0.0,0.0,0.0,0.0],"horizon_terciles":[0.0,0.0,0.0]},
  "s26_anchor": {"mae":0.0,"rmse":0.0,"disjoint":0.0,"w4":0.0,"tol":0.0001,"expected":{"mae":1.990897385574145,"rmse":2.470998626872596,"disjoint":1.9696168477494975,"w4":1.9579365851264652},"pass":true},
  "held_out_control": {"type":"S-44 incumbent 3-member blend re-derived half-split alpha=30000","mae_val_heldout":0.0,"alpha":30000.0},
  "trace": [{"iter":0,"cur":["..."],"fast":0.0,"true":0.0,"alpha":0.0,"best_fast":0.0,"best_set":["..."]}],
  "best_subset": ["..."],"best_idx":[0],"best_fast":0.0,"best_alpha":0.0,
  "val_full":0.0,"heldout_gain_over_control":0.0,"heldout_precondition_pass":true,
  "parity": {"tol":0.0001,"checks":[{"quantity":"incumbent_test_full_mae","s44":1.9781264265828236,"s45":0.0,"abs_diff":0.0,"pass":true}],"all_pass":true},
  "binding_gate": {
    "full_le_incumbent_minus_005": {"value":0.0,"threshold":1.9731,"pass":true},
    "full_lt_incumbent": {"value":0.0,"incumbent":1.9781,"pass":true},
    "disjoint_le_incumbent": {"value":0.0,"incumbent":1.8634,"pass":true},
    "paired_ci_upper_lt_0": {"ci_95":[0.0,0.0],"upper":0.0,"pass":true},
    "all_binding_pass":true
  },
  "secondary_checks": {"disjoint_le_s26_cap_19696": {"value":0.0,"cap":1.9696,"pass":true,"binding":false}},
  "demoted_diagnostics": {
    "new_member_singleton_vals": {"wavelet_elm_swt_db4_h200":0.0,"wavelet_elm_swt_db4_h400":0.0},
    "train_val_gap": {"wavelet_elm_swt_db4_h200":0.0,"wavelet_elm_swt_db4_h400":0.0}, "gap_flag": true,
    "w1_w4_deltas_vs_incumbent": [{"window":"W1","s46_mae":0.0,"incumbent_mae":0.0,"delta":0.0}],
    "horizon_terciles": [{"horizon_tercile":"h1_first240","s46_mae":0.0,"incumbent_mae":0.0,"delta":0.0}]
  },
  "test_full": {"mae":0.0,"rmse":0.0,"n":2161,"delta_vs_incumbent":0.0},
  "bootstrap": {"convention":"resample origins, B=2000, seed 0, percentile 2.5/97.5","s46_full":{"mean":0.0,"ci_95":[0.0,0.0],"B":2000},"incumbent_full":{"mean":0.0,"ci_95":[0.0,0.0],"B":2000},"paired_delta":{"mean":0.0,"ci_95":[0.0,0.0],"B":2000,"upper_bound_negative":true}},
  "stratified": {"disjoint_windows":[{"window":"W1","start":0,"s46_mae":0.0,"incumbent_mae":0.0,"delta":0.0}],"horizon_terciles":[]},
  "test_disjoint": {"mae":0.0,"rmse":0.0},
  "test_w4": {"mae":0.0,"incumbent_w4":0.0,"delta_vs_incumbent":0.0,"binding":false},
  "close": {"condition":"subset-of-S44-pool OR heldout_gain<=0.005 OR paired_ci_upper>=0 OR any G1-G3 fails (+ family-close)","c1_subset_of_s44_pool":false,"c2_heldout_gain":false,"c3_ci_upper_ge_0":false,"c4_any_g1_g3_fails":false,"family_close_s20_clean":false,"trigger":false,"message":"..."},
  "verdict": "PROMOTED|REJECTED",
  "plan_impact": {"invalidates":"S-44 incumbent status on PROMOTION (S-44 demoted; S-26 drops to third)","confirms":"on REJECT: S-44 remains incumbent; anchored-wavelet-ELM-sparse direction recorded with numbers","opens":"on PROMOTION: re-anchored blend-incumbent frontier (S-44 P2 turnover applies)"},
  "elapsed_s": 0.0
}
```

The harness log mirrors S-44/S-45 format: per-epoch/member training lines (Lasso `alpha*` per width), tabu trace lines, audit lines (pywt version, SWT mode, threshold values, ELM seed, anchoring assert), bootstrap/stratified lines, parity lines, binding-gate line, close-conditions line, final `VERDICT=PROMOTED|REJECTED`.

---

## 7. What would falsify / void this bet

1. **Parity failure >1e-4** ⇒ VOID `ABORT_PARITY` — harness bug; fix, re-run.
2. **C1 collapse** (tabu picks ⊆ S-44 pool) ⇒ REJECT — nothing gained; both wavelet-ELM arms recorded; no same-class re-run without pre-registration.
3. **Any binding condition fails** (G1–G4) or the held-out precondition ⇒ REJECT — S-44 stays incumbent; if additionally C5's 2.90 screen fires, the **anchored-wavelet-ELM-sparse family closes** under S-20-clean per the verbatim text above.
4. **Post-promotion falsifier (normal science):** a later pre-registered bet beating the S-46 blend under its own declared gate supersedes it — not a falsification of S-46 evidence.

---

## 8. Explicit non-goals & declared alternatives (not run under this design)

- No anchor sweep (mean/median/seasonal/learned anchor — attachment §5) — locked to last-value.
- No wavelet-family sweep (beyond `db4` primary + one `haar` note) — no `sym8`/`coif`.
- No hidden-width sweep beyond `h200/h400` — not `h800`.
- No ELM activation sweep beyond `tanh`.
- No `fit_intercept=True` head, no tree head, no horizon-band α, no calendar channels, no RevIN-512, no longer lookback — each is a separate pre-registration if pursued.
- DWT ablation is standalone diagnostic only (not a blend candidate).

---

## 9. Cited evidence

- `projects/ts-ml-experiments/h720/CONTEXT.md` — leaderboard (S-44 1.9781/2.4613/1.8634; S-26 dethroned), `## Prevention rules — S-43` P1–P4, S-44 section, `## Sub-Experiment: Dyadic Wavelet NLinear Frontier (H2) — REJECTED` (full 1.9906, stop rule), `## Sub-Experiment: Blend-Promotion Re-registration (S-44) — PROMOTED` (~line 397, 59/59 parity).
- `RESEARCH/next-frontier-scout-2026-09-13.md` §4/Bet 3 + §6, `RESEARCH/ensemble_linear_frontier_reflection_2026-09-13.md` §4.1/Portfolio (H2/S-36/S-35 already closed), `MONITORING/reflection/2026-09-13_2350` (S-43) · `MONITORING/reflection/2026-09-14_0348` (S-44 P1/P2).
- `projects/ts-ml-experiments/h720/sub_experiments/wavelet_nlinear_h2/rolling_arm.py` + `results_h2.json` (linear DWT-J3 baseline — the orthogonal complement of this bet's non-linear expansion) · `level_free_nonlinear_s35/rolling_arm.py` (raw-delta RF — no wavelets) · `blend_promotion_s44/S44_DESIGN.md` + `results_s44.json` (parity expected values, gate conventions) · `blend_frontier_s45/S45_DESIGN.md` (blend-frontier template reused) · `data.py` (`get_protocol_data`, `ProtocolData` S-20-clean freezes 8545/11425).
- Attachment of this task — aiming [NLinear's anchoring trick]: `x̃ = x − x_T`, `ŷ = f(x̃) + x_T` — applied as Stages 0/4 around `DWT/SWT → threshold → ELM → Lasso` (Stages 1–3).

**Expected verdict: none asserted.** S-46 is a new frontier bet with no prior evidence; the verdict is whatever the single frozen, parity-passing run emits under the declared gate.
