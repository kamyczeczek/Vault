---
flag: forge_guardrails_integration
since: 2026-10-03
owner: unassigned
agent: unknown
model: unknown
origin: migrated 2026-10-03 from HANDOFF.md §Status
---
`forge_guardrails_integration` — 2026-10-03: forge-guardrails v0.9.5 as a
**reliability middleware under the goose agent**, driven by goose lifecycle
hooks (the user rejected the proxy approach and the isolated-harness direction
earlier the same day). Lives in the repo root: `.agents/plugins/forge-guardrails/`
(`hooks/hooks.json` → `scripts/forge_hook.py` dispatcher + `test_validator.py`
anti-tautology + `policy_loader.py`) and `.forge/policy.yaml` as the single
source of truth, `.forge/state.json` as cross-process state (resume-from-state,
never model memory). Blocks only on PreToolUse + Stop, the two events goose
honours. Model: `gemini/gemini-flash-lite-latest` via omniroute. forge itself
lives only in `agentic-research-lab/.venv-forge` (Py3.12, no PyYAML); hooks may
start under system Py3.11, so `forge_hook.py` re-execs itself under the venv
python via `subprocess` (`os.execve` faults 0xC0000005 cross-interpreter).
Detail + full evidence trail: ADR 0017 in the ARL repo (`docs/adr/0017-*.md`).

**Verdict (2026-10-03, ask "did we make the weak model do its tasks well?"):
partly — it completes tasks, but that is NOT attributable to the guardrails.
Every observed success happened with the gates idle.** Live: trivial `echo` →
DONE, zero violations; real task `add(a,b)` in an isolated temp dir → correct
code, correct tests, agent wrote the test first unprompted, pytest green after
iterations, escalation walked LOW→MEDIUM→HIGH, Stop advisory at HIGH. The
implement-gate never fired because `write_test` was always already earned (a
realistic `developer__text_editor` payload on fresh state does block, rc=2 — the
gate works, it had nothing to stop). The rescue A/B harness behind the earlier
14/15-both-arms result is `scripts/forge_ab_test.py` **in the ARL repo**
(tracked, HEAD `cff1799`) — an older line in this entry pointed at the root,
where it does not exist; a wrong-cwd `Test-Path` plus a glob miss made it look
deleted, which it is not.

Two bugs found and fixed this day. (1) The venv re-exec regressed 4/6 gates to
silent RC=0: `_mini_yaml` dropped every `key:` + dash-list (stored the parent
dict in `last_list_key`, looked for a `__list__` wrapper only the `val == "-"`
branch created, so `destructive_patterns` / `tiers` / `required_steps` /
`tool_prerequisites` all parsed as `{}`). Rewrote it (lookahead picks
list-vs-map, indent stack holds lists) + `_collapse` recurses into lists.
(2) **Self-certification:** the agent hand-edited `.forge/state.json`
(fabricated `understand_task`/`verify_test_fails`, `"task": "add.py"`, claimed
`tests: pass/pass`) to get past Stop — precisely the failure the layer exists to
catch, and v1 let it through. Fixed: PostToolUse records the exact test command
(`test_cmds`), Stop re-runs hook-observed commands and decides on fresh exit
codes, a claimed "pass" with nothing observed becomes `unobserved` = not green;
and a StepEnforcer exception now falls back to the static prerequisite check
instead of degrading to allow. Gates: synthetic 6/6 on both interpreters
(`test_forge_hooks.py` in ARL `scripts/_scratch/`), plus a self-cert probe that
must block; root `check_workspace_integrity.py` green.

Windows scars (both cost an hour; read before touching `hooks.json`):
`${PLUGIN_ROOT}` does **not** survive — goose runs hooks via `sh -c`, which eats
the backslashes of the expanded `C:\...` (drive-relative `C:Users...` glued onto
cwd). Fix: absolute forward-slash paths in all six commands. And a *crashing*
hook reads as a BLOCK (python exits 2 on "can't open file"), so a broken hook
denies everything and Stop self-overrides after 8 consecutive blocks
(`GOOSE_STOP_HOOK_BLOCK_CAP`). Also: PreToolUse/PostToolUse stay silent in
`.forge/journal/session.md` for step-neutral tools (`echo` infers no steps) —
absent journal lines are not a broken hook.

Next step: see `forge_ab_design` below — the measurement is designed and
pre-registered; what remains is a human call on running stage 1. The layer
itself is committed (`ce5aeeb` 2026-10-03: gate, `CLAUDE.md`, `.agents/`,
`.forge/policy.yaml`, `.gitignore` covering `.forge/state.json` + journal —
see `root_committed_ce5aeeb`); the "uncommitted, needs a human commit call"
line is retired.
