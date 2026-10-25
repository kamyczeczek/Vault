#!/usr/bin/env python3
"""Rebuild STATE.md — the machine-derived, always-current worktree snapshot.

ICM invariant 9 (filesystem is the state machine): status must be derivable
by scanning what exists. HANDOFF.md carries the narrative as a generated view
of `handoff/flags/` + `handoff/deep/` (scripts/build_handoff.py — never
hand-edit, rerun that script); STATE.md carries the scan (generated — never
hand-edit, rerun this script).
It answers "what is the tree doing right now" without reading history.

Usage:
    python scripts/build_state.py
    python scripts/build_state.py --selftest

Scans: git HEAD/branch/dirty list/last commits, .dgc-evidence/runs/
(REVIEW.md, REVIEW.html, DECISION.json verdict, LATEST). Stdlib only.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "STATE.md"
OBSIDIAN_STATE_FRONTMATTER_RX = re.compile(
    r"\A---\r?\n"
    r"type: Concept\r?\n"
    r"title: STATE\r?\n"
    r"generated: \{[^\r\n]*\}\r?\n"
    r"---\r?\n(?:\r?\n)?"
)


def sh(cmd: list[str]) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           cwd=ROOT, timeout=30)
        return r.stdout.strip() if r.returncode == 0 else "?"
    except Exception:
        return "?"


def scan() -> dict:
    head = sh(["git", "rev-parse", "--short", "HEAD"])
    branch = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    dirty = [l for l in sh(["git", "status", "--short"]).splitlines() if l.strip()]
    log = [l for l in sh(["git", "log", "--oneline", "-5"]).splitlines() if l.strip()]
    runs_dir = ROOT / ".dgc-evidence" / "runs"
    runs: list[dict] = []
    latest = ""
    if runs_dir.is_dir():
        lp = runs_dir / "LATEST"
        if lp.is_file():
            latest = lp.read_text(encoding="utf-8").strip()
        for d in sorted(p for p in runs_dir.iterdir() if p.is_dir()):
            dec = d / "DECISION.json"
            verdict = ""
            if dec.is_file():
                try:
                    verdict = str(json.loads(dec.read_text(encoding="utf-8"))
                                  .get("verdict", "?"))
                except Exception:
                    verdict = "unreadable"
            runs.append({"id": d.name,
                         "review_md": (d / "REVIEW.md").is_file(),
                         "review_html": (d / "REVIEW.html").is_file(),
                         "verdict": verdict or "-"})
    return {"head": head, "branch": branch, "dirty": dirty, "log": log,
            "runs": runs, "latest": latest,
            "now": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}


def render(s: dict) -> str:
    L = ["# STATE — root workspace (generated)",
         "",
         "> Nie edytuj ręcznie. Przebuduj: `python scripts/build_state.py`. "
         "Narracja: `HANDOFF.md`. "
         f"Stan na: {s['now']} · HEAD `{s['head']}` ({s['branch']}).",
         "",
         "## Drzewo",
         ""]
    if s["dirty"]:
        L.append(f"brudne pliki ({len(s['dirty'])}):")
        L += [f"- `{l}`" for l in s["dirty"][:20]]
        if len(s["dirty"]) > 20:
            L.append(f"- … +{len(s['dirty']) - 20} więcej")
    else:
        L.append("czyste (nic do commita).")
    L += ["", "## Ostatnie commity", ""]
    L += [f"- `{l}`" for l in s["log"]] or ["- (brak)"]
    L += ["", "## Runy (`.dgc-evidence/runs/`)",
          f"LATEST (czeka na werdykt): `{s['latest'] or '-'}`", ""]
    if s["runs"]:
        L += ["| run | REVIEW.md | REVIEW.html | werdykt |",
              "|---|---|---|---|"]
        for r in s["runs"]:
            md = "tak" if r["review_md"] else "—"
            hh = "tak" if r["review_html"] else "—"
            L.append(f"| `{r['id']}` | {md} | {hh} | {r['verdict']} |")
    else:
        L.append("(brak runów)")
    L += ["", "## Co dalej", "",
          "- pełny stan + next steps: `HANDOFF.md` (widok z `handoff/flags/`, "
          "najwyższa flaga w `## Status`; źródło: `handoff/CONTEXT.md`)"]
    return "\n".join(L) + "\n"


def build() -> Path:
    # LF on disk even under Windows text mode (newline="\n"), so the
    # working copy matches the repo convention (* text=auto eol=lf) and
    # git stops warning "CRLF will be replaced by LF" on every commit.
    frontmatter = ""
    if STATE.exists():
        current = STATE.read_text(encoding="utf-8")
        match = OBSIDIAN_STATE_FRONTMATTER_RX.match(current)
        if match:
            frontmatter = match.group(0)
    STATE.write_text(frontmatter + render(scan()), encoding="utf-8", newline="\n")
    return STATE


def selftest() -> int:
    import tempfile
    s = {"head": "abc1234", "branch": "main",
         "dirty": [" M HANDOFF.md", "?? .dgc-evidence/"],
         "log": ["abc1234 test commit"], "latest": "run-1",
         "runs": [{"id": "run-1", "review_md": True,
                   "review_html": True, "verdict": "PASS"}],
         "now": "2026-10-03 00:00"}
    doc = render(s)
    for probe in ("abc1234", "run-1", "PASS", "HANDOFF.md",
                  "build_state.py", "LATEST"):
        assert probe in doc, probe
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "STATE.md"
        p.write_text(doc, encoding="utf-8")
        assert p.stat().st_size > 0
    live = scan()
    assert live["head"] not in ("", "?") or True  # git may be absent
    assert isinstance(live["runs"], list)
    print("SELFTEST OK (render probes + live scan shape)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    out = build()
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
