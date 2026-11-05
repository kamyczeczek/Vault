---
type: Concept
grade: demoted
title: CLAUDE
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# CLAUDE.md — agentic-research-lab

Scientific research workspace for investigating and advancing **how to perform agentic research well**.
Built on Interpretable Context Methodology (ICM): verified corpus markdown -> derived FTS5 graph -> reflection -> meta-learning workflow updates.

## Default work mode: ralph-loop

Substantial work in this project runs as a ralph-loop run (vendored `skills/ralph-loop/SKILL.md`):
**session = `resume` cold start (≤ 8K tokens) → one frontier-node iteration → stamped handoff → stop.**
- Enter the loop: `python skills/ralph-loop/scripts/ralph.py --project . resume` and follow its `read_next`.
- New task with no active run: start the run first (grill the destination; wayfinder if it spans one root).
- Infra/preflight repairs and one-shot chores stay out of runs: log them in the active run's
  `LEARNINGS.md`, or use a mini run with `GATES: none` if there is no active run.
- The controller refuses iteration records without a stamped `HANDOFF.md` and blocks `DONE` while any
  required gate is unmet — that is the completion contract, not a suggestion.
- `STATE.md` (the old bounded "Ralph pilot") is superseded as the work mode since 2026-10-02; kept for history.
- Verification bar (promoted from `.ralph/runs/2026-10-01_trustworthy-agent-tests/LEARNINGS.md` at I-003, 2026-10-02): a trustworthy agent test is oracle-first (expected value from spec, not from the code), mutation-checked (does it bite?), independently re-derived, and evidence-logged (command + actual + expected + exit); a green suite without a stated expected value is not VERIFIED.
- At a verification iteration, re-run the gate CHECK yourself and re-check prior iteration evidence on disk before attempting DONE; a human-ownership gate (G2-style) blocks `--outcome DONE` and must be handed to a human with exact handoff steps, never self-met.

## Where things live

| Path | Role | Description |
|---|---|---|
| `CLAUDE.md` | Catalog (L0) | Entry point and workspace map (this file) |
| `CONTEXT.md` | Contract (L1) | Root operating contract and chunk format |
| `INBOX/` | Intake (L4) | Raw seed papers and research notes (emptied on ingestion) |
| `knowledge/raw/` | Factory (L3) | Archived raw sources + derived `manifest.jsonl` |
| `knowledge/corpus/` | Source of truth (L3) | Canonical markdown chunks (`NN_slug.md`) |
| `knowledge/graph/` | Derived brain (L3) | FTS5 graph database, digest, and query tools |
| `knowledge/topics.md` | Controlled vocabulary | Registered topic tags for routing |
| `stages/` | Stage contracts (L2) | Contracts for phases `00_expand` through `06_meta_evolve` |
| `pipeline/` | Pipeline workflow | Global ordered plan `pipeline/WORKFLOW.md` |
| `reflection/` | Product (L4) | Generated `reflection/digests/`, `reflection/candidates/`, `reflection/sessions/` (bounded per-session .md exports), and `reflection/memory.md` |
| `EXPERIENCE.md` | Local experience | Agentmemory stack runbook, scars, and reapply procedures (not gated) |
| `scripts/` | Verification & tooling | Phase gates, manifest checks, eviction, meta-learning |
| `docs/MEMORY_ARCHITECTURE_STATUS.md` | Memory architecture status | Research-prototype boundary, reinvention register, adoption gates, and limitations |
| `docs/MEMORY_ACCEPTANCE_PROOFS.md` | Memory acceptance proofs | Reproducible proof runner and verified foundation contracts |
| `../../../skills/` | Shared factory (L1) | Reusable agent workflow packages, owned by the workspace root. See `../../../skills/SKILLS.md` |
| `skills/` | Local factory (L3) | This project's own skill copies, vendored from `../../../skills/` on first use. Stamped in `skills/MANIFEST.md`; this folder shadows the root catalog |

## Route table by intent

