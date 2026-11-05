---
type: Concept
id: 01_a_complete_guide_to_managing_thousands_of_files
title: "The ICM Folder Structure: A Detailed Guide to Keeping 9,916 Files in One Folder Without Rot (part 2/10)"
source: "A Complete Guide to Managing Thousands of Files in One Folder.md"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

- **One folder** at the top named after the company, because everything belongs to it.
- **The map** — one text file that says what the folder is and where to go for any job.
- **The state** — one text file that says what is true today, with a date written inside it.
- **41 folders** — one for every brand, site, app, client, and kit.
- **`.claude/`** — the AI’s own room. It contains settings, hooks, and memory. In the walkthrough, this had **156 files** about how the speaker works.
- **`START-HERE.md`** — a quick orientation file that explains the system in about two minutes.

### Each Subfolder Repeats the Pattern

Every brand, site, app, client, or kit folder is its own filing cabinet. Open any one of them, and you find the same shape again:

- A **map** (`CLAUDE.md`)
- A **state** (`CONTEXT.md`)
- **Drawers** named in the order the work happens

This means every folder is treated as its own desk with its own map and context layer.

### Drawers Named in Work Order

A typical project folder might look like:

```
Project Folder/
├── CLAUDE.md
├── CONTEXT.md
├── 01-research/
├── 02-offer/
├── 03-build/
├── 04-launch/
└── 05-results/
```

The structure mirrors the workflow, so the AI always knows where to look next.

---

## 4. The Four Layers That Stop Rot

The speaker says the system was not pre-built to stop rot. Every piece was painfully structured from fixing a problem. Without these layers, the folder rots in **two to three weeks**.

### Layer 1: The Map

**File:** `CLAUDE.md`

**Purpose:** Routes every job to the correct location without reading thousands of files.

**What the Map Contains:**

- **Route table by intent** — what you want to do, and where to go.
- **Hard rules** that are enforced.
- **Ownership information** — who owns what.
- **References** to the state file and other important files.

**Example Routes from the Walkthrough:**

| Intent                        | Where It Routes                        |
| ----------------------------- | -------------------------------------- |
| Writing copy                  | Writing Room → context → choose client |
| Edit First Colony Notary site | `/FirstColonyNotary`                   |
| Edit Only RAM site            | `/OnlyRAM` context                     |
| Video production              | `/Production/[ProjectName]`            |
| Blog post                     | Loads voice/style skill automatically  |

**Key Principle:** The map is GPS. It tells the AI where to go, not what to do. It does not describe every file. It routes by intent.

**Hard Rules:** The map contains hard rules that are enforced. It also points to reference hard rules at the top level.

---

### Layer 2: The State

**File:** `CONTEXT.md`

**Purpose:** Declares what is true *today*, with an embedded date.

**Critical Rule:** Always use the **newest state inside the file**, never the file’s modification date.
