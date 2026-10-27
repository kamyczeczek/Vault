import numpy as np
from members.amr_24_168 import AMR24168Forecaster

def test_amr_24168_shapes_and_finite():
    s=np.cumsum(np.random.default_rng(4).normal(size=1400))
    p=AMR24168Forecaster(lookback=336,hdict=32).fit(s,96).predict_hist(s)
    assert p.shape==(96,) and np.isfinite(p).all()

def test_amr_24168_periodic_features():
    m=AMR24168Forecaster(lookback=168)
    x=np.linspace(-1,1,168)
    f=m._extract_features(x)
    assert f.shape[0]==168 and f.shape[1]>0

def test_amr_24168_anchor_rule_levels():
    m=AMR24168Forecaster(lookback=168, weekly_anchor=168)
    win=np.arange(200, dtype=float)
    assert AMR24168Forecaster(anchor_rule="last")._anchor_level(win)==199.0
    assert m.anchor_rule=="weekly"
    assert m._anchor_level(win)==float(np.mean(win[-168:]))
    b=AMR24168Forecaster(anchor_rule="blend")
    assert b._anchor_level(win)==0.5*199.0+0.5*float(np.mean(win[-168:]))

def test_amr_24168_anchor_rule_invalid():
    try:
        AMR24168Forecaster(anchor_rule="bogus"); raise AssertionError("no raise")
    except ValueError:
        pass

def test_amr_24168_anchor_changes_prediction():
    s=np.cumsum(np.random.default_rng(4).normal(size=1400))
    lo=AMR24168Forecaster(anchor_rule="last", lookback=336, hdict=32).fit(s,96).predict_hist(s)
    wk=AMR24168Forecaster(anchor_rule="weekly", lookback=336, hdict=32).fit(s,96).predict_hist(s)
    assert lo.shape==wk.shape and np.isfinite(wk).all()
    assert not np.allclose(lo, wk), "weekly anchor must actually move the forecast"
