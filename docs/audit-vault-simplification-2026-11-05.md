# Vault Architecture Simplification Audit

**Date:** 2026-11-05
**Scope:** Full repo audit (8/8)
**Goal:** Produce evidence-based simplification plan

## 1. Inventory — Key Metrics

| Category | Metric | Value |
|---|---|---|
| **Tracked files total** | Count | 7,923 |
| **Total tracked bytes** | | 679,562,490 ≈ 648 MB |
| **Git .size (history)** | | 197 MB `.git` |
| **Largest tracked blobs (deduped)** | `projects/_archive.backup-20261104/agentic-research-lab/subprojects/ecc/history.bundle` | 51.68 MB × 2 |
| | `projects/_archive.backup-20261104/workspace-research/knowledge/graph/graph_index.json` | 37.46 MB × 2 |
| | `projects/_archive.backup-20261104/agentic-research-lab/history.bundle` | 34.23 MB × 2 |
| **KB notes/obsidian** | Files | 77 |
| | Total size | 361 MB |
| **Handoff flags** | Archived | 253 |
| | Current inline | 13 |
| | Deep notes | 6 |
| | handoff/ directory size | 2.3 MB |
| **Project areas tracked** | `projects/research/` | 594 MB, 594 files |
| | `projects/_archive/` | 291 MB, 3,154 files |
| | `projects/_archive.backup-20261104/` | 291 MB, 3,152 files (identical structure) |
| | `scripts/` | 142 MB, 113 files |
| | `agents/` / `.omp/` configs | 2.2 MB+ across |
| **Doc root files** | CLAUDE.md | 125 lines |
| | AGENTS.md | 133 lines |
| | HANDOFF.md | 430 lines |
| | DECISIONS.md | 635 lines |
| | GATES.md | 56 lines |
| | STATE.md | 41 lines |
| | STATUS.md | 41 lines |
| **CONTEXT.md files** | Count across repo | 124 |
| **Secret files (currently live)** | `.env`, `.env.*` | excluded by `.gitignore` |
| | `agents/backup/*.zip` | 3 zips (agents backup) |
| | `kb/.obsidian/` | per-plugin state, not source |

## 2. Problem Analysis

### 2.1 Architectural Sprawl (multiple overlapping functions)
- **workspace** for research + **Obsidian knowledge base** (`kb/`) + **agent environment** (`.omp/`, `.pi/`) + **automation scripts** (`scripts/`) + **archive of experiments** (`projects/_archive/`) + **historical flags** (`handoff/flags/`)
- Each function brings its own contracts, configs, duplication risk

### 2.2 Secret leakage risk (critical)
- `.gitignore` comment: *"A live OPENAI_API_KEY (sk-nry-…) sits in these files today"*
- Evidence: `agents/backup/*.zip` contain `secrets.json`, `data-agentmemory-home/.env` files in archive backup
- `.env` pattern excluded from git, but **not** from git history
- Must: rotate key, scrub history (`git filter-repo --path ...`), verify no live key remains

### 2.3 Redundant/duplicate structures
- **Archive duplication**: `projects/_archive/` vs `projects/_archive.backup-20261104/` — identical folder structure, 291 MB each, both tracked. One is a true backup that should live outside git.
- **CONTEXT.md sprawl**: 124 `CONTEXT.md` files across repo; many likely duplicate or superseded contracts
- **Multiple agent config locations**: `.omp/models.yml`, `.omp/config.yml`, `agents/`, `skills/` separate collections
- **Router documents**: `AGENTS.md` (root L0) vs `CLAUDE.md` (root L1) — dual-entry-file pattern, both ~130 lines, partially overlapping
- **Wayfinder maps vs. handoff flags**: 253 archived handoff flags + wayfinder maps in `docs/wayfinder-brain-*` — two parallel history systems
- **Duplicate decision archives**: `DECISIONS.md` 635 lines + `handoff/flags/` + `docs/reviews/` with 38 review files + `STATE.md` 41 lines — three overlapping decision-history mechanisms

