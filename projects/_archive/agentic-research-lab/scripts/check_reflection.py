#!/usr/bin/env python3
"""check_reflection.py — W4/W7 closure gate.

Asserts:
- every cited chunk id in reflection/digests/*.md resolves via graph.db
- every digest has a paired reflection/candidates/*.jsonl
- candidate rows use the canonical claim/evidence schema, with valid state
  and grounded evidence ids
"""
import json, re, sqlite3, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DIGESTS = ROOT / "reflection" / "digests"
CANDIDATES = ROOT / "reflection" / "candidates"
SCRATCH_DIGESTS = ROOT / "reflection" / "scratch" / "digests"
SCRATCH_CANDIDATES = ROOT / "reflection" / "scratch" / "candidates"
DB = ROOT / "knowledge" / "graph" / "graph.db"
WORKFLOW = ROOT / "pipeline" / "WORKFLOW.md"
TRACE_FILE = ROOT / "reflection" / "trace" / "events.jsonl"
PROV_FP = re.compile(r"\bfingerprint(?:\s*[:=]\s*|\s+)(?:[`\"']?)([0-9a-f]{8,12})(?:[`\"']?)")
PROV_PLAN = re.compile(r"\bplan_version(?:\s*[:=]\s*|\s+)(?:[`\"']?)([0-9a-f]{12})(?:[`\"']?)")

try:
    from audit_candidate import audit_claim_grounding  # type: ignore
except Exception:
    audit_claim_grounding = None  # optional sub-gate; warn if missing



def provenance_ok_jsonl(text: str, live_fp: str, plan_ver: str) -> tuple[bool, str]:
    """Candidate rows are JSON: read the nested `provenance` object rather than the
    first `fingerprint` token in raw text, which is often a quoted hash inside claim
    prose ("fingerprint 35b86bc954fa in its Determinism clause") and would always
    mismatch the live corpus."""
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            return False, "not valid JSON"
        prov = obj.get("provenance") or {}
        fp, pv, ph = prov.get("fingerprint"), prov.get("plan_version"), prov.get("phase")
        if not fp:
            return False, "missing provenance.fingerprint"
        if fp != live_fp:
            return False, f"fingerprint {fp} != live corpus {live_fp} (stale output)"
        if not pv:
            return False, "missing provenance.plan_version"
        if pv != plan_ver:
            return False, f"plan_version {pv} != current WORKFLOW.md {plan_ver}"
        if not ph:
            return False, "missing provenance.phase"
    return True, ""


def trace_provenance_errors(obj: dict, location: str) -> list[str]:
    errors: list[str] = []
    prov = obj.get("provenance") or {}
    event_ids = prov.get("retrieval_event_ids", [])
    if not event_ids:
        return errors
    if not TRACE_FILE.exists():
        return [f"{location}: trace file missing for retrieval_event_ids"]
    events = {}
    for line in TRACE_FILE.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        events[event.get("event_id")] = event
    run_id = prov.get("run_id")
    for event_id in event_ids:
        event = events.get(event_id)
        if not event:
            errors.append(f"{location}: unknown retrieval event `{event_id}`")
        elif event.get("kind") != "retrieval":
            errors.append(f"{location}: event `{event_id}` is not retrieval")
        elif run_id and event.get("run_id") != run_id:
            errors.append(f"{location}: retrieval event `{event_id}` belongs to another run")
    return errors


PROV_PHASE = re.compile(r"\bphase(?:\s*[:=]\s*|\s+)(?:[`\"']?)([A-Za-z0-9_-]+)(?:[`\"']?)")
REFLECTION_PHASE = "04_reflect"
ID_RE = re.compile(r"`([0-9]{2}_[a-z0-9_]+)`")
ROUTE_KEYS = {"tags", "limit", "anchor_id", "returned_ids", "expansion_traces"}
TRACE_KEYS = {"source_id", "target_id", "edge", "tag"}
ROUTE_FIELD_RE = re.compile(r"^\s*(?:-\s+)?([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$")
TRACE_START_RE = re.compile(r"^\s*-\s+([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$")
ROUTE_ITEM_RE = re.compile(r"^\s*-\s+(.*)$")
_MISSING = object()


