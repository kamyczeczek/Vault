"""Scarred-from edge generation and reflection-classification utilities.

Builds SCARRED_FROM edges from reflection candidates into graph.db, and provides
helpers for hard-gate / soft-guidance classification and lattice-based
consolidation of overlapping reflections.

Design rationale (from Liu 2607.11226, Rule of Scars):
  - Scars are compiled from failure traces; they are not just "lessons learned"
    but *negative-space constraints* that block entire classes of bad actions.
  - Hard gates (non-negotiable) vs soft guidance (preferential heuristics) get
    different retrieval/application weights downstream.
  - Lattice GLB consolidation merges overlapping scars into the most general
    subsuming constraint, keeping the library sublinear.
  - Hash-chain signing gives tamper-evident provenance without crypto deps.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CANDIDATES = ROOT / "reflection" / "candidates"
DIGESTS = ROOT / "reflection" / "digests"
MEMORY = ROOT / "reflection" / "memory.md"

# Deterministic classification keywords — a candidate whose Rule+Action contain
# any of these is treated as a HARD GATE (non-negotiable, blocks actions outright).
HARD_GATE_PATTERNS = [
    r"\bblock\b", r"\bprevent\b", r"\bmust not\b", r"\bmust\s+enforce\b",
    r"\bnever\b", r"\bdemoted\b", r"\bcannot\b", r"\bforbidden\b",
    r"\bprohibit\b", r"\bgate\b", r"\bhardening\b", r"\bsandboxing\b",
    r"\bisolation\b", r"\bvalidation\b", r"\bverification\b",
    r"\bfail\s+loud\b", r"\binvariant\b", r"\bcircular\b",
    r"\bgaming\b", r"\bconfabulation\b", r"\bdegradation\b",
]
SOFT_GUIDANCE_PATTERNS = [
    r"\boptimal\b", r"\bprefer\b", r"\brecommend\b", r"\bshould\b",
    r"\bhelpful\b", r"\befficient\b", r"\bbest\s+practice\b",
    r"\begregious\b", r"\bimprove\b", r"\bsuggest\b",
]


# ---------------------------------------------------------------------------
# Classification helpers
# ---------------------------------------------------------------------------

def classify_candidate(rule: str, action: str) -> tuple[str, float]:
    """Return (strength, type) where type is 'hard-gate' or 'soft-guidance'.

    A candidate is a hard gate if its combined text matches >= 2 HARD patterns
    OR contains an explicit 'must not' / 'never' / 'prohibit'. Soft guidance
    matches >= 1 SOFT pattern. Otherwise it falls through to 'neutral'.
    """
    combined = (rule + " " + action).lower()
    hard_hits = sum(1 for p in HARD_GATE_PATTERNS if re.search(p, combined))
    soft_hits = sum(1 for p in SOFT_GUIDANCE_PATTERNS if re.search(p, combined))

    if hard_hits >= 2 or re.search(r'\bmust not\b|\bnever\b|\bprohibit\b', combined):
        strength = min(1.0, 0.5 + hard_hits * 0.1)
        return ("hard-gate", round(strength, 2))
    if soft_hits >= 1:
        strength = min(1.0, 0.3 + soft_hits * 0.1)
        return ("soft-guidance", round(strength, 2))
    return ("neutral", 0.5)


def extract_failure_mode(rule: str, action: str, candidate_id: str) -> str:
    """Derive a concise failure-mode label from the candidate text."""
    combined = (rule + " " + action)
    for keyword in ["prevent", "block", "avoid", "stop", "halt", "refuse",
                    "no ungrounded", "not reduce", "never"]:
        m = re.search(r'([^.]*\b' + keyword + r'\b[^.]+\.?)', combined, re.I)
        if m:
            snippet = m.group(1).strip()
            if len(snippet) > 20:
                return snippet[:120]
    return f"failure_mode_from_{candidate_id}"


# ---------------------------------------------------------------------------
# Lattice consolidation (greedy pairwise GLB join)
# ---------------------------------------------------------------------------

def _overlap_score(a: dict, b: dict) -> float:
    """Heuristic overlap between two reflection dicts (0..1).

    Scores based on shared evidence chunks and similar Rule/Action text.
    """
    ev_a = set(re.findall(r"`(\w[\w\-]*)`", a.get("Evidence", "") + " " + a.get("action", "")))
    ev_b = set(re.findall(r"`(\w[\w\-]*)`", b.get("Evidence", "") + " " + b.get("action", "")))
    evidence_overlap = len(ev_a & ev_b) / max(1, len(ev_a | ev_b))

    rule_a = a.get("Rule", "").lower()
    rule_b = b.get("Rule", "").lower()
    words_a = set(rule_a.split())
    words_b = set(rule_b.split())
    rule_overlap = len(words_a & words_b) / max(1, len(words_a | words_b))

    return round(0.6 * evidence_overlap + 0.4 * rule_overlap, 3)


def consolidate_lattice(candidates: list[dict]) -> list[dict]:
    """Merge highly-overlapping candidates into a single representative.

    Returns a list where overlapping candidates (>0.7 overlap) are replaced by
    a combined entry. Non-overlapping entries pass through unchanged.
    """
    THRESHOLD = 0.7
    if len(candidates) < 2:
        return candidates

    sorted_cands = sorted(candidates, key=lambda c: c.get("id", c.get("source", "")))
    kept: list[dict] = []

    for cand in sorted_cands:
        merged = False
        for i, existing in enumerate(kept):
            score = _overlap_score(cand, existing)
            if score >= THRESHOLD:
                ev_existing = set(re.findall(r"`(\w[\w\-]*)`", existing.get("Evidence", "")))
                ev_new = set(re.findall(r"`(\w[\w\-]*)`", cand.get("Evidence", "")))
                merged_ev = sorted(ev_existing | ev_new)
                existing["Evidence"] = ", ".join(f"`{e}`" for e in merged_ev)
                if len(cand.get("Rule", "")) > len(existing.get("Rule", "")):
                    existing["Rule"] = cand.get("Rule", "")
                existing.setdefault("_merge_count", 1)
                existing["_merge_count"] += 1
                existing.setdefault("_merged_from", [])
                existing["_merged_from"].append(cand.get("id", cand.get("source", "unknown")))
                merged = True
                break
        if not merged:
            kept.append(dict(cand))

    return kept


# ---------------------------------------------------------------------------
# Hash-chain signing (tamper-evident, no crypto deps)
# ---------------------------------------------------------------------------

def _hash_prev(prev_hash: str, entry: dict) -> str:
    """Compute the next link in the hash chain."""
    payload = prev_hash + json.dumps(entry, sort_keys=True, ensure_ascii=False)
    h = hashlib.sha256(payload.encode()).hexdigest()[:16]
    return h


def sign_memory_chunk(content: str, prev_hash: str = "genesis") -> tuple[str, str]:
    """Append a hash-chain footer to memory.md content.

    Returns (signed_content, chain_hash) where chain_hash is the final link.
    """
    lines = content.splitlines()
    last_hash = prev_hash

    for line in lines:
        if line.startswith("### ") and "— accepted" in line:
            last_hash = _hash_prev(last_hash, {"type": "section_accepted", "hash": last_hash})
        elif line.startswith("### ") and "— proposed" in line:
            last_hash = _hash_prev(last_hash, {"type": "section_proposed", "hash": last_hash})

    chain_footer = f"\n<!-- chain-hash: {last_hash} -->\n"
    signed_content = "".join(lines) + chain_footer
    return signed_content, last_hash


def verify_memory_chain(content: str) -> tuple[bool, str]:
    """Verify the hash chain in memory.md content. Returns (is_valid, final_hash)."""
    footer_match = re.search(r"<!-- chain-hash:\s+([a-f0-9]{16}) -->", content)
    if not footer_match:
        return False, "no chain footer found"
    expected = footer_match.group(1)
    _, computed = sign_memory_chunk(content, "genesis")
    return computed == expected, computed


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_accepted_lessons() -> list[dict]:
    """Load all accepted lessons from memory.md as structured dicts."""
    if not MEMORY.exists():
        return []
    text = MEMORY.read_text(encoding="utf-8")
    lessons = []
    for block in re.split(r"\n(?=###\s+)", text):
        header = block.strip().splitlines()[0] if block.strip() else ""
        if not re.match(r"###\s+.+\s+—\s+accepted\s*$", header, re.I):
            continue
        id_match = re.match(r"###\s+(\S+)\s+—\s+accepted", header)
        if not id_match:
            continue
        lesson_id = id_match.group(1)
        rule_m = re.search(r"^Rule:\s*(.+)$", block, re.MULTILINE)
        evidence_m = re.search(r"^Evidence:\s*(.+)$", block, re.MULTILINE)
        target_m = re.search(r"^Target:\s*(.+)$", block, re.MULTILINE)
        action_m = re.search(r"^Action:\s*(.+)$", block, re.MULTILINE)
        bet_m = re.search(r"^Bet:\s*(.+)$", block, re.MULTILINE)
        lessons.append({
            "id": lesson_id,
            "Rule": rule_m.group(1).strip() if rule_m else "",
            "Evidence": evidence_m.group(1).strip() if evidence_m else "",
            "Target": target_m.group(1).strip() if target_m else "",
            "Action": action_m.group(1).strip() if action_m else "",
            "bet": bet_m.group(1).strip() if bet_m else "",
        })
    return lessons


def run_consolidation(candidates_dir: Path = CANDIDATES) -> int:
    """Run lattice consolidation on all candidate files. Returns count merged."""
    if not candidates_dir.exists():
        return 0
    all_cands: list[dict] = []
    for p in sorted(candidates_dir.glob("*.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    all_cands.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    before = len(all_cands)
    merged = consolidate_lattice(all_cands)
    after = len(merged)
    if before > after:
        print(f"[scars] Lattice consolidation: {before} candidates -> {after} (merged {before - after})")
    return before - after


def add_chain_signing(memory_path: Path = MEMORY) -> None:
    """Add hash-chain signing to memory.md in-place. Idempotent."""
    if not memory_path.exists():
        return
    text = memory_path.read_text(encoding="utf-8")
    if "<!-- chain-hash:" in text:
        return
    signed, final_hash = sign_memory_chunk(text)
    memory_path.write_text(signed, encoding="utf-8")
    print(f"[scars] Signed memory.md with chain-hash: {final_hash}")


def classify_all() -> None:
    """Print classification for every candidate."""
    if not CANDIDATES.exists():
        print("[scars] No candidates dir found")
        return
    for p in sorted(CANDIDATES.glob("*.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            rule = obj.get("Rule", "")
            action = obj.get("Action", "")
            strength, ctype = classify_candidate(rule, action)
            print(f"{p.stem}: state={obj.get('state','')} type={ctype} strength={strength} id={obj.get('id','?')}")


def print_edges(nodes_ids: set[str]) -> None:
    """Print SCARRED_FROM edges as JSON."""
    import sqlite3
    edges = []
    conn = sqlite3.connect(ROOT / "knowledge" / "graph" / "graph.db")
    existing_kinds = {r[0] for r in conn.execute("SELECT DISTINCT kind FROM edges").fetchall()}
    conn.close()
    if "SCARRED_FROM" not in existing_kinds:
        print("[scars] No SCARRED_FROM edges in graph.db yet — run build_graph.py first")
        return
    conn = sqlite3.connect(ROOT / "knowledge" / "graph" / "graph.db")
    rows = conn.execute("SELECT src, dst, conf, tag FROM edges WHERE kind='SCARRED_FROM' ORDER BY conf DESC, src").fetchall()
    conn.close()
    for src, dst, conf, tag in rows:
        edges.append({"scar_id": src, "lesson_id": dst, "kind": "SCARRED_FROM",
                      "confidence": conf, "tag": tag})
    print(json.dumps(edges, indent=2))


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--classify", action="store_true", help="classify all candidates")
    ap.add_argument("--consolidate", action="store_true", help="run lattice consolidation")
    ap.add_argument("--sign-memory", action="store_true", help="add hash-chain to memory.md")
    ap.add_argument("--edges", action="store_true", help="print SCARRED_FROM edges as JSON")
    args = ap.parse_args()

    if args.classify:
        classify_all()
        return 0

    if args.edges:
        nodes_ids = set()
        try:
            import sqlite3
            conn = sqlite3.connect(ROOT / "knowledge" / "graph" / "graph.db")
            nodes_ids = {r[0] for r in conn.execute("SELECT id FROM nodes").fetchall()}
            conn.close()
        except Exception:
            pass
        print_edges(nodes_ids)
        return 0

    if args.consolidate:
        n = run_consolidation()
        print(f"[scars] Merged {n} overlapping candidates")
        return 0

    if args.sign_memory:
        add_chain_signing()
        return 0

    # Default: run all
    n = run_consolidation()
    print(f"[scars] Consolidated {n} overlapping candidates")
    add_chain_signing()
    if args.edges:
        print_edges(set())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
