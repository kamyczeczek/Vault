---
type: Concept
title: A Complete Guide to Managing Thousands of Files in One Folder
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
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

**Example: “Game Plan” Hook**
- The speaker asked for a research artifact that had his dad’s game plan on it.
- The hook fired on the word “game plan.”
- It told him to run the video production checkpoint.
- He ran it, and it turned out to be a link lockup, not video work.
- Nothing was built and no stage moved.
- The hook fired, realized it was not needed, and stopped.
- The power is in hooks and running your skills automatically.

**Example: “Blog Post” Hook**
- The speaker asked how many blog posts were posted on FNF and what the current impressions and clicks were.
- The hook fired on “blog post” and told him to load the voice skill.
- He loaded it. Nothing was written for publishing.
- The hook enforced the rule without being asked.

**Key Principle:** Hooks are the enforcement layer. They run before the AI, check rules, and prevent drift.

---

### Layer 4: Cadence — The Sunday Audit

**Command:** “Am I crazy?”

**Purpose:** Weekly maintenance to catch drift before it becomes rot.

**When to Run It:**
- Every Sunday as a cadence.
- Any time you notice drift or something feels wrong.

**What the Audit Does:**

1. Walks every route in the system.
2. Confirms route misses are harmless.
3. Finds the stale section.
4. Reads the state block.
5. Checks each nested project for unsaved work.
6. Provides a scorecard with pass/fail status.
7. Writes ranked fixes below—not applied automatically.

**Audit Output Example:**

```
You are not crazy. A little drift is back.
One of four failure modes up from zero on 9/14.

Your fast state block says the hooks and videos
are at stage four waiting on your voice.
The video library not fixed.

Three fixes written below (ranked, not applied):
1. Fix the hooks bullet
2. Drop the type stage numbers
3. Make the prompt trigger match a word, never a piece of a word
```

**What the Audit Found in the Walkthrough:**
- One of four failure modes was back.
- It was up from zero on 9/14.
- The fast state block said a live video was still waiting on the voice.
- The video library was not fixed.
- It pointed out that only 9 of 35 builds had a results folder.
- Only 11 of 35 builds had a results layer that fills up.
- It had 224 data entries.
- It noted that the fast state block said a live video was still waiting on the voice, and it had gotten worse since 9/14.

**The Fix Process:**
- The audit gives ranked fixes.
- The speaker says, “Fix them all.”
- It fixes them and should run another audit.

**Key Principle:** Without the Sunday habit, the system rots in 2–3 weeks. The audit is routine maintenance.

---

## 5. Live Walkthrough Examples

### 5.1 The One Folder at the Top

- The speaker opens **Oath Driven** on the desktop.
- It contains `CLAUDE.md`, `CONTEXT.md`, `.claude/`, and 41+ folders.
- The `.claude/` folder has 156 files about how he works.
- The handoff is the door for Claude Code to come in and figure out what is going on.
- The daily brain is a plain text file. The newest entry is at the top.

### 5.2 Dad’s Notary

- A recently launched notary business for the speaker’s dad.
- Contains contacts, commissions, positioning, web presence, and outreach.
- Shows how a real business is organized inside the one folder.

### 5.3 Production Folder

- Contains checks, Claude’s AI room, voice checks, and different production assets.
- The speaker is currently in production for the live one-folder walkthrough.
- Files include game plan, script, spec fold, voiceover reader, full API, and Remotion assets.
- At the end, it becomes **nine stages**.
- It captures silence, transcripts, words, matches them up, and creates the final output.

### 5.4 The Final Video Output

- The `out/` folder holds the final video that goes to YouTube.
- Example title: “How I stop Claude Code from breaking my rules.”
- The file has metadata in its properties:
  - Title
  - Five stars
  - Tags
  - Comments
  - Promotion
  - Links back out
- This metadata helps YouTube understand the video and can help get more views.
- A hook and skill trigger called **set video metadata** turns this into an automatic process based on research.

### 5.5 The Map in Action

- The speaker opens `CLAUDE.md` with Notepad.
- It contains a **route by intent** table.
- It has rules, ownership, and references.
- Example: “Writing copy” routes to the Writing Room context.
- Example: “Edit First Colony Notary site” routes to the dad’s folder.
- Example: “Edit Only RAM site” routes to the Only RAM context.
- The map has hard rules that are enforced and points to reference hard rules.

