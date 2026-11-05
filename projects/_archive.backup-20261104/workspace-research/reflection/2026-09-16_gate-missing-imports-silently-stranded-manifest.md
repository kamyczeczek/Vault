---
type: Concept
title: 2026-09-16_gate-missing-imports-silently-stranded-manifest
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# Reflection — phase-1/2 gate crashed on every ingest since new call sites were added

Date: 2026-09-16
Project: projects/workspace-research
Trigger: T1 (a bug in a rule I had just invoked)

## Problem

`python scripts/ingest.py` completed its corpus work, then crashed while rebuilding the
manifest — the phase-1/2 exit gate. The crash left the on-disk manifest 9 sources behind
the corpus: **36 rows vs 45**, with all 5 hand-written paper chunks and all 4 new findings
untraced. Worse, `ingest.py` exited **0** because the crash happened inside the
`check_manifest.rebuild_after_ingest()` call rather than in `main()`, so a failing gate
reported success.

## Root cause

Three stdlib modules were used in `scripts/check_manifest.py` without being imported:

```
line 53   corpus_index()    glob.glob(...)        -> NameError: glob
line 152   build_rows()      collections.defaultdict -> NameError: collections
line 188   rebuild_after_ingest()  file=sys.stderr -> NameError: sys
```

The call sites were added across separate edits, each using a module the original import
block did not cover. Each failure mode was masked differently:
- `sys` was only reached when `main()` returned non-zero — i.e. only when the manifest was
  *already broken*, so the warning path itself crashed on exactly the condition it existed
  to report.
- `glob` and `collections` are hit on every run, so `rebuild_after_ingest()` had been
  crashing on **every** ingest since they were introduced, silently stranding the manifest.

## Solution

Added all three imports to the existing block (now `argparse, collections, glob, hashlib,
json, os, re, sys`). Then:

```
python scripts/ingest.py                    # 8 new chunks (4 findings x 2 parts)
python scripts/check_manifest.py --write    # regenerated 45 rows / 610 ids
python scripts/check_manifest.py --json     # verdict: PASS (610/610 covered, 0 no-source)
python knowledge/graph/build_graph.py       # fingerprint 7038862ef74e, 610 nodes
python knowledge/graph/watch.py --once      # no change — graph fresh
python scripts/check_reflection.py          # OK: 9 digests / 9 candidate files
```

## Verification

All four pipeline gates exit 0: stage contracts, manifest, graph, reflection. Manifest went
36 -> 45 rows and 596 -> 610 traced ids with `chunks_without_source_field: 0`. INBOX is
empty. Confirmed by exhaustive scan that the module references in the file are now exactly
the imported set — no fourth latent `NameError` remains.

## Prevention rules

- **R1 — a gate that crashes exits non-zero, or it is not a gate.** `ingest.py` swallowed
  the failure because the crash was nested one level below `main()`. Any gate invoked from
  another script must propagate its real status; a crash inside a helper reported as
  success is worse than no gate, because it makes drift invisible.
- **R2 — error paths are code, and they get tested last.** The `sys.stderr` line was
  dead-until-broken: reachable only on the failure it was written to announce. Any branch
  that exists solely to handle a bad state needs to be exercised in that state at least
  once, or it will be the thing that fails when the state arrives.
- **R3 — when a gate fails on a missing import, scan for all of them.** The first crash
  revealed `sys`; fixing only that would have surfaced `glob` on the next run and
  `collections` on the third. Enumerate every `module.` reference and diff against the
  import block in one pass instead of iterating through three round trips.
- **R4 — derived artifacts must be verifiable independent of the write path.** The manifest
  had been drifting across runs precisely because its only writer was the code that
  crashed. A rebuild that can be run standalone (`--write`) is what made the recovery a
  single command.
