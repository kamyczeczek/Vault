---
type: Concept
title: WORKFLOW
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# Pipeline WORKFLOW — Canonical Global Plan (P1)

Single ordered artifact. Every run follows `01→02→03→04→05` in order; no phase skipped, no phase reordered. Each phase has an entry condition, an Inputs Table pointer, and an exit gate. Spawned agents emit `phase:` and are rejected if phase order or gate fails.

Evidence: `00_from_plan_to_action_how_well_do_agents_follow_th` (explicit ordered plan beats implicit stages; subpar plan hurts more than none; periodic reminders mitigate).

**Why phase 5 exists:** phases 1–4 produce knowledge; phase 5 decides when that knowledge stops being
trustworthy. Without it the loop never closes — a stored lesson outlives the evidence it was derived from,
which is the failure `04_honest_lying_memory_confabulation` measured directly: 0 of 121 reflections
mentioned the correct object, and those reflections were reused across trials. Phase 5 is the missing half
of `02_expel_experiential_insight_extraction`'s ADD/EDIT/UPVOTE/DOWNVOTE ledger — eviction at importance
zero — applied to this project's own candidate files.

## Phases

| # | Phase | Stage contract | Basis | Entry condition | Inputs Table | Exit gate (must pass) | Handoff artifact |
|---|-------|---------------|------|-----------------|--------------|----------------------|------------------|
| 1 | `01_inbox` | `stages/01_inbox/CONTEXT.md` | **environment-validated** (an empty folder is ground truth) | none | `INBOX/` + `knowledge/raw/` | `INBOX` empty ∧ `knowledge/raw/manifest.jsonl` rebuilt ∧ `check_manifest.py` exit 0 | `manifest.jsonl` |
| 2 | `02_corpus` | `stages/02_corpus/CONTEXT.md` | **environment-validated** (file contents + `source:` frontmatter are ground truth) | phase 1 gate passed | `knowledge/raw/` | `knowledge/corpus/*.md` count consistent with manifest `corpus_ids` ∧ every chunk has a `source:` field ∧ `check_manifest.py` exit 0 | `corpus` file set |
| 3 | `03_graph` | `stages/03_graph/CONTEXT.md` | **artifact-validated** (`graph.db` must equal the corpus it is derived from) | phase 2 gate passed | `knowledge/corpus/*.md` | `.graph_fingerprint` == digest fingerprint ∧ `graph.db` `nodes == corpus count` | `.graph_fingerprint` + `GRAPH-DIGEST.md` |
| 4 | `04_reflect` | `stages/04_reflect/CONTEXT.md` | **artifact-validated** (digests + candidates cite resolving ids) | phase 3 gate passed (`watch.py --once` clean) | `knowledge/graph/graph.db` + `GRAPH-DIGEST.md` + `knowledge/topics.md` + `pipeline/WORKFLOW.md` | `reflection/digests/<topic>.md` cites ≥1 `ask.py --tag` id ∧ `reflection/candidates/<topic>.jsonl` state-machine valid ∧ `check_reflection.py OK` ∧ `check_reachability.py OK` (questions a working agent asks reach ≥1 chunk) | digest + candidates |
| 5 | `05_evict` | `stages/05_evict/CONTEXT.md` | **artifact-validated** (rejections must cite ids that no longer resolve) | phase 4 gate passed (`check_reflection.py OK`) | `reflection/candidates/*.jsonl` + `knowledge/graph/graph.db` + `.graph_fingerprint` + `reflection/memory.md` | every rejected candidate carries a non-empty auditable `why` ∧ every audit row rejects over ids that genuinely no longer resolve ∧ `check_eviction.py` exit 0 ∧ `check_reflection.py` still OK ∧ `check_promotion.py` OK (accepted rules land on the read path) | survivors + `reflection/evictions/<run>.jsonl` |
- **Promotion is a loop, not a write (W-INJECT):** `scripts/promote_candidate.py` validates
  evidence ids resolve in `graph.db` before accepting a rule and appends it to
  `reflection/memory.md`. `scripts/check_promotion.py` is the gate for the other half —
  every accepted candidate must have a landed entry in `memory.md`, that file must be
  listed as an input in `stages/04_reflect/CONTEXT.md` (or a spawned reflection cannot
  read what promotion wrote), and each rule's evidence ids must appear backticked in its
  own entry. The project shipped the hole this closes: 30 candidates sat in `accepted`
  while `memory.md` did not exist and the string appeared in one place — the promoter's
  docstring. Injection was one-directional, which is not injection. An accepted rule that
  no agent reads is a stored opinion, not a constraint.
- **Specification detail is inversely proportional to horizon (basis column, W-HORIZON):**
  each phase's `Basis` classifies its spec as environment-validated (the state of the world is
  ground truth — `INBOX` empty, corpus files present), artifact-validated (a produced file must
  equal its source — `graph.db` vs corpus, digest citations vs `graph.db`), or
  anticipation-only (spec for work not yet done). A far phase carrying procedure-level detail
  is a violation: it is anticipating a future the preceding phase will change. Keep far specs
  to entry condition + exit gate; put procedure in the phase's `CONTEXT.md`, where it can be
  invalidated locally. `00_01_planning_horizon` is the measured basis: agents make worse
  decisions the further the horizon they plan for, and the plan is more accurate when it
  specifies near actions concretely and far actions abstractly.

