---
flag: close-py-correct-flag-landed-2026-10-18
since: 2026-10-18
owner: mateusz
agent: opencode
model: opencode/beam-free
origin: session-close
---

`close-py-correct-flag-landed-2026-10-18` — 2026-10-18: implemented `close.py --correct <flag>` (edit-in-place + rebuild views + gate + commit, same transaction guarantees) as the S86 mitigation; manual `.commit-approved` minting + `git commit` is no longer needed to correct a committed flag.
not checked: --correct tested via --dry-run only (no full end-to-end overwrite of an existing flag); end-to-end close with git-rm'd --include still untested.
