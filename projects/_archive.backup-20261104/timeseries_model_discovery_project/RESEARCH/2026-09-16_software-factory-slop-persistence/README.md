---
type: Concept
id: 2026-09-16_software-factory-slop-persistence
date: 2026-09-16
scenario: S4
surface: agentic software factories — spec→software mapping, slop, chaos, agent persistence, aiming/tuning
status: done
supersedes: none
title: README
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Research: Software Factories — Aiming, Slop, Chaos, and Agent Persistence

Source item: `projects/workspace-research/INBOX/software_factory.txt`, a video transcript
("Systems Building Systems"). The transcript's thesis is that a software factory is a mapping from
spec-like inputs to shipped software; the machinery is easy to build and *aiming* at the tiny
desirable subset of outputs is the hard, slow, expensive part. Everything outside that subset is
slop. Four of its claims were checkable against primary literature; all four were confirmed or
sharpened, and two had named mechanisms the transcript only asserted. See `findings.md`.

## Headline findings

1. **The concept is live and named.** "Software factory" is the vendor term for exactly the
   transcript's mapping, framed as a closed feedback loop (signals → triage → build/test/review/
   secure/ship/monitor → more signals). Factory.ai, 2026-06-15.
2. **The slop claim is empirically settled** as a *tragedy of the commons*, not a code-quality
   quibble — 1,154 posts, 15 codes, three clusters. arXiv 2603.27249.
3. **The chaos claim is no longer speculation.** Jacobian analysis finds Transformer sub-blocks
   exhibit sensitivity to initial conditions with bounded, intermittently divergent trajectories
   (arXiv 2607.27805). Empirically, one trailing space flips a generation's shape (drose.io).
4. **The persistence claim is the best-supported and it inverts the transcript's second idea.**
   Summarization is lossy in *unpredictable* ways and the retained knowledge is *unpredictable
   across runs* (arXiv 2605.23296). The transcript's "babysitter the agent never sees" already
   exists as a named failure class — layers that manage context beneath the agent — and the
   repair is the opposite: expose the runtime state *to* the agent (arXiv 2606.30005, VISTA).

## Route

Row R-09 added to `RESEARCH/CONTEXT.md` §"Deterministic routing" in this session. Topic matched
no prior row at the 3-of-N threshold (best was R-03 at 1 token, `slop`), so this is route outcome
3 (new record), not a reopen.

## Status

- done — `findings.md` cites every claim; `references.md` lists all 9 sources with access dates;
  `open_questions.md` records the 4 that could not be closed and why.
