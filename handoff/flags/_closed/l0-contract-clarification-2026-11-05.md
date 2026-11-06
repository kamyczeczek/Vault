---
flag: l0-contract-clarification-2026-11-05
since: 2026-11-05
owner: mateusz
agent: omp
model: omniroute/agy/gemini-3.8-flash-low
origin: user-requested-continuation
---

`l0-contract-clarification-2026-11-05` — 2026-11-05: sformalizowano kontrakt poziomu zero (L0). `AGENTS.md` zdefiniowano jako jedyny obowiązkowy router L0 (<2K tokenów) ładowany na cold start; `HANDOFF.md` oznaczono jako stan aktywny przy wznawianiu/zmianie stanu; root `CLAUDE.md` sklasyfikowano jako L1 (katalog wpisów repozytorium do ładowania on-demand). Zachowano niezmiennik 133 linii w `AGENTS.md` (R13).

Weryfikacja: `python scripts/audit_agents_md.py --check` OK; `python scripts/test_audit_agents_md.py` 29/29 OK; `git diff --check` OK; `python scripts/check_workspace_integrity.py` OK (38 declared entries, 7 projects).

not checked: brak.
