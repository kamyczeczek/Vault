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

<!-- handoff/flags/workspace-gate-repair-2026-10-25.md · owner: mateusz · agent: codex · model: openai/gpt-5 -->
`workspace-gate-repair-2026-10-25` — 2026-10-25: repaired root gate data after the Notes extension migration: restored `.opencode/agents/answerpilot.md`, removed the stale `handoff/state_description/` route from `CLAUDE.md`, moved the unexpected `Welcome.md` and `test.md` to the Recycle Bin, rebuilt `handoff/status/STATUS.md`, and rebuilt the seven stale project `MAP.md` views. Next step: run the final gates and commit the complete change set.

<!-- handoff/flags/smart-connections-cache-exclusions-2026-10-25.md · owner: mateusz · agent: codex · model: gpt-5 -->
`smart-connections-cache-exclusions-2026-10-25` — 2026-10-25: corrected Smart Connections folder exclusions for the active vault root by adding the root-level `scripts/`, `projects/`, and `handoff/` paths while preserving the legacy `root_workspace/` paths. Because the old cache continued to load excluded entries, the derived `smart_sources`, `smart_blocks`, `embedding_models`, and `event_logs` directories were moved to `.smart-env/_recovery-2026-10-25`; notes and `smart_env.json` were preserved. Next step: reopen Obsidian and allow Smart Connections to rebuild with the corrected scope.

<!-- handoff/flags/retrieval-answer-contract-2026-10-25.md · owner: mateusz · agent: codex · model: openai/gpt-5 -->
`retrieval-answer-contract-2026-10-25` — 2026-10-25: dodano kontrakt odpowiedzi
retrieval, porównano 15 wariantów zapytań dla pięciu raw-only missów i wdrożono
generator powtarzalnych source slices z manifestem i `origin_hash`. Slice
retrieval odzyskał właściwy temat jako top-1 w `5/5` przypadków, a `rg`
potwierdził źródłowe passage jako `direct`. Next: przetestować generator na
jednym dużym imporcie `napkin.md`.

not checked:
- pełny folder `Notes/OKF-rag` nadal ma stare wskaźniki Smart Connections po usuniętych prototypach;
- benchmark wszystkich 20 pytań nie został jeszcze ponownie uruchomiony na wygenerowanych slice'ach.

<!-- handoff/flags/okf-rag-synthesis-draft-2026-10-25.md · owner: mateusz · agent: codex · model: openai/gpt-5 -->
`okf-rag-synthesis-draft-2026-10-25` — 2026-10-25: utworzono syntezy, decyzję i raporty retrieval; dodano zakresy linii źródłowych, wykonano benchmark blokowy 20 pytań, kontrolę raw-only oraz ręczną kontrolę 10 brakujących trafień. Wszystkie brakujące treści istnieją w dużych importach `okf-rag.md`, `napkin.md` i `okforge.md`; problem dotyczy retrieval/segmentacji, nie braku wiedzy. Następny krok: porównać zapytania naturalne, z nazwą narzędzia i z dokładnym nagłówkiem.

<!-- handoff/flags/okf-rag-benchmark-local-2026-10-25.md · owner: codex · agent: codex · model: openai/gpt-6 -->
`okf-rag-benchmark-local-2026-10-25` — 2026-10-25: utrwalono pełne, jawnie zrekonstruowane 20 pytań, hash korpusu i ranking source/passage dla `all` oraz `raw_only`; powtarzalne missy Q17–Q18 dostały dwa slice'y z mapą oryginalnych linii. Next: ręcznie przejrzeć Q02 i Q20 — jedyne pytania bez exact/related w top-10 — przed decyzją o potrzebie OKF-RAG.

not checked: nie oceniano treści generowanej odpowiedzi ani literalnej poprawności cytatu; OOC sprawdza retrieval abstention. Oryginalne prompty baseline nie zachowały się, więc zgodność prompt-for-prompt nie jest potwierdzona.

<!-- handoff/flags/notes-txt-to-md-2026-10-25.md · owner: mateusz · agent: codex · model: openai/gpt-5 -->
`notes-txt-to-md-2026-10-25` — 2026-10-25: renamed all 12 `.txt` files under `Notes/` (including `Notes/OKF-rag/`) to `.md`; no target-name collisions existed. Obsidian updated the affected index links. Next step: review and commit the rename set if desired.

<!-- handoff/flags/mcp-smart-connections-v4-2026-10-25.md · owner: mateusz · agent: codex · model: gpt-5 -->
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

