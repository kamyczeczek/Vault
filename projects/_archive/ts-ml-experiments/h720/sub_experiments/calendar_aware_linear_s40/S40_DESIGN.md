---
type: Concept
title: S40_DESIGN
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# S-40 — Calendar-Aware Level-Free Linear Ensemble for ETTh1 H=720

**Lane:** FRONTIER — exogenous calendar features in a level-free linear pool.
**Status:** DESIGN / skeleton implementation.
**Protocol:** S-20-clean (train 8545 fit, chronological val split 1080/1081, test 11425 refit, 2161 rolling origins).
**Target:** full rolling MAE < 1.9909 (S-26 incumbent), disjoint-4 < 1.9696.
**Zero-tuning:** no grid search over calendar feature combinations; all calendar features always included.

---

## 1. Feature Spec

All features are derived from the origin timestamp only (strictly past data).

### 1.1 Hour-of-Day sin/cos
```python
hod = (timestamp.hour + timestamp.minute / 60.0) / 24.0
hour_sin = sin(2π * hod)
hour_cos = cos(2π * hod)
```
**Rationale:** hourly demand cycles are non-linear in raw hour index; sin/cos preserves periodicity and avoids boundary discontinuity. Two features instead of 24 one-hots keeps dimension low and avoids the linear-independence problem with anchoring.

### 1.2 Day-of-Week sin/cos
```python
dow = timestamp.weekday() / 7.0   # Monday=0 .. Sunday=6
dow_sin = sin(2π * dow)
dow_cos = cos(2π * dow)
```
**Rationale:** ETTh1 is electricity transformer temperature; weekday/weekend patterns matter. sin/cos again avoids boundary artifacts.

### 1.3 Month sin/cos
```python
month = (timestamp.month - 1) / 12.0
month_sin = sin(2π * month)
month_cos = cos(2π * month)
```
**Rationale:** seasonal temperature effects (summer vs winter) drive transformer load.

