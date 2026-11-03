#!/usr/bin/env python3
"""Dump a redacted snapshot of the AI agent configuration into the vault.

Read-only sources (never modified):
  ~/.pi/agent/settings.json, mcp.json, pi-permissions.jsonc
  ~/.pi/agent/agents/*.md
  <vault>/.pi/settings.json
  ~/.config/opencode/opencode.jsonc

Deliberately NOT read (secrets / bulk): auth.json, models.json, npm/,
sessions/, trust.json, extensions/.

Writes:
  handoff/agent-config/SNAPSHOT.json   machine-readable, secrets redacted
  handoff/agent-config/SNAPSHOT.md     human-readable summary

Every secret-shaped value is replaced by "<redacted sha256:xxxxxxxx len=N>",
so drift is still detectable without leaking the value.

Usage:
  python scripts/dump_agent_config.py            # write snapshots
  python scripts/dump_agent_config.py --check    # exit 1 if stale
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VAULT = Path(__file__).resolve().parent.parent
AGENT_DIR = Path(os.environ.get("PI_AGENT_DIR", Path.home() / ".pi" / "agent"))
OPENCODE_CONFIG = Path(
    os.environ.get(
        "OPENCODE_CONFIG",
        Path.home() / ".config" / "opencode" / "opencode.jsonc",
    )
)
OUT_DIR = VAULT / "handoff" / "agent-config"
OUT_JSON = OUT_DIR / "SNAPSHOT.json"
OUT_MD = OUT_DIR / "SNAPSHOT.md"

REDACT_KEY = re.compile(
    r"(?i)(api[_-]?key|apikey|token|secret|password|passwd|authorization|"
    r"cookie|credential|private[_-]?key)"
)
REDACT_VALUE = (
    re.compile(r"^(sk|rk|pk|nvapi|ghp|gho|ghs|github_pat|xox[abp]|thk_live|AQ\.)[-_A-Za-z0-9.]{8,}$"),
    re.compile(r"^(?=.*[A-Za-z])(?=.*[0-9])[A-Za-z0-9_\-.]{32,}$"),
)


# ---------------------------------------------------------------- jsonc parsing


def strip_jsonc(text: str) -> str:
    """Remove // and /* */ comments plus trailing commas, outside strings."""
    out: list[str] = []
    i, n = 0, len(text)
    in_str = False
    while i < n:
        ch = text[i]
        if in_str:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_str = False
            i += 1
            continue
        if ch == '"':
            in_str = True
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(ch)
        i += 1
    cleaned = "".join(out)
    return re.sub(r",(\s*[}\]])", r"\1", cleaned)


def load_jsonc(path: Path) -> tuple[Any, str | None]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"{type(exc).__name__}: {exc}"
    try:
        return json.loads(strip_jsonc(raw)), None
    except json.JSONDecodeError as exc:
        return None, f"JSONDecodeError: {exc}"


# ------------------------------------------------------------------- redaction


def fingerprint(value: Any) -> str:
    blob = repr(value).encode("utf-8")
    return f"sha256:{hashlib.sha256(blob).hexdigest()[:8]} len={len(blob)}"


def is_secret_value(value: str) -> bool:
    return any(p.match(value) for p in REDACT_VALUE)


def redact(obj: Any, parent_key: str = "") -> Any:
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            if REDACT_KEY.search(str(k)):
                out[k] = f"<redacted {fingerprint(v)}>"
            elif str(k).lower() == "env" and isinstance(v, dict):
                out[k] = {
                    ek: f"<redacted {fingerprint(ev)}>" for ek, ev in v.items()
                }
            else:
                out[k] = redact(v, str(k))
        return out
    if isinstance(obj, list):
        return [redact(v, parent_key) for v in obj]
    if isinstance(obj, str) and is_secret_value(obj):
        return f"<redacted {fingerprint(obj)}>"
    return obj


def count_redactions(obj: Any) -> int:
    if isinstance(obj, str):
        return 1 if obj.startswith("<redacted ") else 0
    if isinstance(obj, dict):
        return sum(count_redactions(v) for v in obj.values())
    if isinstance(obj, list):
        return sum(count_redactions(v) for v in obj)
    return 0


# ------------------------------------------------------------------ md parsing

FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?", re.S)


