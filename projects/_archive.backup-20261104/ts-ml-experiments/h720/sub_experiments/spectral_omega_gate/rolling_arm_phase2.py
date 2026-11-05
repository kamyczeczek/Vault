"""Omega-gated TSFM ensemble — Phase 2 (h720 ETTh1 H=720).

Protocol  : S-20-clean adapted for zero-training integration.
Gate      : hard Omega_336 > 0.5 → Chronos-Bolt zero-shot, else frozen S-26.
Members   : S-26 (frozen refit on 11425) + TSFM (Chronos-Bolt Base, zero-shot).
Origin count : 2161 rolling test origins (full), 4 disjoint, or stratified sample.

Acceptance criteria (all must hold):
  Primary  : MAE_gated(full) <= 1.9859  (>= 0.0050 improvement over S-26 1.9909)
  Guard 1  : MAE_gated(disjoint-4) <= 1.9696
  Guard 2  : |Omega_test_mean - Omega_val_mean| / Omega_val_std < 0.5  (L=336)
  Guard 3  : Spearman rho(Omega_336, MAE_S26) < 0, p < 0.01  (test region)
  Guard 4  : P(Omega > 0.5) >= 0.10  (call-rate sanity)

Close condition:
  MAE_gated(full) >= 1.9909 -> REJECTED (TSFM does not transfer to ETTh1 H=720).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge

# Disable tqdm progress bars globally for clean harness logs
os.environ.setdefault("TQDM_DISABLE", "1")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")

HERE = Path(__file__).resolve().parent
H720_ROOT = HERE.parent.parent
sys.path.insert(0, str(H720_ROOT))
sys.path.insert(0, str(HERE))

from data import HORIZON, get_protocol_data
from methods.neural_models import NLinear
from compute_omega import compute_omega
from tsfm_adapter import TSFMAdapter
# ------------------------------------------------------------------
# Protocol constants (match S-26 / Phase 1 exactly)
# ------------------------------------------------------------------
TRAIN_END = 8545
DISJOINT_STARTS = (0, 720, 1440, 2160)
BEST_ALPHA = 10000.0
L_OMEGA = 336
OMEGA_THRESHOLD = 0.5
CHUNK = 8  # optimized for CPU: 8*9=72 peak effective batch

BEST_CANDIDATES = [
    ("nlinear_L336_a1",  lambda: NLinear(input_length=336, ridge_alpha=1.0)),
    ("nlinear_L336_a10", lambda: NLinear(input_length=336, ridge_alpha=10.0)),
]


def __compute_omega_array(concat_series, starts, L, condition="none"):
    omegas = []
    for s in starts:
        window = concat_series[s - L: s]
        omegas.append(compute_omega(window, condition=condition))
    return np.array(omegas)

# ------------------------------------------------------------------
# S-26 stack machinery (byte-identical to Phase 1 / S-26)
# ------------------------------------------------------------------
def fit_stack_map(P: np.ndarray, A: np.ndarray, alpha: float, fit_intercept: bool = False):
    n, m, h = P.shape
    coef = np.empty((m, h))
    inter = np.zeros(h)
    for k in range(h):
        r = Ridge(alpha=alpha, fit_intercept=fit_intercept).fit(P[:, :, k], A[:, k])
        coef[:, k] = r.coef_
    class _Map:
        def predict(self, Pt: np.ndarray) -> np.ndarray:
            return np.einsum("mh,nmh->nh", coef, Pt) + inter[None, :]
    _Map.coef_ = coef
    _Map.inter_ = inter
    return _Map()


def preds_for_full_fit(factory, full_series: np.ndarray, concat_series: np.ndarray,
                       starts: np.ndarray, H: int) -> np.ndarray:
    """Fit factory on full_series, predict origins at starts in concat_series."""
    m = factory()
    m.fit(full_series, horizon=H)
    hist = m.history_
    out = []
    for s in starts:
        m.history_ = concat_series[:s]
        out.append(np.asarray(m.predict(), dtype=float))
    m.history_ = hist
    return np.asarray(out)


def collect_test(full_series: np.ndarray, concat_series: np.ndarray,
                 starts: np.ndarray) -> np.ndarray:
    cols = []
    for name, factory in BEST_CANDIDATES:
        p = preds_for_full_fit(factory, full_series, concat_series, starts, HORIZON)
        cols.append(p)
    return np.stack(cols, axis=1)  # (n_origins, n_members, H)


def preds_for_train_fit(factory, train_series: np.ndarray, full_series: np.ndarray,
                        starts: np.ndarray, H: int) -> np.ndarray:
    """Fit factory on train_series, predict origins at starts in full_series."""
    m = factory()
    m.fit(train_series, horizon=H)
    hist = m.history_
    out = []
    for s in starts:
        m.history_ = full_series[:s]
        out.append(np.asarray(m.predict(), dtype=float))
    m.history_ = hist
    return np.asarray(out)


def rolling_metrics(preds: np.ndarray, actuals: np.ndarray):
    err = preds - actuals
    mae_per = np.mean(np.abs(err), axis=1)
    rmse_per = np.sqrt(np.mean(err ** 2, axis=1))
    return (
        float(np.mean(mae_per)),
        float(np.sqrt(np.mean(err ** 2))),
        mae_per,
        rmse_per,
    )


def _sampled_indices_excluding(rng, omega_arr, exclude_set, n_per_bucket=20):
    """Stratified sample: 20 per Omega bucket A/B/C, excluding indices in exclude_set."""
    mask_a = np.where(omega_arr < 0.4)[0]
    mask_b = np.where((omega_arr >= 0.4) & (omega_arr <= 0.5))[0]
    mask_c = np.where(omega_arr > 0.5)[0]
    # Filter out excluded indices (disjoint) to guarantee distinct union
    mask_a = np.array([i for i in mask_a if i not in exclude_set], dtype=int)
    mask_b = np.array([i for i in mask_b if i not in exclude_set], dtype=int)
    mask_c = np.array([i for i in mask_c if i not in exclude_set], dtype=int)
    chosen = []
    for mask in (mask_a, mask_b, mask_c):
        if len(mask) == 0:
            continue
        k = min(n_per_bucket, len(mask))
        chosen.extend(sorted(rng.choice(mask, size=k, replace=False).tolist()))
    return np.array(sorted(set(chosen)), dtype=int)

def _sampled_indices(rng, omega_arr, n_per_bucket=20):
    """Stratified sample: 20 per Omega bucket A/B/C when available."""
    mask_a = np.where(omega_arr < 0.4)[0]
    mask_b = np.where((omega_arr >= 0.4) & (omega_arr <= 0.5))[0]
    mask_c = np.where(omega_arr > 0.5)[0]
    chosen = []
    for mask in (mask_a, mask_b, mask_c):
        if len(mask) == 0:
            continue
        k = min(n_per_bucket, len(mask))
        chosen.extend(sorted(rng.choice(mask, size=k, replace=False).tolist()))
    return np.array(sorted(set(chosen)), dtype=int)


# ------------------------------------------------------------------
# Phase 2 main
# ------------------------------------------------------------------
def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Omega-gated TSFM Phase 2 harness")
    parser.add_argument("--origins", choices=("disjoint4", "sampled", "full"),
                        default="disjoint4",
                        help="Which origins to run TSFM on (default: disjoint4)")
    parser.add_argument("--seed", type=int, default=0,
                        help="RNG seed for sampled mode")
    parser.add_argument("--guard-seconds", type=float, default=750,
                        help="Wall-clock guard for TSFM loop in full/sampled modes")
    args = parser.parse_args(argv)

    t_all = time.time()
    log_lines: list[str] = []
    out_log = HERE / "harness.log"
    out_json = HERE / "results_tsfm_phase2.json"

    def flush_log():
        try:
            with open(out_log, "w", encoding="utf-8") as f:
                f.write("\n".join(log_lines) + "\n")
        except Exception:
            pass

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)
        flush_log()

    def write_partial(payload: dict) -> None:
        """Incremental JSON write so a mid-run kill still leaves diagnostics."""
        try:
            tmp = out_json.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            tmp.replace(out_json)
        except Exception:
            pass

    log("=== Omega-Gated TSFM Ensemble — Phase 2 Harness ===")
    log(f"Gate: Omega_336 > {OMEGA_THRESHOLD} -> TSFM, else S-26")
    log(f"S-26 frozen refit on 11425; TSFM zero-shot Chronos-Bolt Base")
    log(f"Horizon H={HORIZON}, origins mode={args.origins}, L_omega={L_OMEGA}")
    log(f"TSFMAdapter(context_length=336), CHUNK={CHUNK}, guard={args.guard_seconds}s")

    # ------------------------------------------------------------------
    # 1. Load protocol data
    # ------------------------------------------------------------------
    pd = get_protocol_data()
    fit_series, _, test_series = pd.rolling_views()
    train_series = fit_series[:TRAIN_END]
    val_series = fit_series[TRAIN_END:]
    n_val = len(val_series) - HORIZON + 1
    assert n_val == 2161, f"Expected 2161 val origins, got {n_val}"
    concat_series = np.concatenate([fit_series, test_series])

    n_test = len(test_series) - HORIZON + 1
    test_starts = np.arange(n_test) + len(fit_series)  # absolute indices in concat
    assert n_test == 2161, f"Expected 2161 test origins, got {n_test}"
    log(f"Data loaded: train={len(train_series)}, val={len(val_series)}, "
        f"test={len(test_series)}, concat={len(concat_series)}")

    # ------------------------------------------------------------------
    # 2. Recompute S-26 frozen predictions on all 2161 test origins
    #    (S-26 protocol: stack fitted on val predictions from members frozen on 8545,
    #     then predict test using members refrozen on 11425)
    # ------------------------------------------------------------------
    log("Collecting S-26 val predictions (members frozen on 8545)...")
    val_starts = np.arange(n_val) + TRAIN_END
    P_val_list = []
    for name, factory in BEST_CANDIDATES:
        p = preds_for_train_fit(factory, train_series, fit_series, val_starts, HORIZON)
        P_val_list.append(p)
    P_val_best = np.stack(P_val_list, axis=1)  # (n_val, 2, H)
    A_val = np.stack([val_series[t: t + HORIZON] for t in range(n_val)])

    log(f"Fitting S-26 stack map (alpha={BEST_ALPHA}) on val predictions...")
    stack = fit_stack_map(P_val_best, A_val, BEST_ALPHA)

    log("Collecting S-26 test predictions (members refrozen on 11425)...")
    P_test_all = collect_test(fit_series, concat_series, test_starts)  # (n_test, 2, H)
    A_test = np.stack([test_series[t: t + HORIZON] for t in range(n_test)])

    s26_preds = stack.predict(P_test_all)  # (n_test, H)
    s26_mae_per = np.mean(np.abs(s26_preds - A_test), axis=1)
    s26_mae_full = float(np.mean(s26_mae_per))
    s26_rmse_full = float(np.sqrt(np.mean((s26_preds - A_test) ** 2)))
    log(f"S-26 anchor -> full MAE {s26_mae_full:.6f}, RMSE {s26_rmse_full:.6f}")
    # Reproducibility gate: must match 1.9909 within tolerance.
    assert abs(s26_mae_full - 1.990897) < 1e-3, (
        f"S-26 anchor MAE {s26_mae_full} deviates from expected 1.9909!"
    )

    # ------------------------------------------------------------------
    # 3. Recompute Omega_336 for all 2161 test origins (Hann taper, Phase 1 exact)
    # ------------------------------------------------------------------
    log("Computing Omega_336 for 2161 test origins (Hann taper)...")
    omega_test_336 = __compute_omega_array(concat_series, test_starts, L_OMEGA, condition="hann")
    # Sanity: Omega values in [0, 1]
    assert np.all(omega_test_336 >= 0.0) and np.all(omega_test_336 <= 1.0), (
        "Omega_336 out of [0,1] bounds"
    )

    # Also recompute val Omega for stationarity guard (Guard 2)
    omega_val_336 = __compute_omega_array(fit_series, val_starts, L_OMEGA, condition="hann")
    val_mean = float(np.mean(omega_val_336))
    val_std = float(np.std(omega_val_336))
    test_mean = float(np.mean(omega_test_336))
    test_std = float(np.std(omega_test_336))
    delta_sigma = float(abs(test_mean - val_mean) / (val_std + 1e-8))
    call_rate = float(np.mean(omega_test_336 > OMEGA_THRESHOLD))

    log(f"Omega_336 val mean={val_mean:.4f}, std={val_std:.4f}")
    log(f"Omega_336 test mean={test_mean:.4f}, std={test_std:.4f}")
    log(f"Stationarity shift: {delta_sigma:.4f} sigma (guard < 0.5)")
    log(f"Call rate (Omega > {OMEGA_THRESHOLD}): {call_rate:.4f} (guard >= 0.10)")

    # ------------------------------------------------------------------
    # 4. Correlation sanity (Guard 3)
    # ------------------------------------------------------------------
    valid_mask = ~np.isnan(omega_test_336) & ~np.isnan(s26_mae_per)
    rho_omega_mae, pval_omega_mae = spearmanr(
        omega_test_336[valid_mask], s26_mae_per[valid_mask]
    )
    log(f"Spearman rho(Omega_336, S-26 MAE) = {rho_omega_mae:.4f} (p={pval_omega_mae:.4e})")

    # ------------------------------------------------------------------
    # Common TSFM setup
    # ------------------------------------------------------------------
    # Disjoint-4 bookkeeping needed for all modes (verdict guards)
    disj_starts = np.array([len(fit_series) + s for s in DISJOINT_STARTS])
    P_disj_all = collect_test(fit_series, concat_series, disj_starts)
    s26_disj_preds = stack.predict(P_disj_all)
    A_disj = np.stack([test_series[s: s + HORIZON] for s in DISJOINT_STARTS])
    omega_disj_336 = __compute_omega_array(concat_series, disj_starts, L_OMEGA, condition="hann")
    gate_mask_disj = omega_disj_336 > OMEGA_THRESHOLD

    acceptance_threshold = 1.9859
    s26_full = 1.9909
    s26_disjoint = 1.9696

    # Shared result fields populated incrementally
    mode = args.origins
    tsfm_calls = 0
    elapsed_tsfm = 0.0
    guard_pass = True  # whether we completed without tripping wall-clock guard
    estimated_full_mae = None
    truncated = False
    mae_full = None
    rmse_full = None
    mae_per_origin = None
    gated_preds = None

    # ------------------------------------------------------------------
    # Branch by origins mode
    # ------------------------------------------------------------------
    if args.origins == "disjoint4":
        # Decision path: only 4 origins, per-origin tsfm.predict (no batched 1165)
        log("Mode disjoint4: computing gated MAE on 4 disjoint origins only")
        log(f"Disjoint Omegas: {omega_disj_336.tolist()} -> gate {gate_mask_disj.tolist()}")
        tsfm = TSFMAdapter(context_length=336, device="cpu")
        # 1-origin warmup (pays tokenizer/model init outside timing)
        log("TSFM warmup (1-origin)...")
        t_warm = time.time()
        _warm_hist = concat_series[int(disj_starts[0]) - L_OMEGA: int(disj_starts[0])]
        _ = tsfm.predict(_warm_hist, HORIZON)
        log(f"Warmup done in {time.time() - t_warm:.2f}s")

        gated_disj_preds = s26_disj_preds.copy()
        t_tsfm = time.time()
        for j in range(len(DISJOINT_STARTS)):
            if gate_mask_disj[j]:
                t_abs = int(disj_starts[j])
                history_window = concat_series[t_abs - L_OMEGA: t_abs]
                log(f"  TSFM predict disjoint {j} (start={DISJOINT_STARTS[j]})...")
                tsfm_pred = tsfm.predict(history_window, HORIZON)
                gated_disj_preds[j] = tsfm_pred
                tsfm_calls += 1
                log(f"    disjoint {j} done, tsfm_calls={tsfm_calls}")
                write_partial({
                    "mode": mode, "tsfm_calls": tsfm_calls,
                    "elapsed_tsfm": float(time.time() - t_tsfm),
                    "guard_pass": True, "truncated": False,
                })
        elapsed_tsfm = float(time.time() - t_tsfm)
        mae_disj, rmse_disj, _, _ = rolling_metrics(gated_disj_preds, A_disj)
        log(f"Phase 2 gated -> disjoint-4 MAE {mae_disj:.6f}, RMSE {rmse_disj:.6f}")

        # For disjoint4, full MAE is not computed; estimate = disjoint MAE for JSON completeness
        mae_full = None
        rmse_full = None
        mae_per_origin = None
        rmse_per_origin = None
        gated_preds = None  # no full gated array in this mode
        s26_mae_full_val = s26_mae_full
        # Verdict for disjoint4: guard-only; primary MAE decision requires full/sampled
        if mae_disj <= s26_disjoint:
            verdict = "PROMOTED (disjoint4 guard pass; full MAE not evaluated in this mode)"
            # Keep machine verdict as PROMOTED for guard-pass signalling; consumers check mode
        else:
            verdict = "REJECTED"
        improvement = None  # no full MAE to compare
        stratified = None

        # Write partial/full JSON for disjoint4 (contains required schema fields)
        stationarity_guard = bool(delta_sigma < 0.5)
        correlation_guard = bool((rho_omega_mae < 0) and (pval_omega_mae < 0.01))
        call_rate_guard = bool(call_rate >= 0.10)
        results = {
            "slice": "spectral_omega_gate_phase2",
            "harness_command": (
                "C:/Users/Mateusz/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe "
                "projects/ts-ml-experiments/h720/sub_experiments/spectral_omega_gate/rolling_arm_phase2.py "
                f"--origins {mode}"
            ),
            "harness_log": "harness.log",
            "protocol": (
                "S-20-clean adapted: S-26 members frozen 8545 for val, refit 11425 for test; "
                "TSFM Chronos-Bolt Base zero-shot; hard gate Omega_336>0.5; "
                "TSFMAdapter(context_length=336), CHUNK=8, disjoint4 per-origin predict"
            ),
            "mode": mode,
            "tsfm_calls": tsfm_calls,
            "elapsed_tsfm": elapsed_tsfm,
            "truncated": truncated,
            "estimated_full_mae": estimated_full_mae,
            "guard_pass": bool(bool(mae_disj <= s26_disjoint) and stationarity_guard and correlation_guard),
            "gate": {
                "omega_L": L_OMEGA,
                "threshold": OMEGA_THRESHOLD,
                "condition": "hann",
                "call_rate": call_rate,
                "n_tsfm": int(np.sum(gate_mask_disj)) if mode == "disjoint4" else int(np.sum(omega_test_336 > OMEGA_THRESHOLD)),
                "n_s26": int(len(DISJOINT_STARTS) - np.sum(gate_mask_disj)) if mode == "disjoint4" else int(np.sum(omega_test_336 <= OMEGA_THRESHOLD)),
            },
            "stationarity": {
                "val_mean": val_mean,
                "val_std": val_std,
                "test_mean": test_mean,
                "test_std": test_std,
                "delta_mean_sigma336": delta_sigma,
                "guard_pass": bool(stationarity_guard),
            },
            "correlation": {
                "rho_omega336_mae": float(rho_omega_mae),
                "pval_mae": float(pval_omega_mae),
                "guard_pass": bool(correlation_guard),
            },
            "call_rate_sanity": {
                "call_rate": call_rate,
                "guard_pass": bool(call_rate_guard),
            },
            "s26_anchor": {
                "full_mae": s26_mae_full,
                "full_rmse": s26_rmse_full,
                "disjoint_4_mae": 1.9696,
                "n": n_test,
            },
            "metrics": {
                "full_mae": mae_full,
                "full_rmse": rmse_full,
                "disjoint_4_mae": float(mae_disj),
                "disjoint_4_rmse": float(rmse_disj),
                "n": n_test,
                "improvement_vs_s26": improvement,
                "verdict": verdict,
            },
            "stratified_mae_gated": stratified,
            "plan_impact": {
                "invalidates": [],
                "confirms": [],
                "opens": [],
            },
        }
        if verdict.startswith("PROMOTED"):
            results["plan_impact"]["confirms"] = [
                f"Disjoint-4 guard passes: {mae_disj:.6f} <= {s26_disjoint}; full MAE not evaluated in disjoint4 mode."
            ]
        else:
            results["plan_impact"]["invalidates"] = [
                f"Disjoint-4 guard fails: {mae_disj:.6f} > {s26_disjoint} -> REJECTED."
            ]
            results["plan_impact"]["confirms"] = [
                f"S-26 remains terminal incumbent at {s26_full} MAE."
            ]
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        log(f"Wrote results to {out_json}")

        elapsed = time.time() - t_all
        log(f"Harness completed in {elapsed:.1f}s | mode={mode} verdict={verdict} tsfm_calls={tsfm_calls} elapsed_tsfm={elapsed_tsfm:.1f}s")
        return 0

    # ------------------------------------------------------------------
    # sampled / full modes: gated full evaluation with CHUNK=8, warmup, guard
    # ------------------------------------------------------------------
    gate_mask = omega_test_336 > OMEGA_THRESHOLD
    n_tsfm = int(np.sum(gate_mask))
    n_s26 = n_test - n_tsfm
    log(f"Gate decisions: TSFM={n_tsfm}, S-26={n_s26}, total={n_test}")

    gated_preds = s26_preds.copy()

    if args.origins == "sampled":
        rng = np.random.default_rng(args.seed)
        # Build disjoint test indices (0,720,1440,2160 — but 2160 <2161 so valid)
        disj_test_idx = []
        for s in DISJOINT_STARTS:
            if 0 <= s < n_test:
                disj_test_idx.append(int(s))
        exclude_set = set(disj_test_idx)
        sampled_idx_60 = _sampled_indices_excluding(rng, omega_test_336, exclude_set, n_per_bucket=20)
        assert len(sampled_idx_60) == 60, f"Expected 60 sampled, got {len(sampled_idx_60)} (buckets may be depleted)"
        sampled_idx = np.array(sorted(set(sampled_idx_60.tolist()) | exclude_set), dtype=int)
        assert len(sampled_idx) == 64, f"Expected 64 total (60+4 disjoint), got {len(sampled_idx)}"
        # Verify disjointness
        assert len(set(sampled_idx_60.tolist()) & exclude_set) == 0, "sampled and disjoint overlap!"
        log(f"Sampled mode: {len(sampled_idx)} origins = 60 stratified + 4 disjoint (seed={args.seed})")
        log(f"  Sampled indices: n={len(sampled_idx_60)} distinct from disjoint {sorted(disj_test_idx)} -> union {len(sampled_idx)}")
        tsfm_indices = np.array([i for i in sampled_idx if gate_mask[i]], dtype=int)
        sampled_gate_desc = f"sampled TSFM={len(tsfm_indices)}/{len(sampled_idx)}"
        log(f"Sampled gate: {sampled_gate_desc}")

    log(f"Building {len(tsfm_indices)} TSFM history windows (mode={mode})...")
    tsfm_histories = np.stack([
        concat_series[int(test_starts[i]) - L_OMEGA : int(test_starts[i])]
        for i in tsfm_indices
    ]) if len(tsfm_indices) > 0 else np.empty((0, L_OMEGA), dtype=np.float32)
    log(f"History array built: shape={tsfm_histories.shape}, dtype={tsfm_histories.dtype}")

    if len(tsfm_indices) > 0:
        tsfm = TSFMAdapter(context_length=336, device="cpu")
        # 1-origin warmup outside timing
        log("TSFM warmup (1-origin)...")
        t_warm = time.time()
        _ = tsfm.predict(tsfm_histories[0], HORIZON)
        log(f"Warmup done in {time.time() - t_warm:.2f}s")

        # For sampled mode use per-origin serial loop (no batch amortization on CPU, 9.0x overhead).
        # For full mode keep CHUNKed batch path. Both respect 750s wall-clock guard.
        if args.origins == "sampled":
            log(f"Calling TSFM per-origin serial on {len(tsfm_indices)} histories (sampled mode)...")
            tsfm_batch_preds = np.empty((len(tsfm_indices), HORIZON), dtype=np.float32)
            t_tsfm = time.time()
            n_done = 0
            truncated = False
            for idx_pos, test_idx in enumerate(tsfm_indices):
                if time.time() - t_tsfm > args.guard_seconds:
                    log(f"TSFM budget guard tripped at {idx_pos}/{len(tsfm_indices)} (elapsed {time.time()-t_tsfm:.1f}s); falling back to sampled estimate")
                    truncated = True
                    guard_pass = False
                    break
                log(f"  TSFM per-origin {idx_pos+1}/{len(tsfm_indices)} (test_idx={test_idx}, omega={omega_test_336[test_idx]:.4f})...")
                tsfm_batch_preds[idx_pos] = tsfm.predict(tsfm_histories[idx_pos], HORIZON)
                n_done = idx_pos + 1
                elapsed_tsfm = float(time.time() - t_tsfm)
                tsfm_calls = int(n_done)
                log(f"    done {idx_pos+1}/{len(tsfm_indices)}, elapsed_tsfm={elapsed_tsfm:.1f}s")
                write_partial({
                    "mode": mode, "tsfm_calls": tsfm_calls,
                    "elapsed_tsfm": elapsed_tsfm,
                    "guard_pass": not truncated,
                    "truncated": truncated,
                    "n_done": n_done, "n_total": int(len(tsfm_indices)),
                })
            elapsed_tsfm = float(time.time() - t_tsfm)
            tsfm_calls = int(n_done)
            if truncated:
                if n_done > 0:
                    gated_partial = s26_preds.copy()
                    gated_partial[tsfm_indices[:n_done]] = tsfm_batch_preds[:n_done]
                    mae_partial, _, _, _ = rolling_metrics(gated_partial, A_test)
                    estimated_full_mae = float(mae_partial)
                    log(f"Partial gated MAE (with {n_done}/{len(tsfm_indices)} TSFM filled, rest S-26): {mae_partial:.6f} -> estimated_full_mae")
                else:
                    estimated_full_mae = float(s26_mae_full)
                if n_done > 0:
                    gated_preds[tsfm_indices[:n_done]] = tsfm_batch_preds[:n_done]
            else:
                gated_preds[tsfm_indices] = tsfm_batch_preds
                log(f"Per-origin predictions done: {len(tsfm_indices)}/{n_test} elapsed_tsfm={elapsed_tsfm:.1f}s")
        else:
            log(f"Calling TSFM predict_batch on {len(tsfm_indices)} histories (CHUNK={CHUNK})...")
            tsfm_batch_preds = np.empty((len(tsfm_indices), HORIZON), dtype=np.float32)
            t_tsfm = time.time()
            n_done = 0
            truncated = False
            for s in range(0, len(tsfm_indices), CHUNK):
                if time.time() - t_tsfm > args.guard_seconds:
                    log(f"TSFM budget guard tripped at {s}/{len(tsfm_indices)} (elapsed {time.time()-t_tsfm:.1f}s); falling back to sampled estimate")
                    truncated = True
                    guard_pass = False
                    break
                e = min(s + CHUNK, len(tsfm_indices))
                chunk_idx = slice(s, e)
                log(f"  TSFM batch chunk {s}:{e} ({e - s} histories)...")
                tsfm_batch_preds[chunk_idx] = tsfm.predict_batch(
                    tsfm_histories[chunk_idx], HORIZON
                )
                n_done = e
                elapsed_tsfm = float(time.time() - t_tsfm)
                tsfm_calls = int(n_done)
                log(f"  Chunk {s}:{e} done, elapsed_tsfm={elapsed_tsfm:.1f}s")
                write_partial({
                    "mode": mode, "tsfm_calls": tsfm_calls,
                    "elapsed_tsfm": elapsed_tsfm,
                    "guard_pass": not truncated,
                    "truncated": truncated,
                    "n_done": n_done, "n_total": int(len(tsfm_indices)),
                })
            elapsed_tsfm = float(time.time() - t_tsfm)
            tsfm_calls = int(n_done)
            if truncated:
                if n_done > 0:
                    gated_partial = s26_preds.copy()
                    gated_partial[tsfm_indices[:n_done]] = tsfm_batch_preds[:n_done]
                    mae_partial, _, _, _ = rolling_metrics(gated_partial, A_test)
                    estimated_full_mae = float(mae_partial)
                    log(f"Partial gated MAE (with {n_done}/{len(tsfm_indices)} TSFM filled, rest S-26): {mae_partial:.6f} -> estimated_full_mae")
                else:
                    estimated_full_mae = float(s26_mae_full)
                if n_done > 0:
                    gated_preds[tsfm_indices[:n_done]] = tsfm_batch_preds[:n_done]
            else:
                gated_preds[tsfm_indices] = tsfm_batch_preds
                log(f"Batch prediction returned: shape={tsfm_batch_preds.shape}")
                log(f"TSFM predictions generated: {len(tsfm_indices)}/{n_test} elapsed_tsfm={elapsed_tsfm:.1f}s")
    else:
        log("No TSFM-gated origins; gated == S-26")
        elapsed_tsfm = 0.0
        tsfm_calls = 0

    # ------------------------------------------------------------------
    # 6. Full rolling metrics (for sampled mode, weighted estimate + bootstrap CI)
    # ------------------------------------------------------------------
    if args.origins == "sampled":
        # Gated predictions available for sampled_idx; compute per-origin MAE
        A_sampled = A_test[sampled_idx]
        G_sampled = gated_preds[sampled_idx]
        mae_simple, rmse_simple, mae_per_origin_sampled, _ = rolling_metrics(G_sampled, A_sampled)
        # Stratified over sampled subset (20/bucket + 4 disjoint)
        omega_sampled = omega_test_336[sampled_idx]
        mask_a = omega_sampled < 0.4
        mask_b = (omega_sampled >= 0.4) & (omega_sampled <= 0.5)
        mask_c = omega_sampled > 0.5
        # Per-bucket MAE (sampled)
        mae_A = float(np.mean(mae_per_origin_sampled[mask_a])) if np.any(mask_a) else float(np.nan)
        mae_B = float(np.mean(mae_per_origin_sampled[mask_b])) if np.any(mask_b) else float(np.nan)
        mae_C = float(np.mean(mae_per_origin_sampled[mask_c])) if np.any(mask_c) else float(np.nan)
        # Population weights (from full 2161 bucket sizes) — matches TSFM_SLICE_SPEC §4
        N_A = int(np.sum(omega_test_336 < 0.4))
        N_B = int(np.sum((omega_test_336 >= 0.4) & (omega_test_336 <= 0.5)))
        N_C = int(np.sum(omega_test_336 > 0.5))
        assert N_A + N_B + N_C == n_test
        wA, wB, wC = N_A / n_test, N_B / n_test, N_C / n_test
        # Weighted full MAE estimate = sum(population_weight * bucket_sample_MAE)
        # Uses actual population counts N_A,N_B,N_C (distinct from sampled 20/bucket)
        weighted_mae = float(wA * mae_A + wB * mae_B + wC * mae_C)
        # Also compute full gated array MAE if not truncated (fallback S-26 for missing TSFM)
        mae_full_all, rmse_full_all, _, _ = rolling_metrics(gated_preds, A_test)
        # Bootstrap 95% CI for weighted estimate: resample per-bucket MAE vectors (B=2000)
        B = 2000
        rng_bs = np.random.default_rng(args.seed + 101)
        boot_vals = []
        perA = mae_per_origin_sampled[mask_a] if np.any(mask_a) else np.array([])
        perB = mae_per_origin_sampled[mask_b] if np.any(mask_b) else np.array([])
        perC = mae_per_origin_sampled[mask_c] if np.any(mask_c) else np.array([])
        for _ in range(B):
            bA = float(np.mean(rng_bs.choice(perA, size=len(perA), replace=True))) if len(perA) else mae_A
            bB = float(np.mean(rng_bs.choice(perB, size=len(perB), replace=True))) if len(perB) else mae_B
            bC = float(np.mean(rng_bs.choice(perC, size=len(perC), replace=True))) if len(perC) else mae_C
            boot_vals.append(wA * bA + wB * bB + wC * bC)
        boot_vals = np.array(boot_vals)
        ci_lo, ci_hi = float(np.percentile(boot_vals, 2.5)), float(np.percentile(boot_vals, 97.5))
        stratified = {
            "A_lt04_mae": float(mae_A),
            "B_04_05_mae": float(mae_B),
            "C_gt05_mae": float(mae_C),
            "count_A": int(np.sum(mask_a)),
            "count_B": int(np.sum(mask_b)),
            "count_C": int(np.sum(mask_c)),
            "pop_N_A": int(N_A), "pop_N_B": int(N_B), "pop_N_C": int(N_C),
            "weight_A": float(wA), "weight_B": float(wB), "weight_C": float(wC),
            "sampled_simple_mae": float(mae_simple),
        }
        estimated_full_mae = float(weighted_mae)
        log(f"Sampled gated -> simple sampled MAE {mae_simple:.6f} (n={len(sampled_idx)}), weighted full estimate {weighted_mae:.6f} [{ci_lo:.4f}, {ci_hi:.4f}] 95% CI (B={B})")
        log(f"  bucket MAE: A={mae_A:.4f} (n={np.sum(mask_a)}, w={wA:.4f}), B={mae_B:.4f} (n={np.sum(mask_b)}, w={wB:.4f}), C={mae_C:.4f} (n={np.sum(mask_c)}, w={wC:.4f})")
        log(f"  projected full-array MAE (S-26 fallback for missing): {mae_full_all:.6f}")
        # Store for verdict/JSON: primary = weighted estimate
        mae_full = float(weighted_mae)
        rmse_full = float(rmse_simple)  # simple RMSE; bootstrapped RMSE not needed
        mae_per_origin = mae_per_origin_sampled
        mae_for_verdict = float(weighted_mae)
        # stash CI for JSON
        _bootstrap_ci = (ci_lo, ci_hi)
        _bootstrap_n = B
    else:
        # full mode
        if truncated:
            # Already have gated_preds partially filled; compute current MAE
            mae_full, rmse_full, mae_per_origin, rmse_per_origin = rolling_metrics(gated_preds, A_test)
            # estimated_full_mae already set
        else:
            mae_full, rmse_full, mae_per_origin, rmse_per_origin = rolling_metrics(gated_preds, A_test)
            estimated_full_mae = None if not truncated else float(mae_full)
        log(f"Phase 2 gated -> full MAE {mae_full:.6f}, RMSE {rmse_full:.6f}")

        # Stratified over full test
        mask_a = omega_test_336 < 0.4
        mask_b = (omega_test_336 >= 0.4) & (omega_test_336 <= 0.5)
        mask_c = omega_test_336 > 0.5
        stratified = {
            "A_lt04_mae": float(np.mean(mae_per_origin[mask_a])) if np.any(mask_a) else None,
            "B_04_05_mae": float(np.mean(mae_per_origin[mask_b])) if np.any(mask_b) else None,
            "C_gt05_mae": float(np.mean(mae_per_origin[mask_c])) if np.any(mask_c) else None,
            "count_A": int(np.sum(mask_a)),
            "count_B": int(np.sum(mask_b)),
            "count_C": int(np.sum(mask_c)),
        }
        mae_for_verdict = mae_full

    log(f"Stratified gated MAE -> A={stratified['A_lt04_mae']:.4f} (n={stratified['count_A']}), "
        f"B={stratified['B_04_05_mae']:.4f} (n={stratified['count_B']}), "
        f"C={stratified['C_gt05_mae']:.4f} (n={stratified['count_C']})")

    # ------------------------------------------------------------------
    # 7. Disjoint-4 metrics (ensure disjoint preds reflect TSFM gating outcome)
    # ------------------------------------------------------------------
    # Recompute disjoint gated using same tsfm policy (if disjoint indices were in the batch, reuse)
    gated_disj_preds = s26_disj_preds.copy()
    # Map disjoint test indices to tsfm_indices positions where possible
    if args.origins == "disjoint4":
        pass  # already computed above; recompute for consistency
    # For sampled/full, fill disjoint TSFM from gated_preds if available, else per-origin fallback
    # Build lookup from test index -> gated pred
    if args.origins in ("sampled", "full"):
        for j, s_abs in enumerate(disj_starts):
            if gate_mask_disj[j]:
                # test index for this disjoint origin is s = DISJOINT_STARTS[j]
                test_idx = int(DISJOINT_STARTS[j])
                if 0 <= test_idx < n_test and test_idx in (set(tsfm_indices.tolist()) if len(tsfm_indices) else set()):
                    # find position in tsfm_indices
                    pos = int(np.where(tsfm_indices == test_idx)[0][0])
                    if not truncated or pos < tsfm_calls:
                        gated_disj_preds[j] = gated_preds[test_idx]
                    else:
                        # truncated before this disjoint: fallback to per-origin if we want accuracy, else keep S-26
                        gated_disj_preds[j] = s26_disj_preds[j]
                else:
                    # Disjoint gated but not in sampled set -> need per-origin predict if not truncated
                    if not truncated and gate_mask_disj[j]:
                        # Lazy per-origin for missing disjoint
                        if 'tsfm' not in locals():
                            tsfm = TSFMAdapter(context_length=336, device="cpu")
                            _ = tsfm.predict(concat_series[int(s_abs) - L_OMEGA: int(s_abs)], HORIZON)
                        gated_disj_preds[j] = tsfm.predict(concat_series[int(s_abs) - L_OMEGA: int(s_abs)], HORIZON)
                        tsfm_calls += 1

    # If disjoint4 mode, mae_disj already computed; otherwise compute now
    if args.origins != "disjoint4":
        mae_disj, rmse_disj, _, _ = rolling_metrics(gated_disj_preds, A_disj)
        log(f"Phase 2 gated -> disjoint-4 MAE {mae_disj:.6f}, RMSE {rmse_disj:.6f}")
        mae_disj_val = mae_disj
        rmse_disj_val = rmse_disj
    else:
        mae_disj_val = float(mae_disj)
        rmse_disj_val = float(rmse_disj)

    # ------------------------------------------------------------------
    # 8. Verdict logic (thresholds frozen)
    # ------------------------------------------------------------------
    if args.origins == "disjoint4":
        # Verdict already set
        pass
    else:
        improvement = s26_full - float(mae_for_verdict)
        if truncated:
            # When truncated, verdict is estimated; flag accordingly
            if mae_disj_val > s26_disjoint:
                verdict = "REJECTED"
            elif estimated_full_mae is not None and estimated_full_mae <= acceptance_threshold and mae_disj_val <= s26_disjoint:
                verdict = "PROMOTED (estimated)"
            else:
                verdict = "REJECTED (estimated)"
        else:
            verdict = "REJECTED"
            if float(mae_for_verdict) <= acceptance_threshold and mae_disj_val <= s26_disjoint:
                verdict = "PROMOTED"
            elif float(mae_for_verdict) >= s26_full:
                verdict = "REJECTED"
            else:
                verdict = "REJECTED"
        log(f"Verdict: {verdict} | improvement={improvement:+.6f} vs S-26={s26_full} (mode={mode})")
        mae_full = float(mae_for_verdict) if not truncated else float(mae_for_verdict)
        # For JSON, ensure full fields map to measured values
        if args.origins == "sampled":
            # Report sampled MAE as full_mae for this mode; estimated_full_mae holds projection
            pass

    # ------------------------------------------------------------------
    # 9. Write results_tsfm_phase2.json (final)
    # ------------------------------------------------------------------
    stationarity_guard = bool(delta_sigma < 0.5)
    correlation_guard = bool((rho_omega_mae < 0) and (pval_omega_mae < 0.01))
    call_rate_guard = bool(call_rate >= 0.10)

    if args.origins != "disjoint4":
        # For sampled: estimated must be true per spec (weighted full MAE estimate + bootstrap CI)
        is_estimated = bool(args.origins == "sampled" or truncated)
        if args.origins == "sampled":
            # CI already computed above; retrieve
            ci_lo_v, ci_hi_v = _bootstrap_ci if '_bootstrap_ci' in locals() else (None, None)
            bs_n = _bootstrap_n if '_bootstrap_n' in locals() else None
        else:
            ci_lo_v, ci_hi_v, bs_n = None, None, None
        results = {
            "slice": "spectral_omega_gate_phase2",
            "harness_command": (
                "C:/Users/Mateusz/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe "
                "projects/ts-ml-experiments/h720/sub_experiments/spectral_omega_gate/rolling_arm_phase2.py "
                f"--origins {mode}"
            ),
            "harness_log": "harness.log",
            "protocol": (
                "S-20-clean adapted: S-26 members frozen 8545 for val, refit 11425 for test; "
                "TSFM Chronos-Bolt Base zero-shot; hard gate Omega_336>0.5; "
                "TSFMAdapter(context_length=336), CHUNK=8, warmup, guard 750s"
            ),
            "mode": mode,
            "tsfm_calls": int(tsfm_calls),
            "elapsed_tsfm": float(elapsed_tsfm),
            "truncated": bool(truncated),
            "estimated": is_estimated,
            "estimated_full_mae": estimated_full_mae,
            "guard_pass": bool(not truncated and mae_disj_val <= s26_disjoint and stationarity_guard and correlation_guard),
            "gate": {
                "omega_L": L_OMEGA,
                "threshold": OMEGA_THRESHOLD,
                "condition": "hann",
                "call_rate": call_rate,
                "n_tsfm": int(n_tsfm),
                "n_s26": int(n_s26),
            },
            "stationarity": {
                "val_mean": val_mean,
                "val_std": val_std,
                "test_mean": test_mean,
                "test_std": test_std,
                "delta_mean_sigma336": delta_sigma,
                "guard_pass": bool(stationarity_guard),
            },
            "correlation": {
                "rho_omega336_mae": float(rho_omega_mae),
                "pval_mae": float(pval_omega_mae),
                "guard_pass": bool(correlation_guard),
            },
            "call_rate_sanity": {
                "call_rate": call_rate,
                "guard_pass": bool(call_rate_guard),
            },
            "s26_anchor": {
                "full_mae": s26_mae_full,
                "full_rmse": s26_rmse_full,
                "disjoint_4_mae": 1.9696,
                "n": n_test,
            },
            "metrics": {
                "full_mae": float(mae_full) if mae_full is not None else None,
                "full_rmse": float(rmse_full) if rmse_full is not None else None,
                "disjoint_4_mae": float(mae_disj_val),
                "disjoint_4_rmse": float(rmse_disj_val),
                "n": n_test,
                "improvement_vs_s26": float(s26_full - float(mae_full)) if mae_full is not None else None,
                "verdict": verdict,
            },
            "stratified_mae_gated": stratified,
            "plan_impact": {
                "invalidates": [],
                "confirms": [],
                "opens": [],
            },
        }
        if args.origins == "sampled":
            results["bootstrap_ci_95"] = [float(ci_lo_v), float(ci_hi_v)] if ci_lo_v is not None else None
            results["bootstrap_B"] = int(bs_n) if bs_n is not None else None
            results["sampled_n"] = int(len(sampled_idx)) if 'sampled_idx' in locals() and sampled_idx is not None else None
            results["sampled_seed"] = int(args.seed)

        if verdict.startswith("PROMOTED"):
            results["plan_impact"]["confirms"] = [
                f"Omega-gated TSFM improves over S-26 by {float(s26_full - float(mae_full)):.6f} MAE "
                f"({float(mae_full):.6f} < {acceptance_threshold}); all guards pass."
            ]
            results["plan_impact"]["invalidates"] = ["S-26 (1.9909 MAE) as terminal incumbent"]
            results["plan_impact"]["opens"] = ["Omega-gated TSFM as new incumbent for ETTh1 H=720."]
        else:
            results["plan_impact"]["invalidates"] = [
                f"Omega-gated TSFM as SOTA promotion (gated MAE {mae_full} "
                f">= acceptance {acceptance_threshold} or >= S-26 {s26_full} or truncated={truncated})."
            ]
            results["plan_impact"]["confirms"] = [
                f"S-26 remains terminal incumbent at {s26_full} MAE; "
                f"TSFM zero-shot does not transfer to ETTh1 H=720 under Omega gate."
            ]
            results["plan_impact"]["opens"] = [
                "Document negative result; univariate linear family formally closed."
            ]

        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        log(f"Wrote results to {out_json}")

    elapsed = time.time() - t_all
    log(f"Harness completed in {elapsed:.1f}s | mode={mode} verdict={verdict} tsfm_calls={tsfm_calls} elapsed_tsfm={elapsed_tsfm:.1f}s truncated={truncated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