### 5.6 The State in Action

- The speaker opens `CONTEXT.md`.
- It says: “Read the handoff set this session first before you do anything.”
- The state file routing table lives in `CLAUDE.md` (the map).
- The twin table that used to live there drifted from the map and was killed.
- It holds ownership, branch room, and the five-line current state, pruned.
- Current state example: “Idea 19 is at Stage 4.”
- It shows dates and earlier work with Andrew on version five of his tree and skill audit.
- It shows the live board for screen power was made.

### 5.7 Start Here

- `START-HERE.md` explains the system in two minutes.
- It says: “You are looking at Oath Driven’s whole operation in one folder. It’s built so any Claude session can drop in, find work, without you re-explaining what the last session did.”
- It describes three layers:
  1. **The Map** — autoload it. Every session, every folder, every name rule. What not to load. It’s GPS.
  2. **The Router** — open it. Start test. What do you want to do? Go to this home and workspace folder.
  3. **Context** — the workspace itself tells the agent exactly what to load for each task.
- It also lists the rules that keep it from scattering.

### 5.8 Dispatch Zap

- A random folder example.
- Contains the map, context, research, offer, build, launch as a website.
- Had not been touched since 99, but the structure is still there.
- Shows that any folder can be opened and understood quickly.

### 5.9 Lead Magnets

- The lead magnets produced every time.
- Contains all the different zips and giveaways.
- Shows how free downloads are organized.

### 5.10 VIP Call

- Another folder example.
- Shows that brands, websites, applications, mini-applications, and clients are all organized in the same way.

### 5.11 Terminal Walkthrough: Idea 19

- The speaker opens Claude in the terminal.
- He asks: “What are we doing on Idea 19?”
- The AI reads through everything.
- Response: “ID 19 is sitting at stage 409. The reader is done. Your next move is yours. You record.”
- The AI went into production, wiggled through the files, and found the voiceover reader.
- This shows how the AI navigates to the right file without reading all 9,916 files.

### 5.12 Dad’s Game Plan Research

- The speaker asks: “Can you get me the research artifact that has my dad’s game plan on it?”
- This is a completely different task in another folder.
- The research was done over a month ago.
- A hook fires on the word “game plan.”
- It tells him to run the video production checkpoint.
- He runs it, and it turns out to be a link lockup, not video work.
- Nothing was built and no stage moved.
- The AI then realizes the hook was not needed.
- It finds the game plan.
- This shows the power of hooks and skills.

### 5.13 FNF Blog Posts and Search Numbers

- The speaker asks: “How many blog posts have we posted on FNF? And what is the current impressions and clicks from the search engines?”
- The hook fires on “blog post” and tells him to load the voice skill.
- He loads it. Nothing was written for publishing.
- The AI counts 45 blog posts live on filesandfos.com.
- It counts them two ways and both say 45.
- The blog folder on the computer holds 45 posts with blog homepage live sitemap.
- Search numbers: 13 and 30 days old.
- 1,300 impressions, 61 clicks.
- One click for every 22 impressions, about 4%.
- Clicks tripled week over week in the last two to three days.
- One post, “Is Jake Van Clief legit?”, has 19 clicks off 204 impressions.
- This shows the AI can pull real data from the system.

### 5.14 Paid on Deploy

- The speaker had an idea for a website called Paid on Deploy.
- He was going to run a cohort thing for developers who can build anything but freeze when it’s time to close the customer.
- The idea was a 4-week live cohort for developers and five coders, people building with AI tools and terrified of sales.
- The AI pulled up the idea from the folder.
- It went through the content and the offer.

### 5.15 Email List and CRM

- The speaker asks: “How many total subscribers are on my email list and other in my CRM?”
- The AI checks the CRM.
- It has all the nerdy stuff in there.
- There is a context and a Claude file.
- Response: “You have 630 real people on your list.”

### 5.16 Mini SAS Production Line

