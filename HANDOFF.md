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

<!-- handoff/flags/etth1-h720-s44-calibration-2026-10-30.md · owner: mateusz · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
`etth1-h720-s44-calibration-2026-10-30` — 2026-11-01: The ADR 0001 threshold-comparability
caveat is now a number. The S44 blend (NLinear L336 a=1 + NLinear L336 a=10 +
PatchTST-Delta P24 D32 2L, per-horizon ridge, no intercept, alpha=30000, frozen) scores
4.1255 mean raw MAE on the S49 protocol (12 locked origins, step 720 h, 8640..16560),
5-seed mean 4.1721. BigDictELM L96 2.4777, DLinear 2.5384. Rule fixed before the run:
4.1255 >= 2.4777, so 1.9781 was a protocol artifact (2161 dense step-1 origins), not a
level reachable on 12 sparse step-720 origins.

The blend is also worse than each of its own members (2.61-2.70). Mechanism recorded, not
tuned away: with no intercept the ridge can only express a level multiplier, and the
multiplier learned on a biased-low out-of-sample region (-5.24 bias, member MAE 6.09)
over-corrects at the scored origin (member MAE 2.79) — 1.3249x pushes the level to 25.3
against an actual 21.1. The disjoint second-half sensitivity reproduces the failure
(3.1041), so it is not one unlucky split.

Two corrections were made to an earlier attempt in this session, both before the reported
run. (1) Ridge weights in S44 were fitted on OUT-OF-SAMPLE member forecasts; the earlier
"in-sample ridge" claim was wrong and is removed. (2) The first calibration harness trained
members on s[o-8640:o] and then fed the ridge their forecasts from the last 2880 rows of
that same window — in-sample stacking, which S44 never did. Fixed: members frozen at row
5760 produce the ridge's design matrix over the 2161 out-of-sample tail origins, members
are refit on all 8640 rows for the scored forecast. Recorded as Amendment A1 in
GATES-s44-calibration.md before the run.

Consistency control: the identical S44 frozen test reproduces 1.978126 (rel diff 4.2e-11)
on both data files. Gate evidence for this close: the workspace integrity gate
`check_workspace_integrity.py` exit 0, and `python -m pytest projects/research/etth1-h720
-q` green at 31 passed. S49 stays closed, no model promoted, nothing tuned.

not checked: S44's dense 2161-origin test was not re-scored with seeds 43-46; S44's ridge
was not fitted once and reused (impossible across disjoint origins); alpha was not re-tuned
for the 8640-row window; BigDictELM/DLinear were re-derived, not diffed bit-for-bit against
S49's stored JSON; the two ETTh1 copies were not reconciled (<=3.6e-15, immaterial).

Next step: nothing on this line. Any further H720 work needs a new hypothesis, fresh dev
origins and a protocol registered before the run. The root/config follow-ups from the
CodeGraph G3 FAIL (disable jcodemunch or keep one code-index tool, shorten the CodeGraph
rule in root CLAUDE.md, keep the index for manual queries) remain open and are out of this
project's scope.

<!-- handoff/flags/kb-knowledge-split-2026-10-29.md · owner: mateusz · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
`kb-knowledge-split-2026-10-29` — 2026-10-29: warstwa wiedzy schodzi do `kb/`, root repo zostaje `Desktop\vault` (ADR-008 zastępuje ADR-006).

