---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# CONTEXT.md — datasets

One job: put a trustworthy, provenance-carrying series in `data/` — or refuse to.

## Inputs

- Reference (every run): `data/ett_readme.md` — the worked example of provenance
- Reference (every run): `new_datasets_catalog.py` — how a series enters the catalog
- Working (this run): `INBOX/raw/` — source documents awaiting extraction

## Process

1. Name the series and what it measures. If the answer is "a plausible curve",
   it is synthetic and must be labeled as such.
2. Fetch it with a script in this folder. Never hand-place a CSV.
3. Record source URL, retrieval date, units, sampling rate, and known gaps.
4. Verify the loader parses it and the column semantics match the readme.
5. Register it in the catalog.

## Outputs

- `data/<series>.csv` — the series
- A catalog entry with provenance
- Updated `data/ett_readme.md` when ETT itself changes

## Human check

Open the fetched file and confirm: does the row count match the published length,
is the index monotonic, and are the units the ones the benchmark assumes? A
mislabeled unit is worse than a missing dataset — it produces a number that
looks valid and is not.

## What a dataset must carry

| Field | Why it exists |
|---|---|
| Source URL | Reproducibility — anyone must be able to re-fetch it |
| Retrieval date | Series get revised; an undated fetch cannot be checked |
| Units and scale | MAE is meaningless across incompatible units |
| Sampling rate | Hourly vs daily changes every horizon argument |
| Synthetic or real | The finding that broke a prior benchmark |

## Known traps

- `ETTh1_h1.csv` is the one file large enough to slow a repo down. It is
  gitignored for that reason; run `fetch_etth1.py` instead of copying it.
- A series with a long front-matter block in its source PDF will ingest as
  garbage. Extract with the layout mode — this is the same defect class that
  `../brain/scripts/ingest.py` guards against.

## Open work

Every item below was read off the code on 2026-09-27, not inferred.

**1. The "scientific" datasets are not scientific.** `fetch_scientific_datasets.py`
opens with a `Sources:` block citing ETTDataset, the UCI Traffic archive, and
Petrovay (2010), and `benchmark_scientific_datasets.py` prints those three
citations as a banner. All three `get_*_data()` functions are `np.random`
generators — sinusoids plus noise, with a hard-coded `seed=42`. Nothing
contacts UCI, SIDC, or any mirror. The provenance table this project exists to
enforce is absent from the one fetcher whose name advertises provenance. These
are the `get_*_data()` functions three `../benchmark-core` scripts import, so
the fix is a breaking change for those callers and must be staged.

**2. `benchmark_scientific_datasets.py` cannot run.** It imports
`members.amr_fbs`, `members.knn_feature_forecaster`,
`members.adaptive_amr_knn_hybrid`, `members.meta_ensemble_stacker`, and
`members.sota_baselines`. There is no `members/` package in this project and no
glob match for one anywhere in the workspace. The import fails before `main()`
is reached, so no scientific benchmark number in this project was ever produced
here. It also silently swallows every per-origin error
(`except Exception: continue` in `evaluate_model`) and then reports `NaN` as
`FAILED` — a broken model and a model that legitimately cannot be fit are
indistinguishable in the output.

**3. `results/` does not exist, and three scripts write into it.**
`fetch_scientific_datasets.py:155`, `new_datasets_catalog.py:183`, and
`benchmark_scientific_datasets.py:98` all open `results/<file>.json`. `results/`
does not exist in this project, and no script anywhere creates it —
`fetch_scientific_datasets.py:120` calls `mkdir` for `data/` only, and
`new_datasets_catalog.py` creates no directory at all. Each of the three
therefore raises `FileNotFoundError` at the metadata write. In the two fetchers
that write happens *after* the series are generated and saved, so the CSVs land
in `data/` and the run still dies, reporting a partial success. That metadata
write is also the only place the project records anything resembling a catalog
entry, and it records `source` as `name.replace("_", " ")` — the series name,
not a URL. There is no retrieval date, no units, no sampling rate: three of
the four fields "What a dataset must carry" requires.

**4. `fetch_etth1.py` is broken in both paths, and one of them would corrupt
the real file.** Verified 2026-09-27 against
`zhouhaoyi/ETDataset@main`: the upstream data now lives at
`ETT-small/ETTh1.csv` (one file per variant), header
`date,HUFL,HULL,MUFL,MULL,LUFL,LULL,OT` — byte-identical to the first rows of
the working `data/ETTh1_h1.csv`, so that file is genuine. But all three URLs in
`github_try` (lines 77-79) request `ETT.csv`, which no longer exists — each
returns `HTTP Error 404`, so the whole GitHub path is dead and its
`ETTh1`-row-masking logic targets a multi-variant layout the repo abandoned.
The HF path runs instead, and it is the one that does damage: both
`parse_to_etth1` and `github_try` write only a `date,OT` pair, so
`python fetch_etth1.py` — the command `CLAUDE.md` tells every consumer to run
— silently drops the six load columns that `data/ett_loader.py:233`, the
canonical loader every benchmark uses, depends on for its multivariate
feature set. Three more defects in the HF path: the temperature guess-list at
line 56 is `("ot", "oiltemp", "temperature", "hufl")` and `HUFL` is a *load*
column, so a discovered file carrying `HUFL` but not `OT` yields high useful
load recorded as oil temperature; line 68 builds `date` from
`df.iloc[:len(s)].index`, the positional index rather than the date column,
so a parquet-backed file with a RangeIndex yields a `date` field of integers;
and the 8640-row floor accepts any series long enough, which is how a
non-ETTh1 file gets through. The working file was not produced by this script.

