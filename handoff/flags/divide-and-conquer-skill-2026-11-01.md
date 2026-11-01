---
flag: divide-and-conquer-skill-2026-11-01
since: 2026-11-01
owner: mateusz
agent: opencode
model: nara/step-5-preview
origin: session-close
---

`divide-and-conquer-skill-2026-11-01` — 2026-11-01: The Divide-and-Conquer skill
exists and is routable from every discovery surface. It splits a task into 2+
workstreams with disjoint file sets, each run by its own sub-agent in its own git
worktree on its own branch (`../Vault-wt/<flag>-<slug>`, `dnc/<flag>/<slug>`),
merged only after the user confirms. §0 is a hard gate: disjoint files, per-piece
verification, and an explicit do-not-use list (compute runs, ledgers, handoff
flags, generated views, scripts/hooks/skills edits, dependent pieces).

Wiring: row in `skills/SKILLS.md` (catalog gate R11), line in `skills/INDEX.md`
and in the injected `~/.config/opencode/workspace-skills.md` (kept byte-identical,
verified with `fc`), and a frontmatter description carrying both positive
("Use when") and negative ("Do NOT use") triggers, with no
`disable-model-invocation` flag, so the harness auto-discovers it. The harness
skill list picked the new skill up immediately after the folder was created.

Gate evidence (unlazy ledger G1–G8, all met, raw output in the session
transcript): `verify_catalog.py` exit 0 (32 catalog rows, 32 on-disk folders);
findstr confirmed the name/title frontmatter, both trigger classes in the
description, and the forbidden-write list in the body; the negative control for
`disable-model-invocation` fired on `skills/wayfinder/SKILL.md` and did not fire
on the new skill; both index copies name the skill and match byte-for-byte;
`check_workspace_integrity.py` exit 0.

not checked: the skill has not been exercised on a real multi-workstream task —
the benchmark-core Phase 1 files sitting untracked in the working tree
(manifest.py, metrics.py, bootstrap.py, ledger.py, guards.py and their tests)
are the natural first candidate, but they are another session's uncommitted work
and were left untouched; close.py `--verify-claims` was not used because the
gates were executed directly and their raw output is in the transcript; the
`~/.config/opencode/workspace-skills.md` copy lives outside the repo and is not
git-tracked; the pre-existing "benchmark-core: MAP.md is stale" advisory comes
from that other session's uncommitted files and is theirs to clear.

Next step: once the benchmark-core Phase 1 work is committed, run this skill on
it — one parallel batch of 4 (manifest, metrics, bootstrap, ledger) plus 1
serialized (guards), with conftest.py written by the orchestrator first — and
amend the skill from what that run teaches.