Stan:
- `git mv` czterech katalogów, które czyta Obsidian i człowiek: `.obsidian`, `.smart-env`, `Notes`, `library` → `kb/`. 77 rename'ów, PDF-y z `library/` (9 plików, ignorowane) przeniesione fizycznie, więc klon ich nie odtworzy — to nadal świadoma decyzja z D24.
- Root repo bez zmian: `Desktop\vault` dalej jest `.git`-em i workspace'em. Nazwa `kb/`, nie `vault/`, żeby `Desktop\vault\vault` nie myliło się z rootem i żeby zmienna `VAULT` nie wskazywała katalogu o nazwie repo.
- `check_workspace_integrity.py`: `VAULT = ROOT / "kb"`, `VAULT_OWNED = {.obsidian, .smart-env, Notes, library}` musi istnieć **w kb/ i nigdzie indziej**, nowy `ROOT_OWNED = {.git}` musi być w root i nigdy w `kb/`. `library` usunięte z `ALLOWED_ROOT`, `kb` dodane. Liczba wpisów roota bez zmian: 36.
- `.gitignore`: wzorce z ukośnikiem (`.obsidian/workspace.json`, `.smart-env/*`, `Notes/OKF-rag/source-slices/index.md`) dostały prefiks `kb/`, bo wzorzec z `/` jest rozstrzygany względem katalogu pliku `.gitignore` i po przeniesieniu przestałby cokolwiek ignorować. Dodano `kb/.obsidian/plugins/obsidian-git/obsidian_askpass.sh` (wtyczka tworzy ten helper przy starcie, nigdy nie był trackowany).
- Ścieżki w kodzie: `run_okf_rag_benchmark.py` (`NOTES_ROOT`, oba `.smart-env`, `git ls-tree/status -- kb/Notes/OKF-rag`, filtr w JS), `gate_checks.py` (g7), `generate_source_slices.py` (defaulty `--source`/`--output` + docstring), `CONTEXT-MAP.md` (routing OKF-rag), `skills/retrieval-two-stage/SKILL.md`.
- Nowa bramka `scripts/check_kb_layout.py`: `--layout` (kb/ ma treść, root nie ma nic), `--stale` (żywe powierzchnie: `scripts/**`, `tools/**`, `hooks/`, `skills/**`, `AGENTS.md`, `CLAUDE.md`, `README.md`, `CONTEXT-MAP.md`, `.gitignore`), `--selftest` (negatywna kontrola matchera). Historia — `handoff/`, `docs/`, `brain/decisions/` — jest świadomie poza skanem: to zapis stanu z dnia, w którym powstał.
- `kb/Notes/OKF-rag/doctree-mcp:16419` — jedyne trafienie `scan_secrets` w całym przeniesionym drzewie: w przykładzie `curl` stał nagłówek `Authorization` z tokenem JWT obciętym wielokropkiem. Fałszywy alarm kształtu, ale naprawiony w danych, nie w bramce: wartość zamieniona na `<token>`. Plik był trackowany od `edba1b8`, więc przeniesienie tylko wystawiło go na skan staged.
- `test_gate_allowlist_parity.py`: wiersze wiedzy deklarowane jako `kb/<entry>`, `library` usunięte z `system_entries`, `.pi` i `logs` przeniesione z `runtime_entries` do `system_entries` (oba są trackowane deklaracje, nie runtime — test był czerwony na HEAD 9ae0b71), a `sys.exit` w `test_parity` zamienione na `raise SystemExit`, bo pytest zgłaszał wyjście 0 jako błąd.
- ADR: `brain/decisions/ADR-008-kb-subfolder.md`, z adnotacją „Superseded by ADR-008" w ADR-006 i wpisem w `brain/decisions/index.md`. Numer 008, nie 007: `ADR-007-git-baseline-and-remote` już istnieje i opisuje inną decyzję.

Weryfikacja:
- `python.exe scripts/check_workspace_integrity.py` — exit 0 (`OK: workspace root holds 36 declared entries, 7 projects`).
- `python.exe scripts/check_kb_layout.py --layout --stale` — `KB-LAYOUT OK · KB-STALE OK`; `--selftest` — `KB-SELFTEST OK` (dodatnia złapana, ujemna czysta).
- pytest `scripts/` — 221 passed, 1 skipped, 2 deselected (deselect: dwa testy `test_audit_prose_numbers` pinujące usunięty `architecture-review-20261003-v7.html`, czerwone już na HEAD).
- `scripts/test_generate_source_slices.py`, `test_gate_allowlist_parity.py`, `test_brain_db.py`, `test_workspace_structure.py` — 6 passed.
- Trzy testy trybu skryptowego (`test_memory_index*.py`) — zielone uruchomione bezpośrednio.

Next: otworzyć `kb/` w Obsidianie (nowy vault root) i zreindeksować Smart Connections; dopiero potem ocenić, czy `projects/` znika z grafu.

