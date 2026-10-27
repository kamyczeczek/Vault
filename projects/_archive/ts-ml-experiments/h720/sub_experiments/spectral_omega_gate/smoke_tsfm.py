"""Smoke-test TSFMAdapter latency and batching behavior."""
from __future__ import annotations

import time
import numpy as np

from tsfm_adapter import TSFMAdapter

H = 720
N = 10
L = 336
CONTEXT = 1024
LOG_PATH = "projects/ts-ml-experiments/h720/sub_experiments/spectral_omega_gate/smoke.log"


def main() -> int:
    lines: list[str] = []
    def log(msg: str) -> None:
        print(msg)
        lines.append(msg)

    log("Loading TSFMAdapter...")
    t0 = time.perf_counter()
    tsfm = TSFMAdapter(context_length=CONTEXT, device="cpu")
    load_sec = time.perf_counter() - t0
    log(f"Load time: {load_sec:.3f}s")

    np.random.seed(0)
    single_history = np.random.randn(L).astype(np.float32)
    batch_histories = np.random.randn(N, L).astype(np.float32)

    # Warmup single to avoid one-off tokenizer/model init skew.
    log("Warmup single predict...")
    _ = tsfm.predict(single_history, H)

    log(f"Single predict: history shape={single_history.shape}, H={H}")
    t1 = time.perf_counter()
    single_out = tsfm.predict(single_history, H)
    single_sec = time.perf_counter() - t1
    log(f"Single output shape: {tuple(single_out.shape)}")
    log(f"Single latency: {single_sec:.4f}s")

    # Warmup batch.
    log("Warmup batch predict...")
    _ = tsfm.predict_batch(batch_histories, H)

    log(f"Batch predict: histories shape={batch_histories.shape}, H={H}")
    t2 = time.perf_counter()
    batch_out = tsfm.predict_batch(batch_histories, H)
    batch_sec = time.perf_counter() - t2
    log(f"Batch output shape: {tuple(batch_out.shape)}")
    log(f"Batch latency: {batch_sec:.4f}s")

    ratio = batch_sec / single_sec if single_sec > 0 else float("inf")
    log(f"Batch/Single latency ratio: {ratio:.2f}x")

    log("---")
    log("Recommended CHUNK heuristic:")
    if ratio <= 1.8:
        log("Batch is nearly linear/amortized. CHUNK=50-100 is fine on CPU.")
    elif ratio <= 3.5:
        log("Batch is moderately superlinear. CHUNK=20-50 is safer.")
    else:
        log("Batch looks superlinear or memory-bound. CHUNK=10-20 recommended.")

    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    log(f"Log saved to {LOG_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
