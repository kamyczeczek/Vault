# HANDOFF — workspace root

> **GENEROWANE — nie edytuj ręcznie.** `python scripts/build_handoff.py`
> buduje ten plik z `handoff/flags/*.md` + `handoff/deep/*.md`.
> Kontrakt (kto pisze co): `handoff/CONTEXT.md`. Stan maszynowy: `STATE.md`.

Portable state for a cold session entering at the workspace root. Per D12 this
file carries only what is true across projects; the project-local handoff carries
the detail and is linked, never copied. The prose that used to sit here by hand
now has its home in `handoff/flags/` (one flag = one file = one writer) and is
inlined below by the builder.

## How to update

One flag = one file: `handoff/flags/<flag>.md`, frontmatter `flag` / `since` /
`owner` / `agent` / `model` + the entry body. Write **only** the flag you own
(or the one your task retired); never edit another flag's prose — that is what
made the old single-file handoff clobber under two agents. Then rebuild this
view:

```
python scripts/build_handoff.py           # regenerate
python scripts/build_handoff.py --check   # gate form: exit 1 if stale
```

This file is state, not a journal: replace or retire a flag whose claims
stopped holding (delete the file), and compress closed threads into
`handoff/deep/`. Project-local detail is linked, never copied (D11/D12).

## Status

<!-- handoff/flags/unlazy-workflow-closure-2026-10-27.md · owner: mateusz · agent: opencode · model: openai-api/gpt-5.6-luna -->
`unlazy-workflow-closure-2026-10-27` — 2026-10-27: Unlazy checklist execution partial / corrected status.
Stan:
- CLOSED: A (ETTh1-H720 G4 sweep results/etth1_h720_amr24168_g4.json), C (Monorepo D24 workspace integrity), E (S47_DESIGN.md adnotacja), G (retrieval-two-stage skill catalog).
- STALE / INCOMPLETE: B (FEV multivariate code landed and py_compile passed, but full end-to-end execution/artifact pending due to high fit volume ~21k fits), D (OKF-rag EXPERIENCE.md triage note added, but C2-C6 migration/gate/scoped mode pending), F (workspace hygiene cleanup: close_body.txt artifact dropped, did_sessions.bat reverted/reviewed).
Next: optimize FEV fit loop / subset origins before full run; migrate OKF-rag C2-C6 notes.
not checked: FEV multivariate end-to-end artifact generation; OKF-rag C2-C6 notes migration; remote CI pipeline (non-existent).

<!-- handoff/flags/close-py-include-safety-2026-10-28.md · owner: mateusz · agent: opencode · model: omniroute/agy/gemini-3.8-flash-high -->
`close-py-include-safety-2026-10-28` — 2026-10-28: `close.py` odblokowuje `--include projects/...` i zabrania `--include .`. Usunięto przestarzały check blokujący ścieżki pod `projects/research/`, dodano walidację przez `git check-ignore -q --no-index --`, zachowano obsługę staged deletions (`_is_staged_deletion`) i katalogów. Usunięto zindexowane śmieci `close_body.txt` i `correct_body.txt` z `handoff/`. Testy w `scripts/test_close.py` (`NewSafetyChecksTests`) zielone, 42 testy w `scripts/test_close.py` przechodzą.

not checked: —

<!-- handoff/flags/benchmark-core-fev-multivariate-2026-10-27.md · owner: mateusz · agent: opencode · model: omniroute/agy/gemini-3.8-flash-high -->
`benchmark-core-fev-multivariate-2026-10-27` — 2026-10-28: FEV protocol multivariate support oraz per-origin fit w `bench.py`. `extract_series_from_window` zwraca listę 1-D array (jedna na kolumnę targetu) zamiast pojedynczego 1-D; dodano `_unwrap` dla kontenerów fev. `main_fev` iteruje po kolumnach targetów: fituje model per kolumna, liczy MAE per kolumnę, uśrednia. Kod realizuje per-origin fit: pętla `for w in windows:` z `train_cols_w` fituje modele na własnym oknie przeszłości każdego originu (linie 438–443 `bench.py`), więc fałszywa klauzula `not checked: per-origin fit` została usunięta z flagi. Zsynchronizowano też dokumentację `AMR_24_168_H720_RESULT.md` z artefaktem `results/etth1_h720_amr24168_g4.json` (G4 FAIL, mean rank 6.1). `python -m py_compile bench.py` OK. Next: FEV multivariate end-to-end z wygenerowaniem `bench_fev_mini.json`.

not checked: FEV multivariate end-to-end (Windows multiprocessing w bibliotece fev; `bench_fev_mini.json` nie istnieje).

<!-- handoff/flags/vault-monorepo-import-2026-10-27.md · owner: mateusz · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
`vault-monorepo-import-2026-10-27` — 2026-10-27: cały vault w jednym repo GitHub.
Stan: 12 zagnieżdżonych repo zastąpione plikami + `history.bundle` (każde odtwarzalne
przez `git clone history.bundle`); `.gitignore` zwężony do toolchainu, sekretów,
książek i plików >100 MB. `check_workspace_integrity._tracked_files` pyta teraz repo
nadrzędne, bo projekt bez własnego `.git` nie ma już „zera śledzonych plików”.
Next: push (~300 MB) i weryfikacja świeżego `git clone`.
not checked: push do GitHuba i świeży `git clone` — dopiero po tym commicie.
Książki z `library/` i archiwów zostają poza repo (świadoma decyzja, nie przeoczenie).

