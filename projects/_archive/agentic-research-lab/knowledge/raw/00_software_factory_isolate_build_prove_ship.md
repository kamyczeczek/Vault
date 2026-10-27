---
id: 00_software_factory_isolate_build_prove_ship
 title: "Software Factory: Isolate, Build, Prove, Ship"
source: "Ras Mic / Modern Creator, Building a Software Factory that actually works; related harness and agentic engineering sources"
tags: [software-factory, agentic-engineering, harness-engineering, worktree-isolation, evidence-driven-testing, code-review, verification, workflow-design]
trust_tier: 1
---

# Research question

What makes an AI software factory operationally trustworthy, and how does the isolate-build-prove-ship workflow relate to the memory and verification architecture in this workspace?

# Primary source synthesis

The course presents a software factory as a portable workflow rather than a product, model, or proprietary harness. Its core claim is that workflow, skills, and domain knowledge can be encoded in agent instruction files and reusable skills so different coding agents follow the same delivery process.

The workflow has four stations:

1. **Isolate.** Start every feature, fix, or task in a fresh Git worktree and branch. Parallel agents must not share mutable worktrees, branches, dev servers, ports, or databases. Work is merged only after independent completion.
2. **Build.** Use an opinionated code-structure rule. The presented preference is a service-layer architecture in which orchestration owns business decisions and services own reusable mechanics. This is not universally optimal, but it creates a stable shape for agents and human reviewers.
3. **Prove.** Capture the before state while a bug or behavior is reproducible, then capture after evidence. Evidence may be screenshots, recordings, test output, metrics, logs, or before/after output pairs. The agent must inspect the evidence and continue building if the acceptance condition is not met.
4. **Ship.** Open a pull request containing the evidence, run an independent code-review agent, address findings, and loop back through build and prove until the review threshold is reached. Human merge remains the final release decision in the described workflow.

The factory analogy is useful only when each station has an observable contract. A sequence of Markdown instructions alone is not a factory unless the repository can detect incomplete or false completion.

# Local graph reflection

The local context gateway retrieved accepted lessons that strongly reinforce the workflow:

- `agent-sandboxing`: exploratory agent actions must occur in isolated worktrees or disposable namespaces before canonical state changes.
- `automated-peer-review-loops`: artifacts must pass automated peer review or test-runner feedback before promotion.
- `defensive-failure-mode-hardening`: negative controls, provenance validation, and citation grounding prevent metric gaming and ungrounded promotion.
- `design-first-planning`: explicit specifications improve autonomous implementation success.
- `minimalist-script-harness`: transparent scripts and direct command loops are preferred for core verification.
- `one-stage-one-job-modules`: each module should own one responsibility with explicit interfaces.
- `icm-methodology-hardening`: closed-loop promotion checks and fingerprint synchronization prevent write-only memory and stale routing.

This is unusually coherent with the course. The workspace already has the beginning of the same factory:

- isolated worktree guidance in `CONTEXT.md`;
- frontier state and session event stores;
- bounded proof runner in `scripts/prove_memory_system.py`;
- graph and projection rebuild checks;
- explicit retention authorization;
- a context gateway that combines evidence under a budget.

The gap is not conceptual coverage. The gap is that many contracts are still instructions or tests rather than universally enforced station gates.

# External comparison

Related external material adds three important refinements:

## Harness engineering

OpenAI's harness-engineering report describes the agent's environment as the primary engineering surface: repository structure, AGENTS instructions, test tooling, worktree bootability, browser automation, ephemeral observability, structured documentation, and automated cleanup. The core lesson is that agents become reliable when the environment makes the correct action easy and the incorrect action observable.

## HAR and WorktreeProof

HAR describes isolated slots with worktrees, ports, databases, deterministic verification, logs, artifacts, and validated tree hashes. WorktreeProof emphasizes scoped task contracts, reservations, bounded commands, closure receipts, and fail-closed validation. These projects suggest that a factory needs machine-readable run receipts, not only screenshots or narrative PR descriptions.

## Spec Kit Agents and Harness-of-Harness

Spec Kit Agents reports that context-grounding and validation hooks improve judged quality while preserving repository test compatibility. Its key contribution is phase-level grounding before generation and validation after intermediate artifacts. Harness-of-Harness adds iterative planning, implementation, and independent evaluation, with progressive disclosure and versioned histories. Both support a factory model that carries verified evidence forward rather than resetting context every iteration.