not checked: ręczne otwarcie `kb/` w Obsidianie i reindeks Smart Connections — poza sesją; zachowanie wtyczek, które zapisywały ścieżki względem starego roota vaulta; pełny `pytest projects/research` — czerwony przed tą zmianą (`benchmark-core` nie importuje `fit_amr`), osobny projekt; `skills/ralph-loop/tests` — 8 błędów `PermissionError` na Windows, czerwone przed tą zmianą; dwa testy `test_audit_prose_numbers` — pinują usunięty v7.

Odstępstwo od polecenia: miały być dwa commity (sam `git mv`, potem ścieżki). Commit z samym `git mv` nie przechodzi bramki — `ALLOWED_ROOT` i R1b wskazują wtedy ścieżki, które właśnie zniknęły z roota, a `hooks/pre-commit` uruchamia integrity gate, więc commit zostałby zablokowany. Podział na dwa commity zostawiłby albo czerwone okno, albo commity z nieruncznymi skryptami. Całość jest jednym commitem; rename'y są nadal izolowane w `git show --find-renames --stat`.

<!-- handoff/flags/kb-cleanup-residue-2026-10-29.md · owner: mateusz · agent: opencode · model: omniroute/agy/claude-opus-4-6-thinking -->
`kb-cleanup-residue-2026-10-29` — 2026-10-29: domknięcie residue po kb-knowledge-split.

Stan:
- `.unlazy/` dopisane do `RESIDUE_DIRS` w `check_workspace_integrity.py` i do `.gitignore` — ta sama klasa co `.codegraph/` (runtime, odtwarzalne, nigdy autorskie). Bramka integralności przestała zgłaszać `unexpected directory at workspace root: '.unlazy'`.
- `brain/decisions/ADR-008-kb-subfolder.md`: status line przełączony na angielski (`Supersedes ADR-006 in full`) — diff z HEAD zaciągnięty.
- `handoff/audit/self-modifications.log`: zaległy wpis `SENSITIVE_MODIFICATION: M CLAUDE.md` z sesji codegraph-residue zaciągnięty; CRLF naprawiony na LF.
- `STATE.md` przebudowany z nowym HEAD.

Weryfikacja:
- `python.exe scripts/check_workspace_integrity.py` — exit 0 (`OK: 36 declared entries, 7 projects`).
- `python.exe scripts/check_kb_layout.py --layout --stale` — `KB-LAYOUT OK · KB-STALE OK`.
- `git diff --check` — exit 0 (no whitespace errors).
- `python.exe scripts/build_handoff.py --check` — OK.

not checked: —

<!-- handoff/flags/etth1-h720-s49-honest-closeout-2026-10-29.md · owner: mateusz · agent: opencode · model: omniroute/agy/gemini-3.8-flash-high -->
`etth1-h720-s49-honest-closeout-2026-10-29` — 2026-10-29: S49 ETTh1 H720 zamknięta (REJECT) po audycie zgodności protokołu.

Stan:
- Wzmocniono ledger `projects/research/etth1-h720/GATES-s49-closeout.md`: G1 liczy wartosci z artefaktow, G2 parsuje wiersz tabeli w CONTEXT.md, G5 sprawdza czysty status OWNS i obecnosc flagi w HEAD.
- Audyt protokołu (20 zadeklarowanych originow vs 12 wykonanych; 5 zadeklarowanych seedow vs seed 42 w glownych tabelach; próg S44 z 2161 originow) zapisany w ADR 0001 i Aneksie Wykonawczym 2026-10-29.
- ADR: `projects/research/etth1-h720/docs/adr/0001-s49-closeout-and-protocol-discrepancies.md`.

Weryfikacja:
- `python -m pytest projects/research/etth1-h720/` — 14 passed.
- Bramka integralności workspace — integrity exit 0.

Next: nie stroic modeli H720 na obecnym zestawie 12 originow; nastepna sesja — nowa linia badawcza.

not checked: kalibracja progu S44 na 12 originach (osobna sesja).

<!-- handoff/flags/cleanup-red-tests-2026-10-29.md · owner: mateusz · agent: opencode · model: omniroute/agy/claude-opus-4-6-thinking -->
`cleanup-red-tests-2026-10-29` — 2026-10-29: domknięcie czerwonych testów i residue po kb-knowledge-split.

