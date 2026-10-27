import numpy as np
from bench import get_sunspot
from sunspot_eval import safe_forecast, evaluate_sunspot
from sunspot_methods import get_sunspot_methods
from sunspot_hybrid import hybrid_sunspot_forecast
from sunspot_selector import choose_methods


def test_safe_forecast_nonnegative():
    s=get_sunspot(400); m=get_sunspot_methods()["nlinear_a1"]
    p=safe_forecast(m,s[:300],s[204:300],12)
    assert p.shape==(12,) and np.isfinite(p).all() and (p>=0).all()


def test_hybrid_and_selector():
    s=get_sunspot(500); methods={"persistence":get_sunspot_methods()["persistence"], "hybrid":hybrid_sunspot_forecast}
    p=hybrid_sunspot_forecast(s[:300],s[204:300],12)
    assert p.shape==(12,) and (p>=0).all()
    assert choose_methods(methods,s,(250,300),12) in methods


def test_evaluation_structure():
    r=evaluate_sunspot(n=500,horizons=(1,12),origins=(300,400))
    assert set(r["horizons"])=={1,12}
    assert "nlinear_a1" in r["methods"]