def _markdown_scalar(raw: str, location: str, errors: list[str]) -> str:
    """Decode the scalar subset used by digest route metadata."""
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "`\"'":
        value = value[1:-1].strip()
    elif value[:1] in {"\"", "'"}:
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            decoded = value
        if isinstance(decoded, str):
            value = decoded
    if not value:
        errors.append(f"{location}: empty route value")
    return value


def _markdown_tags(raw: str, location: str, errors: list[str]) -> list[str]:
    value = _markdown_scalar(raw, location, errors)
    if not (value.startswith("[") and value.endswith("]")):
        errors.append(f"{location}: tags must be a bracketed list")
        return []
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        inner = value[1:-1].strip()
        parsed = [_markdown_scalar(part, location, errors).strip()
                  for part in inner.split(",")] if inner else []
    if not isinstance(parsed, list):
        errors.append(f"{location}: tags must be a list")
        return []
    tags: list[str] = []
    for item in parsed:
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{location}: tags must contain non-empty strings")
            continue
        tags.append(item.strip())
    if not tags:
        errors.append(f"{location}: tags must contain at least one tag")
    return tags


def parse_digest_route(text: str, name: str) -> tuple[dict | None, list[str], bool]:
    """Parse the markdown ``# Route metadata`` block without a YAML dependency."""
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines)
                  if re.fullmatch(r"#\s+Route metadata\s*", line.strip())), None)
    if start is None:
        return None, [], False
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if re.match(r"^#{1,6}\s+", lines[i]):
            end = i
            break
    section = [(i + 1, line) for i, line in enumerate(lines[start + 1:end], start + 1)]
    route: dict = {}
    seen: set[str] = set()
    errors: list[str] = []
    pos = 0

    while pos < len(section):
        lineno, line = section[pos]
        if not line.strip():
            pos += 1
            continue
        match = ROUTE_FIELD_RE.match(line)
        if not match:
            errors.append(f"{name}:{lineno}: malformed route metadata line")
            pos += 1
            continue
        key, raw = match.group(1), match.group(2)
        if key in seen:
            errors.append(f"{name}:{lineno}: duplicate route field `{key}`")
        seen.add(key)
        location = f"{name}:{lineno}"
        if key not in ROUTE_KEYS:
            errors.append(f"{location}: unknown route field `{key}`")
            pos += 1
            continue

        if key == "tags":
            route[key] = _markdown_tags(raw, location, errors)
            pos += 1
        elif key == "limit":
            value = _markdown_scalar(raw, location, errors)
            try:
                route[key] = int(value)
            except (TypeError, ValueError):
                errors.append(f"{location}: limit must be an integer")
                route[key] = None
            pos += 1
        elif key == "anchor_id":
            route[key] = _markdown_scalar(raw, location, errors)
            pos += 1
        elif key == "returned_ids":
            pos += 1
            values: list[str] = []
            while pos < len(section):
                item_lineno, item_line = section[pos]
                if not item_line.strip():
                    pos += 1
                    continue
                if ROUTE_FIELD_RE.match(item_line):
                    break
                item_match = ROUTE_ITEM_RE.match(item_line)
                if not item_match:
                    errors.append(f"{name}:{item_lineno}: returned_ids entries must be list items")
                    pos += 1
                    continue
                values.append(_markdown_scalar(item_match.group(1),
                                               f"{name}:{item_lineno}", errors))
                pos += 1
            route[key] = values
        else:  # expansion_traces
            pos += 1
            traces: list[dict] = []
            while pos < len(section):
                trace_lineno, trace_line = section[pos]
                if not trace_line.strip():
                    pos += 1
                    continue
                trace_match = TRACE_START_RE.match(trace_line)
                if not trace_match:
                    errors.append(f"{name}:{trace_lineno}: malformed expansion trace")
                    pos += 1
                    continue
                first_key = trace_match.group(1)
                if first_key not in TRACE_KEYS:
                    break
                trace: dict = {}
                trace_seen: set[str] = set()
                trace[first_key] = _markdown_scalar(
                    trace_match.group(2), f"{name}:{trace_lineno}", errors)
                trace_seen.add(first_key)
                pos += 1
                while pos < len(section):
                    field_lineno, field_line = section[pos]
                    if TRACE_START_RE.match(field_line):
                        break
                    if not field_line.strip():
                        pos += 1
                        continue
                    field_match = ROUTE_FIELD_RE.match(field_line)
                    if not field_match:
                        errors.append(f"{name}:{field_lineno}: malformed expansion trace field")
                        pos += 1
                        continue
                    field_key, field_raw = field_match.group(1), field_match.group(2)
                    if field_key not in TRACE_KEYS:
                        break
                    if field_key in trace_seen:
                        errors.append(f"{name}:{field_lineno}: duplicate trace field `{field_key}`")
                    trace_seen.add(field_key)
                    trace[field_key] = _markdown_scalar(
                        field_raw, f"{name}:{field_lineno}", errors)
                    pos += 1
                traces.append(trace)
            route[key] = traces

    for key in sorted(ROUTE_KEYS - seen):
        errors.append(f"{name}: missing route field `{key}`")
    return route, errors, True


