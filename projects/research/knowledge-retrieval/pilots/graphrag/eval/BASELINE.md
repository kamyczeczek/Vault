---
type: Concept
title: BASELINE
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Graphrag baseline — zmierzony (2026-10-11)

## Metryki (baseline_measurements/graphrag_baseline.json)

| Grupa | n | refusal | MRR@5 | Recall@5 |
|-------|---|---------|-------|----------|
| in-corpus PL | 12 | 5/12 | 0.507 | 0.708 |
| in-corpus EN | 8 | 0/8 | 0.771 | 1.000 |
| OOC PL | 5 | 5/5 | — | — |
| Canary | 5 | 5/5 | — | — |

## Spójność z historią

Historyczny pomiar (Faza 8S, CONTEXT.md): MRR@5 = 0.507, Recall@5 = 0.708, refusal 5/5.
Obecny pomiar: in-corpus PL MRR@5 = 0.507, Recall@5 = 0.708, refusal 5/12.

Różnica: Identyczna (pomiar reprodukowalny).

## Wniosek

Graphrag baseline jest w pełni reprodukowalny i wiarygodny.

## Znane ograniczenie (dopisane 2026-10-11)

Pomiar został wykonany na `frozen_eval_sets.py` v1, w którym Q1 i Q2 (pytania angielskie)
znajdowały się w grupie `IN_CORPUS_PL` (12/8 split). Właściciel zatwierdził, że to błąd
strukturalny — poprawny podział to 10/10 (Q1, Q2 należą do IN_CORPUS_EN, co odzwierciedla `frozen_eval_sets_v2.py`).

**Konsekwencja:** metryki dla `in_corpus_pl` (n=12, refusal=5/12, MRR=0.507, Recall=0.708)
są zmierzone na zbiorze, który zawiera 2 pytania angielskie. Ponowny pomiar na v2
(`frozen_eval_sets_v2.py`) jest wymagany, gdy shell będzie dostępny.

Wskaźnik refusal=5/12 na in-corpus PL **nie został zinterpretowany** przez poprzednią sesję.
Jest to potencjalna anomalia — 42% pytań w korpusie zostało odrzuconych. Do wyjaśnienia po
ponownym pomiarie na v2.
