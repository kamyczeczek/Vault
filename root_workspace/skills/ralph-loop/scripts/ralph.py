#!/usr/bin/env python3
"""Small file-backed controller for the human-confirmed Ralph loop."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATUSES = {"READY", "WORKING", "VERIFICATION", "WAITING_FOR_CONFIRMATION", "APPROVED", "DONE", "BLOCKED", "ABANDONED"}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def project_root(value: str | None) -> Path:
    return Path(value or ".").resolve()


def ralph_dir(root: Path) -> Path:
    return root / ".ralph"


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def append_jsonl(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False) + "\n")


def parse_handoff(path: Path) -> str | None:
    """Return the front-matter `updated:` value of a handoff file, or None if unstamped."""
    if not path.exists():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.strip().startswith("updated:"):
            value = line.split(":", 1)[1].strip()
            return None if (not value or value.startswith("<")) else value
    return None


def parse_gates(run: Path) -> dict[str, Any]:
    """Count met/unmet gates and abandons in a run's GATES.md."""
    path = run / "GATES.md"
    if not path.exists():
        return {"present": False, "none": False, "met": 0, "unmet": 0, "abandoned": 0, "ok": True}
    met = unmet = abandoned = none_declared = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("GATES:") and "<" not in stripped and "none" in stripped.lower():
            none_declared = True
        elif stripped.startswith("- [x]"):
            met += 1
        elif stripped.startswith("- [ ]"):
            unmet += 1
        elif stripped.startswith("ABANDON:"):
            abandoned += 1
    return {"present": True, "none": none_declared, "met": met, "unmet": unmet, "abandoned": abandoned, "ok": none_declared or (unmet == 0 and abandoned == 0)}


def update_index(workspace: Path, dry_run: bool = False) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for state_path in workspace.glob("**/.ralph/STATE.json"):
        if state_path == workspace / ".ralph" / "STATE.json":
            continue
        state = read_json(state_path, {})
        entries.append({"project": str(state_path.parent.parent.relative_to(workspace)), **state})
    root_state = workspace / ".ralph" / "STATE.json"
    if root_state.exists():
        entries.append({"project": ".", **read_json(root_state, {})})
    entries.sort(key=lambda item: item.get("updated_at", ""), reverse=True)
    root = workspace / ".ralph"
    registry_data = {"generated_at": now(), "entries": entries}
    lines = ["# Ralph activity", "", "Generated from project-local `.ralph/STATE.json` files.", "", "| Project | Status | Iteration | Updated | Next frontier |", "|---|---|---:|---|---|"]
    for item in entries:
        lines.append(f"| `{item['project']}` | `{item.get('status', 'UNKNOWN')}` | {item.get('iteration', 0)} | {item.get('updated_at', '')} | {item.get('next_frontier', '')} |")
    if not entries:
        lines.append("| _none_ | — | 0 | — | — |")
    index_content = "\n".join(lines) + "\n"
    if not dry_run:
        write_json(root / "registry.json", registry_data)
        (root / "INDEX.md").write_text(index_content, encoding="utf-8")
    return {"registry": registry_data, "index": index_content, "dry_run": dry_run}


def init(args: argparse.Namespace) -> None:
    root = project_root(args.project)
    ralph = ralph_dir(root)
    run = ralph / "runs" / f"{datetime.now().date().isoformat()}_{args.slug}"
    run.mkdir(parents=True, exist_ok=False)
    (run / "decisions").mkdir()
    (run / "iterations").mkdir()
    state = {"status": "READY", "iteration": 0, "run": str(run.relative_to(root)), "next_frontier": args.frontier, "updated_at": now()}
    write_json(ralph / "STATE.json", state)
    append_jsonl(ralph / "history.jsonl", {"event": "init", **state})
    templates = Path(__file__).parent.parent / "assets" / "templates"
    (run / "REQUEST.md").write_text((templates / "REQUEST.md").read_text(encoding="utf-8").replace("<why this run exists>", args.intent).replace("<observable end state>", args.destination), encoding="utf-8")
    (run / "PLAN.md").write_text((templates / "PLAN.md").read_text(encoding="utf-8").replace("<what reaching the end looks like>", args.destination).replace("D-001", args.frontier), encoding="utf-8")
    (run / "decisions" / f"{args.frontier}.md").write_text((templates / "DECISION.md").read_text(encoding="utf-8").replace("<decision title>", args.frontier).replace("<one decision this node resolves>", args.intent), encoding="utf-8")
    (run / "HANDOFF.md").write_text((templates / "HANDOFF.md").read_text(encoding="utf-8"), encoding="utf-8")
    (run / "GATES.md").write_text((templates / "GATES.md").read_text(encoding="utf-8").replace("<run name>", args.slug).replace("<complete outcome for this run>", args.destination), encoding="utf-8")
    (run / "LEARNINGS.md").write_text((templates / "LEARNINGS.md").read_text(encoding="utf-8"), encoding="utf-8")
    update_index(root if args.workspace is None else project_root(args.workspace))
    print(json.dumps(state, indent=2))


def set_status(args: argparse.Namespace) -> None:
    root = project_root(args.project)
    path = ralph_dir(root) / "STATE.json"
    state = read_json(path, {})
    if not state:
        raise SystemExit("No active Ralph state; run init first.")
    if args.status not in STATUSES:
        raise SystemExit(f"Invalid status: {args.status}")
    state.update({"status": args.status, "updated_at": now()})
    if args.status == "APPROVED":
        state["iteration"] = int(state.get("iteration", 0)) + 1
    if args.frontier is not None:
        state["next_frontier"] = args.frontier
    write_json(path, state)
    append_jsonl(ralph_dir(root) / "history.jsonl", {"event": "status", **state})
    update_index(root if args.workspace is None else project_root(args.workspace))
    print(json.dumps(state, indent=2))


