"""Comprehensive test suite for benchmark-core v2 foundation modules.

Exercises:
- manifest.py: family extraction, 7 domains, disjointness, window indexing, SHA256 stability.
- metrics.py: seasonal error, MASE, clipping [0.01, 100.0], geometric mean, skill score.
- bootstrap.py: cluster bootstrap over families, alpha thresholds, sensitivity variants.
- ledger.py: canonical JSON, hash chaining, genesis binding, corruption detection.
- guards.py: Gate 1, Gate 2, Gate 3, population capacity, conditional eviction, STOP rules.
"""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pytest

import manifest
import metrics
import bootstrap
import ledger
import guards


# ---------------------------------------------------------------- manifest
def test_manifest_build_and_invariants():
    # Use real mini and full task definitions cached in scripts/_scratch/
    base = Path(__file__).resolve().parent
    # Prefer task definitions shipped with the repo (fresh-clone friendly);
    # fall back to the legacy scratch cache, then skip explicitly.
    candidates = [
        (base / "results" / "fev_tasks_mini.json", base / "results" / "fev_tasks_full.json"),
        (base.parent.parent.parent / "scripts" / "_scratch" / "mini_tasks.json",
         base.parent.parent.parent / "scripts" / "_scratch" / "full_tasks.json"),
    ]
    mini_path = full_path = None
    for mini_cand, full_cand in candidates:
        if mini_cand.exists() and full_cand.exists():
            mini_path, full_path = mini_cand, full_cand
            break

    if mini_path is None:
        pytest.skip(
            "Brak definicji zadan (results/fev_tasks_*.json ani "
            "scripts/_scratch/*_tasks.json); test pomija sprawdzenia manifestu."
        )

    mini_tasks = json.loads(mini_path.read_text(encoding="utf-8"))
    full_tasks = json.loads(full_path.read_text(encoding="utf-8"))
    m = manifest.build_manifest(mini_tasks, full_tasks)
    assert m["counts"]["dev_tasks"] == 20
    assert m["counts"]["dev_families"] == 15
    assert "ETT" not in set(t["family"] for t in m["lockbox_tasks"])
    assert any(q["dataset_config"] == "ETT_1D" for q in m["unused_sibling_quarantine"])
    assert any(l["dataset_config"] == "m5_1D" for l in m["lockbox_tasks"])
    sha = manifest.compute_manifest_sha256(m)
    assert len(sha) == 64


def test_window_selection():
    assert manifest.select_window_indices(20, 3) == [17, 18, 19]
    assert manifest.select_window_indices(5, 3) == [2, 3, 4]
    assert manifest.select_window_indices(2, 3) == [0, 1]
    assert manifest.select_window_indices(1, 3) == [0]


# ---------------------------------------------------------------- metrics
def test_seasonal_error_and_mase():
    # Simple constant seasonal signal: period 2
    past = np.array([1.0, 5.0, 1.0, 5.0, 1.0, 5.0])
    s_err = metrics.compute_in_sample_seasonal_error(past, seasonality=2)
    assert s_err == 0.0  # Perfect periodic

    past_noisy = np.array([1.0, 5.0, 2.0, 6.0])
    # diffs: |2 - 1| = 1, |6 - 5| = 1 -> mean = 1.0
    assert metrics.compute_in_sample_seasonal_error(past_noisy, seasonality=2) == 1.0

    y_true = np.array([1.0, 2.0])
    y_pred = np.array([2.0, 4.0])
    # MAE = (|1-2| + |2-4|)/2 = 1.5. mase = 1.5 / 1.0 = 1.5
    assert metrics.compute_mase(y_true, y_pred, seasonal_error=1.0) == 1.5


def test_relative_error_clipping_and_skill():
    assert metrics.clip_relative_error(0.001) == 0.01
    assert metrics.clip_relative_error(150.0) == 100.0
    assert metrics.clip_relative_error(0.8) == 0.8

    # If model is 20% better across all tasks (r = 0.8), skill score is 0.2
    assert pytest.approx(metrics.compute_skill_score([0.8, 0.8, 0.8])) == 0.2


# ---------------------------------------------------------------- bootstrap
def test_cluster_bootstrap_positive_detection():
    # Suppose we have 4 families, model is clearly better on all tasks
    task_ratios = {
        "t1": 0.7, "t2": 0.8,
        "t3": 0.75,
        "t4": 0.6, "t5": 0.7,
        "t6": 0.8,
    }
    task_families = {
        "t1": "famA", "t2": "famA",
        "t3": "famB",
        "t4": "famC", "t5": "famC",
        "t6": "famD",
    }
    res = bootstrap.cluster_bootstrap_families(task_ratios, task_families, n_resamples=1000, alpha=0.05, seed=123)
    assert res["point_estimate"] > 0.2
    assert res["one_sided_lower_ci"] > 0.0
    assert res["passes_gate"] is True


