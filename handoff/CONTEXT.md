# CONTEXT — handoff/ (root workspace)

Multi-agent handoff state for the workspace root. Contract per ICM invariant 4.

## What it reads

- `handoff/flags/<flag>.md` — one flag = one file = one writer. The flag is the
  claim; ownership belongs to the flag, not to the agent, so retiring a flag you
  did not create is still a legal single-file write.
- `handoff/status/` — human-facing view (CONTEXT.md + generated STATUS.md + manual NEXT/PLAN/GOALS/HISTORY). Ignored by build_handoff.py; own contract above.

## What it writes

- `HANDOFF.md` (root) — **generated, never hand-edited**. `scripts/build_handoff.py`
  owns the template; the builder is the only writer of that file.

## Flag file schema

```markdown
---
flag: <machine-unique-id>      # matches the filename stem
since: YYYY-MM-DD
owner: <agent allowed to edit> # who may retire this claim
agent: <writer>
model: <provider/model-id>     # real id from the session, never a nickname
origin: <where the claim came from>
---

`flag` — YYYY-MM-DD: state + next step. One entry, one paragraph block.
```

`owner` means **role** here — the agent allowed to edit this file — and nothing
else. The same word names a script path in a *retention contract*, where "who
owns this check" is answered with a file. Reading a flag's `owner: opencode` as
"a tool owns this" is the misreading that produced a reviewer "fixing" a flag
that was correct.

## Process

Preferred: one transaction via `scripts/close.py` (flag → views → gate →
commit, or no commit at all):

```
python.exe scripts/close.py --flag <id> --model <provider/model-id> --body-file <path>
```

`--body-file` beats `--body` (Windows quoting scars). Extra worktree paths
go via `--include`; any other dirty tracked file fails the run instead of
being swept in silently. Manual fallback below; the pre-commit hook
rebuilds + stages all three generated views (`HANDOFF.md`, `STATE.md`,
`handoff/flags/INDEX.md`) anyway, so a forgotten rebuild can no longer
ship a stale view.

1. Claim a flag: create `handoff/flags/<flag>.md` with the schema above.
2. Retire a flag: edit **your own** file, or delete it when the claim stopped
   holding. State, not a journal — never append history to a live claim.
3. Move prose that no longer belongs at root to `handoff/deep/<topic>.md` and
   link it from the flag.
4. Rebuild the shared read surface:

   ```
   python scripts/build_handoff.py           # regenerate HANDOFF.md
   python scripts/build_handoff.py --check   # gate form: exit 1 if stale
   ```

5. Gate before done: `python scripts/check_workspace_integrity.py`.

## Human check

A human reads `HANDOFF.md` and decides two things: is the state true, and is the
flag that claims a human decision still open? The builder never decides
`owner`/`agent` for you — a wrong owner hides who must act.

## Anti-patterns

- Editing `HANDOFF.md` by hand (it is a view; the edit is lost on the next build).
- Editing a flag whose `owner` is someone else to "fix" it — open a new flag or
  coordinate instead.
- A second handoff system next to this one. One home per fact; `HANDOFF.md`
  inlines what `flags/` and `deep/` hold, so a copied narrative would drift.
- Real-time concurrent merging of the same file. That is where ICM loses and
  framework code wins; the flag-per-file split is the deliberate boundary.

## Triggers

Zmiana w `scripts/**`, `hooks/**`, `skills/**`, `check_workspace_integrity.py`, `audit_*.py`
wymaga odczytu `SCARS.md` przed edycją.

Adnotacja: ten trigger jest **konwencją, nie mechanizmem** — precedens:
`scripts/memory/CONTEXT.md` (`AGENTS.md:33`, "trigger is a convention nothing invokes").
Hook enforcement: TODO.

Sesja, która staje przed pytaniem strategicznym (debug/decyzja nierozstrzygalna
lokalnie), najpierw wypycha stan (`python.exe scripts/notebook_push.py --auto
--sessions 5`), potem pyta (`nlm query notebook a49ff8cb-31e0-470e-b747-3f2a0ded1699
'<pytanie>'`). Kontrakt całości: `scripts/notebook/CONTEXT.md`.
