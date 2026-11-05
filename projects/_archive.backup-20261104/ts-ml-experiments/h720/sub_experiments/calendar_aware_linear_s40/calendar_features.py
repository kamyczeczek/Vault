"""Calendar feature engineering for S-40.

Precomputes 7-dim calendar features for all 17,420 ETTh1 timestamps:
  [hour_sin, hour_cos, dow_sin, dow_cos, month_sin, month_cos, holiday]

All features are deterministic, origin-only, and horizon-broadcast.
"""

from __future__ import annotations

import holidays
import numpy as np
from datetime import datetime
from math import sin, cos, pi
from pathlib import Path

H720_DIR = Path(__file__).resolve().parent
FEATURES_PATH = H720_DIR / "calendar_features.npy"

# Chinese holidays for ETTh1 date range 2016-07-01 .. 2018-06-26
_HOLIDAY_SET: set | None = None


def _get_holidays() -> set:
    global _HOLIDAY_SET
    if _HOLIDAY_SET is None:
        years = {2016, 2017, 2018}
        cn = holidays.country_holidays("CN", years=years)
        _HOLIDAY_SET = set(cn.keys())
    return _HOLIDAY_SET


def calendar_vector(timestamp: datetime) -> np.ndarray:
    """7-dim calendar feature vector for a single origin timestamp."""
    holiday_set = _get_holidays()
    hod = (timestamp.hour + timestamp.minute / 60.0) / 24.0
    dow = timestamp.weekday() / 7.0
    month = (timestamp.month - 1) / 12.0
    holiday = 1.0 if timestamp.date() in holiday_set else 0.0
    return np.array(
        [sin(2 * pi * hod), cos(2 * pi * hod),
         sin(2 * pi * dow), cos(2 * pi * dow),
         sin(2 * pi * month), cos(2 * pi * month),
         holiday],
        dtype=np.float32,
    )


def precompute(dates: list[datetime]) -> np.ndarray:
    """Precompute calendar features for a list of timestamps.

    Returns array of shape (len(dates), 7).
    """
    return np.stack([calendar_vector(d) for d in dates], axis=0)


def load_or_compute(dates: list[datetime]) -> np.ndarray:
    """Load cached calendar features or compute and cache them."""
    if FEATURES_PATH.exists():
        cached = np.load(FEATURES_PATH)
        if cached.shape == (len(dates), 7):
            return cached
    arr = precompute(dates)
    np.save(FEATURES_PATH, arr)
    return arr
