from pathlib import Path
import numpy as np
from plot_sunspot_longterm import forecast_sunspot, plot_sunspot_longterm
from bench import get_sunspot


def test_sunspot_forecast_shapes():
    series = get_sunspot(500)
    forecasts = forecast_sunspot(series, origin=300, horizon=24)
    assert "actual" in forecasts
    expected = {"persistence", "nlinear_a1", "nlinear_a10", "rff_h64", "subband_cA1", "subband_d1", "bigdict_elm", "bigdict_tree", "subband_bigdict", "esn_reservoir", "deterministic_esn", "ridge_delay_recursive"}
    assert expected.intersection(forecasts) >= {"persistence", "nlinear_a1"}
    assert all(np.asarray(x).shape == (24,) for x in forecasts.values())
    assert all(np.isfinite(x).all() for x in forecasts.values())


def test_sunspot_plot():
    output = Path("_test_sunspot_longterm.png")
    try:
        plot_sunspot_longterm(origin=300, horizon=24, output=output)
        assert output.exists() and output.stat().st_size > 0
    finally:
        output.unlink(missing_ok=True)
