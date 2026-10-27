---
type: Concept
id: 01_real_design_patterns_for_agentic_software_factor
title: "**Real Design Patterns for Agentic Software Factories — with Dex & Vibb** (part 2/3)"
source: "Real Design Patterns for Agentic Software Factories - with Dex & Vibb.md"
tags: [agentic, agents, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

1. **Research + Spec**: Back-and-forth with models to create PRD with HTML mockups
2. **Overnight Implementation**: Queue up 15 prompts for agents to argue and build
3. **Slop PR Creation**: One massive PR that validates the concept
4. **Decomposition**: Use models to break the slop PR into digestible chunks
5. **Incremental Merging**: Ship 1-3K line PRs, have humans pick up the rest

**Key insight**:
> "It's how do I get leverage from AI? How do I get it to unblock my writer's block without me actually having to fix every single issue that it introduces?"

## The Trust Hierarchy for Feedback

Boundary's bug-fixing pipeline reveals a crucial principle:

```
Untrusted (user feedback)
→ Verify against latest version
→ Deduplicate (even 50% accuracy saves time)
→ Create own repro (burn tokens to build trust)
→ Only then create issue
```

**Core principle**: Never execute or trust raw user input directly. Transform it through your own verification.

## Human-in-the-Loop Design

The goal isn't full automation—it's pushing human time to minimum viable intervention:

- **Shepherd pattern**: One human assigned to triage
- **Notification design**: Slack ping only when agent needs human (PR review, plan approval)
- **Issue difficulty classification**: Agents pre-classify, humans can correct later

> "95% automatic is much easier than 100% automatic."

## The Interface Problem

**Key tension**: No standard exists for harness-to-orchestration communication.

- MCP: Too narrow
- AGUI: Great for UI broadcast, but no hooks
- Each harness (Claude, Codex, Pi) has fundamentally different hook systems

**The React analogy**: Web development needed the concept of "state" before real abstraction emerged. We haven't found the equivalent primitive for agent orchestration yet.

## Monorepo Simulation for Multi-Repo Companies

For organizations with many repos:

1. **Create a coordination repo** with a CLAUDE.md describing the organization
2. Place all repos one level up in the filesystem
3. Tell the agent: "Research what matters, here's where everything lives"
4. **Avoid submodules** (commit pinning nightmare)
5. Consider **subtrees** or **symlinks** for specific workflows

## The Browser Wars Analogy

Companies betting on owning the harness (like owning browsers in the '90s) are making a calculated bet. The question is whether harness ownership becomes as valuable as browser ownership was.

## Extendable Software (The Future)

The most forward-looking concept:

> "The best way to extend software is to let agents write code."

This manifests as:
- **Code mode**: Users drop in TypeScript files that modify system behavior
- **Live reloading**: Agent-written extensions immediately available
- **Sandboxed execution**: User code runs in isolated environments

This is VSCode extensions taken to the logical extreme—where the "extensions" are agent-generated and can modify application behavior in real-time.

## Practical Takeaways
