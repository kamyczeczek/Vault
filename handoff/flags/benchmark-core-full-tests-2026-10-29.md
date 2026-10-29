---
flag: benchmark-core-full-tests-2026-10-29
since: 2026-10-29
owner: mateusz
agent: opencode
model: omniroute/agy/claude-opus-4-6-thinking
---

`benchmark-core-full-tests-2026-10-29` — 2026-10-29: pełny suite benchmark-core przeszedł 24/24.

Stan:
- `python.exe -m pytest -v projects/research/benchmark-core/` — **24 passed, 1 warning, 540.88s (9:00)**. Jedyny warning: statsmodels SARIMAX `Non-invertible starting MA parameters found` — kosmetyczny, nie wpływa na wynik.
- Poprzednio (flaga `cleanup-red-tests-2026-10-29`) uruchomiono tylko collect + import smoketest z powodu timeoutu >5 min. Pełne uruchomienie potwierdza, że fix martwego importu `fit_amr` w `sunspot_methods.py` nie złamał żadnego testu trenującego modele.
- Pliki testowe: `test_benchmark_protocol` (6), `test_chaos_protocol` (2), `test_lasso` (1), `test_sunspot_eval` (3), `test_sunspot_longterm` (2), `test_thomas` (5), `test_thomas_compare` (2), `test_thomas_forecasts` (2), `test_thomas_methods` (1).

Weryfikacja:
- pytest 24 passed (pełne uruchomienie z trenowaniem modeli).
- `check_workspace_integrity` — exit 0.
- `git diff --check` — exit 0.

not checked: FEV 100-task `tasks.yaml` run (osobny punkt); push do remote (wykonany w tej sesji dla wcześniejszych commitów).
