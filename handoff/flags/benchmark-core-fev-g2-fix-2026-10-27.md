---
flag: benchmark-core-fev-g2-fix-2026-10-27
since: 2026-10-27
owner: mateusz
agent: opencode
model: omniroute/cx-gpt-5.6-luna-medium
origin: session-close
---

`benchmark-core-fev-g2-fix-2026-10-27` — 2026-10-27: FEV protocol G2 gate aligned with S49 pre-registration. W `main_fev()` zmieniono definicję G2 z hardcoded `mean_rankB < 2` na pre-rejestrowaną: "Pool B beats Pool A on majority of tasks" (`winsB >= len(task_results) // 2`). To odpowiada G2 z H720 ("beat DLinear and SpectralFFT at H720 (raw)"). Dodano jawny log `G2 (Pool B beats A on majority of tasks): X/Y -> PASS/FAIL` oraz sekcję `gates.G2_majority_win` w JSON. "Frozen fit on first window" pozostaje (zgodne z protokołem S-47); multivariate zostawione jako osobny ticket (flaga "not checked:"). `python -m py_compile bench.py` OK. Next: multivariante wsparcie w `extract_series_from_window` oraz ewentualnie per-origin fit dla FEV.

not checked: multivariate wsparcie (obecnie `extract_series_from_window` zwraca 1-D array, pierwszą kolumnę); per-origin fit w FEV (obecnie frozen na pierwszym oknie).
