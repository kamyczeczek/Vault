---
flag: graphrag-1to1-experiment-2026-10-12
since: 2026-10-12
owner: mateusz
agent: pi
model: muse-spark/muse-spark
origin: session-close
---

`graphrag-1to1-experiment-2026-10-12` — 2026-10-12: sukces pomiarowy. Zamrożono goldy f7d6966 (8 EN); graphrag-hybryda family_recall 0.906 vs ask.py 0.938 (delta w szumie n=8). Na 33 PL trust: ask.py MRR 0.116 vs graphrag 0.303 (2.6x). Na wspólnym zbiorze v2 (12 pytań): graphrag 0.819 > v2-Hybrid 0.708 (z pliku) > ask 0.278. Werdykt: v2 vs KR to artefakt różnych zbiorów, nie sprzeczność warstw; promować hybrydę FTS5+wektory, ask.py zostaje read-only precedensem. Commit projektu f0747d0. Raport: projects/research/knowledge-retrieval/reports/session-2026-10-12-1to1-experiment.md.

not checked: merytoryczna poprawność goldów f7d6966 (użyte jako zamrożone); pipeline v2 HybridRetriever nie uruchamiany ponownie (liczby z pliku); graphrag na 33 pytaniach z istniejącego trust_set_results.json (nie mierzony w tej sesji); reguła prefix-match dla oracle v2 (wpływ na graphrag-vs-v2 niepomijalny, delta 0.11); rozbieżności per-question Q15/Q22 do dalszej analizy.
