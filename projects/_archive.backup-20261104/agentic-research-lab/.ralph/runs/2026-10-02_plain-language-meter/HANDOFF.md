---
updated: 2026-10-02T11:35:00+00:00
---

# Handoff — plain-language-meter

## State

READY, iteration 1 pending record; D-001 RESOLVED (meter picked); frontier D-002.

## Next-session reads (in order, target ≤ 8K tokens)

1. `python skills/ralph-loop/scripts/ralph.py --project . resume`
2. `.ralph/runs/2026-10-02_plain-language-meter/decisions/D-002.md`
3. `.ralph/runs/2026-10-02_plain-language-meter/GATES.md`

## What the last iteration did

I-001: resolved D-001 — two-tier meter (held-out lay-reader comprehension
task primary; G-Eval-style rubric proxy; FactPICO-style faithfulness as
safety counter-metric; surface indices rejected as primary). Evidence:
six `00_web_*` chunks read; the key facts are logged in
`decisions/D-001.md` §Context.

## Open questions and blockers

- G1/G2 reference `scripts/_scratch/verify_design_doc.py` and
  `tests/test_plain_language_meter.py`, which do not exist yet — both are
  D-002 work items, not defects.
- G3 (human spot-check of proxy validity) is manual; flag to the user at
  verdict time.

## Next action

D-002: write the comparison design to
`docs/research/plain-language-meter.md` (meter, three mechanism candidates,
eval protocol, verdict rule) and add the meter harness skeleton + tests
so G1/G2 become checkable.

## Suggested skills

none beyond this run's contract.

## Learnings to promote

LEARNINGS.md I-001: "surface readability metrics are not a meter" —
corpus-backed, worth the project CONTEXT.md at DONE.
