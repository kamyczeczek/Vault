#!/usr/bin/env python3
"""Hermetic tests for scripts/close.py (pure helpers only; the transaction
itself is dogfooded by real closes, not mocked)."""
from __future__ import annotations

import argparse
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import close as c  # noqa: E402


def _init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True)


def _commit_all(root: Path, message: str) -> None:
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", message], cwd=root, check=True)


class CloseTests(unittest.TestCase):
    def test_flag_rx_accepts_ids(self):
        for ok in ("abc", "a1-b2_c3", "0x"):
            self.assertTrue(c.FLAG_RX.match(ok), ok)

    def test_flag_rx_rejects(self):
        for bad in ("", "ABC", "has space", "dot.name", "-lead", "../x"):
            self.assertFalse(c.FLAG_RX.match(bad), bad)

    def test_check_body_ok(self):
        self.assertIsNone(c.check_body("my-flag", "`my-flag` — 2026-10-10: done.\nnot checked: —"))

    def test_check_body_rejects(self):
        self.assertIsNotNone(c.check_body("my-flag", ""))
        self.assertIsNotNone(c.check_body("my-flag", "`other` — 2026-10-10: done.\nnot checked: —"))
        self.assertIsNotNone(c.check_body("my-flag", "my-flag — no backticks.\nnot checked: —"))

    def test_check_body_requires_not_checked(self):
        self.assertIsNotNone(c.check_body("my-flag", "`my-flag` — 2026-10-10: done."))
        self.assertIsNone(c.check_body("my-flag", "`my-flag` — 2026-10-10: done.\nnot checked: hook on projects/"))

    def test_check_includes(self):
        self.assertIsNone(c.check_includes(["scripts/close.py"]))
        self.assertIsNotNone(c.check_includes(["scripts/no-such-file.py"]))

    def test_format_failure_keeps_diff_check_full(self):
        # S66: a diff-check FAIL is the repair list; never truncate it.
        out = "\n".join(f"f.py:{i}: trailing whitespace." for i in range(1, 14))
        rendered = c.format_failure("diff-check", ["git", "diff", "--check"], 1, out)
        for i in range(1, 14):
            self.assertIn(f"f.py:{i}: trailing whitespace.", rendered)
        self.assertNotIn("more lines", rendered)

    def test_format_failure_truncates_other_steps_with_hint(self):
        out = "\n".join(f"line {i}" for i in range(1, 14))
        rendered = c.format_failure("commit", ["git", "commit"], 1, out)
        self.assertIn("line 13", rendered)
        self.assertIn("(5 more lines; run `git commit` for full output)", rendered)

    def test_untracked_includes(self):
        self.assertEqual(c.untracked_includes(["scripts/close.py"]), [])
        self.assertEqual(c.untracked_includes(["scripts/no-such-file.py"]), [])

    def test_generated_views_include_index_md(self):
        # S81: close.py must stage (and not treat as a stray) all three
        # generated views. Before the fix INDEX.md was omitted from
        # allowed/add/hook, so every close needed `--include`.
        self.assertIn("HANDOFF.md", c.GENERATED_VIEWS)
        self.assertIn("STATE.md", c.GENERATED_VIEWS)
        self.assertIn("handoff/flags/INDEX.md", c.GENERATED_VIEWS)
        self.assertIn("handoff/status/STATUS.md", c.GENERATED_VIEWS)

    def test_render_flag_shape(self):
        t = c.render_flag("f", "2026-10-10", "mateusz", "opencode",
                          "m/model", "session-close", "`f` — 2026-10-10: x.")
        self.assertTrue(t.startswith("---\nflag: f\n"))
        self.assertIn("model: m/model\n", t)
        self.assertTrue(t.endswith("x.\n"))
        self.assertNotIn("\r", t)

    def test_load_body_from_file(self):
        import argparse
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                         encoding="utf-8") as f:
            f.write("  `f` — 2026-10-10: x.  \n")
            name = f.name
        ns = argparse.Namespace(body=None, body_file=Path(name))
        try:
            self.assertEqual(c.load_body(ns), "`f` — 2026-10-10: x.")
        finally:
            Path(name).unlink()
        ns = argparse.Namespace(body=" inline ", body_file=None)
        self.assertEqual(c.load_body(ns), "inline")


