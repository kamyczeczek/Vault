"""SOTA Literature Baselines for Time-Series Benchmarking.

Includes:
1. DLinear (Decomposition-Linear, AAAI): Moving average trend/seasonal decomposition + two independent linear models.
2. SpectralFFT: Top-K Fourier frequency component extrapolation (Frequency-domain SOTA baseline).
3. ThetaMethod: Classical decomposition (Trend + Ses) for statistical baseline comparison.
4. ARIMA (statsmodels): Classical autoregressive integrated moving average baseline.
5. ETS (statsmodels): Exponential smoothing state space model baseline.
6. RidgeLag: Autoregressive ridge regression over lag features.
"""
from __future__ import annotations
import numpy as np
from sklearn.linear_model import Ridge

def _moving_avg(x, kernel_size):
    pad = (kernel_size - 1) // 2
    padded = np.pad(x, (pad, kernel_size - 1 - pad), mode='edge')
    c = np.cumsum(np.concatenate([[0.0], padded]))
    out = (c[kernel_size:] - c[:-kernel_size]) / kernel_size
    return out

class DLinearBaseline:
    def __init__(self, kernel_size=25):
        self.kernel_size = kernel_size
        self.W_trend_ = None
        self.W_seas_ = None
        self.H_ = 24

    def fit(self, train: np.ndarray, H: int):
        self.H_ = H
        x = np.asarray(train, dtype=float)
        L = len(x)
        if self.kernel_size >= L:
            self.kernel_size = max(3, L // 2 * 2 + 1)

        trend = _moving_avg(x, self.kernel_size)
        seasonal = x - trend

        lookback = min(96, L - H)
        if lookback < 10:
            lookback = max(5, L // 2)

        X_tr, Y_tr = [], []
        for i in range(lookback, L - H + 1):
            X_tr.append(trend[i-lookback:i])
            Y_tr.append(trend[i:i+H])
        if len(X_tr) > 0:
            X_mat = np.array(X_tr)
            Y_mat = np.array(Y_tr)
            A = X_mat.T @ X_mat + 1e-3 * np.eye(X_mat.shape[1])
            self.W_trend_ = np.linalg.solve(A, X_mat.T @ Y_mat)
        else:
            self.W_trend_ = np.zeros((lookback, H))

        X_se, Y_se = [], []
        for i in range(lookback, L - H + 1):
            X_se.append(seasonal[i-lookback:i])
            Y_se.append(seasonal[i:i+H])
        if len(X_se) > 0:
            X_mat = np.array(X_se)
            Y_mat = np.array(Y_se)
            A = X_mat.T @ X_mat + 1e-3 * np.eye(X_mat.shape[1])
            self.W_seas_ = np.linalg.solve(A, X_mat.T @ Y_mat)
        else:
            self.W_seas_ = np.zeros((lookback, H))

    def predict(self, hist: np.ndarray, H: int) -> np.ndarray:
        x = np.asarray(hist, dtype=float)
        trend = _moving_avg(x, min(self.kernel_size, len(x)))
        seasonal = x - trend

        lookback = self.W_trend_.shape[0]
        if len(trend) < lookback:
            trend = np.pad(trend, (lookback - len(trend), 0), mode='edge')
            seasonal = np.pad(seasonal, (lookback - len(seasonal), 0), mode='edge')

        x_t = trend[-lookback:]
        x_s = seasonal[-lookback:]

        pred_trend = x_t @ self.W_trend_
        pred_seas = x_s @ self.W_seas_
        return (pred_trend + pred_seas).ravel()[:H]


class SpectralFFTBaseline:
    def __init__(self, top_k=5):
        self.top_k = top_k
        self.freqs_ = None
        self.amps_ = None
        self.phases_ = None
        self.mean_ = 0.0
        self.H_ = 24

    def fit(self, train: np.ndarray, H: int):
        self.H_ = H
        x = np.asarray(train, dtype=float)
        self.mean_ = np.mean(x)
        xc = x - self.mean_

        fft_vals = np.fft.rfft(xc)
        freqs = np.fft.rfftfreq(len(x))

        amps = np.abs(fft_vals)
        idx = np.argsort(amps)[::-1]
        top_idx = idx[:self.top_k]

        self.freqs_ = freqs[top_idx]
        self.amps_ = amps[top_idx] / len(x) * 2
        self.phases_ = np.angle(fft_vals[top_idx])

    def predict(self, hist: np.ndarray, H: int) -> np.ndarray:
        t = np.arange(len(hist), len(hist) + H)
        pred = np.zeros(H)
        for f, a, p in zip(self.freqs_, self.amps_, self.phases_):
            pred += a * np.cos(2 * np.pi * f * t + p)
        return (pred + np.mean(hist)).ravel()[:H]


class ThetaBaseline:
    def __init__(self):
        self.H_ = 24

    def fit(self, train: np.ndarray, H: int):
        self.H_ = H

    def predict(self, hist: np.ndarray, H: int) -> np.ndarray:
        x = np.asarray(hist, dtype=float)
        drift = (x[-1] - x[0]) / max(1, len(x))
        t = np.arange(1, H + 1)
        return (x[-1] + drift * t).ravel()[:H]


class ARIMABaseline:
    def __init__(self, order=(1, 1, 1)):
        self.order = order
        self.model_fit = None
        self.H_ = 24

    def fit(self, train: np.ndarray, H: int):
        self.H_ = H
        try:
            from statsmodels.tsa.arima.model import ARIMA
            history = np.asarray(train, dtype=float)
            model = ARIMA(history, order=self.order)
            self.model_fit = model.fit()
        except Exception as e:
            self.model_fit = None

    def predict(self, hist: np.ndarray, H: int) -> np.ndarray:
        if self.model_fit is not None:
            try:
                fc = self.model_fit.forecast(steps=H)
                return np.asarray(fc, dtype=float)[:H]
            except Exception:
                pass
        # Fallback to persistence/drift
        x = np.asarray(hist, dtype=float)
        return np.full(H, x[-1])


class ETSBaseline:
    def __init__(self):
        self.model_fit = None
        self.H_ = 24

    def fit(self, train: np.ndarray, H: int):
        self.H_ = H
        try:
            from statsmodels.tsa.holtwinters import ExponentialSmoothing
            history = np.asarray(train, dtype=float)
            model = ExponentialSmoothing(history, trend='add', seasonal=None, initialization_method='estimated')
            self.model_fit = model.fit(optimized=True)
        except Exception as e:
            self.model_fit = None

    def predict(self, hist: np.ndarray, H: int) -> np.ndarray:
        if self.model_fit is not None:
            try:
                fc = self.model_fit.forecast(steps=H)
                return np.asarray(fc, dtype=float)[:H]
            except Exception:
                pass
        x = np.asarray(hist, dtype=float)
        return np.full(H, x[-1])


class RidgeLagBaseline:
    def __init__(self, lookback=48):
        self.lookback = lookback
        self.model = Ridge(alpha=1.0)
        self.H_ = 24

    def fit(self, train: np.ndarray, H: int):
        self.H_ = H
        x = np.asarray(train, dtype=float)
        L = len(x)
        lb = min(self.lookback, L - H)
        if lb < 5:
            lb = max(2, L // 2)
        X_tr, Y_tr = [], []
        for i in range(lb, L - H + 1):
            X_tr.append(x[i-lb:i])
            Y_tr.append(x[i:i+H])
        if len(X_tr) > 0:
            X_mat = np.array(X_tr)
            Y_mat = np.array(Y_tr)
            self.model.fit(X_mat, Y_mat)
        self.lb_ = lb

    def predict(self, hist: np.ndarray, H: int) -> np.ndarray:
        x = np.asarray(hist, dtype=float)
        if len(x) < self.lb_:
            x = np.pad(x, (self.lb_ - len(x), 0), mode='edge')
        feat = x[-self.lb_:][None, :]
        try:
            pred = self.model.predict(feat)
            return pred.ravel()[:H]
        except Exception:
            return np.full(H, x[-1])


def fit_dlinear(train, H):
    m = DLinearBaseline()
    m.fit(train, H)
    return m

def pred_dlinear(model, hist):
    return model.predict(hist, model.H_)

def fit_fft(train, H):
    m = SpectralFFTBaseline()
    m.fit(train, H)
    return m

def pred_fft(model, hist):
    return model.predict(hist, model.H_)

def fit_theta(train, H):
    m = ThetaBaseline()
    m.fit(train, H)
    return m

def pred_theta(model, hist):
    return model.predict(hist, model.H_)

def fit_arima(train, H):
    m = ARIMABaseline()
    m.fit(train, H)
    return m

def pred_arima(model, hist):
    return model.predict(hist, model.H_)

def fit_ets(train, H):
    m = ETSBaseline()
    m.fit(train, H)
    return m

def pred_ets(model, hist):
    return model.predict(hist, model.H_)

def fit_ridgelag(train, H):
    m = RidgeLagBaseline()
    m.fit(train, H)
    return m

def pred_ridgelag(model, hist):
    return model.predict(hist, model.H_)
