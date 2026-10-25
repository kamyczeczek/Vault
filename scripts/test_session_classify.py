"""Stdlib tests for the card-only `--classify` judgment pass."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import session_digest as digest  # noqa: E402


def card(key, marker=None, raw=None, commits=None, flags=None, kind="marker",
         text=None, reason="no_evidence"):
    ending = {"kind": kind}
    if kind == "marker":
        ending.update({
            "marker": marker,
            "raw_line": raw if raw is not None else marker,
            "source_line": 3,
            "markers_version": "2026-10-22",
        })
    elif kind == "quote":
        ending["text"] = text
    else:
        ending["reason"] = reason
    return {
        "stable_key": key,
        "flags": flags or [],
        "commits": commits or [],
        "ending": ending,
        "card_sha256": "0" * 64,
    }


class ClassifyTests(unittest.TestCase):
    def payload(self, cards):
        return digest.classify_cards(cards, "coverage-sha")

    def sections(self, payload):
        return [j["section"] for j in payload["judgments"]]

    def test_open_thread_carries_evidence(self):
        out = self.payload([card("a:1", marker="blokada", raw="BLOKADA")])
        self.assertEqual(self.sections(out), ["open_threads"])
        ev = out["judgments"][0]["evidence"]
        self.assertEqual(ev["quote"], "BLOKADA")
        self.assertEqual(ev["source"], "body")
        self.assertEqual(out["judgments"][0]["supports"], "unverified_inference")

    def test_stop_gate_without_commits_is_not_a_decision(self):
        out = self.payload([card("a:1", marker="stop_gate", raw="STOP GATE")])
        self.assertNotIn("decisions", self.sections(out))

    def test_stop_gate_with_commits_is_a_decision(self):
        out = self.payload([card("a:1", marker="stop_gate", raw="STOP GATE",
                                 commits=["8da09f6"])])
        self.assertEqual(self.sections(out), ["decisions"])

    def test_contradiction_connects_open_and_committed_sessions(self):
        cards = [
            card("a:1", marker="blokada", raw="BLOKADA", flags=["f"]),
            card("a:2", marker="stop_gate", raw="STOP GATE", commits=["abc1234"],
                 flags=["f"]),
        ]
        out = self.payload(cards)
        self.assertIn("contradictions", self.sections(out))
        item = next(j for j in out["judgments"] if j["section"] == "contradictions")
        self.assertEqual(item["sessions"], ["a:1", "a:2"])
        self.assertEqual(item["flag"], "f")

    def test_missing_quote_is_not_checked_not_fabricated(self):
        out = self.payload([card("a:1", marker="blokada", raw="")])
        self.assertEqual(out["judgments"], [])
        self.assertEqual(out["not_checked"][0]["section"], "open_threads")
        self.assertTrue(out["not_checked"])

    def test_ids_are_deterministic_and_input_order_independent(self):
        cards = [
            card("a:2", marker="blokada", raw="BLOKADA"),
            card("a:1", marker="blokada", raw="BLOKADA"),
        ]
        left = self.payload(cards)
        right = self.payload(list(reversed(cards)))
        self.assertEqual(left["judgments"], right["judgments"])
        self.assertEqual([j["id"] for j in left["judgments"]], ["j-0001", "j-0002"])

    def test_never_promotes(self):
        out = self.payload([card("a:1", marker="blokada", raw="BLOKADA")])
        self.assertEqual(out["judgment_status"], "candidate")
        self.assertIsNone(out["promotion"])
        self.assertEqual(out["classifier"]["model_calls"], 0)
        self.assertEqual(out["classifier"]["reads"], "cards_only")


if __name__ == "__main__":
    unittest.main(verbosity=2)
