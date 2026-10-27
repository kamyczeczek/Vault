"""Phase 2 KG ablation runner: OFF (no graph) vs ON (graph context injected).

Same agent, same prompt, same guarded loop — the ONLY difference is the
presence of a graph-context block built via ask.py + route.py. Metrics are
computed deterministically afterwards by score_ablation.py over blind
arm_A.json / arm_B.json transcripts (the ON/OFF mapping stays sealed in
mapping.json until analysis).

Run under the project forge venv (proven pipe, same as forge_ab_test.py):

    .venv-forge/Scripts/python.exe scripts/run_ablation.py --build-check
    .venv-forge/Scripts/python.exe scripts/run_ablation.py --smoke
    .venv-forge/Scripts/python.exe scripts/run_ablation.py --full
"""

import argparse
import asyncio
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

BASE_URL = "http://localhost:20128/v1"
MODEL = "gemini/gemini-flash-lite-latest"
KEY_ENV = "OMNIROUTE_API_KEY"
SEED = 20261004
MAX_ITER = 6
ASK_CHAR_BUDGET = 2500
OUT_DIR = ROOT / "scripts" / "_scratch" / "ablation"

BASE_PROMPT = (
    "Answer the research question below in 3-6 sentences. "
    "Support every factual claim with a citation on its own line in exactly "
    "this form:\nChunk id: `NN_slug`\n"
    "Only cite chunk ids you have evidence for. If you know no chunk id for "
    "a claim, write the claim without a citation rather than inventing an id."
)
CONTEXT_BLOCK = (
    "Retrieved graph context for this question "
    "(chunk id, title, snippet - cite using these Chunk id values):\n{context}"
)

SMOKE_TASKS = ("bf-concentration", "feat-critic", "perf-ppr")


def load_tasks() -> dict:
    with open(ROOT / "benchmark" / "tasks.json", encoding="utf-8") as fh:
        return json.load(fh)


def build_context(task: dict) -> tuple[str, list[dict]]:
    """Run ask.py + route.py for one task. Returns (context, query records)."""
    queries: list[dict] = []
    ask = subprocess.run(
        [sys.executable, "knowledge/graph/ask.py", task["question"],
         "--limit", str(task["k"])],
        cwd=ROOT, capture_output=True, text=True, timeout=120,
    )
    queries.append({"tool": "ask.py", "rc": ask.returncode, "dead": ask.returncode == 2})
    route_cmd = [sys.executable, "pipeline/06_reflect/route.py", "--limit", "5"]
    for tag in task["tags"]:
        route_cmd += ["--tag", tag]
    route = subprocess.run(
        route_cmd, cwd=ROOT, capture_output=True, text=True, timeout=120,
    )
    queries.append({"tool": "route.py", "rc": route.returncode, "dead": route.returncode == 2})
    return ask.stdout[:ASK_CHAR_BUDGET], queries


def make_workflow(has_context: bool):
    from forge import Workflow, respond_tool

    system = BASE_PROMPT
    if has_context:
        system += "\n\n" + CONTEXT_BLOCK
    return Workflow(
        name="phase2_ablation",
        description="Phase 2 ablation QA with citations",
        tools={"respond": respond_tool()},
        required_steps=[],
        terminal_tool="respond",
        system_prompt_template=(
            "You are a precise research assistant. " + system + " "
            "Finish by calling the respond tool with the final answer."
        ),
    )


def task_text(task: dict) -> str:
    return task["question"]


async def one_run(task: dict, has_context: bool, context: str, api_key: str) -> dict:
    from forge_bridge import build_compat_runner

    runner = build_compat_runner(base_url=BASE_URL, model=MODEL, api_key=api_key)
    runner.max_iterations = MAX_ITER
    wf = make_workflow(has_context)
    prompt_vars = {"context": context} if has_context else None
    t0 = time.monotonic()
    try:
        res = await runner.run(wf, task_text(task), prompt_vars=prompt_vars)
        return {"answer": str(res), "secs": round(time.monotonic() - t0, 1), "err": ""}
    except Exception as exc:  # noqa: BLE001 - record, never raise in a run
        return {"answer": "", "secs": round(time.monotonic() - t0, 1),
                "err": f"{type(exc).__name__}: {str(exc)[:150]}"}


