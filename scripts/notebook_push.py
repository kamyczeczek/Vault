#!/usr/bin/env python3
"""Push a NotebookLM pack + session files to the fixed notebook.

Factory (generator, committed under scripts/). Two-step automation:
1. scripts/build_notebook_pack.py builds the .txt pack (workspace + sessions).
2. THIS script pushes the pack + optional per-session .md exports via the
    `nlm` CLI (notebooklm-mcp-cli, jacob-bd/gemini-notebook-mcp-cli)
    authenticated via CDP live-Chrome session, profile `piwowarski`
    (piwowarski.mateusz99@gmail.com). Old notebooklm-py venv kept as
    fallback only (Chrome 127+ App-Bound Encryption breaks its cookie read).

Full auto (build + export sessions + push):
  python.exe scripts/notebook_push.py --auto --sessions 5
Pack-only push:
  python.exe scripts/notebook_push.py --pack scripts/out/notebook-root-debug.txt
Push with extra session files:
  python.exe scripts/notebook_push.py --pack scripts/out/notebook-root-debug.txt --extra-dir scripts/out/sessions

Usage:
  python.exe scripts/notebook_push.py --pack scripts/out/notebook-root-debug.txt
  python.exe scripts/notebook_push.py --pack scripts/out/notebook-root-debug.txt --extra-dir scripts/out/sessions
  python.exe scripts/notebook_push.py --pack <file> --notebook a49ff8cb-31e0-470e-b747-3f2a0ded1699 --wait

Exit 0: every file registered READY. Exit 1: anything stuck/error.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NB_ENV = "NOTEBOOKLM_NOTEBOOK"
DEFAULT_NOTEBOOK = "a49ff8cb-31e0-470e-b747-3f2a0ded1699"
NLM = Path(r"C:\Users\Mateusz\.local\bin\nlm.exe")
PROFILE = "piwowarski"


def run(*args: str, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(NLM), *args], capture_output=True, text=True, timeout=timeout,
        cwd=str(ROOT),
    )


def add_file(path: Path, notebook: str) -> tuple[str, str]:
    """Register one file as a source. Returns (source_id, status)."""
    p = run("source", "add", notebook, "--file", str(path),
            "-p", PROFILE, "--json", timeout=300)
    if p.returncode != 0:
        raise RuntimeError(f"add failed for {path.name}: {(p.stderr or p.stdout)[:300]}")
    try:
        data = json.loads(p.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"non-JSON add output for {path.name}: {p.stdout[:200]}")
    # nlm schema: {"source_type": ..., "source_id": ..., "title": ...}
    # (old notebooklm-py used {"sources": [{"id": ...}]} — not supported anymore)
    sid = data.get("source_id", "") if isinstance(data, dict) else ""
    if not sid:
        raise RuntimeError(f"no source id returned for {path.name}: {p.stdout[:200]}")
    return sid, "registered"


def source_status(sid: str, notebook: str) -> str:
    """Poll source list; READY sources report status 2. Returns status str."""
    p = run("source", "list", notebook, "-p", PROFILE, timeout=120)
    if p.returncode != 0:
        return f"LIST_FAILED: {(p.stderr or p.stdout)[:200]}"
    try:
        data = json.loads(p.stdout)
    except json.JSONDecodeError:
        return f"LIST_NONJSON: {p.stdout[:150]}"
    items = data if isinstance(data, list) else data.get("sources", [])
    for s in items:
        if s.get("id") == sid:
            return "ready" if s.get("status") == 2 else f"status={s.get('status')}"
    return "not-found"


def wait_ready(sid: str, notebook: str, timeout_s: int = 600) -> str:
    # nlm has no `source wait`; poll `source list` until status 2 (ready).
    deadline = time.time() + timeout_s
    last = "unknown"
    while time.time() < deadline:
        last = source_status(sid, notebook)
        if last == "ready":
            return last
        if last.startswith(("LIST_FAILED", "LIST_NONJSON")):
            return last
        time.sleep(15)
    return f"TIMEOUT: last={last}"


def build_pack(scope: str, project: str, sessions: int, out: Path, level: int = 1) -> Path:
    p = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_notebook_pack.py"),
         "--scope", scope, *(["--project", project] if scope == "project" else []),
         "--sessions", str(sessions), "--level", str(level), "-o", str(out)],
        capture_output=True, text=True, timeout=300, cwd=str(ROOT),
    )
    if p.returncode != 0:
        raise RuntimeError(f"build pack failed: {(p.stderr or p.stdout)[:300]}")
    return out


def export_sessions(n: int, outdir: Path) -> list[Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(ROOT / "scripts"))
    from agent_sessions import get_all_sessions, _safe_name, _session_header
    latest = get_all_sessions(limit_per_agent=10)[:n]
    paths: list[Path] = []
    for i, s in enumerate(latest, 1):
        name = f"{i:02d}_{s.agent}_{_safe_name(s)}.md"
        fp = outdir / name
        fp.write_text(_session_header(s, i, len(latest)) + (s.text_markdown or "(empty)"),
                      encoding="utf-8")
        paths.append(fp)
    return paths


def list_sources(notebook: str) -> list[dict]:
    """All sources in the notebook (id + title). Empty list on error."""
    p = run("source", "list", notebook, "-p", PROFILE, timeout=120)
    if p.returncode != 0:
        print(f"  ! source list failed: {(p.stderr or p.stdout)[:200]}")
        return []
    try:
        data = json.loads(p.stdout)
    except json.JSONDecodeError:
        print(f"  ! source list non-JSON: {p.stdout[:150]}")
        return []
    return data if isinstance(data, list) else data.get("sources", [])


def delete_source(sid: str) -> bool:
    p = run("source", "delete", sid, "--confirm", "-p", PROFILE, timeout=120)
    return p.returncode == 0


def prune(notebook: str, fresh: dict[str, str]) -> int:
    """Replace, don't accumulate. Deletes superseded OUR sources only:
    - pack files (title starts with `notebook-`) whose id is not fresh
    - session files whose title exactly repeats a fresh upload (rerun dedup)
    Never touches PDFs, URLs, Drive, or the user's expert sources.
    Returns the number deleted. `fresh`: {title: new_source_id}."""
    removed = 0
    fresh_ids = set(fresh.values())
    for s in list_sources(notebook):
        sid, title = s.get("id", ""), s.get("title", "")
        if not sid or sid in fresh_ids:
            continue
        if title.startswith("notebook-") or title in fresh:
            if delete_source(sid):
                print(f"  - pruned {title} ({sid[:8]}...)")
                removed += 1
            else:
                print(f"  ! prune failed for {title} ({sid[:8]}...)")
    return removed


def main() -> int:
    ap = argparse.ArgumentParser(description="Push pack + session files to NotebookLM.")
    ap.add_argument("--pack", default="", help="Path to the .txt pack")
    ap.add_argument("--auto", action="store_true", help="Build pack + export sessions + push")
    ap.add_argument("--scope", choices=["root", "project"], default="root")
    ap.add_argument("--project", default="")
    ap.add_argument("--level", type=int, choices=[0, 1, 2], default=1,
                    help="Pack depth: L1 summary default; L2 full for structural audits")
    ap.add_argument("--sessions", type=int, default=5)
    ap.add_argument("--extra-dir", default="", help="Extra dir of session .md/.txt files")
    ap.add_argument("--notebook", default=DEFAULT_NOTEBOOK)
    ap.add_argument("--wait", action="store_true", help="Wait for READY (default: register only)")
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--no-prune", action="store_true",
                    help="Skip pruning superseded pack/session sources (default: --auto prunes)")
    args = ap.parse_args()

    if args.auto:
        stamp = time.strftime("%Y%m%d-%H%M")
        pack_path = ROOT / "scripts" / "out" / f"notebook-{args.scope}-{stamp}.txt"
        build_pack(args.scope, args.project, args.sessions, pack_path, args.level)
        print(f"built pack: {pack_path.name}")
        extra = ROOT / "scripts" / "out" / f"sessions-{stamp}"
        exported = export_sessions(args.sessions, extra)
        print(f"exported {len(exported)} sessions -> {extra.name}/")
        args.pack = str(pack_path)
        args.extra_dir = str(extra)

    if not args.pack:
        ap.error("--pack <file> or --auto required")

    if not NLM.is_file():
        print(f"nlm CLI missing: {NLM} — reinstall via `uv tool install notebooklm-mcp-cli`")
        return 1
    pack = Path(args.pack)
    if not pack.is_absolute():
        pack = ROOT / pack
    if not pack.is_file():
        print(f"pack not found: {pack}")
        return 1

    files = [pack]
    if args.extra_dir:
        d = Path(args.extra_dir)
        d = d if d.is_absolute() else ROOT / d
        if d.is_dir():
            files += sorted(p for p in d.iterdir()
                            if p.suffix.lower() in (".txt", ".md") and p.is_file())

    print(f"notebook: {args.notebook} | files: {len(files)}")
    failed = 0
    fresh: dict[str, str] = {}
    for f in files:
        try:
            sid, st = add_file(f, args.notebook)
            print(f"  + {f.name} -> {sid[:8]}... [{st}]")
            fresh[f.name] = sid
            if args.wait:
                final = wait_ready(sid, args.notebook, args.timeout)
                print(f"    ready-state: {final}")
                if final.lower() not in ("ready", "processed", "complete"):
                    failed += 1
        except Exception as e:  # keep pushing the rest, report at the end
            print(f"  ! {f.name}: {e}")
            failed += 1
    if args.auto and not args.no_prune and failed == 0:
        n = prune(args.notebook, fresh)
        print(f"pruned {n} superseded source(s)")
    print("OK: all registered" if failed == 0 else f"FAILED: {failed} file(s)")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
