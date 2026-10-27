#!/usr/bin/env python3
"""promote_candidate.py — W7 state-machine transition + validator.

Transitions a candidate id through proposed→experimental→accepted|rejected,
validates evidence ids against graph.db, and optionally writes an accepted
canonical rule to memory and/or a corpus chunk.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SESSION_DB = ROOT / "knowledge" / "graph" / "sessions.db"
REVIEW_LOG = ROOT / "reflection" / "review_gate.jsonl"
FINGERPRINT_FILE = ROOT / "knowledge" / "graph" / ".graph_fingerprint"
CANDIDATES = ROOT / "reflection" / "candidates"
DB = ROOT / "knowledge" / "graph" / "graph.db"
VALID = {"proposed", "experimental", "accepted", "rejected"}
TRANS = {
    ("proposed", "experimental"),
    ("experimental", "accepted"),
    ("experimental", "rejected"),
}
CANONICAL_FIELDS = ("Rule", "Evidence", "Target", "Action")
LEGACY_KEYS = ("claim", "evidence", "evidence_ids", "principle")


def _verified_lesson_link_exists(candidate_id: str) -> bool:
    """Accepted lessons need an independent verification event in the session store."""
    if not SESSION_DB.exists():
        return False
    conn = sqlite3.connect(SESSION_DB)
    try:
        row = conn.execute(
            "SELECT 1 FROM lesson_links WHERE lesson_id=? AND status='verified' LIMIT 1",
            (candidate_id,),
        ).fetchone()
        return row is not None
    except sqlite3.OperationalError:
        return False
    finally:
        conn.close()


def _review_pair_exists(candidate_id: str) -> bool:
    """Acceptance needs a complete peer-review before→after pair for this candidate.

    CRITIC verify-then-correct (`00_07_critic_external_tool_verification`) and the
    automated peer-review rule (`00_automated_peer_review_and_self_correction`):
    no promotion on self-critique alone. The pair must carry the candidate id as
    its label and be stamped with the live corpus fingerprint, so a review of an
    older corpus cannot bless a newer state.
    """
    if not REVIEW_LOG.exists():
        return False
    live_fp = FINGERPRINT_FILE.read_text(encoding="utf-8").strip() if FINGERPRINT_FILE.exists() else ""
    try:
        rows = [json.loads(line) for line in REVIEW_LOG.read_text(encoding="utf-8").splitlines() if line.strip()]
    except (OSError, ValueError):
        return False
    for prev, cur in zip(rows, rows[1:]):
        if (prev.get("phase") == "before" and cur.get("phase") == "after"
                and prev.get("label") == candidate_id and cur.get("label") == candidate_id
                and cur.get("metrics") and prev.get("fingerprint") == live_fp and cur.get("fingerprint") == live_fp):
            return True
    return False


def _atomic_write(path: Path, content: str) -> None:
    """Replace a file atomically on the same filesystem."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def _legacy_section(body: str) -> bool:
    return bool(
        re.search(
            r"^\s*-\s*(?:claim|evidence)\s*:",
            body,
            flags=re.MULTILINE | re.IGNORECASE,
        )
    )


def _canonical_candidate(obj: dict) -> tuple[dict[str, str] | None, list[str]]:
    values: dict[str, str] = {}
    missing: list[str] = []
    for name in CANONICAL_FIELDS:
        value = obj.get(name)
        if not isinstance(value, str) or not value.strip():
            missing.append(name)
        else:
            values[name] = value.strip()

    legacy_keys = [key for key in LEGACY_KEYS if key in obj]
    missing.extend(f"legacy {key}" for key in legacy_keys)
    return (values if not missing else None, missing)


def _evidence_list(value: str) -> list[str]:
    return re.findall(r"`([^`]+)`", value)


def existing_ids() -> set[str]:
    c = sqlite3.connect(DB)
    rows = c.execute("SELECT id FROM nodes").fetchall()
    c.close()
    return {r[0] for r in rows}


def find_candidate(cid: str):
    for jl in CANDIDATES.glob("*.jsonl"):
        for line in jl.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            if obj.get("id") == cid or obj.get("candidate_id") == cid:
                return jl, obj
    return None, None


