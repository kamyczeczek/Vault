"""S-37 — Sparse Subset Multivariate NLinear with channel dropout.

Level-free via last-row OT subtraction. Channel dropout during training
masks one random exogenous channel with probability p=0.3.
"""

from __future__ import annotations

import numpy as np
from sklearn.linear_model import Ridge

COLS = ["HUFL", "HULL", "MUFL", "MULL", "LUFL", "LULL", "OT"]
OT_IDX = 6


class MultiNLinear:
    """Multivariate NLinear over a sparse channel subset.

    Parameters
    ----------
    input_length : int
        Lookback window length.
    ridge_alpha : float
        Ridge penalty for the horizon readout.
    channels : list[str]
        Channel subset to use, must include ``"OT"``.
    dropout_prob : float
        Probability of zeroing one random exogenous channel per training
        sample. Applied only during ``fit()``.
    """

    def __init__(
        self,
        input_length: int = 336,
        ridge_alpha: float = 1.0,
        channels: list[str] | None = None,
        dropout_prob: float = 0.3,
    ) -> None:
        self.input_length = input_length
        self.ridge_alpha = ridge_alpha
        self.channels = channels if channels is not None else ["OT", "HUFL", "LUFL"]
        self.dropout_prob = dropout_prob
        self._ot_in_subset = "OT" in self.channels
        if not self._ot_in_subset:
            raise ValueError("channel subset must include OT")
        self._exo_idx = [i for i, c in enumerate(self.channels) if c != "OT"]
        self._subset_index = {c: i for i, c in enumerate(self.channels)}

    def fit(self, X_dict: dict[str, np.ndarray], y: np.ndarray, *, horizon: int) -> "MultiNLinear":
        """Fit on a multi-channel window.

        Parameters
        ----------
        X_dict : dict[str, np.ndarray]
            Mapping channel name -> 1-D window array of length ``len(y) - horizon + 1 + input_length - 1``.
            The array must cover the training window aligned to ``y``.
        y : np.ndarray
            1-D target series (OT).
        horizon : int
            Forecast horizon.
        """
        y_arr = np.asarray(y, dtype=float)
        if y_arr.ndim != 1:
            raise ValueError("y must be 1-D for MultiNLinear.fit")
        n = len(y_arr)
        L = self.input_length
        if n < L + horizon:
            raise ValueError("series too short for window/horizon")

        # Build multi-channel history matrix (n, n_channels)
        n_channels = len(self.channels)
        history = np.empty((n, n_channels), dtype=float)
        for c, arr in X_dict.items():
            if c not in self._subset_index:
                continue
            history[:, self._subset_index[c]] = np.asarray(arr, dtype=float)

        X_rows, Y_rows = [], []
        rng = np.random.default_rng(0)
        for end in range(L, n - horizon + 1):
            window = history[end - L : end]           # (L, n_channels)
            anchor = window[-1, self._subset_index["OT"]]
            x = (window - window[-1]).reshape(-1)     # (L*n_channels,)
            # channel dropout: with prob p, zero one random exogenous channel block
            if rng.random() < self.dropout_prob and len(self._exo_idx) > 0:
                ch = rng.choice(self._exo_idx)
                start = ch * L
                stop = (ch + 1) * L
                x[start:stop] = 0.0
            X_rows.append(x)
            Y_rows.append(y_arr[end : end + horizon] - anchor)

        self.model = Ridge(alpha=self.ridge_alpha, fit_intercept=True).fit(
            np.asarray(X_rows), np.asarray(Y_rows)
        )
        self.history_ = history
        self.horizon_ = int(horizon)
        self._fitted = True
        return self

    def predict(self, X_dict: dict[str, np.ndarray] | None = None) -> np.ndarray:
        """Predict horizon from the last ``input_length`` window.

        If ``X_dict`` is None, use ``self.history_`` (history_ swap mode).
        """
        self._check_fitted()
        if X_dict is not None:
            window = np.column_stack([X_dict[c][-self.input_length:] for c in self.channels])
        else:
            window = self.history_[-self.input_length :]
        anchor = window[-1, self._subset_index["OT"]]
        x = (window - window[-1]).reshape(-1)
        return (
            np.asarray(self.model.predict([x])[0])
            + anchor
        )

    def _check_fitted(self) -> None:
        if not getattr(self, "_fitted", False):
            raise RuntimeError("predict called before fit")
