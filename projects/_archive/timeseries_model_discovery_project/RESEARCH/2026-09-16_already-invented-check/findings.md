---
type: Concept
title: findings
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Findings — Is This Already Built By Someone?

Posture: primary sources only. Three read in full via Exa → direct fetch (no
secondary summaries, no blog-to-blog echo). Search backend used: **agent-reach / Exa**
(`mcporter call 'exa.web_search_exa(...)'`); doctor reported github/twitter/reddit
`warn` (unauthenticated), so no login-state platform was used.

## §0. What this workspace has on disk today (the delta baseline)

Before comparing outwards, the honest baseline — because a finding is only useful as
"reinvented X, here is the delta", not as a literature summary:

| Built here (last 2 sessions) | Status |
|---|---|
| `PROCESS/check_python_compiles.py` — compile every staged `.py` | live, 9/9 gates, negative-control proven |
| `PROCESS/run_gates.py` — gate list as data, in-process, one command | live |
| `PROCESS/check_brain_identity.py` — brain-federation contract | live |
| failure-ledger → reflection → promotion → `memory.md` loop | live (promotions *repaired* this session) |
| `.jcode/hooks/epidemiology.py` — staleness gate `--require-fresh DAYS` | live |
| class-3 detection (parses-fine-but-line-missing) | **NOT built** — asserted as invariant |

The last row is the axis the whole audit turns on.

## §1. LAYER 1 IS FULLY INVENTED — by `Agent-Proof` (Heretek-AI, TypeScript, MIT, 1★)

My compile gate is a strict **subset** of its Stage 2 "Hard Git Gate":
- Same boundary: `git commit` → staged blobs only, `< 2.0s` SLA.
- Same enforcement model: *deterministic mechanical* checks, explicitly replacing
  prompt-based guardrails (`CLAUDE.md`/`.cursorrules`), on the stated ground that
  prompt rules "inevitably degrade under context saturation" — the same reasoning
  that produced my `run_gates.py` over hand-enumerated shell commands.
- Superset: 3-tier stage model. **Stage 1 (`<50ms`) runs at `PostFileEdit`, i.e. the
  edit hook itself** — exactly the position where my class-2/class-3 errors originate,
  and a position my workspace has no gate in. Stage 3 is CI/graph audit.
- It already has my planned next step: a **`LoopBreaker`** that hard-trips
  `FAILURE_LOOP_HALT` after ≥3 consecutive identical failures — my failure-ledger's
  recurrence problem, solved as a mechanism, not an invariant.
- Also covers my other axes: test/spec freezing (blocks agents rewriting the
  acceptance criteria), swallowed-error detection, and Ed25519 provenance receipts.

**Delta = 0 for the gate itself.** The one thing it has that mine does not is the
Stage-1 edit-time position. Mine is identical in *intent and boundary* but strictly
narrower in *timing* (commit-time only). I was building a strict subset.

## §2. THE REFLECTION LOOP IS INVENTED — the `AGENTS.md` compound-learning loop

Read in full (Osmani, "Self-Improving Coding Agents", Jan 2026). The correspondence is
near-exact, concept for concept:

| This workspace | Prior art |
|---|---|
| `PROGRESS.md` | `progress.txt` — chronological journal |
| `STATE.md` (bounded, 60-line, front-loaded) | task state `prd.json` |
| `AGENTS.md` | `AGENTS.md` (same file, same name) |
| reflection → promotion → `memory.md` | "agents update AGENTS.md: discovered patterns documented for future iterations" |
| failure_ledger → scar → prevention rule | error-to-rule pattern; Nevo's pipeline name is literal |
| "each improvement makes future improvements easier" (my stated goal, record R-04) | Compound Product's stated philosophy, verbatim |

The philosophy sentence I had been treating as this workspace's own formulation is a
direct quote from `snarktank/compound-product`. **The loop is not novel; it is
archetypal.**

Its unmet warning for this workspace, verbatim in spirit: *"Whatever persistence you
use, periodically verify that the agent is actually utilizing it. A memory file only
helps if it's injected into the prompt in future runs."* That is the exact failure
mode my promotion loop had: **30 candidates marked `accepted` while `memory.md` did not
exist** — the loop was writing to a contract file that nothing read.

## §3. CLASS 3 IS INVENTED — ChangeGuard (FSE 2025, Gröninger/Souza/Pradel)

My class-3 ("parses fine, but a line is missing → semantics silently change") is
exactly their target: "code changes meant to be semantics-preserving… actually modify
the behavior", with the motivating scrapy example being a *line-level* simplification
that silently changes behavior on one input.

