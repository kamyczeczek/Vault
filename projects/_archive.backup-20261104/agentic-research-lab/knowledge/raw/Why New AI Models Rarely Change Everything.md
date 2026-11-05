---
type: Concept
title: Why New AI Models Rarely Change Everything
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Testing Claude Fable 5: Why New AI Models Rarely Change Everything

## Overview

A live, unscripted testing session of Anthropic's newly released "Fable 5" model, conducted by Dex (CEO/co-founder of Human Layer) and Bibo (working on BAML programming language). The episode was an impromptu pivot from a planned observability topic to hands-on model evaluation.

---

## Context & Setup

- **Release timing:** Fable 5 dropped ~20 minutes before recording
- **Zero prep:** No benchmarks prepared in advance; fully ad hoc testing
- **Location:** Dex was at a YC conference in Cancun; Bibo was remote
- **Purpose:** Evaluate Fable 5 on real, hard problems the hosts were actively working on

---

## Testing Methodology

### Bibo's Approach: Hard Current Problems
- Give the model the hardest problem currently being worked on
- Have it regurgitate understanding back — looking for **leverage**, not just task completion
- Success criteria: coherent description + 1-2 key insights not previously considered
- If the model can solve something Opus couldn't after weeks, that's meaningful

### Dex's Approach: Old Solved Problems (Personal Benchmarks)
- Keep a collection of hard problems already solved (e.g., commits logged with prompts)
- Check out old git SHA, give model the prompt, see if it can one-shot
- Advantage: You know the answer key; you remember the pain of debugging
- Origin story: A race condition in Human Layer (Oct) involving Golang daemon → socket → Claude Code → MCP server → API → back through the chain — took a week to solve

### Key Evaluation Principles Discussed
- **Don't test on problems Opus already solves** — no signal on improvement
- **One-shot vs. loop:** Different evaluation types; a model that solves in hours what Opus couldn't in 6 weeks is significant
- **Switching products/evals to new model** is one way to benchmark
- **Old problems require context recall** — harder to judge if you don't remember details

---

## Test 1: Bibo's BAML Architecture Problem

### Problem Description
Building an observable programming language where:
- Code generates deterministic diagrams (change code → diagram changes)
- Runtime execution ties to visualization (flame graphs, etc.)
- **Constraints:**
  - Multi-threaded: 1,000+ threads simultaneously
  - Max 2% performance penalty for observability
  - <10 nanoseconds per event
  - Maximally correct, lossless data (every function call recorded)
  - Support diffing profiles between runs
  - Track all method calls including array.length, array.push, etc.

### Architecture Context
- Virtual/green threads in runtime
- Each green thread writes to OS-pinned data structure (lock-free)
- Single green thread per OS thread at any time (OS constraint)
- Consumer thread swaps data structures rapidly
- Minimal locking required

### Fable 5's Performance
**Process:**
- Took 3+ minutes initially, seemed slow
- Read files one at a time
- Encountered "auto mode" safety classifier error (tried to use Fable 5 for bash approval — not intended)
- Required prompt correction to disregard error

**Output:**
- Wrote a V2 design document
- Captured use cases, branch information, architecture correctly
- Identified flame graphs as data visualization option
- **Found genuinely new insights:**
  1. **Causality clock instead of wall time** — smart, correct
  2. **Per-step exec ring pointer** — exec is synchronous, thread cannot migrate OS threads mid-step; engine can resolve and lazily create TLS ring once per step, hand VM raw pointer → eliminates TLS from push path entirely, makes on-thread start hooks unnecessary
  3. **Tag context (u32)** — engine ID, back ID, tick base changes once per exec step; can store once and use u32 for uniqueness → reduces data written to memory
  4. **Found inconsistency in docs:** Gap 7 framed heap pointers as stable across yield — actually never was an option
  5. **Identified clock read issue:** Function start/end each carry timestamp = 2 clock reads per call pair = 20-30 ns minimum (40-60 ns total) — but team already knew this

