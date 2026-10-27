---
type: Concept
title: EXPERIENCE
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# EXPERIENCE.md — agentmemory stack runbook & scars

Local experience (D11). The agentmemory engine is an *external runtime*; this project
treats it as the capture/sensor layer. Durable knowledge lives in markdown (ICM).

## Stack topology (Windows, verified 2026-09-30)

- **Engine**: `iii.exe` (native, `AppData\Local\agentmemory\engine\bin`) — holds port `:3111`.
- **Worker/launcher**: `node <npx-cache>\node_modules\@agentmemory\agentmemory\dist\cli.mjs`
  (cache instance `ba4b5775a0ab44e2`) — spawns the engine; MCP shim `npx -y @agentmemory/mcp`
  (stdio, `cwd: ~/.agentmemory` in `~/.pi/agent/mcp.json`) proxies to `:3111`.
- **Config**: `~/.agentmemory/.env` — read **at engine boot only** (no hot reload).
  Any change ⇒ engine restart.
- **Restart**: `powershell -File scripts/restart_agentmemory.ps1`
  (add `-Elevated` if the tree was launched elevated — UAC on the kill step; the respawn
  is always non-elevated/detached, so after one `-Elevated` restart plain restarts work).

## npx-cache patches (per-package-instance — they die on package update)

- Patches P1/P2/P3 applied by `scripts/patch_agentmemory_template_distillation.py`
  (plus the root `reapply-agentmemory-patch.ps1`).
- **Reapply runbook (post npx update)**: re-run *both* patch scripts → restart engine →
  run `python preflight.py` (checks model + engine + circuit).
- Patches are **secondary** while the LLM path is active: they only fire when the engine
  resolves `provider.name === "noop"`. With a valid `.env` + LLM key the native LLM
  distillation runs and the template tiers are dormant.

## Silent-failure scars (probe these; never trust surface flags)

1. **`success: true` + empty result** = LLM circuit open (zero-LLM mode). Probe:
   `memory_health` → `circuitBreaker.state` closed, `failureCount:0`, and `totalObservations`
   actually moving downstream.
2. **"Provider: ✓ llm" = key set, model unverified** (404 scar: `nex-n2.5-pro` did not
   exist on the router). Probe: `GET {OPENAI_BASE_URL}/models` — must list the configured
   model. `preflight.py` now does this at session start; `configure_agentmemory_env.py`
   validates at generation time.
3. **`chmod` is a no-op on NTFS** (`.env` found world-readable 0666). Use
   `icacls <path> /inheritance:r /grant:r "User:R,W"` — the generator does this on Windows.
4. **MSYS/Git Bash mangles Windows commands** (`taskkill /F`→`F:/`, `$_`→`/usr/bin/bash`,
   `dir /b`→`- /b`) and the harness once injected `\r` into tool-arg strings. Mitigation:
   write commands to a file; on 2 failed attempts at an operation, rewrite the whole
   artifact instead of a third variant.
5. **Elevated process tree**: `taskkill` fails with "Access denied" even for the same
   user (engine was in session 12, elevated). Kill via `Start-Process taskkill -Verb RunAs`.
