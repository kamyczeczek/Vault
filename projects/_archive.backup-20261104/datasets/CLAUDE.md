---
type: Concept
grade: demoted
title: CLAUDE
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# CLAUDE.md — datasets

Acquisition and cataloging of time-series data. Owns the fetchers, the dataset
catalog, and the raw inbox. Nothing here is vendored: every consumer re-fetches.

## Where things live

| Path | Role | Description |
|---|---|---|
| `CLAUDE.md` | Catalog (L0) | This file |
| `CONTEXT.md` | Contract (L1) | What a dataset must satisfy to enter the catalog |
| `data/` | Product (L4) | Downloaded series. Gitignored — re-fetch, do not commit |
| `data/ett_loader.py` | Factory (L3) | Canonical ETT loader used by every benchmark |
| `data/ett_readme.md` | Reference (L3) | ETT provenance and column semantics |
| `INBOX/raw/` | Product (L4) | Source PDFs awaiting ingestion. Gitignored |
| `fetch_etth1.py` | Factory (L3) | Genuine ETTh1 — transformer temperature, hourly, OT column |
| `fetch_scientific_datasets.py` | Factory (L3) | Scientific series from published benchmark sets |
| `new_datasets_catalog.py` | Factory (L3) | Extend the catalog with a new series |
| `benchmark_scientific_datasets.py` | Factory (L3) | Evaluate models on the scientific catalog |

## Route by intent

| Intent | Go to |
|---|---|
| Get ETTh1 | `python fetch_etth1.py` |
| Get the scientific dataset set | `python fetch_scientific_datasets.py` |
| Add a new dataset | `new_datasets_catalog.py`, then a fetcher beside it |
| Evaluate models on scientific data | `python benchmark_scientific_datasets.py` |
| Search the catalog for a series | `search_datasets_kg.py` |
| Read a source PDF from the inbox | `read_book_excerpts.py`, `search_books_content.py` |
| Inspect inbox state | `check_inbox_*.py`, `find_inbox_refs.py`, `inspect_inbox_books.py` |
| Verify a market data fetch | `test_stock_fetch.py` |

## Dependencies

- No sibling project. This is a leaf: it depends on the network, not on code.

  Other projects depend on *it*. `fetch_scientific_datasets` is imported directly
  by three scripts in `../benchmark-core`, which put this folder on `sys.path`.
  Its three `get_*_data()` functions are therefore a public interface — changing a
  name or signature breaks those callers, and they are not covered by any test
  in this project.

## Rules

- **Never commit a dataset.** `data/*.csv` and `INBOX/` are gitignored. A
  consumer that needs a series runs the fetcher.
- **A synthetic series must be labeled synthetic.** The standing finding from
  `AGENTIC_DISCOVERY.md` is that a catalog of "real" datasets containing
  generated data invalidates the comparison. Label it or drop it.
- A fetcher records the source URL and the retrieval date. A dataset with no
  provenance is not a dataset.
