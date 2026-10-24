#!/usr/bin/env python3
"""Workspace integrity gate — runs from the root, where the mess actually lands.

The per-project gates inside `projects/research/*/scripts/` all resolve ROOT to their own
repository. A file created one level above that repository is outside every one
of them. This gate is the one that looks at the root.

This docstring is the check catalogue — the single home of gate semantics.
Other documents (CLAUDE.md, HANDOFF.md, CONTEXT-MAP.md) link here instead of
restating which check is which or which is hard; a restatement drifts.

Hard checks — any failure stops the commit:

  R1 shape       the root contains exactly the allowed entries, nothing else
  R2 integrity   every `../` link in a project entry/contract file resolves
  R3 hygiene     no untracked build residue, no zero-byte file at the root
  R9 routing     every file route named in a routing section resolves —
                 tables in the root entry files, Where/Route/Task sections
                 in project entry files, Inputs/Process/Outputs in project
                 contracts (icm-architect walk test: a cold agent follows
                 routes, it does not remember them). A dead FILE route is a
                 failure; an unverifiable route (missing parent, runtime
                 artifact) is a warning.
  R11 catalog    the root skills catalog (skills/SKILLS.md) is consistent
                 with the filesystem, via skills/verify_catalog.py: every
                 on-disk skill has exactly one row, every row points at a
                 real skill folder, no duplicates. Drift is a dead routing
                 surface — same class as an R9 dead route.
  R12 handoff    the generated HANDOFF.md matches handoff/flags/ + handoff/deep/
                 (scripts/build_handoff.py --check). Hard, because the only
                 reader of a stale cold-start view is the next cold session,
                 which cannot tell it is stale.
R13 citation   three gates over the same claim. `audit_agents_md.py --check`
                  (AGENTS.md matches its recorded baseline) and
                  `--report-check` over every report in docs/reviews/ (its
                  embedded block is exactly what the script emits, with exactly
                  one marker pair), then `audit_prose_numbers.py --check` on
                  each report: every figure in the prose is emitted by the
                  block, matched by a named shape, or listed with a class and a
                  reason. Hard, because a report that misquotes a measured
                  number is the failure this workspace keeps re-discovering in
                  prose: "35", then "610", then "22", then "18". The first two
                  gates cannot see each other's document — and neither could see
                  the prose, which is why "137" survived four mentions while the
                  block beside it was verified.
  R14 memory     the session-memory index covers the sessions on disk
                  (`memory_index.py freshness`, lag limit 24h). Hard, because a
                  stale index answers "nobody has hit this" confidently and the
                  agent that believes it re-invents a rejected fix. Degrades to
                  OK only when there is no index and no sessions (a fresh clone)
                  — an index that exists but cannot be compared against any
                  store is a FAIL, because nothing verified it.

Advisory checks — warn, never stop the commit (trimmed 2026-10-01; a gate
that stops the world for taste costs more than it saves):

  R4 grade       every project entry file declares exactly one grade:
                 candidate | active | demoted (D4)
  R5 open work   every project contract has a `## Open work` heading (D7)
  R6 skills      every project has a `skills/` home plus a `MANIFEST.md`;
                 a vendored skill must be stamped (D8)
  R7 map         every project MAP.md is current, not merely present (D9)
  R10 integrity  a project's `## Open work` must not assert a known defect
                 as current (mutation-tested)
   R16 usage      a commit that touched `scripts/**`, `hooks/**`, `skills/**`
                  or `.dsh/**` within the last 30 min should leave a
                  session-memory usage trace: a fresh
                  `scripts/_scratch/sessions/05_store/queries.jsonl` entry, or a
                  mention of the word `query` in the commit subject
                  (substring check, not a verified `query "..."`
                  citation — see the function docstring). Warns, never
                  blocks — it flags the skipped visit to the door
                  (the debug-with-memory skill).
   R17 hookspath  `core.hooksPath` must be `hooks`, otherwise the pre-commit
                  gate (whitespace + rebuilt views + this script) never runs
                  and every other hard check is advisory in practice. Hard,
                  because a gate with no automatic caller is documentation,
                  not a gate. Fix: `git config core.hooksPath hooks`
                  (per-clone setting, not versioned).
   R18 governance a streak of >=3 consecutive HEAD commits touching only
                  governance paths (`handoff/`, `HANDOFF.md`, `STATE.md`,
                  `docs/`) with no `projects/` change warns that research
                  progress stalled. Advisory, never blocks. Second half is
                  `handoff/flags/session-decision.md` older than 3 days
                  warns; older than 14 days fails — a recorded decision
                  without an executor must not silently age out (Reguła 62),
                  but a hard fail on day 4 would freeze unrelated commits
                  while the owner finds time to decide.
   R19 new-flag    a newly added flag (`handoff/flags/*.md` untracked or
                  staged-new) whose `since:` is older than 3 days, or whose
                  body lacks a `not checked:` line, warns as
                  SUSPECTED_RETROSPECTIVE — a flag documenting somebody
                  else's older work (session inflation) instead of this
                  session's state. A new flag with a fresh `since:` but no
                  commit in `git log --since=<since>` about the flag's topic
                  warns as flag-without-commit. Advisory, never blocks.
   R20 scars      SCARS.md must not repeat a `## S<number>` heading — two scars
                  sharing one id makes `problems:<n>` ambiguous for the brain
                  layer's evaluation. Advisory.
   R21 brain      the curated brain layer is real. `brain/brain.db` is a
                  gitignored, derived artifact: `scripts/ingest_brain.py`
                  rebuilds it from SCARS.md / DECISIONS.md / brain/lessons.md,
                  and `--check` asserts it is exactly the parse of those sources
                  (freshness and coverage are the same question). Then
                  `scripts/memory/eval_brain.py --check` asserts the layer's
                  checked-in evaluation has not fallen below its recorded
                  baseline. Hard, because this layer's entire job is to be *the*
                  answer to "what is the rule about X": a layer that quietly
                  stopped holding a scar answers "no such rule" with exactly the
                  confidence of a correct one, and 12 of the 24 rows it used to
                  hold were fabricated. Degrades to a warning — never to a
                  silent pass — only when `brain.db` is absent altogether, which
                  is what a fresh clone looks like, and names the rebuild.
   R22 store      no agent store has silently dropped sessions (S68 shape):
                  `scripts/memory_index_check_drift.py --check --drift-only`
                  asserts, per store, that a store holding records on disk is
                  not read as empty and that its expected tables still exist.
                  Advisory, and drift-only on purpose — the "newest session is
                  indexed" condition also trips on ordinary staleness (a session
                  newer than the last ingest), which R14 already gates, so
                  including it here would make the advisory shine on almost
                  every close. The full assertion is the hard caller
                  `memory_index.py ingest`, which exits 1 right after it indexes.
                  A store absent from this clone is skipped; there is nothing
                  to drift.

R1 is a shape assertion, not a count. "No new .py files" is a rule someone
who reads it can route around; naming every allowed entry is not. R3
caught a real incident: a malformed shell command left two files
literally named `$(git` and `'` at the root, and seventeen project-level
gates passed while they sat there.

Adding a root-level entry is a structural decision, made in one place:
declare it in `CLAUDE.md` ("Where things live") and add the name to
`ALLOWED_ROOT` below, in the same change. R1 then asserts both halves.
A gate that can be silenced by editing its own allow-list alone is not a
gate — the table edit is what keeps this one honest.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# R1: the exact set the root is allowed to contain. Adding a root-level folder is
# a structural decision and belongs in the root CLAUDE.md project table, not in
# someone's shell history.
ALLOWED_ROOT = {
    "CLAUDE.md",
    "AGENTS.md",
    "projects",
    "skills",
    "CONTEXT-MAP.md",
    "TOOLS.md",
    "DECISIONS.md",
    "PHILOSOPHY.md",
    "TOKEN-EFFICIENCY.md",  # D15: measured token/cache evidence behind the L0 rules
    "GLOSSARY.md",
    "HANDOFF.md",       # D16: portable cold-start state; hand-written, links project detail (never copies)
    ".ralph",           # ralph-loop generated projection (INDEX.md + registry.json); rebuilt by skills/ralph-loop/scripts/ralph.py, never hand-edited
    "library",          # raw source documents; content-addressed, bytes never committed
    "scripts",          # this gate and its siblings
    "__pycache__",
    ".git",             # the root is versioned (D6)
    ".gitignore",
    ".gitattributes",
    ".pi",              # pi coding-agent harness working dir (settings.json); runtime artifact, declared not tracked
    ".opencode",        # opencode project config: custom subagents (.opencode/agents/answerpilot.md); declared in CLAUDE.md
    ".agents",          # goose lifecycle plugins (forge-guardrails hooks); declared in CLAUDE.md
    ".forge",           # forge-guardrails policy + runtime state; declared in CLAUDE.md
    "WORKFLOW_GOOSE_ICM.md",  # goose research-to-implementation ICM design; declared in CLAUDE.md
    ".dgc-evidence",  # per-run review product (runs/<id>/REVIEW.md + DECISION.json); declared in CLAUDE.md
    "STATE.md",       # generated worktree snapshot (build_state.py, ICM inv. 9); declared in CLAUDE.md
    "handoff",        # handoff state: flags/<flag>.md (one writer per flag) + deep/*.md; declared in CLAUDE.md, contract in handoff/CONTEXT.md
    "docs",           # workspace-level audit reports (docs/reviews/); declared in CLAUDE.md
    "tools",          # small single-file tools (tools/*.py + TOOL.md); declared in CLAUDE.md
    "agents",         # agent-config registry + backup/restore scripts (REGISTRY.md); declared in CLAUDE.md
    "hooks",          # repository Git hooks; declared in CLAUDE.md
    "SCARS.md",       # operational scars from real failures; pointer target of the L0 router, trigger in handoff/CONTEXT.md
    "TASKS.md",
    "PLAN.md",
    "brain",
    "wayfinder",
    "logs",
    ".obsidian",      # Obsidian per-device state (plugins tracked, cache/workspace gitignored); declared in CLAUDE.md
    ".smart-env",     # Smart Connections vector index (gitignored except smart_env.json); declared in CLAUDE.md
    "Notes",          # User notes in vault (untracked); declared in CLAUDE.md
    # Commit-approval token: minted by scripts/close.py immediately before its
    # own commit, consumed by scripts/commit_gate_guard.py from the pre-commit
    # hook. Runtime artifact — declared in CLAUDE.md, listed in .gitignore, never
    # committed. Without this entry R1 would fail the moment close.py mints it.
    ".commit-approved",
}

# Live projects live one level down in `projects/research/` (the research
# group); `projects/_archive/` stays directly under `projects/` and is
# excluded by the name filters below, which is the point of archiving.
PROJECTS = sorted(
    p for p in (ROOT / "projects" / "research").iterdir()
    if p.is_dir() and not p.name.startswith(".") and not p.name.startswith("_")
) if (ROOT / "projects" / "research").is_dir() else []

RESIDUE_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".ipynb_checkpoints"}
RESIDUE_SUFFIX = {".pyc", ".pyo", ".tmp", ".orig", ".rej", ".bak", ".log"}

# Declared runtime-output directories: regenerable per-run telemetry a tool owns
# end to end, tracked in the project's .gitignore, never hand-edited and never a
# product. Without this list a background job's own log is indistinguishable from
# an untracked stray, and the two available responses are both wrong: commit
# churn on every run, or delete the log and lose the only evidence of what the
# run actually did.
#
# Each entry is a project-relative directory. Its contents are still checked for
# the other rules (dead links, grades, MAP freshness); only R3 residue exempts
# them. A project that wants a directory exempted must list it in its .gitignore
# too — this list is the gate's half of that contract, and
# `check_declared_output_dirs_ignored` enforces the agreement.
DECLARED_OUTPUT_DIRS = {
    "reflection/logs",  # background-reflection supervisor: {topic}.status.json/.lock/.log
}

FAILS: list[str] = []
WARNS: list[str] = []


def check_r1_root_shape() -> None:
    """The root holds only what the catalog declares. Stray files are failures."""
    actual = {p.name for p in ROOT.iterdir() if p.name not in RESIDUE_DIRS}
    unexpected = actual - ALLOWED_ROOT
    # Declared but legitimately absent. __pycache__ exists only after a Python
    # run; scripts/ is tooling-created; .commit-approved exists only while a
    # close.py commit is in flight — it is minted immediately before that commit
    # and is inert 300 s later. A declared-optional entry must not fail the gate
    # for being absent, or the gate would demand a permanent runtime artifact.
    optional = {"__pycache__", "scripts", ".commit-approved"}
    missing = ALLOWED_ROOT - actual - optional
    for name in sorted(unexpected):
        kind = "directory" if (ROOT / name).is_dir() else "file"
        FAILS.append(f"unexpected {kind} at workspace root: {name!r}")
    for name in sorted(missing):
        FAILS.append(f"missing required root entry: {name!r}")


def check_r2_reference_integrity() -> None:
    """Every `../` path in a routing or contract file must resolve.

    A routing file is a promise. A link that does not resolve is a promise the
    reader cannot keep, and a cold agent has no way to tell it apart from one
    that does.
    """
    # A glob is a pattern, not a literal path; it is checked by R1/R3 instead.
    link_re = re.compile(r"`(\.\.[^`\s]*)`")
    for proj in PROJECTS:
        for name in ("CLAUDE.md", "CONTEXT.md"):
            doc = proj / name
            if not doc.is_file():
                continue
            for raw in link_re.findall(doc.read_text(encoding="utf-8", errors="replace")):
                # Only a claim of the form `./x` or `../x` is a path claim. A
                # backticked regex example in prose also starts with dots, and
                # a link checker that cries wolf on prose gets switched off.
                if not re.match(r"^\.\.?/", raw):
                    continue
                target = raw.rstrip("/.,)").rstrip("*")
                if any(c in target for c in "*?["):
                    continue
                if not (proj / target).resolve().exists():
                    FAILS.append(f"{proj.name}/{name}: dead link {raw!r}")


def check_r3_hygiene() -> None:
    """No build residue, and no zero-byte file at the root.

    "Residue" is what no human asked for. A tracked file is never residue: a
    .log inside results/ that a run produced and a commit kept is a product,
    and failing the build on it teaches people to delete their own evidence.
    """
    for proj in PROJECTS:
        tracked = _tracked_files(proj)
        for path in proj.rglob("*"):
            parts = set(path.parts)
            if parts & RESIDUE_DIRS or ".git" in parts:
                continue
            if _in_declared_output_dir(path, proj):
                continue
            if not path.is_file() or path.suffix.lower() not in RESIDUE_SUFFIX:
                continue
            if path.relative_to(proj).as_posix() in tracked:
                continue
            FAILS.append(f"untracked build residue: {path.relative_to(ROOT)}")
    for path in ROOT.iterdir():
        if path.is_file() and path.stat().st_size == 0 and path.name != ".gitkeep":
            FAILS.append(f"zero-byte file at workspace root: {path.name!r}")
    check_declared_output_dirs_ignored()


def _in_declared_output_dir(path: Path, proj: Path) -> bool:
    """True when `path` sits under one of this project's declared output dirs."""
    try:
        rel = path.relative_to(proj).as_posix()
    except ValueError:
        return False
    return any(rel == d or rel.startswith(d + "/") for d in DECLARED_OUTPUT_DIRS)


