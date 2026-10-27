"""SWT subband-expert: direct Ridge on one SWT subband (cA3/d3/d2/d1), no pooling, no ELM."""
from __future__ import annotations
import numpy as np
import pywt

def _ridge_multioutput(Phi, Y, alpha):
    d = Phi.shape[1]
    A = Phi.T @ Phi + alpha * np.eye(d)
    B = Phi.T @ Y
    try:
        L = np.linalg.cholesky(A)
        W = np.linalg.solve(L.T, np.linalg.solve(L, B))
    except np.linalg.LinAlgError:
        W = np.linalg.solve(A, B)
    return W

class SubbandExpert:
    def __init__(self, band: str = "cA3", input_length: int = 336, wavelet: str = "db4", levels: int = 3, alpha: float = 100.0):
        assert band in ("cA3","d3","d2","d1")
        self.band=band; self.input_length=int(input_length); self.wavelet=wavelet; self.levels=int(levels); self.alpha=float(alpha)
        self._fitted=False

    def _swt_band(self, x_anch):
        coeffs = pywt.swt(x_anch, self.wavelet, level=self.levels)  # [(cA3,cD3),(cA2,cD2),(cA1,cD1)]
        cA3,d3=coeffs[0]; _,d2=coeffs[1]; _,d1=coeffs[2]
        return {"cA3":cA3,"d3":d3,"d2":d2,"d1":d1}[self.band]

    def fit(self, y, *, horizon: int, target_index: int = 0):
        series=np.asarray(y,dtype=float)
        if series.ndim>1: series=series[:,target_index] if target_index < series.shape[1] else series[:,0]
        self.history_=np.asarray(series,dtype=float)
        self.horizon_=int(horizon)
        L=self.input_length; H=self.horizon_
        target=series
        ends=np.arange(L, len(target)-H+1)
        # anchored windows -> SWT band features
        X=np.stack([self._swt_band(target[e-L:e]-float(target[e-1])) for e in ends])
        Y=np.stack([target[e:e+H]-target[e-1] for e in ends])
        self.coef_=_ridge_multioutput(X, Y, self.alpha)  # (336,H)
        self._fitted=True
        return self

    def predict(self):
        if not getattr(self,"_fitted",False): raise RuntimeError("fit before predict")
        w=self.history_[-self.input_length:]; a=float(w[-1]); xa=w-a
        band_vec=self._swt_band(xa)[None,:]
        dhat=(band_vec @ self.coef_)[0]
        return np.asarray(dhat + a, dtype=float)
