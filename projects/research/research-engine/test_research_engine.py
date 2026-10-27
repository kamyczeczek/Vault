"""Tests for research_engine.py (AntiLeakageHarness and ModelDiscoveryEngine)."""
from __future__ import annotations

import tempfile
from pathlib import Path
import numpy as np
import pytest

from research_engine import AntiLeakageHarness, ModelDiscoveryEngine, LeakageError


def test_anti_leakage_harness_metrics_are_finite():
    series = np.sin(np.linspace(0, 50, 500)) + 0.1 * np.random.normal(size=500)
    harness = AntiLeakageHarness(train_window=100, horizon=12, embargo=2, step=12)

    def simple_predict(train, horizon):
        return np.full((horizon,), train[-1])

    metrics = harness.evaluate_forecaster(series, simple_predict)
    assert "mae" in metrics
    assert "smape" in metrics
    assert "mase" in metrics
    assert np.isfinite(metrics["mae"])
    assert metrics["n_fallbacks"] == 0


def _clean_fit(series, fit_end, horizon):
    """Fit using data before fit_end only: last-value level."""
    train = np.asarray(series)[:fit_end]
    return {"level": float(train[-1]), "horizon": horizon}


def _clean_pred(model, hist):
    return np.full((model["horizon"],), model["level"])


def _leaky_fit(series, fit_end, horizon):
    """Leak: normalize by the full-series mean, which includes the future."""
    y = np.asarray(series)
    return {"level": float(y[:fit_end][-1] - y.mean()), "horizon": horizon}


def test_c1_passes_clean_and_fails_leaky():
    y = np.sin(np.linspace(0, 20, 600))
    h = AntiLeakageHarness(train_window=200, horizon=24, embargo=4, step=24)
    folds = h.folds(len(y))
    assert folds and all(fe <= vs for _, fe, vs, _ in folds)  # disjoint+embargo
    res = h.check_window_isolation(_clean_fit, _clean_pred, y, fit_end=300)
    assert res["passed"]
    with pytest.raises(LeakageError):
        h.check_window_isolation(_leaky_fit, _clean_pred, y, fit_end=300)


def test_c2_rejects_target_derived_names():
    h = AntiLeakageHarness()
    ok = h.check_features(["lag_1", "lag_24", "hour_sin"])
    assert ok["passed"] and ok["n_features"] == 3
    with pytest.raises(LeakageError):
        h.check_features(["lag_1", "future_mean_24"])


def test_c3_locks_choice_before_test_scores():
    h = AntiLeakageHarness()
    select = ["o0", "o1", "o2"]
    test = ["o3", "o4"]
    scores = {"o0": 1.0, "o1": 0.5, "o2": 0.8, "o3": 0.1, "o4": 0.2}
    pick_best = lambda s: min(s, key=s.get)
    out = h.screened_decision(scores.__getitem__, pick_best, select, test)
    assert out["passed"] and out["choice"] == "o1"
    assert set(out["test_scores"]) == set(test)
    with pytest.raises(LeakageError):
        h.screened_decision(scores.__getitem__, pick_best, ["o0", "o3"], test)  # overlap
    with pytest.raises(LeakageError):
        h.screened_decision(scores.__getitem__, pick_best, [], test)  # nothing to select on


def test_anti_leakage_harness():
    series = np.sin(np.linspace(0, 50, 500)) + 0.1 * np.random.normal(size=500)
    harness = AntiLeakageHarness(train_window=100, horizon=12, embargo=2, step=12)

    def simple_predict(train, horizon):
        return np.full((horizon,), train[-1])

    metrics = harness.evaluate_forecaster(series, simple_predict)
    assert "mae" in metrics
    assert "smape" in metrics
    assert "mase" in metrics
    assert np.isfinite(metrics["mae"])


def test_model_discovery_engine():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir)
        engine = ModelDiscoveryEngine(out_path)

        residuals = np.array([0.1, -0.2, 0.15, -0.05, 0.3, -0.1])
        analysis = engine.analyze_residuals(residuals)
        assert "mean_bias" in analysis
        assert "std_resid" in analysis
        assert "lag1_autocorr" in analysis
        assert np.isfinite(analysis["mean_bias"])

        log_file = engine.log_experiment("test_exp", {"mae": 1.23}, {"model": "naive"})
        assert log_file.exists()
        content = log_file.read_text(encoding="utf-8")
        assert "test_exp" in content
        assert "1.23" in content


