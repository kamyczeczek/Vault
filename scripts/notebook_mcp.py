#!/usr/bin/env python3
"""NotebookLM over MCP (stdio) — ask + upload without a browser.

Thin stdio JSON-RPC client for `notebooklm-mcp` (fastmcp). Same auth profile
as the CLI (~/.notebooklm). No browser, no CSRF, no cookies refresh dance:
the MCP server opens its client lazily and surfaces auth as tool errors.

Requires NOTEBOOKLM_MCP_ALLOWED_ROOTS to cover the upload dir for
source_add(file). Example:
  $env:NOTEBOOKLM_MCP_ALLOWED_ROOTS="C:\\Users\\Mateusz\\Desktop\\root_worksapce\\scripts\\out"

Usage:
  python.exe scripts/notebook_mcp.py ask -n <notebook> "question" [--json-out FILE]
  python.exe scripts/notebook_mcp.py add-file -n <notebook> <path> [--wait]
  python.exe scripts/notebook_mcp.py list-sources -n <notebook>
  python.exe scripts/notebook_mcp.py auto --scope root --sessions 5 -n <notebook>
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MCP_BIN = Path(r"C:\Users\Mateusz\.notebooklm-venv\Scripts\notebooklm-mcp.exe")
DEFAULT_NOTEBOOK = "a49ff8cb-31e0-470e-b747-3f2a0ded1699"


class Mcp:
    def __init__(self) -> None:
        env = dict(os.environ)
        self.proc = subprocess.Popen(
            [str(MCP_BIN)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, encoding="utf-8",
            errors="replace", bufsize=1, env=env,
        )
        self._id = 0
        self._call({"jsonrpc": "2.0", "id": self._next(), "method": "initialize",
                    "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                               "clientInfo": {"name": "notebook_mcp", "version": "0"}}})
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})

    def _next(self) -> int:
        self._id += 1
        return self._id

    def _send(self, obj: dict) -> None:
        self.proc.stdin.write(json.dumps(obj) + "\n")
        self.proc.stdin.flush()

    def _recv(self) -> dict:
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError("mcp server closed stdout")
        return json.loads(line)

    def _call(self, obj: dict) -> dict:
        self._send(obj)
        while True:
            m = self._recv()
            if m.get("id") == obj.get("id"):
                return m

    def tool(self, name: str, args: dict, timeout_s: int = 600) -> str:
        m = self._call({"jsonrpc": "2.0", "id": self._next(),
                        "method": "tools/call",
                        "params": {"name": name, "arguments": args}})
        if "error" in m:
            raise RuntimeError(json.dumps(m["error"])[:400])
        res = m.get("result", {})
        if res.get("isError"):
            txt = " ".join(b.get("text", "") for b in res.get("content", []))
            raise RuntimeError(txt[:600])
        return "\n".join(b.get("text", "") for b in res.get("content", [])
                         if b.get("type") == "text")

    def close(self) -> None:
        try:
            self.proc.terminate()
            self.proc.wait(timeout=5)
        except Exception:
            try:
                self.proc.kill()
            except Exception:
                pass


def cmd_ask(m: Mcp, notebook: str, question: str, out: str) -> int:
    text = m.tool("chat_ask", {"notebook": notebook, "question": question}, timeout_s=900)
    if out:
        fp = Path(out)
        fp = fp if fp.is_absolute() else ROOT / fp
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(f"# NotebookLM answer {time.strftime('%Y-%m-%d %H:%M')}\n\n"
                      f"## Question\n\n{question}\n\n## Answer\n\n{text}\n",
                      encoding="utf-8")
        print(f"saved {fp}")
    else:
        print(text)
    return 0


def cmd_add_file(m: Mcp, notebook: str, path: str, wait: bool) -> int:
    text = m.tool("source_add", {"notebook": notebook, "source_type": "file",
                                 "path": str(path), "wait": wait}, timeout_s=900)
    print(text)
    return 0


def cmd_list_sources(m: Mcp, notebook: str) -> int:
    print(m.tool("source_list", {"notebook": notebook}))
    return 0


def cmd_auto(m: Mcp, notebook: str, scope: str, project: str, sessions: int) -> int:
    stamp = time.strftime("%Y%m%d-%H%M")
    pack = ROOT / "scripts" / "out" / f"notebook-{scope}-{stamp}.txt"
    sys.path.insert(0, str(ROOT / "scripts"))
    from build_notebook_pack import _header, _workspace_part, _sessions_part, _grill_part, _expert_slot
    import build_context_txt as ctx
    parts = [_header(scope, project, sessions, 2),
             _workspace_part(scope, project, 2)]
    shelf_b, _ = _sessions_part(sessions, 15_000)
    parts += [shelf_b, _grill_part(scope, project), _expert_slot()]
    text = "\n".join(parts) + f"\n{'=' * 70}\n[token estimate: ~{ctx.tok_estimate(chr(10).join(parts))}]\n"
    pack.parent.mkdir(parents=True, exist_ok=True)
    pack.write_text(text, encoding="utf-8")
    print(f"built pack: {pack.name}")

    from agent_sessions import get_all_sessions, _safe_name, _session_header
    sdir = ROOT / "scripts" / "out" / f"sessions-{stamp}"
    sdir.mkdir(parents=True, exist_ok=True)
    latest = get_all_sessions(limit_per_agent=10)[:sessions]
    files = [pack]
    for i, s in enumerate(latest, 1):
        fp = sdir / f"{i:02d}_{s.agent}_{_safe_name(s)}.md"
        fp.write_text(_session_header(s, i, len(latest)) + (s.text_markdown or "(empty)"),
                      encoding="utf-8")
        files.append(fp)
    print(f"exported {len(latest)} sessions")

    failed = 0
    for f in files:
        try:
            out = m.tool("source_add", {"notebook": notebook, "source_type": "file",
                                        "path": str(f), "wait": True}, timeout_s=900)
            print(f"  + {f.name}: {out[:150]}")
        except Exception as e:  # noqa: BLE001 — push the rest, report at end
            print(f"  ! {f.name}: {e}")
            failed += 1
    print("OK: all registered" if failed == 0 else f"FAILED: {failed}")
    return 0 if failed == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="NotebookLM over MCP (no browser).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("ask")
    p.add_argument("-n", "--notebook", default=DEFAULT_NOTEBOOK)
    p.add_argument("question")
    p.add_argument("--json-out", default="", dest="out")
    p = sub.add_parser("add-file")
    p.add_argument("-n", "--notebook", default=DEFAULT_NOTEBOOK)
    p.add_argument("path")
    p.add_argument("--wait", action="store_true")
    p = sub.add_parser("list-sources")
    p.add_argument("-n", "--notebook", default=DEFAULT_NOTEBOOK)
    p = sub.add_parser("auto")
    p.add_argument("-n", "--notebook", default=DEFAULT_NOTEBOOK)
    p.add_argument("--scope", choices=["root", "project"], default="root")
    p.add_argument("--project", default="")
    p.add_argument("--sessions", type=int, default=5)
    args = ap.parse_args()

    if not MCP_BIN.is_file():
        print(f"MCP server missing: {MCP_BIN}")
        return 1
    m = Mcp()
    try:
        if args.cmd == "ask":
            return cmd_ask(m, args.notebook, args.question, args.out)
        if args.cmd == "add-file":
            return cmd_add_file(m, args.notebook, args.path, args.wait)
        if args.cmd == "list-sources":
            return cmd_list_sources(m, args.notebook)
        if args.cmd == "auto":
            return cmd_auto(m, args.notebook, args.scope, args.project, args.sessions)
    finally:
        m.close()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
