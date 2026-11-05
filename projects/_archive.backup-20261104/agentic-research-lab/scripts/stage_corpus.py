#!/usr/bin/env python3
"""Stage all untracked knowledge/corpus/ files in batches."""
import subprocess, sys
from pathlib import Path

ROOT = Path('.')

result = subprocess.run(
    ['git', 'status', '--porcelain', '--untracked-files=normal'],
    cwd=ROOT, capture_output=True, text=True
)
if result.returncode:
    print(f"git status failed: {result.stderr}", file=sys.stderr)
    sys.exit(1)

new_files = []
for line in result.stdout.splitlines():
    if line.startswith('?? knowledge/corpus/'):
        fname = line[3:].strip()
        new_files.append(fname)

print(f'Found {len(new_files)} new untracked corpus files')

total = len(new_files)
staged = 0
failed = 0
for i, fname in enumerate(new_files):
    proc = subprocess.run(
        ['git', 'add', '--', fname],
        cwd=ROOT, capture_output=True, text=True
    )
    if proc.returncode == 0:
        staged += 1
    else:
        failed += 1
    if (i + 1) % 500 == 0:
        print(f'Staged {i+1}/{total}...')

print(f'Staged: {staged}/{total}, Failed: {failed}')
if failed:
    sys.exit(1)
