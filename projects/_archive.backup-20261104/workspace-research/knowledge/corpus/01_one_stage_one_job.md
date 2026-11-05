---
type: Concept
id: 01_one_stage_one_job
title: "One Stage, One Job.md (part 2/3)"
source: "One Stage, One Job.md"
tags: [agentic, agents, context-engineering, icm]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

> "A multi-pass compiler transforms source code through a sequence of discrete passes. The lexer produces tokens. The parser produces a syntax tree. Semantic analysis annotates the tree. Optimization passes rewrite it. Code generation produces the final output. Each pass reads the output of the previous pass, transforms it according to its own rules, and writes an intermediate representation."

ICM stages work the same way:

| Compiler Pass     | ICM Stage           |
| :---------------- | :------------------ |
| Lexer             | Fetch raw data      |
| Parser            | Structure the data  |
| Semantic Analyzer | Filter and validate |
| Code Generator    | Format final output |

Each pass is simple, verifiable, and produces an intermediate artifact that can be inspected.

---

#### 5. How Big Should a Stage Be?

The paper doesn't prescribe a specific size, but the heuristic is:

- **Too Big:** The stage's `CONTEXT.md` requires multiple distinct instructions (e.g., "research the topic AND write the script").
- **Too Small:** The stage produces no meaningful intermediate artifact worth human review.
- **Just Right:** The stage has one clear verb (fetch, filter, draft, format, verify) and one clear output that a human can meaningfully review.

A practical test: *"Can I describe this stage's job in a single sentence without using the word 'and'?"*

---

#### 6. Relationship to the U-Shaped Intervention Pattern

The paper observes that human edits follow a U-shape: heavy at Stage 1, light in the middle, heavy at the final stage.

Single-purpose stages contribute to the **light middle** because:
- The stage's job is narrow enough to be done reliably.
- The input from the previous stage is a well-defined anchor.
- The reference material (Layer 3) constrains the execution.

When a stage tries to do too much, it breaks this pattern. The agent's output becomes less predictable, and the human feels compelled to review and edit more heavily.

---

#### 7. Connection to Other Principles

"One Stage, One Job" enables the other ICM principles:

- **Plain Text as Interface:** A single-purpose stage produces a single, well-defined text file.
- **Layered Context Loading:** A narrow job means fewer files in the Inputs table.
- **Every Output is an Edit Surface:** A clean, single-purpose output is easier for a human to review and edit.
- **Configure the Factory, Not the Product:** With clear stage boundaries, reference material stays in Layer 3, not mixed into the working artifacts.

---

#### 8. When to Bend the Rule

The paper acknowledges that stages can be slightly broader in practice. For example, the `03_production` stage in the script-to-animation pipeline "produces animation specifications and working Remotion code." This is two outputs, but they are part of the same logical job: *turn the script into production-ready materials*.
