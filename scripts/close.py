#!/usr/bin/env python3
"""Close a root-workspace session as one transaction: flag -> views -> gate -> commit.

The closing ritual used to be six separate commands (write flag,
build_handoff, build_state, integrity gate, diff --check, commit), and the
gate only fired at the end — so a skipped step surfaced at commit time, or
never when the commit never happened. This script couples the steps: either
everything lands in one commit, or nothing is committed and the script says
which step failed.

Usage:
    python.exe scripts/close.py --flag <id> --model <provider/model-id>
        (--body "..." | --body-file <path>)
        [--since YYYY-MM-DD] [--owner ROLE] [--agent NAME] [--origin WHERE]
        [--include <path> ...] [--correct]

The commit contains exactly: the new flag file, the two rebuilt views
(HANDOFF.md, STATE.md), plus whatever --include lists (the work being
closed). Any other dirty tracked file fails the run with "commit or stash
your work first, or pass it via --include" — a close must not silently
leave half a session behind, and must not silently sweep unrelated work
into its commit either.

On any failure the script exits 1 and leaves the written files on disk
(the flag prose is real work; deleting it would be worse than leaving it
uncommitted). "Almost closed" still has no commit, so the next session
sees the same gate, not a stale view.

Notes:
- --body-file beats --body (Windows quoting scars: write a file, execute it).
- --model takes the real provider/model id, never a nickname (flag contract).
- R16 advisory: if the closed work touched scripts/**, hooks/**,
  skills/** or .dsh/**, record a memory query first
  (scripts/memory/CONTEXT.md) — otherwise expect a non-blocking R16 WARN
  on the close commit. This script does not fake the trace.
- The flag body must contain a `not checked:` line naming what was NOT
  verified (may be `not checked: —`). Negative space is invisible by
  default; the ritual forces it into the flag instead of leaving it for
  the reviewer to find.
- `--verify-claims` (E6, decision B3) re-derives the flag body's claims that
  have an *executable artifact*: a `commit <hash>` must exist in the root repo
  or in a nested projects/ repo; a counter that names its artifact
  (`handoff/flags/`, `brain.db`) must match the recomputed value; a bare gate
  claim is already enforced by this transaction's own `integrity` step, so it
  is reported rather than re-run a second time (96 s measured).
  `--dry-run --verify-claims` exits 1 on a contradicted claim; a real close
  only WARNs, so verification can never block a session close on a false
  positive (B3). Narration and artifact-less counters are reported, never
  silently passed — a gate that cannot fail is documentation (S56/S62).
- Known gaps (candidates, not bugs): no `--amend` mode — fixing a flag
  means retire + full re-close, so a close with corrections costs 2+
  commits. Deliberate: re-running the transaction is safer than patching
  a commit, but the history noise is real.
- `--correct` (S86 fix 2026-10-18): edit an existing committed flag in place
  (overwrite flag file, rebuild views, gate, commit) with the same transaction
  guarantees as a normal close. Without it, correcting a committed flag
  required manual `.commit-approved` minting + `git commit` — a bypass of the
  mechanism that exists to ensure no commit lands without rebuilt views and a
  green gate.
- Stdlib only.
"""
from __future__ import annotations

import argparse
import datetime
import re
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(Path(__file__).resolve().parent))
from git_paths import repo_prefix, repo_rel  # noqa: E402
FLAGS = ROOT / "handoff" / "flags"
HANDOFF = ROOT / "HANDOFF.md"
STATE = ROOT / "STATE.md"
STATUS_MD = ROOT / "handoff" / "status" / "STATUS.md"
INDEX_MD = ROOT / "handoff" / "flags" / "INDEX.md"
# The generated views close.py rebuilds, stages, and must never treat as a
# stray. INDEX.md belongs here too (S81): build_handoff.py regenerates it
# alongside HANDOFF.md, so leaving it out forced every close to pass
# `--include handoff/flags/INDEX.md`.
GENERATED_VIEWS = (HANDOFF.relative_to(ROOT).as_posix(),
                   STATE.relative_to(ROOT).as_posix(),
                   INDEX_MD.relative_to(ROOT).as_posix(),
                   STATUS_MD.relative_to(ROOT).as_posix())
