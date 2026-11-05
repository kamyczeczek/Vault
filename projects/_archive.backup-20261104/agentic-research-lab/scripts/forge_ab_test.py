"""Forge guardrail A/B test: gemini/gemini-flash-lite-latest via omniroute.

Deterministic 3-step tool task:
  1. search('fibonacci') -> reference text mentions 8 and 13
  2. add(8, 13)          -> 21
  3. respond(message='21') -> terminal

Compares rescue_enabled=False (baseline) vs True (guardrails), N runs each.
Reports: correct-answer rate, wall time, failure mode per run.

Run (requires the local .venv-forge Python 3.12 env and OMNIROUTE_API_KEY):

    cd projects/research/agentic-research-lab
    .venv-forge/Scripts/python.exe scripts/forge_ab_test.py

Construction-only check (no LLM calls, no key needed):

    .venv-forge/Scripts/python.exe scripts/forge_ab_test.py --build-check

API verified against forge-guardrails 0.9.5 (probe, 2026-10-03):
  ToolSpec.from_json_schema(name, description, schema_dict)
  ToolDef(spec=..., callable=...)          # kwargs name/parameters/handler: NO
  respond_tool() -> ToolDef with spec.name='respond', arg field `message`
  WorkflowRunner.run(workflow, user_message) -> terminal tool result
"""
import asyncio
import json
import os
import sys
import time
import urllib.request
from dataclasses import dataclass

BASE_URL = "http://localhost:20128/v1"
MODEL = "gemini/gemini-flash-lite-latest"  # default; override with --model
KEY_ENV = "OMNIROUTE_API_KEY"
N = 5
MAX_ITER = 6

from forge import ToolDef, ToolSpec, Workflow, respond_tool

from forge_bridge import build_compat_runner

SEARCH_RESULT = (
    "The Fibonacci sequence goes 1, 1, 2, 3, 5, 8, 13, 21. "
    "Two numbers of interest are 8 and 13."
)


def search(topic: str) -> str:
    """Fetch reference text about a topic (deterministic fixture)."""
    return SEARCH_RESULT


def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


def make_tools() -> dict:
    return {
        "search": ToolDef(
            spec=ToolSpec.from_json_schema(
                "search",
                "Fetch reference text about a topic.",
                {
                    "type": "object",
                    "properties": {"topic": {"type": "string", "description": "Topic to look up"}},
                    "required": ["topic"],
                },
            ),
            callable=search,
        ),
        "add": ToolDef(
            spec=ToolSpec.from_json_schema(
                "add",
                "Add two integers.",
                {
                    "type": "object",
                    "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
                    "required": ["a", "b"],
                },
            ),
            callable=add,
        ),
        "respond": respond_tool(),
    }


TASK = (
    "Look up the reference text about 'fibonacci' with the search tool. "
    "Find the two numbers of interest, add them with the add tool, "
    "then call respond with the sum as a single number."
)


def make_workflow() -> Workflow:
    return Workflow(
        name="forge_ab",
        description="Deterministic 3-step tool task (search -> add -> respond)",
        tools=make_tools(),
        required_steps=["search", "add"],
        terminal_tool="respond",
        system_prompt_template=(
            "You are a precise tool-using assistant. Use the given tools. "
            "Finish by calling the respond tool with the final answer."
        ),
    )


@dataclass
class RunResult:
    ok: bool
    secs: float
    answer: str = ""
    err: str = ""


def api_key() -> str:
    key = os.environ.get(KEY_ENV, "")
    if not key:
        raise SystemExit(f"env {KEY_ENV} is not set — set it and retry (router: {BASE_URL})")
    return key


def sanity_router() -> None:
    req = urllib.request.Request(
        BASE_URL + "/models", headers={"Authorization": f"Bearer {api_key()}"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        ids = [m["id"] for m in json.loads(r.read()).get("data", [])]
    present = MODEL in ids
    print(f"router models: {len(ids)} | target present: {present}")
    if not present:
        raise SystemExit(f"{MODEL} not in router model list — check omniroute config")


async def one_run(rescue: bool) -> RunResult:
    runner = build_compat_runner(base_url=BASE_URL, model=MODEL, api_key=api_key())
    runner.rescue_enabled = rescue
    runner.max_iterations = MAX_ITER
    wf = make_workflow()
    t0 = time.monotonic()
    try:
        res = await runner.run(wf, TASK)
        answer = str(res)
        return RunResult(ok="21" in answer, secs=time.monotonic() - t0, answer=answer[:120])
    except Exception as e:
        return RunResult(
            ok=False, secs=time.monotonic() - t0, err=f"{type(e).__name__}: {str(e)[:150]}"
        )


async def main() -> None:
    global N, MODEL, MAX_ITER
    if len(sys.argv) > 2 and sys.argv[1] == "--runs":
        N = int(sys.argv[2])
    if len(sys.argv) > 3 and sys.argv[3] == "--model":
        MODEL = sys.argv[4]
    if len(sys.argv) > 5 and sys.argv[5] == "--max-iter":
        MAX_ITER = int(sys.argv[6])
    sanity_router()
    for label, rescue in (("rescue=OFF (baseline)", False), ("rescue=ON (guardrails)", True)):
        print(f"\n=== {label} ===")
        wins = 0
        for i in range(N):
            rr = await one_run(rescue)
            wins += int(rr.ok)
            extra = f" | {rr.err}" if rr.err else f" | ans='{rr.answer[:60]}'"
            print(f"  run {i + 1}: ok={rr.ok} secs={rr.secs:.1f}{extra}")
        print(f"  => {wins}/{N} correct")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--build-check":
        wf = make_workflow()
        print(f"build-check OK: {wf.name} | tools={sorted(wf.tools)} | terminal={sorted(wf.terminal_tools)}")
    else:
        asyncio.run(main())
