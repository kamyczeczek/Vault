---
type: Concept
title: Theo's AGENTS.md & SKILLS.md Breakdown
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Structured Notes: Theo's AGENTS.md & SKILLS.md Breakdown

## 1. Context & Motivation

**Background:**
- Theo has been coding more than ever — dozens of PRs landed in 3 days
- Productivity attributed to T3 Code improvements (parallel work across machines) and heavy editor time
- Spent ~6 hours editing markdown, then 6–10 hours testing changes — "as long as you consider markdown files code"

**Core thesis:**
- The value isn't in copying his exact instructions — it's in **how he thought about them**, the reasons behind additions, and the iterative path
- He **intentionally does not publish** his AGENTS.md/CLAUDE.md files
- Copying them = copying someone's generic code template and applying it to everything you've ever worked on
- These files influence how *all* agents work across *everything* — you should control, edit, and evolve them based on your own needs/problems
- **Main goal of all this work is not making the model better at code — it's making the model better at communicating with him**

---

## 2. The Fleet Repo & Multi-Machine Setup

**Setup:**
- 4–5 machines used for dev work, controlled via T3 Code
- T3 Code lets you click and choose which box runs a given task/diff
- Managing skills availability across machines became complex → started building a custom system → buggy, annoying edge cases → **stopped**

**The "fleet repo" solution:**
- Just markdown files + a fork of `vibe-proxy` (modified CLI proxy API for his needs)
- Contains:
  - `AGENTS.md` / `CLAUDE.md` describing the project and what agents should do
  - `skills/` directory with subfolders:
    - **Claude-only skills**
    - **Command center skills** (only on the leader machine that controls others)
    - **Universal skills** (all machines)
  - Metadata indicating which skills should appear on which machines
- Machines are color-coded (matching tmux colors) for easy identification over SSH
- Recently doing less SSH — mostly working through T3 Code

---

## 3. The Global AGENTS.md / CLAUDE.md

### Old File (lived with for ~2 years)
- Repo-specific agent instructions override these; user instructions override both
- TypeScript: avoid `any` unless no reasonably typed alternative or explicitly requested
- Commands: stop spinning up dev servers / breaking environment; prefer targeted verification first (typecheck, lint, focused tests) over full builds
- Package manager preferences (bun > pnpm)
- Tech preferences, code styles
- Recently added YAGNI bit (meaningfully helped)
- Computer inventory (added by an agent during fleet work)

### New File — Key Sections

**Identity framing:**
- "I'm Theo, you're my agent. We're working together a lot, so I thought it'd be worth introducing myself."
- Mentions YouTube channel, T3 products (T3 GG, T3 Chat, T3 Code, UploadThing)
- "I love to build. I focus on building complex things as simple as possible. I love to find ways to reduce complexity when solving problems."
- **Why this matters:** models are good at tone-matching — talk a certain way and the model mirrors it back. This helped with overeager models (5.6 Soul, Opus 5) that were too proactive and wrote too much code.

**General coding preferences:**
- Keep things simple; type safety is useful
- Don't be scared to propose bold ideas that meaningfully benefit the work
- Be careful with destructive actions that aren't explicitly requested
- Tests are good; endless smoke tests/regression tests for feature deletions are less good — focused, not slop
- Comments clarify functions and usage; don't comment every line; keep comments up to date

**TypeScript preferences:**
- "If your TypeScript code looks like a Python dev wrote it, it's bad TypeScript code"
- Avoid one-liners that are just casting wrappers
- "Write TypeScript in ways that Matt Pocock and Theo would be proud of"
- Preferred stack for complex web/React Native: Zustand, React Query, TanStack Start, Clerk or Better Auth (self-hosting), ArkType or Zod

**Behavioral rules:**
- **Questions are read-only** — helped stop 5.5/5.6 from making changes when just asked about things
- **Match ceremony to the task** — don't spawn sub-agents/multi-agent panels for work a single agent finishes in one pass; delegation is for breadth or adversarial review, not ordinary tasks
- **State file ownership up front** so parallel agents don't collide (fixed sub-agents editing same files)
- Visual/design work: don't edit real components first; use stand-in contrasts; prefer dark mode with white text; glass radius; avoid grays
- Separate pull request section (see skills below)

---

## 4. Skills Deep Dive

### 4.1 The Description Mistake (Most Important Concept)

**Most people (and agents) get this wrong:**
- The description is **always inserted into context even if the skill isn't used**
- It should NOT describe what the skill does — it should be **trigger keywords** telling the model *when* to pull the skill in
- Treat the description as trigger keywords, not an actual description
- Example: could delete "monitor a pull request through review and CI" and just have: *"Use when the user asks to monitor, watch, or babysit a PR."*

