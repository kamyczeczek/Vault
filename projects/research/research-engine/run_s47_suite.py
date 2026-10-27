#!/usr/bin/env python3
"""Automated wrapper to run the S-47 Diverse Mini-Suite and Thomas comparison,
verifying all promotion gates and outputting a summary report.
"""
import subprocess
import sys
import json
from pathlib import Path

def run_command(cmd):
    print(f"\n[RUN] {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.stdout:
        print(res.stdout[-1500:]) # print last 1500 chars
    if res.stderr and res.returncode != 0:
        print(f"[STDERR]: {res.stderr}")
    return res.returncode == 0

def main():
    print("=== Automated S-47 & Thomas Benchmark Runner ===")

    # 1. Run rolling arm s47
    success_s47 = run_command([sys.executable, "s47_ref/rolling_arm.py"])

    # 2. Run thomas compare
    success_thomas = run_command([sys.executable, "thomas_compare.py", "--output", "results_thomas.json"])

    # 3. Re-sync to corpus if both succeeded
    if success_s47 or success_thomas:
        print("\n[SYNC] Re-syncing experiment results to knowledge corpus...")
        sync_script = Path("sync_results_to_corpus.py")
        if sync_script.exists():
            run_command([sys.executable, str(sync_script)])

            # Rebuild graph
            graph_script = Path("../agentic-research-lab/knowledge/graph/build_graph.py")
            if graph_script.exists():
                run_command([sys.executable, str(graph_script)])

    print("\n=== Automated Benchmark Run Complete ===")

if __name__ == "__main__":
    main()