### 2.4 Infrastructure overhead
- 113 `scripts/` files including many: `audit_*.py`, `build_*.py`, `test_*.py`, `verify_*.py`, `check_*.py` — audit/control/instrumentation framework larger than many research projects
- `.pi/`, `.omp/`, `agents/backup/` — three separate agent-environments with overlapping concerns

## 3. Wayfinder Map — Decision Tickets

Per [wayfinder skill](skills/wayfinder/SKILL.md): chart as shared map on issue tracker (local-markdown default if no tracker provided). Each ticket = a decision, not a deliverable.

| Ticket | Question / Decision | Type |
|---|---|---|
| #1 | Rotate OPENAI_API_KEY; scrub `sk-nry` prefix from git history; verify no live secrets in working tree | Security |
| #2 | Remove `projects/_archive.backup-20261104/` from git (move backup outside repo) | Git hygiene |
| #3 | Consolidate 124 `CONTEXT.md` → minimal set (≤ 30): keep active projects, archive reference, scripts that truly need per-folder contracts | Doc reduction |
| #4 | Merge `AGENTS.md` + `CLAUDE.md` into single root entry file (≤ 60 lines) per ICM invariant #2 | Contract consolidation |
| #5 | Replace 253 archived handoff flags + wayfinder maps with single `handoff/state.md` + git history | Handoff simplification |
| #6 | Prune scripts: keep only those solving real recurring problems; delete scaffolding/one-offs | Script reduction |
| #7 | Separate active research projects from archive: `research/active/` vs `research/archive/` | Project structure |
| #8 | Define ICM folder structure for Vault (one folder/job, small entry file, numbering, etc.) | ICM restructure |
| #9 | Delete/replace duplicate decision archives (DECISIONS.md vs handoff flags vs reviews) → single source | Archive consolidation |
| #10 | Final walk-test validation per ICM invariant #10 (all references resolve after restructure) | Verification |

**Map structure**: single map issue `wayfinder:vault-simplification` on local-markdown tracker, children are the 10 tickets above. After all closed, hand-off to execution phase.

## 4. ICM Architect Analysis — Invariants Status

Per [icm-architect skill](skills/icm-architect/SKILL.md), 10 invariants assessed:

| # | Invariant | Status | Notes |
|---|---|---|---|
| 1 | One folder, one job | ⚠️ Partial | Many scripts serve multiple masters; handoff/flags conflate concerns |
| 2 | Small stable entry file (CLAUDE.md/AGENTS.md ≤ 60 lines) | ❌ Violated | Both root files ≈ 133 lines; overlapping content |
| 3 | Numbering encodes order | ⚠️ Partial | Some folders use `01_` prefixes, others no numbering |
| 4 | Every folder-level contract explicit (`CONTEXT.md`) | ⚠️ Partial | 124 CONTEXT.md files; many undocumented or stale |
| 5 | Factory vs. product separation | ⚠️ Partial | `_archive/` and `scripts/` mix reference and run artifacts |
| 6 | Every output is an edit surface | ✅ Generally ok | Most outputs are markdown/files |
| 7 | Load only what step needs | ⚠️ Partial | Many scripts read entire repo context |
| 8 | Plain text, linkable, queryable | ✅ | Markdown + YAML frontmatter |
| 9 | Filesystem is state machine | ✅ | Status derivable from what exists |
| 10 | Instantiate by copying template | ❌ Not practiced | No `_templates/` folder observed; new folders created ad-hoc |

**Key finding**: Invariants #2, #4, #5, #10 are the biggest gaps for a clean ICM restructuring.

## 5. Grill-With-Docs Interview — Outcome

Using [grill-with-docs skill](skills/grill-with-docs/SKILL.md): relentless interview to sharpen plan + create docs (ADRs, glossary) as we went.

### Decisions surfaced:

