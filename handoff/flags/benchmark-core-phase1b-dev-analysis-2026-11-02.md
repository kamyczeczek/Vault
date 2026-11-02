---
flag: benchmark-core-phase1b-dev-analysis-2026-11-02
since: 2026-11-02
owner: mateusz
agent: opencode
model: omniroute/gemini/gemini-flash-lite-latest
origin: session-close
---

`benchmark-core-phase1b-dev-analysis-2026-11-02` — 2026-11-02: Faza 1b na Dev (suchy przebieg baselines: SeasonalNaive, NLinear, DLinear) zakończona i zweryfikowana.

Stan:
- Przebieg 20/20 zadań Dev (3 okna każde, total 1359.0 s) wykonany w pełni; 19 wspólnych zadań bit-identycznych z Run 1 (`compare_runs.py` OK).
- Czasy dopasowań i budżet: SeasonalNaive (11.1 s, mediana 0.015 ms), NLinear (233.5 s, mediana 10.9 ms, p95 144.2 ms), DLinear (712.2 s, mediana 35.9 ms, p95 478.5 ms). Wszystkie mieszczą się w budżecie 20 min/model.
- Skill score vs SNaive: NLinear +14.88% (dolne CI +3.75%, passes gate), DLinear +12.08% (dolne CI -0.63%).
- Analiza MDE i Bootstrap: Klaster bootstrap (B=10,000, 15 rodzin, alpha=0.05). MDE dla NLinear vs SNaive = 0.1781 (halfwidth 0.1114).
- Weryfikacja mianowników MASE: Zadania z MASE > 3 zweryfikowane — zero itemów z zerowym błędem.

Weryfikacja:
- python scripts/check_workspace_integrity.py → OK.
- git diff --cached --check → exit 0.

not checked: pełny lockbox (skażony A6); optymalizacja hiperparametrów NLinear/DLinear; przebieg testowy (quarantine/test partition).

Next step: Decyzja o przejściu do Fazy 2 (populacja startowa, dashboard) lub dalsze kroki badawcze.
