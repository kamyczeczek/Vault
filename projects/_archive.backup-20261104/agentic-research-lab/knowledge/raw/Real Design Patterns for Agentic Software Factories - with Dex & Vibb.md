---
type: Concept
title: Real Design Patterns for Agentic Software Factories - with Dex & Vibb
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# **Real Design Patterns for Agentic Software Factories — with Dex & Vibb**

## Core Insight: Architecture Over Model

The conversation reveals a fundamental shift in thinking about AI output quality. The key takeaway is that **getting better output isn't primarily about choosing the "right" model—it's about building the right system around whatever model you're using.**

## The Buy vs. Build Spectrum

The discussion frames this as a spectrum rather than a binary choice:

**Build Everything (Boundary's Approach):**
- Own MacBooks/Mac minis as compute
- Use Claude Code/Codex CLI directly
- Custom orchestration layer with webhooks
- Full control over the dev environment

**Buy Everything (Full-Stack Cloud Agents):**
- Cognition, Devon, or similar
- Managed compute, environment, and orchestration
- Fastest to start, least control

**The "Real Answer" (Middle Ground):**
> "You should have as an engineer choice and the ability to work in open systems and plug these things together."

This echoes **composition over inheritance** from software design—mixing and matching layers based on needs.

## The Four-Layer Software Factory Stack

### 1. Compute (Infrastructure)
- Can range from physical MacBooks to cloud sandboxes
- Key distinction: **pets vs. cattle**
  - *Pets*: Named machines you maintain (Vibb's MacBooks)
  - *Cattle*: Ephemeral, provisioned on-demand (Lambda functions, Daytona sandboxes)
- **Insight**: Start with pets, graduate to cattle as scale demands

### 2. Dev Environment
- Language runtimes, testing infrastructure, service dependencies
- **Critical insight from Google/Facebook experience**: They already solved this with "cloudtops"—remote development environments with shareable URLs
- **Identity provisioning** belongs here (auth to internal services, API keys)
- The friction point: When vendor-managed sandboxes can't access your internal services

### 3. Harness (Agent Runtime)
- Split into **inner harness** (Claude Code, Codex CLI) and **outer harness** (custom while-loops, merge queue babysitters, skills)
- Examples of outer harness patterns:
  - Loop until CodeRabbit passes (max 3 iterations, then escalate to human)
  - Post-human-approval merge queue watcher
- **Key insight**: The harness will keep changing; don't over-invest in one vendor

### 4. Orchestration/Control Plane
The most underserved layer:
- Dispatch work (Slack, Linear, webhooks)
- Session traces and review
- Scheduling and automation
- Permissions, audit, budgeting
- **Compounding engineering**: Building memory systems from repeated human corrections

## The "Slop PR" Workflow Pattern

Dexter's iterative approach reveals a powerful pattern:

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

1. **Don't chase models**—build good systems around whatever model works for your task
2. **Define your interfaces**—even if they're internal conventions, know where the boundaries are
3. **Trust nothing from users**—verify through your own pipeline
4. **Design for human intervention**—make it a feature, not a failure
5. **The slop PR is a feature**—use it to validate direction before decomposition
6. **Own your dev environment**—the friction of vendor lock-in here compounds fast
7. **Build for swapability**—the harness layer will evolve quickly; don't over-invest

## The Meta-Insight

The conversation itself demonstrates the answer to "how to get better output from AI":

- **Iterative back-and-forth**—not one-shot prompting
- **Small increments** with human polish between steps
- **Explicit pattern instruction**—"Read what I changed, do the next section, don't screw it up"
- **Anti-pattern documentation**—collecting examples of what the model does wrong
- **Model-appropriate workflows**—using Opus for UI, Codex for execution

The structure of the conversation itself—two experts sharing their specific, hard-won workflows—*is* the content. There's no abstraction that replaces concrete examples of what actually works in production.
