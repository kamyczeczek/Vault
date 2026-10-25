---
flag: okf-rag-corpus-pin-2026-10-25
since: 2026-10-25
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
---

`okf-rag-corpus-pin-2026-10-25` — 2026-10-25: historia jest **liniowa, bez
rozjazdu** — `e356f08` jest dzieckiem `eeba3fc` (nie dwoma równoległymi
domknięciami). Naprawiono przyczynę „rozgrzebanego repo": `edba1b8`
(„vault-migrated") usunął **111 plików `scripts/`**, czego message nie
wspominał, więc HEAD śledził 5 plików przy 98 na dysku — bramki
(`check_workspace_integrity.py`) i harness (`run_okf_rag_benchmark.py`) były
nieodtwarzalne z klonu; przywrócone w `6890b66` razem z ignorowaniem
`_scratch/` (407.7 MB), `out/`, `__pycache__/` i tokenu. `8271f41` wciągnął
do repo `CONTEXT.md` i `EXPERIMENT-benchmark-scope` oraz rozstrzygnął pusty
`source-slices/index.md` (generator pisze do `_slices/`, więc katalog był
samym indeksem folderu Obsidiana). `84ba387` przeniósł pin korpusu z dysku na
drzewo git: `corpus_paths()`/`corpus_blobs()` liczą z `git ls-tree` +
`cat-file --batch`, a `corpus_drift()` odmawia przebiegu, gdy korpus roboczy
różni się od HEAD. Pin `2f0491bd` **nie odpowiadał żadnemu commitowi** (drzewo
HEAD: `d4c2db0d`, dysk: `56774761`), więc `benchmark-results-20.json` mierzył
korpus nieodtwarzalny z repo. Nowy pin: `85038826`, 40 plików,
`corpus_drift=0`.

**Korekta 2026-10-25 (commit `okf-rag-benchmark-rerun`):** przebieg 20 pytań
pod nowym pinem **został wykonany** — nie było to „nieprzetestowane". Wynik:
wszystkie metryki identyczne jak w `e356f08` (`exact@10` 10/20,
`any_exact_or_related@10` 18/20, `source_recall@10` 19/20, OOC01 abstain),
mimo przebudowanego indeksu wektorowego. Czyli liczby baseline'u były poprawne,
a nieodtwarzalna była tylko ich proweniencja — i ta jest już naprawiona.
Next: dodać tryb `scoped` do `run_okf_rag_benchmark.py` (bez niego
`EXPERIMENT-benchmark-scope` pozostaje `blocked_on`), potem commit 2 (migracja
5 notatek do `sources: [{file, lines}]`).

not checked: tryb `scoped` nadal nie istnieje; 5 notatek nie zmigrowano do
`sources: [{file, lines}]`; gate cytowań i skill `retrieval-two-stage` nie
istnieją; Q02 i Q20 nadal bez ręcznego przeglądu; 10 passage'ów `related` bez
adnotacji „zawiera zdanie odpowiedzi: tak/nie"; determinizm przebiegu nie
sprawdzony (jeden przebieg). `CONTEXT.md` jest słownikiem warstwy nawigacji,
ale `CURATED_PREFIXES` go nie obejmuje, więc `raw_only` traktuje go jako
materiał surowy — otwarta decyzja, świadomie nierozstrzygnięta. Proces:
`SCARS.md` przeczytany **po** pierwszej edycji `scripts/**`, oraz jedno użycie
`python -c` na starcie wbrew scarowi o Windows tooling — oba bez skutku, ale
powtarzalne.
