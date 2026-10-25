---
type: Concept
flag: verification_tool_scars
since: 2026-10-03
owner: opencode
agent: build
model: opencode/space-bunny-free
origin: this session (post-mortem #2)
title: verification_tool_scars
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`verification_tool_scars` — 2026-10-03: **blizny (d)–(g) zapisane i domknięte; punkt (2) świadomie otwarty.** Poprzednia wersja tej flagi mówiła „domknięte", skoro `pytest.ini` czeka — to był overclaim w dokładnie tej klasie, którą flaga diagnozuje, więc sformułowanie poprawione. Diagnoza trzech powracających klas błędu zamiast reaktywnego kasowania. (1) **Detektor whitespace nie istnieje w repo** — no-op `line.rstrip() != line.rstrip(b' \t\r\n')` był wyłącznie inline; `grep rstrip(b?['"]` w całym workspace daje 4 trafienia, wszystkie poprawne (`_scratch/patch_lines.py:51` robi dokładnie `rstrip("\r\n").split("\n")`). Autoritetem jest `git diff --check`. (2) **`pytest.ini` nie ma generatora w repo** — `git log --all -- pytest.ini` pusty w root i ARL, w całym workspace string `pytest.ini` występuje tylko w mojej flagowej prozie, `forge_hook.py` tylko *czyta* komendy pytest z tekstu, a w root nie ma `pyproject.toml`/`setup.cfg`/`tox.ini`/`conftest.py`. Wniosek: plik powstawał z ad-hoc shella (ta sama klasa co `$null`), a "wrócił" bo powtarzała się komenda, nie narzędzie. (3) Blizny zapisane w `AGENTS.md` § Rules: (d) nigdy nie ręcznie rollować whitespace-checku, (e) plik, który wraca po usunięciu, ma generatora — znajdź go przed ponownym kasowaniem, (f) `git diff --cached` czyta index, nie working tree — `git reset HEAD` raz, (g) cały nowy plik jako `+` to untracked, nie duplikat.

Commit rota zrobiony (`e61d8c8`); `build_handoff.py --check` wpięty do integrity gate jako **R12, hard** (`19253e4`) — twardy, bo jedynym czytającym przeterminowany widok cold-start jest następna zimna sesja, która nie potrafi odróżnić go od aktualnego. Falsyfikacja sprawdzona w obie strony przed commitem (tymczasowa flaga → rc=1 z nazwą komendy; po usunięciu i rebuildzie rc=0). Efekt uboczny tej samej zmiany: epilog FAIL mówił „A root-level file is outside every project gate", co nigdy nie było prawdą dla R4–R11 ani dla R12 — przepisany na dwa realne wyjścia (zadeklaruj wpis w `CLAUDE.md` + `ALLOWED_ROOT` albo usuń debris) z zachowaniem reguły „nie rozszerzaj checku, żeby go wyciszyć".

Next: decyzja o `pytest.ini` (`testpaths = scripts`) — własny commit + `ALLOWED_ROOT`, bo inaczej bare `pytest` skanuje `projects/`. Do decyzji właściciela.