#!/usr/bin/env python3
"""
spawn.py — Spawn an isolated reflection agent for the workspace-research KB.

The reflection agent is auto-injected with the project's knowledge graph digest
so it reasons over the actual artifact graph, not free recall. It is read-only
on source, and writes only to reflection/digests/ and reflection/candidates/.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRAPH_DIGEST = ROOT / "knowledge" / "graph" / "GRAPH-DIGEST.md"
REFLECT_DIGESTS = ROOT / "reflection" / "digests"
REFLECT_CANDIDATES = ROOT / "reflection" / "candidates"

REFLECTION_PROMPT = """You are a reflection agent for the Workspace-Research context-engineering / ICM
knowledge base. You are auto-injected with the project's knowledge graph digest below.
REFLECTION TOPIC: {topic}
PLAN PHASE: {phase} (from pipeline/WORKFLOW.md) — fingerprint {fingerprint}, plan_version {plan_version}
ROUTING: deterministic tag-intersection via route.py --tag; same tags+fingerprint => same ids.
COMPACTION GUARD (P3): If context was truncated, re-inject: stages/04_reflect/CONTEXT.md Inputs Table + pipeline/WORKFLOW.md current phase header above. Every N tool calls, restate current phase.

DETERMINISTIC ROUTING CONTRACT (you MUST follow this; no free recall):
1. Route ONLY by ICM topic tags from knowledge/topics.md. For each topic tag set,
   run EXACT tag-intersection queries:
     python knowledge/graph/ask.py --tag <tag1> --tag <tag2> --limit 12
   If cardinality < threshold, retry one level via route.py --threshold 3 alias split (decomposition/htn/pddl/classical-planning) — depth logged.
   This returns the reproducible set of chunk ids sharing ALL given tags.
   Same tags + same graph digest => same id set. Do NOT free-associate.
2. Expand a top chunk via graph edges if needed (REFERS_TO / SHARES_TAG in graph.db).
3. Every claim you write MUST cite >=1 chunk id returned by the queries above.
   A claim with no citation is rejected. Quote the chunk id in evidence.
4. Do NOT browse knowledge/corpus/ for "ideas" — ground in query results.

OUTPUTS (write to these two paths ONLY; never edit source or corpus):
  Use the filename slug "{topic}" for both outputs below.
  1. reflection/digests/{topic}.md — sections: Claim / Evidence (chunk-id citations) /
     Decision / Next bet. MUST start with provenance stamp: `fingerprint: {fingerprint} plan_version: {plan_version} phase: {phase} routing: <queries>`
  2. reflection/candidates/{topic}.jsonl — one JSON object per candidate:
     {{"id": "<slug>", "state": "proposed", "claim": "...",
       "evidence": ["<chunk_id>", ...], "bet": "...", "provenance": {{"fingerprint": "{fingerprint}", "plan_version": "{plan_version}", "phase": "{phase}"}}}}
     State machine: proposed -> experimental -> accepted | rejected.

