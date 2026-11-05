"""Cross-family ensemble (S-08, h720): ELM + kNN + seasonal-naive.

Blends the three structurally-diverse strongest families with
non-negative, sum-1 weights fit on VALIDATION windows only (the
S-02 convention: 2,161 stride-1 origins over the 2,880-row
validation segment; per-origin history = all rows strictly before
the scored window; members are frozen — fit on the full train+val
series exactly once, no refit inside the weight search). The test
region is never consulted for weighting (``fit`` receives only the
train+validation series).

Weight solver — TWO objectives, both fit on validation windows
only, both deterministic (no RNG):

1. PRIMARY ``weights_`` — squared-error blend (the slice Goal is
   to blend the three families; classic convex surrogate):
   closed-form equality-constrained solve + Euclidean simplex
   projection (Duchi et al. 2008).
2. DIAGNOSTIC ``mae_weights_`` — the L1 optimum over the simplex,
   i.e. the acceptance metric itself (validation rolling MAE):
   convex piecewise-linear objective, pairwise coordinate descent
   + exact 1-D ternary line search → global optimum. On this data
   it degenerates to a VERTEX (single best member): no non-trivial
   blend beats the best member in validation MAE. Recorded so the
   acceptance boolean's outcome can be attributed to the data,
   not to the choice of surrogate.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np

from .base import BaseForecaster
from .baselines import Persistence, seasonal_forecast
from .knn_models import HeuristicLagKNN
from .neural_models import HeuristicLagELM


def _simplex_project(v: np.ndarray) -> np.ndarray:
    """Euclidean projection of ``v`` onto the probability simplex."""
    u = np.sort(v)[::-1]
    css = np.cumsum(u)
    rho_candidates = u + (1.0 - css) / np.arange(1, len(v) + 1)
    rho = np.max(np.where(rho_candidates > 0, np.arange(1, len(v) + 1), 0))
    theta = (css[rho - 1] - 1.0) / rho
    return np.maximum(v - theta, 0.0)


def _ternary_min(f, lo: float, hi: float, tol: float = 1e-9) -> float:
    """Deterministic ternary search min of convex piecewise-linear f
    on [lo, hi]; returns the midpoint of the final bracket."""
    while hi - lo > tol:
        m1 = lo + (hi - lo) / 3.0
        m2 = hi - (hi - lo) / 3.0
        if f(m1) <= f(m2):
            hi = m2
        else:
            lo = m1
    return 0.5 * (lo + hi)


def _minimize_mae_weights(
    P: np.ndarray, A: np.ndarray, tol: float = 1e-9, max_sweeps: int = 10
) -> tuple[np.ndarray, float]:
    """Global minimizer of validation rolling MAE over the simplex.

    f(w) = mean |R w| over all (origin, horizon) cells, R = member
    residuals, is convex; pairwise coordinate descent — move mass
    between members i<j along the edge with an exact 1-D ternary
    line search — converges to the global optimum. Deterministic.
    """
    n_members = P.shape[1]
    # Residual matrix in CELL order: one row per (origin, horizon
    # step) cell, one column per member — R[cell, j] = residual of
    # member j at that cell. (P - A) has shape (n, m, H); a direct
    # reshape(-1, m) would SCRAMBLE axes (C-order flattening mixes
    # member index with horizon step), so transpose to (n, H, m)
    # first. This exact mistake silently produced homogeneous
    # per-member MAEs (~3.09) and garbage weights before it was
    # caught by the stateless-daily validation sensor.
    R = (P - A[:, None, :]).transpose(0, 2, 1).reshape(-1, n_members)

    def f(w: np.ndarray) -> float:
        return float(np.mean(np.abs(R @ w)))

    w = np.full(n_members, 1.0 / n_members)
    best = f(w)
    for _ in range(max_sweeps):
        improved = False
        for i in range(n_members):
            for j in range(i + 1, n_members):
                d = np.zeros(n_members)
                d[i], d[j] = 1.0, -1.0
                # feasible step range: w_i + a >= 0, w_j - a >= 0
                lo, hi = -w[i], w[j]

                def fa(a: float, _d=d, _w=w) -> float:
                    return f(_w + a * _d)

                a = _ternary_min(fa, lo, hi, tol)
                cand = w + a * d
                val = f(cand)
                if val < best - 1e-12:
                    w, best = cand, val
                    improved = True
        if not improved:
            break
    return w, best


class CrossFamilyEnsemble(BaseForecaster):
    """ELM + kNN + seasonal-naive blend, validation-weighted (S-08).

    Members are the canonical strongest per family under the rolling
    protocol: ``elm_h64_full_fastlags`` (HeuristicLagELM h64, full
    history, fast lags), ``knn_q3_k32_recent10`` (HeuristicLagKNN q3
    k32, recent 10%), and daily seasonal-naive (lag 24).
    """

    #: (name, factory) — members are constructed fresh in fit()
    MEMBERS: tuple[tuple[str, object], ...] = (
        ("elm_h64_full_fastlags", lambda: HeuristicLagELM(
            hidden_dim=64, history_fraction=1.0, delays=(1, 2, 3, 6, 12))),
        ("knn_q3_k32_recent10", lambda: HeuristicLagKNN(
            q=3, neighbors=32, history_fraction=0.1,
            delays=(1, 2, 3, 6, 12, 24))),
        ("daily", None),  # functional member, handled separately
    )

    def __init__(self, validation_rows: int = 2880, horizon: int = 720,
                 weight_stride: int = 1):
        self.validation_rows = validation_rows
        self.horizon = horizon
        self.weight_stride = weight_stride

    def _daily_pred(self, hist: np.ndarray) -> np.ndarray:
        return seasonal_forecast(hist, self.horizon_, "daily")

    def _member_pred(self, idx: int, hist: np.ndarray) -> np.ndarray:
        name, factory = self.MEMBERS[idx]
        if factory is None:
            return self._daily_pred(hist)
        model = self.models_[idx]
        model.history_ = hist
        return np.asarray(model.predict())

    # -- fit --------------------------------------------------------------
    def fit(self, y: Iterable[float], *, horizon: int,
            target_index: int = 0) -> "CrossFamilyEnsemble":
        series = np.asarray(list(y), dtype=float)
        if series.ndim != 1 or not np.isfinite(series).all():
            raise ValueError("ensemble fit requires a finite 1-D series")
        self._check_horizon(horizon)
        self.horizon_ = int(horizon)

        # Structural anti-leakage note: the weight search sees ONLY
        # the fit series (train + validation rows — 11,425 in the
        # canonical protocol); no sanctioned runner ever hands test
        # rows to this method.
        train_val_end = len(series)

        # 1) Freeze members on the FULL fit history (train+validation
        #    rows — the canonical frozen-fit protocol; identical to
        #    every other model in the project).
        self.models_ = []
        for name, factory in self.MEMBERS:
            if factory is None:
                self.models_.append(None)
            else:
                m = factory()
                m.fit(series, horizon=horizon)
                self.models_.append(m)

        # 2) Weight search on validation windows ONLY (S-02
        #    convention): the validation segment is the LAST
        #    ``validation_rows`` rows of the fit series; origins roll
        #    stride-1 with history = all rows strictly before the
        #    scored window. Members stay frozen (no refit).
        val_start = train_val_end - self.validation_rows
        if val_start < 0:
            raise ValueError(
                f"validation_rows={self.validation_rows} exceeds the fit "
                f"series length {train_val_end} — the weight search needs "
                f"a non-negative train prefix before the validation segment"
            )
        val = series[val_start:train_val_end]
        n_origins = len(val) - horizon + 1  # 2,161 for 2,880 rows
        if n_origins < 1:
            raise ValueError(
                f"validation segment ({self.validation_rows} rows) too short "
                f"for horizon {horizon} — no weight-search origins"
            )
        strides = range(0, n_origins, self.weight_stride)
        preds, actuals = [], []
        for t in strides:
            hist_end = val_start + t
            hist = series[:hist_end]
            actual = val[t : t + horizon]
            preds.append([self._member_pred(i, hist) for i in range(3)])
            actuals.append(actual)
        P = np.asarray(preds)   # (n, 3, H) — VALIDATION predictions only
        A = np.asarray(actuals)  # (n, H)
        self._weight_search_saw_test_ = False  # structurally impossible

        # 3) PRIMARY weights — squared-error blend of the three
        #    families, fit on VALIDATION windows only (the slice Goal
        #    is to blend the families, not to re-select one):
        #    closed-form equality-constrained solve, then Euclidean
        #    simplex projection (Duchi et al. 2008).
        R = (P - A[:, None, :]).transpose(0, 2, 1).reshape(-1, 3)
        G = R.T @ R / len(R)
        ones = np.ones(3)
        try:
            w_dir = np.linalg.solve(G + 1e-9 * np.eye(3), ones)
            w_dir = w_dir / np.sum(w_dir)
        except np.linalg.LinAlgError:
            w_dir = ones / 3.0
        w = _simplex_project(w_dir)
        if not np.isclose(w.sum(), 1.0):
            w = ones / 3.0
        self.weights_ = w

        # DIAGNOSTIC weights — the L1 optimum over the simplex (the
        # acceptance metric itself): convex objective, pairwise
        # coordinate descent + exact ternary line search — global
        # and deterministic. On this data it degenerates to the kNN
        # vertex [0, 1, 0]: no non-trivial blend beats the best
        # member in validation MAE. Recorded so the acceptance
        # boolean's outcome can be attributed to the data, not to
        # the choice of surrogate.
        self.mae_weights_ = _minimize_mae_weights(P, A)[0]

        # Cheap re-scoring surface for downstream diagnostics: the
        # validation predictions/actuals the weights were fit on.
        self._val_P = P
        self._val_A = A

        # 4) Persist members with the full fit history for predict().
        self.history_ = series
        self._fitted = True
        return self

    def predict(self) -> np.ndarray:
        self._check_fitted()
        hist = self.history_
        out = np.zeros(self.horizon_)
        for i in range(3):
            p = self._member_pred(i, hist)
            out += self.weights_[i] * p
        return out
