---
type: Concept
id: 02_real_design_patterns_for_agentic_software_factor
title: "**Real Design Patterns for Agentic Software Factories — with Dex & Vibb** (part 3/3)"
source: "Real Design Patterns for Agentic Software Factories - with Dex & Vibb.md"
tags: [agentic, agents, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

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
