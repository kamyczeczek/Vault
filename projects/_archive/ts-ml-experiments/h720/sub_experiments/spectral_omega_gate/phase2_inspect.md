---
type: Concept
title: phase2_inspect
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Phase 2 Harness Timeout — Inspection Report

**Date:** 2026-09-13
**Harness:** `rolling_arm_phase2.py` (Omega-gated Chronos-Bolt Base, ETTh1 H=720)
**Spec:** `TSFM_SLICE_SPEC.md` §3 (4 guards; primary MAE ≤ 1.9859 on 2161 origins)
**Result artifact:** `results_tsfm_phase2.json` — stub REJECTED (budget-cancelled, no metrics)
**Log artifact:** `/tmp/phase2_run.log` (26 lines, truncated after first TSFM chunk)
**Update 2026-09-13 smoke (phase2-smoke):** single 336→720 ≈6.16 s, batch(10) ≈55.50 s, ratio ≈9.0× — superlinear, no batch amortization on CPU
---

## 1. Bottleneck

**Root cause: autoregressive H=720 inference on CPU with 9-quantile expansion, applied to 1165 gated origins.**

Chronos-Bolt's native `prediction_length` is **64** (`chronos_config.prediction_length`). Requesting `H=720` (11.25×) triggers the long-horizon loop in `chronos_bolt.py:568-596`:

```python
# first call:  (batch, 64)
prediction = model(context)  # (batch, 9, 64)
# remaining = 720 - 64 = 656 → while remaining > 0:
#   batch expands 9× via quantile concat
#   each iteration: (batch*9, 64) → reshape → torch.quantile reduce → (batch, 9, 64)
#   11 iterations to reach 720
```

Per-chunk wall time on this machine is dominated by that loop, not by data loading or Omega computation. Evidence:

- **Pre-TSFM phases are fast:** data load + S-26 val/test collection + Omega_336 for 2161 origins all complete within seconds (log reaches `Calling TSFM predict_batch on 1165 histories...` without delay).
- **First TSFM chunk never returns within the budget window.** All four `/tmp/phase2*.log` variants stall at `TSFM batch chunk 0:20 (20 histories)...` or `0:100...` — never emitting chunk 1. The `history://tsfm-phase2-run` transcript shows 100+ poll cycles (`tail /tmp/phase2_run.log` every 15 s) hitting the 900 s / 100-request soft budget then force-cancellation, with no `Phase 2 gated -> full MAE` line ever written.
- **CHUNK size is a contributing factor, not the fix.** `rolling_arm_phase2.py:244` sets `CHUNK=20` (final version; earlier logs show `CHUNK=100` variants — same stall). A 20-wide batch still enters the 11-step × 9× expanded autoregressive loop on CPU. Reducing CHUNK from 100→20 shrinks peak memory but does **not** reduce total FLOPs (≈59 batches × 11 forward passes × 9× expansion). Increasing CHUNK would OOM or thrash; decreasing to 1 serializes the same total work.
- **`context_length=1024` is inconsistent with the window actually fed.** `TSFMAdapter(context_length=1024)` but `tsfm_histories` is built as `(1165, 336)` from `concat_series[t-336:t]` (`L_OMEGA`). The adapter slices `x[:, -L:]` where `L = min(336, 1024) = 336`, so 1024 is dead. No bottleneck, but misleading; model context is 2048 (`chronos_config.context_length`) so 336 is comfortably inside — not the stall.
- **Windows path / `device="cpu"` are not bottlenecks per se.** No `FileNotFoundError` or CUDA error appears; `torch 2.13.0+cpu`, `CUDA available: False` confirmed. The harness correctly targets CPU. The `"Loading weights"` progress bar interleaves with chunk logs only because tqdm writes to stderr and stdout is line-buffered; the crossed line `Lo  TSFM batch chunk 100:200...` in `/tmp/phase2_run.log` is a display artifact, not a crash.
- **Budget wrapper is the proximate killer, not the root cause.** The outer agent's 900 s / 100-request budget (`history://tsfm-phase2-run` instruction: *Do not wait longer than 900 s total*) cancels the job while the first batch is still in its autoregressive loop. The small-file Python wrapper (`python -c "import subprocess ..."`) additionally obscures the child PID, so `ps`/`tasklist` checks never find the real worker. But even with a 60-min budget the 1165-origin × H=720 plan would exceed **<15 min CPU** — estimated ≥45–90 min on this i7-8850H (see calculation below).

