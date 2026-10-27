---
type: Concept
title: 2026-09-15_provenance-stamp-enforced-spawn-hangs
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# Reflection — provenance stamp enforced; reflection spawn hangs at the harness level

Date: 2026-09-15
Project: projects/workspace-research
Trigger: T1 (a problem was hit), T2 (a rule was added), T3 (an output was retro-stamped)

## Problem

P5 (every output must be traceable to the corpus + plan version that produced it) was an
unexercised contract: `spawn.py` demanded a provenance stamp in its prompt, but nothing
checked for one. All 7 digests and 7 candidate files carried no stamp, and three digests
(`planning-research-workflow`, `planning-tasks`, `workspace-health`) still claimed the
pre-repair fingerprint `35b86bc954fa` / `1cf1e4aea87c` after the corpus tag repair moved
the corpus to `0626262b2982` — their routing claims were stale.

Separately, spawning a live reflection to exercise the contract produced **no output after
10 minutes**, twice (`planning-verify` this session and the prior one).

## Root cause (spawn hang)

Not the pipeline. Isolated by elimination:

| Test | Result |
|---|---|
| `omp agent -p "PING_OK"` **with** the workspace-research extension | timeout 120s, no output |
| `omp agent -p "PING_OK"` **without** any extension | timeout 90s, no output |
| `omp --version` | instant, `omp/18.1.4` |

A trivial prompt with no extension still hangs, so the cause is in `omp agent`'s
orchestrator mode (it stays alive after responding), not in the prompt or the extension.
`spawn.py` called `subprocess.run(cmd, input="")` with no timeout, so a spawn blocked
forever and orphaned omp/bun children that held `graph.db` open.

## Solution

**1. `check_reflection.py` now enforces P5 as a hard gate** (returns 1 on failure):
`provenance_ok(text, live_fp, plan_ver)` requires `fingerprint:`, `plan_version:`,
and `phase:` tokens, and the fingerprint must equal the live corpus hash. Regexes accept
both prose (`fingerprint: abc`) and JSON (`"fingerprint": "abc"`) so one validator covers
digests and candidate rows. Runs on every digest **and** its paired `.jsonl`.

**2. Retro-stamped all 7 digests + 7 candidate files.** The three stale digests were
re-fingerprinted to the live corpus and marked `regenerated after corpus tag repair`
rather than silently re-dated; candidate rows carry a `provenance` object plus flat tokens.

**3. Triage: 25 of 35 candidates closed.** 24 `accepted` (bets delivered by `d2572cc` /
this session — provenance stamp, topic repair, shadow-dir removal, hard-fail gates),
1 `rejected` (`C9`, empty placeholder with no claim/bet/evidence), 10 remain `proposed`
as genuinely open work (`W5` raw-source manifest, `W6` INBOX atomic purge,
`P4` per-run budget separation, `planning-research-workflow-memory-world-model`, the
`icm_reflection_*` cluster, `workspace-health-observability-headless`).

**4. `spawn.py` now has a 300s timeout** returning exit 3 on expiry instead of hanging.

## Verification

- Gate: `OK: checked 7 digests / 7 candidate files — all grounded.`
- Contract proven with negative controls — both real failure modes fail correctly:
  missing stamp → `missing \`fingerprint:\` provenance stamp`; wrong hash →
  `fingerprint deadbeef1234 != live corpus 0626262b2982 (stale output)`.
- `watch.py --once` → `[watch] no change — graph fresh`; INBOX empty.
- The live-spawn test could not be completed: `omp agent` hangs at the harness level
  (evidence above). The stamp contract is therefore proven in-process through the exact
  functions the gate and the prompt use, not through a live agent run.

## Prevention rules

- **R1 — an unenforced contract is not a contract.** Any requirement written into a prompt
  must have a matching check in the gate; `spawn.py` asked for stamps for two sessions
  while nothing validated them.
- **R2 — never call an orchestrator subprocess without a timeout.** An agent that stays
  alive after responding turns a bounded task into an infinite hang and orphans
  child processes that hold derived indexes open (compounding the Win32 lock).
- **R3 — validate a contract with its negative controls, not just the happy path.** The
  gate's value is that it fails on a missing stamp *and* on a stale fingerprint; only the
  paired failing cases prove it works.
