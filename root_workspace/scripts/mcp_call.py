"""Call a tool on an MCP server over stdio and report the payload size.

Used to verify claims empirically: the point of symbol-level retrieval is a
small, precise payload, so every call prints the returned character count next
to the tokenizer estimate. A call that returns a whole file fails the test.

Usage:
  python3 scripts/mcp_call.py jcodemunch-mcp search_symbols '{"query":"build_project_map","max_results":5}'
  python3 scripts/mcp_call.py jcodemunch-mcp get_symbol_source '{"repo":"...","path":"scripts/build_project_map.py","symbol":"main"}' --show 400
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys

CHARS_PER_TOKEN = 3.5


def call(command: list[str], tool: str, args: dict, timeout: int = 300) -> tuple[str, bool]:
    proc = subprocess.Popen(
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", errors="replace", bufsize=1,
    )

    def send(obj: dict) -> None:
        proc.stdin.write(json.dumps(obj) + "\n")
        proc.stdin.flush()

    def recv() -> dict:
        line = proc.stdout.readline()
        if not line:
            raise RuntimeError("server closed stdout")
        return json.loads(line)

    try:
        send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
              "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                         "clientInfo": {"name": "probe", "version": "0"}}})
        while True:
            m = recv()
            if m.get("id") == 1:
                break
        send({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
        send({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
              "params": {"name": tool, "arguments": args}})
        while True:
            m = recv()
            if m.get("id") == 2:
                break
        if "error" in m:
            return json.dumps(m["error"], indent=2), True
        result = m.get("result", {})
        parts = []
        for blk in result.get("content", []):
            if blk.get("type") == "text":
                parts.append(blk.get("text", ""))
        return "\n".join(parts), bool(result.get("isError"))
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("server")
    ap.add_argument("tool")
    ap.add_argument("args", nargs="?", default="{}")
    ap.add_argument("--show", type=int, default=1200)
    args = ap.parse_args()

    try:
        payload = json.loads(args.args)
    except json.JSONDecodeError as exc:
        print(f"bad args json: {exc}", file=sys.stderr)
        return 1

    text, is_err = call([args.server], args.tool, payload)
    chars = len(text)
    tokens = int(chars / CHARS_PER_TOKEN) + 1
    status = "ERROR" if is_err else "ok"
    print(f"--- {args.tool} [{status}] ---")
    print(f"payload: {chars:,} chars  ~= {tokens:,} tokens")
    print(f"first {args.show} chars:")
    print(text[: args.show])
    if chars > args.show:
        print(f"\n...[{chars - args.show:,} more chars]")
    return 0


if __name__ == "__main__":
    sys.exit(main())