BUILD_HANDOFF = ROOT / "scripts" / "build_handoff.py"
BUILD_STATE = ROOT / "scripts" / "build_state.py"
BUILD_STATUS = ROOT / "scripts" / "build_status.py"
GATE = ROOT / "scripts" / "check_workspace_integrity.py"
# Option A (2026-10-15): the token hooks/pre-commit's commit_gate_guard looks
# for. Path must match commit_gate_guard.APPROVAL_TOKEN.
APPROVAL_TOKEN = ROOT / ".commit-approved"

FLAG_RX = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
BLOKADA_RX = re.compile(r"^(?:BLOKADA:|## .*BLOKADA|status:\s*BLOKADA)", re.MULTILINE)
NOTCHECKED_RX = re.compile(r"^not checked:", re.MULTILINE)
PY = sys.executable

# S66 fix (2026-10-16, from residue-closeout 1f5e81c): a diff-check FAIL is the
# repair list, so it must never be truncated. Every other step keeps a short
# tail but names the command that shows the rest.
FULL_OUTPUT_STEPS = {"diff-check", "dry-diff-check"}
OUTPUT_TAIL = 8


def check_body(flag: str, body: str) -> str | None:
    """Return an error string when the body breaks the flag entry shape."""
    if not body:
        return "flag body is empty"
    if not body.startswith(f"`{flag}`"):
        return (f"body must start with `` `{flag}` `` — "
                "entry shape: `flag` — YYYY-MM-DD: state + next step")
    if not NOTCHECKED_RX.search(body):
        return ("body must contain a `not checked:` line naming what was NOT "
                "verified (may be `not checked: —`) — negative space stays "
                "invisible unless the ritual forces it into the flag")
    return None


def check_model(model: str) -> str | None:
    """Return an error string when `model` is not a real provider/model-id.

    The flag contract requires `provider/model-id` (with `/`). Nicknames and
    placeholders (`current`, `default`) break provenance: a later session cannot
    tell which model produced the claim. E4 enforces this at the close gate so
    the transaction itself never writes an invalid `model:` line.
    """
    if "/" not in model:
        return ("`--model` must be `provider/model-id` (with `/`); "
                "nicknames and placeholders like `current`/`default` are not allowed")
    return None


# --- --verify-claims (E6, decision B3 2026-10-16) ---------------------------
# Flag prose drifts exactly like a stale MAP: the body says `commit abc1234` or
# `162 plików`, a week later the claim is false and nothing sees it. Measured
# over the 168 flags in handoff/flags/: 33 bodies carry commit hashes, 60 carry
# counters, 12 carry exit-0 claims — a class, not an edge case. --verify-claims
# re-derives the subset that has an *executable artifact* (a command recomputes
# it) and reports the rest instead of guessing.
CLAIM_COMMIT_RX = re.compile(r"\bcommit\w*\s+`?([0-9a-f]{7,40})`?", re.IGNORECASE)
# Counter units are matched by stem + any suffix so an ASCII-transliterated
# body ("plikow", "flagow") is reported as an unverifiable claim instead of
# being skipped in silence — a claim nobody looks at is the failure mode.
CLAIM_COUNTER_RX = re.compile(
    r"\b(\d+)\s+((?:plik|flag|file|wiersz|rows?|problem|scar|decyzj|"
    r"decisions?|lekcj|lessons?|sesj|sessions?|tabel|tables?|cases?)\w*)\b",
    re.IGNORECASE)
CLAIM_EXIT0_RX = re.compile(r"exit\s*=?\s*0|EXIT\s*=?\s*0|bramk\w*\s+zielon\w*",
                            re.IGNORECASE)
GATE_NOUN_RX = re.compile(
    r"\b(bramk\w*|gate|integrity|check_workspace_integrity)\b", re.IGNORECASE)
