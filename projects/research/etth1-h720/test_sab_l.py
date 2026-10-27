"""Focused SAB-L correctness checks."""
from __future__ import annotations

import numpy as np

from members.big_dict_elm import _filter_bank_one
from members.sab_l import SABLForecaster, _ema, _ma


def _windows(s, length, step):
    return np.stack([s[o:o + length] for o in range(0, len(s) - length + 1, step)])


def test_ema_operates_over_time_not_training_windows():
    w = _windows(np.arange(20.0), 6, 1)
    actual = _ema(w, 0.3)
    expected = np.stack([_ema(row, 0.3) for row in w])
    np.testing.assert_allclose(actual, expected)
    # An isolated row and the corresponding row of a batch must agree.
    # The old axis-0 implementation instead made the last batch row differ.
    old_ema = np.empty_like(w)
    old_ema[0] = w[0]
    for i in range(1, len(w)):
        old_ema[i] = .3 * w[i] + .7 * old_ema[i - 1]
    assert not np.allclose(old_ema[-1], actual[-1])


def test_ma_operates_over_time_not_training_windows():
    w = _windows(np.arange(35.0), 12, 1)
    actual = _ma(w, 5)
    expected = np.stack([_ma(row, 5) for row in w])
    np.testing.assert_allclose(actual, expected)
    # Isolate a later window: the old batch-axis implementation depended
    # on preceding training windows, so this equality must fail for it.
    old_ma = np.empty_like(w)
    for i in range(len(w)):
        start = max(0, i - 4)
        old_ma[i] = w[start:i + 1].mean(axis=0)
    assert not np.allclose(old_ma[-1], actual[-1])


def test_single_and_batched_context_transforms_match():
    s = np.cumsum(np.random.default_rng(7).normal(size=500))
    xa = s[-96:] - s[-1]
    m = SABLForecaster(input_length=96, profile="approx", dict_dim=32)
    single = m._bank(xa, "approx")[0]
    batched = m._bank(xa[None, :], "approx")[0]
    np.testing.assert_allclose(single, batched, rtol=1e-6, atol=1e-7)
    assert single.shape[0] > 96


def test_ema_feature_bank_matches_bigdict_on_finite_context():
    # Both implementations must produce the same time-axis EMA values.
    rng = np.random.default_rng(11)
    xa = rng.normal(size=96)
    sab_ema = _ema(xa[None, :], 0.3)[0]
    # `_filter_bank_one` groups: identity, MA3, MA6, MA12, MA24, EMA.3, EMA.7.
    big_groups = _filter_bank_one(xa, filter_profile="compact")
    np.testing.assert_allclose(big_groups[5], sab_ema, rtol=1e-6, atol=1e-7)


def test_fit_predict_is_finite_and_leakage_safe():
    rng = np.random.default_rng(2)
    train = 20.0 + np.sin(np.arange(1200) * 2 * np.pi / 24) + rng.normal(scale=.05, size=1200)
    model = SABLForecaster(input_length=96, dict_dim=32, heads=(24, 72, 120)).fit(train, 120)
    pred = model.predict_hist(train)
    assert pred.shape == (120,)
    assert np.isfinite(pred).all()
    # A future-only change must not alter this fit's stored coefficients.
    before = model.W_[120].copy()
    model.predict_hist(np.r_[train, 999.0])
    np.testing.assert_array_equal(before, model.W_[120])
