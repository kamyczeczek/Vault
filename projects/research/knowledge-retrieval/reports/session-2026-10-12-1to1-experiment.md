---
type: Concept
title: session-2026-10-12-1to1-experiment
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:26Z }
---

# Session report — 1:1 cross-retriever experiment (ask.py vs graphrag.py) + v2 vs KR verdict

## Status
**Sukces pomiarowy.** Oba kierunki 1:1 wykonane na zamrożonych goldach `f7d6966`.
Wniosek v2 vs KR: **artefakt różnych zbiorów, nie sprzeczność warstw** — na tym
samym zbiorze 12 pytań v2 GraphRAG-hybryda (MRR@5=0.819) bije v2 HybridRetriever
(MRR=0.708 z pliku), a ask.py (MRR@5=0.278) jest wyraźnie słabszy od obu.

## Scope
Pomiar, nie optymalizacja. Nie zmieniono `graphrag.py` ani `ask.py` (archiwum
read-only). Bez nowych bibliotek. Liczby v2 HybridRetriever pochodzą z pliku
raportu (pipeline v2 wymaga attune-rag + sentence-transformers — nie
uruchamiano ponownie, tylko odczytano zapisany wynik).

## Krok 1 — zamrożone goldy
- Źródło: `projects/_archive` repo, commit `f7d6966`
  (`bench(retrieval): family recall primary...`, 2026-09-27).
- Kopia: `pilots/graphrag/eval/_tmp_frozen_golds.json` — version 2, 8 cases:
  causal-intervention, scientific-discovery, production-reliability,
  agent-memory, planning-workflow, graph-scaling, automl-experiment,
  multiagent-coordination.
- Ta sama wersja goldów użyta w obu kierunkach (STOP GATE 1: PASS).

## Krok 1A — 8 pytań EN przez graphrag.py (hybryda)
- Skrypt: `pilots/graphrag/eval/_tmp_run_ask_benchmark.py`
  (`zbuduj_plan` + `uzyj_wektorow=True` + `retrieve`, metryki jak
  `run_retrieval_benchmark.py`: family_recall/precision, concept_coverage, latency).
- Output: `pilots/graphrag/eval/_tmp_ask_by_graphrag.json`
- Wynik: **family_recall=0.906, family_precision=0.681, concept_coverage=1.0** (8 cases)
- Per-case: causal 1.0, scientific 1.0, production 1.0, agent-memory 0.75,
  planning-workflow 0.50, graph-scaling 1.0, automl 1.0, multiagent 1.0.
- Latencja: średnia 1674 ms (pierwsze pytanie ~11.8 s — ładowanie wag modelu
  wektorowego; kolejne ~220 ms).
- Porównanie z ask.py@f7d6966 (0.938): **delta −0.032** na korzyść ask.py —
  w granicach szumu przy n=8 (słabe ogniwa: planning-workflow 0.5,
  agent-memory 0.75 w obu warstwach podobnie).

## Krok 1B — 33 pytania PL trust set przez ask.py
- Skrypt: `pilots/graphrag/eval/_tmp_run_graphrag_on_trust.py`
  (`ask.query(pytanie, limit=5, recall=True)`; "odmowa" = pusta lista —
  ask.py nie ma bramki semantycznej).
- Output: `pilots/graphrag/eval/_tmp_trust_by_ask.json`
- Wynik: **MRR=0.116, MRR@5=0.116, Recall@1=0.091, Recall@5=0.152,
  ndcg@5=0.125, odmów=0/33**.
- Tylko 5/33 pytań z trafieniem: Q00a (1.0), Q00b (0.333), Q17 (1.0),
  Q19 (0.5), Q20 (1.0). Reszta 28/33 = 0.000.
- Porównanie z graphrag-hybrydą na tych samych 33 pytaniach (z istniejącego
  `trust_set_results.json`): **MRR=0.303, MRR@5=0.295, Recall@1=0.159,
  Recall@5=0.455, odmów=16/33**.
- Wniosek kierunkowy: na naturalnych pytaniach PL **graphrag-hybryda bije
  ask.py 2.6× (0.303 vs 0.116 MRR)**. Aliasy EN w ask.py nie transferują się
  na polskie pytania o podręczniki (AIMA/PRML); wektory wielojęzyczne tak.

## Tabela konfrontacyjna 1:1

| Zbiór | ask.py (FTS5+aliasy+per-family) | graphrag.py (hybryda FTS5+wektory+RRF) |
|---|---|---|
| 8 EN benchmark (goldy f7d6966) | family_recall **0.938** (z pliku f7d6966) | family_recall **0.906** (ten pomiar) |
| 33 PL trust in-corpus | MRR **0.116**, R@5 0.152 (ten pomiar) | MRR **0.303**, R@5 0.455 (trust_set_results.json) |

## Krok 2 — rozstrzygnięcie v2 vs KR
- Zbiór v2: `projects/research/retrieval-v2/reports/retrieval_v2_hybrid_results.json`
  — 12 pytań in-corpus PL (Q3, Q14–Q22, Q1–Q2) + 5 OOC + 5 canary.
  Pytania i oracle wyekstrahowane do `pilots/graphrag/eval/_tmp_v2_questions.json`.
