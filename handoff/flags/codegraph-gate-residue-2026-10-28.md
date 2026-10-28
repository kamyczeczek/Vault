---
flag: codegraph-gate-residue-2026-10-28
since: 2026-10-28
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
---

`codegraph-gate-residue-2026-10-28` — 2026-10-28: `.codegraph/` uznany za artefakt narzędzia w `RESIDUE_DIRS`, nie za wpis katalogu workspace.

Stan: `codegraph init` tworzy w root `.codegraph/` (~70 MB SQLite, wpisane do `.gitignore`), a `check_workspace_integrity.check_r1_root_shape` zgłaszał go jako `unexpected directory at workspace root`. Wyjątek jest świadomy i wąski: `.codegraph` dołącza do `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `.ipynb_checkpoints` — ta sama klasa (gitignored, odtwarzalne przez narzędzie, nigdy nie autorskie). `ALLOWED_ROOT` **nie** poszerzono: indeks nie istnieje w świeżym klonie i nie jest treścią workspace, więc deklarowanie go jako wpisu katalogu kazałoby bramce wymagać artefaktu runtime. Komentarz w kodzie nazywa powód.

Next: domknięcie sesji `single-repo-codegraph-2026-10-28` (`.gitignore`, `scripts/close.py`) osobnym commitem.

not checked: czy `RESIDUE_DIRS` wpływa na reguły inne niż R1 — sprawdzono tylko wyjście bramki; zachowanie drzewa po `codegraph uninit`.
