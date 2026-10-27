"""S-08 scratch: acceptance pre-check — do MAE-fit weights satisfy
``ensemble <= min(members)`` on validation, and how do the
MSE-comparator weights score on the same metric?

The primary solver minimizes validation rolling MAE directly (convex
f(w) = mean |Rw|; pairwise coordinate descent + ternary line search,
global + deterministic). The MSE-comparator weights
(``mse_weights_``) minimize squared error instead. This scratch
re-fits, prints both weight vectors, and reports the acceptance
boolean for both against the per-member validation rolling MAE.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from data import HORIZON, get_protocol_data  # noqa: E402
from methods.ensemble import CrossFamilyEnsemble  # noqa: E402


def main() -> None:
    pd_data = get_protocol_data()
    fit_history = pd_data.fit_history
    ens = CrossFamilyEnsemble().fit(fit_history, horizon=HORIZON)

    P, A = ens._val_P, ens._val_A  # validation predictions/actuals
    # CELL-order residual matrix (see ensemble.py transpose note):
    # one row per (origin, horizon-step) cell, one column per member.
    R = (P - A[:, None, :]).transpose(0, 2, 1).reshape(-1, 3)

    def val_mae(w):
        return float(np.mean(np.abs(R @ w)))

    names = ["elm", "knn", "daily"]
    solo = {n: val_mae(np.eye(3)[i]) for i, n in enumerate(names)}
    print("member validation MAE:", {k: round(v, 4) for k, v in solo.items()})
    print("MAE-fit weights:", ens.weights_.round(4),
          "-> val MAE", round(val_mae(ens.weights_), 4))
    print("MSE-comparator weights:", ens.mse_weights_.round(4),
          "-> val MAE", round(val_mae(ens.mse_weights_), 4))
    best_member = min(solo.values())
    print("acceptance (MAE-fit):   ensemble",
          round(val_mae(ens.weights_), 4), "<=", round(best_member, 4),
          "->", bool(val_mae(ens.weights_) <= best_member))
    print("acceptance (MSE-comp.): ensemble",
          round(val_mae(ens.mse_weights_), 4), "<=", round(best_member, 4),
          "->", bool(val_mae(ens.mse_weights_) <= best_member))


if __name__ == "__main__":
    main()
