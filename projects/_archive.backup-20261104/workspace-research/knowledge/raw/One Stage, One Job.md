---
type: Concept
title: One Stage, One Job
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Here is a comprehensive expansion of the "One Stage, One Job" principle from the ICM paper.

---

### One Stage, One Job: Single Responsibility per Folder

This is the foundational principle of ICM, borrowed directly from Doug McIlroy's Unix philosophy ("Make each program do one thing well") and David Parnas's information-hiding criterion. Applied to AI workflows, it means each folder in the pipeline handles exactly one discrete step and no more.

---

#### 1. The Core Idea

A stage that fetches data does not also filter it.
A stage that filters does not also format the final output.

Each stage:
- **Reads** a defined input
- **Transforms** it according to a single, clear instruction
- **Writes** a defined output to its own folder

---

#### 2. Why This Matters

| Problem with Multi-Purpose Stages                            | Benefit of Single-Purpose Stages                             |
| :----------------------------------------------------------- | :----------------------------------------------------------- |
| **Context Pollution:** Agent loads irrelevant instructions and reference material. | **Focused Context:** Agent receives only what it needs for this specific job. |
| **Debugging Difficulty:** When output is wrong, it's unclear *which part* of a complex instruction caused it. | **Clear Accountability:** Errors can be traced to a specific stage and its contract. |
| **Poor Editability:** Changing one aspect requires understanding the whole monolithic process. | **Independent Modification:** A stage can be swapped, edited, or re-run without affecting others. |
| **Reduced Output Quality:** LLMs perform worse on complex, multi-part instructions. | **Improved Output Quality:** Simpler tasks produce more reliable results. |

---

#### 3. What This Looks Like in Practice

Instead of:

```
workspace/
└── pipeline/
    ├── instructions.md  (fetch data, filter it, format it, write report)
    └── output/
        └── final_report.md
```

ICM structures it as:

```
workspace/
└── stages/
    ├── 01_fetch_data/
    │   ├── CONTEXT.md       # "Fetch raw data from API"
    │   └── output/
    │       └── raw_data.md
    │
    ├── 02_filter_data/
    │   ├── CONTEXT.md       # "Filter raw data for relevance"
    │   └── output/
    │       └── filtered_data.md
    │
    └── 03_format_report/
        ├── CONTEXT.md       # "Format filtered data into final report"
        └── output/
            └── final_report.md
```

Each `CONTEXT.md` contains a **single, focused instruction**. The agent executing `02_filter_data` never sees the instructions for fetching or formatting. It only sees "filter this data."

---

#### 4. The Compiler Analogy

The paper draws a parallel to multi-pass compilers:

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

The key is that the stage's *purpose* is singular ("produce the final deliverable"), even if its outputs are multiple. A stage that "fetches data, filters it, and writes the final report" has three purposes and should be split into three folders.