import sqlite3

db_path = "../agentic-research-lab/knowledge/graph/graph.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

query = "SELECT title, path, body FROM nodes WHERE body LIKE '%memory%' OR body LIKE '%persistence%' OR body LIKE '%re-orientation%' OR body LIKE '%eviction%' LIMIT 5"
for row in cursor.execute(query).fetchall():
    print(f"=== {row[0]} ({row[1]}) ===\n{row[2][:500]}...\n")

conn.close()
