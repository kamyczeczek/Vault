---
type: Concept
title: open_questions
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Open Questions — Antifragile Workspace Design

<!-- Each question states what could not be resolved and WHY
     (missing access, conflicting sources, out of scope). -->

1. **Can the scar model stay audit-safe under a merge/prune
   discipline? (R1 gap)** CONFLICT-5's resolution direction
   (digest-budget-driven merging of superseded scars) is sound in
   principle, but merging changes what future sessions see without
   changing the source reflections — the merged form must remain
   byte-faithful to the invariant it enforces. Unresolvable here:
   this is a design decision requiring an S5 round with red-path
   validation of the merge mechanism itself. Out of research scope
   (implementation territory).

2. **Is DREAMTEAM's typed-slot failure routing transferable beyond
   games?** A3/A6 describe six role surfaces for ARC-AGI-3's
   executable world model. This workspace's surfaces (problem
   files, owning docs, gates) are coarser-grained. Whether the
   interface-level attribution (prediction emitted by one named
   interface) would improve THIS workspace's credit assignment is
   untested — our failures are already named at capture (ledger
   entry carries the failing command), so the marginal gain is
   unknown. Conflicting evidence absent; empirical question for a
   future S1 prototype.

3. **Do Memento/SkillOpt gains survive without benchmarks?** Both
   B3 and F2 are measured against well-defined evaluation suites.
   The workspace's "objective" is gate-green + no-recurrence, which
   is binary and local, not a scored generalization signal. Whether
   validation-gated skill/scars edits (F1's discipline) transfer to
   no-benchmark environments is precisely the antifragility
   question at workspace scale — this workspace's 9 validation
   rounds (zero defects found at round 7; one genuine recurrence
   caught at round 9) is suggestive evidence both ways: the loop
   catches real defects, and also generates its own residue.
   Unresolvable: needs a defined workspace-level metric (out of
   scope; candidate for a future S5 doctrine round).

4. **ICM_knowledge_big.md provenance.** The 935 KB merged-notes
   file duplicates the icm_brain corpus (verified by slice probes,
   2026-09-05 23:17Z). Which is the canonical upstream source (and
   its license terms for the G1–G3 expansions) is not stated inside
   the file. Missing access: the file's header says "Jake's
   content" without a canonical repo URL. Resolution: preserved in
   the record folder (sources/), question stays open until the user
   names the upstream.

5. **Atomic Agents' dispatcher economics at this workspace's
   scale.** C3/C4 are validated in production on a Mac Mini since
   Aug 2026 (per the doc). This workspace is single-agent by Rule 2
   (Single-Agent Invariant) with harness-managed concurrency. When
   (if ever) a card/board dispatcher would beat the current
   WORKFLOW.md classifier for THIS user's workload is unknown —
   the classifier's determinism already provides the antifragile
   properties. Out of scope: adopting Atomic Agents is an S1-level
   architecture decision requiring user intent.

6. **The 2026-03 ICM paper vs 2026-09 workspace state (CONFLICT-2
   dating).** The ICM paper's Table 1 concessions are empirical
   claims about ICM as of writing. Our refutation (error recovery/
   branching/concurrency now exist on the filesystem substrate) is
   about THIS workspace only — other ICM instantiations may still
   hit the original limits. Unresolvable without surveying other
   ICM deployments (missing access; out of scope).
