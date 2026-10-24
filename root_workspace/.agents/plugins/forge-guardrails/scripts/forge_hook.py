#!/usr/bin/env python3
"""forge-guardrails hook dispatcher.

goose fires this once per lifecycle event; it is a *separate process* every
time, so all cross-call state lives in .forge/state.json (resume-from-state,
never model memory). Each run:

    1. read the goose payload (JSON on stdin)
    2. load .forge/policy.yaml + .forge/state.json
    3. infer which workflow step the tool evidence satisfies
    4. run the matching guardrail, persist state, emit the decision

Decision protocol (goose): exit 2 + stderr reason  ==  block; or stdout
`{"decision":"block","reason":...}`. On non-blocking events stdout is kept
empty and notes go to stderr / .forge/journal.

Blocks only where goose honours it: PreToolUse and Stop.
"""
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import policy_loader as pl  # noqa: E402

# --- forge integration -------------------------------------------------
# forge is installed in the workspace's .venv-forge (Python 3.12). Hooks may be
# launched by the system python (3.11) which cannot import forge. If forge is
# unavailable, re-exec this script under the venv interpreter that has it,
# forwarding stdin so the payload is preserved.
def _forge_root_python() -> "pl.Path | None":
    base = pl.Path(os.path.abspath(__file__)).parents[4]
    cand = [
        base / "projects" / "research" / "agentic-research-lab"
        / ".venv-forge" / "Scripts" / "python.exe",
        base / "projects" / "research" / "agentic-research-lab"
        / ".venv-forge" / "bin" / "python",
    ]
    for c in cand:
        if c.exists():
            return c
    return None


try:
    import forge.guardrails as forge  # type: ignore
    from forge.guardrails.response_validator import ToolCall  # type: ignore
    HAS_FORGE = True
except Exception:  # noqa: BLE001
    HAS_FORGE = False
    forge = None
    ToolCall = None

TEST_FILE_RE = re.compile(r"(^|/|\\)(test_.*|.*_test)\.(py|js|ts|go|rs|java)|/tests?/",
                          re.IGNORECASE)
PYTEST_RE = re.compile(r"\b(pytest|unittest|nose|tox)\b", re.IGNORECASE)
DIFF_RE = re.compile(r"\bgit\s+(diff|show|status|log)\b", re.IGNORECASE)
SHELL_TOOL_RE = re.compile(r"(shell|bash|terminal|exec|run|command)", re.IGNORECASE)
WRITE_TOOL_RE = re.compile(r"(write|edit|apply_patch|text_editor|str_replace)",
                          re.IGNORECASE)
READ_TOOL_RE = re.compile(r"(read|open|cat|grep|search|fetch|ls|list)",
                         re.IGNORECASE)


# --- helpers -------------------------------------------------------------

def log(msg: str) -> None:
    print(f"[forge] {msg}", file=sys.stderr)


def tool_name(payload: dict) -> str:
    return payload.get("tool_name") or payload.get("matcher_context") or ""


def tool_input(payload: dict) -> dict:
    ti = payload.get("tool_input") or payload.get("matcher_context") or ""
    if isinstance(ti, dict):
        return ti
    if isinstance(ti, str):
        return {"command": ti, "path": ti}
    return {}


def command_text(inp: dict) -> str:
    parts = [str(inp.get(k, "")) for k in
             ("command", "cmd", "args", "script", "text", "content", "path")]
    return " ".join(p for p in parts if p)


def block(reason: str, code: int = 2) -> None:
    # stdout JSON is the reliable channel; exit 2 + stderr is the belt-and-braces.
    sys.stdout.write(json.dumps({"decision": "block", "reason": reason}))
    sys.stdout.write("\n")
    log(f"BLOCK: {reason}")
    raise SystemExit(code)


def read_payload() -> dict:
    raw = sys.stdin.read() if not sys.stdin.isatty() else ""
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except Exception:  # noqa: BLE001
        return {"_raw": raw}


def _resolve(payload: dict) -> "pl.Path":
    hint = payload.get("working_dir") or payload.get("cwd")
    return pl._resolve_root(hint)


# --- step inference ------------------------------------------------------

