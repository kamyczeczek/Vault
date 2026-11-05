"""S-08 scratch: reconcile the validation-MAE discrepancy.

run_sweep (pre-solver-rewrite) reported on validation windows:
    elm 3.1246 / knn 2.6566 / daily 3.4977 / ensemble 3.1834
The ensemble's internal weight search (same windows claimed) sees:
    elm 3.0897 / knn 3.0930 / daily 3.0962
Daily is stateless, so its number must match — it does not. This
script recomputes the validation daily MAE BOTH ways in one process:
(a) ensemble-internal loop (series slicing), (b) run_sweep's
rolling_mae_over(val_seg, TRAIN_END, fit_history), and (c) direct
hand-rolled windows, to find where the two window sets diverge.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from data import (  # noqa: E402
    HORIZON, TRAIN_END, VALIDATION_END, get_protocol_data,
)
from methods.baselines import seasonal_forecast  # noqa: E402


def main() -> None:
    pd = get_protocol_data()
    fit_history = pd.fit_history
    print(f"fit_history rows: {len(fit_history)} (expect {VALIDATION_END})")

    # (a) ensemble-internal convention: val = LAST validation_rows rows
    val_start = len(fit_history) - 2880
    print(f"(a) val_start = len - 2880 = {val_start}")
    errs_a = []
    for t in range(2880 - HORIZON + 1):
        hist = fit_history[: val_start + t]
        actual = fit_history[val_start + t : val_start + t + HORIZON]
        pred = seasonal_forecast(hist, HORIZON, "daily")
        errs_a.append(np.abs(pred - actual))
    mae_a = float(np.mean(errs_a))

    # (b) run_sweep convention: val_seg = fit_history[TRAIN_END:VALIDATION_END]
    val_seg = fit_history[TRAIN_END:VALIDATION_END]
    seg_start = TRAIN_END
    print(f"(b) seg range [{seg_start}:{VALIDATION_END}] = "
          f"{VALIDATION_END - seg_start} rows")
    per_origin = []
    for t in range(len(val_seg) - HORIZON + 1):
        hist = fit_history[: seg_start + t]
        actual = val_seg[t : t + HORIZON]
        pred = seasonal_forecast(hist, HORIZON, "daily")
        per_origin.append(float(np.mean(np.abs(pred - actual))))
    mae_b = float(np.mean(per_origin))

    # (c) hand check on a single origin (t=0) both ways
    t0_pred_a = seasonal_forecast(fit_history[:val_start], HORIZON, "daily")
    t0_pred_b = seasonal_forecast(fit_history[:seg_start], HORIZON, "daily")
    same_t0 = bool(np.array_equal(t0_pred_a, t0_pred_b))
    print(f"(c) t=0 hist identical: {same_t0} "
          f"(val_start={val_start}, seg_start={seg_start})")

    print(f"(a) ensemble-internal daily val MAE: {mae_a:.4f}")
    print(f"(b) run_sweep-style daily val MAE:   {mae_b:.4f}")
    print(f"match: {np.isclose(mae_a, mae_b)}")


if __name__ == "__main__":
    main()
