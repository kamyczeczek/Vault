# Gates: kb-split-cleanup

OWNS: .gitignore, scripts/check_workspace_integrity.py, STATE.md, brain/decisions/ADR-008-kb-subfolder.md, handoff/audit/self-modifications.log, handoff/flags/kb-cleanup-residue-2026-10-29.md, HANDOFF.md

Scope: Commit the residual dirty state from the kb-knowledge-split and close the integrity gate to green.

- [ ] G1: `.unlazy/` is in RESIDUE_DIRS and `.gitignore`, so the integrity gate no longer fails on it
  CHECK: python.exe scripts/check_workspace_integrity.py 2>&1 | Select-String "unexpected directory.*unlazy"
  EXPECT: (no match — empty output means the error is gone)
  EVIDENCE: pending

- [ ] G2: `check_workspace_integrity.py` exits 0
  CHECK: python.exe scripts/check_workspace_integrity.py
  EXPECT: OK
  EVIDENCE: pending

- [ ] G3: `check_kb_layout.py --layout --stale` exits 0
  CHECK: python.exe scripts/check_kb_layout.py --layout --stale
  EXPECT: KB-LAYOUT OK
  EVIDENCE: pending

- [ ] G4: `git status --short` shows no modified files after the commit
  EVIDENCE: pending

- [ ] G5: `git diff --check` passes (no whitespace errors)
  CHECK: git diff --check
  EXPECT: (empty — no errors)
  EVIDENCE: pending

- [ ] G6: `build_handoff.py --check` confirms HANDOFF.md is current
  CHECK: python.exe scripts/build_handoff.py --check
  EXPECT: OK
  EVIDENCE: pending
