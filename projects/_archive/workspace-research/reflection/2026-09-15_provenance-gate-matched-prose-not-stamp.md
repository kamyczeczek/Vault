---
type: Concept
title: 2026-09-15_provenance-gate-matched-prose-not-stamp
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# Reflection — provenance gate matched claim prose instead of the stamp

Date: 2026-09-15
Project: projects/workspace-research
Trigger: T1 (a bug in a rule I had just written)

## Problem

The P5 gate I added this session failed a candidate file whose provenance was actually
correct: `workspace-organization-audit.jsonl` reported
`fingerprint 0626262b2982 != live corpus a77f6925b6c7` even though every row carried a
valid `provenance` object with the live hash.

## Root cause

`provenance_ok()` scanned raw file text with a regex and returned the **first**
`fingerprint` token. In a candidate JSONL row, that first match is a quoted hash inside
claim prose, not the stamp:

```json
{"claim":"...cites fingerprint 35b86bc954fa in its Determinism clause...",
 "provenance":{"fingerprint":"a77f6925b6c7", ...}}
```

So the gate compared historical prose against the live corpus and could never pass. The
bug was invisible on all 7 original files because none of their claims quoted a hash —
it only surfaced once an audit row cited a stale fingerprint as evidence.

Compounding it, a **concurrent agent was writing to this workspace while I worked**:
three corpus chunks changed ~61s before my check, `build_graph.py` 12s before, and
`WORKFLOW.md` had advanced to a commit I did not make (`f1f31b2`). My stamps went stale
mid-session because the corpus and plan moved underneath them.

## Solution

Split the validators by surface:
- digests (markdown) keep `provenance_ok` — raw-text scan is correct for prose;
- candidates (jsonl) use new `provenance_ok_jsonl`, which parses each row and reads the
  nested `provenance` object.

Re-stamped all outputs to the live values (corpus `a77f6925b6c7`, plan `a2d5b26552ee`)
after the graph rebuild picked up the new chunks.

## Verification

- Gate: `OK: checked 8 digests / 8 candidate files — all grounded.`
- Negative controls on the new validator, all correct:
  - prose stale-hash + valid object → **pass** (prose is evidence, not a stamp)
  - valid prose + stale object → **fail** `fingerprint 35b86bc954fa != live corpus …`
  - no provenance object → **fail** `missing provenance.fingerprint`
- Manifest gate 35 rows / 596 chunks; stage-contract gate reports no hardcoded moving
  values; INBOX empty.

## Prevention rules

- **R1 — validate the artifact, not the text.** When a file is structured (JSON/JSONL),
  parse it and read the field. A raw-text scan of structured data can match a value that
  appears as *content* and silently validate against the wrong thing.
- **R2 — a new check is unproven until it fails correctly.** This gate passed on 7 files
  and was still wrong; it took a row that quoted a stale hash to expose it. Always run the
  negative control that the check was built to catch.
- **R3 — re-derive moving values at gate time.** Fingerprint and plan version change on
  every corpus/plan edit, and can change mid-session when another writer is active. Read
  them live; never cache between the read and the check.
