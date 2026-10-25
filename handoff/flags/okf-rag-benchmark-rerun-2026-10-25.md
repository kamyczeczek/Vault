---
type: Concept
flag: okf-rag-benchmark-rerun-2026-10-25
since: 2026-10-25
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
title: okf-rag-benchmark-rerun-2026-10-25
generated: { by: okf-enforcer/0.6, at: 2026-10-25T20:41:02Z }
---

`okf-rag-benchmark-rerun-2026-10-25` — 2026-10-25: `benchmark-results-20.json`
przeliczony pod pinem `85038826` (40 plików, `corpus_drift=0`), bo zapisany
wynik z `e356f08` deklarował `2f0491bd` — hash, który nie odpowiadał żadnemu
stanowi repo (drzewo HEAD: `d4c2db0d`, dysk: `56774761`). Przebieg: tryby `all`
i `raw_only`, 20 pytań + OOC01, ten sam runner i te same ustawienia
(`top_k=10`, `min_score=0.55`), bez `--allow-corpus-drift`.

**Wszystkie metryki pozostały identyczne**: `exact@10` 10/20,
`any_exact_or_related@10` 18/20, `related@10` 10/20, `exact@1` 9/20,
`source_recall@10` 19/20, `source_recall@1` 15/20 (`all`) i 17/20 (`raw_only`),
`citation_target_correct@1` 11/20 (`all`) i 12/20 (`raw_only`),
`citation_target_valid@1` 20/20, OOC01 abstain w obu trybach. Żadna metryka
liczona z pozycji 1 nie drgnęła, więc **wnioski baseline'u zostają w mocy** —
kłamała wyłącznie proweniencja, nie liczby.

Zmieniły się: `corpus` (hash + 40 plików), `created_at`, `index_inventory`
(`in_scope` 44→45, `rankable` 37→39, `without_vector` 2→1, wektory źródeł
478→510, wektory bloków 2506→2600, bloki 374→387) i ogony list kandydatów
(od pozycji 2–4 w dół; pierwsze pozycje bez zmian). Indeks wektorowy był w
międzyczasie przebudowany, więc to nie jest ten sam stan indeksu — a mimo to
ranking czołówki jest stabilny.

Skorygowano też pin korpusu w `EXPERIMENT-benchmark-scope-2026-10-25.md`:
dokument miał w treści martwy `2f0491bd` (39 plików) i twierdził „korpus bez
zmian". Status to `planned`, eksperyment nie wystartował, więc korekta pinu
**przed** przebiegiem jest dozwolona przez jego własną regułę — bez niej runner
odrzuciłby własny przebieg eksperymentu jako drift. Next: commit 2 z planu
(migracja 5 notatek kuratorskich do `sources: [{file, lines}]` + allowlista
`DECISION-minimalny` i `DECISION-kontrakt`), bo bez niej gate cytowań nie ma
czego pilnować.

not checked: nie sprawdzono determinizmu — drugi przebieg nie wykonany
(embeddingi idą przez Obsidian CLI; dowiedziona jest proweniencja, nie
powtarzalność wyniku). Tryb `scoped` nadal nie istnieje, więc
`EXPERIMENT-benchmark-scope` pozostaje `blocked_on`. `EXPERIMENT-retrieval-
benchmark-20` nie był przeliczany pod nowym pinem — nie zawierał starego hasha,
więc nie kłamał jawnie. Q02 i Q20 nadal bez ręcznego przeglądu; 10 passage'ów
`related` nadal bez adnotacji „zawiera zdanie odpowiedzi: tak/nie", więc próg
`any@10` pozostaje warunkowy. `CONTEXT.md` nadal poza `CURATED_PREFIXES`, czyli
`raw_only` traktuje słownik warstwy nawigacji jako materiał surowy — otwarta
decyzja. Nie pushowano (`master` wyprzedza `origin/master` o 9 commitów).
