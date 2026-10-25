#!/usr/bin/env python3
"""Re-verify pytest evidence claimed in a REVIEW.md.

Takes every fenced block that runs pytest, re-executes it, and compares the
fresh "N passed" count against the number the REVIEW claims nearby. A number
retyped from memory instead of pasted from the terminal is exactly the
failure class this catches (2026-10-03: agent reported "11 passed" for a
4-test file).

Usage:
    python scripts/verify_review_evidence.py REVIEW.md [--root DIR]
    python scripts/verify_review_evidence.py --selftest

Exit codes: 0 = all claims match fresh runs; 2 = mismatch, failing command,
or unrunnable block; 1 = usage error. Blocks with no claimed number are
reported SKIP (prose, not evidence) — only numbers are checked.

Contract enforced: every "N passed" claim in a REVIEW must come from a
re-runnable pytest block in the same file. Stdlib only.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

FENCE = re.compile(r"^(`{3,})\w*\s*$")
PYTEST_CMD = re.compile(r"(?m)^\s*(python(?:3)?(?:\.exe)?\s+-m\s+pytest\s+[^\n`]+)")
CLAIM = re.compile(r"(\d+)\s+passed")
SUMMARY = re.compile(r"(\d+)\s+passed|(\d+)\s+failed|(\d+)\s+errors?")


def extract_blocks(md: str) -> list[tuple[str, int, int]]:
    """Return (block_text, open_line, close_line) for each fenced block."""
    blocks: list[tuple[str, int, int]] = []
    lines = md.split("\n")
    i = 0
    while i < len(lines):
        if FENCE.match(lines[i]):
            start = i
            i += 1
            buf: list[str] = []
            while i < len(lines) and not FENCE.match(lines[i]):
                buf.append(lines[i])
                i += 1
            blocks.append(("\n".join(buf), start + 1, i + 1))
        i += 1
    return blocks


def pytest_cmd_in(block: str) -> str | None:
    m = PYTEST_CMD.search(block)
    return m.group(1).strip() if m else None


def claim_after(md_lines: list[str], after_line: int, window: int = 20) -> int | None:
    """First 'N passed' claim after a block (prose or ```text output block).

    Fence markers are skipped, not terminators — claims live inside output
    blocks. Stops at the next pytest command (that belongs to another claim).
    `after_line` is the 0-indexed line to start scanning from.
    """
    for line in md_lines[after_line:after_line + window]:
        if PYTEST_CMD.search(line):
            break
        m = CLAIM.search(line)
        if m:
            return int(m.group(1))
    return None


def run_pytest(cmd: str, root: Path) -> tuple[int, int, str]:
    """Run a pytest command; return (returncode, passed_count, tail)."""
    try:
        p = subprocess.run(cmd, shell=True, cwd=str(root), timeout=300,
                           capture_output=True, text=True)
    except Exception as e:  # noqa: BLE001
        return -1, -1, f"could not execute: {e}"
    out = (p.stdout or "") + "\n" + (p.stderr or "")
    tail = "\n".join(out.splitlines()[-5:])
    m = list(CLAIM.finditer(out))
    return p.returncode, (int(m[-1].group(1)) if m else -1), tail


def verify(review: Path, root: Path) -> tuple[int, list[str]]:
    md = review.read_text(encoding="utf-8")
    md_lines = md.replace("\r\n", "\n").split("\n")
    report: list[str] = []
    failures = 0
    checked = 0
    for block, lineno, close_line in extract_blocks(md):
        cmd = pytest_cmd_in(block)
        if not cmd:
            continue
        claimed = claim_after(md_lines, close_line)
        if claimed is None:
            report.append(f"SKIP line {lineno}: pytest block with no claimed "
                          f"number — `{cmd[:80]}`")
            continue
        checked += 1
        rc, actual, tail = run_pytest(cmd, root)
        if rc != 0:
            failures += 1
            report.append(f"FAIL line {lineno}: command exits {rc} — `{cmd}`\n"
                          f"  tail: {tail}")
        elif actual != claimed:
            failures += 1
            report.append(f"FAIL line {lineno}: REVIEW claims {claimed} passed, "
                          f"fresh run gives {actual} — `{cmd}`")
        else:
            report.append(f"OK line {lineno}: {actual} passed matches — `{cmd[:80]}`")
    if checked == 0:
        report.append("no verifiable pytest claims found")
        return 2, report
    return (0 if failures == 0 else 2), report


def selftest() -> int:
    # unit: parsing helpers on synthetic text, no subprocess
    md = ("# R\n\n```powershell\npython -m pytest tests/x.py -q\n```\n"
          "**Output:**\n```text\n....\n4 passed in 0.02s\n```\n")
    blocks = extract_blocks(md)
    assert len(blocks) == 2, blocks
    assert pytest_cmd_in(blocks[0][0]) == "python -m pytest tests/x.py -q"
    assert pytest_cmd_in(blocks[1][0]) is None
    lines = md.split("\n")
    assert claim_after(lines, blocks[0][2]) == 4
    assert claim_after(lines, blocks[1][2]) is None  # claim was inside block 1
    assert claim_after(lines, 0, window=2) is None  # nothing claimed up top
    # live: temp REVIEW against a real trivial suite
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "test_tiny.py").write_text(
            "def test_a(): assert 1 + 1 == 2\n"
            "def test_b(): assert True\n", encoding="utf-8")
        good = (d / "good.md")
        good.write_text("```powershell\npython -m pytest test_tiny.py -q\n```\n"
                        "2 passed\n", encoding="utf-8")
        bad = (d / "bad.md")
        bad.write_text("```powershell\npython -m pytest test_tiny.py -q\n```\n"
                       "11 passed\n", encoding="utf-8")
        rc_good, rep_good = verify(good, d)
        rc_bad, rep_bad = verify(bad, d)
        assert rc_good == 0, rep_good
        assert rc_bad == 2, rep_bad
        assert any("claims 11 passed, fresh run gives 2" in r for r in rep_bad), rep_bad
    print("SELFTEST OK (parse units + live good/bad REVIEW)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("review", nargs="?", help="REVIEW.md to verify")
    ap.add_argument("--root", default=".",
                    help="cwd for re-running pytest (default: cwd)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.review:
        ap.error("REVIEW.md required (or --selftest)")
    review = Path(args.review)
    if not review.is_file():
        print(f"no such file: {review}", file=sys.stderr)
        return 1
    rc, report = verify(review, Path(args.root))
    print("\n".join(report))
    print("EVIDENCE-VERIFY " + ("PASS" if rc == 0 else "FAIL"))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
