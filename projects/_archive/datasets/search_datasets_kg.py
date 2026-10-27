import sqlite3

db_path = r'.\.brain\graph\graph.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

topics = ["dataset", "benchmark", "data", "monash", "archive", "m4", "fev", "etth", "electricity"]

for t in topics:
    cursor.execute("SELECT title, content FROM nodes WHERE content LIKE ? LIMIT 2", (f"%{t}%",))
    rows = cursor.fetchall()
    print(f"\n--- Query: {t.upper()} ---")
    for title, content in rows:
        idx = content.lower().find(t)
        start = max(0, idx - 80)
        end = min(len(content), idx + 300)
        snippet = content[start:end].replace('\n', ' ')
        print(f"  [{title}]")
        print(f"    ...{snippet}...")

conn.close()