6. **Determinism gate is a dirtying-convergence, not a pure check** (observed 2026-09-30):
   `build_graph.build()` has an "automatically re-sync reflection routes" step that
   *writes* `reflection/digests/*.md` + `reflection/candidates/*.jsonl` (fingerprint
   restamp + `returned_ids`) during the build. So after any `check_reflection --replan`
   (or any candidate edit), the first `check_graph_determinism.py` run's build #1 mutates
   the candidates that build #2 reads → "output differs" / edge-count drift (12436 →
   12439, stable within the run). The second run converges and passes. This is the same
   defect class git history fixed before ("determinism gate was dirtying the tree it
   verifies") and it regressed. Symptom right after a restamp: 3-artifact drift
   (GRAPH-DIGEST.md, graph_index.json, generation.json). Recovery: re-run the check
   once; it passes. Real fix (open work): make the re-sync step read-only or run it
   after edge/FTS construction in a way that cannot change the build under test.

7. **"Look one level up at the workspace root" is a depth that silently breaks on a
   group move.** 2026-10-02: after the move to `projects/research/<repo>`, anything
   that resolves the *workspace root* by a fixed number of `..` hops ends up one hop
   short. Two instances aborted every commit and hard-FAILed a gate:
   - `scripts/quality_check.py` Q0 resolved the root gate at `ROOT.parents[1]`
     (= `projects/scripts/check_workspace_integrity.py`, missing) → pre-commit "No
     such file or directory". Fixed to `ROOT.parents[2]`.
   - `scripts/check_entropy.py` resolved the library index at
     `ROOT.parents[1]/library/index.json` (= `projects/library/...`, missing). The real
     index is at the workspace root `library/index.json` = `ROOT.parents[2]`. The empty
     lookup made `library_sources()` return `{}`, so 4,209 chunks (40%, across 9 book
     sources) read as "no recoverable source" and the hard Q19 gate FAILed. Fixed to
     `ROOT.parents[2]`.
   Probe: any new "look up to root / workspace" path — grep for `parents[` and
   hard-coded `../..` in `scripts/*.py` and re-count hops from the *current* depth.
   Two instances fixed (`1d20066`); treat any other `parents[1]`-to-root as suspect.

8. **Commit hygiene + verification scope: the workspace-wide home is root
   `SCARS.md`** (promoted 2026-10-05 on owner feedback — one home per fact,
   so `benchmark-core` and every other project see them too). Read that
   entry before committing anything or narrowing any verification. What stays
   in THIS home is the ARL delta only:
   - `agent_commit.py` rolls back its own staging on every pre-commit failure
     (`unstage()`, pinned by `tests/test_agent_commit.py::StagedResidueTests`
     — do not re-add manually after a fail; the tool is the only caller that
     stages explicitly).
   - **Orphan-repo pin (measured, not assumed):** on git 2.54,
     `git reset -q HEAD -- <path>` unstages on a HEAD-less repo, while
     `git restore --staged` FAILS there (rc 128, "could not resolve 'HEAD'").
     Probe: `scripts/_scratch/probe_unstage_orphan.py`; regression test
     `StagedResidueTests::test_unstage_works_on_orphan_repo`. If you see an
     orphan-branch complaint again, run the probe before changing `unstage()`
     — the "restore fallback" is non-portable in the wrong direction on this
     host.
   - the stale-`MAP.md` root-gate advisory is cleared at the FIRST signal
     with `python ../../../scripts/build_project_map.py .` (ARL's regen
     command; the why is in root `SCARS.md`).

9. **Never narrow a verification to survive a timeout.** Full
   `pytest tests/` exceeded the 60s tool timeout, so the session ran only
   the two relevant files and reported "22/22" with "pominięte: pełna suita"
   as a note. The honest report did not hide it — but a narrowed verification
   is a weaker claim, not a shorter one. Rule: on timeout, raise the tool's
   timeout limit (or run in the background) and get the full-suite number;
   name every excluded file as "not verified". "N/22 green" is only a claim
   about those 22. (Workspace-wide copy lives in root `SCARS.md`; this entry
   records the ARL incident: the first subset-run that the owner then
   measured as 309/309.)

## Configuration (durable)

- `python scripts/configure_agentmemory_env.py` — writes `~/.agentmemory/.env`, validates
  `OPENAI_MODEL` against the router `/v1/models` (exits with the free-model candidates on
  mismatch), restricts the ACL on NTFS.
- Working free model on `router.bynara.id` (57 models, 2026-09-30):
  `nemotron-3.5-lightning-free` (also `space-bunny-alpha`, `agnes-3-flash`).
- `AGENTMEMORY_SEMANTIC_MIN_SUMMARIES=1` — semantic-tier floor (default 5); the "fewer
  than 5 summaries" string in the dist is cosmetic, the env var is the real gate.
- No-LLM fallback (only if the router goes down): `AGENTMEMORY_TEMPLATE_SUMMARIZE=true`
  + `AGENTMEMORY_TEMPLATE_SEMANTIC=true`.

## Rotation & secrets

- Decision (2026-09-30, user): the nara router key is **not** treated as sensitive;
  it appears in local pi transcripts by design and needs no rotation. Do not re-raise
  key rotation for this key.
- Secrets still live in `~/.agentmemory/.env` only; never commit them to the repo.
- Leak scanner (gitignored, one-shot): `python scripts/_scratch/scan_secret_leak.py`
  reports file + line + masked shape, never the key itself.

## Preflight gate semantics (2026-10-01, user decision)

- Engine-down check downgraded **hard → advisory**. Evidence: `close_session.py`
  is the only runtime caller of `:3111` and it skips consolidation gracefully when
  the engine is down (`WARN ... consolidation skipped`). Nothing in
  pipeline/stages/reflection calls the engine at runtime. .env/model checks stay
  hard (the 2026-09-30 silent-distillation scar). Restart the engine only when you
  actually want a session distilled before close.
