#!/usr/bin/env python3
"""Tests for scripts/sync_did_sessions.py — pure logic plus a real local copy.

Nothing here touches Google Drive: the sync client is the thing under test in
production, and it is proven by a live run, never by a unit test.
"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sync_did_sessions as sds  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


class Md5Tests(unittest.TestCase):
    def test_md5_of_known_content(self):
        import hashlib

        with tempfile.NamedTemporaryFile(delete=False) as handle:
            handle.write(b"did_sessions")
            path = Path(handle.name)
        try:
            self.assertEqual(sds.md5_of(path), hashlib.md5(b"did_sessions").hexdigest())
        finally:
            path.unlink()


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.source = self.tmp / "did_sessions.md"
        self.source.write_text("tresc", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_copy_lands_next_to_target_and_matches(self):
        target = self.tmp / "My Drive"
        target.mkdir()
        destination = sds.sync(self.source, target)
        self.assertEqual(destination.name, "did_sessions.md")
        self.assertEqual(destination.read_text(encoding="utf-8"), "tresc")

    def test_missing_target_dir_fails_instead_of_guessing(self):
        with self.assertRaises(SystemExit) as ctx:
            sds.sync(self.source, self.tmp / "nie-istnieje")
        self.assertEqual(ctx.exception.code, sds.EXIT_TARGET)

    def test_copy_overwrites_in_place(self):
        target = self.tmp / "My Drive"
        target.mkdir()
        (target / "did_sessions.md").write_text("stara zawartosc", encoding="utf-8")
        destination = sds.sync(self.source, target)
        self.assertEqual(destination.read_text(encoding="utf-8"), "tresc")

    def test_dry_run_writes_nothing(self):
        target = self.tmp / "My Drive"
        target.mkdir()
        destination = sds.sync(self.source, target, dry_run=True)
        self.assertFalse(destination.exists())

    def test_missing_source_fails_with_exit_3(self):
        with self.assertRaises(SystemExit) as ctx:
            sds.main([str(self.tmp / "nie-ma.md"), "--target", str(self.tmp)])
        self.assertEqual(ctx.exception.code, sds.EXIT_SOURCE)


class ResolveTargetTests(unittest.TestCase):
    def setUp(self):
        self._saved = dict(__import__("os").environ)

    def tearDown(self):
        __import__("os").environ.clear()
        __import__("os").environ.update(self._saved)

    def test_cli_beats_env_and_detection(self):
        import os

        os.environ["DID_SESSIONS_TARGET"] = r"G:\z-env"
        self.assertEqual(
            sds.resolve_target(r"D:\z-cli"), Path(r"D:\z-cli")
        )

    def test_env_beats_detection(self):
        import os

        os.environ["DID_SESSIONS_TARGET"] = r"G:\z-env"
        self.assertEqual(sds.resolve_target(None), Path(r"G:\z-env"))

    def test_detection_is_used_without_any_override(self):
        import os

        os.environ.pop("DID_SESSIONS_TARGET", None)
        original = sds.candidates
        sds.candidates = lambda: [Path(r"G:\My Drive")]
        try:
            self.assertEqual(sds.resolve_target(None), Path(r"G:\My Drive"))
        finally:
            sds.candidates = original

    def test_no_candidate_fails_with_target_exit(self):
        import os

        os.environ.pop("DID_SESSIONS_TARGET", None)
        original = sds.candidates
        sds.candidates = lambda: []
        try:
            with self.assertRaises(SystemExit) as ctx:
                sds.resolve_target(None)
            self.assertEqual(ctx.exception.code, sds.EXIT_TARGET)
        finally:
            sds.candidates = original

    def test_several_candidates_fail_rather_than_guess(self):
        import os

        os.environ.pop("DID_SESSIONS_TARGET", None)
        original = sds.candidates
        sds.candidates = lambda: [Path(r"G:\My Drive"), Path(r"H:\My Drive")]
        try:
            with self.assertRaises(SystemExit) as ctx:
                sds.resolve_target(None)
            self.assertEqual(ctx.exception.code, sds.EXIT_TARGET)
        finally:
            sds.candidates = original

    def test_several_candidates_pick_the_one_with_existing_file(self):
        import os

        os.environ.pop("DID_SESSIONS_TARGET", None)
        with tempfile.TemporaryDirectory() as tmp_dir:
            d1 = Path(tmp_dir) / "drive1"
            d2 = Path(tmp_dir) / "drive2"
            d1.mkdir()
            d2.mkdir()
            (d2 / "target.md").write_text("x", encoding="utf-8")
            original = sds.candidates
            sds.candidates = lambda: [d1, d2]
            try:
                chosen = sds.resolve_target(None, filename="target.md")
                self.assertEqual(chosen, d2)
            finally:
                sds.candidates = original


class DefaultsDriftTests(unittest.TestCase):
    """The .bat default and the module default must not drift apart."""

    def test_default_source_matches_bat_default(self):
        text = (ROOT / "scripts" / "did_sessions_drive.bat").read_text(encoding="utf-8")
        self.assertRegex(
            text, r'set OUT=scripts\\_scratch\\sessions\\02_products\\did_sessions\.md'
        )
        self.assertEqual(sds.DEFAULT_SOURCE.name, "did_sessions.md")

    def test_bat_calls_this_module(self):
        text = (ROOT / "scripts" / "did_sessions_drive.bat").read_text(encoding="utf-8")
        self.assertIn(r"python scripts\sync_did_sessions.py", text)


if __name__ == "__main__":
    unittest.main()
