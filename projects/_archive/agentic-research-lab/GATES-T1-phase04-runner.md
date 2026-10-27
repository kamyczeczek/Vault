---
type: Concept
title: GATES-T1-phase04-runner
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# T1 — Which runner is phase 04?

Ticket from `docs/wayfinder/research-graph-reflection-execution.md`. One ticket,
one session, one human decision at the end. Gates written before the first run,
per `unlazy`.

## The question

Phase 04 currently has two runners. `pipeline/06_reflect/spawn.py` is an `omp`
agent loop and is what `CLAUDE.md` routes to. `pipeline/06_reflect/reflect.py` is
a single structured LLM call over a deterministically-built evidence packet,
and is what carries the metadata `check_reflection.py` accepts.

T1 asks which one is canonical. It does not ask which one is *better* in the
abstract — it asks which one phase 04 *is*, and it accepts that the answer may
be "neither, and here is the third shape".

## What the two runners actually need

Established by reading the code, before planning the measurement, because a
measurement whose prerequisites are missing is not a measurement.

| | `spawn.py` | `reflect.py` |
|---|---|---|
| Entry | `python pipeline/06_reflect/spawn.py --topic T --scratch` | `python pipeline/06_reflect/reflect.py --topic T --scratch` |
| External dependency | `OMP_WORKSPACE_RESEARCH_EXTENSION` or default `.omp/extensions/workspace-research.ts` | live OpenAI-compatible endpoint resolved from `~/.pi/agent/models.json` |
| Dependency present? | **yes** — `workspace-research.ts` exists | **unverified** — endpoint availability is not asserted by any check |
| Pre-model gates | stale-digest refusal, `watch.py`, `check_stage_contracts.py` | none; writes only after a model call succeeds |
| Failure surface | exits 1 on stale graph, 4 on missing extension | raises out of `_call_model` on network/provider error |

The asymmetry is the finding, and it exists independently of any timing run: a
`reflect.py` failure writes **no artifact at all**, so a failed run is
indistinguishable from a run that never happened. `spawn.py` fails loudly and
early with a named reason.

## Gates

Gates G8–G11 are about the *measurement*; G12 is the decision itself, which is
not mine to make.

- [x] G8: Both runners are runnable on the same topic, writing to scratch
  CHECK: run each runner with `--topic t1-runner-compare --scratch`
  EXPECT: exit 0 for both, OR a named failure for each
  ABANDON if a runner's dependency is unavailable — record which, do not
  substitute a proxy runner and present it as the real one
  RESULT (2026-10-02, after port): `reflect.py` exit 0; `spawn.py` exit 0.
  See "Post-port execution" below.

- [x] G9: Neither run touches graded artifacts
  CHECK: compare `git status --porcelain reflection/digests
  reflection/candidates` before and after, and compare the mtime of the two
  pre-existing files named below
  EXPECT: the set of paths is unchanged, and those two files keep their mtimes
  BASELINE (measured 2026-10-01, not assumed):
  - `?? reflection/digests/project-entropy.md`      mtime 2026-09-30 21:02
  - `?? reflection/candidates/project-entropy.jsonl` mtime 2026-09-30 22:13
  NOTE: the baseline is *not* a clean tree. Those two files are untracked but
  real — `check_reflection.py --paths project-entropy` passes on them. They are
  the output of an earlier run by someone else, they are graded evidence, and
  the workspace rule is that a gate-passing artifact is not deleted to make a
  gate green. So "clean" here means "this exact set, untouched", not "empty".
  A measurement that contaminates the corpus is worse than no measurement.
  RESULT (2026-10-02): graded set unchanged before/after; the two files kept
  their mtimes (2026-09-30 21:02 / 22:13). PASS.

- [ ] G10: Wall-clock and token cost are measured, not estimated
  CHECK: record elapsed seconds per runner; token counts from the provider
  response where the runner exposes them
  EXPECT: both numbers, or an explicit "not exposed by this runner"
  NOTE: `reflect.py` returns parsed JSON, not usage. If usage is unavailable,
  record that as the finding rather than inferring tokens from prompt size.
  RESULT (2026-10-02): elapsed recorded per runner (see Post-port execution).
  Token counts: **not exposed by either runner** — `reflect.py` returns parsed
  JSON without a usage field; `spawn.py`'s loop output surfaces no usage.
  This is the finding, per the note.

