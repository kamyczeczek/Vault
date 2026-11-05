#!/usr/bin/env python -X utf8
"""check_orchestration.py — commit-time enforcement of _factory/ORCHESTRATION.md (§9).

Checks, with the epoch boundaries each check uses (fail loud, never skip):
  C1  The ACTIVE plan section in PROCESS/03_plan/slices.md declares
      `sloppy: true`, `rev: N`, `terminal_slice:`, `terminal_trigger:`,
      and a valid repo-contained `artifact_root:`.
      (The active section = first `## Active` header containing `sloppy: true`;
      it ends at the next `## ` header.)
  C2  The most recent executor artifact (`results_*.json` by mtime under
      the active plan's repo-relative `artifact_root`) has a non-empty
      sibling `harness.log`. Unrelated tasks never select this artifact.
  C3  That artifact contains a non-empty `plan_impact` (§4: missing
      plan_impact = invalid artifact).
  C4  If that artifact carries `plan_rev`, the active plan's rev MUST be
      greater (plan advanced past the evidence it produced). Artifacts
      without `plan_rev` predate this field; noted, not failed.
  C5  Every OPEN slice in the active section declares `worker_cwd:` whose
      directory contains `.omp/extensions/` (G6: no knowledge-less
      delegation). Closed slices (heading carries DONE / REJECTED /
      ACCEPTED) are exempt — their execution already happened.
  C6  Frontier-First (§12.1): when any slice is OPEN, exactly one OPEN slice
      carries `frontier: true` (zero frontiers legal only with zero OPEN
      slices); that frontier carries `scenario·stage:`, `re_plan_signal:`, and
      a numeric Acceptance threshold; no non-frontier OPEN slice carries
      `#### F-` or a `frontier:` line.
  C7  Chunking (§12.2): a slice with `chunking_trigger:` != none must carry
      2–4 `#### F-*-C` chunk blocks, each with Goal/Touches/Acceptance/Budget/
      `worker_cwd:` (with `.omp/extensions/`) and `scenario·stage:`, plus a
      `merge:` line. Trigger `none` requires `chunking: none — <reason>`.
      Sub-blocks without any `chunking_trigger:` are a violation.
  C8  Chunk artifacts (§12.3/§9.8): every `results_*.json` recursively under
      the same active `artifact_root` carrying
      `chunk_id` has a boolean `needs_further_chunking` (non-empty
      `sub_chunk_proposal` when true); an artifact carrying `merged_from`
      must have `needs_further_chunking` equal to the OR of its children's
      flags (a missing/unreadable child path is itself a violation).
  C9  Green Zone (§12.5): a slice with chunk sub-blocks declares `green_zone:`;
      `parallel` needs a non-empty `auth:` ref and pairwise-disjoint chunk
      Touches, and no chunk Acceptance may name a sibling unless
      `serializes_after:` names it. Shared paths (or `green_zone: serial`)
      require a `serialized:` line naming the shared path and every chunk
      touching it to carry `serializes_after:`; those chains must be acyclic.

Exit 0 = compliant. Exit 1 lists every violation with its path. No skips.

Red-path fixtures (pack-probe scar: a check that cannot fail is not a check)
live under `.jcode/session-state/orch_fixtures/` (gitignored scratch):
These are retained historical plans, not current runtime provenance; their
original headers predate artifact_root and remain byte-preserved. Invoke with
`--plan <fixture> --artifacts-dir <fixture-evidence-dir>`. For C6/C7/C9 plan-only
defects use a temporary empty evidence directory; for C8 use live_active.md
with the corresponding bad_c8* evidence directory. The override explicitly
REPLACES the plan's artifact scope for C2–C4 and C8 (fixture use only).
Normal plans must name an existing repo-contained `artifact_root`; invalid
scope fails closed. The registered gate uses the live plan without overrides.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PLAN = REPO_ROOT / "PROCESS/03_plan/slices.md"

CLOSED_MARKERS = ("DONE", "REJECTED", "ACCEPTED")


def parse_active_section(text: str):
    """Return (header_block, slice_blocks) of the active plan section.

    Active section = first `## Active ...` line whose section body carries
    `sloppy: true`. Section ends at the next `## ` header line.
    slice_blocks = list of (heading_line, body_text) for `### ` slices.
    """
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.startswith("## Active"):
            # confirm sloppy: true appears within this section
            end = len(lines)
            for j in range(i + 1, len(lines)):
                if lines[j].startswith("## "):
                    end = j
                    break
            body = "\n".join(lines[i:end])
            if "sloppy: true" in body or "sloppy:true" in body:
                start = (i, end)
                break
    if start is None:
        return None, None
    i, end = start
    section = lines[i:end]
    first_slice = next((k for k, ln in enumerate(section) if ln.startswith("### ")),
                       len(section))
    header = "\n".join(section[:first_slice])
    slices = []
    k = first_slice
    while k < len(section):
        if section[k].startswith("### "):
            heading = section[k]
            j = k + 1
            while j < len(section) and not section[j].startswith("### "):
                j += 1
            slices.append((heading, "\n".join(section[k + 1:j])))
            k = j
        else:
            k += 1
    return header, slices


def slice_name(heading: str) -> str:
    """`### S5-CHK — Foo — OPEN` -> `S5-CHK`; `#### F-S5-CHK-C1 — Bar` -> `F-S5-CHK-C1`."""
    return heading.lstrip("# ").strip().split(" — ")[0].strip()


def is_closed(heading: str) -> bool:
    return any(marker in heading.upper() for marker in CLOSED_MARKERS)


def field_value(body: str, name: str):
    """Value after `**Name:**` / `Name:` (bold form first). None when absent.

    The bold pattern allows one parenthesized qualifier before the colon
    (`**Acceptance (numeric):**`) but requires `:**` to follow the name, so
    `chunking` never matches the `chunking_trigger:` line.
    """
    bold = rf"^[ \t]*[-*]?[ \t]*\*\*{re.escape(name)}(?:[ \t]*\([^)]*\))?:\*\*[ \t]*(.*)$"
    plain = rf"^[ \t]*[-*]?[ \t]*{re.escape(name)}[ \t]*:[ \t]*(.*)$"
    for pat in (bold, plain):
        m = re.search(pat, body, re.M)
        if m:
            return m.group(1).strip()
    return None


def iter_sub_blocks(body: str):
    """Yield (heading_line, block_body) for every `#### ` sub-block."""
    lines = body.splitlines()
    blocks = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("#### "):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("#### "):
                j += 1
            blocks.append((lines[i], "\n".join(lines[i + 1:j])))
            i = j
        else:
            i += 1
    return blocks


def chunk_blocks(body: str):
    """Sub-blocks whose heading matches the §12.2 `#### F-*-C*` chunk shape."""
    return [(h, b) for h, b in iter_sub_blocks(body) if re.match(r"####\s+F-", h)]


PATH_TOKEN = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_./\\-]*[/\\][A-Za-z0-9_./\\-]*")


def norm_path(token: str) -> str:
    return token.strip().strip("`.,;:()").replace("\\", "/").rstrip("/").lower()


def extract_paths(text: str):
    """Path-like tokens from a Touches line (backticked or bare), normalized."""
    out = set()
    for m in re.finditer(r"`([^`]+)`", text or ""):
        for tok in PATH_TOKEN.findall(m.group(1)):
            out.add(norm_path(tok))
    for tok in PATH_TOKEN.findall(text or ""):
        out.add(norm_path(tok))
    return out


def find_cycle(graph: dict):
    """Return a cycle (list of nodes, first repeated) or None. DFS colours."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in graph}
    stack: list = []

    def dfs(n):
        color[n] = GRAY
        stack.append(n)
        for m in graph.get(n, ()):
            if color.get(m) == GRAY:
                return stack[stack.index(m):] + [m]
            if color.get(m) == WHITE:
                r = dfs(m)
                if r:
                    return r
        stack.pop()
        color[n] = BLACK
        return None

    for n in list(graph):
        if color[n] == WHITE:
            r = dfs(n)
            if r:
                return r
    return None


