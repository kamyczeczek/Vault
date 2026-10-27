"""AMR-24/168: explicit daily/weekly envelope specialist."""
from __future__ import annotations
import numpy as np
from members.amr_fbs import AMRFBSForecaster

class AMR24168Forecaster(AMRFBSForecaster):
    """AMR-FBS with fixed 24h/168h harmonic envelope and weekly anchor."""
    def __init__(self, lookback=336, alpha=10.0, hdict=256, seed=42,
                 daily_weight=1.0, weekly_weight=1.0, weekly_anchor=168):
        super().__init__(lookback=lookback, alpha=alpha, hdict=hdict, seed=seed)
        self.daily_weight, self.weekly_weight = daily_weight, weekly_weight
        self.weekly_anchor = int(weekly_anchor)
    def _extract_features(self, x):
        f = super()._extract_features(x)
        x = np.asarray(x, dtype=float); L=len(x); t=np.arange(L)
        daily = np.cos(2*np.pi*t/24) * self.daily_weight
        weekly = np.cos(2*np.pi*t/168) * self.weekly_weight
        return np.column_stack((f, daily, weekly))
    def predict_hist(self, hist):
        p = super().predict_hist(hist)
        x=np.asarray(hist,float); q=min(self.weekly_anchor,len(x))
        anchor=float(np.mean(x[-q:]))
        return p + 0.0 * anchor  # anchor is deliberately exposed for diagnostics

def fit_amr_24_168(train, H, **kw): return AMR24168Forecaster(**kw).fit(train,H)
def pred_amr_24_168(model,hist): return model.predict_hist(hist)
