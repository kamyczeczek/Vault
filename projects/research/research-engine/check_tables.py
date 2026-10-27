import sqlite3
db_path = "../agentic-research-lab/knowledge/graph/graph.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", cursor.fetchall())
conn.close()
