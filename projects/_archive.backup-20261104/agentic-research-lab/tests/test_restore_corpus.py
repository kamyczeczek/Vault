"""Contracts for scripts/restore_corpus.py.

Measured defect this pins: `knowledge/corpus/` is deliberately untracked
(c8a5f8a, "a derived projection is not source"), so a fresh clone has zero
corpus files, `build_graph.py` yields `nodes 0 edges 0`, and 2 of 200 tests
fail with `sqlite3.OperationalError: no such table: nodes`. The recovery
existed only as a commit hash someone had to rediscover from history.

These tests pin the two things that make the recovery trustworthy:
1. discovery finds the LAST commit that actually HOLDS the corpus, not merely
   the last commit that touched the path (the untracking commit itself is in
   that list and holds nothing);
2. the script is safe to run on a healthy tree.
"""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import restore_corpus  # noqa: E402


class DiscoveryTests(unittest.TestCase):
    def test_finds_a_commit_that_really_holds_the_corpus(self) -> None:
        sha, count = restore_corpus.last_commit_holding_corpus()
        self.assertIsNotNone(sha, "no commit in history holds the corpus")
        self.assertGreaterEqual(count, restore_corpus.EXPECTED_MIN_FILES)
        # the returned commit must actually contain corpus files in its tree
        tree = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", sha, "--", restore_corpus.CORPUS_REL],
            cwd=ROOT, capture_output=True, text=True).stdout
        self.assertGreaterEqual(len([l for l in tree.splitlines() if l.strip()]),
                                restore_corpus.EXPECTED_MIN_FILES)

    def test_discovery_skips_the_untracking_commit(self) -> None:
        """The removing commit is in `rev-list` but holds zero files.

        If discovery returned it, restore would silently produce an empty
        corpus and the script would report success while leaving the graph
        broken -- the exact failure it exists to prevent.
        """
        removals = subprocess.run(
            ["git", "log", "--diff-filter=D", "-1", "--format=%H",
             "--", restore_corpus.CORPUS_REL],
            cwd=ROOT, capture_output=True, text=True).stdout.strip()
        self.assertTrue(removals, "expected a commit that removed the corpus")
        tree = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", removals, "--",
             restore_corpus.CORPUS_REL],
            cwd=ROOT, capture_output=True, text=True).stdout
        self.assertEqual(len([l for l in tree.splitlines() if l.strip()]), 0,
                         "precondition: the removal commit holds no corpus")
        sha, _ = restore_corpus.last_commit_holding_corpus()
        self.assertNotEqual(sha, removals,
                            "discovery must skip the commit that removed the corpus")

    def test_discovery_is_not_a_hardcoded_hash(self) -> None:
        """The script must read history, not embed a sha.

        If someone hardcodes `0cc21ac`, the recovery breaks the next time the
        corpus is re-tracked and untracked. The hashes ARE allowed to appear
        in the module docstring as historical explanation; what must not
        exist is a hash in executable code, i.e. outside strings and comments.
        """
        import ast
        source = (ROOT / "scripts" / "restore_corpus.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        docstrings = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)):
                doc = ast.get_docstring(node, clean=False)
                if doc is not None:
                    docstrings.add(doc)
        bare = {n for n in ast.walk(tree) if isinstance(n, ast.Constant)
                and isinstance(n.value, str) and n not in docstrings}
        literals = {n.value for n in bare}
        for forbidden in ("0cc21ac", "c8a5f8a"):
            self.assertNotIn(forbidden, literals,
                             f"{forbidden} must be discovered from history, "
                             f"not embedded in executable code")

    def test_existing_tree_is_left_alone(self) -> None:
        present = restore_corpus.corpus_file_count(ROOT / restore_corpus.CORPUS_REL)
        if present < restore_corpus.EXPECTED_MIN_FILES:
            self.skipTest("corpus not present; run scripts/restore_corpus.py first")
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "restore_corpus.py")],
                           cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("nothing to restore", r.stdout)
        self.assertEqual(restore_corpus.corpus_file_count(ROOT / restore_corpus.CORPUS_REL),
                         present, "a no-op run must not disturb the corpus")


if __name__ == "__main__":
    unittest.main()
