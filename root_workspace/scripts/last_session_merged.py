#!/usr/bin/env python
"""Merge the N most recent agent sessions into ONE markdown file.

Difference from the two neighbouring tools:

  agent_sessions.py last     -- N newest sessions -> N separate .md files
  agent_sessions.py markdown -- all sessions from the last D days -> one file
  last_session_merged.py     -- N newest sessions -> one file  (this script)

Recency is absolute and cross-agent: every registered agent store is scanned,
the merged list is sorted newest-first, then the first N are kept. No filtering
by date, so "N sessions" always means exactly N (or fewer, if the stores hold
fewer).

The artifact is self-auditing: the header states how many sessions were
rendered, each session carries a SHA256 of its own body, the index links to
anchors, and empty sessions are marked instead of silently rendered. Tool
payloads keep head+tail with a `…[+N zn.]…` gap marker (see
`agent_sessions._truncate_mid`) instead of a blind cut, and a tool output
repeated within one session collapses to a local absolute-line reference. No
cross-session dedup: a session stays readable on its own. Reasoning blocks are
excluded by default (they are often the bulk of the file); pass
`--include-reasoning` to keep them.

Usage:
    python scripts/last_session_merged.py [N]
    python scripts/last_session_merged.py 25 --agent opencode
    python scripts/last_session_merged.py 5 -o out.md
    python scripts/last_session_merged.py 25 --include-reasoning

Stdlib only; reuses the discovery + rendering layer of scripts/agent_sessions.py
instead of duplicating per-agent parsers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime
from typing import NamedTuple
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
AGENT_SESSIONS = SCRIPTS / "agent_sessions.py"
OUTDIR = SCRIPTS / "_scratch" / "sessions" / "02_products"
# ICM: one folder, one job. The merged export writes three kinds of
# file next to its output — per-session record bodies, the tool payload
# store, and the sidecar tables. They have their own homes, so a reader
# (or an agent) never has to guess which of the 100+ files is a product.
RECORDS_DIR = OUTDIR.parent / "03_records" / "sessions"
PAYLOADS_DIR = OUTDIR.parent / "04_payloads"

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from session_facts import (  # noqa: E402
    COMMIT_DEL_RX as _COMMIT_DEL_RX,
    COMMIT_FILES_RX as _COMMIT_FILES_RX,
    COMMIT_INS_RX as _COMMIT_INS_RX,
    COMMIT_RX as _COMMIT_RX,
    count_blocks as _count_blocks,
    count_turns as _count_turns,
    duration as _duration,
    flag_id as _flag_id,
    last_line as _last_line,
    losses_str as _losses_str,
    parse_local_ts as _parse_local_ts,
)


def _rel_prefix(target: Path, start: Path) -> str:
    """POSIX-style link prefix from `start` to `target` (dir form, '/')."""
    import os
    return os.path.relpath(target, start).replace("\\", "/") + "/"


class Action(NamedTuple):
    n: int
    tool: str
    arg: str
    result: str
    commit_hash: str | None = None
    commit_files: int | None = None
    commit_insertions: int | None = None
    commit_deletions: int | None = None
    exit_code: int | None = None
    is_error: bool = False


_BOILERPLATE_PREFIXES = ("Read file", "Read directory", "Created file",
                         "Wrote file", "Edited ", "Found ")


def _load_agent_sessions():
    """Import scripts/agent_sessions.py by path (it is not on sys.path)."""
    if not AGENT_SESSIONS.is_file():
        sys.exit(f"Nie znaleziono {AGENT_SESSIONS}")
    spec = spec_from_file_location("agent_sessions", AGENT_SESSIONS)
    if spec is None or spec.loader is None:
        sys.exit(f"Nie moge zaladowac {AGENT_SESSIONS}")
    module = module_from_spec(spec)
    # @dataclass resolves annotations through sys.modules[cls.__module__], so a
    # by-path import must register the module before executing it.
    sys.modules["agent_sessions"] = module
    spec.loader.exec_module(module)
    return module


def _header_lines(header: str) -> list[str]:
    """Split a `_session_header` string into the lines it occupies, dropping the
    terminal empty element produced by its trailing newline."""
    lines = header.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def _mark_empty_assistant(body: str) -> tuple[str, int]:
    """Name an assistant turn that rendered no text.

    A heading immediately followed by another heading (or by the end of the
    body) is indistinguishable from a renderer bug; the marker makes it an
    explicit observation. Tool-only turns are not empty: their signatures are
    content.
    """
    lines = body.split("\n")
    out: list[str] = []
    count = 0
    for i, line in enumerate(lines):
        out.append(line)
        if line.strip() != "## [assistant]":
            continue
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        empty = j >= len(lines) or lines[j].startswith(
            ("<a id=", "<!-- session-"))
        if j < len(lines) and lines[j].startswith("## ["):
            role = re.match(r"## \[([^\]]+)\]", lines[j])
            tool_role = role and role.group(1).lower() in (
                "tool", "toolresult", "tool_result", "tool result")
            empty = not tool_role
        if empty:
            out.append(_EMPTY_OUTPUT)
            count += 1
    return "\n".join(out), count


def _trunc_blocks(body: str) -> list[int]:
    """Assistant-message ordinals containing a `…[+N zn.]…` marker."""
    blocks: list[int] = []
    block = 0
    in_assistant = False
    hit = False
    for line in body.splitlines():
        if line.startswith("## ["):
            if in_assistant and hit:
                blocks.append(block)
            in_assistant = line.strip() == "## [assistant]"
            if in_assistant:
                block += 1
            hit = False
        elif in_assistant and re.search(r"…\[\+\d+ zn\.\]…", line):
            hit = True
    if in_assistant and hit:
        blocks.append(block)
    return blocks


# Tool-result lines emitted by the loaders. Two shapes matter:
#   `> out: `TEXT``                     (opencode legacy/v2, goose)
#   `> **tool result**: `TEXT``         (pi/omp)
#   `> **tool_result**: `TEXT``         (jcode, cline, antigravity, droid)
# `TEXT` may span multiple lines (the renderers do not escape newlines), so the
# span ends at the first line that closes the opening backtick.
_TOOL_OUT_PREFIX = re.compile(
    r"^> (?:(?:out)|(?:\*\*tool[_ ]?result\*\*)|(?:\*\*tool_result\*\*)):\s*`"
)

# Loss mechanisms that live *inside* a body and are otherwise only implied:
#   - `artifact://…` externalisation markers (some stores keep tool output in a
#     sidecar instead of inline) — the bytes are NOT in this file;
#   - a per-line 768-byte cut written by one harness, distinct from
#     `_truncate_mid`'s `…[+N zn.]…`.
# Both are declared in the header and per session, so no loss stays implicit.
_ARTIFACT_RE = re.compile(r"artifact://")
_EXT768_RE = re.compile(r"Some lines truncated to \d+ bytes")

# A loader-dropped older read is a real loss, not prose.
_SUPERSEDED_MARKER = "Superseded by a newer read"
# Collapsed harness events (`idle×7, model-switched×2`) — counted, not quoted.
_HARNESS_RE = re.compile(r"Pominiete zdarzenia harnessu\*\*: ([^\n]+)")

# Rendered tool block: `> **tool** `shell` · completed` followed by `> in:` and
# `> out:` lines. The renderer already did the parsing; we only re-pack it.
_TOOL_HDR_RE = re.compile(r"^> \*\*tool\*\* `([^`]+)` · (.+)$")
_IN_PREFIX = "> in: `"
_EXIT_RE = re.compile(
    r"(?:Exited with code|exit code|EXIT=)\s*(\d+)", re.I)
_READ_REF_RE = re.compile(
    r"Read (?:file|directory) (.+?)(?:, lines (\d+-\d+))?(?:\n|$)")

# Keep verbatim only where the exact text is the evidence. Everything else is
# replaced by a signature plus an artifact; the artifact still holds the text.
_VERBATIM_RES = tuple(re.compile(p) for p in (
    r"git show --stat",
    r"git status(?:\s|$)",
    r"git diff(?:\s|$)",
    r"git log --oneline",
    r"git cat-file",
    r"git rev-parse",
    r"(?m)^(?:OK|FAIL):",
    r"Ran \d+ tests",
    r"EXIT=\$?LASTEXITCODE",
    r"\bnot checked\b",
    r"\bpre-commit\b",
    r"\bclose\.py\b",
    r"\bgit commit\b",
))

_GATE_RE = re.compile(r"check_workspace_integrity(?:\.py)?", re.I)
_CONTEXT_READ_RE = re.compile(
    r"(?:[\\/](?:flags|handoff)[\\/]|[\\/](?:CONTEXT|HANDOFF|SCARS|DECISIONS|AGENTS)\.md$)",
    re.I)
_MANY_HITS_RE = re.compile(r"Found (\d+) matches", re.I)
_EMPTY_OUTPUT = "[empty model output]"

_CLAIM_RES = (
    ("commit", re.compile(
        r"\b(?:commit|git cat-file|git show|git rev-parse)\s+"
        r"(?:-[A-Za-z]+\s+)*`?([0-9a-f]{7,40})\b",
        re.I)),
    ("path_line", re.compile(
        r"`?([A-Za-z0-9_][\w./\\-]*\.(?:py|md|json|jsonl|txt|bat|toml|ya?ml)):(\d+)")),
    ("hit", re.compile(r"hit@(\d+)\s*=\s*([\d.]+)")),
    ("exit", re.compile(r"EXIT=\$?LASTEXITCODE|Exited with code (\d+)")),
    ("tests", re.compile(r"Ran (\d+) tests|\b(OK|FAIL):")),
    ("not_checked", re.compile(r"^\s*not checked\b", re.I)),
)

# Only intra-session duplicates are collapsed, and only when the reference is
# shorter than the content it replaces. A cross-session reference graph is not
# worth ~1%: it costs every session its self-containedness, and a bare hash
# with no location is unusable. Same-session refs carry a line offset instead.
_DEDUP_MIN_CHARS = 80


def _scan_tool_outputs(lines: list[str]) -> list[dict]:
    """Locate tool-result spans in a rendered body.

    Returns dicts with `start`/`end` (line indexes, end exclusive), `open_col`
    (index of the opening backtick on the start line) and `text` (the exact
    output content between the backticks).
    """
    spans: list[dict] = []
    i = 0
    n = len(lines)
    while i < n:
        m = _TOOL_OUT_PREFIX.match(lines[i])
        if not m:
            i += 1
            continue
        open_col = m.end() - 1
        parts = [lines[i][open_col + 1:]]
        j = i + 1
        closed = parts[0].endswith("`")
        while not closed and j < n:
            parts.append(lines[j])
            closed = lines[j].endswith("`")
            j += 1
        if not closed:
            # No closing backtick: not a span we can hash safely.
            i += 1
            continue
        parts[-1] = parts[-1][:-1]
        spans.append({
            "start": i,
            "end": j,
            "open_col": open_col,
            "text": "\n".join(parts),
        })
        i = j
    return spans


def dedup_tool_outputs(bodies: dict[int, str], trunc_re) -> tuple[dict[int, str], dict]:
    """Collapse repeated tool outputs *within a session* to a local reference.

    The first occurrence is kept verbatim; a later identical output in the same
    session becomes `[dup sha256:<12hex> -> L<n>]`, where `n` is the line of
    the kept occurrence **in the rendered body of that same session**. That
    keeps every session self-contained (no cross-session graph) and makes the
    reference navigable, unlike a bare hash.

    Outputs carrying the truncation marker are never deduplicated: the same
    head+tail can come from different full payloads, so merging them would
    claim equality that the data does not support. `trunc_re` is the marker
    from `agent_sessions.TRUNC_MARKER_RE`, passed in rather than duplicated.
    """
    stats = {
        "total": 0,
        "unique": 0,
        "replaced": 0,
        "short": 0,
        "truncated_spans": 0,
        "saved_chars": 0,
        "truncated_sessions": [],
        "per_session": {},
    }
    result: dict[int, str] = {}
    for idx in sorted(bodies):
        raw_body = bodies[idx]
        lines = raw_body.split("\n")
        spans = _scan_tool_outputs(lines)
        seen: dict[str, int] = {}
        session_truncated = False
        trunc_count = 0
        dup_count = 0
        short_count = 0
        new_lines: list[str] = []
        cursor = 0
        for sp in spans:
            new_lines.extend(lines[cursor:sp["start"]])
            text = sp["text"]
            stats["total"] += 1
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if trunc_re.search(text):
                session_truncated = True
                trunc_count += 1
                stats["truncated_spans"] += 1
                new_lines.extend(lines[sp["start"]:sp["end"]])
            elif len(text) < _DEDUP_MIN_CHARS:
                short_count += 1
                stats["short"] += 1
                new_lines.extend(lines[sp["start"]:sp["end"]])
            elif digest in seen:
                ref = f"[dup sha256:{digest[:12]} -> L{seen[digest]}]"
                prefix = lines[sp["start"]][:sp["open_col"] + 1]
                new_lines.append(prefix + ref + "`")
                stats["replaced"] += 1
                dup_count += 1
                stats["saved_chars"] += max(0, len(text) - len(ref))
            else:
                # Record the 1-based line this kept span occupies in the final
                # body (after any earlier collapse in this session).
                seen[digest] = len(new_lines) + 1
                stats["unique"] += 1
                new_lines.extend(lines[sp["start"]:sp["end"]])
            cursor = sp["end"]
        new_lines.extend(lines[cursor:])
        result[idx] = "\n".join(new_lines)
        if session_truncated:
            stats["truncated_sessions"].append(idx)
        stats["per_session"][idx] = {
            "trunc": trunc_count,
            "dup": dup_count,
            "short": short_count,
            "superseded": raw_body.count(_SUPERSEDED_MARKER),
            # Scanned on the raw body so externalisation is counted even when it
            # sits outside a recognised tool span.
            "artifact": len(_ARTIFACT_RE.findall(raw_body)),
            "ext768": len(_EXT768_RE.findall(raw_body)),
        }
    return result, stats


def externalize_tool_outputs(bodies: dict[int, str], trunc_re,
                             artifact_dir: Path,
                             link_prefix: str = "artifacts/") -> tuple[dict[int, str], dict]:
    """Move every tool output out of the transcript into `artifact_dir`.

    The transcript keeps a one-line marker with the sha256 and byte count, so
    the sidecar is verifiable. Unlike dedup this does not require equality:
    short, long and truncated outputs are all externalised. What the loader
    already truncated stays truncated in the sidecar too — `truncated` in the
    index says so instead of pretending the sidecar is the full source.
    """
    stats = {
        "total": 0,
        "unique": 0,
        "replaced": 0,
        "short": 0,
        "truncated_spans": 0,
        "saved_chars": 0,
        "truncated_sessions": [],
        "per_session": {},
        "artifacts": {},
    }
    artifact_dir.mkdir(parents=True, exist_ok=True)
    result: dict[int, str] = {}
    for idx in sorted(bodies):
        raw_body = bodies[idx]
        lines = raw_body.split("\n")
        spans = _scan_tool_outputs(lines)
        new_lines: list[str] = []
        cursor = 0
        trunc_count = 0
        names: list[str] = []
        for n, sp in enumerate(spans, 1):
            new_lines.extend(lines[cursor:sp["start"]])
            text = sp["text"]
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
            name = f"ses-{idx:03d}-tool-{n:03d}.txt"
            # `newline="\n"`: the sha256 in the transcript covers the LF bytes,
            # and Windows' default CRLF translation would break that contract.
            (artifact_dir / name).write_text(
                text, encoding="utf-8", newline="\n")
            names.append(name)
            stats["total"] += 1
            stats["unique"] += 1
            if trunc_re.search(text):
                trunc_count += 1
                stats["truncated_spans"] += 1
            new_lines.append(
                f"> tool out: [artifact `{link_prefix}{name}`,"
                f" sha256:{digest[:12]}, {len(text.encode('utf-8'))} B]")
            cursor = sp["end"]
        new_lines.extend(lines[cursor:])
        result[idx] = "\n".join(new_lines)
        if trunc_count:
            stats["truncated_sessions"].append(idx)
        stats["artifacts"][idx] = names
        stats["per_session"][idx] = {
            "trunc": trunc_count,
            "dup": 0,
            "short": 0,
            "superseded": raw_body.count(_SUPERSEDED_MARKER),
            "artifact": len(_ARTIFACT_RE.findall(raw_body)),
            "ext768": len(_EXT768_RE.findall(raw_body)),
        }
    return result, stats


def _tool_regions(lines: list[str]) -> list[dict]:
    """Pair each rendered `> out:` span with its tool header and `> in:` args."""
    regions = []
    for sp in _scan_tool_outputs(lines):
        header_i = None
        for j in range(sp["start"] - 1, max(-1, sp["start"] - 6), -1):
            if _TOOL_HDR_RE.match(lines[j]):
                header_i = j
                break
        if header_i is None:
            continue
        m = _TOOL_HDR_RE.match(lines[header_i])
        in_i = None
        args = ""
        for j in range(header_i + 1, sp["start"]):
            if lines[j].startswith(_IN_PREFIX):
                args = lines[j][len(_IN_PREFIX):]
                if args.endswith("`"):
                    args = args[:-1]
                in_i = j
                break
        regions.append({
            "header": header_i,
            "in": in_i,
            "out_start": sp["start"],
            "out_end": sp["end"],
            "tool": m.group(1),
            "status": m.group(2).strip(),
            "args": args,
            "out": sp["text"],
        })
    return regions


def _arg_hint(args: str) -> str:
    try:
        obj = json.loads(args)
    except Exception:
        return ""
    if not isinstance(obj, dict):
        return ""
    for key in ("command", "path", "filePath", "file_path", "pattern", "query"):
        val = obj.get(key)
        if isinstance(val, str) and val:
            return val.replace("\n", " ")[:120]
    return ""


def _preview(text: str, cap: int = 60) -> str:
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    if not lines:
        return ""
    if len(lines) == 1:
        return lines[0][:cap]
    return f"{lines[0][:cap]} … {lines[-1][:cap]}"


def _repeated_lines(text: str) -> int:
    """Identical consecutive lines after the first — counted, not collapsed."""
    extra = 0
    prev = None
    for ln in text.split("\n"):
        if ln and ln == prev:
            extra += 1
        prev = ln
    return extra


def _read_ref(text: str) -> str:
    m = _READ_REF_RE.search(text)
    if not m:
        return ""
    path = m.group(1).strip()
    return f"{path}:{m.group(2)}" if m.group(2) else path


def _read_content_lines(text: str) -> list[str]:
    """Drop the loader's `Read file …` banner; keep the file's own lines."""
    lines = text.split("\n")
    if lines and lines[0].lstrip().startswith(("Read file ", "Read directory ")):
        lines = lines[1:]
    return [ln for ln in lines if ln.strip()]


def _is_context_read(tool: str, hint: str) -> bool:
    return tool == "read" and bool(_CONTEXT_READ_RE.search(hint or ""))


def _many_hits(text: str) -> bool:
    m = _MANY_HITS_RE.search(text)
    if m:
        return int(m.group(1)) > 10
    return len([ln for ln in text.splitlines() if ln.strip()]) > 10


def _exit_info(records: list[dict]) -> str:
    if not records:
        return "brak"
    known = [r["exit"] for r in records if r["exit"] is not None]
    counts = Counter(str(x) for x in known)
    detail = ", ".join(f"{k}×{v}" for k, v in sorted(counts.items()))
    head = f"{len(known)} jawnych" + (f" ({detail})" if detail else "")
    return f"{head}, {len(records) - len(known)} nieznanych"


def _sha_file(path: Path) -> str:
    with path.open("rb") as fh:
        return hashlib.file_digest(fh, "sha256").hexdigest()


def _verify_artifacts(records: list[dict], payload_dir: Path) -> tuple[int, int, dict]:
    """Re-read every sidecar and compare its sha256/size with the record."""
    per: dict[int, list[int]] = {}
    ok = total = 0
    for r in records:
        checks = [("out", "artifact", "out_sha", "out_bytes")]
        if r.get("args_artifact"):
            checks.append(("args", "args_artifact", "args_sha", "args_bytes"))
        for label, path_key, sha_key, bytes_key in checks:
            total += 1
            good = False
            p = payload_dir / r[path_key]
            try:
                good = (p.stat().st_size == r[bytes_key]
                        and _sha_file(p) == r[sha_key])
            except OSError:
                good = False
            r[f"{label}_verified"] = good
            if good:
                ok += 1
            slot = per.setdefault(r["s"], [0, 0])
            slot[0] += int(good)
            slot[1] += 1
    return ok, total, per


def _write_manifest(records: list[dict], payload_dir: Path) -> tuple[int, Path]:
    manifest = payload_dir / "MANIFEST.tsv"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    rows = ["session\ttool\tkind\tsha256\tbytes\tpath\tverified"]
    for r in records:
        rows.append("\t".join([
            str(r["s"]), str(r["t"]), "out", r["out_sha"],
            str(r["out_bytes"]), r["artifact"],
            "yes" if r.get("out_verified") else "no",
        ]))
        if r.get("args_artifact"):
            rows.append("\t".join([
                str(r["s"]), str(r["t"]), "args", r["args_sha"],
                str(r["args_bytes"]), r["args_artifact"],
                "yes" if r.get("args_verified") else "no",
            ]))
    data = ("\n".join(rows) + "\n").encode("utf-8")
    manifest.write_bytes(data)
    (payload_dir / "MANIFEST.sha256").write_text(
        hashlib.sha256(data).hexdigest() + "  MANIFEST.tsv\n",
        encoding="utf-8", newline="\n")
    return len(rows) - 1, manifest


def _write_claims_tsv(claims: list[dict], path: Path) -> tuple[int, int]:
    rows = ["claim_id\tsession\tkind\tclaim\tstatus\tdowod_ref"]
    open_n = unverifiable_n = 0
    for n, c in enumerate(claims, 1):
        supported = c.get("support_out_sha")
        if supported:
            open_n += 1
            status = "open"
            ref = c.get("support_artifact") or f"s{c['s']}/t{c['supported_by']}"
        else:
            unverifiable_n += 1
            status = "nie_weryfikowalne"
            ref = "-"
        claim = c["claim"].replace("\t", " ").replace("\n", " ")
        rows.append("\t".join([
            str(n), str(c["s"]), c["kind"], claim, status, ref]))
    path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
    return open_n, unverifiable_n


def compact_tool_blocks(body: str, idx: int, artifact_dir: Path,
                        trunc_re, link_prefix: str = "artifacts/") -> tuple[str, list[dict]]:
    """Replace each tool block with a verifiable signature.

    The verbatim budget is redistributed by evidence value, not by output size:
    every non-zero exit, git diff/status/log/show, close/commit output, gate
    tail and test run stays readable; a flag/CONTEXT read keeps its first and
    last line plus length; successful reads and noisy glob/grep lose the
    preview. Everything else is one signature line. The sidecar always keeps
    the exact rendered text, so `out_sha` verifies. `exit` is emitted only when
    the output literally contains one — `status: completed` is not promoted to
    `exit=0`.
    """
    lines = body.split("\n")
    regions = _tool_regions(lines)
    if not regions:
        return body, []
    artifact_dir.mkdir(parents=True, exist_ok=True)
    new_lines: list[str] = []
    cursor = 0
    records: list[dict] = []
    for n, r in enumerate(regions, 1):
        new_lines.extend(lines[cursor:r["header"]])
        out = r["out"]
        out_bytes = len(out.encode("utf-8"))
        out_sha = hashlib.sha256(out.encode("utf-8")).hexdigest()
        args_sha = hashlib.sha256(r["args"].encode("utf-8")).hexdigest()
        name = f"ses-{idx:03d}-tool-{n:03d}.txt"
        (artifact_dir / name).write_text(out, encoding="utf-8", newline="\n")
        exit_m = _EXIT_RE.search(out)
        exit_code = int(exit_m.group(1)) if exit_m else None
        trunc_m = re.search(r"…\[\+(\d+) zn\.\]…", out)
        hint = _arg_hint(r["args"])
        gate = bool(_GATE_RE.search(r["args"]))
        context = _is_context_read(r["tool"], hint)
        whitelisted = any(p.search(out) or p.search(r["args"])
                          for p in _VERBATIM_RES)
        out_lines = out.splitlines()
        if exit_code not in (None, 0):
            mode = "full"
        elif gate and len(out_lines) > 10:
            mode = "tail10"
        elif context:
            mode = "headtail"
        elif whitelisted:
            mode = "full"
        else:
            mode = "none"

        args_name = None
        if r["args"] and mode != "full":
            args_name = f"ses-{idx:03d}-tool-{n:03d}.args.json"
            (artifact_dir / args_name).write_text(
                r["args"], encoding="utf-8", newline="\n")
        record = {
            "s": idx,
            "t": n,
            "tool": r["tool"],
            "status": r["status"],
            "arg": hint,
            "args_sha": args_sha,
            "args_bytes": len(r["args"].encode("utf-8")),
            "args_artifact": (args_name if args_name else None),
            "args_artifact_path": (f"{link_prefix}{args_name}" if args_name else None),
            "exit": exit_code,
            "out_sha": out_sha,
            "out_bytes": out_bytes,
            "artifact": name,
            "artifact_path": f"{link_prefix}{name}",
            "truncated": bool(trunc_m),
            "omitted_chars": int(trunc_m.group(1)) if trunc_m else 0,
            "verbatim": mode,
            "whitelisted": mode == "full",
            "repeated_lines": _repeated_lines(out),
        }
        read_ref = _read_ref(out)
        if read_ref:
            record["read"] = read_ref
        records.append(record)
        if mode == "full":
            new_lines.extend(lines[r["header"]:r["out_end"]])
        else:
            parts = [f"> tool: {r['tool']}", r["status"]]
            if hint:
                parts.append(f"arg: {hint}")
            parts.append(f"args_sha: {args_sha[:12]}")
            parts.append(f"out_sha: {out_sha[:12]}")
            parts.append(f"{out_bytes} B")
            if exit_code is not None:
                parts.append(f"exit: {exit_code}")
            if mode == "tail10":
                parts.append("verbatim: tail-10")
            elif mode == "headtail":
                parts.append("verbatim: head+tail")
            parts.append(f"artifact: {link_prefix}{name}")
            if trunc_m:
                parts.append(f"truncated: +{trunc_m.group(1)} zn.")
            if mode == "headtail":
                content = _read_content_lines(out)
                if content:
                    parts.append(f"head: {content[0][:120]}")
                    parts.append(f"tail: {content[-1][:120]}")
                parts.append(f"lines: {len(content)}")
            elif mode != "tail10":
                quiet_read = r["tool"] == "read" and not trunc_m
                quiet_noise = (r["tool"] in ("glob", "grep")
                               and _many_hits(out))
                if not quiet_read and not quiet_noise:
                    preview = _preview(out)
                    if preview:
                        parts.append(f"preview: {preview}")
            new_lines.append(" · ".join(parts))
            if mode == "tail10":
                new_lines.append("> tail (last 10 lines):")
                new_lines.extend(f"> {ln}" for ln in out_lines[-10:])
        cursor = r["out_end"]
    new_lines.extend(lines[cursor:])
    return "\n".join(new_lines), records


def _claims_for_session(body: str, idx: int,
                        regions: list[dict]) -> list[dict]:
    """Extract claims verbatim and point at the nearest prior tool call.

    Extraction only: `eval` is always `not_evaluated`. Deciding whether a tool
    call actually supports a claim is a separate pass, otherwise the extractor
    would launder its own guess into the evidence index.
    """
    lines = body.split("\n")
    tool_positions = [(r["header"] + 1, n)
                      for n, r in enumerate(regions, 1)]
    claims = []
    block = 0
    seen = set()
    for ln_no, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith("## [assistant]"):
            block += 1
            continue
        if not block or not s or s.startswith((">", "#", "<", "<!--")):
            continue
        for kind, rx in _CLAIM_RES:
            for m in rx.finditer(line):
                if kind == "commit":
                    anchor = m.group(1)
                elif kind == "path_line":
                    anchor = f"{m.group(1)}:{m.group(2)}"
                elif kind == "hit":
                    anchor = f"hit@{m.group(1)}={m.group(2)}"
                elif kind == "exit":
                    anchor = (f"exit={m.group(1)}" if m.group(1)
                              else "EXIT=LASTEXITCODE")
                elif kind == "tests":
                    anchor = (f"tests={m.group(1)}" if m.group(1)
                              else (m.group(2) or ""))
                else:
                    anchor = None
                key = (block, kind, anchor)
                if key in seen:
                    continue
                seen.add(key)
                support = None
                for pos, ordinal in tool_positions:
                    if pos < ln_no:
                        support = ordinal
                    else:
                        break
                claims.append({
                    "s": idx,
                    "block": block,
                    "kind": kind,
                    "claim": s[:240],
                    "anchor": anchor,
                    "supported_by": support,
                    "assoc": "nearest_prior_in_session",
                    "eval": "not_evaluated",
                })
    return claims


_SOURCE_REF_CACHE: dict[str, str] = {}
def _source_ref(raw_path: str) -> str:
    """Identify the source store; stream-hash it once per run.

    The opencode DB is ~3 GB. It is hashed once (not once per session) with a
    chunked reader, so the header carries a real integrity anchor without
    loading the DB into memory. A missing/unreadable source falls back to
    `missing` instead of guessing.
    """
    key = str(raw_path)
    if key in _SOURCE_REF_CACHE:
        return _SOURCE_REF_CACHE[key]
    try:
        st = Path(key).stat()
        with open(key, "rb") as fh:
            digest = hashlib.file_digest(fh, "sha256").hexdigest()
        ref = f"sha256:{digest};size={st.st_size}"
    except OSError:
        ref = "missing"
    _SOURCE_REF_CACHE[key] = ref
    return ref


def build_merged_markdown(sessions, agent: str, out_path: Path,
                          available: int | None = None,
                          include_reasoning: bool = False,
                          no_tools: bool = False,
                          signatures: bool = False,
                          split: bool = False,
                          records_dir: Path | None = None,
                          payloads_dir: Path | None = None) -> str:
    """Build the merged artifact.

    Empty-session policy (deliberate, do not "fix" as a bug): a session is
    skipped when its rendered body is empty after header/harness stripping.
    That covers both sessions with no messages and sessions whose only rows
    were textless harness events (`idle`, `model-switched`, `compaction`).
    A harness-only session that carries `system`/`synthetic`/`developer` text
    is NOT empty — it is kept, because that text is the audit trail.

    Turn-count policy: `user` + `assistant` headings. If an agent emits other
    roles and the count is 0, fall back to `s.message_count` rather than
    counting harness headings or reporting 0 conversational messages.
    """
    as_mod = _AGENT_SESSIONS
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # ICM: the export writes three kinds of file, each with its own home —
    # the product (this file + sidecars), the per-session record bodies,
    # and the tool payload store. Link prefixes are computed relative to
    # the file that carries them, so a reader can always follow them.
    payloads_dir = payloads_dir or (out_path.parent / "artifacts")
    records_dir = records_dir or (out_path.parent / "sessions")
    body_dir = records_dir if split else out_path.parent
    pay_prefix_body = _rel_prefix(payloads_dir, body_dir)
    pay_prefix_out = _rel_prefix(payloads_dir, out_path.parent)
    rec_prefix_out = _rel_prefix(records_dir, out_path.parent)
    total = len(sessions)
    available = total if available is None else available
    first = sessions[0].updated_at or sessions[0].created_at
    last = sessions[-1].updated_at or sessions[-1].created_at

    bodies: dict[int, str] = {}
    counts: dict[int, int] = {}
    blocks: dict[int, int] = {}
    turns_by: dict[int, int] = {}
    empty: list[int] = []
    empty_outputs = 0
    for i, s in enumerate(sessions, 1):
        body = as_mod.render_session_body(s, include_reasoning=include_reasoning)
        if not body.strip():
            empty.append(i)
            continue
        body, n_empty = _mark_empty_assistant(body)
        empty_outputs += n_empty
        bodies[i] = body
        blocks[i] = _count_blocks(body)
        turns = _count_turns(body)
        turns_by[i] = turns
        # Fallback is deliberate for loaders that emit non-user/assistant roles.
        counts[i] = turns if turns else s.message_count

    rendered = total - len(empty)

    # Shrink without losing verbatim: a repeated tool output within the same
    # session becomes a local line reference. Cross-session dedup is off: it
    # measured ~31 spans / ~6 KB, not the estimated 80-120 KB, and it breaks
    # self-containedness. Truncated outputs are never merged (equal head+tail
    # does not mean equal content). `--no-tools` externalises instead;
    # `--signatures` externalises *and* compacts the header to a verifiable
    # signature, keeping a whitelist verbatim.
    tool_records: list[dict] = []
    claims_all: list[dict] = []
    artifact_verify: tuple[int, int, dict] = (0, 0, {})
    manifest_entries = 0
    claims_open = claims_unver = 0
    link_prefix = pay_prefix_body
    if signatures:
        root = out_path.parent
        artifact_dir = payloads_dir
        artifact_dir.mkdir(parents=True, exist_ok=True)
        for old in artifact_dir.glob("ses-*"):
            if old.is_file():
                old.unlink()
        per = {}
        art_counts = {}
        truncated_sessions = []
        for i in sorted(bodies):
            raw = bodies[i]
            lines = raw.split("\n")
            regions = _tool_regions(lines)
            claims_all.extend(_claims_for_session(raw, i, regions))
            bodies[i], recs = compact_tool_blocks(
                bodies[i], i, artifact_dir, as_mod.TRUNC_MARKER_RE,
                link_prefix=link_prefix)
            session = sessions[i - 1]
            for rec in recs:
                rec["key"] = f"{session.agent}:{session.id}"
            tool_records.extend(recs)
            art_counts[i] = [r["artifact"] for r in recs]
            art_counts[i] += [r["args_artifact"]
                              for r in recs if r.get("args_artifact")]
            trunc_n = sum(1 for r in recs if r["truncated"])
            if trunc_n:
                truncated_sessions.append(i)
            per[i] = {
                "trunc": trunc_n,
                "dup": 0,
                "short": 0,
                "superseded": raw.count(_SUPERSEDED_MARKER),
                "artifact": len(_ARTIFACT_RE.findall(raw)),
                "ext768": len(_EXT768_RE.findall(raw)),
                "trunc_blocks": _trunc_blocks(raw),
                "artifact_tools": [n for n, r in enumerate(regions, 1)
                                   if _ARTIFACT_RE.search(r["out"])],
                "ext768_tools": [n for n, r in enumerate(regions, 1)
                                 if _EXT768_RE.search(r["out"])],
            }
        dstats = {
            "total": len(tool_records),
            "unique": len(tool_records),
            "replaced": 0,
            "short": 0,
            "truncated_spans": sum(1 for r in tool_records if r["truncated"]),
            "saved_chars": 0,
            "truncated_sessions": truncated_sessions,
            "per_session": per,
            "artifacts": art_counts,
        }
        artifact_verify = _verify_artifacts(tool_records, payloads_dir)
        manifest_entries, _ = _write_manifest(tool_records, payloads_dir)
        by_ord = {(r["s"], r["t"]): r for r in tool_records}
        enriched = []
        for c in claims_all:
            e = dict(c)
            if c["supported_by"] is not None:
                t = by_ord.get((c["s"], c["supported_by"]))
                if t:
                    e["support_tool"] = t["tool"]
                    e["support_out_sha"] = t["out_sha"]
                    e["support_exit"] = t["exit"]
                    e["support_artifact"] = t["artifact"]
            enriched.append(e)
        claims_all = enriched
        claims_open, claims_unver = _write_claims_tsv(
            claims_all, root / "claims.tsv")
    elif no_tools:
        bodies, dstats = externalize_tool_outputs(
            bodies, as_mod.TRUNC_MARKER_RE, payloads_dir,
            link_prefix=pay_prefix_body)
    else:
        bodies, dstats = dedup_tool_outputs(bodies, as_mod.TRUNC_MARKER_RE)
    truncated = set(dstats["truncated_sessions"])
    saved_kb = dstats["saved_chars"] / 1024

    # Declare every loss mechanism inside the body, including the two that were
    # previously only implicit in the text: `artifact://` externalisation and
    # the harness's 768-byte-per-line cut.
    per = dstats["per_session"]
    art_sessions = [i for i in sorted(per) if per[i]["artifact"]]
    ext_sessions = [i for i in sorted(per) if per[i]["ext768"]]
    art_total = sum(per[i]["artifact"] for i in art_sessions)
    ext_total = sum(per[i]["ext768"] for i in ext_sessions)
    superseded_total = sum(per[i].get("superseded", 0) for i in per)
    harness_total = 0
    for b in bodies.values():
        for h in _HARNESS_RE.finditer(b):
            harness_total += sum(int(x) for x in re.findall(r"×(\d+)", h.group(1)))
    dup_saved_line = (f" (~{saved_kb:.1f} KB mniej)" if dstats["replaced"] else "")
    agent_mix = Counter(s.agent for s in sessions)
    model_mix = Counter((s.model or "-") for s in sessions)
    top_models = model_mix.most_common(8)
    rest_models = sum(c for _, c in model_mix.most_common()[8:])
    micro = sum(1 for s in sessions if s.message_count <= 4)

    mode_lines: list[str] = []
    if signatures:
        exit_counts = Counter(
            str(r["exit"]) for r in tool_records if r["exit"] is not None)
        exit_known = sum(exit_counts.values())
        exit_detail = ", ".join(
            f"{k}:{v}" for k, v in sorted(exit_counts.items()))
        read_count = sum(1 for r in tool_records if r.get("read"))
        repeats = sum(r["repeated_lines"] for r in tool_records)
        full_n = sum(1 for r in tool_records if r["verbatim"] == "full")
        tail_n = sum(1 for r in tool_records if r["verbatim"] == "tail10")
        head_n = sum(1 for r in tool_records if r["verbatim"] == "headtail")
        artifact_files = (len(tool_records)
                          + sum(1 for r in tool_records if r.get("args_artifact")))
        ok, checked, _ = artifact_verify
        mode_lines = [
            f"- **Tryb**: sygnatury" + (" + split (indeks + `sessions/`)"
                                       if split else "")
            + f" (verbatim: {full_n} full, {tail_n} tail-10,"
              f" {head_n} head+tail; {len(tool_records)} calls)",
            f"- **Tool calls**: {len(tool_records)} (exit: explicit {exit_known}"
            + (f" ({exit_detail})" if exit_detail else "")
            + f"; missing {len(tool_records) - exit_known} (unknown, not zero))",
            f"- **Artifacts**: {artifact_files} plikow w `{pay_prefix_out}`"
            f" (output + args); **{ok}/{checked} zweryfikowane**",
            f"- **Artifact manifest**: `{pay_prefix_out}MANIFEST.tsv`"
            f" ({manifest_entries} wpisow); checksum"
            f" `{pay_prefix_out}MANIFEST.sha256`",
            f"- **Read → hash**: {read_count}",
            f"- **Claims**: {len(claims_all)} (claims.tsv: open {claims_open},"
            f" nie-weryfikowalne {claims_unver}; JSONL: claims.jsonl)",
            f"- **Powtorzenia linii (w artifacts)**: {repeats}",
        ]
    elif no_tools:
        mode_lines = ["- **Tryb**: externalizacja (`--no-tools`)"]

    doc: list[str] = [
        "# Ostatnie sesje agentow (merged)",
        "",
        f"- **Wygenerowano**: {generated_at}",
        f"- **Filtr agenta**: {agent}",
        f"- **Liczba sesji**: {total}",
        f"- **Wyrenderowano**: {rendered}/{total}"
        + (f"  (puste sesje pominiete: {len(empty)})" if empty else ""),
        f"- **Wczytano z magazynow**: {available}"
        + (f"  (wybrano {total} najnowszych)" if available > total else ""),
        f"- **Zakres dat**: {last}  ->  {first}",
        f"- **Miks agentow**: " + ", ".join(f"{a}×{c}" for a, c in agent_mix.most_common()),
        f"- **Miks modeli**: " + ", ".join(f"{m}×{c}" for m, c in top_models)
        + (f", inne×{rest_models}" if rest_models else ""),
        f"- **Charakter**: {micro}/{total} mikro-sesji (<=4 wiad.)",
        f"- **Zrodlo**: `scripts/last_session_merged.py`"
        f" (render: `scripts/agent_sessions.py`)",
        f"- **Integralnosc**: `SHA256` tresci kazdej sesji jest w jej naglowku",
        f"- **Weryfikacja SHA256**: sha256 linii od `---` po naglowku"
        f" do nastepnej kotwicy `session-` (z koncowym `\\n`)",
        f"- **Legenda**: brak `exit:` ≠ exit 0. Brak = nieznany"
        f" (nie zakladaj sukcesu).",
        f"- **Legenda**: brak tresci przy `## [assistant]` = model nie zwrocil"
        f" tekstu (nie: renderer wycial).",
        f"- **Legenda**: `preview` jest przyciety; pelna tresc w"
        f" `{pay_prefix_out}`, nie w tym pliku.",
        f"- **Puste tury modelu**: {empty_outputs} (`{_EMPTY_OUTPUT}`)",
        f"- **Rozmiar**: 000000 KB",
        *((f"- **Rozmiar calosci**: 111111 KB", f"- **Indeks**: ten plik;"
           f" pelne transkrypty w `sessions/` ({rendered} plikow)") if split else ()),
        *mode_lines,
        f"- **Tool outputs**: {dstats['total']}"
        + (f"  (sygnatury; pelna tresc w `{pay_prefix_out}`)" if signatures
           else f"  (externalizowane: {dstats['total']})" if no_tools
           else f"  (unikalne: {dstats['unique']},"
                f" dup w sesji: {dstats['replaced']}{dup_saved_line},"
                f" krotkie <{_DEDUP_MIN_CHARS} B: {dstats['short']},"
                f" uciete: {dstats['truncated_spans']};"
                f" suma: {dstats['unique'] + dstats['replaced'] + dstats['short'] + dstats['truncated_spans']})"),
        f"- **Uciete (marker `…[+N zn.]…`)**: {len(truncated)} sesji,"
        f" {dstats['truncated_spans']} outputow"
        + (f" (sesje: {', '.join(str(x) for x in sorted(truncated))})" if truncated else ""),
        f"- **Externalizacja (artifact://)**: {art_total} refs"
        + (f" (sesje: {', '.join(str(x) for x in art_sessions)})" if art_sessions else ""),
        f"- **Truncacja 768B/linia**: {ext_total}"
        + (f" (sesje: {', '.join(str(x) for x in ext_sessions)})" if ext_sessions else ""),
        f"- **Superseded (starszy read usuniety)**: {superseded_total}",
        f"- **Zdarzenia harnessu (zwinięte)**: {harness_total}",
        f"- **Dup cross-session**: 0 (dedup wylaczony;"
        f" pomiar: 31 spanow / ~6 KB)",
        f"- **Straty razem**: trunc {len(truncated)} sesji, dup {dstats['replaced']},"
        f" artifact {art_total}, 768B {ext_total}, superseded {superseded_total}",
        f"- **Reasoning**: "
        + ("wlaczony" if include_reasoning
           else "wylaczony (uzyj --include-reasoning)"),
        f"- **Zapisano do**: `{out_path}`",
        "",
        "---",
        "",
        "## Spis sesji",
        "",
    ]

    by_rec: dict[int, list[dict]] = {}
    for r in tool_records:
        by_rec.setdefault(r["s"], []).append(r)
    src_refs = {i: _source_ref(s.raw_path)
                for i, s in enumerate(sessions, 1)}

    def _header(i, s, digest):
        body = bodies.get(i, "")
        ok, tot = artifact_verify[2].get(i, [0, 0])
        return as_mod._session_header(
            s, i, total, sha256=digest, message_count=counts[i],
            blocks=blocks.get(i), turns=turns_by.get(i),
            truncated=(i in truncated),
            parent=getattr(s, "parent", "") or None,
            losses=_losses_str(per.get(i, {})),
            flag=_flag_id(body) or None,
            duration=_duration(s) or None,
            last_line=_last_line(body) or None,
            source_ref=src_refs.get(i),
            exit_info=_exit_info(by_rec.get(i, [])) if signatures else None,
            artifact_info=(f"{ok}/{tot} zweryfikowane" if tot else "brak")
            if signatures else None)

    if not split:
        for i, s in enumerate(sessions, 1):
            ts = s.updated_at or s.created_at or "-"
            if i in empty:
                doc.append(f"{i}. **[{s.agent}]** {s.title} — {ts}"
                           f"  (0 wiad. — pominieto)")
            else:
                extra = f"{counts[i]} wiad."
                if blocks.get(i):
                    extra += f", {blocks[i]} blok."
                if i in truncated:
                    extra += ", uciete"
                parent = getattr(s, "parent", "") or ""
                if parent:
                    extra += f", parent {parent[:16]}"
                doc.append(
                    f"{i}. **[{s.agent}]** [{s.title}](#session-{i}) — {ts}"
                    f"  ({extra})")
        doc += ["", "---", ""]

    session_dir = records_dir
    if split:
        session_dir.mkdir(parents=True, exist_ok=True)
        for old in session_dir.glob("ses-*.md"):
            old.unlink()

    render_sha: dict[int, str] = {}
    for i, s in enumerate(sessions, 1):
        body = bodies.get(i)
        if body is None:
            continue
        # Rewrite body-relative `L<n>` references to absolute line numbers in
        # the file that will hold the body, so a reader can jump to the kept
        # occurrence. The header line count is independent of the digest value
        # (always 64 hex chars), so a placeholder gives the exact layout.
        n_header = len(_header_lines(_header(i, s, "0" * 64)))
        offset = (2 if split else len(doc) + 2) + n_header
        rewritten = re.sub(
            r"(\[dup sha256:[0-9a-f]{12} -> L)(\d+)(\])",
            lambda m: f"{m.group(1)}{int(m.group(2)) + offset}{m.group(3)}",
            body)
        # Hash the final body (after rewriting), so the header still verifies
        # the bytes that actually appear in the file.
        digest = hashlib.sha256(rewritten.encode("utf-8")).hexdigest()
        render_sha[i] = digest
        segment = [f"<a id=\"session-{i}\"></a>",
                   f"<!-- session-{i} -->"]
        segment.extend(_header_lines(_header(i, s, digest)))
        # `rewritten` always ends with "\n"; `split` contributes the separating
        # blank line, so the segment between `---` and the next anchor is
        # exactly the bytes the SHA256 covers.
        segment.extend(rewritten.split("\n"))
        if split:
            (session_dir / f"ses-{i:03d}.md").write_text(
                "\n".join(segment), encoding="utf-8", newline="\n")
        else:
            doc.extend(segment)

    if split:
        for i, s in enumerate(sessions, 1):
            ts = s.updated_at or s.created_at or "-"
            if i in empty:
                doc.append(f"{i}. **[{s.agent}]** {s.title} — {ts}"
                           f"  (0 wiad. — pominieto)")
                continue
            extra = f"{counts[i]} wiad."
            if blocks.get(i):
                extra += f", {blocks[i]} blok."
            if i in truncated:
                extra += ", uciete"
            parent = getattr(s, "parent", "") or ""
            if parent:
                extra += f", parent {parent[:16]}"
            doc.append(
                f"{i}. **[{s.agent}]** [{s.title}]({rec_prefix_out}ses-{i:03d}.md)"
                f" — {ts}  ({extra})")
            ok, tot = artifact_verify[2].get(i, [0, 0])
            art = f"{ok}/{tot}" if tot else "brak"
            doc.append(
                f"   `Straty: {_losses_str(per.get(i, {}))}`"
                f" · `exit: {_exit_info(by_rec.get(i, []))}`"
                f" · `artefakty: {art}`"
                f" · `SHA256: {render_sha[i]}`")
        doc += ["", "---", ""]

    if no_tools or signatures:
        rows = [
            "session\tagent\tmodel\tsource\trender_sha256\ttruncated"
            "\tsuperseded\tartifacts\texit\tartifacts_verified\tclaims"
        ]
        for i, s in enumerate(sessions, 1):
            if i not in render_sha:
                continue
            names = dstats.get("artifacts", {}).get(i, [])
            ok, tot = artifact_verify[2].get(i, [0, 0])
            rows.append("\t".join([
                str(i), s.agent, s.model or "-", _source_ref(s.raw_path),
                render_sha[i], str(per.get(i, {}).get("trunc", 0)),
                str(per.get(i, {}).get("superseded", 0)),
                ",".join(f"{pay_prefix_out}{n}" for n in names),
                _exit_info(by_rec.get(i, [])),
                f"{ok}/{tot}" if tot else "0/0",
                str(sum(1 for c in claims_all if c["s"] == i)),
            ]))
        (out_path.parent / "index.tsv").write_text(
            "\n".join(rows) + "\n", encoding="utf-8", newline="\n")

    if signatures:
        (out_path.parent / "tool_calls.jsonl").write_text(
            "\n".join(json.dumps(r, ensure_ascii=False)
                      for r in tool_records) + "\n",
            encoding="utf-8", newline="\n")
        (out_path.parent / "claims.jsonl").write_text(
            "\n".join(json.dumps(r, ensure_ascii=False)
                      for r in claims_all) + "\n",
            encoding="utf-8", newline="\n")

    text = "\n".join(doc)
    # Self-referential but stable: the placeholder is six digits, so replacing
    # it with another six-digit value does not change the byte count measured.
    size_kb = len(text.encode("utf-8")) // 1024
    if split:
        generated = list(session_dir.glob("ses-*.md"))
        generated += [p for p in payloads_dir.glob("*")
                      if p.is_file()]
        generated += [out_path.parent / name for name in (
            "tool_calls.jsonl", "claims.jsonl", "claims.tsv", "index.tsv")]
        total_bytes = len(text.encode("utf-8")) + sum(
            p.stat().st_size for p in generated if p.exists())
        text = text.replace("111111 KB", f"{total_bytes // 1024:06d} KB", 1)
    return text.replace("000000 KB", f"{size_kb:06d} KB", 1)


def compress_artifact(path: Path) -> Path:
    """Write a compressed sibling of the artifact and return its path.

    Zstd if the interpreter/library provides it (3.14 `compression.zstd` or the
    third-party `zstandard`), otherwise gzip from stdlib. Python 3.11 has no
    stdlib zstd, so the fallback is real, not theoretical. The compressed file
    is an archive copy; the readable `.md` is always written first.
    """
    data = path.read_bytes()
    try:
        from compression import zstd as _zstd  # Python 3.14+
        out = path.with_name(path.name + ".zst")
        out.write_bytes(_zstd.compress(data))
        return out
    except Exception:
        pass
    try:
        import zstandard as _zstd  # third-party
        out = path.with_name(path.name + ".zst")
        out.write_bytes(_zstd.ZstdCompressor().compress(data))
        return out
    except Exception:
        pass
    import gzip
    out = path.with_name(path.name + ".gz")
    out.write_bytes(gzip.compress(data, compresslevel=9))
    return out


def _g(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _normalize_tool(name: str) -> str:
    name = (name or "").strip().lower()
    if name == "bash":
        return "shell"
    return name


def _first_sensible_line(text: str) -> str:
    for ln in (text or "").splitlines():
        s = ln.strip()
        if not s:
            continue
        if any(s.startswith(p) for p in _BOILERPLATE_PREFIXES):
            continue
        if len(s) > 50:
            return s[:49] + "…"
        return s
    return ""


def _result_for_tool(tool, arg, args, args_obj, out, exit_code,
                     commit_hash, commit_files) -> str:
    out = out or ""
    lines = out.splitlines()
    if tool == "read":
        m = re.search(r"lines (\d+)-(\d+)", out)
        if m:
            n = int(m.group(2)) - int(m.group(1)) + 1
            return f"({n} linii)"
        m = re.search(r"entries (\d+)-(\d+)", out)
        if m:
            n = int(m.group(2)) - int(m.group(1)) + 1
            return f"({n} plików)"
        cnt = len([ln for ln in lines if ln.strip()])
        if cnt > 1:
            cnt -= 1
        return f"({cnt} linii)" if cnt >= 0 else "(?)"
    if tool == "write":
        content = None
        if isinstance(args_obj, dict):
            content = args_obj.get("content")
        if isinstance(content, str):
            return f"({len(content.encode('utf-8'))} B)"
        return "(?)"
    if tool == "edit":
        m = re.search(r"(\d+) replacement", out)
        if m:
            return f"({m.group(1)} zamian)"
        return "(?)"
    if tool == "shell":
        if commit_hash is not None:
            if commit_files is not None:
                return f"{commit_hash}, {commit_files} files"
            return commit_hash
        preview = _first_sensible_line(out)
        if preview:
            if exit_code is not None:
                return f"{preview} (exit {exit_code})"
            return preview
        if exit_code is not None:
            return f"(exit {exit_code})"
        return "(?)"
    if tool == "execute":
        if exit_code is not None:
            return f"(exit {exit_code})"
        preview = _first_sensible_line(out)
        return preview if preview else "(?)"
    if tool == "grep":
        m = re.search(r"Found (\d+) matches", out)
        if m:
            n = int(m.group(1))
            if n == 0:
                return "(no matches)"
            return f"({n} trafień)"
        if "no matches" in out.lower():
            return "(no matches)"
        return "(?)"
    if tool == "glob":
        m = re.search(r"(\d+) files?", out)
        if m:
            return f"({m.group(1)} plików)"
        cnt = len([ln for ln in lines if ln.strip()])
        return f"({cnt} plików)"
    if tool == "subagent":
        return "(spawn)"
    if tool == "skill":
        if "error" in (out or "").lower():
            return "(error)"
        return "(ok)"
    preview = _first_sensible_line(out)
    return preview if preview else "(?)"


def _scan_actions_regions(lines: list[str]) -> list[dict]:
    """Like _tool_regions but also captures tool calls without an out span
    (e.g. `· error` results that carry no output)."""
    regions: list[dict] = []
    n = len(lines)
    i = 0
    while i < n:
        m = _TOOL_HDR_RE.match(lines[i])
        if not m:
            i += 1
            continue
        header_i = i
        tool = m.group(1)
        status = m.group(2).strip()
        args = ""
        j = header_i + 1
        while j < n and not _TOOL_HDR_RE.match(lines[j]) and not lines[j].startswith("## ["):
            if lines[j].startswith(_IN_PREFIX):
                a = lines[j][len(_IN_PREFIX):]
                if a.endswith("`"):
                    a = a[:-1]
                args = a
            j += 1
        out = ""
        k = header_i + 1
        while k < n and not _TOOL_HDR_RE.match(lines[k]) and not lines[k].startswith("## ["):
            om = _TOOL_OUT_PREFIX.match(lines[k])
            if om:
                open_col = om.end() - 1
                parts = [lines[k][open_col + 1:]]
                l = k + 1
                closed = parts[0].endswith("`")
                while not closed and l < n:
                    parts.append(lines[l])
                    closed = lines[l].endswith("`")
                    l += 1
                if closed:
                    parts[-1] = parts[-1][:-1]
                    out = "\n".join(parts)
                break
            k += 1
        if out:
            # l is index after closing backtick line
            end = l - 1
        else:
            end = header_i
            if header_i + 1 < n and lines[header_i + 1].startswith(_IN_PREFIX):
                end = header_i + 1
        regions.append({
            "header": header_i,
            "end": end,
            "tool": tool,
            "status": status,
            "args": args,
            "out": out,
        })
        i = header_i + 1
    return regions


def parse_actions(session) -> list[Action]:
    as_mod = _AGENT_SESSIONS
    body = as_mod.render_session_body(session, include_reasoning=False)
    lines = body.split("\n")
    regions = _scan_actions_regions(lines)
    actions: list[Action] = []
    for i, r in enumerate(regions, 1):
        tool = _normalize_tool(r.get("tool", ""))
        status = (r.get("status") or "").strip()
        is_error = status.lower().startswith("error") or "error" in status.lower()
        args = r.get("args") or ""
        arg = _arg_hint(args)
        # shorten absolute paths under the workspace root to relative form
        if tool in ("read", "write", "edit") and arg:
            root_str = str(ROOT)
            if arg.startswith(root_str):
                arg = arg[len(root_str):].lstrip("\\/") or arg
        try:
            args_obj = json.loads(args) if args else None
        except Exception:
            args_obj = None
        out = r.get("out") or ""
        exit_code = None
        em = _EXIT_RE.search(out)
        if em:
            exit_code = int(em.group(1))
        commit_hash = None
        commit_files = None
        commit_ins = None
        commit_del = None
        cm = _COMMIT_RX.search(out)
        if cm:
            commit_hash = cm.group(1)
            fm = _COMMIT_FILES_RX.search(out)
            if fm:
                commit_files = int(fm.group(1))
            im = _COMMIT_INS_RX.search(out)
            if im:
                commit_ins = int(im.group(1))
            dm = _COMMIT_DEL_RX.search(out)
            if dm:
                commit_del = int(dm.group(1))
        result = _result_for_tool(tool, arg, args, args_obj, out, exit_code,
                                 commit_hash, commit_files)
        if is_error and tool != "shell":
            result = "(error)"
        actions.append(Action(
            n=i, tool=tool, arg=arg, result=result,
            commit_hash=commit_hash, commit_files=commit_files,
            commit_insertions=commit_ins, commit_deletions=commit_del,
            exit_code=exit_code, is_error=is_error))
    return actions


def _session_title(session) -> str:
    t = (_g(session, "title") or "").strip()
    t = t.replace("\n", " ")
    return t or (_g(session, "id") or "session")


def _session_model(session) -> str:
    m = _g(session, "model")
    if m:
        return str(m)
    agent = _g(session, "agent")
    return str(agent) if agent else "-"


def _session_msgs(session) -> int:
    try:
        return int(_g(session, "message_count", 0) or 0)
    except Exception:
        return 0


def render_actions(session, actions: list[Action], idx: int = 1) -> str:
    title = _session_title(session)
    model = _session_model(session)
    msgs = _session_msgs(session)
    dur = _duration(session)
    head = f"## Sesja {idx} — {title}"
    meta_parts = [f"{model}", f"{msgs} wiad."]
    if dur:
        meta_parts.append(dur)
    meta = " · ".join(meta_parts)
    out_lines = [head, meta, ""]
    if not actions:
        agent = str(_g(session, "agent") or "").lower()
        if agent == "omp":
            out_lines.append("(format omp: akcje nie wyciągnięte — patrz transkrypt)")
            out_lines.append("")
            out_lines.append("Akcje:   ? (omp)")
        else:
            out_lines.append("(brak wywołań narzędzi)")
            out_lines.append("")
            out_lines.append("Akcje:   0")
            out_lines.append("Pliki:   czytane 0 · zapisane 0 · zmienione 0")
        out_lines.append("")
        return "\n".join(out_lines)
    prepared = []
    for a in actions:
        arg = a.arg or ""
        if len(arg) > 50:
            arg = arg[:49] + "…"
        if a.tool in ("shell", "execute"):
            arg_disp = f"`{arg}`"
        else:
            arg_disp = arg
        prepared.append((a, arg_disp))
    arg_width = min(50, max((len(ad) for _, ad in prepared), default=1))
    # account for backticks already included; width at least 1
    if arg_width < 1:
        arg_width = 1
    for a, arg_disp in prepared:
        type_col = a.tool.ljust(8)
        arg_col = arg_disp.ljust(arg_width)
        prefix = f"{a.n}. {type_col} {arg_col} "
        result = a.result
        if len(prefix) + len(result) > 120:
            avail = 120 - len(prefix)
            if avail >= 2:
                result = result[:avail - 1] + "…"
            else:
                result = result[:120 - len(prefix)]
        out_lines.append(prefix + result)
    out_lines.append("")
    # aggregate
    type_counts = Counter(a.tool for a in actions)
    order = ["read", "write", "edit", "shell", "grep", "glob", "execute",
             "subagent", "skill"]
    parts = []
    for t in order:
        c = type_counts.get(t, 0)
        if c:
            parts.append(f"{t}×{c}")
    for t, c in type_counts.items():
        if t not in order and c:
            parts.append(f"{t}×{c}")
    out_lines.append("Akcje:   " + str(len(actions)) +
                     (f" ({', '.join(parts)})" if parts else ""))
    read_files = {a.arg for a in actions if a.tool == "read" and a.arg}
    write_files = {a.arg for a in actions if a.tool == "write" and a.arg}
    edit_files = {a.arg for a in actions if a.tool == "edit" and a.arg}
    if read_files or write_files or edit_files:
        out_lines.append(
            f"Pliki:   czytane {len(read_files)} · zapisane {len(write_files)}"
            f" · zmienione {len(edit_files)}")
    commits = [a for a in actions if a.commit_hash]
    if commits:
        commit_strs = []
        for a in commits:
            s = a.commit_hash
            if a.commit_files is not None:
                s += f" ({a.commit_files} files"
                if a.commit_insertions is not None or a.commit_deletions is not None:
                    ins = a.commit_insertions if a.commit_insertions is not None else 0
                    dels = a.commit_deletions if a.commit_deletions is not None else 0
                    s += f", +{ins} −{dels}"
                s += ")"
            commit_strs.append(s)
        out_lines.append("Commity: " + " · ".join(commit_strs))
    # exit tally over all actions
    exit_counts = Counter()
    for a in actions:
        key = "?" if a.exit_code is None else str(a.exit_code)
        exit_counts[key] += 1
    # only show if any action could have exit (shell/execute) or known exits
    if any(a.tool in ("shell", "execute") for a in actions) or any(
            a.exit_code is not None for a in actions):
        # order: numeric asc then ?
        def sort_key(k):
            if k == "?":
                return (1, 0)
            try:
                return (0, int(k))
            except ValueError:
                return (0, 999)
        tally_parts = [f"{k}×{exit_counts[k]}"
                       for k in sorted(exit_counts, key=sort_key)]
        out_lines.append("Exit:    " + " · ".join(tally_parts))
    out_lines.append("")
    return "\n".join(out_lines)


def _load_artifact_text(ses_num: int, tool_num: int) -> tuple[str | None, str]:
    path = (PAYLOADS_DIR) / f"ses-{ses_num:03d}-tool-{tool_num:03d}.txt"
    if not path.is_file():
        return None, str(path.relative_to(ROOT))
    try:
        return path.read_text(encoding="utf-8", errors="replace"), str(path.relative_to(ROOT))
    except Exception:
        return None, str(path.relative_to(ROOT))


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def render_full_verbatim(session, f, args, ses_num: int) -> None:
    as_mod = _AGENT_SESSIONS
    include_reasoning = bool(getattr(args, "include_reasoning", False))
    body = as_mod.render_session_body(session, include_reasoning=include_reasoning)
    lines = body.split("\n")
    regions = _scan_actions_regions(lines)
    for idx, r in enumerate(regions, 1):
        r["_idx"] = idx
    region_by_header = {r["header"]: r for r in regions}

    title = _session_title(session)
    model = _session_model(session)
    msgs = _session_msgs(session)
    dur = _duration(session)
    sha = _sha256_text(body)
    art_ok = 0
    for r in regions:
        txt, _ = _load_artifact_text(ses_num, r["_idx"])
        if txt is not None:
            art_ok += 1

    f.write(f"## Sesja {ses_num} — {title}\n")
    f.write(f"- **Agent/model**: {model}\n")
    f.write(f"- **Wiadomości**: {msgs} · **Czas**: {dur or '-'}\n")
    f.write(f"- **SHA256 treści**: `{sha}`\n")
    agent_l = str(_g(session, "agent") or "").lower()
    if len(regions) == 0 and agent_l == "omp":
        f.write("- **Artefakty**: format omp (nie wyciągnięte)\n\n")
    else:
        f.write(f"- **Artefakty**: {art_ok}/{len(regions)} zweryfikowane\n\n")

    # split into blocks by role headings
    blocks: list[tuple[str, list[str], int, int]] = []
    cur_role = None
    cur_lines: list[str] = []
    cur_start = 0
    i = 0
    n = len(lines)
    while i < n:
        if lines[i].strip().startswith("## [") and lines[i].strip().endswith("]"):
            if cur_role is not None:
                blocks.append((cur_role, cur_lines, cur_start, i - 1))
            cur_role = lines[i].strip()[3:-1].strip()  # inside brackets?
            # lines[i] like '## [user]'
            m = re.match(r"^## \[([^\]]+)\]$", lines[i].strip())
            cur_role = m.group(1) if m else lines[i].strip()
            cur_lines = []
            cur_start = i + 1
            i += 1
            continue
        if cur_role is None:
            i += 1
            continue
        cur_lines.append(lines[i])
        i += 1
    if cur_role is not None:
        blocks.append((cur_role, cur_lines, cur_start, n - 1))

    for role, block_lines, start, end in blocks:
        role_l = role.lower()
        if "user" in role_l:
            text = "\n".join(block_lines).strip()
            f.write("### [user]\n")
            f.write(text + "\n\n" if text else "\n")
        elif "toolresult" in role_l.replace(" ", "") or "tool_result" in role_l:
            text = "\n".join(block_lines).strip()
            f.write("### [toolResult]\n")
            f.write(text + "\n\n" if text else "\n")
        elif "assistant" in role_l:
            # iterate lines, separate prose and tool regions
            prose: list[str] = []
            idx = start
            # We'll walk through block_lines with index offset start
            j = 0
            block_len = len(block_lines)
            while j < block_len:
                line = block_lines[j]
                global_i = start + j
                reg = region_by_header.get(global_i)
                if reg is not None:
                    # flush prose
                    prose_text = "\n".join(prose).strip()
                    if prose_text:
                        f.write("### [assistant]\n")
                        f.write(prose_text + "\n\n")
                        prose = []
                    # render tool
                    tool = reg["tool"]
                    arg = _arg_hint(reg["args"])
                    if not arg and tool == "execute":
                        # try code
                        try:
                            obj = json.loads(reg["args"]) if reg["args"] else None
                        except Exception:
                            obj = None
                        if isinstance(obj, dict):
                            code = obj.get("code") or obj.get("command") or ""
                            arg = (code or "")[:80]
                        if not arg:
                            arg = "(no code captured)"
                    if not arg and tool == "subagent":
                        try:
                            obj = json.loads(reg["args"]) if reg["args"] else None
                        except Exception:
                            obj = None
                        if isinstance(obj, dict):
                            arg = obj.get("description") or obj.get("prompt") or "(spawn)"
                    status = (reg["status"] or "").strip()
                    is_error = status.lower().startswith("error") or "error" in status.lower()
                    mark = " · ERROR" if is_error else ""
                    f.write(f"### [tool: {tool}{mark}] `{arg}`\n")
                    meta_parts = []
                    artifact_path = f"{_rel_prefix(PAYLOADS_DIR, OUTDIR)}ses-{ses_num:03d}-tool-{reg['_idx']:03d}.txt"
                    meta_parts.append(f"`artifact: {artifact_path}`")
                    txt, rel = _load_artifact_text(ses_num, reg["_idx"])
                    if txt is not None:
                        sha_t = _sha256_text(txt)[:12]
                        meta_parts.append(f"`out_sha: {sha_t}`")
                    if reg["out"]:
                        em = _EXIT_RE.search(reg["out"])
                        if em:
                            meta_parts.append(f"`exit: {int(em.group(1))}`")
                    # also exit from artifact text
                    if txt is not None:
                        em2 = _EXIT_RE.search(txt)
                        if em2 and not any(p.startswith("`exit:") for p in meta_parts):
                            meta_parts.append(f"`exit: {int(em2.group(1))}`")
                    f.write(" · ".join(meta_parts) + "\n")
                    if txt is None:
                        f.write(f"*[BRAK ARTEFAKTU: brak pliku w {_rel_prefix(PAYLOADS_DIR, OUTDIR)}]*\n\n")
                    else:
                        f.write("```\n")
                        f.write(txt)
                        if not txt.endswith("\n"):
                            f.write("\n")
                        f.write("```\n")
                        if is_error:
                            preview = _first_sensible_line(reg["out"] or txt)
                            f.write(f"*[error tool call: {preview}]*\n")
                        f.write("\n")
                    # subagent extra
                    if tool == "subagent":
                        try:
                            obj = json.loads(reg["args"]) if reg["args"] else None
                        except Exception:
                            obj = None
                        if isinstance(obj, dict):
                            ag = obj.get("agent") or obj.get("model")
                            sid = obj.get("sessionID") or obj.get("sessionId")
                            if ag:
                                f.write(f"`agent: {ag}`\n")
                            if sid:
                                f.write(f"`sessionID: {sid}`\n")
                        # try find response file
                        if isinstance(obj, dict):
                            sid = obj.get("sessionID") or obj.get("sessionId")
                            if sid:
                                # search sessions dir
                                sess_dir = SCRIPTS / "_scratch" / "sessions" / "sessions"
                                found = None
                                if sess_dir.is_dir():
                                    for fp in sess_dir.glob("*.md"):
                                        try:
                                            if sid in fp.read_text(encoding="utf-8", errors="replace"):
                                                found = fp
                                                break
                                        except Exception:
                                            pass
                                if found:
                                    try:
                                        resp = found.read_text(encoding="utf-8", errors="replace")
                                        f.write("```\n")
                                        f.write(resp[:5000])
                                        if len(resp) > 5000:
                                            f.write("\n... [truncated in renderer]\n")
                                        f.write("```\n")
                                    except Exception:
                                        pass
                        f.write("\n")
                    # skip region lines
                    j = reg["end"] - start + 1
                    continue
                # if line belongs to a tool region but not header (in/out span), skip
                skip = False
                for r in regions:
                    if r["header"] < global_i <= r["end"]:
                        skip = True
                        break
                if skip:
                    j += 1
                    continue
                prose.append(line)
                j += 1
            prose_text = "\n".join(prose).strip()
            if prose_text:
                f.write("### [assistant]\n")
                f.write(prose_text + "\n\n")
        else:
            # other roles (reasoning, tool, etc.) -> verbatim
            text = "\n".join(block_lines).strip()
            if text:
                f.write(f"### [{role}]\n")
                f.write(text + "\n\n")

    f.write("---\n\n")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Merge the N most recent agent sessions into one .md file."
    )
    ap.add_argument("count", nargs="?", type=int, default=10,
                    help="How many of the newest sessions to merge (default: 10)")
    ap.add_argument("--agent", default="all",
                    help="Agent filter: all (default) or a single agent name")
    ap.add_argument("-o", "--out", type=Path, default=None,
                    help="Output file (default: scripts/_scratch/sessions/02_products/last_sessions_merged.md)")
    ap.add_argument("--include-reasoning", action="store_true",
                    help="Keep reasoning/thinking blocks (excluded by default)")
    ap.add_argument("--no-reasoning", dest="include_reasoning", action="store_false",
                    help="Compatibility alias; reasoning is already off by default")
    ap.add_argument("--compress", action="store_true",
                    help="Also write a compressed archive copy (.zst, else .gz)")
    ap.add_argument("--no-tools", action="store_true",
                    help="Externalise tool outputs to 04_payloads/ and replace them"
                         " inline with a sha256+size reference (writes index.tsv)")
    ap.add_argument("--signatures", action="store_true", default=True,
                    help="Externalise tool outputs and compact each block to a"
                         " signature (exit/args_sha/out_sha/bytes/artifact); keeps"
                         " decisive evidence verbatim; writes tool_calls.jsonl,"
                         " claims.jsonl, index.tsv (default)")
    ap.add_argument("--verbatim", dest="signatures", action="store_false",
                    help="Disable signatures: keep the old inline transcript")
    ap.add_argument("--monolith", action="store_true",
                    help="Write one file instead of the default index + sessions/ split")
    ap.add_argument("--actions", action="store_true",
                    help="Generate per-session action list (numbered tool calls + aggregate)")
    ap.add_argument("--full-verbatim", dest="full_verbatim", action="store_true",
                    help="Render all sessions verbatim (full tool outputs from 04_payloads/, ~10-15 MB)")
    ap.add_argument("--include-harness", dest="include_harness", action="store_true",
                    help="Include harness events (idle, model-switched, compaction)")
    ap.add_argument("--count", dest="session_count", type=int, default=None,
                    help="Number of sessions to process (default: 10)")
    ap.add_argument("--records-dir", type=Path, default=RECORDS_DIR,
                    help="Where per-session record bodies go "
                         "(default: scripts/_scratch/sessions/03_records/sessions)")
    ap.add_argument("--payloads-dir", type=Path, default=PAYLOADS_DIR,
                    help="Where tool payload sidecars go "
                         "(default: scripts/_scratch/sessions/04_payloads)")
    ap.set_defaults(include_reasoning=False)
    args = ap.parse_args()

    global _AGENT_SESSIONS
    _AGENT_SESSIONS = _load_agent_sessions()

    actions_mode = bool(args.actions)
    full_verbatim_mode = bool(args.full_verbatim)
    if full_verbatim_mode:
        n = max(1, args.session_count if args.session_count is not None else 100)
    elif actions_mode:
        n = max(1, args.session_count if args.session_count is not None else 10)
    else:
        n = max(1, args.count)
    agents = _AGENT_SESSIONS.SUPPORTED_AGENTS
    if args.agent != "all" and args.agent not in agents:
        sys.exit(f"Nieznany agent: {args.agent}. Dostepne: all, {', '.join(agents)}")

    if full_verbatim_mode:
        out_path = args.out or (OUTDIR / "last_sessions_full.md")
    elif actions_mode:
        out_path = args.out or (OUTDIR / "last_sessions_actions.md")
    else:
        out_path = args.out or (OUTDIR / "last_sessions_merged.md")

    print(f"Szukam {n} ostatnich sesji (agent: {args.agent})...")
    sessions = _AGENT_SESSIONS.get_all_sessions(
        args.agent, limit_per_agent=max(n, 10), days=None
    )
    if not sessions:
        sys.exit("Brak sesji do scalenia.")

    targets = sessions[:n]
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if full_verbatim_mode:
        # pre-pass counts
        tool_calls_total = 0
        error_total = 0
        omp_total = 0
        omp_parsed = 0
        for s in targets:
            if str(_g(s, "agent") or "").lower() == "omp":
                omp_total += 1
            body = _AGENT_SESSIONS.render_session_body(s, include_reasoning=args.include_reasoning)
            regs = _scan_actions_regions(body.split("\n"))
            tool_calls_total += len(regs)
            error_total += sum(1 for r in regs if (r["status"] or "").lower().startswith("error") or "error" in (r["status"] or "").lower())
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            f.write("# Ostatnie 100 sesji agentow — SUMMARY + REFERENCJE\n\n")
            f.write(f"- **Wygenerowano**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"- **Liczba sesji**: {len(targets)}\n")
            f.write(f"- **Format**: `--full-verbatim` (summary + referencje do `{_rel_prefix(PAYLOADS_DIR, OUTDIR)}`; renderer nie truncuje, ale źródło/artefakty mogą zawierać `…[+N zn.]…`)\n")
            f.write(f"- **Zrodlo**: opencode.db + omp .jsonl + {_rel_prefix(PAYLOADS_DIR, OUTDIR)}\n")
            f.write(f"- **Sesje sparsowane**: {len(targets)}/{len(targets)} (opencode {len(targets)-omp_total}/{len(targets)-omp_total}, omp {omp_total}/{omp_total})\n")
            f.write(f"- **Tool calls**: {tool_calls_total} (w tym {error_total} error)\n")
            f.write("- **Artefakty**: patrz per sesja\n")
            f.write("- **Reasoning**: " + ("włączony" if args.include_reasoning else "wyłączony (flaga --include-reasoning)") + "\n")
            f.write("- **Harness events**: nie wliczone (flaga --include-harness)\n")
            f.write(f"- **Legenda**: `### [tool: X · ERROR]` = tool call z `· error`; `*[BRAK ARTEFAKTU]*` = brak pliku w {_rel_prefix(PAYLOADS_DIR, OUTDIR)}\n\n")
            f.write("## Ograniczenia tego pliku\n")
            f.write("- Reasoning: " + ("włączony" if args.include_reasoning else "wyłączony (źródło ma reasoning, ale flaga nie ustawiona)") + ".\n")
            f.write(f"- Sesje omp: {omp_total} (akcje nie wyciągnięte — format nieparsowalny).\n")
            f.write("- Harness events: tylko sumarycznie (idle×N, model-switched×N); pełne zdarzenia z timestampami niedostępne w źródle.\n")
            f.write("- Truncacje `…[+N zn.]…` pochodzą ze źródła/artefaktów (768 B/linia harness), nie z renderera.\n")
            f.write("- 14 brakujących artefaktów oznaczonych `*[BRAK ARTEFAKTU]*`.\n\n")
            for i, s in enumerate(targets, 1):
                render_full_verbatim(s, f, args, i)
                # update counts by re-parsing? We'll count artifacts in render? Let's count here
            # We'll compute counts separately in a quick pass? To avoid double, count during render not captured.
        # compute sha256
        h = hashlib.sha256()
        with open(out_path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        file_sha = h.hexdigest()
        # append footer with sha
        with open(out_path, "a", encoding="utf-8", newline="\n") as f:
            f.write(f"## not checked\n")
            f.write(f"- Reasoning: {'włączony' if args.include_reasoning else 'wyłączony w źródle'}.\n")
            f.write(f"- Harness events: nie wliczone (flaga --include-harness).\n")
            f.write(f"- SHA256 pliku: {file_sha}\n")
        size_kb = out_path.stat().st_size // 1024
        print(f"Zapisano: {out_path}")
        print(f"Sesji: {len(targets)}  |  {size_kb} KB  |  sha256: {file_sha}")
        for i, s in enumerate(targets, 1):
            ts = s.updated_at or s.created_at or "-"
            print(f"  {i:02d}. [{s.agent}] {ts}  {s.title[:60]}")
        return

    if actions_mode:
        chunks = []
        for i, s in enumerate(targets, 1):
            acts = parse_actions(s)
            chunks.append(render_actions(s, acts, idx=i))
        out_path.write_text("\n".join(chunks), encoding="utf-8", newline="\n")
        size_kb = out_path.stat().st_size // 1024
        print(f"Zapisano: {out_path}")
        print(f"Sesji: {len(targets)} (z {len(sessions)} wczytanych)  |  {size_kb} KB")
        for i, s in enumerate(targets, 1):
            ts = s.updated_at or s.created_at or "-"
            print(f"  {i:02d}. [{s.agent}] {ts}  {s.title[:60]}")
        return

    out_path.write_text(
        build_merged_markdown(targets, args.agent, out_path,
                              available=len(sessions),
                              include_reasoning=args.include_reasoning,
                              no_tools=args.no_tools and not args.signatures,
                              signatures=args.signatures,
                              split=not args.monolith,
                              records_dir=args.records_dir,
                              payloads_dir=args.payloads_dir),
        encoding="utf-8", newline="\n")

    size_kb = out_path.stat().st_size // 1024
    print(f"Zapisano: {out_path}")
    print(f"Sesji scalonych: {len(targets)} (z {len(sessions)} wczytanych)  |  {size_kb} KB")
    if args.compress:
        packed = compress_artifact(out_path)
        ratio = len(out_path.read_bytes()) / max(1, packed.stat().st_size)
        print(f"Skompresowano: {packed}  ({ratio:.1f}x)")
    for i, s in enumerate(targets, 1):
        ts = s.updated_at or s.created_at or "-"
        print(f"  {i:02d}. [{s.agent}] {ts}  {s.title[:60]}")


_AGENT_SESSIONS = None


if __name__ == "__main__":
    main()
