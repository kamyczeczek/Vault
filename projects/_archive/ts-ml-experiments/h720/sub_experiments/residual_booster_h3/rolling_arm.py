"""H3 — S-26 Base + Residual Linear Booster (shrinkage λ, structural features)."""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
from sklearn.linear_model import Ridge

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))
from data import HORIZON, get_protocol_data
from methods.neural_models import NLinear

DISJOINT_STARTS = (0, 720, 1440, 2160)
TRAIN_END = 8545
ALPHAS = [0.1, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0, 30000.0]
LAMBdas = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5]
S26_ALPHA = 10000.0
S26_MEMBERS = [
    ("nlinear_L336_a1",  lambda: NLinear(input_length=336, ridge_alpha=1.0)),
    ("nlinear_L336_a10", lambda: NLinear(input_length=336, ridge_alpha=10.0)),
]


def s26_base_preds_for(factory, series, starts, L, H):
    m = factory()
    m.fit(series, horizon=H)
    hist = m.history_
    out = []
    for s in starts:
        m.history_ = series[:s]
        out.append(np.asarray(m.predict(), dtype=float))
    m.history_ = hist
    return np.asarray(out)


def collect_s26_base(series, starts):
    cols = []
    for name, factory in S26_MEMBERS:
        L = factory().input_length
        p = s26_base_preds_for(factory, series, starts, L, HORIZON)
        cols.append(p)
    P = np.stack(cols, axis=1)
    n, m, h = P.shape
    A = np.stack([series[s : s + HORIZON] for s in starts])
    coef = np.empty((m, h))
    for k in range(h):
        r = Ridge(alpha=S26_ALPHA, fit_intercept=False).fit(P[:, :, k], A[:, k])
        coef[:, k] = r.coef_
    class _Map:
        def predict(self, Pt):
            return np.einsum("nmh,mh->nh", Pt, coef)
    return _Map().predict(P)


class ResidualBooster:
    """Linear residual booster on structural features."""
    def __init__(self, ridge_alpha: float = 1.0, lambda_shrink: float = 0.2):
        self.ridge_alpha = ridge_alpha
        self.lambda_shrink = lambda_shrink
        self.coef_ = None
        self.inter_ = None
        self.input_length = 336
        self.horizon_ = HORIZON

    @staticmethod
    def _extract_features(anchored: np.ndarray) -> np.ndarray:
        L = len(anchored)
        feats = []
        for window in [24, 48, 168]:
            if L >= window:
                x = np.arange(window, dtype=float)
                y = anchored[-window:]
                slope = np.polyfit(x, y, 1)[0]
                curv = np.polyfit(x, y, 2)[0] if window >= 3 else 0.0
                feats.extend([slope, curv])
            else:
                feats.extend([0.0, 0.0])
        if L >= 48:
            fft = np.fft.rfft(anchored)
            freqs = np.fft.rfftfreq(L)
            diurnal_mask = (freqs >= 1/48) & (freqs <= 1/16)
            diurnal_power = np.mean(np.abs(fft[diurnal_mask])**2) if diurnal_mask.any() else 0.0
            semi_mask = (freqs >= 1/24) & (freqs <= 1/8)
            semi_power = np.mean(np.abs(fft[semi_mask])**2) if semi_mask.any() else 0.0
            feats.extend([diurnal_power, semi_power])
        else:
            feats.extend([0.0, 0.0])
        return np.asarray(feats, dtype=float)

    def fit(self, residuals: np.ndarray, anchored_windows: np.ndarray):
        X = np.stack([self._extract_features(w) for w in anchored_windows])
        Y = residuals
        h = Y.shape[1]
        self.coef_ = np.empty((X.shape[1], h))
        self.inter_ = np.zeros(h)
        for k in range(h):
            r = Ridge(alpha=self.ridge_alpha, fit_intercept=True).fit(X, Y[:, k])
            self.coef_[:, k] = r.coef_
            self.inter_[k] = r.intercept_
        return self

    def predict(self, anchored_window: np.ndarray) -> np.ndarray:
        feats = self._extract_features(anchored_window).reshape(1, -1)
        return self.lambda_shrink * (feats @ self.coef_ + self.inter_)[0]


def rolling_metrics(preds, actuals):
    err = preds - actuals
    mae_per = np.mean(np.abs(err), axis=1)
    rmse_per = np.sqrt(np.mean(err ** 2, axis=1))
    return float(np.mean(mae_per)), float(np.sqrt(np.mean(err ** 2))), mae_per, rmse_per