def resolve_worker_cwd(raw: str):
    token = raw.strip().strip("`").split()[0]
    return (REPO_ROOT / token).resolve()


def parse_args(argv=None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="ORCHESTRATION.md §9 enforcement gate")
    ap.add_argument("--plan", default=str(DEFAULT_PLAN),
                    help="plan file to check (default PROCESS/03_plan/slices.md)")
    ap.add_argument("--artifacts-dir", default=None,
                    help="replace the plan artifact_root for C2–C4/C8 (test fixtures)")
    return ap.parse_args(argv)


def collect_artifacts(header, override):
    """Resolve one explicit evidence scope; never infer ownership from global mtime."""
    if override is not None:
        root = Path(override)
        if not root.is_absolute():
            root = REPO_ROOT / root
        root = root.resolve()
    else:
        value = field_value(header, "artifact_root")
        if not value:
            raise ValueError("C1 active plan header missing `artifact_root`")
        path = Path(value.strip().strip("`"))
        if path.is_absolute() or path.drive or path.root:
            raise ValueError("C1 artifact_root must be repo-relative")
        root = (REPO_ROOT / path).resolve()
        if not root.is_relative_to(REPO_ROOT.resolve()):
            raise ValueError("C1 artifact_root resolves outside the repository")
    if not root.is_dir():
        raise ValueError(f"C1 artifact_root is not an existing directory: {root}")
    artifacts = sorted(root.rglob("results_*.json"))
    for artifact in artifacts:
        if not artifact.resolve().is_relative_to(root):
            raise ValueError(f"C1 artifact_root contains escaped artifact: {artifact}")
    return root, artifacts


