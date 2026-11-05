---
type: Concept
id: 00_real_design_patterns_for_agentic_software_factor
title: "**Real Design Patterns for Agentic Software Factories — with Dex & Vibb** (part 1/3)"
source: "Real Design Patterns for Agentic Software Factories - with Dex & Vibb.md"
tags: [agentic, agents, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
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