def check_declared_output_dirs_ignored() -> None:
    """A declared output dir must also be gitignored by the project that owns it.

    Otherwise the gate exempts a directory that git still considers untracked,
    and the project accumulates residue the gate can no longer see — the worst
    outcome, because hygiene stops being enforced rather than being satisfied.
    """
    for proj in PROJECTS:
        for rel in sorted(DECLARED_OUTPUT_DIRS):
            target = proj / rel
            if not target.is_dir():
                continue
            probe = subprocess.run(
                ["git", "-C", str(proj), "check-ignore", "-q", rel + "/"],
                capture_output=True, text=True, check=False,
            )
            if probe.returncode != 0:
                FAILS.append(
                    f"{proj.name}: declared output dir `{rel}/` is not in .gitignore "
                    f"— the gate exempts it but git would still report it untracked"
                )


def _tracked_files(proj: Path) -> set[str]:
    """Files git already tracks in this project; a set of repo-relative posix paths."""
    if not (proj / ".git").exists():
        return set()
    out = subprocess.run(
        ["git", "-C", str(proj), "ls-files"],
        capture_output=True, text=True, check=False,
    )
    return {line for line in out.stdout.splitlines() if line}

GRADES = ("candidate", "active", "demoted")


def check_r4_grade_declared() -> None:
    """Every project entry file declares a grade (D4).

    Advisory after the 2026-10-01 gate trim: the field's value is that a
    reader can sort the portfolio by it; an undeclared grade just means
    the reader cannot sort, which no longer stops the commit.
    """
    for proj in PROJECTS:
        entry = proj / "CLAUDE.md"
        if not entry.is_file():
            WARNS.append(f"{proj.name}: no entry file (CLAUDE.md)")
            continue
        text = entry.read_text(encoding="utf-8", errors="replace")
        found = [g for g in GRADES if re.search(rf"^grade:\s*{g}\s*$", text, re.M)]
        if not found:
            WARNS.append(
                f"{proj.name}/CLAUDE.md: no grade: frontmatter "
                f"(expected one of {', '.join(GRADES)})"
            )
        elif len(found) > 1:
            WARNS.append(
                f"{proj.name}/CLAUDE.md: {len(found)} grades declared ({', '.join(found)}); "
                "exactly one is the project's position"
            )


