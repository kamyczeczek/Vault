---
flag: arl-transfer-pivot
since: 2026-10-08
owner: mateusz
agent: opencode
model: muse-spark-1.3-contributor-free
origin: user steering decision 2026-10-08 (follows notebook runs sens-arl answer + answer2)
---

`arl-transfer-pivot` — 2026-10-08: ARL przekształcony z projektu badawczego
"czy agent z grafem jest lepszy" w laboratorium walidacji przenośnych rozwiązań
workspace. Hipoteza B zostaje jako tania bramka zamykająca (re-scoring `perf`
przy 8000 znaków; brak wzrostu 0.083 -> >=0.400 zamyka B, anuluje n>=25).
Główny produkt: katalog transferowy 4 wzorców (ICM L0-L4 + flagi; gate'y
mutacyjne via core.hooksPath; D5/ADR-0003; regex + echo-guard). Zamrożone:
korpus/graf, n>=25 do sygnału z perf. Zabite: embeddings, MCP-autonomia,
syntetyczny meta-learning, guardraile na trywialnych zadaniach, phase2c.
Next: sesja ARL w ralph-loop (wayfinder, spans root+projekty) tworzy TRANSFER.md
w ARL + odpala tani test perf; potem Faza 1 ekstrakcja (adaptery+testy
akceptacyjne), Faza 2 pilot w 1 projekcie-kandydacie (NIE root), Faza 3 promocja
do roota z ADR+rollbackiem. Gate'y: A perf-8000, B ralph reviewer-vs-bramka
(3 iteracje, false-SHIP), C pamięć sesji (hook debug.py po 2. failu, check po
10 sesjach), D transfer (brak poprawy cold-start/handoff => brak promocji).
Ewidencja: `handoff/notebook-runs/2026-10-08-sens-arl/` (problem, answer, answer2).
