---
type: Concept
flag: gate_trimmed
since: 2026-10-01
owner: unassigned
agent: unknown
model: unknown
origin: migrated 2026-10-03 from HANDOFF.md §Status
title: gate_trimmed
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---
`gate_trimmed` — 2026-10-01: ceremony cut after user critique (one move cost
~100 reference fixes — too many copies of one fact). Deleted: `ROOT-CONTEXT.txt` +
4× `ctx_root_*.bat` (root L1 pack; gate R8 removed). Routing single-homed:
`AGENTS.md` "Where to go" (intents) + `CONTEXT-MAP.md` §Routing (procedure);
`CLAUDE.md` "Route by intent" table → one-line pointer. Gate now FAILs only on
R1/R2/R3/R9 + R11 (R11 wired 2026-10-02 in `0ae22ef`); R4/R5/R6/R7/R10
demoted to advisory WARN. The gate's own docstring is the single home for
that catalogue — this entry predates R11, so trust the docstring over it.
Per-project
`ctx_project_*.bat` and `build_project_map.py`/`build_context_txt.py` generators
untouched (on-demand, not gated).

`G12_CLOSED` — G12 resolved 2026-10-01 (`reflect.py` canonical); both
follow-ups done 2026-10-01: `scripts/pi_models.py` un-ignored and committed
(`82b078a`), and the no-artifact-on-failure defect fixed — every `reflect.py`
run now leaves run/failure trace records in
`reflection/trace/events.jsonl`, pinned by `tests/test_reflect_failure.py`
(`024f9a5`). No run is in flight.
