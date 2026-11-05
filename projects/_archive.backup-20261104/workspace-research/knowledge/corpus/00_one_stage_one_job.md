---
type: Concept
id: 00_one_stage_one_job
title: "One Stage, One Job.md (part 1/3)"
source: "One Stage, One Job.md"
tags: [agentic, agents, context-engineering, icm]

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