def check_r5_open_work() -> None:
    """Every project contract has a `## Open work` heading (D7; advisory
    after the 2026-10-01 gate trim). The gate requires the heading, not its contents. "Nothing known" is a true
    and useful sentence; what must not happen is a missing heading going
    unnoticed, which is how `datasets` reached 0 of 23.
    """
    for proj in PROJECTS:
        contract = proj / "CONTEXT.md"
        if not contract.is_file():
            WARNS.append(f"{proj.name}: no contract (CONTEXT.md)")
            continue
        if not re.search(r"^##\s+Open work\s*$", contract.read_text(
            encoding="utf-8", errors="replace"
        ), re.M | re.I):
            WARNS.append(f"{proj.name}/CONTEXT.md: missing '## Open work' section")


def check_r6_skills_home() -> None:
    """Every project owns a `skills/` home and a MANIFEST.md (D8; advisory
    after the 2026-10-01 gate trim). Contents may be empty — skills are vendored on first use. What must never
    happen is a vendored skill that does not say where it came from, because
    an unstamped copy is a second home that looks identical to the first.
    """
    for proj in PROJECTS:
        skills_dir = proj / "skills"
        if not skills_dir.is_dir():
            WARNS.append(f"{proj.name}: no skills/ home (D8 — every project owns its skills)")
            continue
        manifest = skills_dir / "MANIFEST.md"
        if not manifest.is_file():
            WARNS.append(f"{proj.name}/skills/MANIFEST.md: missing (vendoring must be stamped)")
            continue
        text = manifest.read_text(encoding="utf-8", errors="replace")
        vendored = {p.name for p in skills_dir.iterdir() if p.is_dir()}
        for name in sorted(vendored):
            if not re.search(rf"`{re.escape(name)}`", text):
                WARNS.append(
                    f"{proj.name}/skills/{name}: vendored but not named in MANIFEST.md — "
                    "stamp it with its upstream and the date"
                )


def check_r7_map_current() -> None:
    """Every project with source has a MAP.md that is not stale (D9; advisory
    after the 2026-10-01 gate trim — a stale map warns, it does not stop a
    commit; the reader regenerates on demand). A generated index is only worth anything if it is current, so this checks
    freshness rather than existence. The generator is the single source: hand
    edits to MAP.md are overwritten on the next run, which is the point.
    """
    for proj in PROJECTS:
        out = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_project_map.py"),
             "--check", str(proj)],
            capture_output=True, text=True, check=False,
        )
        if out.returncode == 1:
            WARNS.append(f"{proj.name}: MAP.md is stale — run build_project_map.py")
        elif out.returncode != 0:
            WARNS.append(f"{proj.name}: MAP.md check errored: {out.stderr.strip()[:120]}")


