# ARCHIVED 2026-09-24: no wins recorded in any results file. Archived per REFLECTION_PROMISING_METHODS.md - imports kept for compatibility
"""Leakage-safe constrained stacker for the strongest forecasting experts.

The previous implementation fitted every base model on the full training
series and then estimated blend weights on a tail of that same series.  The
tail was therefore already visible to the base learners.  This version uses
strictly chronological validation: each validation origin is predicted by
models fitted only on its prefix, weights are selected on a convex simplex,
and the final base models are refit on all available training data.
"""
from __future__ import annotations

from typing import Callable, List, Optional, Sequence, Tuple

import numpy as np

from members.adaptive_amr_knn_hybrid import AdaptiveAMRKNNHybrid
from members.amr_fbs import fit_amr_fbs, pred_amr_fbs
from members.knn_feature_forecaster import KNNFeatureForecaster


def _as_prediction(prediction, horizon: int) -> np.ndarray:
    values = np.asarray(prediction, dtype=float).ravel()
    if len(values) == 0:
        return np.full(horizon, np.nan)
    if len(values) < horizon:
        values = np.pad(values, (0, horizon - len(values)), mode="edge")
    return values[:horizon]


def _fit_experts(train: np.ndarray, horizon: int, input_length: int) -> List[object]:
    return [
        AdaptiveAMRKNNHybrid(input_length=input_length, k_neighbors=12, blend_mode="adaptive").fit(train, horizon),
        fit_amr_fbs(train, horizon),
        KNNFeatureForecaster(input_length=input_length, k_neighbors=24).fit(train, horizon),
    ]


def _predict_experts(models: Sequence[object], history: np.ndarray, horizon: int) -> np.ndarray:
    adaptive, amr, knn = models
    return np.column_stack(
        [
            _as_prediction(adaptive.predict_hist(history), horizon),
            _as_prediction(pred_amr_fbs(amr, history), horizon),
            _as_prediction(knn.predict_hist(history), horizon),
        ]
    )


def _simplex_grid(step: float = 0.1) -> np.ndarray:
    """Enumerate a small deterministic convex simplex grid."""
    units = int(round(1.0 / step))
    if units < 1 or not np.isclose(units * step, 1.0):
        step = 1.0 / max(1, units)
    rows = []
    for i in range(units + 1):
        for j in range(units + 1 - i):
            k = units - i - j
            rows.append((i / units, j / units, k / units))
    return np.asarray(rows, dtype=float)


class MetaEnsembleStacker:
    """Chronological, non-negative convex ensemble of three novel experts."""

    def __init__(
        self,
        input_length: int = 192,
        validation_origins: int = 6,
        weight_step: float = 0.1,
    ) -> None:
        if int(input_length) < 2:
            raise ValueError("input_length must be at least 2")
        self.input_length = int(input_length)
        self.validation_origins = max(0, int(validation_origins))
        self.weight_step = float(weight_step)
        self.model_adaptive_ = None
        self.model_amr_ = None
        self.model_knn_ = None
        self.stacking_weights_ = np.array([1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0])
        self.horizon_: Optional[int] = None
        self.validation_mae_: Optional[float] = None
        self.validation_origins_used_: int = 0

    def fit(self, train: np.ndarray, horizon: int) -> "MetaEnsembleStacker":
        values = np.asarray(train, dtype=float).ravel()
        H = int(horizon)
        self.horizon_ = H
        L = min(self.input_length, len(values) - H)
        if L < 2 or len(values) - L - H < 1:
            raise ValueError("training series is too short for stacking")

        # Validation origins are strictly before the final training endpoint.
        # Leave at least one sample after each validation target.
        max_origins = max(0, (len(values) - L - H) // max(1, H))
        n_origins = min(self.validation_origins, max_origins)
        validation_predictions = []
        validation_actuals = []
        origins_used = 0
        for ordinal in range(n_origins):
            origin = len(values) - (n_origins - ordinal) * H
            prefix = values[:origin]
            history = values[max(0, origin - L) : origin]
            actual = values[origin : origin + H]
            if len(prefix) < L or len(actual) < H:
                continue
            try:
                base = _fit_experts(prefix, H, L)
                pred = _predict_experts(base, history, H)
            except (ValueError, np.linalg.LinAlgError, RuntimeError):
                continue
            if np.isfinite(pred).all() and np.isfinite(actual).all():
                validation_predictions.append(pred)
                validation_actuals.append(actual)
                origins_used += 1

        if validation_predictions:
            pred_matrix = np.concatenate(validation_predictions, axis=0)
            actual_matrix = np.concatenate(validation_actuals, axis=0)
            candidates = _simplex_grid(self.weight_step)
            losses = np.mean(np.abs(candidates @ pred_matrix.T - actual_matrix[:, None]), axis=0)
            self.stacking_weights_ = candidates[int(np.argmin(losses))].copy()
            self.validation_mae_ = float(np.min(losses))
        self.validation_origins_used_ = origins_used

        # Refit the production experts only after validation is complete.
        final_models = _fit_experts(values, H, L)
        self.model_adaptive_, self.model_amr_, self.model_knn_ = final_models
        return self

    def predict_hist(self, history: np.ndarray) -> np.ndarray:
        if self.model_adaptive_ is None:
            raise RuntimeError("fit must be called before prediction")
        h = np.asarray(history, dtype=float).ravel()
        if len(h) < self.input_length:
            h = np.pad(h, (self.input_length - len(h), 0), mode="edge")
        h = h[-self.input_length :]
        H = int(self.horizon_)
        p = _predict_experts((self.model_adaptive_, self.model_amr_, self.model_knn_), h, H)
        weights = self.stacking_weights_
        return weights @ p


def fit_meta_ensemble(train: np.ndarray, H: int) -> MetaEnsembleStacker:
    return MetaEnsembleStacker(input_length=192).fit(train, H)


def pred_meta_ensemble(model: MetaEnsembleStacker, hist: np.ndarray) -> np.ndarray:
    return model.predict_hist(hist)


__all__ = ["MetaEnsembleStacker", "fit_meta_ensemble", "pred_meta_ensemble"]
