---
flag: codegraph-residue-and-gate3-tighten-2026-10-28
since: 2026-10-28
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
---

`codegraph-residue-and-gate3-tighten-2026-10-28` — 2026-10-28: Domknięto residue `self-modifications.log` po edycji `CLAUDE.md`; uściślono orakuł G3 w ledgerze bramek.

Stan: `self_modification_audit.py` dopisał do `handoff/audit/self-modifications.log` ślad modyfikacji pliku sensytywnego (`CLAUDE.md`), który nie został wciągnięty do poprzedniego commita aff9ed1. Wciągnięto log do repo. Zbadano linię 548 w `scripts/check_workspace_integrity.py`: check `check_r8_routing_targets` sprawdza tabelowe linki markdownowe (`line.lstrip().startswith("|")`), więc `CLAUDE.md` podlega R8 (rozstrzyganie linków) i R1 (ALLOWED_ROOT), ale nie podlega R13 (liczba linii w audit_agents_md). Zaostrzono orakuł G3 w `docs/codegraph-routing-GATES.md`: wywołania muszą pochodzić z `shell/bash` — wywołania MCP nie zaliczają bramki routera.

Next: Czysty punkt startowy dla sesji badawczej na `projects/research/etth1-h720/` z weryfikacją G3.

not checked: G3 — deferred to etth1-h720 session; zachowanie CLAUDE.md przy dodawaniu wierszy w tabelach (podlega R8).
