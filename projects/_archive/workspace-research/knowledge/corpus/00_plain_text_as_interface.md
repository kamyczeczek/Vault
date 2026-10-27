---
type: Concept
id: 00_plain_text_as_interface
title: "Stage 02: Script (part 1/4)"
source: "Plain Text as Interface.md"
tags: [agentic, agents, context-engineering, icm, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
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
