---
type: Concept
flag: benchmark-core-fev-honest-2026-10-26
since: 2026-10-26
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
title: benchmark-core-fev-honest-2026-10-26
generated: { by: okf-enforcer/0.6, at: 2026-10-26T21:01:17Z }
---

`benchmark-core-fev-honest-2026-10-26` — 2026-10-26: `bench.py --fev` przestało kłamać (nested commits `726daa6` kod + testy, `e54644d` MAP.md; tylko `bench.py` + `test_benchmark_protocol.py` — 36 wcześniejszych brudnych wpisów w `benchmark-core` **nie** ruszono). Martwe URL-e były prawdziwe: `benchmarks/fev_bench.yaml` i `fev_bench_mini.yaml` → 404; właściwe to `benchmarks/fev_bench/tasks.yaml` i `.../tasks_mini.yaml`, sprawdzone 200, a `Benchmark.from_yaml` ładuje 20 zadań i przechodzi probe. `--fev` domyślnie **failuje zamknięciem** (exit 2, zero artefaktów); `--allow-synthetic-fallback` to jawny opt-in. Każdy wynik niesie `data_source` (`real` / `synthetic_fallback` / `builtin_suite`) i `confirmatory` (true tylko dla real); fallback jest stemplowany `synthetic_fallback` / `false`, zapisuje `fev_attempt` i ląduje w `bench_synthetic_fallback.json` — nigdy w `results_s47.json`, który wcześniej nadpisywał. `test_benchmark_protocol.py` 6/6.
Next: protokół FEV — zadania, metryki, sposób raportowania — i pierwszy run na realnych danych, z commitem artefaktu. To jedyna ścieżka, która może cokolwiek promować; S-47 zostaje sondą.
not checked: `main_fev()` nadal liczy werdykt starym hardcoded `mean_rankB < 2` zamiast definicji G2 z pre-rejestracji, dopasowuje raz na pierwszym oknie i ignoruje multivariate. To należy do protokołu FEV, nie do tej poprawki.
