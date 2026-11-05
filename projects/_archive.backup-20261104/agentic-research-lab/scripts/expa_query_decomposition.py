#!/usr/bin/env python3
"""
Experiment A: Query Decomposition Harness
Target: Beat 0.53 recall (B0.2 baseline) without 3× cost
"""
import json
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]

def run_ask(query, limit=8):
    """Run ask.py with specified limit"""
    result = subprocess.run(
        [sys.executable, str(ROOT / "knowledge" / "graph" / "ask.py"), query, "--limit", str(limit)],
        capture_output=True, text=True, cwd=ROOT
    )
    return result.returncode == 0, result.stdout, result.stderr

def run_context_gateway(query, mode="default"):
    """Run context_gateway.py for DB-1 integration"""
    result = subprocess.run(
        [sys.executable, str(ROOT / "knowledge" / "graph" / "context_gateway.py"), query, "--mode", mode],
        capture_output=True, text=True, cwd=ROOT
    )
    return result.returncode == 0, result.stdout, result.stderr

def run_context_gateway_direct(query, mode="default", limit=5):
    """Run context_gateway.py directly (import) for DB-1 integration"""
    sys.path.insert(0, str(ROOT / "knowledge" / "graph"))
    from context_gateway import context_packet
    result = context_packet(query, mode=mode, limit=limit)
    return result

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

def parse_context_gateway_output(result):
    """Parse context_gateway result to extract chunk IDs"""
    chunks = []
    for item in result.get("items", []):
        if item.get("kind") == "corpus":
            chunks.append(item.get("id"))
    return chunks

def load_questions():
    """Load benchmark questions from QUESTIONS.md"""
    questions = {}
    qfile = ROOT / "subprojects" / "vera" / "benchmark" / "QUESTIONS.md"
    content = qfile.read_text(encoding="utf-8")

    current_q = None
    current_question_text = None
    for line in content.splitlines():
        if line.startswith("### Q"):
            current_q = line[4:].strip().split()[0]
            questions[current_q] = {"seeds": [], "pinned": [], "question": ""}
        elif current_q and line.startswith("question:") and not current_question_text:
            current_question_text = line.split("question:")[1].strip().strip('"').strip("'")
            questions[current_q]["question"] = current_question_text
        elif current_q and "seeds:" in line and not line.strip().startswith("`"):
            # Parse seeds - extract chunk IDs using regex
            # Chunk IDs follow patterns like: 00_xxx, 01_xxx, bm25_xxx, 240_xxx, 335_xxx, 365_xxx, 452_xxx, 50_xxx, 10_xxx
            seeds_part = line.split("seeds:")[1].strip()
            # Split by ; and take first part (before workspace:)
            seeds_text = seeds_part.split(";")[0].strip()
            # Use regex to find all chunk IDs
            # Pattern: starts with 2-3 digits or lowercase word, followed by underscores and alphanumerics
            chunk_id_pattern = r'\b(?:0[0-9]|[1-9]\d?|[1-9]\d{2,3})[a-zA-Z0-9_]*[a-zA-Z0-9]\b|\b[a-z]+_\w+(?:_\w+)*\b'
            filtered = re.findall(chunk_id_pattern, seeds_text)
            questions[current_q]["seeds"] = filtered
        elif current_q and "pinned_query:" in line:
            pinned = line.split("pinned_query:")[1].strip().split("#")[0].strip().strip('"').strip("'")
            # Handle multi-query pins separated by +
            for p in pinned.split("+"):
                p = p.strip().strip('"').strip("'")
                if p:
                    questions[current_q]["pinned"].append(p)

    return questions

def run_baseline_retrieval(questions, limit=8):
    """Run baseline B0.2 retrieval (pinned queries via ask.py)"""
    all_results = {}
    total_tools = 0
    total_tokens_est = 0

    for qid, qdata in questions.items():
        if not qdata.get("pinned"):
            continue

        all_chunks = set()
        for pin in qdata["pinned"]:
            total_tools += 1
            success, stdout, _ = run_ask(pin, limit=limit)
            if success:
                chunks = parse_ask_output(stdout)
                all_chunks.update(chunks)
            total_tokens_est += len(pin) * 4 + len(stdout) * 1.5

        all_results[qid] = {
            "retrieved": list(all_chunks),
            "seeds": qdata["seeds"],
            "recall": 0.0
        }

        # Compute recall
        seeds = set(qdata["seeds"])
        if seeds:
            hits = seeds & set(all_chunks)
            all_results[qid]["recall"] = len(hits) / len(seeds)
            all_results[qid]["hits"] = list(hits)

    return all_results, total_tools, total_tokens_est

