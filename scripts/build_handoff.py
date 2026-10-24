#!/usr/bin/env python3
"""Build root HANDOFF.md from handoff/flags/*.md + handoff/deep/*.md.

ICM invariants this rests on:
  4  every folder-level contract is explicit -> handoff/CONTEXT.md
  5  factory vs product -> this script owns the view template; flags/ + deep/ are
     the product, written by agents
  8  one home per fact -> a flag lives in exactly one file; the view only links
  9  the filesystem is the state machine; a generated index is never hand-edited

Granularity: ONE FLAG = ONE FILE = ONE WRITER. Ownership is a property of the
flag, not of the agent, so retiring a flag you did not create is still a legal
single-file write and two agents never clobber each other.

Usage:
    python scripts/build_handoff.py                # -> HANDOFF.md
    python scripts/build_handoff.py --check        # exit 1 if the view is stale
    python scripts/build_handoff.py --as-of DATE   # pin the inline window's
                                                   # reference day (default:
                                                   # newest flag `since`)
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FLAGS = ROOT / "handoff" / "flags"
DEEP = ROOT / "handoff" / "deep"
DEFAULT_OUT = ROOT / "HANDOFF.md"

KEYS = ("flag", "since", "owner", "agent", "model", "origin")
RX = {k: re.compile(rf"^{k}:\s*(.+?)\s*$") for k in KEYS}

# Deep notes are inlined in this order; unknown files follow, alphabetically.
DEEP_ORDER = (
    "where-the-work-landed.md",
    "gotchas-that-cost-time-worth-60-seconds-to-read-before-worki.md",
    "gate-note-if-you-touch-allowed-root.md",
    "g12-resolved-2026-10-01-human-decision-closed-same-day.md",
)

HEADER = """\
# HANDOFF — workspace root

> **GENEROWANE — nie edytuj ręcznie.** `python scripts/build_handoff.py`
> buduje ten plik z `handoff/flags/*.md` + `handoff/deep/*.md`.
> Kontrakt (kto pisze co): `handoff/CONTEXT.md`. Stan maszynowy: `STATE.md`.

Portable state for a cold session entering at the workspace root. Per D12 this
file carries only what is true across projects; the project-local handoff carries
the detail and is linked, never copied. The prose that used to sit here by hand
now has its home in `handoff/flags/` (one flag = one file = one writer) and is
inlined below by the builder.

## How to update

One flag = one file: `handoff/flags/<flag>.md`, frontmatter `flag` / `since` /
`owner` / `agent` / `model` + the entry body. Write **only** the flag you own
(or the one your task retired); never edit another flag's prose — that is what
made the old single-file handoff clobber under two agents. Then rebuild this
view:

```
python scripts/build_handoff.py           # regenerate
python scripts/build_handoff.py --check   # gate form: exit 1 if stale
```

