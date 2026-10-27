import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import check_corpus_health  # noqa: E402


CLEAN = """---
source: "A Clean Paper (2020)"
tags: [retrieval]
---

Causal inference in statistics is a well established discipline. It asks
what would happen if we intervened on a variable, and it distinguishes
correlation from causation using counterfactual reasoning.
"""

# The defect class: whitespace dropped inside words by lossy extraction. The
# collapsed page below is verbatim from the real corpus.
CORRUPT = """---
source: "A Paper (2020)"
tags: [retrieval]
---

purposeofcopyrightistoencouragewritersandartiststoproducethecreativeworksthatenrich
"""

LOWERCASE_ARTIFACT = (
    "purposeofcopyrightistoencouragewritersandartiststoproducethecreativeworksthatenrich"
)


class SuspiciousRunTests(unittest.TestCase):
    def test_clean_prose_raises_nothing(self) -> None:
        self.assertEqual(check_corpus_health.suspicious_runs(CLEAN), [])

    def test_lowercase_glue_is_caught(self) -> None:
        self.assertIn(LOWERCASE_ARTIFACT, check_corpus_health.suspicious_runs(CORRUPT))

    def test_legitimate_camel_case_identifiers_are_not_artifacts(self) -> None:
        # Regression: the old gate's CamelCase signal flagged these and reported
        # 6,401/10,364 chunks (62%) damaged instead of the true 476 (4.6%).
        # They are real identifiers from *Refactoring* and *Beginning Software
        # Engineering*, not extraction damage.
        text = ("public String basePrice; daysOverdrawn frequentRenterPoints "
                "outstandingBalance customerStatement rentalRecord")
        self.assertEqual(check_corpus_health.suspicious_runs(text), [])

    def test_real_long_english_words_are_not_artifacts(self) -> None:
        text = ("counterfactual instrumentation misunderstanding "
                "incomprehensibilities antidisestablishmentarianism")
        self.assertEqual(check_corpus_health.suspicious_runs(text), [])

    def test_acronyms_and_digits_are_not_artifacts(self) -> None:
        self.assertEqual(check_corpus_health.suspicious_runs("The FTS5 INDEX and JSON API."), [])

    def test_hyphenated_and_underscored_tokens_are_not_artifacts(self) -> None:
        self.assertEqual(
            check_corpus_health.suspicious_runs("a well-known counterfactual_estimate"), [])

    def test_short_lowercase_words_are_not_artifacts(self) -> None:
        self.assertEqual(check_corpus_health.suspicious_runs("the quick brown fox"), [])

    def test_signal_needs_no_corpus_frequency(self) -> None:
        # The structural rule must behave identically on a two-chunk fixture and
        # on the 10,364-chunk corpus; that is what the frequency heuristic could
        # not do, since it punished ordinary rare technical vocabulary.
        self.assertIn(LOWERCASE_ARTIFACT, check_corpus_health.suspicious_runs(CORRUPT))
        self.assertEqual(check_corpus_health.suspicious_runs(CLEAN), [])


class ScanBySourceTests(unittest.TestCase):
    def test_groups_damage_by_declared_source(self) -> None:
        # Damage is a property of a source PDF, so the actionable unit is the
        # source, not the chunk. Both units are reported because a token count
        # alone reads as a chunk count and overstates the damage by ~10x.
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "a.md").write_text(CORRUPT, encoding="utf-8")
            (d / "b.md").write_text(CORRUPT.replace("A Paper (2020)", "Other Book"),
                                    encoding="utf-8")
            (d / "c.md").write_text(CLEAN, encoding="utf-8")
            by_source = check_corpus_health.scan_by_source(d)
        self.assertEqual(len(by_source), 2)
        for counts in by_source.values():
            self.assertEqual(counts["chunks"], 1)
            self.assertGreaterEqual(counts["tokens"], 1)
        self.assertEqual(check_corpus_health._totals(by_source)[0], 2)
        self.assertNotIn("A Clean Paper (2020)", " ".join(by_source))

    def test_token_count_exceeds_chunk_count_when_severely_damaged(self) -> None:
        # *Mythical Man-month* is the live example: 98 damaged chunks carrying
        # 1014 glue tokens. A source with several glued runs must report more
        # tokens than chunks, or the two columns are not comparable.
        heavy = " ".join([
            "purposeofcopyrightistoencouragewritersandartiststoproducecreativework",
            "thequickbrownfoxjumpsoverthelazydogagainandagainandagaintillitwearsout",
        ])
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "a.md").write_text(CORRUPT.replace(CORRUPT.split("---")[2], heavy),
                                    encoding="utf-8")
            by_source = check_corpus_health.scan_by_source(d)
        self.assertEqual(len(by_source), 1)
        counts = next(iter(by_source.values()))
        self.assertEqual(counts["chunks"], 1)
        self.assertEqual(counts["tokens"], 2)

    def test_empty_corpus_yields_no_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(check_corpus_health.scan_by_source(Path(tmp)), {})


class CorpusHealthGateTests(unittest.TestCase):
    def _run_gate(self, corpus_dir: Path) -> subprocess.CompletedProcess:
        """Run the gate against a temp corpus dir by overriding CORPUS_DIR."""
        with tempfile.TemporaryDirectory() as tmp:
            shim = Path(tmp) / "run_gate.py"
            shim.write_text(
                "import sys, pathlib\n"
                "sys.path.insert(0, %r)\n" % str(SCRIPTS) +
                "import check_corpus_health as m\n"
                f"m.CORPUS_DIR = pathlib.Path({str(corpus_dir)!r})\n"
                "sys.exit(m.main())\n",
                encoding="utf-8",
            )
            return subprocess.run([sys.executable, str(shim)],
                                  capture_output=True, text=True, cwd=str(ROOT))

    def test_clean_corpus_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "a_clean_chunk.md").write_text(CLEAN, encoding="utf-8")
            result = self._run_gate(d)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("PASS", result.stdout)

    def test_corrupt_corpus_fails_and_reports_clean_fraction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "a_clean_chunk.md").write_text(CLEAN, encoding="utf-8")
            (d / "b_corrupt_chunk.md").write_text(CORRUPT, encoding="utf-8")
            result = self._run_gate(d)
        self.assertEqual(result.returncode, 1)
        self.assertIn("FAIL", result.stdout)
        self.assertIn("50.0% chunks", result.stdout.replace("1/2 chunks (50.0%)", "50.0% chunks"))
        # The gate must name the damaged source, not just the chunk.
        self.assertIn("A Paper (2020)", result.stdout)

    def test_empty_corpus_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self._run_gate(Path(tmp))
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
