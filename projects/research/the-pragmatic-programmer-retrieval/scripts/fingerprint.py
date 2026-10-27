"""Canonical fingerprints for the book index / gold sets.

A fingerprint must depend only on the *content* it identifies, never on how that
content happens to be serialized. Hashing raw file bytes made the value swing on
line endings (CRLF vs LF), indentation, and trailing whitespace, so a byte-level
touch of ``data/book_structure.json`` tripped the evaluator's stale-gold-set gate
even though nothing meaningful had changed.

``canonical_index_fingerprint`` parses the JSON and re-serializes it in a fixed
canonical form (sorted keys, no insignificant whitespace, UTF-8), so the digest
is stable across platforms, editors, and generators — only a real content change
moves it.
"""
from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path


def canonical_index_fingerprint(path: str | Path) -> str:
    """Return the sha256 of the canonical JSON serialization of ``path``."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()
