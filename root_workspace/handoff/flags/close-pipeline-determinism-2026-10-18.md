---
flag: close-pipeline-determinism-2026-10-18
since: 2026-10-18
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
---

`close-pipeline-determinism-2026-10-18` — 2026-10-18: Naprawiono dwa udowodnione bugi close pipeline (midnight determinism + `INDEX.md` staging) — close przechodzi **bez** `--include handoff/flags/INDEX.md` i bez wrażliwości na północ. Następny krok: decyzja ownera o pozostałych długach (stary flag, S76 leak, S78, S80, R14 shelf).

Wejście: HEAD `927c14e`, drzewo czyste, `check_workspace_integrity.py` EXIT=0, `build_handoff.py --check` EXIT=0. `INLINE_WINDOW_DAYS` zostaje **3** — nie ruszono progu, logiki `--check`, R12/R17/R20/R21.

## Zmiany
- `scripts/build_handoff.py`: nowy `newest_since(flags)` — deterministyczny punkt odniesienia okna = najnowszy `since` w korpusie, nie `date.today()`; `split_flags(flags, as_of=None, window_days=3)`, domyślnie `as_of = newest_since(flags)`; nowy argument `--as-of YYYY-MM-DD`. `INLINE_WINDOW_DAYS = 3` bez zmian — naprawiony generator, nie próg.
- `scripts/close.py`: `GENERATED_VIEWS = ("HANDOFF.md", "STATE.md", "handoff/flags/INDEX.md")` — użyte w `allowed` `dry_run()`, w `allowed` i `add` `main()`.
- `hooks/pre-commit`: `git add -- HANDOFF.md STATE.md handoff/flags/INDEX.md` (wyłącznie ta zmiana).
- `scripts/test_close.py`: `test_generated_views_include_index_md`; `scripts/test_build_handoff.py`: 4 testy determinizmu (`newest_since`, identyczność per `as_of`, przesunięcie tylko flag brzegowych, `since` brakuje → fresh).
- `SCARS.md`: +S81 (candidate, heading `## S81:` — parseable, „candidate" po dwukropku, nie bug S76).

## Adversarialne przypadki (S56/S62) — oczekiwania zapisane PRZED runem
M1–M5 zapisane w `%TEMP%\opencode\close-fix-expect.md` przed pierwszą edycją kodu; poniżej raw output (S65, nie streszczenie).

M1 (`--as-of` 2026-10-17 vs 2026-10-18) — zapisane z góry: różnica **wyłącznie** w archiwizacji wg okna 3 dni; `--check --as-of` zgodne z wygenerowanym plikiem:
```
M1 as_of=2026-10-17 cutoff=2026-10-14 fresh=57 archived=119
M1 as_of=2026-10-18 cutoff=2026-10-15 fresh=32 archived=144
M1 moved inline->INDEX: 25
M1 since==2026-10-14: 25
M1 moved == boundary: True
M1 no other fresh/archived change: True
```

M2 (dwa buildy przy tym samym `--as-of` → bajtowo identyczne):
```
M2 HANDOFF identical per as_of: {'2026-10-17': (True, True), '2026-10-18': (True, True)}
M2 default==10-18 view: True
M5 on-disk HANDOFF == default render: True
M5 on-disk INDEX == default render_index: True
```
CLI, dwa rebuildy pod rząd (Get-FileHash):
```
CHECK_EXIT=0
M2 HANDOFF byte-identical: True
M2 INDEX byte-identical: True
```

M3 (niepowiązany plik → nadal stray; `allowed` **nie** poszerzone poza trzy generowane widoki) — `docs/reviews/README.md` zmodyfikowany, `close.py --dry-run`, własne brudne pliki przekazane przez `--include`:
```
close.py FAIL at [dry-stage]: a real close would stop on uncommitted tracked work:
   M docs/reviews/README.md
M3_EXIT=1
```

M4 (realny close **bez** `--include handoff/flags/INDEX.md` → przechodzi):
```
close.py: wrote handoff\flags\close-pipeline-determinism-2026-10-18.md
close.py: views rebuilt, gate green
close.py: minted .commit-approved
close.py: committed `close-pipeline-determinism-2026-10-18` — session closed
CLOSE_EXIT=0
```
Po close: `git status --porcelain` → puste; `git log --oneline -1` → commit close. Uwaga: `handoff/flags/INDEX.md` nie pojawił się w tym commicie, bo w tej sesji jego treść się **nie zmieniła** (najnowszy `since` już `2026-10-18`, okno 3-dniowe się nie przesunęło) — brak zmiany treści = `git add` bez efektu. Staging `INDEX.md`, gdy faktycznie się zmienia, dowiedziony osobno (E4) na realnym `close.py::find_strays`/`GENERATED_VIEWS` i linii hooka.

M5 (`build_handoff.py --check` po zmianie): `CHECK_EXIT=0`, `HANDOFF_CHECK_EXIT=0`.

E4 (dodatkowy dowód: `INDEX.md` jest nie-stray i stagowany, gdy się zmienia) — `build_handoff.py --as-of 2026-10-19` (cutoff 2026-10-16 przesuwa 11 flag `since=2026-10-15` do archiwum, więc `INDEX.md` realnie się różni od HEAD), następnie realny `close.py::find_strays` ze starym i nowym zbiorem `allowed`:
```
GENERATED_VIEWS: ('HANDOFF.md', 'STATE.md', 'handoff/flags/INDEX.md')
old allowed -> strays: [' M handoff/flags/INDEX.md']
new allowed -> strays: []
```
Linia hooka `git add -- HANDOFF.md STATE.md handoff/flags/INDEX.md` → `git diff --cached --name-only` = `HANDOFF.md`, `handoff/flags/INDEX.md`. Po eksperymencie drzewo przywrócone (rebuild default + `git checkout`), `--check` EXIT=0.

Unittest: `python.exe -m unittest scripts.test_close scripts.test_build_handoff` → `Ran 49 tests in 1.713s ... OK` (EXIT=0).

Bramki: `check_workspace_integrity.py` EXIT=0; `build_handoff.py --check` EXIT=0; `git diff --check` EXIT=0; `ingest_brain.py --check` OK (SCARS.md → 61 problems, S81 sparsowane); `eval_brain.py --check` OK (hit@5=9/10, refusal=3/4, MRR=0.900 — baseline `brain_eval.json` nietknięty); `SCARS.md` kończy się dokładnie jednym `\n`.

## Retire flagi (§5)
Flaga wspominająca dług „`handoff/flags/INDEX.md` poza `allowed`/`find_strays`" to `residue-closeout-2026-10-15` (`not checked`, niegdyś HANDOFF:248). **Nie retire**: jej claim jest **szerszy** — łączy ten dług z R18 (`D-2026-10-11-03`/`-04` PENDING_IMPLEMENTATION) i jest retro-close dwóch cudzych sesji. `cold-start-recall-proof-2026-10-17` również wspomina dług, ale jej claim to cold-start proof (szerszy). **retire=0** — żadna flaga nie ma tego długu jako jedynego claimu; prozy nie edytowano.

## Memory recall (R16)
`memory_index.py query "close midnight determinism INDEX staging build_handoff" --type curated --limit 5`:
- `curated::curated::SCA::24  score=-12.130  ## S69: close.py --dry-run nie waliduje sesji, która wycofuje flagę`
- `curated::curated::fla::0  score=-12.408  # INDEX — archived flags`
R16 trace: `memory_index.py query "close determinism INDEX staging S81" --type curated --limit 3` → `DEC::4 (-8.882)`, `fla::0 (-8.240)`, `fla::0 (-7.364)`.

not checked:
- **midnight bug (`date.today()` w `split_flags`)** — **naprawione** (`newest_since` + `--as-of`); `INLINE_WINDOW_DAYS = 3` bez zmian.
- **`handoff/flags/INDEX.md` staging** (poza `allowed`/`add`/hook) — **naprawione** (`GENERATED_VIEWS` w `close.py` + `git add` w `hooks/pre-commit`).
- **stary flag `recall-protocol-curated-correction-2026-10-17`** — **nadal otwarte**; wymaga decyzji ownera (edit dopisać „skorygowane przez S79" vs retire), nie ruszany (`review-debt-named-s80`).
- **S76 leak w `brain/brain.db`** — **nadal otwarte**; nieparsowalny `## S76 (candidate):`, bulle `id=1023/1024`; nie naprawiano `parse_scars` (R21).
- **S78 (close.py friction)** — **nadal otwarte**; decyzja ownera.
- **S80 (kolizja frazy)** — **nadal otwarte**; candidate, nie wdrożone (nie ruszać bm25/tokenizacji, R15).
- **R14 freshness po shelf-only refresh** — **nadal otwarte**; nie sprawdzono, czy `ingest_curated_shelf` w ogóle powinien aktualizować `sessions_meta`.
- **`python -c`** — trywialne naruszenie S8 odnotowane, nie warte blizny.
- S81: dodany jako **candidate** do `SCARS.md` (klasa: każdy generowany widok/bramka musi mieć deterministyczny punkt odniesienia i być w zbiorze stagowanym), nie wdrożony jako reguła bramki.
- Nie zmieniano semantyki archiwizacji na „po liczbie flag" (decyzja ownera); nie zmieniano `query_memory`/`debug.py`/`parse_scars`/`brain_eval.json`/`AGENTS.md`/`core.hooksPath`.