def infer_steps(tool: str, inp: dict, completed: list[str]) -> list[str]:
    """Which required workflow steps does this tool evidence satisfy?"""
    found: list[str] = []
    cmd = command_text(inp)
    name = tool.lower()
    low = cmd.lower()

    if WRITE_TOOL_RE.search(name) or re.search(r"(write|edit|patch)", low):
        if TEST_FILE_RE.search(cmd) or "test" in low and TEST_FILE_RE.search(cmd):
            if "write_test" in completed:
                pass
            found.append("write_test")
        elif not TEST_FILE_RE.search(cmd):
            found.append("implement")
    if SHELL_TOOL_RE.search(name) or "command" in inp:
        if re.search(r"(pytest|unittest|tox|npm test|pnpm test|cargo test)", low):
            if re.search(r"(pytest|unittest|tox)\s+([^\s]+\.(py|js|ts)|-\s)", low) \
               or " " in low.strip().lower():
                found.append("run_targeted_tests")
            else:
                found.append("run_full_tests")
        if re.search(r"pytest|unittest|tox", low):
            found.append("run_targeted_tests")
        if DIFF_RE.search(cmd):
            found.append("inspect_diff")
    if READ_TOOL_RE.search(name) and any(
            re.search(p, low) for p in (r"policy\.ya?ml", r"contributing",
                                         r"claude\.md", r"\bagents\.md")):
        found.append("read_repo_rules")
    # de-dup, keep order
    seen, out = set(), []
    for s in found:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def _mark_test_result(payload: dict, inp: dict, completed: list[str]) -> str | None:
    """Record whether the last test run was green; return the status."""
    low = command_text(inp).lower()
    if not re.search(r"pytest|unittest|tox|npm test|pnpm test|cargo test", low):
        return None
    # best-effort: targeted vs full inferred by presence of a file target
    targeted = bool(re.search(r"(pytest|unittest|tox)\s+\S+", low))
    key = "targeted" if targeted else "full"
    return key


def _parse_test_counts(output: str) -> str:
    """Pull 'N passed / M failed / K errors' from pytest-like output.

    Returns a compact 'N passed[, M failed][, K errors]' string, or ''
    when the output carries no summary line (non-pytest runners, crashes).
    Counts come from the tool's own stdout — never from agent prose.
    """
    passed = re.findall(r"(\d+)\s+passed", output)
    failed = re.findall(r"(\d+)\s+failed", output)
    errors = re.findall(r"(\d+)\s+errors?", output)
    if not (passed or failed or errors):
        return ""
    parts = []
    if passed:
        parts.append(f"{passed[-1]} passed")
    if failed:
        parts.append(f"{failed[-1]} failed")
    if errors:
        parts.append(f"{errors[-1]} errors")
    return ", ".join(parts)


def _post_test_status(root: "pl.Path", inp: dict, completed: list[str],
                       policy: dict) -> str:
    """Run the test command to capture a real pass/fail, store it in state."""
    cmd = command_text(inp)
    if not re.search(r"pytest|unittest|tox|npm test|pnpm test|cargo test",
                      cmd.lower()):
        return "unchanged"
    import subprocess
    try:
        p = subprocess.run(cmd, shell=True, cwd=str(root), timeout=120,
                           capture_output=True, text=True)
        status = "pass" if p.returncode == 0 else "fail"
        counts = _parse_test_counts((p.stdout or "") + "\n" + (p.stderr or ""))
        if counts:
            status = f"{status} ({counts})"
    except Exception:  # noqa: BLE001
        status = "fail"
    targeted = bool(re.search(r"(pytest|unittest|tox)\s+\S+", cmd))
    key = "targeted" if targeted else "full"
    return f"{key}:{status}"


# --- recall helpers ----------------------------------------------------

def is_recall_command(cmd: str) -> bool:
    low = cmd.lower()
    return "debug.py" in low or "ask.py" in low or "memory_index" in low


def extract_query(inp: dict, cmd: str) -> str:
    path = str(inp.get("path") or inp.get("file_path") or "")
    if path:
        return f"{path} {cmd[:80]}"
    return cmd[:120] if cmd else "general workspace query"


def run_recall(root: pl.Path, query: str) -> tuple[int, int]:
    import subprocess
    mem_hits = 0
    graph_hits = 0
    try:
        p1 = subprocess.run([sys.executable, str(root / "scripts" / "debug.py"), query],
                            cwd=str(root), capture_output=True, text=True, timeout=10)
        out1 = p1.stdout or ""
        mem_hits = len([line for line in out1.splitlines() if "hit" in line.lower() or "::" in line])
    except Exception:
        pass

    try:
        p2 = subprocess.run([sys.executable, str(root / "scripts" / "ask.py"), query],
                            cwd=str(root), capture_output=True, text=True, timeout=10)
        out2 = p2.stdout or ""
        graph_hits = len([line for line in out2.splitlines() if line.strip().startswith("#")])
    except Exception:
        pass

    return mem_hits, graph_hits


