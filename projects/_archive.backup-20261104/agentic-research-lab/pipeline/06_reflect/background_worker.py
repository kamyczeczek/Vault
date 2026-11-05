#!/usr/bin/env python3
"""
background_worker.py — Background execution worker for reflection spawn.
Handles launching omp, timeout, post-processing (provenance, candidate validation,
root cause attribution), atomic locking with stale-lock detection, and status file writing.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
SPAWN_DIR = Path(__file__).resolve().parent
if str(SPAWN_DIR) not in sys.path:
    sys.path.insert(0, str(SPAWN_DIR))

try:
    from agent_trace import emit as emit_trace
except ImportError:
    emit_trace = None

from spawn import attach_trace_provenance, REFLECTION_PROMPT

GRAPH_DIGEST = ROOT / "knowledge" / "graph" / "GRAPH-DIGEST.md"
REFLECT_CANDIDATES = ROOT / "reflection" / "candidates"
SCRATCH_DIGESTS = ROOT / "reflection" / "scratch" / "digests"
SCRATCH_CANDIDATES = ROOT / "reflection" / "scratch" / "candidates"
LOGS_DIR = ROOT / "reflection" / "logs"

def is_pid_running(pid: int) -> bool:
    if os.name == "nt":
        try:
            res = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True)
            return str(pid) in res.stdout
        except Exception:
            return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

def write_status(status_file: Path, payload: dict) -> None:
    """Write the status file atomically.

    A bare write_text truncates first, so a hard kill (or a reader polling at the
    wrong moment) observes a 0-byte file indistinguishable from 'never started'.
    Write to a temp file in the same directory, then os.replace.
    """
    tmp = status_file.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload), encoding="utf-8")
    os.replace(tmp, status_file)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", required=True)
    ap.add_argument("--extension", required=True)
    ap.add_argument("--timeout", type=int, default=1200)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--scratch", action="store_true",
                    help="artifacts live under reflection/scratch/ (verification run)")
    args = ap.parse_args()

    topic = args.topic
    run_id = args.run_id
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    lock_file = LOGS_DIR / f"{topic}.lock"
    status_file = LOGS_DIR / f"{topic}.status.json"
    log_file = LOGS_DIR / f"{topic}.log"

    # Atomic lock check with stale-lock eviction
    if lock_file.exists():
        try:
            content = lock_file.read_text(encoding="utf-8").strip()
            old_pid = int(content) if content.isdigit() else 0
            if old_pid and is_pid_running(old_pid):
                print(f"[background_worker] active lock exists for topic {topic} (PID {old_pid})", file=sys.stderr)
                return 1
            else:
                print(f"[background_worker] removing stale lock for topic {topic} (PID {old_pid} dead)", file=sys.stderr)
                lock_file.unlink()
        except Exception:
            pass

    try:
        # Atomic create lock file
        fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode("utf-8"))
        os.close(fd)
    except OSError:
        print(f"[background_worker] failed to acquire lock atomically for topic {topic}", file=sys.stderr)
        return 1

    write_status(status_file, {"state": "running", "pid": os.getpid(), "timestamp": time.time()})

    try:
        workflow = ROOT / "pipeline" / "WORKFLOW.md"
        plan_version = ""
        if workflow.exists():
            import hashlib
            plan_version = hashlib.sha256(workflow.read_bytes()).hexdigest()[:12]
        phase = "04_reflect"

        fp_file = ROOT / "knowledge" / "graph" / ".graph_fingerprint"
        live_fp = fp_file.read_text(encoding="utf-8").strip() if fp_file.exists() else ""
        digest_fp = ""
        if GRAPH_DIGEST.exists():
            for line in GRAPH_DIGEST.read_text(encoding="utf-8").splitlines():
                if "fingerprint:" in line:
                    import re
                    m = re.search(r"fingerprint:\s*([0-9a-f]{12})", line)
                    if m:
                        digest_fp = m.group(1)
                    break

        digest = GRAPH_DIGEST.read_text(encoding="utf-8").strip()[:6000]
        stage_context = ROOT / "stages" / "04_reflect" / "CONTEXT.md"
        stage_hint = stage_context.read_text(encoding="utf-8").strip()[:1500] if stage_context.exists() else "(stage CONTEXT missing)"
        digest_with_hint = digest + f"\n\n--- Current phase CONTEXT (P3 re-injection source) ---\n{stage_hint}\n"

        out_digests = SCRATCH_DIGESTS if args.scratch else ROOT / "reflection" / "digests"
        out_candidates = SCRATCH_CANDIDATES if args.scratch else REFLECT_CANDIDATES
        out_digests.mkdir(parents=True, exist_ok=True)
        out_candidates.mkdir(parents=True, exist_ok=True)
        prompt = REFLECTION_PROMPT.format(
            topic=topic, digest=digest_with_hint, phase=phase,
            fingerprint=live_fp or digest_fp, plan_version=plan_version,
            digests_dir=out_digests.relative_to(ROOT).as_posix() + "/",
            candidates_dir=out_candidates.relative_to(ROOT).as_posix() + "/",
        )

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
            "--extension", str(args.extension),
            "-p", prompt,
            "--no-session",
        ]

        with log_file.open("w", encoding="utf-8") as out:
            proc = subprocess.run(cmd, stdout=out, stderr=subprocess.STDOUT, timeout=args.timeout, text=True)

        exit_code = proc.returncode
        candidate_path = (SCRATCH_CANDIDATES if args.scratch else REFLECT_CANDIDATES) / f"{topic}.jsonl"

        # A non-zero agent exit is not conclusive on its own: a router 400 can
        # abort the agent AFTER it has written valid artifacts. Fall through to
        # validation and let the gate decide, recording the agent's exit code as
        # a warning rather than as the verdict.
        agent_error = None
        if exit_code != 0:
            agent_error = f"agent exited with {exit_code}"
            log_file.open("a", encoding="utf-8").write(f"\n[worker] {agent_error}\n")
            if not candidate_path.exists():
                write_status(status_file, {"state": "failed", "exit_code": exit_code,
                                           "reason": agent_error, "timestamp": time.time()})
                return exit_code

        if candidate_path.exists():
            attach_trace_provenance(candidate_path, run_id)
            validator = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "candidate_writer.py"), str(candidate_path)],
                text=True, capture_output=True
            )
            if validator.returncode not in (0, 2):
                write_status(status_file, {"state": "failed", "gate": "candidate_writer", "exit_code": validator.returncode, "timestamp": time.time()})
                return 1

            subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "root_cause_attribution.py"), str(candidate_path)],
                text=True, capture_output=True
            )

        # Never claim success the gate has not confirmed. A background run that
        # writes artifacts failing check_reflection.py must report `failed` and
        # leave the artifacts on disk as evidence — deleting them would destroy
        # the only signal that something is wrong.
        gate_cmd = [sys.executable, str(ROOT / "scripts" / "check_reflection.py")]
        if args.scratch:
            # A scratch run's artifacts live outside the graded dirs; a whole-directory
            # gate would pass vacuously because it never sees them. Scope the gate
            # to exactly this run's artifacts so the gate is not bypassable by
            # writing to the wrong place.
            gate_cmd += ["--paths",
                        f"reflection/scratch/digests/{topic}.md",
                        f"reflection/scratch/candidates/{topic}.jsonl"]
        gate = subprocess.run(
            gate_cmd,
            text=True, capture_output=True, cwd=str(ROOT),
        )
        if gate.returncode != 0:
            # check_reflection.py reports on both streams; a stdout-only filter
            # silently yields an empty failure list and hides the real cause.
            failures = [ln for ln in (gate.stdout + gate.stderr).splitlines()
                        if ln.startswith(("FAIL", "WARN"))]
            log_file.open("a", encoding="utf-8").write(
                "\n--- gate failures ---\n" + (gate.stdout + gate.stderr) + "\n")
            write_status(status_file, {
                "state": "failed",
                "gate": "check_reflection",
                "exit_code": gate.returncode,
                "failures": failures,
                "timestamp": time.time(),
            })
            if emit_trace:
                emit_trace("failure", run_id=run_id, status="failed", module="reflection",
                           failure_kind="gate_failure", condition="check_reflection",
                           correction="inspect reflection/logs/" + topic + ".log; artifacts retained as evidence")
            return 1

        write_status(status_file, {
            "state": "done",
            "exit_code": exit_code,
            "warnings": [agent_error] if agent_error else [],
            "timestamp": time.time(),
        })
        if emit_trace:
            emit_trace("run", run_id=run_id, status="completed", workflow="06_reflect", topic=topic,
                       artifacts=[f"reflection/digests/{topic}.md", f"reflection/candidates/{topic}.jsonl"])
        return 0

    except subprocess.TimeoutExpired:
        write_status(status_file, {"state": "timeout", "timestamp": time.time()})
        return 3
    except Exception as exc:
        write_status(status_file, {"state": "error", "error": str(exc), "timestamp": time.time()})
        return 1
    finally:
        if lock_file.exists():
            try:
                lock_file.unlink()
            except OSError:
                pass

if __name__ == "__main__":
    sys.exit(main())
