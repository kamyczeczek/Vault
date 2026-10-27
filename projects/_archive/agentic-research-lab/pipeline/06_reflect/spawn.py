#!/usr/bin/env python3
"""
spawn.py — Spawn an isolated reflection agent for the workspace-research KB.

The reflection agent receives the graph digest through the configured
workspace-research extension. Spawn fails before launch if that extension is
unavailable. The agent is read-only on source and writes only to
reflection/digests/ and reflection/candidates/.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
try:
    from agent_trace import emit as emit_trace, new_run_id
except ImportError:
    emit_trace = None
    def new_run_id(prefix: str = "run") -> str:
        return f"{prefix}-{int(time.time() * 1000)}"
GRAPH_DIGEST = ROOT / "knowledge" / "graph" / "GRAPH-DIGEST.md"
EXTENSION_ENV = "OMP_WORKSPACE_RESEARCH_EXTENSION"
DEFAULT_EXTENSION = ROOT / ".omp" / "extensions" / "workspace-research.ts"
REFLECT_DIGESTS = ROOT / "reflection" / "digests"
REFLECT_CANDIDATES = ROOT / "reflection" / "candidates"
# Verification runs write here instead of the graded corpus. Decided before a
# test runs, not after a gate goes red: a smoke test's artifacts are proof the
# pipeline works, not research output, and grading their prose as slop would make
# the gate's verdict depend on how many tests ran this week. The separation is
# structural (different output directory) rather than a filter on the real one,
# because a filter added after a failure is a scope change wearing a fix's
# clothes. Grading is unaffected — these files are still fully checked by
# `check_reflection.py --paths <slug>`, and they are still never deleted.
SCRATCH_DIGESTS = ROOT / "reflection" / "scratch" / "digests"
SCRATCH_CANDIDATES = ROOT / "reflection" / "scratch" / "candidates"
EVENTS_FILE = ROOT / "reflection" / "events.jsonl"
LOOP_STATE_FILE = ROOT / "reflection" / "loop_state.json"
TIMINGS_DIR = ROOT / "reflection" / "timings"
MAX_IDENTICAL_EVENTS = 3
LOOP_WINDOW = 12


def record_stage(stages: dict, name: str, started: float) -> None:
    """Record one stage's wall-clock in ms so latency regressions are measurable."""
    stages[name] = round((time.perf_counter() - started) * 1000.0, 1)