- The speaker asks: “Where are we at on the production line? Mini SAS.”
- It says files and followers 80%.
- It went from 0 to 550 since 8:15.
- It was 8:15 when the site first went on the internet.
- It has been a month.
- The production line mini is three phases of five.
- Three phases of five done and has been parked since 96.
- It is waiting on the speaker, not on a build problem.
- It read a state file.
- Phase one: the money subscriber can pay monthly through Stripe.
- Phase two: the door, a login link by email, 13 setup screens.
- Phase three: the line itself, on your own account, and a real transcript into a game plan.
- What has left: stage four, the shelf, and then stage five.
- What happened? Nothing since then.
- Do you want to build for now? No.
- It says “same” because it was a read and a health check.
- It also says “better or worse” because the speaker used to ask, “I don’t understand when you’re saying all this random stuff to me. I don’t know if things are better or worse.”

---

## 6. Automatic Backup System

### How It Works

Every time Claude finishes entering a small script, a short-lived instruction runs on its own. The speaker never clicks anything.

**Step 1: Three Quick Safety Checks**

1. Checks payment links.
2. Makes sure no folder is being saved as an empty pointer.
3. Checks that the folder map still matches the real folders.

**Step 2: Change Detection**

- It looks at every file in the workspace.
- It asks if anything changed since the last save.
- If nothing changed, it stops. No empty saves pile up.
- If something changed, it saves a copy of that change.

**Step 3: Save and Stamp**

- It stamps the copy with a date, time, and label.
- It sends the copy to GitHub.
- GitHub is the website that stores every save version of the files.
- If the laptop dies, the business is still there.

**Step 4: Constraints**

- All this runs in the background.
- It has a **60-second limit**.
- The speaker never waits on it.
- It only says it is allowed to see a project with its own separate save history if it is on the skip list.
- It needs its own backup from inside the project.
- Check two catches a project missing from the skipped list.

**Last Two Backups Example:**
- Stamped 11:54 p.m. and 12:39 a.m.
- It was 12:52 and the last automatic backup was during the call.

**Result:**
- Since June, there have been over **2,164 backups**.
- The system automatically commits and backs up to GitHub.

---

## 7. Proof and Results

The one folder produced real numbers:

| Metric                         | Number        |
| ------------------------------ | ------------- |
| Files                          | 9,916         |
| Folders                        | 2,205         |
| Words                          | 2,640,000     |
| State files                    | 170           |
| Routes                         | 48            |
| Skills                         | 81            |
| Skills with their own check    | 61            |
| Backups                        | 2,164         |
| Live websites                  | 13            |
| Videos built                   | 58            |
| School packages and post files | 55            |
| Free downloads built           | 63            |
| Free downloads sent            | 1,193         |
| YouTube views                  | Almost 67,000 |
| YouTube hours watched          | 3,000         |

**Note:** These numbers were from a few days before the walkthrough, so they may have changed slightly.

---

## 8. Getting Started

### 8.1 Free ICM Folder System Brain Interview

- Go to **filesandfolders.com/brain-interview**
- This is where you get the starter folder for free.
- You can get moves one and moves two.
- It will create your one folder.
- It will create an interview, map, and proposal.
- If you want a review first, find the speaker in school and he will help.

### 8.2 Free School Community

- Go to **school.buildmarketclose.com**
- It is free to join.
- You can find the speaker there if you get stuck.
- It has hours of free training on ICM structure, sales, and marketing.
- Inside, go to **Classroom → ICM Folder System Foundation → How do you steal Claude hooks, learn my production line**.
- You get:
  - MDs before you write
  - Approval gate
  - The three jobs rule
  - The library card
  - The term sheet
- You can download a zip with all of it.
- Updated production line includes:
  - Rent math
  - Stage 02 to stage 09 lines
  - Business shapes
  - Term sheets
  - Production line freeze

### 8.3 Free Skills

- The speaker offers **14 free skills**.
- Each one has a video explainer.
- You can see them used and make sure you understand what is happening before you get them.
- Make sure it is for you.

### 8.4 Practice Project

- Fill out five text files on a four-stage workflow.
- You will have a halfway-done website project.
- You can mess around and practice with a halfway-built ICM.

### 8.5 Paid Production Line

