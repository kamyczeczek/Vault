#!/usr/bin/env python3
"""reflect.py — single-pass structured reflection using pre-computed evidence packets.

Replaces the omp agent loop: runs deterministic tag queries in parallel via
presearch, builds an evidence packet, makes one LLM call that outputs claims,
candidates, and next bets in a validated schema, then writes the digest and
candidate file. All provenance and timing stays in Python.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import agent_trace
import presearch
import pi_models

# ─── Model endpoint resolution ───

def _resolve_endpoint() -> tuple[str, str, str]:
    """Return (api_key, base_url, model_id) from the session's provider config.

    Provider/model are driven by PI_PROVIDER/PI_MODEL (pi session config),
    not pinned in the runner. pi's models.json is parsed through
    pi_models.load_models, which tolerates pi's trailing-comma write artifact;
    config files must never be hand-edited (see GATES-T1, port constraints).
    """
    return pi_models.resolve_endpoint()


class ReflectionError(Exception):
    """Typed reflection failure; `kind` feeds the trace ledger's failure_kind."""

    def __init__(self, kind: str, message: str) -> None:
        super().__init__(message)
        self.kind = kind


# ─── Grounded review gate + decision-point ledger ───
# Derived from candidate entropy-001-peer-review-graph (reflection topic
# decision_graphs_workflow): introduce a Review state to the reflection
# transition logic — verify cited chunk ids exist in the corpus BEFORE the
# digest/candidates are written, and record the review/accepted/rejected
# decision point in a persistent ledger (ADR-007-style decision record:
# state + question + answer + context, auditable after the fact).

DECISION_LEDGER = ROOT / "reflection" / "decision_points.jsonl"
CORPUS_DIR = ROOT / "knowledge" / "corpus"


def _log_decision_point(topic: str, state: str, detail: dict, ledger: Path | None = None) -> None:
    path = ledger if ledger is not None else DECISION_LEDGER
    record = {
        "topic": topic,
        "state": state,
        "detail": detail,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _cited_chunk_ids(output: dict) -> list[str]:
    """All chunk ids cited by claims (evidence lists) and candidates (Evidence)."""
    ids: set[str] = set()
    for claim in output.get("claims", []):
        for ev in claim.get("evidence", []):
            ids.update(re.findall(r"[A-Za-z0-9_]{4,}", str(ev)))
    for cand in output.get("candidates", []):
        ids.update(re.findall(r"[A-Za-z0-9_]{4,}", str(cand.get("Evidence", ""))))
    return sorted(ids)


def _ungrounded_citations(output: dict, corpus_dir: Path | None = None) -> list[str]:
    """Cited chunk ids that do not exist in the corpus (fail-closed review)."""
    cdir = corpus_dir if corpus_dir is not None else CORPUS_DIR
    return [cid for cid in _cited_chunk_ids(output) if not (cdir / f"{cid}.md").exists()]

# ─── Tag query mapping ───

# Default tag sets for a reflection topic. These are the same four the planner
# selected in the last successful run. Can be extended/overridden per topic.
DEFAULT_TAG_SETS: list[list[str]] = [
    ["workflow-evolution"],
    ["memory", "reflection"],
    ["icm", "memory"],
    ["provenance"],
]

# ─── LLM prompt ───

REFLECTION_SYSTEM = """You are a reflection agent for the Workspace-Research ICM knowledge base.
Your input is an evidence packet: pre-retrieved, grounded chunks from the graph.
Your output is a single JSON object with three arrays: claims, candidates, next_bets.
Do not add extra keys. Do not include reasoning outside the JSON."""

REFLECTION_USER_TEMPLATE = """TOPIC: {topic}
GRAPH FINGERPRINT: {fingerprint}
PLAN VERSION: {plan_version}

EVIDENCE PACKET:
{evidence}

INSTRUCTIONS:
1. Each claim must cite >=1 chunk id from the evidence packet. Use the exact chunk id.
2. Each candidate must follow the exact schema:
   {{
     "id": "entropy-001-<short>",
     "state": "proposed",
     "type": "candidate",
     "date": "YYYY-MM-DD",
     "Rule": "...",
     "Evidence": "`id1`, `id2`",
     "Target": "...",
     "Action": "...",
     "Condition": "...",
     "Reason": "...",
     "Correction": "..."
   }}
3. Next bets are short actionable probes (strings).
4. Output ONLY the JSON object, no markdown fences, no extra text.

EVIDENCE FORMAT:
Each entry: {{"chunk_id": "...", "tags": [...], "excerpt": "..."}}
Only the excerpt is provided; you must cite by chunk_id.

JSON SCHEMA (output must match exactly):
{{
  "claims": [
    {{
      "claim": "...",
      "evidence": ["chunk_id1", "chunk_id2"],
      "decision": "...",
      "next_bet": "..."
    }}
  ],
  "candidates": [ ... per candidate schema above ... ],
  "next_bets": ["...", "..."]
}}"""


def _call_model(messages: list[dict[str, str]], api_key: str, base_url: str, model_id: str) -> str:
    """Call the OpenAI-compatible chat endpoint with a 300s timeout."""
    import httpx
    url = f"{base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 4096,
    }
    with httpx.Client(timeout=300.0) as client:
        resp = client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
    if "choices" not in data:
        print(f"[reflect] unexpected response: {json.dumps(data)[:500]}", file=sys.stderr)
        raise ReflectionError("unexpected_response", f"unexpected response format: {list(data.keys())}")
    return data["choices"][0]["message"]["content"]


