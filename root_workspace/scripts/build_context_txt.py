#!/usr/bin/env python3
"""Build layered .txt context packs — root or one project, at depth L0–L3.

Research basis (2026-09-27):
- Repomix: single AI-friendly file, sections (summary/structure/files),
  git-aware, secret filtering, token counts, per-pattern depth
  (full / compress / structure-only), --stdout pipe, CI regen.
- Progressive disclosure: L0 names -> L1 summary -> L2 full -> L3 deep.
  Always-loaded layer stays <2K tokens; deeper layers load on demand.
- llms.txt: layered docs standard — router file points at detail files.

ICM fit: this script is factory (generator, committed under scripts/).
Its OUTPUTS are derived — never committed; print to stdout or -o <path>.
Mirrors D9 (MAP.md generated, never hand-edited).

Levels:
  L0 ping     router only: AGENTS.md + project table + grades        (~0.5K tok,
              always-loaded ceiling 2K)
  L1 brief    + PHILOSOPHY s1, root contract summaries, per-project
              CLAUDE + CONTRACT headers + EXPERIENCE lesson titles   (~4K;
              on demand, never always-loaded — load one project's L1/L2
              per session, never the whole root L1 pack)
  L2 standard + full root docs (DECISIONS/GLOSSARY/TOOLS/MAP summary),
              full project CLAUDE/CONTEXT/EXPERIENCE + ref listings  (~15-30K)
  L3 deep     + MAP.md full, docs/adr + reports listings, capped source
              (opt-in, size caps, secret redaction)                  (bounded)

Usage:
  python scripts/build_context_txt.py --scope root --level 1 > root-L1.txt
  python scripts/build_context_txt.py --project datasets --level 2 > datasets-L2.txt
  python scripts/build_context_txt.py --project brain --level 3 --include-source -o /tmp/brain-L3.txt
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = sorted(
    p for p in (ROOT / "projects" / "research").iterdir()
    if p.is_dir() and not p.name.startswith(".") and not p.name.startswith("_")
) if (ROOT / "projects" / "research").is_dir() else []

SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache",
             ".ruff_cache", ".ipynb_checkpoints", ".brain", "node_modules",
             "data", "INBOX"}
SKIP_SUFFIX = {".pyc", ".pyo", ".db", ".sqlite", ".csv", ".parquet",
               ".png", ".jpg", ".pdf", ".log"}
SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|secret|token|password|private[_-]?key)\s*[:=]\s*\S+")
MAX_SOURCE_BYTES = 200_000  # L3 total source cap
MAX_FILE_BYTES = 20_000     # per-file cap at L3


def tok_estimate(text: str) -> int:
    return len(text) // 4


def read_capped(path: Path, limit: int = 200_000) -> str:
    try:
        data = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return f"[unreadable: {path.name}]"
    if len(data) > limit:
        return data[:limit] + f"\n[... truncated {len(data) - limit} chars ...]"
    return data


def redact(text: str) -> str:
    return SECRET_RE.sub(r"\1=<redacted>", text)


def headings(md: str, depth: int = 2) -> list[str]:
    out = []
    for line in md.splitlines():
        if line.startswith("#" * depth + " ") and not line.startswith("#" * (depth + 1)):
            out.append(line.strip("# ").strip())
    return out


def section(title: str, body: str) -> str:
    return f"\n{'=' * 70}\n{title}\n{'=' * 70}\n{body.rstrip()}\n"


def l0_router() -> str:
    parts = ["# L0 — router (always-loaded, ~2K tokens)",
             read_capped(ROOT / "AGENTS.md")]
    table = ["\n## Projects + grades"]
    for proj in PROJECTS:
        grade = "?"
        entry = proj / "CLAUDE.md"
        if entry.is_file():
            m = re.search(r"^grade:\s*(\w+)\s*$",
                          entry.read_text(encoding="utf-8", errors="replace"), re.M)
            if m:
                grade = m.group(1)
        table.append(f"- {proj.name} [{grade}]")
    parts.append("\n".join(table))
    return "\n".join(parts)


def l1_brief(scope: str, project: str = "") -> str:
    parts = [l0_router()]
    phil = ROOT / "PHILOSOPHY.md"
    if phil.is_file():
        text = read_capped(phil)
        s1 = text.split("## 2.")[0]
        parts.append(section("PHILOSOPHY s1 (principle)", s1))
    targets = [ROOT / "CONTEXT.md", ROOT / "CONTEXT-MAP.md"]
    for doc in targets:
        if doc.is_file():
            parts.append(section(f"{doc.name} (headings)",
                                 "\n".join("- " + h for h in headings(read_capped(doc))) or "(empty)"))
    projs = [ROOT / "projects" / "research" / project] if scope == "project" else PROJECTS
    for proj in projs:
        if not proj.is_dir():
            continue
        buf = [f"# {proj.name}"]
        for name in ("CLAUDE.md", "CONTEXT.md"):
            doc = proj / name
            if doc.is_file():
                text = read_capped(doc)
                first = "\n".join(text.splitlines()[:12])
                buf.append(f"\n### {name} (head + headings)\n{first}\n"
                           + "\n".join("- " + h for h in headings(text)))
        exp = proj / "EXPERIENCE.md"
        if exp.is_file():
            text = read_capped(exp)
            lessons = [ln for ln in text.splitlines()
                       if re.match(r"^\d+\.\s+\*\*", ln.strip()) or ln.startswith("## ")]
            buf.append("### EXPERIENCE.md (lesson titles)\n" + "\n".join(lessons[:30]))
        parts.append(section(f"PROJECT {proj.name} (L1)", "\n".join(buf)))
    return "\n".join(parts)


def l2_standard(scope: str, project: str = "") -> str:
    parts = [l1_brief(scope, project)]
    if scope == "root":
        for name in ("DECISIONS.md", "GLOSSARY.md", "TOOLS.md"):
            doc = ROOT / name
            if doc.is_file():
                parts.append(section(f"ROOT {name} (full)", redact(read_capped(doc))))
    projs = [ROOT / "projects" / "research" / project] if scope == "project" else PROJECTS
    for proj in projs:
        if not proj.is_dir():
            continue
        for name in ("CLAUDE.md", "CONTEXT.md", "EXPERIENCE.md"):
            doc = proj / name
            if doc.is_file():
                parts.append(section(f"{proj.name}/{name} (full)",
                                     redact(read_capped(doc))))
        for sub in ("references", "docs/adr", "reports", "skills"):
            d = proj / sub
            if d.is_dir():
                files = sorted(f.relative_to(proj).as_posix()
                               for f in d.rglob("*") if f.is_file())[:100]
                parts.append(section(f"{proj.name}/{sub} (listing)",
                                     "\n".join("- " + f for f in files) or "(empty)"))
    return "\n".join(parts)


def l3_deep(project: str, include_source: bool) -> str:
    proj = ROOT / "projects" / "research" / project
    parts = [l2_standard("project", project)]
    if not proj.is_dir():
        return "\n".join(parts) + f"\n[unknown project: {project}]\n"
    mapf = proj / "MAP.md"
    if mapf.is_file():
        parts.append(section(f"{project}/MAP.md (full)", redact(read_capped(mapf))))
    if include_source:
        budget = MAX_SOURCE_BYTES
        buf = []
        for f in sorted(proj.rglob("*.py")):
            if any(part in SKIP_DIRS for part in f.parts):
                continue
            if f.suffix.lower() in SKIP_SUFFIX:
                continue
            if f.stat().st_size > MAX_FILE_BYTES * 4:
                continue
            text = redact(read_capped(f, MAX_FILE_BYTES))
            cost = len(text)
            if budget - cost < 0:
                buf.append(f"... [source cap reached, {f.name} and rest omitted] ...")
                break
            budget -= cost
            buf.append(f"\n--- {f.relative_to(proj).as_posix()} ---\n{text}")
        parts.append(section(f"{project}/source (capped py, {MAX_SOURCE_BYTES - budget} chars)",
                             "\n".join(buf) or "(no source files)"))
    else:
        parts.append(section("source", "Omitted (pass --include-source for capped source)."))
    return "\n".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description="Build layered .txt context packs.")
    ap.add_argument("--scope", choices=["root", "project"], default="root")
    ap.add_argument("--project", default="")
    ap.add_argument("--level", type=int, choices=[0, 1, 2, 3], default=1)
    ap.add_argument("--include-source", action="store_true")
    ap.add_argument("-o", "--output", default="")
    args = ap.parse_args()

    if args.scope == "project" and not args.project:
        ap.error("--project <name> required with --scope project")

    if args.level == 0:
        text = l0_router()
    elif args.level == 1:
        text = l1_brief(args.scope, args.project)
    elif args.level == 2:
        text = l2_standard(args.scope, args.project)
    else:
        target = args.project or "knowledge-retrieval"
        text = l3_deep(target, args.include_source)

    footer = (f"\n{'=' * 70}\n[token estimate: ~{tok_estimate(text)} | "
              f"scope={args.scope} level=L{args.level}]\n")
    text += footer
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"wrote {args.output} (~{tok_estimate(text)} tokens)")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
