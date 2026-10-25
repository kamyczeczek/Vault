---
type: Concept
flag: hermes_perf_d17
since: 2026-10-02
owner: unassigned
agent: unknown
model: unknown
origin: migrated 2026-10-03 from HANDOFF.md §Status
title: hermes_perf_d17
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---
`hermes_perf_d17` — 2026-10-02: Hermes runtime tuned for tokens-per-task
(D17 in DECISIONS.md, lever table in TOKEN-EFFICIENCY.md § Hermes runtime
levers): `config.yaml` now sets `prompt_caching.cache_ttl: 1h` — the only
config delta; an `auxiliary.compression` → `nara/agnes-3-flash` pin that had
been set was **reverted the same day on user rule: never pin a model in
config, everything runs on the model of the session** (slot back to `auto`
= session main model; see D17 § User rule). Verified CRLF-safe against
`config.yaml.bak-20261002` (diff: only the `prompt_caching` section).
Per-task meter landed: `scripts/hermes_per_task.py` (stdlib read of
`state.db` `sessions`/`session_model_usage`; baseline: 146 sessions,
86.4% hit ratio, 3.8M avg tokens/task, new_session-ended tasks 0.95 vs
cli_close 0.82).
Next step: after a tool-heavy Hermes session run
`python C:/Users/Mateusz/AppData/Local/hermes/hermes-agent/scripts/micro_compaction_report.py`
to measure compaction effect on the session's own model; separately, check
nara/omniroute `session_affinity_header` support (external, unfetched —
401 on `/v1/models`). Committed as `3fac7e7` (root repo; the GATES ledger
stays untracked under `scripts/_scratch/`).
