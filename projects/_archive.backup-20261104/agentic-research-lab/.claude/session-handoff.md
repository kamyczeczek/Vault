# Session handoff — 2026-10-03 (agentic-research-lab)

## Status

`goose_decision_graph_wrong_model` — 2026-10-03: the first full Goose run for the topic "building a decision graph as support for an AI agent in debugging and work organization" used the wrong model: `nara/agnes-3-flash`, not the required `omniroute/gemini-flash-lite-latest`. It ran for 441.86 seconds and eventually produced corpus chunks including `02_decision_graphs_ai_agents_debugging_web_research` and `02_cleverthis_adr007_decision_tree_correction`, but it is not valid evidence for the target model.

`goose_decision_graph_correct_model_ready` — 2026-10-03: verified that Goose accepts and reports the required configuration:

```text
goose run --provider omniroute --model gemini/gemini-flash-lite-latest
```

The smoke run reported `provider: omniroute` and `requestedModel: gemini/gemini-flash-lite-latest`. A second full run was started with this configuration and the `agent-reach` requirement, but its captured output is dominated by project-tree exploration and needs final artifact review before any success claim.

## Required next run

Run Goose from the ARL directory with the required model and a fresh evidence directory:

```cmd
cd projects/research/agentic-research-lab
goose run --provider omniroute --model gemini/gemini-flash-lite-latest --instructions "../../../scripts/_scratch/goose_g3_decision_graph_agent_reach_task.txt" --output-format json --stats --max-turns 40
```

The task must execute this exact evidence chain:

1. `agent-reach doctor --json` before reading the repository.
2. Internet research through the `agent-reach` web backend, with exact URLs recorded.
3. Fresh source notes in `INBOX/`, not only existing `knowledge/raw/`.
4. `scripts/ingest.py` result and graph rebuild result.
5. Graph query and exact new chunk IDs tied to the fresh sources.
6. Non-scratch reflection digest and candidates with claim-to-source links.
7. One small implementation change directly derived from the reflection.
8. Tests and project checks, with before/after evidence.

Do not count pre-existing corpus chunks or old reflection artifacts as evidence for this run. If any stage lacks a fresh artifact, verdict is `FAIL`.

## What the first run taught us

- The weak model spent most of its budget exploring `tree`, `dir`, `MAP.md`, and project documentation before using the required web skill.
- A broad prompt did not enforce stage ordering strongly enough.
- Existing artifacts made it difficult to distinguish new output from old output.
- The run needs per-stage checkpoints, a fresh evidence directory, and hard failure rules.
- The model must be named explicitly in the command and verified from Goose metadata, not inferred from configuration.

## Current blockers

- The correct-model full run has not yet been judged from its final output.
- The internet source trail, fresh `INBOX` files, reflection provenance, implementation diff, and final checks must be verified as belonging to that run.
- G3 remains human-owned: after the run, a human must verify that the implementation is grounded in the retrieved evidence and that the artifact trail is complete.
- The earlier reflection artifact had missing `provenance.fingerprint` and was created with `--scratch`; it cannot satisfy G3.

## Related artifacts

- `scripts/_scratch/goose_g3_decision_graph_task.txt` — first, insufficient task prompt.
- `scripts/_scratch/goose_g3_decision_graph_agent_reach_task.txt` — corrected prompt requiring `agent-reach` and stage evidence.
- `.ralph/runs/2026-10-02_plain-language-meter/GATES.md` — G3 contract and required evidence.
- `docs/research/plain-language-meter.md` — design context.

## Human review checklist for G3

A run can pass G3 only if the reviewer can identify:

- the exact research question,
- URLs and source notes created by this run,
- ingest and graph rebuild outputs,
- new retrieved chunk IDs,
- reflection claims linked to those IDs,
- the implementation diff or output,
- final test/verification result,
- and a judgment that the implementation follows from the evidence rather than from pre-existing memory.
