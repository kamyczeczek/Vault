---
flag: benchmark-core-fev-multivariate-2026-10-27
since: 2026-10-28
owner: mateusz
agent: opencode
model: omniroute/agy/gemini-3.8-flash-high
origin: session-close
---

`benchmark-core-fev-multivariate-2026-10-27` — 2026-10-28: FEV protocol multivariate support oraz per-origin fit w `bench.py`. `extract_series_from_window` zwraca listę 1-D array (jedna na kolumnę targetu) zamiast pojedynczego 1-D; dodano `_unwrap` dla kontenerów fev. `main_fev` iteruje po kolumnach targetów: fituje model per kolumna, liczy MAE per kolumnę, uśrednia. Kod realizuje per-origin fit: pętla `for w in windows:` z `train_cols_w` fituje modele na własnym oknie przeszłości każdego originu (linie 438–443 `bench.py`), więc fałszywa klauzula `not checked: per-origin fit` została usunięta z flagi. Zsynchronizowano też dokumentację `AMR_24_168_H720_RESULT.md` z artefaktem `results/etth1_h720_amr24168_g4.json` (G4 FAIL, mean rank 6.1). `python -m py_compile bench.py` OK. Next: FEV multivariate end-to-end z wygenerowaniem `bench_fev_mini.json`.

not checked: FEV multivariate end-to-end (Windows multiprocessing w bibliotece fev; `bench_fev_mini.json` nie istnieje).
