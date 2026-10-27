#!/usr/bin/env python3
"""Analyze graph database and surface evidence-based improvements from reflection memory."""
import sqlite3
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "knowledge" / "graph" / "graph.db"
MEM = ROOT / "reflection" / "memory.md"
CAND = ROOT / "reflection" / "candidates"

def analyze_graph():
    c = sqlite3.connect(DB)

    # Basic stats
    nodes = c.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    edges = c.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    refers_to = c.execute("SELECT COUNT(*) FROM edges WHERE kind='REFERS_TO'").fetchone()[0]
    shares_tag = c.execute("SELECT COUNT(*) FROM edges WHERE kind='SHARES_TAG'").fetchone()[0]

    print("=== GRAPH STATS ===")
    print(f"Nodes: {nodes}")
    print(f"Edges: {edges}")
    print(f"  REFERS_TO: {refers_to}")
    print(f"  SHARES_TAG: {shares_tag}")

    # Junk tags
    junk = ['1','00a2b5','111111','4D8DFF','4a4a50','5c5c2e','6E6A5E','6b5b00','7a7a3d','999999','9A9585','9BE7C4','206','409']
    print("\n=== JUNK TAGS ===")
    for j in junk:
        count = c.execute('SELECT COUNT(*) FROM nodes WHERE tags LIKE ?', (f'%\"{j}\"%',)).fetchone()[0]
        if count > 0:
            print(f"  {j}: {count} nodes")

    # Degree stats
    degrees = c.execute('''
        SELECT n.id, COUNT(e.dst) as degree FROM nodes n
        LEFT JOIN edges e ON n.id = e.src
        GROUP BY n.id ORDER BY degree DESC
    ''').fetchall()
    deg_vals = [d[1] for d in degrees]
    print(f"\n=== DEGREE DISTRIBUTION ===")
    print(f"  Max: {max(deg_vals)}")
    print(f"  Min: {min(deg_vals)}")
    print(f"  Avg: {sum(deg_vals)/len(deg_vals):.1f}")
    print(f"  Nodes with degree > 500: {sum(1 for d in deg_vals if d > 500)}")
    print(f"  Nodes with degree < 10: {sum(1 for d in deg_vals if d < 10)}")
    print(f"  Isolated nodes: {sum(1 for d in deg_vals if d == 0)}")

    # Tag distribution
    tags = c.execute('SELECT tags FROM nodes').fetchall()
    tc = Counter()
    for t in tags:
        for tag in json.loads(t[0]):
            tc[tag] += 1
    print(f"\n=== TOP 10 TAGS ===")
    for tag, count in tc.most_common(10):
        print(f"  {tag}: {count}")

    # Edge confidence
    confs = c.execute('SELECT conf, COUNT(*) FROM edges GROUP BY conf').fetchall()
    print(f"\n=== EDGE CONFIDENCE ===")
    for conf, count in confs:
        print(f"  {conf}: {count}")

    c.close()

def scan_reflection_for_graph_rules():
    print("\n=== REFLECTION MEMORY: GRAPH/RETRIEVAL RULES ===")
    if not MEM.exists():
        print("  (no memory.md)")
        return
    mem_text = MEM.read_text()
    for line in mem_text.splitlines():
        if any(k in line.lower() for k in ['graph', 'edge', 'node', 'tag', 'route', 'refer', 'retrieval', 'deterministic']):
            print(f"  {line.strip()}")

    print("\n=== CANDIDATES: GRAPH/RETRIEVAL RULES ===")
    if not CAND.exists():
        print("  (no candidates/)")
        return
    for p in sorted(CAND.glob("*.jsonl")):
        for line in p.read_text().splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            text = json.dumps(obj).lower()
            if any(k in text for k in ['graph', 'edge', 'node', 'tag', 'route', 'refer', 'retrieval', 'deterministic']):
                rule = obj.get("Rule", obj.get("claim", obj.get("principle", "")))
                print(f"  [{p.stem}] {obj.get('id')}: {rule[:120]}")

if __name__ == "__main__":
    analyze_graph()
    scan_reflection_for_graph_rules()
