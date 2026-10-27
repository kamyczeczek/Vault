"""Full forecasting-method registry for long-horizon sunspot plots."""
from __future__ import annotations
import numpy as np
from bench import (fit_nlinear, pred_nlinear, fit_rff, pred_rff, fit_subbands,
                   pred_subband, fit_bigdict, pred_bigdict,
                   fit_amr, pred_amr, fit_bigdict_tree,
                   pred_bigdict_tree, fit_subband_bigdict, pred_subband_bigdict,
                   fit_esn, pred_esn, fit_det_esn, pred_det_esn,
                   fit_knn_forecaster, pred_knn_forecaster)
from members.amr_tree_elm import fit_amr_tree_elm, pred_amr_tree_elm
from members.amr_dynamo_attractor import fit_amr_dynamo_attractor, pred_amr_dynamo_attractor

try:
    from anchored_wavelet_elm import fit_anchored_wavelet_elm, pred_anchored_wavelet_elm
    HAS_WAVELET = True
except ImportError:
    HAS_WAVELET = False

from thomas_models import recursive_delay_forecast
from sunspot_hybrid import hybrid_sunspot_forecast


def _direct(fit, predict, train, history, horizon):
    return predict(fit(train, horizon), history)


def get_sunspot_methods():
    methods = {
        "persistence": lambda train, hist, H: np.repeat(hist[-1], H),
        "nlinear_a1": lambda train, hist, H: _direct(lambda x, h: fit_nlinear(x, h, 1.0), pred_nlinear, train, hist, H),
        "nlinear_a10": lambda train, hist, H: _direct(lambda x, h: fit_nlinear(x, h, 10.0), pred_nlinear, train, hist, H),
        "rff_h64": lambda train, hist, H: _direct(fit_rff, pred_rff, train, hist, H),
        "subband_cA1": lambda train, hist, H: pred_subband(fit_subbands(train, H), hist, "cA1"),
        "subband_d1": lambda train, hist, H: pred_subband(fit_subbands(train, H), hist, "d1"),
        "bigdict_elm": lambda train, hist, H: _direct(fit_bigdict, pred_bigdict, train, hist, H),
        "bigdict_tree": lambda train, hist, H: _direct(fit_bigdict_tree, pred_bigdict_tree, train, hist, H),
        "subband_bigdict": lambda train, hist, H: _direct(fit_subband_bigdict, pred_subband_bigdict, train, hist, H),
        "esn_reservoir": lambda train, hist, H: _direct(fit_esn, pred_esn, train, hist, H),
        "deterministic_esn": lambda train, hist, H: _direct(fit_det_esn, pred_det_esn, train, hist, H),
        "knn_forecaster": lambda train, hist, H: _direct(fit_knn_forecaster, pred_knn_forecaster, train, hist, H),
        "ridge_delay_recursive": lambda train, hist, H: recursive_delay_forecast(train, H),
        "hybrid_lowfreq_residual": hybrid_sunspot_forecast,
        "amr_tree_elm": lambda train, hist, H: _direct(fit_amr_tree_elm, pred_amr_tree_elm, train, hist, H),
        "amr_dynamo_attractor": lambda train, hist, H: _direct(fit_amr_dynamo_attractor, pred_amr_dynamo_attractor, train, hist, H),
    }
    if HAS_WAVELET:
        methods["anchored_wavelet_elm"] = lambda train, hist, H: _direct(fit_anchored_wavelet_elm, pred_anchored_wavelet_elm, train, hist, H)
    return methods