### 4.2 Babysit PR Skill

**Origin:** same few instructions repeated over and over with inconsistent results; many projects have AI code reviewers (T3 Code has 3–4)

**Purpose:** agent monitors PR — rebasing, pulling in main, reading review comments, addressing them, looping until green and approved

**Failure patterns that prompted it:**
- Agent commenting through Theo's account without indicating it's an agent
- PR getting 3× larger than it should because every comment treated as mission-critical

**Key instructions:**
- Use harness tools to monitor PR if available; otherwise poll
- Only act on checks/comments newer than the latest push
- Verify every bot finding against source before changing code
- Fix real findings and CI failures
- Distinguish repository failures from infrastructure flakes
- Reply with written reason when dismissing false positives
- Watch changes to main; rebase when needed
- If overlapping PR makes this obsolete: stop, report, ask before closing unless closure was authorized
- Format comments on Theo's behalf: markdown, model slug, "responding on behalf of Theo", actual reply
- **Most important line:** "Do not let review feedback expand the PR beyond the user's original goal. Address real shortcomings, but avoid scope creep."

### 4.3 File PR Skill

**Description:** "File a concise pull request. Use when the user asks to file, open, or create a PR."

**Why separated from babysit PR:** once keywords were good enough at triggering, didn't need them combined; often wants one and not the other

**Problems it fixed:** agents filed PRs in ways he hated

**Bad PR example (title):** "fix server, parse CLI version and update preflight" — summary about verifying pinned runtimes, self-updating processor, wrong version coverage — **unreadable in plain language**

**Instructions:**
- Before filing, check whether a PR for this branch already exists
- Review diff locally against origin main to make sure contents match goal
- PR titles usually become commit messages → follow repo title conventions; look at recently merged PRs and git history
- Prefer concise human-readable title explaining *why* changes matter
- **Bad example:** "perf server, negotiate per message deflate on the websocket"
- **Good example:** "perf server, cut websocket frame size by 70% with gzipping"
- **Agents are really good at bad/good examples** — if an agent does something poorly, put 1–2 examples in a skill or globals to seed its weights with what matters to you

