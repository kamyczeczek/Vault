"""S-47 Diverse Mini Suite — fast cross-domain probe.
6 tasks (ETTh1 H96 + 5 synthetic), W=5 origins, refit at every origin.
Compares Pool A (linear+RFF), Pool B (+SWT subband experts), Pool C (+pooled-ELM).
Fit-window policy is a flag: `--window fixed` (default, 2000 trailing points) or
`--window expanding` (all history up to the origin). See S47_DESIGN.md, Q9.
"""
from __future__ import annotations
import json, time, pathlib, sys
import numpy as np
import pywt
from sklearn.linear_model import Ridge

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent.parent  # projects/
sys.path.insert(0, str(HERE.parent))  # research_engine.py (AntiLeakageHarness)
sys.path.insert(0, str(ROOT / "benchmark-core" / "members"))
from anchored_wavelet_elm import AnchoredWaveletELM, _ridge_multioutput
from research_engine import AntiLeakageHarness, LeakageError

ETTH1_CSV = ROOT.parent / "_archive" / "datasets" / "data" / "ETTh1_h1.csv"


def _load_etth1(n=2600):
    """First `n` points of the OT column of the canonical ETTh1 fetch.

    Replaces the lost `data.get_protocol_data().rolling_views()` helper from
    the pre-split tree. Fails loud when the fetch is absent — run
    `python fetch_etth1.py` in `projects/datasets/` (never commit the CSV).
    """
    if not ETTH1_CSV.exists():
        raise FileNotFoundError(
            f"{ETTH1_CSV} missing — run `python fetch_etth1.py` in projects/_archive/datasets/"
        )
    import pandas as pd

    s = pd.to_numeric(pd.read_csv(ETTH1_CSV)["OT"], errors="coerce").dropna().to_numpy(float)
    if s.ndim > 1:
        s = s[:, 0]
    return s[:n]

SEARCH_ALPHA = 3000.0
TRAIN_WINDOW = 2000
N_ORIGINS = 5
N_SELECT_ORIGINS = 3

