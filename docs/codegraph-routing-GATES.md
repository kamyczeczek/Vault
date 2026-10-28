---
type: Concept
title: gates-codegraph-routing
generated: { by: okf-enforcer/0.6, at: 2026-10-28T00:00:00Z }
---

# Gates: codegraph routing in CLAUDE.md

OWNS: CLAUDE.md, docs/codegraph-routing-GATES.md

Scope: wpisanie reguły wywoływania CodeGraph CLI do CLAUDE.md §Rules (poza R13/AGENTS.md) i zdefiniowanie odroczonej bramki ewaluacyjnej dla następnej sesji.

- [x] G1: CLAUDE.md zawiera regułę CodeGraph w §Rules bez naruszenia R13
  CHECK: python -c "import pathlib; s=pathlib.Path('CLAUDE.md').read_text(encoding='utf-8'); assert 'codegraph query' in s and 'codegraph callers' in s; print('CLAUDE_ROUTING_OK')"
  EXPECT: CLAUDE_ROUTING_OK
  EVIDENCE: exit=0, EXPECT matched

- [x] G2: workspace integrity gate green (brak regresji w audit_agents_md ani ALLOWED_ROOT)
  CHECK: python scripts/check_workspace_integrity.py
  EXPECT: OK: workspace root holds 36 declared entries, 7 projects, all routing links resolve
  EVIDENCE: exit=0, EXPECT matched

- [ ] G3: [DEFERRED: sesja etth1-h720] empiryczny dowód zmiany zachowania (spadek read vs użycie codegraph)
  EXPECT: W następnej sesji badawczej (bez słowa 'codegraph' w zadaniu użytkownika): liczba wywołań CLI `codegraph` w shell/bash > 0 oraz brak blind read całych plików .py w projects/research/etth1-h720/. Uwaga: wywołanie przez MCP nie zalicza tej bramki (to byłby dowód na Wariant C, a nie na skuteczność routera w CLAUDE.md). Jeśli nie zajdzie w shellu — odrzucenie CLI i świadome przejście na MCP.
  EVIDENCE: DEFERRED to next session owner
