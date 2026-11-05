import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


GRAPH_DIR = Path(__file__).resolve().parents[1] / "knowledge" / "graph"
if str(GRAPH_DIR) not in sys.path:
    sys.path.insert(0, str(GRAPH_DIR))

import apply_meta_learning  # noqa: E402
import apply_rules  # noqa: E402
import check_frontier  # noqa: E402
import context_gateway  # noqa: E402
import frontier_state  # noqa: E402
import memory_rules  # noqa: E402


CANONICAL = """# Memory

### accepted_one — accepted
Rule: Always cite the chunk that carries a claim.
Evidence: `chunk_a`, `chunk_b`
Target: reflection pipeline
Action: Cite the carrying chunk before promoting a rule.

### experimental_one — experimental
Rule: Not yet promoted.
Evidence: `chunk_a`
Target: reflection pipeline
Action: Should never be applied.

### legacy_one — accepted
- claim: A rule in the obsolete shape.
- evidence: chunk_a
"""

BROKEN = {
    "missing_action": """### no_action — accepted
Rule: Rule text.
Evidence: `chunk_a`
Target: reflection pipeline
""",
    "blank_evidence": """### blank_evidence — accepted
Rule: Rule text.
Evidence: no backticks here
Target: reflection pipeline
Action: Do the thing.
""",
    "no_evidence_field": """### no_evidence_field — accepted
Rule: Rule text.
Target: reflection pipeline
Action: Do the thing.
""",
}


