---
type: Concept
title: DECISIONS
generated: { by: okf-enforcer/0.6, at: 2026-10-23T19:33:52Z }
---

# DECISIONS.md — workspace

Why the portfolio looks the way it does. One entry per decision, newest last.
Each entry records the decision, the reason, and what was rejected — the rejected
options are the part a future reader needs, because they will otherwise propose
one again.

---
## D16 — Keep tool chunks indexed but filter diagnostic evaluation by type

**Decision.** Keep `tool` chunks in the derived FTS5 corpus for drill-down, but
retrieval evaluations for failures use `--type error` and evaluations for choices
use `--type decision`. Do not silently delete tool chunks.

**Why.** The full corpus contains 40,756 tool chunks out of 100,173 (40.7%).
The three previously failing evaluation cases become attributable to ranking
noise when evaluated without a type filter; the error-focused query is the
actual contract for failure recall. Keeping the chunks preserves context while
making the measurement answer the intended question.

**Rejected.** Deleting tool chunks at ingest, which loses command evidence and
cannot be reversed without a rebuild. Global rank weighting is deferred until a
separate mixed-type benchmark demonstrates a benefit rather than being guessed.

---
## D17 — Keep the workspace gate all-or-nothing

**Decision.** A stale workspace-wide report blocks all commits. Fix the report or
its source data; do not allow a known-dirty check to be bypassed for unrelated
staged work.

**Why.** The gate protects generated views and live numeric claims. Allowing a
known debt would make the next commit carry an explicitly unverified workspace
state and would turn the gate into an advisory list.

**Rejected.** Per-check debt exemptions and `--no-verify`; both hide a known
failure and weaken the single source of truth. The report blocker was instead
fixed at its source and recorded in `docs_reviews_stale_quote`.

This file is a **catalog of decisions**, not a log of work. The portfolio map is
`CONTEXT-MAP.md`; the promotion rubric is `TOOLS.md`.

---

## D1 — A tool is a project, not a staging area

**Decision.** Anything being built, tested, or polished for effectiveness is a
project under `projects/research/`, with its own entry file and its own contract. There is
no separate staging layer between "idea" and "project".

**Why.** A tool at 60% effectiveness is not a different *kind* of thing from a
project — it has the same inputs, outputs, and open questions. Giving it its own
lifecycle stage would mean a second set of rules for the same kind of work, and
two places to look when asking "what are we working on".

**Rejected.** A root-level `_tools/` staging folder. It reads as a natural
counterpart to `_archive/`, but it makes evaluation a *peer* of the work being
evaluated, and it invites tools to accumulate there indefinitely.

**Consequence.** Project count grows faster than the number of subjects. That is
the accepted cost; the entry file is the thing that keeps it navigable.

---

## D2 — Grading a tool reuses the model lifecycle vocabulary

**Decision.** Tools are graded **PROMOTE / REJECT / DEMOTED** — the same three
verdicts already used for forecasting models in
`projects/research/etth1-h720` and `research-engine`. A tool is promoted only on recorded
measurements plus a stated bar, never on impression.

**Why.** The discipline already exists and works. A second vocabulary for tools
would be a second dialect in the same workspace, and nothing would translate
between them.

**Rejected.** Inventing a tool-specific lifecycle. Also rejected: DEMOTED meaning
"deleted" — a demoted tool is *kept*, with the measurement that demoted it. That
is what makes the workspace carry its own negative results.

---

## D3 — Graduation is copy-then-delete, in one commit

**Decision.** When a tool is promoted, the code is copied into the target
project and the original is deleted **in the same commit**. A duplicate never
exists across two commits.

**Why.** "Copy and merge" are different operations and the workspace needs one
rule. A copy that outlives its commit is a second home and will drift.

**Rejected.** *Hand-merge* — correct only when the tool collides with existing
code, which is the rare case and should be an explicit per-tool decision.
*Reference-don't-copy* — this is what `skills/` does and it does not work for
tools: a project depending on a mutable folder has no stable input, which is
exactly what a project must have.

---

---

## D4 — Every project declares its grade in frontmatter

**Decision.** Each project entry file (`CLAUDE.md`) declares
`grade: candidate | active | demoted`. The root gate fails a project whose
entry file declares none.

