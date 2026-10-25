---
type: Concept
flag: session-brief-valuable-2026-10-23
since: 2026-10-23
owner: opencode
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: user request for scripts/session_brief.py --last N --valuable
title: session-brief-valuable-2026-10-23
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`session-brief-valuable-2026-10-23` — 2026-10-23: **`session_brief.py` built;
committed in `e98237a`.** The tool reads the N latest main sessions, reuses the L1 cards
from `session_digest.py` for selection (commits, files, flags, tests, micro) and
the `did` event stream from `extract_did.py` for content, then writes a compact
per-session brief. No model call and no free-form summary: every line is a
mechanical fact, a quote, or a truncated tool excerpt.

Selection with `--valuable` drops durably excluded meta-sessions, micro sessions
with no delta, and sessions with no mutating event and no commit/flag/test
signal. Read-only `bash`/PowerShell noise is dropped, including `--help`,
`--version`, null redirects, temp-path writes, and fixture-like flag ids.
Quoted spans are stripped before the mutation test, so a `>` or `rm` inside a
pattern does not make `grep`/`Select-String` look mutating, and `rm`/`mv`/`cp`
only match as commands, not inside ids like `git-rm`. `skill` calls are not
actions. Session `flags` are split into present and `absent now` (the latter
replaces the old `flags missing` line, which read like loss instead of
retirement).

Evidence:
- `scripts/session_brief.py` — `--last N`, `--valuable`, `--agent`, `--days`,
  `--until`, `-o/--out`, `--session-kb` (8), `--total-kb` (120),
  `--max-actions` (8). Default output:
  `scripts/_scratch/sessions/02_products/session_brief.md`.
- `scripts/session_brief.bat` — wrapper: `session_brief.bat N [OUT]`.
- `scripts/test_session_brief.py` — stdlib-only helper tests; `OK session_brief`.
- Sample run: `--last 20 --valuable --until "2026-10-23 05:00:00"` selected
  18/20 (skipped 1 meta, 1 micro), 70,001 bytes; `--last 10 --valuable` selected
  8/10, 27,722 bytes. The `--until` keeps the in-flight session out of the
  sample; without it the running session becomes #1 and its "Ending" is just the
  latest reply, not an ending.
- `scripts/_scratch/sessions/CLAUDE.md` and `02_products/CONTEXT.md` — product
  routing rows (derived shelf docs).

not checked: the selector is heuristic — a session whose only mutating calls are
`python -c` probes or temp-dir experiments can still pass; `2>/dev/null` counts
as an attempted redirect (on PowerShell it really does try to write
`C:\dev\null`); `--last N` filters inside the N-session window instead of
backfilling to N valuable sessions; the sample was inspected by eye, not graded
against a gold set; nothing yet uses it on a real analytical question, so it is
a tool, not a product. The tool, its `.bat`, and its test landed in `e98237a`.

Related: `handoff/flags/memory-meta-session-exclusion-durable-2026-10-23.md`
(durable meta-session exclusion used by the selector).
