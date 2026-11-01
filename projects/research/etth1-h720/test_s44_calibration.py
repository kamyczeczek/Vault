"""Correctness and leakage checks for the S44 calibration harness.

These tests are deliberately cheap: they exercise the stack machinery, the
history-swap discipline, the seed plumbing, and the ridge-fit origin sets
without ever training the PatchTST member (which costs ~2 minutes per fit and
belongs to the measurement, not to the test suite).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

import run_s44_calibration as cal


# --------------------------------------------------------------- stack
def test_stack_has_no_intercept_and_is_per_horizon():
    """A no-intercept per-horizon ridge must not gain a bias term, and each
    horizon must get its own coefficient vector."""
    rng = np.random.default_rng(0)
    n, m, h = 40, 3, 5
    P = rng.normal(size=(n, m, h))
    A = rng.normal(size=(n, h))
    stack = cal.fit_stack_map(P, A, 30000.0, fit_intercept=False)
    assert stack.coef_.shape == (m, h)
    assert np.all(stack.inter_ == 0.0)
    # per-horizon: perturbing horizon 2's targets must not move horizon 0's coefs
    A2 = A.copy()
    A2[:, 2] += 10.0
    s2 = cal.fit_stack_map(P, A2, 30000.0, fit_intercept=False)
    assert np.allclose(stack.coef_[:, 0], s2.coef_[:, 0])
    assert not np.allclose(stack.coef_[:, 2], s2.coef_[:, 2])


def test_stack_recovers_a_known_linear_combination():
    """With exact targets the no-intercept ridge must recover the weights."""
    rng = np.random.default_rng(1)
    n, m, h = 400, 3, 4
    P = rng.normal(size=(n, m, h))
    w = np.array([[0.5, -0.25, 0.75, 1.0]]).T @ np.ones((1, m))  # (h, m)
    A = np.einsum("nmh,hm->nh", P, w)
    stack = cal.fit_stack_map(P, A, 1e-8, fit_intercept=False)
    assert np.allclose(stack.coef_, w.T, atol=1e-4)
    assert np.allclose(stack.predict(P), A, atol=1e-3)


def test_stack_alpha_is_regularisation_not_a_no_op():
    rng = np.random.default_rng(2)
    n, m, h = 60, 2, 3
    P = rng.normal(size=(n, m, h))
    A = rng.normal(size=(n, h))
    small = cal.fit_stack_map(P, A, 1e-6)
    large = cal.fit_stack_map(P, A, 1e6)
    assert np.linalg.norm(large.coef_) < np.linalg.norm(small.coef_)


# --------------------------------------------------- history-swap discipline
def test_predict_at_never_sees_data_after_the_end_index():
    """`history_ = train[:e]` must make the prediction a function of train[:e]
    only — changing train[e:] must not move it."""
    rng = np.random.default_rng(3)
    train = rng.normal(size=1200) * 5.0 + 20.0
    model = cal._fit_member(cal._nlinear_factory(1.0), train)
    ends = [400, 700, 1100]
    base = cal._predict_at(model, train, ends)
    tampered = train.copy()
    tampered[700:] += 100.0
    after = cal._predict_at(model, tampered, ends)
    assert np.allclose(base[0], after[0]) and np.allclose(base[1], after[1])
    assert not np.allclose(base[2], after[2])  # e=1100 does see tampered rows


def test_predict_at_shape_and_finiteness():
    rng = np.random.default_rng(4)
    train = rng.normal(size=1500)
    model = cal._fit_member(cal._nlinear_factory(10.0), train)
    out = cal._predict_at(model, train, [500, 900])
    assert out.shape == (2, cal.H)
    assert np.isfinite(out).all()


# --------------------------------------------------------- ridge-fit origins
def test_ridge_fit_origin_sets_are_strictly_before_the_scored_window():
    """Every ridge-fit origin's scored window must end at or before index CAP,
    i.e. strictly before the scored origin's own target window."""
    for ends in (cal._TAIL_FIT_ENDS, cal._TAIL_FIT_ENDS_SENS):
        assert ends, "ridge-fit set is empty"
        assert max(ends) + cal.H <= cal.CAP, (
            f"a ridge-fit origin's target reaches past the training slice: "
            f"max end {max(ends)} + H {cal.H} > CAP {cal.CAP}")
        assert len(set(ends)) == len(ends), "duplicate ridge-fit origins"
    # the scored origin itself is never in a fit set
    assert cal.CAP not in cal._TAIL_FIT_ENDS
    assert cal.CAP not in cal._TAIL_FIT_ENDS_SENS


