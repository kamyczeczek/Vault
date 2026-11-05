---
type: Concept
title: findings
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Findings — Project Workspace Design: Modular, Deterministic, Antifragile

<!-- Every claim cited to a URL, file path, or local document. No unsourced claims. -->

## 1. The workspace is the trainable state

With frozen model weights, the filesystem is the only thing that improves. NVIDIA's workspace-optimization work names this directly: the workspace IS the trainable state, and adaptation = editing typed artifacts, replayed against retained evidence before acceptance. DREAMTEAM's +38.4% RHAE with 31% fewer actions is the measured proof that learning-in-workspace beats brute force.

Source: `RESEARCH/2026-09-05_antifragile-workspace-design/findings.md` §1 (ledger entries A1, A5); `MONITORING/reflection/` scars S-s13/S-s15/S-s19.

Implication: every problem must leave the directory structure measurably different, and the delta must be mechanism, not prose.

## 2. The modularity principle: many small projects, merge later

A workspace should contain many independent small projects, not one large project. The ICM paper explicitly models this: numbered folders are stages, and each stage owns its own contract, inputs, and outputs. The workspace-builder described in the paper produces exactly this shape: discovery → stage mapping → scaffolding → questionnaire → validation. The workspaces it produces are consistent because the builder encodes the conventions into its process.

Source: <https://arxiv.org/abs/2603.16021> §4.4; `RESEARCH/2026-09-16_idiotproof-workspace-depth-breadth/findings.md` §1.

The modularity advantage is twofold:
- **Failure isolation:** a defect in one project cannot corrupt another.
- **Merge clarity:** independent projects can be merged only when their contracts are satisfied, not before.

This is the same reasoning behind Unix pipelines: small composable tools versus one monolithic program.

## 3. The three functions of a good workspace

A project workspace exists to do exactly three things:

1. **Navigation** — an agent or human can tell where things live without exploring.
2. **Contract** — every artifact states what must be true about it; invalid states cannot be written.
3. **Learning** — every failure, user complaint, and wrong turn produces a gate or invariant that makes that class impossible next time.

Anything else is overhead. This converges from four independent sources in the 2026-09-05 antifragile record: NVIDIA/DREAMTEAM (trainable state), Memento-Skills/SkillOpt (markdown-as-memory trained by experience), ICM/Atomic Agents (folders-as-stages, deterministic routing), and the practitioner corpus (bookend rituals, adversarial verification).

Source: `RESEARCH/2026-09-05_antifragile-workspace-design/findings.md` §1; `RESEARCH/2026-09-07_agent-activity-file-logging-workspace-setup/findings.md` §1.

## 4. Simplicity as the primary failure-reduction mechanism

The workspace already does simplicity in places: corpus chunk id == filename stem; research record folder == `YYYY-MM-DD_slug`; reflection file name encodes scenario + timestamp. These are not cosmetic — they are failure-prevention.

The agentpatterns.ai source states the mechanism precisely: "Every choice an agent makes is a chance for a wrong answer... When the answer is not obvious, an agent guesses. Inconsistent guesses compound over time into a codebase that is hard to navigate." The counter-mechanism: "When naming and placement are deterministic — derivable from the issue number, content category, or file type — an agent needs no context about what previous agents chose, because the answer is discoverable from the inputs rather than remembered."

Source: <https://www.agentpatterns.ai/instructions/convention-over-configuration/>; `RESEARCH/2026-09-16_idiotproof-workspace-depth-breadth/findings.md` §8.

The boundary is important: "A convention that requires exceptions at every turn is a signal it was specified too narrowly."

## 5. Heuristic 1: Remove the decision, don't document it

Convention-over-configuration is the only idiotproofing that survives model improvement. Deterministic naming and placement are free at inference. The workspace already does this in places: corpus chunk id == filename stem; research record folder == `YYYY-MM-DD_slug`; reflection file name encodes scenario + timestamp.

Source: <https://www.agentpatterns.ai/instructions/convention-over-configuration/>; `RESEARCH/2026-09-16_idiotproof-workspace-depth-breadth/findings.md` §8.

## 6. Heuristic 2: Make wrong states impossible, not detectable later

A gate that checks is weaker than a structure that refuses. Total-function constraints are states that cannot be expressed in the first place. The live workspace already has examples: `INBOX/` must be empty at session close; a bare 12-hex fingerprint literal is rejected by `check_stage_contracts.py`; corpus chunk id must equal filename stem.

The type-driven development source frames it as: a partial function throws or returns nonsense for some inputs; a total function returns a sensible value for every input. The workspace version: if you can write an invalid state, you will. Fix the writer, delete the checker.

Source: <https://jessewarden.com/2026/06/type-driven-development-total-function.html>; `RESEARCH/2026-09-16_idiotproof-workspace-depth-breadth/findings.md` §6; `PRINCIPLES.md` P2.

