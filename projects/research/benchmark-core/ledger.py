"""Append-only cryptographic ledger for benchmark-core v2.

Compliant with PROTOCOL.md:
- Canonical JSON formatting (sorted keys, compact separators, utf-8).
- Cryptographic hash chaining: prev_sha256 = sha256(canonical_bytes(previous_row)).
- Genesis block binds manifest_sha256.
- Entry types: cycle_card, run_result, lockbox_registration, lockbox_result, amendment.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


LEDGER_FILENAME = "ledger.jsonl"


def canonical_json_bytes(data: Dict[str, Any]) -> bytes:
    """Serialize data dictionary into canonical, deterministic JSON bytes."""
    return json.dumps(data, sort_keys=True, indent=None, separators=(",", ":")).encode("utf-8")


def sha256_hex(data_bytes: bytes) -> str:
    """Compute hex SHA-256 digest."""
    return hashlib.sha256(data_bytes).hexdigest()


class Ledger:
    def __init__(self, ledger_path: Path):
        self.path = Path(ledger_path)

    def exists(self) -> bool:
        return self.path.is_file()

    def read_entries(self) -> List[Dict[str, Any]]:
        """Read and parse all entries from the JSONL file."""
        if not self.exists():
            return []
        entries = []
        with open(self.path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                s = line.strip()
                if not s:
                    continue
                try:
                    entries.append(json.loads(s))
                except json.JSONDecodeError as err:
                    raise ValueError(f"Corrupt ledger JSON at {self.path}:{line_num}: {err}")
        return entries

    def verify_integrity(self, expected_manifest_sha256: Optional[str] = None) -> None:
        """Verify the full hash chain and genesis block invariants."""
        if not self.exists():
            raise FileNotFoundError(f"Ledger file not found: {self.path}")

        lines = [line.strip() for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if not lines:
            raise ValueError(f"Ledger is empty: {self.path}")

        entries = [json.loads(l) for l in lines]

        # Genesis block check
        genesis = entries[0]
        if genesis.get("type") != "genesis":
            raise ValueError(f"Block 0 must be 'genesis', got {genesis.get('type')}")
        if genesis.get("prev_sha256") is not None:
            raise ValueError(f"Genesis block must have prev_sha256=null, got {genesis.get('prev_sha256')}")

        if expected_manifest_sha256 is not None:
            actual_m_sha = genesis.get("manifest_sha256")
            if actual_m_sha != expected_manifest_sha256:
                raise ValueError(
                    f"Genesis manifest SHA mismatch: expected {expected_manifest_sha256}, got {actual_m_sha}"
                )

        # Hash chain verification
        prev_hash = sha256_hex(canonical_json_bytes(genesis))
        for i in range(1, len(entries)):
            entry = entries[i]
            recorded_prev = entry.get("prev_sha256")
            if recorded_prev != prev_hash:
                raise ValueError(
                    f"Hash chain broken at entry {i} ({entry.get('type')}): "
                    f"expected prev_sha256={prev_hash}, found {recorded_prev}"
                )
            prev_hash = sha256_hex(canonical_json_bytes(entry))

    def append_entry(self, entry: Dict[str, Any]) -> str:
        """Append a new entry to the ledger, computing prev_sha256 automatically."""
        entries = self.read_entries()
        if not entries:
            if entry.get("type") != "genesis":
                raise ValueError("First entry in ledger must be 'genesis'")
            entry["prev_sha256"] = None
        else:
            last_entry = entries[-1]
            prev_bytes = canonical_json_bytes(last_entry)
            entry["prev_sha256"] = sha256_hex(prev_bytes)

        entry_bytes = canonical_json_bytes(entry)
        curr_hash = sha256_hex(entry_bytes)

        # Write canonical representation + newline
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(entry_bytes.decode("utf-8") + "\n")

        return curr_hash

    @classmethod
    def initialize_genesis(
        cls,
        ledger_path: Path,
        manifest_sha256: str,
        protocol_version: str = "2.0.0",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "Ledger":
        """Initialize a new ledger with the Genesis block."""
        ledger = cls(ledger_path)
        if ledger.exists():
            raise FileExistsError(f"Cannot initialize genesis: ledger already exists at {ledger_path}")

        genesis_record = {
            "type": "genesis",
            "protocol_version": protocol_version,
            "manifest_sha256": manifest_sha256,
            "metadata": metadata or {},
        }
        ledger.append_entry(genesis_record)
        return ledger