def write_timings(topic: str, run_id: str, stages: dict) -> None:
    """Persist per-stage wall-clock (foreground runs). Telemetry, never blocks launch."""
    try:
        TIMINGS_DIR.mkdir(parents=True, exist_ok=True)
        total = round(sum(stages.values()), 1)
        (TIMINGS_DIR / f"{topic}.json").write_text(
            json.dumps({"topic": topic, "run_id": run_id, "stages": stages, "total_ms": total},
                       indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        print(f"[spawn] failed to record timings: {exc}", file=sys.stderr)


def loop_guard(event: str, **fields: object) -> bool:
    """Detect repeated identical spawn events and request escalation."""
    import hashlib
    try:
        state = json.loads(LOOP_STATE_FILE.read_text(encoding="utf-8")) if LOOP_STATE_FILE.exists() else {"events": []}
        signature = hashlib.sha256(json.dumps({"event": event, **fields}, sort_keys=True, default=str).encode()).hexdigest()
        history = state.get("events", [])[-(LOOP_WINDOW - 1):]
        repeats = sum(1 for item in history if item == signature)
        history.append(signature)
        LOOP_STATE_FILE.write_text(json.dumps({"events": history}, indent=2) + "\n", encoding="utf-8")
        if repeats >= MAX_IDENTICAL_EVENTS - 1:
            print(f"[spawn] loop guard blocked repeated event: {event}", file=sys.stderr)
            return False
    except (OSError, ValueError, TypeError):
        # Telemetry must never prevent a valid launch when state is unavailable.
        return True
    return True


def emit_event(event: str, **fields: object) -> None:
    """Append an observable spawn/escalation event without blocking launch."""
    if not loop_guard(event, **fields):
        raise RuntimeError(f"loop guard blocked repeated event: {event}")
    payload = {"t": time.time(), **fields}
    payload["event"] = event
    try:
        EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with EVENTS_FILE.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except OSError as exc:
        print(f"[spawn] failed to record event {event!r}: {exc}", file=sys.stderr)


def resolve_extension_path(configured: str | None = None) -> Path:
    """Resolve the extension relative to ROOT; absolute paths are accepted."""
    value = configured if configured is not None else os.environ.get(EXTENSION_ENV)
    path = Path(value).expanduser() if value is not None else DEFAULT_EXTENSION
    if not path.is_absolute():
        path = ROOT / path
    return path.resolve()



REFLECTION_PROMPT = """You are a reflection agent for the Workspace-Research context-engineering / ICM
knowledge base. You are operating under an explicit planner/executor split.

ROLE CONTRACT
- PLANNER: choose deterministic topic tags, retrieve chunk ids, define the claim structure, and specify evidence.
- EXECUTOR: read only planner-selected chunks, verify each citation, and write the digest/candidates.
- The executor MUST NOT change the plan, broaden retrieval, or invent uncited evidence.
- If the plan cannot be executed deterministically, emit a terminal `ESCALATE` record with fields
  `condition`, `reason`, and `correction`; do not retry indefinitely or write a partial artifact.

The configured workspace-research extension auto-injects the project's knowledge graph digest before agent start.
REFLECTION TOPIC: {topic}
GRAPH DIGEST (direct payload; the extension also auto-injects the same source): {digest}
PLAN PHASE: {phase} (from pipeline/WORKFLOW.md) — fingerprint {fingerprint}, plan_version {plan_version}
ROUTING: deterministic tag-intersection via route.py --tag; same tags+fingerprint => same ids.
COMPACTION GUARD (P3): If context was truncated, re-inject: stages/04_reflect/CONTEXT.md Inputs Table + pipeline/WORKFLOW.md current phase header above. Every N tool calls, restate current phase.

DETERMINISTIC ROUTING CONTRACT (you MUST follow this; no free recall):
1. Route ONLY by ICM topic tags from knowledge/topics.md. For each topic tag set,
   run EXACT tag-intersection queries:
     python knowledge/graph/ask.py --tag <tag1> --tag <tag2> --limit 12
   If cardinality < threshold, retry one level via route.py --threshold 3 alias split (decomposition/htn/pddl/classical-planning) — depth logged.
   This returns the reproducible set of chunk ids sharing ALL given tags.
2. Expand a top chunk via graph edges if needed (REFERS_TO / SHARES_TAG in graph.db).
3. Every claim you write MUST cite >=1 chunk id returned by the queries above.
4. Do NOT browse knowledge/corpus/ for ideas — ground in query results.

OUTPUTS (write to these two paths ONLY; never edit source or corpus):
  Use the filename slug "{topic}" for both outputs below.
  1. {digests_dir}{topic}.md — sections: Claim / Evidence / Decision / Next bet. MUST start with provenance stamp.
  2. {candidates_dir}{topic}.jsonl — one JSON object per candidate with state proposed and grounded evidence.
  State machine: proposed -> experimental -> accepted | rejected.

CANDIDATE SCHEMA (exact key names, capitalised — check_reflection.py rejects any other spelling):
  Every line of {topic}.jsonl is one JSON object with EXACTLY these keys:
    "id"        — slug, e.g. "entropy-001-<short-name>"
    "state"     — MUST be "proposed"
    "type"      — "candidate"
    "date"      — YYYY-MM-DD
    "Rule"      — the generalising claim (pattern level, not a single instance)
    "Evidence"  — comma-separated chunk ids in backticks: `id_one`, `id_two`
    "Target"    — the file/contract this rule bears on
    "Action"    — the concrete correction to apply
    "Condition" — when the rule fires
    "Reason"    — why it is true
    "Correction"— what to do instead
  FORBIDDEN: lowercase "evidence"/"rule"/"action"/"target", and any extra alias key.
  Note: `attach_trace_provenance` backfills provenance.fingerprint / plan_version / phase
  deterministically after you write. You must NOT hand-author those.

If execution fails, output exactly one JSON object to `reflection/escalations.jsonl`:
{{"event":"ESCALATE","condition":"...","reason":"...","correction":"...","topic":"{topic}"}}


"""


def live_provenance() -> tuple[str, str]:
    """Read the live graph fingerprint and current WORKFLOW.md plan_version.

    Single source of truth for the deterministic provenance fields, so the
    foreground and background paths cannot drift apart.
    """
    import hashlib
    fp_file = ROOT / "knowledge" / "graph" / ".graph_fingerprint"
    live_fp = fp_file.read_text(encoding="utf-8").strip() if fp_file.exists() else ""
    if not live_fp and GRAPH_DIGEST.exists():
        for line in GRAPH_DIGEST.read_text(encoding="utf-8").splitlines():
            match = re.search(r"fingerprint:\s*([0-9a-f]{12})", line)
            if match:
                live_fp = match.group(1)
                break
    workflow = ROOT / "pipeline" / "WORKFLOW.md"
    plan_ver = hashlib.sha256(workflow.read_bytes()).hexdigest()[:12] if workflow.exists() else ""
    return live_fp, plan_ver


def attach_trace_provenance(candidate_path: Path, run_id: str) -> None:
    """Attach operational trace references without changing graph fingerprints.

    Also backfills the *deterministic* provenance fields (fingerprint,
    plan_version, phase) that check_reflection.py requires. The agent is not
    trusted to supply these: a run whose digest omitted the stamp would
    otherwise never pass the gate, and the failure would be blamed on the model
    instead of on the missing deterministic step.
    """
    live_fp, plan_ver = live_provenance()
    trace_file = ROOT / "reflection" / "trace" / "events.jsonl"
    retrieval_ids: list[str] = []
    if trace_file.exists():
        for line in trace_file.read_text(encoding="utf-8").splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("run_id") == run_id and event.get("kind") == "retrieval":
                retrieval_ids.append(event["event_id"])
    rows: list[dict] = []
    route_payload = None
    for line in candidate_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            obj = json.loads(line)
            route_payload = (obj.get("provenance") or {}).get("route") or route_payload
            rows.append(obj)
    if not retrieval_ids and route_payload and emit_trace:
        retrieval_ids.append(emit_trace("retrieval", run_id=run_id, route=route_payload,
                                        returned_ids=route_payload.get("returned_ids", []),
                                        selected_ids=[], expansion_depth=len(route_payload.get("expansion_traces", []))))
    for obj in rows:
        provenance = obj.setdefault("provenance", {})
        provenance["run_id"] = run_id
        provenance["retrieval_event_ids"] = retrieval_ids
        provenance.setdefault("fingerprint", live_fp)
        provenance.setdefault("plan_version", plan_ver)
        provenance.setdefault("phase", "04_reflect")
    candidate_path.write_text("\n".join(json.dumps(obj, ensure_ascii=False) for obj in rows) + ("\n" if rows else ""), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--since", help="only reflect on corpus added since ISO date (advisory)")
    ap.add_argument("--topic", required=True, help="reflection topic slug; used for output filenames")
    ap.add_argument("--extension", help="workspace-research extension path (relative paths resolve from ROOT)")
    ap.add_argument("--timeout", type=int, default=0,
                    help="agent timeout in seconds (default 900; 0 = use OMP_SPAWN_TIMEOUT or default)")
    ap.add_argument("--background", action="store_true", help="run reflection agent in background (non-blocking)")
    ap.add_argument("--scratch", action="store_true",
                    help="write artifacts to reflection/scratch/ — for verification runs, not research")
    args = ap.parse_args()
    topic = (args.topic or "reflection").strip().replace(" ", "_")
    run_id = new_run_id("reflect")
    os.environ["AGENT_TRACE_RUN_ID"] = run_id
    if emit_trace:
        emit_trace("run", run_id=run_id, status="started", workflow="06_reflect", topic=topic)
    extension = resolve_extension_path(args.extension)
    if not extension.is_file():
        reason = f"configured extension is not a file: {extension}"
        print(f"[spawn] ESCALATE: {reason}", file=sys.stderr)
        emit_event(
            "ESCALATE",
            condition="extension_missing",
            reason=reason,
            correction="install the workspace-research extension or pass --extension with its path",
            topic=topic,
        )
        return 4

    workflow = ROOT / "pipeline" / "WORKFLOW.md"
    plan_version = ""
    if workflow.exists():
        import hashlib
        plan_version = hashlib.sha256(workflow.read_bytes()).hexdigest()[:12]
    phase = "04_reflect"
    emit_event("spawn", topic=topic, plan_version=plan_version)
    # determinism gate also validates phase via WORKFLOW.md presence
    if not workflow.exists():
        print(f"WORKFLOW.md missing — create pipeline/WORKFLOW.md (P1) before reflecting", file=sys.stderr)
        return 1

    # W1: hard determinism gate — refuse to spawn on stale digest
    stages: dict = {}
    t_gate = time.perf_counter()
    watch = subprocess.run([sys.executable, str(ROOT / "knowledge" / "graph" / "watch.py"), "--once"],
                           text=True, capture_output=True)
    fp_file = ROOT / "knowledge" / "graph" / ".graph_fingerprint"
    digest_fp = ""
    if GRAPH_DIGEST.exists():
        for line in GRAPH_DIGEST.read_text(encoding="utf-8").splitlines():
            if "fingerprint:" in line:
                import re
                m = re.search(r"fingerprint:\s*([0-9a-f]{12})", line)
                if m:
                    digest_fp = m.group(1)
                break
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
    record_stage(stages, "pre_gates", t_gate)

    digest = GRAPH_DIGEST.read_text(encoding="utf-8").strip()[:6000]
    # inject phase CONTEXT for P3 reminder contract
    stage_context = ROOT / "stages" / "04_reflect" / "CONTEXT.md"
    stage_hint = stage_context.read_text(encoding="utf-8").strip()[:1500] if stage_context.exists() else "(stage CONTEXT missing)"
    # append stage hint to digest so agent can re-anchor without extra fetch
    digest_with_hint = digest + f"\n\n--- Current phase CONTEXT (P3 re-injection source) ---\n{stage_hint}\n"
    out_digests, out_candidates = (SCRATCH_DIGESTS, SCRATCH_CANDIDATES) if args.scratch else (REFLECT_DIGESTS, REFLECT_CANDIDATES)
    prompt = REFLECTION_PROMPT.format(
        topic=topic, digest=digest_with_hint, phase=phase,
        fingerprint=live_fp or digest_fp, plan_version=plan_version,
        digests_dir=out_digests.relative_to(ROOT).as_posix() + "/",
        candidates_dir=out_candidates.relative_to(ROOT).as_posix() + "/",
    )
    out_digests.mkdir(parents=True, exist_ok=True)
    out_candidates.mkdir(parents=True, exist_ok=True)

    # omp is a Node/Bun CLI (NOT a python module). Use the native `omp.exe`
    # from the user's .bun dir — never the npm shim `omp.cmd` (not a valid
    # Win32 app for subprocess). Fall back to PATH if not installed there.
    #
    # omp/18.2 has no `agent` subcommand. `omp agent ...` parses as
    # `omp launch` (the default command) with the literal "agent" as its
    # message, so it sat waiting on interactive input and hung every spawn.
    # The correct non-interactive form is `omp launch -p`.
    bun_omp = os.path.join(os.path.expanduser("~"), ".bun", "bin", "omp.exe")
    if os.path.exists(bun_omp):
        omp_bin = bun_omp
    elif shutil.which("omp.exe"):
        omp_bin = shutil.which("omp.exe")
    else:
        omp_bin = shutil.which("omp") or "omp"
    cmd = [
        omp_bin, "launch",
        "--cwd", str(ROOT),
        "--extension", str(extension),
        "-p", prompt,
        "--no-session",
    ]
    print(f"[spawn] launching reflection agent (cwd={ROOT})")
    print(f"[spawn] inject digest chars={len(digest)}")
    timeout_seconds = int(getattr(args, "timeout", 0) or
                        (os.environ.get("OMP_SPAWN_TIMEOUT") or 1200))
    if args.background:
        worker_script = ROOT / "pipeline" / "06_reflect" / "background_worker.py"
        worker_cmd = [
            sys.executable, str(worker_script),
            "--topic", topic,
            "--extension", str(extension),
            "--timeout", str(timeout_seconds),
            "--run-id", run_id,
        ]
        if args.scratch:
            worker_cmd.append("--scratch")
        creationflags = 0
        if os.name == "nt":
            creationflags = 0x00000008 | 0x00000200 # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        # Redirect the worker's own stdout/stderr into the same log the agent uses.
        # With DETACHED_PROCESS the worker otherwise inherits the parent's console
        # handles; when that parent exits the handles die and the worker is killed
        # mid-run, taking the lock and status file with it (observed: 0-byte status,
        # orphaned lock, no traceback anywhere).
        logs_dir = ROOT / "reflection" / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        worker_log = (logs_dir / f"{topic}.log").open("a", encoding="utf-8")
        p = subprocess.Popen(worker_cmd, stdout=worker_log, stderr=subprocess.STDOUT,
                             stdin=subprocess.DEVNULL, creationflags=creationflags)
        worker_log.close()
        print(f"[spawn] launched reflection supervisor in background (PID {p.pid}, log: reflection/logs/{topic}.log)")
        if emit_trace:
            emit_trace("run", run_id=run_id, status="background_spawned", workflow="06_reflect", topic=topic, pid=p.pid)
        return 0

    t_agent = time.perf_counter()
    try:
        proc = subprocess.run(cmd, text=True, input="", timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        escalation = {
            "event": "ESCALATE",
            "condition": "reflection_timeout",
            "reason": f"reflection agent exceeded {timeout_seconds}s",
            "correction": "inspect the deterministic route and retry only after reducing scope",
            "topic": topic,
        }
        try:
            with (ROOT / "reflection" / "escalations.jsonl").open("a", encoding="utf-8") as f:
                f.write(json.dumps(escalation) + "\n")
        except OSError:
            pass
        emit_event("escalate", **{key: value for key, value in escalation.items() if key != "event"})
        if emit_trace:
            emit_trace("failure", run_id=run_id, status="failed", module="reflection", failure_kind="timeout", condition=escalation["condition"], correction=escalation["correction"])
        print(f"[spawn] ESCALATE: {escalation['reason']}", file=sys.stderr)
        record_stage(stages, "agent", t_agent)
        write_timings(topic, run_id, stages)
        return 3
    record_stage(stages, "agent", t_agent)
    if proc.returncode:
        emit_event("escalate", condition="reflection_process_failure",
                   reason=f"agent exited with {proc.returncode}",
                   correction="inspect agent output before retrying", topic=topic)
        if emit_trace:
            emit_trace("failure", run_id=run_id, status="failed", module="system", failure_kind="process_failure", artifact=f"{out_digests.relative_to(ROOT).as_posix()}/{topic}.md")
    else:
        t_validation = time.perf_counter()
        candidate_path = out_candidates / f"{topic}.jsonl"
        if candidate_path.exists():
            attach_trace_provenance(candidate_path, run_id)
            validator = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "candidate_writer.py"), str(candidate_path)],
                text=True, capture_output=True
            )
            print(validator.stdout.strip())
            if validator.returncode not in (0, 2):
                print(validator.stderr, file=sys.stderr)
                if emit_trace:
                    emit_trace("validation", run_id=run_id, status="failed", gate="candidate_writer", artifact=str(candidate_path.relative_to(ROOT)))
                return 1
            # vera-expa-004: AgentDebug root-cause stage — classify every
            # quarantined candidate (retrieval_miss / grounding_gap /
            # logical_inconsistency / tool_misuse) before the run is counted
            # complete, so correction targets the attributed root cause.
            record_stage(stages, "validation", t_validation)
            t_attribution = time.perf_counter()
            attrib = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "root_cause_attribution.py"), str(candidate_path)],
                text=True, capture_output=True
            )
            print(attrib.stdout.strip())
            record_stage(stages, "attribution", t_attribution)
            # Emit one typed event summarising attribution for this topic; the
            # structured per-candidate diagnostics live in reflection/diagnostics/.
            n_attrib = len([l for l in attrib.stdout.splitlines() if l.startswith("  ") and ": " in l])
            if n_attrib:
                emit_event("root_cause", topic=topic, candidates_attributed=n_attrib,
                           diagnostics=f"reflection/diagnostics/{topic}_root_cause.jsonl")
            if emit_trace:
                emit_trace("validation", run_id=run_id, status="completed", gate="root_cause_attribution",
                           artifact="reflection/diagnostics")
            if emit_trace:
                emit_trace("artifact", run_id=run_id, status="validated", artifact=str(candidate_path.relative_to(ROOT)), artifact_type="candidate", retrieval_event_ids=[os.environ["AGENT_TRACE_LAST_RETRIEVAL"]] if os.environ.get("AGENT_TRACE_LAST_RETRIEVAL") else [])
        if emit_trace:
            emit_trace("run", run_id=run_id, status="completed", workflow="06_reflect", topic=topic,
                       artifacts=[f"{out_digests.relative_to(ROOT).as_posix()}/{topic}.md", f"{out_candidates.relative_to(ROOT).as_posix()}/{topic}.jsonl"])
    write_timings(topic, run_id, stages)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