def test_cluster_bootstrap_rejection():
    # Model is worse on average
    task_ratios = {"t1": 1.2, "t2": 1.3, "t3": 1.1}
    task_families = {"t1": "famA", "t2": "famB", "t3": "famC"}
    res = bootstrap.cluster_bootstrap_families(task_ratios, task_families, n_resamples=500, alpha=0.05, seed=42)
    assert res["point_estimate"] < 0.0
    assert res["passes_gate"] is False


# ---------------------------------------------------------------- ledger
def test_ledger_genesis_and_chain():
    scratch_dir = Path(__file__).resolve().parent / "__pycache__" / "_test_ledger_scratch"
    scratch_dir.mkdir(parents=True, exist_ok=True)
    led_file = scratch_dir / "ledger.jsonl"
    if led_file.exists():
        led_file.unlink()

    led = ledger.Ledger.initialize_genesis(led_file, manifest_sha256="abc123sha")
    assert led.exists()

    h1 = led.append_entry({"type": "cycle_card", "candidate": "test_model"})
    h2 = led.append_entry({"type": "run_result", "skill_score": 0.05})

    led.verify_integrity(expected_manifest_sha256="abc123sha")

    # Verify tampering detection on an entry preceding the last
    content = led_file.read_text(encoding="utf-8")
    tampered = content.replace("test_model", "evil_tampered_model")
    led_file.write_text(tampered, encoding="utf-8")

    with pytest.raises(ValueError, match="Hash chain broken"):
        led.verify_integrity()

    # Cleanup
    if led_file.exists():
        led_file.unlink()


# ---------------------------------------------------------------- guards
def test_population_and_capacity():
    pop = guards.PopulationManager([
        {"name": "DLinear", "roles": ["champion", "anchor"]},
        {"name": "NLinear", "roles": ["anchor"]},
    ])
    assert pop.get_champion()["name"] == "DLinear"
    assert len(pop.get_anchors()) == 2

    # Cannot evict anchor
    card = {
        "candidate_name": "model_x",
        "hypothesis": "test",
        "falsifier": "test",
        "replaces": "DLinear",
    }
    # Fill to capacity
    for i in range(6):
        pop.apply_adoption(f"challenger_{i}", ["challenger"])
    assert len(pop.models) == 8

    valid, reason = pop.validate_cycle_card(card)
    assert not valid
    assert "Cannot evict protected method" in reason

    # Evict valid challenger
    card["replaces"] = "challenger_0"
    valid, reason = pop.validate_cycle_card(card)
    assert valid

    pop.apply_adoption("model_x", ["champion"], replaces="challenger_0")
    assert len(pop.models) == 8
    assert pop.get_champion()["name"] == "model_x"
    dlinear_entry = [m for m in pop.models if m["name"] == "DLinear"][0]
    assert "champion" not in dlinear_entry["roles"]


def test_gates_and_stop_rules():
    # Gate 1
    p1, _ = guards.check_gate1_entry(True, 600.0, failed_fits=2, total_fits=741)
    assert p1 is True
    p1_fail, msg = guards.check_gate1_entry(True, 1300.0, failed_fits=2, total_fits=741)
    assert p1_fail is False
    assert "exceeded 20m" in msg

    # Gate 2
    boot_pass = {"one_sided_lower_ci": 0.02}
    dom_ok = {"cloud": 0.98, "energy": 1.02}
    ratios_ok = {"t1": 0.9, "t2": 1.25}  # 1 task > 1.20 is allowed
    p2, reasons = guards.check_gate2_promotion(boot_pass, dom_ok, ratios_ok)
    assert p2 is True

    # Gate 2 failure on domain
    dom_bad = {"cloud": 0.98, "energy": 1.08}  # > 1.05
    p2_bad, reasons = guards.check_gate2_promotion(boot_pass, dom_bad, ratios_ok)
    assert p2_bad is False

    # Stop rules
    s, reason = guards.check_stop_conditions(lockbox_passed=False, lockbox_eval_count=3, consecutive_stagnation_cycles=0, total_cycle_count=5)
    assert s is True
    assert "Lockbox burned" in reason


# ------------------------------------------------------------- scanner helpers
class _ColumnLike:
    """Mimics datasets.Column: iterable and indexable, but not a list/tuple/ndarray.

    This is the exact shape that broke the first denominator scanner:
    `np.asarray` on the container either concatenated every item into a single
    vector (when items shared a length) or raised on ragged columns.
    """

    def __init__(self, items):
        self._items = list(items)

    def __len__(self):
        return len(self._items)

    def __getitem__(self, i):
        return self._items[i]

    def __iter__(self):
        return iter(self._items)


def test_scanner_unwraps_column_per_item():
    pytest.importorskip("fev")
    import scan_denominator_anomalies as scan

    col = _ColumnLike([
        np.array([1.0, 2.0, 1.0, 2.0]),
        np.array([5.0, 6.0, 5.0, 6.0]),
    ])
    items = scan.as_item_arrays(col)
    # The bug collapsed this into one concatenated 8-element vector.
    assert len(items) == 2
    assert items[0].shape == (4,)
    assert items[1].shape == (4,)


