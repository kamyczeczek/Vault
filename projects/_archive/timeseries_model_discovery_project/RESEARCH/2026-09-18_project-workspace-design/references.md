---
type: Concept
title: references
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# References — Project Workspace Design: Modular, Deterministic, Antifragile

<!-- Flat list of every external source consulted: URL + access date + 1-line summary. Local sources: file path + access date. -->

## External sources

1. <https://arxiv.org/abs/2603.16021> — Van Clief & McDermott, "Interpretable Context Methodology: Folder Structure as Agent" (2026-03). The ICM paper; folder-as-stage, plain-text contracts, deterministic routing, multi-pass compilation.
2. <https://arxiv.org/abs/2607.17598> — "Is Progressive Disclosure All You Need for Long-Document Agentic Reasoning?" (2026-07). First controlled study of progressive disclosure; second routing level collapses accuracy 0.91 → 0.64 for one model/harness pairing.
3. <https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models> — Anthropic blog (2026-07-24). Removed 80% of Claude Code's system prompt for Opus 5/Fable 5 with no measurable loss; constraints were compensating for a model limitation.
4. <https://arxiv.org/abs/2603.27249> — "AI Slop: A Tragedy of the Commons" (2026-03). 1,154 posts, 15 codes, three clusters; slop as systemic quality degradation with asymmetric effort.
5. <https://arxiv.org/abs/2607.27805> — Jaca, Benedek, Török, "Jacobian analysis of Transformer sub-blocks" (2026-07-30). LLMs exhibit chaos signatures; self-attention and FFN expand perturbations, normalization/residual counteract.
6. <https://drose.io/blog/nearby-prompts-distant-trajectories> — David W. Rose (2026-07-24). One trailing space flips generation shape; LLMs deterministic-but-chaotic under greedy decoding; bf16 non-associativity adds second nondeterminism source.
7. <https://arxiv.org/abs/2605.23296> — Cim, Topcu, Das, Kandemir, "Summarization is lossy in unpredictable ways" (2026-05-22). Compaction makes retained knowledge unpredictable across runs; "unpredictable across runs" is the load-bearing phrase.
8. <https://arxiv.org/html/2606.30005> — "LLM Agents Are Latent Context Managers" (2026-06). Invisible babysitter is a documented failure class; repair is lossless externalization the agent can see (VISTA).
9. <https://arxiv.org/abs/2606.26924> — Padmaraj Madatha, "A Deterministic Control Plane for LLM Coding Agents" (2026-06-25). Prevalence study of 10,008 repos; 10.1% exact-duplicate propagation of agent configs; deterministic governance overlay proposal.
10. <https://www.agentpatterns.ai/instructions/convention-over-configuration/> — Convention-over-configuration for agents; deterministic naming removes decision errors; boundary: narrow enough to avoid exceptions at every turn.
11. <https://jessewarden.com/2026/06/type-driven-development-total-function.html> — Total-function constraint as idiotproofing; make wrong states impossible, not detectable later.
12. <https://www.ability.ai/blog/modular-ai-agent-architecture> — Modular AI agent architecture; specialization beats monolithic power; persistent context as long-term memory.
13. <https://developers.cloudflare.com/reference-architecture/diagrams/ai/enterprise-ai-agent-workspace/index.md> — Cloudflare enterprise AI agent workspace reference architecture; stateful workspace as durable authority.
14. <https://arxiv.org/abs/2607.26637> — "Agent Memory as a Rooted Path Hierarchy of Files" (2026-07). Agents reorganize unpredictably; file counts misdescribe organization; invariants not shape.

## Local sources

1. `C:/Users/Mateusz/desktop/root/PRINCIPLES.md` — Seven central principles of this workspace; mechanism over recall, make wrong states impossible, fix in the same session, one disclosure level, invariants not shape, workspace is the trainable state, fail loud.
2. `C:/Users/Mateusz/desktop/root/AGENTS.md` — Root router; Layer-1 folder routing table; single-agent invariant; INBOX deterministic cleanup.
3. `C:/Users/Mateusz/desktop/root/MONITORING/reflection/CONTEXT.md` — Reflection stage contract; worker-file-only handoff; schema-complete reflection or no close.
4. `C:/Users/Mateusz/desktop/root/PROCESS/WORKFLOW.md` — Deterministic task intake; S1–S7 scenario routing; stage-skip rules; knowledge-routing table.
5. `C:/Users/Mateusz/desktop/root/PROCESS/05_verify/CONTEXT.md` — Verification stage contract; empirical not narrative; fail closed; log files as evidence.
6. `RESEARCH/2026-09-05_antifragile-workspace-design/findings.md` — Five antifragile mechanisms; anti-slop stack; contradictions resolved; gaps R1–R4.
7. `RESEARCH/2026-09-06_scar-efficacy-typed-interfaces/findings.md` — Ledger 391→534 entries; 27% recurrence after scars; 54 failures killed by one interface change.
8. `RESEARCH/2026-09-16_idiotproof-workspace-depth-breadth/findings.md` — ICM paper measurement; navigation as dominant failure mode; progressive disclosure study; worse-is-better; making wrong states impossible; Anthropic deletion of constraints; convention-over-configuration; filesystem self-organization; framework trap.
9. `RESEARCH/2026-09-16_software-factory-slop-persistence/findings.md` — Slop as tragedy of the commons; chaos in LLM generation; compaction lossiness; invisible babysitter anti-pattern; VISTA repair; verification-agent ceiling.
10. `RESEARCH/2026-09-07_agent-activity-file-logging-workspace-setup/findings.md` — Contract half + state half; always-loaded contract files; agent-written state; bounded scratchpad; three-document handoff.
11. `RESEARCH/2026-09-06_self-improving-workspace-framework/findings.md` — Self-improving workspace architecture; candidate heuristics; procedural families; validation gates; SkillOpt/SkillGLoW/CODESKILL compilation.
12. `projects/workspace-research/pipeline/WORKFLOW.md` — Five-phase pipeline; basis classification; promotion loop; eviction grounded; reachability; provenance stamp.
13. `projects/workspace-research/stages/04_reflect/CONTEXT.md` — Isolated reflection contract; fingerprint gating; single disclosure level; citation requirement.
