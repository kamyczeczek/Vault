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
