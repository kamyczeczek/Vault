"""AMR-24/168: explicit daily/weekly envelope specialist.

A long-horizon (H720) variant of AMR-FBS that adds fixed 24h/168h harmonic
envelope features and, critically, a *weekly level anchor*.  At a 30-day
horizon the dominant error is level drift, not shape, so instead of anchoring
the delta on the single last observed point (the base NLinear behavior) the
design anchors it on a 7-day mean level.  The anchor rule is a first-class
parameter so that the base ELM core, feature bank and random dictionary are
reused verbatim -- only the base level changes, and it changes identically in
`fit` and `predict_hist` (train/serve consistency).

Decision record for the previously no-op anchor (`p + 0.0 * anchor`):
the skeleton computed a weekly mean but multiplied it by zero, so the
long-horizon anchoring the design specifies was inert.  This rewrite routes
the anchor through the base class's `_anchor_level` hook and pre-declares three
rules (last / weekly / blend) that the early-dev diagnostic is free to select
between before the locked final pass.  The rule is chosen on early dev
origins only, then frozen; see `diag_amr_early_dev.py` / `run_amr_h720_final.py`.
"""
from __future__ import annotations

import numpy as np

from members.amr_fbs import AMRFBSForecaster


class AMR24168Forecaster(AMRFBSForecaster):
    """AMR-FBS with a 24h/168h harmonic envelope and a configurable level anchor.

    ``anchor_rule``:
      - ``"last"``   : ``x[-1]``                       -- base NLinear behavior
      - ``"weekly"`` : ``mean(x[-weekly_anchor:])``    -- design intent
      - ``"blend"``  : ``0.5*last + 0.5*weekly``
    """

    _ANCHOR_RULES = ("last", "weekly", "blend")

    def __init__(self, lookback=336, alpha=10.0, hdict=256, seed=42,
                 daily_weight=1.0, weekly_weight=1.0, weekly_anchor=168,
                 anchor_rule="weekly"):
        super().__init__(lookback=lookback, alpha=alpha, hdict=hdict, seed=seed)
        self.daily_weight, self.weekly_weight = daily_weight, weekly_weight
        self.weekly_anchor = int(weekly_anchor)
        if anchor_rule not in self._ANCHOR_RULES:
            raise ValueError(f"anchor_rule must be one of {self._ANCHOR_RULES}")
        self.anchor_rule = anchor_rule

    def _extract_features(self, x):
        f = super()._extract_features(x)
        x = np.asarray(x, dtype=float); L = len(x); t = np.arange(L)
        daily = np.cos(2 * np.pi * t / 24) * self.daily_weight
        weekly = np.cos(2 * np.pi * t / 168) * self.weekly_weight
        return np.column_stack((f, daily, weekly))

    def _anchor_level(self, window):
        window = np.asarray(window, dtype=float)
        if self.anchor_rule == "last":
            return float(window[-1])
        q = min(self.weekly_anchor, len(window))
        weekly = float(np.mean(window[-q:]))
        if self.anchor_rule == "weekly":
            return weekly
        return 0.5 * float(window[-1]) + 0.5 * weekly


def fit_amr_24_168(train, H, **kw):
    return AMR24168Forecaster(**kw).fit(train, H)


def pred_amr_24_168(model, hist):
    return model.predict_hist(hist)
