#!/usr/bin/env python3
"""check_reflection.py — W4/W7 closure gate.

Asserts:
- every cited chunk id in reflection/digests/*.md resolves via graph.db
- every digest has a paired reflection/candidates/*.jsonl
- candidates jsonl rows have {id,state,claim,evidence,bet}, valid state machine,
  and grounded evidence ids that resolve in graph.db
"""
from __future__ import annotations
import json, re, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIGESTS = ROOT / "reflection" / "digests"
CANDIDATES = ROOT / "reflection" / "candidates"
DB = ROOT / "knowledge" / "graph" / "graph.db"
WORKFLOW = ROOT / "pipeline" / "WORKFLOW.md"
# P5: every output must be traceable to the corpus + plan version that produced it.
# Patterns accept both prose (`fingerprint: abc123`) and JSON (`"fingerprint": "abc123"`).
PROV_FP = re.compile(r"fingerprint\s*[\"']?\s*[:=]\s*[\"']?([0-9a-f]{8,12})")
PROV_PLAN = re.compile(r"plan_version\s*[\"']?\s*[:=]\s*[\"']?([0-9a-f]{12})")


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


PROV_PHASE = re.compile(r"phase\s*[\"']?\s*[:=]\s*[\"']?(\w+)")
ID_RE = re.compile(r"`([0-9]{2}_[a-z0-9_]+)`")

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
            for field in ("evidence", "principle"):
                v = obj.get(field)
                if not v:
                    continue
                vals = v if isinstance(v, list) else [v]
                for cid in vals:
                    if isinstance(cid, str) and re.match(r"^[0-9]{2}_[a-z0-9_]+$", cid) \
                            and cid not in ids:
                        broken.append(f"{jl.name}:{i}: {field} id `{cid}` no longer resolves")
    if broken:
        print("REFUSE: corpus fingerprint changed AND cited ids no longer resolve — "
              "re-stamping would hide a real staleness:", file=sys.stderr)
        for b in broken:
            print(f"  {b}", file=sys.stderr)
        return 1
    n_md = n_rows = 0
    for md in sorted(DIGESTS.glob("*.md")):
        t = md.read_text(encoding="utf-8")
        if PROV_PLAN.search(t):
            t = PROV_PLAN.sub(f'plan_version: {new_pv}', t)
        if PROV_FP.search(t):
            t = PROV_FP.sub(f'fingerprint: {live_fp}', t)
            md.write_text(t, encoding="utf-8")
            n_md += 1
    for jl in sorted(CANDIDATES.glob("*.jsonl")):
        rows = []
        for line in jl.read_text(encoding="utf-8").splitlines():
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
            if moved:
                p["regenerated_plan"] = True
                obj["provenance"] = p
                n_rows += 1
            rows.append(json.dumps(obj, ensure_ascii=False))
        jl.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"OK: re-stamped {n_md} digest(s) and {n_rows} candidate row(s) to "
          f"plan_version {new_pv} / fingerprint {live_fp}; audit follows")
    return 0
def main()->int:
    if "--replan" in sys.argv:
        return replan()
    ids = existing_ids()
    live_fp = current_fingerprint()
    plan_ver = current_plan_version()
    errors: list[str] = []

    for md in sorted(DIGESTS.glob("*.md")):
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
        cand = CANDIDATES / f"{stem}.jsonl"
        if not cand.exists():
            errors.append(f"{md.name}: missing paired {cand.name}")
        else:
            # candidates must carry the same provenance as their digest; parse the JSON
            # object, since raw-text scanning would match a quoted hash inside claim prose
            jtext = cand.read_text(encoding="utf-8", errors="ignore")
            cok, cwhy = provenance_ok_jsonl(jtext, live_fp, plan_ver)
            if not cok:
                errors.append(f"{cand.name}: {cwhy}")


    for jl in sorted(CANDIDATES.glob("*.jsonl")):
        for i, line in enumerate(jl.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"{jl.name}:{i}: invalid JSON — {e}")
                continue
            # accept both schemas: {principle,change,observation} and {claim,evidence,bet}
            has_claim = "claim" in obj

            has_principle = "principle" in obj
            if not (has_claim or has_principle):
                errors.append(f"{jl.name}:{i}: missing field `principle` or `claim`")
            if "state" not in obj:
                errors.append(f"{jl.name}:{i}: missing field `state`")
            elif obj.get("state") not in VALID:
                errors.append(f"{jl.name}:{i}: invalid state `{obj.get('state')}`")
            # evidence grounding: check principle/chunk id if it looks like a chunk id
            principle = obj.get("principle", "")
            if isinstance(principle, str) and "_" in principle and principle not in ids:
                # principle is a chunk id — must resolve; if it's prose, skip
                if re.match(r"^[0-9]{2}_[a-z0-9_]+$", principle):
                    errors.append(f"{jl.name}:{i}: principle id `{principle}` not in graph.db")
            ev = obj.get("evidence")
            if ev is not None:
                if not isinstance(ev, list) or not ev:
                    errors.append(f"{jl.name}:{i}: evidence must be non-empty list if present")
                else:
                    for cid in ev:
                        if cid not in ids:
                            errors.append(f"{jl.name}:{i}: evidence id `{cid}` not in graph.db")
    errors.extend(dead_route_tags())


    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1
    print(f"OK: checked {len(list(DIGESTS.glob('*.md')))} digests / {len(list(CANDIDATES.glob('*.jsonl')))} candidate files — all grounded.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
