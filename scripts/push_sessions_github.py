#!/usr/bin/env python3
"""Publish the raw session export into a dedicated GitHub archive repo.

Vault's `.gitignore` refuses `**/raw_sessions.md` ("raw session exports may
contain secrets; never publish them"; the Vault remote is public). This script
therefore pushes the export into a SEPARATE, PRIVATE repo (default:
kamyczeczek/raw-sessions) — never into the workspace repo.

Single-writer model: the local clone under `scripts/_scratch/sessions-github/`
(gitignored) is the only writer, and every run fast-forwards it to the remote
before committing, so the archive always builds on the remote's state.

Repo resolution order:
    --repo URL  >  SESSIONS_GITHUB_REPO  >  DEFAULT_REPO

Before every commit the export is scanned by `scripts/scan_secrets.py`. A hit
aborts the push (exit 5): the same gate guards the workspace repo, and it is
never bypassed here.

Exit codes: 0 ok (including "nothing changed"), 2 repo unresolved, 3 source
missing, 4 git failure, 5 secrets found.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from scan_secrets import PATTERNS  # noqa: E402

DEFAULT_REPO = "https://github.com/kamyczeczek/raw-sessions.git"
CLONE_DIR = ROOT / "scripts" / "_scratch" / "sessions-github"
DEST_NAME = "raw_sessions.md"
SCANNER = ROOT / "scripts" / "scan_secrets.py"

EXIT_OK = 0
EXIT_REPO = 2
EXIT_SOURCE = 3
EXIT_GIT = 4
EXIT_SECRETS = 5


def fail(code: int, message: str) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)
    raise SystemExit(code)


def run(*args: str, cwd: Path | None = None, timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(
        args, capture_output=True, text=True, cwd=str(cwd) if cwd else None, timeout=timeout
    )


def git(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    cp = run("git", *args, cwd=cwd)
    if cp.returncode != 0:
        detail = (cp.stderr or cp.stdout or "").strip()
        fail(EXIT_GIT, f"git {' '.join(args)}: {detail}")
    return cp


def remote_default_branch(url: str) -> str | None:
    """Remote default branch from `ls-remote --symref`; None for an empty repo."""
    cp = run("git", "ls-remote", "--symref", url, "HEAD")
    if cp.returncode != 0:
        return None
    for line in cp.stdout.splitlines():
        if line.startswith("ref:"):
            return line.split()[1].removeprefix("refs/heads/")
    return None


def ensure_clone(url: str) -> tuple[Path, str]:
    """Clone-or-init the archive, then fast-forward it to the remote."""
    if CLONE_DIR.exists() and not (CLONE_DIR / ".git").is_dir():
        fail(
            EXIT_GIT,
            f"{CLONE_DIR} istnieje, ale nie jest repo git — usuń katalog i puść ponownie",
        )
    if not (CLONE_DIR / ".git").is_dir():
        clone = run("git", "clone", "--quiet", url, str(CLONE_DIR))
        if clone.returncode != 0:
            # A clone fails on a bad URL or missing credentials; an EMPTY repo
            # clones fine, so anything else is a resolution problem.
            fail(
                EXIT_REPO,
                f"nie można sklonować {url}: {(clone.stderr or clone.stdout or '').strip()}",
            )
    branch = remote_default_branch(url)
    if branch is None:
        branch = "master"  # empty repo: unborn HEAD, we name the branch
    else:
        run("git", "fetch", "--quiet", "origin", cwd=CLONE_DIR)
        # -B resets any stray local state (documented single-writer behaviour).
        git(["checkout", "--quiet", "-B", branch, "FETCH_HEAD"], cwd=CLONE_DIR)
    return CLONE_DIR, branch


def sanitize_file(dest: Path) -> int:
    """Sanitize secrets using PATTERNS from scan_secrets.py."""
    if not dest.is_file():
        return 0
    try:
        text = dest.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return 0

    count = 0
    for name, rx in PATTERNS:
        matches = rx.findall(text)
        if matches:
            count += len(matches)
            text = rx.sub(f"[REDACTED_SECRET:{name}]", text)

    if count > 0:
        dest.write_text(text, encoding="utf-8")
        print(f"[INFO] zredagowano {count} sekret(ów) przed pushem na GitHub")
    return count


def scan_clean(dest: Path) -> bool:
    """Reuse the workspace secrets gate; True means clean."""
    cp = run(sys.executable, str(SCANNER), str(dest))
    if cp.returncode not in (0, 1):
        fail(EXIT_GIT, f"scan_secrets.py nie zadziałał: {(cp.stderr or '').strip()}")
    if cp.stdout.strip():
        print(cp.stdout.strip())
    return cp.returncode == 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="push_sessions_github.py")
    ap.add_argument(
        "file",
        nargs="?",
        default=str(ROOT / "scripts" / "_scratch" / "sessions" / "02_products" / "raw_sessions.md"),
        help="plik eksportu do opublikowania",
    )
    ap.add_argument("--repo", default=None, help="URL repo archiwum (albo env SESSIONS_GITHUB_REPO)")
    ap.add_argument("--count", default="", help="liczba sesji — tylko do wiadomości commita")
    ap.add_argument("--dry-run", action="store_true", help="pokaż plan bez commit/push")
    a = ap.parse_args()

    source = Path(a.file)
    if not source.is_file():
        fail(EXIT_SOURCE, f"brak pliku źródłowego: {source}")

    url = a.repo or os.environ.get("SESSIONS_GITHUB_REPO") or DEFAULT_REPO
    clone, branch = ensure_clone(url)

    dest = clone / DEST_NAME
    shutil.copyfile(source, dest)
    sanitize_file(dest)

    if not scan_clean(dest):
        fail(
            EXIT_SECRETS,
            f"scan_secrets znalazł wzorce sekretów w {dest.name} — push zablokowany. "
            "Wyczyść eksport albo zmień repo (nie omijaj tej bramki).",
        )

    git(["add", "--", DEST_NAME], cwd=clone)
    if run("git", "diff", "--cached", "--quiet", cwd=clone).returncode == 0:
        print(f"EXPORT_UNCHANGED — {url} [{branch}] już ma tę wersję, nic do pushowania")
        return EXIT_OK

    message = "chore: refresh raw sessions export"
    if a.count:
        message += f" ({a.count} sessions)"
    if a.dry_run:
        print(f"DRY-RUN: commit '{message}' + push do {url} [{branch}]")
        return EXIT_OK

    git(["commit", "--quiet", "-m", message], cwd=clone)
    push = run("git", "push", "--quiet", "origin", f"HEAD:refs/heads/{branch}", cwd=clone)
    if push.returncode != 0:
        fail(EXIT_GIT, f"push do {url} [{branch}]: {(push.stderr or push.stdout or '').strip()}")

    print(f"PUSHED: {DEST_NAME} -> {url} [{branch}]")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
