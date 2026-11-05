---
type: Concept
title: 2026-09-15_manifest-gate-verified-reconstruction
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# Reflection — manifest gate verified a self-reconstruction, not the artifact

Date: 2026-09-15
Project: projects/workspace-research
Trigger: T1 (a problem was hit and fixed), T2 (a rule was added), T3 (a gate was retro-fitted)

## Problem

`scripts/check_manifest.py` was added as the phase-1/2 exit gate, but in verify mode it
never read `knowledge/raw/manifest.jsonl` — `MANIFEST` was opened **only for writing**
(line 179, `--write`). The gate reconstructed rows from corpus `source:` frontmatter and
compared them against nothing, so any on-disk manifest — stale, incomplete, or fabricated
— always "passed". This is exactly the unenforced-contract failure R1 of the prior
record, in a second place.

The committed manifest was in fact corrupt: 5 of its 18 rows named raw files that do not
exist on disk or in git (`skills.txt` → 235 chunks, `chief-of-staff-crew.txt` → 13,
`ai-planning-classical.md`, `ai-planning-htn-pddl.md`, `planning-with-files-pattern.md`
→ 1 each). 240 of 596 chunks were attributed to phantom provenance. Separately, 3 chunks
declared composite prose sources (`ai_planning.txt (Aiello & Georgievski, …) + arXiv …`)
that matched no raw basename, so the pre-existing derivation reported
`missing_from_manifest: 3` while `orphan_in_manifest` stayed 0.

Two secondary defects in the same script:
- `--write` crashed with `NameError: name 'json' is not defined` **after** truncating
  `manifest.jsonl.tmp`, leaving a 0-byte tmp behind and no manifest update.
- `raw_basenames()` included `manifest.jsonl.tmp`, so the leftover tmp became an
  "unmapped raw file" in the next report.

## Root cause

The gate was written to derive the answer and then verify the derivation, not the
artifact. A gate that regenerates its subject cannot detect that the subject is wrong —
it can only detect that the corpus is wrong. The manifest was treated as an output of
the script rather than as the phase-1 handoff artifact that the phase-2 consumer trusts.

The phantom rows were the residue of an earlier manifest format that keyed rows by
synthesized slug names; when the corpus later moved to full-filename `source:` fields,
the old rows were never invalidated. Nothing noticed because nothing looked.

## Solution

Attribution: the derived reverse-index rebuild and the W5/W6 candidate closure were
delivered earlier in the session (`51123bf`); this record covers the gate-hardening that
followed, which found and fixed defects the first pass left in place.

1. **`load_manifest()`** — parse and validate the on-disk rows (each needs
   `raw`/`sha256`/`corpus_ids`); absent or unparseable ⇒ `FAIL` with a reason. Verify mode
   can no longer pass on a missing or corrupt handoff artifact.
2. **`manifest_problems(disk, built)`** — judges the disk manifest against a freshly
   derived one: key-set equality both directions (phantom raw / untraced corpus),
   `sha256` content-drift per row, and duplicate chunk claims. Composite/web-source rows
   are intentional keys, so they are compared by key set, not by filesystem existence —
   the first attempt wrongly flagged them as phantom because it tested `os.path.isfile`
   on composite citation strings.
3. `--write` wrapped in try/finally with guaranteed tmp cleanup; `import json` restored;
   `raw_basenames()` excludes `*.tmp`.
4. Regenerated manifest from the corpus: **35 rows, 596 chunks traced, 33/33 raw files
   mapped, 0 unmapped, 0 no-source.**
5. `pipeline/WORKFLOW.md` phases 1/2 gate on `check_manifest.py` exit code; the `Invoke`
   block lists all four gates; `stages/01_inbox` + `02_corpus` contracts state the
   manifest-is-derived invariant.
6. Re-stamped 14 reflection outputs to `plan_version 0a95cca836e2` (WORKFLOW.md changed,
   so the old stamps were legitimately stale — the P5 gate correctly failed).
7. `spawn.py` — omp binary resolution corrected to the user `~/.bun/bin/omp.exe`
   (the hardcoded repo-relative path did not exist; it silently fell back to PATH);
   `AGENT_TIMEOUT` raised 300→900s and made configurable (`--timeout`,
   `OMP_SPAWN_TIMEOUT`) after 300s cut an audit pass mid-flight.

## Verification

Negative controls, both directions:
- Corrupt/stale manifest (18 rows, phantom keys, placeholder chunk ids) ⇒ `verdict: FAIL`
  with per-chunk `untraced corpus (manifest has no row)` diagnostics.
- Regenerated manifest ⇒ `verdict: PASS`, `staleness: []`.

Full gate suite green post-commit:
- `check_manifest.py` → PASS (exit 0)
- `watch.py --once` → `[watch] no change — graph fresh`
- `check_reflection.py` → `OK: checked 7 digests / 7 candidate files — all grounded.`

## Prevention rules

- **R1 — a gate must read the artifact it gates.** Never verify a reconstruction of the
  subject; derive the expected state, then compare it against the actual on-disk state.
  A regenerate-then-trust gate is a no-op gate.
- **R2 — composite sources are data, not corruption.** When a reverse index can carry
  non-filename keys (web/composite citations), judge correctness by key-set equality
  against the derivation, not by `os.path.exists`. Testing the wrong property produced
  false positives on the very rows the design intends.
- **R3 — a write-path crash after truncation is data loss.** Any temp-file write must be
  wrapped so a failure between truncate and replace cannot leave a partial artifact or a
  stray tmp that the next run misreads as an input.
- **R4 — changing the plan invalidates every stamp of the plan.** Editing `WORKFLOW.md`
  moves `plan_version`; all stamped reflection outputs must be re-stamped in the same
  change or the P5 gate fails by design. That failure is the gate working, not a bug.
- **R5 — never spawn a concurrent agent into the working tree you are editing.** The
  live audit spawn shares the cwd and holds write access, so running it mid-edit produced
  a write/write race: concurrent commits to the same files, gate results flipping between
  runs (`plan_version` failures appearing and vanishing), and functions materializing in a
  script this record's author did not write. It produced good work and a dangerous race at
  the same time. Serialize — finish edits and commit first, or spawn into an isolated
  worktree — and cancel the spawn before resuming edits.