- The paid one is in the classroom under **done-for-you video content**.
- It costs **$50**.
- It includes:
  - All 20 skills
  - Nine stages
  - All the skills
  - A playbook
  - Artifact
  - How to use a render in AWS Lambda with 100 free credits
  - An example of a storyboard
  - Ninja SEO stuff
  - How to build a video
  - How to fix everything on prompt
- This is the full-blown actual production line.
- The speaker ran a dime sale and it was closed when the timer hit zero because he does not do fake scarcity.

### 8.6 ICM Folder Systems

- At the bottom of the site, you can pick whatever one you might need:
  - Starter kit
  - Your brain interview
  - Turn your YouTube into a school package
  - ICM folder for that
  - Free 14 quad skills
  - ICM production line (paid)

---

## 9. Testimonials

The speaker shares what people in his school say:

- **Miguel, paying member:** “This was the best investment I’ve made so far. We are tapped in.”
- **Angelo, paying member:** “Rhyac helped me out for five straight hours. I landed the prospect.”
- **Mason, paying member:** “I was ready to give up on AI thinking it was overhyped crap. Now everything is properly set up.”
- **Phil, paying member:** “If you’re looking for a great sales training for the AI industry, you’re in the right spot.”
- **Marcelo, paying member:** “It doesn’t matter how well you can create an AI system if you don’t know how to market and sell it.”
- **Marcelo again this week:** “29 emails, seven replies, two qualified opportunities in one day.”
- There are 28 more on the wall. Every one is a real person in the school.

**Mason’s longer review:**
> “Rhyac helped me decluttered my tangled AI brain before working with him. I was ready to give up on AI thinking it was overhyped crap. Now, because of Rhyac and his ICM structure, everything is properly set up and configured. It was refreshing knowing I was not completely wasting my time. Now my AI runs like all the videos you see on YouTube and it’s amazing. I highly recommend Rhyac and his build market close community to anyone looking for a lead guidance on AI setups.”

---

## 10. Key Rules Summary

| Rule                              | Description                                                  |
| --------------------------------- | ------------------------------------------------------------ |
| **One folder**                    | Everything belongs to the company folder.                    |
| **Map routes, not describes**     | `CLAUDE.md` tells where to go, not what to do.               |
| **State has a date**              | Always trust the embedded date, not the file date.           |
| **Hooks enforce**                 | Rules run automatically based on trigger words.              |
| **Sunday audit**                  | Weekly maintenance prevents rot.                             |
| **Backups are automatic**         | 60-second background saves to GitHub.                        |
| **Structure mirrors workflow**    | Folders named in order work happens.                         |
| **One agent, not seven**          | The desk is one worker. The map sits on the desk.            |
| **Read two files and one drawer** | The AI reads the map, the state, and one drawer—not 9,916 files. |
| **No fake scarcity**              | The speaker does not do fake scarcity.                       |

---

## 11. Maintenance Analogy

The speaker compares the system to a Toyota Camry:

- It lasts forever if you keep it clean.
- But you do have to do maintenance.
- You have to take your car in.
- Get the oil changed.
- Check the brakes after 60,000 miles.
- Routine maintenance is required.
- The Sunday audit is that maintenance.
- Without it, the system rots in two to three weeks.

---

## 12. Final Takeaway

> “That’s how 9,916 files sit in one folder without turning into her picture. The map routes the job. The state carries a date. The rules run themselves. And every Sunday, the audit reads the folder. None of my system was pre-built. Every piece was painfully structured from doing.”

If you are stuck trying to figure this out or living through the same pains, click the link in the description and get your free ICM folder system interview. It will give you a fantastic foundational start if you haven’t started, and it will organize your mess if you already have one.

The lesson lives in the free school with hours of free training on ICM structure, sales, and marketing. You do not need to pay anything to get yours free in the link below. The school is also free. You can find the speaker in there if you get stuck.

If you like content like this, subscribe so you are alerted on the next drop. Join the free school community and say hello. If you like free software that helps you build, market, and close your offers, go to **buildmarketclose.com**. If you are just starting with AI or currently stuck in a multi-agent workflow, go get your free files and folder system at **filesinfolders.com**.

Now go be dangerous. Always got your back. — Rhyac