def load_route_tags() -> set[str]:
    """Mirror route.py's topic vocabulary lookup."""
    topics = ROOT / "knowledge" / "topics.md"
    if not topics.exists():
        return set()
    tags: set[str] = set()
    for line in topics.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if s.startswith("- ") and len(s) > 2:
            tags.add(s[2:].strip())
    return tags


def load_graph_edges() -> set[tuple[str, str, str, str]]:
    if not DB.exists():
        return set()
    c = sqlite3.connect(DB)
    rows = c.execute("SELECT src, dst, kind, tag FROM edges").fetchall()
    c.close()
    return {(src, dst, kind, tag) for src, dst, kind, tag in rows}


def common_tag_threshold() -> set[str]:
    """Return tags that are too common to be discriminative (>50% of nodes).
    These tags are intentionally excluded from SHARES_TAG edge generation to
    prevent near-complete graph expansion, so expansion traces using them are
    allowed to reference missing edges."""
    if not DB.exists():
        return set()
    c = sqlite3.connect(DB)
    total = c.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    rows = c.execute("""
        SELECT json_each.value FROM nodes, json_each(nodes.tags)
        GROUP BY json_each.value HAVING COUNT(*) > ?
    """, (total * 0.5,)).fetchall()
    c.close()
    return {r[0] for r in rows}


def query_route_ids(tags: list[str], limit: int) -> list[str]:
    """Use the exact tag-intersection/order/limit semantics as pipeline route.py."""
    c = sqlite3.connect(DB)
    where = " AND ".join(["tags LIKE ?" for _ in tags]) if tags else "1"
    params = [f'%"{tag}"%' for tag in tags] if tags else []
    rows = c.execute(f"SELECT id FROM nodes WHERE {where} ORDER BY id LIMIT ?",
                     (*params, limit)).fetchall()
    c.close()
    return [row[0] for row in rows]


