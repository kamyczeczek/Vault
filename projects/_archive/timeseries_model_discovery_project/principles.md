---
type: Concept
title: principles
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# PRINCIPLES.md — Workspace Core Doctrine

All agents working in this workspace MUST adhere to these foundational principles. Normative keywords follow RFC 2119 (`MUST`, `MUST NOT`, `WHEN`, `BEFORE`).

---

### P1: Routing Freshness (ICM Synchronization)
- **WHEN ANY** change alters stage structure, contracts, skills, tools, or worker subworkspaces, the agent **MUST** update affected routing tables (`AGENTS.md`, `CONTEXT.md`, `PROCESS/WORKFLOW.md`, `brain/CONTEXT.md`) and run verification in the same session.
- Stale routing paths or orphan references are forbidden.

### P2: Mandatory Skill Selection
- **BEFORE** executing any task, if the user has not explicitly assigned a skill, the agent **MUST** review `skills/SKILLS.md`, select the best-matching skill(s) based on task intent, and adhere to its procedure.
- If no skill applies, the agent **MUST** explicitly state why general execution is chosen.

### P3: Git Context & Reversibility (Anchoring & History Awareness)
- **BEFORE** modifying existing modules or contracts, the agent **MUST** inspect recent git history on touched files (`git log -n 5 --oneline -- <paths>`) to avoid reverting deliberate recent changes or re-exploring refuted paths.
- **BEFORE** non-trivial, multi-file, or exploratory edits, the agent **MUST** establish a clean anchor (`git status` clean or explicit `git stash create` / checkpoint commit) so broken states can be reverted cleanly without code debris.
- Exploratory edits that fail acceptance thresholds **MUST** be cleanly rolled back (`git reset --hard` to the anchor) rather than left as half-finished residue.

### P4: Structured Git Commits (Decision Records via Git Trailers)
- **UPON** completing a task and confirming all relevant gates pass (`python brain/internal/verify_sync.py`, `python PROCESS/run_gates.py`), the agent **MUST** produce an atomic git commit.
- Commit messages **MUST** follow a structured decision record using native Git Trailers:
  1. **Header**: Concise imperative summary with conventional scope (e.g., `feat(brain): ...`, `fix(routing): ...`).
  2. **Body**: Concrete explanation of what changed and the architectural rationale.
  3. **Trailers (RFC 822 / Lore Protocol format)** at the end:
     - `Intent:` Primary goal / why this change exists.
     - `Rejected-Alternative:` Other approaches considered and why they were abandoned.
     - `Verified-By:` Exact command and exit code / output summary confirming behavior.
     - `Gates-Passed:` Comma-separated list of passing gates.
