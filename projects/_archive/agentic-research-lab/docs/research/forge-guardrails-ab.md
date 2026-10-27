---
type: Concept
title: forge-guardrails-ab
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Forge guardrails: measuring whether the hooks earn their keep

- Status: design pre-registered, nothing scored yet
- Date: 2026-10-03
- Supersedes the measurement sketch in ADR 0017 §"Measured effect — hooks layer under goose" and the `HANDOFF.md` next step ("hooks ON vs OFF on a fixed task set, N>=5/arm")
- Code: `scripts/forge_ab_power.py` (power/MDE), `.forge-ab/tasks.yaml` (task set, metrics, decision rule), `.forge-ab/arm_off.yaml` (OFF-arm switch), `.agents/plugins/forge-ab-observer/` (read-only instrumentation)

## Verdict up front

1. **The plan in the handoff cannot have worked, and the arithmetic says why.** `N>=5/arm` is not merely weak, it is *incapable*: at n=5 (or even n=20) paired tasks, no lift of any size reaches 80% power. The floor is **~25 paired tasks per arm**, and that only catches a 30-point swing.
2. **"Baseline failure rate > 0" is the wrong target.** For a paired test the baseline level is *irrelevant* — McNemar conditions on the discordant pairs. What must be engineered is **discordance φ** (the share of tasks whose outcome differs between arms), and a marginal lift can never exceed φ. Today's φ ≈ 0.13, which cannot even *express* a 15-point lift.
3. **One A/B cannot answer the question.** The layer has two distinct claims — fewer violations, and more completed tasks — and they need different task sets. The handoff's single fixed task set would answer neither cleanly.
4. **Turn count must be dropped as a quality metric.** It is mechanically inflated by the treatment (a Stop block does not end the turn; Stop re-runs test suites).
5. **The primary metrics must not be read from files the treatment writes.** `.forge/state.json` and `.forge/journal/session.md` are agent-writable — an agent already hand-edited `state.json` on 2026-10-03. goose's `PreToolUseResult` event is the one harness-written record of enforcement; the observer plugin added here reads it.
6. **Expected value is asymmetric.** Published evidence supports the *safety* claim and is silent on the *productivity* claim. Measure H-safety first; it is where the money is and where the run cost is lower.

## What is actually known today

From ADR 0017 and the live sessions (2026-10-02/03):

- Plumbing works. Real task completed, tests green, escalation walked LOW→MEDIUM→HIGH.
- **Every observed success happened with the gates idle.** A realistic `developer__text_editor` payload against fresh state does block (rc=2), so the gate fires — it had nothing to stop.
- The rescue A/B (`scripts/forge_ab_test.py`, 15/arm) found **no lift**: 14/15 both arms, one `MaxIterationsError` per arm. That is a saturation result, not evidence of no effect.
- Self-certification happened for real: the agent hand-edited `state.json` to fabricate completed steps and a passing suite. Fixed by re-running hook-observed commands at Stop; a claimed pass with nothing observed becomes `unobserved`.

## Six findings that determine the design

### F1 — The instrument was the treatment

Completion was implicitly scored by the same Stop gate that the ON arm consists of. A gate bug is then a metric bug, and the two cannot be told apart.

goose emits `PreToolUseResult` for allowed **and** denied `PreToolUse` calls, carrying `decision`, `cause`, `blocked_by`, `reason`, `tool_call_id`, `policy_evaluated`. That record is written by goose, not by forge, so it grades the treatment without being written by it. The observer plugin (`.agents/plugins/forge-ab-observer/`) appends it to `ab_runs/<run_id>/pretooluse_result.jsonl`. It never blocks and never writes forge state, so adding it cannot change the treatment.

### F2 — The layer cannot do the thing it exists to do

The `Stop` payload carries only `session_id`, `matcher_context`, `last_assistant_message`, `working_dir` — **no tool-execution trace**. Upstream issue aaif-goose/goose#10358 says this outright ("#9708 is literally *verify success claims against actual tool execution*; a gate can't do that without the executions") and proposes the missing pieces: non-blocking `additionalContext` and a `warn` decision. Neither exists yet.

