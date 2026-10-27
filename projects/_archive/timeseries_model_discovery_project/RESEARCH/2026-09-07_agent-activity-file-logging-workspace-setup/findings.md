---
type: Concept
title: findings
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Findings — agent writing what it is doing into files, workspace setup

All claims from the 2026-09-07 Exa passes (agent-reach Exa backend).
No unsourced claims. Local-workspace notes cite repo paths.

## 1. The converged shape: contract half + state half

- The steering-coding-agents system splits the workspace into State
  ("where are we?", changes every session, rots if neglected) and
  Standing rules ("how do we work, what must never happen?", barely
  changes) — the two halves answer different questions
  (https://github.com/erikperttu/steering-coding-agents).
- The ai-workspace-template uses the same split under other names:
  `brain/` = what is true right now (telegraphic, 1 line = 1 fact),
  `docs/` = how to understand/reproduce (prose runbooks), `code/` =
  where work lives; one source of truth per fact, linked not duplicated
  (https://github.com/hess0ul/ai-workspace-template).
- Long-project failure modes this split addresses: lost working state
  between sessions, context bloat within a session, decay of the notes
  themselves (https://github.com/erikperttu/steering-coding-agents).

## 2. Always-loaded contract files (small, every session)

- Claude Code: `CLAUDE.md` files are human-written persistent
  instructions, loaded into context at the start of every session;
  project file at `./CLAUDE.md` or `./.claude/CLAUDE.md`, `/init`
  generates a starter, target under ~200 lines, discovered by walking
  up the directory tree and concatenated root-down
  (https://code.claude.com/docs/en/memory,
  https://code.claude.com/docs/en/claude-md).
- Codex: `AGENTS.md` chain built once per run — global
  (`~/.codex/AGENTS.override.md` else `AGENTS.md`), then project root
  down to cwd, at most one file per directory, concatenated root-down
  so deeper files override; empty files skipped, combined cap 32 KiB
  (`project_doc_max_bytes`), rebuilt every run/TUI session
  (https://developers.openai.com/codex/guides/agents-md).
- `AGENTS.md` is an open cross-vendor format (agents.md) used by 60k+
  open-source projects as the agent README (https://agents.md/).
- ai-workspace-template convention: thin `CLAUDE.md` router importing
  canonical `AGENTS.md`; path-scoped rules under `.claude/`; skills for
  task-specific instructions so the always-loaded file stays small
  (https://github.com/hess0ul/ai-workspace-template).
- Contract content is context, not enforcement: vague/conflicting
  instructions are followed unreliably; hard blocks need hooks
  (PreToolUse / pre_tool gates)
  (https://code.claude.com/docs/en/memory).

## 3. State files the agent itself writes (the "what I'm doing" layer)

- Bounded scratchpad pattern: one `.ai_scratchpad.md` at repo root, cap
  80 physical lines, four sections — Dead Ends (attempted+failed, do
  not re-propose), Current State & Assumptions (verified state, assumptions
  marked), Suggestions for Durable Changes (human reviews before
  promotion), Next Immediate Steps (ordered continuation); `AGENTS.md`
  tells the agent when/how to maintain it; temporary, subordinate to
  code, user instructions, and permanent docs
  (https://gist.github.com/corpulent/f7fbad0a4d9cdb6a5d4f31d249a2341c).
- Three-document handoff pattern: `CONTINUE_FROM_HERE` (forward
  worklist, present tense, the ONLY thing the next session reads first),
  `SESSION_HISTORY` (narrative, grows then rotates), `ARCHITECTURE_GAPS`
  (structured backlog ledger, table not prose); rotation done by
  `scripts/archive_rotate.py` — a script moves old entries verbatim,
  never the agent rewriting, so detail is never lost
  (https://github.com/erikperttu/steering-coding-agents).
- ai-workspace-template post-action protocol: after every change,
  note → index → area log → worksite `state.md`; close-session via a
  `handoff-update` skill/Stop hook so it is routine not ritual; success
  test — a zero-context agent given the files states where things stand
  and what to do next from `state.md` + journal + logs alone
  (https://github.com/hess0ul/ai-workspace-template,
  https://github.com/erikperttu/steering-coding-agents).
- Semantic/episodic/procedural split: notes edited in place with
  `status: superseded` (never deleted) = semantic; append-only logs +
  journal = episodic; `procedures/` + skills = procedural; a curator
  periodically folds episodic into semantic so the brain doesn't rot
  (https://github.com/hess0ul/ai-workspace-template).

## 4. Machine-written memory (vendor layer, complements repo files)

- Claude Code auto memory: Claude writes notes itself (build commands,
  debugging insights, architecture notes, preferences); per-repo
  directory at `~/.claude/projects/<slug>/memory/`, `MEMORY.md` index,
  first 200 lines or 25 KB loaded each session, topic files on demand;
  machine-local, not shared across machines; subagent memory separate
  (https://code.claude.com/docs/en/memory).
- After `/compact`, project-root `CLAUDE.md` is re-read from disk;
  nested `CLAUDE.md` / path-scoped rules reload only on matching file
  reads — conversation-only instructions vanish unless promoted to a
  file (https://code.claude.com/docs/en/memory).

## 5. What this means for THIS workspace (local mapping, not web claims)

- Current layout already implements the converged shape:
  `AGENTS.md` router + `.jcode/prompt-overlay.md` (always-loaded
  contract) vs `PROGRESS.md` + `logs/` + `MONITORING/` (agent-written
  state) — see `C:/Users/Mateusz/Desktop/ROOT/AGENTS.md`,
  `C:/Users/Mateusz/Desktop/ROOT/PROGRESS.md`.
- Gaps vs the surveyed patterns worth considering as S1/S2 follow-ups
  (not this record — research is read-only): (a) no bounded single
  scratchpad — `PROGRESS.md` (91 KB) violates the 80-line / small-hub
  discipline; (b) rotation is manual — no verbatim archive script;
  (c) close-session is doctrine, not a skill/hook, so it can be skipped.
