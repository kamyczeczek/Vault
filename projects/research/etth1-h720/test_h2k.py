"""Focused correctness and leakage checks for H2K."""
from __future__ import annotations

import numpy as np

from members.h2k import H2KForecaster


def _series(n=1600, seed=3):
    rng = np.random.default_rng(seed)
    t = np.arange(n, dtype=float)
    return (20.0 + .03 * t + 3.0 * np.sin(t * 2 * np.pi / 24) +
            rng.normal(scale=.15, size=n))


def test_fit_predict_shape_and_finite():
    train = _series()
    model = H2KForecaster(input_length=96, k_neighbors=12, block_length=240)
    pred = model.fit(train, 720).predict_hist(train)
    assert pred.shape == (720,)
    assert np.isfinite(pred).all()


def test_fit_is_anchored_to_training_slice_only():
    train = _series()
    model = H2KForecaster(input_length=96, k_neighbors=8).fit(train, 240)
    before = model.X_.copy(), model.Y_.copy(), model.ends_.copy()
    # A change after the fit is not a training observation and must not alter
    # any learned matrix or endpoint.
    model.predict_hist(np.r_[train, 10_000.0, -10_000.0])
    np.testing.assert_array_equal(before[0], model.X_)
    np.testing.assert_array_equal(before[1], model.Y_)
    np.testing.assert_array_equal(before[2], model.ends_)


def test_block_boundaries_are_reevaluated_from_previous_prediction():
    train = _series()
    model = H2KForecaster(input_length=96, k_neighbors=5, block_length=240).fit(train, 480)
    pred = model.predict_hist(train)
    # The second block is a genuine continuation: its local anchor uses the
    # first predicted block, not a hidden future value.
    first_mean = float(np.mean(pred[:240]))
    shifted = model.predict_hist(np.r_[train[:-240], train[-240:] + 3.0])
    assert abs(float(np.mean(shifted[:240])) - first_mean) > 1e-6


def test_single_and_batched_representation_are_deterministic():
    model = H2KForecaster()
    w = _series(120, seed=9)[-96:]
    a, la, sa, qa = model._represent(w)
    b, lb, sb, qb = model._represent(w[None, :].ravel())
    np.testing.assert_array_equal(a, b)
    assert la == lb
    assert sa == sb
    assert qa == qb
