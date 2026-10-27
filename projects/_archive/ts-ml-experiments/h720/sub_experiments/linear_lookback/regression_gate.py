"""S-06 regression gate: models other than the S-06 additions are
byte-identical.

The S-06 Touches list allows behavior changes ONLY for the new-model
wiring (RLinear registry entry, NLinear lookback param usage). This
gate re-fits the canonical models on train.csv and checks their
origin-t=0 predictions against the recorded legacy anchors
(4-decimal reproduction). Anchors include the legacy t=0 NLinear
number (2.3507/2.8173, heuristic/elm sweeps reference config:
default input_length=336, ridge_alpha=1.0, full history).

Run: python sub_experiments/linear_lookback/regression_gate.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

H720_ROOT = Path(__file__).resolve().parent.parent.parent  # h720/
sys.path.insert(0, str(H720_ROOT))

from data import HORIZON, get_protocol_data  # noqa: E402
from methods import HeuristicLagELM, HeuristicLagKNN, make_forecaster  # noqa: E402
from methods.baselines import Persistence, seasonal_forecast  # noqa: E402
from methods.neural_models import NLinear  # noqa: E402

# Legacy t=0 anchors (4-decimal reproduction, same as S-05 gate)
ANCHORS = {
    "elm_h64_full_fastlags": (1.5923, 1.9823, ("elm", {
        "hidden_dim": 64, "history_fraction": 1.0,
        "delays": (1, 2, 3, 6, 12)})),
    "knn_q3_k32_recent10": (1.7204, 2.1405, ("knn", {
        "q": 3, "neighbors": 32, "history_fraction": 0.1,
        "delays": (1, 2, 3, 6, 12, 24)})),
    "persistence": (1.7952, 2.2503, ("persistence", {})),
}
DAILY_ANCHOR = (1.6720, 2.1719)
NLINEAR_ANCHOR = (2.3507, 2.8173)  # t=0, default config (legacy reference)

FAST_LAGS = (1, 2, 3, 6, 12)
DEFAULT_LAGS = (1, 2, 3, 6, 12, 24)


def mae_rmse(pred: np.ndarray, actual: np.ndarray) -> tuple[float, float]:
    err = actual - pred
    return float(np.mean(np.abs(err))), float(np.sqrt(np.mean(err**2)))


def main() -> int:
    pd_data = get_protocol_data()
    fit_history, _, test = pd_data.rolling_views()

    failures: list[str] = []

    def check(name: str, mae: float, rmse: float, expected: tuple[float, float]) -> None:
        ok = abs(mae - expected[0]) < 5e-5 and abs(rmse - expected[1]) < 5e-5
        print(f"{'OK ' if ok else 'FAIL'} {name:<24} {mae:.4f}/{rmse:.4f} "
              f"expected {expected[0]:.4f}/{expected[1]:.4f}")
        if not ok:
            failures.append(name)

    # HeuristicLagELM (rolling leader family)
    m = HeuristicLagELM(hidden_dim=64, history_fraction=1.0, delays=FAST_LAGS)
    m.fit(fit_history, horizon=HORIZON)
    check("elm_h64_full_fastlags", *mae_rmse(m.predict(), test[:HORIZON]),
          (1.5923, 1.9823))

    # HeuristicLagKNN
    m = HeuristicLagKNN(q=3, neighbors=32, history_fraction=0.1, delays=DEFAULT_LAGS)
    m.fit(fit_history, horizon=HORIZON)
    check("knn_q3_k32_recent10", *mae_rmse(m.predict(), test[:HORIZON]),
          (1.7204, 2.1405))

    # Persistence
    m = make_forecaster("persistence")
    m.fit(fit_history, horizon=HORIZON)
    check("persistence", *mae_rmse(m.predict(), test[:HORIZON]),
          (1.7952, 2.2503))

    # Daily seasonal-naive
    pred = seasonal_forecast(fit_history, HORIZON, "daily")
    check("daily", *mae_rmse(pred, test[:HORIZON]), DAILY_ANCHOR)

    # NLinear legacy reference (t=0, default input_length=336, alpha=1.0)
    m = NLinear()  # defaults: input_length=336, ridge_alpha=1.0
    m.fit(fit_history, horizon=HORIZON)
    check("nlinear_default", *mae_rmse(m.predict(), test[:HORIZON]),
          NLINEAR_ANCHOR)

    if failures:
        print(f"\nREGRESSION GATE FAILED: {len(failures)} model(s)")
        return 1
    print("\nRegression gate PASSED — pre-existing models unchanged "
          "(5/5 anchors).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
