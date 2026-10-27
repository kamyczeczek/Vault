---
type: Concept
title: C6_pdf_extraction_repair
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# C-6 — The corpus was never damaged. The extractor was.

Date: 2026-09-26
Supersedes: `C2_corpus_repair_triage.md` (its conclusion was wrong)
Preceded by: `C1_corpus_whitespace_defect.md`, `C4_retrieval_baseline.md`

## What C-2 got wrong

C-2 recovered the original *Design Patterns* and *Refactoring* PDFs from commit `3ff56137e97a`,
found that both pypdf and PyMuPDF produced identically glued text, and concluded:

> The principal corruption is in the source PDF text layer, not `ingest.py` or solely pypdf.
> Extractor swapping and re-extraction are therefore not sufficient repairs; cleaner source PDFs
> are required.

That conclusion was drawn from testing PyMuPDF's default `get_text("text")` and pypdf's default
`extract_text()` — **two different libraries, one extraction mode each.** It never tried
pypdf's `extraction_mode="layout"`. The conclusion "the bytes are damaged" followed from not
looking for the obvious alternative.

Measured on the two PDFs later placed in `INBOX`:

| mode | glue runs across 7 sampled pages, both books |
|---|---|
| pypdf `extract_text()` (default) | 31 |
| pypdf `extract_text(extraction_mode="layout")` | **0** |
| PyMuPDF `get_text("text")` | 0 |

The whitespace is in the PDF. The default mode discards the glyph positioning that encodes it
and re-joins the words. Nothing was ever lost at download time.

## The fix

`scripts/ingest.py` now selects the extraction mode **per page by measuring it**, rather than
hardcoding one:

```python
for kwargs in ({"extraction_mode": "layout"}, {}):
    text = page.extract_text(**kwargs) or ""
    glue = len(suspicious_runs(text))
    ...  # keep whichever page came out cleanest
```

The detector is imported from `check_corpus_health` rather than reimplemented, so the extractor
and the gate that judges it can never disagree about the threshold.

Layout mode introduces its own artifacts — 407 printed hyphenations (`Sys-\ntem/360`) and 28,923
padding runs across *Mythical Man-month* — so `_normalize_layout()` de-hyphenates across line
breaks, collapses padding, and strips per-line indentation. Without it FTS5 would index
`Sys tem` as two tokens and `man-monthmythical` as one, reintroducing the same defect in a
different shape.

## Two bugs found while doing this, both serious

**1. `--dry` destroyed the corpus.** The first dry run against *The Book of Why* deleted 369
live corpus chunks. `ingest_file(dry=True)` wrote every chunk, then tried to clean up by
recomputing the ids it had just written — using `slugify(name, 55)` while `write_chunk` had used
`slugify(name)`. The new id truncated to the same 48 characters as the old one, so the preview
overwrote a live file and then unlinked it. Restored with `git checkout -- knowledge/corpus/`;
manifest re-verified at 10,364 files. Fixed by extracting `chunk_id()` as the single definition
of an id, and by making `--dry` extract-and-split only, never write.

**2. Chunk ids are reused across re-ingestion.** `NN_<slug>` is derived from the filename, so
re-ingesting a book regenerates the *same* ids pointing at *different text*. Four benchmark golds
silently drifted to new content after the repair. Any id in this corpus is therefore a reference
to content, not to a position, and must be re-validated after any re-ingest. Four drifted
alternates were dropped; each affected case retains a valid primary gold.

## Result

| | before | after |
|---|---|---|
| damaged chunks | 428 | **2** (0.0%) |
| glue tokens | 1,784 | 3 |
| *Book of Why* | 319/386 damaged | 0 |
| *Mythical Man-month* | 98/103 damaged | 0 |
| corpus fingerprint | `44172cafee34` | `0a5b47437367` |
| mean_family_precision | 0.652 | 0.746 |

The 2 remaining chunks (1 in *Paradigms of AI Programming*, 1 in *AIMA*, 3 glue tokens) are
below the detector's own reporting threshold of significance and are left in place; the
corpus-health gate reports FAIL at 0.0% by design, since a clean bill of health should mean
exactly zero.

Retrieval check: the glued strings `ofthe`, `causalinferenceengine`, and `describedinthe` now
return 0 FTS hits, and *"what is a causal intervention and a counterfactual"* returns a
substantive *Book of Why* content chunk instead of front matter.

## Detector blind spot closed

`GLUE_RE` ended runs with `\b`, which requires a non-word character after the run. A glue run
running straight into a Capitalised word — `...describedintheIntroduction` — was invisible.
`GLUE_TRAILING_CAPITAL_RE` adds a lookahead for exactly that shape. It found **71 further
instances in the live corpus** and raised the count from 419 to 428, which is why the two books
were re-ingested rather than declared already-clean.

## Provenance re-stamping

Repairing the corpus changed the fingerprint, so ten reflection artifacts were correctly
flagged stale. Before re-stamping, two things were verified:

- **All 24 evidence chunk ids cited by the candidates still exist in `graph.db`.** Their content
  is unchanged, so the claims they support remain true; only the corpus stamp moved.
- **One digest cites a chunk that was never in the corpus at all** — `04_honest_lying_memory_confabulation`,
  from a paper that was never ingested. This is a pre-existing broken citation, not damage from
  this repair. The claim it supports is now marked unverified in place rather than deleted or
  silently re-stamped.

`scripts/restamp_provenance.py` refuses to stamp a file whose *evidence* chunk ids have
disappeared, because a blind hash rewrite would turn `check_reflection.py` into a rubber stamp.
Its first two versions each corrupted a file and were reverted: one matched a fingerprint
mid-object and split a JSON record; the other re-serialized with `json.dumps(indent=2)` and
expanded each object across 13 lines, breaking the one-object-per-line contract. It now
replaces the fingerprint value in place, as a string edit, and parses records with
`raw_decode` because these files are not strictly one-per-line.

## Lessons

1. **C-2 tested two libraries but one mode.** When a defect looks like source corruption,
   enumerate the parameter space of one tool before concluding the input is at fault. One
   keyword argument separated "unrecoverable" from "fully recoverable".
2. **`--dry` is a write path.** Any cleanup that recomputes what it just wrote is a second
   write. The preview destroyed 369 files.
3. **Re-ingestion reuses chunk ids.** Ids are content references, and a corpus repair silently
   invalidated four of them. Re-validate every cited id after re-ingest.
4. **A gate that refuses is information.** The one refusal I hit was a citation to a paper that
   was never ingested — a defect that had been sitting in the workspace, invisible, because
   nothing had changed the fingerprint since.
