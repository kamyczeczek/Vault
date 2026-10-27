import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing

x = np.sin(np.linspace(0, 50, 200)) + np.linspace(0, 2, 200)
try:
    model = ARIMA(x, order=(1,1,1)).fit()
    pred = model.forecast(24)
    print("ARIMA OK:", pred.shape)
except Exception as e:
    print("ARIMA failed:", e)

try:
    model = ExponentialSmoothing(x, trend='add', seasonal=None).fit()
    pred = model.forecast(24)
    print("ETS OK:", pred.shape)
except Exception as e:
    print("ETS failed:", e)
