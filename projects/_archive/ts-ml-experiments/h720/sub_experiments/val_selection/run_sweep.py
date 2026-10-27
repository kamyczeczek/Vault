"""Sub-experiment: validation-split model re-selection (S-02).

Question: the current winning configs (ELM hidden 64 / full history /
normal init; kNN q=3, k=32, recent-10%) were tuned against the legacy
single 720-row window (test.csv[:720]) — a high-variance one-window
protocol. How much of their standing is a *window-tuning artifact*?
Each family's config is re-selected on held-out validation data and
the test-region delta between validation-selected and window-tuned
configs is reported.

Protocol (pinned in ``PROCESS/03_plan/slices.md`` S-02):
- **Validation phase (selection)**: every candidate is fit exactly once
  on ``fit_history[:8545]`` — the TRAIN-ONLY slice (asserted in-script;
  never the full 11,425-row fit history) — then rolled over the
  2,880-row validation segment: 2,161 stride-1 origins ``t in
  [0, 2160]``; history at origin ``t`` is ``fit_history[:8545+t]``
  (all rows strictly before the scored window ``validation[t:t+720]``).
- **Test phase (scoring, once)**: every candidate is fit exactly once
  on all of ``train.csv`` (11,425 rows) — the locked protocol — then
  rolled over the full test region per S-01: 2,161 stride-1 origins,
  history ``eval_series[:11425+t]``, scored vs ``test[t:t+720]``.
  Selection consults validation numbers only; the test region is
  scored once per candidate and never used for selection.

Grid: 18 candidates
- ELM: hidden_dim {64,256} x history_fraction {0.1,0.5,1.0} x
  weight_init {normal,sobol_iid}, delays (1,2,3,6,12)          -> 12
- kNN: q=3, history_fraction=0.1, delays (1,2,3,6,12,24),
  k in {8,16,24,32}                                            -> 4
- daily (seasonal-naive lag 24) + persistence references       -> 2

Legacy window-tuned configs under study (both scored identically on
test): ELM ``elm_h64_f100_normal`` (hidden 64, fraction 1.0, normal),
kNN ``knn_q3_k32_recent10`` (k=32).

Anti-leakage: history slices end one row before the scored window —
structurally guaranteed by the slicing, asserted per origin. The
validation phase never touches test data; the test phase fits never
see validation rolling scores before selection is recorded (selection
is computed from the val numbers alone).

Anchors (fail-loud — any mismatch aborts the run, no results.json):
- Validation t=0 (train-only fit): daily 2.4645/2.9771,
  persistence 3.2365/3.7233 (deterministic references, self-pinned
  under this protocol).
- Test t=0 (full 11,425-row fit): legacy leaderboard / sobol-sweep
  published numbers for every grid config that appears there (7 rows).
- Test-region rolling means must reproduce the S-01 harness
  (``sub_experiments/rolling_eval/results.json``) for the five configs
  it published (identical computation; tol 1e-4 vs 4-decimal values).

Determinism: model constructors seed 42 (ELM weight draw
RandomState(42) / scrambled Sobol seed 42); this runner has no RNG.

Outputs (in this directory):
- ``results.json`` — per-candidate val + test rolling metrics,
  selection table, anchors
- ``CONTEXT.md``   — results section (written by hand after the run)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

H720_ROOT = Path(__file__).resolve().parent.parent.parent  # h720/
sys.path.insert(0, str(H720_ROOT))
from data import HORIZON, TRAIN_ROWS, VALIDATION_END, get_protocol_data  # noqa: E402
from methods import HeuristicLagELM, HeuristicLagKNN, make_forecaster  # noqa: E402
from methods.baselines import Persistence, seasonal_forecast  # noqa: E402

SWEEP_DIR = H720_ROOT / "sub_experiments" / "val_selection"

FAST_LAGS = (1, 2, 3, 6, 12)
DEFAULT_LAGS = (1, 2, 3, 6, 12, 24)
DISJOINT_STARTS = (0, 720, 1440, 2160)

# Validation-phase t=0 anchors (train-only frozen fit): deterministic
# references pinning the fit-slice + history-slicing machinery.
VAL_ANCHORS = {
    "daily": (2.4645, 2.9771),
    "persistence": (3.2365, 3.7233),
}

# Test-phase t=0 anchors (full 11,425-row fit) — legacy published
# numbers (leaderboard / sobol sweep) for every grid config on them.
TEST_ANCHORS = {
    "elm_h64_f100_normal": (1.5923, 1.9823),
    "elm_h64_f100_sobol_iid": (2.0317, 2.4419),
    "elm_h256_f100_normal": (1.7108, 2.1425),
    "elm_h256_f100_sobol_iid": (1.6330, 2.0550),
    "knn_q3_k32_recent10": (1.7204, 2.1405),
    "daily": (1.6720, 2.1719),
    "persistence": (1.7952, 2.2503),
}

# Test-region rolling means must reproduce the S-01 harness exactly
# (sub_experiments/rolling_eval/results.json; stored 4-decimal -> tol 1e-4).
ROLLING_ANCHORS = {
    "elm_h64_f100_normal": (2.3092, 2.8046),
    "elm_h256_f100_sobol_iid": (2.3409, 2.8431),
    "knn_q3_k32_recent10": (2.5583, 3.0994),
    "daily": (2.5491, 3.1120),
    "persistence": (2.5985, 3.1282),
}

LEGACY_TUNED = {"elm": "elm_h64_f100_normal", "knn": "knn_q3_k32_recent10"}


def mae_rmse(pred: np.ndarray, actual: np.ndarray) -> tuple[float, float]:
    err = actual - pred
    return float(np.mean(np.abs(err))), float(np.sqrt(np.mean(err**2)))


def rolling_metrics(per_origin: np.ndarray) -> tuple[float, float, dict]:
    """Aggregate per-origin (mae, rmse) rows into rolling + disjoint views."""
    rolling_mae = float(np.mean(per_origin[:, 0]))
    rolling_rmse = float(np.mean(per_origin[:, 1]))
    disjoint = {
        f"window_{i + 1}": {
            "mae": float(per_origin[t, 0]),
            "rmse": float(per_origin[t, 1]),
        }
        for i, t in enumerate(DISJOINT_STARTS)
    }
    return rolling_mae, rolling_rmse, disjoint


def evaluate_rolling(
    name: str, model, base_series: np.ndarray, base_len: int,
    score_segment: np.ndarray,
) -> tuple[tuple[float, float, dict], np.ndarray]:
    """Frozen-fit rolling evaluation over ``score_segment`` (2,880 rows).

    ``base_series`` is ``fit_history ++ score_segment`` (chronological).
    At origin ``t`` the model's ``history_`` is set to
    ``base_series[:base_len + t]`` — every observed row strictly before
    the scored window ``score_segment[t:t+720]`` — and ``predict()`` is
    called fresh (no refit, no state carry-over between origins).
    ``Persistence`` additionally re-sets ``last_value_``.
    """
    assert len(base_series) == base_len + len(score_segment), \
        f"{name}: base/score geometry broken"
    n_origins = len(score_segment) - HORIZON + 1  # 2,161
    per_origin = np.empty((n_origins, 2), dtype=float)

    is_persistence = isinstance(model, Persistence)
    for t in range(n_origins):
        # Anti-leakage: history ends one row before the scored window.
        assert base_len + t + HORIZON <= len(base_series), \
            f"{name}: scored window overruns series"
        hist = base_series[: base_len + t]
        actual = score_segment[t : t + HORIZON]

        model.history_ = hist
        if is_persistence:
            model.last_value_ = float(hist[-1])
        pred = model.predict()

        assert len(pred) == HORIZON, f"{name}: predict returned {len(pred)}"
        per_origin[t] = mae_rmse(pred, actual)

    return rolling_metrics(per_origin), per_origin


def evaluate_daily_rolling(
    base_series: np.ndarray, base_len: int, score_segment: np.ndarray,
) -> tuple[tuple[float, float, dict], np.ndarray]:
    """Rolling seasonal-naive (lag 24) — function-based, no fitted state."""
    assert len(base_series) == base_len + len(score_segment)
    n_origins = len(score_segment) - HORIZON + 1
    per_origin = np.empty((n_origins, 2), dtype=float)
    for t in range(n_origins):
        hist = base_series[: base_len + t]
        pred = seasonal_forecast(hist, HORIZON, "daily")
        per_origin[t] = mae_rmse(pred, score_segment[t : t + HORIZON])
    return rolling_metrics(per_origin), per_origin


def build_candidates() -> list[dict]:
    """18 candidates: 12 ELM + 4 kNN + daily + persistence."""
    cands: list[dict] = []
    for hidden in (64, 256):
        for frac in (0.1, 0.5, 1.0):
            for init in ("normal", "sobol_iid"):
                name = f"elm_h{hidden}_f{int(frac * 100)}_{init}"
                cands.append({
                    "name": name,
                    "family": "elm",
                    "legacy": name == LEGACY_TUNED["elm"],
                    "params": {
                        "hidden_dim": hidden, "history_fraction": frac,
                        "weight_init": init, "delays": list(FAST_LAGS), "q": 3,
                    },
                    "factory": (lambda h=hidden, f=frac, i=init: HeuristicLagELM(
                        hidden_dim=h, history_fraction=f,
                        delays=FAST_LAGS, weight_init=i)),
                })
    for k in (8, 16, 24, 32):
        name = f"knn_q3_k{k}_recent10"
        cands.append({
            "name": name,
            "family": "knn",
            "legacy": name == LEGACY_TUNED["knn"],
            "params": {
                "q": 3, "neighbors": k, "history_fraction": 0.1,
                "delays": list(DEFAULT_LAGS),
            },
            "factory": (lambda kk=k: HeuristicLagKNN(
                q=3, neighbors=kk, history_fraction=0.1, delays=DEFAULT_LAGS)),
        })
    cands.append({
        "name": "daily", "family": "reference", "legacy": False,
        "params": {"kind": "seasonal-naive lag 24"}, "factory": None,
    })
    cands.append({
        "name": "persistence", "family": "reference", "legacy": False,
        "params": {"kind": "last-value repeat"},
        "factory": lambda: make_forecaster("persistence"),
    })
    assert len(cands) == 18
    return cands


def main() -> int:
    pd_data = get_protocol_data()
    fit_history, eval_series, test = pd_data.rolling_views()

    # ---- pinned split geometry (fail-loud) ----
    assert len(fit_history) == VALIDATION_END == 11425
    assert TRAIN_ROWS == 8545
    train_only = fit_history[:TRAIN_ROWS]
    assert len(train_only) == 8545, "train-only fit slice must be 8,545 rows"
    val_segment = fit_history[TRAIN_ROWS:]
    assert len(val_segment) == 2880

    candidates = build_candidates()
    results: list[dict] = []
    raw: dict[str, dict] = {}  # name -> unrounded val/test metrics + per-origin

    print(f"{'model':<26}{'val MAE':>9}{'val RMSE':>10}{'test MAE':>10}{'test RMSE':>11}")
    for cand in candidates:
        name = cand["name"]

        # --- validation phase: frozen fit on the TRAIN-ONLY slice ---
        if name == "daily":
            (v_mae, v_rmse, v_dis), v_per = evaluate_daily_rolling(
                fit_history, TRAIN_ROWS, val_segment)
        else:
            model = cand["factory"]()
            model.fit(train_only, horizon=HORIZON)
            (v_mae, v_rmse, v_dis), v_per = evaluate_rolling(
                name, model, fit_history, TRAIN_ROWS, val_segment)

        # --- test phase: frozen fit on ALL of train.csv (locked protocol) ---
        if name == "daily":
            (t_mae, t_rmse, t_dis), t_per = evaluate_daily_rolling(
                eval_series, VALIDATION_END, test)
        else:
            model = cand["factory"]()
            model.fit(fit_history, horizon=HORIZON)
            (t_mae, t_rmse, t_dis), t_per = evaluate_rolling(
                name, model, eval_series, VALIDATION_END, test)

        raw[name] = {"val": (v_mae, v_rmse), "test": (t_mae, t_rmse),
                     "val_per": v_per, "test_per": t_per}
        results.append({
            "model": name,
            "family": cand["family"],
            "params": cand["params"],
            "is_legacy_window_tuned": cand["legacy"],
            "selected_on_val": False,
            "protocol": ("val: train-only frozen fit (8,545 rows), 2,161 "
                         "stride-1 validation origins; test: frozen fit on "
                         "full train.csv (11,425 rows), 2,161 stride-1 "
                         "origins"),
            "val_rolling_mae": round(v_mae, 4),
            "val_rolling_rmse": round(v_rmse, 4),
            "val_disjoint_windows": v_dis,
            "test_rolling_mae": round(t_mae, 4),
            "test_rolling_rmse": round(t_rmse, 4),
            "disjoint_windows": t_dis,
            "status": "ok",
        })
        print(f"{v_mae:>9.4f}{v_rmse:>10.4f}{t_mae:>10.4f}{t_rmse:>11.4f}  {name}")

    # ---- selection: lowest val rolling MAE per family (val numbers only) ----
    selection: dict = {
        "criterion": ("lowest val_rolling_mae per family (train-only frozen "
                       "fit, 2,161 stride-1 validation origins); test region "
                       "scored once per candidate, never used for selection"),
    }
    for family in ("elm", "knn"):
        fam = [r for r in results if r["family"] == family]
        selected = min(fam, key=lambda r: raw[r["model"]]["val"][0])
        selected["selected_on_val"] = True
        legacy = next(r for r in fam if r["is_legacy_window_tuned"])
        delta = raw[legacy["model"]]["test"][0] - raw[selected["model"]]["test"][0]
        selection[family] = {
            "val_selected": {
                "model": selected["model"], "params": selected["params"],
                "val_rolling_mae": round(raw[selected["model"]]["val"][0], 4),
                "val_rolling_rmse": round(raw[selected["model"]]["val"][1], 4),
                "test_rolling_mae": round(raw[selected["model"]]["test"][0], 4),
                "test_rolling_rmse": round(raw[selected["model"]]["test"][1], 4),
            },
            "legacy_window_tuned": {
                "model": legacy["model"], "params": legacy["params"],
                "val_rolling_mae": round(raw[legacy["model"]]["val"][0], 4),
                "val_rolling_rmse": round(raw[legacy["model"]]["val"][1], 4),
                "test_rolling_mae": round(raw[legacy["model"]]["test"][0], 4),
                "test_rolling_rmse": round(raw[legacy["model"]]["test"][1], 4),
            },
            "same_config": selected["model"] == legacy["model"],
            "tuning_artifact_test_mae_delta": round(delta, 4),
            "note": ("delta = legacy_test_mae - selected_test_mae; positive "
                     "=> the window-tuned choice cost test-region accuracy"),
        }
    selection["references"] = {
        r["model"]: {
            "val_rolling_mae": r["val_rolling_mae"],
            "test_rolling_mae": r["test_rolling_mae"],
            "test_rolling_rmse": r["test_rolling_rmse"],
        }
        for r in results if r["family"] == "reference"
    }

    # ---- fail-loud anchors (abort before ANY write) ----
    anchor_results: list[dict] = []

    def check(kind: str, name: str, got: tuple[float, float],
              expected: tuple[float, float], tol: float) -> None:
        mae, rmse = got
        exp_mae, exp_rmse = expected
        ok = bool(abs(mae - exp_mae) < tol and abs(rmse - exp_rmse) < tol)
        anchor_results.append({
            "model": name, "phase": kind,
            "t0_mae": round(mae, 4), "t0_rmse": round(rmse, 4),
            "expected": [exp_mae, exp_rmse], "ok": ok,
        })
        print(f"anchor [{kind}] {name}: {mae:.4f}/{rmse:.4f} "
              f"expected {exp_mae}/{exp_rmse} -> {'OK' if ok else 'FAIL'}")

    for name, expected in VAL_ANCHORS.items():
        check("validation_t0", name, tuple(raw[name]["val_per"][0]), expected, 5e-5)
    for name, expected in TEST_ANCHORS.items():
        check("test_t0", name, tuple(raw[name]["test_per"][0]), expected, 5e-5)
    for name, expected in ROLLING_ANCHORS.items():
        check("test_rolling_s01", name, raw[name]["test"], expected, 1e-4)

    failed = [a for a in anchor_results if not a["ok"]]
    if failed:
        print(f"\nANCHOR CHECK FAILED for {len(failed)} row(s) — aborting, "
              f"no results.json written")
        for a in failed:
            print(f"  [{a['phase']}] {a['model']}: got {a['t0_mae']}/"
                  f"{a['t0_rmse']}, expected {a['expected']}")
        return 1

    # ---- selection summary ----
    print("\nSelection (lowest val rolling MAE per family):")
    for family in ("elm", "knn"):
        s = selection[family]
        print(f"  {family}: selected {s['val_selected']['model']} "
              f"(val {s['val_selected']['val_rolling_mae']:.4f}, "
              f"test {s['val_selected']['test_rolling_mae']:.4f}) | "
              f"legacy {s['legacy_window_tuned']['model']} "
              f"(val {s['legacy_window_tuned']['val_rolling_mae']:.4f}, "
              f"test {s['legacy_window_tuned']['test_rolling_mae']:.4f}) | "
              f"delta {s['tuning_artifact_test_mae_delta']:+.4f}")

    out = {
        "slice": "S-02",
        "protocol": {
            "fit_rows": 8545,
            "fit": ("validation phase: frozen fit on train.csv[:8545] "
                    "(train-only slice), fit once per candidate"),
            "val_rows": 2880,
            "val_origins": 2161,
            "stride": 1,
            "horizon": HORIZON,
            "test_fit": ("test phase: frozen fit on all of train.csv "
                         "(11,425 rows) — the locked protocol, fit once"),
            "test_origins": 2161,
            "selection_criterion": selection["criterion"],
            "note": ("per-origin history = all observed rows strictly "
                     "before the scored window"),
        },
        "results": results,
        "selection": selection,
        "anchors_t0": anchor_results,
    }
    (SWEEP_DIR / "results.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nWrote {SWEEP_DIR / 'results.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
