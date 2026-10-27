---
type: Concept
title: GATES-research-graph-reflection-execution
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# Map: research ↔ knowledge-graph ↔ reflection ↔ execution

OWNS: docs/wayfinder/research-graph-reflection-execution.md, GATES-research-graph-reflection-execution.md

## Destination

See [`docs/wayfinder/research-graph-reflection-execution.md`](docs/wayfinder/research-graph-reflection-execution.md)
§ Destination. One canonical phase-04 runner, a measured (or explicitly bounded-as-unmeasurable)
execution seam, one gate per layer seam that can fail on the seam, and a passing cold walk test.

**This ledger covers the charting pass only.** It does not gate the implementation —
the implementation's gates are ticket T3's output, and writing them before T1/T2
close would encode unchosen semantics into an oracle.

## Notes

Each gate below is the charting pass's own completion criterion. `CHECK:` treats
are one observable outcome each. Frontier tickets in the map file are wayfinder
decision tickets and are deliberately *not* duplicated here — the map is the
index, and two copies drift (icm-architect: duplicated entry files that drift).

## Gates

- [ ] G1: Exactly one `## Destination` — two means a cold agent cannot tell which plan it follows
  CHECK: python scripts/check_wayfinder_map.py docs/wayfinder/research-graph-reflection-execution.md --gate G1
  EXPECT: G1_OK

- [ ] G2: Every frontier ticket is a question, not a build step
  CHECK: python scripts/check_wayfinder_map.py docs/wayfinder/research-graph-reflection-execution.md --gate G2
  EXPECT: 5 tickets, all question-shaped

- [ ] G3: All six sections present; no live ticket restated as a decision
  CHECK: python scripts/check_wayfinder_map.py docs/wayfinder/research-graph-reflection-execution.md --gate G3
  EXPECT: G3_OK

- [ ] G4: Every relative link in the map resolves on disk
  CHECK: python scripts/check_wayfinder_map.py docs/wayfinder/research-graph-reflection-execution.md --gate G4
  EXPECT: relative link(s) resolve

- [ ] G5: `Out of scope` records excluded work rather than dropping it
  CHECK: python scripts/check_wayfinder_map.py docs/wayfinder/research-graph-reflection-execution.md --gate G5
  EXPECT: 5 out-of-scope entries recorded

- [ ] G6: The map declares its own status — `PROPOSED`, or `CONFIRMED` with an ISO date
  CHECK: python scripts/check_wayfinder_map.py docs/wayfinder/research-graph-reflection-execution.md --gate G6
  EXPECT: map is confirmed (2026-10-01) — destination accepted by a human

- [ ] G7: The gate above can actually fail — every mutation is detected
  CHECK: python scripts/_scratch/negative_control_wayfinder_map.py
  EXPECT: NEGATIVE_CONTROL_OK: 8/8 mutations detected

## Confirmation record

`CONFIRMED 2026-10-01` — destination accepted by a human, option A
(canonical seam + measured execution + seam gates).

Confirmation settled **what** the map is for. It settled **no ticket**: all five
are open, and T1 is the frontier. `wayfinder` puts the human at the boundary
between charting and resolving, so a confirmed destination authorises T1 to
start and nothing else.

G6 was rewritten at that moment, and the rewrite is the interesting part. It had
required the words `PROPOSED` or `provisional`, which encoded *charting
precedes confirmation* as *this text is permanent* — so a correctly-updated map
failed a gate that had been written for the previous state. The gate now accepts
either state and requires a date on a confirmation, because an undated
`CONFIRMED` is indistinguishable from a proposal nobody read.

Widening a gate without extending its negative control is how a gate starts
asserting things it never tests, so two mutations were added at the same time:
`status-absent` and `undated-confirmation`. The first of the pair immediately
reported `MUTATION-NOOP` — the old mutation was pinned to the text
`PROPOSED`, which no longer exists in a confirmed map, so it had stopped
testing anything without anyone noticing. 7/7 before the confirmation, 8/8
after.

## Abandonment protocol

ABANDON: <id> <non-empty reason> — handoff recorded in CONTEXT.md or issue tracker

## Verification record

`python scripts/check_wayfinder_map.py <map>` — all six gates green.
`python scripts/_scratch/negative_control_wayfinder_map.py` — 8/8 mutations
detected.

The negative control earned its place immediately: of its first seven mutations,
two passed a gate that looked green. G2 asserted "every ticket is a question"
while matching a line shape the map never used, and G3 searched for a bare
`- T1` bullet while Decisions entries are written `- **[T1 — title]**`. Both were
the C-7 shape this project has already paid for twice — a gate asserting a
property its code did not implement — caught before the gate was trusted rather
than after. Neither was found by reading the validator; both were found by
watching a mutated map go green.

It then earned its place a second time at the confirmation boundary, where a
third gate went stale and a fourth mutation quietly stopped testing anything.

## Known limits of these gates

- **G2 checks shape, not intent.** A ticket could phrase a build step as a
  question ("should we implement the reflect runner?") and pass. Intent is
  reviewed by a human at the confirmation boundary. If T3 lands, its successor
  should gate ticket *content*, not ticket count.
- **G4 resolves links that exist, not links that are correct.** A link to the
  right file carrying the wrong claim still passes.
- **The control lives in `scripts/_scratch/`**, which is gitignored, so it does
  not travel with the gate. It is a development instrument, not a shipped gate.
  Promoting it to `tests/` is T3's work if the gate is promoted.
- **G6 checks for two statuses, not truth.** A map can claim `CONFIRMED` and
  name a date without any human having agreed. The gate can verify the marker is
  well-formed; it cannot verify the decision happened. That boundary is
  deliberate — the alternative is a gate that claims to know what a human
  decided, which is the C-7 shape again.