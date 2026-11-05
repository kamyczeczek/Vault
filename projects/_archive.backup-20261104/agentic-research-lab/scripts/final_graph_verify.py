#!/usr/bin/env python3
"""Final verification of graph quality fixes."""
import sqlite3

c = sqlite3.connect('knowledge/graph/graph.db')

print("=== GRAPH QUALITY VERIFICATION ===")

# 1. Junk tags
junk_tags = ['1', '00a2b5', '111111', '4D8DFF', '4a4a50', '5c5c2e', '6E6A5E', '6b5b00', '7a7a3d', '999999', '9A9585', '9BE7C4', '206', '409']
placeholders = ','.join(['?'] * len(junk_tags))
rows = c.execute(f'SELECT COUNT(*) FROM nodes, json_each(nodes.tags) WHERE json_each.value IN ({placeholders})', junk_tags).fetchall()
junk_count = rows[0][0]
print(f"1. Junk tags in nodes: {junk_count} {'PASS' if junk_count == 0 else 'FAIL'}")

# 2. Node types
types = c.execute('SELECT node_type, COUNT(*) FROM nodes GROUP BY node_type').fetchall()
has_type_col = len(types) > 0 and all(t[0] == 'corpus' for t in types)
print(f"2. Node type column: {types} {'PASS' if has_type_col else 'FAIL'}")

# 3. Edge kinds
kinds = c.execute('SELECT kind, COUNT(*) FROM edges GROUP BY kind').fetchall()
kind_set = {k[0] for k in kinds}
expected_kinds = {'SHARES_TAG', 'PART_OF', 'SEQUENCE', 'PROMOTED_TO'}
has_all_kinds = expected_kinds.issubset(kind_set)
print(f"3. Edge kinds: {dict(kinds)} {'PASS' if has_all_kinds else 'FAIL'}")

# 4. Confidence variation
confs = c.execute('SELECT conf, COUNT(*) FROM edges WHERE kind="SHARES_TAG" GROUP BY conf').fetchall()
conf_vals = [c[0] for c in confs]
has_variation = len(conf_vals) > 1
print(f"4. Confidence variation: {len(conf_vals)} distinct values {'PASS' if has_variation else 'FAIL'}")

# 5. Degree stats
degrees = c.execute('''
    SELECT n.id, COUNT(e.dst) as degree FROM nodes n
    LEFT JOIN edges e ON n.id = e.src
    GROUP BY n.id ORDER BY degree DESC
''').fetchall()
deg_vals = [d[1] for d in degrees]
max_deg = max(deg_vals)
avg_deg = sum(deg_vals) / len(deg_vals)
high_deg = sum(1 for d in deg_vals if d > 500)
print(f"5. Max degree: {max_deg} (was 613) {'PASS' if max_deg < 500 else 'FAIL'}")
print(f"   Avg degree: {avg_deg:.1f} (was 299.0) {'PASS' if avg_deg < 200 else 'FAIL'}")
print(f"   Nodes > 500: {high_deg} (was 94) {'PASS' if high_deg == 0 else 'FAIL'}")

# 6. Truly isolated nodes
isolated = c.execute('''
    SELECT COUNT(*) FROM nodes n
    WHERE n.id NOT IN (SELECT src FROM edges UNION SELECT dst FROM edges)
''').fetchone()[0]
print(f"6. Truly isolated nodes: {isolated} {'PASS' if isolated == 0 else 'FAIL'}")

# 7. Total edges
total_edges = c.execute('SELECT COUNT(*) FROM edges').fetchone()[0]
print(f"7. Total edges: {total_edges} (was 182,078)")

# 8. Route.py compatibility test
try:
    import subprocess, sys
    result = subprocess.run(
        [sys.executable, 'pipeline/06_reflect/route.py', '--tag', 'icm', '--limit', '5'],
        capture_output=True, text=True, cwd='.'
    )
    route_ok = result.returncode == 0 and len(result.stdout.strip().splitlines()) > 0
    print(f"8. Route.py compatibility: {'PASS' if route_ok else 'FAIL'}")
except Exception as e:
    print(f"8. Route.py compatibility: FAIL ({e})")

c.close()
