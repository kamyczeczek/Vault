"""Rolling sweep for Hybrid MultiRateRBF (S-13 bet).

Frozen fit on train.csv (11,425 rows), 2,161 stride-1 origins over test region.
Compares hybrid rates vs parents and leader NLinear.

Configs:
- hybrid (1,)      ≡ RBFELM identity control (should be 2.2812)
- hybrid (1,2)
- hybrid (1,2,4)   ← main bet (S-10 winner rates + RBF)
- hybrid (1,4)
- plus anchors: RBFELM raw, MultiRateELM (1,2,4), NLinear L336, ELM, daily, persistence

Protocol: same as S-10/S-11 rolling_arm.py — fail-loud anchors, deterministic.
"""

import json, sys, pathlib
import numpy as np

# add h720 to path for data.py
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from data import get_protocol_data
from methods.multirate_rbf import MultiRateRBF
from methods.rbf import RBFELM
from methods.multirate import MultiRateELM
from methods.neural_models import NLinear, HeuristicLagELM
from methods.baselines import Persistence, seasonal_forecast

H=720
data = get_protocol_data()
views = data.forecast_views()  # we need rolling_views
# rolling_views is the correct protocol
from data import get_protocol_data as gpd
pd = gpd()
rolling = pd.rolling_views()  # has train, eval_series, test, etc? check
# Use the h720 helper: data.py exposes rolling_views via ProtocolData
# Let's just use pd.rolling_views() directly
rv = pd.rolling_views()
train = rv.train  # private? Actually rolling_views returns train/eval? Let's inspect
print("rolling keys", dir(rv))
# Fallback: use data.rolling_views
try:
    rv2 = data.rolling_views()
    print("data.rolling_views ok", type(rv2))
except Exception as e:
    print("data.rolling_views fail", e)
    rv2 = None

# The canonical rolling runner in prior sweeps uses `data.rolling_views()` -> need to see its return
# Let's introspect data.py
import inspect
print(inspect.getsource(pd.rolling_views)[:800])