def test_primary_ridge_set_mirrors_s44_val_geometry():
    """The primary fit set must be the first 1080 of the 2161 origins inside the
    last 2880 rows — S44's val[0:1080) translated into the S49 window."""
    assert len(cal._TAIL_ENDS) == 2161
    assert len(cal._TAIL_FIT_ENDS) == 1080
    assert cal._TAIL_FIT_ENDS == cal._TAIL_ENDS[:1080]
    assert cal._TAIL_FIT_ENDS[0] == cal.CAP - 2880
    assert cal._TAIL_FIT_ENDS[-1] == cal.CAP - 2880 + 1079


def test_ridge_fit_origins_are_strictly_out_of_sample_for_ridge_members():
    """Ridge members are frozen on the first RIDGE_TRAIN_CAP rows, so every
    ridge-fit origin must start at or after that freeze point — otherwise its
    member forecast is in-sample (the defect this calibration must not repeat)."""
    for ends in (cal._TAIL_FIT_ENDS, cal._TAIL_FIT_ENDS_SENS):
        assert min(ends) >= cal.RIDGE_TRAIN_CAP, (
            f"ridge-fit origin {min(ends)} starts before the member freeze point "
            f"{cal.RIDGE_TRAIN_CAP}: its member forecast would be in-sample")


def test_sensitivity_set_is_disjoint_from_primary_and_same_size():
    assert len(cal._TAIL_FIT_ENDS_SENS) == len(cal._TAIL_FIT_ENDS)
    assert not set(cal._TAIL_FIT_ENDS) & set(cal._TAIL_FIT_ENDS_SENS)
    assert set(cal._TAIL_FIT_ENDS) | set(cal._TAIL_FIT_ENDS_SENS) <= set(cal._TAIL_ENDS)



def test_needed_ends_cover_every_fit_set_and_the_scored_origin():
    need = set(cal._NEEDED_ENDS)
    assert cal.CAP in need
    assert set(cal._TAIL_FIT_ENDS) <= need
    assert set(cal._TAIL_FIT_ENDS_SENS) <= need
    assert need == set(sorted(need))


# -------------------------------------------------------------- seed plumbing
def test_seed_module_sets_the_requested_seed():
    import torch
    original, seeded = cal._seed_module(4242)
    try:
        cal._pte._set_deterministic = seeded
        seeded()
        assert torch.initial_seed() == 4242
    finally:
        cal._pte._set_deterministic = original
    assert cal._pte._set_deterministic is original


def test_seed_module_restores_the_original_even_on_failure():
    original = cal._pte._set_deterministic

    class _Boom:
        def fit(self, train, horizon):
            raise RuntimeError("boom")

        def predict(self):
            raise AssertionError("must not be reached")

    def factory():
        return _Boom()

    cal._patchtst_factory = lambda: factory
    try:
        with pytest.raises(RuntimeError):
            cal._fit_member(factory, np.arange(900.0), seed=7)
    finally:
        cal._patchtst_factory = lambda: cal.PatchTSTModel(
            patch_size=24, D=32, n_layers=2, H=cal.H)
    assert cal._pte._set_deterministic is original


# ------------------------------------------------------- pre-registered facts
def test_protocol_constants_match_the_pre_registration():
    assert cal.ORIGINS == [8640 + 720 * k for k in range(12)]
    assert len(cal.ORIGINS) == 12
    assert cal.ORIGINS[0] == 8640 and cal.ORIGINS[-1] == 16560
    assert cal.SEEDS == [42, 43, 44, 45, 46]
    assert cal.BLEND_ALPHA == 30000.0
    assert cal.H == 720 and cal.CAP == 8640
    assert cal.REPRODUCTION_TOL == 0.01


