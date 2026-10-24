---
updated: <ISO-8601 timestamp of this handoff>
---

# Handoff — <run slug>

## State

<one line: status, iteration, last decision; detail lives in STATE.json>

## Next-session reads (in order, target ≤ 8K tokens)

1. `python skills/ralph-loop/scripts/ralph.py --project <path> resume`
2. <frontier decision file>
3. <one more file, only if required>

## What the last iteration did

<2–3 lines; link `iterations/I-NNN.md`, do not restate it>

## Open questions and blockers

-

## Next action

<exactly one: which node to take, the smallest complete change, which CHECKs to run>

## Suggested skills

<name the skills the next session should invoke, e.g. grilling, agent-reach, unlazy>

## Learnings to promote

<pointers into LEARNINGS.md worth copying into the project's AGENTS.md at DONE>
