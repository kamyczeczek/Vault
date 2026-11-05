---
type: Concept
title: spawn-fix-probe
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

fingerprint: 5f4f9d29057b plan_version: ad0a031aa564 phase: 04_reflect routing: ask.py --tag icm --tag reflection; ask.py --tag context-engineering --tag reflection; ask.py --tag planning --tag decomposition (card=1 -> route.py --threshold 3, ADAPT depth=1 via=classical-planning => [ai-planning-classical, ai-planning-htn-pddl]); ask.py --tag context-engineering --tag memory; ask.py --tag icm --tag planning; ask.py --tag planning --tag world-models

# Reflection: spawn-fix-probe

Probe target: the uncommitted `pipeline/06_reflect/spawn.py` fix on anchor `5bcb9e7`
("pre-spawn-fix state: gates green, omp agent hang reproduced"). Working-tree state at
this run: `omp agent` (hung on interactive stdin) replaced by `omp launch -p` +
`--no-session` + bounded 1200s default timeout (rc=3 on expiry, `OMP_SPAWN_TIMEOUT`
overridable), `omp.exe` resolved from `~/.bun/bin` on Windows, W1 hard gate
(`watch.py --once` + `.graph_fingerprint` vs `GRAPH-DIGEST.md` compare -> `STALE_DIGEST`
rc=1), P7 `check_stage_contracts.py` gate before spawn. `git status` confirms `spawn.py`
is `M` (modified, uncommitted) and the two probe artifacts are untracked.

## Claim

Three open defects in the spawn path, one deeper than the last:

1. **Hang repaired, liveness not closed.** The fix repairs the *hang* (bounded timeout
   converts a dead-but-running process into a loud rc=3) and adds a *consistency* gate
   (W1 stale-digest). It does **not** add a liveness gate on the success path: line 153
   `return proc.returncode` fires when the launched process exits cleanly, with no check
   that the two required artifacts (`reflection/digests/<topic>.md`,
   `reflection/candidates/<topic>.jsonl`) exist or that the digest's first line carries
   the `fingerprint`/`plan_version`/`phase` stamp.
2. **W1 silently self-disarms.** Line 113 `fingerprint=live_fp or digest_fp`: when
   `.graph_fingerprint` is missing, `live_fp` is `""` and spawn proceeds with the digest's
   *own* fingerprint — the consistency check turns itself off without reporting it, so a
   frozen fp still emits a spawn.
3. **The P3 compaction guard re-injects a truncated source.** Line 107 caps the digest at
   12000 chars; line 110 caps `stage_hint` at 1500 chars. Measured at this run: the digest
   is 245936 chars, so `digest[:12000]` ends mid-tag-list (`pocock-writing-for-agents ...
   tags=['icm', 'context-eng`), and the 2796-char `stages/04_reflect/CONTEXT.md` is cut at
   1500 ending mid-command (`python`). The prompt's P3 guard says "re-inject:
   stages/04_reflect/CONTEXT.md Inputs Table + pipeline/WORKFLOW.md current phase header",
   but the injected `stage_hint` is itself truncated before the Inputs Table / Invoke
   block completes. On a compaction the agent re-injects a corrupted re-anchoring source.

## Evidence

