#!/usr/bin/env bash
# run_and_rc.sh — run a command, print its last N output lines, report the REAL exit code.
#
# Usage:
#   bash scripts/_scratch/run_and_rc.sh [-n LINES] <command...>
#   bash scripts/_scratch/run_and_rc.sh -n 50 python scripts/ingest.py
#
# Why: `cmd | tail -20; echo "exit=$?"` reports the PIPE's exit code (always 0),
# not cmd's — documented in HANDOFF.md § Gotchas. This wrapper captures cmd's
# exit code directly, so a failed command can never masquerade as success.
set -u
n=30
if [ "${1:-}" = "-n" ]; then n="$2"; shift 2; fi
out=$("$@" 2>&1); rc=$?
[ -n "$out" ] && printf '%s\n' "$out" | tail -n "$n"
echo "[run_and_rc] rc=$rc :: $*"
exit "$rc"
