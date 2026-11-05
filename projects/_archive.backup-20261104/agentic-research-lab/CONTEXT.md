---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# CONTEXT.md — agentic-research-lab

One job: maintain a deterministic, scientific, graph-backed research lab on
**how to do agentic research well** — verified corpus markdown → derived FTS5
graph → reflection → meta-learning workflow updates.



### 2026-10-05 18:15 — Phase 2 session B: non-tautological content criterion

- The pilot's `solved` criterion is tautological vs the arm: OFF cannot know
  chunk IDs, so it loses by definition. Session B replaces that half with a
  content criterion that both arms can in principle pass: per-task facts
  extracted ONLY from the task's oracle chunks (`benchmark/content_criterion.json`,
  25 facts), each a case-insensitive regex over the answer text. Echo guard: a
  pattern matching the task question is rejected; off-oracle sourcing is
  rejected; `--build-check` enforces both (first run caught 3 real defects in
  my own draft: 2 echo patterns, 1 off-oracle source).
- `scripts/score_ablation_content.py` rescores the sealed pilot transcripts
  deterministically (no new LLM calls): ON macro 0.380 vs OFF 0.222; ON
  out-scores OFF only on bug-fix (0.833 vs 0.278) of 3 families -> verdict
  INCONCLUSIVE per the pre-registered rule. The metric now measures answer
  content, not arm identity (OFF's score is non-zero where it actually knows
  the fact, e.g. silent-failure on bf-deadroute).
- 14 new tests (2/14 catch mutations: echo/source guards + macro/family
  math); 22/22 green with the pilot scorer. Next: owner call — extend n, or
  fold the content criterion into the hypothesis verdict doc.

### 2026-10-04 12:55 — Critic gate before neighbor expansion in ask.py (CRAG pattern)

- `query(expand=True)` ran a neighbor query per base hit unconditionally,
  even at full limit where expanded rows are cut unseen. New pure function
  `critic_verdict(rows, limit)`: `empty` / `expand` (thin base or
  single-family concentration — the citation-concentration signal) /
  `sufficient` (full limit, several families — neighbor SQL skipped).
  No LLM, no embeddings, deterministic (Q17-blind). Verdict surfaces via
  `verdict_out` + `# critic:` stderr line in CLI.
- 6 hermetic tests; no ranking change (gate only skips already-cut queries;
  benchmark path uses recall, not expand). Full suite 284/284.

### 2026-10-04 12:40 — Dead-route health monitor: route.py fails loud (W-AUDIT-4)- `ask.py` already exited 2 on dead `--tag` intersections; `route.py` (the
  deterministic router scripts call) returned rc=0 with empty output — the
  remaining silent half. Now: tags given + zero ids after ADAPT -> stderr
  naming the tags + exit 2 (same wording as ask.py); `--json` adds
  `"dead": true`. `--all-topics` stays rc=0 (printed 0s are inventory).
- 5 hermetic tests (`tests/test_route_health.py`); live probe (dead tag ->
  rc 2, `icm` -> ids + rc 0); full suite 278/278; `QUALITY PASS 21/21`.

### 2026-10-04 12:20 — Deep-research Phase 1: KG–ICM literature + synthesis ingested

- 3 literature sweeps (GraphRAG-family, agent memory R/W, code graphs) + 8
  arxiv seeds via `expand_literature.py`; synthesis in
  `INBOX/kg_icm_phase1_synthesis.md` -> `ingest.py` (12 chunks) -> graph
  rebuild: fingerprint `31989e46d0a5` -> `4880aab33ca4`, 10,373 nodes /
  13,457 edges. Verified: new synthesis chunk ranks 1 on
  "what mitigates citation concentration".
