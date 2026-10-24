"""Stdlib tests for the shared session fact extractors."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
import session_facts as facts  # noqa: E402


class SessionFactsTests(unittest.TestCase):
    def test_duration(self):
        session = SimpleNamespace(created_at="2026-01-01 10:00:00",
                                  updated_at="2026-01-01 10:02:05")
        self.assertEqual(facts.duration(session), "2m5s")

    def test_goal_first_user_prompt(self):
        body = "## [system]\nignore\n## [user]\nZrób X.\n## [assistant]\nOK\n"
        self.assertEqual(facts.extract_goal(body), {"kind": "prompt", "text": "Zrób X."})

    def test_goal_unsupported_agent(self):
        self.assertEqual(facts.extract_goal("## [user]\nX\n", "goose"),
                         {"kind": "none", "reason": facts.REASON_AGENT_UNSUPPORTED})

    def test_marker_standalone(self):
        body = "## [assistant]\nSTOP GATE\n"
        ending = facts.extract_ending(body)
        self.assertEqual(ending["kind"], "marker")
        self.assertEqual(ending["marker"], "stop_gate")
        self.assertEqual(ending["source_line"], 2)

    def test_marker_inside_fence_is_not_marker(self):
        body = "## [assistant]\n```\nSTOP GATE\n```\n"
        ending = facts.extract_ending(body)
        self.assertEqual(ending["kind"], "quote")
        self.assertEqual(ending["text"], "```")

    def test_marker_with_prefix_is_not_marker(self):
        body = "## [assistant]\n> STOP GATE\n"
        ending = facts.extract_ending(body)
        self.assertEqual(ending["kind"], "none")

    def test_flags_dedup(self):
        body = "handoff/flags/a.md handoff/flags/a.md handoff/flags/b.md"
        self.assertEqual(facts.flag_ids(body), ["a", "b"])
        self.assertEqual(facts.flag_id(body), "b")

    def test_commits_only_git_commit_lines(self):
        body = "[main abc1234]\ncommit deadbee\nabc1234\n"
        self.assertEqual(facts.extract_commits(body), ["abc1234", "deadbee"])

    def test_tests_last_five(self):
        body = "\n".join(f"{n} passed in 0.1s" for n in range(1, 8))
        self.assertEqual(facts.extract_tests(body),
                         ["3 passed in 0.1s", "4 passed in 0.1s", "5 passed in 0.1s",
                          "6 passed in 0.1s", "7 passed in 0.1s"])

    def test_files_from_write_inputs(self):
        body = (
            '> **tool** `write` · completed\n'
            '> in: `{"filePath":"scripts/a.py","content":"x"}`\n'
            "> out: `ok`\n"
        )
        self.assertEqual(facts.extract_files(body), ["scripts/a.py"])

    def test_losses(self):
        body = "artifact://x Some lines truncated to 768 bytes …[+2 zn.]… Superseded by a newer read"
        self.assertEqual(facts.extract_losses(body),
                         {"trunc": 1, "artifact": 1, "ext768": 1, "superseded": 1})

    def test_normalize(self):
        self.assertEqual(facts.normalize_text("a\t b\r\nc"), "a b\nc")


if __name__ == "__main__":
    unittest.main(verbosity=2)