class ModelContractTests(unittest.TestCase):
    """E4 (B12): `model:` must be `provider/model-id`.

    close.py rejects placeholders/nicknames at the transaction boundary;
    check_workspace_integrity.py reports legacy flags as FAIL/WARN.
    """

    def test_check_model_accepts_provider_slash_id(self):
        self.assertIsNone(c.check_model("opencode/deepseek-v4.1-flash-free"))
        self.assertIsNone(c.check_model("nara/stepfun-3.7-flash"))

    def test_check_model_rejects_current_and_default(self):
        for bad in ("current", "default"):
            self.assertIsNotNone(c.check_model(bad), bad)

    def test_check_model_rejects_nickname_without_slash(self):
        self.assertIsNotNone(c.check_model("gpt-4"))
        self.assertIsNotNone(c.check_model("pi-bolt"))


class VerifyClaimsTests(unittest.TestCase):
    """E6 (decision B3): --verify-claims re-derives claims with an artifact.

    B3's three mutations are tests here (false hash -> FAIL, true hash -> PASS,
    artifact-less counter -> WARN), plus the map's fourth (narrative -> no-op)
    and the false-positive guards the live 168-flag corpus scan forced: clause
    scoping, the transition guard and the commit-diff guard. Fixtures are a
    throwaway git repo + brain.db in a tmpdir, so nothing touches the workspace.
    """

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="e6-verify-claims-"))
        cls.root = cls.tmp / "root"
        (cls.root / "handoff" / "flags").mkdir(parents=True)
        for i in range(7):
            (cls.root / "handoff" / "flags" / f"f{i}.md").write_text(
                "x\n", encoding="utf-8")
        cls._db(cls.root, problems=3, decisions=4, lessons=5)
        cls.head = cls._repo(cls.root)
        cls.nested = cls.tmp / "nested"
        cls.nested_head = cls._repo(cls.nested)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @staticmethod
    def _db(root: Path, problems: int, decisions: int, lessons: int) -> None:
        db = root / "brain" / "brain.db"
        db.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(str(db))
        try:
            for table in ("problems", "decisions", "lessons"):
                con.execute(f"CREATE TABLE {table} (id INTEGER PRIMARY KEY)")
            con.executemany("INSERT INTO problems (id) VALUES (?)",
                            [(i,) for i in range(problems)])
            con.executemany("INSERT INTO decisions (id) VALUES (?)",
                            [(i,) for i in range(decisions)])
            con.executemany("INSERT INTO lessons (id) VALUES (?)",
                            [(i,) for i in range(lessons)])
            con.commit()
        finally:
            con.close()

    @staticmethod
    def _repo(path: Path) -> str:
        """A throwaway git repo with one commit; returns its hash."""
        path.mkdir(parents=True, exist_ok=True)
        (path / "seed.txt").write_text("seed\n", encoding="utf-8")
        for args in (["init", "-q"], ["add", "-A"],
                     ["-c", "user.name=t", "-c", "user.email=t@t",
                      "commit", "-q", "-m", "seed"]):
            subprocess.run(["git", *args], cwd=str(path), check=True,
                           capture_output=True, text=True)
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(path),
                              check=True, capture_output=True,
                              text=True).stdout.strip()

    def claims(self, body: str, repos=()):
        return c.verify_claims(body, root=self.root, repos=list(repos))

    # --- B3 mutation 1: false `commit <hash>` -> FAIL -----------------------
    def test_mutation1_false_commit_hash_fails(self):
        rep = self.claims("`f` — 2026-10-16: commit `deadbeefdeadbeef` nie "
                          "istnieje.\nnot checked: —")
        self.assertTrue(any(f.startswith("FAIL") for f in rep.findings),
                        rep.findings)
        self.assertIn("deadbeefdeadbeef", rep.findings[0])

    # --- B3 mutation 2: true hash -> PASS ----------------------------------
    def test_mutation2_true_commit_hash_passes(self):
        rep = self.claims(f"`f` — 2026-10-16: commit `{self.head}` istnieje."
                          "\nnot checked: —")
        self.assertEqual(rep.findings, [])
        self.assertEqual(rep.re_derived, 1)

    def test_nested_repo_commit_resolves(self):
        # A hash from a nested projects/ repo is absent from the root repo;
        # resolving root-only reported a false divergence on 14 of 33 claims.
        rep = self.claims(f"`f` — 2026-10-16: commit `{self.nested_head}` z "
                          "repo KR.\nnot checked: —", repos=[self.nested])
        self.assertEqual(rep.findings, [])
        self.assertEqual(rep.re_derived, 1)

    # --- B3 mutation 3: counter without artifact -> WARN, not silent -------
    def test_mutation3_counter_without_artifact_warns(self):
        rep = self.claims("`f` — 2026-10-16: 162 plików w repo.\nnot checked: —")
        self.assertEqual([f for f in rep.findings if f.startswith("FAIL")], [])
        self.assertEqual(len(rep.findings), 1)
        self.assertTrue(rep.findings[0].startswith("WARN"), rep.findings)
        self.assertIn("162", rep.findings[0])
        self.assertEqual(rep.re_derived, 0)

    def test_ascii_transliteration_is_reported_not_skipped(self):
        rep = self.claims("`f` — 2026-10-16: 162 plikow.\nnot checked: —")
        self.assertEqual(len(rep.findings), 1)
        self.assertTrue(rep.findings[0].startswith("WARN"), rep.findings)

    # --- map mutation 4: narrative -> no-op --------------------------------
    def test_mutation4_narrative_is_noop(self):
        rep = self.claims("`f` — 2026-10-16: system działa, rozstrzygnięto X."
                          "\nnot checked: —")
        self.assertEqual(rep.findings, [])
        self.assertEqual(rep.re_derived, 0)
        self.assertEqual(rep.gate_covered, 0)

    # --- named counters can FAIL ------------------------------------------
    def test_named_counter_matching_passes(self):
        rep = self.claims("`f` — 2026-10-16: 7 plików w handoff/flags/."
                          "\nnot checked: —")
        self.assertEqual(rep.findings, [])
        self.assertEqual(rep.re_derived, 1)

    def test_named_counter_diverging_fails(self):
        rep = self.claims("`f` — 2026-10-16: 4 pliki w handoff/flags/."
                          "\nnot checked: —")
        self.assertEqual(len([f for f in rep.findings if f.startswith("FAIL")]), 1)
        self.assertIn("handoff/flags/*.md holds 7", rep.findings[0])

    def test_brain_db_counter_fails_on_drift(self):
        rep = self.claims("`f` — 2026-10-16: brain.db ma 2 problems."
                          "\nnot checked: —")
        self.assertIn("brain.db:problems holds 3", rep.findings[0])

    # --- false-positive guards found by the live corpus scan ---------------
    def test_clause_scoping_blocks_cross_clause_bleed(self):
        # "(9 plików z eval/); ... i handoff/flags/" — the artifact is in the
        # next clause, so the eval/ count must not be re-derived against it.
        rep = self.claims("`f` — 2026-10-16: 9 plików z eval/; untracked "
                          "docs/ i handoff/flags/.\nnot checked: —")
        self.assertEqual([f for f in rep.findings if f.startswith("FAIL")], [])

    def test_transition_counter_is_historical_warn(self):
        rep = self.claims("`f` — 2026-10-16: 22 flagi → `handoff/flags/<flag>.md`."
                          "\nnot checked: —")
        self.assertEqual([f for f in rep.findings if f.startswith("FAIL")], [])
        self.assertTrue(rep.findings[0].startswith("WARN"), rep.findings)

    def test_commit_diff_counter_is_historical_warn(self):
        rep = self.claims(f"`f` — 2026-10-16: root w `{self.head[:7]}` "
                          "(41 plików, +1881/-179) — handoff/flags/ generowany."
                          "\nnot checked: —")
        self.assertEqual([f for f in rep.findings if f.startswith("FAIL")], [])

    def test_dotted_path_does_not_break_the_clause(self):
        # The dot in `SCARS.md` is not a sentence break: the artifact named
        # earlier in the sentence still owns the count.
        rep = self.claims("`f` — 2026-10-16: baseline bez zmian w `SCARS.md` "
                          "(48 problems).\nnot checked: —")
        self.assertEqual(len(rep.findings), 1)
        self.assertIn("brain.db:problems holds 3", rep.findings[0])

    # --- gate claims -------------------------------------------------------
    def test_gate_claim_is_covered_not_rerun(self):
        rep = self.claims("`f` — 2026-10-16: Integrity przechodzi (exit 0)."
                          "\nnot checked: —")
        self.assertEqual(rep.findings, [])
        self.assertEqual(rep.gate_covered, 1)

    def test_exit0_without_gate_noun_warns(self):
        rep = self.claims("`f` — 2026-10-16: `test_x.py` zielony (exit 0)."
                          "\nnot checked: —")
        self.assertEqual(len(rep.findings), 1)
        self.assertTrue(rep.findings[0].startswith("WARN"), rep.findings)

    def test_gate_note(self):
        self.assertEqual(c.gate_note(c.ClaimsReport([], 0, 0)), "")
        self.assertIn("1 gate claim", c.gate_note(c.ClaimsReport([], 0, 1)))

    def test_clause_around_bounds(self):
        body = "aaa. bbb; ccc\nddd"
        self.assertEqual(c._clause_around(body, body.index("bbb")), " bbb")
        self.assertEqual(c._clause_around(body, body.index("ddd")), "ddd")

    def test_dry_run_verify_claims_rejects_empty_claims(self):
        body = "`test-empty-claims-2026-10-28` — 2026-10-28: purely narrative.\nnot checked: —"
        ns = argparse.Namespace(
            flag="test-empty-claims-2026-10-28",
            correct=False,
            body_file=None,
            body=body,
            model="test/provider",
            include=[],
            verify_claims=True,
        )
        with mock.patch("scripts.close.load_body", return_value=body):
            rc = c.dry_run(ns)
            self.assertEqual(rc, 1)


