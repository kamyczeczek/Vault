---
status: decided
recommendation: add a stdlib preflight.py to projects/research/retrieval-v2/ — the invariant "every project ships a preflight.py" is the structural fix; grade correction is the alternative if the project is stalled
decided_at: 2026-11-06
owner: mateusz
---

# retrieval-v2-preflight

`projects/research/retrieval-v2/` is graded **active** (`CONTEXT-MAP.md:77`)
but ships no `preflight.py`, while the other six active research projects do.
This breaks the AGENTS.md invariant "every project ships a `preflight.py`
(stdlib only)" — a session that starts inside `retrieval-v2/` has no first
command to run.

Context: found by the session-5 walk-test (flag
`final-walk-test-2026-11-06`, commit `6605de3`). Not fixed there: creating
files inside another owner's active project was outside that session's scope.

Recommendation: add the missing `preflight.py` (stdlib-only, exit 1 lists
what is missing), keeping the grade honest. If the project is actually
stalled, the alternative is to correct the grade — that is a routing decision
for `CONTEXT-MAP.md`, not a preflight question.

not checked: — (whether `retrieval-v2` is genuinely active work was not
verified with the owner; the grade says active, and that was taken at face
value)