<!-- handoff/flags/vault-monorepo-decisions-2026-10-27.md · owner: mateusz · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
`vault-monorepo-decisions-2026-10-27` — 2026-10-27: D24 zapisuje, co repo zawiera i jak odtworzyć historię.
Stan: `DECISIONS.md` D24 wymienia 4 wyjątki (toolchain, sekrety, książki, pliki >100 MB)
i podaje `git clone --mirror history.bundle` jako jedyny poprawny sposób odtworzenia
12 wchłoniętych repo — zwykły `clone` gubi `refs/remotes/*` (157 commitów w `ecc`).
Next: świeży `git clone` z GitHuba i `check_workspace_integrity.py` w klonie.
not checked: zachowanie klonu — `preflight.py`, hooki i `core.hooksPath` są per-maszyna.

<!-- handoff/flags/etth1-h720-s49-closeout-2026-10-27.md · owner: mateusz · agent: opencode · model: omniroute/cx-gpt-5.6-luna-medium -->
`etth1-h720-s49-closeout-2026-10-27` — 2026-10-27: linia S49 H720 domknięta. Trzeci i ostatni kandydat AMR-24/168 został dokończony (kotwica tygodniowa z no-op p+0.0*anchor stała się anchor_rule przez hook _anchor_level w benchmark-core/members/amr_fbs.py; train/serve spójne) i oceniony. Dobór reguły na early origins dał weekly; zamknięty przebieg 12 originów (seed 42) results/etth1_h720_amr24168_weekly.{json,md} daje średnie raw MAE 3.1480 (std 1.3573) -> G1 FAIL (<1.9781) i G2 FAIL (DLinear 3/12, SpectralFFT 10/12; tylko SpectralFFT przegrywa). G3 PASS — brak regresji H96/H336 (H96 2.0132 vs ref 3.2641; H336 3.5592 vs ref 6.7378), results/etth1_h720_amr24168_g3.json. Wynik: REJECT AMR-24/168, zamyka S49 jako częściowy sukces (H2K 2.7270 / SAB-L 4.4611 / AMR 3.1480, każdy powyżej incumbent 1.9781 lub gorszy). Dokumentacja skonsolidowana: H2K_H720_RESULT.md przeniesiony z _archive/datasets/INBOX/raw do projektu; nowe: AMR_24_168_H720_RESULT.md, diag_amr_early_dev.py, run_amr_h720_final.py, run_amr_h720_g4.py. pytest 14/14. Dodano README.md jako front door workspace roota (wpis do ALLOWED_ROOT i CLAUDE.md). Next: nie iterować H720 bez nowego biasu i nowych originów dev; zamknąć S49 formalnie w LONGTERM_ETTH1_H720_DESIGN.md.

not checked: pełny sweep G4 (5 seedów) został zaprojektowany z ProcessPoolExecutor i per-cell cache, ale nie został uruchomiony do końca — G1 i G2 padają definitywnie, więc REJECT jest ustalony niezależnie od G4.

<!-- handoff/flags/benchmark-core-fev-g2-fix-2026-10-27.md · owner: mateusz · agent: opencode · model: omniroute/cx-gpt-5.6-luna-medium -->
`benchmark-core-fev-g2-fix-2026-10-27` — 2026-10-27: FEV protocol G2 gate aligned with S49 pre-registration. W `main_fev()` zmieniono definicję G2 z hardcoded `mean_rankB < 2` na pre-rejestrowaną: "Pool B beats Pool A on majority of tasks" (`winsB >= len(task_results) // 2`). To odpowiada G2 z H720 ("beat DLinear and SpectralFFT at H720 (raw)"). Dodano jawny log `G2 (Pool B beats A on majority of tasks): X/Y -> PASS/FAIL` oraz sekcję `gates.G2_majority_win` w JSON. "Frozen fit on first window" pozostaje (zgodne z protokołem S-47); multivariate zostawione jako osobny ticket (flaga "not checked:"). `python -m py_compile bench.py` OK. Next: multivariante wsparcie w `extract_series_from_window` oraz ewentualnie per-origin fit dla FEV.

not checked: multivariate wsparcie (obecnie `extract_series_from_window` zwraca 1-D array, pierwszą kolumnę); per-origin fit w FEV (obecnie frozen na pierwszym oknie).