def _rewrite_candidate_state(jl: Path, cid: str, dst_state: str) -> None:
    lines: list[str] = []
    for line in jl.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        if obj.get("id") == cid or obj.get("candidate_id") == cid:
            obj["state"] = dst_state
        lines.append(json.dumps(obj, ensure_ascii=False))
    _atomic_write(jl, "\n".join(lines) + "\n")


def _write_memory(mem: Path, obj: dict, canonical: dict[str, str]) -> None:
    existing = mem.read_text(encoding="utf-8") if mem.exists() else ""
    if _legacy_section(existing):
        raise ValueError(f"{mem} contains a legacy claim/evidence section")

    evidence = ", ".join(f"`{e}`" for e in _evidence_list(canonical["Evidence"]))
    cid = obj.get("id") or obj.get("candidate_id")
    header = f"### {cid} — accepted"
    text = (
        f"\n{header}\n"
        f"Rule: {canonical['Rule']}\n"
        f"Evidence: {evidence}\n"
        f"Target: {canonical['Target']}\n"
        f"Action: {canonical['Action']}\n"
    )

    if header in existing:
        start = existing.index(header)
        next_start = existing.find("\n### ", start + len(header))
        end = next_start if next_start != -1 else len(existing)
        old_body = existing[start:end]
        if _legacy_section(old_body):
            raise ValueError(f"{mem} contains a legacy section for {cid}")
        lines = existing.splitlines()
        for index, line in enumerate(lines):
            if line.strip() == header:
                next_index = index + 1
                while next_index < len(lines) and not lines[next_index].startswith("### "):
                    next_index += 1
                lines[index:next_index] = text.strip().splitlines()
                break
        updated = "\n".join(lines) + "\n"
    else:
        updated = existing + text if existing else text.lstrip("\n")
    _atomic_write(mem, updated)


