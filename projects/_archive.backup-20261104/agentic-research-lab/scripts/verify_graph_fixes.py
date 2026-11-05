#!/usr/bin/env python3
"""Verify graph quality fixes."""
import sqlite3
import json
from collections import Counter

c = sqlite3.connect('knowledge/graph/graph.db')

# 1. Junk tags
junk_tags = ['1', '00a2b5', '111111', '4D8DFF', '4a4a50', '5c5c2e', '6E6A5E', '6b5b00', '7a7a3d', '999999', '9A9585', '9BE7C4', '206', '409']
placeholders = ','.join(['?'] * len(junk_tags))
rows = c.execute(f'SELECT COUNT(*) FROM nodes, json_each(nodes.tags) WHERE json_each.value IN ({placeholders})', junk_tags).fetchall()
print(f'Junk tags remaining: {rows[0][0]} nodes')

# 2. Node types
types = c.execute('SELECT node_type, COUNT(*) FROM nodes GROUP BY node_type').fetchall()
print(f'Node types: {types}')

# 3. Edge kinds
kinds = c.execute('SELECT kind, COUNT(*) FROM edges GROUP BY kind').fetchall()
print(f'Edge kinds: {kinds}')

# 4. SHARES_TAG confidence distribution
confs = c.execute('SELECT conf, COUNT(*) FROM edges WHERE kind="SHARES_TAG" GROUP BY conf ORDER BY conf DESC LIMIT 10').fetchall()
print(f'Top 10 SHARES_TAG conf: {confs}')

# 5. Degree stats
degrees = c.execute('''
    SELECT n.id, COUNT(e.dst) as degree FROM nodes n
    LEFT JOIN edges e ON n.id = e.src
    GROUP BY n.id ORDER BY degree DESC
''').fetchall()
deg_vals = [d[1] for d in degrees]
print(f'Degree stats: max={max(deg_vals)}, min={min(deg_vals)}, avg={sum(deg_vals)/len(deg_vals):.1f}')
print(f'Nodes degree > 500: {sum(1 for d in deg_vals if d > 500)}')
print(f'Isolated nodes: {sum(1 for d in deg_vals if d == 0)}')

# 6. Top tags (should not include '1')
tags = c.execute('SELECT tags FROM nodes').fetchall()
tc = Counter()
for t in tags:
    for tag in json.loads(t[0]):
        tc[tag] += 1
print(f'Top tag: {tc.most_common(1)[0]}')

c.close()