# Clause breaks: `;`, newline, and a sentence-ending dot. A dot inside a
# token (`brain.db`, `SCARS.md`, `close.py`) is not a break — splitting there
# hid the artifact named later in the same sentence.
CLAUSE_BREAK_RX = re.compile(r";|\n|\.(?=\s|$)")
# A counter that describes a change ("22 flagi → one-file-per-flag", "było 161")
# is a historical statement, not a present-tense count: re-deriving it against
# today's artifact reports a drift that was never a lie. Those stay WARNs.
TRANSITION_RX = re.compile(r"→|->|=>|\b(był\w*|was|were|before|przed)\b",
                           re.IGNORECASE)
# A counter in a clause that cites a commit describes *that commit* ("root w
# `e61d8c8` (41 plików, +1881/-179)"), not the current worktree — re-deriving
# it against today's artifact reports a drift that was never a lie.
COMMIT_CITE_RX = re.compile(r"`[0-9a-f]{7,40}`|\bcommit\w*\s+`?[0-9a-f]{7,40}",
                            re.IGNORECASE)


class ClaimsReport(NamedTuple):
    findings: list[str]   # `FAIL: ...` contradicted, `WARN: ...` not re-derived
    re_derived: int       # claims actually recomputed against an artifact
    gate_covered: int     # gate claims enforced by the transaction's own gate


def nested_repos(root: Path) -> list[Path]:
    """Git repos nested under projects/ — own history, own commit objects.

    A flag written during a knowledge-retrieval session cites a KR commit hash;
    that object does not exist in the root repo. Re-deriving hashes against the
    root alone reports a false divergence on 14 of the 33 commit claims in the
    current corpus, so resolution is root-first, then nested.
    """
    base = root / "projects"
    if not base.is_dir():
        return []
    seen: set[Path] = set()
    found: list[Path] = []
    for pattern in ("*/*", "*/*/*"):
        for cand in sorted(base.glob(pattern)):
            if cand in seen or not cand.is_dir():
                continue
            seen.add(cand)
            if (cand / ".git").exists():
                found.append(cand)
    return found


def _commit_repo(root: Path, rev: str, repos: list[Path] | None = None) -> Path | None:
    """First repo holding `rev` as a commit — root first, then nested repos."""
    if repos is None:
        repos = nested_repos(root)
    for repo in [root, *repos]:
        if subprocess.run(["git", "cat-file", "-e", f"{rev}^{{commit}}"],
                          capture_output=True, cwd=str(repo)).returncode == 0:
            return repo
    return None


def _count_flag_files(root: Path) -> int:
    return len([p for p in (root / "handoff" / "flags").glob("*.md") if p.is_file()])


def _db_count(root: Path, table: str) -> int | None:
    """Rows in a brain.db table; None when the db or the table is absent."""
    db = root / "brain" / "brain.db"
    if not db.is_file():
        return None
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        return con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    except sqlite3.Error:
        return None
    finally:
        con.close()


def _clause_around(body: str, pos: int) -> str:
    """The clause containing `pos` — a claim is scoped to its own statement.

    A fixed character window bleeds across clause boundaries: "(9 plików z
    eval/); untracked ... i handoff/flags/..." made a count of eval/ files look
    like a claim about the flag directory. The artifact has to be named in the
    same clause as the number, or the claim is not re-derived.
    """
    left = 0
    for m in CLAUSE_BREAK_RX.finditer(body, 0, pos):
        left = m.end()
    nxt = CLAUSE_BREAK_RX.search(body, pos)
    right = nxt.start() if nxt else len(body)
    return body[left:right]


