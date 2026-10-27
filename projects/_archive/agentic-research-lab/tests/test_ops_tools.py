"""Contracts for the ops tools (warn, eval_traces, skill_usage, eval_insights,
link_repair, cost_ledger, check_dead_code).

Human-authored specs: each test pins behavior an agent must not silently
change. Agent-generated tests assert whatever the code happens to do;
these assert what the workspace requires, with the reason inline.
"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import warn  # noqa: E402
import eval_traces  # noqa: E402
import skill_usage  # noqa: E402
import cost_ledger  # noqa: E402
import eval_insights  # noqa: E402


class WarnTests(unittest.TestCase):
    """warn.py retrieves recorded failures, never generates lessons."""

    def test_repair_task_surfaces_ledger_defect(self) -> None:
        rows = warn.warnings_for("repair quarantined graph defect evidence", limit=3)
        ids = [r["id"] for r in rows]
        self.assertIn("defect-8a9b18b65914db3e", ids,
                      "the quarantined graph-consistency defect must surface")

    def test_warnings_are_pointers(self) -> None:
        for r in warn.warnings_for("agent evaluation workflow", limit=5):
            self.assertIn("source", r)
            self.assertIn("matched", r)
            self.assertNotIn("remediation", r,
                             "warnings point; remediation lives in RepairProposals")

    def test_deterministic_order(self) -> None:
        a = warn.warnings_for("graph defect quarantine", limit=3)
        b = warn.warnings_for("graph defect quarantine", limit=3)
        self.assertEqual(a, b)


class EvalTracesTests(unittest.TestCase):
    """eval_traces scores shape honestly: orphans count, even ours."""

    def test_orphan_decision_detected(self) -> None:
        rows = [
            {"kind": "graph_decision", "run_id": "r",
             "decision": {"use_graph": True}},
        ]
        out = eval_traces.score(rows)
        self.assertEqual(out["runs"]["r"]["orphan_decisions"], 1)

    def test_retrieval_without_decision_flagged(self) -> None:
        rows = [{"kind": "retrieval", "run_id": "r"}]
        out = eval_traces.score(rows)
        self.assertTrue(out["runs"]["r"]["no_decision"])

    def test_closed_loop_scores_clean(self) -> None:
        rows = [
            {"kind": "graph_decision", "run_id": "r",
             "decision": {"use_graph": True}},
            {"kind": "retrieval", "run_id": "r"},
            {"kind": "artifact", "run_id": "r"},
        ]
        out = eval_traces.score(rows)
        run = out["runs"]["r"]
        self.assertEqual((run["orphan_decisions"], run["dry_retrievals"]), (0, 0))
        self.assertEqual(out["aggregate"]["failure_rate"], 0)


class SkillUsageTests(unittest.TestCase):
    """The audit must not count prose as skill use (C-5 lesson applied)."""

    def test_corpus_excluded(self) -> None:
        files = [str(p) for p in skill_usage.project_files()]
        self.assertTrue(files)
        self.assertFalse(any(f.startswith("knowledge") for f in files),
                         "corpus prose is not skill usage")
        self.assertFalse(any(f.startswith("docs") for f in files),
                         "docs prose is not skill usage")

    def test_router_and_contracts_scanned(self) -> None:
        names = [p.name for p in skill_usage.project_files()]
        self.assertIn("skill_router.py", names)
        self.assertIn("local_skills.md", names)


class CostLedgerTests(unittest.TestCase):
    """Blanks mean unlogged, never zero. The ledger refuses to lie."""

    def test_uncomputable_not_zero(self) -> None:
        rows = [{"insight_id": "x", "basis": "provisional-n1",
                 "token_cost_usd": "", "eval_compute_usd": "",
                 "human_cost_usd": "", "delta": "0.192", "issues_closed": "1"}]
        (summary,) = cost_ledger.summarize(rows)
        self.assertIn("UNCOMPUTABLE", summary["total_cost_usd"])
        self.assertNotEqual(summary["total_cost_usd"], 0)

    def test_estimated_marker_not_silent(self) -> None:
        v, flag = cost_ledger.num({"eval_runs": "~10"}, "eval_runs")
        self.assertIsNone(v)
        self.assertEqual(flag, "estimated")


class FixLinkageTests(unittest.TestCase):
    """Correction edges are human-verified links over real ledger data."""

    def test_linkage_rates_bounded(self) -> None:
        out = eval_insights.fix_linkage()
        for key in ("fix_linkage_rate", "edge_linkage_rate"):
            self.assertGreaterEqual(out[key], 0)
            self.assertLessEqual(out[key], 1)
        self.assertGreaterEqual(out["quarantined_entries"], 2)


if __name__ == "__main__":
    unittest.main()
