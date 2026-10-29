---
flag: kb-cleanup-residue-2026-10-29
since: 2026-10-29
owner: mateusz
agent: opencode
model: omniroute/agy/claude-opus-4-6-thinking
---

`kb-cleanup-residue-2026-10-29` — 2026-10-29: domknięcie residue po kb-knowledge-split.

Stan:
- `.unlazy/` dopisane do `RESIDUE_DIRS` w `check_workspace_integrity.py` i do `.gitignore` — ta sama klasa co `.codegraph/` (runtime, odtwarzalne, nigdy autorskie). Bramka integralności przestała zgłaszać `unexpected directory at workspace root: '.unlazy'`.
- `brain/decisions/ADR-008-kb-subfolder.md`: status line przełączony na angielski (`Supersedes ADR-006 in full`) — diff z HEAD zaciągnięty.
- `handoff/audit/self-modifications.log`: zaległy wpis `SENSITIVE_MODIFICATION: M CLAUDE.md` z sesji codegraph-residue zaciągnięty; CRLF naprawiony na LF.
- `STATE.md` przebudowany z nowym HEAD.

Weryfikacja:
- `python.exe scripts/check_workspace_integrity.py` — exit 0 (`OK: 36 declared entries, 7 projects`).
- `python.exe scripts/check_kb_layout.py --layout --stale` — `KB-LAYOUT OK · KB-STALE OK`.
- `git diff --check` — exit 0 (no whitespace errors).
- `python.exe scripts/build_handoff.py --check` — OK.

not checked: —