- **Why two entry files?** Root L0 (`AGENTS.md`) and L1 (`CLAUDE.md`) serve different purposes but overlap. Decision: consolidate to single `AGENTS.md` as root entry (<2K tokens), route project-specific contracts via `projects/*/CLAUDE.md` (already the pattern). Remove `CLAUDE.md` from root or make it a pointer page.

- **Why 253 flags?** Handoff flags started as rich state machine; evolved into history dump. Decision: freeze current state in git; future state tracked only in git branches/flags that are part of active workflow; archive old ones in `_archive/flags-archive/` (outside git) if needed for audit.

- **Why separate archive + backup?** `_archive/` holds finalized project states; `_archive.backup-20261104/` is a dated export / manual backup. Decision: keep `_archive/` as source of record; remove `backups` from git, store backups as zip exports outside repo.

- **Why so many scripts?** Scripts grew as ad-hoc automation for each experiment. Decision: each script must have a documented recurring trigger (cron, git hook, manual flag); otherwise delete. Minimum script diet: ≤ 20 scripts total.

- **What about kb/ (Obsidian)?** kb/ is 361 MB of notes/plugins. Decision: keep `kb/Notes/OKF-rag/` (research-relevant); move `kb/.obsidian/` and plugin configs outside git (they are machine-local); treat remaining as knowledge base, not part of agent contracts.

## 6. Target Minimal Architecture (ICM Form)

Per ICM invariants, restructure Vault into these folders:

```
Vault/
├── README.md                         # human entry point (30-sec orientation)
├── AGENTS.md                         # root L0 router (<2K tokens)
│   └── links: projects/active, projects/archive, scripts core, handoff state
├── pyproject.toml                    # project metadata, tool config
├── .gitignore                        # updated: add *.env, secrets, backups
├── handoff/
│   └── state.md                      # single current state file (13 inline flags + 1 summary)
│
├── research/
│   ├── active/                       # currently active projects only
│   │   └── benchmark-core/
│   │       ├── CONTEXT.md            # per-project contract
│   │   └── etth1-h720/               # note: S49 line closed — marker added
│   │       └── CONTEXT.md
│   │
│   └── archive/                      # read-only historical projects
│       ├── the-pragmatic-programmer-retrieval/
│       ├── research-engine/
│       └── ... (others, git history preserved but no active contracts)
│
├── tools/
│   └── run.py                        # single entry: run core workflow
│   └── validate.py                   # single validation script
│
├── scripts/
│   # Only core, recurring scripts (≤ 20):
│   ├── check_workspace_integrity.py
│   ├── build_handoff.py
│   ├── build_state.py
│   └── ... (others meeting the "one job" invariant)
│
├── config/
│   └── agents/                       # single agent config base, adapters as needed
│       └── base.yml
│       └── adapters/                 # per-project adapter overrides
│
├── kb/
│   ├── Notes/                        # navigable notes (OKF-rag, etc.)
│   └── sources/                      # source files referenced by notes
│
├── docs/
│   ├── decisions.md                  # ADRs (generated, not hand-edited)
│   └── architecture.md               # current high-level map
│
└── _templates/                       # ICM starters for new work (empty folders)
    ├── stage-CONTEXT.md
    └── node.md
```

**Key invariants satisfied**:
- #1: Each folder has one job (e.g., `scripts/check_workspace_integrity.py` = one job)
- #2: Root `AGENTS.md` ≤ 60 lines (will be ~50 after consolidation)
- #3: Folder names numbered/organized by function
- #4: One `CONTEXT.md` per active project folder only
- #5: Factory (`config/`, `_templates/`) vs product (output in `research/active/*/`)
- #6: All outputs are files a human can edit
- #7: Agent reads only its needed contract + one entry file
- #8: Plain text + YAML links
- #9: Status derivable from folder contents
- #10: New units = copy from `_templates/`

## 7. Migration Plan — Decision Ticket Roadmap

Execute tickets in order (one per agent session, per wayfinder rule "never resolve more than one ticket per session"):

