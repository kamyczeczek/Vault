"""Load + persist forge workspace state (.forge/policy.yaml + state.json).

Stdlib only. No forge import here -- the guardrail dispatcher (forge_hook.py)
is the only place that touches the forge package, so a broken forge install
degrades the hooks to plain step-enforcement instead of crashing goose.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

YAML_RE = re.compile(r"^( *)(- )?([A-Za-z_][\w.-]*)\s*:\s*(.*)$")

DEFAULT_POLICY = {
    "rules": {
        "git": {
            "forbid_force_push": True,
            "forbid_destructive_commands": True,
            "destructive_patterns": [
                r"git\s+push\s+.*--force",
                r"git\s+reset\s+--hard",
                r"git\s+clean\s+-[a-z]*f[a-z]*d",
                r"git\s+clean\s+.*\s-fdx",
                r"git\s+filter-branch",
                r"git\s+branch\s+-D",
                r"git\s+checkout\s+--\s\.(.*)$",
            ],
        },
        "tests": {
            "require_behavioral_tests": True,
            "forbid_tautological_tests": True,
            "require_test_before_implementation": True,
            "require_test_fails_first": True,
        },
        "verification": {
            "require_targeted_tests": True,
            "require_full_suite": True,
        },
    },
    "workflow": {
        "terminal_tools": ["done"],
        "required_steps": [
            "read_repo_rules",
            "understand_task",
            "write_test",
            "verify_test_fails",
            "implement",
            "run_targeted_tests",
            "run_full_tests",
            "inspect_diff",
            "final_review",
        ],
        "tool_prerequisites": {
            "implement": ["write_test"],
            "run_targeted_tests": ["implement"],
            "run_full_tests": ["run_targeted_tests"],
            "final_review": ["run_full_tests"],
        },
    },
    "escalation": {
        "low_max_retries": 2,
        "medium_max_retries": 3,
        "tiers": ["LOW", "MEDIUM", "HIGH"],
        "escalate_on": [
            "repeated_test_failure",
            "step_enforcement_violation",
            "context_overflow",
        ],
    },
}


def _mini_yaml(text: str) -> dict:
    """Tiny YAML subset parser: nested maps + lists of scalars.

    Supports the exact shapes policy.yaml uses. No external dependency so the
    hook works even if PyYAML is absent in the runner's venv.
    """
    lines = [ln for ln in text.splitlines()
             if ln.strip() and not ln.lstrip().startswith("#")]

    def peek_kind(idx: int, indent: int) -> str:
        for j in range(idx, len(lines)):
            raw = lines[j]
            if not raw.strip():
                continue
            ind = len(raw) - len(raw.lstrip(" "))
            if ind <= indent:
                return "scalar"
            s = raw.strip()
            if s.startswith("- "):
                return "list"
            if re.match(r"^[A-Za-z_][\w.-]*\s*:", s):
                return "map"
            return "scalar"
        return "scalar"

    root: dict = {}
    # stack of (indent, container) where container is dict or list
    stack: list[tuple[int, object]] = [(-1, root)]
    for i, raw in enumerate(lines):
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if line.startswith("- "):
            val = _coerce(line[2:].strip())
            if isinstance(parent, list):
                parent.append(val)
            continue
        m = re.match(r"^(?P<key>[A-Za-z_][\w.-]*)\s*:\s*(?P<val>.*)$", line)
        if not m:
            continue
        key, val = m.group("key"), m.group("val").strip()
        if val != "":
            if isinstance(parent, dict):
                parent[key] = _coerce(val)
            continue
        kind = peek_kind(i + 1, indent)
        child: object = [] if kind == "list" else {}
        if isinstance(parent, dict):
            parent[key] = child
        stack.append((indent, child))
    return _collapse(root)


def _coerce(val: str):
    if val.startswith("[") and val.endswith("]"):
        return [x.strip().strip('"\'') for x in val[1:-1].split(",") if x.strip()]
    if re.fullmatch(r"[\d.]+", val):
        return float(val) if "." in val else int(val)
    low = val.lower()
    if low in ("true", "false"):
        return low == "true"
    if low in ("none", "null", "~"):
        return None
    return val.strip('"\'')


def _collapse(d: dict) -> dict:
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out[k] = _collapse(v)
        elif isinstance(v, list):
            out[k] = [(_collapse(x) if isinstance(x, dict) else x) for x in v]
        else:
            out[k] = v
    return out


def _deep_update(base: dict, extra: dict) -> dict:
    for k, v in extra.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_update(base[k], v)
        else:
            base[k] = v
    return base


def _resolve_root(hint: str | None) -> Path:
    if hint:
        p = Path(hint)
        if p.is_dir():
            return p.resolve()
    env = os.environ.get("FORGE_ROOT")
    if env:
        return Path(env).resolve()
    # scripts/forge-guardrails/plugins/.agents -> parents[4] == repo root
    return Path(__file__).resolve().parents[4]


def load_policy(root: Path) -> dict:
    p = root / ".forge" / "policy.yaml"
    base = json.loads(json.dumps(DEFAULT_POLICY))
    if not p.exists():
        return base
    text = p.read_text(encoding="utf-8")
    user = {}
    try:
        import yaml  # type: ignore
        user = yaml.safe_load(text) or {}
    except Exception:
        user = _mini_yaml(text)
    return _deep_update(base, user if isinstance(user, dict) else {})


def load_state(root: Path) -> dict:
    p = root / ".forge" / "state.json"
    if not p.exists():
        return {
            "task": None,
            "current_step": None,
            "completed_steps": [],
            "failed_steps": [],
            "error_counts": {"consecutive_failures": 0},
            "tests": {"targeted": "pending", "full": "pending"},
            "escalation_tier": "LOW",
            "terminal_reached": False,
            "history": [],
        }
    return json.loads(p.read_text(encoding="utf-8"))


def save_state(root: Path, state: dict) -> None:
    d = root / ".forge"
    d.mkdir(parents=True, exist_ok=True)
    (d / "state.json").write_text(
        json.dumps(state, indent=2, sort_keys=True), encoding="utf-8"
    )


def journal(root: Path, line: str) -> None:
    d = root / ".forge" / "journal"
    d.mkdir(parents=True, exist_ok=True)
    with (d / "session.md").open("a", encoding="utf-8") as f:
        f.write(line.rstrip() + "\n")
