"""Shared time-series data processing for the h720 protocol.

Single source of truth for loading, splitting, and materializing the
ETTh1 data. Every sub-experiment and the main leaderboard MUST consume
data through this module so that all runs share one identical
chronological split.

Materialized split files (in this directory, generated from the raw CSV):

- ``train.csv`` — rows 0..11424 (11,425 hourly rows). This is the
  **fit history** of the locked protocol. Internally it contains the
  train segment (rows 0..8544) followed by the validation segment
  (rows 8545..11424); the boundary is exposed as
  ``TRAIN_ROWS``/``TRAIN_END``.
- ``test.csv``  — rows 11425..14224 (2,880 hourly rows). The first
  720 rows are the locked H=720 scoring window. Rows 14225+ of the raw
  file are unused reserve and are NOT part of any split file.

Processing pipeline (explicit steps):

1. **Load raw**  Read ``ETTh1.csv`` (17,420 hourly rows,
               2016-07-01 00:00 .. 2018-06-26 19:00, all columns).
               File order == time order; no resampling, no
               interpolation — the raw series has no gaps.
2. **Validate** Assert the OT series is finite, 1-D, expected length.
3. **Split**    Chronological (time-based) split, no shuffling, no
               overlap — written to ``train.csv`` / ``test.csv``
               (all original columns preserved, dates intact).
4. **Forecast views** The locked H=720 protocol scores a single
               720-step forecast: fit on ``train.csv`` (11,425 rows),
               predict the next 720 points, compare against the first
               720 rows of ``test.csv``.

Usage:
    python data.py                     # (re)generate train.csv / test.csv
    from data import get_protocol_data
    pd = get_protocol_data()
    train, actual = pd.forecast_views()
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np

# ----------------------------------------------------------------------
# Constants — the locked protocol (mirrors config.json)
# ----------------------------------------------------------------------
H720_DIR = Path(__file__).resolve().parent
H720_DATA_FILE = H720_DIR / "ETTh1.csv"   # raw, untouched
TRAIN_FILE = H720_DIR / "train.csv"       # materialized fit history
TEST_FILE = H720_DIR / "test.csv"         # materialized holdout

TARGET_COLUMN = "OT"
EXPECTED_ROWS = 17_420  # hourly, 2016-07-01 .. 2018-06-26

TRAIN_ROWS = 8_545        # config.json split.train_rows
VALIDATION_ROWS = 2_880  # config.json split.validation_rows
TEST_ROWS = 2_880         # config.json split.test_rows
HORIZON = 720             # config.json horizons[0]

TRAIN_END = TRAIN_ROWS                          # 8545 (inside train.csv)
VALIDATION_END = TRAIN_END + VALIDATION_ROWS    # 11425 (train.csv length)
TEST_END = VALIDATION_END + TEST_ROWS           # 14305 (raw rows used)


# ----------------------------------------------------------------------
# Step 1 + 2: load and validate the raw series
# ----------------------------------------------------------------------
def load_series() -> np.ndarray:
    """Load the raw OT series (step 1) and validate it (step 2)."""
    with open(H720_DATA_FILE) as f:
        series = np.array(
            [float(row[TARGET_COLUMN]) for row in csv.DictReader(f)]
        )
    if series.ndim != 1 or len(series) != EXPECTED_ROWS:
        raise ValueError(
            f"expected {EXPECTED_ROWS} hourly points, got shape {series.shape}"
        )
    if not np.isfinite(series).all():
        raise ValueError("series contains NaN/inf — raw ETTh1 must be gapless")
    return series


# ----------------------------------------------------------------------
# Step 3: chronological split -> train.csv / test.csv
# ----------------------------------------------------------------------
def make_split() -> tuple[Path, Path]:
    """Materialize ``train.csv`` and ``test.csv`` from the raw file.

    Time-based split of the raw rows (all columns preserved, header kept):
        train.csv = raw rows [0    : 11425)
        test.csv  = raw rows [11425: 14225)
    """
    with open(H720_DATA_FILE, newline="") as f:
        rows = list(csv.reader(f))
    header, body = rows[0], rows[1:]
    if len(body) != EXPECTED_ROWS:
        raise ValueError(
            f"raw file has {len(body)} data rows, expected {EXPECTED_ROWS}"
        )
    with open(TRAIN_FILE, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(body[:VALIDATION_END])
    with open(TEST_FILE, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(body[VALIDATION_END:TEST_END])
    return TRAIN_FILE, TEST_FILE


def ensure_split_files() -> None:
    """Generate the split files if absent; never overwrite existing."""
    if not (TRAIN_FILE.exists() and TEST_FILE.exists()):
        make_split()


# ----------------------------------------------------------------------
# Step 4: protocol views over the split files
# ----------------------------------------------------------------------
def _read_ot(path: Path, expected: int) -> np.ndarray:
    with open(path) as f:
        vals = [float(row[TARGET_COLUMN]) for row in csv.DictReader(f)]
    if len(vals) != expected:
        raise ValueError(
            f"{path.name}: expected {expected} rows, found {len(vals)} — "
            f"re-run `python data.py` to regenerate the split"
        )
    return np.array(vals)


class ProtocolData:
    """Chronological split loaded from the materialized CSV files.

    Anti-leakage design: test data is **not** a public attribute. The
    only sanctioned access is ``forecast_views()`` (fit on train.csv,
    score against test.csv[:720]) and ``test_scores()`` (explicit,
    auditable holdout access). Nothing here can be passed to ``fit``.
    """

    def __init__(self) -> None:
        ensure_split_files()
        train_full = _read_ot(TRAIN_FILE, VALIDATION_END)
        test = _read_ot(TEST_FILE, TEST_ROWS)
        series = load_series()  # raw, for cross-validation of the split
        if (
            not np.array_equal(train_full, series[:VALIDATION_END])
            or not np.array_equal(test, series[VALIDATION_END:TEST_END])
        ):
            raise ValueError(
                "train.csv/test.csv are out of sync with ETTh1.csv — "
                "re-run `python data.py` to regenerate the split"
            )
        # Private by convention: double-underscore name-mangled so a
        # stray `pd.test` raises AttributeError instead of leaking data.
        self.__train = train_full[:TRAIN_END]
        self.__validation = train_full[TRAIN_END:VALIDATION_END]
        self.__test = test

    @property
    def fit_history(self) -> np.ndarray:
        """History the locked H=720 protocol fits on: all of train.csv."""
        return np.concatenate([self.__train, self.__validation])

    def forecast_views(self) -> tuple[np.ndarray, np.ndarray]:
        """Return `(fit_history, ground_truth)` for the locked protocol.

        fit_history  — train.csv contents (11,425 rows)
        ground_truth — first 720 rows of test.csv (for scoring only)
        """
        return self.fit_history, self.__test[:HORIZON]

    def rolling_views(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return `(fit_history, eval_series, test)` for rolling-origin
        evaluation over the full test region.

        fit_history — train.csv contents (11,425 rows): what a frozen-fit
        model is fit on, exactly once.
        eval_series — fit_history ++ test.csv (14,305 rows): a
        chronological concatenation so a runner can slice, per origin t
        (test-row index), the trailing history ``eval_series[:11425+t]``
        (all rows strictly before the scored window — past observed data
        only) and score against ``test[t:t+720]``. Test rows are never
        handed to ``fit``; sliding windows on past observations follow
        the benchmark convention.
        test        — the full 2,880-row test holdout (scoring only).
        """
        return self.fit_history, np.concatenate([self.fit_history, self.__test]), self.__test.copy()

    def test_scores(self) -> np.ndarray:
        """Explicit, auditable access to the full test holdout.

        Named ``*_scores`` to signal scoring use; still returns the
        entire test.csv OT column for leaderboard evaluation windows.
        """
        return self.__test.copy()
@lru_cache(maxsize=1)
def _cached_protocol() -> ProtocolData:
    return ProtocolData()


def get_protocol_data() -> ProtocolData:
    """Cached accessor — one parse per process, shared everywhere."""
    return _cached_protocol()


if __name__ == "__main__":
    train_path, test_path = make_split()
    print(f"wrote {train_path} ({VALIDATION_END} rows)")
    print(f"wrote {test_path} ({TEST_ROWS} rows)")
    print(f"fit history = train.csv ({VALIDATION_END} rows; "
          f"train {TRAIN_ROWS} + validation {VALIDATION_ROWS})")
    print(f"scoring window = first {HORIZON} rows of test.csv")
