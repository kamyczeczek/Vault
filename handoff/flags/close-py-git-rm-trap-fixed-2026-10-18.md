---
type: Concept
flag: close-py-git-rm-trap-fixed-2026-10-18
since: 2026-10-18
owner: mateusz
agent: opencode
model: opencode/beam-free
origin: session-close
title: close-py-git-rm-trap-fixed-2026-10-18
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`close-py-git-rm-trap-fixed-2026-10-18` — 2026-10-18: fixed `check_includes` in scripts/close.py so a staged deletion (`git rm`) is accepted as a valid `--include` path; added hermetic test in scripts/test_close.py.
supersedes: previous close-py-git-rm-trap-fixed-2026-10-18 flag (commit 05979d9) which had `not checked: no new hermetic test`.
not checked: full end-to-end close with git-rm'd --include not re-run; SCARS.md S84b line added (optional); commit completed via git commit after close.py timeout (hook fired, SECRETS_CLEAN).
