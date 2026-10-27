#!/usr/bin/env python3
"""robust_eval.py — Scale-independent and magnitude metrics for the benchmark suite.
"""
from __future__ import annotations

import numpy as np


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


def mse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean((y_true - y_pred) ** 2))


def smape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    denominator = (np.abs(y_true) + np.abs(y_pred)) / 2.0
    mask = denominator == 0
    diff = np.abs(y_true - y_pred) / np.where(mask, 1.0, denominator)
    return float(100.0 * np.mean(diff))


def wape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    sum_abs_true = np.sum(np.abs(y_true))
    if sum_abs_true == 0:
        return 0.0
    return float(100.0 * np.sum(np.abs(y_true - y_pred)) / sum_abs_true)


def mase(y_true: np.ndarray, y_pred: np.ndarray, y_train: np.ndarray, seasonality: int = 1) -> float:
    n = len(y_train)
    if n <= seasonality:
        return 1.0
    mae_naive = np.mean(np.abs(y_train[seasonality:] - y_train[:-seasonality]))
    if mae_naive == 0:
        return 1.0
    return float(mae(y_true, y_pred) / mae_naive)
