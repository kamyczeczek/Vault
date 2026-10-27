"""BigDict-LASSO: causal filter-bank features with sparse direct forecasting.

The first LASSO experiment in this workspace standardized each filter row in
isolation, changed the feature width when PyWavelets rejected an odd-length
window, and predicted one target step per sliding context.  That made the
reported sparsity result difficult to reproduce and was not a direct
multi-horizon forecaster.  This version keeps the experiment's core idea,
but makes the protocol explicit:

* fixed-length anchored windows and a fixed feature schema;
* feature scaling learned from training windows only;
* target scaling learned from training windows only;
* a shared multi-task LASSO fit over all requested forecast horizons;
* a direct prediction from the latest causal history, with no future data
  used to construct features or choose regularization.

``use_expansion`` is available for the quadratic/interactions ablation, but
is disabled by default because it expands an already large dictionary.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np

try:
    import pywt
    _HAS_PYWT = True
except Exception:  # pragma: no cover
    pywt = None

try:
    from sklearn.linear_model import MultiTaskLasso
    _HAS_SKLEARN = True
except Exception:  # pragma: no cover
    MultiTaskLasso = None
    _HAS_SKLEARN = False


def _causal_ma(x: np.ndarray, win: int) -> np.ndarray:
    if win <= 1:
        return x.copy()
    cumulative = np.cumsum(np.concatenate(([0.0], x)))
    out = np.empty_like(x)
    for i in range(len(x)):
        start = max(0, i - win + 1)
        out[i] = (cumulative[i + 1] - cumulative[start]) / (i - start + 1)
    return out


def _ema(x: np.ndarray, alpha: float) -> np.ndarray:
    out = np.empty_like(x)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = alpha * x[i] + (1.0 - alpha) * out[i - 1]
    return out


def _resample(values: np.ndarray, length: int) -> np.ndarray:
    values = np.asarray(values, dtype=float).ravel()
    if len(values) == length:
        return values.astype(float)
    if len(values) == 1:
        return np.repeat(values, length).astype(float)
    old = np.linspace(0.0, 1.0, len(values))
    new = np.linspace(0.0, 1.0, length)
    return np.interp(new, old, values).astype(float)


def _filter_bank(
    xa: np.ndarray,
    *,
    levels: int = 2,
    profile: str = "full",
    wavelet_bank: Tuple[str, ...] = ("db4", "sym4"),
) -> List[np.ndarray]:
    """Return fixed-width groups of length ``len(xa)``.

    ``full`` retains the original approximation/detail ablation schema.
    ``approx`` drops detail bands, which is the robust configuration for
    general forecasting; ``compact`` retains only identity, MA, and EMA.
    """
    profile = str(profile).lower().replace("-", "_")
    if profile not in {"full", "approx", "compact"}:
        raise ValueError("profile must be full, approx, or compact")
    length = len(xa)
    feats: List[np.ndarray] = [xa]
    feats.extend(_causal_ma(xa, w) for w in (3, 6, 12, 24))
    feats.extend(_ema(xa, a) for a in (0.3, 0.7))
    d1 = np.concatenate(([0.0], np.diff(xa)))
    feats.extend((d1, np.concatenate(([0.0], np.diff(d1)))))
    feats.extend((xa - _causal_ma(xa, 12), xa - _causal_ma(xa, 24)))
    if profile == "compact":
        return feats[:7]
    if profile == "linear":  # accepted as a convenient alias
        return feats

    approx: List[np.ndarray] = []
    details: List[np.ndarray] = []
    if _HAS_PYWT:
        for wav in wavelet_bank:
            try:
                level = max(1, min(int(levels), pywt.dwt_max_level(length, wav)))
                swt = pywt.swt(xa, wav, level=level)
                for lev_idx in range(level):
                    c_a, c_d = swt[lev_idx]
                    if len(c_a) == length:
                        approx.append(c_a.astype(float))
                    if len(c_d) == length:
                        details.append(c_d.astype(float))
                continue
            except Exception:
                pass
            try:
                level = max(1, min(int(levels), pywt.dwt_max_level(length, wav)))
                coeff = pywt.wavedec(xa, wav, mode="symmetric", level=level)
                # wavedec order: [cA_n, cD_n, ..., cD_1].
                for index, values in enumerate(coeff):
                    target = approx if index % 2 == 0 else details
                    target.append(_resample(values, length))
            except Exception:
                continue
    if profile == "approx":
        return feats + approx
    return feats + approx + details


def _interaction_pairs(width: int, count: int, seed: int) -> np.ndarray:
    """Deterministically choose distinct feature pairs without replacement."""
    count = max(0, min(int(count), width * max(0, width - 1) // 2))
    rng = np.random.default_rng(int(seed))
    if count == 0:
        return np.empty((0, 2), dtype=int)
    pairs: List[Tuple[int, int]] = []
    seen = set()
    # Sampling unique pairs is fast for the modest budgets used here.
    while len(pairs) < count and len(seen) < width * max(0, width - 1) // 2:
        i = int(rng.integers(0, width))
        j = int(rng.integers(0, width - 1))
        if j >= i:
            j += 1
        key = (min(i, j), max(i, j))
        if key not in seen:
            seen.add(key)
            pairs.append(key)
    return np.asarray(pairs, dtype=int)


def _raw_feature_matrix(series: np.ndarray, ends: np.ndarray, L: int, *, levels: int, profile: str) -> np.ndarray:
    rows = []
    for end in ends:
        window = np.asarray(series[end - L : end], dtype=float).ravel()
        anchor = float(window[-1])
        groups = _filter_bank(window - anchor, levels=levels, profile=profile)
        # Assert the schema at the boundary rather than silently dropping a
        # row when a wavelet backend changes behavior.
        if not groups or any(len(group) != L for group in groups):
            raise RuntimeError("filter bank returned an inconsistent feature width")
        rows.append(np.concatenate(groups))
    return np.stack(rows, axis=0)


class BigDictLASSO:
    """Direct sparse multi-horizon forecaster over a BigDict feature bank."""

    def __init__(
        self,
        input_length: int = 96,
        hidden: int = 384,
        alpha: float = 0.01,
        max_iter: int = 10000,
        cv: int = 0,
        random_state: int = 42,
        use_expansion: bool = False,
        max_interactions: int = 100,
        profile: str = "approx",
        levels: int = 2,
        wavelet_bank: Tuple[str, ...] = ("db4", "sym4"),
    ) -> None:
        if int(input_length) < 2:
            raise ValueError("input_length must be at least 2")
        if float(alpha) <= 0:
            raise ValueError("alpha must be positive")
        self.input_length = int(input_length)
        self.hidden = int(hidden)  # retained for API compatibility
        self.alpha = float(alpha)
        self.max_iter = int(max_iter)
        self.cv = int(cv)  # 0 means deterministic fixed-alpha fit
        self.random_state = int(random_state)
        self.use_expansion = bool(use_expansion)
        self.max_interactions = int(max_interactions)
        self.profile = str(profile)
        self.levels = int(levels)
        self.wavelet_bank = tuple(wavelet_bank)
        self.model_ = None
        self.history_ = None
        self.feature_mask_: Optional[np.ndarray] = None
        self.selected_features_ = 0
        self.mu_: Optional[np.ndarray] = None
        self.sigma_: Optional[np.ndarray] = None
        self.target_mu_: Optional[np.ndarray] = None
        self.target_sigma_: Optional[np.ndarray] = None
        self.interaction_pairs_: Optional[np.ndarray] = None
        self.horizon_: Optional[int] = None
        self.input_width_: Optional[int] = None
        self.base_width_: Optional[int] = None
        self._fitted = False

    def _expand(self, x: np.ndarray) -> np.ndarray:
        """Expand an already train-scaled matrix, using fixed pair indices."""
        if not self.use_expansion:
            return x
        pieces = [x, x * x]
        if self.interaction_pairs_ is None:
            return x
        pairs = self.interaction_pairs_
        if len(pairs):
            pieces.append(x[:, pairs[:, 0]] * x[:, pairs[:, 1]])
        return np.concatenate(pieces, axis=1)

    def _raw_to_features(self, raw: np.ndarray) -> np.ndarray:
        if self.mu_ is None or self.sigma_ is None:
            raise RuntimeError("feature scaling is not fitted")
        scaled = (raw - self.mu_) / self.sigma_
        return self._expand(scaled)

    def fit(self, series: np.ndarray, horizon: int = 24) -> "BigDictLASSO":
        if not _HAS_SKLEARN:
            raise ImportError("scikit-learn is required for BigDictLASSO")
        values = np.asarray(series, dtype=float).ravel()
        H = int(horizon)
        if H < 1:
            raise ValueError("horizon must be positive")
        L = min(self.input_length, len(values) - H)
        if L < 2 or len(values) - H - L < 1:
            raise ValueError("series is too short for input_length and horizon")
        ends = np.arange(L, len(values) - H + 1)
        raw = _raw_feature_matrix(
            values,
            ends,
            L,
            levels=self.levels,
            profile=self.profile,
        )
        y = np.stack([values[e : e + H] - float(values[e - 1]) for e in ends], axis=0)

        # All scaling statistics come from the training window set only.
        self.mu_ = raw.mean(axis=0)
        self.sigma_ = raw.std(axis=0)
        self.sigma_[self.sigma_ < 1e-8] = 1.0
        self.base_width_ = raw.shape[1]
        self.interaction_pairs_ = (
            _interaction_pairs(self.base_width_, self.max_interactions, self.random_state)
            if self.use_expansion
            else np.empty((0, 2), dtype=int)
        )
        x = self._raw_to_features(raw)
        self.target_mu_ = y.mean(axis=0)
        self.target_sigma_ = y.std(axis=0)
        self.target_sigma_[self.target_sigma_ < 1e-8] = 1.0
        y_scaled = (y - self.target_mu_) / self.target_sigma_

        # A fixed-alpha multi-task LASSO is reproducible and avoids the
        # very expensive per-horizon CV grid on a 1,000+ feature dictionary.
        self.model_ = MultiTaskLasso(
            alpha=self.alpha,
            max_iter=self.max_iter,
            tol=1e-4,
            selection="cyclic",
            random_state=self.random_state,
        )
        self.model_.fit(x, y_scaled)
        self.feature_mask_ = np.abs(self.model_.coef_) > 1e-7
        self.selected_features_ = int(self.feature_mask_.sum())
        self.horizon_ = H
        self.input_width_ = L
        self.history_ = values.copy()
        self._fitted = True
        return self

    def _query_features(self, history: np.ndarray) -> np.ndarray:
        h = np.asarray(history, dtype=float).ravel()
        width = self.input_width_ or self.input_length
        if len(h) < 2 or not np.isfinite(h).all():
            raise ValueError("history must contain finite values")
        if len(h) < width:
            h = np.pad(h, (width - len(h), 0), mode="edge")
        h = h[-width:]
        raw = _raw_feature_matrix(h, np.array([width]), width, levels=self.levels, profile=self.profile)
        return self._raw_to_features(raw)

    def predict_hist(self, context: np.ndarray) -> np.ndarray:
        if not self._fitted or self.model_ is None:
            raise RuntimeError("fit must be called before predict_hist")
        x = self._query_features(context)
        pred_scaled = self.model_.predict(x)[0]
        return pred_scaled * self.target_sigma_ + self.target_mu_

    def predict(self, history: Optional[np.ndarray] = None) -> np.ndarray:
        if history is None:
            history = self.history_
        return self.predict_hist(history)

    def fit_predict(self, series: np.ndarray, horizon: int = 24) -> Tuple[np.ndarray, np.ndarray]:
        self.fit(series, horizon)
        return self.predict_hist(series), np.asarray(series[horizon:], dtype=float)


def fit_bigdict_lasso(series, horizon=24, alpha=0.01, cv=0):
    """Compatibility wrapper used by experiment scripts."""
    return BigDictLASSO(alpha=alpha, cv=cv).fit(series, horizon)


__all__ = ["BigDictLASSO", "fit_bigdict_lasso", "_filter_bank"]
