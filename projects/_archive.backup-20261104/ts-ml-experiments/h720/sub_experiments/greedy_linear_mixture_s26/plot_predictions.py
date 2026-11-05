"""Plot S-26 vs S-20 vs baselines t=0 H=720."""
from pathlib import Path
import sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge

H720_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(H720_ROOT))
from data import HORIZON, get_protocol_data
from methods.neural_models import NLinear, DLinear, RLinear
from methods.baselines import seasonal_forecast
from methods import make_forecaster

TRAIN_END=8545
ALPHAS=[0.1,1.0,3.0,10.0,30.0,100.0,300.0,1000.0,3000.0,10000.0,30000.0]

S20_MEMBERS=[
    ("nlinear_L336_a1", lambda: NLinear(input_length=336, ridge_alpha=1.0)),
    ("nlinear_L96_a1", lambda: NLinear(input_length=96, ridge_alpha=1.0)),
    ("nlinear_L720_a1", lambda: NLinear(input_length=720, ridge_alpha=1.0)),
    ("dlinear_L96_k25_a0", lambda: DLinear(input_length=96, kernel_size=25, ridge_alpha=0.0)),
    ("dlinear_L336_k25_a0", lambda: DLinear(input_length=336, kernel_size=25, ridge_alpha=0.0)),
    ("dlinear_L720_k25_a0", lambda: DLinear(input_length=720, kernel_size=25, ridge_alpha=0.0)),
]
S26_MEMBERS=[
    ("nlinear_L336_a1", lambda: NLinear(input_length=336, ridge_alpha=1.0)),
    ("nlinear_L336_a10", lambda: NLinear(input_length=336, ridge_alpha=10.0)),
    ("nlinear_L720_a1", lambda: NLinear(input_length=720, ridge_alpha=1.0)),
]

def fit_stack_map(P,A,alpha):
    n,m,h=P.shape; coef=np.empty((m,h)); inter=np.zeros(h)
    for k in range(h):
        r=Ridge(alpha=alpha, fit_intercept=False).fit(P[:,:,k], A[:,k]); coef[:,k]=r.coef_
    class M:
        def predict(self, Pt): return np.einsum("mh,nmh->nh", coef, Pt)
    return M()

def preds_for(factory, series, starts):
    m=factory(); m.fit(series, horizon=HORIZON)
    out=[]
    for s in starts:
        m.history_=series[:s]
        out.append(np.asarray(m.predict(), dtype=float))
    return np.asarray(out)

def collect(members, fit_series, starts):
    cols=[preds_for(f, fit_series, starts) for _,f in members]
    return np.stack(cols, axis=1)

def s20_s26_predictions():
    pd=get_protocol_data()
    fit_series, _, test_series = pd.rolling_views()
    y_true=test_series[:HORIZON]
    val_series=fit_series[TRAIN_END:]
    n_val=len(val_series)-HORIZON+1
    val_starts=np.arange(n_val)+TRAIN_END
    # S-20 val
    P_val20=collect(S20_MEMBERS, fit_series, val_starts)
    A_val=np.stack([val_series[t:t+HORIZON] for t in range(n_val)])
    n2=n_val//2
    best=None; best_a=None
    for a in ALPHAS:
        r=fit_stack_map(P_val20[:n2], A_val[:n2], a)
        sel=float(np.mean(np.mean(np.abs(r.predict(P_val20[n2:])-A_val[n2:]),axis=1)))
        if best is None or sel<best: best=sel; best_a=a
    stack20=fit_stack_map(P_val20, A_val, best_a)
    # S-26 val
    P_val26=collect(S26_MEMBERS, fit_series, val_starts)
    best=None; best_a26=None
    for a in ALPHAS:
        r=fit_stack_map(P_val26[:n2], A_val[:n2], a)
        sel=float(np.mean(np.mean(np.abs(r.predict(P_val26[n2:])-A_val[n2:]),axis=1)))
        if best is None or sel<best: best=sel; best_a26=a
    stack26=fit_stack_map(P_val26, A_val, best_a26)
    # frozen test t=0 (and also 4 disjoint for metrics)
    concat=np.concatenate([fit_series, test_series])
    # single t0
    t0_start=len(fit_series)
    P20_t0=collect(S20_MEMBERS, concat, np.array([t0_start]))
    P26_t0=collect(S26_MEMBERS, concat, np.array([t0_start]))
    pred20=stack20.predict(P20_t0)[0]
    pred26=stack26.predict(P26_t0)[0]
    # also disjoint 4 for title
    disj_starts=np.array([len(fit_series)+s for s in (0,720,1440,2160)])
    # but we just need t0
    return y_true, pred20, pred26, (best_a, best_a26)

