---
type: Concept
title: grounded_tool_reliability_failure_modes_web_research
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

# Grounded Tool-Use Reliability and Failure Modes

## Core concepts

Tool use is reliable only when the tool's output is the direct evidence for the next decision, not paraphrased, summarized, or selectively filtered by the agent. Reliability failure modes follow a pattern: tool selected for the wrong failure mode, tool output ignored, tool output paraphrased and thereby distorted, or tool unavailable and the loop silently collapses to intrinsic self-correction.

## Evidence from web sources

- CRITIC ablation (2305.11738): removing the external tool collapses performance to intrinsic self-correction and sometimes below baseline. Measured delta: +7.7 F1 with tools, sometimes negative without. The mechanism is not tool quality but tool presence.
- Self-Debug (2304.05128): +12% where unit tests exist, +2-3% where no verifier exists. Same agent, same capability, different tooling. The 4x gap is explained by Huang et al.'s intrinsic self-correction failure mode.
- ToolBench and API integration studies show that hallucinated tool parameters and silent fallback behavior are the dominant reliability risks. Hallucinated parameters mean the agent issues syntactically plausible but semantically wrong calls; silent fallback means the tool call returns an error the agent treats as success.
- Agent harness design guidelines recommend: type-safe tool schemas, output capture that is concatenated not paraphrased, explicit failure states, and a "no tool" branch that is opt-in not silent default.

## Why it matters for this workspace

The ICM pipeline already gates tool-driven steps with scripts (`check_manifest`, `watch --once`, `check_reflection`), but these are coarse. Adding per-step output capture with provenance and explicit failure escalation would prevent silent degradation when a tool is unavailable or returns noise.

## Source

Web research: CRITIC, Self-Debug, ToolBench, agent harness reliability.