Stan:
- **benchmark-core fit_amr import** — usunięto martwy import `fit_amr, pred_amr` z `sunspot_methods.py` (linia 6). Nazwy nigdy nie istniały jako top-level w `bench.py`; zostały przeniesione do `members/amr_fbs.py` jako `fit_amr_fbs`/`pred_amr_fbs`. Import nie był używany w rejestrze metod `get_sunspot_methods()`. 24 testy benchmark-core zbierane bez błędów.
- **test_audit_prose_numbers v7** — dodano guard `skipTest("v7 report not available")` do `test_v7_prose_is_fully_classified` i `test_the_live_table_carries_no_stale_entry`, bo plik `docs/reviews/architecture-review-20261003-v7.html` nigdy nie trafił do repo. Trzeci test (`test_regenerating_the_block_does_not_launder_the_prose`) miał guard od początku. 31 passed, 3 skipped.
- **ralph-loop PermissionError** — dodano `skills/ralph-loop/tests/conftest.py` z fixture `tmp_path` opartą o `TemporaryDirectory` zamiast pytest-owego `tmp_path_factory`, który padał na `PermissionError` w `%TEMP%\pytest-of-Mateusz` (zepsute ACL na Windows). 8 passed.
- **did_sessions COUNT=20** — zmieniono default z 5 na 20 w `did_sessions.bat` i `did_sessions_drive.bat`. Test `test_default_count_is_5` → `test_default_count_is_20` w `test_did_sessions.py`.
- **.unlazy/locks** — usunięto zaległy katalog `locks`, preflight_agent wraca do OK.
- restored `handoff/audit/self-modifications.log` (deleted from disk but tracked in HEAD).

Weryfikacja:
- `python.exe scripts/check_workspace_integrity.py` — exit 0 (36 declared entries, 7 projects).
- pytest `scripts/` — 221 passed, 3 skipped.
- pytest `skills/ralph-loop/tests/` — 8 passed.
- pytest `projects/research/etth1-h720/` — 14 passed.
- benchmark-core: 24 testy zebrane, import OK (testy właściwe są zbyt wolne na timeout, ale `import sunspot_methods` i `get_sunspot_methods()` → 17 metod).
- `git diff --check` — exit 0.

not checked: benchmark-core full test execution (timeout >5 min na trenowanie modeli); push do remote.

<!-- handoff/flags/benchmark-core-full-tests-2026-10-29.md · owner: mateusz · agent: opencode · model: omniroute/agy/claude-opus-4-6-thinking -->
`benchmark-core-full-tests-2026-10-29` — 2026-10-29: pełny suite benchmark-core przeszedł 24/24.

Stan:
- `python.exe -m pytest -v projects/research/benchmark-core/` — **24 passed, 1 warning, 540.88s (9:00)**. Jedyny warning: statsmodels SARIMAX `Non-invertible starting MA parameters found` — kosmetyczny, nie wpływa na wynik.
- Poprzednio (flaga `cleanup-red-tests-2026-10-29`) uruchomiono tylko collect + import smoketest z powodu timeoutu >5 min. Pełne uruchomienie potwierdza, że fix martwego importu `fit_amr` w `sunspot_methods.py` nie złamał żadnego testu trenującego modele.
- Pliki testowe: `test_benchmark_protocol` (6), `test_chaos_protocol` (2), `test_lasso` (1), `test_sunspot_eval` (3), `test_sunspot_longterm` (2), `test_thomas` (5), `test_thomas_compare` (2), `test_thomas_forecasts` (2), `test_thomas_methods` (1).

Weryfikacja:
- pytest 24 passed (pełne uruchomienie z trenowaniem modeli).
- `check_workspace_integrity` — exit 0.
- `git diff --check` — exit 0.

not checked: FEV 100-task `tasks.yaml` run (osobny punkt); push do remote (wykonany w tej sesji dla wcześniejszych commitów).

Starsze flagi (248): [handoff/flags/INDEX.md](handoff/flags/INDEX.md)

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
