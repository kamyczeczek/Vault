# brain/ — the curated layer

Two layers of memory live in this workspace and they answer **different questions**.
Neither replaces the other; do not merge them.

| Layer | Question it answers | Store | Door |
|---|---|---|---|
| Session memory | *Did I try this before, and how did it break?* | `scripts/_scratch/sessions/05_store/memory.db` (derived, gitignored) | `python.exe scripts/memory_index.py query "<text>"` |
| **Brain (this)** | *What is the rule / scar / decision about X?* | `brain/brain.db` (derived, gitignored) | `python.exe scripts/brain.py "<topic>"` |

Session memory is per-transcript and exhaustive; the brain is ~one line per rule for
the whole workspace and curated. A miss in the brain is normal — the door prints the
session door as the next step. Contract for the other layer: `scripts/memory/CONTEXT.md`.

## What is in it

    problems   <- SCARS.md         one row per scar (named `## S<n>` blocks, `- S<n>:`
                                   lines, and the flat one-line scars)
    decisions  <- DECISIONS.md     one row per `## D<n> — ...` block
    lessons    <- brain/lessons.md one row per failure-condition group

Scars stay in `problems` rather than getting their own table: the table already
carries `title, root_cause, fix, scar, gate`, and "scar vs lesson" is already the
*table* boundary (`problems` vs `lessons`). A separate table would split one file
across two directories and two ingest paths.

Row ids are file-derived and stable, so the checked-in evaluation and the FTS rowids
survive a rebuild: `decisions` → the D-number, named scars → the S-number, unnamed
one-line scars → `1000 + line order`, lessons → `1..n` in file order.

## Rebuild and verify

`brain.db` is a **gitignored derived artifact** — it is reproducible only because the
transformation is a committed script.

    python.exe scripts/ingest_brain.py          # rebuild from the three sources
    python.exe scripts/ingest_brain.py --check  # is brain.db the parse of them?

`--check` is freshness and coverage in one question: a source line that stopped being
parsed, a row that drifted, and a row in the database with no source (fabricated) are
all the same failure — the layer claims to hold a rule it does not hold. Gate **R21**
in `scripts/check_workspace_integrity.py` runs it on every commit, plus the retrieval
evaluation, and warns only when `brain.db` is absent entirely (a fresh clone).

## Retrieval

`scripts/brain.py` is a thin door over `scripts/memory/retrieval_v1.py` unchanged —
the validated lexical config. The evaluation is `scripts/memory/eval_brain.py` over
`scripts/memory/brain_eval.json`; cases are anchored on exact `table:id` and the
refusal cases are as much of the set as the answerable ones. `--check` fails only on a
regression below the baseline recorded in that file, and prints its `known_gaps` so a
tolerated miss stays visible instead of silently accepted.

**No vectors and no reranker.** This layer has no measured insufficiency that would
justify either; the scars about metric-design and semantic thresholds in `SCARS.md`
are the standing argument for measuring first.

## For a fresh agent

The layer table and the door commands are at the top of this file; the other layer's
contract is `scripts/memory/CONTEXT.md`. What follows is only what is stated here and
nowhere else.

**Two layers, two questions — the door enforces the order.** The two doors answer
different questions and spend different budgets:

- **Brain (curated):** ~one line per fact for the whole workspace. The counts are
  live — check `python.exe scripts/ingest_brain.py --check`. Cheap. Ask *what is the
  rule / decision / scar about X?*
- **Session (episodic):** exhaustive, full traceback per transcript. Expensive — the
  size is live: `python.exe scripts/memory_index.py stats` (1508 sessions / 197 944
  chunks on 2026-10-16). Ask *did I try this, and how did it break?*

Query brain first; fall back to session only when the brain is silent. `brain.py`
prints the session door as its next step on a miss, so the order is enforced by the
door, not by memory.