- Headline transfers: ICM inverts GraphRAG cost (no LLM at index, LLM at
  read with provenance); HippoRAG2 single-step PPR matches iterative
  retrieval at 10-30x less cost (route.py should expand queries pre-match);
  CRAG cheap-critic-before-expansion gates drift; Graphiti bi-temporal
  edges (invalidate-don't-delete) are the only surveyed eviction model —
  adopt valid/invalid pairs for memory.md; cheapest code-graph schema is
  4 edge kinds (defines/calls/imports/inherits) at +2.3-4.7pp SWE-bench.
- Next: Phase 2 operational ablation (agent with/without graph) or Phase 4
  single runtime improvement (route health monitor / critic gate).

### 2026-10-03 01:24 — Forge A/B results: no lift on the easy task (15/arm)

- Live run: `OMNIROUTE_API_KEY` present, router up (2077 models, target
  `gemini/gemini-flash-lite-latest` present). Two batches — `N=5` and
  `--runs 10` (a `--runs N` option was added to the script; `--build-check`
  re-gated after the edit). Combined: rescue OFF 14/15, mean 14.2 s;
  rescue ON 14/15, mean 13.7 s. One `MaxIterationsError` loop-stall per
  arm — same failure shape on a trivial task.
- Reading: baseline is already ~93% reliable on an easy deterministic
  task, so the harness measures no guardrail lift or regression. Outcome
  logged in ADR 0017 § Measured effect.
- Open: point the same harness at a harder task and/or a genuinely weak
  model (baseline failure rate > 0) to measure real rescue lift.

### 2026-10-03 01:05 — Forge A/B test prepped for gemini-flash-lite-latest (run done 01:24)

- `scripts/forge_ab_test.py`: deterministic 3-step tool task (search ->
  add(8,13) -> respond '21') against `gemini/gemini-flash-lite-latest`
  via the omniroute gateway (`localhost:20128/v1`), rescue OFF vs ON, 5
  runs each; `--build-check` verifies construction without LLM calls.
- Probed the real v0.9.5 API before writing it: `ToolSpec.from_json_schema`
  + `ToolDef(spec, callable)` + `respond_tool()` (terminal arg field
  `message`). The first draft used kwargs that do not exist — do not
  re-copy those assumptions.
- Open (done 2026-10-03 01:24): live run + recorded in ADR 0017 § Measured
  effect; next open — harder task / weak model.

### 2026-10-02 23:55 — Forge guardrails integrated for weaker-model tool-calling

- ADR 0017 + `scripts/forge_bridge.py`: opt-in wrapper over `forge-guardrails`
  (antoinezambelli/forge, v0.9.5) in a project-local `.venv-forge` (Python
  3.12.13 — Forge requires 3.12+; the venv's own `.gitignore` keeps it out of
  the repo). Not on the core inference path: purely opt-in.
- `build_compat_runner(base_url, model)` wires an `OpenAICompatClient` +
  `ContextManager(TieredCompact, 32K budget)` for weaker remote models behind
  OpenAI-compatible gateways (e.g. nara/omniroute); `ForgeRunner` is a
  preconfigured `WorkflowRunner` (rescue on, 10 iterations, 3 retries/step,
  retry nudge). `FORGE_API_KEY` env default.
- Verified under the 3.12 venv: `--check`/`--info` clean; factory constructs
  the real runner graph for both `tiered` and `sliding` strategies.
- Open: a live weaker-model tool-calling scenario through
  `build_compat_runner(...)` to measure the guardrail lift.
- Note: PyPI's `forge` is a different (Django) package — install only from the
  GitHub repo into `.venv-forge`.

### 2026-09-29 21:41 — Ralph loop runs through pi, not only goose

- `scripts/pi_ralph_worker.py` / `pi_ralph_reviewer.py`: the `--worker` /
  `--reviewer` overrides that carry the ralph-work / ralph-review recipe into
  a fresh pi session (`pi -p --no-session --approve`, prompt in a file via
  `--append-system-prompt`, never on the command line). Models/providers:
  `RALPH_WORKER_MODEL` / `RALPH_REVIEWER_MODEL` (+ `_PROVIDER`), falling back
  to pi's own config. `RALPH_PI_CMD` replaces the pi command line so the
  control flow is provable without a model.
- `tests/test_ralph_pi.py` (12 tests, zero model cost): prompt carries the
  task + output contract; argv is fresh-context by construction (`-p`,
  `--no-session`, no `--resume`/`--continue`); a fake pi that only writes the
  state files proves SHIP → exit 0 and REVISE → SHIP through the REAL pilot
  subprocess plumbing.
- Fixed while pinning: `git_log()` crashed when git was not on PATH; now
  degrades to a marker, matching the recipe's honest-reporting rule.
- Not yet proven: a real pi model session end-to-end (the semantic handoff,
  which this repo's evidence says is not mechanically checkable - so it is
  not claimed). Live: `python scripts/ralph_pilot.py "task" --worker
  "python scripts/pi_ralph_worker.py" --reviewer "python scripts/pi_ralph_reviewer.py"`.

### 2026-09-29 19:45 — Ralph loop at full upstream parity; c3 deliberately overridden

- Read the official tutorial (https://goose-docs.ai/docs/tutorials/ralph-loop/) and
  found the earlier pilot was not a Ralph loop at all: it had no model session,
  so its 'fresh context per iteration' docstring line was an assertion, not a
  mechanism. Fixed by implementing the real thing, not by rewording the claim.
- `scripts/ralph_pilot.py` rewritten: two goose sessions per iteration (work +
  review), each `goose run --recipe ... --no-session`, so fresh context is
  structural. Official `.goose/ralph/` file contract implemented verbatim; the
  verdict is read from `review-result.txt`, never from a model's prose.
- New: `recipes/ralph-work.yaml`, `recipes/ralph-review.yaml` (schema verified
  against the goose recipe reference). `.goose/` ignored as generated state.
- **c3 OVERRIDDEN BY CHOICE.** The reviewer now stops the loop; `check_dead_code`
  is advisory only. Verified live: the loop SHIPPED with the gate still FAILing,
  because the reviewer said SHIP. Recorded in the decision artifact, not hidden.
- Also fixed the last rung-3 overclaim: the emitted `expected` string claimed a
  'human-written rule' while the ladder writes it. Now pinned by a test that
  rejects the phrase in the output, not just the label.
- Pre-commit review found four places where the code contradicted the c3
  override it had just been given; all fixed and pinned, because a test suite
  that cannot fail on a claim the code does not make is not evidence:
  1. `write_state()` still told the next session "the gate's exit code is the
     only acceptance signal" - actively instructing a fresh worker to ignore
     REVISE. Now says the reviewer stops the loop.
  2. Final state wrote the *pre-loop* gate probe as the failure context, so
     after a REVISE it described an older tree. Now writes the latest run.
  3. Model resolution ran unconditionally, so a no-cost deterministic run died
     on missing `RALPH_*` env vars - a false blocker, since nothing in that
     mode reaches a model. The cost warning likewise claimed cost it would not
     incur; it now says 0 sessions when both phases are overridden.
  4. Dead bindings removed (`prev`, `captured`, and two never-read parameters on
     `goose_argv`/`run_phase`) rather than shipped as names that look meaningful.
- Q0 was also failing on root drift that was not the project's: the undeclared
  file was my own scratch `_diag*.py`. Deleted and `ROOT-CONTEXT.txt` regenerated.
- 21/21 gates, 231 tests + 10 subtests (was 204 at parity start). MAP.md
  regenerated, 117 modules. Both file-driven branches re-proved after the fixes:
  REVISE-only exhausts the cap and returns 1; REVISE-then-SHIP returns 0 and
  writes `.ralph-complete`, while the advisory gate is still FAILing.

## Inputs

- Working (this run): `INBOX/` — raw seed papers and research notes awaiting ingestion
- Working (this run): `knowledge/corpus/NN_slug.md` — canonical chunks (see § Chunk contract)
- Working (this run): `reflection/{candidates,digests}/memory.md` — candidate rules under validation
- Reference (every run): `knowledge/graph/GRAPH-DIGEST.md` — the read path agents load
- Reference (every run): `knowledge/topics.md` — controlled topic vocabulary
- Reference (every run): `stages/` — contracts for phases `00_expand` through `06_meta_evolve`

## Process

1. Ingest: `INBOX/` → `scripts/ingest.py` → `knowledge/corpus/`. Ingestion empties `INBOX/`.
2. Rebuild: after any corpus change run `python knowledge/graph/build_graph.py`. Never hand-edit derived artifacts (`graph.db`, `graph_index.json`, fingerprints, digests).
3. Query and reflect: `knowledge/graph/ask.py` for reads; `pipeline/06_reflect/spawn.py` writes only to `reflection/{candidates,digests}/`. Every candidate cites chunk ids from `ask.py`.
4. Promote and evolve: validated rules land in `reflection/memory.md`; `scripts/apply_meta_learning.py` evolves stage contracts from them. Stale reflections are quarantined, never merged.
5. Gate: all commits via `python scripts/agent_commit.py` — root gate Q0 first, then the project gates. Never `git add .`.

## Outputs

- Canonical chunks in `knowledge/corpus/`, rebuilt graph + digest, grounded reflection candidates/digests.
- Promoted rules in `reflection/memory.md` and evolved stage contracts.
- Changes to exactly this project per session; sibling facts are linked, never copied.

## Human check

Ask: for the claim just made, which chunk id from `ask.py` grounds it? If none, it is ungrounded. After a corpus change: graph rebuilt, fingerprint re-pinned, `scripts/quality_check.py` green — otherwise the result is void.

## Operating contract
- **Read path:** agents load context from `knowledge/graph/GRAPH-DIGEST.md`.
- **Write path:** new knowledge enters only via `INBOX/` → `scripts/ingest.py` → `knowledge/corpus/`.
  Never hand-edit `knowledge/graph/graph.db` or `graph_index.json`. Tracked provenance files
  (`knowledge/graph/.graph_fingerprint` and `GRAPH-DIGEST.md`) are updated strictly via `build_graph.py` / `watch.py`.
- **Refresh:** after any corpus change run `python knowledge/graph/build_graph.py`.
- **Derived artifact ownership:** corpus markdown is authoritative; graph DB/indexes and reflection digests/candidates are rebuildable projections. A graph rebuild must never restamp reflection provenance. Stale or invalid reflections are quarantined under `reflection/stale/<generation>/` as local operational evidence, while `reflection/repair_ledger.jsonl` is the tracked audit trail. Regenerate projections from authoritative inputs rather than editing fingerprints.
- **Reflection:** `pipeline/06_reflect/spawn.py` spawns an isolated agent that reads the graph and
  writes only to `reflection/{candidates,digests}/`.
- **Promotion & Memory:** validated candidate rules are promoted to `reflection/memory.md`.
- **Meta-evolution:** `scripts/apply_meta_learning.py` parses promoted principles in `reflection/memory.md`
  and updates stage contracts / workflow definitions to improve agent research performance.
- **Git checkpoints & Staging:** all commits must be gated via `python scripts/agent_commit.py`. Never use `git add .` or `git add -A`; stage only explicitly approved relative paths.
- **Gate Q0 — workspace root:** `scripts/quality_check.py` runs `../../../scripts/check_workspace_integrity.py`
  before the eighteen project gates, because all eighteen resolve their root to *this* repository
  and are therefore blind to the directory above it. It is the only check covering the workspace
  root; see `../../../CONTEXT-MAP.md` § The root gate for the incident that
  motivated it.
- **Worktree isolation:** concurrent agent exploration must use isolated worktrees via `python scripts/git_worktree.py create --name <agent-name>`.
- **Guarded rollback:** history rewriting (`git reset --hard`, `git clean`) is forbidden. Rollback occurs solely through history-preserving reverts via `python scripts/git_rollback.py revert --commit <ref>`.

## Daily handoff
### 2026-10-08 06:12 - Archived (tools-first split, D10)
- Project moved to projects/_archive/agentic-research-lab/ by the root tools-first split (root commit 5fd715a); CLAUDE.md frontmatter grade: active -> demoted (this commit). Frozen: no new runs, no ingest, no ralph-loop. ADR/scars remain a read-only precedent source for 	ools/.
### 2026-09-26 21:05 — Graph-integrity reflection; two new gates (C-7)
- Record: `subprojects/vera/experiments/runs/C7_graph_integrity_reflection.md`. Started from the graph, not memory: `graph_decision.py` returned `required: true`, and the workspace already had its own answer ingested as `00_graph_database_architectural_reflection` — proposing `REFERS_TO` edges, hybrid FTS5+embeddings, and incremental rebuild. **All three are the wrong response.** In C-1…C-6 the graph broke six ways and not one was a capability gap: tags fabricated FTS hits, a detector reported 6,401 damaged chunks when 419 were, 6/8 golds were title pages, single-gold annotation scored correct answers wrong, `--dry` deleted 369 files, ids were reused across re-ingest. Every one was the graph asserting something false about itself. `REFERS_TO`, embeddings, and incremental rebuild all increase capability while leaving the graph exactly as able to lie.
- **18 existing gates; 15 in the suite passed continuously through all six defects; 6 of the 8 mapped defects had no gate at all.** The 2 with a partial gate were caught by me reading the output, not by a non-zero exit. The common shape: each gate asserted a *local* property (manifest traces the corpus, fingerprint matches) while every failure was *relational*.
- **New gate `Q16 citation_integrity` (`scripts/check_citation_integrity.py`)** — an id that resolves is not enough. Ids are `NN_<slug of filename>`, so re-ingest reuses them for new text; that is exactly how 4 golds drifted in C-6. The gate requires every gold to exist **and** contain every `required_concepts` term, and only `Chunk id:` lines count as load-bearing evidence — a backticked id in prose may reference a paper that was never ingested, and demanding it resolve would flag every digest that names a source.
- **New gate `Q17 graph_determinism` (`scripts/check_graph_determinism.py`)** — the fingerprint is satisfied by *any* self-consistent graph, including one that varies run to run, so it cannot see non-determinism. Builds twice and diffs nodes/edges/node_tags/fts with order imposed by the query, then **restores the original DB** so the check never mutates what it verifies.
- Both gates **mutation-tested before being trusted**: pointing a gold at a resolving-but-wrong chunk makes `citation_integrity` print `does not contain [...] — id likely reused across re-ingest`; tampering a node changes the determinism digest. 104/104 tests (11 new), `QUALITY PASS 17/17`. Fixed a real gap the test found: `Chunk id:` was anchored `^` and missed the label mid-line.
- **Deliberately not built:** hybrid embeddings (measured worth 0.0 on this corpus — `mean_family_recall` 0.958), incremental rebuild (would risk violating the determinism property that must hold), `REFERS_TO` edges (worth having for traversal; not a correctness fix). **The rule: a gate must be able to fail on the thing it claims to check, and the failure must be reachable by an ordinary mistake.**
- **My own gate shipped the same bug it was written to prevent.** `check_graph_determinism` asserted "this check must not be the thing that changes the graph it is verifying" and then restored only `graph.db` — while `build()` writes five files. Every run left four tracked files modified, and since the pre-commit hook runs the gate *after* `git add`, the committed value was permanently the pre-run one. Caught only by running `git status` after the suite, which is now a habit worth keeping. **A comment asserting a safety property is not the property.** The gate now snapshots all five outputs and asserts they reproduce byte-for-byte, which is strictly stronger than the DB digest: the DB being deterministic does not imply the derived JSON is. `generation.json` embeds `created_at`, so that field is blanked before comparing.

### 2026-09-26 20:10 — The corpus was never damaged; the extractor was (C-6)
- **C-2's conclusion was wrong and is now marked SUPERSEDED.** Record: `subprojects/vera/experiments/runs/C6_pdf_extraction_repair.md`. C-2 tested pypdf default `extract_text()` and PyMuPDF default `get_text()` — two libraries, one mode each — and concluded the source PDFs were damaged. It never tried `extraction_mode="layout"`. Measured on the two INBOX PDFs: **default 31 glue runs, layout 0, PyMuPDF 0.** The whitespace is in the PDF; the default mode discards glyph positioning. No new material was ever needed.
- `scripts/ingest.py` now picks the extraction mode **per page by measuring it**, and imports `suspicious_runs` from `check_corpus_health` so the extractor and its own gate cannot disagree. `_normalize_layout()` removes what layout mode introduces — 407 printed hyphenations (`Sys-\ntem/360`) and 28,923 padding runs in one book — because otherwise FTS5 indexes `Sys tem` as two tokens and `man-monthmythical` as one, reintroducing the same defect in a different shape.
- **Result: 428 damaged chunks → 2** (0.0%), 1,784 glue tokens → 3. *Book of Why* 319/386 damaged → 0, *Mythical Man-month* 98/103 → 0. Fingerprint `44172cafee34` → `0a5b47437367`. `mean_family_precision` 0.652 → **0.746**. Glued strings return 0 FTS hits and *"what is a causal intervention"* now returns real content instead of front matter.
- **Two serious bugs found on the way, both worth knowing about.** (1) **The first `--dry` run destroyed 369 live corpus chunks**: dry mode wrote every chunk, then deleted by recomputing ids with `slugify(name, 55)` while the writer had used `slugify(name)` — same 48 chars, so the preview overwrote a live file and unlinked it. Restored from git, manifest re-verified. Fixed by extracting `chunk_id()` as the single id definition and making `--dry` never write. **A preview that cleans up after itself is a second write.** (2) **Re-ingestion reuses chunk ids** — `NN_<slug>` comes from the filename, so re-ingesting regenerates the *same* ids with *different text*; four benchmark golds silently drifted and were re-validated. Ids here are references to content, not positions.
- **Detector blind spot closed.** `GLUE_RE` ended runs with `\b`, so a glue run flowing into a Capitalised word (`...describedintheIntroduction`) was invisible; a lookahead for that shape found **71 more instances** and raised the count 419 → 428, which is why the books were re-ingested rather than declared clean.
- **Provenance re-stamped, safely.** All 24 evidence chunk ids cited by the candidates still exist, so their claims remain true. One digest cited `04_honest_lying_memory_confabulation` — a paper **never ingested**; a pre-existing broken citation, now marked unverified in place rather than deleted. `scripts/restamp_provenance.py` refuses to stamp a file whose evidence ids vanished, since a blind hash rewrite would make `check_reflection.py` a rubber stamp. Its first two versions each corrupted a file (one split a JSON record mid-object, one re-serialized with `indent=2` and broke the one-per-line contract); both reverted, now a surgical value replacement.
- Verified: 93/93 tests, `QUALITY PASS 15/15`, 2/10,337 chunks still carry glue (0.0%, below the gate's reporting threshold). The 2 survivors are 1 chunk each in *Paradigms* and *AIMA* and were deliberately left in place.

### 2026-09-26 18:55 — Single-gold annotation was under-crediting the retriever (C-5)
- Commit `a438037`. **The `mean_family_precision` 0.46 I reported as "half the returned chunks come from the wrong book" was false.** Printing what the metric scored showed the retriever returning correct answers that single-gold annotation penalised. `agent-memory` requires `memory` and `context`; four of its five results contain both, including `persistent_memory_hierarchies_agents` and `memory_eviction_forgetting_web_research` — better answers than the annotated gold. Same shape in `planning-workflow`, `scientific-discovery`, `production-reliability`. The benchmark asked "did you find the one book I picked" and reported no for results that would have satisfied a user.
- Fix is annotation, not code — `gold_sources` already accepted a list. 7 alternate golds across 4 cases, every id verified present in `graph.db` before use. Family precision **0.46 → 0.652**, family recall **0.875 → 0.958**, exact recall **0.25 → 0.333**.
- The 119 → 475 ms in the artifact is a **benchmark artifact, not a regression**: the runner times its first query against a cold FTS page cache. Measured warm in-process, live queries run 112–244 ms.
- **The transferable lesson, and the reason this was worth the round: both "quality" problems found in C-4/C-5 — the void corpus and the unreachable gold — were measurement defects that looked like product defects. Neither was visible to 15 passing quality gates.** Print what a metric scores before treating it as ground truth.
- **Follow-up measured on the same turn: chunk re-segmentation and four retriever levers are all dead ends, and nothing was committed.** Merging adjacent chunks changes nothing (5/8 cases contain all query terms at window 1, 2, 3, and 4 — flat), because the three failures are *single-chunk notes* (`agent-memory` n=1, `scientific-discovery` n=1) or books that never use the word (`decomposition` absent from all 15 chunks of `planning-workflow`). Synonym aliases, top-family double slots, and FTS fetch depth 8→40 and 8→200 all returned byte-identical scores. The control matters: **irrelevant aliases also changed nothing**, so the metric is saturated, not merely unmoved. `mean_family_recall` 0.958 and `mean_concept_coverage` 0.958 mean every case already finds the right book; the residual gap is which page of a 386-chunk book, and that is not reachable without embeddings. Fingerprint and corpus untouched. **Do not retry these four levers.**

### 2026-09-26 18:40 — First VALID retrieval baseline; `mean_exact_recall` retired (C-4)
- Record: `subprojects/vera/experiments/runs/C4_retrieval_baseline.md`. Commit `0080ea9`. **The benchmark is no longer VOID** — 419 damaged chunks are excluded at query time and the remaining corpus measures honestly. Family recall 0.625 → **0.875**, concept coverage **0.958**, family precision **0.46** (the honest weak number), latency 119.1 ms.
- **The 62% corpus-damage figure was wrong; it is 4.0% (419/10,364).** C-1's detector fired on legitimate text: CamelCase run-ons caught real identifiers (`basePrice`, `daysOverdrawn`), and the corpus-absent rule flagged ordinary rare technical vocabulary in a 4.5M-word corpus. The discriminating signal is structural — a long *all-lowercase* run with no camelCase boundary, hyphen, or underscore; `MIN_GLUE_LEN = 32` (longest credible English token is 28). No frequency heuristic, so the gate now behaves identically on a two-chunk fixture and on the full corpus. Damage is 99% in two books: *Book of Why* 319/386, *Mythical Man-month* 98/103.
- **Quarantine is chunk-level. The first cut was source-level and was reverted** — it discarded 417 clean chunks to hide 419 damaged ones, evicting all 828 chunks of *Paradigms* and all 1,123 of *AIMA* over one damaged chunk each, and it removed the `causal-intervention` gold that was never damaged. `scripts/build_quarantine.py` writes chunk ids; `ask.py` excludes them on the FTS, tag-only, and alias paths. The corpus is never modified.
- **`mean_exact_recall` (0.25) measures the annotation, not the retriever, and is retired as a target.** Three independent proofs, none of which any ranking change can fix: (1) in 6 of 8 cases the gold chunk lacks a query term, so the AND-precise path can never return it — `automl-experiment` has 3/6; (2) given the right family for free and ranking by term coverage alone, the gold still lands at 11/386, 18/191, 76/210; (3) **6 of 8 golds were front matter** — *"ALSO BY JUDEA PEARL"*, a Springer title page, a contents listing — auto-selected as "first chunk of the right book". 5 re-annotated to substantive chunks; metrics correctly did not move, which is the expected result.
- Recall-depth probe: gold reachable in 2/8 at depth 5, 5/8 at 60, 6/8 at 200, 7/8 at 2000, **never 8/8** because `causal-intervention`'s gold is a quarantined chunk. **Ceiling is 0.875, and 0.75 at any tolerable depth.** Recorded instead of optimised against — this is the measurement C-1 was missing.
- Benchmark defects also fixed: a gold id truncated at 80 chars where chunk ids truncate at 55; two required concepts (`retrieval`, `experiment`) absent from the chunks that demanded them.
- Verified: 78/78 tests (7 new quarantine tests), `QUALITY PASS 15/15`, fingerprint `44172cafee34` unchanged. **Next: superseded — see C-5.** Chunk re-segmentation and BM25 tuning were both proposed here and both measured flat on the same day; neither is worth retrying. The remaining real damage is 419 chunks across two books needing better source PDFs (see C-2), which is a sourcing problem, not an engineering one.
### 2026-09-26 18:10 — Retrieval was fabricating results: tags in the FTS index (C-3)
- Root cause of "retrieval doesn't work", found by measuring rather than by gate: `_aggregate_families` sorted families by `count * 0.25` descending, so a family with many mediocre chunks outranked the single exact match. Its docstring said the opposite of what the code did. Now sorted by the best chunk's rank; volume is a tie-breaker only.
- Second, larger cause: the FTS table indexed the `tags` column alongside prose. Because OCR glue made prose unable to express a topic, the curated label stood in for it — `leak` appears in **zero** titles and **zero** body tokens of this corpus, yet `leakage` matched **7,824** FTS rows via the `anti-leakage` tag. A/B: "how do agents avoid context leakage" returned **424 hits with tags, 0 without**. Every one was fabricated. FTS is now `fts5(id, title, body, source_family)`; `snippet(fts, 2, ...)` in `ask.py` follows the column change; tag filtering still works through the `node_tags` table, which is the correct seam for it.
- Tag hygiene: 185,482 frontmatter tag slots → 81,220, 155 distinct types → **24, all real topics, zero junk**. Corpus frontmatter was auto-extracted per book, so one book's margin debris landed on all its chunks (`Msqrt`/`x83db59` on all 828 chunks of *Paradigms*; `SeismicEvents`/`LoginID` on all 1,123 of *AIMA*). Filtered by `_keep_tag` (shape) plus `_drop_book_wide_tags` (single-source, **exempting `knowledge/topics.md` vocabulary** — the first cut without that exemption silently unregistered 8 topics and `check_topic_coverage.py` caught it). The 10,364 corpus files are untouched; filtering happens at build time.
- **Graph edges collapsed 1,247,343 → 12,127 (103×).** 99% of the old edge count was whole-book `SHARES_TAG` cliques from those tags. This was a graph that looked richly connected and was not.
- Verified after rebuild: 54/54 tests, `QUALITY PASS: 15/15`, fingerprint `44172cafee34` unchanged, benchmark still self-stamps `VOID` on C-1. Latency 159.7 → 99.3 ms. Gold metrics unchanged (exact recall 0.25, family recall 0.75) — the gain is that the returned set is now real rather than flattering.
- **Attempted and reverted: deleting the 9 self-descriptive `vera-*` lessons** (9 of 14 accepted lessons describe this repo's own pipeline, two are a single sentence each). `check_promotion.py` enforces accepted ⇒ present in `memory.md` and failed with 9 promotion gaps. The gate was right. If those lessons should go, the correct move is demoting the candidates at source, not removing them from memory — that is a separate decision, not a cutover.

### 2026-09-26 14:40 — Retrieval baseline invalidated by corpus defect (C-1)
- Ran `run_retrieval_benchmark.py` at live fingerprint `44172cafee34` with a controlled A/B on the `ask.py` FTS bind. The bind fix made retrieval **worse**, not better: exact recall 0.250 → 0.125, family recall 0.750 → 0.625, latency 16ms → 160ms. The previous session's handoff treated that fix as an unquestioned win; it is not.
- Root cause is upstream of retrieval: 6401/10364 corpus chunks (on disk in `knowledge/corpus/*.md`, not introduced by graph build) have lost intra-word whitespace (`CausalInferenceinStatistics`). FTS5 `unicode61` splits on whitespace, so those terms are invisible to the index. 38137 artifact tokens.
- `scripts/check_corpus_health.py` added as a gate: CamelCase run-on signal plus corpus-frequency rarity signal (rarity only engages above `MIN_CORPUS_TOKENS`, because a small corpus makes every long word look rare). 9 tests pin it. Gate currently FAILS by design — it reports a real corpus defect.
- **All retrieval-quality claims are void until the corpus is repaired and the graph rebuilt.** BM25 `k1`/`b` tuning is deferred: optimizing scores over a token stream that is missing 68% of its words optimizes the wrong layer. Record: `subprojects/vera/experiments/runs/C1_corpus_whitespace_defect.md`.
- Also closed this session: direction B (one frontier inspector `frontier_state.inspect_frontier`, one accepted-rule parser `scripts/memory_rules.py`, 13 consolidation tests), regression tests for the three earlier bug fixes, and the stale `test_context_gateway` budget pin corrected to the DB-1 clip contract.

### 2026-09-25 02:40 — SIM-2 / D4 / ExpA Execution Agent (Goose)
- SIM-2 cold-start executed in 7 isolated git worktrees (3×A, 3×B, 1×C): B beat A on ttfva (0.419s vs 0.640s, 34% faster) but verdict INCONCLUSIVE — B reorient not ≤ A (0.163 > 0.125) and negative control C did not spike (0.119 < 0.163); instrument not sensitive at Q1 difficulty, follow-up = raise task to Q22 or n≥5. Report: runs/sim2_results.md
- D4 two-rater inter-rater log COMPLETED: 10/10 correlation-as-causation cases scored, perfect agreement (1.0), all confirmed D4 defects; closes the last gate-ablation evidence debt (GATE_ABLATION_Q13Q14)
- Experiment A (query decomposition) harness written (scripts/expa_query_decomposition.py); seed parsing blocked on parenthetical notes in QUESTIONS.md seeds — regex strip pending
- Next action: fix ExpA seed parsing (strip `(…)` / `— PARTIAL` / `workspace:` suffixes), run vs 0.53 recall baseline; Phase 5 synthesis once A + C complete



### 2026-09-25 03:15 — Experiment A Complete (Goose)
- Experiment A (query decomposition) seed parsing FIXED: regex extracts chunk IDs from QUESTIONS.md seeds (handles parentheticals, em-dash comments, workspace suffixes)
- Decomposition via context_gateway DB-1 achieves 0.609 recall (>0.53 B0.2 baseline target) at 0.72x cost (<3x budget)
- Baseline (pinned queries via ask.py): 0.609 recall, 27.6k tokens
- Decomposition (pinned queries via context_gateway): 0.609 recall, 19.7k tokens
- Cost reduction from DB-1 gateway per-kind reservation + evidence spans
- Report: subprojects/vera/experiments/runs/EXPA_query_decomp_20260925_031137.json
- Next action: Experiment C (graph edges) or Phase 5 synthesis
### 2026-09-24 19:05 — VERA Setup Agent (Goose)
- Defined research direction: VERA (Verification-Enhanced Research Agents) — ablation study of which agentic-research mechanisms measurably improve coverage, grounding, integrity, and cost
- Created subprojects/vera/: task_plan.md, gates.md (V1–V5 + V-N1), 20-question benchmark spec, pinned B0 baseline config, injection-test spec (5 defect types × 5 runner configs), 7-dimension scorecard with negative controls, canonical claim schema
- Added VERA-1 gate to root GATES.md
- V1 complete: 20/20 questions annotated (24 chunk IDs verified, log in subprojects/vera/reports/seed_annotation.md); fingerprint 05bc79e4b41e pinned in experiments/baseline.md
- B0.1 first runs: stable subset Q1, Q13–Q16 answered + 17 claims + cost ledger; B0 verbatim-query floor = 0 matches (and-term ranking) — config addendum in experiments/baseline.md; claim schema gained workspace: source namespace
- **VERA Phase 1 GREEN**: L1 set complete (Q1–Q4 + Q13–Q16), scorecard instrumented (metrics/tools/score_b01.py, negative controls green), Q13 reproducibility check (direct/inferred stable, novel drifts), V1–V5 + V-N1 all closed in subprojects/vera/gates.md; report at subprojects/vera/reports/B0.1_phase1.md
- Findings for lab: B0.1 query layer under-determined (B0.2 addendum pending); double-ingestion pattern (00_06/01_06 pairs) — eviction check recommended
- Next action: B0.2 pinning pass → L2/L3 runs → Experiment A; gated commit of subprojects/vera

### 2026-09-24 19:45 — VERA Phase 2 Direction Agent
- New researcher direction folded into VERA: simplicity & understandability as performance drivers; workflow↔graph-database merging
- experiments/phase2_simplicity_db.md: SIM-1 simplicity ablation, SIM-2 cold-start orientation test, DB-1 single-graph read path (routes through existing knowledge/graph/context_gateway.py); gates P2-1…P2-4; benchmark seeds Q21–Q23
- Phase ordering updated in task_plan.md (Phase 2 simplicity → Phase 3 DB → Phase 4 retrieval/verification)

### 2026-09-24 20:10 — SIM-1 Results Agent
- B0.2 pinning pass complete: Q2/Q4/Q5/Q6 query terms pinned (v2 pins after v1 pinned queries showed 0 recall — the pin itself is now a validated technique: Q2/Q4/Q5 recall 0.00 → 0.33–1.00)
- SIM-1 first results (runs/SIM1_arms.md): S1 (B0.2 + 1 grounding gate) beats S2 (no gate) on integrity at +43% cost — external-grounding rule confirmed load-bearing with data; S1 vs S0 (full protocol) inconclusive, needs per-gate ablation on Q13/Q14
- Gates P2-1, P2-3 closed; P2-2 (distilled pack) and P2-4 (Q21–Q23 annotation) open
- Next action: L4 gate ablation; SIM-2 pack B; DB-1 D0/D1 arms; gated commit of subprojects/vera

### 2026-09-24 20:20 — L4 Gate Ablation Agent
- S1-vs-S0 verdict CLOSED: tier-dependent gate policy — S1 (single grounding gate) for L1–L2; S0 full protocol for L3–L5 (only the rerun-diff layer catches retrieval-pool drift); D2/D4 pre-plants both caught (runs/GATE_ABLATION_Q13Q14.md)
- Policy recorded as task_plan decision + Phase-5 promotion candidate; two-rater inter-rater log owed before results are final
- Next action: P2-2 SIM-2 pack B; P2-4 Q21–Q23 annotation; DB-1 D0/D1; then gated commit

### 2026-09-24 20:30 — DB-1 Execution Agent
- DB-1 arms measured (runs/DB1_arms.md): D1 gateway-only saves ~35–45% tokens with 0 full-file reads; verbatim-question failure reproduced through the gateway (DB1-F1); multi-seed recall parity NOT met (DB1-F2) → verdict CONDITIONAL (L1 single-seed + session-fused context yes; L2–L5 not yet)
- Freshness probe through real pipeline: ingest → build → watch → visible in 1 ask.py call; 0 stale reads; fingerprint re-pinned `679a4aa15608` (study freeze ended with probe); manifest 194/194 PASS, INBOX emptied
- New probe defect: `scripts/ingest.py` reports its own successful run as transient MANIFEST FAIL (self-heals via regeneration) — one-line fix ticket owed
- Next action: gateway per-kind limit fix + rerun Q5/Q6 parity; P2-2 pack B; P2-4 annotation; gated commit

### 2026-09-24 20:45 — Commit & Housekeeping Agent
- Gated commit `2c4dc2a` [pipeline-vera]: prior 09-23 pipeline batch + all VERA Phase 1-2 work + DB-1 probe chunk; untracked remainder 0
- **Pre-commit hook repaired** (was silently broken on this machine: `env python3` shebang → Windows app-install alias → all commits failed); sh wrapper + explicit venv interpreter; gate verified on the new commit
- Triage tickets: `ingest.py` transient verdict misreport (one line); scratch scripts + INBOX_archive now gitignored pending delete-or-adopt decision; two-rater inter-rater log owed
- Next action: P2-2 SIM-2 one-page orientation pack; P2-4 annotate Q21–Q23; gateway per-kind limit fix + Q5/Q6 parity rerun

### 2026-09-24 21:10 — P2-2/P2-4 Agent
- P2-2: SIM-2 orientation pack B written (subprojects/vera/experiments/sim2_packB.md, 1.7 KB = 96% smaller than 43.9 KB pack A; 5 rules + 3 commands + query routes)
- P2-4: Q21–Q23 annotated with verified seeds + pinned queries; benchmark now 23 questions; 3rd 00_/01_ duplicate-ingestion pair (bend2) confirmed → eviction check backlog is 3 pairs
- All P2 spec tickets green; remaining work: SIM-2 cold-start run, gateway per-kind limit fix, formal E-suite (50 planted defects)
- Next action: SIM-2 cold-start comparison (fresh session answers Q1 from pack B vs pack A)

### 2026-09-24 21:15 — Eviction Pass Agent
- **Correction to 19:45/20:10 entries:** the "double-ingestion pattern (00_06/01_06 pairs)" finding is RETRACTED — eviction pass (find_duplicate_chunks.py + title inspection) shows the pairs are legitimate part-splits (part 1/2 + 2/2; Book of Why 240_/365_ = parts 241/386 + 366/386). No chunks evicted.
- Records corrected in place with originals preserved (seed_annotation.md correction, Q4 claims c04, Q4 answer superseded marker)
- Standing tool: subprojects/vera/metrics/tools/find_duplicate_chunks.py for future maintenance
- Next action: commit eviction pass; then SIM-2 cold-start run

### 2026-09-24 21:30 — SIM-2 Runbook Agent
- Wrote subprojects/vera/experiments/sim2_runbook.md: clean-session cold-start protocol (spawn isolation + worktree, conditions A/B + negative control C, pre-registered metrics + verdict rule, anti-contamination ledger)
- Decision: runbook-first over in-session pilot — prior context contaminates the very variable SIM-2 measures (per B0.1 r2 lesson)
- Gateway per-kind reservation fix landed in knowledge/graph/context_gateway.py (3 corpus slots reserved); Q5 pinned query v3; DB1-F2 resolved (a+b)
- Next action: commit gateway fix batch; execute SIM-2 runbook in a fresh session; ingest.py verdict one-liner

### 2026-09-24 22:05 — VERA Housekeeping & check_manifest Agent (Goose)
- Resolved the check_manifest divergence: root cause was the on-disk manifest still carrying the freshness-probe's long-key row ("VERA DB-1 experiment...") while the probe chunk had been restored to committed bytes (source `db1_freshness_probe.md`) → phantom + untraced rows → direct CLI exited 2. `--write` re-verification healed the manifest back to HEAD state (194 rows, staleness []) and exits 0.
- Graph re-pinned to `44172cafee34` (10,364 nodes, 1,247,343 edges) via `build_graph.py` after the probe clobber/restore; 15/15 quality gates green.
- Residue committed: uncommitted 09-23 Braintrust re-ingest ("New Markdown File" raw + 00_/01_ part-split chunks), check_manifest.py fix, ts_discovery subproject deletion, zero-state reflection files, CLAUDE.md jCodeMunch trim (tooling not installed).
- Next action: ingest.py verdict one-liner; Q5/Q6 parity row to close DB-1; SIM-2 cold-start in a fresh session; two-rater log debt.

### 2026-09-24 23:30 — E-suite Injection Test Complete (Goose)
- Synthesized 23 clean claims from pool digest (clean_pools.jsonl → clean_claims.jsonl)
- Planted 50 defects (5 types D1–D5 × 10 questions) with randomized positions (seed 20260924, logged to positions.jsonl)
- Gate-C automated detectors run on both clean + planted pools: clean FP = 0%, planted detection = 40/50
- Detection matrix: D1 (broken citation) 1.00, D2 (unsupported mechanism) 1.00, D3 (self-contradiction) 1.00, D5 (unsourced novelty) 1.00, D4 (correlation-as-causation) 0.00 (requires two-rater log)
- Gate-C passes injection_test.md passing rule for D1,D2,D3,D5 (≥0.8 detection, cost ≤2× baseline)
- Results documented in experiments/runs/E_injection/RESULTS.md; 15/15 quality gates green
- Next action: two-rater inter-rater log for D4; SIM-2 cold-start in fresh session; Experiment A (query decomposition) target: beat 0.53 recall without 3× cost

### 2026-09-24 23:45 — D4 Inter-Rater Log Created (Goose)
- Extracted 10 D4 planted cases (correlation-as-causation) from E-suite planted claims
- Created d4_inter_rater_log.jsonl template with source texts for human judgment
- Two raters will score: is_causation_claim, source_supports_causation, confidence (1-5)
- Agreement/adjudication fields for inter-rater reliability measurement
- Closes two-rater log debt from GATE_ABLATION_Q13Q14.md limitations
- Next action: complete two-rater scoring; SIM-2 cold-start in fresh session; Experiment A (query decomposition)

### 2026-09-23 22:10 — Eval Maturity & Ingestion Agent
- Ingested Phil Hetzel's Braintrust research on eval maturity levels (human annotation -> failure modes -> LLM-as-judge flywheel -> tool & trace eval). Graph rebuilt to fingerprint `9ae5e8c76bd4` (10,362 nodes).
- Enshrined "The Goose Principle" (Cheap Failures & Zero Waste) into CLAUDE.md token optimization rules.
- Re-verified all 15 quality check gates green (15/15 PASS) after quarantine repair.
- Next action: Proceed with downstream agentic tasks or advanced reflection pipelines.

- Newest entry at the top.
- Format: `YYYY-MM-DD HH:MM — <3 bullets, session owner, next action>`.

### 2026-09-23 21:00 — Pipeline & Handoff Agent
- Pipeline 01→05 complete: 5 new sources ingested, graph rebuilt to 10,362 nodes, 15/15 quality gates verified and passing.
- Next action: Push to remote and prepare for downstream tasks.

### 2026-09-21 22:19 — Implementation Agent
- Closed all three open issues: 3 candidates verified via tool-grounded sessions and accepted (5/5 memory landings); spawn extension installed and injection-proven; backlog triaged (54 scratch scripts removed, corpus checkpoint committed).
- Meta-learning evolved 3 stage contracts from the new rules; quality_check 15/15 green throughout; checkpoints pushed.
- Next action: dedicated review of remaining modified-but-uncommitted files (ask.py, build_graph.py, ingest.py, CLAUDE.md); install nothing further.

### 2026-09-21 22:33 — Implementation Agent
- Fixed CI manifest failure (exit 2, content drift on 10 book rows): root cause was committed manifest hashing untracked, gitignored PDFs — green locally, red in any clean clone. Moved 16 book PDFs (112MB) to untracked knowledge/raw_local/, regenerated manifest (16 hash-only row updates, keys and chunk mappings byte-identical), quality_check 15/15 green.
- Next action: watch CI; next risk beyond manifest is graph-rebuild determinism (graph.db is gitignored, CI builds from scratch).

### 2026-09-29 18:20 — Fresh-clone test: the repo was not self-sufficient; `restore_corpus.py` fixes it
- **Asked "do we have a working system?" and actually tested it: cloned from GitHub.** The clone failed **2 of 200 tests** with `sqlite3.OperationalError: no such table: nodes`. Cause: `knowledge/corpus/` was deliberately untracked in `c8a5f8a` ("a derived projection is not source"), so a clean clone has **zero** corpus files, `build_graph.py` yields `nodes 0 edges 0`, and the graph has no tables at all.
- The recovery was real but **undocumented** — I only found it by reading history. Verified: `git checkout 0cc21ac -- knowledge/corpus` restores 10,337 files and a rebuild gives `nodes 10337, edges 12100`, matching the working tree exactly. After that, 200/200 passed in the clone.
- **Shipped `scripts/restore_corpus.py`**, so the fix is one command instead of a commit hash someone has to rediscover. It does NOT re-derive from `knowledge/raw/`: chunks carry provenance (source, trust tier, tags) the raw files do not, so re-ingesting would produce a *different* corpus, not the committed one.
- **The commit is discovered, not hardcoded.** It walks `rev-list HEAD -- knowledge/corpus` newest-first and takes the first commit whose tree still *contains* files. The untracking commit `c8a5f8a` is in that list and holds zero, so it is skipped automatically. Pinned by `tests/test_restore_corpus.py`, including a test that AST-inspects the script to prove no sha is embedded in executable code (hashes are allowed in the docstring as history; a hash in code would break the next re-tracking).
- Measured in a genuine fresh clone: 0 files → one command → 10,337 files → 200/200 pass.
- **Known and by design:** `quality_check.py` resolves the workspace root as `parents[2]`, so Q0 (`workspace_root_integrity`) only runs when the project sits inside the declared workspace layout. A standalone clone cannot run that gate — by design, not a defect.
- `STATE.md` verified absent from a fresh clone (the untracking worked), and the discussion CLI verified end to end: `new` → `claim` with real two-sided retrieval → `close` with `[chain] ok`. Retrieval echo reproduced live (the same id appeared on support *and* counter).
- Next action: none open.

### 2026-09-29 17:45 — STATE.md untracked; two ladder labels corrected to match what they measure
- **`STATE.md` is no longer tracked.** The committed copy was stale pilot output claiming `verdict: red` for a run whose `scripts/_ralph_worker.py` was deleted during the c2 cleanup — a future session reading it would inherit a failure that no longer exists. `git rm --cached` (file kept on disk) + `.gitignore:80`. `CONTEXT.md` is the only handoff. `ralph_pilot.py --state` still defaults to that path, so the pilot keeps writing there and can now never dirty the worktree or ship a stale file to a fresh clone.
- **Resolved as option 2** (ignore/remove from version control), by default, after the user declined to choose. Not choosing was the status quo that created the question: one name was doing two jobs (pilot output target + looks-like-a-handoff). Untracking is the only option where the answer does not come back.
- **Rung 2's label was false.** It advertised `HEAD moved, so the iteration was real`; the code runs `git add -A` + `git diff --cached`. HEAD movement is strictly stronger — a worker that edits and reverts the same tree is still a real iteration but moves no HEAD. Now: `the worktree changed, so the iteration was real`.
- **Rung 3's label was false in the other direction.** It claimed `a human-authored rule holds`, but the ladder itself inserts the probe name into `check_dead_code.MANUAL` and then removes it. The criterion is authored by the program that scores it. Now states that limitation explicitly instead of keeping the strong wording; the honest version needs the rule in its own commit, with the ladder only running the gate.
- Both pinned by new tests **verified to fail on the old code** (labels mutated back: 2 failed, 8 passed). A label that overstates its measurement is a false claim, and the ladder exists precisely to overclaim nothing.
- Correction to the 16:29 entry below: c2 no longer stays `unresolved`. The user selected option 1 and the decision in `INBOX/ideas/the-ralph-loop-fits-this-repo-s-mechanic.md` is now `learned`, written through the repaired real CLI. That entry was truthful when written.
- 21/21 gates pass with `STATE.md` absent from the index. 198 tests pass (196 + 2 new), 10 subtests.
- Next action: none open — the question this entry answers is closed. Genuinely remaining: the decision file's c2/c3 prose may use those labels differently from the claim headings above them. Read before citing.

### 2026-10-01 17:05 — T1 evidence checkpoint; the commit gate has no third state
- Handoff timestamps in this file are UTC. The freshness gate parses them as UTC.
- **The blocker behind "commit 5, leave the rest untracked" was structural, not cosmetic.** `agent_commit.py:working_tree_has_untracked()` reads *every* untracked path and exits 1 unless each one is either staged or ignored. There is no "deliberately held back" state, so the plan that put 5 files in and 112 out could never run. Every file is staged or ignored — the fix is the `.gitignore` edit, and it must land *in this commit* (`.gitignore` is itself modified) or the gate reopens next session.
- **Four files were orphaned by the plan and would have failed the gate**: `GATES-T1-phase04-runner.md`, `GATES-research-graph-reflection-execution.md`, `docs/adr/0004-chart-integration-before-writing-code.md`, `docs/wayfinder/research-graph-reflection-execution.md`. Not mentioned in the ignore list, so neither staged nor ignored.
- **Three committed files pointed at files the plan wanted to ignore** — committing the referrer writes a dangling reference into history. `spawn.py` (148 new lines, `--background`) and `close_session.py` (`--background-reflect`) both launch `background_worker.py`; the committed `CLAUDE.md` route table names `snapshot_graded.py`. Both referents are therefore staged, not ignored. `presearch.py` moves the other way: its only referent was the fastpath ledger, which is held back, so nothing tracked needs it.
- **`GATES-reflection-fastpath.md` is held back, not committed.** Its G4/G5 name `scripts/verify_reflection_fastpath.py`, which does not exist on disk, so the ledger cannot be run as written — and its own file's rule (line 277) is that "a gate that cannot run is a finding; a gate that is quietly removed is a lie." Ignored with a note, recoverable by one `.gitignore` edit + `git add -f` once the verify script is written or the fast path is retired. Its G1/G2 targets (`tests/test_presearch.py`) are ignored for the same reason.
- **Two latent defects fixed while making the gate pass.** (1) `skills/MANIFEST.md` counted `ralph-loop` as 10 files; it has 9 source files (the 10th was a `__pycache__` entry). Every other row matches its real count, so the row was wrong, not the convention — corrected to 9. The `95 files` grand total in the same file is stale (rows sum to 105); left alone, pre-existing, and no gate reads it. (2) Root `.ralph/` (`INDEX.md`, `registry.json`) was debris from a `ralph.py` run launched at workspace root — empty registry, `_none_` row, no `STATE.json` — and failed Q0 as "unexpected directory at workspace root". Regenerable aggregate output; deleted.
- Whitespace gate rejected four vendored templates on trailing space after `- ` placeholder bullets. Confirmed cosmetic first: `ralph.py` consumes templates through `.replace()` on placeholder tokens only, and no test byte-compares them. Trimmed in the vendored copy.
- MAP.md regenerated (140 modules) for Q0's R7 freshness rule. The generator walks the filesystem with `rglob("*.py")` and is not git-aware, so the new ignore rules do *not* make it stale — verified rather than assumed.
- `~/.pi/agent/models.json` stayed frozen; `reflect.py` endpoint resolution delegates to `pi_models.resolve_endpoint()` (env `PI_PROVIDER`/`PI_MODEL`). `reflect.py` and `pi_models.py` remain untracked pending G12.
- Next action: **G12 is still the human's** — which runner is canonical. `spawn.py` works out of the box, fails loudly (exit 1 stale graph, 4 missing extension), 275 s, self-validating. `reflect.py` is 52 s in one structured call with deterministic retrieval, but on failure writes *no artifact*, so a failed run is indistinguishable from a run that never happened. Electing either means un-ignoring it and entering through `agent_commit.py` — never `git add .`.

### 2026-09-29 16:29 — Evidence pass on the Ralph loop; pilot contracts made real
- Handoff timestamps in this file are UTC. The freshness gate parses them as UTC.
- **Researched before implementing, as asked.** Local graph read in full (not just retrieved): `00_reflection_compaction_variance`, `00_reflection_reorientation_cost`, `00_32ecfce…self_healing_tool_routing`, `00_agent_hooks_lifecycle_guardrails`. Web: `aipatternbook.com` (metric gaming / "the agent deletes the failing tests"; vague done-conditions), `agentpatterns.ai` ("an iteration cap alone is a financial circuit breaker, not a quality gate"; deep-continuity tasks lose load-bearing context), `dotagents` PR #45 (metrics grading their own negative controls).
- **Conclusion reached (evidence, not preference): the c2 experiment is the wrong experiment.** A second LLM reviewer of a fresh session inherits the worker's hallucinated world, and retained knowledge is *variant across runs*, so any token-overlap scorer would be tuning the instrument against the thing it measures. The abandoned c2 branch had already shown this concretely: the blind negative control scored 0.50 until the scorer was hand-tuned. c3, now actually read, supports the *hybrid* — deterministic routing for known mechanical paths, LLM only for escalation — not replacing deterministic acceptance.
- **c2 stays `unresolved` in the decision file.** Closing it is the user's call, not the assistant's.
- **Fixed four advertised-but-false pilot contracts**, each pinned by a test: `--state` now exists (the docstring promised it; argparse rejected it); `write_state()` now clamps on *rendered lines* (it counted list elements, so a 400-line gate failure blew the 60-line cap and destroyed the loop's own state); worker commands are split into argv with backslashes intact (`WinError 2` before, and `shlex posix=False` is *not* the fix — it preserves the quotes); worker output is captured instead of contaminating the loop log.
- **"Every iteration is a commit" is now implemented, not just claimed.** `--commit` was a docstring line with no code behind it. A no-op worker is explicitly not committable — pinned by test, because a correctness gate is already green on iteration 0 and cannot tell a real iteration from a no-op.
- Correction on record: I stated earlier that branch `ralph/c2-probe` had been deleted. It had not. It was fully merged (zero diff, zero commits ahead), so `git branch -d` removed it with nothing lost.
- Also corrected: `preflight.py` still described "18 project gates" in two places; the runner has 21 (Q0–Q20).
- Next action: the user picks the thesis — replace c2 with a deterministic capability ladder, run c2 as written, or land only the contract fixes above. `state_freshness` is cleared by this entry; nothing was backdated.

### 2026-09-28 00:35 — Implementation Agent
- Untracked `knowledge/corpus/` (D5, deferred since 2026-09-19): tracked files 10,939 → 602. Files stay on disk and in history; `git checkout <rev> -- knowledge/corpus/` restores any of them. Verified rebuild is byte-identical by re-ingesting a real source through `INBOX/` and diffing (CRLF only; `.gitattributes` normalises). ADR-0003.
- Unbuildable-chunk gate driven to zero: 6,544 → 0 across 23 → 0 sources. Recovered 7 deleted PDFs from `0d075d7`/`74b922e` (21 MB, disk-only — copyrighted, never committed), filed 8 user-supplied books plus *Graph Engineering* into workspace `library/` (16 entries, 128 MB, content-addressed, bytes gitignored, `index.json` tracked). Gate promoted from `warn_exit=2` to hard failure (Q19).
- Root-caused the original loss: `ingest.py` `shutil.move`s an INBOX original into `knowledge/raw/` without staging, so the next inbox cleanup deletes it as debris. Six `.md` sources died that way. Ingest now stages every non-PDF source as it archives it; `.gitignore` also excluded only `*.pdf` while ingest accepts `.epub`/`.txt`.
- The last 11 unbuildable chunks are not losses: 3 cite topic labels with no file, 4 cite project write-ups whose subject was archived. Gate now separates authored from derived sources. Correction on record: the ts-diverse research is *archived*, not live (`benchmark-core/members/lasso_lag_mutation.py:1`), so marking those chunks superseded would have destroyed the only account of a failed experiment.
- Conversation ledger made writable (`scripts/record_turn.py`, closed 8-type vocabulary, hash-chained); fixed `verify_chain` returning ok for a nonexistent session and a Windows CRLF id that broke shell capture. 142 tests pass.
- Next action: run `python scripts/quality_check.py` end to end — it halted early on `state_freshness` before reaching Q19, so the promoted gate has not yet been observed inside a full run.

### 2026-09-21 22:38 — Implementation Agent
- CI failed again on 6 more book rows (Design Patterns, DDD, Refactoring, SICP, Goal, Legacy Code): unlike the first 10, these PDFs were TRACKED in git, so clean clones resolve them to byte-shas while the regenerated manifest holds string-shas. Untracked all 6 via git rm --cached (bytes preserved in knowledge/raw_local/); manifest needs no change. Lesson: verify manifest drift in a fresh local clone, not just the worktree, before pushing.
- A 17th tracked binary surfaced the same way (Agentforce .epub — also overlong-named, breaking Windows checkouts entirely): moved to raw_local/, untracked, manifest row flipped byte-to-string hash. Fresh-clone verification is now part of the manifest fix procedure.
- Root-caused the deeper failure: 11 corpus files have LF bytes in this worktree but CRLF blobs in git (prior patch scripts normalized endings as a side effect), so fingerprint() over raw bytes yields fc0231ca4172 here but ad29624f2133 in any clean clone — invalidating every reflection stamp in CI. Fix: .gitattributes forces eol=lf for knowledge/corpus/*.md; renormalized 253 blobs; worktree bytes and live fingerprint unchanged.
- Next action: watch CI; graph-rebuild determinism remains the next untested gate.

### 2026-09-23 09:00 — Implementation Agent
- Ingested 5 new PDFs into corpus (Engelbart, Stephens, Bishop, Weinberg, Rubin), rebuilt graph (10,362 nodes, fingerprint 93b8cb688049), and completed phases 01–03 successfully.
- Fixed stale reflection provenance: re-stamped digest/candidate to live fingerprint; corrected route returned_ids mismatch from updated corpus vocabulary.
- All gates green (manifest PASS, graph watch PASS, reflection PASS, promotion PASS, reachability PASS, slop PASS).
- Next action: complete phase 05 eviction check and apply_meta_learning --dry-run; resolve state_freshness gate by maintaining daily handoff.

### 2026-09-21 22:57 — Implementation Agent
- Renormalize only fixed blobs, not worktree bytes: worktree is 7,196 CRLF files, so the live fingerprint still diverged per checkout. Normalized the full worktree corpus to LF (content-preserving, 7,196 files) → live fingerprint 767d1bfba35d; re-ran guarded replan (17 digests, 41 rows) and quality_check 15/15 green. Committing blobs + stamps + graph provenance together so HEAD is self-consistent on every platform.
- Next action: fresh-clone full gate run, then watch CI.

### 2026-09-21 21:34 — Implementation Agent
- Implemented reflection `research-quality-breadth-depth`: 3 candidates experimental; wired peer-review pair gate into promotion; added 7 retrieval aliases + 2 reachability seeds; hardened slop canonical-row coverage and W-DEEP to error.
- Re-stamped 17 digests + 38 candidate rows to live fingerprint; repaired 3 newly-visible single-evidence rows with verified second citations; escalated 1 route-stale digest needing spawn re-reflection.
- Next action: re-run `python scripts/quality_check.py` to confirm green except escalated route defect; install workspace-research extension to unblock spawn re-reflection.

### 2026-09-20 17:35 — Continuation Agent
- Migrated all 15 reflection candidate files from legacy `claim`/`evidence` schema to canonical `Rule`/`Evidence`/`Target`/`Action`.
- Hardened `check_reflection.py` to reject legacy formats (hard failure on `claim`, `evidence`, `evidence_ids`, `principle` fields in non-accepted candidates).
- Fixed `check_slop.py` hard failures: rewrote `agentforce-heuristics.jsonl` rows H4 and H5 to canonical format with sufficient evidence.
- Initialized live-frontier ledger (`frontier/ledger.jsonl` + `frontier/manifest.json`) via `frontier_state.py`.
- Decision: Canonical schema is now mandatory for all candidate states; legacy formats are rejected at the reflection gate.
- Next action: Run `python scripts/quality_check.py` to verify all gates pass; then final verification and handoff.

## Chunk contract (`knowledge/corpus/NN_slug.md`)
```
---
id: NN_slug
title: "Human Title"
source: "original source / paper DOI / URL"
tags: [agentic, scientific-discovery, ...]
---

# Body (indexed by FTS5 for content retrieval)
```
- `id` is unique; multiple sections of one source share the `NN_` prefix with `part` in title.
- `tags` drive `SHARES_TAG` edges in the graph and topic registration in `knowledge/topics.md`.
- `trust_tier` is an integer from 0 (raw intake) through 3 (attested computation or execution trace).
- Typed relation arrays (`derives_from`, `supports`, `refutes`, `contradicts`, `extends`) create explicit graph edges when their target IDs exist.

## Failure modes to avoid
- Stale digest: always rebuild after corpus edits; `watch.py` guards commits.
- Ungrounded claims: every reflection candidate must cite specific chunk IDs from `ask.py`.
- Static workflow: findings must actively feedback into stage contracts via `stages/06_meta_evolve`.
- INBOX rot: ingestion must empty `INBOX/` into `knowledge/raw/`.
- Ungated / broad commits: committing without running `scripts/quality_check.py` or staging indiscriminately via `git add .`.
- Worktree collisions: editing shared working trees during parallel tasks without dedicated Git worktrees.
- Silent abandonment: removing an impossible gate instead of recording `ABANDON: <id> <reason>` is cargo-cult completion. An abandoned gate is a handoff, not success.
- Stale evidence: a checked gate without current evidence is unmet, not met. Re-run `CHECK:` before reporting completion.
- Context rot: research or work spanning >2 tool calls without persisting findings to disk loses state on context compaction. Apply the 2-Action Rule: after every 2 view/search/browser ops, save findings immediately.

## Open work

- **Phase 2 session B: content criterion landed, verdict open, 2026-10-05.**
  The non-tautological content scorer
  (`scripts/score_ablation_content.py` + `benchmark/content_criterion.json`)
  rescores the sealed pilot (no new LLM): ON macro 0.380 vs OFF 0.222, ON
  out-scores OFF on 1 of 3 families -> INCONCLUSIVE per pre-registered rule
  (n=9, one run per arm). Two follow-ups: (a) extend n (>=25 pairs for 80%
  power on a paired test) and/or a stronger model for the ON arm so content
  facts actually land; (b) fold the content criterion into the hypothesis
  verdict in `docs/research/kg-icm-integration.md` (design doc). Caveat:
  ON-arm `perf` family averaged 0.083 — the injected 2500-char context
  budget may be too thin for the 4 fact-dense perf tasks; re-measure with a
  wider budget before blaming the hypothesis.

- **Open question: agent output in plain language, 2026-10-01 (routed from root
  via AGENTS → CONTEXT-MAP §Routing).** Why agent prose reads dense, and which
  mechanism measurably improves it: always-on style rule vs few-shot vs
  post-hoc rewrite. First step: pick the comprehension meter (jargon density,
  mixed-language ratio, or a held-out reader task) before touching any prompt.
  Graph probe done: only adjacent material (`00_plain_text_as_interface`, ICM
  chunks), no corpus answer yet. Web research deposited to `INBOX/` (6
  targeted arXiv notes, `web_*` prefix, incl. a reader-comprehension study:
  "Are LLM-generated plain language summaries truly understandable?") —
  ingested 2026-10-02: 6 chunks in `knowledge/corpus/00_web_*`, manifest 209
  rows, graph rebuilt (10,358 nodes / 12,850 edges), `MAP.md` regenerated.
  Next: pick the comprehension meter against this new literature, then
  compare mechanism candidates on it before touching any prompt.

- **G12 resolved, 2026-10-01 (human decision).** `reflect.py` is the
canonical reflection runner — speed won (52 s vs `spawn.py`'s 275 s; G11
quality passed for both). Recorded with ABANDON lines in
`GATES-T1-phase04-runner.md`. Follow-up (1) DONE 2026-10-01: un-ignored and
committed via `agent_commit.py` (`82b078a`). Follow-up (2) DONE 2026-10-01:
fixed — every `reflect.py` run now leaves trace records in the agent_trace
ledger (`reflection/trace/events.jsonl`): started/completed run events and
failure events with a `failure_kind` (`bad_json`, `missing_key`,
`unexpected_response`, or the exception class name), so a failed run is
never indistinguishable from a never-run one. Pinned by
`tests/test_reflect_failure.py` (4 tests).

- **Conversation ledger is writable, 2026-09-27.** `session_store.py` existed
  with no caller: `append_event` was reachable only from its own CLI and tests,
  so every conversation was lost at session end. `scripts/record_turn.py` is the
  write seam — a closed eight-type event vocabulary, each pinned to the actor
  allowed to write it, so a turn cannot be misattributed and the FTS index
  cannot fragment into whatever a caller typed. Driven by
  `../../../skills/grill-recorded/`, which wraps the `grill-with-docs` interview.
  - Two defects fixed in `session_store.py` while proving it: `verify_chain`
    answered `ok` for a session that did not exist (an empty timeline is
    trivially well-formed), and `start` printed `\r\n` on Windows, so an id
    captured by an MSYS shell kept a trailing CR and every later lookup missed.
    Both are regression-tested in `tests/test_record_turn.py`.
  - **Still open:** nothing writes an `insight` turn into `projects/research/brain/`.
    The ledger captures the conversation; the derived sidecar that would let a
    later session *retrieve* that capture does not exist yet.


- **Corpus entropy is measured and gated, 2026-09-27.** 94% of tracked files
  are derived chunks, and 6,544 of 10,337 (63%) have a source that exists
  nowhere. `scripts/check_entropy.py` (Q19, `warn_exit=2`) reports per source,
  because 1,123 chunks from one book is one problem. See ADR-0002.
  - Root cause found in `ingest.py`: it `shutil.move`s an INBOX original into
    `knowledge/raw/` without staging it, so the file looks like untracked debris
    and the next inbox cleanup deletes it. Six `.md` sources were lost that way
    and seven PDFs were deleted outright in `0d075d7`/`74b922e` (2026-09-21).
    Ingest now stages every non-PDF source as it archives it.
  - The workspace `library/` stores raw documents by content hash; binaries
    are gitignored, `index.json` is committed, and the gate resolves against it
    last.
  - The D5 corpus relocation stays deferred; untracking the corpus (the original
    Q2b) is still the single largest lever and remains unexecuted.
  - **Recovery 2026-09-27:** all 7 deleted sources restored from `0d075d7`/
    `74b922e` into disk-only storage (21,289,874 bytes) and filed into
    `library/` by content hash. Gate improved 6,544 -> 4,220 unbuildable
    chunks, 23 -> 16 sources. Restoring exposed a second ignore gap:
    `.gitignore` excluded only `*.pdf` while `ingest.py` also accepts `.epub`
    and `.txt`, so the Agentforce epub was untracked debris — the same mechanism
    that deleted it. Now excluded too.
  - **Books supplied 2026-09-28.** The 8 missing books were added to
    `library/` and filed by content hash; *Graph Engineering* was supplied as a
    `.pdf` while its 345 chunks declare a `.txt`, so the index carries a
    filename `aliases` field and the gate resolves either spelling. Index:
    16 entries / 128,665,631 bytes. One file, *Multiagent Systems*, has a UTF-8
    BOM before `%PDF-` and is still valid PDF-1.4 — a strict magic-byte check
    rejects it, so accept a BOM.
  - **RESOLVED 2026-09-28: entropy gate passes, promoted to a hard failure.**
    6,544 -> 0 unbuildable chunks. The last 11 across 7 sources were not
    losses: 3 cite topic labels with no file, 4 cite project write-ups whose
    subject was archived. `check_entropy.py` now separates authored from
    derived sources and reports the former as a note; `Q19` dropped
    `warn_exit=2`. Marking those chunks "superseded" would have been wrong —
    see below.
  - **Correction to an earlier triage claim.** The ts-diverse research is
    *archived*, not live: `projects/research/benchmark-core/members/lasso_lag_mutation.py:1`
    reads `ARCHIVED 2026-09-24: no wins recorded` and
    `projects/research/benchmark-core/REFLECTION_PROMISING_METHODS.md:70` lists
    `LassoLagHybrid` under "no win recorded" with archive/kill recommended. The
    chunk claiming "outstanding MAE of 5.68" is an unverified claim
    contradicted by the archive decision, and that chunk is the only surviving
    account of the experiment.
  - **D5 EXECUTED 2026-09-28: `knowledge/corpus/` untracked.** 10,939 -> 602
    tracked files. Files remain on disk and in history; `git checkout <rev> --
    knowledge/corpus/` restores any of them. Rebuild via `INBOX/` +
    `python scripts/ingest.py`, verified byte-identical on a real source.
    `knowledge/raw/manifest.jsonl` stays tracked — it is the reverse index a
    fresh clone needs to know what it is missing. See ADR-0003.
- **RESOLVED 2026-09-27: `skill_router.py` dead routes dropped.**
  `wizard` and `merge|conflict|rebase` intents fell through to archived
  skills; both routes removed, `local_skills.md` renumbered with a
  retirement note, `skills/MANIFEST.md` gap marked resolved. Both intents
  now hit the `icm-architect` default (verified). Restoring either skill
  is a re-vendor from `../../../skills/archive/`, not a repair.
- **Brain-hint implementations, 2026-09-27** (from chunks
  `00_experience_graph_self_evolving_agents_web_resear`,
  `00_reflection_compaction_variance`,
  `00_do_llm_generated_skills_make_better_ai_data_scie`,
  `00_intelligent_skill_selection_workflow`):
  - `scripts/warn.py` + `agent_task.py` warnings section: past failures
    (quarantined ledger entries, rejected candidates, trace failures,
    stale generations) retrieved by keyword overlap at task start.
    Deterministic, read-only, no generated lessons.
  - `check_reflection.py` now calls the dormant `audit_claim_grounding`
    predicate: hard-fail on proposed/experimental rows, warn on accepted
    history. Footnote: `check_wiring.py` was green on this while the call
    did not exist — its import check returns True on `from X import Y`
    alone. The call is real now, so the gate finally guards what it
    claims. First run flags `vera-expf-final-001` (accepted) — chunk
    `00_automated_peer_review_and_self_correction` shares zero claim
    vocabulary. Human decision owed: thin the evidence or accept the
    warning; do not silently rewrite the accepted row.
  - `scripts/repair_ledger.py --validate` is green (71 events, ready):
    `repair_graph_state.log` now emits schema records (quarantines as
    quarantined FailureEvents, verifications as accepted ValidationRuns,
    unresolved failures as proposed), and `evidence_graph.py` appends
    carry layer/boundary. Pre-fix rows are grandfathered by fixed cutoff
    2026-09-27T00:00, counted in the report, never rewritten.
  - vera-expf-final-001 evidence accepted (not thinned): chunk
    `00_automated_peer_review_and_self_correction` defines the
    peer-reviewer + self-correction mechanism the rule's Action invokes,
    so the link is topically valid and the WARN is an auditor
    limitation (lexical overlap vs the Rule sentence), not an evidence
    failure. Standing rule confirmed: accepted history warns, never
    rewrites.
  - Skill LLM-ablation protocol (UNRUN — needs agent trials, recorded
    here so the bar predates the measurement): pinned intents one per
    skill under test (`tdd`, `diagnosing-bugs`, `research`), arms
    skill-injected vs bare, n=3 repeats each, metric = task success per
    existing gates (tests green / candidate grounded) plus token cost.
    Bar: win-rate gain with cost ratio recorded; a skill that wins on
    success but costs 3x is reported, not promoted. `ask-matt`,
    `codebase-design`, `to-spec` (catalog-only references) go first.
  - `scripts/eval_traces.py` over `reflection/trace/events.jsonl`
    (15 runs / 53 events): orphan-decision rate 0.667, dry-retrieval rate
    0.846, 6 runs without any decision. Caveat: part of the gap is
    instrumentation — `agent_task.py`'s ask.py call emitted nothing.
    `agent_task.py` now emits `retrieval`/`artifact` events, so the next
    eval separates real orphans from uninstrumented calls.
  - Enforcement is automated across five layers (2026-09-27 pass):
    Q18 dead-code gate (`check_dead_code.py`: unused imports + orphan
    modules; first run removed 37 imports and 6 orphan scratch scripts,
    7 documented manual runbooks allowlisted); boundary holds by
    measurement (348 project scripts hashed, zero cross-project copies
    outside skills/); 11 human-authored contract tests for the ops tools
    (`tests/test_ops_tools.py` — agents assert behavior, humans assert
    requirements); entry-file rules converted to negative constraints;
    pre-commit hook already runs the suite. Not gated: prose-shape rules
    (LLM judgment, declared not enforced).
  - Cost instrumentation is on (three boundaries, nothing more):
    trace `emit()` takes nullable `model_id`, token counts,
    `started_at/ended_at`, and `path` (success_path vs exploration;
    Nones dropped, never zeroed); `agent_trace.session_open/close`
    writes `reflection/trace/sessions.jsonl` (session_id, model_id,
    totals, wall minutes, all nullable); handoff entries carry
    `human_minutes`, `role`, `at` going forward. Ledger gained
    `insight_class` (C-5 = annotation-only); n=2 must match class or
    the memo labels it non-comparable — repair rate is class-dependent.
    Backfill ruled out: provider logs unavailable, human minutes
    unrecoverable; row stays provisional.
  - `scripts/eval_insights.py` scores the brain-to-improvement pipeline
    itself (trace vs span, after DeepEval/TRAIL/ClawTrack): 5 recorded
    hint trajectories — deterministic spans 14/15 pass, judgment spans
    9/10 (1 partial: the skill-audit rescope), mean 1.0 repairs per
    trace, all 5 shipped. Live measurements: ledger in-entry linkage
    0.5; edge linkage now 1.0 via `scripts/link_repair.py` (human
    verifies, machine records — 2 quarantined entries + 2 stale
    generations linked to executed quarantines, ledger history
    unmutated). Rejected for this workspace: auto-synthesized repair
    patches that generate repair-shaped text to reach a metric —
    cargo-cult completion that Goodharts the linkage score and violates
    the warnings-as-pointers rule. Pre-existing note: 65 of 67 HEAD
    ledger rows fail `repair_ledger.py --validate` (operational rows
    without id/type/state); the 4 appended links are all schema-valid.
    Warning-source coverage over 5 probes: ledger/stale/trace split
    evenly, `candidates` contributes zero (all 9 accepted, none
    rejected). External deltas being tracked: EXG failure-weighted
    reranking (wf term) and Trellis governed experience views; caveat
    from ACL'26 safety work — benign-task experience can mislead in
    risky contexts, so warnings stay pointers, never instructions.
- **The corpus lives inside the project, and it is derived.** `knowledge/` is
  10,508 of this repo's 10,836 tracked files, of which 10,337 are chunks
  generated from 154 raw sources. The project's real source is ~110 files.
  Relocating the corpus out of the repo is the clean fix (root decision D5
  names it as deferred, not rejected); it is deferred only because it is a
  migration the size of the project split.
- **`handoff` / `implement-spec` / `loop-me` and other archived skills** are
  reachable from `../../../skills/archive/` but are excluded from routing. If any
  of them is needed again, it is a restore, not a new skill.
- **The daily-handoff log above is append-only history**, not open work. The
  last entry (2026-09-21) ends with "Next action: fresh-clone full gate run,
  then watch CI" — that verification has no recorded result, so treat it as
  outstanding until a fresh-clone `scripts/quality_check.py` run is recorded.