**Assessment:**
- Only 2 real options: Either the team's docs are already excellent, or Fable isn't dramatically better than Opus
- Didn't wow — needed to read more to verify correctness
- Writing style still felt "AI-ish" (not robotic like Codex, but not human either)
- **Critical miss:** Didn't proactively identify that thread IDs must be **U64, not U32** despite the "thousands of threads" constraint being explicitly stated

### The U32 vs. U64 Thread ID Issue (Post-Test Analysis)
- U32 thread ID with 10,000 threads/sec → collision in ~5 days
- U32 with 1,000 threads/sec → collision in ~50 days
- U64 with 1 million threads/sec → collision in 585,000 years
- **This is the kind of subtle constraint-attention failure that matters**

---

## Test 2: Dex's Race Condition Problem

### Problem Description (Human Layer)
- UI ↔ daemon (REST/SSE)
- Daemon runs multiple Claude Code sessions
- Claude Code calls MCP server for approvals
- MCP server writes to socket → daemon → database → UI
- User approves/denies with feedback

### The Bug
- Claude Code includes tool call ID from upstream model provider when calling MCP
- This ID was not being passed through the flow
- Daemon had to guess which session an approval belonged to (multiple sessions possible)
- **Correct solution:** Map tool call ID into database for deterministic correlation (guaranteed unique across tool calls)

### Fable 5's Performance
- **Failed.** Added correlation but used a different key not guaranteed unique per tool call
- Did not pipe the tool call ID through
- Same result as previous models
- **Could not one-shot with a three-sentence prompt**

---

## Performance Observations

| Aspect      | Observation                                                  |
| ----------- | ------------------------------------------------------------ |
| Speed       | Dex found it slow (3+ min initial); Bibo found it fast (similar to Opus) |
| Thinking    | "Very thinky" — high effort mode                             |
| Tool calls  | Made many tool calls                                         |
| Variability | Speed may depend on internet/connection                      |

---

## Key Takeaways

### On Model Hype vs. Reality
- Model releases are generally **more hyped than the value they produce**
- Fable 5 is likely better than Opus — but not by an order of magnitude
- Improvement may be incremental (e.g., handling 15 constraints vs. 10) rather than breakthrough
- Even small improvements compound: cutting corrections from 5 to 2 per conversation doubles effectiveness

### On Constraint Handling
- Models struggle with attending to tens or hundreds of constraints simultaneously
- Humans must still handle many constraints the model misses
- The U32/U64 thread ID issue exemplifies this: model didn't proactively identify a critical constraint violation

### On Practical Utility
- Most people won't benefit from switching to Fable in real-time product pipelines due to latency
- UX redesign may be required to tolerate wait times
- Background/async tasks are more suitable
- Dex will switch to Fable anyway — if it handles one more constraint, that's leverage

### On Evaluation Strategy
- Hardest current problem (with full context) = best test
- Old solved problems (with answer key) = good supplement
- Don't test on problems already solved by previous models
- Keep personal mini-benchmarks of hard problems

### On Techniques
- Prompt corrections can work around model limitations (e.g., "disregard previous error")
- Model context window updates can prevent repeated mistakes
- Auto mode safety classifiers may not work with new models initially

---

## Verdict

| Speaker | Assessment                                                   |
| ------- | ------------------------------------------------------------ |
| Bibo    | Not wowed; model found some new things but failed to identify critical U32/U64 issue despite explicit constraints |
| Dex     | Fable failed his race condition benchmark (same as previous models); will still switch to Fable for incremental gains |
| Overall | Model releases rarely "change everything" — Fable is better, but not dramatically so; practical value is in marginal constraint-handling improvements |

---

## Miscellaneous Notes

- Fable 5 reportedly "beat Pokemon" (allegedly)
- Bibo was coding from Cancun at a YC conference
- The episode was originally planned to be about agent observability
- Bibo's BAML repo branch: `trim-events` (PR #206 or #409)
- Dex's benchmark: Human Layer race condition with approval correlation
- Mentioned: Jake Nations (ex-Netflix Cloud Code engineer) — understanding bad patterns from painful debugging
- The "Ralph loop" concept: If you leave a model in a loop for hours/days, it may solve what it can't one-shot
- Model writing styles: Codex = robotic, clearly not for humans; Claude = "AI-ish" but nice sentences