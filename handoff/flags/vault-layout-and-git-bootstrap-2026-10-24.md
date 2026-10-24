---
flag: vault-layout-and-git-bootstrap-2026-10-24
since: 2026-10-24
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
---

`vault-layout-and-git-bootstrap-2026-10-24` — 2026-10-24: root workspace re-bootstrapped after the vault move. `.projects/` renamed back to `projects/` (CLAUDE.md, AGENTS.md and all 20 routing links already said `projects/`; no file referenced the dot form), gate went from 25 problems to 3. `git init` plus `core.hooksPath hooks` restore the pre-commit gate; this is the new baseline commit. Memory index re-ingested (lag 1d13h) and `brain.db` rebuilt (R21: 18 sourceless rows cleared). Gate green: 38 declared entries, 7 projects, all routes resolve, retrieval 15/15. Next: decide the single Obsidian vault root, then fix `session_ground_truth.py` at its real path.

History is unrecoverable, verified three ways: `.git/` was an empty hidden
directory (0 files, emptied 2026-10-24 17:18–17:41), none of the 6 candidate GitHub
repos holds this tree (`obsidian-vault` is notes only, last push 2026-10-23), and
`Desktop\ARCHIVE\ROOT` is a different, older workspace (last write 2026-09-17).

not checked:
- whether `.obsidian/`, `.smart-env/` and `Notes/` belong to this folder at all:
  a second Obsidian vault appeared one level up (`Desktop\vault`) at 16:39 today,
  after this folder was opened as a vault at 15:54. Those three were deliberately
  left UNTRACKED. Decide the single vault root before committing them.
- `handoff/state_description/` (32 MB of txt dumps from the one-off
  `scripts/oneoff/move_state_description.py` bridge) is now gitignored, not purged.
- this commit is a new baseline, not a continuation of the lost history; nothing
  before it can be recovered from this machine.
- `scripts/_scratch/sessions/session_ground_truth.py` does not exist; the file the
  prior plan named is at `scripts/_scratch/sessions/01_tools/session_ground_truth.py`
  and its 4 defects are still unverified.
- bootstrap exception, named rather than hidden: `close.py --include` accepts
  individual files, not directories, and the baseline is 686 files (≈40 KB of
  argv, over the Windows limit). So the commit was authorized the documented
  outside-close way — an explicitly minted `.commit-approved` (guard docstring
  sanctions it) — and `git commit -F` carried this exact subject and body.
  `hooks/pre-commit` still ran the full gate and every guard unchanged.
