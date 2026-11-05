---
type: Concept
title: Plain Text as Interface
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Here is a comprehensive expansion of the "Plain Text as Interface" principle from the ICM paper.

---

### Plain Text as Interface: Markdown/JSON as the Universal Communication Layer

This is the second foundational principle of ICM, directly borrowed from Kernighan and Pike's argument that text is the universal interface in Unix systems. Applied to AI agent workflows, it means every instruction, every input, every intermediate artifact, and every output is stored as a plain text file—specifically Markdown or JSON.

---

#### 1. The Core Idea

> "Stages communicate through markdown and JSON files. No binary formats, no database connections, no proprietary serialization."

There are three distinct communication flows in an ICM pipeline, and all of them happen through plain text:

| Communication Flow | Plain Text Medium                                  |
| :----------------- | :------------------------------------------------- |
| **Human → Agent**  | Instructions in `CONTEXT.md` files                 |
| **Stage → Stage**  | Output files (`.md`, `.json`) in `output/` folders |
| **Agent → Human**  | Intermediate artifacts the human can read and edit |

No stage talks to another through an API. No stage writes to a database. No stage produces a binary blob. Everything is a file you can open in any text editor.

---

#### 2. Why Plain Text?

**2.1 Universal Accessibility**

- Any tool that can read a text file can participate in the workflow.
- Any human who can open a text editor can inspect or modify any artifact.
- No proprietary software, no special viewer, no IDE required.

**2.2 Git Compatibility**

- Plain text files are natively diffable, mergeable, and versionable.
- Every change to a prompt, every edit to an output, is trackable in Git.
- Stage outputs can be committed after each run, creating a complete version history.

**2.3 Debuggability**

- When something goes wrong, you open the file and read it.
- There is no "deserialize the state object" step before you can understand what happened.
- The intermediate representation *is* the system's state.

**2.4 Model-Native**

- LLMs are trained on text. They process text most effectively.
- Markdown provides lightweight structure (headings, lists, tables) that models parse well.
- JSON provides machine-readable structure when needed, but remains human-readable.

---

#### 3. What This Looks Like in Practice

**3.1 The Instruction File (`CONTEXT.md`)**

```markdown
# Stage 02: Script

## Inputs
- Layer 4 (working): ../01_research/output/research.md
- Layer 3 (reference): ../../_config/voice.md
- Layer 3 (reference): references/structure.md

## Process
Write a script based on the research output.
Follow the structure in structure.md.
Match the tone described in voice.md.

## Outputs
- script_draft.md -> output/
```

This is simultaneously:
- The prompt the agent reads.
- The documentation a human reads.
- The contract that defines the stage's contract.

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

| ICM Principle                              | How Plain Text Enables It                                    |
| :----------------------------------------- | :----------------------------------------------------------- |
| **One Stage, One Job**                     | A stage's single job is defined in a single, focused text file. |
| **Layered Context Loading**                | Each layer (0-4) is composed of specific plain text files that can be scoped. |
| **Every Output is an Edit Surface**        | You can only edit output if it's a file you can open. Plain text makes this universal. |
| **Configure the Factory, Not the Product** | Factory config (voice guides, templates) is stored in plain text files in Layer 3. |

---

#### 7. Markdown vs. JSON: When to Use Which

| Format       | Best For                                                     | Example                             |
| :----------- | :----------------------------------------------------------- | :---------------------------------- |
| **Markdown** | Human-readable documents, instructions, narrative content, research summaries | `script_draft.md`, `research.md`    |
| **JSON**     | Structured data that needs to be programmatically consumed by the next stage | `scene_specs.json`, `metadata.json` |

The rule of thumb: **if a human will primarily read it, use Markdown. If a script or the next stage will primarily parse it, use JSON. But in both cases, keep it human-readable.**

---

#### 8. What This Rejects

The principle explicitly rejects:

- **Binary formats:** `.docx`, `.pdf` (as intermediate state), `.pickle`, images as intermediate artifacts.
- **Database dependencies:** No PostgreSQL, no Redis, no SQLite for state.
- **Proprietary serialization:** No custom binary protocols, no opaque object graphs.
- **Framework-specific state:** No LangChain "agent state" objects that can't be read outside the framework.

---

#### 9. The Portability Argument

The paper emphasizes that a workspace is a folder. This is only true because everything is plain text.

> "It can be copied to another machine, committed to Git, emailed as a zip file, or synced through any cloud storage service. It carries its own prompts, its own context structure, its own stage definitions. There is no server to configure, no environment to replicate, no deployment step."

If any artifact were binary or database-backed, this portability would collapse. Plain text is what makes the workspace a self-contained, transferable unit.

---

#### 10. When to Bend the Rule

The paper acknowledges some exceptions:

- **Final deliverables** may be binary (e.g., a rendered `.mp4` video or `.pptx` deck). But the *intermediate* artifacts that lead to them are always plain text.
- **Local scripts** may process data in non-text formats (e.g., fetching a PDF as source material). But the extracted, structured content is written back as Markdown for the next stage.
- **Large datasets** may be stored as CSV or JSONL, which are still text-based and diffable.

The principle is: **the communication layer between stages is always plain text. Only the very first input and very last output may be binary.**