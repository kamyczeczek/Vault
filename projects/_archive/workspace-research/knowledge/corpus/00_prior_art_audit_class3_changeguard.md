---
id: 00_prior_art_audit_class3_changeguard
title: "Class-3 silent semantic breakage is detectable — ChangeGuard proves it (part 2/2)"
source: web: software-lab.org/publications/fse2025_ChangeGuard.pdf (Gröninger/Souza/Pradel, FSE 2025)
date: 2026-09-16
tags: ["agentic", "agents", "verification", "semantic", "prior-art", "refactoring", "testing", "measurement"]
provenance: primary — ChangeGuard, Proc. ACM Softw. Eng. 2, FSE, Article FSE043 (July 2025), Gröninger/Souza/Pradel; read abstract through RQ1
---

# Class-3 silent semantic breakage is detectable — ChangeGuard proves it

## Claim

The failure class this workspace named "class 3" — an edit that parses cleanly but
silently changes behavior, e.g. a dropped line — is not merely assertable as an
invariant. It is *mechanically detectable*, at measured precision and recall, by
existing published work.

## The mechanism

**Pairwise learning-guided execution.** Given a change from `f_old` to `f_new`, both
versions are executed side-by-side in isolation while a fine-tuned CodeT5 model
predicts and injects any values that would otherwise cause a crash. The two
executions' behavior is then compared on four axes: argument/return values, console
output, sequence of external function calls, and exceptional behavior. Repeat up to
k=300 executions to cover different paths.

## The numbers that matter

- **precision 77.1%, recall 69.5%** on 224 manually-annotated code changes.
- **Regression-test recall: 7.6%.** Existing project test suites **miss 92.4%** of
  semantics-changing changes.
- Changed-code coverage lifted from 27% to 92% by the value-injection improvements.
- Runtime: seconds per change.

## Why this inverts the naive mitigation

The instinct "just run the tests" is not a sufficient fix for class 3. Measured:
regression suites catch fewer than 1 in 12 semantics-changing edits. ChangeGuard's
motivating example is a scrapy commit whose message says "Simplify retry_times
assignment statement" — a line-level simplification that silently changes behavior on
one input. The developers caught it days later, manually.

## Cost and the honest gap

ChangeGuard needs a fine-tuned neural model plus per-change pairwise execution. That
is far too heavy for an every-commit gate, let alone an every-edit one. So the space
between "cheap but non-mechanical" (this workspace's current invariant: *edited
Python is executed before the session yields*) and "mechanical but heavy"
(ChangeGuard) is **unfilled**. A cheap proxy or a triage-then-validate hybrid is the
open question (research Q3).

## Delta

This workspace's class-3 invariant is a weaker, non-mechanical shadow of a mechanism
that already exists at 77/70 precision/recall. What is genuinely open is making it
cheap enough to sit in the gate suite, not inventing the detection.