def _counter_artifact(root: Path, unit: str,
                      clause: str) -> tuple[str, int] | None:
    """Map `<N> <unit>` to a recomputable artifact, when the claim names one.

    Naming is the whole test: `162 plików` names nothing, so no command
    recomputes it — that is the B3 WARN case, not a FAIL. `168 plików w
    handoff/flags/` names the directory, so the count is re-derivable and a
    divergence can fail the gate. The artifact must be named in the same
    clause as the number (`_clause_around`).
    """
    u = unit.lower()
    low = clause.lower()
    if u.startswith(("flag", "plik", "file")):
        if "handoff/flags" not in low:
            return None
        return ("handoff/flags/*.md", _count_flag_files(root))
    if u.startswith(("problem", "scar")):
        if "brain.db" not in low and "scars.md" not in low:
            return None
        n = _db_count(root, "problems")
        return None if n is None else ("brain.db:problems", n)
    if u.startswith(("decyzj", "decision")):
        if "brain.db" not in low:
            return None
        n = _db_count(root, "decisions")
        return None if n is None else ("brain.db:decisions", n)
    if u.startswith(("lekcj", "lesson")):
        if "brain.db" not in low and "lessons.md" not in low:
            return None
        n = _db_count(root, "lessons")
        return None if n is None else ("brain.db:lessons", n)
    return None


def verify_claims(body: str, root: Path = ROOT,
                  repos: list[Path] | None = None) -> ClaimsReport:
    """Re-derive the flag body's claims that have an executable artifact (B3).

    FAIL means the artifact contradicts the claim; WARN means there was no
    artifact to re-derive from, which is reported rather than passed silently.
    A narrative claim ("system działa", "rozstrzygnięto X") yields nothing —
    there is no command that recomputes a sentence, so a deterministic gate
    has nothing to fail on (S56/S62).
    """
    findings: list[str] = []
    re_derived = 0
    gate_covered = 0
    for m in CLAIM_COMMIT_RX.finditer(body):
        rev = m.group(1)
        re_derived += 1
        if _commit_repo(root, rev, repos) is None:
            findings.append(
                f"FAIL: claim `commit {rev}` — no such commit in the root repo "
                "or any nested projects/ repo")
    for m in CLAIM_COUNTER_RX.finditer(body):
        claimed, unit = int(m.group(1)), m.group(2)
        clause = _clause_around(body, m.start())
        artifact = _counter_artifact(root, unit, clause)
        if artifact is None:
            findings.append(f"WARN: counter claim `{claimed} {unit}` names no "
                            "recomputable artifact — not re-derived")
            continue
        label, actual = artifact
        if TRANSITION_RX.search(clause) or COMMIT_CITE_RX.search(clause):
            findings.append(f"WARN: counter claim `{claimed} {unit}` reads as a "
                            "historical change or a commit's own diff, not a "
                            "present-tense count — not re-derived")
            continue
        re_derived += 1
        if actual != claimed:
            findings.append(
                f"FAIL: claim `{claimed} {unit}` — {label} holds {actual}")
    for m in CLAIM_EXIT0_RX.finditer(body):
        if GATE_NOUN_RX.search(_clause_around(body, m.start())):
            # The transaction's own `integrity` step runs
            # check_workspace_integrity.py and aborts the close on non-zero, so
            # a false gate claim cannot be committed — re-running it here would
            # spend a second 96 s run for zero extra detection.
            gate_covered += 1
        else:
            findings.append("WARN: exit-0 claim names no re-derivable check "
                            "(only the workspace gate is re-derived) — not re-derived")
    return ClaimsReport(findings, re_derived, gate_covered)


def gate_note(rep: ClaimsReport) -> str:
    if not rep.gate_covered:
        return ""
    return (f"; {rep.gate_covered} gate claim(s) enforced by this transaction's "
            "own integrity step")


def render_flag(flag: str, since: str, owner: str, agent: str,
                model: str, origin: str, body: str) -> str:
    return (
        "---\n"
        f"flag: {flag}\n"
        f"since: {since}\n"
        f"owner: {owner}\n"
        f"agent: {agent}\n"
        f"model: {model}\n"
        f"origin: {origin}\n"
        "---\n"
        "\n"
        f"{body}\n"
    )


def fail(step: str, hint: str) -> int:
    print(f"close.py FAIL at [{step}]: {hint}")
    return 1