### 1.4 Holiday flag
```python
holiday_flag = 1.0 if timestamp.date() in chinese_holidays else 0.0
```
**Rationale:** ETTh1 covers 2016-07-01 → 2018-06-26, which includes Chinese public holidays (Spring Festival, Labor Day, National Day, etc.). Holidays shift electricity load patterns.
**Source:** `holidays` package, `country_holidays('CN', years=[2016, 2017, 2018])`.
**Edge handling:** non-CN holidays (e.g., New Year's Day) also flag 1.0 — any calendar outlier is a useful signal; we do not tune which holidays matter.

**Total calendar features per origin: 7** (hour sin/cos + dow sin/cos + month sin/cos + holiday flag).
**Broadcast across horizon:** the 7 calendar features are repeated identically for all 720 horizon steps (origin time is the forecasting anchor; horizon-shifted calendar would leak future information).

---

## 2. Member Pool

We extend the S-26 incumbent pool with calendar-aware variants. The S-26 pair is retained as a control.

### 2.1 Calendar-Aware Member Design

**Core idea:** a linear Ridge regressor on the **concatenation of**:
- an anchor-differenced OT window of length L (same as S-26),
- the 7 calendar features broadcast across all 720 horizon steps.

The model predicts level-free deltas `(target_h - anchor)` for each horizon step h. Anchor is the last observed OT value at origin (identical to S-26 NLinear). No intercept on the horizon ridge head (S-20/S-28 scar).

**Why this is a *new* member type, not a modification:** the stacking head in S-20 operates on member predictions, not features. Calendar features are injected at the *member* level — each calendar-aware member produces its own 720-step forecast, and the per-horizon ridge stack combines member predictions as before. This keeps the S-20 stacking interface intact.

**Feature matrix for member j at origin t:**
```
X_j[t] = [ (OT[t-L : t] - anchor).reshape(-1) ,  calendar[7,] ]
         └────────── L anchor-differenced OT values ──────────┘   └ broadcast ─┘
```
Shape: `(n_origins, L + 7)` → Ridge → `(n_origins, H)`.

**Level-free guarantee:** target is `OT[t : t+H] - anchor`; predict returns `pred + anchor`. Calendar features are not level-dependent (they are timestamp-derived), so they do not re-introduce level. The last-row subtraction anchor is identical to S-26 NLinear.

### 2.2 Pool Membership

The full S-40 pool has **8 members**:

| # | Name | L | α | Calendar |
|---|------|---|---|----------|
| 0 | `nlinear_L336_a1` | 336 | 1 | **no** (S-26 control) |
| 1 | `nlinear_L336_a10` | 336 | 10 | **no** (S-26 control) |
| 2 | `nlinear_L336_a1_cal` | 336 | 1 | **yes** |
| 3 | `nlinear_L336_a10_cal` | 336 | 10 | **yes** |
| 4 | `nlinear_L96_a1_cal` | 96 | 1 | **yes** |
| 5 | `nlinear_L720_a1_cal` | 720 | 1 | **yes** |
| 6 | `dlinear_L96_a0_cal` | 96 | 0 | **yes** (DLinear decomposition + calendar) |
| 7 | `rlinear_L336_a0_cal` | 336 | 0 | **yes** (RevIN + calendar) |

**Selection rationale:**
- Members 0–1: S-26 control pair; if the calendar-aware pool regresses, we know exactly where the loss came from.
- Members 2–3: direct calendar extension of the S-26 pair, isolating calendar's contribution.
- Member 4: short lookback with calendar — tests whether calendar alone can substitute for long history.
- Member 5: long lookback with calendar — tests whether calendar adds orthogonal signal to long memory.
- Member 6: DLinear decomposition + calendar — tests whether calendar benefits from trend/seasonal separation.
- Member 7: RLinear RevIN + calendar — tests whether calendar benefits from window standardization.

**Zero-tuning enforcement:** every calendar-aware member uses the **same** 7-feature calendar vector. No feature selection, no holiday subset, no per-member calendar mask. The calendar feature set is fixed and identical for all calendar-aware members.

---

## 3. Calendar Feature Engineering

### 3.1 Source Data

The raw `ETTh1.csv` has a `date` column in ISO format `YYYY-MM-DD HH:MM:SS`. No external holiday dataset is required beyond the `holidays` Python package.

### 3.2 Derivation Function

```python
def calendar_features(timestamp: datetime) -> np.ndarray:
    """7-dim calendar feature vector for origin timestamp."""
    hod = (timestamp.hour + timestamp.minute / 60.0) / 24.0
    dow = timestamp.weekday() / 7.0
    month = (timestamp.month - 1) / 12.0
    holiday = 1.0 if timestamp.date() in CHINESE_HOLIDAYS else 0.0
    return np.array([
        sin(2π * hod), cos(2π * hod),
        sin(2π * dow), cos(2π * dow),
        sin(2π * month), cos(2π * month),
        holiday
    ], dtype=float)
```

### 3.3 Precomputation

Calendar features are precomputed once for all 17,420 raw timestamps and stored in `calendar_features.npy` (shape `(17420, 7)`). This is deterministic and takes <1 second. The rolling arm slices origin-specific calendar rows from this array; no recomputation per origin.

### 3.4 Anti-Leakage

Calendar features for origin `t` are computed from `timestamp[t]` only. No future calendar information is ever included. The `holidays` lookup uses `timestamp.date()` which is the origin date — no horizon-shifted holidays.

---

## 4. Calendar-Aware Member Implementation

Each calendar-aware member inherits from the existing `BaseForecaster` and overrides `fit`/`predict` to include calendar features.

**Key design choices:**
1. **Anchor:** last OT value in the lookback window, identical to S-26 NLinear.
2. **Level-free target:** `Y = OT[origin : origin+H] - anchor`.
3. **Calendar broadcast:** `calendar[origin]` is tiled `H` times and concatenated to every training row's OT window features. At predict time, the origin's calendar features are broadcast identically.
4. **No intercept on the Ridge head:** same S-20/S-28 scar avoidance.
5. **DLinear variant:** decomposition into trend (moving average) + seasonal (remainder), then calendar concatenated to the seasonal component's anchor-differenced window. Final prediction = trend_forecast + seasonal_forecast + anchor. The trend component is the trailing moving average projected forward; the seasonal component is the calendar-aware Ridge on the residual window.
6. **RLinear variant:** window standardized (mean/std), then calendar concatenated to standardized window. Predict de-standardizes output.

---

## 5. Protocol

Identical to S-20-clean:
1. **Members frozen on train 8,545** — fit all 8 members on `train.csv[:8545]`.
2. **Val predictions** — collect P `(2161, 8, 720)` from `fit_history` (train+val) using origin starts `8545 .. 8545+2160-H`.
3. **Chronological alpha selection** — fit per-horizon ridge on val origins `[0, 1080)`, select α on `[1080, 2161)` from 11-α grid `[0.1, 1, 3, 10, 30, 100, 300, 1000, 3000, 10000, 30000]`.
4. **Refit stack on ALL val** with selected α.
5. **Frozen test** — members re-fit on full 11,425; stack applied to test predictions; 2161 rolling origins.
6. **Test never consulted** for member selection or α choice.

---

## 6. Acceptance Criteria

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| **Primary (full MAE)** | < 1.9909 | Must beat S-26 |
| **Stability (disjoint-4)** | < 1.9696 | S-26 disjoint-4 cap |
| **Transfer guard** | val_full - test_full ∈ [-0.02, +0.02] | S-36 val→test vol-regime shift scar |
| **Calendar ablation** | at least one calendar-aware member must beat its no-calendar twin | otherwise calendar adds zero signal |
| **Determinism** | byte-identical re-run | no random projections |

**Rejection criteria (any fires → REJECT):**
- full MAE ≥ 1.9909 (no improvement over S-26).
- disjoint-4 > 1.9696 (stability guard fails).
- transfer delta > 0.02 (val→test divergence).
- non-deterministic results across re-runs.

**Close condition:**
- If rejected, the specific scar is recorded (e.g., "calendar features collapsed to OT-only linear combination," "calendar-aware members overfit val calendar regime," or "S-26 pair dominates regardless of calendar").
- If all 8 calendar-aware members individually underperform their no-calendar twins, the univariate linear family is declared saturated under exogenous calendar features, and the frontier moves to non-linear readouts or protocol changes.

---

## 7. Skeleton File Map

- `calendar_aware_linear_s40/S40_DESIGN.md` — this file.
- `calendar_aware_linear_s40/rolling_arm.py` — skeleton with TODOs.
- `calendar_aware_linear_s40/calendar_features.py` — calendar feature engineering module.
- `calendar_aware_linear_s40/calendar_members.py` — calendar-aware forecaster classes.
- `CONTEXT.md` — S-40 section appended.
