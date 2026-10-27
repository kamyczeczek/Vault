---
type: Concept
title: omp-launch-fix
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

fingerprint: 5f4f9d29057b plan_version: ad0a031aa564 phase: 04_reflect routing: route.py --tag icm --tag reflection --limit 12; route.py --tag icm --tag planning --limit 12; route.py --tag context-engineering --tag reflection --limit 12; route.py --tag planning --tag decomposition --limit 12 (card<3 -> ADAPT --threshold 3 split via classical-planning alias, depth=1); route.py --tag context-engineering --tag memory --limit 12; route.py --tag planning --tag world-models --limit 12; edge expansion on top chunks (REFERS_TO empty — SHARES_TAG only)

# omp-launch-fix — reflection digest

## Claim

The `omp-launch-fix` defect was not a missing-feature bug but a **liveness defect in an invocation contract**: `spawn.py` called `omp agent ...`, but omp 18.2 has no `agent` subcommand, so the CLI parsed it as `omp launch` with the literal string "agent" as its message and blocked on interactive input — every spawn hung until timeout. The invocation *looked* syntactically valid and the surrounding pipeline *looked* ready, yet the thing it was supposed to start never actually started. This is the measured failure shape documented in the corpus: gates that check consistency (plan exists, digest present, contracts parse) pass while the guarded process is dead.

The repair has three parts, each making a wrong state impossible rather than detecting it late:

1. **Correct non-interactive form** (`omp launch -p` with `--no-session`, `omp.exe` resolved from `~/.bun/bin` because the npm shim `omp.cmd` is not a valid Win32 subprocess target) — the invocation now cannot silently degrade into interactive mode.
2. **W1 hard determinism gate** — `spawn.py` runs `watch.py --once` and refuses on `STALE_DIGEST` (corpus fingerprint vs digest fingerprint mismatch) before any spawn, so the pipeline can never reflect against a graph that no longer exists.
3. **W3/W6 closure** — `spawn_recursive.py` runs `check_reflection.py` after leaves exit and every output carries a provenance object (`fingerprint` + `plan_version` + `phase`), so a reflection is only accepted when its citations and plan identity resolve against the live artifacts.

## Evidence (chunk-id citations)

- `00_measured_liveness_not_consistency` — "Consistency Gates Pass While the Thing They Guard Is Dead (root audit 2026-09-16)": the `omp agent` hang is exactly this shape; the transferable rule is to gate on liveness/execution, not on file-presence consistency.
- `00_measured_gate_semantics_s43` — "Fused Acceptance Gates Hide Decision-Theoretic Holes": two logically distinct gates (is-the-input-valid vs does-the-agent-actually-run) were fused into one chain, so the dead spawn read as "pipeline healthy". The W1/W3 split re-separates them.
- `00_06_self_correction_grounding_requirement` — "Ungrounded self-correction is not neutral — it measurably degrades performance": running `check_reflection.py` post-merge (W3) instead of trusting the leaves' self-report is the grounding requirement applied to this project's own output loop.
- `00_07_critic_external_tool_verification` — "CRITIC — verify-then-correct with external tools": the verify-then-correct ordering of `watch.py --once` → fingerprint compare → spawn is the CRITIC pattern with the "tool" being the determinism gate rather than a model.
- `00_from_plan_to_action_how_well_do_agents_follow_th` — explicit ordered plans beat implicit stage conventions: the injected `phase: 04_reflect` + WORKFLOW.md sha12 in every spawn prompt and every provenance stamp is the mechanism that keeps spawned agents on the canonical `01→02→03→04→05` order.
- `00_08_lesson_persistence_eviction_requirement` — a stored lesson is trustworthy only if eviction bounds it: the candidate jsonl here stays in `proposed` state; phase 5 (`evict_stale.py` / `check_eviction.py`) is what later removes it if its evidence ids stop resolving.
- `00_graph_memory_starter_inventory` — the determinism/hook tagging of the corpus underpins the W1 gate: fingerprints make "which graph does this reflection describe" a machine-checkable property.
- `00_pocock_writing_for_agents` — the `spawn.py` comments that record *why* the `omp agent` → `omp launch -p` change happened (subcommand parse, shim non-app) follow write-for-agents: future readers of the contract can reconstruct the decision without re-discovering the hang.

## Decision

Accept the three-part repair as the permanent launch contract for `pipeline/06_reflect/spawn.py` and `spawn_recursive.py`:

- **Keep** the W1 hard gate (refuse `STALE_DIGEST`, refuse missing `WORKFLOW.md`, refuse stale stage contracts via `check_stage_contracts.py`).
- **Keep** the `omp.exe` resolution order (`~/.bun/bin/omp.exe` → PATH fallback) — never the npm shim.
- **Keep** the 1200s default spawn timeout; a full 12k-digest reflection pass was cut live at 540s, so the old default was a silent liveness killer in the same family as the hang.
- **Record** this reflection as candidates in `reflection/candidates/omp-launch-fix.jsonl`, state `proposed`; do not mark any candidate `accepted` from within phase 4.

## Next bet

Extend the W-AUDIT-4 dead-route guard: today `check_reflection.py` validates that every `--tag` named in `pipeline/06_reflect/*.prompt` files exists in `knowledge/topics.md`. Bet that the same guard applied to the **routing line embedded in every digest/candidate output** (the `routing: <queries>` provenance field) will catch the second-order failure where a reflection cites a route tag that later drops off the controlled vocabulary. Implementation: one regex pass over `routing:` lines in `reflection/digests/*.md` + `reflection/candidates/*.jsonl`, diff against `topics.md`, fail the gate on any tag not in the vocabulary. Evidence for the shape: `00_measured_liveness_not_consistency` (guards must track the thing they guard, not a snapshot of it) and `00_hooks_board_events` (hooks as cheap, always-on observability of state transitions).
