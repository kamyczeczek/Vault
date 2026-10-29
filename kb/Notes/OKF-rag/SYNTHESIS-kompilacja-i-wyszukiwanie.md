---
type: report
title: Synteza — kompilacja, wyszukiwanie i narzędzia
description: Co naprawdę daje pipeline OKF/llmwiki/okforge oraz które elementy warto odłożyć do czasu potwierdzenia potrzeby.
status: draft
tags: [knowledge-management, compilation, retrieval, okf, tooling]
sources:
  - okf-rag.md
  - llm-wiki.md
  - okforge.md
  - SYNTHESIS.md
  - DECISION-minimalny-przeplyw-wiedzy.md
generated:
  by: codex
  at: 2026-10-25T00:00:00Z
---

# Pytanie

Które elementy kompilacji i wyszukiwania wiedzy są naprawdę potrzebne w moim
vaultcie, a które są dopiero narzędziami skalowania?

# Rozróżnienie poziomów

Materiały opisują trzy różne problemy, których nie należy mieszać:

1. **Kompilacja** — zamiana surowych dokumentów w koncepty, relacje i strony z
   cytowaniami.
2. **Publikacja i kontrola** — decyzja, które wygenerowane koncepty są aktualne,
   duplikaty usunięte, a linki poprawne.
3. **Retrieval** — znalezienie właściwego konceptu lub źródła dla konkretnego
   pytania.

Wniosek: wyszukiwarka nie naprawi braku decyzji o tym, co jest wiedzą trwałą,
a kompilator nie powinien samodzielnie ustalać ostatecznej prawdy. [inferred]

# Powtarzające się twierdzenia

## 1. Kompilator powinien proponować, a nie być źródłem prawdy

W pipeline OKF-RAG `llm-wiki-compiler` tworzy kandydatów konceptów i linków,
ale reconciler decyduje o publikowanym zbiorze. Wynik kompilatora nie jest
traktowany bezpośrednio jako prawda.

Źródło: [okf-rag](okf-rag.md) (sekcja „Generate OKF with llm-wiki-compiler”,
linie 445–466).

Konsekwencja: automatycznie wygenerowana notatka wymaga kontroli pochodzenia,
duplikatów i statusu przed awansem do warstwy używanej jako wiedza.

## 2. Granica źródło–output jest ważniejsza niż wybór narzędzia

Pipeline rozdziela Raw Markdown, manifesty, kandydatów, staging i opublikowany
bundle. W okforge podobnie istnieją `raw/` oraz wygenerowane `wiki/`. Ręczna
edycja outputu może zostać utracona przy kolejnym recompile.

Źródła: [okf-rag](okf-rag.md) (linie 445–466, 511–527),
[okforge](okforge.md) (linie 760–825, 4715–4748).

Konsekwencja: poprawki wprowadzamy w źródłach lub w jawnej warstwie kuratorskiej,
nie w plikach generowanych przez pipeline.

## 3. Retrieval jest warstwą konsumpcji, nie metodą myślenia

Hybrid retrieval łączy podobieństwo semantyczne z wyszukiwaniem leksykalnym,
rerankingiem, metadanymi i relacjami. Pozwala szybciej znaleźć materiał, ale
nie rozstrzyga, czy twierdzenie jest prawdziwe ani czy jest decyzją dla naszego
workspace'u.

Źródła: [okf-rag](okf-rag.md) (linie 231–260, 573–601),
[llm-wiki](llm-wiki.md) (linie 54–78).

Konsekwencja: najpierw ustalamy format i przepływ wiedzy, a dopiero potem
optymalizujemy wyszukiwanie.

## 4. Narzędzie powinno mieć ścieżkę przeglądu i świeżości

llmwiki opisuje review queue, cytowania, provenance, lifecycle i wykrywanie
starych stron. To nie są dodatki kosmetyczne: bez nich nie wiadomo, czy wynik
jest wygenerowany, zweryfikowany, aktualny czy tylko podobny semantycznie.

Źródło: [llm-wiki](llm-wiki.md) (linie 54–78, 113–122).

Konsekwencja: w małym vaultcie wystarczy na początku prosty `status`, `sources`
i ręczny przegląd; pełne workflow można dodać później.

