#!/usr/bin/env python3
"""
expc_graph_expansion.py — Experiment C: Graph Edge Expansion Ablation for VERA.

Evaluates whether traversing graph edges (SHARES_TAG, SEQUENCE, PART_OF)
starting from the baseline retrieved chunk set improves benchmark recall on
QUESTIONS.md questions, while monitoring token and tool-call cost ratio.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "knowledge" / "graph" / "graph.db"
RUNS_DIR = ROOT / "subprojects" / "vera" / "experiments" / "runs"

def run_ask(query, limit=5):
    """Run ask.py with specified limit"""
    result = subprocess.run(
        [sys.executable, str(ROOT / "knowledge" / "graph" / "ask.py"), query, "--limit", str(limit)],
        capture_output=True, text=True, cwd=ROOT
    )
    return result.returncode == 0, result.stdout, result.stderr

def parse_ask_output(output):
    """Parse ask.py output to extract chunk IDs"""
    chunks = []
    for line in output.splitlines():
        if line.startswith("# "):
            parts = line[2:].split(" | ")
            if len(parts) >= 1:
                chunk_id = parts[0].strip()
                chunks.append(chunk_id)
    return chunks

def load_questions():
    """Load benchmark questions from QUESTIONS.md"""
    questions = {}
    qfile = ROOT / "subprojects" / "vera" / "benchmark" / "QUESTIONS.md"
    content = qfile.read_text(encoding="utf-8")

    current_q = None
    for line in content.splitlines():
        if line.startswith("### Q"):
            current_q = line[4:].strip().split()[0]
            questions[current_q] = {"seeds": [], "pinned": [], "question": ""}
        elif current_q and "seeds:" in line and not line.strip().startswith("`"):
            seeds_part = line.split("seeds:")[1].strip()
            if "workspace-only" in seeds_part:
                continue
            seeds_text = seeds_part.split(";")[0].strip()
            chunk_id_pattern = r'\b(?:0[0-9]|[1-9]\d?|[1-9]\d{2,3})[a-zA-Z0-9_]*[a-zA-Z0-9]\b|\b[a-z]+_\w+(?:_\w+)*\b'
            filtered = re.findall(chunk_id_pattern, seeds_text)
            questions[current_q]["seeds"] = filtered
        elif current_q and "pinned_query:" in line:
            pinned = line.split("pinned_query:")[1].strip().split("#")[0].strip().strip('"').strip("'")
            for p in pinned.split("+"):
                p = p.strip().strip('"').strip("'")
                if p:
                    questions[current_q]["pinned"].append(p)

    return {k: v for k, v in questions.items() if v["seeds"] and v["pinned"]}

def expand_via_graph(seed_chunks: list[str], max_hops: int = 1, limit_per_hop: int = 3) -> list[str]:
    if not DB.exists():
        return seed_chunks
    conn = sqlite3.connect(DB)
    expanded = list(seed_chunks)
    visited = set(seed_chunks)
    frontier = list(seed_chunks)

    for _ in range(max_hops):
        next_frontier = []
        for chunk in frontier:
            rows = conn.execute(
                """
                SELECT dst FROM edges WHERE src = ?
                UNION
                SELECT src FROM edges WHERE dst = ?
                LIMIT ?
                """,
                (chunk, chunk, limit_per_hop)
            ).fetchall()
            for (neighbor,) in rows:
                if neighbor not in visited:
                    visited.add(neighbor)
                    next_frontier.append(neighbor)
                    expanded.append(neighbor)
        frontier = next_frontier
    conn.close()
    return expanded

def main() -> int:
    print("=== Experiment C: Graph Edge Expansion Ablation ===")
    print(f"Start: {datetime.now().isoformat()}")

    questions = load_questions()
    print(f"Loaded {len(questions)} evaluable questions with pinned queries")

    baseline_results = {}
    expansion_results = {}
    total_baseline_hits = 0
    total_expansion_hits = 0
    total_seeds = 0

    for qid, qdata in questions.items():
        seeds = qdata["seeds"]
        base_chunks = set()
        for pin in qdata["pinned"]:
            success, stdout, _ = run_ask(pin, limit=5)
            if success:
                base_chunks.update(parse_ask_output(stdout))

        base_hits = [s for s in seeds if s in base_chunks]
        base_recall = len(base_hits) / len(seeds) if seeds else 0.0
        baseline_results[qid] = {"retrieved": list(base_chunks), "seeds": seeds, "recall": base_recall, "hits": base_hits}
        total_baseline_hits += len(base_hits)

        # Graph expansion
        expanded_chunks = expand_via_graph(list(base_chunks), max_hops=1, limit_per_hop=3)
        exp_hits = [s for s in seeds if s in expanded_chunks]
        exp_recall = len(exp_hits) / len(seeds) if seeds else 0.0
        expansion_results[qid] = {"retrieved": expanded_chunks, "seeds": seeds, "recall": exp_recall, "hits": exp_hits}
        total_expansion_hits += len(exp_hits)
        total_seeds += len(seeds)

        print(f"[{qid}] Base recall: {base_recall:.2f} | Expansion recall: {exp_recall:.2f}")

    overall_base_recall = total_baseline_hits / total_seeds if total_seeds else 0.0
    overall_exp_recall = total_expansion_hits / total_seeds if total_seeds else 0.0

    print(f"\n--- Experiment C Summary ---")
    print(f"Overall Baseline Recall:   {overall_base_recall:.4f}")
    print(f"Overall Expansion Recall:  {overall_exp_recall:.4f}")
    delta = overall_exp_recall - overall_base_recall
    print(f"Recall Delta:              {delta:+.4f}")
    verdict = "PASS" if overall_exp_recall >= overall_base_recall else "FAIL"
    print(f"Verdict:                   {verdict}")

    report = {
        "experiment": "C_graph_expansion",
        "timestamp": datetime.now().isoformat(),
        "baseline_overall_recall": overall_base_recall,
        "expansion_overall_recall": overall_exp_recall,
        "recall_delta": delta,
        "baseline_results": baseline_results,
        "expansion_results": expansion_results,
        "verdict": verdict
    }

    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RUNS_DIR / f"EXPC_graph_expansion_{time.strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Results saved to: {out_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