- [x] G11: Output quality is compared by the gate that already exists
  CHECK: `python scripts/check_reflection.py --paths t1-runner-compare`
  EXPECT: PASS/FAIL per runner, and the failing gates named
  NOTE: this is the only quality signal that already has a negative control
  behind it. Inventing a new scoring rubric here would be exactly the
  gate-without-control shape this repo has paid for twice.
  RESULT (2026-10-02): PASS per runner, sequential. `reflect.py`'s fresh
  artifact was graded immediately after its run, before `spawn.py` clobbered
  the same topic files; the final state (spawn's) re-graded, PASS. Caveat:
  grading one topic directory cannot tell the two runs apart, so the
  sequence + this note are the record. The 10-01 FAIL finding survives in
  the Research answers section; the 10-01 file itself was overwritten in
  place by the G8a run (scratch is not snapshot-covered by
  `snapshot_graded.py`).

- [ ] G12: A human chooses the canonical runner
  CHECK: the ADR named in the ticket exists and names one runner
  EXPECT: `docs/adr/0005-*.md` with a decision
  OWNER: human. Not delegable to this session.

## Honest limits of this plan

- **G8 may not be satisfiable.** `reflect.py` needs a live model endpoint. If
  it is down, the ticket stops at "one runner measured, one blocked", and that
  is a legitimate outcome to report — but it does **not** answer the question,
  and I will not present a partial measurement as a decision input.
- **Wall-clock is not quality.** A fast runner that emits ungrounded citations
  is worse than a slow one, and G11 is the only thing in this plan that looks
  at grounding at all.
- **One topic is not a distribution.** A single topic cannot tell you how the
  runners behave on a topic with thin evidence. It can tell you whether they
  work, and it can expose asymmetry between them.
- **This plan measures two runners, not three.** The ticket's third option —
  a deterministic Python pipeline calling a model only for claim text — is a
  shape, not an existing implementation, and nothing here measures it. If the
  human finds that shape most attractive, the measurement does not support it
  and the gap should be named rather than papered over.

## REPRISE 2026-10-01 — the ticket's premise was false

The question as originally written assumed both runners work and asked which is
better. `reflect.py` does not run on this machine, and the reason inverts the
ticket.

**`scripts/pi_models.py` already exists and already solves this exact failure.**
Its own docstring: *"pi writes models.json with trailing commas and stray tab
lines on some platforms, which makes the file unparseable by stdlib json. This
loader normalises those artifacts before parsing so reflection code can depend
on the file without a repair step each time."*

- `reflect_fast.py` and `single_call_test.py` import `pi_models`. Correct.
- `reflect.py` does not. It has its own `_resolve_endpoint()` calling
  `json.loads` directly, so it dies on a file the project already knows how to
  read.

So the failure is not "no endpoint" and not "the runner is slow". It is that one
runner bypasses the project's own loader. **This is a one-line-class fix, not a
measurement question**, and it was not visible while the ticket was framed as a
comparison.

Two further facts, both established by `git status --porcelain`:

- `reflect.py`, `reflect_fast.py`, `presearch.py`, `backend_probe.py` are all
  **untracked**. They have never been committed.
- Therefore `GATES-reflection-fastpath.md` claiming G1–G5 met with grounded
  artifacts is **unverified against `reflect.py` specifically**. I cannot tell
  from the gate ledger whether the fast path was measured on `reflect.py` or on
  `reflect_fast.py`.

### A correction to the record

I hand-edited `~/.pi/agent/models.json` to strip two trailing commas, then wrote
that the file "corrupts itself, pi writes trailing commas". Both parts were
wrong in a way worth recording: `json.loads` rejects a trailing comma but accepts
the blank line that was actually there, so my isolated reproduction disproved my
own hypothesis; and the trailing commas are a **known, documented** pi artifact
that `scripts/pi_models.py` exists to handle, not a new discovery. Editing the
file was unnecessary and it hid the real defect — `reflect.py` reading it naively.
The edit is harmless, the backup sits at `~/.pi/agent/models.json.bak`, and the
lesson is the one this repo keeps paying for: fixing a symptom without asking
whether the project already owns the fix.

### What T1 now has to answer first

1. Does `reflect.py` produce an artifact once it goes through `pi_models`?
2. Which file did `GATES-reflection-fastpath.md` actually measure — `reflect.py`
   or `reflect_fast.py`?
3. Only then: which runner is canonical.

Answering (1) is a research step, not a prototype: one deterministic command, no
model tokens, `git log` plus the scratch tree. The ticket cannot be resolved by
timing a runner that may never have run.

## Research answers — new session, 2026-10-02

T1 reclassified research (per handoff). The three open questions from the
reprise, each answered deterministically. No model tokens spent.

### Q1: Does `reflect.py` produce an artifact?

**YES — and it already did, without `pi_models`.** Evidence chain, all on disk:

- `reflection/scratch/digests/t1-runner-compare.md` +
  `reflection/scratch/candidates/t1-runner-compare.jsonl` exist, mtime
  2026-10-01 17:32.
- Their provenance carries `run_id: "reflect-1790868768418"`.
  `f"reflect-{int(time.time()*1000)}"` appears **only in `reflect.py`
  (line 262)**; 1790868768 s ≈ 2026-10-01 15:32 UTC = 17:32 local,
  matching the mtime to the second. So this artifact is `reflect.py`'s.
- The precondition: that run only worked because the hand-edited
  `~/.pi/agent/models.json` is stdlib-`json.loads`-able. Verified just now:
  `models.json.bak` (original, pi-written) **fails** `json.loads` (line 31,
  trailing-comma artifact); the current file parses. `pi_models.load_models`
  parses **both** — including the backup.
- Therefore the fix is confirmed as one the project already owns:
  `reflect.py` must read config through `scripts/pi_models.py`.
  Caveat before calling it a one-liner: `reflect.py` hardcodes provider
  `nara` + model index 1, while `pi_models.resolve_endpoint` is
  `PI_PROVIDER`/`PI_MODEL`-driven with default `omniroute`. The port must
  preserve or deliberately change that selection semantics.

### Q2: Which file did `GATES-reflection-fastpath.md` measure?

**Neither cleanly. The ledger conflates three runners:**

- G3's evidence topic `dealing-with-project-entropy` produced scratch
  candidates whose provenance is exactly `{fingerprint, plan_version:
  "a4d9465d311f", phase}` with **no `run_id`** — the signature
  `reflect_fast.py` writes verbatim (its `plan_version` is hardcoded to
  that value, `reflect_fast.py` line 184). Not `reflect.py`'s output
  (which always injects `run_id`).
- `reflection/timings/dealing-with-project-entropy.json` carries
  `run_id "reflect-5dad2ba4522e4636"` — the `reflect-<uuid16>` space that
  only `spawn.py` (via `agent_trace.new_run_id`) generates.
- The OWNS line names `reflect.py`, not `reflect_fast.py`, and the G4/G5
  check script `scripts/verify_reflection_fastpath.py` **no longer exists
  anywhere in the tree** — G4/G5 evidence (`REFLECTION_FASTPATH_VERIFIED`)
  is unproducible as written.

Conclusion: the fast-path ledger's claims about "reflect.py" are
unverified; its actual artifacts came from `reflect_fast.py` (candidates)
and `spawn.py` (timings). Mark GATES-reflection-fastpath.md as
**superseded-until-remeasured**, do not cite it as decision input.

### G11 on the existing t1 artifact

`python scripts/check_reflection.py --paths t1-runner-compare` → **FAIL**:
`entropy-001-lifecycle-score` cites chunk `00_automated_peer_review_and_
self_correction` with zero meaningful keyword overlap (single fail line,
the rest grounded). Artifact kept, not deleted, not re-run.

### What remains open

1. Port `reflect.py`'s endpoint resolution onto `pi_models` (decision:
   keep hardcoded `nara`+index-1, or adopt `PI_PROVIDER`/`PI_MODEL`).