def run_decomposition_context_gateway(questions, mode="default", limit=5):
    """Run query decomposition using context_gateway (DB-1 integrated retrieval)"""
    all_results = {}
    total_tools = 0
    total_tokens_est = 0

    for qid, qdata in questions.items():
        if not qdata.get("pinned"):
            continue

        all_chunks = set()
        # Decomposition: use each pinned query as a sub-query
        for pin in qdata["pinned"]:
            total_tools += 1
            result = run_context_gateway_direct(pin, mode=mode, limit=limit)
            chunks = parse_context_gateway_output(result)
            all_chunks.update(chunks)
            total_tokens_est += result.get("estimated_tokens", 0)

        all_results[qid] = {
            "retrieved": list(all_chunks),
            "seeds": qdata["seeds"]
        }

    return all_results, total_tools, total_tokens_est

def compute_recall(results, questions):
    """Compute recall metrics"""
    total_recall = 0.0
    total_questions = 0

    for qid, result in results.items():
        if qid in questions:
            seeds = set(questions[qid]["seeds"])
            if seeds:
                retrieved = set(result.get("retrieved", []))
                hits = seeds & retrieved
                recall = len(hits) / len(seeds)
                total_recall += recall
                total_questions += 1
                result["recall"] = recall
                result["hits"] = list(hits)

    return total_recall / total_questions if total_questions > 0 else 0.0

def main():
    print("=== Experiment A: Query Decomposition ===")
    print(f"Target: Beat 0.53 recall without 3x cost")
    print(f"Start: {datetime.now().isoformat()}")

    questions = load_questions()
    print(f"Loaded {len(questions)} questions with pinned queries")

    # Run baseline (B0.2 pinned queries via ask.py)
    print("\n--- Running Baseline (B0.2 pinned via ask.py) ---")
    baseline_results, baseline_tools, baseline_tokens = run_baseline_retrieval(questions)
    baseline_recall = compute_recall(baseline_results, questions)
    print(f"Baseline recall: {baseline_recall:.4f}")
    print(f"Baseline tools: {baseline_tools}, tokens: {baseline_tokens}")

    # Run decomposition using context_gateway (DB-1 integrated retrieval)
    print("\n--- Running Query Decomposition (context_gateway DB-1) ---")
    decomp_results, decomp_tools, decomp_tokens = run_decomposition_context_gateway(questions, mode="default", limit=5)
    decomp_recall = compute_recall(decomp_results, questions)
    print(f"Decomposition recall: {decomp_recall:.4f}")
    print(f"Decomposition tools: {decomp_tools}, tokens: {decomp_tokens}")

    # Cost ratio
    cost_ratio = decomp_tokens / baseline_tokens if baseline_tokens > 0 else float('inf')
    print(f"Cost ratio: {cost_ratio:.2f}x")

    # Verdict
    print("\n=== VERDICT ===")
    print(f"Baseline recall: {baseline_recall:.4f}")
    print(f"Decomposition recall: {decomp_recall:.4f}")
    print(f"Improvement: {decomp_recall - baseline_recall:.4f}")
    print(f"Cost ratio: {cost_ratio:.2f}x")

    if decomp_recall > baseline_recall and cost_ratio < 3.0:
        print("PASS: Decomposition beats baseline recall within cost budget")
    elif decomp_recall > 0.53 and cost_ratio < 3.0:
        print("PASS: Decomposition beats 0.53 recall target within cost budget")
    else:
        print("FAIL: Does not meet criteria")

    # Save results
    runs_dir = ROOT / "subprojects" / "vera" / "experiments" / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "experiment": "A_query_decomposition",
        "timestamp": datetime.now().isoformat(),
        "baseline_recall": baseline_recall,
        "decomposition_recall": decomp_recall,
        "cost_ratio": cost_ratio,
        "baseline_tools": baseline_tools,
        "baseline_tokens": baseline_tokens,
        "decomposition_tools": decomp_tools,
        "decomposition_tokens": decomp_tokens,
        "baseline_results": baseline_results,
        "decomposition_results": decomp_results,
        "verdict": "PASS" if (decomp_recall > baseline_recall and cost_ratio < 3.0) or (decomp_recall > 0.53 and cost_ratio < 3.0) else "FAIL"
    }

    out_file = runs_dir / f"EXPA_query_decomp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_file.write_text(json.dumps(results, indent=2))
    print(f"\nResults saved to: {out_file}")

    return 0 if results["verdict"] == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main())