def format_failure(step: str, cmd: list[str], returncode: int, out: str) -> str:
    """Render a failed step; truncate only non-diff-check output (S66).

    The step name decides: a diff-check FAIL carries the list of violations to
    repair, so its full output is printed (S66: residue-closeout saw 3 of 13).
    Other steps keep the last OUTPUT_TAIL lines plus a pointer to the command.
    """
    joined = " ".join(cmd)
    body = out.strip()
    if not body:
        return f"command `{joined}` exited {returncode}\n(no output)"
    lines = body.splitlines()
    if step in FULL_OUTPUT_STEPS or len(lines) <= OUTPUT_TAIL:
        return f"command `{joined}` exited {returncode}\n{body}"
    hidden = len(lines) - OUTPUT_TAIL
    return (f"command `{joined}` exited {returncode}\n"
            + "\n".join(lines[-OUTPUT_TAIL:])
            + f"\n... ({hidden} more lines; run `{joined}` for full output)")


def run(step: str, cmd: list[str]) -> int | None:
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    if p.returncode != 0:
        return fail(step, format_failure(step, cmd, p.returncode, p.stdout + p.stderr))
    return None


def untracked_includes(includes: list[str]) -> list[str]:
    """--include paths that exist on disk but git does not track yet."""
    found: list[str] = []
    for i in includes:
        if not (ROOT / Path(i)).exists():
            continue
        rc = subprocess.run(["git", "ls-files", "--error-unmatch", i],
                            capture_output=True, cwd=str(ROOT)).returncode
        if rc != 0:
            found.append(Path(i).as_posix())
    return found


def _intent_to_add(includes: list[str]) -> list[str]:
    """S67 fix (2026-10-16, from residue-closeout 1f5e81c): make untracked
    --include paths visible to `git diff --check`. Returns the paths added, so
    a dry-run can undo the index change."""
    added = untracked_includes(includes)
    if added:
        subprocess.run(["git", "add", "--intent-to-add", "--", *added],
                       capture_output=True, cwd=str(ROOT))
    return added


def _unstage(paths: list[str]) -> None:
    if paths:
        subprocess.run(["git", "reset", "--", *paths],
                       capture_output=True, cwd=str(ROOT))


def load_body(a: argparse.Namespace) -> str | None:
    if a.body_file is not None:
        if not a.body_file.is_file():
            return None
        return a.body_file.read_text(encoding="utf-8").strip()
    return (a.body or "").strip()


def find_strays(root: Path, allowed: set[str]) -> list[str]:
    """Tracked worktree modifications outside the declared close set.

    `git status --short` prints paths relative to the REPO root, not to `root`
    (ADR-006: `root` is a subfolder of the repo). `repo_rel()` maps them back;
    a path outside `root` is a vault-level change and not this close's business.
    An `allowed` entry that names a directory allows everything under it, so
    `--include some/dir` covers the files it holds.
    """
    prefix = repo_prefix(root)
    p = subprocess.run(["git", "status", "--short"],
                       capture_output=True, text=True, cwd=str(root))
    strays: list[str] = []
    for line in p.stdout.splitlines():
        if not line.strip() or line.startswith("??"):
            continue
        rel = repo_rel(line[3:], prefix)
        if rel is None:
            continue
        if "." in allowed:  # `--include .`: the whole workspace is the change
            continue
        if rel in allowed or any(rel.startswith(a.rstrip("/") + "/") for a in allowed):
            continue
        strays.append(line)
    return strays


def explain() -> None:
    print("""close.py explanation & rules:
- close.py sam tworzy plik flagi przez --body-file
- nie twórz pliku flagi ręcznie
- commit message = <flag>: <first-line[:96]> + blank + FULL body (S60)
- brak --amend — poprawka flagi = retire + re-close
- --correct <flag> — korekta istniejącej flagi w miejscu (ten sam commit gate)
- --include nie działa z projects/research/... (zagnieżdżone repo)
- --verify-claims: re-derywuje twierdzenia z artefaktem (commit <hash>, licznik
  z nazwanym źródłem); --dry-run FAILuje na sprzeczności, close tylko WARN (B3)
""")
    sys.exit(0)


