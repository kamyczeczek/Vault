---
type: report
title: Control raw-only — retrieval bez warstwy kuratorskiej
description: Kontrolny ranking tych samych 20 pytań po odfiltrowaniu syntez, decyzji, raportów i indeksu.
status: draft
tags: [experiment, benchmark, retrieval, raw-corpus, smart-connections]
sources:
  - EXPERIMENT-retrieval-benchmark-20-2026-10-25.md
  - SYNTHESIS.md
  - SYNTHESIS-kompilacja-i-wyszukiwanie.md
generated:
  by: codex
  at: 2026-10-25T00:00:00Z
---

# Cel

Oddzielić dwa pytania:

1. Czy Smart Connections dobrze znajduje kuratorowaną syntezę?
2. Czy potrafi znaleźć bezpośrednio oryginalny materiał?

W tym teście usunięto z rankingu warstwę pochodną, aby zobaczyć zachowanie na
samych materiałach źródłowych.

# Metoda

Użyto tego samego gold setu 20 pytań co w
[benchmarku blokowym](EXPERIMENT-retrieval-benchmark-20-2026-10-25.md).
Smart Connections zwróciło do 100 bloków z `Notes/OKF-rag`, a następnie z
rankingu usunięto:

- `index.md`;
- `SYNTHESIS*.md`;
- `DECISION-*.md`;
- `EXPERIMENT-*.md`.

To jest filtr ewaluacyjny po wyszukaniu, a nie natywne ograniczenie pluginu.
Parametry: `scope=blocks`, `min_score=0.55`, model `TaylorAI/bge-micro-v2`.

# Wyniki

| ID | Oczekiwany plik | Raw-only rank | Score |
|---|---|---:|---:|
| Q01 | `ontoship.md` | 1 | 0.6488 |
| Q02 | `SPEC.md` | 2 | 0.5983 |
| Q03 | `SPEC.md` | 1 | 0.6354 |
| Q04 | `SPEC.md` | 2 | 0.6689 |
| Q05 | `SPEC.md` | 1 | 0.7331 |
| Q06 | `okf-rag.md` | — | — |
| Q07 | `okf-rag.md` | — | — |
| Q08 | `okf-rag.md` | — | — |
| Q09 | `okf-rag.md` | — | — |
| Q10 | `okf-rag.md` | — | — |
| Q11 | `llm-wiki.md` | 2 | 0.6811 |
| Q12 | `llm-wiki.md` | 2 | 0.5628 |
| Q13 | `llm-wiki.md` | 3 | 0.5664 |
| Q14 | `napkin.md` | — | — |
| Q15 | `napkin.md` | — | — |
| Q16 | `napkin.md` | — | — |
| Q17 | `okforge.md` | — | — |
| Q18 | `okforge.md` | — | — |
| Q19 | `ontoship.md` | 1 | 0.6419 |
| Q20 | `okf-generator.md` | 1 | 0.7139 |

# Metryki raw-only

- top-1: **5/20**;
- top-5: **10/20**;
- top-10: **10/20**;
- średni rank dla znalezionych źródeł: **1,6**;
- znaleziony plik źródłowy: **10/20**.

# Porównanie z rankingiem mieszanym

| Ranking | top-1 | top-5 | top-10 |
|---|---:|---:|---:|
| Wszystkie notatki razem | 0/20 | 1/20 | 10/20 |
| Po odfiltrowaniu warstwy kuratorskiej | 5/20 | 10/20 | 10/20 |

Warstwa kuratorska zabiera miejsca w top-5, ale jednocześnie daje użytkownikowi
lepszy punkt wejścia do pytania. Raw-only poprawia bezpośrednie trafienie w
źródło, lecz nadal nie znajduje połowy oczekiwanych plików powyżej progu `0.55`.

# Wniosek

Nie ma jednego najlepszego indeksu dla obu zadań. Warto utrzymać dwa tryby pracy:

- **nawigacja po sensie** — syntezy i decyzje jako huby;
- **weryfikacja dowodu** — raw-only search, dokładne wyszukiwanie tekstowe lub
  odczyt wskazanego zakresu linii.

To potwierdza decyzję o retrieval dwuetapowym, ale nie uzasadnia jeszcze
instalowania pełnego OKF-RAG. Brakujące trafienia należy najpierw przeanalizować
jako problem segmentacji, nazewnictwa lub zbyt ogólnych pytań.

# Następny krok

Dla 10 pytań bez trafienia przeprowadzić ręczną kontrolę `rg` + odczyt gold
fragmentu i sprawdzić, czy problem leży w indeksie, czy w samym pytaniu. Dopiero
po tej kontroli można ocenić, czy potrzebna jest zmiana narzędzia.
