import sqlite3
import os

def init_db(db_path="brain/brain.db"):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lessons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        metadata TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS decisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS problems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        root_cause TEXT,
        fix TEXT,
        scar TEXT,
        gate TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS lessons_fts USING fts5(content, metadata, content='lessons', content_rowid='id');
    """)
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS lessons_ai AFTER INSERT ON lessons BEGIN
        INSERT INTO lessons_fts(rowid, content, metadata) VALUES (new.id, new.content, new.metadata);
    END;
    """)
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS lessons_ad AFTER DELETE ON lessons BEGIN
        INSERT INTO lessons_fts(lessons_fts, rowid, content, metadata) VALUES('delete', old.id, old.content, old.metadata);
    END;
    """)
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS lessons_au AFTER UPDATE ON lessons BEGIN
        INSERT INTO lessons_fts(lessons_fts, rowid, content, metadata) VALUES('delete', old.id, old.content, old.metadata);
        INSERT INTO lessons_fts(rowid, content, metadata) VALUES (new.id, new.content, new.metadata);
    END;
    """)

    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS decisions_fts USING fts5(title, content, content='decisions', content_rowid='id');
    """)
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS decisions_ai AFTER INSERT ON decisions BEGIN
        INSERT INTO decisions_fts(rowid, title, content) VALUES (new.id, new.title, new.content);
    END;
    """)
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS decisions_ad AFTER DELETE ON decisions BEGIN
        INSERT INTO decisions_fts(decisions_fts, rowid, title, content) VALUES('delete', old.id, old.title, old.content);
    END;
    """)
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS decisions_au AFTER UPDATE ON decisions BEGIN
        INSERT INTO decisions_fts(decisions_fts, rowid, title, content) VALUES('delete', old.id, old.title, old.content);
        INSERT INTO decisions_fts(rowid, title, content) VALUES (new.id, new.title, new.content);
    END;
    """)

    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS sessions_fts USING fts5(session_id, summary, content='sessions', content_rowid='id');
    """)
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS sessions_ai AFTER INSERT ON sessions BEGIN
        INSERT INTO sessions_fts(rowid, session_id, summary) VALUES (new.id, new.session_id, new.summary);
    END;
    """)
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS sessions_ad AFTER DELETE ON sessions BEGIN
        INSERT INTO sessions_fts(sessions_fts, rowid, session_id, summary) VALUES('delete', old.id, old.session_id, old.summary);
    END;
    """)
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS sessions_au AFTER UPDATE ON sessions BEGIN
        INSERT INTO sessions_fts(sessions_fts, rowid, session_id, summary) VALUES('delete', old.id, old.session_id, old.summary);
        INSERT INTO sessions_fts(rowid, session_id, summary) VALUES (new.id, new.session_id, new.summary);
    END;
    """)

    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS problems_fts USING fts5(title, root_cause, fix, scar, gate, status, content='problems', content_rowid='id');
    """)
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS problems_ai AFTER INSERT ON problems BEGIN
        INSERT INTO problems_fts(rowid, title, root_cause, fix, scar, gate, status) VALUES (new.id, new.title, new.root_cause, new.fix, new.scar, new.gate, new.status);
    END;
    """)
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS problems_ad AFTER DELETE ON problems BEGIN
        INSERT INTO problems_fts(problems_fts, rowid, title, root_cause, fix, scar, gate, status) VALUES('delete', old.id, old.title, old.root_cause, old.fix, old.scar, old.gate, old.status);
    END;
    """)
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS problems_au AFTER UPDATE ON problems BEGIN
        INSERT INTO problems_fts(problems_fts, rowid, title, root_cause, fix, scar, gate, status) VALUES('delete', old.id, old.title, old.root_cause, old.fix, old.scar, old.gate, old.status);
        INSERT INTO problems_fts(rowid, title, root_cause, fix, scar, gate, status) VALUES (new.id, new.title, new.root_cause, new.fix, new.scar, new.gate, new.status);
    END;
    """)

    conn.commit()
    conn.close()
    print(f"Database initialized successfully at {db_path}")

if __name__ == "__main__":
    init_db()