## 7. Heuristic 3: One disclosure level, never two

The first controlled study of progressive disclosure found that a second routing level never helps and sometimes breaks accuracy outrageously — one Pi/model pairing saw multiple-choice accuracy collapse from 0.91 to 0.64. The mechanism is exactly what a deep folder tree recreates: "the always-loaded child descriptions eat exactly the context budget the structure was meant to save."

The workspace's current single-level routing (`AGENTS.md` → stage folder → stage `CONTEXT.md`) is already on the right side of this. Do not add meta-routers, sub-workspace dispatchers, or "for scale" indirection. Depth is bought one level at a time, with a stated reason.

Source: <https://arxiv.org/abs/2607.17598>; `RESEARCH/2026-09-16_idiotproof-workspace-depth-breadth/findings.md` §4; `PRINCIPLES.md` P4.

## 8. Heuristic 4: Mechanism over scars; scars over memory

Scars are necessary but not sufficient. The workspace ledger shows 27% of live failures are recurrences of trap classes whose scars already existed. The mechanism that killed 54 failures in one move was an interface change, not a louder warning.

The hierarchy:
- **Mechanism** (gate, invariant, type constraint) — eliminates the class.
- **Scar** — records that the class existed and where the rule lives.
- **Memory card / prose doc** — explains the why for the human.

If a failure recurs and your response edits prose, you violated P1.

Source: `RESEARCH/2026-09-06_scar-efficacy-typed-interfaces/findings.md` §1, §3; `PRINCIPLES.md` P1.

## 9. The graph database for AI agents: corpus-based markdown

The workspace-research project demonstrates a working graph brain for AI agents: corpus chunks are `.md` files with structured frontmatter, indexed into SQLite via `build_graph.py`. The graph stores entities and relational edges; `ask.py` queries return ranked chunks with tags. This is not RAG over embeddings — it is a **corpus-based knowledge graph** where every chunk is a file, every edge is explicit, and every claim can be traced to a path.

The key design points from the live implementation:
- **Chunk identity == filename stem** — total-function constraint; invalid chunks cannot be written.
- **Tags as edges** — `SHARES_TAG` relationships allow thin intersections to expand deterministically.
- **Fingerprint gating** — `watch.py --once` + fingerprint comparison ensures the graph is fresh before any query.
- **Local-authority digests** — brains live under `brains/<name>/`; no overlay injection; freshness proven by fingerprint.

Source: `projects/workspace-research/knowledge/graph/ask.py`; `projects/workspace-research/knowledge/graph/build_graph.py`; `projects/workspace-research/knowledge/corpus/08_icm_knowledge_big.md`; `projects/workspace-research/knowledge/corpus/10_interpretable_context_methodology_folder_structu.md`.

## 10. The workspace builder: files for a new agent creating a new workspace

The ICM paper includes a workspace-builder as a five-stage workspace whose output is a new workspace. It walks through:
1. **Discovery** — what is the domain, what is the workflow.
2. **Stage mapping** — where are the natural breakpoints.
3. **Scaffolding** — creating the folder structure.
4. **Questionnaire design** — what setup questions should the workspace ask.
5. **Validation** — does the pipeline run end to end.

The builder itself follows ICM conventions. The workspaces it produces are consistent because the builder encodes the conventions into its process. This means practitioners can create new workspaces for their own domains without understanding the underlying conventions in detail.

Source: <https://arxiv.org/abs/2603.16021> §4.4.

**The concrete output files for a new agent creating a new workspace:**

| File | Purpose | Invariant |
|---|---|---|
| `IDENTITY.md` | Layer 0: "Where am I?" | ~800 tokens; domain, owner, version |
| `CONTEXT.md` | Layer 1: "Where do I go?" | ~300 tokens; deterministic routing table |
| `PROCESS/WORKFLOW.md` | Layer 2: "What do I do?" | Scenario routing S1–S7; stage playbooks |
| `_config/` | Layer 3: "What rules apply?" | 500–2k tokens; voice guide, templates |
| `output/` | Layer 4: "What am I working with?" | Stage outputs; never edited by agent |
| `AGENTS.md` | Root router | Layer-1 routing table; single-agent invariant |
| `PRINCIPLES.md` | Core doctrine | Seven central principles; override any local CONTEXT |
| `PROGRESS.md` | Session state | Append-only; reconnection point |
| `MONITORING/reflection/` | Learning ledger | Schema-complete reflection or no close |
| `RESEARCH/` | Research shelf | Deterministic R-row routing; `check_catalog.py` exit 0 |

Source: <https://arxiv.org/abs/2603.16021> §4.4; <https://github.com/ktnCodes/icm-template>; `RESEARCH/2026-09-16_idiotproof-workspace-depth-breadth/findings.md` §1.

## 11. The failure modes this shape prevents