class CanonicalParserTests(unittest.TestCase):
    def test_only_accepted_canonical_rules_parse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "memory.md"
            path.write_text(CANONICAL, encoding="utf-8")
            rules = memory_rules.parse_accepted_rules(path)
        self.assertEqual([rule.id for rule in rules], ["accepted_one"])

    def test_legacy_record_is_rejected_with_a_reason(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "memory.md"
            path.write_text(CANONICAL, encoding="utf-8")
            rejections: list[memory_rules.Rejection] = []
            rules = memory_rules.parse_accepted_rules(path, on_rejection=rejections.append)
        self.assertEqual([rule.id for rule in rules], ["accepted_one"])
        self.assertEqual([r.rule_id for r in rejections], ["legacy_one"])
        self.assertIn("legacy", rejections[0].message())

    def test_incomplete_canonical_blocks_are_rejected_not_applied(self) -> None:
        for name, body in BROKEN.items():
            with self.subTest(name), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "memory.md"
                path.write_text(body, encoding="utf-8")
                rejections: list[memory_rules.Rejection] = []
                rules = memory_rules.parse_accepted_rules(path, on_rejection=rejections.append)
                self.assertEqual(rules, [], f"{name} must not parse as an applicable rule")
                self.assertEqual(len(rejections), 1, f"{name} must report exactly one reason")

    def test_duplicate_title_is_rejected_only_when_deduping(self) -> None:
        duplicate = CANONICAL + """
### accepted_one_copy — accepted
Rule: Always cite the chunk that carries a claim.
Evidence: `chunk_c`
Target: reflection pipeline
Action: A different action entirely.
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "memory.md"
            path.write_text(duplicate, encoding="utf-8")
            plain = memory_rules.parse_accepted_rules(path)
            deduped = memory_rules.parse_accepted_rules(path, dedupe=True)
        self.assertEqual(len(plain), 2)
        self.assertEqual([rule.id for rule in deduped], ["accepted_one"])

    def test_evidence_without_backticks_yields_no_citation_ids(self) -> None:
        rule = memory_rules.MemoryRule(
            id="r", rule="R", evidence=(), evidence_text="plain text",
            target="t", action="a", title_key="r",
        )
        self.assertEqual(rule.fingerprint(), ("a", ("plain text",)))


class ConsumerAgreementTests(unittest.TestCase):
    """A rule must be applied and evolved-or-not under the same decision."""

    def _parsed_titles(self, body: str, *, dedupe: bool) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "memory.md"
            path.write_text(body, encoding="utf-8")
            return [rule.rule for rule in memory_rules.parse_accepted_rules(path, dedupe=dedupe)]

    def test_lesson_adapter_and_meta_learning_agree_on_live_memory(self) -> None:
        live = apply_rules.MEMORY_FILE
        adapter_rules = memory_rules.parse_accepted_rules(live)
        evolution_rules = memory_rules.parse_accepted_rules(live, dedupe=True)
        self.assertTrue(adapter_rules, "live memory must expose applicable rules")
        self.assertEqual(
            [rule.id for rule in adapter_rules],
            [rule.id for rule in evolution_rules],
            "a duplicate-only difference between consumers means one would re-apply a rule",
        )

    def test_broken_block_is_invisible_to_both_consumers(self) -> None:
        for name, body in BROKEN.items():
            with self.subTest(name):
                self.assertEqual(self._parsed_titles(body, dedupe=False), [])
                self.assertEqual(self._parsed_titles(body, dedupe=True), [])

    def test_dedupe_hides_only_the_repeat_from_meta_learning(self) -> None:
        duplicate = CANONICAL + """
### accepted_one_copy — accepted
Rule: Always cite the chunk that carries a claim.
Evidence: `chunk_c`
Target: reflection pipeline
Action: A different action entirely.
"""
        self.assertEqual(self._parsed_titles(duplicate, dedupe=False),
                         ["Always cite the chunk that carries a claim."] * 2)
        self.assertEqual(self._parsed_titles(duplicate, dedupe=True),
                         ["Always cite the chunk that carries a claim."])


class FrontierInspectorTests(unittest.TestCase):
    """check_frontier and the gateway must inherit the canonical verdicts."""

    def setUp(self) -> None:
        """Fail loudly if a test ever writes the live frontier instead of its tmpdir."""
        live = frontier_state.DEFAULT_FRONTIER.resolve()
        original_append = frontier_state.append_record

        def guarded_append(record, frontier_dir=frontier_state.DEFAULT_FRONTIER):
            if Path(frontier_dir).resolve() == live:
                raise AssertionError("test tried to write the live frontier")
            return original_append(record, frontier_dir)

        patcher = unittest.mock.patch.object(frontier_state, "append_record", guarded_append)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _frontier(self, tmp: str) -> Path:
        return Path(tmp) / "frontier"

    def test_consistent_frontier_reports_no_errors_through_every_reader(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            frontier = self._frontier(tmp)
            frontier_state.initialize(frontier)
            view = frontier_state.inspect_frontier(frontier)
            self.assertTrue(view["present"])
            self.assertEqual(view["errors"], [])
            self.assertEqual(check_frontier.check_frontier(frontier), [])
            self.assertEqual(context_gateway._frontier_integrity(frontier)[0], "valid")
            self.assertEqual(frontier_state.status(frontier)["open_turn_count"], 0)

    def test_half_written_frontier_is_fail_closed_in_all_readers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            frontier = self._frontier(tmp)
            frontier_state.initialize(frontier)
            frontier_state.manifest_path(frontier).unlink()
            self.assertTrue(check_frontier.check_frontier(frontier))
            self.assertEqual(context_gateway._frontier_integrity(frontier)[0], "partial")
            with self.assertRaises(frontier_state.FrontierError):
                frontier_state.status(frontier)
            with self.assertRaises(frontier_state.FrontierError):
                frontier_state.inspect_frontier(frontier)

    def test_stale_manifest_is_rejected_by_the_canonical_seam(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            frontier = self._frontier(tmp)
            frontier_state.initialize(frontier)
            frontier_state.open_turn(session_id="s1", turn_id="t1", next_action="act",
                                    frontier_dir=frontier)
            manifest = frontier_state.rebuild_manifest(frontier)
            self.assertEqual(manifest["ledger_line_count"], 1)

            tampered = dict(manifest)
            tampered["ledger_line_count"] = 99
            frontier_state.atomic_write(frontier_state.manifest_path(frontier),
                                        frontier_state.canonical_bytes(tampered))
            view = frontier_state.inspect_frontier(frontier)
            self.assertTrue(any("does not match replay" in error for error in view["errors"]))
            self.assertTrue(check_frontier.check_frontier(frontier))
            self.assertEqual(context_gateway._frontier_integrity(frontier)[0], "invalid")
            with self.assertRaises(frontier_state.FrontierError):
                frontier_state.status(frontier)

    def test_recover_write_repairs_a_stale_manifest_that_status_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            frontier = self._frontier(tmp)
            frontier_state.initialize(frontier)
            frontier_state.open_turn(session_id="s1", turn_id="t1", next_action="act",
                                    frontier_dir=frontier)
            tampered = dict(frontier_state.read_manifest(frontier))
            tampered["ledger_line_count"] = 99
            frontier_state.atomic_write(frontier_state.manifest_path(frontier),
                                        frontier_state.canonical_bytes(tampered))
            with self.assertRaises(frontier_state.FrontierError):
                frontier_state.status(frontier)
            repaired = frontier_state.recover(write=True, frontier_dir=frontier)
            self.assertEqual(repaired["open_turn_count"], 1)
            self.assertEqual(check_frontier.check_frontier(frontier), [])

    def test_gateway_labels_a_missing_frontier_missing_not_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(context_gateway._frontier_integrity(self._frontier(tmp)), ("missing", []))


if __name__ == "__main__":
    unittest.main()
