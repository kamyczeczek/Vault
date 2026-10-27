"""Contract tests for discuss.py — the file-is-the-conversation convention.

These are the acceptance conditions candidate idea-session-001 promised and
never received, plus the negative controls it named in its own falsification
clause: the counter side must survive, a missing graph must not masquerade as
a silent corpus, and a decision without an attack must not stage.
"""
import argparse
import os
import json
import re
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import discuss  # noqa: E402


def _fm(**kw):
    base = {"id": "t", "thesis": "T", "stance": "synth", "status": "open",
            "run_id": "r", "graph_generation": "g", "sid": "s"}
    base.update(kw)
    return base


def _claim(cid="c1", text="A surface with no artifact decays",
           support=("chunk_a",), counter=("chunk_r",)):
    return {"id": cid, "text": text, "support": list(support),
            "counter": list(counter)}


class ParseRenderRoundTripTests(unittest.TestCase):
    def test_claim_block_round_trips_both_sides(self):
        body = "## claims\n\n" + discuss._claim_block(_claim())
        parsed = discuss._parse_claims(body)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["support"], ["chunk_a"])
        # The regression that killed the old workflow: counters are KEPT.
        self.assertEqual(parsed[0]["counter"], ["chunk_r"])
        self.assertFalse(parsed[0]["counter_empty"])

    def test_empty_counter_is_explicit_unrefuted_not_dropped_silently(self):
        body = discuss._claim_block(_claim(counter=()))
        parsed = discuss._parse_claims(body)
        self.assertIn("unrefuted", body)
        self.assertEqual(parsed[0]["counter"], [])
        self.assertTrue(parsed[0]["counter_empty"])

    def test_note_survives_render(self):
        body = discuss._claim_block(_claim())
        body = body.replace("- counter:", "- note: librarian says corpus is thin\n- counter:")
        self.assertEqual(discuss._parse_claims(body)[0]["note"],
                         "librarian says corpus is thin")

    def test_upsert_replaces_in_place_not_duplicates(self):
        body = "## claims\n\n" + discuss._claim_block(_claim())
        body = discuss._upsert_claim(body, _claim(text="revised claim"))
        self.assertEqual(len(discuss._parse_claims(body)), 1)
        self.assertEqual(discuss._parse_claims(body)[0]["text"], "revised claim")

    def test_append_section_creates_then_appends(self):
        body = "## claims\n\n"
        body = discuss._append_section(body, "red-team", "first attack")
        body = discuss._append_section(body, "red-team", "second attack")
        self.assertEqual(body.count("## red-team"), 1)
        # each entry is a `### <ts>` header plus its prose line
        lines = [ln for ln in discuss._parse_section(body, "red-team") if ln]
        self.assertEqual(sum(1 for ln in lines if ln.startswith("### ")), 2)
        self.assertIn("second attack", body)

    def test_decision_parses_value_why_next(self):
        body = "## decision\n- value: unresolved\n- why: gates not run\n- next: measure coverage\n"
        d = discuss._parse_decision(body)
        self.assertEqual(d["value"], "unresolved")
        self.assertEqual(d["next"], "measure coverage")


class _Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class DiscussTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ideas = Path(self.tmp.name) / "ideas"
        self.ideas.mkdir()
        self.cands = Path(self.tmp.name) / "cands"
        self.cands.mkdir()
        self.p = self.ideas / "t.md"
        p = mock.patch.multiple(
            discuss,
            IDEAS=self.ideas, CANDIDATES=self.cands, ROOT=Path(self.tmp.name),
        )
        p.start()
        self.addCleanup(p.stop)
        for fn in ("start_session", "append_event", "finish_session",
                   "verify_chain", "emit", "new_run_id", "generation_id"):
            self.addCleanup(mock.patch.object(discuss, fn, mock.Mock(
                **{"return_value": "sid" if "session" in fn else "id"}), create=True)
                .stop)
        mock.patch.object(discuss, "start_session", mock.Mock(return_value="s"),
                          create=True).start()
        mock.patch.object(discuss, "append_event", mock.Mock(return_value="e"),
                          create=True).start()
        mock.patch.object(discuss, "finish_session", mock.Mock(), create=True).start()
        mock.patch.object(discuss, "verify_chain", mock.Mock(return_value=(True, "ok")),
                          create=True).start()
        mock.patch.object(discuss, "emit", mock.Mock(), create=True).start()

    def _write(self, body, fm=None):
        fm = fm or _fm()
        discuss._write(self.p, fm, body)

    def _run(self, fn, **kw):
        fn(_Args(path=None, **kw))


