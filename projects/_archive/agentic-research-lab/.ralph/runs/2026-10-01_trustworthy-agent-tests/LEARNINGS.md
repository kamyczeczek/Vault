# Learnings

Append-only. One line per learning, most recent last:

- <date> <pattern, gotcha, or discovered convention for this project>
- 2026-10-01 Gotcha: gh CLI `search` is auth-blocked in this env; fall back to the unauthenticated GitHub REST API (`curl https://api.github.com/search/repositories?q=...&sort=stars`) for repo search, and `curl r.jina.ai/<url>` to read pages. Both are zero-config.
- 2026-10-01 Pattern: verify every cited URL returns HTTP 200 before citing it as a primary source; keep the reachable-URL set explicitly in the doc so the G1 count check stays reproducible.
- 2026-10-01 Findings to promote at DONE: a trustworthy agent test is oracle-first (expected value from spec, not from the code), mutation-checked (does it bite?), independently re-derived, and evidence-logged (command+actual+expected+exit). A green suite without a stated expected value is not VERIFIED.
- 2026-10-02 Pattern: at a verification iteration, re-run the gate CHECK yourself and re-check prior iteration evidence on disk before attempting DONE; the controller counts unmet gates, not claims — a human-ownership gate (G2) blocks `--outcome DONE` and must be handed to a human with exact steps in the handoff, not weakened or self-met.
- 2026-10-02 PROMOTED: the "oracle-first + mutation-checked + independently re-derived + evidence-logged" findings line and the verification-iteration pattern line above were moved into the project's `CLAUDE.md` (section "Default work mode: ralph-loop") at I-003 (closing iteration); this run's LEARNINGS.md is now fully promoted.

Promotion is a human gate at DONE: copy the load-bearing entries into the
project's `AGENTS.md` or `CONTEXT.md` so the next session (agent or human)
inherits them. A loop that does not promote learnings re-discovers them every
run.
