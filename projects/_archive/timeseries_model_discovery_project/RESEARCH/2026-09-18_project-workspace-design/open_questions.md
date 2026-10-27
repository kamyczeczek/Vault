---
type: Concept
title: open_questions
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Open Questions — Project Workspace Design: Modular, Deterministic, Antifragile

<!-- Questions that remain unanswered, each with the reason it could not be resolved. -->

1. **Which constraints are now net-negative?** The Anthropic finding (80% prompt deletion, no loss) is a strong signal that some of this workspace's layered-context design is compensating for a model limitation that no longer exists. The ablation test exists (strip to invariants, compare gate pass rates) but has not been run. Reason not resolved: requires controlled experiment across full S1–S7 workflow; out of scope for a single research record.

2. **What is the right scar-lifetime budget mechanism?** R1 from the 2026-09-05 antifragile record is named but not implemented. SkillOpt's learned optimizer is too heavy; a digest-size budget with merge-or-drop at reflection time is the likely shape, but the exact trigger threshold, merge policy, and human-signoff step are unspecified. Reason not resolved: design decision requiring S5 implementation; this record can only name the gap.

3. **Does the "one disclosure level" finding generalize to this workspace's specific routing pattern?** The study measured accuracy collapse under a hierarchical pack where every chunk becomes its own skill under a meta-router. This workspace's routing is different (flat table → stage folder → stage CONTEXT.md), but no controlled comparison exists for this exact pattern. Reason not resolved: no published study matches this routing shape; requires internal A/B or red-path validation.

4. **How does the deterministic control plane pattern map to this workspace's existing gates?** Rel(AI)Build proposes supply-chain hashing, HMAC lockfiles, phase-state machines, and compile-to-many dialects. The workspace already has some of these (fingerprint gating, phase-state routing via WORKFLOW.md, run_gates.py as single entry point). The unmapped gap is the supply-chain/hashchain layer for agent configs and the compile-to-many portability question. Reason not resolved: cross-cutting S5 design work; this record can only flag the correspondence.

5. **What is the minimal viable "always-loaded contract" size under current frontier models?** The ICM paper targets 2,000–8,000 tokens per stage; Anthropic's result implies the ceiling has moved down. No measurement exists for this workspace's actual `AGENTS.md` + overlay token count under current session loading. Reason not resolved: requires empirical measurement; tooling for token-counting session startup is not in place.
6. **What is the exact merge protocol for independent small projects?** The modularity principle says many small projects, merge later, but no source specifies the merge trigger, contract-check list, or conflict-resolution policy. Reason not resolved: design decision requiring S5 implementation; this record can only name the gap.

7. **How should the graph database be structured for corpus-based markdown?** The workspace-research project demonstrates a working SQLite graph with chunk-level frontmatter and tag edges, but no external source specifies the optimal schema for agent querying across many independent projects. Reason not resolved: requires empirical evaluation of schema variants against real agent workloads.
