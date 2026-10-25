---
type: Concept
flag: ralph_loop_upgraded
since: 2026-10-01
owner: unassigned
agent: unknown
model: unknown
origin: migrated 2026-10-03 from HANDOFF.md §Status
title: ralph_loop_upgraded
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---
`ralph_loop_upgraded` — 2026-10-01: `skills/ralph-loop` rebuilt around the
small-session contract (resume cold-start ≤ 8K tokens, one frontier node per
session, controller-enforced stamped `HANDOFF.md`, DONE blocked while gates
unmet, `LEARNINGS.md` promotion to project AGENTS.md). Borrowed from
`unlazy` (gate semantics), `icm-architect` (load-only-what-the-step-needs),
`wayfinder` (fog/frontier), `grill-with-docs` (run-start sharpening),
`agent-reach` (prior-art sweep: snarktank/ralph, SantanderAI/ralph — both
unattended, not this model). Tests: `python skills/ralph-loop/tests/test_ralph.py`
(8/8). Integrity check flags one pre-existing root `.pi/` dir (pi harness
settings debris, 3-byte `settings.json`) — unrelated, needs a human call.
