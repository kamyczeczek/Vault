# Gates: trustworthy-agent-tests

GATES: listed below

OWNS: docs/research/trustworthy-agent-tests.md (new); .ralph/runs/2026-10-01_trustworthy-agent-tests/** (run artifacts)

Scope: dokument research: docs/research/trustworthy-agent-tests.md z >=5 zewnętrznymi źródłami primary i kryteriami do wdrożenia

- [x] G1: research doc exists at docs/research/trustworthy-agent-tests.md and cites >= 5 distinct external primary-source URLs
  CHECK: python .ralph\runs\2026-10-01_trustworthy-agent-tests\checks\g1_doc.py   (run from the project root)
  EXPECT: G1 OK
  EVIDENCE: I-001 (2026-10-01): CHECK exit=0, "G1 OK: docs\research\trustworthy-agent-tests.md cites 11 distinct external source URLs". Doc created with 11 reachable (HTTP 200) primary-source URLs; outline (1)-(3) covered.

- [x] G2: human review — a person has read the doc and marks this gate with a dated one-line verdict [2026-10-02: verdict APPROVED by run owner — doc sources and outline are sound; sufficient to close]
  EVIDENCE: pending (manual)

<!-- Keep every gate honest. Do not remove an impossible gate; use ABANDON with a reason and handoff.
     Declaring `GATES: none` also means deleting every placeholder checkbox above, or the controller will count them as unmet. -->
