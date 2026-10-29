---
type: report
title: Kontrola brakujących trafień retrieval
description: Ręczna kontrola dziesięciu pytań, dla których raw-only Smart Connections nie znalazło oczekiwanego pliku powyżej progu.
status: complete
tags: [experiment, retrieval, diagnosis, source-corpus]
sources:
  - EXPERIMENT-retrieval-raw-only-2026-10-25.md
  - okf-rag.md
  - napkin.md
  - okforge.md
generated:
  by: codex
  at: 2026-10-25T00:00:00Z
---

# Cel

Sprawdzić, czy dziesięć brakujących trafień oznacza brak wiedzy w korpusie,
czy problem z rankingiem i segmentacją dużych importów.

# Kontrola ręczna

| ID | Oczekiwany materiał | Dowód znaleziony tekstowo | Diagnoza |
|---|---|---|---|
| Q06 | `okf-rag.md` | pipeline `Raw Markdown → llm-wiki → publish` jest opisany przy linii 447 | problem retrieval; treść istnieje |
| Q07 | `okf-rag.md` | `proposal-to-truth` przy linii 447 | problem retrieval; treść istnieje |
| Q08 | `okf-rag.md` | `End-to-End Knowledge Flow` 231–260 i `hybrid recall` przy 260 | problem retrieval; treść istnieje |
| Q09 | `okf-rag.md` | metryki Recall@1/5/10 i MRR przy 579–583 | problem retrieval; treść istnieje |
| Q10 | `okf-rag.md` | niedeterministyczna ekstrakcja i niepełny pruning przy 1139–1140 | problem retrieval; treść istnieje |
| Q14 | `napkin.md` | `Distill — Conversation to Vault` 3774, gate 3782, clustering 3804, merge/create 3831–3844 | problem retrieval; treść istnieje |
| Q15 | `napkin.md` | `Tend — Vault Upkeep` 3916, priorytety 3940–3952 | problem retrieval; treść istnieje |
| Q16 | `napkin.md` | `Agent Memory System — Progressive Disclosure` 3094–3141 | problem retrieval; treść istnieje |
| Q17 | `okforge.md` | pipeline `summary → concept plan → generate → index` 760–788 | problem retrieval; treść istnieje |
| Q18 | `okforge.md` | `recompile` 4718 i ostrzeżenie o nadpisywaniu przy 4730 | problem retrieval; treść istnieje |

# Wspólna cecha

Wszystkie trzy problematyczne pliki są dużymi, heterogenicznymi importami:

- `napkin.md`: około **680 kB**;
- `okf-rag.md`: około **2,4 MB**;
- `okforge.md`: około **2,2 MB**.

Każdy zawiera wiele dokumentów, README, kodu, testów i powtórzonych wersji
językowych. Dla człowieka `rg` znajduje właściwy fragment natychmiast, ale
semantyczny indeks może traktować cały import jako mieszaninę wielu tematów.

# Diagnoza

To nie jest brak wiedzy ani błąd w syntezach. Jest to ograniczenie obecnego
retrieval na dużych importach, najprawdopodobniej związane z jednym lub kilkoma
czynnikami:

- segmentacja bloków nie zachowuje wystarczająco precyzyjnych granic sekcji;
- wiele niepowiązanych tematów konkuruje w jednym pliku;
- pytanie semantyczne nie zawiera nazw własnych, które odróżniłyby sekcję od
  innych części importu;
- próg `0.55` odrzuca oczekiwany plik, gdy odpowiedni blok ma słaby wektor.

Pierwsze dwa punkty są hipotezami do sprawdzenia, nie zmierzonym wyjaśnieniem.

# Wniosek

Dwuwarstwowy przepływ jest uzasadniony:

1. synteza/decyzja prowadzi do właściwego tematu;
2. `rg` albo odczyt znanego zakresu linii potwierdza dowód w dużym imporcie.

Nie należy teraz przepisywać ani dzielić trzech dużych źródeł tylko po to, aby
poprawić jeden benchmark. Najpierw trzeba sprawdzić, czy ten sam problem
pojawia się w realnych pytaniach użytkownika.

# Następny eksperyment

Dla dziesięciu brakujących pytań porównać trzy warianty zapytania:

