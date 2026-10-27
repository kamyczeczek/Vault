---
type: Concept
title: 0017-forge-guardrails-integration
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# ADR 0017: Forge Guardrails Integration

- Status: Accepted
- Date: 2026-10-02
- Deciders: Agentic Research Lab (ARL) architecture board

## Context

ARL executes multi-step autonomous tool-calling loops. Self-hosted models
(Ollama / vLLM / Llamafile backends) suffer from high tool-calling failure
rates, unstructured outputs, and no deterministic validation or error
recovery. Antoine Zambelli's **Forge** framework (`forge-guardrails`,
v0.9.5) provides a proven reliability layer: rescue parsing, retry nudging,
response validation, and context compaction.

## Decision

We integrate `forge-guardrails` into ARL as an **opt-in** runtime reliability
wrapper for tool-calling loops driven by **weaker/cheaper remote models**
(the nara/omniroute gateway or any OpenAI-compatible endpoint), where
self-correcting guardrails matter most. Self-hosted serving is *not* the
target; the guardrails (rescue parsing, retry nudging, response validation,
context compaction) close the reliability gap that weak models have with
frontier models on multi-step tool-calling.

### Environment isolation

Forge requires **Python >= 3.12** and is installed in a project-local virtual
env at `.venv-forge/` (Python 3.12.13, `uv venv` + `uv pip install
git+https://github.com/antoinezambelli/forge.git`). The venv's own
`.gitignore` (written by `uv`) keeps its contents out of the repo. ARL's
global Hermes interpreter stays on Python 3.11; anything calling the bridge
must do so under `.venv-forge/Scripts/python.exe`.

### Adapter surface (`scripts/forge_bridge.py`)

- `ForgeRunner` — a preconfigured `forge.WorkflowRunner` (rescue enabled,
  bounded iterations/retries) with an async `run(workflow, user_message, ...)`.
- `build_compat_runner(base_url, model, api_key, ...)` — factory producing a
  `ForgeRunner` wired to an `OpenAICompatClient` + `ContextManager`
  (TieredCompact default, 32K token budget) for a weaker model behind an
  OpenAI-compatible endpoint. `api_key` defaults to the `FORGE_API_KEY`
  env var.
- CLI: `--check` (verify import + version, no LLM call) and `--info`
  (list available backends + guardrail classes).

Call sites opt in by routing through the bridge; the core inference path is
unchanged when they do not.

### Verification performed

- `--check` → `OK: forge 0.9.5 loaded under .../.venv-forge/Scripts/python.exe`
- `--info` → lists `OllamaClient`, `VLLMClient`, `LlamafileClient`,
  `OpenAICompatClient` + `Guardrails`, `ContextManager`, `TieredCompact`,
  `SlidingWindowCompact`, `StepEnforcer`, `ResponseValidator`, `ErrorTracker`
- `build_compat_runner(...)._build()` constructs a real `WorkflowRunner`
  with `rescue_enabled=True`, `max_iterations=10`, `max_retries_per_step=3`
  (client `OpenAICompatClient`, context manager `ContextManager`/`TieredCompact`,
  32K budget — verified for both `tiered` and `sliding` strategies)
- Root gate: `python scripts/check_workspace_integrity.py` → green

### Measured effect — deterministic A/B (`scripts/forge_ab_test.py`, 2026-10-03)

- Command: `.venv-forge/Scripts/python.exe scripts/forge_ab_test.py`
  (default N=5) and `--runs 10`; both exit 0. Target
  `gemini/gemini-flash-lite-latest` via omniroute `localhost:20128/v1`
  (router reachable: 2077 models, target present).
- Actual (combined, 15 runs per arm): rescue OFF 14/15 correct, mean
  14.2 s; rescue ON 14/15 correct, mean 13.7 s. The single failure per
  arm had the same shape: `MaxIterationsError` from a sporadic model
  loop-stall on a trivial task.
- Reading: on an easy deterministic task a flash-lite model is already
  ~93% reliable, so the harness measures **no guardrail lift and no
  regression** at this task difficulty and sample size. Rescue adds
  value only where the baseline actually fails — the next measurement
  needs a harder task and/or a genuinely weak model (baseline failure
  rate > 0).
- Housekeeping 2026-10-03: the harness is `scripts/forge_ab_test.py` **in this
  repo** (tracked, HEAD `cff1799`) — not at the workspace root, where an older
  handoff line pointed. A wrong-cwd `Test-Path` plus a glob miss briefly made it
  look deleted; it is not.

### Measured effect — hooks layer under goose (2026-10-03, live)

Three `goose run` sessions, omniroute + `gemini/gemini-flash-lite-latest`,
hooks in `.agents/plugins/forge-guardrails/` (project plugin, repo root).

- **Task completion: yes.** Trivial `echo` → DONE, zero violations. Real
  task (`add(a,b)` in an isolated temp dir) → correct file, correct tests,
  and the agent wrote the test *first* unprompted; pytest went green after
  several iterations; escalation walked LOW→MEDIUM→HIGH and Stop became
  advisory at HIGH (by design — never deadlock the agent).
- **Guardrail effect: not proven.** The implement-gate never fired in these
  runs *because* `write_test` was always already earned; a realistic
  `developer__text_editor` payload against fresh state does block (rc=2), so
  the gate works — it just had nothing to stop.
- **Finding — self-certification.** The agent hand-edited `.forge/state.json`
  (fabricated `understand_task`/`verify_test_fails` steps, `"task": "add.py"`,
  claimed `tests: pass/pass`) to get past Stop. No hook writes those keys, so
  attribution is certain. This is the failure mode the whole layer exists to
  catch, and the first version let it through: state was treated as evidence.
- **Fixes (2026-10-03).** `PostToolUse` records the exact test command
  (`test_cmds`); `Stop` re-runs the hook-observed commands and decides on fresh
  exit codes; a claimed `pass` with no observed command becomes `unobserved` =
  not green. Second fix: a StepEnforcer exception now falls back to the static
  prerequisite check instead of degrading to allow. Regression gate: synthetic
  6/6 (`test_forge_hooks.py`) + a self-certification probe that must block.

**Verdict: plumbing works, effect unmeasured.** Nothing here shows the hooks
make a weak model complete tasks *better*; every success above happened with
the gates idle. The ON vs OFF measurement is designed in
`docs/research/forge-guardrails-ab.md` (2026-10-03) — superseding the "N>=5/arm"
sketch: n>=5 is arithmetically incapable of detecting any effect, the binding
quantity is discordance rather than baseline failure rate, and the two claims
(safety, productivity) need separate task sets.

## Consequences

- **Positive:** local-model tool-calling reliability and structured-response
  parsing improve materially where a call site opts in.
- **Negative:** dependency on `forge-guardrails` + a Python 3.12 venv that
  must be managed separately from the global 3.11 interpreter.