def _is_staged_deletion(path: str) -> bool:
    """True if `path` is staged for deletion (git rm), so it is a valid --include.

    `git diff --cached --name-only` prints repo-relative paths (ADR-006), so the
    comparison normalizes them to `ROOT`-relative before matching.
    """
    rel = Path(path).as_posix()
    r = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=D", "--", rel],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if r.returncode != 0:
        return False
    prefix = repo_prefix(ROOT)
    staged = {repo_rel(line, prefix) for line in r.stdout.splitlines() if line.strip()}
    return rel in staged


def _validate_correction_target(a: argparse.Namespace, flag_path: Path,
                                is_tracked_flag: bool) -> str | None:
    """Validate --correct: only tracked flags can be corrected in place."""
    if a.correct:
        if not is_tracked_flag:
            return "--correct requires an already-tracked flag"
        if flag_path.exists():
            return None
        return "--correct: flag file does not exist"
    if flag_path.exists() and is_tracked_flag:
        return "flag is already committed; use retire + re-close"
    if flag_path.exists():
        return (f"{flag_path.name} already exists — retire or delete it "
                "first; close never overwrites a claim")
    return None


def check_includes(includes: list[str]) -> str | None:
    """Every --include path must exist under ROOT, be tracked in git, or be a
    staged deletion (e.g. after `git rm`).

    `git rm` removes the file from both the worktree and the index, so neither
    `exists_on_disk` nor `is_tracked` holds — but the deletion is still staged
    and `git add`/commit in close.py will record it. Treat a staged deletion
    (status `D ` in `git status --porcelain`, equivalently present in
    `git diff --cached --diff-filter=D`) as a valid --include target.

    A **directory** is a valid target too: it passes `exists_on_disk` and
    `find_strays` matches its contents by prefix, so `--include some/dir` covers
    every file under it without expanding 686 paths into one command line.
    """
    for raw in includes:
        if "projects/research/" in raw or raw.startswith("projects/research/") or raw.startswith("projects\\research\\"):
            return f"--include projects/research/... is ignored by root .gitignore (nested repo); commit in KR instead: {raw}"
        exists_on_disk = (ROOT / Path(raw)).exists()
        is_tracked = subprocess.run(["git", "ls-files", "--error-unmatch", raw], capture_output=True, cwd=str(ROOT)).returncode == 0
        if not exists_on_disk and not is_tracked and not _is_staged_deletion(raw):
            return f"--include path is neither on disk nor tracked: {raw}"
    return None


