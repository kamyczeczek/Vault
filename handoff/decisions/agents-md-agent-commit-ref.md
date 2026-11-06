---
status: open
recommendation: requalify the reference to the archived path, bundled as its own R13 cascade — new review report version + docs/reviews/README.md row + EXEMPT baseline entries + view rebuild, one commit; never a bare 1-line AGENTS.md edit
decided_at:
owner: mateusz
---

# agents-md-agent-commit-ref

The gate rule in `AGENTS.md` — "An exemption (e.g. `agent_commit.py`'s
whitespace scope)" — cites `scripts/agent_commit.py`, which does not exist
live anywhere; the only surviving copy is
`projects/_archive/agentic-research-lab/scripts/agent_commit.py`. A cold agent
following that reference finds a dead path in the L0 router.

Context: found by the session-5 walk-test (flag
`final-walk-test-2026-11-06`, commit `6605de3`). The one-line requalification
was prepared and then **reverted**: the first commit attempt reproduced the
R13 cascade of SCARS.md:20 — regenerated audit block plus 31 unclassified
prose figures in `docs/reviews/architecture-review-20261007-v8.html`
(values 64/70/99/100/102/133, all shifted by +1). Restored from HEAD, gates
green again.

Recommendation: fix as its own cascade — new report version in `docs/reviews/`
(v8 → `projects/_archive/reviews/`), the README row, EXEMPT baseline entries
in `scripts/audit_prose_numbers.py`, and the view rebuild, all in one commit.
The precedent is the 2026-10-07 cascade (regen block + 7 prose shifts + 3
EXEMPT changes).

not checked: — (which EXEMPT classes the 31 figures finally land in after the
shift was not enumerated; the trial edit showed the drift, not the final
baseline)