def build_check() -> int:
    """No-LLM validation: tasks, oracles, tags, prompts, workflow shape."""
    from check_citation_integrity import known_ids

    data = load_tasks()
    tasks = data["tasks"]
    fams: dict[str, int] = {}
    for t in tasks:
        fams[t["family"]] = fams.get(t["family"], 0) + 1
    assert len(tasks) == 9, f"expected 9 tasks, got {len(tasks)}"
    assert sorted(fams.values()) == [3, 3, 3], f"families: {fams}"
    known = known_ids()
    for t in tasks:
        missing = [c for c in t["oracle_ids"] if c not in known]
        assert not missing, f"{t['id']}: oracle ids absent from graph: {missing}"
        _, queries = build_context(t)
        dead = [q for q in queries if q["dead"]]
        assert not dead, f"{t['id']}: dead harness query: {dead}"
        assert BASE_PROMPT in make_workflow(False).system_prompt_template
        assert "Retrieved graph context" in make_workflow(True).system_prompt_template
    print(f"build-check OK: 9 tasks, oracles resolve, tags live, prompts render "
          f"({len(known)} ids indexed)")
    return 0


async def run_subset(task_ids: list[str], arms: tuple[str, ...], seed: int) -> dict:
    api_key = os.environ.get(KEY_ENV, "")
    if not api_key:
        raise SystemExit(f"env {KEY_ENV} is not set")
    data = load_tasks()
    by_id = {t["id"]: t for t in data["tasks"]}
    rng = random.Random(seed)
    mapping: dict[str, dict[str, str]] = {}
    transcripts: dict[str, list] = {"A": [], "B": []}
    for tid in task_ids:
        task = by_id[tid]
        context, queries = build_context(task)
        order = ["ON", "OFF"]
        rng.shuffle(order)
        mapping[tid] = {"A": order[0], "B": order[1]}
        for label in ("A", "B"):
            arm = mapping[tid][label]
            if arm not in arms:
                continue
            rec = await one_run(task, arm == "ON", context, api_key)
            transcripts[label].append({
                "task_id": tid,
                "answer": rec["answer"],
                "secs": rec["secs"],
                "err": rec["err"],
                "queries": queries if arm == "ON" else [],
            })
            print(f"  {tid} [{label}]: secs={rec['secs']} "
                  f"chars={len(rec['answer'])} err={rec['err'][:60]}")
    return {"transcripts": transcripts, "mapping": mapping}


def write_outcome(outcome: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for label in ("A", "B"):
        with open(OUT_DIR / f"arm_{label}.json", "w", encoding="utf-8") as fh:
            json.dump(outcome["transcripts"][label], fh, ensure_ascii=False, indent=2)
    with open(OUT_DIR / "mapping.json", "w", encoding="utf-8") as fh:
        json.dump(outcome["mapping"], fh, indent=2, sort_keys=True)
    print(f"wrote {OUT_DIR}/arm_A.json arm_B.json mapping.json (mapping sealed)")


async def main_async(args: argparse.Namespace) -> int:
    data = load_tasks()
    if args.smoke:
        outcome = await run_subset(list(SMOKE_TASKS), ("OFF",), args.seed)
        write_outcome(outcome)
        return 0
    tids = [t["id"] for t in data["tasks"]]
    outcome = await run_subset(tids, ("ON", "OFF"), args.seed)
    write_outcome(outcome)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 2 ablation runner.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--build-check", action="store_true")
    group.add_argument("--smoke", action="store_true",
                       help="3 tasks, OFF only: confirm baseline failure > 0")
    group.add_argument("--full", action="store_true",
                       help="9 tasks x ON/OFF, blind A/B")
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args(argv)
    if args.build_check:
        return build_check()
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    raise SystemExit(main())