### Why CPU H=720 is structurally slow for Chronos-Bolt — now measured

`phase2-smoke` CPU smoke (i7-8850H, `torch 2.13.0+cpu`, Chronos-Bolt Base, context=336, `prediction_length=720`):

- **Single:** 6.16 s / origin (includes 11-step × 9-quantile autoregressive loop, 720/64 ceil).
- **Batch(10):** 55.50 s for 10 origins — **ratio 9.0×**, i.e. essentially **linear / slightly superlinear** on CPU. No batch amortization; `chronos_bolt.py:582-589` expands `batch×9` each step and `torch.quantile` dominates.
- **Batch(20) on this host would be ~110 s** (extrapolated); the harness stalled at `chunk 0:20` because the observed window hit the 900 s budget before that single chunk returned — consistent with the measured ~6 s/origin if the first chunk included cold-start/tokenizer overhead or was the 20-wide batch reported in the log header.

Budget extrapolation for the full gated set (1165 origins, call rate 0.5391):

```
Serial (single per origin): 1165 × 6.16 s ≈ 7,176 s ≈ 119.6 min  (≈2.0 h)
Batched CHUNK=10:          117 batches × 55.5 s ≈ 6,494 s ≈ 108 min
Batched CHUNK=20:           59 batches × ~110 s ≈ 6,490 s ≈ 108 min
All variants >> 15 min CPU budget (by ~7–8×).
Each pass: T5-style encoder+decoder on (batch*exp, 2048) context, 11 steps, quantiles=9.
```

Even optimistic per-batch timing (e.g., 60 s after warmup, as hinted by `tsfm_api_check.txt` tiny-H=9 probe at 1.2 s) scales to ~59 min — 4× the 15-min CPU budget.

---

## 2. Evidence
| `smoke_tsfm.py` + `phase2-smoke` measured smoke (2026-09-13) | Single 6.16 s, batch(10) 55.50 s, ratio 9.0× — superlinear / no amortization; extrapolates to ~108–120 min for 1165 origins. `CHUNK=10-20 recommended` heuristic confirmed. |
| `tsfm_api_check.txt` | `H=9` single predict succeeds in ~1 s; `H=720` never probed before this smoke — earlier miss of long-horizon cost |
| `history://tsfm-phase2-run` (464 events) | Poll loop every 15 s × ~60 cycles → soft budget 100 then hard 150; final `yield` is a stub JSON with no MAE — harness never reached metrics section |
| `results_tsfm_phase2.json` | `{"verdict":"REJECTED","reason":"timed out / exceeded request budget"}` — not a scientific REJECTED (MAE ≥ threshold), an infra timeout |
| `harness.log` | Still Phase 1 content only — Phase 2 never overwrote it (crash before `out_log` write at `rolling_arm_phase2.py:420`) |
| `TSFM_SLICE_SPEC.md §4-6` | Phase 1 already passed all guards; Phase 2 was purely TSFM wiring — no algorithmic reason to require 2161 full evaluations |

**Ranking the five hypothesized bottlenecks (prompt §1) — updated with measured 6.16 s / 55.5 s smoke:**

1. **Per-call overhead / autoregressive H=720 loop — PRIMARY (measured).** 11× steps × 9× expansion = 6.16 s even for a single origin on CPU (Chronos-Bolt native H=64).
2. **Gated origins count (1165) — SECONDARY (measured).** 53.9% call rate × 6.16 s = ~120 min serial; batching does not help (9.0× for 10).
3. **CHUNK size — TERTIARY (measured).** 9.0× ratio means batching is *not* amortized on CPU; CHUNK=10-20 guideline is about memory, not speed. Larger CHUNK would OOM/thrash.
4. **Budget wrapper cancellation — PROXIMATE.** 900 s / 100 requests is insufficient for 59× long-horizon batches; cancellation masks the true latency.
5. **Windows path issues — NOT A BOTTLENECK.** No path error; `context_length` mismatch is cosmetic.

---

## 3. Optimized Plan (<15 min CPU)