<!-- handoff/flags/vault-single-repo-2026-10-24.md · owner: mateusz · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
`vault-single-repo-2026-10-24` — 2026-10-24: rozstrzygnięty spór o root vaulta. `Desktop\vault` jest jedynym vaultem i jedynym repo; `root_workspace` staje się podfolderem bez własnego `.git`. Cztery wpisy (`.git`, `.obsidian`, `.smart-env`, `Notes`) są vault-owned i bramka egzekwuje dla nich XOR między `ROOT` i `VAULT`. `Notes/` będzie trackowane w prywatnym repo (`kamyczeczek/vault`), `.smart-env/` odtwarzane od nowa, zagnieżdżony `.gitignore` zostaje. Historia: `59faa7d` przyjęty jako baseline, `697b9e3` tagowany jako `archival-697b9e3` **przed** bundle'em. Decyzje: `brain/decisions/ADR-006-single-vault-single-repo.md`, `ADR-007-git-baseline-and-remote.md`. Kolejne kroki: gate XOR (osobny commit), `_repo_rel()` w `scripts/` przed migracją, migracja jako ostatni commit, `gh repo create --push`.

not checked:
- czy `Desktop\ARCHIVE\ROOT` zawiera cokolwiek, czego nie ma w `59faa7d` — nie porównywano; przyjęto, że to starszy, inny workspace.
- czy `Notes/` nie zawiera materiału, którego właściciel nie chce w prywatnym repo — decyzja właściciela: trackowane.
- czy plugin Smart Connections da się zainstalować w tym vaulcie — w żadnym z dwóch vaultów nie ma katalogu `plugins/`, więc `.smart-env/` jest dziś sierotą.

<!-- handoff/flags/vault-repo-rel-paths-2026-10-24.md · owner: mateusz · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
`vault-repo-rel-paths-2026-10-24` — 2026-10-24: przygotowanie `scripts/**` na repo, którego root jest o poziom wyżej (ADR-006). Nowy `scripts/git_paths.py` (`repo_prefix`, `repo_rel`) normalizuje wyjście gita: `git status --short` i `--name-only` drukują ścieżki względem **repo root**, a `ls-files` i pathspecs względem **cwd** — dopóki ROOT był repo rootem, obie bazy się pokrywały. Podłączone w `close.py` (`find_strays`, `_is_staged_deletion`), `pre_close_check.py` (uncommitted work vs `--include`), `scan_secrets.py` (`staged_files`) i bramce R19 (nowe flagi). Bez tego po migracji `find_strays` widziałby `root_workspace/handoff/flags/x.md` i każdy commit byłby czerwony, a R19 po cichu przestałby widzieć nowe flagi (advisory, więc bez błędu). Test `scripts/test_git_paths.py` buduje repo z podkatalogiem w tempie i dowodzi asymetrii: z `sub/` status zwraca `rootfile.txt` i `sub/inner.txt`, `ls-files` zwraca `inner.txt`. `--include` przyjmuje teraz katalog: `find_strays` dopasowuje zawartość po prefiksie, więc 686 ścieżek nie musi wejść w jeden argv.

not checked:
- `build_state.py`, `upgrade_sessions_report.py`, `verify_session_claims.py` czytają `git status` bez normalizacji — używają wyniku tylko do wyświetlania/hasha, nie do porównania ze ścieżką workspace'u; nie ruszane.
- pełny przebieg `pre_close_check.py` i `scan_secrets.py --staged` na żywym repo po migracji — dopiero po przeniesieniu `.git`, bo dziś prefiks jest pusty i ścieżka nowa i stara dają ten sam wynik.