## Compliance
- **Manifest is derived, not appended:** `knowledge/raw/manifest.jsonl` is rebuilt from
  corpus `source:` frontmatter on every ingest (never appended to by hand or by script).
  `scripts/check_manifest.py` is the phase 1/2 exit gate; exit 2 = provenance break.
- **Ordered execution:** phases run `01→02→03→04→05`. Any out-of-order `phase:` is a gate failure.
  Phase 5 is not optional: a run that stops at 4 has written lessons it never maintains, which is
  exactly the recurrence failure this project's own corpus documents
  (`04_honest_lying_memory_confabulation`, `02_expel_experiential_insight_extraction`).
- **Gate enforcement:** `scripts/check_reflection.py` + `knowledge/graph/watch.py --once` are the exit gates for phase 3/4. CI runs both; `spawn.py` hard-refuses on `STALE_DIGEST`. For phase 5, `scripts/evict_stale.py` is the action and `scripts/check_eviction.py` is the exit gate — the action and the audit are separate scripts on purpose, so the gate can fail the eviction.
- **Eviction is grounded, not opinionated:** a candidate is rejected only when its evidence ids no
  longer resolve in `graph.db`. A rejection recorded over ids that still resolve is an *opinion*
  eviction — the second-order confabulation this stage exists to prevent, caught by `check_eviction.py`.
- **Reachability is the read half of the pipeline (W-REACH):** `dead_route_tags()` verifies that
  every `--tag` a prompt names exists in `knowledge/topics.md` — but that only checks the
  *write* side. `scripts/check_reachability.py` asserts the *read* side: a question a working
  agent actually asks reaches ≥1 chunk via `ask.py`. A corpus that holds a concept but cannot be
  asked about it is closed in prose and open in practice
  (`00_reflection_closed_vocabulary_before_content`: "questions silently go unanswered"). Seeds
  are recorded from observed zero-hit runs in `reflection/reachability-seed.jsonl`; a seed whose
  `expect` is 0 is a negative control and a later match is a failure, not a pass — a control that
  silently stops controlling is the defect this gate exists to catch.
- **Provenance stamp:** every `reflection/digests/*.md` and `candidates/*.jsonl` embeds `fingerprint + plan version (this file's sha12) + routing queries`. Missing provenance ⇒ gate failure (P5).
- **Plan reminders (P3):** reflection agents re-inject current phase `CONTEXT.md` Inputs Table + this `WORKFLOW.md` phase header every N tool calls and on compaction (see `spawn.py` periodic reminder contract).
- **Contracts must not hardcode moving values (P7), and moving values need a
  sanctioned re-stamp path (S-47 P1):** the corpus fingerprint and this file's sha12
  change on every corpus/plan edit, and both are stamped into every digest and
  candidate row. An ADDITIVE corpus change (ingesting chunks) therefore invalidates
  every prior reflection at check-time even though no cited evidence changed. `stages/*/CONTEXT.md` may quote the
  current fingerprint only beside a pointer to `knowledge/graph/.graph_fingerprint`;
  `scripts/check_stage_contracts.py` enforces this (exit 1 on a bare literal). A
  contract quoting a stale fingerprint silently describes a graph that no longer exists
  — the project already shipped that defect: `stages/03_graph` carried the
```bash
python scripts/check_stage_contracts.py  # contracts quote live values, not stale ones
python scripts/check_manifest.py            # phase 1/2 gate (raw <-> corpus provenance)
python scripts/evict_stale.py                    # phase 5 action (evict ungrounded candidates)
python scripts/check_eviction.py                 # phase 5 gate (evictions are grounded)
python knowledge/graph/watch.py --once      # phase 3 gate (graph == corpus)
python scripts/check_reflection.py          # phase 4 gate (provenance + citations)
python pipeline/06_reflect/spawn.py --topic <s> # phase 4 spawn (enforces gates)
python scripts/check_reachability.py        # phase 4 sub-gate (questions reach answers)
python scripts/check_promotion.py       # phase 5 sub-gate (accepted rules land on read path)
python scripts/check_reflection.py --replan # repair: re-stamp to live plan_version + corpus fingerprint (guarded: refuses if a cited id no longer resolves)
```

## References

- Brain query: `knowledge/graph/ask.py "<q>" [--tag T ...] [--limit N] [--raw]`
- ADAPT decomposition (P2): `pipeline/06_reflect/route.py` threshold split
- Determinism: `CONTEXT.md:00_interpretable_context_methodology_folder_structu`, `00_agent_memory_hierarchies`
- Disclosure: `00_is_progressive_disclosure_all_you_need_for_long` (one level)
