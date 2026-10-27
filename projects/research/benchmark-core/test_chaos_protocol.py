import numpy as np
from chaos_protocol import evaluate_forecaster
from bench import gen_thomas


def test_evaluation_is_causal_and_horizon_wise():
    series = gen_thomas(500, seed=7)
    calls = []

    def persistence(history, horizon):
        calls.append(len(history))
        return np.repeat(history[-1], horizon)

    result = evaluate_forecaster(series, persistence, horizons=(1, 4),
                                 origins=(200, 300, 400), min_history=96)
    assert set(result) == {1, 4}
    assert calls == [200, 300, 400, 200, 300, 400]
    for metrics in result.values():
        assert metrics["origins"] == 3
        assert np.isfinite(metrics["mae"])
        assert np.isfinite(metrics["rmse"])


def test_evaluation_rejects_invalid_prediction():
    series = gen_thomas(300)

    def bad_forecaster(history, horizon):
        return np.full(horizon - 1, np.nan)

    try:
        evaluate_forecaster(series, bad_forecaster, horizons=(4,), origins=(200,))
    except ValueError as exc:
        assert "invalid predictions" in str(exc)
    else:
        raise AssertionError("invalid predictions were accepted")
