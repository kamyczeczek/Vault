---
type: Concept
title: SKILLS
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# skills/SKILLS.md — Layer-1 Skills Catalog

> Re-Orienting here is a routing descent by the same single
> agent into the skills area. This file is the catalog: it
> routes, it stores almost nothing. Each skill is a
> self-contained package; the catalog only knows each skill's
> name and what task it is for.
>
> Physical home: `skills/<name>/SKILL.md`, project-local and git-tracked.
> This catalog is the registry of record, mapping task → skill without
> relying on a harness-specific discovery directory or global installation.

## 1. Purpose
This file tells the agent which skill to load for a given task.
Dispatch is **deterministic** — plain markdown, no LLM in the
routing loop. The agent matches the task against each skill's
`description` (in the skill's frontmatter) and picks the
best-fitting skill, then descends into that skill's `SKILL.md`.

Load the matching package's `SKILL.md` directly. Harness discovery and
slash commands, when available, are optional hints rather than authority.
OMP's `--skills` option filters skills; it does not add discovery paths.
- **Routing signal**: `brains/skills_brain/digest.md` is the up-to-date,
  token-budgeted artifact generated from this catalog. Read it explicitly;
  generation and the freshness gate compare this local file, not an overlay.
  No automatic prompt loading is implied (see `brains/CONTEXT.md` §3).

Use this catalog for task→skill routing when working agent-side
per `AGENTS.md` §2; explicit file reads work independently of the harness.

## 2. Routing Table
| Skill | Path | Trigger / intended use |
|---|---|---|
| icm-architect | `skills/icm-architect/` | Design any process/idea/problem into an ICM workspace (Build mode), restructure an existing folder/repo/vault into ICM conventions (Restructure mode), or audit code into a walkable edit map (System map form). Use when structuring, restructuring, or auditing a workspace. |
| planning-with-files | `skills/planning-with-files/` | Manus-style persistent file-based planning: task_plan.md, findings.md, progress.md on disk so work survives context loss. |
| unlazy | `skills/unlazy/` | Completion discipline for substantial autonomous work: acceptance gates before execution, Depth Tree decomposition, evidence re-verification before reporting. |
| agent-reach | `skills/agent-reach/` | Internet read layer: 15 platforms via upstream CLIs/APIs (web, YouTube, RSS, GitHub, Reddit, Twitter, Bilibili, V2EX, ...). Use for web research, platform lookups, URL reading; `agent-reach doctor --json` shows live backends. |
| ask-matt | `skills/ask-matt/` | Ask which skill or flow fits your situation. A router over the skills in this repo. |
| code-review | `skills/code-review/` | Review changes since a fixed point along standards and spec axes. |
| codebase-design | `skills/codebase-design/` | Deep-module vocabulary; finding deepening opportunities. |
| diagnosing-bugs | `skills/diagnosing-bugs/` | Diagnosis loop for hard bugs and performance regressions. |
| domain-modeling | `skills/domain-modeling/` | Build/sharpen a project's domain model, write CONTEXT.md, record ADRs. |
| grill-with-docs | `skills/grill-with-docs/` | Relentless interview to sharpen a plan while creating ADRs and glossary. |
| implement | `skills/implement/` | Implement a piece of work based on a spec or set of tickets. |
| improve-codebase-architecture | `skills/improve-codebase-architecture/` | Scan a codebase for deepening opportunities, present as HTML report. |
| prototype | `skills/prototype/` | Throwaway prototype to answer a design question. |
| research | `skills/research/` | Investigate against primary sources, capture findings as Markdown. |
| resolving-merge-conflicts | `skills/resolving-merge-conflicts/` | Resolve in-progress git merge/rebase conflicts. |
| tdd | `skills/tdd/` | Test-driven development loop and practices. |
| to-spec | `skills/to-spec/` | Turn requirements into a specification. |
| to-tickets | `skills/to-tickets/` | Break a spec into tracer-bullet tickets with blocking edges. |
| triage | `skills/triage/` | Triage incoming issues and bugs through a state machine. |
| wayfinder | `skills/wayfinder/` | Plan work too big for one session as a map of decision tickets. |
| wizard | `skills/wizard/` | Interactive bash wizard for human-only steps (infra, credentials, CI). |
| claude-handoff | `skills/claude-handoff/` | Handoff workflow for Claude. |
| implement-spec | `skills/implement-spec/` | Implement a specification directly. |
| loop-me | `skills/loop-me/` | Run iterative feedback loops. |
| retro | `skills/retro/` | Conduct retrospectives. |
| setup-ts-deep-modules | `skills/setup-ts-deep-modules/` | Setup deep TypeScript modules with dependency cruiser. |
| writing-beats | `skills/writing-beats/` | Writing narrative beats. |
| writing-fragments | `skills/writing-fragments/` | Writing short prose fragments. |
| writing-shape | `skills/writing-shape/` | Shaping writing structure. |
| git-guardrails-claude-code | `skills/git-guardrails-claude-code/` | Block dangerous git operations with guardrails. |
| migrate-to-shoehorn | `skills/migrate-to-shoehorn/` | Migrate projects to shoehorn layout. |
| scaffold-exercises | `skills/scaffold-exercises/` | Scaffold learning or coding exercises. |
| setup-pre-commit | `skills/setup-pre-commit/` | Setup pre-commit hooks. |
| setup-matt-pocock-skills | `skills/setup-matt-pocock-skills/` | One-time repo setup for the engineering skills: issue tracker, triage label vocabulary, domain doc layout. |
| grill-me | `skills/grill-me/` | Grill me session for sharpening thoughts. |
| grilling | `skills/grilling/` | Grilling process for requirements. |
| handoff | `skills/handoff/` | Structured session handoff. |
| teach | `skills/teach/` | Teaching structured knowledge. |
| to-questionnaire | `skills/to-questionnaire/` | Turn unstructured thoughts into a questionnaire. |
| wait-what | `skills/wait-what/` | Sanity check and reality check. |
| writing-for-agents | `skills/writing-for-agents/` | Writing markdown optimized for AI agents. |
| timeseries-classical | `skills/timeseries-classical/` | Classical forecasting models: ARIMA, SARIMA, ETS, Holt-Winters. Baseline protocol and when to use classical methods. |
| timeseries-deep-learning | `skills/timeseries-deep-learning/` | Deep learning forecasting: LSTM, GRU, TCN, Transformer, PatchTST, iTransformer, NLinear, DLinear. Selection, implementation, and comparison. |
| timeseries-evaluation | `skills/timeseries-evaluation/` | Forecasting evaluation: metric selection (MAE, MSE, MAPE, sMAPE, MASE, CRPS), backtesting, probabilistic metrics, baseline comparison rules. |
| timeseries-methodology | `skills/timeseries-methodology/` | Time series methodology: classical model selection, baseline protocol (naive, seasonal naive, classical), classical vs ML vs deep learning guidance. |
| timeseries-ml | `skills/timeseries-ml/` | Machine learning for forecasting: XGBoost, LightGBM, CatBoost, feature engineering (lags, rolling stats, date features), hybrid classical+ML approaches. |

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