Their numbers are the important part:
- **precision 77.1%, recall 69.5%** on 224 manually-annotated changes.
- **Regression tests recall only 7.6%** — i.e. existing test suites **miss 92.4%** of
  semantics-changing changes. So "just run the tests" is not a sufficient class-3 fix.
- Median coverage of changed code lifted 27% → 92% by their value-injection work.
- Runtime: seconds.

**Delta = the machine that catches class 3 already exists, at measured 77/70
precision/recall.** My class-3 invariant ("edited Python is executed before the
session yields") is a weaker, non-mechanical shadow of it.

## §4. WHY CLASS 3 RESISTS PROMPTING — validated independently (arXiv 2603.25764)

"Confident and Wrong: Silent Semantic Failures in Coding Agents" (Mehta, Snowflake AI
Research). 1,750 trajectories, 50 SWE-bench Verified tasks, 4 frontier models, 5 runs each.

Three findings that bear directly on my session:
1. **Silent semantic failure dominates**: 80% of Llama 4's failing runs and 68% of
   GPT-5's are "5/5 submit, 0/5 resolve" — confidently, consistently wrong, and
   *invisible to completion- and consistency-based monitoring*. This is my class 3 at
   population scale: no crash, no tool error, the run looks done.
2. **Pre-edit prompting does NOT fix it**: interpretation guard (Claude 65.2%→64.8%,
   GPT-5 44.4%→46.0%) and test-anchored guard (GPT-5 44.4%→44.0%) both null. Their
   conclusion: "a whole class of pre-edit prompts doesn't repair validity." So my
   reflexive mitigation — add a prompt/reminder before editing — is a proven-null
   intervention. Only a **criterion** (executing the code) moves it.
3. **Action bias**: on already-fixed bugs, all four models edit correct code on
   60–90% of runs instead of abstaining. This matches the workspace's own
   `AUDIT-2026-09-16.md` failure mode and is the specificity mirror of the same
   validity failure.

This converts my session's anecdote ("7 silent edit errors, prompt-based mitigation
insufficient") into a measured result (n=1,750). The convergence is the evidence.

## §5. THE ONE DELTA THAT IS NOT INVENTED — recurrence measurement

Across all four prior-art sources, nobody *measures whether the loop actually works*.
`AGENTS.md` loops assume accumulation helps. `Agent-Proof`'s LoopBreaker halts a
repeated failure but does not measure recurrence rates. ChangeGuard detects a bad
change but says nothing about whether the agent stops making it.

This workspace has that measurement, from record R-04 (measured on its own exhaust
before any external reading): **known trap classes keep firing after their scars are
born — 69 of 256 live ledger entries (27%) are recurrences of scarred classes.**

That number is the delta. Accumulation is assumed-beneficial by every prior-art
source; this workspace has the data showing it is partially failing. Nobody measures
the efficacy of the memory loop itself.

## §6. Consolidated verdict

| Mechanism | Already invented? | By | Delta of this workspace |
|---|---|---|---|
| Staged-file compile gate at commit | **YES** | `Agent-Proof` Stage 2 | 0 (strict subset) |
| Edit-time gate position | **YES** | `Agent-Proof` Stage 1 (`<50ms`) | mine absent — real gap |
| Failure loop halting | **YES** | `Agent-Proof` LoopBreaker | 0 |
| Reflection→memory compound loop | **YES** | compound-product / AGENTS.md loop | 0 (archetypal) |
| Class-3 semantic-change detection | **YES** | ChangeGuard (77.1%/69.5%) | 0 (mine is a weaker invariant) |
| "prompting fixes silent failure" | **REFUTED** | arXiv 2603.25764 | my intuition was wrong |
| **Measuring loop efficacy / recurrence** | **NO** | — | **27% recurrence — the only open delta** |

## §7. Method notes (for the next audit)

- **Exa via agent-reach is the working zero-config search path** on this host; doctor
  shows github/twitter/reddit as `warn` (unauthenticated) — do not burn time on
  login-state platforms for a prior-art audit.
- **`r.jina.ai` and direct GitHub fetch both worked**; the Nevo blog returned HTTP 402
  (paywalled) and was dropped rather than substituted with a summary of it.
- **Primary-source posture paid for itself twice**: reading ChangeGuard directly is
  what produced the 7.6% regression-test recall number, which inverts the naive
  "just run the tests" mitigation. A summary would not have carried it.
- This record is deliberately **negative-result-shaped**: the finding is that there is
  less to invent than assumed, and the one open axis is named rather than padded.