**5. All nine non-ETT CSVs in `data/` are orphans.** `Electricity_Transformer_Load`,
`Traffic_Flow`, and `Solar_Activity_Cycle` are named like output but the
generators that build them (`fetch_scientific_datasets.py:161-163`) write them
only when `main()` runs — and `main()` dies at the `results/` write on its
previous line, so they are not reproducible from this folder as it stands. The
other six — `Industrial_Sensor_A`, `Industrial_Sensor_B`,
`Weather_Temperature_Realistic`, `Solar_Activity_SIDC`, `Financial_Returns_GARCH`,
`ETT_Load_Synthetic` — match no filename anywhere in the project: the catalog
keys are `Electricity_Hourly`, `Traffic_Flow`, `Financial_Returns`,
`Weather_Temperature`, `Web_Traffic`, `Healthcare_Vitals`, and
`new_datasets_catalog.py` never writes a CSV at all. All nine are 8000-row
single `value` columns with no date column and no metadata sidecar.
`Solar_Activity_SIDC` and `Weather_Temperature_Realistic` name real, citable
sources (SIDC, a station series) while carrying generated data, which is
exactly the failure the "label it or drop it" rule exists to prevent. Not one
of the nine carries a synthetic marker in its filename or its rows.

**6. `test_stock_fetch.py` now always returns invented data, unlabeled.**
`get_stock_data` falls back to seeded GBM+GARCH and prints
`Falling back to synthetic Geometric Brownian Motion for {ticker}` — to
stdout, not into the returned array. Verified on 2026-09-27: the primary path
now answers `HTTP Error 401: Unauthorized` — Yahoo retired the unauthenticated
`v7/finance/download` endpoint this script was written against — so the
fallback is not a rare path, it is the *only* path, and the `except` block
prints a failure line immediately above a success-looking return. A caller
gets a plausible 2600-point price path with no way to tell it from SPY except
by scraping the console. The `close_idx` loop takes the *last* column matching
`Close`, and because `'Close' in col` is also true for `Adj Close`, a standard
`Date,Open,High,Low,Close,Adj Close,Volume` header always lands on `Adj Close`;
the `close_idx = 4` default at line 16 is dead on any normal header.

**7. `search_datasets_kg.py` depends on a gitignored file.** It opens
`.\.brain\graph\graph.db`; `.brain/` is gitignored and produced by
`../brain/scripts/ingest.py` in another project. On a fresh clone this raises
`sqlite3.OperationalError: unable to open database file`, and the path is
Windows-separator-only, so it also fails on any other platform. `CLAUDE.md`
routes "search the catalog for a series" here, but the project has no catalog
file to search — `new_datasets_catalog.py` is a generator, not a registry.

**8. No test coverage for the three public functions.** `get_*_data()` in
`fetch_scientific_datasets.py` are imported directly by three
`../benchmark-core` scripts, as `CLAUDE.md` already notes, and there is no
test file in this project at all — `test_jina_search.py`, `test_jina_web.py`,
and `test_stock_fetch.py` are manual `if __name__ == "__main__"` scripts with
no assertions, so a name or signature change in a public function surfaces as
`ImportError` in a sibling project instead of a test failure here.

**9. The INBOX readers are broken against the current layout, by inspection.**
`INBOX/raw/` holds five source books (Auffarth 2021, Joseph 2024, Bartos &
McCleary 2017, Korstanje 2026, Gridin) and six result notes, none ingested.
`read_inbox_files.py` and `read_new_markdown.py` and
`check_inbox_frontmatter.py` all open
`PROJECTS\agentic-research-lab\INBOX\New Markdown File.md`, which does not
exist — the file is now at `INBOX/raw/`. `read_inbox_files.py:2` also points at
`PROJECTS\ROOT\INBOX\issues.md`, and that tree does not exist at all; the script
uses `os` at line 7 without ever importing it, so it raises `NameError` before
it can report either miss. `check_inbox_all.py`, `check_inbox_details.py`,
`read_all_inbox.py`, and `check_recent.py` each walk all of `C:\Users\Mateusz`
or `C:\Users\Mateusz\Desktop` rather than this project's `INBOX/`, and
`check_inbox_all.py` mixes escaped and raw separators in the same path. Four
scripts embed the 90-character Auffarth filename as a literal, so a rename
breaks them silently. `CLAUDE.md` cites `AGENTIC_DISCOVERY.md` as the origin of
the synthetic-labeling rule; that file is in neither this project nor the
workspace.

**10. `fix_corpus_source.py` writes malformed frontmatter into a sibling
project.** It rewrites every corpus file missing a `source:` field in
`../agentic-research-lab/knowledge/corpus/`, and its reconstruction
(`"----" + meta + "---" + body`) produces a four-dash opening fence that no
YAML frontmatter parser will accept — so the "fix" destroys the frontmatter it
was repairing. It also overwrites `title` with the bare filename when the
existing frontmatter had a real title, and takes `parts[2]` as the body when
`content.split('---', 2)` has already consumed the closing fence as part of
`parts[1]`. Run once against 10,000+ corpus files this is a destructive
migration with no dry-run flag. It is a `main`-less top-level script: importing
it performs the rewrite.
