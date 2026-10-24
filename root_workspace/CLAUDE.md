---
type: Concept
title: CLAUDE
generated: { by: okf-enforcer/0.6, at: 2026-10-23T19:30:46Z }
---

# CLAUDE.md — workspace

Workspace of independent research projects. Each project under `projects/research/` is
self-contained: its own git repo, its own entry file, its own contracts. This
file routes; it holds no content.

## Where things live

| Path | Role | Description |
|---|---|---|
| `CLAUDE.md` | Catalog (L0) | This file — identity and routing |
| `AGENTS.md` | Router (L0) | Terse agent entry (<2K tokens): intent → project. Points here for detail |
| `CONTEXT-MAP.md` | Map (L1) | The portfolio map: bounded contexts, what each project owns, relationships, what is shared, the routing procedure |
| `TOOLS.md` | Rubric (L1) | Tool lifecycle: the promotion bar and the three verdicts |
| `SCARS.md` | Lessons | Operational scars from real failures: Windows tooling, executable, verification-tool, metric-design. Read before editing `scripts/**`, `hooks/**`, `skills/**`, `check_workspace_integrity.py`, `audit_*.py`; trigger: `handoff/CONTEXT.md` |
| `DECISIONS.md` | Record (L1) | Why the portfolio looks the way it does, with rejected options |
| `PHILOSOPHY.md` | Principles (L1) | First read: why small working systems compose; what the workspace proved |
| `GLOSSARY.md` | Vocabulary (L1) | One definition per shared term; projects narrow, never redefine |
| `HANDOFF.md` | Cold start (L0) | Where the work stands and what is open, at the level a fresh session needs. Links project handoffs, never copies them (D12) |
| `STATE.md` | Snapshot (generated) | Machine-derived right-now: HEAD, dirty files, last commits, runs + verdicts. Rebuild via `python scripts/build_state.py`, never hand-edit (ICM inv. 9) |
| `handoff/` | Handoff state (one flag = one file) | `flags/<flag>.md` (one writer per flag, frontmatter `flag`/`since`/`owner`/`agent`/`model`) + `deep/*.md` for prose. `HANDOFF.md` is the generated view: rebuild via `python scripts/build_handoff.py`, `--check` gates staleness. Contract: `handoff/CONTEXT.md` |
| `handoff/state_description/` | Export | Workspace + per-project state snapshots (repomix), 3 poziomy workspace × 2 poziomy projekt. Contract: `CONTEXT.md`; wybór poziomu: `README.md`; run: `python handoff/state_description/scripts/run_exports.py` |
| `skills/` | Factory (L3) | Upstream catalog of agent workflow skills — the full set, kept redundant for root-level changes. Projects vendor their own subsets from here (D8) |
| `projects/research/` | Portfolio | The research projects — one group folder, one folder one subject |
| `projects/_archive/` | Graveyard | Finished work, ungated and unrouted (D10) |
| `.ralph/` | Index (generated) | ralph-loop navigation projection: `INDEX.md` + `registry.json`, rebuilt by `skills/ralph-loop/scripts/ralph.py` from each project's local `.ralph/STATE.json`; never hand-edited (projects keep their own `.ralph/` as source of truth) |
| `.pi/` | Harness (generated) | pi coding-agent working settings (empty default `settings.json`, auto-created by the harness; never hand-edited) |
| `.opencode/` | Config | opencode project config: custom subagents (`.opencode/agents/answerpilot.md` — answer-layer pilot, tools denied via permissions + corpus read-block); declared in ALLOWED_ROOT |
| `.commit-approved` | Gate token (runtime) | Commit-approval token. Minted by `scripts/close.py` after validation and immediately before its own commit; read by `scripts/commit_gate_guard.py`, which `hooks/pre-commit` calls before the integrity gate. A token older than 300 s authorizes nothing. Listed in `.gitignore`, never committed |
| `.agents/` | Plugins | goose lifecycle plugins (e.g. `forge-guardrails` hooks); auto-load from project dir |
| `.forge/` | Policy | forge-guardrails single source of truth (`policy.yaml`) + runtime state/journal; enforced by hooks, read by CI |
| `scripts/` | Gate | `check_workspace_integrity.py` — the only check that sees the workspace root. Run before every commit **by convention, not by a hook**: as of 2026-10-03 there is no `core.hooksPath` and no CI in this repo, so nothing enforces it. See the `gate_has_no_automatic_caller` flag |
| `hooks/` | Git hooks | Repository hooks; `hooks/pre-commit` runs `git diff --cached --check` and the workspace integrity gate before a commit. **Per-clone**: a fresh clone must run `git config core.hooksPath hooks` — the setting is local, not versioned |
| `tools/` | Tools | Small single-file tools (one file = one job = one `--selftest`); router `tools/README.md`, contract per tool `tools/<name>.md` |
| `scripts/memory/` | Recall (L1) | Session memory: the contract for the FTS5 index over past agent sessions — when an agent must query it (a convention, not an automatic call: nothing invokes it), the survey-then-`get` pair, and the ingest cadence. Store (`scripts/_scratch/sessions/05_store/memory.db`) is derived and gitignored; R14 keeps it a day fresh and refuses to pass when it cannot compare. Run it with `python.exe` — the WSL `python3` sees no agent store |
| `scripts/_scratch/sessions/` | Sessions lab (derived) | Readable views of agent sessions: raw / did / merged / ground-truth products, per-session records, tool payloads, the memory store. Entry: `scripts/_scratch/sessions/CLAUDE.md`; contract per folder `CONTEXT.md`. Everything is derived and gitignored — regenerate, never hand-edit |
| `WORKFLOW_GOOSE_ICM.md` | Design | Goose research-to-implementation workflow (ICM Pipeline design); factory vs per-run product, human gates |
| `.dgc-evidence/` | Runs | Per-run product: `.dgc-evidence/runs/<run-id>/REVIEW.md` + `REVIEW.html` + `DECISION.json`; `LATEST` names the run awaiting verdict. Reviewed via `python scripts/review.py <run-dir>` |
| `docs/workflow/README.md` | Reference | Enforcement mechanisms: scan_secrets, pre_close_check, verify_report_evidence (contract: `docs/workflow/CONTEXT.md`) |
| `docs/reviews/` | Audits | Workspace-level audit reports (e.g. the architecture review). **Typed directory**: every `*.html` here is an audit report and must carry exactly one `<!-- audit:begin -->`/ `<!-- audit:end -->` pair or the root gate fails (R13). A report that quotes a measured number embeds `scripts/audit_agents_md.py` output — including its derived sums — between the markers and never types a live total in prose; `docs/reviews/README.md` is the contract and the provenance of each file |
| `agents/` | Registry | Where every AI agent's config, data and secrets live on this machine: `agents/REGISTRY.md` (path table per agent), `agents/RESTORE.md`, `agents/backup-agents.ps1` + the `agents/backup/` snapshot dir. Bookkeeping, not source; created 2026-10-04. **Docs are tracked; `agents/backup/` (snapshot zips containing live agent configs + auth) is gitignored and never committed** |
| `brain/` | Database | Project Brain SQLite FTS5 database (derived, gitignored) + the curated layer: scars/decisions/lessons, rebuilt from `SCARS.md`/`DECISIONS.md`/`brain/lessons.md` by `python.exe scripts/ingest_brain.py`. Door: `python.exe scripts/brain.py "<topic>"` — answers *what is the rule about X?*; the other layer (session memory, *did I try this before?*) is `scripts/memory/`. Contract: `brain/CONTEXT.md`; gate: R21 |
| `wayfinder/` | Planning | Wayfinder maps and architecture plans |
| `../.obsidian/` | Obsidian state (vault) | Obsidian per-device state at the vault root, beside the workspace folder; community plugins and configs tracked, workspace/cache/graph gitignored (ADR-006) |
| `../.smart-env/` | Smart Connections (vault) | Smart Connections vector index at the vault root; derived, gitignored except `smart_env.json`, regenerated after the plugin is installed (ADR-006) |
| `../Notes/` | Vault notes (vault) | User notes at the vault root; tracked in the private repo (ADR-006) |
| `../.git/` | Repo root (vault) | One repository for the whole vault; the workspace is a subfolder of it, not its own repo (ADR-006, ADR-007) |
| `PLAN.md` | Plan | Workspace reorganization master plan |
| `TASKS.md` | Tasks | Reorganization ticket list (TASKS.md) |

