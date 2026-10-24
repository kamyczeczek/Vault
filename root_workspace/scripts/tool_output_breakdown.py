"""Break tool-result volume down by tool name, and estimate the addressable share.

jCodeMunch replaces `read` on source files. It does NOT replace `bash`/`grep`
output. So the honest question is: what fraction of tool-result characters in my
own sessions came from reads of source files, versus shell output and everything
else? Only the first part is addressable by symbol-level retrieval.

Usage: python3 scripts/tool_output_breakdown.py [--since 60d] [--cwd SUBSTR]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

SESSIONS = Path.home() / ".pi" / "agent" / "sessions"
SOURCE_SUFFIX = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".rs", ".go", ".java", ".c", ".h",
    ".cpp", ".hpp", ".cs", ".rb", ".php", ".swift", ".kt", ".scala", ".sh",
    ".sql", ".lua", ".m", ".mm", ".ex", ".exs", ".zig", ".dart", ".jl", ".r",
}
DOC_SUFFIX = {".md", ".txt", ".rst"}


def _raw_len(content) -> int:
    if content is None:
        return 0
    if isinstance(content, str):
        return len(content)
    try:
        return len(json.dumps(content))
    except (TypeError, ValueError):
        return len(str(content))


def parse_since(spec: str) -> float:
    if spec.endswith("d"):
        return (datetime.now(timezone.utc) - timedelta(days=int(spec[:-1]))).timestamp()
    if spec.endswith("h"):
        return (datetime.now(timezone.utc) - timedelta(hours=int(spec[:-1]))).timestamp()
    return 0.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="60d")
    ap.add_argument("--cwd", default="")
    args = ap.parse_args()
    since = parse_since(args.since)
    since_label = args.since

    by_tool = defaultdict(int)
    calls_by_tool = defaultdict(int)
    read_source = 0
    read_doc = 0
    read_other = 0
    read_source_calls = 0
    total = 0

    for path in SESSIONS.rglob("*.jsonl"):
        if path.parent.parent != SESSIONS:
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        # map toolCallId -> (toolName, path argument) so results can be attributed
        call_meta: dict[str, tuple[str, str]] = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("type") == "message":
                m = rec.get("message") or {}
                role = m.get("role")
                if role == "assistant":
                    content = m.get("content")
                    if isinstance(content, list):
                        for b in content:
                            if isinstance(b, dict) and b.get("type") == "toolCall":
                                args = b.get("arguments") or {}
                                call_meta[str(b.get("id"))] = (
                                    str(b.get("name") or ""),
                                    str(args.get("path") or ""),
                                )
                elif role == "toolResult":
                    name = str(m.get("toolName") or rec.get("toolName") or "?")
                    cid = str(m.get("toolCallId") or rec.get("toolCallId") or "")
                    n = _raw_len(m.get("content") if m.get("content") is not None else m.get("output"))
                    by_tool[name] += n
                    calls_by_tool[name] += 1
                    total += n
                    if name == "read":
                        src_path = call_meta.get(cid, ("read", ""))[1]
                        suf = Path(src_path).suffix.lower()
                        if suf in SOURCE_SUFFIX:
                            read_source += n
                            read_source_calls += 1
                        elif suf in DOC_SUFFIX:
                            read_doc += n
                        else:
                            read_other += n

    if not total:
        print("no tool results found")
        return 0

    print(f"total tool-result characters: {total:,}   since {since_label}\n")
    print(f"{'tool':<24}{'calls':>8}{'chars':>13}{'share':>9}")
    for name, n in sorted(by_tool.items(), key=lambda kv: -kv[1]):
        print(f"{name[:22]:<24}{calls_by_tool[name]:>8}{n:>13,}{100.0 * n / total:>8.1f}%")

    print()
    print(f"reads of SOURCE files: {read_source:,} chars over {read_source_calls} calls"
          f"  ({100.0 * read_source / total:.1f}% of all tool output)")
    print(f"reads of DOC files:    {read_doc:,} chars  ({100.0 * read_doc / total:.1f}%)")
    print(f"reads of other:        {read_other:,} chars  ({100.0 * read_other / total:.1f}%)")
    print()
    addr = 100.0 * read_source / total
    print(f"ADDRESSABLE by symbol-level retrieval (source reads only): {addr:.1f}%")
    print(f"  at a 70% reduction on those reads -> {read_source * 0.7:,} chars saved"
          f" ({100.0 * read_source * 0.7 / total:.1f}% of all tool output)")
    print(f"  NOT addressable: shell/test/git output = "
          f"{100.0 * (total - read_source - read_doc) / total:.1f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())