def check_r9_routing_targets() -> None:
    """Every file route named in a routing section resolves (icm-architect).

    A cold agent follows routes; it does not remember workflows. A route
    table that names a file which no longer exists is how a built workflow
    gets "forgotten" — the agent follows the dead pointer, finds nothing,
    and reinvents the work. R2 covers `../` links; this covers the
    in-project routes (`scripts/ingest.py`) and the root tables.

    Scope is deliberately the routing edge only, not all prose:
    tables in the root entry files, Where/Route/Task sections in project
    entry files, Inputs/Process/Outputs in project contracts. History logs,
    open work, and rejected options are free prose and are not asserted.

    A missing FILE whose parent exists is a dead route: FAIL. A missing
    directory, or anything whose parent is absent (gitignored products,
    runtime-created outputs), is unverifiable rather than dead: WARN.
    Placeholders (`<name>`), globs, brace expansions, scores (`17/17`),
    and naming patterns (`NN_slug.md`) are not routes: skipped.
    """
    span_re = re.compile(r"`([^`]+)`")
    h2_re = re.compile(r"^##\s+(.*)")
    numfrac_re = re.compile(r"^\d+/\d+$")
    nolower_re = re.compile(r"^[^a-z]*$")
    placeholder_seg_re = re.compile(r"^[A-Z]{2,}_")
    line_suffix_re = re.compile(r":\d+$")

    def candidates(span: str):
        # A span may be a whole command (`python scripts/x.py --flag`):
        # test each whitespace-separated piece as a possible route.
        for piece in span.split():
            t = piece.strip("'\"(),;:")
            if "/" not in t:
                continue
            t = re.sub(r"^[.]/", "", t)
            if t.startswith("../"):
                continue  # R2 territory
            if re.search(r"[<>{}*?\[\]$@\\]", t):
                continue
            if "://" in t:
                continue
            t = line_suffix_re.sub("", t).rstrip("/.,;)")
            if not t or t in (".", ".."):
                continue
            if numfrac_re.match(t) or nolower_re.match(t):
                continue
            segs = [s for s in t.split("/") if s not in ("", ".")]
            if not segs or segs[0].startswith("."):
                continue  # optional hidden sidecars (.brain/, .claude/)
            if any(placeholder_seg_re.match(s) for s in segs):
                continue  # naming patterns, e.g. NN_slug.md
            yield t

    def section_lines(path: Path, kinds: tuple[str, ...]) -> list[tuple[int, str]]:
        out: list[tuple[int, str]] = []
        cur = ""
        for i, line in enumerate(
                path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            m = h2_re.match(line)
            if m:
                cur = m.group(1).strip().lower()
                continue
            if any(k in cur for k in kinds):
                out.append((i, line))
        return out

    targets: list[tuple[Path, str, int, str]] = []  # (base, doc, lineno, line)
    for name in ("AGENTS.md", "CLAUDE.md"):
        doc = ROOT / name
        if not doc.is_file():
            continue
        for i, line in enumerate(
                doc.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if line.lstrip().startswith("|"):  # the router is the tables
                targets.append((ROOT, name, i, line))
    for proj in PROJECTS:
        entry = proj / "CLAUDE.md"
        if entry.is_file():
            for i, line in section_lines(entry, ("where", "route", "task")):
                targets.append((proj, "CLAUDE.md", i, line))
        contract = proj / "CONTEXT.md"
        if contract.is_file():
            for i, line in section_lines(contract, ("inputs", "process", "outputs")):
                targets.append((proj, "CONTEXT.md", i, line))

    for base, docname, lineno, line in targets:
        src = "root" if base == ROOT else base.name
        for span in span_re.findall(line):
            for t in candidates(span):
                target = base / t
                if target.exists():
                    continue
                where = f"{src}/{docname}:{lineno} -> {t}"
                if target.parent.exists() and "." in target.name:
                    FAILS.append(f"dead route (file): {where}")
                elif target.parent.exists():
                    WARNS.append(f"route dir absent (runtime-created or moved?): {where}")
                else:
                    WARNS.append(f"route unverifiable (parent absent): {where}")


def check_r11_skills_catalog() -> None:
    """The root skills catalog stays consistent with the filesystem (R11).

    skills/verify_catalog.py is the deterministic check (MISSING-ROW,
    STALE-PATH, NAME-MATCH, DUP-ROW). Exit 1 is drift — a routing surface
    that will mislead a cold agent, so it fails like an R9 dead route.
    Exit 2 is the catalog itself missing or unparseable: also a failure.
    """
    out = subprocess.run(
        [sys.executable, str(ROOT / "skills" / "verify_catalog.py")],
        capture_output=True, text=True, check=False,
    )
    if out.returncode in (1, 2):
        detail = " ".join(
            line[4:] for line in out.stdout.splitlines() if line.startswith("  - ")
        )
        FAILS.append(
            f"skills/SKILLS.md drift (verify_catalog rc={out.returncode}): "
            f"{detail or out.stdout.strip()[:160]}"
        )


def check_r10_open_work_integrity() -> None:
    """R10: ## Open work must not hide a known integrity defect as current.

    Fails if Open work still asserts as live any of: unrunnable entry point
    ("cannot run", "cannot import"), unimplemented guard ("does not check",
    "does not implement", "bypasses it"), unwritten artifact ("never written"),
    single-sample numbers ("no seed sweep", "single sample"), silent fallback
    ("falls back silently", "silent LIKE", "silent fallback"), or unverified
    headline ("no artifact", "no file behind it", "0.746").
    Entries marked RESOLVED are ignored. Mutation-tested: reinsert any one
    phrase without RESOLVED and the gate must fail.
    """
    markers = (
        "cannot run", "cannot import", "cannot currently run",
        "does not check", "does not implement", "bypasses it",
        "never written", "no seed sweep", "single sample",
        "falls back silently", "silent like", "silent fallback",
        "no artifact", "no file behind it",
    )
    for proj in PROJECTS:
        contract = proj / "CONTEXT.md"
        if not contract.is_file():
            continue
        text = contract.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^##\s+Open work\s*$", text, re.M | re.I)
        if not m:
            continue
        section = text[m.end():]
        # Cut at next ## heading
        nxt = re.search(r"^##\s+", section, re.M)
        if nxt:
            section = section[:nxt.start()]
        for line in section.splitlines():
            if "resolved" in line.lower():
                continue
            low = line.lower()
            for mk in markers:
                if mk in low:
                    # 0.746 retired: allow only if line also says retired/unverified
                    if mk in ("no artifact", "no file behind it") and any(
                        w in low for w in ("retired", "unverified", "resolved")
                    ):
                        continue
                    WARNS.append(f"{proj.name}/CONTEXT.md Open work still live: {line.strip()[:140]}")
                    break


def check_r12_handoff_view_current() -> None:
    """The generated handoff view matches its flag files (hard; wired 2026-10-03).

    HANDOFF.md is derived from handoff/flags/*.md + handoff/deep/*.md by
    scripts/build_handoff.py and is never hand-edited (ICM inv. 9). Nothing
    else notices when it drifts: a session that edits a flag and forgets the
    rebuild leaves a cold-start view that contradicts the state it claims to
    carry, and the reader is the next cold session — the one that cannot tell
    it is stale. This is the same freshness argument as R7, made hard because
    HANDOFF.md is read by every session that enters at the root and is
    regenerated in one command.

    Hard, not advisory: the fix is one command and the failure is invisible to
    everyone but the reader. The cost is one subprocess on the root gate.
    """
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_handoff.py"), "--check"],
        capture_output=True, text=True, check=False,
    )
    if out.returncode == 1:
        FAILS.append(
            "HANDOFF.md is stale — run scripts/build_handoff.py "
            f"({(out.stdout + out.stderr).strip().splitlines()[-1][:120] if (out.stdout + out.stderr).strip() else 'no detail'})"
        )
    elif out.returncode != 0:
        FAILS.append(f"build_handoff.py --check errored (rc={out.returncode}): {out.stderr.strip()[:120]}")


def check_r24_status_view_current() -> None:
    """STATUS.md generated view matches flags + decisions + NEXT.md (hard).

    STATUS.md is derived by scripts/build_status.py and is never hand-edited
    (ICM inv. 9). Added 2026-10-18 to close the gap where only close.py
    enforced freshness.
    """
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_status.py"), "--check"],
        capture_output=True, text=True, check=False,
    )
    combined = (out.stdout + out.stderr).strip()
    detail = combined.splitlines()[-1][:120] if combined else "no detail"
    if out.returncode == 1:
        FAILS.append(f"STATUS.md is stale — run scripts/build_status.py ({detail})")
    elif out.returncode != 0:
        FAILS.append(f"build_status.py --check errored (rc={out.returncode}): {out.stderr.strip()[:120]}")