class ClaimRetrievalTests(DiscussTestCase):
    """The two-sided contract, and the graph-must-exist guard."""

    def _query(self, support, counter):
        def q(question, limit=5, **kw):
            stem = support if "evidence" in question else counter
            return [{"id": f"{stem}_{i}"} for i in range(limit)]
        return q

    def test_claim_persists_counter_ids(self):
        self._write("## claims\n\n")
        q = self._query("chunk_s", "chunk_c")
        with mock.patch("ask.query", q), \
             mock.patch.object(discuss, "_graph_available", lambda: True), \
             mock.patch.object(discuss, "_record"):
            self._run(discuss.cmd_claim, text=["a surface decays"])
        st = discuss._parse(self.p)
        self.assertEqual(st["claims"][0]["support"], ["chunk_s_0", "chunk_s_1", "chunk_s_2"])
        # THE regression test. idea_session.py:147 wrote "counter": [].
        self.assertEqual(st["claims"][0]["counter"], ["chunk_c_0", "chunk_c_1", "chunk_c_2"])

    def test_missing_graph_refuses_instead_of_reporting_silence(self):
        self._write("## claims\n\n")
        with mock.patch.object(discuss, "_graph_available", lambda: False), \
             mock.patch.object(discuss, "_record"):
            with self.assertRaises(discuss.DiscussError) as ctx:
                self._run(discuss.cmd_claim, text=["x"])
        self.assertIn("graph.db missing", str(ctx.exception))
        self.assertEqual(discuss._parse(self.p)["claims"], [])

    def test_retrieval_failure_raises_not_silently_empty(self):
        with mock.patch("ask.query", mock.Mock(side_effect=RuntimeError("boom"))), \
             mock.patch.object(discuss, "_graph_available", lambda: True), \
             mock.patch.object(discuss, "_record"):
            with self.assertRaises(discuss.DiscussError):
                self._run(discuss.cmd_claim, text=["x"])


class DecisionGateTests(DiscussTestCase):
    def _seed(self, claims=True, attack=True, decision=None):
        body = "## claims\n\n"
        if claims:
            body += discuss._claim_block(_claim())
        if attack:
            body += "## red-team\n- attack: gate not run every session\n"
        if decision:
            body += (f"## decision\n- value: {decision}\n"
                     "- why: because\n- next: experiment E\n")
        self._write(body)

    def test_stage_requires_red_team_turn(self):
        self._seed(attack=False, decision="unresolved")
        with self.assertRaises(discuss.DiscussError) as c:
            self._run(discuss.cmd_stage, rule="R", target="T")
        self.assertIn("red-team", str(c.exception))

    def test_stage_requires_decision(self):
        self._seed(decision=None)
        with self.assertRaises(discuss.DiscussError) as c:
            self._run(discuss.cmd_stage, rule="R", target="T")
        self.assertIn("no decision", str(c.exception))

    def test_learned_decision_may_not_stage(self):
        """The whole point: not every discussion yields a rule."""
        self._seed(decision="learned")
        with self.assertRaises(discuss.DiscussError) as c:
            self._run(discuss.cmd_stage, rule="R", target="T")
        self.assertIn("only an 'unresolved'", str(c.exception))

    def test_unresolved_without_next_may_not_stage(self):
        body = ("## claims\n\n" + discuss._claim_block(_claim())
                + "## red-team\n- attack: a\n"
                + "## decision\n- value: unresolved\n- why: w\n")
        self._write(body)
        with self.assertRaises(discuss.DiscussError) as c:
            self._run(discuss.cmd_stage, rule="R", target="T")
        self.assertIn("next experiment", str(c.exception))

    def test_unresolved_with_next_stages_both_sides(self):
        self._seed(decision="unresolved")
        self._run(discuss.cmd_stage, rule="R", target="T")
        rows = [json.loads(l) for l in
                (self.cands / "discuss_t.jsonl").read_text().splitlines()]
        self.assertEqual(rows[0]["state"], "proposed")
        self.assertIn("`chunk_a`", rows[0]["Evidence"])
        # Both sides reach the candidate — the old one never could.
        self.assertIn("`chunk_r`", rows[0]["Evidence"])
        self.assertEqual(rows[0]["provenance"]["graph_generation"], "g")

    def test_stage_refuses_when_no_evidence(self):
        self._seed(claims=False, decision="unresolved")
        with self.assertRaises(discuss.DiscussError) as c:
            self._run(discuss.cmd_stage, rule="R", target="T")
        self.assertIn("no claims", str(c.exception))