## 5. Wyniki benchmarku są dowodem lokalnym, nie obietnicą uniwersalną

OKF-RAG pokazuje bardzo dobre wyniki lokalnego benchmarku recall/hit@k i szybki
hot path, ale są to wyniki dla określonego korpusu, modelu i zestawu pytań.

Źródło: [okf-rag — benchmark](okf-rag.md) (linie 573–601, 1005–1056).

Konsekwencja: przed wyborem narzędzia trzeba zbudować mały benchmark z własnych
pytań, zamiast przenosić cudze liczby na swój vault.

## 6. Automatyczna kompilacja ma realne ograniczenia

W opisanych testach ekstrakcja konceptów nie była deterministyczna, a pruning
historycznych duplikatów był niepełny. Automatyzacja działa, ale wymaga warstwy
reconcile, review i możliwości rollbacku.

Źródło: [okf-rag — findings](okf-rag.md) (linie 1134–1140).

Konsekwencja: nie uruchamiamy automatycznej reorganizacji na całym vaultcie bez
kopii, stagingu i kontroli zmian.

## 7. Najpierw opłaca się użyć prostego trybu ręcznego

Zarówno llmwiki, jak i okforge są najbardziej przydatne wtedy, gdy korpus ma
być wielokrotnie używany, cytowany i rozwijany. Jednorazowe pytanie lub szybko
zmieniający się strumień logów nie musi być kompilowany w trwałą wiki.

Źródło: [llm-wiki](llm-wiki.md) (linie 54–78, 122–124).

Konsekwencja: obecny vault powinien najpierw przejść kilka ręcznych cykli
`źródło → synteza → decyzja`; dopiero powtarzalny ból uzasadnia cięższe tooling.

# Synteza

Najważniejszym elementem całego systemu nie jest embedding, MCP ani konkretna
baza indeksowa. Jest nim granica odpowiedzialności:

```text
człowiek / źródło
    → kurator wybiera twierdzenia
    → pipeline może zaproponować koncepty
    → review/reconcile dopuszcza publikację
    → retrieval pomaga znaleźć wynik
```

Pipeline ma sens dopiero wtedy, gdy ręczne utrzymywanie konceptów, cytowań i
relacji staje się powtarzalnym kosztem. [inferred]

# Implikacja dla vaultu

Na obecnym etapie wystarczy:

- surowe pliki pozostawić nietknięte;
- tworzyć krótkie syntezy i decyzje z linkami do źródeł;
- używać metadanych `type`, `description`, `status` i `sources`;
- mierzyć wyszukiwanie na kilku własnych pytaniach;
- nie traktować automatycznie wygenerowanych stron jako finalnej prawdy.

Nie ma jeszcze podstaw, aby instalować lub uruchamiać pełny pipeline OKF-RAG na
całym vaultcie. Jego wartość trzeba najpierw porównać z prostym wyszukiwaniem
Obsidiana i ręczną syntezą.

# Mały eksperyment porównawczy

Utworzyć 5 pytań dotyczących `Notes/OKF-rag`, na przykład:

1. Jak powinien wyglądać przepływ od źródła do decyzji?
2. Co jest źródłem prawdy w pipeline OKF?
3. Kiedy wygenerowane koncepty wymagają review?
4. Jakie są ograniczenia automatycznej deduplikacji?
5. Kiedy kompilacja wiki jest przesadą?

Dla każdego pytania porównać:

- ręczne wyszukiwanie w Obsidianie;
- wyszukiwanie semantyczne, jeśli jest dostępne;
- odpowiedź z cytowaniami i linkami do plików.

Minimalny wynik to nie wynik modelu, lecz informacja, czy właściwe źródło dało
się znaleźć i czy odpowiedź zachowała rozróżnienie faktu, syntezy i hipotezy.

# Wniosek roboczy

Kompilacja i retrieval są warstwami skalowania. Najpierw trzeba ustabilizować
mały, ręcznie weryfikowalny przepływ wiedzy; dopiero jego powtarzalne ograniczenia
powinny wyznaczyć wybór narzędzia. [inferred]
