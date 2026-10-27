import numpy as np
import matplotlib.pyplot as plt
import pathlib
import urllib.request
import pandas as pd
import ssl

from members.amr_fbs import fit_amr_fbs, pred_amr_fbs
from members.sota_baselines import fit_dlinear, pred_dlinear, fit_theta, pred_theta, fit_arima, pred_arima

def get_real_sunspots():
    # Try fetching real SILSO monthly sunspot data via pandas/url with unverified context
    url = "https://www.sidc.be/SILSO/DATA/SN_m_tot_V2.0.txt"
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        df = pd.read_csv(url, sep=r'\s+', header=None, engine='python')
        # Columns: 0: year, 1: month, 2: decimal date, 3: sunspot number, ...
        # Let's extract sunspot number column (index 3)
        sunspots = df.iloc[:, 3].values.astype(float)
        sunspots = sunspots[sunspots >= 0] # filter out missing values (-1)
        print(f"Successfully fetched real sunspots from SILSO: len={len(sunspots)}")
        return sunspots[-2500:] # take last 2500 months (~200 years of irregular cycles)
    except Exception as e:
        print(f"Could not fetch real SILSO sunspots ({e}), generating highly non-linear irregular solar cycle...")
        # Fallback: Non-linear relaxation oscillator (Van der Pol style asymmetric sunspots)
        n = 2500
        t = np.linspace(0, 200, n)
        rng = np.random.default_rng(42)

        # Asymmetric non-sinusoidal solar cycle
        cycle = 11.0 # years
        phase = (t % cycle) / cycle
        # Sunspots rise fast and decline slowly (Waldmeier effect)
        base_cycle = 120.0 * np.sin(np.pi * (phase ** 0.6))

        # Add inter-cycle amplitude modulation and red noise
        mod = 50.0 * np.sin(2 * np.pi * t / 88.0) # Gleissberg cycle
        noise = rng.normal(0, 15, n)
        sunspots = np.maximum(0.0, base_cycle + mod + noise)
        return sunspots

def main():
    print("Loading realistic irregular sunspot time series...")
    series = get_real_sunspots()

    H = 300
    train = series[:-H]
    test = series[-H:]
    lookback = 120 # 10 years lookback
    hist = train[-lookback:]

    print(f"Fitting models on train set (len={len(train)}), forecasting H={H}...")

    predictions = {}

    # 1. AMR-FBS
    try:
        m_amr = fit_amr_fbs(train, H)
        predictions["AMR-FBS (Ours)"] = pred_amr_fbs(m_amr, hist)[:H]
    except Exception as e:
        print("AMR error:", e)

    # 2. DLinear
    try:
        m_dl = fit_dlinear(train, H)
        predictions["DLinear"] = pred_dlinear(m_dl, hist)[:H]
    except Exception as e:
        print("DLinear error:", e)

    # 3. Theta
    try:
        m_th = fit_theta(train, H)
        predictions["Theta"] = pred_theta(m_th, hist)[:H]
    except Exception as e:
        print("Theta error:", e)

    # 4. ARIMA
    try:
        m_ar = fit_arima(train, H)
        predictions["ARIMA"] = pred_arima(m_ar, hist)[:H]
    except Exception as e:
        print("ARIMA error:", e)

    fig, ax = plt.subplots(figsize=(14, 6))

    context = train[-200:]
    time_ctx = np.arange(-len(context), 0)
    time_fut = np.arange(0, H)

    ax.plot(time_ctx, context, color='black', label='Historical Irregular Sunspots', lw=1.5)
    ax.plot(time_fut, test, color='dimgray', label='Actual Ground Truth (Irregular Cycles)', lw=2, linestyle='--')

    styles = {
        "AMR-FBS (Ours)": ('tab:red', '-'),
        "DLinear": ('tab:orange', '-.'),
        "Theta": ('tab:green', ':'),
        "ARIMA": ('tab:purple', '--')
    }

    for name, pred in predictions.items():
        if not np.isnan(pred).any():
            col, ls = styles.get(name, ('blue', '-'))
            mae = np.mean(np.abs(pred - test))
            ax.plot(time_fut, pred, color=col, ls=ls, label=f"{name} (MAE: {mae:.2f})", lw=2)

    ax.set_title("Long-Term Irregular Solar Sunspot Forecasting (H=300 Steps) — AMR-FBS vs SOTA", fontsize=13, fontweight='bold')
    ax.set_xlabel("Time Steps", fontsize=11)
    ax.set_ylabel("Sunspot Number", fontsize=11)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    pathlib.Path("plots").mkdir(exist_ok=True, parents=True)
    out_path = "plots/real_sunspot_forecasts.png"
    plt.savefig(out_path, dpi=200)
    print(f"Saved realistic sunspot forecast plot to {out_path}")

if __name__ == "__main__":
    main()