class FileIsStateTests(DiscussTestCase):
    """No slug threading: resolution defaults to the newest file, and a
    hand-edited file must still parse."""

    def test_resolve_defaults_to_latest_file(self):
        self.p.write_text(discuss._render(_fm(), "## claims\n\n"), encoding="utf-8")
        self.assertEqual(discuss._resolve(None), self.p)

    def test_resolve_missing_path_raises(self):
        with self.assertRaises(discuss.DiscussError):
            discuss._resolve("nope.md")

    def test_human_edited_file_still_parses(self):
        body = ("# Title\n\n## claims\n\n"
                "## c1 — hand written claim\n"
                "- support: `x_1`\n- counter: (none — unrefuted)\n\n"
                "## decision\n- value: wrong\n- why: it was simply false\n")
        self._write(body)
        st = discuss._parse(self.p)
        self.assertEqual(st["claims"][0]["text"], "hand written claim")
        self.assertTrue(st["claims"][0]["counter_empty"])
        self.assertEqual(st["decision"]["value"], "wrong")

    def test_missing_frontmatter_raises(self):
        self.p.write_text("# no frontmatter\n", encoding="utf-8")
        with self.assertRaises(discuss.DiscussError) as c:
            discuss._parse(self.p)
        self.assertIn("frontmatter", str(c.exception))
class LedgerIntegrityTests(DiscussTestCase):
    """A seal only means something if the chain is read before it is honoured.

    `stage` and `close` both call verify_chain(). Discarding its boolean and
    printing the message beside "session sealed" is how a tampered ledger gets
    stamped as verified.
    """

    def _seed(self):
        body = "## claims\n\n" + discuss._claim_block(_claim())
        body += "## red-team\n- attack: gate not run every session\n"
        body += "## decision\n- value: unresolved\n- why: because\n- next: experiment E\n"
        self._write(body)

    def test_stage_refuses_when_chain_is_broken(self):
        self._seed()
        with mock.patch.object(discuss, "verify_chain", return_value=(False, "broken link at 3")), \
             mock.patch.object(discuss, "finish_session") as fin:
            with self.assertRaises(discuss.DiscussError) as c:
                self._run(discuss.cmd_stage, rule="R", target="T")
        self.assertIn("chain", str(c.exception).lower())
        # The point of the test: a broken chain must never reach a terminal state.
        fin.assert_not_called()

    def test_stage_still_seals_when_chain_is_intact(self):
        self._seed()
        with mock.patch.object(discuss, "verify_chain", return_value=(True, "ok")), \
             mock.patch.object(discuss, "finish_session") as fin:
            self._run(discuss.cmd_stage, rule="R", target="T")
        fin.assert_called_once()

    def test_close_refuses_when_chain_is_broken(self):
        self._seed()
        with mock.patch.object(discuss, "verify_chain", return_value=(False, "broken at 1")), \
             mock.patch.object(discuss, "finish_session") as fin:
            with self.assertRaises(discuss.DiscussError) as c:
                self._run(discuss.cmd_close)
        self.assertIn("chain", str(c.exception).lower())
        fin.assert_not_called()
        # left open, not silently closed
        self.assertNotEqual(discuss._parse(self.p)["fm"].get("status"), "closed")