**Why.** A tool is a project (D1), and the portfolio now mixes a 10,836-file
project with a 4-file one. File count is not a usable signal, and a name prefix
(`_candidate-`) reads as `_archive`, which is the one folder nothing routes to.
The field sorts the map and survives a candidate outgrowing its origin.

**Rejected.** A `_candidate` name prefix — pollutes the projects table and
conflates "not real" with "finished". No marker at all — entry-file length is
only a signal until a candidate reaches 30 files, which D1 makes likely. The
rejected `grade: promote/reject` values belong to *tools* (D2); a project's
entry file records position in the portfolio, not a verdict on a measurement.

**Cost, accepted.** A stale `grade` is worse than no `grade`, so the gate
asserts the field exists. A schema with no gate is a schema that decays.

---

## D5 — Small means few roles, not few files

**Decision.** No numeric file-count limit on a project. "As small as possible"
means as few **roles and functions** as the subject admits, with clear inputs,
outputs, and usage per module.

**Why.** `agentic-research-lab` is 10,836 tracked files, 10,508 of them under
`knowledge/` — but its source is ~110 files. The 10,337 chunk files are a
*projection* of 154 raw sources, i.e. derived data, not 10,000 roles. A
file-count gate would punish the wrong thing and push someone to hide the
corpus in an archive; it measures bytes, not complexity.

**Rejected.** A hard file-count gate — punishes corpora for being corpora.
Structurally relocating the corpus out of the project — technically correct and
rejected here only because it is a migration the size of the project split, and
it is not required to make the property true. Revisit if `knowledge/` grows
past what its raw sources justify.

---

## D6 — The root is a git repository

**Decision.** `workspace` is version-controlled. `DECISIONS.md`,
`CONTEXT-MAP.md`, and `TOOLS.md` get real history, authorship, and diffs.

**Why.** The root previously had no version control, so every decision made
here existed only as commit messages inside individual project repos, or not
at all. A decision catalog without history cannot show that D11 reverses D1.

**Rejected.** Keeping `DECISIONS.md` unversioned (accepted for its size, not
for its role). Workspace-level decisions in one root file, project-level in
each project's `docs/adr/` — this *is* the chosen split; it is listed here
because the alternative was a single file accumulating forever.

**Cost, accepted.** A root `.gitignore` and `.gitattributes` are now required
(CRLF: every project repo hit that warning during the split).

---

## D7 — A project carries its own open work

**Decision.** Every project `CONTEXT.md` has a `## Open work` section. The gate
requires the heading to exist; it does not require the heading to be non-empty.

**Why.** Measured: `datasets` 0 of 23 files mention a caveat, `research-engine`
2 of 25, `brain` 2 of 4. Two places do it well —
`knowledge-retrieval/references/measurements.md` (a retired metric with three
proofs) and `SAB_L_H720_RESULT.md`. Nothing *required* it, which is why the
good pattern exists in exactly two places.

**Rejected.** A per-project `OPEN-WORK.md` — a second home per project for
information that belongs inside the contract, and the very thing D1's
single-source rule warns about. No requirement at all — this is the
convention-only outcome that produced the 0-of-23 measurement.

**Amendment.** "## Open work — nothing known" is a true, useful sentence. What
must not happen is a missing heading going unnoticed.

---

## D8 — Every project owns a `skills/` home; contents are lazy

**Decision.** Every project has `skills/` plus a `MANIFEST.md` recording, per
vendored skill, its upstream name and the date vendored. The gate requires the
folder and the manifest to exist; **contents may be empty**. A skill is
vendored on first use, never speculatively. The root `skills/` keeps a full
redundant set, because root-level changes are made there.

**Why.** Projects must be self-contained: a project that resolves a skill from
a mutable sibling folder has no stable input. Redundancy is accepted
deliberately. But 6 of 7 projects reference **zero** skills today, and
vendoring all 24 into 7 projects is 693 files / 3.5 MB of files nothing reads.
The always-required thing is therefore the *place* and the *record*; the
never-allowed thing is using a skill you did not stamp.

