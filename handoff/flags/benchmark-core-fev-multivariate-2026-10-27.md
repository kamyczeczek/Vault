---
flag: benchmark-core-fev-multivariate-2026-10-27
since: 2026-10-28
owner: mateusz
agent: opencode
model: omniroute/agy/gemini-3.8-flash-high
origin: session-close
---

`benchmark-core-fev-multivariate-2026-10-27` — 2026-10-28: FEV protocol multivariate support oraz per-origin fit w `bench.py`. `extract_series_from_window` zwraca listę 1-D array (jedna na kolumnę targetu) zamiast pojedynczego 1-D; dodano `_unwrap` dla kontenerów fev. `main_fev` iteruje po kolumnach targetów: fituje model per kolumna, liczy MAE per kolumnę, uśrednia. Kod realizuje per-origin fit: pętla `for w in windows:` z `train_cols_w` fituje modele na własnym oknie przeszłości każdego originu. Rozwiązano Windows multiprocessing (`DEFAULT_NUM_PROC = 1`, `num_proc=1`), dopełnianie krótkich szeregów `_pad_train` oraz imputację brakujących danych NaN `_clean_series` i NaN-safe fitting w `pool_blend_mae`. Pełny confirmatory przebieg 20 zadań ukończony z sukcesem w `results/bench_fev_mini.json` (`data_source: "real"`, `confirmatory: true`, `elapsed_s: 2376`): `meanA: 1394255.18`, `meanB: 162480.46`, `meanC: 126113.31`, `meanI: 218548.28`, `winsB: 8/20`, `winsI: 10/20`, `mean_rankB: 2.40`, `verdict: REJECTED` (bramka G2 majority win: 8/20 FAIL). Zsynchronizowano `MAP.md` (91 modułów, `check_workspace_integrity` exit=0).

not checked: pełny 100-zadaniowy `tasks.yaml` (przetestowano 20-zadaniowy oficjalny `tasks_mini.yaml`).
