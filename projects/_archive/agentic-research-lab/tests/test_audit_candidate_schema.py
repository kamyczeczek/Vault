"""Regression tests for the canonical-candidate schema in scripts/audit_candidate.py.

Pins the fix where the auditor reads `Rule`/`Evidence` (post-migrate schema,
backtick-wrapped evidence ids) instead of legacy lowercase `claim`/`evidence`.
A regression to legacy fields makes the auditor treat every migrated candidate
as evidence-less and reject it.
"""
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import audit_candidate  # noqa: E402


class _AuditHarness:
    """Builds a throwaway candidates dir + graph.db and patches the module's constants."""

    def __init__(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.cand_dir = self.base / "candidates"
        self.cand_dir.mkdir()
        self.db_path = self.base / "graph.db"

        conn = sqlite3.connect(self.db_path)
        conn.executescript(
            "CREATE TABLE nodes(id TEXT PRIMARY KEY, title TEXT, body TEXT);"
        )
        # Node whose body contains the claim keywords so a correctly-read
        # candidate passes the content-grounding check.
        conn.execute(
            "INSERT INTO nodes VALUES(?,?,?)",
            ("chunk_1", "Falsification", "adversarial debate and counterfactual ablation"),
        )
        conn.commit()
        conn.close()

        self.patchers = [
            patch.object(audit_candidate, "CANDIDATES", self.cand_dir),
            patch.object(audit_candidate, "DB", self.db_path),
        ]

    def __enter__(self) -> "_AuditHarness":
        for p in self.patchers:
            p.start()
        return self

    def __exit__(self, *exc) -> None:
        for p in reversed(self.patchers):
            p.stop()
        self.tmp.cleanup()

    def write_candidate(self, name: str, obj: dict) -> None:
        path = self.cand_dir / f"{name}.jsonl"
        with path.open("w", encoding="utf-8") as fh:
            fh.write(json.dumps(obj) + "\n")




class AuditSchemaTests(unittest.TestCase):
    def _run_main(self, cand_id: str) -> int:
        with patch.object(sys, "argv", ["audit_candidate.py", cand_id]):
            return audit_candidate.main()

    def test_canonical_schema_candidate_passes(self) -> None:
        """A post-migrate candidate (Rule/Evidence + backtick ids) must be audited,
        not treated as evidence-less. This is the exact regression the fix removed."""
        with _AuditHarness() as h:
            h.write_candidate("vera_canon", {
                "id": "vera-canon",
                "state": "proposed",
                "Rule": "Adversarial debate with counterfactual ablation",
                "Evidence": "`chunk_1`",
            })
            # Before the fix, main() read `claim`/`evidence` (absent here) and
            # failed with "carries no evidence IDs" (exit 1). After the fix it
            # reads Rule/Evidence and passes content grounding (exit 0).
            self.assertEqual(self._run_main("vera-canon"), 0)

    def test_legacy_lowercase_schema_still_supported(self) -> None:
        """Backward-compat: a legacy lowercase `evidence` list still resolves."""
        with _AuditHarness() as h:
            h.write_candidate("vera_legacy", {
                "id": "vera-legacy",
                "state": "proposed",
                "claim": "Adversarial debate with counterfactual ablation",
                "evidence": ["chunk_1"],
            })
            self.assertEqual(self._run_main("vera-legacy"), 0)

    def test_unbackticked_evidence_string_split(self) -> None:
        """A bare string `Evidence` without backticks is treated as a single id."""
        with _AuditHarness() as h:
            h.write_candidate("vera_str", {
                "id": "vera-str",
                "state": "proposed",
                "Rule": "Adversarial debate with counterfactual ablation",
                "Evidence": "chunk_1",
            })
            self.assertEqual(self._run_main("vera-str"), 0)

    def test_missing_evidence_is_rejected(self) -> None:
        """A candidate with no evidence at all must exit 1 regardless of schema."""
        with _AuditHarness() as h:
            h.write_candidate("vera_none", {
                "id": "vera-none",
                "state": "proposed",
                "Rule": "Adversarial debate with counterfactual ablation",
            })
            self.assertEqual(self._run_main("vera-none"), 1)

    def test_unknown_evidence_id_is_rejected(self) -> None:
        """Evidence ids absent from graph.db must fail content grounding."""
        with _AuditHarness() as h:
            h.write_candidate("vera_bad", {
                "id": "vera-bad",
                "state": "proposed",
                "Rule": "Adversarial debate with counterfactual ablation",
                "Evidence": "`does_not_exist`",
            })
            self.assertEqual(self._run_main("vera-bad"), 1)


if __name__ == "__main__":
    unittest.main()
