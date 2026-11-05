---
type: Concept
title: 2026-09-15_graph-identity-invariant-and-edge-deflation
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# Reflection — identity invariant + edge deflation; the index lied about what it indexed

Date: 2026-09-15
Project: projects/workspace-research
Trigger: T1 (a problem was hit and fixed), T2 (a rule was added), T3 (a guard was retro-fitted)

## Problem

Three defects in the graph layer, all silent, all found by testing the one thing the
pipeline claims to guarantee — that a chunk id is a stable, openable address.

**D1 — id/stem drift.** `ask.py` returns ids; `spawn_recursive.read_chunk_body()`
resolves them back to files by `p.stem`. Three chunks broke this chain: their
front-matter ids used underscores while their filenames used hyphens
(`planning_with_files_pattern` vs `planning-with-files-pattern.md`, and the two
`ai-planning-*` chunks). They resolved only via a linear corpus-wide fallback scan.
Worse, they were *cited* in this state — `planning_with_files_pattern` appears in
`workspace-health` evidence, `ai_planning_htn_pddl` four times in
`planning-research-workflow`. Every citation was an address that could not be opened
by the documented resolution path.

**D2 — 1.6M edges for 177k relationships.** `SHARES_TAG` emitted one row per
(shared tag) per pair, and tags carried numeric OCR residue (`1`, `2`, `1234`) plus
hex runs that collide with the 12-hex fingerprint namespace. Consequence: a single
node carried 4,527 edges; `spawn_recursive.py`'s ADAPT one-hop expansion — a
`SELECT dst FROM edges WHERE src IN (4 seeds)` — returned **15,190 rows** that
collapse to 594 distinct neighbors. 90.7% of all edges came from tags selecting >25%
of the corpus (7 tags on 529–594 of 596 nodes carry <0.2 bits each).

**D3 — the determinism gap D1's bet named was real.** `icm`+`determinism` co-tagged
exactly **1** chunk; the tag `determinism` sat on exactly 1 chunk while `icm` sat on
373. The pipeline's central claim — deterministic, replayable retrieval — was
undocumented in its own knowledge base.

## Root cause

The graph was built as a *cumulative* index, never audited as a *contract*.

- **D1:** chunks were hand-authored before `ingest.py`'s `write_chunk()` existed.
  That function already writes `id == filename stem` — the drift came from
  pre-ingester manual chunks, and nothing ever re-derived the invariant, because
  nothing checked it. `check_reflection.py` validates that a cited id *exists in
  graph.db*, not that it *resolves to a file*. Existence ≠ addressability. The gate
  was checking the wrong property, exactly the R1 failure mode from the prior record.
- **D2:** a complete-graph-per-tag emit with no discrimination threshold and no
  dedup. Nobody consumed the duplicated rows — the sole consumer
  (`spawn_recursive.py` line 129) `SELECT`s them and immediately collapses to a set.
  The index was paying 9.2× storage and query cost to carry information its only
  reader discarded.
- **D3:** no coverage probe. The corpus had 95 tags and 596 chunks but no check that
  a concept the architecture depends on was actually represented.

## Solution

1. **Realigned the 3 chunk ids** to their filename stems; rewrote the 6 affected
   citations across `reflection/digests/` and `reflection/candidates/`.
2. **`build_graph.parse_chunk()` now enforces the identity invariant at build time:**
   front-matter `id` must equal the filename stem, else `ValueError` naming the file.
   Drift now fails the build instead of rotting silently. Verified by negative
   control (a planted `id: WRONG_ID` is rejected with the file named).
3. **Edge deflation.** Junk tags (`^\d+$`, `^[a-f0-9]{8,}$`) are skipped in edge
   construction — but kept on `nodes.tags`, so exact-tag routing and `topics.md`
   stay byte-stable. Multi-edges deduped to one row per `(src,dst)` carrying the
   alphabetically-first shared tag (`sorted(tag_map.items())` keeps the choice
   deterministic). **1,638,327 → 177,304 edges (−89%)**, no duplicate pairs, and the
   ADAPT expansion query returns 2,364 rows instead of 15,190 for the same 594
   neighbors.
4. **D1 closed by derived chunk `icm-determinism-rule.md`** — a synthesis over five
   existing corpus chunks (`00_from_plan_to_action...`, `planning-with-files-pattern`,
   `00_hooks_board_events`, `12_is_progressive_disclosure...`), explicitly tagged
   `derived-rule` so its provenance is a *set of corpus ids*, not an external fetch.
   The `icm`+`determinism` intersection went 1 → 2.

## Verification

Negative controls, both directions:
- Junk tags remain on 370 **nodes** (`tags LIKE '%"1"%'` → 370) but appear in **0**
  edge rows — routing invariance proven, not asserted.
- All 5 probe queries (`planning+icm`, `determinism+icm`, `agents+agentic`,
  `reflection+memory`, `icm+derived-rule`) return identical pre/post id sequences.
- Planted bad id → build fails with a named file. Pre-fix corpus → build fails.
- Post-fix corpus → builds clean. Every cited id in every digest resolves to a
  corpus file; the 15 backtick tokens that didn't match are prose (dir names, schema
  keys, `plan_version`), verified not to be corpus ids or filenames.

Full gate suite green post-commit:
- `check_manifest.py` → PASS, 36 rows / 597 chunks / 0 staleness
- `watch.py --once` → `[watch] no change — graph fresh`
- `check_reflection.py` → `OK: checked 8 digests / 8 candidate files — all grounded.`
- `check_stage_contracts.py` → `OK: checked 4 stage contracts`
- `build_graph.py` → `fingerprint 17a3297a22fc nodes 597 edges 177900`

The P5 provenance gate **failed correctly** mid-work: adding the derived chunk moved
the corpus fingerprint, and all 16 stamped outputs were caught as stale
(`a77f6925b6c7 != live corpus 17a3297a22fc`) before re-stamping. The gate works.

## Prevention rules

- **R1 — existence is not addressability.** A gate that checks a cited id exists in
  `graph.db` does not verify it can be opened. Where an id is also a file address,
  the identity invariant must be enforced at build time, not at citation time —
  citation-time checks see the symptom after it has propagated into evidence.
- **R2 — a tag that selects everything selects nothing.** Any co-occurrence edge
  built from a tag should require the tag to discriminate. Non-discriminating tags
  produced 90.7% of the edges and zero information; the fix kept them on nodes
  (routing) while excluding them from edges (adjacency). Filtering at the edge layer,
  not the tag layer, preserved every existing query.
- **R3 — an index needs a coverage probe, not just a freshness probe.** Freshness
  (`watch.py`) proved the graph matched the corpus; it could not reveal that a concept
  the architecture depends on was represented once. The `icm+determinism` intersection
  of 1 was one query away for the entire life of the brain.
- **R4 — close a documentation gap with derived provenance, not invented content.**
  No external fetch was available; the gap was closed by synthesizing five existing
  corpus chunks and tagging it `derived-rule` so the manifest can trace it
  (`derived: synthesis over <ids>` became a 36th manifest row). This kept the
  corpus-is-the-only-source-of-truth invariant intact — the manifest gate initially
  FAILED on the new chunk and passed only after regeneration, which is the contract
  holding.
