---
flag: benchmark-core-fev-multivariate-2026-10-27
since: 2026-10-27
owner: mateusz
agent: opencode
model: omniroute/cx-gpt-5.6-luna-medium
origin: session-close
---

`benchmark-core-fev-multivariate-2026-10-27` — 2026-10-27: FEV protocol multivariate support. `extract_series_from_window` zwraca listę 1-D array (jedna na kolumnę targetu) zamiast pojedynczego 1-D. `main_fev` iteruje po kolumnach targetów: fituje model per kolumna, liczy MAE per kolumnę, uśrednia. `P_dict` przechowuje predykcje pierwszej kolumny (dla pool blending). `A_true_per_target` zapewnia poprawne obliczenia. Działa dla univariate (single-element list) i multivariate. `python -m py_compile bench.py` OK. Next: per-origin fit w FEV (obecnie frozen na pierwszym oknie).

not checked: per-origin fit w FEV (obecnie frozen na pierwszym oknie); FEV multivariate end-to-end (Windows multiprocessing issue w fev library uniemożliwia test).