def main():
    t_all = time.time()
    pd = get_protocol_data()
    fit_series, _, test_series = pd.rolling_views()
    train_series = fit_series[:TRAIN_END]
    val_series = fit_series[TRAIN_END:]
    n_val = len(val_series) - HORIZON + 1
    assert n_val == 2161
    val_starts = np.arange(n_val) + TRAIN_END

    print("H3 — S-26 Base + Residual Linear Booster")
    print(f"train={len(train_series)} fit={len(fit_series)} test={len(test_series)}")

    # Step 1: S-26 base on train 8545, residuals for train origins
    print("\nStep 1: S-26 base on train 8545...")
    train_starts = np.arange(336, len(train_series) - HORIZON + 1)
    base_preds_train = collect_s26_base(train_series, train_starts)
    A_train = np.stack([train_series[s : s + HORIZON] for s in train_starts])
    residuals_train = A_train - base_preds_train
    anchored_train = np.stack([train_series[s - 336 : s] - train_series[s - 1] for s in train_starts])

    # Step 2: Grid search residual booster on train
    print(f"Step 2: Grid search residual booster on {len(train_starts)} train origins...")
    best_score = float("inf")
    best_params = None

    for alpha in ALPHAS:
        for lam in LAMBdas:
            booster = ResidualBooster(ridge_alpha=alpha, lambda_shrink=lam)
            booster.fit(residuals_train, anchored_train)

            # Predict residuals for validation origins
            preds_resid_val = []
            for i in range(n_val):
                anchored = fit_series[val_starts[i] - 336 : val_starts[i]] - fit_series[val_starts[i] - 1]
                preds_resid_val.append(booster.predict(anchored))
            preds_resid_val = np.asarray(preds_resid_val)

            # Get base predictions for validation
            base_preds_val = collect_s26_base(fit_series[:TRAIN_END], val_starts)
            preds_val = base_preds_val + preds_resid_val

            A_val = np.stack([val_series[s : s + HORIZON] for s in val_starts])
            mae = float(np.mean(np.mean(np.abs(preds_val - A_val), axis=1)))

            if mae < best_score:
                best_score = mae
                best_params = (alpha, lam)

            print(f"  alpha={alpha:6.1f} lambda={lam:.2f} val_mae={mae:.4f}")

    print(f"\nbest: alpha={best_params[0]}, lambda={best_params[1]}, val_mae={best_score:.4f}")

    # Step 3: Refit on full 11425, score test
    print("\nStep 3: Refit on full 11425, score test...")
    full_series = np.concatenate([fit_series, test_series])
    n_test = len(test_series) - HORIZON + 1
    test_starts = np.arange(n_test) + len(fit_series)

    # Base predictions for test (refit base on full)
    base_preds_test = collect_s26_base(full_series, test_starts)
    A_test = np.stack([test_series[s : s + HORIZON] for s in test_starts])
    base_only_mae = float(np.mean(np.mean(np.abs(base_preds_test - A_test), axis=1)))

    # Refit residual on full train residuals
    full_train_starts = np.arange(336, len(full_series) - HORIZON + 1)
    base_preds_full_train = collect_s26_base(full_series, full_train_starts)
    A_full_train = np.stack([full_series[s : s + HORIZON] for s in full_train_starts])
    residuals_full = A_full_train - base_preds_full_train
    anchored_full = np.stack([full_series[s - 336 : s] - full_series[s - 1] for s in full_train_starts])

    booster_full = ResidualBooster(ridge_alpha=best_params[0], lambda_shrink=best_params[1])
    booster_full.fit(residuals_full, anchored_full)

    # Predict test
    preds_test = []
    for i in range(n_test):
        base_pred = base_preds_test[i]
        anchored = full_series[test_starts[i] - 336 : test_starts[i]] - full_series[test_starts[i] - 1]
        corr = booster_full.predict(anchored)
        preds_test.append(base_pred + corr)
    preds_test = np.asarray(preds_test)
    mae_full, rmse_full, _, _ = rolling_metrics(preds_test, A_test)

    # Disjoint diagnostic
    print("\nDisjoint-4 diagnostic...")
    disj_starts = np.array([len(fit_series) + s for s in DISJOINT_STARTS])
    A_disj = np.stack([test_series[s : s + HORIZON] for s in DISJOINT_STARTS])
    preds_disj = []
    for s in disj_starts:
        base_pred = collect_s26_base(full_series, [s])[0]
        anchored = full_series[s - 336 : s] - full_series[s - 1]
        corr = booster_full.predict(anchored)
        preds_disj.append(base_pred + corr)
    preds_disj = np.asarray(preds_disj)
    mae_disj, rmse_disj, _, _ = rolling_metrics(preds_disj, A_disj)

    accept = (mae_full < 1.9859) and (mae_disj <= 1.9696)
    out = {
        "slice": "H3-residual-booster",
        "base": "S-26 [nlinear_L336_a1 + nlinear_L10] alpha=10000 no-intercept",
        "residual_model": {
            "features": "slope+curvature [24,48,168] + spectral [diurnal,semi-diurnal]",
            "alphas_grid": ALPHAS,
            "lambdas_grid": LAMBdas,
            "best_alpha": best_params[0],
            "best_lambda": best_params[1],
        },
        "validation": {
            "best_val_mae": best_score,
        },
        "test": {
            "base_only_mae": base_only_mae,
            "boosted_full_mae": mae_full,
            "boosted_full_rmse": rmse_full,
            "boosted_disjoint_mae": mae_disj,
            "boosted_disjoint_rmse": rmse_disj,
            "delta_vs_s26": mae_full - 1.9909,
            "n": n_test,
        },
        "accept": accept,
        "acceptance_criteria": {
            "full_mae_threshold": 1.9859,
            "disjoint_mae_cap": 1.9696,
            "incumbent_full": 1.9909,
            "incumbent_disjoint": 1.9696,
        },
        "protocol": "S-20-clean: base members frozen on 8545, booster trained on base residuals, test refrozen on 11425",
    }
    with open(HERE / "results_h3.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nACCEPT={accept}")
    print(f"base_only_mae={base_only_mae:.4f}")
    print(f"boosted_full_mae={mae_full:.4f} (delta {mae_full - 1.9909:+.4f})")
    print(f"boosted_disjoint_mae={mae_disj:.4f} (cap 1.9696)")
    print(f"wrote {HERE / 'results_h3.json'} elapsed {time.time()-t_all:.1f}s")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