def validate_route(route, ids: set[str], valid_tags: set[str],
                   edges: set[tuple[str, str, str, str]],
                   context: str, common_tags: set[str] | None = None) -> tuple[list[str], set[str]]:
    """Validate route metadata and return its connected expansion targets."""
    errors: list[str] = []
    if not isinstance(route, dict):
        return [f"{context}: route metadata must be an object"], set()

    for key in sorted(set(route) - ROUTE_KEYS):
        errors.append(f"{context}: unknown route field `{key}`")
    for key in sorted(ROUTE_KEYS - set(route)):
        errors.append(f"{context}: missing route field `{key}`")

    tags = route.get("tags")
    if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
        errors.append(f"{context}: route tags must be a list of strings")
        tags = []
    elif not tags:
        errors.append(f"{context}: route tags must contain at least one tag")
    elif len(tags) != len(set(tags)):
        errors.append(f"{context}: route tags must be unique")
    for tag in tags:
        if tag not in valid_tags:
            errors.append(f"{context}: route tag `{tag}` is not in knowledge/topics.md")
    limit = route.get("limit")
    if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
        errors.append(f"{context}: route limit must be a positive integer")

    returned = route.get("returned_ids")
    if not isinstance(returned, list) or any(not isinstance(cid, str) for cid in returned):
        errors.append(f"{context}: returned_ids must be a list of strings")
        returned = []
    for cid in returned:
        if cid not in ids:
            errors.append(f"{context}: returned id `{cid}` is not in graph.db")

    anchor = route.get("anchor_id")
    if not isinstance(anchor, str) or not anchor:
        errors.append(f"{context}: anchor_id must be a non-empty string")

    traces = route.get("expansion_traces")
    if not isinstance(traces, list):
        errors.append(f"{context}: expansion_traces must be a list")
        traces = []

    expected: list[str] = []
    if (isinstance(tags, list) and all(isinstance(tag, str) for tag in tags)
            and isinstance(limit, int) and not isinstance(limit, bool) and limit > 0):
        expected = query_route_ids(tags, limit)
        if returned != expected:
            errors.append(f"{context}: returned_ids do not match deterministic route; "
                          f"expected {expected!r}, got {returned!r}")
    if isinstance(anchor, str) and isinstance(returned, list) and anchor not in returned:
        errors.append(f"{context}: anchor_id `{anchor}` is not in returned_ids")

    reachable = {anchor} if isinstance(anchor, str) and anchor else set()
    valid_targets: set[str] = set()
    for index, trace in enumerate(traces):
        trace_context = f"{context}: expansion_traces[{index}]"
        if not isinstance(trace, dict):
            errors.append(f"{trace_context}: trace must be an object")
            continue
        for key in sorted(set(trace) - TRACE_KEYS):
            errors.append(f"{trace_context}: unknown trace field `{key}`")
        for key in sorted(TRACE_KEYS - set(trace)):
            errors.append(f"{trace_context}: missing trace field `{key}`")
        source = trace.get("source_id")
        target = trace.get("target_id")
        edge = trace.get("edge")
        tag = trace.get("tag")
        trace_valid = True
        if not all(isinstance(value, str) and value for value in
                   (source, target, edge, tag)):
            errors.append(f"{trace_context}: trace fields must be non-empty strings")
            trace_valid = False
        if source not in ids:
            errors.append(f"{trace_context}: source id `{source}` is not in graph.db")
            trace_valid = False
        if target not in ids:
            errors.append(f"{trace_context}: target id `{target}` is not in graph.db")
            trace_valid = False
        if source not in reachable:
            errors.append(f"{trace_context}: source `{source}` is not the anchor or an earlier target")
            trace_valid = False
        edge_exists = ((source, target, edge, tag) in edges
                       or (target, source, edge, tag) in edges)
        # Common tags (>50% of nodes) are intentionally excluded from SHARES_TAG
        # edge generation to prevent near-complete graph expansion.
        if not edge_exists and not (common_tags and tag in common_tags):
            errors.append(f"{trace_context}: no `{edge}`/`{tag}` edge exists in either direction")
            trace_valid = False
        if trace_valid:
            reachable.add(target)
            valid_targets.add(target)

    return errors, valid_targets


def candidate_route(obj: dict):
    provenance = obj.get("provenance")
    if not isinstance(provenance, dict):
        return _MISSING
    return provenance.get("route", _MISSING)




def evidence_ids(obj: dict) -> list[str]:
    """Return every chunk ID cited through supported candidate schemas."""
    ids: list[str] = []
    for field in ("evidence", "evidence_ids"):
        value = obj.get(field)
        if isinstance(value, str):
            value = [value]
        if isinstance(value, list):
            ids.extend(
                item for item in value
                if isinstance(item, str) and re.fullmatch(r"[0-9]{2}_[a-z0-9_]+", item)
            )
    principle = obj.get("principle")
    if isinstance(principle, str) and re.fullmatch(r"[0-9]{2}_[a-z0-9_]+", principle):
        ids.append(principle)
    return ids


VALID = {"proposed","experimental","accepted","rejected"}


def current_fingerprint() -> str:
    """Live corpus fingerprint (source of truth) — matches watch.py/build_graph.py."""
    import hashlib
    h = hashlib.sha256()
    for p in sorted((ROOT / "knowledge" / "corpus").glob("*.md")):
        h.update(p.read_bytes())
    return h.hexdigest()[:12]


def current_plan_version() -> str:
    """WORKFLOW.md sha12 — 0*12 if the plan artifact is absent."""
    import hashlib
    return hashlib.sha256(WORKFLOW.read_bytes()).hexdigest()[:12] if WORKFLOW.exists() else "0" * 12