# --- subcommands ---------------------------------------------------------

def cmd_pre_tool(payload: dict) -> None:
    root = _resolve(payload)
    policy = pl.load_policy(root)
    state = pl.load_state(root)
    completed = list(state.get("completed_steps", []))
    tool = tool_name(payload)
    inp = tool_input(payload)
    cmd = command_text(inp)
    git_rules = policy.get("rules", {}).get("git", {})

    # (a) destructive git gate -- always on, no state needed
    if git_rules.get("forbid_destructive_commands", True):
        for pat in git_rules.get("destructive_patterns", []):
            if re.search(pat, cmd, re.IGNORECASE):
                block(f"forge: destructive git command forbidden by policy: "
                      f"{cmd.strip()[:120]}")

    # (ab) Active Recall enforcement (Slice 1)
    if not state.get("recall_done") and (WRITE_TOOL_RE.search(tool.lower()) or SHELL_TOOL_RE.search(tool.lower())):
        if not is_recall_command(cmd):
            query = extract_query(inp, cmd)
            mem_hits, graph_hits = run_recall(root, query)
            state["recall_done"] = True
            state["recall_hits"] = {"memory": mem_hits, "graph": graph_hits}
            pl.save_state(root, state)
            block(f"forge: RECALL for {query!r}:\n"
                  f"  session memory hits: {mem_hits}\n"
                  f"  knowledge graph hits: {graph_hits}\n"
                  f"Re-plan with this context, then retry.")

    # (b) step-prerequisite gate via forge StepEnforcer (or fallback)
    steps = infer_steps(tool, inp, completed)
    need_test_first = ("implement" in steps
                       and "write_test" not in completed
                       and policy.get("rules", {}).get("tests", {})
                       .get("require_test_before_implementation", True))
    if HAS_FORGE:
        wf = policy.get("workflow", {})
        req = list(wf.get("required_steps", []))
        term = frozenset(wf.get("terminal_tools", ["done"]))
        pre = wf.get("tool_prerequisites", {})
        try:
            enforcer = forge.StepEnforcer(required_steps=req,
                                          terminal_tools=term,
                                          tool_prerequisites=pre)
            for s in completed:
                enforcer.record(s)
            # Guard the tools that carry prerequisites.
            for s in [x for x in steps if pre.get(x)]:
                sc = enforcer.check_prerequisites(
                    [ToolCall(tool=s, args={})])
                if sc.needs_nudge:
                    pending = "write_test" if "write_test" not in completed \
                        else "prerequisite"
                    block(f"forge: '{s}' is blocked by StepEnforcer -- "
                          f"required step '{pending}' not satisfied yet "
                          f"(step enforcement)")
        except Exception as e:  # noqa: BLE001
            # A broken enforcer must NOT silently disable enforcement:
            # fall back to the static prerequisite check, never to allow.
            log(f"StepEnforcer error (static fallback): {e}")
            if need_test_first:
                block("forge: write a test before implementing "
                      "(test-before-implementation policy; "
                      "StepEnforcer unavailable)")
    elif need_test_first:
        block("forge: write a test before implementing "
              "(test-before-implementation policy)")

    # record evidence so post_tool/stop can see it
    for s in steps:
        if s not in completed:
            completed.append(s)
    state["completed_steps"] = completed
    state["current_step"] = steps[-1] if steps else state.get("current_step")
    if steps:
        pl.save_state(root, state)
        pl.journal(root, f"[pre_tool] {tool} -> {steps}")