| Failure mode | Prevention mechanism | Measured effect |
|---|---|---|
| Navigation drift | Single-level routing + `CONTEXT.md` per folder | 33–44% fewer navigation steps; 52% variance reduction across 7,012 sessions |
| Silent failures | Fail-loud gates + mandatory ledger disposition | Loud failure costs a minute; silent one costs an hour |
| Unverified claims | Red-path-validated gates only; committed narratives match store truth | Round-6/9 audit methodology |
| Repeated mistakes | Prior-knowledge check at plan entry; scar digest auto-injection; problem fingerprints blocking duplicates | Post-gate ledger: 13 edit-anchor events, all blocked, zero burned failures |
| Context bloat | Query-don't-load brains; digest-sized injection; claims-ledger research method | 2k–8k tokens per stage vs 30k–50k monolithic |
| State rot between sessions | `PROGRESS.md` as reconnection point; reflection worker output as deterministic file | Stateless agent + filesystem = continuity |
| Monolithic complexity | Many small independent projects; merge only when contracts satisfied | Failure isolation; merge clarity |

Sources: `RESEARCH/2026-09-16_idiotproof-workspace-depth-breadth/findings.md` §3; `RESEARCH/2026-09-05_antifragile-workspace-design/findings.md` §3; `RESEARCH/2026-09-06_scar-efficacy-typed-interfaces/findings.md` §1.

## 12. The one debt the evidence points at directly

The 2026-09-05 antifragile record names it as R1: **scar-lifetime budget**. The digest is append-mostly. Nothing merges or drops superseded scars except ad-hoc forget-first. That is accumulation, not antifragility.

SkillOpt's finding is the mechanism: a budget forces merge-or-drop at reflection time. The workspace already has the evidence channel (`reflection_brain` scars, problem fingerprints); what is missing is the compaction step at reflection close, not at runtime.

This is the single structural change most likely to reduce the "many strategies, still chaos" feeling.

Source: `RESEARCH/2026-09-05_antifragile-workspace-design/findings.md` §4, R1; `RESEARCH/2026-09-06_self-improving-workspace-framework/findings.md`.

## 13. The Anthropic caveat: constraints that compensate for model limitations

Anthropic removed over 80% of Claude Code's system prompt for Claude Opus 5 / Fable 5 with no measurable loss on coding evaluations. Their diagnosis: "we were overconstraining Claude Code, both through our system prompt and in our CLAUDE.md files and skills." The constraints were compensating for a model limitation that no longer exists.

The honest open question: which of this workspace's existing constraints are now net-negative? The ablation test is: run the same task with contracts stripped to invariants and compare gate pass rates.

Source: <https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models>; `RESEARCH/2026-09-16_idiotproof-workspace-depth-breadth/findings.md` §7.

## 14. The concrete project-workspace shape

Not a folder list — an invariant list. Shape will migrate as volume grows (arXiv 2607.26637: agents reorganize unpredictably; file counts misdescribe organization).

| Layer | What it holds | Invariant |
|---|---|---|
| Always-loaded contract | `AGENTS.md` + minimal overlay | ≤ ~200–300 lines; deterministic routing only |
| Active state | `PROGRESS.md`, current `CONTEXT.md` slices | Present tense only; append-only history |
| Stage contract | `PROCESS/<stage>/CONTEXT.md` | One disclosure level; entry/exit contract + gate command |
| Artifacts | Plans, implementations, experiments | Contract-tested; every acceptance has a re-runnable command and log path |
| Learning ledger | `MONITORING/reflection/`, `MONITORING/KNOWLEDGE/problems/` | Every failure → scar → gate/doc edit in the same session |
| Research shelf | `RESEARCH/<YYYY-MM-DD>_<slug>/` | Deterministic R-row routing; `check_catalog.py` exit 0 before commit |
| Brains | `brains/<name>/` | Local-authority digests; no overlay injection; freshness proven by fingerprint |
| Evidence | `PROCESS/05_verify/logs/` | Every "done" claim has a log file; narrative without log path is invalid |
| Modular projects | `projects/<name>/` | Independent small projects; merge only when contracts satisfied |

## 15. The stopping rule

A workspace is good enough when:
- Every failure produces a structural change in the same session (P3).
- Every "done" claim cites a re-runnable command with a log path (05_verify contract).
- The reflection file is schema-complete or the session does not close (REFLECTION_RULES.md).
- `python PROCESS/run_gates.py --all` exits 0.
- The scar digest has a **budget**, not just a ceiling — and the budget is enforced at reflection close, not at runtime.

If those five hold, the workspace is antifragile by construction. If any one fails, the workspace is accumulating experience without converting it into structure.

Source: `PRINCIPLES.md` P1–P7; `PROCESS/05_verify/CONTEXT.md`; `MONITORING/reflection/CONTEXT.md`.
