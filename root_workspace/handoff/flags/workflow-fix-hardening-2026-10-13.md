---
flag: workflow-fix-hardening-2026-10-13
since: 2026-10-13
owner: mateusz
agent: opencode
model: openrouter/deepseek/deepseek-chat
origin: session-close
---

`workflow-fix-hardening-2026-10-13` — 2026-10-13: query: Zakończono naprawę workflow po 10 sesjach. Wprowadzono walidacje w close.py (--explain, --include zagnieżdżonych repo, _tmp_* w eval, wykrywanie BLOKADA), walidację pytań testowych (verify_questions.py), check R20 dla SCARS.md w check_workspace_integrity.py, zaktualizowano SCARS.md o S56–S58 oraz dodano raport w docs/reviews/.
not checked: Evaly eksperymentalne v2 attune-rag w pełnym pipeline'u zewnętrznym; pliki _tmp_* w katalogu eval pozostawione jako artefakty robocze sesji.
