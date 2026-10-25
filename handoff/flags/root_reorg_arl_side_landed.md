---
type: Concept
flag: root_reorg_arl_side_landed
since: 2026-10-02
owner: unassigned
agent: unknown
model: unknown
origin: migrated 2026-10-03 from HANDOFF.md §Status
title: root_reorg_arl_side_landed
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---
`root_reorg_arl_side_landed` — 2026-10-02: the root reorg's ARL-side
blockers were fixed and committed. `1d20066`: `quality_check.py` Q0 root-gate
path -> `ROOT.parents[2]` and `check_entropy.py` library index ->
`ROOT.parents[2]` (the group move's off-by-one made hard Q19 read 4,209
chunks as unrecoverable and aborted every ARL commit) plus the one-line
CONTEXT repoint into `CONTEXT-MAP.md`. `f579847`: scar #7 in ARL
`EXPERIENCE.md` (the off-by-one root-resolution class + probe recipe).
ARL worktree cleaned: accidental nested `agentic-research-lab/` dir (3,766
files, byte-identical CRLF copy of part of the repo — no data) deleted;
121 worktree-deleted files restored from HEAD; two dead links in
`knowledge-retrieval/CONTEXT.md` that pointed into it repointed; `$null`
shell-debris file at the root deleted. ARL 21-gate chain 21/21 green.
