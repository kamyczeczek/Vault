---
type: Concept
title: Can an AI Out-Plan a Senior Engineer
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Can an AI Out-Plan a Senior Engineer? — Structured Notes

## Episode Overview
- Show: *AI That Works* — monthly “No Vibes Allowed” episode: real-time coding, process sharing, practical agentic engineering.
- Hosts/guests:
  - **Vaibhav** — works on BAML programming language.
  - **Kevin Gregory** — ML/AI engineer at EvolutionIQ (disability insurance claims guidance systems; company acquired for ~$730M).
- Topic: How to build design docs for extremely complicated concepts using AI, internal tooling for sharing/reviewing docs, and a deep dive into designing threading for BAML.

---

## Core Thesis
- Implementation can often be **one-shot** if the design is phenomenally correct.
- Good design doc/plan → Claude Code/Cursor can often implement in one shot.
- Bad or incomplete design → implementation fails or requires heavy iteration.
- Hard problems may not be one-shot implementable, but good design can break them into **4–5 chunks**, each individually one-shot implementable and each providing meaningful system upgrades.
- Example: Threading in BAML — Vaibhav had spent ~4 days purely designing, not coding.

---

## Design Docs & Planning Philosophy
- Claude Code founder reportedly goes back and forth on the plan, then kicks it off and starts another.
- Most time is now spent writing/reading design docs and plans, not typing code.
  - Vaibhav: >50% of time on docs/plans.
  - Kevin: most time reading design documents/plans and iterating.
- Hands-on keyboard typing code is largely solved; design docs are more important.
- Assumptions must be explicit in the doc because you’re giving instructions to an agent.
- Design docs also help question assumptions and reveal hidden design patterns.
- Models assume you are correct and have context; ask them to challenge your design.

---

## Fighting AI Slop with Slop
- Internal tools built with AI-generated “slop” are acceptable if they improve workflow.
- Goal: use slop to build internal tools that make it easy to produce high-quality documents.
- Internal tools are not customer-facing; don’t need solid principles if they get the job done.
- BAML’s BEP folder is described as “a pure AI slop mess.”
  - Features are added by tagging coding agents in Slack.
  - Vaibhav has never opened Claude himself to add features to BEPs.

---

## BEP System (BAML Enhancement Proposals)
- **BEP** = BAML Enhancement Proposals — way to add new language features.
- Tooling:
  - Internal website for sharing markdown files with comments.
  - GitHub not good for sharing massive amounts of markdown.
  - Slack integration: every comment creates a Slack thread.
  - Slack used as notification system.
  - Users auto-connected via GitHub account with Boundary email; team members get different privileges.
  - Public can log in with GitHub at `beps.boundaryml.com` to see work.
  - Fully open source in BAML repo, written in TypeScript.
- Problem solved: Google Docs/Drive lacks tracking of what’s discussed, approved, comments, status.
- BEP states:
  - Can mark special things as “good for the LLM.”
  - Other new design docs automatically pull them into context as reference.
- Export:
  - Export all BEPs as a zip with folder structure, every BEP/version/data/pages.
  - Export single BEP with all versions, discussions, questions, comments baked into agent context.
- Assumption: person moving doc from draft → proposed has done legwork that it is good and readable.
- No built-in notifications to ask specific reviewers; they tag people on Slack.
- Claude skills + CLI tool:
  - Python script + Claude skill called “BEP.”
  - `BEP pull` pulls data and tells you if something is out of sync.
  - Example: detects two lines removed from `readme.md`; ask which two lines; Claude fixes it.
  - Robust for renaming.
- Workflow:
  - Developer edits markdown with Claude.
  - Colleagues review on dashboard UI.
  - Vaibhav spends zero time thinking about BEP tooling.

---

## Threading in BAML — Case Study

### Problem
- Designing BAML’s threading system.
- 4 days of pure design, no coding.
- Not expected to be one-shot implementable, but can be split into chunks.

### Key Problem: Function Coloring
- Worst part of threading: colored functions.
- Society chose async IO over threading for convenience/concurrency.
- Async IO gives concurrency, not parallelism.
- Problem: `readFileSync` vs `readFileAsync`; once in async context, hard to leave.
- Sync context cannot `await` without marking upstream functions async.
- Legacy pain: concurrency wasn’t day-one in most languages.
- Want: no function coloring, no separate async/sync versions, but still want parallelism (e.g., 5 LM calls in parallel).

### Proposed Model
- Similar to async IO, but **call site determines** if it happens concurrently or in congruence.
- Example:
  - Ask fastest model.
  - `spawn` a named context with various things.
  - Each runs code directly.
  - Return type is a future.
  - Await any futures, get first response back.
- Design premise: BAML should be great for application development.
  - Frequent behavior should be syntactically most convenient without compromising correctness.
  - Don’t make the right thing harder.
- Thread pools:
  - Spawn things and run at most three at the same time.
  - Concept of a queue.

### Prior Art Considered
- Languages do async/await, virtual threads, OS threads.
- Do not want OS threads: heavyweight, complicated, app developers shouldn’t think about them.
- Likely copy Go/Kotlin coroutines and Python coroutines.
- Avoid async/await coloring.

### Middleware Concept
- Wrap a spawn with retry, timeout, timing, fallback, etc.
- Retry arbitrary blocks of code.
- Fallback: if fails, give a value; guarantees future can never error (error type `never`).
- Examples: retry, timeout, timing, fire-and-forget, unhandled spawns, futures spawning futures, cancellation, rate limiting, cancel token, conditional spawning, select.
- Select was removed after discussion.
- Timing:
  - Logs how long task took.
  - With retry, timing can measure full system or each retry individually depending on composition.