class CorrectFlagTests(unittest.TestCase):
    """Testy dla --correct: tracked flag accept, untracked reject,
    normal close reject existing tracked."""

    def test_correct_accepts_tracked(self):
        import argparse
        ns = argparse.Namespace(correct=True)
        flag_path = Path("handoff/flags/close-py-final-2026-10-18.md")
        self.assertTrue(flag_path.exists(), "fixture: flag must exist on disk")
        err = c._validate_correction_target(ns, flag_path, is_tracked_flag=True)
        self.assertIsNone(err)

    def test_correct_rejects_untracked(self):
        import argparse
        ns = argparse.Namespace(correct=True)
        flag_path = Path("handoff/flags/nonexistent-flag-xyz.md")
        err = c._validate_correction_target(ns, flag_path, is_tracked_flag=False)
        self.assertEqual(err, "--correct requires an already-tracked flag")

    def test_normal_close_rejects_existing_untracked(self):
        import argparse
        ns = argparse.Namespace(correct=False)
        flag_path = Path("handoff/flags/close-py-final-2026-10-18.md")
        err = c._validate_correction_target(ns, flag_path, is_tracked_flag=False)
        self.assertIn("already exists", err)


class CheckIncludesGitRmTests(unittest.TestCase):
    def test_staged_deletion_is_valid_include(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True)

            (root / "victim.txt").write_text("x", encoding="utf-8")
            subprocess.run(["git", "add", "victim.txt"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "add victim"], cwd=root, check=True)

            subprocess.run(["git", "rm", "-q", "victim.txt"], cwd=root, check=True)
            self.assertFalse((root / "victim.txt").exists())

            with mock.patch.object(c, "ROOT", root):
                self.assertIsNone(c.check_includes(["victim.txt"]))