def check_c6(slices, violations):
    """Frontier-First (§12.1): exactly one OPEN frontier when any slice is OPEN."""
    open_slices = [(h, b) for h, b in slices if not is_closed(h)]
    frontiers = [(h, b) for h, b in open_slices if field_value(b, "frontier") == "true"]
    if open_slices:
        if len(frontiers) != 1:
            violations.append(
                f"C6 expected exactly 1 OPEN frontier slice (`frontier: true`), found {len(frontiers)}")
        for h, b in frontiers:
            name = slice_name(h)
            if field_value(b, "scenario·stage") is None:
                violations.append(f"C6 frontier {name} missing `scenario·stage:`")
            if field_value(b, "re_plan_signal") is None:
                violations.append(f"C6 frontier {name} missing `re_plan_signal:`")
            acc = field_value(b, "Acceptance")
            if not acc or not re.search(r"\d", acc):
                violations.append(f"C6 frontier {name} Acceptance carries no numeric threshold")
    elif frontiers:
        violations.append("C6 zero OPEN slices but a frontier is declared")
    frontier_heads = {h for h, _ in frontiers}
    for h, b in open_slices:
        if h in frontier_heads:
            continue
        if re.search(r"####\s+F-", b) or re.search(r"frontier\s*:", b):
            violations.append(
                f"C6 non-frontier OPEN slice {slice_name(h)} carries `#### F-` / `frontier:` (§12.1)")


def check_c7(slices, violations):
    """Frontier chunking (§12.2): trigger ≠ none needs 2–4 chunk blocks + merge."""
    for h, b in slices:
        if is_closed(h):
            continue
        name = slice_name(h)
        trigger = field_value(b, "chunking_trigger")
        subs = iter_sub_blocks(b)
        chunks = chunk_blocks(b)
        if trigger is None:
            if subs:
                violations.append(f"C7 slice {name} has chunk sub-blocks but no `chunking_trigger:`")
            continue
        value = trigger.split()[0].strip("`*") if trigger.split() else ""
        if value == "none":
            reason = field_value(b, "chunking")
            if not reason or not re.match(r"none\s*[—–\-:]\s*\S+", reason):
                violations.append(
                    f"C7 slice {name} chunking_trigger is none but no `chunking: none — <reason>` line")
            continue
        if not 2 <= len(chunks) <= 4:
            violations.append(
                f"C7 slice {name} chunking_trigger `{value}` requires 2-4 `#### F-*-C` chunk blocks, "
                f"found {len(chunks)}")
        for ch, cb in chunks:
            cname = slice_name(ch)
            for fld in ("Goal", "Touches", "Acceptance", "Budget"):
                if field_value(cb, fld) is None:
                    violations.append(f"C7 chunk {cname} missing `{fld}:`")
            if field_value(cb, "scenario·stage") is None:
                violations.append(f"C7 chunk {cname} missing `scenario·stage:`")
            wc = field_value(cb, "worker_cwd")
            if not wc:
                violations.append(f"C7 chunk {cname} missing `worker_cwd:`")
            elif not (resolve_worker_cwd(wc) / ".omp/extensions").is_dir():
                violations.append(f"C7 chunk {cname} worker_cwd {wc} lacks .omp/extensions/ (G6)")
        if field_value(b, "merge") is None:
            violations.append(f"C7 slice {name} is chunked but declares no `merge:` line (§12.2)")


