import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import score_ablation as sc  # noqa: E402

KNOWN = {"00_alpha", "01_beta", "02_gamma", "03_delta"}
TASKS = {
    "t1": {"oracle_ids": ["00_alpha"]},
    "t2": {"oracle_ids": ["01_beta"]},
}


def ans(*cites: str) -> str:
    return "\n".join(f"Claim proven. Chunk id: `{c}`" for c in cites)


class ExtractTests(unittest.TestCase):
    def test_finds_ids_in_order(self) -> None:
        # derived from CHUNK_LINE_RE spec: `Chunk id: `NN_slug`` lines
        got = sc.extract_citations(ans("00_alpha", "01_beta"))
        self.assertEqual(got, ["00_alpha", "01_beta"])

    def test_ignores_prose_without_backticks(self) -> None:
        self.assertEqual(sc.extract_citations("Chunk id: 00_alpha genoemd"), [])


class SolvedTests(unittest.TestCase):
    def test_solved_needs_oracle_and_all_resolve(self) -> None:
        s = sc.score_answer(ans("00_alpha", "02_gamma"), {"00_alpha"}, KNOWN)
        self.assertTrue(s["solved"])

    def test_hallucinated_id_breaks_solved(self) -> None:
        s = sc.score_answer(ans("00_alpha", "99_nonexistent"), {"00_alpha"}, KNOWN)
        self.assertFalse(s["solved"])
        self.assertEqual(s["unresolved"], ["99_nonexistent"])

    def test_no_citation_is_not_solved(self) -> None:
        s = sc.score_answer("No citations here.", {"00_alpha"}, KNOWN)
        self.assertFalse(s["solved"])


class ResolveEligibilityTests(unittest.TestCase):
    def test_below_threshold_excluded(self) -> None:
        # flag: resolve rate only on tasks with >=3 citations
        s = sc.score_answer(ans("00_alpha", "02_gamma"), {"00_alpha"}, KNOWN)
        self.assertFalse(s["resolve_eligible"])

    def test_at_threshold_included(self) -> None:
        s = sc.score_answer(ans("00_alpha", "02_gamma", "03_delta"), {"00_alpha"}, KNOWN)
        self.assertTrue(s["resolve_eligible"])


class ConcentrationTests(unittest.TestCase):
    def test_definition_a_top3_over_all_cites(self) -> None:
        # A with fallback: (cites to arm top-3)/(all cites); t2 cites nothing
        records = [
            {"task_id": "t1", "answer": ans("00_alpha", "00_alpha", "02_gamma",
                                            "03_delta", "01_beta"), "queries": []},
            {"task_id": "t2", "answer": "Abstains.", "queries": []},
        ]
        agg = sc.score_arm(records, TASKS, KNOWN)
        # top-3 = alpha(2), gamma(1), delta(1) -> 4/5
        self.assertAlmostEqual(agg["concentration"], 4 / 5)
        self.assertEqual(agg["concentration_excluded_zero_cite"], 1)
        # resolve: t1 eligible (5 cites, all resolve) -> 1.0; t2 excluded
        self.assertAlmostEqual(agg["resolve_rate"], 1.0)
        self.assertEqual(agg["resolve_excluded_tasks"], 1)


if __name__ == "__main__":
    unittest.main()
