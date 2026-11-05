---
type: Concept
title: 2026-09-15_windows-file-lock-blocks-graph-rebuild
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# Reflection — Windows file lock blocks graph.db rebuild

Date: 2026-09-15
Project: projects/workspace-research
Trigger: T1 (a problem was hit and worked around)

## Problem

`build_graph.py` did `DB.unlink()` before recreating `knowledge/graph/graph.db`.
On this Windows host the delete fails:

```
PermissionError: [WinError 32] The process cannot access the file because it is
being used by another process: '...graph.db'
```

The lock survived: killing every workspace-research python/bun/omp process, killing
the stale `_audit_workspace.prompt` agent (bun 15808 / omp 26540, started 18:59 and
orphaned by an earlier turn), and waiting 15 retries x 0.5s. A fresh, independent
process still got WinError 32. `os.replace` and `os.rename` were also denied.
CreateFileW with `FILE_SHARE_READ` only returns ERROR_SHARING_VIOLATION, while
`FILE_SHARE_READ|WRITE` succeeds — so the holder allows read+write sharing but blocks
delete, which is kernel-level (oplock or filter driver), not an ordinary open handle.
`NtQuerySystemInformation(SystemHandleInformation)` over all 445 processes resolved
zero file handles to `graph.db`, confirming the holder is not a user-space handle.
A sibling file created seconds earlier deletes fine, so the lock is specific to
`graph.db` (opened and held by a kernel driver), not the directory.

## Root cause

The design assumed the derived index can be replaced by deleting it. On Windows,
delete-on-open is a sharing violation, and a held handle — from a live reader, a
spawned agent, or the Search/Defender filter driver — makes the whole rebuild fail.
This is a latent design fault, not an environmental accident: any reader (including
`watch.py`'s own callers and the auto-injected agent digest) can trip it.

## Solution

`build_graph.py` no longer deletes the live DB:

1. Rebuild into `graph.db.new`.
2. `os.replace(tmp, DB)` — atomic on Windows, needs no delete permission on the
   destination. Retries 10x0.5s on PermissionError.
3. If replace is still denied (kernel hold), fall back to an **in-place rebuild**:
   `DELETE FROM nodes/edges/fts` on the live DB, then re-insert all rows. No file
   deletion or rename is attempted, so the lock is irrelevant.

`watch.py` now wraps `mod.build()` in try/except and returns exit code 2 with
`[watch] REBUILD FAILED: ...` on stderr, so `spawn.py`'s existing non-zero-return
check refuses to spawn on a broken graph instead of silently proceeding.

Verified: with the lock still active, `watch.py --once` rebuilt successfully and
printed `[build] live DB locked open — rebuilt in place`; fingerprint `0626262b2982`
matches the corpus hash, tags carry the new `progressive-disclosure` value, and
`check_reflection.py` reports all digests grounded.

## Prevention rules

- **R1 — never delete a derived index file that may be open.** Write-build-to-temp +
  atomic `os.replace`, with an in-place row-level rebuild as the fallback. Applies to
  every derived SQLite/JSON index in the workspace, not just this one.
- **R2 — a rebuild failure is a hard gate, never a warning.** `watch.py` returns 2 and
  `spawn.py` refuses to spawn; the broken state cannot propagate into a digest.
- **R3 — do not hunt the lock holder.** Kernel oplocks/filter drivers are invisible to
  user-space enumeration and are not worth admin escalation. Make the writer
  lock-tolerant instead.
