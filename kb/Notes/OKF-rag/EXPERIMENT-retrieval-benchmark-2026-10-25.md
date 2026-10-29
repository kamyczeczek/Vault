---
type: report
title: Benchmark retrieval — 15 pytań z oczekiwanym źródłem
description: Test rankingu Smart Connections po dodaniu warstwy syntez i decyzji nad surowymi materiałami OKF-rag.
status: draft
tags: [experiment, benchmark, retrieval, smart-connections, okf]
sources:
  - EXPERIMENT-retrieval-2026-10-25.md
  - SYNTHESIS.md
  - SYNTHESIS-kompilacja-i-wyszukiwanie.md
  - DECISION-minimalny-przeplyw-wiedzy.md
generated:
  by: codex
  at: 2026-10-25T00:00:00Z
---

# Cel

Sprawdzić, czy Smart Connections potrafi znaleźć oryginalny materiał źródłowy
dla pytań dotyczących `Notes/OKF-rag`, gdy w tym samym folderze istnieją już
krótkie syntezy, decyzje i raport eksperymentalny.

# Metoda

- 15 pytań napisanych w języku naturalnym.
- Dla każdego pytania wskazano jeden oczekiwany plik źródłowy (gold file).
- Smart Connections: zakres `Notes/OKF-rag`, `top 10`, `scope=auto`,
  `min_score=0.55`.
- Warstwa kuratorska: `SYNTHESIS.md`,
  `SYNTHESIS-kompilacja-i-wyszukiwanie.md`,
  `DECISION-minimalny-przeplyw-wiedzy.md` i raporty `EXPERIMENT-*`.
- Rank oznacza pozycję oczekiwanego pliku wśród 10 wyników note-level.

# Wyniki

| ID | Oczekiwane źródło | Najlepszy wynik | Score | Rank źródła |
|---|---|---|---:|---:|
| Q01 | `ontoship.md` | `DECISION-minimalny-przeplyw-wiedzy.md` | 0.7448 | 6 |
| Q02 | `SPEC.md` | `SYNTHESIS.md` | 0.8199 | — |
| Q03 | `SPEC.md` | `SYNTHESIS.md` | 0.7615 | 7 |
| Q04 | `okf-rag.md` | `SYNTHESIS-kompilacja-i-wyszukiwanie.md` | 0.7531 | — |
| Q05 | `okf-rag.md` | `SYNTHESIS.md` | 0.7834 | 7 |
| Q06 | `okf-rag.md` | `SYNTHESIS-kompilacja-i-wyszukiwanie.md` | 0.7854 | 9 |
| Q07 | `llm-wiki.md` | `SYNTHESIS.md` | 0.7575 | 7 |
| Q08 | `llm-wiki.md` | `SYNTHESIS-kompilacja-i-wyszukiwanie.md` | 0.7370 | 8 |
| Q09 | `napkin.md` | `SYNTHESIS-kompilacja-i-wyszukiwanie.md` | 0.7488 | — |
| Q10 | `napkin.md` | `SYNTHESIS.md` | 0.7581 | — |
| Q11 | `ontoship.md` | `SYNTHESIS.md` | 0.7663 | 7 |
| Q12 | `ontoship.md` | `SYNTHESIS.md` | 0.7706 | 6 |
| Q13 | `okforge.md` | `SYNTHESIS.md` | 0.7716 | 7 |
| Q14 | `okforge.md` | `DECISION-minimalny-przeplyw-wiedzy.md` | 0.7710 | 6 |
| Q15 | `okf-rag.md` | `SYNTHESIS-kompilacja-i-wyszukiwanie.md` | 0.8219 | 8 |

# Metryki

- Kuratorowana synteza lub decyzja była top-1 w **15/15** przypadkach.
- Oczekiwane źródło było w top-5 w **0/15** przypadkach.
- Oczekiwane źródło było w top-10 w **11/15** przypadkach.
- Średni rank oczekiwanego źródła, gdy wystąpiło w top-10: **7,1**.
- Score najlepszego wyniku kuratorskiego mieścił się w zakresie **0,7370–0,8219**.

# Interpretacja

To nie jest porażka wyszukiwania. Indeks bardzo konsekwentnie preferuje nową
warstwę kuratorską, ponieważ syntezy i decyzje używają języka pytań oraz zbierają
wnioski z wielu plików. Dla użytkownika pytającego „co z tego wynika?” jest to
pożądane zachowanie.

Jest to jednak słaby wynik dla zadania „pokaż mi oryginalny dowód”. Cztery
oczekiwane źródła nie trafiły nawet do top-10, a żadne nie trafiło do top-5.
Benchmark jest częściowo kolisty: pytania zostały zbudowane na podstawie
wcześniejszej syntezy, a synteza jest już w indeksie.

# Wniosek

Najlepszym obecnie przepływem jest retrieval dwuetapowy:

```text
pytanie
    → Smart Connections znajduje syntezę lub decyzję-hub
    → hub wskazuje źródła
    → człowiek/agent czyta właściwy fragment źródła
```

Nie należy wymagać od jednego rankingu, aby jednocześnie wybierał najlepszy
koncept i najlepszy dowód pierwotny.

# Decyzja pośrednia

Utrzymujemy syntezy i decyzje jako warstwę nawigacyjną, ale każda istotna teza
ma prowadzić do pliku źródłowego. Do pytań o dokładne szczegóły używamy drugiego
kroku: odczytu wskazanego źródła lub wyszukiwania tekstowego w znanym pliku.

# Ograniczenia

- Gold file został wybrany ręcznie i nie ma jeszcze gold passage/line range.
- Zestaw 15 pytań jest mały i celowo dotyczy jednego folderu.
- Nie porównano jeszcze uczciwie z BM25/FTS5 na identycznym zestawie pytań.
- Wynik zależy od aktualnego indeksu i modelu `TaylorAI/bge-micro-v2`.

# Następny krok

Zamiast zwiększać liczbę narzędzi, dodać do każdej syntezy precyzyjne linki do
źródeł i sekcji, a następnie powtórzyć test na 20 pytaniach z oczekiwanym
plikiem oraz fragmentem źródłowym. Dopiero brakujące trafienia na poziomie
fragmentów uzasadnią zmianę indeksu lub pipeline'u.
