---
flag: planning-debt-2026-10-14
since: 2026-10-14
owner: agent
agent: pi-bolt
model: default
---

Domknięcie długu po sesjach planistyczno-review (01a13ba3–01a13bbf).
- Artefakty planistyczne (PLAN.md, wayfinder/MAP.md, brain/decisions/ADR-*.md) zostały dodane do repo (tracked) zgodnie z deklaracją w CLAUDE.md.
- `brain/brain.db` jest gitignored jako runtime artifact.
- `logs/` usunięty z tabeli "Where things live" w CLAUDE.md jako runtime artefakt; test parytetu rozróżnia wpisy strukturalne (wymagają tabeli) od runtime (wymagają .gitignore).
- Test parytetu oraz check_workspace_integrity przechodzą pomyślnie.
not checked: all checks passing successfully.
