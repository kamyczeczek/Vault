---
type: Concept
id: 02_plain_text_as_interface
title: "Stage 02: Script (part 3/4)"
source: "Plain Text as Interface.md"
tags: [agentic, agents, context-engineering, icm, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

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