def test_assert_preregistration_accepts_the_ledger_on_disk():
    cal._assert_preregistration()


def test_assert_preregistration_fails_loud_when_the_ledger_drifts(monkeypatch):
    """A tampered ledger must abort the run rather than let the protocol drift."""
    import tempfile

    real = (cal.ROOT / "GATES-s44-calibration.md").read_text(encoding="utf-8")
    tampered = real.replace("alpha=30000", "alpha=1")
    assert tampered != real, "the tamper did not change the ledger text"
    # tempfile, not pytest's tmp_path: %TEMP%\pytest-of-Mateusz has broken ACLs here.
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        (tmpdir / "GATES-s44-calibration.md").write_text(tampered, encoding="utf-8")
        monkeypatch.setattr(cal, "ROOT", tmpdir)
        with pytest.raises(RuntimeError):
            cal._assert_preregistration()


# ------------------------------------------------------------ summarise maths
def _synthetic_per_origin():
    rows = []
    for i, o in enumerate(cal.ORIGINS):
        rows.append({
            "origin": o, "train_std": 5.0,
            "references": {"bigdict_elm_L96": 2.0 + 0.01 * i,
                           "dlinear": 3.0 + 0.01 * i},
            "per_seed": {str(s): {
                "blend_mae_raw": 2.5 + 0.001 * s + 0.01 * i,
                "blend_mae_raw_variant_sensitivity_secondhalf": 2.6 + 0.01 * i,
                "member_mae_raw": {"nlinear_L336_a1": 2.1 + 0.01 * i,
                                   "nlinear_L336_a10": 2.2 + 0.01 * i,
                                   "patchtst_P24_D32_2L": 2.7 + 0.01 * i},
            } for s in cal.SEEDS},
        })
    return rows


def test_summarise_agrees_with_a_direct_numpy_mean():
    rows = _synthetic_per_origin()
    s = cal._summarise(rows)
    for seed in cal.SEEDS:
        vals = [r["per_seed"][str(seed)]["blend_mae_raw"] for r in rows]
        assert s[f"blend_seed{seed}"]["mae_raw_mean"] == pytest.approx(float(np.mean(vals)))
        assert s[f"blend_seed{seed}"]["mae_raw_std"] == pytest.approx(float(np.std(vals)))
        assert s[f"blend_seed{seed}"]["mae_raw_median"] == pytest.approx(float(np.median(vals)))
        assert len(s[f"blend_seed{seed}"]["per_origin"]) == 12
    # every method must carry 12 per-origin values and a win count vs DLinear
    for name in ("nlinear_L336_a1", "nlinear_L336_a10", "patchtst_P24_D32_2L",
                 "bigdict_elm_L96", "dlinear"):
        assert len(s[name]["per_origin"]) == 12
        assert 0 <= s[name]["wins_vs_dlinear"] <= 12
    # the deterministic NLinear singletons must be identical across seeds
    for r in rows:
        base = r["per_seed"]["42"]["member_mae_raw"]["nlinear_L336_a1"]
        assert all(r["per_seed"][str(s)]["member_mae_raw"]["nlinear_L336_a1"] == base
                   for s in cal.SEEDS)


def test_summarise_seed_spread_is_reported_for_patchtst_and_blend():
    s = cal._summarise(_synthetic_per_origin())
    assert set(s["patchtst_P24_D32_2L_across_seeds"]["per_seed_mean"]) == {str(x) for x in cal.SEEDS}
    assert set(s["blend_across_seeds"]["per_seed_mean"]) == {str(x) for x in cal.SEEDS}
    assert len(s["patchtst_P24_D32_2L_across_seeds"]["per_origin_spread_std"]) == 12
    assert len(s["blend_across_seeds"]["per_origin_spread_std"]) == 12