def cmd_post_tool(payload: dict) -> None:
    root = _resolve(payload)
    policy = pl.load_policy(root)
    state = pl.load_state(root)
    completed = list(state.get("completed_steps", []))
    tool = tool_name(payload)
    inp = tool_input(payload)

    # (1) test-file anti-tautology gate
    path = str(inp.get("path") or inp.get("file_path") or "")
    if WRITE_TOOL_RE.search(tool.lower()) and TEST_FILE_RE.search(path or
                                                                   command_text(inp)):
        target = path or command_text(inp)
        if os.path.exists(target):
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import test_validator as tv
            verdict = tv.validate_test_file(target)
            if not verdict.ok:
                msg = "; ".join(f.message for f in verdict.findings)
                # advisory (PostToolUse cannot block): record + nudge
                state.setdefault("test_warnings", []).append(
                    {"file": target, "findings": verdict.to_json()})
                pl.journal(root, f"[post_tool] TEST WARNING {target}: {msg}")
                log(f"test warning {target}: {msg}")
            else:
                state["test_warnings"] = []

    # (2) capture real test status
    if _mark_test_result(payload, inp, completed):
        st = _post_test_status(root, inp, completed, policy)
        if ":" in st:
            key, status = st.split(":", 1)
            state["tests"][key] = status
            # remember the exact command so Stop can re-verify it itself
            # (state.json is agent-writable; a claimed "pass" is not evidence)
            state.setdefault("test_cmds", {})[key] = command_text(inp)
            completed_set = set(completed)
            run_step = "run_targeted_tests" if key == "targeted" \
                else "run_full_tests"
            if run_step not in completed_set:
                completed.append(run_step)
            if status.startswith("fail"):
                state["failed_steps"].append(run_step)
        state["completed_steps"] = completed
        pl.save_state(root, state)
        pl.journal(root, f"[post_tool] test {st}")


def cmd_tool_failure(payload: dict) -> None:
    root = _resolve(payload)
    policy = pl.load_policy(root)
    state = pl.load_state(root)
    esc = policy.get("escalation", {})
    tiers = esc.get("tiers", ["LOW", "MEDIUM", "HIGH"])
    tier = state.get("escalation_tier", "LOW")
    cnt = state.setdefault("error_counts", {})
    cnt["consecutive_failures"] = int(cnt.get("consecutive_failures", 0)) + 1
    limit = int(esc.get("low_max_retries", 2) if tier == "LOW"
                else esc.get("medium_max_retries", 3))
    if tier in tiers and cnt["consecutive_failures"] > limit:
        i = tiers.index(tier)
        if i < len(tiers) - 1:
            nxt = tiers[i + 1]
            state["escalation_tier"] = nxt
            cnt["consecutive_failures"] = 0
            pl.journal(root, f"[tool_failure] escalated {tier} -> {nxt}")
            log(f"escalating {tier} -> {nxt}")
    tool = tool_name(payload)
    nudge = _failure_nudge(tool, cnt["consecutive_failures"],
                           state.get("escalation_tier", "LOW"))
    state["last_nudge"] = nudge
    pl.save_state(root, state)
    pl.journal(root, f"[tool_failure] {tool} fail#{cnt['consecutive_failures']}")


def _failure_nudge(tool: str, n: int, tier: str) -> str:
    return (f"forge: tool '{tool}' failed {n}x at {tier}. Re-examine the "
            f"error output, fix the minimal cause, retry -- do not repeat the "
            f"identical call.")


def _reverify_suites(root: "pl.Path", state: dict) -> dict:
    """Re-run hook-observed test commands; return fresh {key: status}.

    The agent can write .forge/state.json itself, so a state-claimed "pass"
    is not evidence. Stop re-executes the recorded commands and decides on
    what it ran, not on what the state file claims.
    """
    import subprocess
    fresh: dict = {}
    for key in ("targeted", "full"):
        cmd = (state.get("test_cmds") or {}).get(key)
        if not cmd:
            continue
        try:
            p = subprocess.run(cmd, shell=True, cwd=str(root), timeout=120,
                               capture_output=True, text=True)
            status = "pass" if p.returncode == 0 else "fail"
            counts = _parse_test_counts((p.stdout or "") + "\n"
                                        + (p.stderr or ""))
            fresh[key] = f"{status} ({counts})" if counts else status
        except Exception:  # noqa: BLE001
            fresh[key] = "fail"
    return fresh


