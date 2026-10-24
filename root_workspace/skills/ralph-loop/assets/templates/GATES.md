# Gates: <run name>

GATES: <"none" if this run truly has no observable outcome, else "listed below">

OWNS: <repository-relative paths>

Scope: <complete outcome for this run>

- [ ] G1: <observable outcome>
  CHECK: <approved command>
  EXPECT: <success-only marker>
  EVIDENCE: pending

- [ ] G2: <manual review outcome>
  EVIDENCE: pending

<!-- Keep every gate honest. Do not remove an impossible gate; use ABANDON with a reason and handoff.
     Declaring `GATES: none` also means deleting every placeholder checkbox above, or the controller will count them as unmet. -->