def test_s47_refits_on_trailing_window_at_every_origin():
    from s47_ref.rolling_arm import rolling_preds

    series = np.arange(14, dtype=float)
    fit_windows = []

    def fit_fn(train, horizon):
        fit_windows.append(train.copy())
        return float(train[-1])

    def pred_fn(model, history):
        return np.full(2, model)

    preds, actual, origins = rolling_preds(
        series, 2, fit_fn, pred_fn, train_window=4, n_origins=3)
    assert origins == [4, 6, 8]
    for got, expected in zip(fit_windows, ([0, 1, 2, 3], [2, 3, 4, 5], [4, 5, 6, 7])):
        np.testing.assert_array_equal(got, expected)
    np.testing.assert_array_equal(preds, [[3, 3], [5, 5], [7, 7]])
    np.testing.assert_array_equal(actual, [[4, 5], [6, 7], [8, 9]])


def test_s47_select_blends_do_not_use_confirmation_targets():
    from s47_ref.rolling_arm import pool_blend_scores, training_scale

    actual = np.arange(10, dtype=float).reshape(5, 2)
    predictions = {
        "a": actual * 0.9,
        "b": actual * 1.1,
        "c": actual * 0.8 + 0.5,
    }
    select = [0, 1, 2]
    names = ["a", "b", "c"]

    def select_scores(targets):
        scores = {}
        for origin in select:
            fit_origins = [i for i in select if i != origin]
            scores[origin] = pool_blend_scores(
                predictions, targets, names, fit_origins, [origin])[origin]
        return scores

    original_scores = select_scores(actual)
    changed_confirmation = actual.copy()
    changed_confirmation[3:] += 1000
    assert select_scores(changed_confirmation) == original_scores
    original_test = pool_blend_scores(
        predictions, actual, names, select, [3])[3]
    changed_test = pool_blend_scores(
        predictions, changed_confirmation, names, select, [3])[3]
    assert changed_test != original_test

    series = np.arange(6, dtype=float)
    perturbed = series.copy()
    perturbed[3:] += 1000
    assert training_scale(series, train_window=3) == training_scale(
        perturbed, train_window=3)


def test_s47_pool_blend_rejects_fit_score_overlap():
    from s47_ref.rolling_arm import pool_blend_scores

    values = np.ones((3, 2), dtype=float)
    with pytest.raises(LeakageError):
        pool_blend_scores({"a": values}, values, ["a"], [0, 1], [1])


def test_s47_etth1_path_uses_workspace_archive():
    from s47_ref.rolling_arm import ETTH1_CSV

    expected = (Path(__file__).resolve().parents[2] / "_archive" / "datasets" /
                "data" / "ETTh1_h1.csv")
    assert ETTH1_CSV == expected


def test_s47_window_policy_changes_sample_size_not_geometry():
    from s47_ref.rolling_arm import rolling_preds

    series = np.arange(20, dtype=float)
    windows = []

    def fit_fn(train, horizon):
        windows.append(train.copy())
        return float(train[-1])

    def pred_fn(model, history):
        return np.full(2, model)

    rolling_preds(series, 2, fit_fn, pred_fn, train_window=4, n_origins=3)
    assert [len(w) for w in windows] == [4, 4, 4]
    np.testing.assert_array_equal(windows[1], [2, 3, 4, 5])

    windows.clear()
    rolling_preds(series, 2, fit_fn, pred_fn, train_window=4, n_origins=3,
                  window="expanding")
    assert [len(w) for w in windows] == [4, 6, 8]
    np.testing.assert_array_equal(windows[2], series[:8])
    # Both policies fit strictly before the origin they score.
    assert all(w[-1] < origin for w, origin in zip(windows, (4, 6, 8)))

    with pytest.raises(ValueError):
        rolling_preds(series, 2, fit_fn, pred_fn, train_window=4, n_origins=3,
                      window="roll")


def test_s47_window_flag_selects_result_file():
    from s47_ref import rolling_arm

    assert rolling_arm._parse_window([]) == "fixed"
    assert rolling_arm._parse_window(["--window", "expanding"]) == "expanding"
    assert rolling_arm.RESULTS_FILE["fixed"] == "results_s47.json"
    assert rolling_arm.RESULTS_FILE["expanding"] != rolling_arm.RESULTS_FILE["fixed"]
    with pytest.raises(SystemExit):
        rolling_arm._parse_window(["--window", "sideways"])