class InboxExemptionTests(unittest.TestCase):
    """`INBOX/ideas/` holds arguments, not research; intake must skip it.

    stages/04_reflect/CONTEXT.md states this as a contract, so it gets a test
    rather than good intentions. Both tools used to skip ideas/ only by
    accident (a non-recursive glob), and `ingest --file` had no exemption at
    all - a one-line invocation would have cut an argument into the corpus.
    """

    def setUp(self):
        import check_research_quality
        import ingest
        self.ingest = ingest
        self.rq = check_research_quality
        self.idea = ROOT / "INBOX" / "ideas" / "dealing-with-growing-project-entropy.md"
        self.paper = ROOT / "CONTEXT.md"

    def test_idea_file_is_recognised_by_both_tools(self):
        if not self.idea.exists():
            self.skipTest("no migrated discussion on disk")
        self.assertTrue(self.ingest.is_idea_file(self.idea))
        self.assertTrue(self.rq.is_idea_file(self.idea))

    def test_ordinary_file_is_not_mistaken_for_an_idea(self):
        self.assertFalse(self.ingest.is_idea_file(self.paper))
        self.assertFalse(self.rq.is_idea_file(self.paper))

    def test_ingest_refuses_an_explicitly_named_idea_file(self):
        """--file bypasses the directory scan, so it needs its own guard."""
        if not self.idea.exists():
            self.skipTest("no migrated discussion on disk")
        with mock.patch.object(sys, "argv", ["ingest.py", "--file", str(self.idea)]):
            self.assertEqual(self.ingest.main(), 1)

    def test_ingest_dry_scan_skips_idea_files(self):
        """The directory scan must never hand a discussion to the chunker."""
        if not self.idea.exists():
            self.skipTest("no migrated discussion on disk")
        seen = []
        with mock.patch.object(sys, "argv", ["ingest.py", "--dry"]), \
             mock.patch.object(self.ingest, "ingest_file",
                               side_effect=lambda p, **kw: (seen.append(p) or [])):
            self.ingest.main()
        for path in seen:
            self.assertFalse(self.ingest.is_idea_file(path),
                             f"dry run tried to ingest a discussion: {path}")
        self.assertNotIn(self.idea.resolve(), [p.resolve() for p in seen])

    def test_quality_gate_ignores_idea_files(self):
        """Q12 grades intake quality; a discussion is not intake."""
        if not self.idea.exists():
            self.skipTest("no migrated discussion on disk")
        graded = []
        with mock.patch.object(self.rq, "check_file",
                               side_effect=lambda p, *args, **kw: graded.append(p) or []), \
             mock.patch.object(self.rq, "load_existing_corpus_ids", return_value=set()):
            self.rq.main()
        for path in graded:
            self.assertFalse(self.rq.is_idea_file(path),
                             f"Q12 graded a discussion as research: {path}")

