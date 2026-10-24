---
flag: graphrag-1to1-interpretation-2026-10-12
since: 2026-10-12
owner: mateusz
agent: opencode
model: gemini/gemini-flash-lite-latest
origin: session-close
---

`graphrag-1to1-interpretation-2026-10-12` — 2026-10-13: Domknięcie trzech luk interpretacyjnych eksperymentu 1:1. (1) Surowy output verify_report.py przeanalizowany i wykazano, że 4 discrepancies to fałszywe alarmy parsera nagłówków `##`. (2) Zbudowano tabelę dopasowań prefix-match dla 12 pytań v2 (10 exact matchów, 0 false positives, 2 misses), potwierdzając MRR@5=0.819. (3) Rozróżniono family-level (ask.py 0.938) vs exact-level (graphrag.py 0.303 / 0.819) i zarekomendowano hybrydę.
not checked: Ponowne uruchomienie ciężkiego pipeline'u v2 attune-rag + sentence-transformers (użyto zamrożonych artefaktów wynikowych).