**Two triggers are brain-only.** The rest are in `scripts/memory/CONTEXT.md`, "When
you MUST query it". Read all of them as binding: a skipped query on a matching trigger
is a bug, not an absence of one.

1. Before editing `scripts/**`, `hooks/**`, `skills/**`,
   `check_workspace_integrity.py`, `audit_*.py` — `SCARS.md` holds the operational
   scars for these files.
2. Before `git commit` — the commit-hygiene scars sit at the end of `SCARS.md` and
   are not script-scoped.

The remaining triggers live in `scripts/memory/CONTEXT.md`: an error you did not write
(traceback, failing test, flaky timeout); after two failed attempts at the same
operation; before a structural root change (a new gate, root entry, or process step);
and any "what have we already tried / why is it like this".

**Commands.**

    python.exe scripts/brain.py "<topic>"            # one line per matching rule
    python.exe scripts/brain.py "<topic>" --all      # full decision blocks, not just top-1
    python.exe scripts/brain.py "<topic>" --json     # machine-readable
    python.exe scripts/brain.py "<topic>" --limit 2  # cap the number of hits
    python.exe scripts/memory_index.py query "<topic>"
    python.exe scripts/memory_index.py get <chunk_id>   # chunk_id, not session_id — e.g.
                                                        # opencode::ses_efc4a483::0
    python.exe scripts/memory_index.py stats            # size and per-agent breakdown
    python.exe scripts/memory_index.py freshness        # exit 1 when the index lags >24h

Use `python.exe`, never WSL `python3`: under WSL `freshness` returns `UNVERIFIED — …
read none of their agent stores`, an interpreter limitation, not a bug.

**The retrieval path is one thin, deterministic chain.**

    brain.py -> scripts/memory/retrieval_v1.py -> brain/brain.db (SQLite FTS5)

`brain.py` holds no retrieval logic of its own — every hit/refusal decision happens in
`retrieval_v1.py`. The query pipeline (**K1**, no model): `tokenize -> drop <=2 chars
-> stem (PL suffix) -> drop stopwords after stemming -> sort`. The engine (**B1**) runs
one `SELECT … fetchall()` per table, then merges and sorts by FTS5 `rank`.

**There is no decision layer.** An empty result list *is* the refusal — no threshold,
no filter. H5 ("reject a hit matched only by a post-stem stopword") was measured and
**rejected as overfit**: it fired on 0/5 new questions and scored worse (72.7%) than
K1 without it (81.8%). Keep it that way: a threshold is a hidden tuning parameter; no
threshold is no tuning.

**R21 (hard) checks two things at once** — freshness/coverage and measurement
regression — and warns, never passes silently, *only* when `brain.db` is absent
(fresh clone). A database that exists is never exempt: "cannot compare" is the one
answer this gate may not give quietly. `brain/brain.db` is gitignored — never hand-edit
it with `INSERT`/`DELETE`, never commit it; the rebuild contract is under "Rebuild and
verify" above, and R21 forces it at commit anyway.

**R21 can fail, and that is the test.** Recipe, not a re-run here: delete a row from
`brain/brain.db` → `ingest_brain.py --check` names it (`N source row(s) absent from
brain.db: [...]`) → re-ingest restores green. The record that this gate actually went
red is in `handoff/flags/brain-memory-v1-landed-2026-10-16.md`. A gate that cannot fail
is decoration.

**Measurement state (2026-10-16, baseline in `scripts/memory/brain_eval.json`).**

| Metric | Value | Set |
|---|---|---|
| hit@5 | 9/10 | `brain_eval.json` (14 cases: 10 answerable + 4 refusals) |
| refusal | 3/4 | same |
| MRR | 0.900 | same |
| family_recall@5 | 81.5% (22/27) | gold set, 38 questions (`retrieval_v1.py` docstring) |
| refusal | 81.8% (9/11) | same |
| MRR | 0.778 | same |

`--check` fails only on a regression below the baseline; an improvement passes, so the
layer can improve without rewriting the baseline.

