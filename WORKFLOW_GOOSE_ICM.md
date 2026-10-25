# Goose research-to-implementation workflow — ICM design

## Form and purpose

This is a **Pipeline** nested inside the root workspace, with each experimental run producing a reviewable evidence bundle. The repeating unit is one Goose run for a research question. The deliverable is not an automatic G3 pass. It is a human-reviewable `REVIEW.md` plus traceable artifacts.

The filesystem is the state machine. Each numbered stage owns one job and writes plain-text outputs. A later stage may not consume an absent or failed checkpoint.

## Factory versus product

**Factory, stable across runs:**

- `scripts/_scratch/goose_g3_decision_graph_agent_reach_task.txt` — task template, to be replaced by the hardened launcher design.
- `.claude/goose-workflow-hardening-handoff.md` — design rationale and review contract.
- `.ralph/runs/2026-10-02_plain-language-meter/GATES.md` — G3 acceptance requirements.
- `skills/agent-reach/` and `skills/icm-architect/` — method references.

**Product, new per run:**

- `.dgc-evidence/runs/<run-id>/` — checkpoints, source manifest, URLs, fingerprints, diff, logs, and review bundle.
- Project `INBOX/` intake files and downstream corpus/graph/reflection artifacts, all listed in the run manifest.

## Pipeline stages

### 00_prepare

**One job:** establish identity and clean boundaries.

**Reads:** root/project entry files and factory contracts only.

**Writes:** `manifest.json`, `baseline.json`, `00_prepare.json`.

**Must record:** run ID, timestamp, repository HEAD, baseline status, provider `omniroute`, exact model `gemini/gemini-flash-lite-latest`.

**Human check:** confirm the baseline and target model before allowing Goose to continue.

### 01_web_research

**One job:** obtain external sources through `agent-reach`.

**Reads:** `skills/agent-reach/SKILL.md` and its relevant reference.

**Writes:** source URLs, retrieval logs, source notes under the run intake and fresh `INBOX/` paths, `01_web_research.json`.

**First action:** `agent-reach doctor --json`. No tree listing or broad repository read may precede it.

**Human check:** verify that each URL is real, relevant, and present in the source notes.

### 02_ingest

**One job:** process only this run's `INBOX` sources through the official ingest interface.

**Reads:** fresh intake notes and `scripts/ingest.py` contract.

**Writes:** `02_ingest.json`, new manifest rows, and a source-to-chunk mapping.

**Human check:** confirm every claimed fresh source has a corresponding ingest result.

### 03_graph

**One job:** rebuild or update the derived graph and capture its identity.

**Reads:** current corpus and graph build contract.

**Writes:** `03_graph.json` with command, exit code, graph fingerprint, node/edge counts, and new chunk IDs.

**Human check:** confirm the graph fingerprint is current and the new chunk IDs resolve.

### 04_retrieval

**One job:** query the graph for the research question.

**Reads:** `03_graph.json` and the query contract.

**Writes:** `04_retrieval.json` with exact query, ranked chunk IDs, snippets, and a relevance judgment.

**Human check:** verify that the retrieved evidence is from this run, not merely an older similarly named chunk.

### 05_reflection

**One job:** synthesize only the retrieved evidence into claims, decisions, and candidate actions.

**Reads:** `04_retrieval.json`, retrieved chunks, reflection contract.

**Writes:** non-scratch digest, candidates, `05_reflection.json`, claim-to-chunk links, and matching graph fingerprint.

**Human check:** inspect one claim and follow its links back to the source chunk.

### 06_implementation

**One job:** apply one small change derived from one named reflection claim.

**Reads:** approved reflection artifact and implementation contract.

**Writes:** `06_implementation.json`, a diff, and before/after evidence.

**Human check:** answer: "Which exact reflection claim caused this change?" If the answer is not in the checkpoint, reject the implementation as unrelated.

### 07_verification

**One job:** run focused and project acceptance checks against the actual change.

**Reads:** implementation diff and verification contract.

**Writes:** `07_verification.json`, real exit codes, test output paths, and final artifact fingerprints.

**Human check:** distinguish a check of the changed result from a green check on stale artifacts.

### 08_review

**One job:** assemble the human decision packet.

**Reads:** all stage checkpoints, manifest, diff, and verification results.

**Writes:** `REVIEW.md` and a read-only summary package.

**Human check:** human selects `PASS`, `FAIL`, or `BLOCKED`. No automatic promotion.

**Mandatory re-verification (2026-10-03, from `review_workflow_live`):**
the human reviews via `python scripts/review.py .dgc-evidence/runs/<run-id>/`
(one command: finds REVIEW.md, re-runs `verify_review_evidence.py`, bakes
its rc + summary into the HTML as a banner, renders, opens the browser).
The banner is launcher-generated — never hand-typed by the agent, so it
cannot be mistyped. A run whose REVIEW holds pytest claims but whose banner
is red is `BLOCKED`, not reviewable. A research-only REVIEW with no pytest
claims gets a neutral gray banner (nothing to re-run), not a red one.
Rationale: 2026-10-03 agent self-reported "11 passed" for a 4-test file;
the verifier caught it (claims 11 / fresh 4). Canonical location per run:
`.dgc-evidence/runs/<run-id>/REVIEW.md` (+ `REVIEW.html` + `DECISION.json`
beside it); `runs/LATEST` names the run awaiting verdict.
`scripts/_scratch/REVIEW_*` were throwaway tool demos — deleted 2026-10-03.

## Handoff contract

A stage handoff is a file, not a chat claim:

```text
stage N output → stage N+1 input
```

Each checkpoint has these fields:

```yaml
run_id:
stage:
status: PASS | FAIL | BLOCKED
started:
finished:
command:
exit_code:
inputs: []
outputs: []
fingerprints: {}
blockers: []
```

The run is `BLOCKED` if a required artifact is missing. It is `FAIL` if the agent violates ordering, model identity, intake path, provenance, or evidence freshness.

## Review packet

`REVIEW.md` is the root-level human surface and must fit on one screen plus linked details:

- proposed verdict;
- exact provider/model evidence;
- question and stage table;
- URLs and fresh `INBOX` paths;
- source-to-chunk mapping and graph fingerprint;
- retrieved chunk IDs;
- reflection claim-to-source table;
- claim-to-diff and before/after verification;
- blockers and stale-artifact warnings;
- explicit form:

```text
G3: PASS / FAIL / BLOCKED
Model: PASS / FAIL
Agent-reach first action: PASS / FAIL
Fresh web evidence: PASS / FAIL
Fresh INBOX intake: PASS / FAIL
Ingest + graph: PASS / FAIL
Retrieval: PASS / FAIL
Reflection: PASS / FAIL
Implementation traceability: PASS / FAIL
Verification: PASS / FAIL
Re-verification banner (launcher-generated, green/red/gray): PASS / FAIL
Verdict (DECISION.json via `review.py --decide`): PASS / FAIL / BLOCKED
Human groundedness judgment: PASS / FAIL
Notes:
```

## Walk test

A cold reviewer should be able to open root `HANDOFF.md`, follow the link to this workflow and then to one run's `REVIEW.md` without crawling the repository. Each stage contract names exact inputs, outputs, and one human check. The root handoff remains a pointer, not a second copy of this design.

## Known ICM boundary

This pipeline is intentionally sequential and human-gated. Real-time multi-agent coordination, high-concurrency serving, and automatic mid-pipeline branching require framework infrastructure beyond this ICM design.