def dry_run(a: argparse.Namespace) -> int:
    """Report whether a close would succeed, changing nothing on disk."""
    if not FLAG_RX.match(a.flag):
        return fail("validate", f"flag id `{a.flag}` must match {FLAG_RX.pattern}")
    if a.correct:
        flag_path = FLAGS / f"{a.flag}.md"
        is_tracked = subprocess.run(["git", "ls-files", "--error-unmatch", str(flag_path.relative_to(ROOT))], capture_output=True, cwd=str(ROOT)).returncode == 0
        if not is_tracked:
            return fail("validate", "--correct requires an already-tracked flag")
    elif (FLAGS / f"{a.flag}.md").exists():
        return fail("validate", "flag file already exists")
    if a.body_file is not None and not a.body_file.is_file():
        return fail("validate", f"--body-file not found: {a.body_file}")
    body = load_body(a)
    if body is None:
        return fail("validate", "cannot read body")
    body_err = check_body(a.flag, body)
    if body_err is not None:
        return fail("validate", body_err)
    model_err = check_model(a.model)
    if model_err is not None:
        return fail("validate", model_err)
    inc_err = check_includes(a.include)
    if inc_err is not None:
        return fail("validate", inc_err)
    if a.verify_claims:
        rep = verify_claims(body)
        contradicted = [f for f in rep.findings if f.startswith("FAIL")]
        if contradicted:
            return fail("verify-claims",
                        "flag body claims something the worktree contradicts "
                        "(B3: fail-loud in --dry-run):\n"
                        + "\n".join(f"  {f}" for f in contradicted))
        # WARNs are printed, not dropped: a claim with no artifact to re-derive
        # from must be *named*, or --verify-claims becomes a silent skip.
        for f in rep.findings:
            print(f"close.py WARNING: {f.split(': ', 1)[1]}")
        print(f"close.py: verify-claims OK — {rep.re_derived} claim(s) "
              f"re-derived, none contradicted{gate_note(rep)}")
    added = _intent_to_add(a.include)
    try:
        for step, cmd in (
            ("diff-check", ["git", "diff", "--check"]),
            ("handoff-check", [PY, str(BUILD_HANDOFF), "--check"]),
            ("integrity", [PY, str(GATE)]),
        ):
            rc = run(f"dry-{step}", cmd)
            if rc is not None:
                return rc
    finally:
        _unstage(added)
    allowed = {f"handoff/flags/{a.flag}.md", *GENERATED_VIEWS}
    allowed.update(Path(i).as_posix() for i in a.include)
    strays = find_strays(ROOT, allowed)
    if strays:
        return fail("dry-stage",
                    "a real close would stop on uncommitted tracked work:\n"
                    + "\n".join(f"  {s}" for s in strays[:10]))
    print("close.py: dry-run OK — a real close would proceed to write + commit")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="close.py")
    ap.add_argument("--explain", action="store_true", help="print explanation of close.py rules and exit")
    ap.add_argument("--flag", help="flag id; must match the filename stem")
    ap.add_argument("--model", help="real provider/model id, never a nickname")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--body", help="flag entry body (short only; prefer --body-file)")
    g.add_argument("--body-file", type=Path, help="file holding the flag entry body")
    ap.add_argument("--since", default=datetime.date.today().isoformat())
    ap.add_argument("--owner", default="mateusz", help="role allowed to edit this flag")
    ap.add_argument("--agent", default="opencode")
    ap.add_argument("--origin", default="session-close")
    ap.add_argument("--include", nargs="*", default=[],
                    help="extra worktree paths to include in the close commit")
    ap.add_argument("--dry-run", action="store_true",
                    help="validate + report closability without writing or committing")
    ap.add_argument("--correct", action="store_true",
                    help="correct an existing committed flag in place: overwrite the "
                         "flag file, rebuild views, gate, commit (same transaction "
                         "guarantees as a normal close)")
    ap.add_argument("--verify-claims", action="store_true",
                    help="re-derive the flag body's claims that have an "
                         "executable artifact (B3); --dry-run fails loud, "
                         "close only warns")
    a = ap.parse_args()
    if a.explain:
        explain()
    if not a.flag or not a.model:
        ap.error("--flag and --model are required unless --explain is passed")
    if a.dry_run:
        return dry_run(a)

    if not FLAG_RX.match(a.flag):
        return fail("validate", f"flag id `{a.flag}` must match {FLAG_RX.pattern}")
    flag_path = FLAGS / f"{a.flag}.md"
    is_tracked_flag = subprocess.run(["git", "ls-files", "--error-unmatch", str(flag_path.relative_to(ROOT))], capture_output=True, cwd=str(ROOT)).returncode == 0
    err = _validate_correction_target(a, flag_path, is_tracked_flag)
    if err:
        return fail("validate", err)

    body = load_body(a)
    if body is None:
        return fail("validate", f"--body-file not found: {a.body_file}")
    body_err = check_body(a.flag, body)
    if body_err is not None:
        return fail("validate", body_err)
    model_err = check_model(a.model)
    if model_err is not None:
        return fail("validate", model_err)
    if a.verify_claims:
        # B3: a real close WARNs, never blocks — verification must not be able
        # to strand a session over a false positive.
        rep = verify_claims(body)
        for f in rep.findings:
            msg = f.split(": ", 1)[1]
            if f.startswith("FAIL"):
                print(f"close.py WARNING: claim contradicted — {msg}")
            else:
                print(f"close.py WARNING: {msg}")
        contradicted = sum(1 for f in rep.findings if f.startswith("FAIL"))
        print(f"close.py: verify-claims — {rep.re_derived} claim(s) re-derived, "
              f"{contradicted} contradicted (WARN only in close, per B3)"
              f"{gate_note(rep)}")

    if BLOKADA_RX.search(body) and not body.startswith("`graphrag-trust-set-freeze`"):

        print("WARNING: flag contains BLOKADA — session is not a success")

    eval_dir = ROOT / "projects" / "research" / "knowledge-retrieval" / "pilots" / "graphrag" / "eval"
    if eval_dir.is_dir():
        tmps = list(eval_dir.glob("_tmp_*"))
        if tmps:
            print(f"WARNING: _tmp_* files present — remove them or list in not checked: {[t.name for t in tmps]}")
    inc_err = check_includes(a.include)
    if inc_err is not None:
        return fail("validate", inc_err)

    flag_text = render_flag(a.flag, a.since, a.owner, a.agent,
                            a.model, a.origin, body)
    flag_path.write_text(flag_text, encoding="utf-8", newline="\n")
    print(f"close.py: wrote {flag_path.relative_to(ROOT)}")

    # S67 fix (2026-10-16): stage untracked --include paths as intent-to-add so
    # the diff-check below sees them; the commit's `git add` fills them in.
    _intent_to_add(a.include)

    for step, cmd in (
        ("build-handoff", [PY, str(BUILD_HANDOFF)]),
        ("build-state", [PY, str(BUILD_STATE)]),
        ("build-status", [PY, str(BUILD_STATUS)]),
        ("diff-check", ["git", "diff", "--check"]),
        ("handoff-check", [PY, str(BUILD_HANDOFF), "--check"]),
        ("status-check", [PY, str(BUILD_STATUS), "--check"]),
        ("integrity", [PY, str(GATE)]),
    ):
        rc = run(step, cmd)
        if rc is not None:
            return rc
    print("close.py: views rebuilt, gate green")

    allowed = {flag_path.relative_to(ROOT).as_posix(), *GENERATED_VIEWS}
    allowed.update(Path(i).as_posix() for i in a.include)
    strays = find_strays(ROOT, allowed)
    if strays:
        return fail("stage",
                    "uncommitted tracked work outside this close:\n"
                    + "\n".join(f"  {s}" for s in strays[:10]) + "\n"
                    "commit or stash it first, or pass it via --include")
    add = [flag_path.relative_to(ROOT).as_posix(),
           *GENERATED_VIEWS]
    for i in a.include:
        rel_i = Path(i).as_posix()
        if not _is_staged_deletion(rel_i):
            add.append(rel_i)
    rc = run("stage", ["git", "add", "--", *add])
    if rc is not None:
        return rc

    # Option A (2026-10-15, owner decision): mint the commit-approval token so
    # hooks/pre-commit's commit_gate_guard authorizes THIS commit. Minted only
    # after every validation above and the integrity gate are green, and never
    # staged (.gitignore) — a leftover token is inert after 300 s, so it cannot
    # authorize a later session's commit.
    APPROVAL_TOKEN.write_text(
        f"approved by close.py for flag {a.flag}\n", encoding="utf-8", newline="\n")
    print(f"close.py: minted {APPROVAL_TOKEN.relative_to(ROOT)}")

    subject = f"{a.flag}: {body.splitlines()[0][:96]}"
    # S60 fix (2026-10-13): commit subject + blank + FULL body instead of
    # subject-only. Rationale: git tooling (log --oneline, R19 subject scans)
    # reads the first line, so the subject stays short; but `%B` must return
    # the full flag body, otherwise agents paste the flag prose into reports
    # and fabricate `git log` output. Standard git shape, no tooling breaks.
    message = f"{subject}\n\n{body}"
    rc = run("commit", ["git", "commit", "-m", message])
    if rc is not None:
        return rc
    if APPROVAL_TOKEN.exists():
        APPROVAL_TOKEN.unlink()
    print(f"close.py: committed `{a.flag}` — session closed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
