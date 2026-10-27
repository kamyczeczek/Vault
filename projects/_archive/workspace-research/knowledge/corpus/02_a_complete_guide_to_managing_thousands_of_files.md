---
type: Concept
id: 02_a_complete_guide_to_managing_thousands_of_files
title: "The ICM Folder Structure: A Detailed Guide to Keeping 9,916 Files in One Folder Without Rot (part 3/10)"
source: "A Complete Guide to Managing Thousands of Files in One Folder.md"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

**Why the Date Matters:**
- File dates can lie because of copies, backups, or sync issues.
- The embedded date ensures the AI reads current truth.
- The state file is the single place the session reads to know what is true today.

**What the State Contains:**

- **Current state in five lines** — the newest truth.
- **Project status** — e.g., “Idea 19 is at Stage 4.”
- **What is built vs. what is pending.**
- **References to the daily brain/handoff log.**
- **Ownership information.**
- **Branch room and five-line current state, pruned.**

**The Daily Brain / Handoff:**
- The newest entry is at the top.
- It acts as a fast shared log.
- It usually puts in three sessions and three bullets at a time.
- Times are included.
- Example: “Early AM hour one build done. Ryan’s go let’s run a trial.”
- Example: “Andrew’s proposed tree. I was working with Andrew on getting his stuff fixed.”

**Drift Catch Example:**
- The state file caught a drift back on **August 11th**.
- The twin table that used to live in the state drifted from the map and was killed.
- The state file now holds ownership, branch room, and the five-line current state.

**Key Principle:** The state carries a date. The AI never guesses. If the state says a live video is waiting on your voice, that is the truth until the state is updated.

---

### Layer 3: Enforcement — Skills and Hooks

**Components:** Skills + Hooks

**Skills:**
- Pre-built capabilities that carry their own validation checks.
- In the walkthrough: **81 skills**, with **61 skills that carry their own check**.
- Skills are triggered by hooks or by intent.

**Hooks:**
- Automated rules that fire based on keywords before the AI responds.
- A hook reads your words before the AI does.
- It checks what you touch when it stops or refuses a file that breaks a rule before it lands.
- Hooks enforce rules automatically, so you do not have to remember to invoke skills.

**How Hooks Work:**

1. You say something.
2. The hook reads your words before the AI does.
3. The hook checks what you are touching.
4. It either stops or refuses files that break a rule before they land.
5. It can fire a skill automatically.

**Example Hooks from the Walkthrough:**

| Trigger Word          | Hook Action                             |
| --------------------- | --------------------------------------- |
| “game plan”           | Fires video production checkpoint skill |
| “blog post”           | Loads voice/style skill automatically   |
| “am I crazy?”         | Runs full system audit                  |
| Writing for the human | Writes in the speaker’s voice and style |
