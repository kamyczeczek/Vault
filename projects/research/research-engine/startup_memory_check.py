#!/usr/bin/env python3
"""
Startup memory check script to prevent session amnesia and provide
instant re-orientation over recent experiments and knowledge graph state.
"""

import os
import json
import sqlite3

def check_memory():
    print("=== Agent Startup Memory Check ===")

    # 1. Check results files
    results_files = ['results_s47.json', 'results_thomas.json']
    for rf in results_files:
        if os.path.exists(rf):
            print(f"[FOUND] {rf} (mtime: {os.path.getmtime(rf)})")
            try:
                with open(rf, 'r') as f:
                    data = json.load(f)
                    if 'slice' in data:
                        print(f"  -> Slice: {data['slice']}")
                    if 'suite' in data:
                        print(f"  -> Suite: {data['suite']}")
            except Exception as e:
                print(f"  -> Error reading {rf}: {e}")
        else:
            print(f"[MISSING] {rf}")

    # 2. Check knowledge graph
    db_path = "../agentic-research-lab/knowledge/graph/graph.db"
    if os.path.exists(db_path):
        print(f"\n[FOUND] Knowledge Graph at {db_path}")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT title, path FROM nodes WHERE path LIKE '%ts_diverse%' OR path LIKE '%experiment%'")
            nodes = cursor.fetchall()
            print(f"  -> Matching KG nodes: {len(nodes)}")
            for title, path in nodes:
                print(f"     - {title} ({path})")
            conn.close()
        except Exception as e:
            print(f"  -> Error querying KG: {e}")
    else:
        print(f"\n[MISSING] Knowledge Graph not found at {db_path}")

    print("===============================================")

if __name__ == '__main__':
    check_memory()
