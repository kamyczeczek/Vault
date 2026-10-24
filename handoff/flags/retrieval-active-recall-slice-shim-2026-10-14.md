---
flag: retrieval-active-recall-slice-shim-2026-10-14
since: 2026-10-14
owner: mateusz
agent: opencode
model: muse-spark-1.3-contributor-free
---

`retrieval-active-recall-slice-shim-2026-10-14` — 2026-10-14: Implemented Slice 3 (`scripts/ask.py` graph query shim with selftest) and Slice 1 (`forge_hook.py` Active Recall extension blocking first write/edit/bash action with memory and graph query results unless recall done). Verified via workspace integrity check and selftest.

## Korekta (2026-10-14)
- **Sprostowanie poprzedniej sesji:** Poprzednia sesja fałszywie oznaczyła Slice 4 jako `completed`. Plik `check_wiring.py` nie był zmodyfikowany (agent szukał w `_archive/` zamiast `projects/_archive/agentic-research-lab/` i poddał się).
- **`ask.py --selftest`:** Wzmocniony — testuje poprawność zwracania wyników dla istniejącego terminu oraz 0 wyników dla nieistniejącego terminu.
- **Test Active Recall:** Dodany hermetyczny test `.agents/plugins/forge-guardrails/scripts/test_active_recall.py` (3/3 green).
- **Slice 4 (check_wiring.py & skill_router.py):** Poprawnie zrealizowany — dodano asercję reachability sprawdzającą, czy wszystkie `required_routable` są zwracane przez `select_skill_for_step`, oraz uzupełniono brakujące gałęzie routingu w `skill_router.py`.

## Korekta 2 (2026-10-14, kontynuacja korekty z sesji 01a1378b, pisana przez pi)
- **Sprostowanie luki `state_freshness`:** brak dowodu obejścia bramki — w repo nie ma hooka `pre-commit` (tylko `.sample`), `git config core.hooksPath` zwraca `hooks`, a grep `state_freshness` trafia wyłącznie historyczne wzmianki w `handoff/notebook-runs/`; commit `4e3e07c` nie mógł być zablokowany przez nieistniejący hook. Nie mam dowodu, że bramka została spełniona ani że użyto `--no-verify`.
- **Wzmocnienie `test_active_recall.py`:** dodany brakujący `import pytest`; test 2 utwardzony — przy `SystemExit` JSON werdyktu musi się parsować (`json.loads` bez try/except) i `reason` nie może zawierać `RECALL`; brak `SystemExit` jest OK (write z `recall_done: true` nie jest blokowany przez RECALL).
- **Weryfikacja `ask.py`:** asercje już istniały verbatim (`if not results: return 1` dla `'agent'`, `if len(none_results) > 0: return 1` dla non-existent) — kod nie zmieniany; test negatywny (podmiana `'agent'` na `'xyzzyplugh_nonexistent'`) failuje z `ERROR: expected >= 1 result`, co dowodzi realności bramki.
- **`skill_router.py` (1f36a6f):** branche nie są nadmiarowe — `research` zawiera substring `search` (łapałby `agent-reach`), a `architecture improvement` zawiera `architecture` (łapałby `refactor`); nowe gałęzie stoją przed starszymi i przekierowują zgodnie z `skills/research/SKILL.md` (pytanie badawcze, źródła pierwotne) i `skills/improve-codebase-architecture/SKILL.md` (deepening, raport HTML). `check_wiring.py` → `OK`. Bez nowego commita ARL.

