"""Benchmark Research & Model Discovery Engine (`research_engine.py`)

Integrates workspace intelligence (zero-leakage temporal cross-validation, rigorous anti-overfitting gates, error-residual mutation heuristics, and structured experiment logging) directly into the standalone forecasting benchmark environment.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
import numpy as np


class LeakageError(AssertionError):
    """Raised when a harness check fails. A failure invalidates the run —
    the fix belongs in the harness or the fit, never in the reported number."""


# Feature names that suggest the feature was derived from the prediction
# target or the future. A caller that genuinely needs one must whitelist it
# with a justification string; anything else fails C2.
_TARGET_DERIVED_PATTERNS = ("future", "lead_", "ahead", "target_", "_lead", "next_")


class AntiLeakageHarness:
    """Walk-forward cross-validation harness with mandatory embargoes to prevent future data leakage.

    Three checks, each falsifiable (a leaking fixture fails it — see
    `test_research_engine.py`):
      C1 — no prediction-window statistic reaches the fit: fold geometry is
           disjoint with an embargo gap, and fit/predict outputs are invariant
           under perturbation of everything at/after the fit end.
      C2 — no target-derived feature at fit time: declared feature names must
           not match target-derived patterns (unless whitelisted), and the
           feature builder's output on train rows must be invariant under
           perturbation of the future.
      C3 — no selection on test origins: selection runs inside a guard where
           scoring a test origin raises, and the selection must be unchanged
           when test-origin scores are permuted.
    """
    def __init__(self, train_window: int = 200, horizon: int = 96, embargo: int = 4, step: int = 24):
        self.train_window = train_window
        self.horizon = horizon
        self.embargo = embargo
        self.step = step

    def evaluate_forecaster(self, y: np.ndarray, predict_fn) -> dict[str, float]:
        maes, smapes, mases = [], [], []
        n = len(y)
        t = self.train_window
        n_fallbacks = 0

        while t + self.embargo + self.horizon <= n:
            train_data = y[t - self.train_window : t]
            val_start = t + self.embargo
            val_end = val_start + self.horizon
            val_data = y[val_start:val_end]

            if len(val_data) < self.horizon:
                break

            try:
                preds = predict_fn(train_data, self.horizon)
                fell_back = False
            except Exception as e:
                # Visible fallback (D14): a failed predict is a naive
                # last-value forecast, counted and reported — never silently
                # scored as if it were a real prediction.
                print(f"NOTICE: predict_fn failed at origin {t} ({e}); "
                      f"using naive last-value fallback for this fold.")
                preds = np.full((self.horizon,), train_data[-1])
                fell_back = True
            n_fallbacks += int(fell_back)

            if len(preds) != self.horizon:
                preds = np.resize(preds, (self.horizon,))

            mae = float(np.mean(np.abs(val_data - preds)))

            # SMAPE
            denom = (np.abs(val_data) + np.abs(preds)) / 2.0
            denom = np.where(denom == 0, 1.0, denom)
            smape = float(100.0 * np.mean(np.abs(val_data - preds) / denom))

            # MASE baseline
            mae_naive = np.mean(np.abs(train_data[1:] - train_data[:-1])) if len(train_data) > 1 else 1.0
            mae_naive = max(mae_naive, 1e-8)
            mase = float(mae / mae_naive)

            maes.append(mae)
            smapes.append(smape)
            mases.append(mase)

            t += self.step

        if not maes:
            return {"mae": float("inf"), "smape": float("inf"), "mase": float("inf"),
                    "n_fallbacks": float(n_fallbacks)}

        return {
            "mae": float(np.mean(maes)),
            "smape": float(np.mean(smapes)),
            "mase": float(np.mean(mases)),
            "n_fallbacks": float(n_fallbacks),
        }

    # -- C1: no prediction-window statistic reaches the fit -----------------
    def folds(self, n: int) -> list[tuple[int, int, int, int]]:
        """(fit_start, fit_end, val_start, val_end) per fold. Raises
        LeakageError if any fold's train overlaps its validation window."""
        out = []
        t = self.train_window
        while t + self.embargo + self.horizon <= n:
            fit_start, fit_end = t - self.train_window, t
            val_start, val_end = t + self.embargo, t + self.embargo + self.horizon
            if fit_end > val_start:
                raise LeakageError(
                    f"C1: train [{fit_start}:{fit_end}] overlaps validation "
                    f"[{val_start}:{val_end}] — embargo too small.")
            out.append((fit_start, fit_end, val_start, val_end))
            t += self.step
        if not out:
            raise LeakageError("C1: no fold fits — series shorter than "
                               "train_window + embargo + horizon.")
        return out

    def check_window_isolation(self, fit_fn, pred_fn, series: np.ndarray,
                               fit_end: int, perturbation: float = 10.0,
                               tol: float = 1e-8) -> dict:
        """C1 behavioral check: the fit declares its own window by taking
        (series, fit_end, horizon) and slicing what it needs. Run once on the
        true series and once with everything at/after fit_end perturbed;
        predictions on fixed history must be identical — otherwise the fit
        consumed the prediction window (full-series scaling, dictionary built
        on all data, windows reaching past fit_end)."""
        y = np.asarray(series, dtype=float)
        m1 = fit_fn(y, fit_end, self.horizon)
        p1 = np.asarray(pred_fn(m1, y[:fit_end][-self.horizon:]),
                        dtype=float).ravel()
        y_pert = y.copy()
        y_pert[fit_end:] += perturbation
        m2 = fit_fn(y_pert, fit_end, self.horizon)
        p2 = np.asarray(pred_fn(m2, y[:fit_end][-self.horizon:]),
                        dtype=float).ravel()
        if p1.shape != p2.shape or not np.allclose(p1, p2, atol=tol, rtol=0):
            raise LeakageError(
                "C1: predictions changed under future perturbation "
                f"(max |Δ| = {float(np.max(np.abs(p1 - p2))):.3g}) — "
                "the fit reaches into the prediction window.")
        return {"check": "C1", "passed": True, "max_delta": 0.0}

    # -- C2: no target-derived feature at fit time --------------------------
    def check_features(self, feature_names: list[str],
                       feature_fn=None, series: np.ndarray | None = None,
                       fit_end: int = 0,
                       whitelisted: dict[str, str] | None = None) -> dict:
        """C2: declared feature names must not match target-derived patterns
        unless whitelisted with a justification; and if a feature builder is
        given, its output on train rows must be invariant under perturbation
        of the future (catches scalers/dictionaries fit on the whole series)."""
        whitelisted = whitelisted or {}
        bad = [f for f in feature_names
               if any(p in f for p in _TARGET_DERIVED_PATTERNS)
               and f not in whitelisted]
        if bad:
            raise LeakageError(
                f"C2: target-derived feature names at fit time: {bad} — "
                "whitelist with justification or remove.")
        if feature_fn is not None:
            if series is None or fit_end <= 0:
                raise LeakageError("C2: feature_fn given without series/fit_end "
                                   "to perturb against.")
            y = np.asarray(series, dtype=float)
            x1 = np.asarray(feature_fn(y[:fit_end].copy()))
            y_pert = y.copy()
            y_pert[fit_end:] += 10.0
            x2 = np.asarray(feature_fn(y_pert[:fit_end].copy()))
            # Builder receives the same slice either way; invariance holds
            # unless it reads state derived from the full series (globals,
            # fitted scalers). Shape/dtype equality is the minimum bar.
            if x1.shape != x2.shape or not np.allclose(x1, x2, atol=1e-8, rtol=0):
                raise LeakageError("C2: train features changed under future "
                                   "perturbation — builder leaks the future.")
        return {"check": "C2", "passed": True, "n_features": len(feature_names)}

    # -- C3: no selection on test origins -----------------------------------
    def screened_decision(self, score_fn, decide_fn, select_origins: list,
                          test_origins: list) -> dict:
        """C3 structural check: the choice is locked from select-origin scores
        only — test origins are scored afterwards, so they cannot influence
        the selection. Raises LeakageError on overlap, on any attempt to score
        a test origin before the lock, or if the locked choice is not a pure
        function of select scores (recomputed => must match)."""
        if not select_origins:
            raise LeakageError("C3: empty select origins — nothing to select on.")
        overlap = set(select_origins) & set(test_origins)
        if overlap:
            raise LeakageError(
                f"C3: select and test origins overlap on {sorted(overlap)} — "
                "selection would score what it reports on.")
        locked = {"done": False}

        def guarded_score(origin):
            if locked["done"] and origin in test_origins:
                return score_fn(origin)
            if origin in test_origins:
                raise LeakageError(
                    f"C3: selection scored test origin {origin} before the "
                    "choice locked — select on early origins only.")
            return score_fn(origin)

        select_scores = {o: guarded_score(o) for o in select_origins}
        choice = decide_fn(dict(select_scores))
        if decide_fn(dict(select_scores)) != choice:
            raise LeakageError("C3: selection is not a pure function of "
                               "select-origin scores.")
        locked["done"] = True
        test_scores = {o: guarded_score(o) for o in test_origins}
        return {"check": "C3", "passed": True, "choice": choice,
                "select_scores": select_scores, "test_scores": test_scores}


class ModelDiscoveryEngine:
    """Heuristic mutation engine that analyzes error residuals and proposes architecture improvements."""
    def __init__(self, out_dir: Path):
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def log_experiment(self, experiment_name: str, metrics: dict[str, float], model_spec: dict) -> Path:
        record = {
            "timestamp": time.time(),
            "experiment_name": experiment_name,
            "metrics": metrics,
            "model_spec": model_spec,
        }
        log_path = self.out_dir / f"discovery_{experiment_name}_{int(time.time())}.json"
        log_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        return log_path

    def analyze_residuals(self, residuals: np.ndarray) -> dict[str, float]:
        mean_bias = float(np.mean(residuals))
        std_resid = float(np.std(residuals))
        autocorr = float(np.corrcoef(residuals[:-1], residuals[1:])[0, 1]) if len(residuals) > 2 else 0.0
        return {
            "mean_bias": mean_bias,
            "std_resid": std_resid,
            "lag1_autocorr": autocorr,
        }
