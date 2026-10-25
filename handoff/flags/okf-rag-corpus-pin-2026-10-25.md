---
type: Concept
flag: okf-rag-corpus-pin-2026-10-25
since: 2026-10-25
owner: opencode
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: Notes/OKF-rag/benchmark-questions.json
title: okf-rag-corpus-pin-2026-10-25
generated: { by: opencode, at: 2026-10-25T00:00:00Z }
---

`okf-rag-corpus-pin-2026-10-25` — 2026-10-25: historia jest **liniowa, bez
rozjazdu** — `e356f08` jest dzieckiem `eeba3fc` (nie dwoma równoległymi
domknięciami); `master` wyprzedza `origin/master` o 3 commity, merge nie jest
potrzebny. Naprawiono przyczynę „rozgrzebanego repo": `edba1b8`
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
różni się od HEAD (retrieval czyta `.smart-env`, czyli drzewo robocze).
Pin `2f0491bd` **nie odpowiadał żadnemu commitowi** (drzewo HEAD: `d4c2db0d`,
dysk: `56774761`), więc `benchmark-results-20.json` mierzył korpus
nieodtwarzalny z repo — nie jest ważną bazą porównawczą. Ten wpis koryguje
`okf-rag-benchmark-local-2026-10-25` w części „utrwalono hash korpusu": hash
był utrwalony, ale nie opisywał żadnego stanu repo. Nowy pin:
`85038826`, 40 plików, `corpus_drift=0`; sprawdzone, że nieśledzona notatka
nie zmienia pinu, tylko zgłasza drift. Next: dodać tryb `scoped` do
`run_okf_rag_benchmark.py` (bez niego reguła scope jest niemierzalna), potem
jeden przebieg 20 pytań jako nowa baza.

not checked: nie uruchomiono benchmarku 20 pytań (wymaga Obsidiana i
Smart Connections) — nowy pin jest nieprzetestowany na przebiegu; tryb
`scoped` nadal nie istnieje; 5 notatek nie zmigrowano do
`sources: [{file, lines}]`; gate cytowań i skill `retrieval-two-stage` nie
istnieją; Q02 i Q20 nadal bez ręcznego przeglądu. `CONTEXT.md` jest słownikiem
warstwy nawigacji, ale `CURATED_PREFIXES` go nie obejmuje, więc `raw_only`
traktuje go jako materiał surowy — otwarta decyzja, świadomie nierozstrzygnięta
w tym commicie. Proces: `SCARS.md` przeczytany **po** pierwszej edycji
`scripts/**` (wymóg z `handoff/CONTEXT.md`), oraz jedno użycie `python -c` na
starcie wbrew scarowi o Windows tooling — oba bez skutku, ale powtarzalne.
