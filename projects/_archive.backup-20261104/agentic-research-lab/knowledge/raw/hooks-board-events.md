---
type: Concept
title: "Hooks as Board Events: PostToolUse → events.jsonl → Live Flow"
source: "https://code.claude.com/docs/en/hooks + https://github.com/glitch-cat-club/chief-of-staff-crew (board.py) + https://github.com/patoles/agent-flow"
tags: [context-engineering, icm, hooks, observability, agents, planning]
retrieved: 2026-09-15
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

Hooks are lifecycle shell commands that fire on every Claude Code event: `SessionStart`, `PreToolUse`/`PostToolUse` (per tool call), `PostToolBatch`, `SubagentStart`/`SubagentStop`, `Stop`, etc. Config in `.claude/settings.json` by event → matcher (tool name) → handler (command/http/mcp_tool/prompt/agent). chief-of-staff-crew uses them minimally for observability, not enforcement: `.claude/settings.json` wires `PreToolUse` on `Agent` → "spawn" event, `PostToolUse` on `TodoWrite` → "board" items, on `Edit`/`Write`/`MultiEdit` → "edit", on `Read` → "read". `board.py` appends one JSONL row per event to `board/events.jsonl` — never blocks, never fails a tool. `board/index.html` polls that file and renders the live flow (lanes, working pips, DONE ticks, iframe viewport) while `serve.py` serves with `no-store`.

Generalizes to `patoles/agent-flow`: Claude Code HTTP hook server streams events with zero latency into a node-graph visualizer; tails `events.jsonl` for replay. Same primitive as `pi-subagents` observability (`async-subagent-runs/<id>/events.jsonl` with `subagent.run.started/completed`, `subagent.steer.*`).

Implication for brain: hooks are the "board" for `spawn_recursive.py` leaves — add a `PostToolUse` hook on `Agent` + `Write` that appends to `reflection/leaves/events.jsonl` so a static `board/index.html` can show leaf lanes (like chief-of-staff's four). Keep hook non-blocking (no decision) to preserve determinism; gate separately via `watch.py` + `check_reflection.py`.

Provenance: code.claude.com/hooks + hooks-guide + chief-of-staff-crew board.py + agent-flow, retrieved 2026-09-15 via agent-reach Exa.