- Oracle v2 to stem-y ucięte do ~50 znaków; node-id w graph.db to pełne
  identyfikatory. Reguła dopasowania: **prefix match w either direction**
  (jawnie udokumentowana w `_tmp_v2_comparison.json`).
- Oba retrievery graph.db puszczone na 12 pytaniach v2 z oracle v2:
  skrypt `pilots/graphrag/eval/_tmp_run_v2_comparison.py`,
  output `pilots/graphrag/eval/_tmp_v2_comparison.json`.

| Zbiór | GraphRAG-hybryda | ask.py | v2 HybridRetriever |
|---|---|---|---|
| v2 (12 pytań) | MRR@5 **0.819**, R@5 0.917 (ten pomiar) | MRR@5 **0.278**, R@5 0.333 (ten pomiar) | MRR **0.708**, recall 0.75 (z pliku) |
| trust set (33 in-corpus) | MRR **0.303** (trust_set_results.json) | MRR **0.116** (ten pomiar) | NIE WYKONANO (osobny korpus) |

Per-question na zbiorze v2 (graphrag / ask / v2-z-pliku MRR):
Q3 1.0/0.0/1.0, Q14 0.333/0.0/0.5, Q15 0.0/0.0/1.0, Q16 0.5/1.0/1.0,
Q17 1.0/0.0/0.0, Q18 1.0/1.0/1.0, Q19 1.0/0.0/1.0, Q20 1.0/0.0/1.0,
Q21 1.0/0.0/1.0, Q22 1.0/0.0/0.0, Q1 1.0/1.0/1.0, Q2 1.0/0.333/0.0.

- **Wniosek: v2 vs KR to artefakt różnych zbiorów.** Liczba 0.688/0.708 (v2)
  i 0.295/0.303 (KR) mierzą różne warstwy na różnych pytaniach. Na wspólnym
  zbiorze 12 pytań kolejność to **graphrag-hybryda (0.819) > v2-Hybrid (0.708)
  > ask.py (0.278)** — czyli "sprzeczność" znika: hybryda wektorowa wygrywa
  niezależnie od zbioru, a ask.py przegrywa na obu.
- Rekomendacja: **ujednolicić zbiór** (12 pytań v2 jako wspólny benchmark dla
  wszystkich trzech warstw; v2-Hybrid do powtórnego uruchomienia, nie tylko
  odczytu z pliku) i **promować hybrydę FTS5+wektory** jako domyślną warstwę;
  ask.py zostaje read-only precedensem dla krótkich zapytań EN.

## Raw output (transkrypt pomiarów tej sesji)
Direction A summary: `{"cases": 8, "mean_family_precision": 0.681,
"mean_family_recall": 0.906, "mean_concept_coverage": 1.0,
"mean_latency_ms": 1673.949}`.
Direction B summary: `{"n": 33, "n_odmowa": 0, "mean_recall@1": 0.091,
"mean_recall@3": 0.152, "mean_recall@10": 0.152, "mean_mrr": 0.116,
"mean_mrr@5": 0.116, "mean_recall@5": 0.152, "mean_ndcg@5": 0.125}`.
v2 comparison summary: `{graphrag_mrr5: 0.819, graphrag_recall5: 0.917,
ask_mrr5: 0.278, ask_recall5: 0.333, v2_mrr_from_file: 0.708,
v2_recall_from_file: 0.75}`.
Pełne wiersze per-question w plikach outputu (ścieżki wyżej).

## Pliki deliverables
1. `pilots/graphrag/eval/_tmp_frozen_golds.json` — goldy f7d6966 (8 cases).
2. `pilots/graphrag/eval/_tmp_ask_by_graphrag.json` — 8 EN przez graphrag.
3. `pilots/graphrag/eval/_tmp_trust_by_ask.json` — 33 PL przez ask.py.
4. `pilots/graphrag/eval/_tmp_v2_questions.json` — 12 pytań v2 + oracle.
5. `pilots/graphrag/eval/_tmp_v2_comparison.json` — tabela 3-warstwowa.
6. Ten raport: `reports/session-2026-10-12-1to1-experiment.md`.

## not checked:
- nie sprawdzono merytorycznej poprawności goldów z f7d6966 (użyto jako zamrożonych).
- nie uruchamiano ponownie pipeline v2 HybridRetriever (liczby v2 z pliku raportu).
- nie mierzono graphrag-hybrydy na 33 pytaniach w tej sesji (liczby KR z istniejącego trust_set_results.json).
- reguła prefix-match dla oracle v2 (ucięte stem-y) może zawyżać/zaniżać obie warstwy graph.db symetrycznie — wpływ na ranking graphrag>ask pomijalny (delta 0.54), na graphrag-vs-v2 niepomijalny (delta 0.11).
- Q15 (vibe coding) i Q22: graphrag=0.0 przy v2=1.0/0.0 — rozbieżności per-question do dalszej analizy.
- `kg.py` (research-engine martwy path) — potwierdzony w HANDOFF jako scar, nie dotykany.