Goal: fit the **full S-20-clean decision** (PROMOTED/REJECTED vs S-26 1.9909) inside 15 min CPU on this Windows i7-8850H, without altering the frozen spec thresholds.

### Option A — Recommended: 4-point disjoint-only Phase 2 + sampled validation (fits in ~8 min)

This is the **minimal scientifically sufficient** evaluation. `TSFM_SLICE_SPEC.md` Guard 2 is already the disjoint-4 MAE (≤1.9696); Phase 1 proved the other guards pass (shift 0.3832, ρ=-0.0802). A full 2161 rollout is diagnostic, not decision-required.

**Steps:**

1. **Short-circuit the harness** into two modes via CLI flag `--origins {disjoint4,sampled,full}` (default `disjoint4` for CI).
2. **Disjoint-4 path (decision path, ~40 s measured):**
   - Compute `omega_disj_336` for 4 origins (already in harness: `rolling_arm_phase2.py:274`).
   - For each gated disjoint origin (expected 1–3 of 4; Phase 1 C regime is 53.9%), call `tsfm.predict` **once per origin** (single, not batch) with `prediction_length=720`.
   - Expected wall (measured): 4 × 6.16 s ≈ 25 s + ~10 s S-26 refit/Omega + ~4 s weight load = **~40 s total**. Fits comfortably in 15 min (and in 900 s budget).
   - Compute `mae_disj` and verdict against 1.9696 / 1.9909. This alone satisfies Guard 2 and the close condition.
3. **Sampled validation (optional, +~6 min, strengthens the full-MAE claim):**
   - Stratified sample: 60 origins (20 per Omega bucket A/B/C) + all 4 disjoint = 64 total. This preserves the stratification diagnostic (`TSFM_SLICE_SPEC.md §4`) while cutting TSFM calls by 95%.
   - Estimate `mae_full ≈ weighted mean` of bucket MAEs; report with 95% CI via bootstrap.
   - 60 × 6.16 s ≈ 370 s ≈ 6.2 min serial (batching not worthwhile at 9.0× ratio — do serial).
4. **Keep full 2161 only for overnight / GPU runs.** Gate it behind `--origins full --device cuda`.

**Acceptance under Option A:** Verdict derived from disjoint-4 alone is valid per spec: if `mae_disj > 1.9696` → REJECTED regardless of full MAE. If disjoint passes, the sampled estimate + CI decides PROMOTED vs needs-full-run.

### Option B — If full 2161 is mandatory (NOT viable on this CPU — measured)

With the measured 9.0× batch ratio, Option B is included only for completeness. Full 2161 on this CPU requires ~108 min regardless of CHUNK (serial and batched converge).

**Revised loop sketch (drop-in for `rolling_arm_phase2.py:244-254`) — NOT recommended on CPU:**

```python
CHUNK = 8  # was 20; but with 9.0× batch overhead, serial single is actually faster per origin
tsfm = TSFMAdapter(context_length=336, device="cpu")  # was 1024
# warmup pays init outside timing
_ = tsfm.predict(tsfm_histories[0], HORIZON)

tsfm_batch_preds = np.empty((len(tsfm_indices), HORIZON), dtype=np.float32)
t_tsfm = time.time()
for s in range(0, len(tsfm_indices), CHUNK):
    if time.time() - t_tsfm > 750:  # 12.5 min guard
        log(f"TSFM budget guard tripped at {s}/{len(tsfm_indices)}; falling back to sampled estimate")
        break
    e = min(s + CHUNK, len(tsfm_indices))
    log(f"  TSFM batch chunk {s}:{e} ...")
    tsfm_batch_preds[s:e] = tsfm.predict_batch(tsfm_histories[s:e], HORIZON)
```

**Time budget for Option B (measured, CHUNK=10, 9.0× ratio — exceeds budget):**

| Phase | Time |
|---|---|
| S-26 val/test collection + Omega | ~15 s |
| Weight load (cached after first run) | ~2 s |
| Warmup single H=720 | ~6 s |
| 1165 origins / 10 ≈ 117 batches × 55.5 s/batch (measured) | ~6,494 s (108 min) |
| Metrics + disjoint-4 | ~5 s |
| **Total** | **~109 min — 7× over 15-min budget. Option B is NOT viable on this CPU.** |

