---
status: decided
recommendation: approve the 4 DELETE candidates from the report, then remove one script per commit with check_workspace_integrity.py + build_handoff.py --check after each
decided_at: 2026-11-06
owner: mateusz
---

# dead-script-deletions

Should the DELETE candidates in
[docs/dead-script-candidates-2026-11-06.md](../../docs/dead-script-candidates-2026-11-06.md)
actually be deleted?

Context: session 3 (flag `dead-script-candidates-2026-11-06`, commit `73be3ab`)
produced the analysis-only report: zero code callers and docs-only references
for every candidate (fresh `git grep`). DELETE list: `move_state_description.py`,
`gate_checks.py`, `check_kb_layout.py`, `debug_skill_resources.mjs` — the last
one referenced only from `~/.pi` config outside this repo, so its deletion is a
config question too, not a repo-only one. UNDECIDED utility (3) and KEEP (4)
lists are in the report; the dependency map from `91a7f6a` corroborates.

Recommendation: approve the 4, then delete one per commit — each commit runs
`git diff --check`, the pre-commit gate, and `python scripts/check_workspace_integrity.py`.
Never one bulk delete: if the gate flags something, the failing script must be
identifiable from the commit that caused it.

not checked: — (external consumers outside the repo — `~/.pi`, scheduled jobs —
were not enumerated; the report scoped references to in-repo grep)