class DecisionOverwriteTests(DiscussTestCase):
    """A decision is a record. `decide` must not silently replace one.

    Found live: a second `decide learned` overwrote an honest
    `unresolved` and took its --next experiment with it. Since the file is
    the only state, that was unrecoverable.
    """

    def _seed(self, value="unresolved"):
        body = "## claims\n\n" + discuss._claim_block(_claim())
        body += "## red-team\n- attack: gates are not evidence\n"
        body += (f"## decision\n- value: {value}\n- why: the honest reason\n"
                 "- next: measure the echo rate\n")
        self._write(body)

    def test_decide_refuses_to_overwrite_without_force(self):
        self._seed()
        with self.assertRaises(discuss.DiscussError) as c:
            self._run(discuss.cmd_decide, value="learned", why=["because"],
                      force=False, **{"next": None})
        self.assertIn("already recorded", str(c.exception))
        # and the record survives the refusal
        d = discuss._parse(self.p)["decision"]
        self.assertEqual(d["value"], "unresolved")
        self.assertEqual(d["why"], "the honest reason")
        self.assertEqual(d["next"], "measure the echo rate")

    def test_decide_force_replaces_deliberately(self):
        self._seed()
        self._run(discuss.cmd_decide, value="learned", why=["revised"],
                  force=True, **{"next": None})
        d = discuss._parse(self.p)["decision"]
        self.assertEqual(d["value"], "learned")
        self.assertIsNone(d["next"])

    def test_decide_force_preserves_the_rationale_beside_it(self):
        # Observed live: `decide --force` deleted 73 lines of `## decision
        # rationale` because the heading pattern also matched it. The rationale
        # is the durable half of the record -- the value/why/next triple is
        # regenerable, the reasoning is not.
        body = "## claims\n\n" + discuss._claim_block(_claim())
        body += "## red-team\n- attack: gates are not evidence\n"
        body += ("## decision\n- value: unresolved\n- why: imported, not measured\n"
                 "- next: run one scoped loop\n")
        body += ("## decision rationale\n\n### why this thesis was raised\n"
                 "Because the corpus says loops need a deterministic exit.\n"
                 "### what would make this wrong\nA loop that converges on judgement.\n")
        self._write(body)
        self._run(discuss.cmd_decide, value="unresolved", why=["measured at b5e5083"],
                  force=True, next="re-run against a gate a dumb worker cannot satisfy")
        after = self.p.read_text(encoding="utf-8")
        self.assertIn("## decision rationale", after)
        self.assertIn("Because the corpus says loops need a deterministic exit.",
                      after)
        self.assertIn("A loop that converges on judgement.", after)
        # exactly one bare decision block, and it is the new one
        self.assertEqual(len(re.findall(r"^## decision\s*$", after, re.M)), 1)
        d = discuss._parse(self.p)["decision"]
        self.assertEqual(d["value"], "unresolved")
        self.assertEqual(d["why"], "measured at b5e5083")
        self.assertIn("b5e5083", after)

    def test_duplicate_decision_blocks_collapse_to_one(self):
        # A hand-edited file can hold two `## decision` blocks (this repo did,
        # briefly, while a patch helper was mid-fix). Leaving the second keeps
        # a contradictory decision in the file while the parser reports the
        # new one.
        body = "## claims\n\n" + discuss._claim_block(_claim())
        body += "## decision\n- value: unresolved\n- why: first\n"
        body += "## decision\n- value: learned\n- why: second\n"
        body += "## decision rationale\n\nkeep this reasoning\n"
        self._write(body)
        self._run(discuss.cmd_decide, value="wrong", why=["refuted"],
                  force=True, **{"next": None})
        after = self.p.read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"^## decision\s*$", after, re.M)), 1)
        self.assertIn("keep this reasoning", after)
        self.assertNotIn("- why: first", after)
        self.assertNotIn("- why: second", after)
        self.assertEqual(discuss._parse(self.p)["decision"]["why"], "refuted")

    def test_rationale_alone_cannot_impersonate_a_decision(self):
        # If the machine block is missing, a rationale heading must not be
        # parsed as one: `- value:` prose is not a record.
        body = "## claims\n\n" + discuss._claim_block(_claim())
        body += "## decision rationale\n\n- value: unresolved\n- why: prose only\n"
        self._write(body)
        self.assertIsNone(discuss._parse(self.p)["decision"])
        self._run(discuss.cmd_decide, value="wrong", why=["refuted"], force=False,
                  **{"next": None})
        self.assertIn("## decision rationale", self.p.read_text(encoding="utf-8"))

    def test_first_decide_is_not_blocked(self):
        self._write("## claims\n\n" + discuss._claim_block(_claim()))
        self._run(discuss.cmd_decide, value="wrong", why=["refuted"],
                  force=False, **{"next": None})
        self.assertEqual(discuss._parse(self.p)["decision"]["value"], "wrong")