This file is state, not a journal: replace or retire a flag whose claims
stopped holding (delete the file), and compress closed threads into
`handoff/deep/`. Project-local detail is linked, never copied (D11/D12).
"""

SUMMARY_CHARS = 200

# Inline window: only flags with `since` within the last N days are inlined
# into HANDOFF.md; older flags go to handoff/flags/INDEX.md (linked).
INLINE_WINDOW_DAYS = 3
INDEX_PATH = ROOT / "handoff" / "flags" / "INDEX.md"
INDEX_REL = "handoff/flags/INDEX.md"
INDEX_SUMMARY_CHARS = 120


def parse_flag(path: Path) -> dict:
    """Parse one flag file: frontmatter + body + a deterministic one-line summary."""
    lines = path.read_text(encoding="utf-8").splitlines()
    meta: dict[str, str] = {}
    i = 0
    if lines and lines[0].strip() == "---":
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            s = lines[i].strip()
            for k in KEYS:
                m = RX[k].match(s)
                if m:
                    meta[k] = m.group(1)
            i += 1
        i += 1 if i < len(lines) and lines[i].strip() == "---" else 0
    body = "\n".join(lines[i:]).strip()
    if meta.get("flag") and meta["flag"] != path.stem:
        meta["problem"] = f"flag `{meta['flag']}` != filename `{path.stem}`"
    meta.setdefault("flag", path.stem)
    meta["path"] = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.name
    meta["body"] = body
    meta["summary"] = summarize(body)
    return meta


def summarize(body: str) -> str:
    """First line, minus the `flag` — date: prefix, clipped at a word boundary."""
    if not body:
        return "(empty)"
    first = body.splitlines()[0]
    first = re.sub(r"^`[^`]+`\s+—\s+\d{4}-\d{2}-\d{2}:\s*", "", first).strip()
    if len(first) <= SUMMARY_CHARS:
        return first
    cut = first[:SUMMARY_CHARS].rsplit(" ", 1)[0]
    return cut + "…"


def collect(flags_dir: Path = FLAGS, deep_dir: Path = DEEP) -> tuple[list[dict], list[str], list[tuple[str, str]]]:
    """Read every flag + deep note. Returns (flags, problems, deep_sections)."""
    flags: list[dict] = []
    problems: list[str] = []
    if flags_dir.is_dir():
        for p in sorted(flags_dir.glob("*.md")):
            if p.name == INDEX_PATH.name:
                continue
            f = parse_flag(p)
            flags.append(f)
            if "problem" in f:
                problems.append(f"{f['path']}: {f['problem']}")
            if not f.get("since"):
                problems.append(f"{f['path']}: missing `since`")
    flags.sort(key=lambda f: (f.get("since", ""), f["flag"]), reverse=True)

    deep: list[tuple[str, str]] = []
    if deep_dir.is_dir():
        files = list(deep_dir.glob("*.md"))
        ordered = [deep_dir / n for n in DEEP_ORDER if (deep_dir / n).exists()]
        ordered += sorted(p for p in files if p not in ordered)
        for p in ordered:
            text = p.read_text(encoding="utf-8").strip()
            head = text.splitlines()[0] if text else p.stem
            title = head.lstrip("# ").strip() if head.startswith("#") else p.stem
            deep.append((title, "\n".join(text.splitlines()[1:]).strip()))
    return flags, problems, deep


def newest_since(flags: list[dict], fallback: date | None = None) -> date:
    """Deterministic reference point for the inline window: newest `since`.

    The window must be a function of repo *content*, not the wall clock. A close
    straddling midnight (S81) had hooks/pre-commit build the view at
    `today=10-17` and the `integrity` step rebuild it at `today=10-18` seconds
    later, so `--check` reported HANDOFF.md stale spuriously. Anchoring on the
    newest flag's `since` makes both builds identical. Only when no flag carries
    a `since` is there nothing to archive, so `fallback` (today) is inert.
    """
    since = [f["since"] for f in flags if f.get("since")]
    return date.fromisoformat(max(since)) if since else (fallback or date.today())


def split_flags(flags: list[dict], as_of: date | str | None = None,
                window_days: int = INLINE_WINDOW_DAYS) -> tuple[list[dict], list[dict]]:
    """Partition flags into (fresh, archived) by the inline window.

    Fresh = `since` >= as_of - window_days (or missing `since`, so problems
    stay visible in the main view). Archived = older flags, index-only.

    `as_of` defaults to the newest `since` in the corpus, NOT `date.today()`
    (S81 midnight bug): the same corpus yields the same partition on any day
    until a newer flag lands. `INLINE_WINDOW_DAYS` stays 3 — only the reference
    point changed. Input order (since desc) is preserved in both lists.
    """
    if as_of is None:
        as_of = newest_since(flags)
    elif isinstance(as_of, str):
        as_of = date.fromisoformat(as_of)
    cutoff = (as_of - timedelta(days=window_days)).isoformat()
    fresh = [f for f in flags if not f.get("since") or f["since"] >= cutoff]
    archived = [f for f in flags if f.get("since") and f["since"] < cutoff]
    return fresh, archived


def render_index(archived: list[dict]) -> str:
    """Render handoff/flags/INDEX.md: one table row per archived flag."""
    out = ["# INDEX — archived flags",
           "",
           f"> Generowane przez `python scripts/build_handoff.py`. Flagi starsze niż {INLINE_WINDOW_DAYS} dni (po `since`, malejąco).",
           "",
           "| flag | since | owner | agent | summary |",
           "| --- | --- | --- | --- | --- |"]
    for f in archived:
        s = f.get("summary", "")
        if len(s) > INDEX_SUMMARY_CHARS:
            s = s[:INDEX_SUMMARY_CHARS].rsplit(" ", 1)[0] + "…"
        s = s.replace("|", "/")
        out.append(f"| `{f['flag']}` | {f.get('since', '?')} | {f.get('owner', '?')} "
                   f"| {f.get('agent', '?')} | {s} |")
    return "\n".join(out).rstrip() + "\n"


def render(flags: list[dict], deep: list[tuple[str, str]], problems: list[str], archived_count: int = 0) -> str:
    out = [HEADER, "## Status", ""]
    for f in flags:
        out += [f"<!-- {f['path']} · owner: {f.get('owner', '?')} · agent: "
                f"{f.get('agent', '?')} · model: {f.get('model', '?')} -->",
                f["body"], ""]
    if archived_count:
        out += [f"Starsze flagi ({archived_count}): [{INDEX_REL}]({INDEX_REL})", ""]
    if problems:
        out += ["## ⚠️ Problemy (wykryte przez builder)", ""]
        out += [f"- {p}" for p in problems]
        out.append("")
    for title, text in deep:
        out += [f"## {title}", "", text, ""]
    return "\n".join(out).rstrip() + "\n"


def is_stale(out: Path, text: str) -> bool:
    return (not out.exists()) or out.read_text(encoding="utf-8") != text


def detect_duplicates(flags: list[dict]) -> tuple[list[str], list[str]]:
    """Duplicate-flag detection (§4.3, R19 companion).

    Returns (hard, advisory). `hard` = two files claiming the same `flag:`
    id — a corrupted one-home-per-fact invariant; these join `problems`, so
    `--check` fails until the collision is retired. `advisory` = clusters of
    flags sharing >=2 significant stem tokens (e.g. `graphrag-phase8-*`) —
    printed for a human to judge, never failing: a thread legitimately owns
    several flags (qrefusal + qground), while a retrospective summary of
    somebody else's older work (8/10, 9/10 pattern) only looks like one.
    """
    from collections import defaultdict

    hard: list[str] = []
    by_id: dict[str, list[str]] = defaultdict(list)
    for f in flags:
        by_id[f.get("flag", "")].append(f["path"])
    for fid, paths in sorted(by_id.items()):
        if len(paths) > 1:
            hard.append(f"duplicate flag id `{fid}` claimed by: {', '.join(paths)}")

    stop = {"graphrag", "phase", "faza", "sesja", "session", "flag", "handoff",
            "update", "updated", "outcome", "fixed", "fix", "result", "review",
            "report", "state", "closed", "open", "new", "v2", "md",
            "and", "or", "the", "a", "an", "of", "to", "in", "on", "for",
            "with", "done", "live", "test"}
    toks: dict[str, set[str]] = {}
    for f in flags:
        parts = set(re.split(r"[-_]+", f["flag"].lower())) - stop
        parts.discard("")
        toks[f["path"]] = parts
    advisory: list[str] = []
    paths = sorted(toks)
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            shared = toks[paths[i]] & toks[paths[j]]
            if len(shared) >= 2:
                advisory.append(
                    f"CLUSTER {paths[i]} <-> {paths[j]} "
                    f"(shared: {', '.join(sorted(shared))})"
                )
    return hard, advisory


def main() -> int:
    ap = argparse.ArgumentParser(prog="build_handoff.py")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if HANDOFF.md is missing, stale, or a flag is malformed")
    ap.add_argument("--as-of", type=date.fromisoformat, default=None,
                    help="reference date for the inline window; default = newest "
                         "flag `since` (keeps the view off the wall clock, S81)")
    ap.add_argument("-o", "--out", type=Path, default=DEFAULT_OUT)
    a = ap.parse_args()
    flags, problems, deep = collect()
    dup_hard, dup_advisory = detect_duplicates(flags)
    problems.extend(dup_hard)
    fresh, archived = split_flags(flags, a.as_of)
    text = render(fresh, deep, problems, len(archived))
    index_text = render_index(archived)
    if a.check:
        if problems:
            for p in problems:
                print(f"PROBLEM {p}")
        rc = 0
        if is_stale(a.out, text):
            print(f"STALE {a.out} — run: python scripts/build_handoff.py")
            rc = 1
        else:
            print(f"OK {a.out.name}: {len(fresh)} flags inline, {len(archived)} archived, {len(deep)} deep notes, view current")
        if is_stale(INDEX_PATH, index_text):
            print(f"STALE {INDEX_PATH} — run: python scripts/build_handoff.py")
            rc = 1
        else:
            print(f"OK {INDEX_PATH.name}: {len(archived)} archived flags, index current")
        for c in dup_advisory[:10]:
            print(c)
        return 1 if problems else rc
    a.out.parent.mkdir(parents=True, exist_ok=True)
    # LF on disk even under Windows text mode (newline="\n"), so the
    # working copy matches the repo convention (* text=auto eol=lf) and
    # git stops warning "CRLF will be replaced by LF" on every commit.
    a.out.write_text(text, encoding="utf-8", newline="\n")
    INDEX_PATH.write_text(index_text, encoding="utf-8", newline="\n")
    print(f"wrote {a.out}  ({len(fresh)} flags inline, {len(archived)} archived, {len(deep)} deep notes, "
          f"{len(problems)} problems)")
    print(f"wrote {INDEX_PATH}  ({len(archived)} archived flags)")
    for c in dup_advisory[:10]:
        print(c)
    return 0


if __name__ == "__main__":
    sys.exit(main())