---
id: 00_prior_art_audit_compile_gate_agent_proof
title: "The staged-file compile gate is already invented: Agent-Proof's Stage 2 (part 1/2)"
source: web: github.com/Heretek-AI/Agent-Proof README (full read, 2026-09-16)
date: 2026-09-16
tags: ["agentic", "agents", "verification", "gates", "prior-art", "compile", "pre-commit", "tooling"]
provenance: primary — full README of Heretek-AI/Agent-Proof read directly via GitHub fetch
---

# The staged-file compile gate is already invented: Agent-Proof's Stage 2

## Claim

A deterministic gate that compiles/lints every staged file at `git commit` is not a
novel mechanism. `Heretek-AI/Agent-Proof` (TypeScript, MIT) implements it as its
Stage 2 "Hard Git Gate", with the same boundary, the same enforcement model, and a
strictly wider scope.

## The correspondence

| Property | This workspace's `check_python_compiles.py` | Agent-Proof Stage 2 |
|---|---|---|
| Boundary | `git commit` | `git commit` |
| Scope | staged `.py` files only | staged blobs, `--staged` |
| Latency target | none asserted | `< 2.0s` SLA |
| Enforcement | deterministic, mechanical | deterministic, mechanical |
| Position in pipeline | commit-time only | Stage 1 edit-time + Stage 2 commit + Stage 3 CI |

Both exist for the same stated reason: prompt-based guardrails (`CLAUDE.md`,
`.cursorrules`, system prompts) "inevitably degrade under context saturation and
complex multi-file refactoring tasks", so correctness must be enforced by
*deterministic mechanical* checks rather than prose rules. This workspace reached the
same conclusion independently and produced a strict subset of the mechanism.

## The gap the comparison exposes

Agent-Proof has a **Stage 1** running at `PostFileEdit` with a `<50ms` SLA on a single
modified file. This workspace has **no gate at the edit-time position at all** — and
edit-time is exactly where class-2/class-3 edit errors originate. Repositioning the
existing gate earlier is a real, unbuilt improvement; the gate itself is not.

It also already implements the failure-loop idea as a mechanism: **`LoopBreaker`**
hard-trips `FAILURE_LOOP_HALT` after `>= 3` consecutive identical failures. This
workspace's failure-ledger recurrence problem (27% of live entries are recurrences of
scarred trap classes) is solved there as a halt, not measured as a rate.

## Caveat

1 star, single-author org. Read for *architecture*, not for adoption or maturity.
The claim is about prior existence of the mechanism, not about production reliability.

## Delta

Zero for the gate. The only transferable thing is the Stage-1 edit-time position.