class TargetingTests(unittest.TestCase):
    """`-p FILE.md` must work, and a filename in prose must be refused.

    The path used to be a trailing positional declared after `nargs='*'`
    text. argparse therefore absorbed it: `attack "..." old.md` recorded a
    red-team turn whose prose ended in "old.md" and edited the most recent
    idea file, reporting success. Every command defaults to the latest file,
    so a discussion you cannot return to is a silent one.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ideas = Path(self.tmp.name) / "ideas"
        self.ideas.mkdir()
        p = mock.patch.multiple(discuss, IDEAS=self.ideas,
                                ROOT=Path(self.tmp.name))
        p.start()
        self.addCleanup(p.stop)
        self.newest = self.ideas / "b-newest.md"
        self.older = self.ideas / "a-older.md"
        for f in (self.older, self.newest):
            discuss._write(f, _fm(id=f.stem),
                           "## claims\n\n" + discuss._claim_block(_claim()))
        now = time.time()
        os.utime(self.older, (now - 60, now - 60))
        os.utime(self.newest, (now, now))

    def _args(self, **kw):
        base = {"path": None}
        base.update(kw)
        return argparse.Namespace(**base)

    def test_resolve_defaults_to_the_most_recent_file(self):
        self.assertEqual(discuss._resolve(None), self.newest)

    def test_path_argument_selects_an_older_file(self):
        discuss.cmd_stance(self._args(path=str(self.older), name="red-teamer"))
        self.assertIn("stance: red-teamer", self.older.read_text(encoding="utf-8"))
        self.assertIn("stance: synth", self.newest.read_text(encoding="utf-8"))

    def test_trailing_md_in_prose_is_refused_not_swallowed(self):
        with self.assertRaises(discuss.DiscussError) as c:
            discuss.cmd_attack(self._args(text=["gates", "pass", "a-older.md"]))
        self.assertIn("--path", str(c.exception))
        with self.assertRaises(discuss.DiscussError) as c:
            discuss.cmd_decide(self._args(value="wrong", why=["refuted",
                                                            "a-older.md"],
                                         **{"next": None, "force": False}))
        self.assertIn("--path", str(c.exception))
        # neither file was touched
        for f in (self.older, self.newest):
            body = f.read_text(encoding="utf-8")
            self.assertNotIn("red-team", body)
            self.assertNotIn("## decision", body)

    def test_prose_mentioning_md_is_still_allowed(self):
        # only a TRAILING filename is suspicious; a claim may cite a file.
        discuss.cmd_attack(self._args(text=["a-new.md", "is", "not", "proof"]))
        self.assertIn("is not proof", self.newest.read_text(encoding="utf-8"))

    def test_cli_parses_a_trailing_path_as_an_option(self):
        ap = argparse.ArgumentParser()
        sub = ap.add_subparsers(dest="command", required=True)
        sp = sub.add_parser("decide")
        discuss._path(sp)
        sp.add_argument("value", choices=discuss.DECISIONS)
        sp.add_argument("why", nargs="*")
        sp.add_argument("--next")
        sp.add_argument("--force", action="store_true")
        ns = ap.parse_args(["decide", "unresolved", "measured", "locally",
                            "--next", "re-run", "--force", "-p", "a-older.md"])
        self.assertEqual(ns.path, "a-older.md")
        self.assertEqual(ns.why, ["measured", "locally"])
        self.assertTrue(ns.force)


if __name__ == "__main__":
    unittest.main()