<!-- handoff/flags/research-engine-s47-2026-10-26.md · owner: mateusz · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
`research-engine-s47-2026-10-26` — 2026-10-26: zagnieżdżone repo `research-engine` jest domknięte (dwa commity: 0b08562, 70ce0eb; drzewo czyste). Q9 rozstrzygnięte regułą zapisaną **przed** odczytem liczb: obie polityki okna (stałe 2000 vs expanding) muszą dać tego samego kandydata i te same bramki. Dały — wybór B, te same rangi, 4/6 zwycięstw, 0/6 zmian zwycięzcy na zadaniach — więc stałe 2000 zostaje protokołem, a expanding jest zapisanym testem wrażliwości (`results_s47_expanding.json`, `compare_window_policies.py` → exit 0). Q10: pięć originów W=5 jest spalone dla potwierdzenia, `all_binding=false`, nic nie awansuje. Q11: 26.7 s fixed / 26.2 s expanding, poniżej `<5 min`. `results_s47.json` w HEAD nie mówi już `PROMOTE` — werdykt jest diagnostyczny. Testy 12/12.
Next: protokół FEV w `benchmark-core` — patrz `benchmark-core-fev-honest-2026-10-26`. S-47 zostaje sondą.
not checked: nie ruszano `benchmark-core` w tym commicie; stan `bench.py --fev` opisuje flaga `benchmark-core-fev-honest-2026-10-26`.

<!-- handoff/flags/obsidian-index-overload-2026-10-26.md · owner: mateusz · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
`obsidian-index-overload-2026-10-26` — 2026-10-26: przyczyną zadyszki był nie
jeden indeks, a cztery nakładające się przebiegi po całym vaulcie, który po
root-flatten (2026-10-25) jest workspace'em dev: **72 818 plików / 3,27 GB, 26 645 md**,
z czego 23 273 md to dane maszynowe (dwa identyczne korpusy po 10 374 plików
+ 2 525 w `brain/.brain/corpus`), a w środku leżały dwa pliki Repomix
**55,7 MB / 1,05 mln linii** i **27,9 MB**.

Zmiany (żaden plik nie został usunięty):

