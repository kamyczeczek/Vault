#!/usr/bin/env python
"""Independent OMP capture/closure gate over the existing failure ledger.

Expected session MUST come from caller --session-id or OMP_CAPTURE_SESSION_ID,
never the receipt. JCODE_FAILURE_LEDGER_STATE_DIR is the existing isolated-store
 override; default remains .jcode/session-state. No transcript/private-store reads.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent


def json_rows(path):
    rows = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
    if any(not isinstance(row, dict) for row in rows):
        raise ValueError(f'invalid object in {path.name}')
    return rows


def disposition_valid(row):
    if row.get('disposition') == 'benign':
        reason = row.get('reason')
        return isinstance(reason, str) and bool(reason.strip())
    if row.get('disposition') == 'problem':
        name = row.get('problem_file')
        if not isinstance(name, str) or Path(name).name != name or not name.endswith('.md'):
            return False
        corpus = (ROOT / 'MONITORING/KNOWLEDGE/problems').resolve()
        target = (corpus / name).resolve()
        return target.parent == corpus and target.is_file()
    return False


def read_store(state):
    entries = json_rows(state / 'failure_ledger.jsonl')
    dispositions = json_rows(state / 'dispositions.jsonl')
    ids = [row.get('id') for row in entries]
    if any(type(i) is not int or i < 1 for i in ids) or len(set(ids)) != len(ids):
        raise ValueError('invalid or duplicate ledger IDs')
    for row in entries:
        if row.get('source') == 'omp-tool-result':
            if row.get('isError') is not True or not row.get('toolCallId') or not row.get('session_id'):
                raise ValueError('invalid OMP failure identity')
    for row in dispositions:
        if type(row.get('entry_id')) is not int or not disposition_valid(row):
            raise ValueError('invalid failure disposition')
    return entries, dispositions


def check(state, session):
    if not session or not re.fullmatch(r'[A-Za-z0-9_-]+', session):
        raise ValueError('expected session ID required (--session-id or OMP_CAPTURE_SESSION_ID)')
    receipt = json.loads((state / 'omp_observers' / f'{session}.json').read_text(encoding='utf-8'))
    if not isinstance(receipt, dict) or receipt.get('session_id') != session:
        raise ValueError('observer session mismatch')
    if receipt.get('active') is not True or receipt.get('failed') is not False:
        raise ValueError('observer inactive or failed')
    if receipt.get('source') != 'omp-tool-result' or receipt.get('lease_ms') != 30000:
        raise ValueError('invalid observer lease contract')
    stamp = datetime.fromisoformat(receipt['ts'].replace('Z', '+00:00'))
    age = (datetime.now(timezone.utc) - stamp).total_seconds()
    if not 0 <= age <= 30:
        raise ValueError(f'observer stale or future timestamp (age={age:.3f}s)')
    entries, dispositions = read_store(state)
    done = {row['entry_id'] for row in dispositions}
    pending = [row['id'] for row in entries if row['id'] not in done]
    if pending:
        raise ValueError(f'undispositioned failures prevent closure: {pending}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--session-id', default=os.environ.get('OMP_CAPTURE_SESSION_ID'))
    parser.add_argument('command', choices=['check', 'dispose'], nargs='?', default='check')
    parser.add_argument('entry_id', nargs='?', type=int)
    parser.add_argument('kind', nargs='?', choices=['problem', 'benign'])
    parser.add_argument('reason', nargs='?')
    args = parser.parse_args()
    state = Path(os.environ.get('JCODE_FAILURE_LEDGER_STATE_DIR') or ROOT / '.jcode/session-state').resolve()
    lock = state / 'omp_capture.lock'
    locked = False
    try:
        # Exclusive with the adapter: never approve a half-written snapshot.
        lock.mkdir(); locked = True
        if args.command == 'dispose':
            entries, _ = read_store(state)
            if args.entry_id not in {row['id'] for row in entries}:
                raise ValueError('disposition must name an existing ledger entry')
            row = {'entry_id': args.entry_id, 'ts': datetime.now(timezone.utc).isoformat(),
                   'disposition': args.kind,
                   'problem_file' if args.kind == 'problem' else 'reason': args.reason}
            if not disposition_valid(row):
                raise ValueError('disposition requires existing corpus filename or nonempty benign reason')
            with (state / 'dispositions.jsonl').open('a', encoding='utf-8') as file:
                file.write(json.dumps(row) + '\n')
            print(f'[omp-capture] disposition recorded for #{args.entry_id}')
        else:
            check(state, args.session_id)
            print(f'[omp-capture] OK: active fresh observer {args.session_id}; all failures dispositioned')
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'[omp-capture] FAIL: {error}', file=sys.stderr)
        return 1
    finally:
        if locked:
            lock.rmdir()


if __name__ == '__main__':
    sys.exit(main())
