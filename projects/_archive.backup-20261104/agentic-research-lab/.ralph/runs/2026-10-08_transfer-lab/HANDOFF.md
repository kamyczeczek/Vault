---
updated: 2026-10-08T02:49:00+02:00
---

# Handoff — 2026-10-08_transfer-lab

## State

Iteration 1 done, G1/G2 green, waiting for human input on Phase 2 candidate.

## Next-session reads (in order, target ≤ 8K tokens)

1. `python skills/ralph-loop/scripts/ralph.py --project . resume`
2. `.ralph/runs/2026-10-08_transfer-lab/decisions/D-001.md`
3. `handoff/flags/arl-transfer-pivot.md`

## What the last iteration did

Completed Iteration 1A (perf-8k test: ON macro = 0.0 vs baseline 0.083, hypothesis B closed) and Iteration 1B (TRANSFER.md created with 4 rows and owners). GATES.md updated, LEARNINGS.md appended. `scripts/_scratch/run_perf_8k.py` and `scripts/_scratch/perf_8k/verdict.json` are the scratch artifacts.

## Open questions and blockers

- **Blocker:** Waiting for Mateusz to choose Phase 2 project-kandydat: `knowledge-retrieval` (retrieval/grounding patterns) or `benchmark-core` (harness/metrics). Do not start Phase 2 without this answer.

## Next action

Ask Mateusz which project-kandydat to use for Phase 2 pilot transfer. Once answered, start Phase 2 in that project (not root) using the 4 patterns from TRANSFER.md.

## Suggested skills

`ralph-loop` (resume), `grilling` (if choosing project-kandydat needs probing)

## Learnings to promote

- `perf ON 8000 avg = 0.0 vs baseline 0.083` → hypothesis B (graph context lifts content scoring) is falsified at 8000 chars; cancel n>=25 plan and proceed to transfer.
- Scratch scripts for isolated LLM runs belong in `scripts/_scratch/` (gitignored), never in the main runner.
- When importing from `scripts/run_ablation.py` fails due to missing `__init__.py`, use `importlib.util.spec_from_file_location` to load the module directly, then monkey-patch constants (e.g. `ASK_CHAR_BUDGET`) before calling `build_context`.