class DeletedDirectoryIncludeTests(unittest.TestCase):
    def test_removed_directory_stages_only_its_tracked_files(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _init_git_repo(root)
            (root / "gone" / "nested").mkdir(parents=True)
            (root / "gone" / "a.txt").write_text("a", encoding="utf-8")
            (root / "gone" / "nested" / "b.txt").write_text("b", encoding="utf-8")
            (root / "keep.txt").write_text("before", encoding="utf-8")
            _commit_all(root, "seed")

            shutil.rmtree(root / "gone")
            (root / "keep.txt").write_text("after", encoding="utf-8")
            with mock.patch.object(c, "ROOT", root):
                self.assertIsNone(c.check_includes(["gone"]))
                self.assertIsNone(c.stage_includes(["gone"]))

            staged = subprocess.run(
                ["git", "diff", "--cached", "--name-only"], cwd=root,
                capture_output=True, text=True, check=True).stdout.splitlines()
            unstaged = subprocess.run(
                ["git", "diff", "--name-only"], cwd=root,
                capture_output=True, text=True, check=True).stdout.splitlines()
            self.assertEqual(set(staged), {"gone/a.txt", "gone/nested/b.txt"})
            self.assertEqual(unstaged, ["keep.txt"])

    def test_staged_removed_directory_is_a_valid_include(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _init_git_repo(root)
            (root / "gone").mkdir()
            (root / "gone" / "a.txt").write_text("a", encoding="utf-8")
            _commit_all(root, "seed")
            subprocess.run(["git", "rm", "-qr", "gone"], cwd=root, check=True)

            with mock.patch.object(c, "ROOT", root):
                self.assertIsNone(c.check_includes(["gone"]))
                self.assertIsNone(c.stage_includes(["gone"]))


class FindStraysRenameTests(unittest.TestCase):
    def test_staged_rename_to_included_directory_is_not_a_stray(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _init_git_repo(root)
            old = root / "root_workspace" / "handoff" / "note.md"
            old.parent.mkdir(parents=True)
            old.write_text("same content\n", encoding="utf-8")
            _commit_all(root, "seed")
            new = root / "handoff" / "note.md"
            new.parent.mkdir(parents=True)
            subprocess.run(
                ["git", "mv", "root_workspace/handoff/note.md", "handoff/note.md"],
                cwd=root, check=True)

            self.assertEqual(c.find_strays(root, {"elsewhere"}), [
                "R  root_workspace/handoff/note.md -> handoff/note.md"])
            self.assertEqual(c.find_strays(root, {"handoff"}), [])


class NewSafetyChecksTests(unittest.TestCase):
    def test_include_dot_is_forbidden(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _init_git_repo(root)
            with mock.patch.object(c, "ROOT", root):
                err = c.check_includes(["."])
                self.assertIsNotNone(err)
                self.assertIn("forbidden for safety", err)

    def test_include_ignored_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _init_git_repo(root)
            (root / ".gitignore").write_text("secret.txt\n", encoding="utf-8")
            (root / "secret.txt").write_text("shh", encoding="utf-8")
            subprocess.run(["git", "add", ".gitignore"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "ignore"], cwd=root, check=True)

            with mock.patch.object(c, "ROOT", root):
                err = c.check_includes(["secret.txt"])
                self.assertIsNotNone(err)
                self.assertIn("ignored by git", err)

    def test_include_project_path_is_allowed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _init_git_repo(root)
            nested = root / "projects" / "research" / "kr" / "benchmark-core"
            nested.mkdir(parents=True)
            (nested / "bench.py").write_text("# bench\n", encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "seed"], cwd=root, check=True)

            with mock.patch.object(c, "ROOT", root):
                self.assertIsNone(c.check_includes(["projects/research/kr/benchmark-core/bench.py"]))
                self.assertIsNone(c.check_includes(["projects/research/kr/benchmark-core"]))


if __name__ == "__main__":
    unittest.main()