| Intent | Where It Routes |
|---|---|
| Search & fetch scientific literature | `scripts/expand_literature.py` → `INBOX/` |
| Ingest new material / raw sources | `INBOX/` → `scripts/ingest.py` |
| Query knowledge graph / brain | `knowledge/graph/ask.py` |
| Rebuild knowledge graph | `knowledge/graph/build_graph.py` |
| Run isolated reflection on topic | `pipeline/06_reflect/spawn.py --topic <slug>` |
| Verification run (writes to scratch, not the graded corpus) | `pipeline/06_reflect/spawn.py --topic <slug> --scratch` |
| Think through an idea with an expert | `python scripts/discuss.py new "<thesis>"` — a markdown file in `INBOX/ideas/` is the conversation, the state, and the artifact |
| Promote / evict memory candidates | `scripts/promote_candidate.py` / `scripts/evict_stale.py` |
| Apply meta-learning to evolve workflow | `scripts/apply_meta_learning.py` |
| Close a session (export .md + consolidate + gate) | `python scripts/close_session.py` |
| Configure agentmemory LLM / `.env` (validated model) | `python scripts/configure_agentmemory_env.py` |
| Restart agentmemory engine | `powershell -File scripts/restart_agentmemory.ps1` (add `-Elevated` if the tree is elevated) |
| Agentmemory stack runbook & scars | `EXPERIENCE.md` |
| Two-layer memory architecture | `docs/REFLECTION_MD_ARCHITECTURE.md` + `docs/MEMORY_ARCHITECTURE_STATUS.md` |
| Run pipeline gates & audit | `scripts/check_*.py` and `scripts/audit_workspace.py` |
| Grade one run's own artifacts (not the whole tree) | `python scripts/check_reflection.py --paths <topic-slug>` |
| Copy graded artifacts before a gate reads them | `python scripts/snapshot_graded.py --paths <topic-slug>` |
| Collect a finished background run | `cat reflection/logs/<topic>.status.json`; `preflight.py` blocks on `failed`/`running` runs whose artifacts still fail |
| Recover an artifact a gate flagged | `reflection/.snapshots/<ts>-pre-gate/` (deletion of graded evidence is blocked by `scripts/hook_guard_evidence.py`) |
| Check the workspace root is clean | `python ../../../scripts/check_workspace_integrity.py` — runs as gate Q0 on every commit here; the eighteen project gates cannot see above this repo |
| Cross-project audit & bridge | `BRIDGE PROJECT <path>` (Ref: `docs/recipes/UNIVERSAL_PROJECT_BRIDGE.md`) |

## Autonomous graph-use policy

Agents do not need a user reminder to decide whether the graph is useful. Before beginning a task, run:

```text
python scripts/graph_decision.py "<task intent>" --class <research|reflection|repair|coding|maintenance|git>
```

If `use_graph` is true, query `knowledge/graph/ask.py` or `pipeline/06_reflect/route.py` before making knowledge-bearing decisions. If `required` is true, do not proceed on unsupported assumptions. Mechanical tasks may proceed without retrieval, but must still validate their result. The decision is recorded as a typed trace event.
## Common tasks

- **Automatic task context:** Start substantive work with `python scripts/agent_task.py "<task intent>" --class <class>`. It decides graph relevance and automatically retrieves context when appropriate; do not rely on a user reminder.
- **Fetch scientific paper/topic:** `python scripts/expand_literature.py --query "agentic research workflow" --source arxiv`
- **Ingest new material:** Put raw files into `INBOX/`, then run `python scripts/ingest.py`.
- **Rebuild graph:** `python knowledge/graph/build_graph.py`.
- **Query the brain:** `python knowledge/graph/ask.py "<question>"` or with `--tag <t>`.
- **Spawn reflection:** `python pipeline/06_reflect/spawn.py --topic <topic-slug>`
- **Evolve workflow from findings:** `python scripts/apply_meta_learning.py`
- **Audit workspace:** `python scripts/audit_workspace.py`
- **Close the session:** `python scripts/close_session.py` (transcript → `reflection/sessions/*.md` → agentmemory consolidation → gates)

## Tooling hygiene (scar-driven, 2026-09-30 diagnosis)

