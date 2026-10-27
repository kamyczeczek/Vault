#!/usr/bin/env python3
"""Phase 5 Active Eviction & Meta-Evolution Hardening Script.
Scans reflection candidates and memory ledger, identifying stale or ungrounded
heuristics (importance == 0 or failed promotion gates) and safely evicting them
to maintain reflection hygiene.
"""
import json
from pathlib import Path

def main():
    print("=== Phase 5 Active Eviction & Meta-Evolution Hardening ===")

    root = Path(__file__).resolve().parent
    candidates_dir = root.parent / "agentic-research-lab" / "reflection" / "candidates"

    evicted_count = 0
    active_count = 0

    if candidates_dir.exists():
        for jsonl_file in candidates_dir.glob("*.jsonl"):
            lines = jsonl_file.read_text(encoding="utf-8", errors="ignore").splitlines()
            valid_lines = []
            for line in lines:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    # Check importance or validation status
                    importance = record.get("importance", 1)
                    validated = record.get("validated", True)
                    if importance <= 0 or not validated:
                        evicted_count += 1
                        print(f"  [Evicting] Stale record in {jsonl_file.name}: {record.get('id', 'unknown')}")
                    else:
                        valid_lines.append(line)
                        active_count += 1
                except Exception:
                    valid_lines.append(line)
                    active_count += 1

            # Rewrite file with active lines only
            jsonl_file.write_text("\n".join(valid_lines) + ("\n" if valid_lines else ""), encoding="utf-8")
    else:
        print("  [Notice] Reflection candidates directory not found; skipping candidate file scan.")

    print(f"\n[Summary] Active reflection records: {active_count}, Evicted stale/ungrounded records: {evicted_count}")
    print("Phase 5 eviction hardening complete.")

if __name__ == "__main__":
    main()