### Design Decisions Recorded
- Do futures start immediately, at await, or at `.start`?
  - Decision: spawns start immediately as soon as you hit `spawn`.
- Futures are shareable.
  - Await twice is idempotent; same response.
- Futures outlive their spawners.
  - Can be returned by a function.
  - Useful for map functions: array of URLs run in parallel.
- Await syntax:
  - Prefix `await` like TypeScript, not postfix `.await` like Rust.
  - Target audience: Python and TypeScript devs.
- Await rethrows errors from futures; type safe.
- Cancellation is a panic.
- Errors are type safe; infer error type a function can throw.
- Two kinds of errors:
  - Errors you deal with.
  - Errors you must explicitly catch.
- To avoid cancellation, explicitly ignore cancel signal and give a value instead.
- By default, cancellations rethrown.
- Cancellations happen at await points.
- Parent canceled → children canceled by default; need work to detach.
- Explicitly out of scope:
  - Task local storage.
  - Thread local storage.
  - Select.
  - Conditional spawning (not relevant).
  - Deadlock detection.

### Huddle Transcript → Design Doc Process
- Recorded Slack huddle, transcribed.
- Copied full transcript; prompted model to reorganize.
- BEP 34 “spawn” very complex; many implicit design decisions.
- Model outlined: summary, motivation, simplest form, design decisions, syntax decisions.
- Some decisions changed/introduced from meeting; some locked into document.
- Asked model to pull out complicated decisions and examples.
- Final optimization: reduce scope, 104 KB → 62 KB (about half verbosity).
- Read whole thing to make it good.
- Created V2 rather than editing in place.
  - Models often mess up if replacing in place for design docs.
  - Analogy: humans get lazy/inconsistent when editing; rewriting from scratch is more coherent.
  - Sunk cost fallacy: people keep editing instead of rewriting.
- Split into two documents:
  - Spawn doc: motivation, function coloring top priority, simplest spawns, named spawns, design decisions.
  - Prior art subpage: nuanced, detailed, code samples.

### Prior Art Subpage
- Abort controller (TypeScript), Go `CTX`.
- Go: every function carries `CTX`; explicit but burdensome for app developers.
- TypeScript: no philosophy around cancel tokens; abort controller rarely used; APIs not cancelable by default.
- BAML prefers implicit cancellation of Python.
- Made subpage instead of main readme because nuanced and needs code samples.

---

## Middleware BEP
- Middleware: add middleware into system.
- Examples:
  - Scope of code has cost limit of $5.
  - Use Cloud SDK with string passed in.
  - Retry with timeout on fetch.
- Discusses why not wrapper functions.
- Prior art:
  - Express, Python decorators, .NET middleware.
  - Vaibhav would have been lazy; AI found .NET mechanism.
- Implemented examples:
  - `with retry`
  - Timeout using spawn
  - Timing
  - Fallback
  - Composition
  - Exponential backoff, jitter, constant
  - Selective error handling: retry only timeout/rate limit, not auth errors
  - Circuit breaker
  - Rate limiter
  - Cache: run block of code with cache key
- Discovery during implementation: “Holy cow, we have to redesign this thing.”
- Cost limit required thread local storage — a hidden dependency.
- LLMs will write every piece of code asked; ask them to challenge what should not be possible but is being done.

---

## Versioning & Tooling
- Two ways to work with BEPs:
  1. Download all BEPs and work off them (need context of other BEPs).
  2. Use web UI with built-in versions.
- Example: Patterns BEP has 7 versions.
- Each version has its own comment chain.
- Old versions read-only; can’t edit comments.
- Export single BEP includes all versions, discussions, questions, comments baked into agent context.
- Don’t use Git because:
  - Comment tracking hard on diffs.
  - Want purely linear history.
  - Push to it and that’s it.
- Might switch to Git eventually.
- Naming depth folders: numbers + name, so `ls` shows depth without reading.
- Build tooling so you don’t have to keep everything in your head.
- Check every implemented BEP for consistency, syntax, weird interactions.

---

## Key Insights & Takeaways
- AI can help out-plan senior engineers by producing thorough design docs when guided well.
- Design docs are where leverage is; implementation is increasingly one-shot.
- Fight AI slop with slop: use AI to build internal tools that improve doc quality.
- Tooling should reduce cognitive load: export, versions, Slack integration, CLI sync.
- Models assume you are correct; ask for alternatives and challenges.
- Models are good at generating examples, prior art, and surfacing hidden design decisions.
- Hard problems need decomposition into chunks; each chunk can be one-shot implementable.
- Rewriting design docs from scratch often works better than in-place editing.
- Frequent behavior should be syntactically convenient; correctness still matters.
- Function coloring is a major pain point BAML wants to avoid.
- Cancellation, futures, spawn semantics, and error handling require many explicit design decisions.
- Internal tools don’t need to be pretty; they need to enable high-quality output.

---

## Notable Quotes
- “This is how you fight AI slop with slop.”
- “Implementation can often be one shot if the design is phenomenally correct.”
- “The real answer is not get good. The real answer is build tooling so that you don’t have to keep track of everything in your head.”
- “Why would a model… humans get lazy and inconsistent when they edit things. Editing is a harder exercise to be coherent in than rewriting from scratch.”
- “LLMs will write every piece of code that you ask them to. Ask it to challenge what should not be possible in this design but is going to actually be done here.”
- “Now that the job of hands-on keyboard typing code is kind of just been solved, we have a lot more time to write these design docs.”