REVIEW_REPORTS = sorted((ROOT / "docs" / "reviews").glob("*.html")) if (ROOT / "docs" / "reviews").is_dir() else []


def first_meaningful_line(stderr: str, report: Path) -> str:
    """The child's own verdict, de-duplicated.

    `--report-check` names the report by absolute path, which would otherwise be
    printed twice — once by this gate and once inside the child's message, the
    second copy truncated mid-path. Strip the child's "FAIL — " lead and its path
    so the line says what is wrong and nothing else.
    """
    line = next((ln.strip() for ln in stderr.strip().splitlines() if ln.strip()), "no detail")
    if line.startswith("FAIL — "):
        line = line[len("FAIL — "):]
    return line.replace(str(report), "").strip()[:160]


def check_reviews_readme_rows() -> None:
    """Every report in this directory is named in the README that governs it.

    `docs/reviews/README.md` is the directory's contract — the five rules a report
    must follow, and the table of which file is which. It was the one document in
    the directory that no gate could check, so it drifted silently: at v8 a new
    report would land beside a README still describing v7's fifteen edits, with
    nothing to notice. Cheap to check, and the failure it prevents is a contract
    that reads as current and is not.
    """
    readme = ROOT / "docs" / "reviews" / "README.md"
    if not readme.is_file():
        FAILS.append("docs/reviews/README.md is missing — the directory has no contract")
        return
    text = readme.read_text(encoding="utf-8")
    for report in REVIEW_REPORTS:
        if report.name not in text:
            FAILS.append(
                f"docs/reviews/README.md does not mention {report.name} — add a row "
                f"to its Files table, or the contract does not describe this directory"
            )


def check_r13_report_citations() -> None:
    """AGENTS.md matches its baseline, and every committed audit report quotes it.

    Three halves of one claim. `--check` (audit_agents_md.py) guards AGENTS.md
    against the recorded baseline. It cannot see a document that misquotes those
    counts, and that is where the errors actually lived across six revisions of
    the architecture review: "35" (block boundaries), "~610 lines" (bytes, not
    lines), "22 evidence" (a hand-split), "18" (no arithmetic path at all). Each
    was invisible to the gate because each was in prose in a document, not in the
    audited file.

    So a report embeds the script's output between <!-- audit:begin/end --> and
    the second half re-derives it. `--report-check` exits 1 on a mismatch, on a
    missing or duplicated marker block, and on baseline drift.

    The third half is the one that was missing, and it is the reason the second
    half was not enough: `--report-check` only reads the generated block. A report
    could quote "AGENTS.md is 137 lines" in its prose while the block said 140,
    and the gate returned 0 — regenerating the block made the document *pass*
    while leaving the sentence wrong. `audit_prose_numbers.py --check` is that
    half: every figure in the prose must be emitted by the block, matched by a
    named shape, or listed in its table with a class and a reason.

    `--check` runs on its own, not only through the report: if docs/reviews/ were
    emptied, the citation half would have nothing to check and the baseline would
    silently stop being enforced.

    Hard: the fix is `--write-block` plus a deliberate baseline edit, and the
    reader of a stale number is a decision-maker quoting it.
    """
    base = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "audit_agents_md.py"), "--check"],
        capture_output=True, text=True, check=False,
    )
    if base.returncode == 1:
        FAILS.append(
            "audit_agents_md.py --check: AGENTS.md no longer matches the recorded "
            "baseline (update the report with --write-block, or the baseline "
            "deliberately)"
        )
    elif base.returncode != 0:
        FAILS.append(f"audit_agents_md.py --check errored (rc={base.returncode}): {base.stderr.strip()[:120]}")

    if not REVIEW_REPORTS:
        WARNS.append("docs/reviews/ holds no report — is the audit product lost?")
        return
    check_reviews_readme_rows()
    for report in REVIEW_REPORTS:
        out = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "audit_agents_md.py"),
             "--report-check", str(report)],
            capture_output=True, text=True, check=False,
        )
        if out.returncode == 1:
            FAILS.append(f"{report.relative_to(ROOT)}: {first_meaningful_line(out.stderr, report)}")
        elif out.returncode != 0:
            FAILS.append(
                f"audit_agents_md.py --report-check errored on "
                f"{report.relative_to(ROOT)} (rc={out.returncode}): {out.stderr.strip()[:120]}"
            )
        prose = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "audit_prose_numbers.py"),
             "--check", str(report)],
            capture_output=True, text=True, check=False,
        )
        if prose.returncode == 1:
            FAILS.append(
                f"{report.relative_to(ROOT)}: "
                f"{first_meaningful_line(prose.stderr, report)}"
            )
        elif prose.returncode != 0:
            FAILS.append(
                f"audit_prose_numbers.py --check errored on "
                f"{report.relative_to(ROOT)} (rc={prose.returncode}): "
                f"{prose.stderr.strip()[:120]}"
            )