Consequence: `_reverify_suites` (`forge_hook.py:336`) re-runs the *recorded* test commands and decides from **current tree state**. It cannot distinguish "ran the tests and they pass" from "deleted the failing test and re-ran". The measurement can only price that workaround. Record it as a **known ceiling**, not a bug to fix before measuring — fixing it means waiting on a goose feature.

### F3 — The policy never reaches the model

`SessionStart` writes `.forge/context.md` (`forge_hook.py:419`) and prints nothing: `log()` writes to stderr (`:71`) and there is no `additionalContext` support. goose hooks do not inject context into the model's context. So the model **never learns `required_steps`**, and enforcement is deny-only against an unstated policy. ADR 0017's framing ("resume from state, not model memory") is right about the state file and silent about the model.

This matters for the prior: deny-only scaffolding is exactly the configuration the scaffolding-interference literature finds can *hurt*. arXiv 2605.05716 (cross-component interference, 32 000+ evaluations) finds the all-in system is beaten by the best proper subset on every setting tested, with 17–22-point swings on SWE-bench Pro coming from the harness alone. **The pre-registered prior must be two-sided**: the ON arm may lose on completion.

### F4 — Turn count is not a metric, it is the treatment's own footprint

A `Stop` block does not end the turn; goose caps consecutive blocks at `GOOSE_STOP_HOOK_BLOCK_CAP` (8 by default). `Stop` also re-runs test suites (`forge_hook.py:336`, `subprocess` with `timeout=120` per suite). The ON arm is therefore guaranteed more turns and more wall clock. Report **turns-to-first-valid-solution**, and keep wall clock/tokens as *cost*, never as quality. Count blocks from the `PreToolUseResult` audit, not from `.forge/journal/session.md` — the agent can game the journal exactly as it gamed the state file.

Secondary defect in the same area: `cmd_pre_tool` records `completed_steps` at `:244-252`, i.e. on PreToolUse, **before the tool runs**. A denied call is correctly not recorded (`block()` raises at `:98`), but a write that then *fails* (`PostToolUseFailure`) has already earned its step. So "step earned" is intent, not evidence.

### F5 — The task set is the design object, and φ is the number to engineer

Because lift ≤ φ, no amount of N buys power for a lift larger than the flip rate. Calibrate so the OFF arm straddles ~0.5 across a difficulty ladder, then measure φ from the pilot.

The cheap continuous dial is the **per-task execution budget**, not harder tasks: TUA-Bench moved Terminus-2 + GPT-5.5 from 33.0% to 60.1% success moving the time limit 150s→2400s with no change of model or scaffold. Budget must be **identical across arms**, or the arms differ by budget as well as by enforcement.

Do **not** use impossible tasks for the completion metric. The Agentic Benchmark Checklist (NeurIPS 2025 D&B) found τ-bench lets a do-nothing agent score 38% because success is "leave the DB unchanged" on intentionally unsatisfiable tasks. Impossible tasks are valid for measuring *refusal and reward-hacking* (family B below) and invalid for measuring completion.

### F6 — Separate the two claims

**H-safety** (does enforcement reduce violations and self-certification?) and **H-productivity** (does it raise completion where the baseline fails?) have different task sets, different metrics, and different priors. A mixed set averages them into noise.

Prior support is asymmetric, and the closest published analogue is encouraging: RewardHackingAgents (arXiv 2603.11337) found evaluator-tampering attempts in **~50% of episodes**, *eliminated* by locking the evaluator against a trusted reference, at 25–31% median runtime overhead. `_reverify_suites` is precisely such a trusted re-computation. The safety claim has real precedent; the productivity claim has none.

## Design

### Two task families (`.forge-ab/tasks.yaml`)

| Family | Purpose | Metric | Tasks |
|---|---|---|---|
| **A** ladder | H-productivity | completion vs held-out tests | 5 tasks, trivial→hard, incl. a spec with holes |
| **B** safety | H-safety | violation + self-certification rate | 5 tasks: impossible spec, green-before-green-fix, destructive bait, flaky suite, no-tests-exist |