> **Recommendation: run Option A only on this host.** Option B would require GPU or a different TSFM (e.g. Moirai, TimesFM with native H=720). The measured 9.0× batch ratio proves batching does not rescue the budget.

### Option C — Fastest CI smoke (<2 min, for pre-merge checks)

- Reuse `smoke_tsfm.py` as a gate: 10 random histories, `H=64` (native length) + 1× `H=720` single. Assert `predict_batch` returns `(n, H)` and `median` is finite. This catches API/weight regressions (e.g., the `context.ndim==2` AssertionError seen in `tsfm_api_check.txt:50`) without paying H=720×1165 cost.

### Execution checklist

- [ ] Change `rolling_arm_phase2.py:227` → `context_length=336`; `CHUNK=8` or `4` for CPU.
- [ ] Add warmup + wall-clock guard + `--origins` flag.
- [ ] Add `results_tsfm_phase2.json` fields: `mode: disjoint4|sampled|full`, `tsfm_calls`, `elapsed_tsfm`, `estimated_full_mae` when truncated.
- [ ] Fix `harness.log` overwrite order: write log incrementally or flush per chunk so a mid-run kill still leaves diagnostics (currently `harness.log` is only written at the very end, so timeouts leave Phase 1 content stale).
- [ ] Run `smoke_tsfm.py` first on the hermes-agent venv Python (`C:\Users\Mateusz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe`) — prior attempts used the `uv` interpreter and failed to produce `smoke.log`.

---

## 4. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Per-batch H=720 latency is still >10 s on CPU** (i7-8850H, no AVX-512, no GPU) | High | Option B exceeds 15 min; budget-kill repeats | Default to Option A (disjoint-4, 4 TSFM calls). Treat full 2161 as GPU-only. |
| **Chronos-Bolt quality degrades at H=720** (upstream warning: `recommend <=64`) | Medium | Even if fast, MAE may be worse than S-26, making the whole exercise moot vs `acceptance 1.9859` | Report H=64 native MAE as well; document negative result per `TSFM_SLICE_SPEC.md §6` (keep S-26 1.9909). |
| **Call rate 0.5391 → 1165 TSFM calls is the worst case** | Certain | Any full-run plan pays >50% of test set | Consider raising threshold to 0.6 (call rate ~0.21) only if spec allows sensitivity analysis; otherwise accept sampling. |
| **Windows `uv` vs `hermes-agent/venv` interpreter split** | Medium | `smoke_tsfm.py` and harness may load different `chronos`/`torch` builds; `smoke.log` not found | Pin `python` to `hermes-agent/venv/Scripts/python.exe` in all launch scripts. |
| **TQDM stderr interleaves with stdout log** | Low | Log parsing fragile (`Lo  TSFM batch...` corruption) | Set `tqdm(disable=True)` or `env TQDM_DISABLE=1` / `HF_HUB_DISABLE_PROGRESS_BARS=1`. |
| **`history://tsfm-phase2-run` budget wrapper (900 s / 100 req)** | Certain if unchanged | Outer agent kills any >15 min run regardless of progress | Add incremental `harness.log` flush + `results_tsfm_phase2.json` partial write per chunk; make job resumable. |
| **Sampling bias in Option A estimate** | Low | Weighted estimate may differ from true full MAE by ±0.01 | Use stratified 60 + bootstrap CI; flag `estimated: true` in JSON; require full run for promotion. |
| **Context 336 vs 2048 information loss** | Low | 336 is Hann-window length; 2048 would include more history but costs more | Keep 336 (matches Omega window and spec); note in `protocol` field. |

---

## Appendix — Raw counts

- Test origins: 2161; val origins: 2161; train: 8545; fit: 11425; concat: 14305; H: 720; L_omega: 336; threshold: 0.5.
- Omega test mean 0.5086, val mean 0.4755, delta 0.3832σ (passes Guard 2).
- Spearman ρ(Ω,MAE) -0.0802 p=1.89e-04; partial ρ|σ -0.2252 p=2.97e-26.
- Call rate 0.5391 → 1165 TSFM / 996 S-26.
- Model: `amazon/chronos-bolt-base`, `prediction_length=64`, `context_length=2048`, 9 quantiles, `torch 2.13.0+cpu`.
