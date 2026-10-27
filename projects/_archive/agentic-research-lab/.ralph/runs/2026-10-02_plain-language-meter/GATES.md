# Gates: plain-language-meter

GATES: listed below

OWNS: .ralph/runs/2026-10-02_plain-language-meter/, docs/research/plain-language-meter.md, scripts/plain_language_meter.py, tests/test_plain_language_meter.py, scripts/build_plain_language_eval_set.py, tests/test_plain_language_eval_set.py, knowledge/eval_sets/plain_language_v1.json

Scope: D-001 meter picked + D-002 comparison design written to docs/research/plain-language-meter.md + D-004 production eval-set seed v1

- [x] G1: design doc exists with all required sections (meter, mechanism candidates, eval protocol, verdict rule)
  CHECK: python scripts/_scratch/verify_design_doc.py docs/research/plain-language-meter.md
  EXPECT: "design doc sections: all present"
  EVIDENCE: 2026-10-03 re-run green. `verify_design_doc.py` asserts four required `## <section>` headings (case-folded); all four present in the design doc.

- [x] G2: meter harness skeleton runs — scoring a fixture text returns a rubric dict and comprehension items are generated from source
  CHECK: python -m pytest tests/test_plain_language_meter.py -q
  EXPECT: "passed"
  EVIDENCE: 2026-10-03 re-run: 4 passed (source-derived items with known answers; fixture comprehension 1.0 + 4-key rubric; empty input rejected; mismatched responses fail closed).

- [ ] G3: end-to-end research task spot check (manual): run a realistic task through research -> ingest -> graph retrieval -> reflection -> implementation of the resulting knowledge; human verifies the final implementation is grounded in retrieved evidence and the workflow artifact trail is complete
  REQUIRED EVIDENCE: task question; source identifier and ingest result; graph query plus retrieved chunk ids; reflection artifact with claim-to-source links; implementation diff or output; final test/verification result; human groundedness verdict
  EVIDENCE: pending (human-owned). Second goose run artifacts present: fresh `knowledge/raw/decision_graphs_ai_agents_debugging_web_research.md` + `cleverthis_adr007_decision_tree_correction.md`, `reflection/digests/decision_graphs_workflow.md` (fingerprint 31989e46d0a5), grounded-review-gate diff in `pipeline/06_reflect/reflect.py`, `tests/test_reflect_grounding.py` 2/2 green (`--basetemp .pytest_tmp`). Human groundedness verdict outstanding.

- [ ] G4: eval-set builder runs clean on seed v1 and emits a fingerprinted, stratified, oracle-first set
  CHECK: python scripts/build_plain_language_eval_set.py knowledge/eval_sets/plain_language_v1.json --passages docs/research/trustworthy-agent-tests.md docs/research/plain-language-meter.md docs/research/forge-guardrails-ab.md --min-items 5 && python -m pytest tests/test_plain_language_eval_set.py -q --basetemp .pytest_tmp
  EXPECT: "3 passages written + 8 passed"
  EVIDENCE: pending

<!-- Keep every gate honest. Do not remove an impossible gate; use ABANDON with a reason and handoff.
     Declaring `GATES: none` also means deleting every placeholder checkbox above, or the controller will count them as unmet. -->