def _write_corpus(obj: dict, jl: Path, canonical: dict[str, str]) -> Path:
    cid = obj.get("id") or obj.get("candidate_id")
    cid_slug = re.sub(r"[^a-z0-9_]+", "_", str(cid).lower()).strip("_")
    chunk_id = f"derived_rule_{cid_slug}"
    chunk_file = ROOT / "knowledge" / "corpus" / f"{chunk_id}.md"
    evidence = _evidence_list(canonical["Evidence"])
    chunk_content = f"""---
id: {chunk_id}
title: "Derived Rule: {canonical['Rule']}"
source: "derived: synthesis over {', '.join(evidence)}"
tags: [derived-rule, promoted-memory, reflection, icm]
---

# Derived Rule — {canonical['Rule']}

Promoted accepted rule from reflection candidates ({jl.name}).

## Rule
{canonical['Rule']}

## Evidence
{', '.join(f'`{e}`' for e in evidence)}

## Target
{canonical['Target']}

## Action
{canonical['Action']}
"""
    _atomic_write(chunk_file, chunk_content)
    return chunk_file


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate_id")
    parser.add_argument("--to", required=True, choices=sorted(VALID))
    parser.add_argument("--memory", help="write an accepted canonical rule to this file")
    parser.add_argument("--corpus", action="store_true", help="write an accepted canonical rule into a corpus chunk")
    args = parser.parse_args()

    jl, obj = find_candidate(args.candidate_id)
    if obj is None:
        print(f"FAIL: candidate {args.candidate_id} not found", file=sys.stderr)
        return 1

    src_state = obj.get("state")
    dst_state = args.to
    canonical: dict[str, str] | None = None
    if dst_state == "accepted":
        canonical, missing = _canonical_candidate(obj)
        if missing:
            print(
                f"FAIL: candidate {args.candidate_id} cannot be accepted: missing or forbidden "
                f"canonical field(s): {', '.join(missing)}; no fields were synthesized",
                file=sys.stderr,
            )
            return 1
    if src_state == dst_state:
        print(f"OK: already {dst_state}")
        return 0
    if (src_state, dst_state) not in TRANS:
        print(f"FAIL: illegal transition {src_state}→{dst_state} (allowed: {TRANS})", file=sys.stderr)
        return 1

    if dst_state == "accepted":
        assert canonical is not None
        candidate_id = str(obj.get("id") or obj.get("candidate_id") or args.candidate_id)
        if not _verified_lesson_link_exists(candidate_id):
            print(
                f"FAIL: candidate {candidate_id} requires a verified lesson link in "
                "knowledge/graph/sessions.db before acceptance",
                file=sys.stderr,
            )
            return 1
        if not _review_pair_exists(candidate_id):
            print(
                f"FAIL: candidate {candidate_id} requires a complete peer-review "
                "before→after pair in reflection/review_gate.jsonl before acceptance "
                "(log via scripts/review_gate.py --label "
                f"{candidate_id} --phase before/after with the live fingerprint)",
                file=sys.stderr,
            )
            return 1

    ids = existing_ids()
    if dst_state in ("experimental", "accepted"):
        if canonical is not None:
            evidence = _evidence_list(canonical["Evidence"])
            claim = canonical.get("Rule") or canonical["Action"]
        else:
            evidence = obj.get("evidence") or obj.get("evidence_ids") or []
            if isinstance(evidence, str):
                evidence = [evidence]
            evidence = [item for item in evidence if isinstance(item, str)]
            claim = obj.get("claim") or obj.get("principle") or obj.get("Rule") or ""
            if not evidence:
                evidence = re.findall(r"`([^`]+)`", str(obj.get("Evidence", "")))
            if not claim:
                claim = str(obj.get("Action", ""))
        if not evidence:
            print(f"FAIL: candidate {args.candidate_id} has no evidence ids", file=sys.stderr)
            return 1
        for evidence_id in evidence:
            if evidence_id not in ids:
                print(f"FAIL: evidence id `{evidence_id}` not in graph.db", file=sys.stderr)
                return 1

        import audit_candidate

        passed, issues = audit_candidate.audit_claim_grounding(str(claim), list(evidence))
        if not passed:
            print(f"FAIL: Auditor check failed: {issues}", file=sys.stderr)
            return 1

    _rewrite_candidate_state(jl, args.candidate_id, dst_state)
    print(f"OK: {args.candidate_id} {src_state}→{dst_state} in {jl.name}")

    if dst_state == "accepted" and args.memory:
        mem = ROOT / args.memory if not Path(args.memory).is_absolute() else Path(args.memory)
        assert canonical is not None
        try:
            _write_memory(mem, obj, canonical)
        except (OSError, ValueError) as exc:
            print(f"FAIL: {exc}", file=sys.stderr)
            return 1
        print(f"appended to {mem}")
        topic_seed = canonical["Rule"][:60].strip()
        if topic_seed:
            print(
                f"NOTE: seed reachability for '{topic_seed}' via "
                "reflection/reachability-seed.jsonl so check_reachability.py covers it"
            )

    # vera-expa-002/003 loop closure: every acceptance is followed by a held-out
    # post-promotion audit recorded in the memory_scores sidecar. A failing audit
    # does not roll back the acceptance — it decrements the rule score so the
    # eviction predicate (score < 0.4) can later evict it.
    if dst_state == "accepted":
        import subprocess
        audit_proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "post_promotion_audit.py"),
             str(obj.get("id") or obj.get("candidate_id") or args.candidate_id), "--record"],
            text=True, capture_output=True,
        )
        sys.stderr.write(audit_proc.stderr)
        for line in audit_proc.stdout.splitlines():
            print(f"  [audit] {line}")
        if audit_proc.returncode == 1:
            import memory_scores
            entry = memory_scores.load_scores().get(str(obj.get("id") or obj.get("candidate_id") or args.candidate_id), {})
            print(
                f"WARNING: post-promotion audit failed for {args.candidate_id} "
                f"(score now {entry.get('score', '?')}); eviction predicate fires at "
                f"{memory_scores.EVICT_THRESHOLD}",
                file=sys.stderr,
            )

    if dst_state == "accepted" and args.corpus:
        assert canonical is not None
        chunk_file = _write_corpus(obj, jl, canonical)
        print(f"OK: wrote canonical rule into corpus chunk {chunk_file.relative_to(ROOT)}")
        print("Run `python knowledge/graph/build_graph.py` and `python scripts/check_manifest.py --write` to rebuild.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