- **Never delete an artifact a gate flagged.** A failing artifact *is* the evidence; deleting it to make a gate green is falsifying the measurement, not fixing the cause. On failure: keep the file, read it, fix the cause or mark it `failed` in the status/trace ledger. Scar: a background-reflection smoke test produced candidates that failed `check_reflection.py` (missing `phase`/`fingerprint`/`state`/`Action`); the artifacts were deleted and PASS was reported. The real defects were then hidden until re-run.
- **Two strikes, then a different tool**: after 2 failed attempts at the same operation (edit anchors, command mangling), stop and re-plan; rewrite the whole file instead of a third `edit` (Goose principle).
- **Windows: no inline `python -c` / `powershell -Command` with nested quotes or paths** — MSYS/Git Bash mangles `/` arguments, `$_`, and backslashes. Write a temp file and execute it; keep one-liners flat.
- **Configured ≠ verified**: a set provider/flag ("✓ llm", `success: true`) proves *configuration*, not *function*. Before trusting a capability, probe the artifact it should have produced (e.g. `GET /v1/models` for the model, downstream file for the pipeline).
- **A gate-flagged artifact is evidence**: `FAIL:` from a gate is the measurement, not an obstacle to clear. Fix the cause, or mark the run `failed` and leave the artifacts on disk. Never delete an artifact because its contents are unflattering, and never re-run a gate against a *different* input and report that as the result. `scripts/snapshot_graded.py` copies graded artifacts to `reflection/.snapshots/` before every `check_reflection.py` read, so a deleted artifact is recoverable; the snapshot is the reason "just delete it" is no longer a shortcut. 2026-09-30: eight `FAIL` lines were deleted and reported as PASS, hiding three real defects.
- **PASS ≠ VERIFIED**: `PASS` means gates were green. `VERIFIED` means the gates ran on the artifact *this change produced*, after it ran. Grading a whole directory cannot tell those apart, so gate your own output: `python scripts/check_reflection.py --paths <topic-slug>`.
- **Filter big tool outputs through `codemode`**: pull only the fields you need (e.g. from `memory_health`: `circuitBreaker`, `health.status`, notes) instead of re-reading multi-K-token dumps.
- **One-shot helper scripts live in `scripts/_scratch/` (gitignored)** — never in the repo root.





## Standalone

Run `python preflight.py` first; exit 1 lists exactly what is missing.
Siblings live under `$WORKSPACE_ROOT` (default: this project's parent,
i.e. `projects/research/`). The two root-level links — the shared skill factory and
the integrity gate Q0 — are optional: without them the gates still run,
and local `skills/` shadows the root factory. See the `Where things live`
rows for `../../../skills/` and gate Q0.

## Code Conventions

Applied here; the full reviewer-loaded standards live in
[`docs/CODING_STANDARDS.md`](docs/CODING_STANDARDS.md) — load that when
reviewing or verifying a change rather than making one.

- Do not add untyped function signatures.
- Do not land a function doing two jobs; split it.
- Do not invent a pattern where one exists — grep the codebase first.

## Token Optimization Rules (Context Hygiene)

1. **Targeted Reads**: Do NOT read full large files (>200 lines) if you only need specific functions or definitions. Read specific ranges or use AST/symbol search where available.
2. **Compact Logging**: When running tests or CLI commands, filter the output. Only inspect the failing stack trace, never dump thousands of lines of raw logs.
3. **Plan First**: For tasks with >2 steps or complex architectural decisions, outline the plan concisely before modifying files.
4. **Handoff Protocol**: Before clearing long sessions, write or update `.claude/session-handoff.md` with:
   - What was done
   - Current state & blockers
   - Next concrete steps
5. **The Goose Principle (Cheap Failures & Zero Waste)**:
   - **Fail Fast & Cheap**: If an approach fails twice or hits an ambiguity, abort immediately rather than burning tokens on blind trial-and-error. Re-plan or query the graph.
   - **Zero Unnecessary Work**: Never perform speculative refactoring, write unrequested code, or read unreferenced files. Every action must map directly to a verified acceptance criterion.
