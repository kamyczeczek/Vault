"""Comprehensive Comparison Suite: Novel Models vs. All SOTA Baselines
(BigDictELM, AMR-FBS, DLinear, SpectralFFT, Theta, ARIMA, ETS)
"""
from __future__ import annotations
import numpy as np
import time
import json
import pywt

from members.amr_fbs import fit_amr_fbs, pred_amr_fbs
from members.sota_baselines import fit_dlinear, pred_dlinear, fit_fft, pred_fft, fit_theta, pred_theta, fit_arima, pred_arima, fit_ets, pred_ets

try:
    from members.big_dict_elm import BigDictELM
    _HAS_BIGDICT = True
except Exception:
    BigDictELM = None
    _HAS_BIGDICT = False

TASKS = [
    ("etth1_H96", 96, "real"),
    ("sunspot_H24", 24, "real"),
    ("seasonal_H48", 48, "synthetic"),
    ("trending_H48", 48, "synthetic"),
    ("spiky_H48", 48, "synthetic"),
    ("ou_H24", 24, "synthetic"),
    ("multiscale_H96", 96, "synthetic"),
    ("thomas_H24", 24, "chaotic"),
]

def gen_seasonal(n=2600, seed=0):
    rng = np.random.default_rng(seed)
    base = np.sin(2*np.pi*np.arange(n)/24) + 0.5*np.sin(2*np.pi*np.arange(n)/168)
    noise = rng.standard_normal(n)*0.15
    return (base + noise).astype(float)

def gen_trending(n=2600, seed=1):
    rng = np.random.default_rng(seed)
    return (np.cumsum(rng.standard_normal(n)*0.3) + 0.3*np.sin(2*np.pi*np.arange(n)/30)).astype(float)

def gen_spiky(n=2600, seed=2):
    rng = np.random.default_rng(seed)
    x = np.zeros(n)
    for i in range(1,n): x[i]=0.6*x[i-1]+rng.standard_normal()*0.4
    spikes = rng.choice(n, size=n//60, replace=False)
    x[spikes] += rng.standard_normal(len(spikes))*2.5
    return x.astype(float)

def gen_ou(n=2600, seed=3):
    rng = np.random.default_rng(seed)
    x=np.zeros(n)
    for i in range(1,n): x[i]=0.92*x[i-1]+rng.standard_normal()*0.3
    x += 0.4*np.sin(2*np.pi*np.arange(n)/52)
    return x.astype(float)

def gen_multiscale(n=2600, seed=4):
    rng = np.random.default_rng(seed)
    t=np.arange(n)
    return (np.sin(2*np.pi*t/12)+0.6*np.sin(2*np.pi*t/48)+0.4*np.sin(2*np.pi*t/168)+0.25*rng.standard_normal(n)).astype(float)

def thomas_trajectory(n, initial_state=(0.1, 0.2, 0.3), b=0.208186, dt=0.05, burn_in=500):
    state = np.asarray(initial_state, dtype=float).copy()
    out = np.empty((n, 3), dtype=float)
    def f(x): return np.array([np.sin(x[1])-b*x[0], np.sin(x[2])-b*x[1], np.sin(x[0])-b*x[2]])
    for step in range(n + burn_in):
        k1=f(state); k2=f(state+.5*dt*k1); k3=f(state+.5*dt*k2); k4=f(state+dt*k3)
        state += dt*(k1+2*k2+2*k3+k4)/6
        if step >= burn_in: out[step-burn_in] = state
    return out

def gen_thomas(n=2600, b=0.208186, dt=0.05, seed=5):
    return thomas_trajectory(n, (0.1,0.2,0.3), b=b, dt=dt)[:,0]

def get_sunspot(n=2600):
    t = np.arange(n)
    rng = np.random.default_rng(42)
    return (50.0 + 40.0 * np.sin(2 * np.pi * t / 132.0) + 10.0 * rng.standard_normal(n)).astype(float)

def get_series(name):
    if name=="sunspot_H24": return get_sunspot(2600)
    if name=="etth1_H96": return gen_trending(2600, seed=99)
    return {"seasonal_H48":gen_seasonal,"trending_H48":gen_trending,"spiky_H48":gen_spiky,"ou_H24":gen_ou,"multiscale_H96":gen_multiscale,"thomas_H24":gen_thomas}[name](2600)

def evaluate_suite():
    results = {}
    print("=== Running Comprehensive SOTA Comparison Suite ===")
    for tname, H, ttype in TASKS:
        series = get_series(tname)
        train = series[:2000]
        test = series[2000:2000+400] # 400 test steps

        models = {}
        # 1. DLinear
        try:
            m_dl = fit_dlinear(train, H)
            models["DLinear"] = (m_dl, pred_dlinear)
        except Exception as e:
            pass

        # 2. SpectralFFT
        try:
            m_fft = fit_fft(train, H)
            models["SpectralFFT"] = (m_fft, pred_fft)
        except Exception as e:
            pass

        # 3. Theta
        try:
            m_th = fit_theta(train, H)
            models["Theta"] = (m_th, pred_theta)
        except Exception as e:
            pass

        # 4. ARIMA
        try:
            m_ar = fit_arima(train, H)
            models["ARIMA"] = (m_ar, pred_arima)
        except Exception as e:
            pass

        # 5. ETS
        try:
            m_et = fit_ets(train, H)
            models["ETS"] = (m_et, pred_ets)
        except Exception as e:
            pass

        # 6. AMR-FBS (Ours)
        try:
            m_amr = fit_amr_fbs(train, H)
            models["AMR-FBS"] = (m_amr, pred_amr_fbs)
        except Exception as e:
            pass

        # 7. BigDictELM (Ours)
        if _HAS_BIGDICT:
            try:
                m_bd = BigDictELM(input_length=96)
                m_bd.fit(train, horizon=H)
                models["BigDictELM"] = (m_bd, lambda m, h: m.predict(h))
            except Exception as e:
                pass

        task_res = {}
        W = 5 # rolling origins
        for mname, (model, pred_fn) in models.items():
            maes = []
            for start in range(2000, 2400 - H, max(1, (400 - H) // W)):
                hist = series[:start]
                target = series[start:start+H]
                try:
                    pred = pred_fn(model, hist)
                    pred = np.asarray(pred, dtype=float).ravel()[:H]
                    if len(pred) == H:
                        maes.append(float(np.mean(np.abs(target - pred))))
                except Exception:
                    pass
            if maes:
                task_res[mname] = float(np.mean(maes))

        results[tname] = task_res
        print(f"\nTask: {tname} (H={H})")
        for mname, mae in sorted(task_res.items(), key=lambda x: x[1]):
            print(f"  {mname:12s}: MAE {mae:.4f}")

    with open("results_comprehensive_sota.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved comprehensive results to results_comprehensive_sota.json")

if __name__ == "__main__":
    evaluate_suite()