def record_iteration(args: argparse.Namespace) -> None:
    root = project_root(args.project)
    ralph = ralph_dir(root)
    state = read_json(ralph / "STATE.json", {})
    if not state:
        raise SystemExit("No active Ralph state; run init first.")
    run = root / state["run"]
    handoff_at = parse_handoff(run / "HANDOFF.md")
    if handoff_at is None:
        raise SystemExit("HANDOFF.md must carry front-matter `updated:` before an iteration can be recorded. Write the next-session handoff first.")
    if args.outcome == "DONE":
        gates = parse_gates(run)
        if not gates["ok"]:
            raise SystemExit(f"DONE blocked: {gates['unmet']} unmet / {gates['abandoned']} abandoned gate(s) in GATES.md. Run `gates` to inspect; satisfy gates or record ABANDON with a reason, or record CONTINUE instead.")
    iteration_num = int(state.get("iteration", 0)) + 1
    iteration_id = f"I-{iteration_num:03d}"
    templates = Path(__file__).parent.parent / "assets" / "templates"
    template = (templates / "ITERATION.md").read_text(encoding="utf-8")
    content = template.replace("{iteration:03d}", f"{iteration_num:03d}").replace("{title}", args.title).replace("{decision_id}", args.decision).replace("{intent}", args.intent).replace("{allowed_paths}", args.paths).replace("{work_performed}", args.work).replace("{command}", args.command).replace("{exit_status}", str(args.exit_status)).replace("{result}", args.result).replace("{files_changed}", args.files).replace("{outcome}", args.outcome).replace("{next_frontier}", args.next_frontier or "")
    (run / "iterations" / f"{iteration_id}.md").write_text(content, encoding="utf-8")
    state.update({"status": "WAITING_FOR_CONFIRMATION", "updated_at": now(), "last_iteration": iteration_id, "last_decision": args.decision, "next_frontier": args.next_frontier or "", "handoff_at": handoff_at})
    write_json(ralph / "STATE.json", state)
    append_jsonl(ralph / "history.jsonl", {"event": "iteration", "iteration": iteration_id, "decision": args.decision, "outcome": args.outcome, "next_frontier": args.next_frontier or ""})
    update_index(root if args.workspace is None else project_root(args.workspace))
    print(json.dumps(state, indent=2))


def resume(args: argparse.Namespace) -> None:
    root = project_root(args.project)
    ralph = ralph_dir(root)
    state = read_json(ralph / "STATE.json", {})
    if not state:
        raise SystemExit("No active Ralph state; run init first.")
    run = root / state["run"]
    frontier = state.get("next_frontier", "")
    read_next = [state.get("run", "") + "/HANDOFF.md"]
    if frontier:
        read_next.append(state.get("run", "") + f"/decisions/{frontier}.md")
    output = {**state, "gates": parse_gates(run), "handoff_at": parse_handoff(run / "HANDOFF.md"), "read_next": read_next}
    print(json.dumps(output, indent=2))


def show_gates(args: argparse.Namespace) -> None:
    root = project_root(args.project)
    state = read_json(ralph_dir(root) / "STATE.json", {})
    if not state:
        raise SystemExit("No active Ralph state; run init first.")
    print(json.dumps(parse_gates(root / state["run"]), indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=".")
    parser.add_argument("--workspace")
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("init")
    start.add_argument("slug")
    start.add_argument("intent")
    start.add_argument("destination")
    start.add_argument("--frontier", default="D-001")
    start.set_defaults(func=init)
    status = sub.add_parser("status")
    status.set_defaults(func=lambda args: print(json.dumps(read_json(ralph_dir(project_root(args.project)) / "STATE.json", {}), indent=2)))
    approve = sub.add_parser("approve")
    approve.add_argument("--frontier")
    approve.set_defaults(func=lambda args: set_status(argparse.Namespace(**vars(args), status="APPROVED")))
    change = sub.add_parser("set-status")
    change.add_argument("status")
    change.add_argument("--frontier")
    change.set_defaults(func=set_status)
    record = sub.add_parser("record-iteration")
    record.add_argument("--decision", required=True)
    record.add_argument("--title", required=True)
    record.add_argument("--intent", required=True)
    record.add_argument("--paths", default="")
    record.add_argument("--work", default="")
    record.add_argument("--command", default="")
    record.add_argument("--exit-status", type=int, default=0)
    record.add_argument("--result", default="")
    record.add_argument("--files", default="")
    record.add_argument("--outcome", choices=["CONTINUE", "DONE", "BLOCKED"], required=True)
    record.add_argument("--next-frontier")
    record.set_defaults(func=record_iteration)
    index = sub.add_parser("index")
    index.add_argument("--dry-run", action="store_true", help="Print index without writing")
    index.set_defaults(func=lambda args: (lambda r: print(f"index updated: {len(r['registry']['entries'])} entries -> .ralph/INDEX.md"))(update_index(project_root(args.workspace or args.project), dry_run=args.dry_run)))
    re_ = sub.add_parser("resume", help="Cold-start read list for a fresh session: state + gates + what to read next")
    re_.set_defaults(func=resume)
    gates_cmd = sub.add_parser("gates", help="Report met/unmet/abandoned gates for the active run")
    gates_cmd.set_defaults(func=show_gates)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
