#!/usr/bin/env python
"""Post-processor: last_sessions_full.md -> last_sessions_full_v2.md with
artifact pointers, git snapshots, claim verdicts and computed counts."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_DEFAULT = ROOT / "scripts" / "_scratch" / "sessions" / "last_sessions_full.md"
OUT_DEFAULT = ROOT / "scripts" / "_scratch" / "sessions" / "last_sessions_full_v2.md"
ARTIFACTS = ROOT / "scripts" / "_scratch" / "sessions" / "artifacts"

GIT_HEAD = "unknown"
GIT_STATUS = ""
GIT_DIFF_STAT = ""


def git_info():
    global GIT_HEAD, GIT_STATUS, GIT_DIFF_STAT
    try:
        GIT_HEAD = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        GIT_HEAD = "unknown"
    try:
        GIT_STATUS = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        GIT_STATUS = "unknown"
    try:
        GIT_DIFF_STAT = subprocess.check_output(
            ["git", "diff", "--stat", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip().splitlines()[-1] if subprocess.check_output(
            ["git", "diff", "--stat", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip() else ""
    except Exception:
        GIT_DIFF_STAT = "unknown"


def run_verify(report_path: Path) -> str:
    # delegate to verify_session_claims.py if available
    vp = ROOT / "scripts" / "verify_session_claims.py"
    if not vp.is_file():
        return ""
    try:
        out = subprocess.check_output(
            ["python", str(vp), "--report", str(report_path)],
            cwd=ROOT, text=True, stderr=subprocess.STDOUT, timeout=300,
        )
        return out
    except Exception as e:
        return str(e)


def transform(text: str) -> str:
    lines = text.split("\n")
    out: list[str] = []
    # computed counts
    sessions = sum(1 for l in lines if re.match(r"^## Sesja \d+ —", l))
    tool_calls = sum(1 for l in lines if l.startswith("### [tool:"))
    error_calls = sum(1 for l in lines if "· ERROR" in l)
    missing_art = sum(1 for l in lines if "[BRAK ARTEFAKTU" in l)
    omp = sum(1 for l in lines if "format omp" in l)
    truncs = sum(1 for l in lines if "…" in l and "[+ " in l.replace("…", ""))  # rough

    # rewrite top header counts in place: replace first 12 lines? Instead prepend new header block.
    # We'll keep original header but append computed summary after title.
    # Simple: insert computed metrics right after title line.
    new_lines: list[str] = []
    header_done = False
    i = 0
    n = len(lines)
    while i < n:
        new_lines.append(lines[i])
        if lines[i].startswith("# Ostatnie 100 sesji agentow"):
            new_lines.append("")
            new_lines.append("## Metryki wyliczone (upgrade v2)")
            new_lines.append(f"- Sesje: {sessions}")
            new_lines.append(f"- Tool calls: {tool_calls} (w tym {error_calls} error)")
            new_lines.append(f"- Artefakty brakujące: {missing_art}")
            new_lines.append(f"- omp (nieparsowalne): {omp}")
            new_lines.append(f"- git_head_end: {GIT_HEAD}")
            new_lines.append(f"- git_status_porcelain_end: {GIT_STATUS!r}")
            new_lines.append(f"- git_diff_stat_end: {GIT_DIFF_STAT}")
            new_lines.append("")
            header_done = True
        i += 1
    lines = new_lines

    # Now process tool sections: add git snapshot after per-session artifact line,
    # and collapse large code blocks to head/tail + pointer.
    out = []
    in_tool = False
    in_code = False
    code_buf: list[str] = []
    code_fence_lang = ""
    current_artifact = ""
    for line in lines:
        if line.startswith("### [tool:"):
            in_tool = True
            out.append(line)
            continue
        if line.startswith("### [") or line.startswith("## Sesja") or line.startswith("---"):
            # flush code buffer if any
            if in_code and code_buf:
                flush_code(out, code_buf, current_artifact, in_tool)
                code_buf = []
                in_code = False
            in_tool = False
            out.append(line)
            continue
        if line.startswith("```"):
            if not in_code:
                in_code = True
                code_buf = []
                out.append(line)
            else:
                # closing fence
                in_code = False
                flush_code(out, code_buf, current_artifact, in_tool)
                code_buf = []
                out.append("```")
            continue
        if in_code:
            code_buf.append(line)
            continue
        # track artifact path
        m = re.search(r"artifact: (artifacts/\S+\.txt)", line)
        if m:
            current_artifact = m.group(1)
        # add git snapshot after Artefakty line in session header
        if line.startswith("- **Artefakty**:") and not line.startswith("- **Artefakty**: format"):
            out.append(line)
            out.append(f"- **git_head_start**: unknown")
            out.append(f"- **git_head_end**: {GIT_HEAD}")
            out.append(f"- **git_status_porcelain_end**: {GIT_STATUS!r}")
            out.append(f"- **git_diff_stat_end**: {GIT_DIFF_STAT}")
            continue
        out.append(line)

    if in_code and code_buf:
        flush_code(out, code_buf, current_artifact, in_tool)

    result = "\n".join(out)

    # Append claim verifier output: run external script and append summary
    vp = ROOT / "scripts" / "verify_session_claims.py"
    if vp.is_file():
        try:
            vout = subprocess.check_output(
                ["python", str(vp), "--report", "stdin"],
                cwd=ROOT, text=True, stderr=subprocess.STDOUT, input=result, timeout=300,
            )
            result += "\n\n## Claim verifier (auto)\n\n```\n" + vout.strip() + "\n```\n"
        except Exception as e:
            result += f"\n\n## Claim verifier (auto)\n\nERROR: {e}\n"

    return result


def flush_code(out, buf, artifact, in_tool):
    text = "\n".join(buf)
    has_trunc = any("…[+" in ln for ln in buf)
    if (not in_tool) or (len(text) <= 8192 and len(buf) <= 200 and not has_trunc):
        out.extend(buf)
        return
    # collapse
    head = buf[:3]
    tail = buf[-3:]
    out.extend(head)
    out.append(f"... (full output in {artifact}) ...")
    out.extend(tail)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT)
    ap.add_argument("--src", type=Path, default=SRC_DEFAULT)
    args = ap.parse_args()
    git_info()
    src_text = args.src.read_text(encoding="utf-8")
    new_text = transform(src_text)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(new_text, encoding="utf-8", newline="\n")
    print(f"Wrote {args.out} ({args.out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
