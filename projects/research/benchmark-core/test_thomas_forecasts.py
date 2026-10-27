from pathlib import Path
import numpy as np
from bench import gen_thomas
from plot_thomas_forecasts import forecast_at, plot_forecasts


def test_forecast_at_shapes():
    series = gen_thomas(500)
    forecasts = forecast_at(series, origin=300, horizon=12)
    expected = {"actual", "persistence", "nlinear_a1", "nlinear_a10", "rff_h64", "subband_cA1", "subband_d1", "ridge_delay_recursive"}
    assert expected.issubset(forecasts)
    assert all(np.asarray(value).shape == (12,) for value in forecasts.values())
    assert all(np.isfinite(value).all() for value in forecasts.values())


def test_plot_forecasts_writes_file():
    output = Path("_test_thomas_forecast.png")
    try:
        plot_forecasts(gen_thomas(500), origins=(300,), horizon=12, output=output)
        assert output.exists()
        assert output.stat().st_size > 0
    finally:
        output.unlink(missing_ok=True)
