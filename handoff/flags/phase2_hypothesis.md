---
type: Concept
flag: phase2_hypothesis
since: 2026-10-04
owner: mateusz
agent: opencode
model: muse-spark
title: phase2_hypothesis
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

2026-10-04: Hipoteza Phase 2 deep-research (KG + ICM):

**Hipoteza:** B — agent z dostępem do grafu (`ask.py` + `route.py`) podejmuje
lepiej ugruntowane decyzje (grounding, mniej halucynacji) na zadaniach
wymagających cytowania niż agent bez grafu.

**Metryki:** (1) citation resolve rate — odsetek cytowań `Chunk id: NN_slug`
rozwiązywalnych w żywym grafie (`check_citation_integrity.py`, deterministyczne),
**mierzone tylko na zadaniach z ≥3 cytowaniami** (inaczej agent może "wygrać"
przez unikanie cytowań — 0/0 = 1.0 trywialnie); (2) citation concentration —
udział top-3 chunków we wszystkich cytowaniach (`project-entropy.jsonl`, cel:
spadek ze 100%), **definicja: concentration = (liczba cytowań do top-3 chunków)
/ (liczba wszystkich cytowań); zadanie z 0 cytowań jest wykluczone z metryki
(nie liczone jako 0), a liczba wykluczonych zadań jest raportowana osobno**
(2026-10-04, decyzja właściciela: wariant A z fallbackiem — inaczej „poprawa"
przez unikanie cytowań wraca tylnymi drzwiami); (3) dead-route rate — odsetek
zapytań kończących się rc=2 / `dead:true` (po `85c3318` mierzalne fail-closed).
Wszystkie bez LLM-sędziego.

**Baseline:** ten sam agent, te same zadania (bug-fix / feature / perf z §Faza 2
deep note), ramię OFF bez dostępu do grafu vs ramię ON z `ask.py` + `route.py`.

**Kryterium sukcesu:** ON wygrywa na resolve rate + concentration przy
niepogorszonym dead-route rate na ≥2 z 3 rodzin zadań.

**Kryterium porażki:** brak różnicy na resolve rate / concentration albo
poprawa tylko na dead-route rate (to byłby efekt monitora, nie grafu), **albo
wzrost resolve rate przy jednoczesnym spadku liczby cytowań na zadanie**
(dowód unikania, nie poprawy) —
wtedy graf nie pomaga, a Phase 4-diversity przejmuje priorytet.

Next: zaprojektowanie i uruchomienie eksperymentu Phase 2 jako osobna sesja
(benchmark zadań + harness ablacji, pre-rejestracja jak `forge_ab_design`).