## Projects

| Project | Subject | Entry |
|---|---|---|
| `projects/_archive/agentic-research-lab/` | Agentic research loop (archived 2026-10-08; read-only precedent source) | `projects/_archive/agentic-research-lab/CLAUDE.md` |
| `projects/research/knowledge-retrieval/` | Quality of knowledge digestion and retrieval — the read path against the graph | `projects/research/knowledge-retrieval/CLAUDE.md` |
| `projects/research/benchmark-core/` | Time-series forecasting models and the cross-domain benchmark harness | `projects/research/benchmark-core/CLAUDE.md` |
| `projects/research/etth1-h720/` | Long-horizon (H720) ETTh1 forecasting line: H2K, SAB-L, AMR-24/168 | `projects/research/etth1-h720/CLAUDE.md` |
| `projects/research/research-engine/` | Autonomous model-mutation and discovery loop, plus knowledge-graph tooling | `projects/research/research-engine/CLAUDE.md` |
| `projects/research/brain/` | Project Brain sidecars — derived FTS5 corpus and graph per project | `projects/research/brain/CLAUDE.md` |

> `projects/datasets/` archived 2026-09-27 to `projects/_archive/datasets/`
> (`grade: demoted`; synthetic fetchers, broken entry points, INBOX walkers).
> Rebuild as a new project per its contract; see D10.