def parse_agent_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    meta: dict[str, Any] = {}
    body = text
    match = FRONTMATTER.match(text)
    if match:
        body = text[match.end():]
        current_key: str | None = None
        for line in match.group(1).splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if line.startswith((" ", "\t", "-")) and current_key:
                item = line.strip().lstrip("-").strip().strip('"').strip("'")
                if isinstance(meta.get(current_key), list):
                    meta[current_key].append(item)
                else:
                    meta[current_key] = [meta[current_key], item]
                continue
            if ":" in line:
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                current_key = key
                if value.startswith("[") and value.endswith("]"):
                    meta[key] = [v.strip().strip('"').strip("'") for v in value[1:-1].split(",") if v.strip()]
                elif value:
                    meta[key] = value
                else:
                    meta[key] = []
    return {
        "file": path.name,
        "meta": redact(meta),
        "body_lines": len(body.splitlines()),
        "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest()[:16],
        "body_redacted": redact(body),
    }


# -------------------------------------------------------------------- snapshot


def file_fact(path: Path, include_content: bool = True, parse_json: bool = True) -> dict[str, Any]:
    fact: dict[str, Any] = {"path": str(path), "exists": path.is_file()}
    if not path.is_file():
        return fact
    data = path.read_bytes()
    fact["bytes"] = len(data)
    fact["sha256"] = hashlib.sha256(data).hexdigest()
    if not include_content:
        return fact
    parsed, err = load_jsonc(path) if parse_json else (None, "not parsed")
    if err:
        fact["parse_error"] = err
        return fact
    if parsed is not None:
        fact["redacted"] = redact(parsed)
        fact["redactions"] = count_redactions(fact["redacted"])
    return fact


def build_snapshot() -> dict[str, Any]:
    agents_dir = AGENT_DIR / "agents"
    agents = (
        [parse_agent_file(p) for p in sorted(agents_dir.glob("*.md"))]
        if agents_dir.is_dir()
        else []
    )

    pi_settings = file_fact(AGENT_DIR / "settings.json")
    mcp = file_fact(AGENT_DIR / "mcp.json")
    permissions = file_fact(AGENT_DIR / "pi-permissions.jsonc")
    opencode = file_fact(OPENCODE_CONFIG)

    hash_only = {
        "append_system": AGENT_DIR / "APPEND_SYSTEM.md",
        "models": AGENT_DIR / "models.json",
        "auth": AGENT_DIR / "auth.json",
        "vault_settings": VAULT / ".pi" / "settings.json",
    }
    extra = {name: file_fact(p, include_content=False) for name, p in hash_only.items()}

    return {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "vault": str(VAULT),
        "redaction": (
            "Secret-shaped keys (apiKey/token/secret/...) and secret-shaped values are "
            "replaced by '<redacted sha256:... len=N>'. auth.json, models.json content, "
            "npm/, sessions/ and extensions/ are excluded on purpose."
        ),
        "sources": {
            "pi_settings": pi_settings,
            "pi_mcp": mcp,
            "pi_permissions": permissions,
            "opencode": opencode,
            **extra,
        },
        "pi": {
            "settings": pi_settings.get("redacted", {}),
            "mcp_servers": sorted((mcp.get("redacted") or {}).get("mcpServers", {})),
            "agents": [
                {
                    "name": a["meta"].get("name", a["file"]),
                    "file": a["file"],
                    "model": a["meta"].get("model"),
                    "fallbacks": a["meta"].get("fallbackModels"),
                    "description": a["meta"].get("description"),
                    "body_lines": a["body_lines"],
                    "body_sha256": a["body_sha256"],
                }
                for a in agents
            ],
        },
        "agents_full": agents,
        "opencode": opencode.get("redacted", {}),
    }