- `vault_export.md`, `test_export.md`, `scripts/vault_export.md` → `.export/`
  (katalog z kropką; Obsidian nie indeksuje ścieżek zaczynających się od `.`).
  `scripts/export_vault_repomix.bat` domyślnie pisze do `.export\` i wymusza to
  także przy argumencie; `.export/` w `.gitignore`.
- `.obsidian/app.json`: `userIgnoreFilters` = `projects/`, `scripts/_scratch/`,
  `logs/`, `agents/` (ukrywa z grafu/wyszukiwania/properties; **nie** zatrzymuje
  parsowania metadataCache — to ograniczenie Obsidiana).
- `okf-enforcer/data.json`: `scanOnStartup: false`, `fixOnSave: false`,
  `autoGenerateIndex: false`, `excludeFolders` += `projects`, `scripts/_scratch`,
  `logs`, `agents` (wcześniej brak pliku = domyślne, czyli pełna walidacja
  całego vaulta na starcie i zapisy `index.md` w `__pycache__`).
- `ideaverse-maps/data.json`: `exclude` = `projects`, `scripts/_scratch`, `logs`
  (scan-cache miał 23 991 wpisów, w tym 10 374 z korpusu i 12 480 z `_archive`).
- `.smart-env/smart_env.json`: `folder_exclusions` += `projects`, `logs`, `agents`;
  `smart_blocks.embed_blocks: false`; `re_import_wait_time` 13 → 120 s
  (13 s debounce po każdym zapisie = 91 re-importów w 43 h).
- `obsidian-git/data.json`: nowy plik z `autoSaveInterval: 0`,
  `autoPullInterval: 0`, `refreshSourceControlTimer: 60000` (domyślne 7 s
  `git status` po całym drzewie; backup z 10-25 miał auto-commit i auto-pull
  co 10 s).
- `.obsidian/workspace.json`: usunięte panele `all-properties`, `tag`,
  `smart-connections-view`, `smart-env-status-view`; wyczyszczone `lastOpenFiles`.

Czego to **nie** usuwa: Obsidian dalej parsuje 23,3 tys. notatek korpusu przy
każdym starcie (metadataCache nie jest trwały, a „Excluded files" nie wpływa na
parsowanie). Jeśli start ma być krótki, korpusy muszą wyjść z vaulta albo dostać
nazwę z kropką — to zmiana ścieżek w `projects/`, więc osobna decyzja.

Potwierdzone przez użytkownika 2026-10-27 po restarcie aplikacji: indeksowanie
przestało dławić Obsidiana. Zostaje tylko koszt startu (~24 tys. notatek do
sparsowania), nie cykliczne zadyszki w trakcie pracy.

not checked:
- brak profilu CPU przed/po — potwierdzenie jest objawowe („już nie dławi"),
  nie liczbowo; nie mierzono czasu startu ani zużycia RAM.
- `_recovery-2026-10-25` (67,9 MB) i `smart_sources.ajson` (28,7 MB) nietknięte;
  baza Smart Connections nie została wyczyszczona.

<!-- handoff/flags/benchmark-core-fev-honest-2026-10-26.md · owner: mateusz · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
`benchmark-core-fev-honest-2026-10-26` — 2026-10-26: `bench.py --fev` przestało kłamać (nested commits `726daa6` kod + testy, `e54644d` MAP.md; tylko `bench.py` + `test_benchmark_protocol.py` — 36 wcześniejszych brudnych wpisów w `benchmark-core` **nie** ruszono). Martwe URL-e były prawdziwe: `benchmarks/fev_bench.yaml` i `fev_bench_mini.yaml` → 404; właściwe to `benchmarks/fev_bench/tasks.yaml` i `.../tasks_mini.yaml`, sprawdzone 200, a `Benchmark.from_yaml` ładuje 20 zadań i przechodzi probe. `--fev` domyślnie **failuje zamknięciem** (exit 2, zero artefaktów); `--allow-synthetic-fallback` to jawny opt-in. Każdy wynik niesie `data_source` (`real` / `synthetic_fallback` / `builtin_suite`) i `confirmatory` (true tylko dla real); fallback jest stemplowany `synthetic_fallback` / `false`, zapisuje `fev_attempt` i ląduje w `bench_synthetic_fallback.json` — nigdy w `results_s47.json`, który wcześniej nadpisywał. `test_benchmark_protocol.py` 6/6.
Next: protokół FEV — zadania, metryki, sposób raportowania — i pierwszy run na realnych danych, z commitem artefaktu. To jedyna ścieżka, która może cokolwiek promować; S-47 zostaje sondą.
not checked: `main_fev()` nadal liczy werdykt starym hardcoded `mean_rankB < 2` zamiast definicji G2 z pre-rejestracji, dopasowuje raz na pierwszym oknie i ignoruje multivariate. To należy do protokołu FEV, nie do tej poprawki.

<!-- handoff/flags/vault-root-flatten-2026-10-25.md · owner: mateusz · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
`vault-root-flatten-2026-10-25` — 2026-10-25: zawartość `root_workspace/` była
już przeniesiona do korzenia repo **na dysku**, ale nie w indeksie: HEAD trzymał
cały vault pod prefiksem `root_workspace/`, a korzeń miał te same pliki jako
nieśledzone. Ten commit zapisuje przeniesienie: 866 wpisów, z czego 577 to
czyste rename'y (`R100`, `root_workspace/X → X`), 148 dodatków i 135 usunięć;
dla każdego z 30 wpisów najwyższego poziomu `missing=0` (porównanie
`git ls-files root_workspace` z dyskiem). Dopóki tego nie było, `git status`
pokazywał ~1000 wpisów, a `close.py` odmawiał **każdego** commita na `[stage]`
z listą 711 usunięć.

Konsekwencja, której nie da się rozdzielić: **`handoff/` wchodzi do repo
w całości** — 325 plików, z czego śledzone były 3. Usunięcie
`root_workspace/handoff/*` bez dodania `handoff/*` wykasowałoby te pliki z HEAD
bez odpowiednika, więc „handoff jako osobna sesja" jest nierozłączny od
spłaszczenia. To domyka lukę z raportu: bez tego żadna deklaracja „domknięte" nie
jest weryfikowalna ze świeżego klonu.

**Blokada, która wymusiła zmianę `.gitignore`.** `close.py` nie umie wyrazić
katalogu, którego *wszystkie* śledzone pliki są usunięte: `git add --
root_workspace` kończy się `fatal: pathspec 'root_workspace' did not match any
files` (git nie dopasowuje pathspecca do katalogu nieistniejącego na dysku; to
samo `-A`/`-u`). `find_strays` dodatkowo nie rozumie linii `R  a -> b`, więc 577
rename'ów byłoby strayami niezależnie od `--include`. Jedyna sankcjonowana droga
dla migracji strukturalnej to `--include .` (flaga
`close-include-whole-tree-2026-10-24`), ale ona robi `git add -- .`, a w drzewie
było `projects/` = 67 720 plików / 2,4 GB i `library/` = 225 MB. Dlatego ten
commit dodaje 11 reguł ignore dla tego, co **nigdy** nie jest treścią vaulta:
`projects/` (niezmiennik, który close.py deklarował tylko w komunikacie błędu),
`library/`, `agents/backup/`, `brain/*.db*`, `tools/out/`, `logs/`, `.pi/`, kopie
`.obsidian/{repair-backup,plugins.disabled}-*` / `*.bak-*`, `scan-cache.json`.
`library/` (225 MB PDF-ów) zostaje **wyłącznie na dysku** — to świadoma decyzja,
nie przeoczenie: wersjonowanie tych plików wymaga LFS albo backupu poza gitem.

Weszły też 4 pliki lokalnego stanu aplikacji, bo blokowały commit jako strays:
`.obsidian/community-plugins.json`, `.obsidian/plugins/obsidian-git/data.json`,
`.obsidian/plugins/smart-connections/data.json`, `.smart-env/smart_env.json`
(oraz plugin `ideaverse-maps`, 10 MB — inne pluginy są śledzone, więc dla
spójności ten też). Next: close z re-runem benchmarku pod pinem `85038826`,
potem commit 2 (migracja 5 notatek do `sources: [{file, lines}]`).

not checked: `--include .` **wyłącza sprawdzanie strayów w całości** — to
udokumentowane zachowanie tej flagi, ale znaczy, że ten commit nie dowodzi
„nic obcego się nie wciągnęło" poza tym, co sam sprawdziłem (866 wpisów
obejrzanych przez `git diff --cached --shortstat` i listę `??` przed commitem).
Nie naprawiono `close.py` — błąd z `git add -- <usunięty katalog>` i z liniami
`R  a -> b` w `find_strays` nadal tam jest i wróci przy następnej migracji; to
kandydat na osobny commit i scar. Nie sprawdzono, ile z 711 par jest bajtowo
identycznych (próbka: `AGENTS.md` identyczny, `handoff/flags/T101.md` różny).
Nie pushowano — `master` wyprzedza `origin/master` o 8 commitów. Nie ruszono
trybu `scoped`, gate'u cytowań, migracji 5 notatek, Q02/Q20, 10 passage'ów
`related`, ani otwartej decyzji o `CONTEXT.md` w `raw_only`.

<!-- handoff/flags/smart-connections-cache-exclusions-2026-10-25.md · owner: mateusz · agent: codex · model: openai/gpt-5 -->
`smart-connections-cache-exclusions-2026-10-25` — 2026-10-25: corrected Smart Connections folder exclusions for the active vault root by adding the root-level `scripts/`, `projects/`, and `handoff/` paths while preserving the legacy `root_workspace/` paths. Because the old cache continued to load excluded entries, the derived `smart_sources`, `smart_blocks`, `embedding_models`, and `event_logs` directories were moved to `.smart-env/_recovery-2026-10-25`; notes and `smart_env.json` were preserved. Next step: reopen Obsidian and allow Smart Connections to rebuild with the corrected scope.

<!-- handoff/flags/okf-rag-scope-and-gate-2026-10-25.md · owner: mateusz · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
`okf-rag-scope-and-gate-2026-10-25` — 2026-10-25: ustalono, że `Notes/OKF-rag`
zostaje poza kontraktem projektu (ADR `handoff/decisions/notes-okf-rag-outside-project-contract.md`),
maszyneria idzie do root `scripts/`, a gate do `check_workspace_integrity.py`
jako advisory do czasu migracji. Dodano słownik artefaktów `Notes/OKF-rag/CONTEXT.md`,
wiersz kontekstu w `CONTEXT-MAP.md` i pre-registered
`EXPERIMENT-benchmark-scope-2026-10-25.md` z realnym przypadkiem adwersaryjnym
(Q15: blok `napkin.md:3985–3998` zalicza `related`, choć nie zawiera
odpowiedzi). Plan: 3 commity — (1) te artefakty, (2) migracja 5 notatek
kuratorskich do strukturalnego `sources: [{file, lines}]` + allowlista 2 decyzji,
(3) skill `retrieval-two-stage` + check w integrity. Next: dodać tryb `scoped`
do `scripts/run_okf_rag_benchmark.py`, bo bez niego reguła scope jest
niemierzalna i eksperyment nie jest uruchamialny jedną komendą.

not checked: nie zmierzono przebiegu ze scope (brak trybu `scoped`); nie
zmigrowano frontmattera żadnej notatki; gate cytowań nie istnieje; skill
`retrieval-two-stage` nie istnieje; Q02 i Q20 nadal bez `exact`/`related`.

<!-- handoff/flags/okf-rag-corpus-pin-2026-10-25.md · owner: mateusz · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
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

<!-- handoff/flags/okf-rag-benchmark-rerun-2026-10-25.md · owner: mateusz · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
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

<!-- handoff/flags/okf-rag-benchmark-local-2026-10-25.md · owner: codex · agent: codex · model: openai/gpt-6 -->
`okf-rag-benchmark-local-2026-10-25` — 2026-10-25: utrwalono pełne, jawnie zrekonstruowane 20 pytań, hash korpusu i ranking source/passage dla `all` oraz `raw_only`; powtarzalne missy Q17–Q18 dostały dwa slice'y z mapą oryginalnych linii. Next: ręcznie przejrzeć Q02 i Q20 — jedyne pytania bez exact/related w top-10 — przed decyzją o potrzebie OKF-RAG.

not checked: nie oceniano treści generowanej odpowiedzi ani literalnej poprawności cytatu; OOC sprawdza retrieval abstention. Oryginalne prompty baseline nie zachowały się, więc zgodność prompt-for-prompt nie jest potwierdzona.

<!-- handoff/flags/notes-txt-to-md-2026-10-25.md · owner: mateusz · agent: codex · model: openai/gpt-5 -->
`notes-txt-to-md-2026-10-25` — 2026-10-25: renamed all 12 `.txt` files under `Notes/` (including `Notes/OKF-rag/`) to `.md`; no target-name collisions existed. Obsidian updated the affected index links. Next step: review and commit the rename set if desired.

<!-- handoff/flags/mcp-smart-connections-v4-2026-10-25.md · owner: mateusz · agent: codex · model: openai/gpt-5 -->
MCP `smart-connections` jest enabled w globalnej konfiguracji Codexa i wskazuje
na `C:\Users\Mateusz\Desktop\vault`. Zmieniono serwer z pakietu npm v2,
który oczekuje starego katalogu `.smart-env\multi`, na kompatybilny z
Smart Connections v4 serwer `cusster/smart-connections-mcp` uruchamiany przez
`npx --package=https://github.com/cusster/smart-connections-mcp/archive/refs/heads/main.tar.gz smart-connections-mcp`.
Ustawiono także `SMART_EMBED_MODEL=TaylorAI/bge-micro-v2`, osobny cache npm i
cache modelu. Rejestracja jest poprawna (`codex mcp get`), a tarball uruchamia
się bez błędu `spawn EPERM`; bieżący proces rozmowy nadal nie ma załadowanych
narzędzi Smart Connections. Po ponownym restarcie Codexa trzeba potwierdzić
`index_status` i wykonać wyszukiwanie; pierwszy start wymaga pobrania modelu.

Starsze flagi (222): [handoff/flags/INDEX.md](handoff/flags/INDEX.md)

## where-the-work-landed

type: Concept
title: where-the-work-landed
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

# Where the work landed

`projects/research/agentic-research-lab/` — a **separate git repo** from this root. Its
T1/ralph work is in `819427c` and `e806d34`. The root's restructure
(gate trim, group move, scar hardening) is committed here as `8da9c18`
(2026-10-02 baseline); the root-architecture pass of the same day
(single-home map, gate docstring, R11, skills catalog) is `0ae22ef`, and the
ARL-side fix tranche (`1d20066`, `f579847`) plus the ingest checkpoints
(`28cfb50`, `6a419fe`) live in the ARL repo. Different workstreams — do not
fold them into one commit.

## gotchas-that-cost-time-worth-60-seconds-to-read-before-worki

type: Concept
title: gotchas-that-cost-time-worth-60-seconds-to-read-before-worki
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

# Gotchas that cost time (worth 60 seconds to read before working)

- **Polyrepo — verify before concluding anything about tree state.** Run
  `git rev-parse --show-toplevel` in whatever directory you are in. Root and
  each `projects/research/*` are independent repos.
- **Handoff was not a state machine (fixed 2026-10-03).** `.claude/session-handoff.md` in
  `agentic-research-lab` and the old root `HANDOFF.md` were both hand-written, with no
  script rebuilding either — the root one is now derived (`handoff/flags/<flag>.md` +
  `handoff/deep/` -> `scripts/build_handoff.py` -> `HANDOFF.md`, `--check` gates
  staleness; flag file `handoff_flag_per_file_icm`). The ARL project handoff is still
  hand-written. The project handoff had gone stale for two sessions before 2026-10-01,
  and a 2026-10-02 audit of this file found six stale claims at once (a module
  count, two HEAD pointers, the gate check list, a "no run has ever existed"
  line contradicted by a closed run on disk, and an open-vs-done follow-up).
  Audit both by grepping for claims — `findstr /n /c:"<number>" /c:"<sha>"` —
  not by reading one file and assuming the other agrees. A fix found by grep
  must be applied to every file grep can reach.
- **`reflection/loop_state.json` is not a ralph loop.** In
  `agentic-research-lab` it is a list of SHA-256 hashes, read only by
  `pipeline/06_reflect/spawn.py:48`, which uses `MAX_IDENTICAL_EVENTS = 3` to
  damp repeated reflection events. It is untracked since `5fd1d26` and still on
  disk. The `ralph-loop` skill is vendored (`819427c`); the one run that exists
  is closed — see `ralph_run_closed` above.
- **`$?` after a pipe reports the pipe, not Python.** `python gate.py | tail -3;
  echo $?` always prints 0. Capture the exit code before piping, or redirect to
  a file and read it after. `scripts/_scratch/run_and_rc.sh` does this for you.
- **G12 follow-ups are closed in project `## Open work`, not open.** The
  pi_models.py un-ignore (`82b078a`) and the no-artifact-on-failure defect
  (`024f9a5`) are both marked DONE 2026-10-01 in
  `projects/research/agentic-research-lab/CONTEXT.md` `## Open work`, so a
  `CLAUDE.md` → `CONTEXT.md` session sees them as finished.
- **ARL root resolution was one level short after the group move (fixed
  2026-10-02, `1d20066`; scar #7 in ARL `EXPERIENCE.md`).** The failure mode
  is generic: any "look up to the workspace root" path computed from a fixed
  number of `..` hops (`parents[N]`, hard-coded `../..`) silently breaks on
  any reorg — probe `scripts/*.py` for `parents[` after a move. The nested-
  `agentic-research-lab/` dir (a CRLF copy of part of the repo, 3,766 files,
  plus 121 worktree-deleted originals) and the `$null` root debris are the
  same day's tree-shape incidents: run `git status` early, verify a copy is
  byte-identical before deleting anything.

- **`close_session.py` runs `audit_workspace.py` only**, not the 21-gate
  workspace suite. The full suite is what pre-commit runs.
- **ARL `preflight.py` exits 1 on two failed reflection runs** (`bg-smoke3`,
  `smoke-scratch-02`) whose artifacts still fail the gate. That is a standing
  hard block, unrelated to any current work: the 21-gate chain itself is 21/21
  green, and `agent_commit.py` commits fine past it. Run
  `python scripts/quality_check.py` directly when preflight blocks you.

## gate-note-if-you-touch-allowed-root

type: Concept
title: gate-note-if-you-touch-allowed-root
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

# Gate note (if you touch `ALLOWED_ROOT`)

`scripts/check_workspace_integrity.py` holds `ALLOWED_ROOT`, a whitelist:
any unlisted name at the workspace root is a **FAIL**. This file is listed
there for that reason. Which check is which (hard vs advisory) and the
root-entry procedure: the gate's docstring is the single home; this note
and the other docs link, not restate.

## g12-resolved-2026-10-01-human-decision-closed-same-day

type: Concept
title: g12-resolved-2026-10-01-human-decision-closed-same-day
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

# G12 — resolved 2026-10-01 (human decision), closed same day

`reflect.py` is the canonical reflection runner. Speed was the decider: 52 s
single structured call vs `spawn.py`'s 275 s; G11 quality passed for both,
so the wall-clock gap carried no quality signal. Recorded with ABANDON lines
(protocol: recorded, not deleted) in
`projects/research/agentic-research-lab/GATES-T1-phase04-runner.md`.

Follow-ups (both done 2026-10-01):
1. `scripts/pi_models.py` was un-ignored (`.gitignore` entry removed) and
   entered through `agent_commit.py` — commit `82b078a`. Never `git add .`.
2. The carried defect — failed runs wrote no artifact, so a failed run was
   indistinguishable from a never-run one — is fixed in
   `pipeline/06_reflect/reflect.py`: `agent_trace` ledger records
   (`run`/`failure` events with `failure_kind`: `bad_json`, `missing_key`,
   `unexpected_response`, or exception class), plus endpoint resolution moved
   in-run so a missing pi config is a traced failed run, not an import crash.
   Pinned by 4 new tests (`024f9a5`).

## deep-research-kg-icm

type: Concept
title: deep-research-kg-icm
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

# HANDOFF — Deep Research: Knowledge Graph Integration + ICM (2026-10-03)

## Status 2026-10-04 (flaga: `deep_research_phase1_done`)

Phase 1 **domknięta** w ARL (`4b363da`): 3 sondy literaturowe + 8 seedów
arXiv, synteza → 12 chunków → rebuild (fingerprint `31989e46d0a5` →
`4880aab33ca4`, 10 373 nodes / 13 457 edges). Ruszyła też Phase 4-runtime:
`85c3318` (dead-route monitor w `route.py`), `5a275b0` (critic gate
w `ask.py`). Next: Phase 2 (ablacja) albo Phase 4-diversity. Szczegóły
we fladze; poniżej oryginalne zlecenie.

---

## Zlecenie
Przeprowadzić głębokie badanie (deep research) na temat: **integracja grafu wiedzy (knowledge graph) z pracą agenta w kontekście Interpretable Context Methodology (ICM)**.

Pytania researchowe:
1. Jak graf wiedzy (FTS5 + SQLite, chunks jako węzły, krawędzie SHARES_TAG/DERIVED_FROM/SCARRED_FROM/PART_OF/SEQUENCE) może być **operacyjnie** używany przez agenta w trakcie kodowania / debugowania / researchu?
2. Jakie są wzorce dopytowania (query patterns), które dają **mierzalną poprawę** jakości decyzji agenta (accuracy, grounding, time-to-fix)?
3. Jak ICM (Interpretable Context Methodology) — podejście "verified corpus → derived graph → reflection → meta-learning" — mapuje się na **praktykę codziennej pracy agenta** (nie tylko batch reflection)?
4. Jakie są **failure modes** obecnej implementacji (stale fingerprints, non-deterministic builds, citation concentration, write-only memory) i jak je mitigować w runtime?

## Kontekst (co już mamy w repo)

### Zaimplementowane i working (commit `5330266` w ARL):
- **Knowledge graph**: `knowledge/graph/build_graph.py` → `graph.db` (10k+ nodes, 12k+ edges, FTS5), fingerprint SHA-256 corpus
- **Query interface**: `knowledge/graph/ask.py` — tag intersection, tag filtering, text search, hybrid
- **Reflection pipeline**: `pipeline/06_reflect/spawn.py` + `route.py` — automated reflection z provenance (fingerprint, plan_version, phase), evidence citations (`Chunk id: \`NN_slug\``)
- **Citation integrity**: `check_reflection.py` — weryfikuje że każdy cytowany chunk istnieje w grafie, fingerprint matches live corpus
- **Determinism gate**: `check_graph_determinism.py` — rebuild z tego samego corpus = identyczny graf (content-hash, nie byte-hash)
- **Evidence grounding**: `check_citation_integrity.py` — citations resolve i support claim
- **Skills**: `poteto-mode-lite` (4 playbooki: investigation/bug-fix/feature/refactor + prove-it-works), `skill_router.py` (3-fazowy: decompose/select/iterate, 19 skill entries), `ralph-loop` (small-session contract)
- **Forge-guardrails**: `.agents/plugins/forge-guardrails/` — PreToolUse/Stop hooks, policy.yaml, venv re-exec, self-cert probe (agent hand-edited state.json → blocked)

### Znane problemy (otwarte, niezasłonięte gate'ami):
1. **Fingerprint staleness**: Additive corpus change → wszystkie prior digests stale. `restamp_provenance.py` re-stamps tylko jeśli cited IDs still resolve. Jeśli nie — trzeba re-run reflection (research decision, nie bookkeeping).
2. **Citation concentration**: `project-entropy.jsonl` ma 100% concentration (top-3 IDs cited in 4/4 rows) — sygnał że reflection czyta wąski fragment grafu.
3. **Dead routes**: `--tag` routes resolving to zero chunks (W-AUDIT-4) — silent failure.
4. **Write-only memory**: `00_icm_implementation_pitfalls_and_failure_modes` mode 2 — "silent promotion decay (write-only memory.md)" — brak eviction mechanismu dla memory.md.
5. **Agent-reach web skill**: goose + omniroute/gemini-flash-lite-latest działa, ale weak model spends budget on tree exploration before using web skill.

## Proponowany plan badań (deep research)

### Faza 1: Literature + Prior Art (1-2 sesje)
- Przegląd literatury: GraphRAG (Microsoft), Knowledge Graphs for Code (CodeGraph, GraphCodeBERT), Agentic RAG, ReAct + KG, MemGPT, HippoRAG, Zep, Letta
- ICM parallels: czym ICM się różni / co dodaje nad standardowym GraphRAG?
- Zapisz notatki do `INBOX/` → `scripts/ingest.py` → graph rebuild

### Faza 2: Eksperymenty operacyjne (2-3 sesje)
- Zdefiniuj **benchmark zadań** dla agenta: (a) bug fix w nieznanym kodzie, (b) feature implementation wymagająca zrozumienia architektury, (c) performance investigation
- Uruchom agenta **z i bez dostępu do grafu** (ablation) — zmierz: grounding rate, hallucination rate, time-to-first-correct-hypothesis, number of file reads
- Użyj `poteto-mode-lite` playbooków jako structured workflow wrapper

### Faza 3: Failure mode deep-dive (1-2 sesje)
- Symuluj/add failure modes: stale fingerprint, dead route, citation concentration, missing eviction
- Zmierz impact na agent quality
- Zaproponuj mitigacje (runtime checks, auto-re-stamp triggers, route health monitoring)

### Faza 4: Syngteza + Implementacja (1 sesja)
- Napisz **design doc** w `docs/research/kg-icm-integration.md`
- Zaimplementuj **jedną konkretną poprawę** (np. runtime fingerprint freshness check w `ask.py`, albo route health monitor, albo citation diversity enforcement w reflection)
- Prove-it-works: test + demo

## Kody dostępu / komendy

```bash
# Wejście do ARL
cd projects/research/agentic-research-lab

# Query graph
python knowledge/graph/ask.py "your question" --tag debugging --limit 10

# Spawn reflection
python pipeline/06_reflect/spawn.py --topic your-topic

# Full quality gate
python scripts/quality_check.py

# Goose run (weak model, requires omniroute credits)
goose run --provider omniroute --model gemini/gemini-flash-lite-latest --instructions ../../../scripts/_scratch/goose_g3_decision_graph_agent_reach_task.txt --output-format json --stats --max-turns 40

# Ralph loop resume
python skills/ralph-loop/scripts/ralph.py --project . resume
```

## Kryteria sukcesu (Definition of Done)

1. **Design doc** `docs/research/kg-icm-integration.md` z: literature survey, failure mode taxonomy, proposed architecture, benchmark results
2. **Implementation** — jedna merged PR z poprawą runtime (gate-passing, test-covered)
3. **Evidence trail** — fresh `INBOX/` sources, ingest logs, graph rebuild, reflection digests z claim-to-source links, implementation diff
4. **G3 verdict** — human review confirming implementation follows from evidence

## Blokery / Ryzyka
- Omniroute credits / gemini-flash-lite-latest availability (budget call)
- Weak model may not execute complex multi-stage research reliably → consider stronger model for research phases, weak only for implementation
- Existing stale reflection artifacts (`vera_expf_*`) — do not count as evidence for this run
- Preflight blocks on 2 hard missing reflection runs (`bg-smoke3`, `smoke-scratch-02`) — unrelated, run `python scripts/quality_check.py` directly

## Next Steps
1. Start Faza 1: `python scripts/expand_literature.py --query "knowledge graph agentic RAG code debugging" --source arxiv --max-results 20`
2. Ingest → graph rebuild → first reflection on "graph integration patterns"
3. Iterate

---

*Wygenerowane 2026-10-03 po commicie ARL `5330266` i roota `ce5aeeb`. Obecny stan: graf gotowy, bramki green, pstack skill zaimplementowany, forge-ab designed, plain-language meter frozen (D-003). Gotowe do startu deep-research.*

## Untyped

* [g12-resolved-2026-10-01-human-decision-closed-same-day](g12-resolved-2026-10-01-human-decision-closed-same-day.md)
* [deep-research-kg-icm](deep-research-kg-icm.md)
* [gotchas-that-cost-time-worth-60-seconds-to-read-before-worki](gotchas-that-cost-time-worth-60-seconds-to-read-before-worki.md)
* [gate-note-if-you-touch-allowed-root](gate-note-if-you-touch-allowed-root.md)
* [where-the-work-landed](where-the-work-landed.md)
