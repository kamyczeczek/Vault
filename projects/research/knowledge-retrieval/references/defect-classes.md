---
type: Concept
title: defect-classes
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:26Z }
---

# Defect classes

Every way retrieval has been found to be wrong, with the gate that now catches it.
Read this before designing a new gate — the useful question is always "which of
these shapes is this, and which assertion would have caught it?"

## 1. Extraction damage — intra-word whitespace loss

**What it looks like.** `Sys tem` instead of `System`, `man-monthmythical` as one
token. FTS5 indexes the first as two terms and the second as one.

**Why the first detector missed it.** The original heuristic fired on CamelCase
run-ons, which caught real identifiers (`basePrice`, `daysOverdrawn`), and on rare
vocabulary, which flagged ordinary technical terms in a 4.5M-word corpus. It
reported 6,401 defects; the true count was 419. **Over-reporting is its own defect
class** — a gate nobody trusts is a gate nobody runs.

**The discriminating signal.** A long *all-lowercase* run with no camelCase
boundary, no hyphen, no underscore. `MIN_GLUE_LEN = 32`; the longest credible
English token is 28.

**Measured effect.** 428 damaged chunks → 2. 1,784 glue tokens → 3.
`mean_family_precision` 0.652 → 0.746.

**Gate.** `check_corpus_health.py`.

## 2. Front matter ingested as content

**What it looks like.** 6 of 8 gold chunks are a copyright page, an "ALSO BY"
listing, or a publisher title block.

**Why it survives.** It is text. It is cleanly extracted. Nothing marks it.

**Gate.** Annotation-time: a gold chunk must contain its required concepts, and
only `Chunk id:` lines count as load-bearing evidence.

## 3. Fabricated tags

**What it looks like.** A tag that no source supports creates an FTS hit for a
query nobody can justify.

**Gate.** `check_tag_hygiene.py`.

## 4. Citations that resolve to the wrong text

**What it looks like.** Chunk ids are `NN_<slug of filename>`, so re-ingest reuses
the id for entirely new text. An id that resolves proves nothing about *what* it
resolves to.

**Gate.** `check_citation_integrity.py` — every gold must exist **and** contain
every required concept.

## 5. Non-determinism in graph construction

**What it looks like.** The same corpus produces a different graph each run. The
fingerprint cannot see it: any self-consistent graph satisfies the hash.

**Gate.** `check_graph_determinism.py` — build twice, diff with order imposed by
the query, then **restore the original DB** so the check never mutates what it
verifies.

## 6. Local assertions passing through relational failure

**What it looks like.** 18 gates existed; 15 passed continuously through all six
defects. 6 of 8 mapped defects had no gate; the 2 that had a partial one were
caught by a human reading the output, not by a non-zero exit.

**The shape.** Each gate asserted a *local* property — the manifest traces the
corpus, the fingerprint matches — while every failure was *relational*: does this
claim's evidence support this claim, does this id mean this text.

**Gate for gates.** `check_wiring.py` asserts claimed integrations are callable.
The durable lesson: **a gate ships the bug it prevents.** Both new gates were
written after the defect that motivated them, and both shipped with a regression
test.
