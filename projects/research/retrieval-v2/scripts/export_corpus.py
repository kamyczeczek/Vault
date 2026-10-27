"""Export graph.db nodes into a markdown corpus directory for attune-rag."""
import sqlite3
from pathlib import Path

DB_PATH = Path("projects/_archive/agentic-research-lab/knowledge/graph/graph.db")
OUT_DIR = Path("projects/research/retrieval-v2/corpus")
OUT_DIR.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(f"file:{DB_PATH.resolve()}?mode=ro", uri=True)
conn.row_factory = sqlite3.Row
try:
    rows = conn.execute("SELECT id, title, body FROM nodes").fetchall()
    print(f"Exporting {len(rows)} nodes from graph.db to {OUT_DIR}")
    for row in rows:
        nid = row["id"]
        title = row["title"] or ""
        body = row["body"] or ""
        content = f"# {title}\n\n{body}\n"
        (OUT_DIR / f"{nid}.md").write_text(content, encoding="utf-8")
    print("Export complete.")
finally:
    conn.close()
