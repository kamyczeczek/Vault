---
type: Concept
id: 00_a_complete_guide_to_managing_thousands_of_files
title: "The ICM Folder Structure: A Detailed Guide to Keeping 9,916 Files in One Folder Without Rot (part 1/10)"
source: "A Complete Guide to Managing Thousands of Files in One Folder.md"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

# The ICM Folder Structure: A Detailed Guide to Keeping 9,916 Files in One Folder Without Rot

## 1. Executive Summary

This guide explains how to organize thousands of files—9,916 files across 2,205 folders—inside a single top-level folder using Jake Van Clief’s **ICM folder structure**. The system prevents the folder from turning into an unmanageable pile by using four anti-rot layers:

1. **The Map** — one text file per tree that tells the AI where everything is.
2. **The State** — one text file per tree that says what is true today, with a date written inside it.
3. **Enforcement** — skills and hooks that automatically enforce rules before the AI acts.
4. **Cadence** — a Sunday audit habit that catches drift before it becomes rot.

The core promise: when you ask an AI agent to do a job, it reads **two text files and one drawer** instead of scanning 9,916 files. It never gets confused, never guesses, and never has to be re-explained.

The folder method belongs to **Jake Van Clief** and **David McDermott**. The **97day tree** and the way the speaker runs **Claw Code** are his own.

---

## 2. What ICM Is

ICM is explained with a simple three-part metaphor:

| Part                   | What It Is                        | Function                               |
| ---------------------- | --------------------------------- | -------------------------------------- |
| **The Desk**           | Where the work happens            | One worker instead of seven agents     |
| **The Map**            | A `CLAUDE.md` or `AGENTS.md` file | Tells the AI where everything is filed |
| **The Filing Cabinet** | The files and folders             | Holds the actual work                  |

### How It Works in Practice

1. You ask the AI to do something.
2. The AI looks down at the map.
3. It reads the map to find the right folder.
4. It gets the folder out of the filing cabinet.
5. It puts the work in front of you.
6. It writes notes—your `CONTEXT.md`—and puts everything back when done.

**Key idea:** The map is GPS. The state is the current truth. The folders are the filing cabinet. The AI only reads what it needs.

---

## 3. The One-Folder Architecture

### Top-Level Layout

Everything sits under one folder named after the company:

```
Oath Driven/
├── CLAUDE.md          ← The Map
├── CONTEXT.md         ← The State
├── START-HERE.md      ← Orientation file
├── .claude/           ← AI’s own room: settings, hooks, memory
├── [41+ brand/site/app/client folders]
└── production/        ← Work-in-progress
```

### What the Top Level Contains