def check_c8(artifacts, artifact_root, violations):
    """Chunk artifacts (§12.3/§9.8): needs_further_chunking + merged_from OR-rollup."""
    cache = {}

    def load(p):
        if p not in cache:
            try:
                cache[p] = json.loads(p.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as e:
                cache[p] = e
        return cache[p]

    def rel(p):
        try:
            return p.relative_to(REPO_ROOT)
        except ValueError:
            return p

    for art in artifacts:
        data = load(art)
        if isinstance(data, Exception):
            violations.append(f"C8 artifact {rel(art)} unreadable/malformed: {data}")
            continue
        if not isinstance(data, dict):
            continue
        if "chunk_id" in data:
            nfc = data.get("needs_further_chunking")
            if not isinstance(nfc, bool):
                violations.append(
                    f"C8 {rel(art)} has chunk_id {data.get('chunk_id')!r} but no boolean "
                    f"`needs_further_chunking` (§12.3)")
            elif nfc:
                prop = data.get("sub_chunk_proposal")
                if not isinstance(prop, list) or not prop:
                    violations.append(
                        f"C8 {rel(art)} needs_further_chunking=true with empty `sub_chunk_proposal` (§12.3)")
        if "merged_from" in data:
            mf = data.get("merged_from")
            if not isinstance(mf, list) or not mf:
                violations.append(f"C8 {rel(art)} `merged_from` is not a non-empty list")
                continue
            child_flags = []
            for item in mf:
                cand = Path(item)
                child = None
                for base in ((REPO_ROOT,), (art.parent,)):
                    c = (base[0] / cand) if not cand.is_absolute() else cand
                    if c.is_file() and c.resolve().is_relative_to(artifact_root):
                        child = c
                        break
                if child is None:
                    violations.append(f"C8 {rel(art)} merged_from path `{item}` missing/unreadable or outside artifact_root")
                    continue
                cd = load(child)
                if isinstance(cd, Exception):
                    violations.append(f"C8 {rel(art)} merged_from path `{item}` unreadable: {cd}")
                    continue
                cf = cd.get("needs_further_chunking") if isinstance(cd, dict) else None
                if not isinstance(cf, bool):
                    violations.append(
                        f"C8 merged_from child `{item}` lacks boolean `needs_further_chunking`")
                    continue
                child_flags.append(cf)
            if child_flags:
                expected = any(child_flags)
                actual = data.get("needs_further_chunking")
                if not isinstance(actual, bool) or actual != expected:
                    violations.append(
                        f"C8 {rel(art)} needs_further_chunking {actual!r} != OR of merged_from ({expected})")


def check_c9(slices, violations):
    """Green Zone (§12.5): parallel needs disjoint Touches + auth; shared → serialized chain."""
    for h, b in slices:
        if is_closed(h):
            continue
        subs = iter_sub_blocks(b)
        if not subs:
            continue
        name = slice_name(h)
        gz = field_value(b, "green_zone")
        if gz is None:
            violations.append(f"C9 slice {name} has chunk sub-blocks but no `green_zone:` line (§12.5)")
            continue
        parallel = "parallel" in gz
        touches, accs, sers = {}, {}, {}
        for ch, cb in subs:
            cname = slice_name(ch)
            touches[cname] = extract_paths(field_value(cb, "Touches") or "")
            accs[cname] = field_value(cb, "Acceptance") or ""
            sers[cname] = field_value(cb, "serializes_after") or "none"
        names = list(touches)
        shared = {}
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                for p in touches[names[i]] & touches[names[j]]:
                    shared.setdefault(p, set()).update({names[i], names[j]})
        if parallel:
            m_auth = re.search(r"auth\s*:\s*([^)]*)", gz)
            if not m_auth or not m_auth.group(1).strip():
                violations.append(f"C9 slice {name} green_zone parallel without non-empty `auth:` ref")
            for p, who in sorted(shared.items()):
                violations.append(
                    f"C9 slice {name} green_zone parallel but path `{p}` is touched by "
                    f"{sorted(who)} — not pairwise-disjoint")
            for cname, acc in accs.items():
                for other in names:
                    if other == cname:
                        continue
                    if other in acc and other not in sers[cname]:
                        violations.append(
                            f"C9 chunk {cname} Acceptance references sibling {other} without "
                            f"`serializes_after:`")
        if shared or not parallel:
            ser_line = field_value(b, "serialized")
            if not ser_line:
                violations.append(f"C9 slice {name} has shared/serial chunks but no `serialized:` line")
            else:
                for p, who in sorted(shared.items()):
                    if p not in ser_line.lower():
                        violations.append(f"C9 `serialized:` line does not name shared path `{p}`")
                    for cname in sorted(who):
                        if sers.get(cname, "none").strip().lower() == "none":
                            violations.append(
                                f"C9 chunk {cname} touches shared path `{p}` but carries no "
                                f"`serializes_after:`")
        graph = {}
        for cname, ser in sers.items():
            deps = [t for t in re.split(r"[,\s]+", ser) if t and t.lower() != "none"]
            graph[cname] = [d for d in deps if d in sers]
        cycle = find_cycle(graph)
        if cycle:
            violations.append(f"C9 `serializes_after:` cycle: {' -> '.join(cycle)}")


def main(argv=None) -> int:
    args = parse_args(argv)
    plan_path = Path(args.plan)
    if not plan_path.is_absolute():
        plan_path = REPO_ROOT / plan_path
    if not plan_path.is_file():
        print(f"[check_orchestration] FAIL: plan {plan_path} missing")
        return 1
    text = plan_path.read_text(encoding="utf-8")
    header, slices = parse_active_section(text)
    if header is None:
        print("[check_orchestration] FAIL: no active section with `sloppy: true` in slices.md")
        return 1

    violations = []

    # --- C1: header fields ----------------------------------------------------
    m_rev = re.search(r"rev:\s*(\d+)", header)
    if not m_rev:
        violations.append("C1 active plan header missing `rev: N`")
    for field in ("terminal_slice", "terminal_trigger"):
        if not re.search(rf"{field}\s*:", header):
            violations.append(f"C1 active plan header missing `{field}:`")
    # --- C5: open slices need a valid worker_cwd ------------------------------
    for heading, body in slices:
        closed = any(marker in heading.upper() for marker in CLOSED_MARKERS)
        m_cwd = re.search(r"worker_cwd:\s*\**\s*`?([^\s`]+)`?", body)
        if closed:
            continue
        if not m_cwd:
            violations.append(f"C5 open slice {heading.strip('# ').split(' — ')[0]} declares no worker_cwd (G6)")
            continue
        cwd = REPO_ROOT / m_cwd.group(1).strip()
        if not (cwd / ".omp/extensions").is_dir():
            violations.append(
                f"C5 slice {heading.strip('# ').split(' — ')[0]} worker_cwd {m_cwd.group(1)} "
                f"lacks .omp/extensions/ (G6: knowledge-less delegation)")

    plan_rev = int(m_rev.group(1)) if m_rev else None

    # --- C6/C7/C9: frontier, chunking, green zone (§12) -----------------------
    check_c6(slices, violations)
    check_c7(slices, violations)
    check_c9(slices, violations)
    # --- C2/C3/C4/C8 share the active plan's evidence boundary -----------------
    try:
        artifact_root, artifacts = collect_artifacts(header, args.artifacts_dir)
    except (ValueError, OSError, RuntimeError) as e:
        violations.append(f"artifact_root: {e}")
        artifacts = []
    else:
        check_c8(artifacts, artifact_root, violations)
    artifacts.sort(key=lambda p: (p.stat().st_mtime_ns, p.as_posix()))
    if artifacts:
        art = artifacts[-1]
        harness = art.parent / "harness.log"
        if not harness.is_file() or harness.stat().st_size == 0:
            violations.append(f"C2 most recent executor artifact {art} "
                              f"has no non-empty sibling harness.log (G4: untrusted)")
        try:
            data = json.loads(art.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            violations.append(f"C3 most recent artifact {art} unreadable/malformed: {e}")
            data = None
        if data is not None and not isinstance(data, dict):
            violations.append(f"C3 most recent artifact {art} must be an object")
        if isinstance(data, dict):
            if not data.get("plan_impact"):
                violations.append(f"C3 most recent artifact {art} "
                                  f"missing non-empty plan_impact (§4)")
            artifact_rev = data.get("plan_rev")
            if artifact_rev is not None and plan_rev is not None:
                if not isinstance(artifact_rev, int) or isinstance(artifact_rev, bool):
                    violations.append(f"C4 artifact {art} plan_rev must be an integer")
                elif plan_rev <= artifact_rev:
                    violations.append(
                        f"C4 plan rev {plan_rev} not greater than artifact plan_rev {artifact_rev}")
    else:
        if not violations:
            print("[check_orchestration] note: no executor artifacts in declared scope (pre-execution)")

    if violations:
        for v in violations:
            print(f"[check_orchestration] FAIL: {v}")
        return 1
    print(f"[check_orchestration] OK — active plan rev {plan_rev}, "
          f"{len(slices)} slice(s), latest artifact compliant")
    return 0


if __name__ == "__main__":
    sys.exit(main())
