---
type: Concept
id: 01_plain_text_as_interface
title: "Stage 02: Script (part 2/4)"
source: "Plain Text as Interface.md"
tags: [agentic, agents, context-engineering, icm, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

**3.2 The Working Artifact (`output/research.md`)**

```markdown
# Research: AI Agent Orchestration

## Key Findings
1. Frameworks add overhead for sequential workflows...
2. Filesystem-based coordination reduces complexity...

## Supporting Data
| Framework | Overhead | Transparency |
|-----------|----------|--------------|
| CrewAI    | High     | Low          |
| ICM       | None     | High         |
```

This is:
- The output of Stage 1.
- The input to Stage 2.
- A file a human can read, edit, and save before Stage 2 runs.

**3.3 The Machine-Readable File (`output/spec.json`)**

```json
{
  "scenes": [
    {
      "id": "scene-01",
      "narration": "The problem with frameworks...",
      "duration_seconds": 12,
      "visual_style": "minimalist"
    }
  ]
}
```

Used when a downstream stage needs structured data, but still human-readable.

---

#### 4. The "No Database" Principle

ICM deliberately avoids databases for state management. The filesystem *is* the state management system.

| Traditional Approach                   | ICM Approach                                |
| :------------------------------------- | :------------------------------------------ |
| Store intermediate state in a database | Write intermediate state to `output/` files |
| Query state via SQL or ORM             | Open the file and read it                   |
| Debug by querying the database         | Debug by reading the file                   |
| Version control requires DB snapshots  | Version control is native Git               |

**Why this matters:**

- No database means no database configuration, no connection strings, no migrations.
- The workspace is fully portable—copy the folder and you've copied the entire system state.
- A new team member can understand the pipeline by reading files top to bottom.

---

#### 5. Connection to Literate Programming

The paper draws a direct line to Donald Knuth's literate programming:

> "The markdown files that instruct the agent are simultaneously the documentation that tells a human what the stage does, what it expects, and what it produces. The instruction set and the documentation are the same artifact."

In Knuth's vision, code and documentation are woven together in a single source. In ICM, the prompt and the documentation are the same file. There is no separate "README" that explains what the prompt does—the `CONTEXT.md` file *is* the explanation.

---

#### 6. Relationship to the Other Principles

"Plain Text as Interface" is the enabler for the other ICM principles:
