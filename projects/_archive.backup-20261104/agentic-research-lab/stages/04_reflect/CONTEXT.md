---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Stage 04_reflect — Reflection & Candidate Generation

Use graph digests and topic routing to produce grounded reflections and machine-validated candidate rules from the corpus.

## Inputs
- `knowledge/graph/graph.db`
- `knowledge/graph/GRAPH-DIGEST.md`
- `knowledge/topics.md`
- `pipeline/WORKFLOW.md`
- `reflection/memory.md`

## Process
1. Inspect coverage via `python knowledge/graph/ask.py "<topic>" --tag <topic> --raw`.
2. Spawn reflection agents via `python pipeline/06_reflect/spawn.py --topic <topic-slug>`.
3. Each reflection must cite resolving chunk ids and stamp the live fingerprint + plan version.
4. Emit `reflection/digests/<topic>.md` and `reflection/candidates/<topic>.jsonl`.
5. Promotion appends accepted rules to `reflection/memory.md`; never hand-edit.
   Acceptance requires BOTH a verified lesson link in `knowledge/graph/sessions.db`
   AND a complete peer-review before→after pair labeled with the candidate id in
   `reflection/review_gate.jsonl` (see `scripts/review_gate.py --label <id>`),
   stamped with the live corpus fingerprint. No promotion on self-critique alone.

## Outputs
- `reflection/digests/<topic>.md`
- `reflection/candidates/<topic>.jsonl`
- updated `reflection/memory.md` via `scripts/promote_candidate.py`

## Invoke
```bash
python pipeline/06_reflect/spawn.py --topic agentic-research
```

## Contract
- **Reachability:** `scripts/check_reachability.py` asserts every seeded question reaches at least one chunk.
- **Promotion read-path:** accepted rules must land on `reflection/memory.md`, and this file must be listed as an input so spawned reflections can read it.
- **Provenance:** every digest and candidate row embeds the corpus fingerprint + plan version.

## Handoff
Outputs feed `stages/05_evict` (`python scripts/evict_stale.py`).


## Evolved Protocol Rule (Automated Peer Review and Self-Correction Loops)
<!-- meta-evolved: Automated Peer Review and Self-Correction Loops -->
- **Origin Evidence:** ``00_automated_peer_review_and_self_correction`, `00_agentic_auto_research_frontier_10_sources``
- **Requirement:** Reflection and code evolution stages must integrate an automated peer-review rubric or test-runner feedback loop to evaluate artifacts before promotion.

 ## Evolved Protocol Rule (Red-Flag Stop Conditions)
 <!-- meta-evolved: Red-Flag Stop Conditions (Karpathy) -->
 - **Origin Evidence:** ``skills/karpathy-guidelines/SKILL.md`
 - **Requirement:** Agents MUST pause and ask when any of the following patterns arise during coding or synthesis work:
   - "I'll just assume..." → state the assumption explicitly and ask for confirmation
   - "There are multiple ways to interpret this..." → present interpretations, do not pick silently
   - "I'll fix this while I'm here..." → stop; scope creep is forbidden unless explicitly requested
   - "This could be more flexible if..." → YAGNI unless the user asks for that flexibility
   - "This seems more complicated than it should be..." → suggest a simpler approach
   - "I'm not sure what this code does..." → ask for explanation before editing
 - **HARD REQUIREMENT:** Do NOT proceed with implementation until ambiguity is resolved.


## Evolved Protocol Rule (Research quality requires external grounding: verify-then-correct with tools, tests, or peer review; never promote on ungrounded self-correction.)
<!-- meta-evolved: Research quality requires external grounding: verify-then-correct with tools, tests, or peer review; never promote on ungrounded self-correction. -->
- **Origin Evidence:** ``00_06_self_correction_grounding_requirement`, `00_07_critic_external_tool_verification`, `00_automated_peer_review_and_self_correction`, `00_deep_analysis_popular_autoresearch_projects``
- **Requirement:** Block any finding, candidate promotion, or self-revision whose only evidence is model self-critique; require tool output, test-runner result, peer-review rubric score, or graph id resolution, and target corrections only at verified-wrong items (oracle discipline).


## Evolved Protocol Rule (Post-promotion audit — run every accepted lesson against held-out trajectories and decrement score when eviction predicate fires.)
<!-- meta-evolved: Post-promotion audit — run every accepted lesson against held-out trajectories and decrement score when eviction predicate fires. -->
- **Origin Evidence:** ``00_08_lesson_persistence_eviction_requirement`, `00_a_bandit_approach_with_evolutionary_operators_fo``
- **Requirement:** promote when externally verified


## Evolved Protocol Rule (Every stored lesson must encode its own eviction predicate; a lesson without an escape hatch compounds confidently wrong guidance.)
<!-- meta-evolved: Every stored lesson must encode its own eviction predicate; a lesson without an escape hatch compounds confidently wrong guidance. -->
- **Origin Evidence:** ``00_08_lesson_persistence_eviction_requirement`, `00_06_self_correction_grounding_requirement`, `00_agent_memory_hierarchies``
- **Requirement:** Require every stored lesson to encode an eviction predicate (firing condition + score decrement + re-test trigger); run the post-promotion audit on held-out trajectories and decrement the lesson score when the predicate fires.


## Evolved Protocol Rule (Promotion gate must require independent external ground truth; self-reported success is unverifiable.)
<!-- meta-evolved: Promotion gate must require independent external ground truth; self-reported success is unverifiable. -->
- **Origin Evidence:** ``00_06_self_correction_grounding_requirement`, `00_00_software_factory_isolate_build_prove_ship`, `00_automated_peer_review_and_self_correction``
- **Requirement:** Require every candidate promotion to resolve at least one evidence node in graph.db AND cite a tool-output artifact (test result, audit log, or review-gate entry) before acceptance; block self-critique-only promotions.


## Evolved Protocol Rule (Add AgentDebug-style root-cause attribution (detect→attribute→correct) to the reflect stage of spawn.py, producing structured error-classified candidates.)
<!-- meta-evolved: Add AgentDebug-style root-cause attribution (detect→attribute→correct) to the reflect stage of spawn.py, producing structured error-classified candidates. -->
- **Origin Evidence:** ``00_agent_error_taxonomy_debugging_web_research`, `00_agent_hooks_lifecycle_guardrails`, `00_agent_execution_hooks_guardrails``
- **Requirement:** On every reflect-stage spawn, run detect→attribute→correct pipeline: classify each failed candidate into an error category (retrieval miss, grounding gap, logical inconsistency, or tool misuse), emit a structured JSON diagnostic, and target correction only at the attributed root cause.


## Evolved Protocol Rule (Adding a third evidence node with non-overlapping tag dimensions raises F1 counterfactual retention from 0.0 to 0.54–0.59, converting fragile verdicts to partial.)
<!-- meta-evolved: Adding a third evidence node with non-overlapping tag dimensions raises F1 counterfactual retention from 0.0 to 0.54–0.59, converting fragile verdicts to partial. -->
- **Origin Evidence:** ``00_automated_peer_review_and_self_correction`, `00_agent_execution_hooks_guardrails`, `00_agent_memory_hierarchies``
- **Requirement:** For automated peer-review correction loops over evidence sets, add a third agent-memory-hierarchy node with non-overlapping tag dimensions and re-run deterministic execution-hook adversarial falsification; evaluation shows F1 counterfactual retention rises from 0.0 to 0.54-0.59, converting fragile verdicts to partial


## Evolved Protocol Rule (When two original evidence nodes share ≥5 of 6 tags, adding a third node does not fix F1 fragility — the redundancy is pairwise; node replacement (not addition) is required.)
<!-- meta-evolved: When two original evidence nodes share ≥5 of 6 tags, adding a third node does not fix F1 fragility — the redundancy is pairwise; node replacement (not addition) is required. -->
- **Origin Evidence:** ``00_08_lesson_persistence_eviction_requirement`, `00_06_self_correction_grounding_requirement`, `00_agent_memory_hierarchies``
- **Requirement:** Before re-running lesson-persistence adversarial falsification, swap the redundant eviction-ledger evidence node with a complementary agent-memory-hierarchy node; pairwise tag redundancy (>=5/6 shared tags) makes self-correction grounding fail when only added, not replaced


## Evolved Protocol Rule (When all candidates in a reflection batch pass adversarial falsification plus post-promotion audit, promote them in the same gate cycle and record pairwise-redundancy lessons as meta-candidates about the pipeline itself.)
<!-- meta-evolved: When all candidates in a reflection batch pass adversarial falsification plus post-promotion audit, promote them in the same gate cycle and record pairwise-redundancy lessons as meta-candidates about the pipeline itself. -->
- **Origin Evidence:** ``00_agent_memory_hierarchies`, `00_automated_peer_review_and_self_correction`, `00_agent_error_taxonomy_debugging_web_research``
- **Requirement:** When a batch of agent-memory-hierarchy candidates all pass automated peer-review correction plus post-promotion audit, promote them in one gate cycle and record the error-taxonomy debugging lessons as meta-candidates about the reflection pipeline; then run apply_meta_learning.py to propagate the new rules into stage contracts


## Evolved Protocol Rule (Adversarial falsification harness (Proponent/Critic/Judge) with counterfactual ablation, counter-evidence search, and defect injection resilience can differentiate candidate robustness and guide promotion decisions.)
<!-- meta-evolved: Adversarial falsification harness (Proponent/Critic/Judge) with counterfactual ablation, counter-evidence search, and defect injection resilience can differentiate candidate robustness and guide promotion decisions. -->
- **Origin Evidence:** ``00_06_self_correction_grounding_requirement`, `00_08_lesson_persistence_eviction_requirement``
- **Requirement:** adopt multi-agent debate pattern for candidate evaluation


## Evolved Protocol Rule (Post-promotion audit harness (test accepted rules against held-out questions, flag vague actions, validate structural correctness) successfully differentiates well-specified rules from those needing revision.)
<!-- meta-evolved: Post-promotion audit harness (test accepted rules against held-out questions, flag vague actions, validate structural correctness) successfully differentiates well-specified rules from those needing revision. -->
- **Origin Evidence:** ``00_08_lesson_persistence_eviction_requirement`, `00_a_bandit_approach_with_evolutionary_operators_fo``
- **Requirement:** adopt automated post-promotion audit pattern

## Discussion layer — "chat with an expert"

Thinking through an idea happens in a markdown file under `INBOX/ideas/`, not in a chat
transcript and not in a stateful CLI. This sits *before* `04_reflect`: it turns a vague
notion into claims the reflection stage can promote, or into a decision that it should not.

```bash
python scripts/discuss.py new "<thesis>"        # create INBOX/ideas/<slug>.md
python scripts/discuss.py claim "<sub-claim>"   # two-sided retrieval, annotated in place
python scripts/discuss.py stance red-teamer    # who speaks next
python scripts/discuss.py attack "<the attack>" # or `concede` for an honest non-refutation
python scripts/discuss.py decide learned|wrong|unresolved "<why>" [--next TEXT] [--force]
python scripts/discuss.py stage --rule R --target T   # only from `unresolved`
```

Every command except `new` takes an optional `-p FILE.md` to target a specific
discussion. Without it the newest idea file is used, so an agent never has to
remember a slug. `-p` is an option, not a trailing positional: as one it was
absorbed into the prose (`attack "..." old.md`), which silently edited the newest
file instead of the named one.

**Contract:**
- **The file is the state.** There is no session id and no slug to thread between commands;
  every subcommand resolves the newest idea file unless given a path. A hand-edited file must
  still parse — the human is a first-class editor of the conversation, per
  `01_plain_text_as_interface` ("the filesystem IS the state management system").
- **Two-sided retrieval, both sides persisted.** Support and counter ids are written to the
  claim block. An empty counter set is recorded as `(none — unrefuted)` and is an honest
  statement about the corpus, not a silently dropped id list. The predecessor
  (`idea_session.py`, removed) retrieved counters and then wrote `"counter": []`, so every
  staged candidate cited one-sided evidence under a rule whose premise was two-sidedness.
- **Red-teaming is an expert, not a query.** `stance` selects who speaks. A red-team attack
  should cite a refuting chunk; when nothing refutes, the librarian records a *concession* in
  the open. Self-endorsement is refused: `stage` requires a red-team turn.
- **A discussion may end without a rule.** `learned` (record a graph node) and `wrong`
  (record a kill/scar) are first-class outcomes. Only `unresolved`, with a named next
  experiment, may `stage` a proposed candidate. This is deliberate: a pipeline that can only
  emit a rule pressures every session into manufacturing one, which is the
  `01_taxonomy_of_20_ai_research_failure_modes` failure in this project's own terms.
- **An unreachable graph is never a silent corpus.** `ask.py` returns `[]` both when the
  corpus has nothing and when `graph.db` is missing; `discuss.py` refuses in the second case
  rather than letting a broken index masquerade as an honest concession
  (`00_07_critic_external_tool_verification`).
- **A discussion is an idea, not an intake seed.** `INBOX/ideas/` is exempt from the
  "INBOX must be emptied on ingestion" rule: these files are arguments, not papers.
  Enforced, not merely intended — `ingest.is_idea_file()` skips them in the
  directory scan *and* refuses an explicitly named one (`--file`), and
  `check_research_quality.py` skips them so Q12 does not grade an argument as
  intake. Pinned by `tests/test_discuss.py::InboxExemptionTests`. Ingesting a
  discussion would let the brain cite the lab's own sceptic as evidence.
- **A seal is only as good as the chain it read.** `stage` and `close` verify the
  ledger *before* sealing and refuse on failure. An audit trail you seal through
  without reading is not an audit trail. Pinned by `LedgerIntegrityTests`.
- **A decision is a record, not scratch.** `decide` refuses to overwrite an
  existing decision; `--force` is required. Found live: a second `decide learned`
  erased an honest `unresolved` together with its `--next` experiment, and since
  the file is the only state that was unrecoverable. Pinned by
  `DecisionOverwriteTests`.
- **A decision has two halves and `--force` may only touch one.** The machine
  block `## decision` (`- value/- why/- next`) is regenerable state; the prose
  `## decision rationale` beside it — what the belief was at decision time, what
  would have made it different, what was rejected, what would falsify it — is the
  durable half. Found live: the heading match was `^## decision\b`, and `\b`
  matches between "decision" and a following space, so a forced rewrite deleted
  73 lines of recorded reasoning (recovered only by `git revert`, commit
  `2a15410` / `d0a7c0b`). The block is now replaced *in place* and only the bare
  heading matches, so a rewrite changes three lines and the rationale stays
  directly below. Pinned by `DecisionOverwriteTests::test_decide_force_preserves_the_rationale_beside_it`
  and `::test_rationale_alone_cannot_impersonate_a_decision`.
- **Naming a file is not a field of the prose.** A filename as the last word of
  `text`/`why` is refused with the `-p` hint, because the alternative is writing
  the note into the newest file while the caller believes it went to the one they
  named. Pinned by `TargetingTests`.
- **Retrieval can echo instead of disagree.** A chunk id appearing on *both* the
  support and counter side of a claim means the counter query returned support,
  not refutation. Read the two id sets for overlap before calling a claim
  "unrefuted" — `concede` is only meaningful when the sets are actually distinct.