def test_scanner_seasonal_error_matches_fev_semantics():
    pytest.importorskip("fev")
    import scan_denominator_anomalies as scan

    # History not longer than m: fev yields NaN (excluded from aggregation),
    # never 0.0 -- 0.0 would falsely read as a zero denominator.
    assert np.isnan(scan.seasonal_error_per_item([np.array([1.0, 2.0])], m=2)[0])
    # Perfectly periodic history: the only genuine zero denominator.
    assert scan.seasonal_error_per_item([np.array([1.0, 5.0, 1.0, 5.0])], m=2)[0] == 0.0
    # Mean absolute seasonal difference.
    assert scan.seasonal_error_per_item([np.array([1.0, 5.0, 2.0, 6.0])], m=2)[0] == 1.0


# ---------------------------------------------------------------- metrics extra (risk 3.2)
def test_compute_mase_zero_seasonal_raises():
    import numpy as np
    with pytest.raises(ZeroDivisionError):
        metrics.compute_mase(np.array([1.0, 2.0]), np.array([1.0, 2.0]), seasonal_error=0.0)


def test_evaluate_task_ratios_and_aggregate():
    ratios = metrics.evaluate_task_ratios({"t1": 0.5, "t2": 2.0}, {"t1": 1.0, "t2": 1.0})
    assert ratios == {"t1": 0.5, "t2": 2.0}
    with pytest.raises(ValueError):
        metrics.evaluate_task_ratios({"t1": 1.0}, {"t1": 0.0})

    summary = metrics.aggregate_benchmark_summary({"t1": 0.5, "t2": 2.0}, {"t1": "cloud", "t2": "energy"})
    assert "skill_score" in summary
    assert "worst_task" in summary


# ---------------------------------------------------------------- bootstrap extra (risk 3.2)
def test_cluster_bootstrap_zero_families_raises():
    with pytest.raises(ValueError, match="0 families"):
        bootstrap.cluster_bootstrap_families({}, {}, n_resamples=10, alpha=0.05, seed=1)


def test_cluster_bootstrap_single_family():
    ratios = {"t1": 0.8, "t2": 0.9}
    fams = {"t1": "famA", "t2": "famA"}
    res = bootstrap.cluster_bootstrap_families(ratios, fams, n_resamples=50, alpha=0.05, seed=7)
    assert res["n_families"] == 1
    assert res["n_tasks"] == 2
    assert "passes_gate" in res


# ---------------------------------------------------------------- guards extra (risk 3.2)
def test_check_stop_conditions_variants():
    # lockbox burn
    stop, reason = guards.check_stop_conditions(False, 3, 0, 1)
    assert stop is True and "Lockbox burned" in reason
    # stagnation
    stop, reason = guards.check_stop_conditions(False, 0, 6, 1)
    assert stop is True and "stagnation" in reason
    # global budget
    stop, reason = guards.check_stop_conditions(False, 0, 0, 20)
    assert stop is True and "Global cycle budget" in reason
    # continue
    stop, reason = guards.check_stop_conditions(False, 0, 0, 1)
    assert stop is False and reason == "CONTINUE"


def test_validate_cycle_card_missing_and_capacity():
    pop = guards.PopulationManager([])
    valid, reason = pop.validate_cycle_card({})
    assert not valid and "candidate_name" in reason

    # capacity eviction of protected role is blocked
    pop2 = guards.PopulationManager([{"name": "A", "roles": ["anchor"]}])
    # fill to capacity artificially by adding 7 more
    for i in range(7):
        pop2.models.append({"name": f"x{i}", "roles": ["challenger"]})
    assert len(pop2.models) == 8
    valid, reason = pop2.validate_cycle_card({"candidate_name": "new", "hypothesis": "h", "falsifier": "f", "replaces": "A"})
    assert not valid and "protected" in reason


# ---------------------------------------------------------------- ledger extra (risk 3.2)
def test_ledger_corruption_detection():
    scratch_dir = Path(__file__).resolve().parent / "__pycache__" / "_ledger_scratch2"
    scratch_dir.mkdir(parents=True, exist_ok=True)
    led_file = scratch_dir / "ledger2.jsonl"
    if led_file.exists():
        led_file.unlink()

    led = ledger.Ledger.initialize_genesis(led_file, manifest_sha256="shaX")
    led.append_entry({"type": "cycle_card", "candidate": "m"})
    led.verify_integrity(expected_manifest_sha256="shaX")

    # tamper manifest in genesis
    content = led_file.read_text(encoding="utf-8")
    tampered = content.replace("shaX", "shaY", 1)
    led_file.write_text(tampered, encoding="utf-8")
    with pytest.raises(ValueError):
        led.verify_integrity(expected_manifest_sha256="shaX")

    if led_file.exists():
        led_file.unlink()