def main():
    y_true, pred20, pred26, (a20,a26) = s20_s26_predictions()
    # baselines
    train, test = get_protocol_data().forecast_views()
    m=make_forecaster("nlinear", input_length=336); m.fit(train, horizon=HORIZON); pred_nl=m.predict()
    daily=seasonal_forecast(train, HORIZON, "daily")
    persist=make_forecaster("persistence"); persist.fit(train, horizon=HORIZON); pred_p=persist.predict()

    x=np.arange(HORIZON)
    # compute MAE for legend
    def mae(a,b): return float(np.mean(np.abs(a-b)))
    out_dir=Path(__file__).resolve().parent
    fig, axes=plt.subplots(2,2, figsize=(14,9), sharex=True, sharey=True)
    axes=axes.flatten()
    plots=[
        ("S-20 ridge 6-member (1.9980 full, t0 %.4f) a=%s" % (mae(pred20,y_true), a20), pred20, "tab:blue"),
        ("S-26 greedy 3-member (1.9882 full, t0 %.4f) a=%s" % (mae(pred26,y_true), a26), pred26, "tab:orange"),
        ("NLinear L336 (2.0571, t0 %.4f)" % mae(pred_nl,y_true), pred_nl, "tab:green"),
        ("Daily (2.5491, t0 %.4f)" % mae(daily,y_true), daily, "tab:red"),
    ]
    for ax,(title,pred,color) in zip(axes, plots):
        ax.plot(x, y_true, color="black", linewidth=1.0, label="truth", alpha=0.9)
        ax.plot(x, pred, color=color, linewidth=1.2, label="pred")
        ax.fill_between(x, y_true, pred, color=color, alpha=0.08)
        ax.set_title(title, fontsize=9)
        ax.grid(True, linewidth=0.3, alpha=0.5)
        ax.legend(fontsize=7, loc="upper right")
        ax.set_xlim(0, HORIZON-1)
    axes[0].set_ylabel("OT")
    axes[2].set_ylabel("OT")
    axes[2].set_xlabel("horizon step (0..719)")
    axes[3].set_xlabel("horizon step (0..719)")
    # overlay inset: S-20 vs S-26 diff
    fig2, ax2 = plt.subplots(figsize=(10,3.5))
    ax2.plot(x, y_true, color="black", linewidth=1.0, label="truth")
    ax2.plot(x, pred20, color="tab:blue", linewidth=1.0, label=f"S-20 (MAE {mae(pred20,y_true):.4f})")
    ax2.plot(x, pred26, color="tab:orange", linewidth=1.0, label=f"S-26 (MAE {mae(pred26,y_true):.4f})")
    ax2.fill_between(x, pred20, pred26, color="gray", alpha=0.15, label="S20-S26 diff")
    ax2.set_title("Overlay: S-20 vs S-26 vs truth (t=0 window test[:720]) — full rolling S-20 1.9980 vs S-26 1.9882", fontsize=10)
    ax2.set_xlabel("horizon step"); ax2.set_ylabel("OT"); ax2.grid(True, linewidth=0.3, alpha=0.5); ax2.legend(fontsize=8)
    fig.suptitle("H=720 ETTh1 predictions vs truth — t=0 origin (test[:720], train=11425 frozen)", fontsize=12)
    fig.tight_layout(rect=[0,0,1,0.96])
    p1=out_dir/"prediction_plots_s26.png"
    p2=out_dir/"prediction_overlay_s26.png"
    fig.savefig(p1, dpi=150); print(f"saved {p1}")
    fig2.tight_layout(); fig2.savefig(p2, dpi=150); print(f"saved {p2}")
    # also print window metrics for reference
    print(f"t0 MAE S-20 {mae(pred20,y_true):.4f} S-26 {mae(pred26,y_true):.4f} NLinear {mae(pred_nl,y_true):.4f}")

if __name__=="__main__":
    main()
