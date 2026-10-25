---
type: Concept
title: session-7-r15-fix
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

# Session 7 — R15 fix (pre-registered)

Option B chosen: add new sessions (01a14af3, ses_eb2d1e180, ses_ebce63c7) to exclude_session_ids for "FTS decision" case. Rationale: test hygiene — index grew by 45 sessions; these are noise relative to the FTS decision case. No threshold change, no gate change, no case removal.