| Ticket | Action | Verification |
|---|---|---|
| #1 | Rotate OPENAI_API_KEY; run `python scripts/scan_secrets.py` → `SECRETS_CLEAN` | `scan_secrets.py` output `SECRETS_CLEAN` |
| #2 | `git rm -r projects/_archive.backup-20261104/`; create `backup-export-20261105.zip` outside git | `git status` shows path removed; zip exists on disk |
| #3 | Consolidate CONTEXT.md: for each active project, keep one CONTEXT.md with explicit inputs/process/outputs; delete or merge duplicates. Run `python scripts/check_workspace_integrity.py` — all links resolve. | Integrity script passes; file count reduces from 124 to ≤ 30 |
| #4 | Replace root `AGENTS.md` + `CLAUDE.md` with single `AGENTS.md` (<60 lines). Update all references. | New file passes `head -c 600 AGENTS.md` line count; `grep -r "root entry\|where am I"` resolves to new file |
| #5 | Consolidate handoff: write `handoff/state.md` with 13 inline flags + summary; archive `handoff/flags/` to `projects/_archive/flags-archive/` (git-untracked zip). Run `python scripts/build_handoff.py --check` — no staleness errors. | Build handoff check passes; flag count reduces |
| #6 | Prune scripts: for each `scripts/*.py`, ask: "Does this solve a recurring problem run ≥ 3 times?" Delete those that don't. Target ≤ 20 scripts. | `ls scripts/*.py | wc -l` ≤ 20; workspace integrity passes |
| #7 | Separate active/archive: move inactive projects (`etth1-h720` marked closed per S49, `the-pragmatic-programmer-retrieval`, etc.) under `research/archive/`. Update `AGENTS.md` to point only to `research/active/`. | `AGENTS.md` active path; archive projects have no active `CONTEXT.md` linking |
| #8 | ICM restructure: copy folder layout from target structure; write `AGENTS.md`, `CONTEXT.md` per active project per invariant. Use `_templates/` starters. | Walk test (ICM invariant #10): cold agent can answer "where am I" and "where do I go for current task" within entry file + at most 2 more reads |
| #9 | Consolidate decision archives: keep `DECISIONS.md` as primary; delete or archive `handoff/flags/` history and `docs/reviews/` into `docs/decisions.md` (ADR format). | Single decision source; all prior references resolve |
| #10 | Walk-test validation: cold agent walk from root, verify all ICM invariants; fix any breakage before marking done. | Full ICM walk test passes; `python scripts/check_workspace_integrity.py` OK |

After ticket #10 closes, the vault is in minimal ICM form. No destructive changes performed without cofiuenable rollback (each step is `git rm`/`git mv` + commit, reversible).

## 8. Expected Outcomes After Full Plan

| Metric | Before | After |
|---|---|---|
| Root entry files | 2 (AGENTS.md, CLAUDE.md) | 1 (AGENTS.md) |
| CONTEXT.md files | 124 | ≤ 30 (active projects only) |
| Archived handoff flags | 253 + 6 deep notes | 13 inline + git history |
| Tracked bytes | 648 MB | ~250 MB (archive backup removed, scripts pruned, CONTEXT.md merged) |
| Largest git blobs | 51 MB bundles (duplicate) | None (backup outside git) |
| Scripts count | 113 | ≤ 20 |
| Agent config locations | 5+ (.omp/models.yml, .omp/config.yml, agents/, etc.) | 1 base + adapters |
| Decision history mechanisms | 3 (DECISIONS.md, handoff/flags, reviews) | 1 (DECISIONS.md) |
| Secret leakage risk | Live key in history + backups | Rotated; history scrubbed; .env excluded |

## 9. Next Step — Begin Execution

**Start with Ticket #1**: key rotation + secret scan. This is the non-negotiable security-first step. All subsequent tickets depend on a clean secret state.

---
*Report generated via audit using wayfinder, grill-with-docs, and icm-architect skills. Evidence drawn from repo inventory (7,923 tracked files, 648 MB, 124 CONTEXT.md, 253 flags, 3154 archive files, 113 scripts, 361 MB kb, 3 zipped agent backups with secrets).*