def provenance_ok(text: str, live_fp: str, plan_ver: str) -> tuple[bool, str]:
    """P5: an output is traceable if it declares fingerprint + plan_version + phase.

    A declared fingerprint must equal the live corpus fingerprint (else the output
    describes a graph that no longer exists). Plan version is advisory for legacy
    digests but required for anything claiming to follow the pipeline contract.
    """
    fp = PROV_FP.search(text)
    plan = PROV_PLAN.search(text)
    phase = PROV_PHASE.search(text)
    if not fp:
        return False, "missing `fingerprint:` provenance stamp"
    if fp.group(1) != live_fp:
        return False, f"fingerprint {fp.group(1)} != live corpus {live_fp} (stale output)"
    if not plan:
        return False, "missing `plan_version:` stamp"
    if plan.group(1) != plan_ver:
        return False, f"plan_version {plan.group(1)} != current WORKFLOW.md {plan_ver}"
    if not phase:
        return False, "missing `phase:` stamp"
    return True, ""


def existing_ids() -> set[str]:
    if not DB.exists():
        print(f"FAIL: {DB} missing — run build_graph.py", file=sys.stderr)
        sys.exit(2)
    c = sqlite3.connect(DB)
    rows = c.execute("SELECT id FROM nodes").fetchall()
    c.close()
    return {r[0] for r in rows}
def dead_route_tags() -> list[str]:
    """W-AUDIT-4 guard: every --tag named in a 06_reflect routing block must exist in
    knowledge/topics.md. A mandated route resolving to zero chunks is a silent failure."""
    prompts = ROOT / "pipeline" / "06_reflect"
    topics = ROOT / "knowledge" / "topics.md"
    if not prompts.exists() or not topics.exists():
        return []
    vocab: set[str] = set()
    for line in topics.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if s.startswith("- ") and len(s) > 2:
            vocab.add(s[2:].strip())
    bad = []
    pat = re.compile(r"--tag\s+([A-Za-z0-9_-]+)")
    for p in sorted(prompts.glob("*.prompt")):
        for m in pat.finditer(p.read_text(encoding="utf-8", errors="ignore")):
            if m.group(1) not in vocab:
                bad.append(f"{p.name}: --tag {m.group(1)} not in knowledge/topics.md (dead route)")
    return bad

