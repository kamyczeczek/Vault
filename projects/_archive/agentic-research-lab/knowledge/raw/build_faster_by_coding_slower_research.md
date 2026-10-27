---
type: Concept
source: "AI that Works podcast / Masterclass — Dex (Human Layer) & Vibhav (BoundaryML): Build Faster by Coding Slower"
title: build_faster_by_coding_slower_research
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Research Report: Build Faster by Coding Slower

**Source Material Analysis:** "AI that Works" Podcast / Masterclass featuring **Dex** (Co-founder, Human Layer) and **Vibhav** (Co-founder, BAML / BoundaryML).

---

## Executive Summary

"Build Faster by Coding Slower" explores the frontier of **agentic engineering** and large-scale software development using LLM coding agents. Counter to the casual "vibe coding" trope where developers blindly prompt models and cross their fingers, advanced practitioners like Vibhav (building complex compiler features and programming language extensions in BAML) demonstrate that shipping massive, high-integrity codebases (such as 16,000+ line pull requests) requires **rigorous upfront design, deep architectural thinking, and structured multi-step workflows**.

This research report synthesizes the core philosophies, workflow mechanics, context management strategies, architectural design patterns (specifically for testing non-deterministic AI systems), and manufacturing principles discussed in the transcript.

---

## 1. Core Philosophy: The Myth of Fast Coding

* **Do Not Outsource the Thinking:** The most critical pitfall in agentic coding is letting the LLM make foundational architectural decisions. Models are naturally sycophantic; if a developer prompts sloppily or presents an idea as absolute truth, the model will follow it down a rabbit hole, compounding errors.
* **Brain Surgery on Design Docs:** Before writing a single line of implementation code, developers must use markdown design documents as an opportunity to perform "brain surgery" on the model's output—re-steering, evaluating options, and refining specifications.
* **The ROI of Upfront Slowness:** Spending 3 to 5 hours crafting a bulletproof specification and refined ticket (`Ticket 2`) saves weeks of painful debugging, architectural drift, and messy refactoring downstream.

---

## 2. The Multi-Step Agentic Workflow (RPI & Riptide)

Vibhav outlines a disciplined, repeatable pipeline for developing complex features with coding agents:

1. **Initial Ticket / PRD:** Groundwork establishing the high-level feature requirements and scope.
2. **Automated Research (`RPI` / Research Phase):** The agent indexes the codebase, answers research questions, and gathers relevant patterns.
3. **Design Discussion:** The model generates a comprehensive design document outlining multiple options and trade-offs. The human reviews, challenges assumptions, and eliminates ambiguity.
4. **Refined Ticket (`Ticket 2`):** Distilling the rigorous design discussion into a clean, actionable implementation ticket.
5. **Implementation & Snapshot Testing:** The agent generates the implementation. The developer inspects test outputs, serialization snapshots, and data models to catch edge-case bugs.
6. **The Nuclear Option (Restarting vs. Patching):** If a codebase implementation drifts >30% or accumulates foundational flaws due to a weak design, trying to patch it incrementally is inefficient. The optimal move is to kill the branch, refine the ticket, and restart from a clean slate.

---

## 3. Managing Context Windows & Long Context Models

The discussion touches on the trade-offs of modern million-token context windows versus structured summarization:

* **Vibhav's Approach (Extended Context):** Leaning into million-token contexts to maintain a continuous reasoning chain across long design discussions without manual compaction. The human remains actively engaged, holding long-term consistency in mind while relying on the model's recency bias for immediate steering.
* **Dex's Approach (Context Anxiety & Persistence):** Preferring unidirectional flows where every major decision is serialized to disk (docs/tickets) to guard against session loss or context degradation.
* **The "Dumb Zone":** Recognizing when cognitive fatigue or model drift sets in (e.g., late-night coding sessions where both human and model make looping errors) and knowing when to pause, sleep, and resume with fresh perspective.

---

## 4. Architecture & Testing for Non-Deterministic / Agentic Systems

A major portion of the discussion covers building a robust testing framework for **BAML** to support AI and agentic pipelines. Traditional static testing (`assert true/false`, `before-each`, `before-all`) is inadequate for non-deterministic systems.

### Key Criteria for AI / Agentic Testing:
1. **Scenario-Driven Testing:** Grouping tests into product-oriented scenarios (slices across multiple dimensions, e.g., handling specific user behaviors or input variations).
2. **Soft Metrics & Aggregation:** Moving away from binary assertions to **named check metrics** that collect data continuously without immediately crashing the test runner, allowing scenario-level aggregation and pass-rate thresholds.
3. **Dynamic Data Loading:** Pulling test cases dynamically from production logs or secure datasets rather than hardcoding static fixtures.
4. **Ergonomic Language Design:**
   * **No Magic Global Hooks:** Eliminating hidden setup/teardown functions like `beforeEach` or `beforeAll` (aligning with Rust and Go philosophies), making every test self-contained and inspectable.
   * **Custom Test Runners (Quorums):** Designing execution wrappers (e.g., a Quorum runner that executes a test $N$ times and requires $M$ passes to account for non-determinism).
   * **Parallel Execution & Semaphores:** Making parallel test execution the default for speed, while providing optional serialization constructs (semaphores) for tests that share state.

---

## 5. Factory & Production Line Theory in Software Engineering

Toward the end, the discussion draws inspiration from Eliyahu M. Goldratt’s classic management book, *The Goal*, applying manufacturing production line theory to software engineering:

* **The Bottleneck Fallacy:** Optimizing non-bottleneck stations (or micro-optimizing individual code components that aren't the primary constraint) is a waste of time and increases work-in-progress (WIP) inventory.
* **End-to-End Flow:** Focus engineering effort strictly on the system's bottleneck and optimizing the end-to-end cycle time from feature inception to production deployment.
* **Task Prioritization:** Maintain a strict primary focus rather than spreading attention across multiple parallel WIP tasks that increase cognitive load and cycle time.

---

## Conclusion

"Build Faster by Coding Slower" redefines what it means to be an AI-augmented software engineer. By replacing impulsive prompt engineering with rigorous upfront design discussions, structured specification refinement, and architectural frameworks built for non-determinism, developers can leverage coding agents to ship massive, production-grade systems with unprecedented velocity and zero slop.
