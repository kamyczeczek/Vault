#!/usr/bin/env python3
"""Pre-close preflight: run every check close.py will run, before it writes.

Usage:
    python scripts/pre_close_check.py --flag <id> --body-file <path>
        [--include <path> ...]

Each check prints PASS/FAIL/WARN with a one-line reason.
Ends with PRE_CLOSE_READY (exit 0) or PRE_CLOSE_BLOCKED (exit 1).
Stdlib only.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FLAGS = ROOT / "handoff" / "flags"
PY = sys.executable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from git_paths import repo_prefix, repo_rel  # noqa: E402

results: list[tuple[str, str]] = []  # (status, message)


def report(status: str, msg: str) -> None:
    results.append((status, msg))
    print(f"{status}: {msg}")


def run_quiet(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))


def main() -> int:
    ap = argparse.ArgumentParser(prog="pre_close_check.py")
    ap.add_argument("--flag", required=True)
    ap.add_argument("--body-file", required=True)
    ap.add_argument("--include", nargs="*", default=[])
    a = ap.parse_args()

    flag, includes = a.flag, a.include
    body_path = Path(a.body_file)

    # 1. flag must not exist
    if (FLAGS / f"{flag}.md").exists():
        report("FAIL", f"flaga istnieje ({FLAGS / f'{flag}.md'}), retire ja najpierw")
    else:
        report("PASS", "flaga nie istnieje, mozna zamykac")

    # 2. body-file exists and starts with `flag`
    try:
        body = body_path.read_text(encoding="utf-8")
    except OSError:
        body = ""
        report("FAIL", f"--body-file nie istnieje: {body_path}")
    else:
        if body.strip().startswith(f"`{flag}`"):
            report("PASS", f"--body-file zaczyna sie od `{flag}`")
        else:
            report("FAIL", f"--body-file nie zaczyna sie od `{flag}`")

    # 3. body contains `not checked:`
    if body and re.search(r"^not checked:", body, re.M | re.I):
        report("PASS", "--body-file zawiera linie `not checked:`")
    elif body:
        report("FAIL", "--body-file nie zawiera linii `not checked:`")

    # 4. --include paths exist or are tracked
    bad: list[str] = []
    for i in includes:
        on_disk = (ROOT / Path(i)).exists()
        tracked = run_quiet(["git", "ls-files", "--error-match", i]).returncode == 0
        if not on_disk and not tracked:
            bad.append(i)
    if bad:
        report("FAIL", f"--include nie istnieje / nie trackowane: {bad}")
    else:
        report("PASS", "--include: wszystkie sciezki istnieja lub sa trackowane")

    # 5. --include must not contain scripts/_scratch/*
    scratch = [i for i in includes
               if Path(i).as_posix() == "scripts/_scratch/GATES.md"
               or Path(i).as_posix().startswith("scripts/_scratch/")]
    if scratch:
        report("FAIL", f"--include zawiera gitignore scripts/_scratch/*: {scratch}")
    else:
        report("PASS", "--include bez scripts/_scratch/*")

    # 6. git diff --check
    p = run_quiet(["git", "diff", "--check"])
    if p.returncode == 0:
        report("PASS", "git diff --check czysty")
    else:
        report("FAIL", f"git diff --check brudny:\n{(p.stdout + p.stderr).strip()[:400]}")

    # 7. build_handoff --check
    p = run_quiet([PY, "scripts/build_handoff.py", "--check"])
    if p.returncode == 0:
        report("PASS", "HANDOFF nie stale (build_handoff --check)")
    else:
        tail = (p.stdout + p.stderr).strip().splitlines()
        report("FAIL", f"HANDOFF stale: {'; '.join(tail[-3:])}")

    # 8. integrity gate
    p = run_quiet([PY, "scripts/check_workspace_integrity.py"])
    if p.returncode == 0:
        report("PASS", "check_workspace_integrity.py zielony")
    else:
        tail = (p.stdout + p.stderr).strip().splitlines()
        report("FAIL", f"integrity FAIL: {'; '.join(tail[-4:])}")

    # 9. secrets scan on --include files
    existing = [i for i in includes if (ROOT / Path(i)).is_file()]
    if existing:
        p = run_quiet([PY, "scripts/scan_secrets.py", *existing])
        if p.returncode == 0:
            report("PASS", f"scan_secrets czysty na {len(existing)} plikach --include")
        else:
            report("FAIL", f"scan_secrets trafil: {p.stdout.strip()[:300]}")
    else:
        report("WARN", "brak plikow --include do skanu sekretow")

    # 10. uncommitted work vs --include
    p = run_quiet(["git", "status", "--short"])
    lines = [l for l in p.stdout.splitlines() if l.strip()]
    modified = [l for l in lines if not l.startswith("??")]
    untracked = [l for l in lines if l.startswith("??")]
    allowed = {Path(i).as_posix() for i in includes}
    prefix = repo_prefix(ROOT)

    def outside_include(line: str) -> bool:
        rel = repo_rel(line[3:], prefix)  # repo-relative -> ROOT-relative (ADR-006)
        if rel is None:                   # vault-level change, not this close's business
            return False
        return rel not in allowed and rel not in ("HANDOFF.md", "STATE.md")

    outside = [l for l in modified if outside_include(l)]
    print(f"INFO: modified={len(modified)} untracked={len(untracked)} "
          f"outside-include={len(outside)}")
    if outside and len(modified) > len(includes) + 1:
        report("WARN", f"uncommitted work poza --include: {[s.strip() for s in outside[:5]]}")
    else:
        report("PASS", "uncommitted work miesci sie w --include (+flaga/views)")

    # 11. reports in --include must carry evidence (S59 wiring)
    review_inc = [i for i in includes
                  if Path(i).as_posix().startswith("docs/reviews/")
                  and Path(i).suffix == ".md"
                  and (ROOT / Path(i)).is_file()]
    if review_inc:
        bad_ev: list[str] = []
        for r in review_inc:
            p = run_quiet([PY, "scripts/verify_report_evidence.py",
                            "--enforce-after", "2026-10-13", r])
            if p.returncode != 0:
                bad_ev.append(r)
        if bad_ev:
            report("FAIL", f"verify_report_evidence FAIL na: {bad_ev} "
                             f"(raporty od 2026-10-13 wymagaja ## Tool calls)")
        else:
            report("PASS", f"verify_report_evidence czysty na {len(review_inc)} "
                             f"raportach (--enforce-after 2026-10-13)")
    else:
        report("PASS", "brak raportow docs/reviews/*.md w --include")

    failed = [r for r in results if r[0] == "FAIL"]
    if failed:
        print(f"PRE_CLOSE_BLOCKED ({len(failed)} FAIL)")
        return 1
    print("PRE_CLOSE_READY")
    return 0


if __name__ == "__main__":
    sys.exit(main())