def replan() -> int:
    """`--replan` action: re-stamp outputs to the live plan version and live corpus.

    WHY THIS EXISTS — plan_version is the sha12 of pipeline/WORKFLOW.md and the
    corpus fingerprint is the sha12 of knowledge/corpus/*.md, both stamped into
    every digest + candidate row. Editing either one therefore invalidates every
    prior reflection by check-time, even though its evidence and citations are
    unchanged. That coupling is the defect; this repair is the bandage: re-stamp to
    live and mark the row `regenerated_plan` so the audit trail records that the
    stamp moved, never silently re-dated.

    The corpus stamp is re-stamped by the same argument and under the same guard:
    an ADDITIVE corpus change (ingesting new chunks) moves the fingerprint while
    leaving every previously cited chunk id intact and still resolvable. A
    SUBTRACTIVE change (a cited chunk deleted or renamed) is a genuine staleness
    that re-stamping would hide — so before moving the corpus stamp this asserts
    that every evidence/principle id cited by a candidate still resolves in the
    live graph. If any does not, it refuses and names them.
    """
    new_pv = current_plan_version()
    live_fp = current_fingerprint()
    # Guard: never re-stamp a corpus fingerprint over a citation that no longer
    # resolves. That would convert a real staleness into a false "grounded" pass.
    ids = existing_ids()
    broken: list[str] = []
    for jl in sorted(CANDIDATES.glob("*.jsonl")):
        for i, line in enumerate(jl.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            obj = json.loads(line)
            for cid in evidence_ids(obj):
                if cid not in ids:
                    broken.append(f"{jl.name}:{i}: evidence id `{cid}` no longer resolves")
    if broken:
        print("REFUSE: corpus fingerprint changed AND cited ids no longer resolve — "
              "re-stamping would hide a real staleness:", file=sys.stderr)
        for b in broken:
            print(f"  {b}", file=sys.stderr)
        return 1
    n_md = n_rows = 0
    for md in sorted(DIGESTS.glob("*.md")):
        t = md.read_text(encoding="utf-8")
        changed = False
        if PROV_PLAN.search(t):
            t = PROV_PLAN.sub(f'plan_version: {new_pv}', t)
            changed = True
        if PROV_FP.search(t):
            t = PROV_FP.sub(f'fingerprint: {live_fp}', t)
            changed = True
        if PROV_PHASE.search(t):
            t = PROV_PHASE.sub(f'phase: {REFLECTION_PHASE}', t)
            changed = True
        else:
            t = f"phase: {REFLECTION_PHASE}\n\n" + t
            changed = True
        if changed:
            md.write_text(t, encoding="utf-8")
            n_md += 1
    for jl in sorted(CANDIDATES.glob("*.jsonl")):
        original = jl.read_text(encoding="utf-8")
        rows = []
        changed_file = False
        for line in original.splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            p = obj.get("provenance") or {}
            moved = False
            if p.get("plan_version") != new_pv:
                p["plan_version"] = new_pv
                moved = True
            if p.get("fingerprint") != live_fp:
                p["fingerprint"] = live_fp
                moved = True
            if p.get("phase") != REFLECTION_PHASE:
                p["phase"] = REFLECTION_PHASE
                moved = True
            if moved:
                p["regenerated_plan"] = True
                obj["provenance"] = p
                n_rows += 1
                changed_file = True
            rows.append(json.dumps(obj, ensure_ascii=False))
        if changed_file:
            suffix = "\n" if original.endswith("\n") else ""
            jl.write_text("\n".join(rows) + suffix, encoding="utf-8")
    print(f"OK: re-stamped {n_md} digest(s) and {n_rows} candidate row(s) to "
          f"plan_version {new_pv} / fingerprint {live_fp}; audit follows")
    return 0
def route_pair_errors(md_name: str, text: str, candidate_obj: dict | None,
                      ids: set[str], valid_tags: set[str],
                      edges: set[tuple[str, str, str, str]],
                      common_tags: set[str] | None = None) -> list[str]:
    """Validate optional route metadata while leaving legacy artifacts untouched."""
    digest_route, digest_parse_errors, digest_present = parse_digest_route(text, md_name)
    candidate_route_value = (candidate_route(candidate_obj)
                             if candidate_obj is not None else _MISSING)
    candidate_present = candidate_route_value is not _MISSING
    errors: list[str] = []

    if md_name == "agentic_workspace_workflow.md":
        if not digest_present:
            errors.append(f"{md_name}: required digest route metadata is missing")
        if not candidate_present:
            errors.append(f"{md_name}: required candidate route metadata is missing")
    if not digest_present and not candidate_present:
        return errors

    digest_targets: set[str] = set()
    candidate_targets: set[str] = set()
    if digest_present:
        errors.extend(f"{md_name}: digest route: {error}"
                      for error in digest_parse_errors)
        if isinstance(digest_route, dict):
            route_errors, digest_targets = validate_route(
                digest_route, ids, valid_tags, edges, f"{md_name}: digest route", common_tags)
            errors.extend(route_errors)
    if candidate_present:
        if not isinstance(candidate_route_value, dict):
            errors.append(f"{md_name}: candidate route metadata must be an object")
        else:
            route_errors, candidate_targets = validate_route(
                candidate_route_value, ids, valid_tags, edges,
                f"{md_name}: candidate route", common_tags)
            errors.extend(route_errors)

    if digest_present and candidate_present and digest_route != candidate_route_value:
        errors.append(
            f"{md_name}: digest route metadata differs from candidate route metadata")

    if candidate_obj is not None and (digest_present or candidate_present):
        route = (candidate_route_value if candidate_present else digest_route)
        allowed: set[str] = set()
        if isinstance(route, dict):
            returned = route.get("returned_ids")
            if isinstance(returned, list):
                allowed.update(cid for cid in returned if isinstance(cid, str))
            allowed.update(candidate_targets if candidate_present else digest_targets)
        for cid in evidence_ids(candidate_obj):
            if cid not in allowed:
                errors.append(
                    f"{md_name}: evidence id `{cid}` is not in the route result "
                    "or a validated connected expansion")
    return errors

def scoped(patterns: list[str]):
    """Restrict digest/candidate iteration to artifacts this run produced.

    Grading a whole directory cannot distinguish "my change is broken" from
    "some earlier artifact is broken", so a run that produced nothing gradeable
    still reports on old files and can be reported as green. `--paths` makes the
    gate grade exactly the artifacts the caller claims to have produced, which
    is what makes a PASS mean something about the change.
    """
    if not patterns:
        return sorted(DIGESTS.glob("*.md")), sorted(CANDIDATES.glob("*.jsonl"))
    mds, jls = [], []
    for pat in patterns:
        p = Path(pat)
        base = p if p.is_absolute() else (ROOT / p)
        if base.is_file() and base.suffix == ".md":
            mds.append(base)
        elif base.is_file() and base.suffix == ".jsonl":
            jls.append(base)
        elif base.is_dir():
            mds.extend(sorted(base.glob("*.md")))
            jls.extend(sorted(base.glob("*.jsonl")))
        else:
            # Search graded dirs AND scratch dirs for bare slugs, so a preflight
            # re-grade of a moved topic finds its artifacts wherever they live.
            search_mds = [DIGESTS, SCRATCH_DIGESTS]
            search_jls = [CANDIDATES, SCRATCH_CANDIDATES]
            matches_md = []
            matches_jsonl = []
            for d in search_mds:
                if pat.endswith(".md"):
                    matches_md.extend(sorted(d.glob(pat)))
                else:
                    matches_md.extend(sorted(d.glob(f"{pat}.md")))
            for d in search_jls:
                if pat.endswith(".jsonl"):
                    matches_jsonl.extend(sorted(d.glob(pat)))
                else:
                    matches_jsonl.extend(sorted(d.glob(f"{pat}.jsonl")))
            mds.extend(matches_md)
            jls.extend(matches_jsonl)
    if not mds and not jls:
        print(f"SCOPE ERROR: --paths {patterns} matched no digest or candidate artifact", file=sys.stderr)
        raise SystemExit(2)
    return sorted(set(mds)), sorted(set(jls))


def main()->int:
    if "--replan" in sys.argv:
        return replan()
    argv = sys.argv[1:]
    patterns: list[str] = []
    if "--paths" in argv:
        i = argv.index("--paths") + 1
        if i < len(argv):
            patterns = [a for a in argv[i:] if not a.startswith("-")]
    scoped_digests, scoped_candidates = scoped(patterns)

    # Snapshot before reading: a gate report that can be deleted along with the
    # artifact it graded is not evidence. Cheap, and it makes "what did the gate
    # actually see" answerable after the working copy is gone.
    try:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "snapshot_graded.py"),
             "--label", "pre-gate", *(["--paths", *patterns] if patterns else [])],
            capture_output=True, text=True, cwd=str(ROOT), check=False,
        )
    except OSError:
        pass  # never let the audit aid block the audit

    ids = existing_ids()
    live_fp = current_fingerprint()
    plan_ver = current_plan_version()
    valid_tags = load_route_tags()
    edges = load_graph_edges()
    common_tags = common_tag_threshold()
    print(f"[check_reflection] common tags (skipped for expansion traces): {sorted(common_tags)}", file=sys.stderr)
    errors: list[str] = []

    for md in scoped_digests:
        text = md.read_text(encoding="utf-8", errors="ignore")
        # P5 provenance: output must declare the fingerprint + plan version it was built against
        ok, why = provenance_ok(text, live_fp, plan_ver)
        if not ok:
            errors.append(f"{md.name}: {why}")
        # chunk ids are NN_slug with underscore; avoid matching stage names like 06_reflect
        cited = {m for m in ID_RE.findall(text) if m in ids}
        # only warn, don't fail, if no chunk ids — some digests cite differently
        if not cited and "`" in text:
            raw = set(ID_RE.findall(text))
            for cid in raw - ids:
                errors.append(f"{md.name}: cited id `{cid}` not in graph.db (check chunk id)")
        stem = md.stem
        # Derive the candidate dir from the digest's actual location: a digest in
        # reflection/digests/ pairs with reflection/candidates/, a digest in
        # reflection/scratch/digests/ pairs with reflection/scratch/candidates/.
        # Hardcoding CANDIDATES here would make any non-graded digest fail with
        # "missing paired", which is not a real failure — it's a path bug.
        digest_dir_name = md.parent.name  # "digests" or "digests"
        cand_dir = md.parent.parent / "candidates"  # sibling of the digest dir
        cand = cand_dir / f"{stem}.jsonl"
        candidate_rows: list[dict] = []
        if not cand.exists():
            errors.append(f"{md.name}: missing paired {cand.name}")
            errors.extend(route_pair_errors(
                md.name, text, None, ids, valid_tags, edges, common_tags))
            continue

        # candidates must carry the same provenance as their digest; parse the JSON
        # object, since raw-text scanning would match a quoted hash inside claim prose
        jtext = cand.read_text(encoding="utf-8", errors="ignore")
        cok, cwhy = provenance_ok_jsonl(jtext, live_fp, plan_ver)
        if not cok:
            errors.append(f"{cand.name}: {cwhy}")
        for line in jtext.splitlines():
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"{cand.name}: invalid JSON — {e}")
                continue
            if not isinstance(obj, dict):
                errors.append(f"{cand.name}: candidate row must be an object")
                continue
            candidate_rows.append(obj)
            errors.extend(trace_provenance_errors(obj, f"{cand.name}:{len(candidate_rows)}"))

        if candidate_rows:
            for candidate_obj in candidate_rows:
                errors.extend(route_pair_errors(
                    md.name, text, candidate_obj, ids, valid_tags, edges, common_tags))
        else:
            errors.extend(route_pair_errors(
                md.name, text, None, ids, valid_tags, edges, common_tags))

    CANONICAL_FIELDS = ("Rule", "Evidence", "Target", "Action")
    LEGACY_KEYS = ("claim", "evidence", "evidence_ids", "principle")

    for jl in scoped_candidates:
        for i, line in enumerate(jl.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"{jl.name}:{i}: invalid JSON — {e}")
                continue
            state = obj.get("state")
            if state not in VALID:
                errors.append(f"{jl.name}:{i}: missing or invalid field `state`")
                continue

            # Strict schema enforcement: legacy claim/evidence formats are forbidden
            legacy_present = [k for k in LEGACY_KEYS if k in obj]
            if legacy_present:
                errors.append(
                    f"{jl.name}:{i}: legacy field(s) {legacy_present!r} are forbidden; "
                    f"use canonical Rule/Evidence/Target/Action"
                )
                continue

            # Canonical fields required for all states
            missing = [name for name in CANONICAL_FIELDS
                       if not isinstance(obj.get(name), str) or not obj[name].strip()]
            if missing:
                errors.append(
                    f"{jl.name}:{i}: missing or blank canonical field(s): "
                    f"{', '.join(missing)}"
                )
                continue

            # Evidence ids must resolve
            ev_ids = re.findall(r"`([^`]+)`", obj.get("Evidence", ""))
            if not ev_ids:
                errors.append(f"{jl.name}:{i}: Evidence field has no backticked citation ids")
            for cid in ev_ids:
                if cid not in ids:
                    errors.append(f"{jl.name}:{i}: evidence id `{cid}` not in graph.db")
            # Content backing (W-AUDIT predicate over LLM-written candidates):
            # cited chunks must share vocabulary with the claim, not merely
            # resolve. Hard-fails on proposed/experimental rows; accepted and
            # rejected rows passed human review, so a thin link warns instead
            # of rewriting admitted history (see Open work).
            if audit_claim_grounding is not None and ev_ids:
                backed, backing_issues = audit_claim_grounding(
                    obj.get("Rule", ""), ev_ids)
                if not backed:
                    loc = f"{jl.name}:{i} ({obj.get('id', '?')})"
                    if state in ("proposed", "experimental"):
                        errors.extend(f"{loc}: {issue}" for issue in backing_issues)
                    else:
                        for issue in backing_issues:
                            print(f"WARN: {loc}: {issue}", file=sys.stderr)
    errors.extend(dead_route_tags())

    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1
    scope_note = f" scoped to {len(scoped_digests) + len(scoped_candidates)} artifact(s) via --paths" if patterns else ""
    print(f"OK: checked {len(scoped_digests)} digests / {len(scoped_candidates)} candidate files — all grounded.{scope_note}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
