---
type: Concept
title: C7_graph_integrity_reflection
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# C-7 — Keeping the knowledge graph honest: what actually prevents defects

Date: 2026-09-26
Method: `graph_decision.py` returned `required: true`; findings read from
`00_graph_database_architectural_reflection` (the workspace's own prior reflection on
this question) and checked against the defect record of C-1 through C-6.
Status: proposal. Three of the five items below are implemented; two are deliberately not.

## The finding that reframes the question

The workspace already had an answer to this question, ingested as
`00_graph_database_architectural_reflection`. It proposed three improvements:
`REFERS_TO` citation edges, hybrid FTS5+embedding search, and incremental rebuild.

**All three are the wrong response to the failures that actually occurred.** In three days
(C-1 … C-6) the graph was broken six ways, and not one of them was a capability gap:

| # | defect | capability that would have prevented it |
|---|---|---|
| 1 | tags were indexed in FTS, fabricating 424 hits for words absent from all text | none — this is a *correctness* bug |
| 2 | the corpus-health detector counted 6,401 damaged chunks when 419 were | none — a *measurement* bug |
| 3 | 6 of 8 benchmark golds were title pages | none — an *annotation* bug |
| 4 | single-gold annotation scored correct answers as false positives | none — an *annotation* bug |
| 5 | `--dry` deleted 369 live corpus chunks | none — a *side-effect* bug |
| 6 | chunk ids were reused across re-ingestion, silently invalidating 4 citations | `REFERS_TO` edges would have *surfaced* it |

The prior reflection optimised the graph's *reach*. Every defect was the graph asserting
something false about itself. `REFERS_TO` edges, embeddings, and incremental rebuild all
make a graph more capable while leaving it exactly as able to lie.

**So the answer to "how do we stop the graph running into problems" is not a better graph.
It is a graph that cannot make a claim without something independent checking it.**

## What 15/15 passing gates missed

The workspace has 18 `check_*.py` gates. All 15 in the suite passed continuously through
C-1 … C-6. Mapping each defect against the gate that should have caught it:

| defect | gate | caught it? |
|---|---|---|
| tags in FTS fabricating hits | `check_corpus_health` | no |
| detector false positives (6,401 vs 419) | `check_corpus_health` | partial |
| golds were title pages | none | **no** |
| single-gold under-crediting | none | **no** |
| chunk ids reused across re-ingest | `check_manifest` | **no** |
| `--dry` destroyed 369 files | `check_manifest` | **no** |
| re-stamp corrupted JSONL layout | `check_reflection` | **no** |
| digest cited a never-ingested paper | `check_reflection` | **no** |

Six of eight had no gate at all. The two with a partial gate were caught by *me printing
the output and reading it*, not by the gate exiting non-zero.

The common shape: every one of these was a claim about the world that no other component
was in a position to contradict.

## The four properties worth protecting

### 1. Derived state is a pure function of sources — and provably so

`graph.db` already claims this (`.graph_fingerprint`), and `check_reflection` verifies the
stamp. That worked: the fingerprint is what made the C-6 repair auditable, and it is what
flagged ten artifacts for re-stamping.

**Strengthen with a rebuild-equivalence check.** Build the graph twice from the same corpus
into two databases and assert the content is byte-identical modulo the fingerprint. This
catches non-determinism — set iteration order, dict ordering, timestamp leaks — which is
the one class of graph bug that a fingerprint check *cannot* see, because it is
self-consistent by construction.

### 2. Every citation resolves, and resolves to the *same content*

This is the gap that cost the most today. `NN_<slug>` ids derive from the filename, so
re-ingesting a book regenerates identical ids pointing at different text. Four benchmark
golds silently drifted and I only found it because I happened to re-check their concepts.

`restamp_provenance.py` already verifies cited ids exist before re-stamping. That check
belongs in a permanent gate over *all* consumers — benchmark golds, digests, candidates,
memory — not inside a repair tool.

**Make ids content-addressed**, or store a per-chunk content hash alongside the id and
verify it on every read. A citation to a chunk whose text changed is a different citation,
and nothing in the current schema can express that.

### 3. The measurement instrument is itself measured

Two of the six defects were measurement bugs, and both produced confident, wrong numbers:
6,401 damaged chunks (actually 419), and family precision 0.46 reported as "half of
returned chunks come from the wrong book" (actually a correct answer, wrongly scored).

**Pin the detectors with fixtures that must not fire**, and assert the false-positive rate.
`tests/test_corpus_health.py` now does this for camelCase and long technical identifiers.
The general rule: a detector that has never been shown a clean document is not a detector,
it is a pattern matcher.

### 4. Side-effecting operations are reversible and prove it

`--dry` deleted 369 files. The bug was structural, not careless: dry mode wrote everything,
then deleted by *recomputing* the ids it had just written, with a different truncation
length. Any cleanup that recomputes what it just wrote is a second write.

**Test `--dry` by asserting the corpus is byte-identical before and after.** Not "the exit
code is 0" — the exit code was 0 while it destroyed a third of a book.

## Implemented now

- **C-6** — `check_corpus_health.py` now fires on structural lowercase glue only
  (`MIN_GLUE_LEN = 32`), with fixtures pinning camelCase, acronyms, and long identifiers as
  clean. Detector blind spot at capital-letter boundaries closed.
- **C-6** — `restamp_provenance.py` refuses to re-stamp a file whose cited evidence chunks
  have vanished, and preserves each file's existing layout.
- **C-6** — `tests/test_pdf_extraction.py` includes an end-to-end assertion that
  normalisation cannot mask the defect it exists to fix.

## Deliberately not implemented

- **Hybrid FTS5 + embeddings.** The prior reflection's recommendation. Measured, all four
  retriever levers (synonym aliases, family double-slots, fetch depth 8→40, 8→200) returned
  byte-identical scores, and `mean_family_recall` is 0.958. Semantic search is the right
  answer to "I don't know the word the book used" — which was measured as worth 0.0 on this
  corpus. Not now.
- **Incremental rebuild.** `build_graph.py` rebuilds 10,337 chunks deterministically. It
  takes long enough to notice and short enough not to matter. Incremental rebuild is a
  classic source of divergence between the incremental result and a full rebuild — i.e. it
  would *violate* property 1, the one thing that must not break.
- **`REFERS_TO` citation edges.** Worth having for traversal, and it would have surfaced
  defect 6. Not a correctness fix, so it does not go in before properties 1–4 hold.

## The transferable rule

> A gate must be able to fail on the thing it claims to check, and the failure must be
> reachable by an ordinary mistake.

Every defect above got past 15 gates because each gate asserted a *local* property
("the manifest traces the corpus", "the fingerprint matches") while the failure was
*relational* ("the manifest traces the corpus", **and** nothing drifted, **and** ids did
not shift, **and** the detector is not lying to you). Local assertions compose badly into
trust. The next gate worth writing is the one that asks whether the graph is telling the
truth about a *question*, not whether its tables are internally consistent.
