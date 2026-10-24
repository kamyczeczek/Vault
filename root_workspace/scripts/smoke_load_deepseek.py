"""Smoke probe for the DSH loader (NOT a pytest test: no assertions).

Run: python scripts/smoke_load_deepseek.py
Prints how many deepseek sessions the tracked loader
`scripts/agent_sessions.py` can see.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from agent_sessions import load_deepseek_sessions, get_all_sessions

def main():
    print("Testing load_deepseek_sessions()...")
    sessions = load_deepseek_sessions(limit=10)
    print(f"Loaded {len(sessions)} deepseek sessions:")
    for s in sessions:
        print(f" - ID: {s.id}, Title: {s.title}, Messages: {s.message_count}, Raw: {s.raw_path}")

    print("\nTesting get_all_sessions(agent_filter='deepseek')...")
    all_ds = get_all_sessions(agent_filter="deepseek", limit_per_agent=10)
    print(f"Total get_all_sessions count: {len(all_ds)}")

if __name__ == "__main__":
    main()
