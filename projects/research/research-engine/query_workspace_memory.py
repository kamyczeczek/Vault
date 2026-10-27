import sqlite3
db_path = "../agentic-research-lab/knowledge/graph/graph.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT title, path FROM nodes WHERE path LIKE '%ts_diverse%' OR path LIKE '%experiment%'")
print("Matching nodes:", cursor.fetchall())

cursor.execute("SELECT title, snippet(fts, 0, '[', ']', '...', 10) FROM fts WHERE fts MATCH 'BigDict OR amr_fbs OR sota'")
print("\nFTS Search results:")
for row in cursor.fetchall():
    print(f"- {row[0]}: {row[1]}")
conn.close()