**Known gaps — recorded, not silently fixed.** In `brain_eval.json#known_gaps`, printed
by the gate as `KNOWN-GAP`, not `FAIL`:

1. **PL↔EN tokenizer.** The Polish question "integralności" stems to `integralnośc` and
   does not reach the English token `integrity` that `lessons:1` uses. The ceiling of
   lexical K1 — there is no PL↔EN stemmer.
2. **`refuse-risotto`.** "risotto alla milanese" → stem `all` → matches `all` in
   `problems:1018` (and `decisions`). Accidental token sharing; 1 of 4 out-of-corpus
   questions is answered.

Do not "fix" either silently by adding vectors or a reranker.
`retrieval-v1-deployed-2026-10-15` says it plainly: there is no measured need on this
corpus — measure first, then add a layer. Whether `lessons:1` *should* be retrievable
from a Polish question is the owner's call: a layer problem (add a PL→EN map) or a
deliberate limit (then drop the case from `brain_eval.json` so it stops depressing the
baseline).

**Three rules this layer enforces.**

1. **Artifact over report.** Every number has a path to a file with raw output; "9/10"
   without `brain_eval.json` is a claim, not a measurement.
2. **A gate must be able to fail.** If you cannot show how it breaks, it is not a gate.
3. **Record the scar, not just the fix.** A mechanical error repeated after review is a
   process gap; one line in `SCARS.md` saves the next session the whole context.

**Do not.**

- Add vectors or a reranker without measuring that K1 is insufficient. `retrieval_v1`
  measures `family_recall@5` 81.5% and `refusal` 81.8% — a baseline, not a ceiling.
- Hand-edit `brain.db`; it exists only because `ingest_brain.py` is committed.
- Use the brain as a substitute for session memory. Brain = "what is the rule";
  session = "did I try it". Different questions.
- Fabricate a row whose source you cannot see. A previous parser injected
  `'Mention of S<n> in SCARS.md'` for missing blocks — 12 of 24 rows were fabricated.
- Use `python -c` (MSYS mangles quotes and paths — write a file) or WSL `python3` (it
  sees none of the agent stores). Use `python.exe`.
- Change a gate's threshold after its test failed — that is S62, fabricating a pass.
  Fix the data or report the discrepancy.

**Routing — why there is no row in `AGENTS.md`.** The `brain/` row lives in
`CLAUDE.md`. `AGENTS.md` is guarded by R13, and R13 is three halves:
`audit_agents_md.py --check` against the recorded *classification* baseline
(`EXPECTED` over the audited span — routing 8 / evidence 23 / heading 1 / blank 5 /
total 37, not a line count), `--report-check` over every report in `docs/reviews/`,
and `audit_prose_numbers.py --check` on the reports' prose. One routing row is
therefore a ≥3-file cascade (`SCARS.md`: "AGENTS.md routing row = R13 cascade"). Do
not add it without an R13 plan — a missing `brain` row in `AGENTS.md` is known debt,
not a bug.

**Open debts — decide, do not silently close.** Owner decision, not an agent's:

| Debt | Recorded in | Needs |
|---|---|---|
| Routing row in `AGENTS.md` | `handoff/flags/brain-memory-v1-landed-2026-10-16.md` | an R13 plan (≥3 files) |
| PL↔EN tokenizer gap | `scripts/memory/brain_eval.json#known_gaps` | layer (a PL→EN map) or metric (drop the case)? |
| `refuse-risotto` | `scripts/memory/brain_eval.json#known_gaps` | badly designed case, or a real gap? |
| `DECISIONS.md` granularity | flag above | whole decisions as chunks, or title + verdict? |
| `brain/problems/` empty | only `README.md` | nothing to ingest |
| `model: current`/`default` in flags | flag above | 12 flags / 13 `model:` lines on 2026-10-16 — a nickname, not an id |
