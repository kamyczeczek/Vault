"""Available forecasting methods adapted to the Thomas comparison protocol."""
from __future__ import annotations
import numpy as np
from bench import fit_nlinear, pred_nlinear, fit_rff, pred_rff, fit_subbands, pred_subband
from thomas_models import recursive_delay_forecast


def get_thomas_methods():
    methods = {
        "persistence": lambda h, H: np.repeat(h[-1], H),
        "nlinear_a1": lambda h, H: pred_nlinear(fit_nlinear(h, H, 1.0), h),
        "nlinear_a10": lambda h, H: pred_nlinear(fit_nlinear(h, H, 10.0), h),
        "rff_h64": lambda h, H: pred_rff(fit_rff(h, H), h),
        "subband_cA1": lambda h, H: pred_subband(fit_subbands(h, H), h, "cA1"),
        "subband_d1": lambda h, H: pred_subband(fit_subbands(h, H), h, "d1"),
        "ridge_delay_recursive": lambda h, H: recursive_delay_forecast(h, H),
    }
    return methods
