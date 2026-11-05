---
type: Concept
title: TRANSFER
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# TRANSFER.md — przenośne rozwiązania workspace

| Rozwiązanie | Status | Dowód | Cel przeniesienia | Adapter | Test akceptacyjny | Owner |
|---|---|---|---|---|---|---|
| ICM L0–L4 + flagi | gotowe | działa w rootcie | inne projekty | szablon CONTEXT.md/HANDOFF.md | cold start ≤8K, handoff kompletny | opencode |
| Gate'y mutacyjne | gotowe | Q0/Q16/Q17 | root + projekty | hook + skrypt | regresja złapana, 0 false-positive | opencode |
| D5/ADR-0003 | gotowe | brak śmieci w git | root | konwencja + skrypt | pochodne odtwarzalne | opencode |
| Regex + echo-guard | gotowe | sesja B | ewaluacje | skrypt | brak metryk tautologicznych | mateusz |

## Owner sources (from root `handoff/flags/*.md`)

- `opencode` — ICM L0–L4: `handoff_flag_per_file_icm.md`, `l0_router_deepened.md`; Gate'y mutacyjne: `gate_has_no_automatic_caller.md`, `verification_tool_scars.md`; D5/ADR-0003: `root_committed_931aac5.md`
- `mateusz` — Regex + echo-guard: `phase2_session_b_done.md`
