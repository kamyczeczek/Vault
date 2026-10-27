import sqlite3
db_path = "../agentic-research-lab/knowledge/graph/graph.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT title, path, body FROM nodes WHERE title LIKE '%reorientation%' OR title LIKE '%retrieval%' OR title LIKE '%compaction%' OR title LIKE '%memory%'")
for row in cursor.fetchall():
    print(f"=== {row[0]} ({row[1]}) ===\n{row[2][:800]}\n")
conn.close()
