---
type: Concept
title: 0002-gate-unbuildable-chunks
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Gate on unbuildable chunks, not on file count or derived ratio

`knowledge/corpus/` holds 10,337 chunks cut from 154 raw sources, and 6,544 of
them (63%) have a source that exists nowhere — not on disk, not in git, not
recoverable. For those documents a chunk is the only surviving copy, so the
first response to "too much entropy here" is also the one that destroys the
most. `scripts/check_entropy.py` fails on the unbuildable count, which is the
one signal that cannot be satisfied by deleting the evidence.

## Considered Options

- **Gate on file count or a derived:source ratio.** Rejected: both are
  satisfied by deleting chunks, and deleting chunks is exactly what must not
  happen. A ratio of 21:1 looks no better after a purge that removed half the
  corpus and all of its provenance.
- **Gate on untracked-file count.** Rejected: it fires on the 16 PDFs that are
  gitignored by policy and present on disk. Policy compliance reported as
  entropy trains you to ignore the gate.
- **Gate on unbuildable chunks (chosen).** It names the actual harm — a chunk
  that cannot be re-derived, verified, or repaired — and it is the only option
  that stays correct as the corpus is repaired.

## Consequences

The gate is a hard failure in `quality_check.py` (Q19), promoted from
`warn_exit=2` on 2026-09-28 when the count reached zero. It began at 6,544
unbuildable chunks across 23 sources; the 7 deleted PDFs were recovered from
git history, 8 books were filed into the workspace `library/`, and *Graph
Engineering* resolved through a filename alias after being supplied in a
different format.

Reporting is per source, not per chunk: 1,123 unbuildable chunks from one book
is one problem to fix, not 1,123. A per-chunk report would bury the seven
sources that account for 76% of the damage under 6,544 lines.

The final 11 chunks across 7 sources were not losses at all, and calling them
losses made the gate unsatisfiable. They were hand-written chunks: three cite a
topic label with no file, and four cite project write-ups whose subject was
archived. `benchmark-core` archived `LassoLagHybrid` on 2026-09-24 with "no
wins recorded", which means the write-up is the only surviving account of why
it failed — clearing the count by deleting those chunks would have destroyed
the research. The gate now separates authored sources from derived ones and
reports the former as a note.

Deleting an unbuildable chunk lowers the count while leaving the source lost,
so the number alone can be improved by making the loss permanent. The gate
cannot prevent that; `tests/test_check_entropy.py` asserts that a genuinely
missing document is still classified as a loss, so the split cannot be used to
excuse a real one.