def check_r14_session_memory_fresh() -> None:
    """The session-memory index covers the sessions on disk.

    The failure is silent and expensive: an index that missed yesterday's
    sessions answers "nobody has ever hit this" with total confidence, and the
    agent that believes it invents a fix that was already tried and rejected. A
    configured check nobody re-derives is exactly the thing this repo keeps
    catching, so `memory_index.py freshness` re-reads the newest session date
    from the six agent stores and compares it with the newest indexed one.

    Degrades only where there is genuinely nothing to check: no index and no
    sessions on disk is OK (a fresh clone), no index with sessions present is a
    FAIL naming the fix, and the 24h lag tolerance keeps the session currently
    being written from failing every commit.

    An index that exists but that this interpreter cannot compare against a
    single agent store is also a FAIL. It used to print `OK — no agent stores
    readable` and exit 0, which is the exact failure this rule exists to stop:
    a green line in the gate output that verified nothing, produced whenever
    the gate runs under the WSL `python3` instead of `python.exe`. Silence
    about not knowing is the one thing this check may never report.
    """
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "memory_index.py"), "freshness"],
        capture_output=True, text=True, check=False,
    )
    message = (out.stdout or out.stderr).strip()
    if out.returncode == 1:
        FAILS.append(f"memory_index.py freshness: {message}")
    elif out.returncode != 0:
        FAILS.append(
            f"memory_index.py freshness errored (rc={out.returncode}): {message[:160]}"
        )
    elif message.startswith("OK"):
        print(f"  - {message}")


def check_r15_session_memory_eval() -> None:
    """Run the checked-in retrieval benchmark so it cannot become write-only."""
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "eval_memory_retrieval.py"), "--limit", "5"],
        capture_output=True, text=True, check=False,
    )
    message = (out.stdout or out.stderr).strip()
    if out.returncode != 0:
        FAILS.append(f"memory retrieval eval: {message[-300:]}")
    else:
        summary = next((line for line in message.splitlines() if line.startswith("retrieval_eval:")), message)
        print(f"  - {summary}")


def check_r16_session_memory_usage() -> None:
    """Advisory: a recent edit to the gate's own machinery should leave a
    session-memory usage trace.

    A commit touching `scripts/**`, `hooks/**`, `skills/**`, or `.dsh/**`
    within the last 30 minutes is expected to have queried the workspace's
    recorded past (the debug-with-memory door) — leaving a fresh entry in
    `scripts/_scratch/sessions/05_store/queries.jsonl` — or to have mentioned the
    word `query` in its subject (a substring check, not a verified
    `query "..."` citation). Neither present => the visit to the door was
    skipped; flag it so the absence is measurable instead of silent.

    `.dsh/` is a forward-looking target: the DSH store lives at `~/.dsh`,
    outside this repo, so no such commit can exist today and that pathspec
    is inert; it fires only if a local `.dsh/` directory ever appears.

    Warns, never blocks: this check only ever appends to WARNS, and
    degrades to silence where there is nothing to compare (no matching
    commit, or git itself fails).
    """
    import json
    import time
    from datetime import datetime

    # `.dsh/` is a forward-looking pathspec (see docstring): inert today,
    # fires only if a local `.dsh/` directory ever appears in this repo.
    out = subprocess.run(
        ["git", "log", "-1", "--pretty=format:%ct%x00%s", "--",
         "scripts/", "hooks/", "skills/", ".dsh/"],
        capture_output=True, text=True, check=False, cwd=str(ROOT),
    )
    if out.returncode != 0 or not out.stdout.strip():
        return  # not a git checkout, or no commit touches the target paths
    commit_ts, sep, subject = out.stdout.partition("\x00")
    if not sep:
        return
    try:
        commit_epoch = int(commit_ts)
    except ValueError:
        return
    if time.time() - commit_epoch > 1800:
        return  # the matching commit is older than the window: out of scope
    if "query" in subject.lower():
        # Substring match: the subject merely mentions "query"; this is not
        # a verified `query "..."` citation (see docstring). Satisfied on mention.
        return
    telemetry = ROOT / "scripts" / "_scratch" / "sessions" / "05_store" / "queries.jsonl"
    try:
        lines = [ln for ln in telemetry.read_text(encoding="utf-8").splitlines() if ln.strip()]
        entry_epoch = datetime.fromisoformat(json.loads(lines[-1])["timestamp"]).timestamp()
        if time.time() - entry_epoch <= 1800:
            return  # a fresh usage trace exists: satisfied
    except Exception:
        pass  # no telemetry file / unreadable last entry: no trace to verify
    WARNS.append(
        "R16 session-memory usage: the latest commit touching "
        "scripts/**/hooks/**/skills/**/.dsh/** (last 30 min) left no fresh "
        "queries.jsonl trace and no mention of `query` in its subject — "
        "the door (debug-with-memory) was not visited"
    )


def check_r17_hookspath_enforced() -> None:
    """R17 (hard): the pre-commit hook must be installed in this clone.

    `hooks/pre-commit` rebuilds the generated views and runs this gate, but
    `core.hooksPath` is a per-clone setting — a fresh clone that never ran
    `git config core.hooksPath hooks` commits without any gate, and every
    hard check above degrades to documentation. FAIL names the one-command
    fix instead of letting the gate pass silently unenforced.
    """
    out = subprocess.run(
        ["git", "config", "core.hooksPath"],
        capture_output=True, text=True, check=False, cwd=str(ROOT),
    )
    if out.returncode != 0 or out.stdout.strip() != "hooks":
        FAILS.append(
            "core.hooksPath is not `hooks` — the pre-commit gate has no "
            "automatic caller in this clone; run "
            "`git config core.hooksPath hooks`"
        )


GOVERNANCE_PREFIXES = ("handoff/", "HANDOFF.md", "STATE.md", "docs/")


def _r18_pending_decisions(
    text: str, today: "datetime.date"
) -> list[tuple[str, int | None, str, str, str | None]]:
    """Every `- id:` entry whose own body carries PENDING_IMPLEMENTATION.

    An entry starts at `- id:` and ends at the first blank line. Closing prose
    after the last entry is NOT entry content — S84a: it used to be, which made
    R18 flag a `status: WYKONANE` entry (D-04) because the closing prose merely
    *mentioned* the word. The 3d/14d thresholds are unchanged; only the scope
    of one entry changes.

    Returns (fid, age_days_or_None, entry_text, reason, raw_date).
    reason: "no_date" | "bad_date" | None. `None` age means either reason;
    raw_date is the `zapisano:` string (used verbatim in the messages) or None.
    """
    import datetime

    out: list[tuple[str, int | None, str, str, str | None]] = []
    for seg in re.split(r"(?m)^- id:\s*", text)[1:]:
        entry = seg.split("\n\n", 1)[0]  # S84a: scope to the first blank line
        if "PENDING_IMPLEMENTATION" not in entry:
            continue
        mid = re.search(r"(D-\S+)", entry)
        fid = mid.group(1) if mid else "?"
        dm = re.search(r"zapisano:\s*(\d{4}-\d{2}-\d{2})", entry)
        if not dm:
            out.append((fid, None, entry, "no_date", None))
            continue
        raw_date = dm.group(1)
        try:
            age = (today - datetime.date.fromisoformat(raw_date)).days
        except ValueError:
            out.append((fid, None, entry, "bad_date", raw_date))
        else:
            out.append((fid, age, entry, None, raw_date))
    return out