def _build_evidence_packet(tag_sets: list[list[str]], limit: int = 12, max_chunks: int = 12) -> tuple[list[dict], dict]:
    """Run presearch queries and return (evidence_list, presearch_report)."""
    report = presearch.run_queries(tag_sets, limit=limit, parallel=True)
    seen: set[str] = set()
    evidence: list[dict] = []
    CHUNK_DIR = ROOT / "knowledge" / "corpus"
    for q in report["queries"]:
        for cid in q["ids"]:
            if len(evidence) >= max_chunks:
                break
            if cid in seen:
                continue
            seen.add(cid)
            chunk_path = CHUNK_DIR / f"{cid}.md"
            excerpt = ""
            if chunk_path.exists():
                txt = chunk_path.read_text(encoding="utf-8")
                excerpt = txt[:400].replace("\n", " ")
            evidence.append({"chunk_id": cid, "tags": q["tags"], "excerpt": excerpt})
        if len(evidence) >= max_chunks:
            break
    return evidence, report


def _write_digest(topic: str, output: dict, fingerprint: str, plan_version: str,
                  digests_dir: Path, candidates_dir: Path) -> None:
    """Write the markdown digest and jsonl candidates from the structured output."""
    from datetime import date
    today = date.today().isoformat()
    # Digest markdown
    lines = [
        f"# Reflection Digest — {topic}",
        "",
        f"- topic: {topic}",
        f"- phase: 04_reflect",
        f"- plan_version: {plan_version}",
        f"- fingerprint: {fingerprint}",
        f"- date: {today}",
        f"- evidence_chunks: {sum(len(c['evidence']) for c in output.get('claims', []))}",
        "",
    ]
    for i, claim in enumerate(output.get("claims", []), 1):
        lines.append(f"## Claim {i} — {claim['claim'][:80]}")
        lines.append("")
        lines.append(f"**Evidence** (`{'`, `'.join(claim['evidence'])}`):")
        lines.append("")
        # The excerpt isn't in the claim; we could enrich but keep it minimal
        lines.append(f"**Decision:** {claim['decision']}")
        lines.append("")
        lines.append(f"**Next bet:** {claim['next_bet']}")
        lines.append("")
    digests_dir.mkdir(parents=True, exist_ok=True)
    (digests_dir / f"{topic}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Candidates jsonl
    candidates_dir.mkdir(parents=True, exist_ok=True)
    cand_path = candidates_dir / f"{topic}.jsonl"
    with cand_path.open("w", encoding="utf-8") as f:
        for cand in output.get("candidates", []):
            # Ensure required keys and exact capitalization
            required = ["id", "state", "type", "date", "Rule", "Evidence", "Target",
                        "Action", "Condition", "Reason", "Correction"]
            for k in required:
                if k not in cand:
                    raise ValueError(f"candidate missing required key: {k}")
            if cand["state"] != "proposed":
                raise ValueError("candidate state must be 'proposed'")
            cand["date"] = today
            f.write(json.dumps(cand, ensure_ascii=False) + "\n")


def reflect_topic(topic: str, scratch: bool = False, tag_sets: list[list[str]] | None = None) -> int:
    """Run one reflection cycle for the given topic.

    Every run — success or failure — leaves trace records in
    `reflection/trace/events.jsonl` via agent_trace, so a failed run is
    never indistinguishable from a never-run one (defect recorded as the
    G12 follow-up open work).
    """
    run_id = agent_trace.new_run_id()
    agent_trace.emit("run", run_id=run_id, status="started", workflow="06_reflect",
                     topic=topic, runner="reflect.py")
    digest_rel = f"reflection/{'' if not scratch else 'scratch/'}digests/{topic}.md"
    try:
        rc = _reflect_topic_inner(topic, scratch, tag_sets)
        agent_trace.emit("run", run_id=run_id, status="completed", workflow="06_reflect",
                         topic=topic, runner="reflect.py")
        return rc
    except ReflectionError as e:
        agent_trace.emit("failure", run_id=run_id, status="failed", module="reflection",
                         runner="reflect.py", topic=topic, failure_kind=e.kind,
                         artifact=digest_rel, condition=e.args[0][:400])
        raise SystemExit(e.args[0]) from None
    except Exception as e:
        agent_trace.emit("failure", run_id=run_id, status="failed", module="reflection",
                         runner="reflect.py", topic=topic, failure_kind=type(e).__name__,
                         artifact=digest_rel, condition=str(e)[:400])
        raise


def _reflect_topic_inner(topic: str, scratch: bool, tag_sets: list[list[str]] | None) -> int:
    """The reflection body: evidence -> LLM call -> validated artifacts."""
    # Provenance
    fp_file = ROOT / "knowledge" / "graph" / ".graph_fingerprint"
    fingerprint = fp_file.read_text(encoding="utf-8").strip() if fp_file.exists() else ""
    workflow = ROOT / "pipeline" / "WORKFLOW.md"
    import hashlib
    plan_version = hashlib.sha256(workflow.read_bytes()).hexdigest()[:12] if workflow.exists() else ""

    # Evidence
    queries = tag_sets if tag_sets is not None else DEFAULT_TAG_SETS
    evidence, presearch_report = _build_evidence_packet(queries)

    # LLM call — endpoint resolution happens in-run, not at import time, so a
    # missing pi config is traced as a failed run rather than crashing import.
    api_key, base_url, model_id = _resolve_endpoint()
    user_prompt = REFLECTION_USER_TEMPLATE.format(
        topic=topic,
        fingerprint=fingerprint,
        plan_version=plan_version,
        evidence=json.dumps(evidence, ensure_ascii=False, indent=2),
    )
    messages = [
        {"role": "system", "content": REFLECTION_SYSTEM},
        {"role": "user", "content": user_prompt},
    ]
    raw = _call_model(messages, api_key, base_url, model_id)

    # Parse JSON
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        # Try to extract JSON from markdown fences
        m = re.search(r"```(?:json)?\n(.*?)\n```", raw, re.DOTALL)
        if m:
            parsed = json.loads(m.group(1))
        else:
            raise ReflectionError("bad_json", f"LLM output not valid JSON: {e}\n--- raw ---\n{raw[:500]}")

    # Validate structure
    for key in ("claims", "candidates", "next_bets"):
        if key not in parsed:
            raise ReflectionError("missing_key", f"LLM output missing required key: {key}")

    # Grounded review gate: verify citations BEFORE writing artifacts.
    packet_ids = {e["chunk_id"] for e in evidence}
    cited = _cited_chunk_ids(parsed)
    out_of_packet = sorted(set(cited) - packet_ids)
    ungrounded = _ungrounded_citations(parsed)
    _log_decision_point(
        topic, "review",
        {"cited_chunks": cited, "out_of_packet": out_of_packet, "ungrounded": ungrounded},
    )
    if ungrounded:
        # Fail closed: an artifact citing nonexistent chunks would propagate
        # fabricated sources into the digest/candidates and downstream gates.
        _log_decision_point(topic, "rejected", {"ungrounded_chunks": ungrounded})
        raise ReflectionError(
            "ungrounded_evidence",
            f"LLM cited chunk ids that do not exist in the corpus: {ungrounded}",
        )
    _log_decision_point(topic, "accepted", {"grounded_chunks": cited, "out_of_packet": out_of_packet})

    # Write artifacts
    out_digests = ROOT / "reflection" / ("scratch" if scratch else "") / "digests"
    out_candidates = ROOT / "reflection" / ("scratch" if scratch else "") / "candidates"
    _write_digest(topic, parsed, fingerprint, plan_version, out_digests, out_candidates)

    # Attach provenance to candidates (reuse existing attach_trace_provenance logic)
    cand_path = out_candidates / f"{topic}.jsonl"
    if cand_path.exists():
        # Minimal provenance injection (run_id, fingerprint, plan_version, phase)
        rows: list[dict] = []
        run_id = f"reflect-{int(time.time() * 1000)}"
        for line in cand_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                obj = json.loads(line)
                provenance = obj.setdefault("provenance", {})
                provenance["run_id"] = run_id
                provenance["fingerprint"] = fingerprint
                provenance["plan_version"] = plan_version
                provenance["phase"] = "04_reflect"
                rows.append(obj)
        cand_path.write_text("\n".join(json.dumps(o, ensure_ascii=False) for o in rows) + "\n", encoding="utf-8")

    print(f"[reflect] wrote digest + candidates for {topic} (evidence chunks: {len(evidence)})")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--topic", required=True, help="reflection topic slug")
    ap.add_argument("--scratch", action="store_true", help="write to reflection/scratch/")
    ap.add_argument("--tag-sets", help="JSON array of tag arrays, e.g. '[[\"icm\"],[\"memory\"]]'")
    args = ap.parse_args()

    tag_sets = json.loads(args.tag_sets) if args.tag_sets else None
    return reflect_topic(args.topic, scratch=args.scratch, tag_sets=tag_sets)


if __name__ == "__main__":
    raise SystemExit(main())