## Route by intent

Single home per fact: intent → entry file routes live in `AGENTS.md`
("Where to go"); research request → owning project in `CONTEXT-MAP.md`
§Routing. This file routes, it does not repeat either table.
| Find out why something is the way it is | `DECISIONS.md` |
| Look up a shared term | `GLOSSARY.md` |

## Rules

- **One folder, one job.** A project that serves two subjects is two projects.
- **No cross-project copies.** Link to a sibling's file; do not fork it. If two
  projects need the same code, it belongs in `skills/` or one named project.
- **Every project owns its skills.** A project vendors the skills it uses into
  its own `skills/`, with a `MANIFEST.md` naming the upstream and the date
  vendored. The root `skills/` keeps a full redundant set (D8). Resolution
  order: the project's own `skills/` first, then the root.
- **A vendored skill is never silently updated.** Re-vendor deliberately and
  bump the stamp — that is the accepted cost of locality (D8).
- **Every project declares its `grade`** in its entry file frontmatter:
  `candidate | active | demoted` (D4). The gate fails a project that declares
  none, because an undeclared grade is indistinguishable from a stale one.
- **Every project carries its open work** in `## Open work` in its `CONTEXT.md`
  (D7). "Nothing known" is a valid sentence; a missing heading is not.
- **Derived state is gitignored.** Graph databases, corpus dumps, and fetched
  datasets are rebuildable artifacts, not source.
- **Each project answers for its own gates.** Read its entry file before its code.
- **The root holds only what this file lists.** A new root-level entry is a
  structural decision — the procedure lives in the gate's docstring
  (`scripts/check_workspace_integrity.py`), single home. A file that
  appears at the root any other way is debris until proven otherwise.

## Conventions

- Entry file: `CLAUDE.md` (L0, under ~60 lines for projects; root catalog
  exempt per D9 amendment, routes only).
- Root `CONTEXT-MAP.md` (L1): the portfolio map — what the projects share,
  how they relate; one home, nothing at the root restates it.
- Stage contracts: `CONTEXT.md` inside each working folder — inputs, process,
  outputs, one human check.
- Content: plain markdown with YAML frontmatter. One home per fact; link, don't copy.
- Module maps: `MAP.md` per project, **generated** by
  `scripts/build_project_map.py`, never hand-edited (D9). One row per module —
  role, inputs, outputs, used by.
- Skills: a project's `skills/` is its own; the root `skills/` is upstream.
  Vendor on first use, stamp in `MANIFEST.md` (D8).
