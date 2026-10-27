---
type: Concept
title: GATES
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# Map: integrate-unlazy-gate-first

OWNS: scripts/quality_check.py, templates/gates.md, CONTEXT.md, stages/00_meta/CONTEXT.md

## Destination

Prove that unlazy's gate-first discipline and abandonment protocol are operational in this workspace.

## Notes

This map adopts wayfinder decision-ticket framing: each gate is a question whose resolution is a decision, not a build step to execute. Research subagents may resolve `research` tickets in parallel; all others are one-per-session.

## Decisions so far

<!-- one line per closed ticket, gist + link -->

- (none yet)

## Not yet specified

- Whether to adopt wayfinder tracker integration (GitHub issues) for future multi-session work
- Whether to add fog-of-war graduation ceremony to CONTEXT.md

## Out of scope

- Production code changes unrelated to gate-first discipline
- Hook/script layer adoption (deferred to Planning with Files integration)

## Leaf tickets

- [ ] G1: Does the gates template support decision framing?
  - Type: research
  - Question: Can `templates/gates.md` express gates as decision tickets with fog/frontier sections?
  - Evidence: templates/gates.md contains "Decisions so far" and "Fog of war"

- [ ] G2: Is the abandonment protocol documented?
  - Type: grilling
  - Question: Does CONTEXT.md describe silent abandonment as cargo-cult completion?
  - Evidence: grep "Silent abandonment" CONTEXT.md

- [ ] G3: Does quality_check.py record per-gate evidence?
  - Type: research
  - Question: Can `--json` output prove each gate's evidence with fingerprints?
  - Evidence: .unlazy/evidence/latest.json contains per-gate fingerprints

- [ ] G4: Is there a meta rule for gate-first discipline?
  - Type: grilling
  - Question: Does stages/00_meta/CONTEXT.md require gates before implementation?
  - Evidence: grep "Gate-First Discipline" stages/00_meta/CONTEXT.md

- [ ] G5: Does the full quality suite pass?
  - Type: task
  - Question: Does `python scripts/quality_check.py` report QUALITY PASS with new gates?
  - Evidence: terminal output "QUALITY PASS: 11/11"

## Integration gates

- [ ] N1: All leaf gates met with evidence
  - Type: task
  - Question: Does `.unlazy/integrate-unlazy-gate-first/evidence.json` prove all leaf gates passed?
  - Evidence: file exists with all gates marked passed

- [ ] N2: Abandonment protocol end-to-end
  - Type: research
  - Question: Can the abandonment parser handle the documented format?
  - Evidence: import succeeds and parse_abandon returns expected tuple

## VERA Phase 1 (live project — full gates in subprojects/vera/gates.md)

- [ ] VERA-1: VERA Phase 1 green
  - Type: task
  - Question: Are benchmark seeds annotated (V1), baseline deterministic with logged run (V2), scorecard + claim schema operational (V3–V4), and injection test spec frozen (V5)?
  - Evidence: subprojects/vera/progress.md entry "VERA Phase 1 complete" with run directory path

## Abandonment protocol

ABANDON: <id> <non-empty reason> — handoff recorded in CONTEXT.md or issue tracker
