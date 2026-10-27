# Learnings

Append-only. One line per learning, most recent last:

- 2026-10-08 perf ON 8000 avg = 0.0 vs baseline 0.083 → hipoteza B ZAMKNIĘTA jako negatywna/nierozstrzygnięta. Anuluj plan n≥25. Idź w transfer. Uwaga metodologiczna: wynik 0.0 < baseline 0.083 to spadek, nie tylko brak wzrostu. Prawdopodobne przyczyny: (1) wariancja pojedynczej próbki (n=1 na zadanie, brak seeda LLM), (2) regex criterion wrażliwy na słownictwo (model parafrazował, nie powtarzał słowa „HippoRAG"). Wniosek o zamknięciu B pozostaje, ale 0.0 nie jest silniejszym dowodem niż brak wzrostu — to artefakt składni. (3 zadania perf-*: perf-ppr 0.0, perf-costinversion 0.0, perf-queryexpand 0.0; wynik zapisany w scripts/_scratch/perf_8k/verdict.json)
- <date> <pattern, gotcha, or discovered convention for this project>

Promotion is a human gate at DONE: copy the load-bearing entries into the
project's `AGENTS.md` or `CONTEXT.md` so the next session (agent or human)
inherits them. A loop that does not promote learnings re-discovers them every
run.