<!-- handoff/flags/vault-migrated-2026-10-24.md · owner: mateusz · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
`vault-migrated-2026-10-24` — 2026-10-24: `Desktop\vault` został single-vault single-repo. `.git` przeniesiony z `root_workspace/` do `vault/`; `root_workspace` jest teraz podfolderem, nie repozytorium. `Notes/` przeniesiony do vaultha; `.smart-env/` istnieje jako pusty katalog w vaulcie (placeholder na future Smart Connections reinstall — plugin nie jest dziś zainstalowany, więc indeks się nie migruje). Nowy `vault/.gitignore` trzyma tylko wpisy vaulta, zagnieżdżony `root_workspace/.gitignore` pozostawiony (wzorce są poprawne względem workspace'u). `archival-697b9e3` i `baseline-59faa7d` w vaulcie, bundle w `Desktop\`. Następne kroki: gh repo create + push, reinstall obsidian-git, clear embeddings.

not checked:
- czy smart_env.json (1 plik, wykluczony) istnieje w `.smart-env/` — plik nie został przeniesiony, tylko usunięty; jeśli istnieje na dysku poza repo, nie został utracony.
- czy `handoff/status/STATUS.md` nie zawiera starej ścieżki `root_workspace` w linkach — wymaga checku po pushu.

<!-- handoff/flags/vault-layout-root-2026-10-24.md · owner: mateusz · agent: opencode · model: omniroute/gemini/gemini-flash-lite-latest -->
`vault-layout-root-2026-10-24` — 2026-10-24: adopt vault = root_workspace layout in ALLOWED_ROOT, CLAUDE.md, and STATUS.md; include pending .gitignore + .smart-env/smart_env.json from prior Smart Connections config session. Removes dead `vault` entry; declares `.obsidian`, `.smart-env`, `Notes` as root entries; rebuilds generated views.

not checked:
- whether `.obsidian/` or `Notes/` should be tracked (left untracked per policy; only root layout allowed in ALLOWED_ROOT).

<!-- handoff/flags/vault-layout-and-git-bootstrap-2026-10-24.md · owner: mateusz · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
`vault-layout-and-git-bootstrap-2026-10-24` — 2026-10-24: root workspace re-bootstrapped after the vault move. `.projects/` renamed back to `projects/` (CLAUDE.md, AGENTS.md and all 20 routing links already said `projects/`; no file referenced the dot form), gate went from 25 problems to 3. `git init` plus `core.hooksPath hooks` restore the pre-commit gate; this is the new baseline commit. Memory index re-ingested (lag 1d13h) and `brain.db` rebuilt (R21: 18 sourceless rows cleared). Gate green: 38 declared entries, 7 projects, all routes resolve, retrieval 15/15. Next: decide the single Obsidian vault root, then fix `session_ground_truth.py` at its real path.

History is unrecoverable, verified three ways: `.git/` was an empty hidden
directory (0 files, emptied 2026-10-24 17:18–17:41), none of the 6 candidate GitHub
repos holds this tree (`obsidian-vault` is notes only, last push 2026-10-23), and
`Desktop\ARCHIVE\ROOT` is a different, older workspace (last write 2026-09-17).

not checked:
- whether `.obsidian/`, `.smart-env/` and `Notes/` belong to this folder at all:
  a second Obsidian vault appeared one level up (`Desktop\vault`) at 16:39 today,
  after this folder was opened as a vault at 15:54. Those three were deliberately
  left UNTRACKED. Decide the single vault root before committing them.
- `handoff/state_description/` (32 MB of txt dumps from the one-off
  `scripts/oneoff/move_state_description.py` bridge) is now gitignored, not purged.
- this commit is a new baseline, not a continuation of the lost history; nothing
  before it can be recovered from this machine.
- `scripts/_scratch/sessions/session_ground_truth.py` does not exist; the file the
  prior plan named is at `scripts/_scratch/sessions/01_tools/session_ground_truth.py`
  and its 4 defects are still unverified.
- bootstrap exception, named rather than hidden: `close.py --include` accepts
  individual files, not directories, and the baseline is 686 files (≈40 KB of
  argv, over the Windows limit). So the commit was authorized the documented
  outside-close way — an explicitly minted `.commit-approved` (guard docstring
  sanctions it) — and `git commit -F` carried this exact subject and body.
  `hooks/pre-commit` still ran the full gate and every guard unchanged.

<!-- handoff/flags/obsidian-repro-needed-2026-10-24.md · owner: mateusz · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
`obsidian-repro-needed-2026-10-24` — 2026-10-24: trzy awarie po stronie Obsidiana są **nadal niepotwierdzone** i nie są „naprawione”. (1) Grey screen (sesje 6, 8): krok odtworzenia — otworzyć `Desktop\vault` w Obsidianie, otworzyć notatkę i graf, sprawdzić, czy renderuje; przegląd 2026-10-31, właściciel Mateusz. (2) Hybrid Search „server did not start” (sesja 8): odtworzyć przy zainstalowanym pluginie i wkleić pierwszy błąd z konsoli deweloperskiej; ten sam przegląd. (3) Fine-grained PAT → HTTP 403 przy Obsidian Git (sesja 24): odtworzyć **po** reinstalacji obsidian-git — dziś nie ma gdzie, bo w żadnym z dwóch vaultów nie istnieje katalog `plugins/`; klasyczny PAT działa, fine-grained nie, przyczyna nieznana.

Stan poza repo, posprzątany w tej sesji (bez commita, bo to nie pliki repo): usunięty martwy wpis MCP `smart-connections` z `~/.config/opencode/opencode.jsonc` (wskazywał na nieistniejący `vault\.obsidian\plugins\smart-connections\main.js`); `~/.pi/agent/trust.json` ma teraz tylko bieżącą ścieżkę `Desktop\vault\root_workspace` (usunięte `Desktop\root_workspace` i literówka `root_worksapce`); usunięty osierocony worktree `kilo/worktree-pool/.../catnip-mantis` (3,8 MB, 565 plików, `.git` wskazywał na nieistniejące `Desktop\root_workspace`); usunięte `handoff/state_description/` (32,4 MB, 79 plików, w pełni pochodne); obie instalacje opencode to 2.1.4 — rozjazd wersji zniknął sam, hermes wygrywa PATH.

not checked:
- cztery rzekome błędy w `session_ground_truth.py` — narzędzie odpowiada na `--help`, ścieżka w docstringu poprawiona w miejscu, ale plik jest pod `scripts/_scratch/*` (gitignored), więc poprawka nie ma commita i nie jest wersjonowana.
- `~/.config/opencode/opencode.jsonc` ma uszkodzoną strukturę w bloku `nara` (dwa klucze `"models"`, wiszący przecinek) — nie naprawiane, bo to nie dotyczy tej sesji; jeśli opencode parsuje plik luźno, część providerów może nie działać.
- czy grey screen wraca po migracji vaulta — wymaga GUI, data przeglądu wyżej.

<!-- handoff/flags/gate-vault-owned-xor-2026-10-24.md · owner: mateusz · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
`gate-vault-owned-xor-2026-10-24` — 2026-10-24: bramka przestaje traktować `.git`, `.obsidian`, `.smart-env` i `Notes` jako wpisy workspace'u. Nowy zbiór `VAULT_OWNED` + R1b egzekwuje dokładnie jedno miejsce (ROOT albo VAULT — „oba" i „żaden" to FAIL); R1 nie zgłasza ich już jako stray w żadnym z dwóch miejsc, bo miejsce jest własnością R1b. `CLAUDE.md` deklaruje cztery wiersze `../` (bez tego druga połowa kontraktu R1 nie istnieje), a `test_gate_allowlist_parity.py` sprawdza teraz także deklarację vault-owned. To zaostrzenie, nie wyciszenie: przed migracją wszystkie cztery leżą w ROOT i XOR przechodzi, po migracji w VAULT i XOR nadal przechodzi — nie ma okna z czerwoną bramką. Stub `root_workspace\.obsidian` (untracked, pusta karta) usunięty przed commitem, żeby `.obsidian` występował tylko w vaulcie.

not checked:
- R16 advisory: ten commit dotyka `scripts/**`, a `queries.jsonl` w `_scratch/sessions/05_store` jest starszy niż 30 min — ostrzeżenie zostaje otwarte do czasu realnego zapytania do pamięci sesji.
- czy inne skrypty czytają `ALLOWED_ROOT` i zakładają w nim `.git` — sprawdzone tylko `test_gate_allowlist_parity.py`; pełny przegląd należy do commita `_repo_rel()`.

<!-- handoff/flags/gate-advisories-deferred-2026-10-24.md · owner: mateusz · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
`gate-advisories-deferred-2026-10-24` — 2026-10-24: pięć otwartych pozycji zostaje **świadomie odłożonych**, nie zamkniętych. (1) R16 advisory: commit dotykający `scripts/**` bez świeżego `queries.jsonl` i bez „query” w temacie — jedyne uczciwe domknięcie to realne zapytanie do pamięci sesji, więc advisory zostaje do najbliższej sesji, która tej bramy faktycznie użyje. (2) R19 `did-sessions-default-5`: commit `1f1937f` ma temat bez roku, więc dopasowanie tokenów nie łapie go; bramka **nie jest** zmieniana (S62), a przepisanie historii byłoby droższe niż ostrzeżenie. (3) `direction_changes` w `session_digest.py:542` zwraca `brak reguły w rules-v1`, bo `classify_cards` nie ma dla niego gałęzi — sekcja istnieje i nigdy się nie wypełni; dopóki nie ma reguły opartej na polach karty i cytacie z `ending_evidence`, jawne `not_checked` jest uczciwsze niż dorabianie osądu. (4) `losses.dup` jest jawnie `not_extracted` (`session_digest.py:697`), zgodnie z ADR-005 — ciche zero byłoby kłamstwem; ekstrakcja wymaga definicji „dupa” w transkrypcie. (5) `--classify` działa tylko na rules-v1 (`CLASSIFIER_BACKEND="rules"`, `model_calls: 0`); backend modelowy odłożony świadomie.

not checked:
- czy R19 da się wyciszyć bez zmiany progu — nie: jedyne legalne wyjście to commit z tematem zawierającym token flagi, a `1f1937f` jest już w historii.
- czy reguła `direction_changes` jest w ogóle wyprowadzalna z obecnego schematu karty — nie sprawdzono; wymaga przeglądu `make_judgment` i pól `ending_evidence`, co jest osobną sesją.
- definicja `losses.dup` — brak; bez niej licznik mierzyłby coś innego niż nazwa.

<!-- handoff/flags/codex-loader-2026-10-24.md · owner: mateusz · agent: codex · model: cx/gpt-5.6-luna-max -->
`codex-loader-2026-10-24` — 2026-10-24: `scripts/agent_sessions.py` rozszerza loader o Codex Desktop (`~/.codex/sessions/`, JSONL + Zstandard fallback), `scripts/extract_did.py` zachowuje wiadomości/narzędzia/outputs z Codex, `scripts/did_sessions.bat` domyślnie zlicza 5 sesji zamiast 1. Test `test_agent_sessions.py` zielony; failure na Hermes DB jest ignorowany zamiast przerywać eksport. Również w `agent_sessions.py`: zabezpieczono `HERMES_DB.exists()` przed OSError — bez tego uprawnieniowy błąd na niektórych maszynach przerywałby cały loader. `codex` dodany do `SUPPORTED_AGENTS`.

not checked:
- czy pliki `.jsonl.zst` z Codex mają pełny schemat sesji (opencode-style) — wymaga audytu przykładowego pliku na maszynie właściciela.
- czy `extract_did.py` obsługuje zrosty z wieloma plikami w jednej sesji — nie testowano przypadku, w którym jeden dzień ma >1 rollout.

<!-- handoff/flags/close-include-whole-tree-2026-10-24.md · owner: mateusz · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
`close-include-whole-tree-2026-10-24` — 2026-10-24: `close.py --include` rozumie katalog i całe drzewo. `find_strays` dopasowuje zawartość katalogu po prefiksie (bez rozwijania 686 ścieżek w jeden argv) oraz traktuje `.` jako „cały workspace jest zmianą" — jawnie, nie po cichu: to jedyny sposób, w jaki strukturalna migracja (przeniesienie `.git`, rename 686 plików) może przejść przez transakcję close bez ręcznego mintowania `.commit-approved` (S86). Domyślne zachowanie bez `--include` / z listą plików jest bez zmian — stray nadal blokuje commit. Test w `scripts/test_git_paths.py` buduje repo w tempie: bez `--include` → 2 strays, `--include .` → 0, `--include sub` → tylko plik poza katalogiem.

not checked:
- `--include .` w realnej migracji — sprawdzony dopiero w commicie migracyjnym; jeśli stray pojawi się mimo to, commit padnie i to jest poprawne zachowanie.
- czy `git add --intent-to-add .` jest potrzebny (S67 dotyczy untracked plików, nie katalogów) — nie testowano na katalogu z untracked treścią.

<!-- handoff/flags/test-memory-index-format-restored-2026-10-23.md · owner: opencode · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
`test-memory-index-format-restored-2026-10-23` — 2026-10-23: **`test_memory_index.py` is green (33/33).** The 2026-10-21 restructure removed `format_results`, `format_brief`, `get_chunk` and `print_usage` from `memory_index.py` but left the regression file importing them, so the suite died at import and its four guards were dead. Restored all four helpers and wired them back into `query --full` / default `query`, `get`, and `stats --usage`; `--with-context` now renders again as `(+Nctx)` in the brief view, which the inline rewrite had silently dropped.

Evidence:
- `scripts/memory_index.py` — `format_results`, `format_brief`, `get_chunk`,
  `print_usage`; `query` prints the brief/full views, `get` drills via
  `get_chunk` (None → exit 1), `stats --usage` delegates counts/window/terms to
  `print_usage` and keeps the usage-rate metrics.
- `scripts/test_memory_index.py` — CLI miss checks read `main()`'s return value
  (`main` returns int; it does not raise `SystemExit` on a miss).
- `python.exe scripts/test_memory_index.py` — 33/33, all checks passed.
- `check_workspace_integrity.py` — OK; freshness OK; retrieval_eval hit@5=1.000
  MRR=0.577; drift OK (10 stores).

not checked: the `format_results` body path prefers a real `snippet` key and
otherwise falls back to the 400-char `_evidence_snippet`, so its per-hit cost is
unchanged from the inline version; no end-to-end `--rebuild` cost measured.

<!-- handoff/flags/session-digest-ab-2026-10-23.md · owner: opencode · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
`session-digest-ab-2026-10-23` — 2026-10-23: **L0 unproven/closed; L1 is a
selection index, not an analysis layer.** A/B on one real question:
*"what happened with `--classify` — candidate count, promotion, cause, next
step?"* Same 3 sessions (review/promotion, classify, commit), three corpora.

| Corpus | Content | Size | Read | Score |
|---|---|---|---|---|
| P (plan A) | L1 cards + 3 full bodies | 270 040 B | 1 828 / 5 670 lines | 4/4 facts |
| Q (plan B) | `did` for the same 3 | 180 308 B | 3 726 / 3 726 | 4/4 + 3 extra |
| R (L1 only) | 3 cards, no bodies | 3 913 B | 147 / 147 | 0/4 — "brak w materiale" |

Scored facts: 6 candidates (4 `open_threads` + 2 `contradictions`); 0/6 true
→ no promotion; cause `session_facts._marker_scan` + `not_checked` in
`OPEN_MARKERS`; next step rules-v2 + `review_ref`. Q additionally found
40 sessions / 93 children, smoke 0 candidates, and the pre-`--classify` state.
L0 contributed nothing: 781 B, all `_brak_`.

Decision: do not build `--profile llm`; do not promote L0. Keep L1 as the
selector (filter `session_cards.json` by `files`/`flags`), then export 2–5
sessions; use `did` or the selected bodies for analysis. Recorded in
`brain/decisions/ADR-005-session-digest-fact-judgment.md` ("Wynik A/B") and
`docs/session-digest-GATES.md` G14.

Reproduction (corpora are one-off, under `%TEMP%`, never committed):

```text
python scripts/session_digest.py 10 --out-dir %TEMP%\digest-probe-10
python scripts/session_digest.py --classify --count 10 --out-dir %TEMP%\digest-probe-10
python scripts/extract_did.py 6 -o %TEMP%\ab-test\did6.md
python scripts/agent_sessions.py export opencode ses_e9ee3df48ffeI2L1QarEEqiSUz -o %TEMP%\ab-test\body-1.md
python scripts/agent_sessions.py export opencode ses_e9ef9abd8ffeilAF4R1y6kPPWq -o %TEMP%\ab-test\body-2.md
python scripts/agent_sessions.py export opencode ses_e9efe1ee0ffeT9xzjalxF9309H -o %TEMP%\ab-test\body-3.md
```

`%TEMP%\ab-test` is disposable; only the numbers above are the evidence.

not checked: n=1 question, 3 sessions, one model; P and Q differ in content
filter (P keeps read-only calls and payloads, Q drops them); scoring was not
fully blind because the formats are recognisable. The design session
(574 KB in `did`) was outside the test, so the "rejected alternatives"
question was not measured; its cost gap would only favour `did` further.

<!-- handoff/flags/session-brief-valuable-2026-10-23.md · owner: opencode · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
`session-brief-valuable-2026-10-23` — 2026-10-23: **`session_brief.py` built;
committed in `e98237a`.** The tool reads the N latest main sessions, reuses the L1 cards
from `session_digest.py` for selection (commits, files, flags, tests, micro) and
the `did` event stream from `extract_did.py` for content, then writes a compact
per-session brief. No model call and no free-form summary: every line is a
mechanical fact, a quote, or a truncated tool excerpt.

Selection with `--valuable` drops durably excluded meta-sessions, micro sessions
with no delta, and sessions with no mutating event and no commit/flag/test
signal. Read-only `bash`/PowerShell noise is dropped, including `--help`,
`--version`, null redirects, temp-path writes, and fixture-like flag ids.
Quoted spans are stripped before the mutation test, so a `>` or `rm` inside a
pattern does not make `grep`/`Select-String` look mutating, and `rm`/`mv`/`cp`
only match as commands, not inside ids like `git-rm`. `skill` calls are not
actions. Session `flags` are split into present and `absent now` (the latter
replaces the old `flags missing` line, which read like loss instead of
retirement).

Evidence:
- `scripts/session_brief.py` — `--last N`, `--valuable`, `--agent`, `--days`,
  `--until`, `-o/--out`, `--session-kb` (8), `--total-kb` (120),
  `--max-actions` (8). Default output:
  `scripts/_scratch/sessions/02_products/session_brief.md`.
- `scripts/session_brief.bat` — wrapper: `session_brief.bat N [OUT]`.
- `scripts/test_session_brief.py` — stdlib-only helper tests; `OK session_brief`.
- Sample run: `--last 20 --valuable --until "2026-10-23 05:00:00"` selected
  18/20 (skipped 1 meta, 1 micro), 70,001 bytes; `--last 10 --valuable` selected
  8/10, 27,722 bytes. The `--until` keeps the in-flight session out of the
  sample; without it the running session becomes #1 and its "Ending" is just the
  latest reply, not an ending.
- `scripts/_scratch/sessions/CLAUDE.md` and `02_products/CONTEXT.md` — product
  routing rows (derived shelf docs).

not checked: the selector is heuristic — a session whose only mutating calls are
`python -c` probes or temp-dir experiments can still pass; `2>/dev/null` counts
as an attempted redirect (on PowerShell it really does try to write
`C:\dev\null`); `--last N` filters inside the N-session window instead of
backfilling to N valuable sessions; the sample was inspected by eye, not graded
against a gold set; nothing yet uses it on a real analytical question, so it is
a tool, not a product. The tool, its `.bat`, and its test landed in `e98237a`.

Related: `handoff/flags/memory-meta-session-exclusion-durable-2026-10-23.md`
(durable meta-session exclusion used by the selector).

<!-- handoff/flags/memory-meta-session-exclusion-durable-2026-10-23.md · owner: opencode · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
`memory-meta-session-exclusion-durable-2026-10-23` — 2026-10-23: **B landed;
A is durable.** `memory_index.EXCLUDED_SESSION_IDS` is the checked-in list; it
holds the four meta-sessions A removed plus this implementation session (that
session took #1 in two eval queries; without it MRR was 0.577 → 0.562).
`ingest` skips the list and purges any rows already in the derived store;
`freshness` and `memory_index_check_drift.py` filter it before asking what is
on disk. The first ingest after the change purged the implementing session and
reported "5 durably excluded"; drift OK (10 stores), freshness OK,
`retrieval_eval` 15/15 MRR 0.577.

Evidence:
- `scripts/memory_index.py` — `EXCLUDED_SESSION_IDS`, `is_excluded`,
  `filter_excluded`, `purge_excluded`; applied in `ingest` and `freshness`.
- `scripts/memory_index_check_drift.py` — `load_sessions_like_ingest` returns
  `memory_index.filter_excluded(sessions)`; the docstring names the policy.
- `scripts/test_memory_index_exclusions.py` — 5/5 (list, filter, purge,
  idempotence, freshness ignores an excluded newest).
- `scripts/test_memory_index_check_drift.py` — 9/9 (added the exclusion check).
- `scripts/memory/CONTEXT.md` — contract note.

Retires `handoff/flags/memory-index-meta-session-exclusion-2026-10-23.md` (A's
per-run workaround): the list is now the source, the DB is rebuilt from it.

not checked: the list is ID-based, so a new meta-session needs an id added (the
title scan found many close-out/instruction sessions; only the ones that
measurably displaced eval entries were excluded); full `--rebuild` cost
after B not measured.

<!-- handoff/flags/did-sessions-default-5-2026-10-23.md · owner: opencode · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
`did-sessions-default-5-2026-10-23` — 2026-10-23: **1f1937f gets its flag
retroactively.** `scripts/did_sessions.bat` now defaults to `COUNT=5` (was 10);
an explicit argument still overrides it. The 10-session run wrote
`scripts/_scratch/sessions/02_products/did_sessions.md` at 1,268,733 bytes, and
that file is read whole by whoever inspects it — 5 halves the default cost and
still covers a working day. No code path depends on the default value.

Evidence:
- commit `1f1937f` — `scripts/did_sessions.bat:7` — `set COUNT=5`.
- `scripts/_scratch/sessions/02_products/did_sessions.md` — 10 sessions,
  1,268,733 bytes, generated 2026-10-23 05:41:32 (the last 10-default run).

not checked: the worktree also held an uncommitted revert to `COUNT=10`; it was
discarded, so the flag claims HEAD, not what an open editor buffer says. Whether
5 is the right size is a judgement call, not a measurement — no read-time or
token-spend comparison of 5 vs 10 exists.

<!-- handoff/flags/session-digest-design-2026-10-22.md · owner: opencode · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
`session-digest-design-2026-10-22` — 2026-10-22: digest sesji zaprojektowany
i zbudowany jako druga warstwa nad L2. **Status 2026-10-23: L0 unproven/closed —
nie jest warstwą analityczną; L1 zostaje selektorem. Wynik A/B:
`handoff/flags/session-digest-ab-2026-10-23.md`.** Rozdzielone fakt i osąd typem
(`mechanical_delta | judgment`), evidence tylko `substring_exists`, stabilny
klucz `agent:session_id`, coverage hash po `coverage_descriptor`.

- Mapa i decyzje: `docs/wayfinder-session-digest.md` (D1, T1–T6 closed, T7 built).
- ADR: `brain/decisions/ADR-005-session-digest-fact-judgment.md` (schema L1/L0,
  normalizer, markery, promocja, worked example 9-vs-10).
- Bramki: `docs/session-digest-GATES.md` G1–G12 — wszystkie `[x]` z evidence.
- Kod: `scripts/session_facts.py`, `scripts/session_digest.py`,
  `scripts/verify_session_digest.py`, `scripts/test_session_facts.py`,
  `scripts/test_session_classify.py`, `scripts/session_digest.bat`.

Pomiar 2026-10-22: 100 sesji głównych + 105 dzieci; L0 788 B; L1 99 277 B;
`SCHEMA_OK`, `QUOTES_OK`, `STABILITY_OK`, `DETERMINISM_OK`, `BUDGET_OK`,
negative controls quote/payload/coverage OK, `REFACTOR_SAFETY_OK`,
`HEADER_OK`, 12 testów ekstraktorów OK. `check_workspace_integrity.py` OK;
`git diff --check` czysty. Commit: design/docs, potem build kodu (dwie części).

`--classify` wbudowany 2026-10-22 jako rules-v1: cards-only, 0 model calls,
`judgment_status: candidate`, `promotion: null`; bramka G13. Wrapper:
`scripts\session_digest.bat N [--classify]`. Pomiar: 40 sesji → 6 kandydatów
(open_threads=4, contradictions=2), `JUDGMENT_OK`.

Review 2026-10-22 (`judgment-check/candidates/digest.judgment.md`): 0/6
kandydatów prawdziwych → **bez promocji**. 4 `open_threads` to obowiązkowa
linia `not checked:` z rytuału `close.py`, nie otwarty wątek (j-0004 ma nawet
commity 0b97dfb, bf0a2f9). 2 `contradictions` porównują sesję, która ma własne
commity (j-0001: 0d0a585, 1a5a19d, 4e3b2ed, bac575a), z sąsiednimi sesjami tej
samej flagi — brak rozjazdu. Przyczyna: `session_facts._marker_scan` bierze
ostatni marker z całego body (także `not checked:` cytowane w treści flagi),
a rules-v1 ma `not_checked` w `OPEN_MARKERS`. Następny krok: rules-v2 (marker
tylko z końcowego bloku, `not_checked` nie jest open) + re-run `--classify`;
promocja dopiero po kandydatach z niezależnym evidence i `review_ref`.

not checked: backend modelowy dla `--classify` (świadomie rules-v1);
`losses.dup` (jawnie w L0 `not_checked`);
stary `tool_calls.jsonl` bez `key` daje `tool_facts.status=missing` do następnego
runu merged. Memory index: ingest 2026-10-23 ponownie dodał wycofane wcześniej
meta-sesje i `retrieval_eval` spadł 15/15 → 13/15; A (workaround) zastosowane
ponownie na minimalnym zbiorze 4 sesji (`ses_ea98f264`, `ses_eb2c4e7e`,
`01a14d3f`, `01a14d44`) → 15/15. To osobny temat retrieval, nie digestu; trwały
fix B (lista `EXCLUDED_SESSION_IDS` w `memory_index.py`) jest w
`handoff/flags/memory-meta-session-exclusion-durable-2026-10-23.md`. Świeżość
trzyma curated shelf.

<!-- handoff/flags/obsidian-vault-2026-10-22.md · owner: opencode · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
`obsidian-vault-2026-10-22` — 2026-10-22: vault Obsidiana zbudowany jako podfolder
`vault/` z własnym repo git (nie nestowany w root repo — `/vault/` w `.gitignore`
roota). Plugin Obsidian Git 2.42.0 preinstalowany w `.obsidian/plugins/obsidian-git/`
z `data.json` (auto-save/pull 10 min, `gitPath` → hermes git).

- Sync: prywatne repo GitHub <https://github.com/kamyczeczek/obsidian-vault> (konto
  `kamyczeczek`, gh device-flow), push przez Git Credential Manager.
- Zrobione: `gh auth login` zalogowany, repo utworzone jako PRIVATE z
  `--source vault --push`, `main` śledzi `origin/main`. Plugin Obsidian Git działa
  na żywo — trzy auto-commity z szablonu `vault: {{date}} {{hostname}}`
  (19:58, 20:05) i notatki `123.md`/`124.md` już na remote.
- Zostaje: nic po stronie workspace'u. Vault otwiera się jako
  `C:\Users\Mateusz\Desktop\root_workspace\vault`.
- Mobile (2026-10-22): Obsidian + Obsidian Git, clone do pustego vaulta działa po
  **classic PAT ze scope `repo`**; fine-grained token dawał HTTP 403 (uprawnienia/
  forma uwierzytelnienia — nie diagnozowane dalej). Token trzymany w localStorage
  apki, nie w repo.

not checked:
- czy drugie urządzenie (mobile/desktop) poprawnie sklonuje vault — test sync
  jednostronny, tylko z tej maszyny.
- czy konflikt przy równoległej edycji dwóch urządzeń rozwiązuje się bez utraty
  notatek — nietestowane.

Starsze flagi (205): [handoff/flags/INDEX.md](handoff/flags/INDEX.md)

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
