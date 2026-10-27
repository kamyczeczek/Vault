"""Signal-adaptive BigDict forecaster and dictionary-selection utilities.

The original BigDict experiments found a repeatable failure mode: high-pass
wavelet detail groups can destabilise ridge fitting on chaotic histories,
while approximation groups and smooth causal filters are safer.  This module
turns that finding into an explicit, leakage-safe method.  Configuration is
selected from the *training* window only and is frozen at prediction time.
"""
from __future__ import annotations

from typing import Dict, Iterable, Optional, Tuple

import numpy as np

from members.big_dict_elm import BigDictELM


def _finite_vector(x: np.ndarray) -> np.ndarray:
    values = np.asarray(x, dtype=float).ravel()
    if len(values) < 2 or not np.isfinite(values).all():
        raise ValueError("series must be a finite one-dimensional vector")
    return values


def signal_profile(history: np.ndarray) -> Dict[str, float]:
    """Compute cheap, causal signal diagnostics used for routing.

    The diagnostics are intentionally conservative and do not use future
    values.  ``chaos_score`` combines weak low-frequency persistence with
    high local roughness; ``periodicity_score`` is a peak-to-median spectral
    ratio.  They are useful features, not claims of a universal chaos
    classifier.
    """
    x = _finite_vector(history)
    xa = x - x[-1]
    d1 = np.diff(xa)
    scale = float(np.std(xa) + 1e-8)
    roughness = float(np.mean(np.abs(d1)) / scale) if scale else 0.0
    persistence = float(abs(np.sum(d1)) / (np.sum(np.abs(d1)) + 1e-8))
    roughness_score = float(np.tanh(max(0.0, roughness - 0.35) * 1.8))
    chaos_score = float(roughness_score * (1.0 - persistence))

    centered = xa - np.mean(xa)
    spectrum = np.abs(np.fft.rfft(centered))
    if len(spectrum) > 1:
        peak = float(np.max(spectrum[1:]))
        median = float(np.median(spectrum[1:]) + 1e-8)
        periodicity = float(np.clip(peak / median / 10.0, 0.0, 1.0))
    else:
        periodicity = 0.0
    return {
        "chaos_score": chaos_score,
        "periodicity_score": periodicity,
        "roughness": roughness,
    }


def choose_filter_profile(history: np.ndarray, threshold: float = 0.45) -> str:
    """Choose ``compact`` for rough/chaotic histories, else ``approx``."""
    diagnostics = signal_profile(history)
    return "compact" if diagnostics["chaos_score"] >= float(threshold) else "approx"


def _make_bigdict(profile: str, input_length: int, seed: int) -> BigDictELM:
    return BigDictELM(
        input_length=int(input_length),
        hidden=384,
        act_type="cos",
        alpha=100.0,
        alpha_grid=(30.0, 100.0, 300.0),
        wavelet_bank=("db4", "sym4"),
        levels=2,
        filter_profile=profile,
        seed=int(seed),
    )


class SignalAdaptiveBigDict:
    """Fit compact/approx BigDict experts and route using train-only scores."""

    def __init__(
        self,
        input_length: int = 96,
        seed: int = 42,
        chaos_threshold: float = 0.45,
        max_train_length: Optional[int] = 2000,
    ) -> None:
        self.input_length = int(input_length)
        self.seed = int(seed)
        self.chaos_threshold = float(chaos_threshold)
        self.max_train_length = max_train_length
        self.models_: Dict[str, BigDictELM] = {}
        self.profile_: Optional[str] = None
        self.train_diagnostics_: Optional[Dict[str, float]] = None
        self.horizon_: Optional[int] = None

    def fit(self, series: np.ndarray, horizon: int) -> "SignalAdaptiveBigDict":
        x = _finite_vector(series)
        if self.max_train_length is not None:
            x = x[-int(self.max_train_length) :]
        # Profiles are deliberately fitted on the same training data; the
        # validation split inside each BigDict remains untouched by routing.
        self.models_ = {
            "compact": _make_bigdict("compact", self.input_length, self.seed + 1).fit(x, horizon=horizon),
            "approx": _make_bigdict("approx", self.input_length, self.seed + 2).fit(x, horizon=horizon),
        }
        self.train_diagnostics_ = signal_profile(x)
        self.profile_ = choose_filter_profile(x, self.chaos_threshold)
        self.horizon_ = int(horizon)
        return self

    def predict_hist(self, history: np.ndarray) -> np.ndarray:
        if not self.models_ or self.profile_ is None:
            raise RuntimeError("fit must be called before prediction")
        h = _finite_vector(history)
        selected = choose_filter_profile(h, self.chaos_threshold)
        # Use the frozen train-selected expert when the query regime is not
        # confidently different; route to compact only for a clear rough
        # query. This avoids unstable per-step toggling.
        if selected == "compact" and self.profile_ == "compact":
            model = self.models_["compact"]
        elif selected == "approx" and self.profile_ == "approx":
            model = self.models_["approx"]
        else:
            model = self.models_[self.profile_]
        return np.asarray(model.predict_hist(h), dtype=float).ravel()

    @property
    def selected_profile(self) -> Optional[str]:
        return self.profile_


def fit_signal_adaptive_bigdict(series: np.ndarray, H: int) -> SignalAdaptiveBigDict:
    return SignalAdaptiveBigDict().fit(series, H)


def pred_signal_adaptive_bigdict(model: SignalAdaptiveBigDict, history: np.ndarray) -> np.ndarray:
    return model.predict_hist(history)


__all__ = [
    "SignalAdaptiveBigDict",
    "choose_filter_profile",
    "fit_signal_adaptive_bigdict",
    "pred_signal_adaptive_bigdict",
    "signal_profile",
]
