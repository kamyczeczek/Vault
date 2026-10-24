---
flag: tooling_scars_hardened
since: 2026-10-02
owner: unassigned
agent: unknown
model: unknown
origin: migrated 2026-10-03 from HANDOFF.md §Status
---
`tooling_scars_hardened` — 2026-10-02: post-mortem of the ingest/graph chore
(pure execution-layer friction, state verdicts were correct) turned the
recurring scars into executable form: `scripts/_scratch/run_and_rc.sh`
(captures a command's real exit code and trims output — the
`cmd | tail; echo $?` pattern reports the pipe's rc and always prints 0) and
a new "Executable scars" rule block in `AGENTS.md` § Rules (rc capture, edit
anchors copied only from `read` output, `--help` before first call of an
unknown CLI). Next step: nothing — these are standing rules; sessions just
follow them.
