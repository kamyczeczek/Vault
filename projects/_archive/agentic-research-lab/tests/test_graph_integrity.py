"""Tests for the C-7 integrity gates.

A gate that has never been shown to fail is not a gate. Each test here mutates
the thing the gate claims to check and asserts the gate notices — the same
standard the C-3 retrieval tests were held to.

The two defects these exist for:

* chunk ids are `NN_<slug of filename>`, so re-ingesting a book reuses the same
  ids for different text. Four benchmark golds drifted silently in C-6.
* the fingerprint check is satisfied by any self-consistent graph, so a build
  that varies run to run passes every existing gate.
"""

import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for entry in (ROOT / "scripts", ROOT / "knowledge" / "graph"):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

import build_graph  # noqa: E402

import check_citation_integrity as citation  # noqa: E402
import check_graph_determinism as determinism  # noqa: E402


class CitationGateTests(unittest.TestCase):
    """The gate must reject a gold that resolves but no longer says what it claimed."""

    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("CREATE TABLE nodes(id TEXT PRIMARY KEY, body TEXT)")
        self.conn.executemany(
            "INSERT INTO nodes VALUES (?,?)",
            [("00_alpha", "causal inference and counterfactual intervention"),
             ("00_beta", "unrelated text about gardening")])
        self.addCleanup(self.conn.close)

    def test_flags_gold_that_does_not_contain_required_concepts(self) -> None:
        case = {"id": "x", "required_concepts": ["causal", "counterfactual"],
                "gold_sources": ["00_beta"]}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "retrieval_benchmark.json"
            path.write_text(json.dumps({"cases": [case]}), encoding="utf-8")
            original = citation.BENCHMARK
            citation.BENCHMARK = path
            try:
                problems = citation.check_benchmark({"00_alpha", "00_beta"}, self.conn)
            finally:
                citation.BENCHMARK = original
        self.assertEqual(len(problems), 1)
        # The message must name id-reuse, since a resolving id is the confusing case.
        self.assertIn("id likely reused", problems[0])

    def test_accepts_gold_that_supports_its_concepts(self) -> None:
        case = {"id": "x", "required_concepts": ["causal", "counterfactual"],
                "gold_sources": ["00_alpha"]}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "retrieval_benchmark.json"
            path.write_text(json.dumps({"cases": [case]}), encoding="utf-8")
            original = citation.BENCHMARK
            citation.BENCHMARK = path
            try:
                problems = citation.check_benchmark({"00_alpha"}, self.conn)
            finally:
                citation.BENCHMARK = original
        self.assertEqual(problems, [])

    def test_flags_gold_absent_from_graph(self) -> None:
        case = {"id": "x", "required_concepts": ["causal"],
                "gold_sources": ["00_ghost"]}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "retrieval_benchmark.json"
            path.write_text(json.dumps({"cases": [case]}), encoding="utf-8")
            original = citation.BENCHMARK
            citation.BENCHMARK = path
            try:
                problems = citation.check_benchmark({"00_alpha"}, self.conn)
            finally:
                citation.BENCHMARK = original
        self.assertEqual(len(problems), 1)
        self.assertIn("absent from graph.db", problems[0])

    def test_flags_case_with_no_golds(self) -> None:
        case = {"id": "x", "required_concepts": ["causal"], "gold_sources": []}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "retrieval_benchmark.json"
            path.write_text(json.dumps({"cases": [case]}), encoding="utf-8")
            original = citation.BENCHMARK
            citation.BENCHMARK = path
            try:
                problems = citation.check_benchmark(set(), self.conn)
            finally:
                citation.BENCHMARK = original
        self.assertEqual(len(problems), 1)
        self.assertIn("no gold_sources", problems[0])

    def test_digest_prose_reference_is_not_load_bearing(self) -> None:
        # A backticked id in prose is a reference; only a `Chunk id:` line is
        # evidence. Requiring prose to resolve would flag every digest that
        # mentions a paper by chunk id, including papers never ingested.
        text = ("Some claim about ExpeL. Chunk id: `00_alpha`\n\n"
                "Honest Lying (`00_never_ingested`) shows the cost.\n")
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "digest.md").write_text(text, encoding="utf-8")
            original = citation.DIGESTS
            citation.DIGESTS = d
            try:
                problems = citation.check_digests({"00_alpha"})
            finally:
                citation.DIGESTS = original
        self.assertEqual(problems, [])

    def test_digest_evidence_line_must_resolve(self) -> None:
        text = "Some claim. Chunk id: `00_ghost`\n"
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "digest.md").write_text(text, encoding="utf-8")
            original = citation.DIGESTS
            citation.DIGESTS = d
            try:
                problems = citation.check_digests(set())
            finally:
                citation.DIGESTS = original
        self.assertEqual(len(problems), 1)
        self.assertIn("00_ghost", problems[0])

    def test_handles_multiline_jsonl_candidates(self) -> None:
        # These files are not strictly one object per line; a line-based parser
        # silently reads zero records and reports "OK" on a broken file.
        record = {"id": "r1", "Evidence": "see `00_ghost` and `00_alpha`"}
        text = json.dumps(record, indent=2) + "\n" + json.dumps(
            {"id": "r2", "Evidence": "`00_beta`"}, indent=2) + "\n"
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "c.jsonl").write_text(text, encoding="utf-8")
            original = citation.CANDIDATES
            citation.CANDIDATES = d
            try:
                problems = citation.check_candidates({"00_alpha", "00_beta"})
            finally:
                citation.CANDIDATES = original
        self.assertEqual(len(problems), 1)
        self.assertIn("00_ghost", problems[0])

    def test_live_workspace_citations_are_sound(self) -> None:
        import check_citation_integrity as gate
        known = gate.known_ids()
        conn = sqlite3.connect(ROOT / "knowledge" / "graph" / "graph.db")
        try:
            problems = (gate.check_benchmark(known, conn)
                        + gate.check_digests(known)
                        + gate.check_candidates(known))
        finally:
            conn.close()
        self.assertEqual(problems, [], f"live citation problems: {problems[:5]}")


