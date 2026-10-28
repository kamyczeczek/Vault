---
flag: close-py-include-safety-2026-10-28
since: 2026-10-28
owner: mateusz
agent: opencode
model: omniroute/agy/gemini-3.8-flash-high
origin: session-close
---

`close-py-include-safety-2026-10-28` — 2026-10-28: `close.py` odblokowuje `--include projects/...` i zabrania `--include .`. Usunięto przestarzały check blokujący ścieżki pod `projects/research/`, dodano walidację przez `git check-ignore -q --no-index --`, zachowano obsługę staged deletions (`_is_staged_deletion`) i katalogów. Usunięto zindexowane śmieci `close_body.txt` i `correct_body.txt` z `handoff/`. Testy w `scripts/test_close.py` (`NewSafetyChecksTests`) zielone, 42 testy w `scripts/test_close.py` przechodzą.

not checked: —
