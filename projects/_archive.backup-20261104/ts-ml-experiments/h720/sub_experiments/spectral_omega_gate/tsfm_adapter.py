"""TSFM adapter — Chronos-Bolt Base zero-shot inference.

Pinned model : amazon/chronos-bolt-base  (chronos forecasting stable tag)
Protocol    : zero-shot throughout; no ETTh1 gradient; history-only input.
"""
from __future__ import annotations

import os
# Disable progress bars to avoid stderr interleaving in harness logs
os.environ.setdefault("TQDM_DISABLE", "1")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")

import numpy as np
import torch
from chronos import ChronosBoltPipeline


class TSFMAdapter:
    """Thin wrapper around Chronos-Bolt for univariate rolling-origin forecasting.

    The pipeline is loaded once at construction.  All inference is zero-shot:
    model weights are frozen and never updated on ETTh1 data.
    """

    def __init__(self, context_length: int = 336, device: str = "cpu"):
        self.context_length = int(context_length)
        # Load once; cached for the lifetime of the adapter.
        self.pipeline = ChronosBoltPipeline.from_pretrained("amazon/chronos-bolt-base")

    def predict(self, history_1d: np.ndarray, prediction_length: int) -> np.ndarray:
        """Return median forecast for a single univariate history window.

        Parameters
        ----------
        history_1d : np.ndarray
            1-D array of historical observations.
        prediction_length : int
            Horizon length H (e.g. 720).

        Returns
        -------
        np.ndarray
            1-D array of shape (prediction_length,) with median quantile forecasts.
        """
        x = np.asarray(history_1d, dtype=np.float32).ravel()
        if x.size == 0:
            raise ValueError("history_1d must be non-empty")
        L = min(int(x.size), self.context_length)
        context = x[-L:]                                # last L points
        ctx_tensor = torch.tensor(context).unsqueeze(0)  # (1, L)
        out = self.pipeline.predict(
            ctx_tensor,
            prediction_length=int(prediction_length),
            limit_prediction_length=False,
        )
        # out: (1, prediction_length, 3) quantiles
        median = out.median(dim=1).values                # (1, prediction_length)
        return median.squeeze(0).numpy()                 # (prediction_length,)

    def predict_batch(
        self, histories_2d: np.ndarray, prediction_length: int
    ) -> np.ndarray:
        """Batch prediction for multiple histories.

        Parameters
        ----------
        histories_2d : np.ndarray
            2-D array of shape (n_series, context_length).
        prediction_length : int
            Horizon length H.

        Returns
        -------
        np.ndarray
            2-D array of shape (n_series, prediction_length) with median forecasts.
        """
        x = np.asarray(histories_2d, dtype=np.float32)
        if x.ndim != 2:
            raise ValueError("histories_2d must be 2-D (n_series, context_length)")
        L = min(x.shape[1], self.context_length)
        contexts = x[:, -L:]                             # (n_series, L)
        ctx_tensor = torch.tensor(contexts, dtype=torch.float32)
        out = self.pipeline.predict(
            ctx_tensor,
            prediction_length=int(prediction_length),
            limit_prediction_length=False,
        )
        median = out.median(dim=1).values                # (n_series, prediction_length)
        return median.numpy()                             # (n_series, prediction_length)
