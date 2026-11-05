---
type: Concept
title: C2_corpus_repair_triage
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# C-2 — Corpus whitespace damage: root cause, and why re-extraction is not the fix

> **SUPERSEDED BY C-6 (`C6_pdf_extraction_repair.md`) — this conclusion was wrong.**
>
> This investigation tested pypdf's default `extract_text()` and PyMuPDF's default
> `get_text("text")` and concluded the source PDFs were damaged. It never tried pypdf's
> `extraction_mode="layout"`, which recovers the whitespace perfectly (0 glue runs vs 31).
> The source files were never damaged; the default extraction mode discards glyph
> positioning. The corpus is now repaired without acquiring any new material.
>
> Everything below is retained as the record of how the wrong conclusion was reached.
>
Date: 2026-09-26
Companion to: `C1_corpus_whitespace_defect.md`
Status: **SUPERSEDED** — the premise below is disproved in C-6

## The experiment that settled it

I recovered original PDFs from git history — `knowledge/raw/*.pdf` is gitignored
(`.gitignore:14`), but six books were committed before that rule applied at add-commit `3ff56137`,
verified as complete binaries (`Design Patterns` 4,205,179 bytes `%PDF-1.5`, `Refactoring`
2,005,554 bytes `%PDF-1.3`, both with `%%EOF` trailers).

I then re-extracted them with both extractors available in this environment:

| Pages 0–150, `Design Patterns` | artifacts |
|---|---|
| pypdf (current `ingest.py`) | 536 |
| PyMuPDF | 536 |

| Pages 0–120, `Refactoring` | artifacts |
|---|---|
| pypdf | 723 |
| PyMuPDF | 732 |

The two independent extractors agree **character for character** on clean prose and reproduce the
**same** corruption in the damaged regions. PyMuPDF is marginally worse on `Refactoring`. A broken
extractor would not produce identical output from a different implementation.

## What is and is not actually damaged

Body prose extracts correctly in both tools. Page 30 of `Refactoring` via PyMuPDF:

```
' \n31\n     } \nI began by replacing totalAmount with a charge method on customer: \n
   \n class Customer... \n ... Enumeration rentals = _rentals.elements(); \n'
```

versus pypdf on the same page, which inserts a false space: `_rentals.ele ments()`. That is a
pypdf-only artifact and is a real, separate, minor defect.

The actual glued runs live in **margin notes and code listings**:

```
'aultController'   for  'FaultController'
'aderTester'       for  'HeaderTester'
'anceTravelled'    for  'DistanceTravelled'
'daryBasePrice'    for  'BoundaryBasePrice'
```

Block geometry shows why extractors cannot separate these: on `Design Patterns` page 40, body text
sits at `x=111.5` spanning `w=395.6` in a 612pt page, while the marginalia occupy a narrow
separate column. The inter-character advance widths in that marginal text are too small for
`unicode61` tokenization, and both extractors read the glyph positions the same way.

The worst case in the corpus, an entire copyright page collapsed to one token:

```
purposeofcopyrightistoencouragewritersandartiststoproducethecreativeworksthatenrich
```

The `causal-intervention` benchmark gold chunk has no standalone `causal` token in body or title,
so that case is unanswerable by any amount of query engineering or BM25 tuning.

## The detector is also wrong, in the other direction

`check_corpus_health.py` reports 38,137 artifact tokens across 21,821 distinct strings. A large
share of that is **legitimate camelCase in a codebase textbook** — `basePrice`, `daysOverdrawn`,
`frequentRenterPoints`, `floatingPointPayroll`. Flagging real source identifiers as extraction
corruption inflates the headline by an unknown but substantial factor, and it is why "6,401 chunks
affected" in C-1 overstates real prose damage.

So the gate currently mixes three genuinely different classes:

| Class | Example | Real? | Fix |
|---|---|---|---|
| OCR/text-layer glue in marginalia | `aultController` | yes | needs cleaner source PDF |
| Line-wrap truncation of identifiers | `sertEqual` (from `assertEqual`) | yes | dehyphenation/wrap-join |
| Legitimate camelCase identifiers | `basePrice`, `daysOverdrawn` | **no** | detector must stop flagging these |

Separating these three is the only improvement available without new source material, and it is a
measurement fix, not a corpus fix.

## What C-1's "unrecoverable without re-acquisition" actually means

The availability triage from C-1 still holds as fact about the disk (25 of 194 manifest sources
absent, 15 of them books), but the conclusion drawn from it was wrong and is now retracted: the 6
sources recoverable from git would not have been repaired by extraction, because extraction is not
the fault. I spent a recovery step on that assumption and it bought no repair.

Real remaining damage concentrates in sources with no copy on disk at all — `The Book of Why`
(6,193 tokens, and the benchmark gold source), `The Mythical Man-month` (5,566), `Artificial
Intelligence A Modern Approach` (3,190), `Building LLMs for Production` (2,117). For these, better
copies are the only fix.

## Prior-run scratch sources

Seven missing sources are experiment scratch, not literature: `1000_financial_forecasting_*`,
`1001_lasso_lag_*`, `999_ts_diverse_*`, `New Dokument tekstowy.txt`,
`adaptive_search_workspace_architecture.md`, `agent_workspace_research`,
`web_research_modular_composition_2026-09-19`. Eleven chunks, 31 artifact tokens — irrelevant to the
corruption.

They are **not** safe to evict on filename alone, which the graph contradicts: all 11 are
graph-connected, `00_new_dokument_tekstowy` carries 5 tags, and two are genuine research reports
present in the live graph digest — `00_adaptive_search_workspace_architecture` (7 tags) and
`00_token_efficiency_strategies_for_jcode` (6 tags, 8 graph edges). Eviction needs a dependency
check, not a filename judgement. Deferred; not part of this defect.

## Not attempted, and why

- **No BM25 `k1`/`b` tuning.** Rejected in C-1, still rejected: it optimizes ranking over a token
  stream that is missing the words.
- **No whitespace-reinsertion heuristics on existing chunks.** Splitting
  `purposeofcopyrightistoencouragewritersandartiststoproducethecreativeworksthatenrich` requires a
  language model or dictionary. A wrong split silently fabricates text, which is worse than
  leaving the corruption visible.
- **No extractor swap in `ingest.py`.** Disproven by the A/B above; it would have churned 10,364
  chunks and moved the graph fingerprint for a 1% artifact delta that is not even a real defect
  (see the camelCase row).
- **No benchmark baseline published.** `run_retrieval_benchmark.py` continues to self-stamp
  `status: VOID` while the corpus defect stands.
