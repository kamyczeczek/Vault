---
name: ralph-loop
description: Run one human-confirmed, evidence-gated iteration of a project or workspace task using a decision graph, local run artifacts, and a generated root activity index. Each session is small and resume-safe: cold-start from one command, do one frontier node, leave a stamped handoff. Use for substantial coding, research, maintenance, documentation, or skill-work tasks.
disable-model-invocation: true
---

# Ralph Loop

Use Ralph as a **decision-graph pipeline**, not as an unbounded task list. The loop advances one frontier node per iteration and always stops for human confirmation.

## Scope and storage

For a project, create the run under `<project>/.ralph/runs/YYYY-MM-DD_<slug>/`. For workspace maintenance, use `.ralph/runs/...` at the workspace root. The project-local `.ralph/` is the source of truth. The workspace root `.ralph/INDEX.md` and `registry.json` are generated navigation projections.

Do not run two active Ralph runs in one project unless the user explicitly approves the coordination plan.

## Small-session contract

A session is **resume + one iteration + one handoff**, sized to fit a short context:

- **Cold start costs ≤ 8K tokens:** `ralph.py resume` (state + gates + read list), the run's `HANDOFF.md`, and the frontier decision node. Load nothing else until the node demands it. That is the ICM rule: load only what the step needs; the catalog files are small on purpose.
- **One iteration per session**, on the one frontier node. If context degrades mid-node, stop: leave the node `OPEN` with the reason in its decision file, write the handoff, record the iteration. A half-done node with a clean handoff beats a confident rushed one.
- **Every session ends by rewriting `HANDOFF.md`** (stamped) for the next session. The controller refuses to record an iteration without it — the loop cannot silently lose its thread.
- Never begin the next iteration in the same turn after reaching `WAITING_FOR_CONFIRMATION`.

## Start a run

0. **Sharpen before scaffolding.** Grill intent and destination with `grill-with-docs` (one round, with a recommended answer attached to each question); settled answers become decision nodes, not prose. External facts block a node → research it now via `agent-reach`/`research` and record the finding in the node's Context. Work bigger than one route through → `wayfinder` first: chart the fog into PLAN.md's *Not yet specified* and ticket only what is specifiable now.
1. Read the workspace `AGENTS.md`, the target project's `CLAUDE.md` and `CONTEXT.md`, and the relevant local contract.
2. Create the run from `assets/templates/` and fill `REQUEST.md`, `PLAN.md`, and `GATES.md`.
3. Represent decisions as separate `decisions/D-NNN.md` files. Link each node from `PLAN.md`; never hide a decision only in prose.
4. Record the frontier: the open, unblocked node that can be handled next.
5. Set local `STATE.json` to `READY` and update the root index.
6. `init` also copies `HANDOFF.md` and `LEARNINGS.md`; fill the handoff so the very next session can resume it.

## Resume and one iteration

An iteration owns exactly one frontier node and one observable outcome:

1. **Resume ritual.** `ralph.py resume` gives state, gate counts, and `read_next`. Read `HANDOFF.md`, then the frontier decision node and only its declared dependencies (plus the project inputs the node names). Target: ≤ 8K tokens of reads before work starts.
2. Set state to `WORKING`; record the selected node and allowed paths in the iteration.
3. Make the smallest complete change. Do not silently widen scope or resolve a human decision yourself.
4. Run the approved targeted checks. Treat every `CHECK:` line as code: inspect it before running, run only understood commands, record command + exit status + evidence. A green command is not proof of an unrelated claim.
5. Set the node to `RESOLVED`, `BLOCKED`, or leave it `OPEN` with the reason in its decision file. Append any discovered pattern or gotcha to the run's `LEARNINGS.md` — one line, dated.
6. **Rewrite `HANDOFF.md` for the next session** and stamp its front-matter `updated:`. The next session must be able to start from this file alone.
7. `ralph.py record-iteration ...` with the next frontier and `CONTINUE`, `DONE`, or `BLOCKED` outcome; it stamps the handoff, updates local `STATE.json`, appends `history.jsonl`, and regenerates the root `.ralph/registry.json` and `INDEX.md`.
8. Set the run to `WAITING_FOR_CONFIRMATION` and stop.

## Confirmation boundary

Only an explicit user confirmation such as `approve next iteration` changes `WAITING_FOR_CONFIRMATION` to `APPROVED`. Then perform one new iteration. Confirmation does not approve commits, pushes, deploys, destructive operations, or unresolved decisions unless the user states that separately.

## Statuses

Run: `READY → WORKING → VERIFICATION → WAITING_FOR_CONFIRMATION → APPROVED → DONE`.

Alternative terminal states are `BLOCKED` and `ABANDONED`. Decision nodes use `OPEN`, `IN_PROGRESS`, `RESOLVED`, and `SUPERSEDED`. A superseded decision remains in history and links to the decision that replaced it.

## Evidence and gates

Use `GATES.md` before implementation for substantial work. Every gate must be observable, and runnable gates need a `CHECK` and `EXPECT`. A run with no observable outcome declares `GATES: none` and deletes its placeholder boxes; the controller counts any leftover checkbox as unmet. Never delete a failing artifact to make a gate pass. If a gate cannot be met, record `ABANDON: <id> <reason>` — abandonment is terminal, never success — and surface it as a required handoff. `ralph.py gates` reports met/unmet/abandoned at any time, and `record-iteration --outcome DONE` is refused while any required gate is unmet or abandoned.

## Learnings

The loop improves work over time only if discoveries leave the run. `LEARNINGS.md` is append-only; at DONE, the human gate promotes the load-bearing entries into the project's `AGENTS.md`/`CONTEXT.md` so the next session — agent or human — inherits them. This is the step that makes iteration N+1 cheaper and better than iteration N.

## Finish and report

Declare `DONE` only when all required gates are met, the destination in `PLAN.md` is reached, no decision is unresolved, and the final evidence was re-verified. Report changed paths, measured gates, current state, next frontier, and the human action required. The root index answers only what was last done and where details live; it is never a second source of truth.

## Controller

Use `scripts/ralph.py` from the workspace root:

```text
python skills/ralph-loop/scripts/ralph.py --project projects/example init feature-x "intent" "destination" --frontier D-001
python skills/ralph-loop/scripts/ralph.py --project projects/example resume
python skills/ralph-loop/scripts/ralph.py --project projects/example gates
python skills/ralph-loop/scripts/ralph.py --project projects/example approve --frontier D-002
python skills/ralph-loop/scripts/ralph.py --project projects/example index --workspace .
```

`init` creates the local state and run directory. `resume` is the fresh-session cold start: it prints state, gate counts, the stamped handoff time, and the exact files to read next. `gates` reports gate health without touching state. `approve` advances the iteration counter but does not perform work; the agent performs the iteration and `record-iteration` — which refuses to run unless the run's `HANDOFF.md` is stamped and, for a `DONE` outcome, all required gates are met — sets `WAITING_FOR_CONFIRMATION`. `index` regenerates the workspace projection and prints only a one-line summary. The controller never commits, pushes, deploys, or executes task commands.

## Templates

Copied into each run by `init`:

- `assets/templates/REQUEST.md`, `PLAN.md`, `DECISION.md`, `ITERATION.md`, `GATES.md`, `HANDOFF.md`, `LEARNINGS.md`

The filesystem and append-only history are the state machine. Keep routing files short, link to detail, and preserve superseded decisions rather than rewriting history.