**Rejected.** Non-empty `skills/` — forces 3.5 MB to satisfy a rule. Symlinked
skill folders — the ideal (one home, no drift) and **proven not to work on
this machine**: `os.symlink` raises `OSError: [Errno 1314]` without admin.
Conventions without a gate — the outcome that produced every gap measured in
D7. Full copies everywhere — uniformity bought with files nothing reads.

**Cost, accepted.** Once stamped, a vendored copy is not updated from upstream.
A correctness or security fix to a root skill does **not** propagate. That is
the trade for locality, and the stamp is what makes the staleness legible
instead of mysterious.

---

## D9 — `MAP.md` is generated, never hand-edited

**Decision.** A project with source code has a generated `MAP.md`: one row per
module — name, role, inputs, outputs, used by. Built by
`scripts/build_project_map.py`; the gate fails if the committed `MAP.md` differs
from the generated one.

**Why.** "Clear usage of each module" is a *query*, not a vibe. Measured
coverage of per-file rows in entry files: `agentic-research-lab` 12 rows for 104
modules, `benchmark-core` 6 for 90, `datasets` 8 for 21. Only `brain` (2
modules) and `knowledge-retrieval` (no code) are covered. A 104-row module map
cannot live in a 60-line entry file, so it needs its own generated home.

**Rejected.** Roles in per-module docstrings with a folder-level `CONTEXT.md` —
puts the truth in the right place but makes the map unqueryable without reading
every file, which defeats "clear usage". A hand-maintained `MAP.md` — most
accurate, rots fastest; the 12-rows-for-104-modules measurement is exactly what
hand-maintenance produces. Module maps inside `CLAUDE.md` — breaks the 60-line
entry-file rule at any scale above ~10 modules.

**Consequence.** A module with no parseable docstring gets an empty role cell
rather than a guess; the gate reports it so the gap is visible.

**Amendment 2026-09-27.** The 60-line rule binds project entry files. The root
catalog (`CLAUDE.md`) scales with the project count and is exempt — it routes,
it holds no content, and R9 asserts its routes resolve.

---

## D10 — Archiving is two-stage: demote in place, then move to `_archive/`

**Decision.** Stage 1: mark `grade: demoted` in place with the measurement
that demoted it (TOOLS.md verdict). Stage 2, after a cooling period or an
explicit call: move the whole folder to `projects/_archive/`, which is
ungated and unrouted. One archive home: lowercase `projects/_archive/`
only — the uppercase `projects/ARCHIVE/` duplicate (2026-09-27) is merged
there and must not recur.

**Why.** In-place demotion keeps evidence where readers still look; immediate
deletion loses negative results. But a demoted project that stays in
`projects/research/` forever keeps paying gate costs (grade, open work, skills home,
MAP) for work nobody reads. `_archive/` is excluded from the gate by design
(check script `PROJECTS` filter) — that is the point of archiving.

**Rejected.** Delete on demote — loses the measurement. Keep demoted gated
forever — gate noise on dead work. Two archive homes (`ARCHIVE` + `_archive`)
— one of them is always treated as a live project by the gate and fails R4–R7.

---

## D11 — Experience is local; distillation is on demand

**Decision.** Each project gathers its own experience in place:
`## Open work` (required, D7) + `docs/adr/` (one file per decision) +
an optional `EXPERIENCE.md` (distilled good practices, written on user
demand, never continuously). The root never copies experience — it links.
Cross-project practices graduate only when the same lesson appears in ≥2
projects independently; then it lands in root `DECISIONS.md` as a new entry.

**Why.** A root-level experience file becomes a second home the day a project
updates its own copy and forgets the root. Locality keeps the lesson next to
the evidence (measurements, bars, negative cases). "On demand" keeps the cost
proportional: distill when asked, not on every commit.

**Rejected.** Single root `PRACTICES.md` — drifts from project truth within
weeks. Pure `OPEN-WORK` with no ADR — open work records what is unfinished,
not why a past call was made.

---

## D12 — Polyrepo with a root coordination layer (no monorepo migration)

**Decision.** Keep separate git repos per project (current shape). The root
is the coordination layer: `CLAUDE.md` (catalog) + `AGENTS.md` (terse agent
router, <2K tokens) + `CONTEXT-MAP.md` (relations) + interface contracts
(`CONTEXT.md` per project) + generated `MAP.md` per project, regenerated in
CI. Extract a module into its own project only on concrete cause:
independent release cadence, scaling, or team autonomy — never speculatively.