def render_md(snap: dict[str, Any]) -> str:
    pi_cfg = snap["pi"]["settings"]
    oc = snap.get("opencode") or {}
    lines: list[str] = []
    add = lines.append

    add("# Agent config snapshot")
    add("")
    add("Generated by `scripts/dump_agent_config.py` (exact timestamp in `SNAPSHOT.json`).")
    add("")
    add("> Redacted: secret-shaped keys/values become `<redacted sha256:... len=N>`.")
    add("> Not read on purpose: `auth.json`, `models.json` content, `npm/`, `sessions/`, `extensions/`.")
    add("> Refresh: `python scripts/dump_agent_config.py`; staleness gate: `--check`.")
    add("")

    add("## Model & runtime (pi)")
    add("")
    add("| Setting | Value |")
    add("| --- | --- |")
    for key in (
        "defaultProvider",
        "defaultModel",
        "defaultThinkingLevel",
        "modelThinkingLevels",
        "compaction",
        "pi-plan",
        "shellPath",
        "packages",
        "piBolt",
    ):
        if key in pi_cfg:
            add(f"| `{key}` | `{json.dumps(pi_cfg[key], ensure_ascii=False)}` |")
    add("")

    add("## Agents (`~/.pi/agent/agents/*.md`)")
    add("")
    add("| Agent | Model | Fallbacks | Body | Description |")
    add("| --- | --- | --- | --- | --- |")
    for agent in snap["pi"]["agents"]:
        fallbacks = agent.get("fallbacks") or "—"
        if isinstance(fallbacks, list):
            fallbacks = ", ".join(str(f) for f in fallbacks)
        add(
            f"| `{agent['name']}` | `{agent.get('model') or '—'}` | {fallbacks} | "
            f"{agent['body_lines']} lines | {agent.get('description') or ''} |"
        )
    add("")

    add("## MCP servers")
    add("")
    pi_mcp = (snap["sources"]["pi_mcp"].get("redacted") or {}).get("mcpServers", {})
    oc_mcp = ((oc.get("mcp") or {}).get("servers")) or {}
    add("| Harness | Server | Command / URL | Exposure |")
    add("| --- | --- | --- | --- |")
    for name, cfg in sorted(pi_mcp.items()):
        cmd = cfg.get("command", "")
        if isinstance(cmd, list):
            cmd = " ".join(str(c) for c in cmd)
        add(f"| pi | `{name}` | `{cmd}` | {cfg.get('exposure', 'direct')} |")
    for name, cfg in sorted(oc_mcp.items()):
        cmd = cfg.get("command", "")
        if isinstance(cmd, list):
            cmd = " ".join(str(c) for c in cmd)
        add(f"| opencode | `{name}` | `{cmd}` | local |")
    add("")

    add("## OpenCode config")
    add("")
    providers = oc.get("provider") or {}
    add(f"- `model`: `{oc.get('model', '—')}`")
    add(f"- providers: {len(providers)}")
    for name, cfg in sorted(providers.items()):
        models = cfg.get("models") or {}
        add(f"  - `{name}` — {len(models)} model(s), baseURL `{(cfg.get('options') or {}).get('baseURL', '—')}`")
    perm = oc.get("permission") or {}
    if perm:
        add("- permission groups: " + ", ".join(f"`{k}` ({len(v) if isinstance(v, dict) else 1})" for k, v in sorted(perm.items())))
    add("")

    add("## Sources (drift detection)")
    add("")
    add("| Source | Bytes | SHA-256 | Redactions |")
    add("| --- | --- | --- | --- |")
    for name, fact in snap["sources"].items():
        if fact.get("exists"):
            add(
                f"| `{name}` | {fact.get('bytes', '—')} | `{fact.get('sha256', '')[:12]}` | "
                f"{fact.get('redactions', '—')} |"
            )
        else:
            add(f"| `{name}` | — | missing | — |")
    add("")
    return "\n".join(lines)


# ------------------------------------------------------------------------ main


def serialize(snap: dict[str, Any]) -> tuple[str, str]:
    js = json.dumps(snap, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    return js, render_md(snap)


def without_timestamp(text: str) -> str:
    return re.sub(r'"generated_at": "[^"]*"', '"generated_at": "<ignored>"', text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if snapshots are stale")
    args = parser.parse_args(argv)

    snap = build_snapshot()
    js, md = serialize(snap)

    if args.check:
        if not OUT_JSON.is_file() or not OUT_MD.is_file():
            print("STALE: snapshot missing — run python scripts/dump_agent_config.py")
            return 1
        old_js = OUT_JSON.read_text(encoding="utf-8")
        old_md = OUT_MD.read_text(encoding="utf-8")
        if without_timestamp(old_js) != without_timestamp(js) or old_md != md:
            print("STALE: agent config changed — run python scripts/dump_agent_config.py")
            return 1
        print("OK: agent config snapshot is current")
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for path, text in ((OUT_JSON, js), (OUT_MD, md)):
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)

    redactions = sum(
        f.get("redactions", 0) for f in snap["sources"].values() if isinstance(f, dict)
    )
    print(f"wrote {OUT_JSON.relative_to(VAULT)}")
    print(f"wrote {OUT_MD.relative_to(VAULT)}")
    print(f"agents={len(snap['pi']['agents'])} redactions={redactions}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