- `00_measured_liveness_not_consistency` — the exact measured shape: "For every maintained
  thing, there must be a gate that asks whether it is alive, not only whether it is
  internally consistent." Its defect #4 ("gate written but never wired") and the
  aggravator (a stale metric "still emitted a line ... the metric was frozen but nothing
  failed") map one-to-one onto (1) spawn.py's success path: rc=0 emitted while the guarded
  artifacts may be absent, and (2) the fp fallback: a spawn emitted while the live-fp
  check is frozen out.
- `00_07_critic_external_tool_verification` — verify-then-correct requires the
  correction to ride on an independent external signal. The only artifact check in
  spawn.py ("agent produced no digest") fires solely on the *failure* (timeout) branch;
  the success path trusts the process's own clean exit — intrinsic self-reporting.
- `00_06_self_correction_grounding_requirement` — a spawn that trusts a clean exit is
  self-reporting; the corpus measures that ungrounded correction degrades, not merely
  fails. Grounding the spawn in artifact existence + stamp match is the external channel.
- `00_graph_memory_starter_inventory` — loud-failure reference from the starter's
  `recall.py`: "with no seeds it returns `(no memory matches for this prompt)` — a loud
  failure, never a guess." The `live_fp or digest_fp` fallback is the inverse: a silent
  fallback to a guess.
- `00_from_plan_to_action_how_well_do_agents_follow_th` — the routing contract in the
  prompt (write exactly two outputs with provenance stamps) is a plan; nothing on the
  success path verifies the agent followed it.
- `00_icm_43_copies_four_moves` — defect (3): a lossy copy is worse than no copy. The
  P3 re-injection is a copy of the CONTEXT/digest made to survive truncation; capping it
  at 12000/1500 chars produces a copy that has lost its own Inputs Table, so the re-anchor
  step silently hands back a truncated disclosure.
- `00_is_progressive_disclosure_all_you_need_for_long` — progressive disclosure must not
  cut at the seam. Capping the digest/stage hint mid-item is disclosure truncated exactly
  where the re-injection guard needs it whole.
- `00_plain_text_as_interface` — the plain-text interface layer (digest + stage CONTEXT)
  is the communication contract between pipeline and agent; a lossy cap degrades that
  interface on every spawn, not just on compaction.
- `00_chief_of_staff_routing`, `00_hooks_board_events`, `00_pocock_grilling`,
  `00_tool_orchestration_multi_tool` — routed context-engineering/icm+reflection
  intersections confirming reflection is routed deterministically through these stage
  contracts, i.e. a broken P3 re-injection source breaks routing's own recovery path.
- `ai-planning-htn-pddl` (via ADAPT one-level split, depth=1, via=classical-planning) —
  the spawn pipeline is a staged task network (digest -> stage context -> prompt -> launch
  -> verify); stages 1-4 are wired, the terminal *verify* method is the missing leaf,
  which is precisely defect (1).

## Decision

- **Accept** the delivered hang fix: `omp launch -p` + bounded timeout + W1/P7 pre-gates
  is the correct liveness-side repair of the reproduced hang (revertible via `5bcb9e7`).
- **Reject committing `spawn.py` in its current form**: it ships a consistency gate
  without the paired liveness gate (`00_measured_liveness_not_consistency`), a silent
  fp self-disarm (`00_graph_memory_starter_inventory`), and a truncating P3
  re-injection source (`00_icm_43_copies_four_moves`).
- **Accept** three probe candidates below as the concrete close-outs before the next
  `git commit` of `spawn.py`: `spawn-post-liveness-gate`,
  `spawn-fp-fallback-silent`, `spawn-p3-reinjection-truncation`.

## Next bet

Add a post-spawn liveness gate to `spawn.py`'s success path: after rc=0, check both
`reflection/digests/<topic>.md` and `reflection/candidates/<topic>.jsonl` exist and that
the digest's first line carries `fingerprint: 5f4f9d29057b plan_version: ad0a031aa564
phase: 04_reflect`; else rc=4 `LIVENESS_FAIL` naming the missing artifact. Replace
`live_fp or digest_fp` with a hard rc=1 when `.graph_fingerprint` is absent (loud, never
guess). Raise the P3 caps so the re-injection source is whole: cap the stage hint at the
*full* `stages/04_reflect/CONTEXT.md` (2.8k, not 1.5k) and cap the digest only at a
boundary that keeps the auto-injected chunk list + the "Current phase CONTEXT" header
intact, not mid-tag-list. Bet: <60 lines total converts the success path from
self-reported to externally verified and stops the P3 guard from re-injecting a corrupted
re-anchor; the three gates each fail loud on a defect shape the corpus already measured
(`00_measured_liveness_not_consistency`, `00_graph_memory_starter_inventory`,
`00_icm_43_copies_four_moves`). Falsifiable: (a) spawn a topic whose artifacts do not yet
exist -> rc=4 names them instead of rc=0; (b) `rm .graph_fingerprint` -> rc=1 STALE_FP
instead of a silent proceed; (c) run with a topic larger than the digest cap and confirm
the injected "Current phase CONTEXT" block still contains the complete Inputs Table.