2. Re-run G8 on topic `t1-runner-compare` *after* the port, so both
   runners are measured from a working state; then G11 fresh.
3. **G12 is still the human's**: which runner is canonical. Decision
   inputs now: `spawn.py` works and fails loudly; `reflect.py` works via
   hand-fixed config only and fails silently; `reflect_fast.py` worked but
   is untracked and its gate ledger is unverified.

## Port constraints (recorded before the port)

1. `reflect.py` and `pi_models.py` are **untracked**; the port may stay
   untracked (exploration). If G12 makes `reflect.py` canonical, entry into
   the repo goes through `agent_commit.py` with explicit staging — never
   `git add .`.
2. `~/.pi/agent/models.json` is **frozen from now on**. `.bak` remains the
   evidence. All config access goes through `pi_models.load_models()`; no
   further hand-edits of the config file.

## Post-port execution — 2026-10-02

Port landed: `reflect.py` endpoint resolution now delegates to
`pi_models.resolve_endpoint()` (env-driven `PI_PROVIDER`/`PI_MODEL`, default
`omniroute` → `agnes-3-flash`). The `nara`+index-1 pin and its
"nemotron-3-ultra-free unreliable" scar were removed from the code; model
selection is now config, not runner logic. Config files frozen; `.bak` kept
as evidence. `reflect.py` and `pi_models.py` remain untracked.

