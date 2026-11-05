"""provenance_logger.py — a real CLI, so the hook records what happened.

The previous version had no argument parsing at all. `hook_post_tool.py`
shells out to it as

    provenance_logger.py record-tool --tool X --payload Y

but every argv fell through to a hardcoded self-test that called
record_step("tool_use", "ast_boundary_linter", {"scope": "scripts"}, ...).
So every tool invocation in the workspace appended a *fabricated* row
claiming the AST linter had run. A ledger that invents its own entries is
worse than no ledger: it is an audit trail that attests to things that never
happened. Hence argparse, and a default that refuses rather than invents.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "reflection" / "provenance_ledger.jsonl"
GENESIS_HASH = "0" * 64
MAX_SUMMARY = 500


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _entries() -> list[str]:
    if not LEDGER_PATH.exists():
        return []
    return [ln.strip() for ln in LEDGER_PATH.read_text(encoding="utf-8").splitlines() if ln.strip()]


def _get_last_hash() -> str:
    """Last hash in the chain, or genesis. A corrupt tail is reported by
    verify_chain(); here it must not silently restart the chain."""
    entries = _entries()
    if not entries:
        return GENESIS_HASH
    try:
        return str(json.loads(entries[-1]).get("entry_hash", GENESIS_HASH))
    except json.JSONDecodeError:
        return GENESIS_HASH


def record_step(
    action_type: str,
    tool_name: str,
    inputs: dict | list | str | None,
    output_summary: str,
    target_files: list[str] | None = None,
) -> dict:
    """Append a cryptographically chained entry to the provenance ledger."""
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry_payload = {
        "prev_hash": _get_last_hash(),
        "timestamp": time.time(),
        "action_type": action_type,
        "tool": tool_name,
        "inputs": inputs,
        "target_files": target_files or [],
        "output_summary": output_summary[:MAX_SUMMARY],
    }
    record = {"entry_hash": _sha256(json.dumps(entry_payload, sort_keys=True)), **entry_payload}
    with LEDGER_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")
    return record


def verify_chain() -> tuple[bool, int, str]:
    """Verify hash chain integrity across all historical entries."""
    entries = _entries()
    if not entries:
        return True, 0, "Empty ledger (ok)"
    prev_expected = GENESIS_HASH
    for idx, line in enumerate(entries):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            return False, idx, f"Corrupt JSON at line {idx + 1}"
        given_hash, given_prev = entry.get("entry_hash"), entry.get("prev_hash")
        if given_prev != prev_expected:
            return False, idx, (f"Broken prev_hash link at line {idx + 1}: "
                                f"expected {prev_expected}, got {given_prev}")
        recomputed = _sha256(json.dumps({k: v for k, v in entry.items() if k != "entry_hash"},
                                       sort_keys=True))
        if recomputed != given_hash:
            return False, idx, (f"Tampered entry hash at line {idx + 1}: "
                                f"expected {recomputed}, got {given_hash}")
        prev_expected = str(given_hash)
    return True, len(entries), "All entries verified"


def _as_payload(raw: str) -> object:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def cmd_record_tool(args: argparse.Namespace) -> int:
    """The hook's entry point. Records the tool that actually ran."""
    record = record_step(
        action_type=args.action_type,
        tool_name=args.tool,
        inputs=_as_payload(args.payload),
        output_summary=args.summary or "",
        target_files=args.target or [],
    )
    print(record["entry_hash"])
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Append-only, hash-chained tool provenance.")
    sub = ap.add_subparsers(dest="command", required=True)

    rec = sub.add_parser("record-tool", help="append one entry describing a tool use")
    rec.add_argument("--tool", required=True, help="tool name, as reported by the harness")
    rec.add_argument("--payload", default="", help="tool input payload (JSON or text)")
    rec.add_argument("--summary", default="", help="short result summary")
    rec.add_argument("--action-type", default="tool_use")
    rec.add_argument("--target", action="append", help="file the tool touched (repeatable)")
    rec.set_defaults(func=cmd_record_tool)

    ver = sub.add_parser("verify", help="verify the hash chain end to end")
    ver.set_defaults(func=lambda a: _print_verify(verify_chain()))
    return ap


def _print_verify(result: tuple[bool, int, str]) -> int:
    ok, count, msg = result
    print(f"[{'OK' if ok else 'FAIL'}] {msg} ({count} records)")
    return 0 if ok else 1


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
