"""Regression tests for chunk-level quarantine (C-4).

Damage is concentrated in a few passages of a few books, so the exclusion must be
per chunk. A source-level cut discarded 417 clean chunks to hide 419 damaged
ones — including all 828 chunks of one book over a single damaged chunk.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
GRAPH = ROOT / "knowledge" / "graph"
for entry in (SCRIPTS, GRAPH):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

import ask  # noqa: E402
import build_quarantine  # noqa: E402


CHUNK = """---
id: {cid}
title: "Test Chunk"
source: "{source}"
trust_tier: 1
tags: [memory]
---

{body}
"""


class DamagedChunkTests(unittest.TestCase):
    def test_reports_damaged_chunks_by_id(self) -> None:
        glue = "purposeofcopyrightistoencouragewritersandartiststoproducethecreativeworksthatenrich"
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "bad.md").write_text(
                CHUNK.format(cid="bad", source="Bad Book.pdf", body=glue), encoding="utf-8")
            (d / "good.md").write_text(
                CHUNK.format(cid="good", source="Good Book.pdf",
                             body="Ordinary prose about causal inference."),
                encoding="utf-8")
            stats = build_quarantine.damaged_chunks(d)
        self.assertEqual(list(stats), ["bad"])
        self.assertEqual(stats["bad"]["glue_tokens"], 1)
        self.assertIn("Bad Book", stats["bad"]["source"])

    def test_empty_corpus_yields_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(build_quarantine.damaged_chunks(Path(tmp)), {})


class QuarantineLoaderTests(unittest.TestCase):
    def _with_quarantine(self, payload):
        """Point ask.QUARANTINE_PATH at a temp file holding `payload`."""
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                          encoding="utf-8")
        json.dump(payload, tmp)
        tmp.close()
        original = ask.QUARANTINE_PATH
        ask.QUARANTINE_PATH = Path(tmp.name)
        self.addCleanup(lambda: setattr(ask, "QUARANTINE_PATH", original))
        self.addCleanup(lambda: Path(tmp.name).unlink(missing_ok=True))

    def test_reads_chunk_ids(self) -> None:
        self._with_quarantine({"chunk_ids": {"a": {}, "b": {}}})
        self.assertEqual(ask.quarantined_chunks(), {"a", "b"})

    def test_missing_file_yields_empty_set(self) -> None:
        original = ask.QUARANTINE_PATH
        ask.QUARANTINE_PATH = Path("/nonexistent/quarantine.json")
        self.addCleanup(lambda: setattr(ask, "QUARANTINE_PATH", original))
        self.assertEqual(ask.quarantined_chunks(), set())

    def test_malformed_file_yields_empty_set(self) -> None:
        self._with_quarantine({"unexpected": "shape"})
        self.assertEqual(ask.quarantined_chunks(), set())

    def test_live_quarantine_is_chunk_level(self) -> None:
        # Guards the regression that mattered: the artifact must key on chunk ids,
        # not source families, or a single damaged chunk evicts a whole book.
        payload = json.loads((GRAPH / "quarantine.json").read_text(encoding="utf-8"))
        self.assertEqual(payload.get("granularity"), "chunk")
        self.assertIn("chunk_ids", payload)
        self.assertNotIn("sources", payload)


class QuarantineEnforcementTests(unittest.TestCase):
    """The exclusion must apply on every retrieval path, not just FTS."""

    def test_fts_path_excludes_quarantined_chunks(self) -> None:
        import sqlite3
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.execute("CREATE VIRTUAL TABLE fts USING fts5(id, title, body, source_family)")
        conn.execute("CREATE TABLE nodes (id TEXT, title TEXT, path TEXT, tags TEXT, "
                     "body TEXT, source_family TEXT, source TEXT, trust_tier INT)")
        for cid, fam in (("keep", "Good.pdf"), ("drop", "Bad.pdf")):
            conn.execute("INSERT INTO nodes VALUES (?,?,?,?,?,?,?,?)",
                         (cid, cid, cid, "[]", "causal inference", fam, fam, 1))
            conn.execute("INSERT INTO fts VALUES (?,?,?,?)",
                         (cid, cid, "causal inference", fam))
        original = ask.QUARANTINE_PATH
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump({"chunk_ids": {"drop": {}}}, tmp)
        tmp.close()
        ask.QUARANTINE_PATH = Path(tmp.name)
        try:
            rows = ask._fts_rows(conn, ["causal"], "", [], 10, False)
        finally:
            ask.QUARANTINE_PATH = original
            Path(tmp.name).unlink(missing_ok=True)
        ids = [r["id"] for r in rows]
        self.assertIn("keep", ids)
        self.assertNotIn("drop", ids, "quarantined chunk must not be returned")


if __name__ == "__main__":
    unittest.main()
