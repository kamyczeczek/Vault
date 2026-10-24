---
flag: notebooklm-cannot-verify-retrieval
since: 2026-10-10
owner: Mateusz
agent: opencode
model: opencode/muse-spark-1.3-contributor-free
origin: handoff/notebook-runs/2026-10-10-root-retrieval-check/
---

`notebooklm-cannot-verify-retrieval` — 2026-10-10: Pipeline `scripts/notebook/CONTEXT.md` nie może służyć do weryfikacji retrievalu. `problem.md` jest pushnięty jako źródło, więc NotebookLM zawsze może echo. Potwierdzone na trzech warstwach: pack (zawiera flagi sens-verdict/sens-arl), sesja (self-contamination), oba problem.md (cytowane w sources_used). Rozróżnienie: guidance (bring back perspective) ≠ verification (czy korpus wspiera twierdzenie). To nie jest defekt pipeline'u — to mismatch między designem (guidance) a use case'em (verification); nie naprawiać pipeline'u, to zły pipeline do tego zadania. Pipeline jest zaprojektowany dla guidance i tam działa. Verification zostaje w KR (`run_retrieval_benchmark.py`, gate relacyjny). Run 2026-10-08-sens-arl NIE jest skażony — to był guidance (streszczenie istniejących danych), nie verification. Next: nie używać notebooka do testów retrievalu; jeśli potrzeba weryfikacji grafu — KR gate.
