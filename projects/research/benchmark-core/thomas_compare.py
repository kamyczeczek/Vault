"""Small horizon-wise model comparison on the Thomas attractor."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from bench import gen_thomas, fit_nlinear, pred_nlinear
from chaos_protocol import evaluate_forecaster
from thomas_models import recursive_delay_forecast

DEFAULT_HORIZONS = (1, 4, 8, 24, 48)
DEVELOPMENT_ORIGINS = (1200, 1400, 1600)
LOCKED_ORIGINS = (1800, 1900)


def run_comparison(n=2600, horizons=DEFAULT_HORIZONS,
                   origins=DEVELOPMENT_ORIGINS, locked_origins=LOCKED_ORIGINS):
    series = gen_thomas(n=n)
    def persistence(history, horizon): return np.repeat(history[-1], horizon)
    def nlinear(history, horizon): return pred_nlinear(fit_nlinear(history, horizon, alpha=1.0), history)
    models = {"persistence": persistence, "nlinear_direct": nlinear,
              "ridge_delay_recursive": recursive_delay_forecast}
    result = {"system": "thomas", "n": n, "horizons": list(horizons),
              "development_origins": list(origins), "locked_origins": list(locked_origins), "models": {}}
    for name, model in models.items():
        result["models"][name] = {
            "development": evaluate_forecaster(series, model, horizons, origins),
            "locked": evaluate_forecaster(series, model, horizons, locked_origins),
        }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    text = json.dumps(run_comparison(), indent=2)
    if args.output: args.output.write_text(text + "\n", encoding="utf-8")
    print(text)

if __name__ == "__main__": main()
