"""Ad-hoc FITS diagnosis (S-07, scratch — not part of the slice gates)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from methods.fits import FITSForecaster  # noqa: E402

rng = np.random.default_rng(5)
t = np.arange(6000)
y = 10.0 + 0.5 * np.sin(2 * np.pi * t / 24.0) + rng.normal(0, 0.05, 6000)

for cut in (48, 64, 100, None):
    m = FITSForecaster(input_length=720, ridge_alpha=1e-6, cutoff=cut)
    m.fit(y[:5000], horizon=720)
    pred = m.predict()
    actual = y[5000:5720]
    print(f"cutoff={cut}: MAE {np.mean(np.abs(pred - actual)):.4f} "
          f"pred std {pred.std():.3f}")