# Critical analysis

## What the workflow gets right

- Isolation prevents agents from overwriting one another and keeps main clean.
- Opinionated structure reduces architectural drift and lowers the cost of re-entry by another agent.
- Before/after evidence catches the difference between code written and behavior changed.
- Independent review prevents the builder from being the sole judge of completion.
- The loop makes failure a normal transition back to build rather than a false success.
- Model and harness agnosticism is valuable because the workflow contract remains portable.

## What it does not prove

- Screenshots can show a visible result but cannot establish security, data integrity, concurrency behavior, or hidden regressions.
- A code-review agent's score is not a formal correctness proof. It is a review signal and can be wrong or gamed.
- Tests written by the same builder may share its blind spots.
- A service-layer architecture is a local convention, not a universal law.
- Worktree isolation prevents file collisions, not semantic conflicts after merge.
- A green pipeline proves only the checks that were actually run against the exact tree being shipped.

## The necessary factory contract

For each station, the system should record:

| Station | Required input | Required output | Machine gate |
|---|---|---|---|
| Isolate | task ID, base revision, file scope | unique worktree/branch and environment | no shared mutable state; base revision recorded |
| Build | approved requirement and plan | bounded code change plus tests | scope and architecture checks |
| Prove | baseline behavior and acceptance criteria | before/after evidence or measured checks | evidence tied to exact revision |
| Ship | verified branch and proof receipt | PR or handoff | independent review, no unresolved critical findings |

Missing evidence must block promotion. A failure should route back to the responsible station, not be silently converted into a pass.

# Implications for this workspace

1. Rename the conceptual pipeline around `isolate -> build -> prove -> ship`, while keeping implementation-specific names as aliases where needed.
2. Turn the existing proof runner into a signed or hash-linked receipt containing base revision, final revision, commands, results, artifacts, and timestamps.
3. Make worktree scope and changed-file scope explicit before implementation. The existing broad working tree demonstrates why this matters.
4. Separate builder evidence from independent evaluator evidence. A test written by the builder is not equivalent to an external check.
5. Add a merge gate that refuses acceptance when required proof categories are absent, stale, or attached to a different tree fingerprint.
6. Keep visual evidence as one proof type among several, not as a universal substitute for tests and invariants.
7. Preserve the current source-of-truth separation. A factory should produce validated projections and receipts, not collapse all state into one memory graph.
8. Measure whether the factory improves task continuation, review time, regression rate, context cost, and merge throughput compared with direct agent work.

# Claims and limits

- **Supported by the primary source and related work:** isolation, explicit structure, before/after evidence, independent review, and feedback loops are practical components of an AI coding workflow.
- **Supported by local graph lessons:** sandboxing, peer review, design-first planning, and fail-closed promotion are already accepted project principles.
- **Not established:** that any particular review agent score, service-layer architecture, or five-skill bundle guarantees quality.
- **Not established:** that a software factory automatically creates production-ready software without human product judgment and independent evaluation.
- **Not established:** that this workspace's current implementation improves delivery outcomes. That requires a baseline comparison.

# Follow-up proof plan

1. Add a receipt schema with exact source and result tree hashes.
2. Run a representative task through direct-agent and factory workflows.
3. Compare task success, regression count, review findings, time, context cost, and human intervention.
4. Seed negative controls: shared-worktree collision, stale proof receipt, missing before state, invalid frontier, and unresolved review comment.
5. Require the factory to fail closed on every seeded failure.
6. Store the resulting receipts and benchmark summary in the research corpus.

# Sources

- Ras Mic / Modern Creator, "I built my own software factory (it's not what you think)," https://moderncreator.app/2026-09-01-ras-mic-i-built-my-own-software-factory-it-s-not-what-you-think
- OpenAI, "Harness engineering: leveraging Codex in an agent-first codebase," https://openai.com/index/harness-engineering/
- HAR, https://harproject.dev/ and https://github.com/os-factory/har
- WorktreeProof, https://github.com/Nedal7707/worktree-proof
- Spec Kit Agents, https://arxiv.org/pdf/2604.05278
- Harness-of-Harness, https://arxiv.org/html/2609.01481