**PR description format (life-changing):**
- Open with a simple explanation of the problem based on the user's original prompt, then briefly explain the solution
- Do NOT lead with an implementation inventory
- **Bad example:** "removed implicit workspace carryover from every new thread entry point. New threads inherit only the project from context, branch work tree audio..."
- **Good example:** "my new work tree default was ignored when starting new threads on existing work trees, super unintuitive. Now your preference is always apply."
- Stop opening draft PRs (Codex loves drafts that don't get reviews) — open real PRs so review bots run
- If user also asked to babysit, continue with babysit PR skill
- Add a blurb at end of PR description about what model and harness made the changes (helps track what's being used for different work)
  - Codex often doesn't know its own model (doesn't include model slug in system prompt) — sometimes says 5.4 filed it when it didn't
  - Claude always knows; most other harnesses know

**Good real example:** "fix for release, skip scripts during Vercel installs. The hosted web deployment runs its filtered Vercel install command twice. Both installs invoke the root prepare lifecycle so the persistent build cache accumulated effect TS go backups until it hit the 100 file limit and blocked releases. So now we're running with ignore scripts."

**Another good example (stash prompts bug):** "Stashing a prompt, switching providers, and restoring it didn't work. The stash was bucketed per provider instance, so after a switch, the badge disappeared and the stash looked lost. Restoring also dragged the stash model selection back, defeating the point of moving a prompt to a different provider."

### 4.4 File Upload Skill

- Custom service he built; bought `tslop.org` on Cloudflare for file hosting
- Uploads any local file (screenshot, screen recording, log, document, markdown, config, build artifact, archive) to `files.tslop.org` and returns public URL
- **Description (rewritten):** "When user asks to upload a file or one is needed for PR descriptions use this skill."
- Has a `requires` section in metadata — don't want skill on machines without global file host token; if unset, tell user instead of guessing
- Uses only file's base name (e.g., `loginflow.mp4`); server slugifies and adds random suffix
- Instructions for using URL in GitHub; can encode GIF preview when it makes sense (included ffmpeg command)
- **Use case:** on T3 Code mobile app, agent builds feature → tell it to upload file and respond with URL → click to watch video recorded on real computer
- Tell it to file a PR → includes URL as embedded video in PR
- **Not super useful for the agent — really useful for Theo when he wants the agent to show him something**

### 4.5 HTML Communication Skill (formerly HTML Planning)

- Originally called "HTML planning" but now used for non-plan things
- **Description:** "When the user asks for an HTML write-up of work, not as part of the code base, use this skill to create and always upload it to post plan" + useful for reading postplan.dev URLs (agent was trying to browser-use instead of curl)
- **When to use:** any request to produce a readable HTML artifact for a human — plan, spec, write-up, findings, summary, report, comparison, set of UI mocks (word "plan" often absent)
- **Reading postplan URLs:** fetch uploaded HTML immediately with shell — do NOT use web search or browsers
- Uses **postplan** — a microservice allowing file upload with one command; same path = same URL, updates with versions
- Write one self-contained HTML file, capped at 512 (KB?), write like a spec not a landing page
- UI mocks: label A, B, C for easy selection; lay out for direct comparison; keep one file across iterations so URL stays stable
- Never open browser or claim document is hosted before upload succeeds
- Do not verify in browser unless user asks (tired of Opus randomly doing this)

**Skill split process (real prompt shown):**
- Refamiliarize with current state before editing
- HTML communication skill is overloaded → break into two (like file PR / babysit PR)
- Descriptions for both should be simple, focused on when to trigger
- One = "post plan read" for reading content from postplan URLs
- Other = "HTML communication" for communicating to user via HTML
- "When to use" section should not exist in postplan skill, only in HTML communication; should be more minimal
- Make changes, don't commit or push yet — **give the model a stop point, life gets much better**
- Added: "Or if they mention HTML with no additional context" → can just say "HTML" at end of prompt

### 4.6 Provision a Box Skill (Command Center)

- For bringing new computers into the network / re-imaging machines
- Didn't want to set up Nix etc. — just wanted machines online ASAP
- Process: configured machines how he liked → told agent to look at config, bash history, everything set up → write it all down → set up another machine with all of it
- Agent got a lot but missed some things and did unnecessary things → told it those → adjusted instructions
- Result: "provision a box" skill with everything wanted on new machines, settable over SSH
- Also made an HTML page updating every time fleet changes — details all machines, specs, what they do, what exists on them, connection methods, baseline software, tmux, shell config, controlling tmux over SSH with mouse

---

## 5. Project-Specific AGENTS.md (T3 Code)

### Key Principle: AGENTS.md ≠ README.md
- README = context on project for humans/agents deciding whether to pull in code
- AGENTS.md/CLAUDE.md = tell the agent *how to change things* in the codebase and *what it should know before making changes*
- Yes, some project description belongs, but majority should focus on **how agents work in the project**
- Written for agents to help them interact with the dev better — not written for devs

### Glossary (One of the Most Important Details)
- Helps agent understand you a bit, but **much more helpful for the agent to describe things to you the way you want**
- Even simple terms the model already knows become powerful when given this simple language
- T3 Code glossary examples:
  - **You** = the agent reading the file and changing T3 Code
  - **We/us/maintainers** = Theo, Julius, and people building T3 Code
  - **User** = person using T3 Code to direct coding agents
  - **Agent** = coding agent a user runs inside T3 Code (may include "you")
  - **Provider** = agent runtime/harness T3 Code talks to (Codex, Claude, Cursor, OpenCode)
  - **Client** = web, desktop, mobile UIs
  - **Environment** = one running T3 server + machine, filesystem, provider credentials, state
  - **Project** = an environment-local workspace record rooted at a directory

### Project Overview Section
- T3 Code = minimal GUI for coding agents; Node WebSocket server wraps provider CLIs (Codex, Claude, Cursor, Grok, OpenCode); serves web/desktop/mobile clients
- "Open source bring your own subscription alternative to apps like Claude Desktop, Codex App, Cursor Glass, Conductor"
- Purpose: agent spends less time figuring out what the project is; knows what to model UI/UX on

### "What Makes T3 Code Special" / Never Compromise On
- Gives model an idea of what it should **never compromise on** — if changes hurt these, don't make them
- **Open at the core** — truly open; share roadmap, thinking, all code; large number of users run forks; work in the open
- **Performance without compromise** — regularly audit for regressions (too much data over WebSockets, CSS animations causing GPU spikes, hard-to-render lists); all changes considerate of performance
- **Remote ready** — WebSocket layer + `npx t3` enables remote features; local network, Tailscale, or T3 Connect tunnel solution
- **Multi-surface** — web (two: public app + locally hosted via `npx t3`), desktop (main surface, Electron app bundling server runner, can host for remote connections), mobile (React Native iOS/Android, early access TestFlight, close to global shipping)

### "A Note from Theo" Section
- "I like ambitious ideas, simple systems, and software that feels obvious"
- Do not preserve complexity just because it exists
- Do not introduce machinery because it looks architecturally impressive
- Understand the real constraint, then fight for the smallest model that makes correct behavior unsurprising
- Channel "measure twice, cut once" and YAGNI
- Fight scope creep
- Honor dev's intent in minimal and realistic fashion
- **Important framing:** "Think of these instructions less as hard rules, more as good defaults" — developer preferences should override anything here

### The "Opus Killed My Jobs" Callout
- Most T3 Code contributions come from T3 Code itself, often controlled remotely
- Be careful about accessing data, killing dev servers, and other things that may damage the contributor's T3 Code instance
- Inspired by Opus killing running jobs — "so annoying that it inspired me to do this whole rewrite. So I guess Opus has contributed a lot."
- Opus 5 went from favorite model to one that pisses him off; avoids it now

### "Three Ways to Hurt Yourself"
- Came directly from Soul auditing his logs and finding frequent failure modes

### "Hit Every Surface" Section
- Most common defect: change works on tested path but missing everywhere else
- Before calling front-end work done, walk the list:
  - Entry points: settings page, command palette, keybindings
  - Clients: web, desktop, mobile
  - Shared logic in shared package client runtime
  - Providers: each has own adapters; provider-shipped features need a decision per adapter even if decision is "not supported here"
  - Contracts package: describes everything crossing the wire over WebSocket/HTTP cold store — changes often not reflected here
  - **Reverse states:** added things like settle and snooze but no logic to unsettle/unsnooze
  - Connection modes: make sure all work as expected
  - Docs

### Docs Split
- Split user and maintainer docs into two entirely separate entry points (PR still open)
- Problem: models writing internal details into user-facing docs
- Clear split + tuning in AGENTS.md steers model correctly

### Dev Server Instructions
- Models often try to call `bun` though project is Vite Plus
- Models bad at Vite Plus — try to type "Vite Plus" which doesn't work; must use `vp`
- Also use `vp dev` instead of `vp run dev` — `vp dev` does its own thing, `vp run dev` does what you want (unlike `pnpm dev`/`bun dev` which do the obvious thing)
- Rant: "our friend Evan You could not get over his [decision]. It is what it is. He's wrong. It is hurting real users. Now I have to add this line and burn millions of tokens over the next few years."
- Custom T3 Code home directories so spinning up dev server doesn't break running server
- Share dev server over Tailnet/Tailscale for remote dev work
- Share correct URL with pairing token
- Save PID when spinning up dev instance so it can kill the right one
- Explicit instructions for test data
- Verification: "Upon request, user-visible front-end changes should get one integrated pass in a real client" — stop spinning up computer use unnecessarily
- Skills: `test-t3-app` and `test-t3-mobile` (written by Julius) for spinning up and testing with computer use

### More PR Instructions
- ~500 PRs; want them easier to read

### "Where Code Lives" / Taste Section
- Complexity belongs at the adapter boundary, orchestration stays pure, UI stays dumb
- Inferred types over annotations; `any` is the enemy
- Comments describe how a thing is used and move when code moves; mostly describe functions, not annotate every line
- Users drive agents all day and notice dropped frames, lying spinners, stale labels
- No continuously repainted animations — they peg the GPU
- Fight the task in front of you, say so loudly, get human sign-off before breaking it
- Security important but don't over-index, especially for dev mode and maintainer-only features

### Complexity Insight
- "You don't notice complexity that isn't necessary until it crosses a certain threshold"
- Problem: stuff got unnecessarily complex; only noticed when too far
- Took all causes, put them in file, now everything is less complex
- **Prompts have gotten way smaller as a result**

### Real Prompt Examples (Showing the Payoff)
1. **iOS/Android marketing site:** "I have to add the iOS and Android apps for T3 code to the marketing site... I want these ASAP." Agent created mocks A/B/C/D. Response: "I hate most of these. It wants C plus D plus A together. Do C plus D plus A. File and babysit." — that's the whole prompt
2. **Remote upgrade path UI fix:** described goal → "File and PR."
3. **Settle button bug:** "I had a woke thread that I wanted to settle and I was unable. The settle button that appeared on hover would not work. Right click settle did. Diagnose and fix, file and babysit." → PR ready to merge in ~15 minutes (was a pointer-events CSS bug)
   - "That's pretty [fucking] cool. I know it's silly, but this has been really nice."

---

## 6. The Audit Process (Using Agents to Analyze History)

### The Prompt That Changed Everything
- Asked agent to write two separate Claude MD drafts based on goals → didn't like them much
- Then asked: **"Can you look through my history with models like Fable, Opus, and GPT-5.6-Soul in Claude Code and Codex on this machine to see what the most common mistakes are? Want to make sure we optimize to steer away from those. Break down the most common failure modes and how often each model hits them."**

### Findings
- **Opus 5** was aggressively killing the wrong process — often killing the T3 Code instance it was running in; confirmed with real numbers (more times in 2 days than Fable in all time used)
- **User data touches:** almost all read-only inspection, but should audit further
- **PR hygiene:** Soul filed drafts 40% of the time; other models much less likely
- **Repo-wide check failures:** running things it didn't need to, taking way more resources/build time
- **Bash error rates** tracked per agent
- **Corrections per 100 user messages per model:** tells Fable things are wrong often (but uses Fable for hardest stuff with less context going in); tells Opus 5 results look wrong way more often; Soul looks good but GPT models aren't used for UI, so "looks wrong" probably means moving off Soul
- **Process problems:** more problems with Fable leaving branches stale, not fixing CI
- **Opus 4.8** misread requests very often
- **Tool misuse:** Opus worst by far; Opus 5 misusing things constantly and breaking environment
- **Overbuild:** Opus 5 and Opus 4.8 most aggressive; Fable slightly worse than Soul overall (universal problem)
- **Stopping early:** universal problem
- **No verify:** pretty universal
- **Regression:** rare but expensive
- **Unasked edits:** only Soul did these; proposed changes to global files it thought made sense
- Note: did all this with Opus because out of Fable; Fable and 5.6 did better audits

### How to Use the Audit
- Purpose: get a better feel for what went right and wrong in history
- Some is vibing/gut feel, but easier to have agents go through history than read it all yourself
- If a thread didn't go how you wanted, ask the agent: "Why did you make this decision? What gave you indication this was the right direction?"
  - Might be something outdated in AGENTS.md/CLAUDE.md
  - Might be something read incorrectly earlier and followed along once in context
- If a simple change took 30+ minutes when you thought 5: ask why, ask it to categorize tool calls into groups and determine which were/weren't helpful
- Notice failure modes, ask questions, adjust

---

## 7. Key Principles & Lessons

### On Writing These Files
1. **Don't copy-paste others' files** — value is in the process and reasoning, not the exact instructions
2. **Descriptions are triggers, not descriptions** — always inserted into context; use keywords for when to pull in
3. **AGENTS.md ≠ README** — write for agents to interact with the dev better
4. **Glossary is one of the most important details** — helps agent describe things to you the way you want
5. **Tone matters** — models tone-match; talk how you want them to talk
6. **Bad/good examples are powerful** — agents are really good at them; seed weights with what matters
7. **Give the model a stop point** — "Don't commit or push yet. I'll tell you when"
8. **Less context is best** — as long as it has the context it needs
9. **Think of instructions as good defaults, not hard rules** — let developer preferences override
10. **Everything is about communication** — main point isn't technical competence but making the model better at communicating with you, maintainers, contributors

### On Process
- Audit your history with agents regularly — get stats on failure modes
- Ask agents why they made decisions
- Ask agents to categorize tool calls when things take too long
- Notice complexity only when it crosses a threshold — capture causes before it's too far
- Keep everything synced across machines (SSH over Tailscale, fleet repo)
- Build skills based on your needs and experience — don't install someone else's

### The Vision
- "How cool is it that I am writing markdown, effectively copy, in order to change the behavior of the agents across all of the machines on my network. And now this just works."
- Igor's observation: "Steve Jobs would be so mesmerized by this. Steve Jobs would go so hard at vibe coding. He would have fired all of his engineers and turned macOS into complete slop."

---

## 8. Sponsors Mentioned (for completeness)

- **WorkOS** — auth for serious apps; enterprise features (Okta, SAML, Duo, ADP, ADFS), admin portal, agent auth standard (partnered with Cloudflare, Firecrawl, Resend, Monday, Kernel); `soydev.link/workos`
- **Convex** — backend/database; all of T3 Chat built on it; CloudKit plugin; one folder representing entire backend makes it easy for agents; Jamie and James (helped Dropbox scale); `swade.link/convex`

---

## 9. Closing Notes

- Video longer than Codex's system prompts
- Don't blindly copy his stuff — learn and understand how your agents work in your projects
- The tips should be genuinely helpful
- "Peace nerds."