**Why.** The "merge small projects later is easy" heuristic is wrong about
where the cost sits: the merge is trivial, the boundaries are not. Clean
contracts + continuous integration carry the benefit; repo topology does not.
A coordination layer gives agents the system view (router + maps + contracts)
without paying a monorepo migration over 7 live projects.

**Rejected.** Monorepo now — migration cost over live forecasting lines for
no measured gain. "Build separately, merge later" without contracts — merges
into a bigger mess. Full MCP server now — router + generated maps cover the
need; revisit when a task demonstrably costs >50K tokens on navigation.

## Status

## D16 — Symbol-level retrieval for indexed code; `bash` output is the bigger fish

**Decision.** Query indexed code by symbol (`search_symbols` →
`get_symbol_source`) instead of reading source files whole. Wire jCodeMunch with
pi's `codemode` MCP exposure so its 91 tools never enter the system prefix.
Rules in `AGENTS.md`; measurements in `TOKEN-EFFICIENCY.md`; probes in
`scripts/mcp_schema_cost.py`, `mcp_call.py`, `tool_output_breakdown.py`.

**Why (measured, on this workspace's own transcripts).** `get_symbol_source`
returned 1,300 chars for a symbol whose file is 7,669 chars — 5.9×. Structural
queries (`find_importers`, `get_call_hierarchy`) answer questions grep cannot.
But the honest denominator: source-file reads are **12.1%** of all tool output;
`bash` alone is **59.4%**. So symbol retrieval addresses ~12% of context, and
cutting shell output is the larger, still-unaddressed win (D15's "cap tool
output" rule). The vendor's 96.5% / 28.3× is a per-read figure and is true; it
is not a share-of-context figure, and treating it as one overstates the win by
roughly an order of magnitude. Both numbers are recorded so the next session
does not re-import the headline.

**Why no enforcement hooks.** The PreToolUse/PostToolUse hooks rewrite client
settings and a global `CLAUDE.md`; pi has no such hook surface, and mutating
global config to change behavior conflicts with the workspace's own
"config ≠ working config" rule. The prompt rule is the enforcement that
actually applies. Per the vendor's own note, installing the server does not
break brute-reading on its own anyway.

**Rejected.** `direct` exposure (91 schemas in the prefix, and the vendor's own
docs show the block is paid once per cache lifetime, so the saving is ~10× less
than it looks). `jDocMunch` now (doc reads are 12.1% and mostly small files).
A tree-sitter/PageRank repo map of our own (D9 `MAP.md` already covers
orientation, and the measured addressable share does not justify a second
indexer).

**Settled.** D1-D16.

---

## D13 — The root stays a thin, strict research OS

**Decision.** The root owns routing, contracts, grades, and gates — nothing
else. No project logic in root. Each project owns one job, one interface,
one local gate. Growth is by composing verified small systems (Gall's law),
never by expanding scope or copying code across projects.

**Why.** Every failure class observed so far is a thickness failure: context
bloat (agents loading the ~4K root L1 pack as if it were the ~0.5K L0
router), interface rot (dependents re-vendoring the owner's contract),
derived drift (hand-edited generated files), gate theater (a gate that
cannot fail on what it claims), premature promotion (unresolved lessons
filed as verified practices). A thin root with asserted boundaries turns
each of these from a convention into a check.

**Rules (all already gated or stated; this entry names them together).**

1. Root stays a router: `AGENTS.md` / L0 pack points to exactly one project.
   Root holds `CONTEXT-MAP.md`, `DECISIONS.md`, `GLOSSARY.md`,
   `PHILOSOPHY.md`, `TOOLS.md`, and the integrity gate. L1 root pack is on
   demand, never always-loaded — one project's L1/L2 per session.
2. Every project has one contract (`CONTEXT.md`): one job, one interface,
   one `## Open work`. A project serving two subjects is two projects.
3. Cross-project only by link + contract test in the owner. Never copy;
   graduation is copy-then-delete in one commit (D3).
4. Generated artifacts are never hand-edited: `MAP.md`,
   `graph.db`, `graph_index.json`, `GRAPH-DIGEST.md`, fingerprints — rebuilt
   by scripts, freshness advisory (R7, 2026-10-01 gate trim); every file route named in a
   routing section must resolve (R9) — a cold agent follows routes, it
   does not remember workflows, so a dead route is how built work gets
   "forgotten". Mutation-tested: R9 fails on a dead file route.
5. Evidence before promotion: `EXPERIENCE.md` holds only verified practices;
   `## Known-unresolved` stays unresolved until a gate that fails on the
   defect passes. A gate must be mutation-tested on what it claims.
6. One project per session: read its `CLAUDE.md`, then its `CONTEXT.md`;
   load one contract + inputs only (~2–8K tokens).

**Priority order.** Root integrity first (gate fails → stop and fix). Then
the most-depended-on contract (`benchmark-core`). Then derived truth
(`brain`, graph reproducibility). Then read-path quality
(`knowledge-retrieval`: the number, the defect list, the gate per defect).
Expansion last: new projects are a last resort — the risk is unverified
composition, not too few projects.

**Rejected.** Monolith root with project logic; scope expansion of existing
projects instead of new composed ones; cross-project copies for speed;
hand-fixing generated files; promoting practices without a failing-then-
passing gate; loading multiple projects per session for "context".

---

## D14 — Fallbacks visible, gates mutation-tested (graduated D11)

**Decision.** Every fallback appears in the return, not just the console, and
every gate proves it can fail on what it claims (mutation test).

**Why (≥2 projects independently).** `datasets/EXPERIENCE.md` ("fallbacks must
be visible in the return"), `brain/scripts/ask.py` LIKE fallback, `datasets`
`test_stock_fetch.py` GBM fallback, `benchmark_scientific_datasets.py`
`except: continue` → `NaN`/`FAILED`. ARL Q16/Q17 mutation-tested gates;
`benchmark-core`/`brain`/`research-engine` assert gates that cannot fail.
Lesson pair "assert relational properties" (ARL, knowledge-retrieval) and
"quarantine chunks, never sources" (ARL, knowledge-retrieval) are recorded
here as graduated alongside.

**Rejected.** Silent fallback with console-only notice; gates that pass over
the defect they name; per-project-only practice with no root graduation.

---

## D15 — One model per session; cache stability beats model routing

**Decision.** Use a single model for the whole session. Never switch models
or thinking level mid-session. Roles like "architect" and "editor" are
thinking modes, not routing targets — no model-delegation split. If the
current model becomes unavailable, end the session and start a new one on a
different model. Token-efficiency rules live in `AGENTS.md`; the measured
evidence lives in `TOKEN-EFFICIENCY.md`, regenerable via
`scripts/pi_cache_forensics.py`.

**Why (measured, not assumed).** Over 29 sessions / 69.5M tokens: cache hit
ratio 78.0%. Attribution of every cold prefix (a turn with `cacheRead == 0`
and `input > 2000`) gives: non-caching provider 61.2% of wasted tokens
(`oc/nemotron-3.5-lightning-free` re-paid the full prefix 250 times, 4.0M
tokens, 0.0% hit ratio), thinking-level changes 12.5% (812K), model switches
7.7% (502K), compaction 5.6%, context edits 3.1%. The decisive observation:
caching is a property of the model, not the task — one model held 90.3% for
363 consecutive turns in a single session. So the lever is staying put, and
the second lever is turn count, since each turn re-pays the whole prefix.

**Why no routing.** Model availability is not stable for this user, so any
architect/editor split is either dead config or a mid-session switch — and
mid-session switching is exactly what cost 502K tokens here.

**Tooling scar (graduated from AGENTS.md).** `cacheWrite` was 0 in every
session: this provider tier has no write-side accounting, so cold prefixes
are invisible in cost data. Detect them via `cacheRead == 0`, never via cost.
And a wrong attribution looks authoritative — attributing every cold prefix
to the nearest preceding event blamed `thinking_level_change` for 67.9% of
waste, when a 0.0%-hit-ratio provider was the real cause. **Verify an
attribution against per-model ratios within one session before acting on it.**

**Rejected.** Architect/editor model delegation (unavailable models); a
runtime cache-ratio guard extension (cannot protect the first turn, needs
model IDs, and the audit scripts already answer it afterwards); a
role→model config file (maintenance cost with no measured gain over one
stable model).

---

## D17 — Hermes-side levers: cheap auxiliary compaction, 1h cache TTL, per-task metering

**Decision.** On the Hermes runtime (`C:\Users\Mateusz\AppData\Local\hermes\config.yaml`):
(1) `prompt_caching.cache_ttl` → `1h` — interactive CLI turns have >5-min gaps,
the 1h tier amortizes; Anthropic-wire tiers only, zero cost for the rest;
(2) `scripts/hermes_per_task.py` is the per-task token/cost meter (stdlib-only
read of `state.db` `sessions` + `session_model_usage`), so "tokens per
successful task" is a measurement, not an estimate.

**Why.** Official docs rate a cheap `auxiliary.compression` model "the single
most important knob" (summary cost drops ~50× vs main-model
self-summarization); the TTL tier is documented as paying off for >5-minute
inter-turn pauses. Local
evidence: 146-session baseline 86.4% hit ratio but 3.8M avg tokens/session,
heavily right-skewed (top-10 marathon sessions 40–110M each); tasks ending
in `new_session` hit 0.95 vs `cli_close` 0.82 — fresh single-model sessions
are the cheap unit.

**Verification.** Config change applied byte/CRLF-safely against a backup
(`config.yaml.bak-20261002`); post-edit diff shows ONLY the `prompt_caching`
section changed; model/compression/memory/delegation sections byte-identical
to backup. Hermes source checked, not just docs:
`agent_init.py:652-680` (TTL tiers), `model_selection_guards.py:90-126`
(switch confirm), `tools/tool_search.py` (deferred bridge).

**User rule (2026-10-02): never pin a model in config.** An
`auxiliary.compression` override to a named model was set and then
reverted on the user's instruction — everything must run on the model of
the active session, not a fixed one. The auxiliary slot therefore stays at
its `auto` default (= the session's main model); the 1/50-cost lever only
materializes when a cheap model happens to be the session's model at
session start. This generalizes D15's "no routing" to the runtime config
side of it.

**Rejected.** Pinning `auxiliary.compression` to a named model (violates the
user rule above; reverted same day); setting `session_affinity_header`
(nara/omniroute support
unverified — 401 on `/v1/models`, external behavior; stays Open work);
enabling `tools.tool_search` (pi's jcodemunch `codemode` already defers the
MCP surface here; the Hermes CLI tool list is small); enabling memory/skill
nudges (`memory_enabled: false` is deliberate — ~1.3K tokens/turn fixed cost,
recall via `session_search` instead).

**Open.** nara `session_affinity_header` support check; run
`scripts/micro_compaction_report.py` after a tool-heavy Hermes session to
measure the auxiliary model's savings.

---

## D18 — Session memory usage log location in `_scratch/`

**Decision.** Store the session memory retrieval query usage log at `scripts/_scratch/sessions/05_store/queries.jsonl` (gitignored, alongside `memory.db`).

**Why.** The usage log records every query (hits, misses, top terms) for telemetry and audit without polluting tracked source control with high-frequency operational telemetry.

**Rejected.**
- An individual tracked file in `scripts/memory/` (rejected: log changes on every query/retrieval, making it a constant magnet for git merge conflicts).
- A table inside `memory.db` (rejected: `memory.db` is a derived, rebuildable store that gets wiped and rebuilt from scratch during ingest/rebuild).

---

## D19 — Mixed type evaluation in `eval_queries.json`

**Decision.** Keep type asymmetry in `scripts/memory/eval_queries.json`: failure/error retrieval evaluation cases explicitly specify `"type": "error"` (per D16), while general or decision retrieval cases run unfiltered (`type: None`).

**Why.** Measured empirically:
- Asymmetric mixed type (filters on error queries, unfiltered on general/decision queries): **`hit@5=1.000 MRR=0.697 (15/15)`**.
- Removing type filters entirely (running all queries unfiltered): **`hit@5=0.800 (12/15)`** — failing on error-focused queries (`provider error`, `provider error variant`, `workspace gate`) because massive numbers of tool chunks introduce ranking noise.
- Forcing all query cases to carry a uniform type filter: drops recall on conceptual/benchmark queries (`12/15` to `13/15`).
Therefore, the asymmetry is load-bearing and empirically verified.

**Rejected.**
- Removing type filters entirely (rejected: drops hit rate to `0.800 (12/15)` per D16).
- Forcing all queries to carry a uniform type filter (rejected: causes recall drops on conceptual/benchmark queries).

---

## D20 — DeepSeek Harness session store (`~/.dsh`) vs CLI harness (`~/.deepseek-harness`) and Zstandard decompression

**Decision.** Point `agent_sessions.py`'s deepseek session loader to both `~/.deepseek-harness/sessions/` (standalone CLI harness JSONL store) and **`~/.dsh/sessions/`** (runtime DSH harness store), supporting both plain `.jsonl` and `.jsonl.zstd` / `.v4.jsonl.zstd` via `zstandard` decompression, with robust DSH v4 event parsing (`session`, `user/message`, `assistant/message`, `system/message`).

**Why.**
1. The standalone CLI harness (`scripts/deepseek_harness.py`) uses `~/.deepseek-harness/`, which remains empty in the main workspace where the actual agent runs under DSH.
2. The runtime DSH platform stores sessions as `.jsonl.zstd` files under `~/.dsh/sessions/` in DSH v4 event format (`type: session`, `type: user/message`, `type: assistant/message`, etc.). Without integrating `~/.dsh/sessions/` and zstd decompression, all workspace sessions were invisible to `agent_sessions.py` and `memory_index.py`.

**Rejected.**
- Ignoring runtime DSH sessions (rejected: would keep all active DSH sessions hidden from session browsing and memory indexing).
- Assuming uncompressed plain JSONL for DSH runtime sessions (rejected: DSH runtime natively compresses all sessions with Zstandard).

---

## D21 — Exclude DSH runtime sessions from memory corpus by default

**Decision.** `memory_index.py ingest` excludes sessions from `~/.dsh/sessions/` by default. Use `--include-runtime` to override.

**Why.** DSH runtime sessions are debug logs of the current session, not historical knowledge. When debugging "provider error", the runtime logs contain thousands of occurrences of "provider error", which pollute the BM25 ranking and push historical sessions out of the top-5. The memory corpus should contain knowledge, not runtime logs.

**Rejected.**
- Including DSH runtime sessions by default (rejected: pollutes ranking with autoreferential content).
- Excluding DSH sessions from `agent_sessions.py` (rejected: browser should show all sessions).

---

## D22 — NotebookLM simplification batch: delete dead eval, activate hook, defer moves

**Decision.** From 4 NotebookLM-grounded suggestions (2026-10-07, notebook
`root_workspace`), execute 2 immediately and defer 2 after worktree verification:
(1) delete `scripts/memory_eval.py` + `scripts/memory_eval_queries.jsonl`
(executed — the gate R15 runs `eval_memory_retrieval.py`, no importers exist);
(2) set `git config --local core.hooksPath hooks` (executed — `hooks/pre-commit`
already runs whitespace + integrity checks); (3) harness dirs
(`.ralph`/`.pi`/`.agents`/`.forge`/`agents/`) stay — all are git-tracked,
declared root entries, moving them breaks ALLOWED_ROOT/R1; any move goes
through the two-stage archive (D10) with the owning project, not unilaterally;
(4) skills stay — 5 of 6 projects hold only a 487-byte `MANIFEST.md` stub
(the 693-file vendoring never happened); only ARL carries 22 local skill dirs
(21 name-overlapping with root) and that dedup belongs to the ARL project
session, not root.

**Why.** Worktree verification overruled two suggestions: the notebook's corpus
described costs (vendored skills, debris dirs) that the current tree does not
carry. Deleting tracked, referenced entries on a stale description would trade
imaginary savings for real breakage. The two executed items were net-positive
with zero dependents.

**Rejected.**
- Moving harness dirs out of root on the notebook's say-so (rejected: tracked +
  declared; breaks the integrity gate).
- Deleting ARL's local skills from root scope (rejected: one project per
  session — ARL owns that call).
- Committing `core.hooksPath` (impossible: per-clone git config; documented
  here instead so the next clone re-runs one command).

---

## D23 — Dedicated bounded context for single-book technical retrieval

**Decision.** Create `the-pragmatic-programmer-retrieval` as an independent bounded context under `projects/research/the-pragmatic-programmer-retrieval` (grade: candidate), rather than expanding `retrieval-v2` or `knowledge-retrieval`.

**Why.**
1. Corpus shape and objective: `retrieval-v2` evaluated open notes / multi-document retrieval with an emphasis on out-of-corpus (OOC) and canary refusal calibration. In contrast, `the-pragmatic-programmer-retrieval` operates on a closed, authoritative 497-page monograph (*The Pragmatic Programmer*, 20th Anniversary Edition) with a strict citation contract (chapter, topic, page).
2. Reranker rationale vs `retrieval-v2` ABORT: `retrieval-v2` aborted cross-encoder reranking as overengineering because of large multi-corpus latency overhead (~500ms) and score distribution overlap on refusal gates. For single-book retrieval over 53 topics (~600–900 chunks), cross-encoder reranking (`BAAI/bge-reranker-base`) is evaluated on candidate retrieval quality, with gating thresholds to be established empirically after initial evaluation (Phase 2.2 of the master plan; proposed target recall@8 >= 0.90, MRR >= 0.85, unvalidated prior to measurement). If hybrid + reranking passes the threshold, expensive synthesis structures (RAPTOR, Graph CTE) are avoided. If it fails specifically on multi-hop questions (e.g. Q4, Q10, Q15, Q20, Q30), RAPTOR/Graph will be triggered conditionally based on evidence.

**Rejected.**
- Merging into `retrieval-v2` (rejected: would pollute `retrieval-v2`'s frozen benchmark and conflicting research goals — refusal calibration vs dense book extraction and multi-hop synthesis).
- Modifying `knowledge-retrieval` (rejected: `knowledge-retrieval` only measures the read path of the historical ARL knowledge graph, not ad-hoc book ingestion).

---

## D24 — GitHub carries the whole vault, not a curated subset

**Decision.** `kamyczeczek/Vault` holds every file under the workspace root except
four declared classes: (1) toolchain (`.venv*`, `node_modules`, `__pycache__`,
1 041 MB of installed third-party code), (2) secrets (`.env*`, `secrets.json`,
`agents/backup/`), (3) third-party books (`library/*` bytes, `datasets/INBOX/`,
`knowledge/raw*/` — 350 MB, much of it z-library), and (4) files GitHub rejects
outright (any file >100 MB). Measured: 72 821 files / 3.3 GB on disk became 4 638
tracked / 189 MB packed.

**Why.** The 2026-10-24 `.gitignore` excluded `projects/` (2.4 GB) and `library/`
(225 MB) to make one structural commit possible, and HANDOFF recorded that as a
conscious choice rather than an oversight. That made the remote a partial copy:
a fresh clone could not answer "what is in this vault". The owner asked for a
full copy, so the exclusion set is now derived from three provable constraints
(size, secrets, copyright) instead of from commit mechanics.

**Nested repos.** Twelve `projects/**` git repos (1.24 GB of the 1.37 GB under
`projects/`, minus `.venv`) were absorbed: each got `history.bundle` beside its
files (`git clone history.bundle` restores the repo with history), then its
`.git` was moved out of the tree. A gitlink would have shown an empty directory
on GitHub; keeping `.git` and committing files is not expressible in git. D12
(polyrepo, one project per session) still governs how work is split; what changed
is that the split is no longer visible to git in this tree.

**Rejected.**
- LFS for the full 3.3 GB (rejected: Free quota is 1 GB; 405 MB `memory.db`,
  292 MB torch DLL and three graph DBs are derived anyway — the producers rebuild
  them, so paying to version them buys nothing).
- Publishing the book bytes to a public repo (rejected: DMCA exposure on content
  that cannot be scrubbed from history; `library/index.json` already makes the
  library reviewable and re-downloadable).
- Gitlinks for the absorbed projects (rejected: satisfies neither "files on
  GitHub" nor "history preserved").
