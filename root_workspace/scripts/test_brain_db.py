import sqlite3
import os
import sys
from init_brain_db import init_db

def test_brain_db():
    db_path = "brain/brain.db"
    init_db(db_path)
    if not os.path.exists(db_path):
        raise AssertionError(f"Database {db_path} does not exist.")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    tables = ["lessons", "decisions", "sessions", "problems"]
    for table in tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
        row = cursor.fetchone()
        if not row:
            raise AssertionError(f"Table {table} does not exist in {db_path}")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%fts%';")
    fts_rows = cursor.fetchall()
    print(f"Found tables/FTS: {fts_rows}")
    conn.close()
    print("ALL BRAIN DB TESTS PASSED")

if __name__ == "__main__":
    try:
        test_brain_db()
    except Exception as e:
        print(f"TEST FAILED: {e}", file=sys.stderr)
        sys.exit(1)