def cmd_stop(payload: dict) -> None:
    root = _resolve(payload)
    policy = pl.load_policy(root)
    state = pl.load_state(root)
    completed = set(state.get("completed_steps", []))
    req = list(policy.get("workflow", {}).get("required_steps", []))
    tests = state.get("tests", {})
    tier = state.get("escalation_tier", "LOW")
    esc = policy.get("escalation", {})
    tiers = esc.get("tiers", ["LOW", "MEDIUM", "HIGH"])

    # if a code change happened but the pipeline is incomplete -> block.
    did_implement = "implement" in completed or "write_test" in completed
    if did_implement:
        # Re-verify: state.json is agent-writable, so re-run the suites
        # instead of trusting a claimed "pass".
        fresh = _reverify_suites(root, state)
        if fresh:
            tests = {**tests, **fresh}
            state["tests"] = tests
            pl.journal(root, f"[stop] re-verified {fresh}")
        elif str(tests.get("targeted", "")).startswith("pass") \
                or str(tests.get("full", "")).startswith("pass"):
            # "pass" with no hook-observed test command on record:
            # nobody saw it run. Treat as not green.
            tests = {"targeted": "unobserved", "full": "unobserved"}
    green = str(tests.get("targeted", "")).startswith("pass") \
        and str(tests.get("full", "")).startswith("pass")
    missing = [s for s in req
               if s in ("run_targeted_tests", "run_full_tests",
                         "inspect_diff") and s not in completed]

    if did_implement and not green and tier != tiers[-1]:
        block(f"forge: task incomplete before stop -- tests not green "
              f"(targeted={tests.get('targeted')}, full={tests.get('full')}), "
              f"missing steps: {missing or 'run the test suite'}. "
              f"Fix the code and run the full suite before finishing.")
    # top tier: advisory only, never deadlock the agent
    state["terminal_reached"] = green and not missing
    state["completed_steps"] = sorted(completed)
    pl.save_state(root, state)
    pl.journal(root, f"[stop] green={green} missing={missing} "
                     f"tier={tier}")


def cmd_session_start(payload: dict) -> None:
    root = _resolve(payload)
    policy = pl.load_policy(root)
    state = pl.load_state(root)
    state["recall_done"] = False
    fresh = {
        "task": state.get("task"),
        "current_step": state.get("current_step"),
        "completed_steps": state.get("completed_steps", []),
        "tests": state.get("tests", {}),
        "escalation_tier": state.get("escalation_tier", "LOW"),
        "required_steps": policy.get("workflow",
                                     {}).get("required_steps", []),
        "terminal_tools": policy.get("workflow",
                                     {}).get("terminal_tools", []),
        "note": ("resume from state, not model memory. Forge enforces "
                  "test-before-implementation, anti-tautological tests, and "
                  "destructive-git bans."),
    }
    (root / ".forge" / "context.md").write_text(
        json.dumps(fresh, indent=2), encoding="utf-8")
    pl.save_state(root, state)
    pl.journal(root, "[session_start] context.md written")
    log(f"session_start: resume tier={fresh['escalation_tier']} "
        f"done={fresh['completed_steps']}")


def cmd_session_end(payload: dict) -> None:
    root = _resolve(payload)
    state = pl.load_state(root)
    summary = {
        "task": state.get("task"),
        "completed_steps": state.get("completed_steps", []),
        "failed_steps": state.get("failed_steps", []),
        "tests": state.get("tests", {}),
        "terminal_reached": state.get("terminal_reached", False),
        "escalation_tier": state.get("escalation_tier", "LOW"),
    }
    (root / ".forge" / "progress" / "last.json").parent.mkdir(
        parents=True, exist_ok=True)
    (root / ".forge" / "progress" / "last.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")
    pl.journal(root, "[session_end] checkpoint written")
    log("session_end: checkpoint -> .forge/progress/last.json")


DISPATCH = {
    "pre_tool": cmd_pre_tool,
    "post_tool": cmd_post_tool,
    "tool_failure": cmd_tool_failure,
    "stop": cmd_stop,
    "session_start": cmd_session_start,
    "session_end": cmd_session_end,
}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in DISPATCH:
        sys.stderr.write("usage: forge_hook.py "
                         "<" + "|".join(DISPATCH) + ">\n")
        raise SystemExit(64)
    if not HAS_FORGE:
        vpy = _forge_root_python()
        if vpy is not None and not os.environ.get("FORGE_REEXEC"):
            # Re-run under the venv python (which has forge), forwarding stdin
            # and mirroring its exit code + stdout/stderr. Subprocess (not
            # os.execve) because a cross-interpreter execve faults on Windows.
            import subprocess as _sp
            p = _sp.run([str(vpy), os.path.abspath(__file__), sys.argv[1]],
                       stdin=sys.stdin.buffer,
                       env=dict(os.environ, FORGE_REEXEC="1"))
            raise SystemExit(p.returncode)
    payload = read_payload()
    try:
        DISPATCH[sys.argv[1]](payload)
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        # a crashing hook must NOT take goose down; log and allow.
        sys.stderr.write(f"[forge] hook {sys.argv[1]} error (allow): {e}\n")
        raise SystemExit(0)


if __name__ == "__main__":
    main()