| Runner | Exit | Wall-clock | G11 |
|---|---|---|---|
| `reflect.py --topic t1-runner-compare --scratch` | 0 | 51.6 s | PASS (all grounded) |
| `spawn.py --topic t1-runner-compare --scratch` | 0 | 275.4 s | PASS (final state) |

Context: `reflect.py` wrote 12 evidence chunks in one structured call.
`spawn.py`'s loop produced 6 claims / 3 candidates, self-graded green, and
repaired six truncated `## Claim` headings in the digest via delta edit. Both
runs from the post-port healthy state; G9 verified the graded corpus stayed
untouched. Neither runner exposes token usage (G10 finding). The ~5×
wall-clock gap is a data point, not a quality signal — G11 is the quality
signal, and it passed for both.

## G12 decision input (for the human)

- `spawn.py`: works out of the box, fails loudly with named reasons (exit 1
  stale graph, 4 missing extension), 275 s, self-validating loop.
- `reflect.py`: 52 s single call, deterministic retrieval, env-driven model
  after the port; on failure writes **no artifact** (indistinguishable from
  never run — the asymmetry stands, now with the config hole closed).
- `reflect_fast.py`: works, but its gate ledger (`GATES-reflection-fastpath.md`)
  is superseded-until-remeasured (G4/G5 check script missing; artifacts
  conflate runners — see Research answers Q2).

## Abandonment protocol

ABANDON: <id> <non-empty reason> — recorded in this file, not deleted. A gate
that cannot run is a finding; a gate that is quietly removed is a lie. The
reprise above supersedes the G8–G10 framing: those gates assumed a comparison
between two working runners, and only one is known to work.

## G12 resolved — 2026-10-01 (human decision)

DECISION: `reflect.py` is the canonical reflection runner. Speed was the
decider: 52 s single structured call vs `spawn.py`'s 275 s self-validating
loop; G11 quality passed for both on the shared topic, so the wall-clock gap
carried no quality signal. Human's words: "i want really fast reflection."

ABANDON: spawn.py (canonical role) G12 elects reflect.py on speed; the runner
stays on disk for the occasional self-validating pass — retired from the
canonical role, not deleted.
ABANDON: reflect_fast.py (canonical role) G12 elects reflect.py; its gate
ledger (`GATES-reflection-fastpath.md`) is superseded-until-remeasured and it
stays ignored (`.gitignore:103`) until re-measured or re-elected.

Consequence (carried out 2026-10-01, commit `82b078a`): `scripts/pi_models.py`
was un-ignored and entered through `agent_commit.py` (never `git add .`); it is
now tracked alongside `reflect.py`. Known defect (FIXED 2026-10-01, same
workstream): on failure `reflect.py` used to write no artifact, so a failed
run was indistinguishable from a never-run one. Every run now emits run/failure
trace records to the agent_trace ledger (`reflection/trace/events.jsonl`),
and `tests/test_reflect_failure.py` pins it.