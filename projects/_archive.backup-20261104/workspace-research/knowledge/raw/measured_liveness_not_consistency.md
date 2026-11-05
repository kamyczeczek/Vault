---
type: Concept
title: measured_liveness_not_consistency
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

# Measured Lesson — Consistency Gates Pass While the Thing They Guard Is Dead (root audit 2026-09-16)

## What was measured

A workspace gate suite reported **13/13 green** while **four real defects persisted
simultaneously**. This was measured directly, not inferred.

The four defects, each verified live:

| # | Defect | Evidence |
|---|---|---|
| 1 | Failure ledger blind for 9 days — 56 commits, **zero** failure capture | ledger last entry 2026-09-07 |
| 2 | Brain router self-test exits 1, run by **nothing** | `ask.py --self-test` rc=1 |
| 3 | graph_brain fully built and gate-synced but **unreachable** by any query | absent from routing table |
| 4 | ts_brain sync gate written but **never wired** | 0 references in `run_gates.py` |

The suite passed because every one of its gates verified **internal consistency** — catalogs
match disk, invariants hold, inboxes empty. **None verified liveness.**

## Why this is the dangerous failure shape

Consistency checks have a blind spot by construction: they verify that a thing is *self-
consistent*, which is orthogonal to whether it *works*. A catalog that matches a stale corpus is
self-consistent. A router that misroutes every query is self-consistent. A gate that runs a
brain nobody can reach is self-consistent.

Defect 1 had an extra aggravation that made it invisible rather than merely undetected: the
epidemiology probe **still ran and still emitted a line**, reporting "4d" of data on
2026-09-16. **The metric was frozen but nothing failed.** A stale check producing output is
worse than a dead check producing no output, because the output is what a reader trusts.

## The repair, and what actually worked

The two defects that were fixed by *adding a gate class* rather than patching symptoms:

1. **`brain_router_liveness`** — runs the router's own self-test as a subprocess. The self-test
   already existed and already failed for an unknown period. It was simply ungated. Wiring it
   converted silent decay into a commit block.
2. **`failure_ledger_freshness`** — the epidemiology probe now warns when the ledger's last
   capture is ≥ 3 days old, so a frozen metric can no longer print as current.

Two secondary discoveries during the repair:

- **A warning at rc=0 was being swallowed.** The gate runner only printed a gate's output on
  failure, so the new freshness warning printed "ok" and hid itself. A *passing gate with a
  warning* read as healthy — the same silent-decay failure the fix was for. The runner now
  surfaces rc=0 gates that warned on stderr.
- **A correct script looked broken.** An earlier reading recorded `verify_sync` as returning 0
  while reporting STALE. That was `tail`'s exit code, not the script's. On a pipeline, `rc` is
  the last command's code, not the first.

## The transferable rule

**For every maintained thing, there must be a gate that asks whether it is alive, not only
whether it is internally consistent.** Concretely:

- Ask the *consumer's* question, not the *maintainer's*. "Is the corpus consistent with the
  manifest?" is the maintainer's question. "Does a query return the right brain?" is the
  consumer's. The defects lived precisely in the gap.
- **Gate the liveness of checks themselves.** A check that emits output on a schedule is not a
  check; it is a printer. Freshness must be part of the contract, or staleness reads as data.
- **Surface warnings from passing gates.** If rc=0 hides stderr, then "warn but continue" is
  indistinguishable from "healthy", and no one ever investigates.
- **Verify exit codes through pipes.** Otherwise a correct script appears broken or a broken
  one appears correct.

The meta-finding: the strategies were sound. The workspace had strong mechanism-class gates and
a verified reflection loop (121 reflections, 88% naming a mechanism). The gap was a *class*
missing — no gate asked "does the thing work?" — and a missing class is invisible to a suite
that only checks what it already knows about.

## Provenance

- Audit: `AUDIT-2026-09-16.md` (read-only whole-workspace assessment, all numbers computed live)
- Fix commit: `789d716` (all four defects + the two liveness gates)
- Gates: `PROCESS/run_gates.py`, `PROCESS/check_brain_router.py`
- Freshness probe: `.jcode/hooks/epidemiology.py`
- Recomputed live for this chunk: 13/13 gates pass; preflight suite 31 pass / 0 fail /
  14 red-path blocks; ledger stale 9 days.
