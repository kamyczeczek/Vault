---
type: Concept
title: WORKFLOW
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# PROCESS/WORKFLOW.md — Time Series Model Discovery Workflow

This workspace is a single-project deterministic pipeline. One agent walks
numbered stage folders; the filesystem is the state machine.

## 1. Stage routing

| Stage | Path | Purpose |
|---|---|---|
| 01_align | `PROCESS/01_align/CONTEXT.md` | Intake, scope, protocol |
| 02_research | `PROCESS/02_research/CONTEXT.md` | Read-only investigation |
| 03_plan | `PROCESS/03_plan/CONTEXT.md` | Slice plan, risks, lanes |
| 04_implement | `PROCESS/04_implement/CONTEXT.md` | Execute changes |
| 05_verify | `PROCESS/05_verify/CONTEXT.md` | Gates, tests, acceptance |
| 06_modify | `PROCESS/06_modify/CONTEXT.md` | Modify existing candidate |
| 07_reflect | `PROCESS/07_reflect/CONTEXT.md` | Reflection, learning |

Execution order: `01_align → 02_research → 03_plan → 04_implement → 05_verify`. Skip rules are stated in each stage's `CONTEXT.md`.

## 2. Stage contract

Each stage folder contains a `CONTEXT.md` with:
- **Inputs** — exact paths, split working/reference
- **Process** — numbered steps, short
- **Outputs** — exact filenames into `output/`
- **Human check** — one concrete action

The agent reads only the current stage's contract + its inputs. Target context: 2,000–8,000 tokens.

## 3. Knowledge routing

- Graph queries: `python brain/ask.py "<question>" --limit 5`
- Before query: `python brain/verify_sync.py --rebuild`
- Corpus additions: edit `brain/corpus/*.md`, then rebuild graph
- Reflection queries: `python brain/ask.py "<query>"`

## 4. Skills routing

Read `skills/SKILLS.md` for the task→skill table. Descend into matched skill folder and follow its `SKILL.md`.

## 5. Knowledge layer — Routing table

Deterministic query table. Run every row in section order at the listed stage boundary. `check_workflow.py` validates this table against live brains on every commit.

| K-01 | 01_align | skill | workspace folder taxonomy structure design icm | 1 | /icm-architect |
| K-02 | 01_align | skill | domain terminology context adr model | 1 | /domain-modeling |
| K-03 | 02_research | skill | investigate research question high-trust primary sources | 1 | /research |
| K-04 | 03_plan | skill | experiment design protocol metrics | 1 | /codebase-design |
| K-05 | 03_plan | skill | planning persistent file task_plan progress | 1 | /planning-with-files |
| K-06 | 04_implement | skill | prototype throwaway sanity check | 1 | /prototype |
| K-07 | 05_verify | skill | test driven development test-first | 1 | /tdd |
| K-08 | 05_verify | skill | diagnose bug failing broken performance regression | 1 | /diagnosing-bugs |
| K-09 | 05_verify | skill | code review standards commit | 1 | /code-review |
| K-10 | 07_reflect | skill | retrospective review improve | 1 | /retro |
| K-11 | 07_reflect | skill | handoff session continuity | 1 | /handoff |
| K-12 | 06_modify | skill | implement existing candidate modify codebase | 1 | /implement |

Row semantics:
- `skill` — passes if exit 0 AND top score ≥ min-score.
- `scar` — passes if exit 0. Any hit whose `owning_doc` touches this task’s files makes its invariants binding for this task.

If a row fails at commit time, fix the corpus/skill or adjust the query/min-score; never disable the row.

## 6. Git lifecycle & gate commands

### Pre-flight (Anchoring & Context)
```bash
git status --short                                # verify clean working tree before new work
git log -n 5 --oneline -- <touched_paths>         # inspect recent decisions/trailers on target files
git stash create                                  # capture anchor hash before risky/exploratory edits
```

### Gate verification
```bash
python PROCESS/run_gates.py --all                 # full gate suite
python PROCESS/run_gates.py --stage 05_verify     # single stage
python brain/internal/verify_sync.py --rebuild    # freshness gate before query
python brain/internal/verify_sync.py              # project brain sync
python PROCESS/check_reflection_close.py          # reflection schema + brain sync
python PROCESS/check_reflection_trigger.py --status complete  # trigger check
```

### Commit standard (P4 Trailers)
Every completed milestone MUST be committed with native git trailers:
```bash
git commit -m "<type>(<scope>): <summary>

<Optional detailed explanation of change>

Intent: <Why this change was made>
Rejected-Alternative: <What was considered and why it was rejected, or None>
Verified-By: <Command output or test log>
Gates-Passed: <List of verified gates>"
```
## 7. Out of scope

Real-time multi-agent orchestration, high-concurrency serving, automated mid-pipeline branching. This workflow is sequential, human-reviewed, repeatable.
