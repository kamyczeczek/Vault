---
type: report
title: Benchmark retrieval — plik i fragment źródłowy
description: Dwudziestopytaniowy test Smart Connections po dodaniu precyzyjnych wskazań plików i zakresów źródłowych.
status: draft
tags: [experiment, benchmark, retrieval, passages, smart-connections]
sources:
  - { file: EXPERIMENT-retrieval-benchmark-2026-10-25.md, lines: "34-87" }
  - { file: SYNTHESIS.md, lines: "126-154" }
  - { file: SYNTHESIS-kompilacja-i-wyszukiwanie.md, lines: "87-118" }
generated:
  by: codex
  at: 2026-10-25T00:00:00Z
---

# Cel

Sprawdzić nie tylko, czy retrieval znajduje właściwy plik, ale czy trafia w
fragment, z którego rzeczywiście wynika odpowiedź. Test wykonano po dodaniu do
syntez wskazań typu „plik + zakres linii”.

# Metoda

- 20 pytań w języku naturalnym.
- Każde pytanie ma ręcznie wybrany `gold file` i zakres fragmentu.
- Smart Connections: folder `Notes/OKF-rag`, `scope=blocks`, `top 10`,
  `min_score=0.55`, model `TaylorAI/bge-micro-v2`.
- „Rank pliku” oznacza pozycję oczekiwanego pliku w top 10.
- „Passage” jest `exact`, jeśli zwrócony blok mieści się w oczekiwanym
  zakresie; `related`, jeśli trafia do właściwej większej sekcji; w pozostałych
  przypadkach wynik nie jest zaliczany jako dowód.

# Gold set i wyniki

| ID | Gold file | Oczekiwany fragment | Rank pliku | Zwrócony fragment | Passage |
|---|---|---|---:|---|---|
| Q01 | `ontoship.md` | README / The idea, 89–103 | 6 | search helper, 2848–2919 | — |
| Q02 | `SPEC.md` | Frontmatter, 167–214 | 8 | Lifecycle/status, 418–429 | — |
| Q03 | `SPEC.md` | Provenance/trust/lifecycle, 283–430 | 6 | Trust, 372–406 | related |
| Q04 | `SPEC.md` | Cross-linking and paths, 443–495 | 8 | Lifecycle/status, 418–429 | — |
| Q05 | `SPEC.md` | Index files, 511–538 | 4 | Index files, 513–538 | exact |
| Q06 | `okf-rag.md` | Generate OKF, 445–466 | — | — | — |
| Q07 | `okf-rag.md` | Proposal-to-truth, 445–466 | — | — | — |
| Q08 | `okf-rag.md` | Architecture, 231–260 | — | — | — |
| Q09 | `okf-rag.md` | Benchmark, 573–601 / 1005–1056 | — | — | — |
| Q10 | `okf-rag.md` | Findings, 1134–1140 | — | — | — |
| Q11 | `llm-wiki.md` | What llmwiki does, 54–78 | 8 | template section, 101–155 | — |
| Q12 | `llm-wiki.md` | When to use this repo, 59–64 | 8 | provider config, 160–462 | — |
| Q13 | `llm-wiki.md` | Review/freshness, 75–78 | 9 | template section, 101–155 | — |
| Q14 | `napkin.md` | Distill, 3774–3900 | — | — | — |
| Q15 | `napkin.md` | Tend, 3916–3983 | — | — | — |
| Q16 | `napkin.md` | Progressive disclosure, 3094–3144 | — | — | — |
| Q17 | `okforge.md` | Add pipeline, 760–790 | — | — | — |
| Q18 | `okforge.md` | Recompile, 4715–4748 | — | — | — |
| Q19 | `ontoship.md` | Decisions/benchmark, 985–1062 | 7 | scoring helper, 3355–3361 | — |
| Q20 | `okf-generator.md` | Incremental updates, 71–84 | 7 | training pair types, 224–230 | — |

# Metryki

- Gold file w top-1: **0/20**.
- Gold file w top-5: **1/20**.
- Gold file w top-10: **10/20**.
- Gold passage exact: **1/20**.
- Gold passage exact lub related: **2/20**.
- Top-1 był zawsze warstwą pochodną, kuratorską albo indeksem; żaden top-1 nie
  był bezpośrednim źródłem pierwotnym.

# Interpretacja

Dodanie precyzyjnych wskazań plików i zakresów linii poprawia audytowalność
notatek, ale nie zmienia zachowania rankera: Smart Connections nadal preferuje
syntezy i decyzje, które opisują sens pytań. To jest dobre dla nawigacji po
wiedzy, lecz niewystarczające jako automatyczny system dowodowy.

Duże importy są dodatkowo trudne dla wyszukiwania blokowego. Gdy wynik wskazuje
plik, często trafia do niewłaściwego fragmentu lub do bloku pomocniczego
oddalonego od właściwej sekcji. Nie należy uznawać samego trafienia pliku za
potwierdzenie tezy.

# Wniosek

Najbardziej wiarygodny obecnie przepływ jest dwuetapowy:

```text
pytanie
    → synteza/decyzja jako hub
    → precyzyjny link do źródła i zakresu
    → ręczny lub agentowy odczyt fragmentu
```

Warstwa kuratorska nie jest błędem rankera — pełni rolę mapy. Natomiast źródło
trzeba otworzyć osobno, gdy odpowiedź ma być cytowalna lub prowadzić do decyzji.

# Decyzja pośrednia

Nie uruchamiamy jeszcze pełnego pipeline'u OKF-RAG ani nie przebudowujemy całego
indeksu. Utrzymujemy krótkie syntezy z linkami do plików i zakresów, a dla
pytań wymagających dowodu stosujemy drugi krok odczytu źródła.

# Następny krok

Jeśli potrzebny będzie automatyczny passage recall, utworzyć osobny, surowy
benchmark lub indeks bez plików `SYNTHESIS*`, `DECISION*` i `EXPERIMENT*`.
Dopiero wynik takiego testu rozstrzygnie, czy problemem jest konfiguracja
Smart Connections, segmentacja dużych importów, czy potrzeba osobnego indeksu
źródłowego.
