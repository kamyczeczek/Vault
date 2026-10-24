"""Shared, pure extractors for session facts and the session digest.

The same functions feed `last_session_merged.py`, the mechanical digest, and
the verifier. They take text or a session object and return plain data; they
do not read stores, write files, or mutate their inputs.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

NORMALIZER_VERSION = "n1"
CARD_SCHEMA_VERSION = "1.0"

FLAG_RE = re.compile(r"handoff[/\\]flags[/\\]([0-9A-Za-z._\-]+)\.md")
COMMIT_RX = re.compile(r"\[(?:master|main) ([a-f0-9]{7,40})\]")
COMMIT_LINE_RX = re.compile(r"\bcommit ([a-f0-9]{7,40})\b", re.I)
COMMIT_WORD_RX = re.compile(r"\b(?:commit|committed|hash)[:` ]+([a-f0-9]{7,40})\b", re.I)
COMMIT_FILES_RX = re.compile(r"(\d+) files? changed")
COMMIT_INS_RX = re.compile(r"(\d+) insertions?\(\+\)")
COMMIT_DEL_RX = re.compile(r"(\d+) deletions?\(-\)")

ARTIFACT_RE = re.compile(r"artifact://")
EXT768_RE = re.compile(r"Some lines truncated to \d+ bytes")
TRUNC_RE = re.compile(r"…\[\+\d+ zn\.\]…")
SUPERSEDED_MARKER = "Superseded by a newer read"

MARKERS = {
    "[empty model output]": "empty_model_output",
    "STOP GATE": "stop_gate",
    "BLOKADA": "blokada",
    "not checked:": "not_checked",
    "CZEKAM": "awaiting_owner",
}
MARKERS_VERSION = "2026-10-22"

REASON_EMPTY_OUTPUT = "empty_model_output"
REASON_BOILERPLATE = "boilerplate"
REASON_NOT_EXTRACTED = "not_extracted"
REASON_AGENT_UNSUPPORTED = "agent_unsupported_mvp"
REASON_NO_EVIDENCE = "no_evidence"

WRITE_TOOLS = {
    "write", "edit", "apply_patch", "create", "delete", "move", "rename",
    "notebookedit", "notebook_edit", "multiedit", "multiedit_file",
}
PATH_KEYS = ("filePath", "file_path", "path", "filename", "notebook_path")
BOILERPLATE_PREFIXES = (
    "<system", "you are opencode", "you are a coding agent", "system prompt",
)


def parse_local_ts(val):
    if not val:
        return None
    s = str(val).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(s[:16 if fmt.endswith("%M") else 19], fmt)
        except ValueError:
            continue
    return None


def duration(s) -> str:
    """Compact created->updated span from the session's own metadata.

    Uses only the session's own timestamps; a missing or inverted pair is
    rendered as an empty string, never as a guessed duration.
    """
    a, b = parse_local_ts(s.created_at), parse_local_ts(s.updated_at)
    if not a or not b or b < a:
        return ""
    sec = int((b - a).total_seconds())
    if sec < 60:
        return f"{sec}s"
    if sec < 3600:
        return f"{sec // 60}m{sec % 60}s"
    return f"{sec // 3600}h{(sec % 3600) // 60}m"


def flag_ids(body: str) -> list[str]:
    seen = []
    for match in FLAG_RE.findall(body):
        if match not in seen:
            seen.append(match)
    return seen


def flag_id(body: str) -> str:
    """The last literal `handoff/flags/<id>.md` a session mentions, if any."""
    found = FLAG_RE.findall(body)
    return found[-1] if found else ""


def last_line(body: str) -> str:
    """Last non-empty prose line, verbatim and capped.

    Deliberately NOT a classified outcome ("STOP GATE" etc.): that would be a
    guess on free text. Quoting the closing line lets the reader judge without
    the tool asserting a conclusion. Tool markers and headings are skipped.
    """
    text, _ = last_prose_line(body)
    return text


def last_prose_line(body: str) -> tuple[str, int]:
    lines = body.split("\n")
    depth = 0
    for idx in range(len(lines) - 1, -1, -1):
        line = lines[idx]
        depth = max(0, depth + line.count("</details>") - line.count("<details"))
        t = line.strip()
        if not t or t.startswith(("> ", "#", "<", "- **", "<!--")):
            continue
        if depth:
            continue
        return t[:120], idx + 1
    return "", 0


def count_turns(body: str) -> int:
    """Count conversational turns (user/assistant headings).

    Deliberate fallback, not a bug: loaders for some agents emit roles other
    than user/assistant, so callers fall back to `s.message_count` when this
    returns 0. Do not count every `## [...]` heading — harness events are not
    turns.
    """
    return len(re.findall(r"^## \[(?:user|assistant)\]$", body, flags=re.M))


def count_blocks(body: str) -> int:
    """Count rendered `## [role]` blocks, ignoring quoted headings inside
    `<details>` (a reasoning trace or system notice may quote one)."""
    depth = 0
    total = 0
    for line in body.splitlines():
        if depth == 0 and re.match(r"^## \[[^\]]+\]$", line):
            total += 1
        depth += line.count("<details") - line.count("</details>")
        if depth < 0:
            depth = 0
    return total


def losses_str(v: dict) -> str:
    parts = []
    if "trunc_blocks" in v:
        ids = ",".join(str(x) for x in v["trunc_blocks"])
        if ids:
            parts.append(f"trunc msg {ids}")
        elif v.get("trunc"):
            parts.append(f"trunc×{v['trunc']}")
        ids = ",".join(str(x) for x in v.get("artifact_tools", []))
        if ids:
            parts.append(f"artifact tool {ids}")
        if v.get("artifact", 0) > len(v.get("artifact_tools", [])):
            parts.append(f"artifact {v['artifact']}")
        ids = ",".join(str(x) for x in v.get("ext768_tools", []))
        if ids:
            parts.append(f"768B tool {ids}")
        if v.get("ext768", 0) > len(v.get("ext768_tools", [])):
            parts.append(f"768B {v['ext768']}")
        if v.get("superseded"):
            parts.append(f"superseded {v['superseded']}")
        return " | ".join(parts) if parts else "brak"
    if v.get("trunc"):
        parts.append(f"trunc×{v['trunc']}")
    if v.get("dup"):
        parts.append(f"dup×{v['dup']}")
    if v.get("artifact"):
        parts.append(f"artifact×{v['artifact']}")
    if v.get("ext768"):
        parts.append(f"768B×{v['ext768']}")
    if v.get("superseded"):
        parts.append(f"superseded×{v['superseded']}")
    return ", ".join(parts) if parts else "brak"


def normalize_text(text: str) -> str:
    text = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t\f\v]+", " ", text)
    return text.strip()


def normalize_quote(text: str, limit: int = 200) -> str:
    return re.sub(r"[ \t\f\v]+", " ", (text or "").replace("\r\n", "\n")).strip()[:limit]


def is_boilerplate_prompt(text: str) -> bool:
    head = normalize_text(text).lower()
    return any(head.startswith(prefix) for prefix in BOILERPLATE_PREFIXES)


def extract_goal(body: str, agent: str = "opencode") -> dict:
    if agent != "opencode":
        return {"kind": "none", "reason": REASON_AGENT_UNSUPPORTED}
    lines = body.split("\n")
    start = None
    for idx, line in enumerate(lines):
        if line.strip() == "## [user]":
            start = idx + 1
            break
    if start is None:
        return {"kind": "none", "reason": REASON_NOT_EXTRACTED}
    collected = []
    depth = 0
    for line in lines[start:]:
        if depth == 0 and re.match(r"^## \[[^\]]+\]$", line.strip()):
            break
        depth += line.count("<details") - line.count("</details>")
        if depth < 0:
            depth = 0
        collected.append(line)
    text = normalize_quote("\n".join(collected))
    if not text:
        return {"kind": "none", "reason": REASON_NO_EVIDENCE}
    if is_boilerplate_prompt(text):
        return {"kind": "none", "reason": REASON_BOILERPLATE}
    return {"kind": "prompt", "text": text}


def _marker_scan(body: str) -> list[tuple[int, str, str]]:
    found = []
    fence = False
    depth = 0
    for idx, line in enumerate(body.split("\n"), 1):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            fence = not fence
            continue
        if fence:
            continue
        depth += line.count("<details") - line.count("</details>")
        if depth < 0:
            depth = 0
        if depth:
            continue
        if stripped.startswith(">"):
            continue
        code = MARKERS.get(stripped)
        if code:
            found.append((idx, stripped, code))
    return found


def extract_ending(body: str, agent: str = "opencode") -> dict:
    if agent != "opencode":
        return {"kind": "none", "reason": REASON_AGENT_UNSUPPORTED}
    markers = _marker_scan(body)
    if markers:
        line_no, raw, code = markers[-1]
        return {
            "kind": "marker",
            "marker": code,
            "text": raw,
            "raw_line": raw,
            "source_line": line_no,
            "markers_version": MARKERS_VERSION,
        }
    text, line_no = last_prose_line(body)
    if text:
        return {"kind": "quote", "text": text, "source_line": line_no}
    return {"kind": "none", "reason": REASON_NO_EVIDENCE}


def extract_commits(body: str) -> list[str]:
    out = []
    for rx in (COMMIT_RX, COMMIT_LINE_RX, COMMIT_WORD_RX):
        for match in rx.findall(body):
            if match not in out:
                out.append(match)
    return sorted(out)


def extract_tests(body: str) -> list[str]:
    out = []
    patterns = (
        re.compile(r"^\s*=+ .*(?:passed|failed).* =+\s*$"),
        re.compile(r"^\s*\d+ passed\b.*$"),
        re.compile(r"^\s*(?:OK|FAILED)(?: \(.*\))?\s*$"),
        re.compile(r"^\s*FAILED\b.*$"),
    )
    for line in body.split("\n"):
        t = line.strip()
        for rx in patterns:
            if rx.match(t):
                if t[:200] not in out:
                    out.append(t[:200])
                break
    return out[-5:]


def extract_losses(body: str) -> dict:
    return {
        "trunc": len(TRUNC_RE.findall(body)),
        "artifact": len(ARTIFACT_RE.findall(body)),
        "ext768": len(EXT768_RE.findall(body)),
        "superseded": body.count(SUPERSEDED_MARKER),
    }


def _path_from_input(tool: str, raw: str) -> str:
    if tool not in WRITE_TOOLS:
        return ""
    text = raw.strip()
    if text.startswith("{"):
        try:
            obj = json.loads(text)
        except Exception:
            obj = None
        if isinstance(obj, dict):
            for key in PATH_KEYS:
                val = obj.get(key)
                if isinstance(val, str) and val.strip():
                    return val.strip()
    match = re.search(r"(?:[A-Za-z]:[\\/])?[^\s`\"']+\.[A-Za-z0-9]{1,8}", text)
    return match.group(0) if match else ""


def extract_files(body: str, limit: int = 5) -> list[str]:
    counts: dict[str, int] = {}
    current_tool = ""
    for line in body.split("\n"):
        header = re.match(r"^> \*\*tool\*\* `([^`]+)`", line)
        if header:
            current_tool = header.group(1).strip().lower()
            continue
        if line.startswith("> in: `") and line.rstrip().endswith("`"):
            raw = line.rstrip()[len("> in: `"):-1]
            path = _path_from_input(current_tool, raw)
            if path:
                counts[path] = counts.get(path, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return [path for path, _ in ranked[:limit]]


def tool_block_count(body: str) -> int:
    return len(re.findall(r"^> \*\*tool\*\* `[^`]+`", body, flags=re.M))


def flags_missing(ids: list[str], flags_dir: Path | None = None) -> list[str]:
    root = flags_dir or (Path(__file__).resolve().parents[1] / "handoff" / "flags")
    return [flag for flag in ids if not (root / f"{flag}.md").is_file()]
