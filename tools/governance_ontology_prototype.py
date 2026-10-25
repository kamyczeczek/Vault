#!/usr/bin/env python3
import sqlite3
import os
import sys

DB_PATH = "tools/out/governance-ontology.db"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE entities (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        description TEXT,
        source_file TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE relations (
        source_id TEXT NOT NULL,
        target_id TEXT NOT NULL,
        predicate TEXT NOT NULL,
        source_file TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE aliases (
        entity_id TEXT NOT NULL,
        alias TEXT NOT NULL
    );
    """)

    # Insert entities (3 rules + supporting entities)
    entities = [
        ("POLICY:R1", "R1 shape", "POLICY", "root contains exactly allowed entries", "check_workspace_integrity.py"),
        ("POLICY:R13", "R13 citation", "POLICY", "citation verification across docs and reports", "check_workspace_integrity.py"),
        ("POLICY:R14", "R14 memory", "POLICY", "session-memory index freshness lag limit 24h", "check_workspace_integrity.py"),
        ("POLICY:R16", "R16 usage", "POLICY", "scripts/ modification requires query trace", "check_workspace_integrity.py"),
        ("SCRIPT:check_workspace_integrity", "check_workspace_integrity.py", "SCRIPT", "Workspace integrity gate runner", "check_workspace_integrity.py"),
        ("DOCUMENT:root", "root directory", "DOCUMENT", "workspace root entries", "check_workspace_integrity.py"),
        ("DOCUMENT:docs_reviews", "docs/reviews/", "DOCUMENT", "review reports directory", "docs/reviews/"),
        ("DOCUMENT:memory_index", "scripts/memory/CONTEXT.md", "DOCUMENT", "session-memory index", "scripts/memory/CONTEXT.md"),
        ("DOCUMENT:queries_jsonl", "scripts/_scratch/sessions/05_store/queries.jsonl", "DOCUMENT", "session memory queries trace log", "scripts/_scratch/sessions/05_store/queries.jsonl"),
        ("FILE_PATH:scripts_wildcard", "scripts/**", "DOCUMENT", "scripts, hooks, skills path pattern", "scripts/"),
        ("ROLE:agent", "coding agent", "ROLE", "workspace agent owner", "AGENTS.md"),
        ("PROCESS:commit", "git commit", "PROCESS", "git commit process", "hooks/pre-commit")
    ]
    cursor.executemany("INSERT INTO entities VALUES (?, ?, ?, ?, ?)", entities)

    # Insert relations
    relations = [
        ("POLICY:R1", "DOCUMENT:root", "requires", "check_workspace_integrity.py"),
        ("POLICY:R13", "DOCUMENT:docs_reviews", "requires", "check_workspace_integrity.py"),
        ("POLICY:R14", "DOCUMENT:memory_index", "requires", "check_workspace_integrity.py"),
        ("POLICY:R16", "DOCUMENT:queries_jsonl", "requires", "check_workspace_integrity.py"),
        ("POLICY:R16", "PROCESS:commit", "blocks", "check_workspace_integrity.py"),
        ("FILE_PATH:scripts_wildcard", "POLICY:R16", "cascade_to", "scripts/"),
        ("FILE_PATH:scripts_wildcard", "POLICY:R14", "cascade_to", "scripts/"),
        ("POLICY:R16", "ROLE:agent", "owned_by", "AGENTS.md"),
        ("POLICY:R14", "ROLE:agent", "owned_by", "AGENTS.md"),
        ("SCRIPT:check_workspace_integrity", "POLICY:R14", "requires", "check_workspace_integrity.py"),
        ("SCRIPT:check_workspace_integrity", "POLICY:R16", "requires", "check_workspace_integrity.py")
    ]
    cursor.executemany("INSERT INTO relations VALUES (?, ?, ?, ?)", relations)

    conn.commit()
    conn.close()

def run_p1_query():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = """
    SELECT
        r_policy.name AS rule,
        s.name AS command_or_script,
        target.name AS target_file,
        owner.name AS owner
    FROM relations rel_trigger
    JOIN entities trigger_ent ON rel_trigger.source_id = trigger_ent.id
    JOIN relations rel_policy ON trigger_ent.id = rel_policy.source_id OR rel_trigger.target_id = rel_policy.source_id
    JOIN entities r_policy ON rel_policy.target_id = r_policy.id AND r_policy.type = 'POLICY'
    LEFT JOIN relations rel_target ON r_policy.id = rel_target.source_id AND rel_target.predicate = 'requires'
    LEFT JOIN entities target ON rel_target.target_id = target.id
    LEFT JOIN relations rel_owner ON r_policy.id = rel_owner.source_id AND rel_owner.predicate = 'owned_by'
    LEFT JOIN entities owner ON rel_owner.target_id = owner.id
    LEFT JOIN entities s ON s.id = 'SCRIPT:check_workspace_integrity'
    WHERE trigger_ent.id = 'FILE_PATH:scripts_wildcard'
      AND rel_policy.predicate = 'cascade_to'
    GROUP BY r_policy.id, target.id
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

def main():
    init_db()
    results = run_p1_query()

    print("=== P1 Query Output: What blocks commit when changing scripts/**? ===")
    print(f"{'Rule':<15} | {'Command / Script':<30} | {'Target File / Doc':<35} | {'Owner':<12}")
    print("-" * 100)
    for row in results:
        rule, cmd, target, owner = row
        print(f"{rule:<15} | {cmd:<30} | {target:<35} | {owner or 'N/A':<12}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        init_db()
        results = run_p1_query()
        output_str = str(results)
        has_r14 = any("R14" in str(r) for r in results)
        has_queries = any("queries.jsonl" in str(r) for r in results)

        print("Selftest execution results:")
        for r in results:
            print("  ", r)

        if has_r14 and has_queries:
            print("SELFTEST PASS")
            sys.exit(0)
        else:
            print("SELFTEST FAIL: Expected R14 and queries.jsonl in query output")
            sys.exit(1)
    else:
        main()
