from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent


def test_seed_sweep_aggregates_every_task_over_every_seed():
    # Two seeds, not the default five: this asserts the aggregation contract,
    # not the benchmark's conclusion, and a 5-seed run does not fit a test.
    # --out-dir keeps this run from overwriting the committed results_s47.json
    # and harness.log, which are the evidence the project is ranked by.
    # Scratch lives under the gitignored __pycache__, not the pytest tmp dir:
    # on Windows the temp root can deny access to a fresh subdirectory, and a
    # scratch dir under results/ would read as untracked build residue (R3).
    out_dir = ROOT / "__pycache__" / "_bench_test_scratch"
    result = subprocess.run(
        [sys.executable, "bench.py", "--seeds", "2", "--out-dir", str(out_dir)],
        cwd=ROOT, capture_output=True, text=True, timeout=1200
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads((out_dir / "results_s47.json").read_text(encoding="utf-8"))
    assert payload["tasks"]["requested"] == 8
    assert payload["tasks"]["evaluated"] == len(payload["tasks"]["names"])
    assert "/6" not in result.stdout
    seeds = payload["protocol"]["seeds"]
    assert len(seeds) == 2 and len(set(seeds)) == 2
    assert len(payload["per_seed"]) == len(seeds)
    # The reported mean must be the mean of the per-seed values it claims to
    # summarise, and the std must actually be present — a number silently
    # collapsed to a single sample is the defect this sweep exists to remove.
    for key in ("meanA", "meanB", "meanC", "meanD"):
        per_seed = [s["aggregate"][key] for s in payload["per_seed"]]
        block = payload["aggregate"][key]
        assert "std" in block and block["std"] > 0.0, f"{key} reports no spread"
        assert abs(block["mean"] - sum(per_seed) / len(per_seed)) < 1e-9
    for task in payload["tasks"]["names"]:
        for pool, block in payload["per_task"][task]["pool_blend"].items():
            assert "std" in block, f"{task} pool {pool} has no std"
    # Win denominators track the tasks actually evaluated.
    for entry in payload["per_seed"]:
        assert entry["aggregate"]["winsB_denominator"] == payload["tasks"]["evaluated"]


def test_seed_sweep_separates_a_real_win_from_a_noise_margin():
    """A win smaller than its own spread must not be reported as a win."""
    from bench import mean_std

    big, big_std = mean_std([-0.30, -0.32, -0.31, -0.29, -0.33])
    noise, noise_std = mean_std([-0.001, 0.002, -0.003, 0.001, 0.0005])
    assert big < -big_std
    assert not noise < -noise_std


def test_strict_mode_fails_closed_when_dependency_is_unavailable(monkeypatch):
    """Strict mode must refuse before any fitting, not partway through a run.

    Asserted in-process with a missing dependency forced, so the check is
    about the gate and not about how long the suite takes. Running `bench.py`
    as a subprocess here would either take minutes or pass by accident on a
    machine where every optional member happens to be installed.
    """
    import bench

    monkeypatch.setattr(bench, "UNAVAILABLE", {"a_member_that_is_not_installed"})
    monkeypatch.setattr(bench, "STRICT_DEPS", True, raising=False)
    # main() parses sys.argv; without this it would read pytest's own flags.
    monkeypatch.setattr(sys, "argv", ["bench.py", "--seeds", "1"])
    with pytest.raises(RuntimeError, match="strict benchmark refused unavailable dependencies"):
        bench.main()


def test_fev_load_failure_returns_none_instead_of_a_suite():
    """A benchmark that cannot be loaded must yield None, never a stand-in.

    The defect this covers: `--fev` used to print a line and carry on with the
    synthetic suite, so the caller got a result that looked like FEV. The URL
    override makes the failure branch reachable without waiting for a real
    outage — the previous hardcoded URLs 404'd and nobody noticed.
    """
    from bench import run_fev_bench

    assert run_fev_bench(url="https://raw.githubusercontent.com/autogluon/fev/main/benchmarks/does_not_exist.yaml") is None


def test_fev_missing_refuses_to_run_the_synthetic_suite():
    """Without an explicit opt-in, a requested FEV that cannot load is a hard stop.

    Exit 2 and no artifact: the synthetic suite must not be written anywhere,
    least of all onto results_s47.json, which is the committed S-47 evidence.
    """
    out_dir = ROOT / "__pycache__" / "_fev_hardstop_test"
    result = subprocess.run(
        [sys.executable, "bench.py", "--fev", "--seeds", "1", "--out-dir", str(out_dir)],
        cwd=ROOT, capture_output=True, text=True, timeout=600,
        env={**os.environ, "FEV_TASKS_URL": "https://raw.githubusercontent.com/autogluon/fev/main/benchmarks/does_not_exist.yaml"},
    )
    assert result.returncode == 2, result.stdout + result.stderr
    assert "refusing to report the synthetic suite as FEV" in result.stderr
    assert not (out_dir / "results_s47.json").exists()
    assert not (out_dir / "bench_synthetic_fallback.json").exists()


def test_fev_fallback_is_stamped_and_kept_off_the_s47_artifact():
    """An opted-in fallback must say what it is and land on its own filename.

    data_source=synthetic_fallback, confirmatory=False, and a name that cannot
    be mistaken for results_s47.json — that is the whole difference between a
    recorded degradation and a result that lies.
    """
    out_dir = ROOT / "__pycache__" / "_fev_fallback_test"
    result = subprocess.run(
        [sys.executable, "bench.py", "--fev", "--allow-synthetic-fallback", "--seeds", "1", "--out-dir", str(out_dir)],
        cwd=ROOT, capture_output=True, text=True, timeout=1800,
        env={**os.environ, "FEV_TASKS_URL": "https://raw.githubusercontent.com/autogluon/fev/main/benchmarks/does_not_exist.yaml"},
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert not (out_dir / "results_s47.json").exists()
    payload = json.loads((out_dir / "bench_synthetic_fallback.json").read_text(encoding="utf-8"))
    assert payload["data_source"] == "synthetic_fallback"
    assert payload["confirmatory"] is False
    assert payload["fev_attempt"]["achieved"] == "synthetic_fallback"