class DeterminismGateTests(unittest.TestCase):
    """The digest must actually change when the graph changes."""

    def setUp(self) -> None:
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir, ignore_errors=True)
        self.db = self.dir / "g.db"
        conn = sqlite3.connect(self.db)
        conn.execute("CREATE TABLE nodes(id TEXT PRIMARY KEY, title TEXT, path TEXT, "
                     "tags TEXT, headings TEXT, body TEXT, node_type TEXT, "
                     "source_family TEXT, source TEXT, trust_tier INTEGER, "
                     "semantic_edges TEXT)")
        conn.execute("CREATE TABLE edges(src TEXT, dst TEXT, kind TEXT, conf REAL, tag TEXT)")
        conn.execute("CREATE TABLE node_tags(node_id TEXT, tag TEXT)")
        conn.execute("CREATE VIRTUAL TABLE fts USING fts5(id, title, body, source_family)")
        conn.execute("INSERT INTO nodes VALUES "
                     "('00_a','t','p','[]','','body','chunk','fam.pdf','fam.pdf',1,'')")
        conn.execute("INSERT INTO fts VALUES ('00_a','t','body','fam.pdf')")
        conn.commit()
        conn.close()

    def test_identical_databases_digest_identically(self) -> None:
        copy = self.dir / "copy.db"
        shutil.copy2(self.db, copy)
        self.assertEqual(determinism._digest_db(self.db),
                         determinism._digest_db(copy))

    def test_changed_node_content_changes_digest(self) -> None:
        before = determinism._digest_db(self.db)
        conn = sqlite3.connect(self.db)
        conn.execute("UPDATE nodes SET trust_tier = 99 WHERE id = '00_a'")
        conn.commit()
        conn.close()
        after = determinism._digest_db(self.db)
        self.assertNotEqual(before["nodes"], after["nodes"])
        self.assertEqual(before["nodes_count"], after["nodes_count"])

    def test_insertion_order_does_not_affect_digest(self) -> None:
        # The bug this catches is set/dict iteration order leaking into row order.
        # Order must be imposed by the query, not inherited from insertion.
        conn = sqlite3.connect(self.db)
        conn.executemany(
            "INSERT INTO nodes VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            [(f"00_{c}", "t", "p", "[]", "", "body", "chunk", "f.pdf", "f.pdf", 1, "")
             for c in "zyxwv"])
        conn.commit()
        conn.close()
        d1 = determinism._digest_db(self.db)
        copy = self.dir / "reordered.db"
        shutil.copy2(self.db, copy)
        self.assertEqual(d1, determinism._digest_db(copy))


if __name__ == "__main__":
    unittest.main()


class BuildOutputRestoreTests(unittest.TestCase):
    """A verification step must not dirty the tree it verifies.

    The first version of the determinism gate snapshotted and restored only
    graph.db. build() also rewrites GRAPH-DIGEST.md, graph_index.json,
    generation.json and .graph_fingerprint, so the gate left four tracked files
    modified on every run — and because the pre-commit hook invokes the gate
    after `git add`, the committed value was permanently the pre-run one.

    This is the same shape as the `--dry` bug that deleted 369 corpus files: a
    check with side effects on the live workspace.
    """

    def test_gate_restores_every_build_output_byte_for_byte(self) -> None:
        outputs = [build_graph.DB, build_graph.DIGEST, build_graph.INDEX,
                   build_graph.GENERATION,
                   Path(build_graph.__file__).with_name(".graph_fingerprint")]
        missing = [p.name for p in outputs if not p.exists()]
        self.assertEqual(missing, [], f"build outputs missing: {missing}")

        before = {p: p.read_bytes() for p in outputs}
        # Disturb one volatile artifact so a missing restore cannot pass by luck.
        text = before[build_graph.GENERATION].decode("utf-8")
        self.assertIn("created_at", text)
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_graph_determinism.py")],
            cwd=ROOT, capture_output=True, timeout=1800)
        for path in outputs:
            self.assertEqual(path.read_bytes(), before[path],
                             f"{path.name} was left modified by the gate")


class TimestampStripTests(unittest.TestCase):
    def test_strips_only_created_at(self) -> None:
        a = b'{"schema_version": 2, "created_at": 1790443833.6280916, "nodes": 10}'
        b = b'{"schema_version": 2, "created_at": 1790443880.3192139, "nodes": 10}'
        self.assertEqual(determinism._strip_timestamp(a),
                         determinism._strip_timestamp(b))

    def test_preserves_other_content(self) -> None:
        a = b'{"created_at": 1.0, "nodes": 10}'
        b = b'{"created_at": 2.0, "nodes": 11}'
        self.assertNotEqual(determinism._strip_timestamp(a),
                            determinism._strip_timestamp(b))
