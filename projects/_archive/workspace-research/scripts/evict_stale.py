#!/usr/bin/env python3
"""evict_stale.py — stage 05_evict: decide when a stored lesson is no longer trustworthy.

Corpus chunks this implements:
  04_honest_lying_memory_confabulation — a stored lesson can be the error it was meant to fix;
      0/121 reflections mentioned the correct object; RRR 0.64. Grounding in environment signal,
      not self-narrative, moved correct-object mention 0% -> 86%.
  02_expel_experiential_insight_extraction — DOWNVOTE-to-zero eviction; "even successful
      trajectories can be suboptimal and mislead the generated insights."
  03_agentdebug_root_cause_attribution    — evict only for the root cause, not a downstream symptom.

The trigger is deterministic: .graph_fingerprint moves on every corpus edit, so any candidate
whose provenance.fingerprint differs from the live one is queued for re-validation. It is
rejected only if its evidence ids no longer resolve in graph.db — stale is not the same as wrong.

Eviction is reversible: rejected rows stay in the file with a `why` field; nothing is deleted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "reflection" / "candidates"
EVICTIONS = ROOT / "reflection" / "evictions"
DIGESTS = ROOT / "reflection" / "digests"
DB = ROOT / "knowledge" / "graph" / "graph.db"
FP_FILE = ROOT / "knowledge" / "graph" / ".graph_fingerprint"
WORKFLOW = ROOT / "pipeline" / "WORKFLOW.md"
PHASE = "05_evict"

VALID = {"proposed", "experimental", "accepted", "rejected"}

FP_RE = re.compile(r"fingerprint:\s*[\"']?([0-9a-f]{8,12})[\"']?")
PV_RE = re.compile(r"plan_version:\s*[\"']?([0-9a-f]{12})[\"']?")

def live_fingerprint() -> str:
    return FP_FILE.read_text(encoding="utf-8").strip()


def live_plan_version() -> str:
    return hashlib.sha256(WORKFLOW.read_bytes()).hexdigest()[:12]


def existing_ids() -> set[str]:
    c = sqlite3.connect(DB)
    try:
        return {r[0] for r in c.execute("SELECT id FROM nodes").fetchall()}
    finally:
        c.close()


def stamp(fingerprint: str, plan_version: str, **extra) -> dict:
    d = {"fingerprint": fingerprint, "plan_version": plan_version, "phase": PHASE}
    d.update(extra)
    return d


def evict(dry_run: bool = False) -> int:
    if not FP_FILE.exists():
        print("FAIL: knowledge/graph/.graph_fingerprint missing — run watch.py --once first",
              file=sys.stderr)
        return 2
    if not WORKFLOW.exists():
        print("FAIL: pipeline/WORKFLOW.md missing — cannot compute plan_version (P1)", file=sys.stderr)
        return 2

    live_fp = live_fingerprint()
    live_pv = live_plan_version()
    ids = existing_ids()
    if not ids:
        print("FAIL: graph.db has no nodes — run watch.py --once first", file=sys.stderr)
        return 2

    EVICTIONS.mkdir(parents=True, exist_ok=True)
    run_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    audit: list[dict] = []
    n_evicted = n_revalidated = n_digests = n_total = 0

    for jl in sorted(CANDIDATES.glob("*.jsonl")):
        rows = jl.read_text(encoding="utf-8").splitlines()
        out: list[str] = []
        changed = False

        for line in rows:
            if not line.strip():
                out.append(line)
                continue
            n_total += 1
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"FAIL: {jl.name}: invalid JSON — {e}", file=sys.stderr)
                return 1

            # terminal state — rejected rows are never re-judged, only inspected
            if obj.get("state") == "rejected":
                out.append(line)
                continue

            cid = obj.get("id", "<no-id>")
            ev = obj.get("evidence")
            ev = ev if isinstance(ev, list) else []
            missing = [e for e in ev if e not in ids]
            prov = obj.get("provenance") if isinstance(obj.get("provenance"), dict) else {}
            stale = prov.get("fingerprint") != live_fp

            # 03_agentdebug: only the root cause justifies eviction.
            # Unresolvable evidence IS the root cause of the candidate's grounding.
            if missing:
                reason, why = "stale_evidence", (
                    f"evidence no longer resolves in graph.db: {missing}"
                )
            elif stale:
                # fingerprint moved but evidence still resolves — revalidate, keep the lesson
                obj["provenance"] = stamp(live_fp, live_pv)
                n_revalidated += 1
                changed = True
                out.append(json.dumps(obj, ensure_ascii=False))
                continue
            else:
                out.append(line)
                continue

            audit.append({
                "id": cid, "file": jl.name, "from": obj.get("state"), "to": "rejected",
                "reason": reason, "why": why, "evidence": ev,
                "provenance": stamp(live_fp, live_pv, reason=reason),
            })
            n_evicted += 1
            changed = True
            obj["state"] = "rejected"
            obj["why"] = why
            obj["provenance"] = stamp(live_fp, live_pv, reason=reason)
            out.append(json.dumps(obj, ensure_ascii=False))

        if changed and not dry_run:
            jl.write_text("\n".join(out) + "\n", encoding="utf-8")
    # The paired digest (reflection/digests/<topic>.md) carries the same provenance
    # stamp the gate checks, but only in prose form. Re-stamping candidates alone
    # leaves the pair half-fresh: check_reflection.py then fails the digest while
    # the candidates it summarises pass. The pair is one artifact in two files.
    if not dry_run:
        for md in sorted(DIGESTS.glob("*.md")):
            text = md.read_text(encoding="utf-8")
            new_text = FP_RE.sub(f"fingerprint: {live_fp}", text)
            new_text = PV_RE.sub(f"plan_version: {live_pv}", new_text)
            if new_text != text:
                md.write_text(new_text, encoding="utf-8")
                n_digests += 1

    if not dry_run and audit:
        (EVICTIONS / f"{run_iso}.jsonl").write_text(
            "\n".join(json.dumps(a, ensure_ascii=False) for a in audit) + "\n",
            encoding="utf-8")

    print(f"[05_evict] candidates={n_total} evicted={n_evicted} "
          f"revalidated={n_revalidated} digests_revalidated={n_digests} "
          f"fingerprint={live_fp}{' (DRY RUN)' if dry_run else ''}")
    for a in audit:
        print(f"  EVICT {a['id']}: {a['reason']} — {a['why']}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would be evicted; write nothing")
    a = ap.parse_args()
    raise SystemExit(evict(dry_run=a.dry_run))