def check_r18_governance_streak() -> None:
    """R18 (advisory): >=3 consecutive governance-only HEAD commits.

    A commit that touches only `handoff/`, `HANDOFF.md`, `STATE.md` or
    `docs/` with no `projects/` change is governance, not research. One is
    routine; three in a row without a project commit means sessions spin on
    documentation while the decision they recorded stays unimplemented.
    Warns, never blocks.
    """
    out = subprocess.run(
        ["git", "log", "-5", "--pretty=format:COMMIT:%H", "--name-only"],
        capture_output=True, text=True, check=False, cwd=str(ROOT),
    )
    if out.returncode != 0 or not out.stdout.strip():
        return
    streak = 0
    current: list[str] | None = None
    commits: list[list[str]] = []
    for line in out.stdout.splitlines():
        if line.startswith("COMMIT:"):
            if current is not None:
                commits.append(current)
            current = []
        elif current is not None and line.strip():
            current.append(line.strip())
    if current is not None:
        commits.append(current)
    for files in commits:
        if not files:
            break  # empty commit (e.g. merge): stop counting, do not guess
        is_governance = all(
            any(f == g.rstrip("/") or f.startswith(g) for g in GOVERNANCE_PREFIXES)
            for f in files
        )
        touches_work = any(
            f.startswith("projects/") or f.startswith("scripts/") or f == "SCARS.md"
            for f in files
        )
        if is_governance and not touches_work:
            streak += 1
        else:
            break
    if streak >= 3:
        WARNS.append(
            f"R18 governance streak: last {streak} commits are governance-only "
            f"(handoff/HANDOFF/STATE/docs, no projects/ change) — "
            f"brak postepu badawczego; check session-decision.md for PENDING"
        )

    # Second half (hard): PENDING_IMPLEMENTATION older than 3 days fails.
    # A decision file in the new executor/status format carries
    # `zapisano: YYYY-MM-DD` + `status: PENDING_IMPLEMENTATION` per entry.
    import datetime as _dt

    decision = ROOT / "handoff" / "flags" / "session-decision.md"
    if decision.is_file():
        try:
            dtext = decision.read_text(encoding="utf-8", errors="replace")
        except OSError:
            dtext = ""
        if "PENDING_IMPLEMENTATION" in dtext:
            today = _dt.date.today()
            for fid, age, entry, reason, raw in _r18_pending_decisions(
                dtext, today
            ):
                if reason == "no_date":
                    FAILS.append(
                        f"R18: decision {fid} is PENDING_IMPLEMENTATION with "
                        f"no `zapisano:` date — every pending decision needs "
                        f"an executor and a date (session-decision.md)"
                    )
                    continue
                if reason == "bad_date":
                    FAILS.append(
                        f"R18: decision {fid} has unparseable date "
                        f"`{raw}`"
                    )
                    continue
                if age > 14:
                    FAILS.append(
                        f"R18: decision {fid} PENDING_IMPLEMENTATION for "
                        f"{age}d (since {raw}) — implement it or "
                        f"retire it; a recorded decision without an executor "
                        f"must not age out"
                    )
                elif age > 3:
                    WARNS.append(
                        f"R18: decision {fid} PENDING_IMPLEMENTATION for "
                        f"{age}d (since {raw}) — needs an executor; "
                        f"becomes a hard FAIL after 14d"
                    )


def check_r19_new_flag_provenance() -> None:
    """R19 (advisory): a newly added flag should be this session's state.

    A flag file that is untracked or staged-new but carries a `since:` date
    older than 3 days, or no `not checked:` line at all, is suspect: the
    8/10 and 9/10 sessions inflated `handoff/flags/` with retrospective
    flags documenting other sessions' older work. A flag is a record of the
    state its own session produced, not a summary of somebody else's.
    Warns, never blocks.
    """
    import datetime

    candidates: set[str] = set()
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=A"],
        capture_output=True, text=True, check=False, cwd=str(ROOT),
    )
    if out.returncode == 0:
        candidates.update(
            ln.strip() for ln in out.stdout.splitlines()
            if ln.strip().startswith("handoff/flags/") and ln.strip().endswith(".md")
        )
    out = subprocess.run(
        ["git", "status", "--short", "--", "handoff/flags/"],
        capture_output=True, text=True, check=False, cwd=str(ROOT),
    )
    if out.returncode == 0:
        for ln in out.stdout.splitlines():
            parts = ln.strip().split(None, 1)
            if len(parts) == 2 and parts[0] == "??" and parts[1].endswith(".md"):
                candidates.add(parts[1].strip('"'))
    today = datetime.date.today()
    for rel in sorted(candidates):
        path = ROOT / rel
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        m = re.search(r"^since:\s*(\d{4}-\d{2}-\d{2})\s*$", text, re.M)
        if m:
            try:
                age = (today - datetime.date.fromisoformat(m.group(1))).days
            except ValueError:
                age = 0
            if age > 3:
                WARNS.append(
                    f"R19 SUSPECTED_RETROSPECTIVE: new flag `{rel}` carries "
                    f"since {m.group(1)} ({age}d ago) — a flag should record "
                    f"this session's state, not older work"
                )
        else:
            WARNS.append(
                f"R19 SUSPECTED_RETROSPECTIVE: new flag `{rel}` has no "
                f"`since:` date — flag schema requires one (handoff/CONTEXT.md)"
            )
        if not re.search(r"^not checked:", text, re.M | re.I):
            WARNS.append(
                f"R19: new flag `{rel}` has no `not checked:` line — "
                f"negative space stays invisible unless the flag names it "
                f"(scripts/close.py enforces this on close)"
            )
        check_r19_flag_has_commit(rel, m.group(1) if m else None)


TOPIC_STOP = {"flag", "handoff", "session", "sesja", "with", "from", "fixed"}


def check_r19_flag_has_commit(rel: str, since: str | None) -> None:
    """R19 (advisory): a new flag should have a commit about its topic.

    The 8/10 and 9/10 pattern was not a shared stem — it was a flag
    describing somebody else's work with no commit behind it. For a newly
    added flag with a fresh `since:` date, search `git log
    --since=<since>` subjects for the flag stem's topic tokens. No match
    warns as flag-without-commit: the flag may document work this session
    never committed. Warns, never blocks.
    """
    if not since:
        return
    stem = Path(rel).stem
    tokens = {
        t.lower() for t in re.split(r"[-_]+", stem)
        if len(t) > 3 and t.lower() not in TOPIC_STOP
    }
    if not tokens:
        return
    out = subprocess.run(
        ["git", "log", f"--since={since}", "--format=%s", "--", "handoff/"],
        capture_output=True, text=True, check=False, cwd=str(ROOT),
    )
    if out.returncode != 0:
        return
    subjects = out.stdout.lower()
    if not any(tok in subjects for tok in tokens):
        WARNS.append(
            f"R19 flag-without-commit: new flag `{rel}` (since {since}) has "
            f"no commit in `git log --since={since}` about its topic "
            f"({', '.join(sorted(tokens))}) — it may document somebody "
            f"else's work instead of this session's state"
        )


