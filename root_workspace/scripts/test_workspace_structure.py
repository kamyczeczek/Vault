#!/usr/bin/env python3
import os
import sys

REQUIRED_PATHS = [
    "AGENTS.md",
    "CLAUDE.md",
    "CONTEXT-MAP.md",
    "TASKS.md",
    "PLAN.md",
    "brain/brain.db",
    "brain/decisions",
    "brain/problems",
    "tools",
    "handoff",
    "handoff/flags",
    "HANDOFF.md",
    "projects/_archive",
    "scripts",
]

def main():
    missing = []
    for p in REQUIRED_PATHS:
        if not os.path.exists(p):
            missing.append(p)

    if missing:
        print(f"FAIL: Missing required ICM/workspace structures: {missing}")
        sys.exit(1)
    else:
        print("SUCCESS: All required ICM/workspace structures and contracts present.")
        sys.exit(0)

if __name__ == "__main__":
    main()
