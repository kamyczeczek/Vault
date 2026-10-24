# skills/SKILLS.md — Layer-1 Skills Catalog

> Re-Orienting here is a routing descent by the same single
> agent into the skills area. This file is the catalog: it
> routes, it stores almost nothing. Each skill is a
> self-contained package; the catalog only knows each skill's
> name and what task it is for.
>
> Physical home: `skills/<name>/SKILL.md` at the workspace root (the full
> upstream set, D8); projects vendor their own subsets from here.
> This catalog is the registry of record, mapping task → skill without
> relying on a harness-specific discovery directory or global installation.

## 1. Purpose
This file tells the agent which skill to load for a given task.
Dispatch is **deterministic** — plain markdown, no LLM in the
routing loop. The agent matches the task against each skill's
`description` (in the skill's frontmatter) and picks the
best-fitting skill, then descends into that skill's `SKILL.md`.

Load the matching package's `SKILL.md` directly. Harness discovery and
slash commands, when available, are optional hints rather than authority;
this table is authoritative and works on any harness via plain file
reads. No automatic prompt loading is implied.

The catalog is checked against the filesystem by `skills/verify_catalog.py`
(runs as gate check R11, hard): every on-disk skill has exactly one row,
every row points at a real skill folder. Add or archive a skill folder and
the gate tells you the catalog has drifted — update it in the same change.

## 2. Routing Table
| Skill | Path | Trigger / intended use |
|---|---|---|
| ask-matt | `skills/ask-matt/` | Ask which skill or flow fits your situation. A router over the skills in this repo. |
| agent-reach | `skills/agent-reach/` | Internet read layer: 15 platforms via upstream CLIs/APIs (web, YouTube, RSS, GitHub, Reddit, Twitter, Bilibili, V2EX, ...). Use for web research, platform lookups, URL reading; `agent-reach doctor --json` shows live backends. |
| grilling | `skills/grilling/` | The interview primitive: relentless rounds over a design tree, frontier-first, with a recommended answer per question. The engine under `grill-with-docs`, `triage`, and `wayfinder`; reach it directly for the bare interview. |
| code-review | `skills/code-review/` | Review changes since a fixed point along standards and spec axes. |
| codebase-design | `skills/codebase-design/` | Deep-module vocabulary; finding deepening opportunities. |
| diagnosing-bugs | `skills/diagnosing-bugs/` | Diagnosis loop for hard bugs and performance regressions. |
| debug-with-memory | `skills/debug-with-memory/` | The door onto the workspace's past: before fixing an unfamiliar error, query the session-memory index (`scripts/debug.py` / `memory_index.py`) for a prior root cause, drill into the one hit worth reading, and record whether it helped. |
| domain-modeling | `skills/domain-modeling/` | Build/sharpen a project's domain model, write CONTEXT.md, record ADRs. |
| grill-with-docs | `skills/grill-with-docs/` | Relentless interview to sharpen a plan while creating ADRs and glossary. |
| grill-recorded | `skills/grill-recorded/` | `grill-with-docs` plus a hash-chained ledger: every turn is written to `session_store` as it happens, then settled decisions become ADRs and resolved terms land in `CONTEXT.md`. Use when a design conversation's outcome must survive the session. |
| icm-architect | `skills/icm-architect/` | Design any process/idea/problem into an ICM workspace (Build mode), restructure an existing folder/repo/vault into ICM conventions (Restructure mode), or audit code into a walkable edit map (System map form). Use when structuring, restructuring, or auditing a workspace. |
| implement | `skills/implement/` | Implement a piece of work based on a spec or set of tickets. |
| improve-codebase-architecture | `skills/improve-codebase-architecture/` | Scan a codebase for deepening opportunities, present as HTML report. |
| karpathy-guidelines | `skills/karpathy-guidelines/` | Behavioral constraints to reduce LLM coding mistakes: think before coding, simplicity first, surgical changes, goal-driven execution. Use before writing, reviewing, or refactoring code. |
| planning-with-files | `skills/planning-with-files/` | Manus-style persistent file-based planning: task_plan.md, findings.md, progress.md on disk so work survives context loss. |
| ponytail | `skills/ponytail/` | Lazy senior dev ladder: check stdlib, native platform, existing deps, one-liners before writing new code. Use for any coding task to prevent over-engineering, bloat, and wrong-abstraction bugs. |
| ralph-loop | `skills/ralph-loop/` | Run one human-confirmed, evidence-gated iteration using a decision graph, local project state, and a generated root activity index. Small resume-safe sessions: cold-start via `resume` (≤ 8K tokens), one frontier node per session, mandatory stamped `HANDOFF.md`, controller blocks DONE while gates are unmet; learnings promote to project AGENTS.md. |
| prototype | `skills/prototype/` | Throwaway prototype to answer a design question. |
| research | `skills/research/` | Investigate against primary sources, capture findings as Markdown. |
| tdd | `skills/tdd/` | Test-driven development loop and practices. |
| to-spec | `skills/to-spec/` | Turn requirements into a specification. |
| to-tickets | `skills/to-tickets/` | Break a spec into tracer-bullet tickets with blocking edges. |
| triage | `skills/triage/` | Triage incoming issues and bugs through a state machine. |
| unlazy | `skills/unlazy/` | Completion discipline for substantial autonomous work: acceptance gates before execution, Depth Tree decomposition, evidence re-verification before reporting. |
| wayfinder | `skills/wayfinder/` | Plan work too big for one session as a map of decision tickets. |
| git-guardrails-claude-code | `skills/git-guardrails-claude-code/` | Block dangerous git operations with guardrails. |
| claude-handoff | `skills/claude-handoff/` | Structured handoff protocol for agent session boundaries: compacts the conversation into a redacted summary and seeds a fresh background agent with it (`claude --bg --name "<desc>"`). |
| i-have-adhd | `skills/i-have-adhd/` | **Always on (root default):** shape every user-facing answer — action first, numbered steps, one next step, no preamble/recap/closers. Upstream: ayghri/i-have-adhd (MIT), vendored 2026-09-27. Overrides the skill's opt-in flag; off only on "stop adhd mode". |
| token-efficiency | `skills/token-efficiency/` | Measure and reduce context, retrieval, and tool-output waste in agent workflows. |
| token-hygiene | `skills/token-hygiene/` | Enforce anti-reread, delta-edit, scoped-read, and verification discipline. |

> Maintenance tool, not a skill: `skills/verify_catalog.py` — the
catalog⇄filesystem check described above; gate R11 runs it.


## 3. Routing Descent
When the agent reads `ROOT/AGENTS.md` and follows the `skills/`
row, it lands on this file. From here:

1. Match the current task against the skill `description`s in
   the Routing Table.
2. Descend into the matched skill folder under `skills/`.
3. Read that skill's `SKILL.md` and follow its steps.
4. Use its `assets/templates/`, `references/`, `agents/`,
   `scripts/` as needed.

## 4. Default routing
When a task matches no skill, there is no default descent:
the agent proceeds with its own judgment and does not force a
skill. Skills are applied when the table matches; they are
never a required step for every task.

## 5. How to add a new skill
1. Create a folder under `skills/`. Use a lowercase,
   hyphenated name matching `^[a-z][a-z0-9-]+$` (e.g.
   `icm-architect`, `code-reviewer`).
2. The skill folder MUST contain a `SKILL.md` with YAML
   frontmatter: `name` and `description` (the routing surface).
   Workspace catalog/index invariants require exactly one level deep:
   `skills/<name>/SKILL.md`.
3. Optionally add `assets/templates/`, `references/`, and a
   `README.md` inside the skill folder.
4. Add a row to the **Routing Table** above.
5. Commit: skills are project-local and git-tracked.

## 6. Filescope
- **Read:** this `SKILLS.md`, each skill's `SKILL.md` +
  frontmatter (`name`, `description`).
- **Write:** this `SKILLS.md` (when adding a skill to the table).
- **Forbidden:** modifying a skill's internal contents from
  this catalog. Each skill is a self-contained package; edits
  happen inside its own folder.

## 7. Out-of-scope
- The catalog does not contain skill content. It only routes.
- The catalog does not choose the skill via LLM reasoning in
  the loop; it is plain description matching. If no skill
  clearly fits, the agent proceeds without one.
- The catalog does not store state; it is re-read on every
  descent.
- The catalog does not modify skill internals.
- Vendored upstream repos (docs/scripts of skill authors) stay
  in `skills/<author>/` as reference material; they are not
  loadable skills.