=== GRAPH DIGEST (auto-injected) ===
{digest}
=== END DIGEST ===
"""

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--since", help="only reflect on corpus added since ISO date (advisory)")
    ap.add_argument("--topic", required=True, help="reflection topic slug; used for output filenames")
    ap.add_argument("--timeout", type=int, default=0,
                    help="agent timeout in seconds (default 900; 0 = use OMP_SPAWN_TIMEOUT or default)")
    args = ap.parse_args()
    topic = (args.topic or "reflection").strip().replace(" ", "_")

    # P1/P5: plan version from WORKFLOW.md sha12; phase is always 04_reflect for this spawn
    workflow = ROOT / "pipeline" / "WORKFLOW.md"
    plan_version = ""
    if workflow.exists():
        import hashlib
        plan_version = hashlib.sha256(workflow.read_bytes()).hexdigest()[:12]
    phase = "04_reflect"
    # determinism gate also validates phase via WORKFLOW.md presence
    if not workflow.exists():
        print(f"WORKFLOW.md missing — create pipeline/WORKFLOW.md (P1) before reflecting", file=sys.stderr)
        return 1

    # W1: hard determinism gate — refuse to spawn on stale digest
    watch = subprocess.run([sys.executable, str(ROOT / "knowledge" / "graph" / "watch.py"), "--once"],
                           text=True, capture_output=True)
    fp_file = ROOT / "knowledge" / "graph" / ".graph_fingerprint"
    digest_fp = ""
    if GRAPH_DIGEST.exists():
        for line in GRAPH_DIGEST.read_text(encoding="utf-8").splitlines():
            if "fingerprint:" in line:
                m = __import__("re").search(r"fingerprint:\s*([0-9a-f]{12})", line)
                if m: digest_fp = m.group(1); break
    live_fp = fp_file.read_text(encoding="utf-8").strip() if fp_file.exists() else ""
    if live_fp and digest_fp and live_fp != digest_fp:
        print(f"STALE_DIGEST: .graph_fingerprint={live_fp} but GRAPH-DIGEST fingerprint={digest_fp} — rebuild required", file=sys.stderr)
        return 1
    if watch.returncode != 0:
        print(f"watch.py failed: {watch.stderr}", file=sys.stderr)
        return 1

    # P7: the stage contracts agents read as their Inputs Table must not describe a
    # graph that no longer exists. A hardcoded fingerprint in a CONTEXT.md goes stale
    # silently on the next rebuild; check_stage_contracts.py catches it now, not later.
    contracts = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_stage_contracts.py")],
                               text=True, capture_output=True)
    if contracts.returncode != 0:
        print(f"STAGE_CONTRACT_STALE: a stages/*/CONTEXT.md hardcodes a moving value\n"
              f"{contracts.stderr.strip()}", file=sys.stderr)
        return 1

    if not GRAPH_DIGEST.exists():
        print("[spawn] graph digest missing — run knowledge/graph/build_graph.py first")
        return 1

    digest = GRAPH_DIGEST.read_text(encoding="utf-8").strip()[:12000]
    # inject phase CONTEXT for P3 reminder contract
    stage_context = ROOT / "stages" / "04_reflect" / "CONTEXT.md"
    stage_hint = stage_context.read_text(encoding="utf-8").strip()[:1500] if stage_context.exists() else "(stage CONTEXT missing)"
    # append stage hint to digest so agent can re-anchor without extra fetch
    digest_with_hint = digest + f"\n\n--- Current phase CONTEXT (P3 re-injection source) ---\n{stage_hint}\n"
    prompt = REFLECTION_PROMPT.format(topic=topic, digest=digest_with_hint, phase=phase, fingerprint=live_fp or digest_fp, plan_version=plan_version)
    REFLECT_DIGESTS.mkdir(parents=True, exist_ok=True)
    REFLECT_CANDIDATES.mkdir(parents=True, exist_ok=True)

    # omp is a Node/Bun CLI (NOT a python module). Use the native `omp.exe`
    # from the user's .bun dir — never the npm shim `omp.cmd` (not a valid
    # Win32 app for subprocess). Fall back to PATH if not installed there.
    #
    # omp/18.2 has no `agent` subcommand. `omp agent ...` parses as
    # `omp launch` (the default command) with the literal "agent" as its
    # message, so it sat waiting on interactive input and hung every spawn.
    # The correct non-interactive form is `omp launch -p`.
    import os as _os
    import shutil as _shutil
    bun_omp = _os.path.join(_os.path.expanduser("~"), ".bun", "bin", "omp.exe")
    if _os.path.exists(bun_omp):
        omp_bin = bun_omp
    elif _shutil.which("omp.exe"):
        omp_bin = _shutil.which("omp.exe")
    else:
        omp_bin = _shutil.which("omp") or "omp"
    cmd = [
        omp_bin, "launch",
        "--cwd", str(ROOT),
        "--extension", str(ROOT / ".omp" / "extensions" / "workspace-research.ts"),
        "-p", prompt,
        "--no-session",
    ]
    print(f"[spawn] launching reflection agent (cwd={ROOT})")
    print(f"[spawn] inject digest chars={len(digest)}")
    # `omp launch -p` exits after printing, but keep the bounded timeout: a
    # slow model still blocks the pipeline, and killing the process tree
    import os as _os_timeout
    # Default 1200s: a full audit/reflection pass (12k digest + deterministic
    # tag routing + writing both outputs) routinely exceeds the 540s cap on
    # the default model — the agent was live and working when cut at 540s.
    # Raise via --timeout or OMP_SPAWN_TIMEOUT for larger topics.
    AGENT_TIMEOUT = int(getattr(args, "timeout", 0) or
                        _os_timeout.environ.get("OMP_SPAWN_TIMEOUT", 0) or 1200)
    try:
        proc = subprocess.run(cmd, text=True, input="", timeout=AGENT_TIMEOUT)
    except subprocess.TimeoutExpired:
        print(f"[spawn] TIMEOUT after {AGENT_TIMEOUT}s — agent produced no digest; "
              f"no orphan processes left running (tree killed)", file=sys.stderr)
        return 3
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
