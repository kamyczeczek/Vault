---
flag: kb-knowledge-split-2026-10-29
since: 2026-10-29
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
---

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