def check_r20_scars_duplicates() -> None:
    """R20: SCARS.md must not contain duplicate ## S<number> headings."""
    scars_path = ROOT / "SCARS.md"
    if not scars_path.is_file():
        return
    text = scars_path.read_text(encoding="utf-8", errors="replace")
    seen = {}
    for m in re.finditer(r"^##\s+(S[0-9]+)", text, re.M):
        s_id = m.group(1)
        seen[s_id] = seen.get(s_id, 0) + 1
    dups = [s for s, count in seen.items() if count > 1]
    if dups:
        FAILS.append(f"R20 SCARS.md has duplicate entries: {', '.join(dups)}")


def check_r21_brain_layer_current() -> None:
    """R21 (hard): the curated brain layer is the parse of its sources, un-regressed.

    Two questions, one check, because a layer that stopped holding a scar is the
    same failure whether the row vanished or drifted: `ingest_brain.py --check`
    compares every source row (SCARS.md scar, DECISIONS.md decision, lesson) with
    the row in `brain.db` by fingerprint, so a scar removed, renamed or never
    parsed is named explicitly. Then the checked-in evaluation must be at or above
    its baseline — a gate on freshness alone would go green on a layer that keeps
    every row and retrieves none of them.

    `brain.db` is gitignored, so a fresh clone has none; that warns with the
    rebuild command instead of failing, which is the only degradation here. A
    database that exists is never exempt, because "I cannot compare" is the one
    answer this check may not give silently.
    """
    db = ROOT / "brain" / "brain.db"
    if not db.is_file():
        WARNS.append(
            "R21 brain layer: no brain/brain.db in this clone — the curated layer "
            "is not built (it is a gitignored derived artifact). "
            "Fix: python.exe scripts/ingest_brain.py"
        )
        return

    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "ingest_brain.py"), "--check"],
        capture_output=True, text=True, check=False,
    )
    message = (out.stdout or out.stderr).strip()
    if out.returncode != 0:
        FAILS.append(f"R21 brain layer is not the parse of its sources:\n{message}")
        return
    print("  - " + message.splitlines()[-1])

    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "memory" / "eval_brain.py"), "--check"],
        capture_output=True, text=True, check=False,
    )
    message = (out.stdout or out.stderr).strip()
    if out.returncode != 0:
        FAILS.append(f"R21 brain retrieval eval: {message[-400:]}")
        return
    summary = next(
        (line for line in message.splitlines() if line.startswith("brain_eval:")),
        message.splitlines()[-1] if message else "",
    )
    print(f"  - {summary}")


def check_r22_store_schema_drift() -> None:
    """R22 (advisory): no agent store silently dropped sessions (S68 shape).

    `scripts/memory_index_check_drift.py --check --drift-only` asks one question
    per store: does a store that *holds records on disk* read as empty (a silent
    loader skip), or have its expected tables vanished? Those are the S68 shape.
    It deliberately does not fail on the "newest session is indexed" condition —
    that lights up on ordinary staleness (a session created after the last ingest),
    which R14 already gates, and including it would make this advisory shine on
    almost every close. The full assertion, membership and all, is the hard caller
    `memory_index.py ingest`, which exits 1 on it. A store absent from this clone
    is skipped; there is nothing to drift.
    """
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "memory_index_check_drift.py"),
         "--check", "--drift-only"],
        capture_output=True, text=True, check=False, timeout=120,
    )
    message = (out.stdout or out.stderr).strip()
    if out.returncode != 0:
        last = message.splitlines()[-1] if message else "check errored"
        WARNS.append(
            f"R22 store schema drift — {last} "
            f"(run scripts/memory_index_check_drift.py --check)"
        )
    else:
        print(f"  - {message.splitlines()[-1] if message else 'no drift'}")


def check_r23_flag_model_contract() -> None:
    """R23 (hard): no flag with since >= 2026-10-17 may use `model: current` or `model: default`.
    R24 (advisory): a flag whose `model:` lacks `/` is a nickname, not a real
    provider/model-id. The contract requires `provider/model-id` so provenance
    survives session handoffs (E4 / B12)."""
    flag_dir = ROOT / "handoff" / "flags"
    if not flag_dir.is_dir():
        return
    frontmatter_rx = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    model_rx = re.compile(r"^model:\s*(.+)$", re.MULTILINE)
    since_rx = re.compile(r"^since:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", re.MULTILINE)
    for path in sorted(flag_dir.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for fm in frontmatter_rx.finditer(text):
            fm_text = fm.group(1)
            s_match = since_rx.search(fm_text)
            if s_match and s_match.group(1) < "2026-10-17":
                continue
            m = model_rx.search(fm_text)
            if not m:
                continue
            model = m.group(1).strip()
            rel = path.relative_to(ROOT)
            if model in {"current", "default"}:
                FAILS.append(f"{rel}: model: {model} — use `provider/model-id`")
            elif "/" not in model:
                WARNS.append(f"{rel}: model: {model} — expected `provider/model-id`")



def main() -> int:
    check_r1_root_shape()
    check_r2_reference_integrity()
    check_r3_hygiene()
    check_r4_grade_declared()
    check_r5_open_work()
    check_r6_skills_home()
    check_r7_map_current()
    check_r9_routing_targets()
    check_r10_open_work_integrity()
    check_r11_skills_catalog()
    check_r12_handoff_view_current()
    check_r24_status_view_current()
    check_r13_report_citations()
    check_r14_session_memory_fresh()
    check_r15_session_memory_eval()
    check_r16_session_memory_usage()
    check_r17_hookspath_enforced()
    check_r18_governance_streak()
    check_r19_new_flag_provenance()
    check_r20_scars_duplicates()
    check_r21_brain_layer_current()
    check_r22_store_schema_drift()
    check_r23_flag_model_contract()
    for msg in WARNS:
        print(f"  - {msg}")
    if FAILS:
        print("WORKSPACE INTEGRITY FAIL:")
        for msg in FAILS:
            print(f"  - {msg}")
        print(
            "\nFix the data the check named above. If it is a new root-level\n"
            "entry, declare it in CLAUDE.md and ALLOWED_ROOT in the same change;\n"
            "if it is shell debris, delete it. Do not widen a check to silence it."
        )
        return 1
    print(
        f"OK: workspace root holds {len(ALLOWED_ROOT - {'__pycache__', 'scripts'})} declared entries, "
        f"{len(PROJECTS)} projects, all routing links resolve"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