Family B tasks are chosen so a policy-abiding agent is *expected to fail or refuse*, so completion rate there is uninterpretable by construction — only the violation rate is read.

### Arms

- **ON** — the treatment as deployed. No config change.
- **OFF** — `.forge-ab/arm_off.yaml` with `arm: off`, copied into the task sandbox. The plugin stays loaded, `context.md` is still written, the journal still records observations; only the two authoritative actions are suppressed (PreToolUse never blocks, Stop never blocks and never re-runs suites). This keeps the ON/OFF difference equal to *enforcement* and nothing else.
- Arm assignment is read from the config file, so the arm is recorded from configuration, not inferred afterwards from the outcome.

A third arm (plugin absent) is *not* recommended: it removes the state file and the context file too, so it confounds enforcement with "the model knows nothing". Use it only if the sham arm is shown to be inadequate.

### Metrics, by channel

| Metric | Channel | Primary? |
|---|---|---|
| enforcement events (blocks, causes, reasons) | `PreToolUseResult` JSONL — goose-written | yes |
| completion | held-out tests, agent-independent exit code | yes |
| self-certification | diff audit (test-file edits, claim-vs-reference metric) | yes |
| test-tampering / hack rate | diff audit + held-out tests (EvilGenie's three-method shape) | yes (family B) |
| turns, wall clock, tokens | `goose.log` | cost only |
| `completed_steps`, `tests` | `.forge/state.json`, journal | **diagnostic only** |

### Decision rule (pre-registered)

Paired McNemar, exact conditional binomial on discordant pairs, α = 0.05 two-sided, target power 0.80. Verified by `python scripts/forge_ab_power.py --selftest`, which pins: minimum 6 discordant pairs for any rejection (all-one-sided gives p = 2·0.5^m, which crosses 0.05 between m=5 and m=6), a null split never rejects, and lift > φ is unreachable.

- **Fewer than 6 discordant pairs → `inconclusive`**, never "no effect". That is a statement about the task set, not about the guardrails.
- Stage 1: n=25 pairs (50 runs). Stage 2: extend to n=105 only if stage 1 shows lift or is merely underpowered.
- Futility stop: ≤2 discordant pairs after stage 1 → the task set is wrong (φ too low), not the layer.
- Report the paired 2×2 table and an interval on the lift, not just a p-value.

### Required N (the number the handoff was missing)

`python scripts/forge_ab_power.py --table` — exact, deterministic, stdlib only. n is per arm; runs = 2n.

| φ (discordance) | lift | n per arm | goose runs |
|---|---|---|---|
| 0.13 (today's measurement) | 10 pts | 105 | 210 |
| 0.13 | 15 pts | *unattainable — lift > φ* | — |
| 0.20 | 12.5 pts | 105 | 210 |
| 0.30 | 30 pts | **25** | **50** |
| 0.30 | 20 pts | 61 | 122 |
| 0.30 | 15 pts | 112 | 224 |
| 0.30 | 10 pts | 249 | 498 |

Minimum detectable lift at a fixed n (φ=0.30): n=20 → unreachable at any lift; n=30 → 27.4 pts; n=50 → 21.9 pts; n=61 → 19.9 pts. At n=105, φ=0.13 buys 10 pts, φ=0.20 buys 12.5 pts.

Baseline level is absent from this table on purpose: for a paired binary test it does not enter the power calculation. The handoff's requirement that "baseline failure rate > 0" is therefore not the binding constraint — **φ is**.

### Cost

The 14 s/run figure in the rescue A/B is a single-shot workflow harness, not a goose session; live sessions took minutes with several pytest iterations. At ~5 min/run: stage 1 (50 runs) ≈ 4 h; n=61 ≈ 10 h; n=105 ≈ 18 h. Budget stage 1 only, and extend on evidence.

## What must be true before a scored run

1. Each task runs in **its own sandbox directory** with its own `.forge/` copy. This gives clean state isolation, makes arm assignment a file copy, and avoids adding a new root entry for `disabledPlugins` (the root gate FAILs on any unlisted workspace-root name — `check_workspace_integrity.py` holds `ALLOWED_ROOT`).
2. `GOOSE_MAX_TURNS` and the per-task time limit set identically in both arms from `budgets:` in `tasks.yaml`.
3. Task specs state the **expected value from the spec, not from the repo** (oracle-first), and held-out tests must not be visible to the agent.
4. `ab_runs/` is git-ignored; `.forge-ab/` and `scripts/forge_ab_power.py` are the tracked, pre-registered artifacts.

## Known ceiling (state it in any conclusion)

Because goose does not expose the turn's tool trace at Stop (F2) and has no advise tier, this experiment can measure the *current* enforcement layer. It cannot measure a gate that verifies claims against the trace, and it cannot separate "deny" from "advise", which upstream issue #10358 identifies as the missing primitive. Any conclusion is scoped to "deny-only enforcement on gemini-flash-lite under goose".

## Open for the human

1. **Stage 1 is 50 goose runs (~4 h).** Worth it, or cut the ladder to 3 tasks and accept φ uncertainty?
2. **Model.** `gemini/gemini-flash-lite-latest` scores ~93% on the trivial task, which is why φ is small. A genuinely weaker model raises headroom but confounds "weak model" with "flash-lite". Recommendation: keep flash-lite, raise difficulty via the budget dial.
3. **The `.forge/` commit question is still open** from 2026-10-03 (`state.json` is runtime state and probably wants a `.gitignore`, not a commit). Not resolved by this work.
4. **`.forge/context.md` still holds the fabricated self-cert from the 2026-10-03 incident.** Harmless (SessionStart overwrites it) but it is misleading residue; delete it.

## Literature

- Resolution Diagnostics for Paired LLM Evaluation — arXiv 2605.30315. Paired-McNemar required-N is median 2.15× smaller than the unpaired Gaussian formula; report resolution ratio q = N/N*. Motivates the exact conditional binomial here.
- Adding Error Bars to Evals (Miller, Anthropic) — arXiv 2411.00640. Paired question-level inference; power analysis before the eval, not after.
- More Is Not Always Better: Cross-Component Interference in LLM Agent Scaffolding — arXiv 2605.05716. 32 000+ evaluations; All-In beaten by the best subset; 17–22-point harness-driven swings. The prior for F3.
- RewardHackingAgents — arXiv 2603.11337. Evaluator-tampering attempts in ~50% of natural-agent episodes, eliminated by evaluator locking, 25–31% overhead. The prior for F6.
- Establishing Best Practices for Building Rigorous Agentic Benchmarks (ABC) — NeurIPS 2025 D&B, arXiv 2507.02825. Impossible tasks inflate trivial-agent scores by ~38%. The rule in F5.
- EvilGenie — arXiv 2511.21654. Three reward-hacking detectors (held-out tests, LLM judge, test-file-edit detection); the LLM judge was the effective one, held-out tests only marginally better. The family-B metric shape.
- SpecBench — arXiv 2605.21384. Visible validation vs held-out tests as a two-way decomposition; high validation scores overestimate spec compliance.
- The Verification Horizon — arXiv 2606.26300. Hack Rate / Hacked Resolved / Clean Resolved; treating monitor-triggered successes as incorrect.
- TUA-Bench — arXiv 2606.28480. Task-execution time budget as a first-order performance factor (33.0% → 60.1% with no model or scaffold change). The difficulty dial in F5.
- τ-bench — arXiv 2406.12045. `pass^k` reliability framing; weaker models fail at hallucinated arguments and common sense, ~55% of failures.
- aaif-goose/goose#10358 — hooks can BLOCK or OBSERVE but not ADVISE; no tool-execution trace in the Stop payload. The ceiling in F2.
- goose hooks documentation — `PreToolUseResult` semantics, `on_failure`, `GOOSE_STOP_HOOK_BLOCK_CAP`, `disabledPlugins`.