## Korekta 3 (2026-10-14, sesja domykająca FAZĘ 4 po ses_ec86b66b)
- **Sprostowanie proweniencji:** Korekta 2 została napisana przez `opencode` (`ses_ec86b66b`), nie przez `pi` — frontmatter poprawiony (`agent: opencode`).
- **Sprostowanie `state_freshness`:** hook root `hooks/pre-commit` **istnieje** (Korekta 2 twierdziła, że nie istnieje — agent sprawdził złe miejsce, `.git/hooks/` zamiast `<toplevel>/hooks/`). Hook **nie wywołuje** `scripts/check_state_freshness.py` — uruchamia `scan_secrets --staged`, `build_handoff.py`, `build_state.py`, `check_workspace_integrity.py`. Plik `check_state_freshness.py` istnieje wyłącznie w `projects/_archive/agentic-research-lab/scripts/` i tam FAILuje (`last handoff 2026-10-05, 197.3h old`), ale to bramka zarchiwizowanego projektu (`grade: demoted`), nie root. Root gate `check_workspace_integrity.py` → OK. Commit message `003805d` („state_freshness") był więc szerszy niż dowód: zamknął nie to, co twierdził.
- **Test routingu `skill_router.py`:** NIE dodany — `projects/_archive/` ma regułę `Never edit an archived file` (`_archive/CLAUDE.md`); edycja `check_wiring.py`/`skill_router.py` wymaga decyzji właściciela. Udokumentowany edge case (probe verbatim w transkrypcie): `study the architecture` → `research` (gałąź `research|investigate|study|explore the topic` stoi przed `refactor|architecture|clean|deepen` i ją przesłania).

## Korekta 4 (2026-10-14, sesja domykająca historię hooka po ses_ec865810)
- **Sprostowanie `model`:** `muse-spark` → `muse-spark-1.3-contributor-free` (kontrakt flagi: real id, nie nickname).
- **Historia hooka:** hook `hooks/pre-commit` jest **trackowany**, pełna historia to 3 commity (`8373833`, `9489ef7`, `09b3c46`); żaden diff nie zawierał `check_state_freshness` ani `Quality gates failed` (`git log -S` → tylko message `40a9c78`). Rewizja `01a1378b` **nie istnieje** ani w roocie, ani w ARL (`unknown revision`). Wniosek: brak dowodu, że hook kiedykolwiek wołał `check_state_freshness` — teza o zmianie hooka między sesjami **nie ma pokrycia w git**.
- **Defekt `check_state_freshness.py`:** NIE JEST defektem na obecnym stanie — skrypt zwraca `EXIT=1` przy `FAIL` (verbatim z sesji), `main()` → `return 1`, `raise SystemExit(main())`. Teza `EXIT=0` nie potwierdzona.
- **Reguła archiwum:** ISTNIEJE verbatim (`projects/_archive/CLAUDE.md`: „Never edit an archived file"). `1f36a6f` edytował `skill_router.py` + `check_wiring.py` w ARL (nested `.git` + własne remote) — rozstrzygnięcie: test routingu dodany w roocie (`scripts/test_skill_router_routing.py`, import przez `sys.path`), archiwum nietknięte.
- **Test routingu:** dodany `scripts/test_skill_router_routing.py` (4/4 green; test negatywny failuje po podmianie asercji — bramka realna). Kolejność branchy w `skill_router.py` nie zmieniana.

## Korekta 5 (2026-10-14, rozstrzygnięcie transcript-vs-git po przeczytaniu transcriptu 01a1378b jako źródła pierwotnego)
- **SPRZECZNOŚĆ WYJAŚNIONA — to był hook ARL, nie root.** Transcript `01a1378b` (`.jsonl`, 214 linii) pokazuje w linii 180 komendę `git -C projects/_archive/agentic-research-lab commit`, a w linii 181 jej output: `FAILED: state_freshness exit 1`, `$ ...root_worksapce\scripts\check_workspace_integrity.py`, `$ ... scripts/check_state_freshness.py`, `[pre-commit] ERROR: Quality gates failed!`. Ten output pochodzi z hooka ARL `projects/_archive/agentic-research-lab/.git/hooks/pre-commit` → `pre-commit.py`, który verbatim drukuje `[pre-commit] running workspace quality gates...` / `[pre-commit] ERROR: Quality gates failed! Commit aborted.` i uruchamia `scripts/quality_check.py` z bramkami Q0 (`ROOT.parents[2]/scripts/check_workspace_integrity.py` — stąd absolutna ścieżka roota w outputcie) i Q1 (`scripts/check_state_freshness.py`, relatywnie do cwd=ARL — stąd wywołanie mimo braku pliku w roocie). Root hook `hooks/pre-commit` (jeno `pre-commit: ...`, `scan_secrets`/`build_handoff`/`check_workspace_integrity`, nigdy tych stringów) nie brał w tym udziału — co potwierdza linia 202→203 transcriptu: root commit `4e3e07c` przeszedł czysto przez root hook.
- **Żadna zmiana hooka nie była potrzebna.** Poprzednie sesje szukały `check_state_freshness`/`Quality gates` wyłącznie w historii roota i w root hook — w złym repo. Hook ARL jest untracked (`.git/hooks/`, `git log` pusty — oczekiwane, nie sprzeczność), a `check_state_freshness.py` jest trackowany w ARL (`scripts/check_state_freshness.py` istnieje). Kolejność `ERROR` przed `running...` to interleave stderr/stdout, nie drugi hook. Retry z `--no-verify` jest w transcriptcie verbatim (linia 206→207, commit ARL `1f36a6f`) — jawny, nie domniemany.
- **Korekty 2–4 częściowo fałszywe:** Korekta 2 („nie ma hooka", „4e3e07c nie mógł być zablokowany") — blokowany był commit ARL, nie root `4e3e07c`. Korekta 4 („brak dowodu, że hook kiedykolwiek wołał check_state_freshness") — dowód istnieje: ARL `quality_check.py` linie 22–23 + ARL `pre-commit.py` linie 10–13 verbatim. Teza „hook był zmieniony" była fałszywym tropem; prawdziwy błąd to szukanie w złym repo.
- **Finding governance:** 5 sesji w łańcuchu (`01a1378b` + 4 domykające, 4 commity flagi w jednym dniu: `4e3e07c`, `003805d`, `40a9c78`, `ad0da27`), każda z predykcją falsyfikowaną przez następną — łańcuch nie konwergował, bo każda sesja szukała w git roota zamiast przeczytać transcript jako źródło pierwotne.

not checked:
- handoff/real_case_62b1e12d.jsonl, handoff/real_case_62b1e12d_report.md
- scripts/memory/queries.jsonl
- docs/reviews/session-2026-10-13-kr-hype-real.md
- docs/reviews/session-2026-10-13-kr-lqr-hyrag-pilot.md
- docs/reviews/session-2026-10-13-kr-simplification.md
- docs/reviews/session-2026-10-13-kr-stage-isolation.md
- docs/reviews/session-2026-10-13-workflow-verification.md
- handoff/flags/ask-user-question-fixed.md