1. opis naturalny;
2. opis z nazwą pliku lub narzędzia (`okf-rag`, `napkin`, `okforge`);
3. dokładne słowa z nagłówka sekcji.

Jeśli wariant 3 odzyska źródła, problem dotyczy języka zapytania. Jeśli nie,
problem leży w segmentacji lub reprezentacji dużych importów.

# Eksperyment wariantów zapytań

## Metoda

Wykonano kontrolę dla Q06–Q10 w Smart Connections:

- folder: `Notes/OKF-rag`;
- zakres: `blocks`, `top 10`, `min_score=0.55`;
- warstwa kuratorska została odfiltrowana tak samo jak w teście raw-only;
- dla każdego pytania użyto trzech wariantów: opis naturalny, opis z nazwą
  pliku/narzędzia oraz dokładne słowa z nagłówka;
- oryginalne teksty pytań nie były zapisane w benchmarku, więc warianty są
  kontrolowaną rekonstrukcją na podstawie gold fragmentów. To test języka
  zapytania, nie nowy wynik benchmarku jakości odpowiedzi.

Indeks w chwili testu miał `443` notatki i `2393` bloki, przy `stale_notes=0`
i `stale_blocks=0`, z modelem `TaylorAI/bge-micro-v2`.

## Wynik rankingu

`—` oznacza, że `okf-rag.md` nie pojawił się w przefiltrowanym top-10.
W nawiasie podano top-1 i jego score.

| ID | Naturalne | Z nazwą | Dokładny nagłówek | `okf-rag.md` |
|---|---|---|---|---|
| Q06 | `okf-generator.md` (0.7957) | `SPEC.md` (0.7770) | `okf-generator.md` (0.8161) | `—` |
| Q07 | `SPEC.md` (0.6680) | `SPEC.md` (0.7533) | `SPEC.md` (0.6155) | `—` |
| Q08 | `ontoship.md` (0.7004) | `okf-generator.md` (0.7236) | `ontoship.md` (0.6779) | `—` |
| Q09 | `ontoship.md` (0.7118) | `ontoship.md` (0.6987) | `ontoship.md` (0.6610) | `—` |
| Q10 | `ontoship.md` (0.6548) | `okf-generator.md` (0.7227) | `ontoship.md` (0.6845) | `—` |

Wynik: `0/15` wariantów odzyskało oczekiwany duży import semantycznie.
Dodanie nazwy pliku ani użycie dokładnego nagłówka nie rozwiązało problemu.

## Rekordy kontraktu odpowiedzi

Wynik semantyczny ma tu status `unknown` dla źródła `okf-rag.md`, ponieważ
plik nie trafił do top-10. Druga warstwa tekstowa potwierdza jednak, że dowód
istnieje, więc finalny status evidence wynosi `direct`:

| ID | Źródło i lokalizator | Potwierdzony passage |
|---|---|---|
| Q06 | `okf-rag.md:445–447` | pipeline jest rozdzielony na propozycje kompilatora i decyzję reconciliatora |
| Q07 | `okf-rag.md:445–447` | compiler output nie jest bezpośrednio final truth |
| Q08 | `okf-rag.md:231–260` | przepływ prowadzi od raw source przez compiler, graph, publish do hybrid recall |
| Q09 | `okf-rag.md:573–583` oraz `1022–1032` | benchmark zawiera Recall/Hit@1/3/5/10 i MRR@10 |
| Q10 | `okf-rag.md:1134–1140` | ekstrakcja jest niedeterministyczna, a pruning duplikatów niepełny |

## Werdykt

To nie jest już przede wszystkim problem języka zapytania. W kontrolowanym
teście nie pomogły ani nazwy własne, ani dokładne nagłówki. Najbardziej
praktyczny wniosek jest taki:

```text
Smart Connections → hub / temat
rg albo FTS5 → plik i dokładny passage
```

Nie należy odpowiadać `unknown` tylko dlatego, że semantyczny ranking nie
zwrócił pliku. `unknown` oznacza brak dowodu po obu warstwach. W tym teście
warstwa lexical podniosła wszystkie pięć przypadków do `direct`.

Hipoteza o uszkodzonej segmentacji lub niejednorodności dużych importów pozostaje
otwarta, ale nie wymaga teraz masowego dzielenia plików. Najpierw należy używać
hubów jako nawigacji i automatyzować drugi krok weryfikacji.