TASKS = [
    ("etth1_H96", 96, "real"),
    ("seasonal_H48", 48, "synthetic"),
    ("trending_H48", 48, "synthetic"),
    ("spiky_H48", 48, "synthetic"),
    ("ou_H24", 24, "synthetic"),
    ("multiscale_H96", 96, "synthetic"),
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

def get_series(name):
    if name=="etth1_H96":
        return _load_etth1(2600)
    return {"seasonal_H48":gen_seasonal,"trending_H48":gen_trending,"spiky_H48":gen_spiky,"ou_H24":gen_ou,"multiscale_H96":gen_multiscale}[name](2600)

# --- fits (frozen on train[:2000]) ---
def fit_nlinear(train, H, alpha):
    L=96 if H<96 else 96  # fix L=96 for fast suite (avoids 336 swt mismatch for H48)
    # for nlinear we use L=96 uniformly in mini suite for speed/comparability
    n=len(train); ends=np.arange(L, n-H+1)
    SW=np.stack([train[i-L:i] for i in ends]); X=SW-SW[:,-1:]
    Y=np.stack([train[e:e+H]-train[e-1] for e in ends])
    W=_ridge_multioutput(X,Y,alpha)
    return (W,L)

def pred_nlinear(model, hist):
    W,L=model; w=hist[-L:]; a=float(w[-1]); return (w-a)[None,:] @ W + a

def fit_rff(train, H):
    L=96; n=len(train); ends=np.arange(L,n-H+1)
    SW=np.stack([train[i-L:i] for i in ends]); X=SW-SW[:,-1:]
    h=64; rng=np.random.default_rng(0); Wr=rng.standard_normal((L,h))*0.5; b=rng.uniform(0,2*np.pi,h)
    Phi=np.cos(X @ Wr + b)
    Y=np.stack([train[e:e+H]-train[e-1] for e in ends])
    Wout=_ridge_multioutput(Phi,Y,100.0)
    return (Wr,b,Wout,L)

def pred_rff(model, hist):
    Wr,b,Wout,L=model; w=hist[-L:]; a=float(w[-1]); phi=np.cos((w-a)[None,:] @ Wr + b); return (phi @ Wout)[0]+a

def fit_subbands(train, H):
    L=96; n=len(train); ends=np.arange(L,n-H+1)
    Xbands={"cA1":[],"d1":[]}  # J=1 for L=96 (SWT level 1 gives cA,d1 length 96)
    for e in ends:
        w=train[e-L:e]; xa=w-float(w[-1])
        cA,d1=pywt.swt(xa,"db4",level=1)[0]
        Xbands["cA1"].append(cA); Xbands["d1"].append(d1)
    for k in Xbands: Xbands[k]=np.stack(Xbands[k],axis=0)
    Y=np.stack([train[e:e+H]-train[e-1] for e in ends])
    W={k:_ridge_multioutput(Xbands[k],Y,100.0) for k in Xbands}
    return (W,L)

def pred_subband(model, hist, band):
    W,L=model; w=hist[-L:]; a=float(w[-1]); xa=w-a
    cA,d1=pywt.swt(xa,"db4",level=1)[0]
    vec={"cA1":cA,"d1":d1}[band]
    return (vec[None,:] @ W[band])[0]+a

def fit_pooled(train,H):
    m=AnchoredWaveletELM(hidden=96, input_length=96, wavelet="db4", levels=1, seed=42)
    m.fit(train, horizon=H)
    return m

def pred_pooled(model, hist):
    model.history_=hist
    return model.predict()

def rolling_preds(series, H, fit_fn, pred_fn, train_window=TRAIN_WINDOW,
                  n_origins=N_ORIGINS, window="fixed"):
    """Fit once at each origin, then forecast H steps.

    `window="fixed"` fits on the trailing `train_window` points, so every fit
    sees the same sample size and only the target window moves.
    `window="expanding"` fits on `series[:origin]`, so each fit sees more
    history. Both fit strictly before the scored origin: the policy changes
    sample size, never the leakage geometry.
    """
    if window not in ("fixed", "expanding"):
        raise ValueError(f"window must be 'fixed' or 'expanding', got {window!r}")
    series = np.asarray(series, dtype=float)
    origins = [train_window + i * H for i in range(n_origins)]
    if not origins or origins[-1] + H > len(series):
        raise ValueError(
            f"need {train_window + n_origins * H} points for "
            f"train_window={train_window}, H={H}, W={n_origins}; got {len(series)}")

    preds, actuals = [], []
    for origin in origins:
        fit_start = origin - train_window if window == "fixed" else 0
        train = series[fit_start:origin]
        model = fit_fn(train, H)
        history = series[max(0, origin - 96):origin]
        pred = np.asarray(pred_fn(model, history), dtype=float).ravel()
        if pred.size != H:
            raise ValueError(f"origin {origin}: expected {H} predictions, got {pred.size}")
        preds.append(pred)
        actuals.append(series[origin:origin + H])
    return np.stack(preds), np.stack(actuals), origins


def training_scale(series, train_window=TRAIN_WINDOW):
    """Population standard deviation from the initial training window only."""
    train = np.asarray(series, dtype=float)[:train_window]
    if train.size != train_window:
        raise ValueError(f"need {train_window} training points, got {train.size}")
    scale = float(np.std(train, ddof=0))
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError(f"training-window standard deviation must be positive, got {scale}")
    return scale


def pool_blend_scores(P_dict, actual, names, fit_origins, score_origins):
    """Fit horizon-wise Ridge weights on fit_origins; score disjoint origins."""
    fit_origins = list(fit_origins)
    score_origins = list(score_origins)
    if not fit_origins:
        raise ValueError("pool blend needs at least one fit origin")
    overlap = set(fit_origins) & set(score_origins)
    if overlap:
        raise LeakageError(f"pool blend fit/score origins overlap: {sorted(overlap)}")
    if not names or any(name not in P_dict for name in names):
        raise ValueError(f"pool members missing from forecasts: {names}")

    actual = np.asarray(actual, dtype=float)
    predictions = np.stack([np.asarray(P_dict[name], dtype=float)
                            for name in names], axis=2)
    if predictions.shape[:2] != actual.shape:
        raise ValueError("pool forecasts and actuals have different origin/horizon shapes")
    if any(i < 0 or i >= len(actual) for i in fit_origins + score_origins):
        raise IndexError("pool blend origin index is outside the forecast matrix")

    per_origin = {}
    for score_origin in score_origins:
        errors = []
        for horizon in range(actual.shape[1]):
            model = Ridge(alpha=SEARCH_ALPHA, fit_intercept=False)
            model.fit(predictions[fit_origins, horizon, :],
                      actual[fit_origins, horizon])
            pred = float(predictions[score_origin, horizon, :] @ model.coef_)
            errors.append(abs(pred - actual[score_origin, horizon]))
        per_origin[score_origin] = float(np.mean(errors))
    return per_origin


def _average_rank(values, name):
    value = values[name]
    lower = sum(other < value for other in values.values())
    tied = sum(other == value for other in values.values())
    return lower + (tied + 1) / 2


def select_gate_metrics(origin_scores, select_indices_by_task, task_scales):
    """Compute G1-G3 from select-origin scores only, with equal task weight."""
    pools = ("A", "B", "C")
    per_task = {}
    for task, indices in select_indices_by_task.items():
        raw = {pool: float(np.mean([origin_scores[(task, i)][pool]
                                    for i in indices]))
               for pool in pools}
        normalized = {pool: raw[pool] / task_scales[task] for pool in pools}
        ranks = {pool: _average_rank(normalized, pool) for pool in pools}
        per_task[task] = {"raw_mae": raw, "normalized_mae": normalized,
                          "rank": ranks}

    mean_normalized = {
        pool: float(np.mean([per_task[t]["normalized_mae"][pool]
                             for t in per_task]))
        for pool in pools
    }
    mean_rank = {
        pool: float(np.mean([per_task[t]["rank"][pool] for t in per_task]))
        for pool in pools
    }
    wins_b = sum(per_task[t]["normalized_mae"]["B"] <
                 per_task[t]["normalized_mae"]["A"] for t in per_task)
    gates = {
        "G1": mean_normalized["B"] < mean_normalized["A"] - 0.005,
        "G2": mean_rank["B"] < mean_rank["A"],
        "G3": wins_b >= 4,
    }
    return {"per_task": per_task, "mean_normalized_mae": mean_normalized,
            "mean_rank": mean_rank, "winsB": int(wins_b), "gates": gates,
            "select_pass": all(gates.values())}

def _parse_window(argv):
    """`--window fixed|expanding` from argv, default fixed."""
    args = list(sys.argv[1:] if argv is None else argv)
    window = "fixed"
    if "--window" in args:
        index = args.index("--window")
        if index + 1 >= len(args):
            raise SystemExit("--window needs a value: fixed | expanding")
        window = args[index + 1]
    if window not in ("fixed", "expanding"):
        raise SystemExit(f"unknown window policy {window!r}; use fixed | expanding")
    return window


RESULTS_FILE = {"fixed": "results_s47.json",
                "expanding": "results_s47_expanding.json"}
LOG_FILE = {"fixed": "harness.log", "expanding": "harness_expanding.log"}


def main(argv=None):
    window = _parse_window(argv)
    t0 = time.time()
    log = []

    def out(message):
        print(message)
        log.append(message)

    policy = ("fixed 2000-point fit per origin" if window == "fixed"
              else "expanding fit from series start at every origin")
    out(f"S-47: 6 tasks, {policy}, W=5; "
        "first 3 select, last 2 post-lock diagnostic")
    for name, horizon, _ in TASKS:
        out(f" task {name:18s} H={horizon:3d} n=2600")

    fits={
        "nlinear_a1": (lambda tr,H: fit_nlinear(tr,H,1.0), pred_nlinear),
        "nlinear_a10": (lambda tr,H: fit_nlinear(tr,H,10.0), pred_nlinear),
        "rff_h64": (fit_rff, pred_rff),
        "subband_cA1": (fit_subbands, lambda m,h: pred_subband(m,h,"cA1")),
        "subband_d1": (fit_subbands, lambda m,h: pred_subband(m,h,"d1")),
        "wavelet_pooled": (fit_pooled, pred_pooled),
    }

    # Harness checks run before any score is reported. Failure aborts the run.
    harness_checks = {}
    try:
        harness = AntiLeakageHarness(train_window=TRAIN_WINDOW, horizon=96,
                                     embargo=0, step=96)
        probe = get_series("spiky_H48")
        for task_name, horizon, _ in TASKS:
            fold_harness = AntiLeakageHarness(
                train_window=TRAIN_WINDOW, horizon=horizon,
                embargo=0, step=horizon)
            folds = fold_harness.folds(TRAIN_WINDOW + N_ORIGINS * horizon)
            if len(folds) != N_ORIGINS:
                raise LeakageError(
                    f"C1: {task_name} expected {N_ORIGINS} origins, got {len(folds)}")
        harness_checks["C1_geometry"] = "pass"
        for fname, (ff, pf) in fits.items():
            harness.check_window_isolation(
                lambda series, fit_end, H, ff=ff:
                    ff(np.asarray(series)[fit_end - TRAIN_WINDOW:fit_end], H),
                lambda model, history, pf=pf: pf(model, history),
                probe, TRAIN_WINDOW)
            harness_checks[f"C1_{fname}"] = "pass"
        lag_names = [f"lag_{i}" for i in range(1, 97)]
        harness.check_features(lag_names)
        harness_checks["C2"] = "pass"
        out("Harness C1+C2 pass (per-origin fit isolation, lag-only features).")
    except LeakageError as exc:
        out(f"HARNESS ABORT: {exc}")
        raise SystemExit(f"harness failed: {exc}")

    pools = {
        "A": ["nlinear_a1", "nlinear_a10", "rff_h64"],
        "B": ["nlinear_a1", "nlinear_a10", "rff_h64",
              "subband_cA1", "subband_d1"],
        "C": ["nlinear_a1", "nlinear_a10", "rff_h64", "wavelet_pooled"],
    }
    task_data = {}
    for task_name,H,_ in TASKS:
        series = get_series(task_name)
        fold_harness = AntiLeakageHarness(train_window=TRAIN_WINDOW, horizon=H,
                                           embargo=0, step=H)
        folds = fold_harness.folds(TRAIN_WINDOW + N_ORIGINS * H)
        expected_origins = [fold[1] for fold in folds]
        P_dict, A_ref = {}, None
        for name, (fit_fn, pred_fn) in fits.items():
            P, actual, origins = rolling_preds(series, H, fit_fn, pred_fn,
                                               window=window)
            if origins != expected_origins:
                raise LeakageError(f"C1: {task_name} fit and score origins differ")
            if A_ref is not None and not np.array_equal(actual, A_ref):
                raise LeakageError(f"C1: {task_name} members received different targets")
            P_dict[name] = P
            A_ref = actual if A_ref is None else A_ref
        task_data[task_name] = {
            "H": H, "origins": origins, "actual": A_ref, "predictions": P_dict,
            "scale": training_scale(series), "pool_names": pools,
        }
        out(f"\n-- {task_name} H={H}: fit {len(fits)} members at "
            f"{len(origins)} origins; train std={task_data[task_name]['scale']:.6g}")

    select_indices = list(range(N_SELECT_ORIGINS))
    confirmation_indices = list(range(N_SELECT_ORIGINS, N_ORIGINS))
    select_indices_by_task = {name: select_indices for name, _, _ in TASKS}
    task_scales = {name: task_data[name]["scale"] for name, _, _ in TASKS}
    select_scores = {}
    for task_name, _, _ in TASKS:
        state = task_data[task_name]
        for score_index in select_indices:
            fit_indices = [i for i in select_indices if i != score_index]
            select_scores[(task_name, score_index)] = {
                pool: pool_blend_scores(state["predictions"], state["actual"], names,
                                        fit_indices, [score_index])[score_index]
                for pool, names in pools.items()
            }

    select_origin_ids = [(name, i) for name, _, _ in TASKS for i in select_indices]
    confirmation_origin_ids = [(name, i) for name, _, _ in TASKS
                               for i in confirmation_indices]

    def score_origin(origin_id):
        task_name, score_index = origin_id
        if origin_id in select_scores:
            return dict(select_scores[origin_id])
        state = task_data[task_name]
        return {
            pool: pool_blend_scores(state["predictions"], state["actual"], names,
                                    select_indices, [score_index])[score_index]
            for pool, names in pools.items()
        }

    def choose_from_select(scores):
        summary = select_gate_metrics(scores, select_indices_by_task, task_scales)
        return "B" if summary["select_pass"] else "A"

    # The harness locks the aggregate A/B decision before score_origin is
    # allowed to calculate any confirmation-origin blend score.
    lock = harness.screened_decision(score_origin, choose_from_select,
                                     select_origin_ids, confirmation_origin_ids)
    select_summary = select_gate_metrics(lock["select_scores"],
                                         select_indices_by_task, task_scales)
    harness_checks["C3"] = "pass"
    choice = lock["choice"]

    per_task = {}
    for task_name, _, _ in TASKS:
        state = task_data[task_name]
        select_raw = {
            pool: float(np.mean([lock["select_scores"][(task_name, i)][pool]
                                 for i in select_indices]))
            for pool in pools
        }
        confirmation_raw = {
            pool: float(np.mean([lock["test_scores"][(task_name, i)][pool]
                                 for i in confirmation_indices]))
            for pool in pools
        }
        select_normalized = {pool: value / state["scale"]
                             for pool, value in select_raw.items()}
        confirmation_normalized = {pool: value / state["scale"]
                                   for pool, value in confirmation_raw.items()}
        P_dict, actual = state["predictions"], state["actual"]
        singleton_select = {
            name: float(np.mean(np.abs(P_dict[name][select_indices] -
                                       actual[select_indices])))
            for name in fits
        }
        singleton_confirmation = {
            name: float(np.mean(np.abs(P_dict[name][confirmation_indices] -
                                       actual[confirmation_indices])))
            for name in fits
        }
        test_gap = confirmation_normalized["B"] - confirmation_normalized["A"]
        per_origin = {
            pool: [lock["select_scores"][(task_name, i)][pool]
                   for i in select_indices]
                  + [lock["test_scores"][(task_name, i)][pool]
                     for i in confirmation_indices]
            for pool in pools
        }
        per_task[task_name] = {
            "H": state["H"], "origins": state["origins"],
            "train_scale": state["scale"],
            "singleton": singleton_select,
            "singleton_confirmation": singleton_confirmation,
            # Compatibility key for the corpus sync: this is select-only MAE.
            "pool_blend": select_raw,
            "pool_blend_normalized": select_normalized,
            "pool_names": state["pool_names"],
            "confirmation": {
                "pool_blend": confirmation_raw,
                "pool_blend_normalized": confirmation_normalized,
                "test_gap_normalized": test_gap,
            },
            "screened": {
                "select_origins": [state["origins"][i] for i in select_indices],
                "confirmation_origins": [state["origins"][i]
                                          for i in confirmation_indices],
                "choice": choice,
                "test_gap_normalized": test_gap,
                "confirmation_claim": "diagnostic_only_prior_exposure",
                "per_origin_raw_mae": per_origin,
            },
        }

    mean_select_raw = {
        pool: float(np.mean([per_task[name]["pool_blend"][pool]
                             for name, _, _ in TASKS]))
        for pool in pools
    }
    mean_select_normalized = select_summary["mean_normalized_mae"]
    mean_rank = select_summary["mean_rank"]
    test_gaps = [per_task[name]["confirmation"]["test_gap_normalized"]
                 for name, _, _ in TASKS]
    test_wins = sum(gap < 0 for gap in test_gaps)
    G1, G2, G3 = (select_summary["gates"][name] for name in ("G1", "G2", "G3"))
    G4 = float(np.mean(test_gaps)) < 0 and test_wins >= 4
    # All five origins were exposed in the pre-correction report. This G4 is
    # therefore diagnostic and cannot count as untouched confirmation.
    confirmation_valid = False
    all_binding = bool(G1 and G2 and G3 and G4 and confirmation_valid)

    out("\n=== Select-only gates (task-normalized MAE) ===")
    out("mean " + " ".join(f"{pool}={mean_select_normalized[pool]:.6f}"
                            for pool in pools))
    out(f"mean rank A={mean_rank['A']:.3f} B={mean_rank['B']:.3f} "
        f"C={mean_rank['C']:.3f}; B wins {select_summary['winsB']}/6")
    out(f"G1 {G1} G2 {G2} G3 {G3}; locked choice={choice}")
    out(f"Post-lock G4 diagnostic: mean gap={float(np.mean(test_gaps)):+.6f}; "
        f"B wins {test_wins}/6; confirmation_valid={confirmation_valid}")
    out("Verdict: DIAGNOSTIC ONLY — these confirmation origins appeared in the "
        "pre-correction report.")

    res = {
        "slice": "S-47-diverse-mini",
        "suite": f"6-task synthetic+ETTh1; {window} fit per origin; W=5",
        "harness_command": f"python s47_ref/rolling_arm.py --window {window}",
        "protocol": {
            "train_window": TRAIN_WINDOW,
            "fit_window": window,
            "n_origins": N_ORIGINS,
            "select_origins": N_SELECT_ORIGINS,
            "confirmation_origins": N_ORIGINS - N_SELECT_ORIGINS,
            "fit_policy": "refit on trailing train_window at every origin; one fit per forecast horizon",
            "stack_policy": "select scores use leave-one-select-origin-out weights; confirmation weights fit on all select origins",
            "task_scale": "population std of the initial training window",
            "confirmation_status": "exposed_in_pre_correction_report; diagnostic_only",
        },
        "per_task": per_task,
        "aggregate": {
            "meanA": mean_select_raw["A"], "meanB": mean_select_raw["B"],
            "meanC": mean_select_raw["C"],
            "meanA_normalized": mean_select_normalized["A"],
            "meanB_normalized": mean_select_normalized["B"],
            "meanC_normalized": mean_select_normalized["C"],
            "winsB": select_summary["winsB"],
            "mean_rankA": mean_rank["A"], "mean_rankB": mean_rank["B"],
            "mean_rankC": mean_rank["C"],
            "confirmation_gap_mean_normalized": float(np.mean(test_gaps)),
            "confirmation_winsB": int(test_wins),
        },
        "gates": {
            "G1": bool(G1), "G2": bool(G2), "G3": bool(G3),
            "G4_diagnostic": bool(G4), "G4_confirmatory_valid": confirmation_valid,
            "select_pass": bool(select_summary["select_pass"]),
            "all_binding": all_binding,
        },
        "harness": dict(harness_checks,
                        screened_decision="aggregate choice locked on select origins before confirmation scoring"),
        "verdict": "DIAGNOSTIC ONLY — historical exposure prevents confirmatory decision",
        "elapsed_s": time.time() - t0,
    }
    with open(HERE / RESULTS_FILE[window], "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    with open(HERE / LOG_FILE[window], "w", encoding="utf-8") as f:
        f.write("\n".join(log) + "\n")
    out(f"wrote {RESULTS_FILE[window]} elapsed {time.time()-t0:.1f}s")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
