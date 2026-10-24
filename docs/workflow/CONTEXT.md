---
folder: docs/workflow/
role: reference — enforcement mechanisms for SCARS (factory, not pipeline)
entry: README.md (mechanisms + mapping); this file is the folder contract
---

# CONTEXT — docs/workflow/

Reference shelf: how SCARS failures are enforced mechanically. Read this when
you ask "where do I run the check for SCARS X" — then go to `README.md` for
the command and run the script. No pipeline lives here; nothing is generated.

## Inputs

- `scripts/scan_secrets.py`, `scripts/pre_close_check.py`,
  `scripts/verify_report_evidence.py`, `scripts/close.py`
- `hooks/pre-commit` (the automatic caller of scan + integrity gate)
- `SCARS.md` (the failures: S58/S59/S60/S62 + commit-hygiene scars)
- `docs/wayfinder-retrieval-map.md` (ticket definitions T14–T16)

## Process

Agent wants to enforce SCARS X → finds the X→mechanism row in `README.md` →
runs the named script exactly as documented → pastes raw output into the
report. No wrapper, no re-implementation.

## Outputs

None — reference folder. Session artifacts go to `docs/reviews/` (reports)
and `handoff/flags/` (claims), never here.

## Human check

Cold agent opens root `CLAUDE.md`, finds this folder in ≤2 reads, and can
answer "where do I run scan_secrets" without asking.
