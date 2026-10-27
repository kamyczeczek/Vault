import contextlib
import io
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
ROUTE_DIR = ROOT / "pipeline" / "06_reflect"
if str(ROUTE_DIR) not in sys.path:
    sys.path.insert(0, str(ROUTE_DIR))

import route  # noqa: E402


class RouteHealthTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.db = Path(self.tempdir.name) / "graph.db"
        conn = sqlite3.connect(self.db)
        conn.execute("CREATE TABLE nodes(id TEXT PRIMARY KEY, tags TEXT)")
        conn.executemany(
            "INSERT INTO nodes VALUES(?, ?)",
            [("n1", '["memory", "graph"]'), ("n2", '["other"]')],
        )
        conn.commit()
        conn.close()
        self.db_patch = patch.object(route, "DB", self.db)
        self.db_patch.start()

    def tearDown(self) -> None:
        self.db_patch.stop()
        self.tempdir.cleanup()

    def run_route(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with patch.object(sys, "argv", ["route.py", *argv]):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = route.main()
        return rc, out.getvalue(), err.getvalue()

    def test_live_tag_returns_ids_rc0(self) -> None:
        rc, out, err = self.run_route("--tag", "memory")
        self.assertEqual(rc, 0)
        self.assertIn("n1", out)
        self.assertEqual(err, "")

    def test_dead_tag_fails_loud_naming_the_tag(self) -> None:
        # W-AUDIT-4: an empty id list with rc=0 silently meant "no principles
        # apply". A dead routing key exits 2 with the tags on stderr.
        rc, out, err = self.run_route("--tag", "nosuchtag")
        self.assertEqual(rc, 2)
        self.assertEqual(out, "")
        self.assertIn("nosuchtag", err)

    def test_dead_tag_json_marks_dead(self) -> None:
        rc, out, err = self.run_route("--tag", "nosuchtag", "--json")
        self.assertEqual(rc, 2)
        body = json.loads(out)
        self.assertEqual(body["ids"], [])
        self.assertTrue(body["dead"])
        self.assertIn("nosuchtag", err)

    def test_dead_intersection_fails_even_if_each_tag_is_live(self) -> None:
        rc, out, err = self.run_route("--tag", "memory", "--tag", "other")
        self.assertEqual(rc, 2)
        self.assertIn("memory", err)

    def test_no_tags_is_not_a_dead_route(self) -> None:
        rc, out, _ = self.run_route("--limit", "5")
        self.assertEqual(rc, 0)
        self.assertIn("n1", out)


if __name__ == "__main__":
    unittest.main()
