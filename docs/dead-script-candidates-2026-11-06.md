# Dead-script candidates — 2026-11-06

> Analysis only — **no file was deleted** in this session. Inputs: dependency map
> `docs/dependency-map-2026-11-06.md` (commit `91a7f6a`) + fresh ref re-count on HEAD
> (`git grep`, non-`_scratch` tracked files, self excluded). Scripts/ tree unchanged
> since the map (only handoff/docs commits after it), so ref counts are current:
> **143 tracked files under `scripts/`** excluding `scripts/_scratch/` = 142 scripts +
> `scripts/index.md` (the map counted `index.md` as INSTRUCTION).

Ref classes: **refs-docs** = mentioned only in markdown; **refs-index** = listed in
`scripts/index.md` (auto-generated listing); **manual** = documented human-run entry
point; **tests** = pytest discovery (invisible to ref scan, still a live use).

## Candidates — one-off tools, recommend delete after owner OK (4)

| Script | refs | Rationale |
|---|---|---|
| `scripts/move_state_description.py` | 6 docs | one-off mover from the `session-2c` plan; no callers, no tests, no manual-use docs |
| `scripts/gate_checks.py` | 3 docs | kb-knowledge-split tranche (2026-10-25) gate helper; kb-split closed |
| `scripts/check_kb_layout.py` | 5 docs incl. `brain/decisions/ADR-008-kb-subfolder.md` | kb-cleanup tranche (2026-10-29) checker; ADR stays as history, script has no planned future run |
| `scripts/debug_skill_resources.mjs` | 3 (incl. `scripts/index.md` self-listing) | debug helper, no referrer in `skills/` or `.agents/`; **caveat**: `~/.pi` global config is outside this repo — owner must confirm no out-of-repo invocation |

## Undecided — utility/manual tools, owner decision (3)

| Script | refs | Note |
|---|---|---|
| `scripts/dump_agent_config.py` | 4 docs | live product: wrote `handoff/agent-config/SNAPSHOT.md`; flag `opencode-shell-permission-key-2026-11-06` compares against it — decide with the SNAPSHOT pipeline |
| `scripts/smoke_load_deepseek.py` | 4 docs | smoke test of the DSH zstd/v4 loader that `extract_exact_sessions.py` uses — documents loader behaviour, not wired |
| `scripts/smoke_zstd.py` | 4 docs | same family as above |

## Keep — tested, data, or manual entry points (not dead despite 0 code refs)

- `scripts/test_did_sessions.py`, `scripts/test_preflight_agent.py`, `scripts/test_handoff_closer_e2e.py` — pytest suites for live scripts (discovery is their invocation).
- `scripts/raw_sessions_drive.bat` — owner-run entry (`cmd /c scripts\raw_sessions_drive.bat N`), E2E-verified in flag `raw-sessions-github-push-2026-11-06`; also carries the foreign `COUNT=5 → 1` change (Session 4).
- `scripts/memory/queries.jsonl` — retrieval-eval data, consumed by `scripts/eval_memory_retrieval.py`.

## No action

- **ENTRY/GATE (20)** — gates and wired entries; never delete without caller audit (core chain: `check_workspace_integrity.py` → `close.py` → `build_handoff.py`/`build_state.py`/`scan_secrets.py`).
- **INTERNAL (85)** — script-to-script wiring.
- **ZERO (27)** — auto-generated `index.md` stubs + `verify_report_tests/fixtures/`; regenerating builds churn if deleted individually.

## Procedure if the owner approves deletion

Per-script commit, message states the evidence (0 refs outside docs + tier), verify
after each: `python scripts/check_workspace_integrity.py`, `python scripts/build_handoff.py --check`,
then rebuild views. Delete candidates one per commit — never as a batch.
