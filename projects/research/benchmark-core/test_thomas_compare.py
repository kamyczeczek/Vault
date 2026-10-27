import numpy as np
from thomas_compare import run_comparison
from thomas_models import recursive_delay_forecast


def test_thomas_comparison_structure_and_metrics():
    result = run_comparison(n=500, horizons=(1, 4), origins=(200, 300), locked_origins=(400,))
    assert set(result["models"]) == {"persistence", "nlinear_direct", "ridge_delay_recursive"}
    assert result["development_origins"] == [200, 300]
    assert result["locked_origins"] == [400]
    for model_scores in result["models"].values():
        for split in ("development", "locked"):
            assert set(model_scores[split]) == {1, 4}
            for scores in model_scores[split].values():
                assert scores["origins"] == (2 if split == "development" else 1)
                assert np.isfinite(scores["mae"])
                assert np.isfinite(scores["rmse"])


def test_recursive_delay_forecast_shape_and_finiteness():
    history = np.sin(np.arange(100) / 10)
    prediction = recursive_delay_forecast(history, horizon=8, lag=12)
    assert prediction.shape == (8,)
    assert np.isfinite(prediction).all()
