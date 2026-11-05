---
type: Concept
title: open_questions
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Open Questions — Scar Efficacy and Typed Interfaces

<!-- Each question states what could not be resolved and WHY. -->

1. **Where can a preflight actually live in Jcode?** ~~RESOLVED
   2026-09-06 (post-record, same session): YES — the `pre_tool` GATE hook
   exists in this Jcode build.** docs/HOOKS.md: the hook runs
   synchronously before every tool call; exit 2 blocks the call with the
   hook's stderr returned to the model; anything else fails open
   (timeout default 5 s). The live `~/.jcode/config.toml` previously
   wired only `post_tool`. The D1 gate is now BUILT, WIRED, and
   live-fire validated: `.jcode/hooks/tool_preflight.py` (P1 edit
   anchor/existence/no-op checks, P2 multiline `python -c`, P3
   run-before-write, P4 bare robocopy; P5 reserved), 23/23 differential
   suite, 4 RED live blocks + 1 GREEN pass-through (ledger #400–#403,
   all dispositioned benign as near-misses). The original text of this
   question is preserved below for the audit trail.**

   > The typed-interface design (D1) assumes a pre-call interception
   > point exists. Jcode's native hooks are post_tool observers and a
   > pre-COMMIT gate (S-s18 finding: "no prompt-time context-injection
   > hook" — and the harness reference lists no pre_tool gate either).
   > If no pre-call channel exists, the preflights must be either (a)
   > tool-wrapper conventions the agent obeys (recall-shaped — weak,
   > contradicts §1), or (b) harness feature requests. ~~Unresolvable
   > from within the workspace; needs the Jcode hooks surface surveyed
   > (S1/verify task against the live harness config,
   > `~/.jcode/config.toml`).~~ (The survey was the resolution path; it
   > resolved YES.)

2. **Can the edit preflight be cheap enough?** Edit-anchor kills came
   with re-reads (~100–300 lines per retry). If the preflight re-reads
   the whole target file per edit, multi-edit sessions pay O(file) per
   edit — possibly worse than the 6.6% failure rate it fixes. Needs a
   cached file-index design (mtime-keyed) with a red-path validated
   staleness check (the pack2 pattern). Implementation research, not
   resolvable by analysis.

3. **Is the 09-06 drop in trap counts (edit 2, todo 3, python-c 0,
   schema 0) signal or censoring?** ~~Partially resolved 2026-09-06:
   the D3 probe took its first same-day measurement — post-birth
   recurrences for all five gated classes = 0 (see findings §5a).
   CONFIRMED AS SIGNAL for the gated classes, with the small-n caveat
   this question named (~29 live entries in the post-birth window,
   one session-mix). Full evaluation still needs ≥3 full days post-D1
   per the original text, which stands:~~ The day is partial (11
   entries at the record's probe time; 47 by the D3 close) — the
   standing EPI probe now measures this daily instead of one-off
   analysis, which is the resolution path. Same-day-of-week effects
   and session mix remain confounders for trend claims; the probe's
   per-day history accumulates the evidence.

4. **Baseline dispositions (135) predate the taxonomy** — do they carry
   the same class distribution as live entries? If the 09-03 retro
   harvest over-represents a class (harvest glob/segmentation evolved
   since), the historical trend line is biased. Resolvable only by
   re-classifying the baseline subset with the pass-5 taxonomy and
   comparing — deferred as a candidate validation round (S6), not
   blocking the record. *(Note 2026-09-06: epidemiology.py classifies
   the baseline too — running it per-day would answer this; the
   baseline/live divide is already at the #136 boundary it needs.)

5. **Does scar-rewrite (D2's third rule) violate the audit-safety
   constraint?** Prior open Q1 established merging must stay
   byte-faithful to enforced invariants. REWRITE-as-mechanism-requirement
   changes the invariant's form, which changes what future sessions see
   WITHOUT changing the source reflections (the index is derived —
   S-s13). Same question, sharper edge: is an index-level rewrite
   legal when the source reflection still says the old form? Needs an
   S5 doctrine decision with the source-of-truth hierarchy made
   explicit (reflection > index > digest, presumably). Routed, not
   resolved.

6. **What is the digest's true injection cost?** ~~RESOLVED 2026-09-06
   (D3 build): 1815 tokens, measured on the same basis gen_digest
   reports (tok() over the marker-block content, marker lines
   excluded) — see findings §5a. The overlay block IS the injected
   budget; D2's budget-basis is this number, tracked daily by the EPI
   line.~~ Original text preserved: 12,616 chars ≈ 3.2K tokens is the
   estimate; the overlay's scar-digest block is what is actually
   injected, and its size differs from the full digest.md. Which
   number is the budget-basis for D2? Trivial to measure (count the
   marker block) — left open because it belongs to the D1/D2
   implementation spec, not this record.
