---
flag: goose_workflow_hardening_planned
since: 2026-10-03
owner: unassigned
agent: unknown
model: unknown
origin: migrated 2026-10-03 from HANDOFF.md §Status
---
`goose_workflow_hardening_planned` — 2026-10-03: ICM design now lives at `WORKFLOW_GOOSE_ICM.md` (root). It defines a nested Pipeline: prepare → web research → intake/ingest → graph → retrieval → reflection → implementation → verification → human review. It separates factory from per-run product, uses file handoffs and explicit human gates, and requires a generated `.dgc-evidence/runs/<run-id>/REVIEW.md`. Detailed rationale remains in `projects/research/agentic-research-lab/.claude/goose-workflow-hardening-handoff.md`. No launcher or experiment changes have been made yet. G3 remains pending.
