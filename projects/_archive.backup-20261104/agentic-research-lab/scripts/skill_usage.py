#!/usr/bin/env python3
"""Skill usage audit: which vendored skills does this project actually use?

For each skill in `skills/`, count references in *operational* files only
(routing, contracts, scripts, prompts, the workspace extension). Corpus,
docs, backups, and reflection prose are excluded on purpose: the word
"research" in a paper chunk is not usage of the `research` skill, and
counting it would turn this audit into flattery.

This is the evidence base for two decisions:

- D8 deviation: all 20 skills were bulk-vendored on 2026-09-27 (503 KB),
  against the "vendor on first use, never speculatively" rule. Unused skills
  are un-vendor candidates — but only with this count plus a post-removal
  gate run, never on impression.
- Ablation bar (pre-registered before any LLM ablation run): for each used
  skill, skill-vs-no-skill on a pinned task set must show a measured gain;
  a skill with zero references cannot pass the bar by construction.

Output JSON to stdout. Deterministic: file order sorted, counts exact.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
SUFFIXES = {".py", ".md", ".jsonl", ".json", ".omp", ".ts"}


OPERATIONAL_DIRS = {
    "scripts", "pipeline", "stages", "hooks", ".omp", "templates", "frontier",
}
OPERATIONAL_FILES = {
    "CLAUDE.md", "CONTEXT.md", "local_skills.md", "skill_router.py",
    "START-HERE.md",
}


def project_files() -> list[Path]:
    out = []
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file() or p.suffix not in SUFFIXES:
            continue
        try:
            rel = p.relative_to(ROOT)
        except ValueError:
            continue
        if ".git" in rel.parts or "__pycache__" in rel.parts:
            continue
        top = rel.parts[0]
        if top == ".omp" and p.suffix == ".ts":
            out.append(p)
        elif top in OPERATIONAL_DIRS:
            out.append(p)
        elif len(rel.parts) == 1 and rel.name in OPERATIONAL_FILES:
            out.append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=0, help="unused")
    ap.add_argument("--out", type=Path, default=None, help="write JSON report here (utf-8)")
    args = ap.parse_args()
    skills = sorted(p.name for p in SKILLS.iterdir() if p.is_dir())
    files = project_files()
    texts = {p: p.read_text(encoding="utf-8", errors="ignore") for p in files}
    report = {}
    for skill in skills:
        pat = re.compile(rf"\b{re.escape(skill)}\b", re.IGNORECASE)
        hits = sorted(
            str(p.relative_to(ROOT)) for p in files if pat.search(texts[p])
        )
        report[skill] = {"references": len(hits), "files": hits[:10]}
    unused = sorted(s for s, r in report.items() if r["references"] == 0)
    out = {
        "skills": len(skills),
        "files_scanned": len(files),
        "unused": unused,
        "report": report,
    }
    print(json.dumps(out, indent=2))
    if args.out:
        args.out.write_text(json.dumps(out, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
