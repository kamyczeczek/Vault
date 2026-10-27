"""Sanity checks for the Thomas chaotic dynamical system."""
from __future__ import annotations
import numpy as np
from bench import (
    autocorrelation, fit_nlinear, gen_thomas, get_series, pred_nlinear,
    TASKS, thomas_divergence_rate,
)

def test_gen_thomas_properties():
    series = gen_thomas(n=2600)
    assert series.shape == (2600,)
    assert np.isfinite(series).all()
    assert series.std() > 0.1
    assert -6.0 <= series.min() <= series.max() <= 6.0

def test_thomas_reproducibility_and_perturbation():
    assert np.array_equal(gen_thomas(100, seed=1), gen_thomas(100, seed=1))
    assert not np.allclose(
        gen_thomas(100, seed=1, perturbation=1e-4),
        gen_thomas(100, seed=2, perturbation=1e-4),
    )

def test_thomas_dynamics_diagnostics():
    series = gen_thomas(1000)
    assert -1.0 <= autocorrelation(series, 1) <= 1.0
    assert np.isfinite(thomas_divergence_rate())

def test_thomas_in_tasks():
    assert any(task[0] == "thomas_H24" and task[2] == "chaotic" for task in TASKS)
    assert len(get_series("thomas_H24")) == 2600

def test_thomas_sanity_forecast():
    series = get_series("thomas_H24")
    model = fit_nlinear(series[:2000], 24, alpha=1.0)
    preds = np.asarray(pred_nlinear(model, series[1904:2000])).ravel()[:24]
    assert preds.shape == (24,)
    assert np.isfinite(preds).all()

if __name__ == "__main__":
    for test in (test_gen_thomas_properties, test_thomas_reproducibility_and_perturbation,
                 test_thomas_dynamics_diagnostics, test_thomas_in_tasks, test_thomas_sanity_forecast):
        test()
    print("All Thomas attractor sanity checks passed successfully!")
