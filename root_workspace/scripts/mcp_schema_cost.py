"""Measure the token cost of an MCP server's tool surface in the system prefix.

Every MCP tool's name + description + JSON schema is sent on EVERY request for
the life of the session. This script does a real MCP handshake, lists tools, and
reports the token cost of that schema block, plus the cost of the top-N tools the
agent will actually use.

Usage:
  python3 scripts/mcp_schema_cost.py jcodemunch-mcp
  python3 scripts/mcp_schema_cost.py jcodemunch-mcp --top 8
  python3 scripts/mcp_schema_cost.py --json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Rough tokens-per-char for tool schema JSON. JSON with many short keys and
# quoted names tokenizes denser than prose; 3.5 is a mid estimate, and the
# conclusion here does not flip between 3.0 and 4.0.
CHARS_PER_TOKEN = 3.5


def handshake(command: list[str], cwd: str | None, timeout: int = 240) -> list[dict]:
    """Minimal stdio JSON-RPC MCP handshake: initialize + tools/list."""
    proc = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )

    def send(obj: dict) -> None:
        assert proc.stdin is not None
        proc.stdin.write(json.dumps(obj) + "\n")
        proc.stdin.flush()

    def recv() -> dict:
        assert proc.stdout is not None
        line = proc.stdout.readline()
        if not line:
            raise RuntimeError("server closed stdout")
        return json.loads(line)

    try:
        send({
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "schema-cost", "version": "0"},
            },
        })
        while True:
            msg = recv()
            if msg.get("id") == 1:
                break
        send({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
        send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        while True:
            msg = recv()
            if msg.get("id") == 2:
                break
        return msg.get("result", {}).get("tools", [])
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


def tok(obj) -> int:
    return int(len(json.dumps(obj)) / CHARS_PER_TOKEN) + 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("server", nargs="?", default="jcodemunch-mcp")
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        tools = handshake([args.server], None)
    except Exception as exc:  # noqa: BLE001
        print(f"handshake failed: {exc}", file=sys.stderr)
        return 1

    if not tools:
        print("no tools returned")
        return 1

    desc_chars = sum(len(t.get("description") or "") for t in tools)
    schema_chars = len(json.dumps([t.get("inputSchema") for t in tools]))
    name_chars = sum(len(t.get("name") or "") for t in tools)
    total_chars = len(json.dumps(tools))

    rows = []
    for t in tools:
        rows.append(
            {
                "name": t.get("name"),
                "tokens": tok(t),
                "desc": len(t.get("description") or ""),
                "schema": len(json.dumps(t.get("inputSchema") or {})),
            }
        )
    rows.sort(key=lambda r: -r["tokens"])

    result = {
        "server": args.server,
        "tool_count": len(tools),
        "total_tokens": tok(tools),
        "total_chars": total_chars,
        "name_chars": name_chars,
        "description_chars": desc_chars,
        "schema_chars": schema_chars,
        "top": rows[: args.top],
    }
    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    print(f"server        {args.server}")
    print(f"tools         {len(tools)}")
    print(f"schema block  {total_chars:,} chars  ~= {tok(tools):,} tokens  ON EVERY REQUEST")
    print(f"  names       {name_chars:,} chars")
    print(f"  descriptions {desc_chars:,} chars")
    print(f"  json schema {schema_chars:,} chars")
    print()
    print(f"largest {min(args.top, len(rows))} tools by prefix cost:")
    print(f"{'tool':<40}{'tokens':>8}{'descChr':>9}{'schemaChr':>11}")
    for r in rows[: args.top]:
        print(f"{str(r['name'])[:38]:<40}{r['tokens']:>8}{r['desc']:>9}{r['schema']:>11}")

    top_sum = sum(r["tokens"] for r in rows[: args.top])
    print()
    print(f"the {args.top} tools you would actually use: {top_sum:,} tokens "
          f"= {100.0 * top_sum / max(tok(tools), 1):.1f}% of the block")
    print(f"the other {len(tools) - args.top}: {tok(tools) - top_sum:,} tokens of dead weight")
    return 0


if __name__ == "__main__":
    sys.exit(main())