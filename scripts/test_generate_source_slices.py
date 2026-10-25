#!/usr/bin/env python3
"""Tests for the deterministic source-slice generator."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import generate_source_slices


class SourceSliceGeneratorTests(unittest.TestCase):
    def test_generate_and_check_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.md"
            spec = root / "spec.json"
            output = root / "out"
            source.write_text(
                "# Root\n\n"
                "## Alpha\n\nalpha body\n\n"
                "### Beta\n\nbeta body\n\n"
                "## Gamma\n\ngamma body\n",
                encoding="utf-8",
            )
            spec.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "source": source.as_posix(),
                        "slices": [
                            {
                                "id": "alpha",
                                "title": "Alpha slice",
                                "source_heading": "Alpha",
                                "start_heading": "Alpha",
                                "end_heading": "Gamma",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            self.assertEqual(
                generate_source_slices.main(
                    [
                        "--source",
                        str(source),
                        "--spec",
                        str(spec),
                        "--output",
                        str(output),
                    ]
                ),
                0,
            )
            first_manifest = (output / "manifest.json").read_text(encoding="utf-8")
            (output / "index.md").write_text("# Generated navigation\n", encoding="utf-8")
            self.assertEqual(
                generate_source_slices.main(
                    [
                        "--source",
                        str(source),
                        "--spec",
                        str(spec),
                        "--output",
                        str(output),
                        "--check",
                    ]
                ),
                0,
            )
            self.assertEqual(
                first_manifest,
                (output / "manifest.json").read_text(encoding="utf-8"),
            )
            generated = (output / "alpha.md").read_text(encoding="utf-8")
            self.assertIn("generated: true", generated)
            self.assertIn("source_lines: [3, 10]", generated)
            self.assertIn("alpha body", generated)
            self.assertNotIn("gamma body", generated)

    def test_ambiguous_selector_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.md"
            spec = root / "spec.json"
            source.write_text("# Repeated\n\n# Repeated\n", encoding="utf-8")
            spec.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "source": source.as_posix(),
                        "slices": [
                            {
                                "id": "bad",
                                "title": "Bad",
                                "source_heading": "Repeated",
                                "start_heading": "Repeated",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(
                generate_source_slices.main(
                    ["--source", str(source), "--spec", str(spec), "--output", str(root / "out")]
                ),
                2,
            )

    def test_source_change_makes_generated_tree_stale(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.md"
            spec = root / "spec.json"
            output = root / "out"
            source.write_text("# Root\n\n## Alpha\n\nalpha body\n", encoding="utf-8")
            spec.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "source": source.as_posix(),
                        "slices": [
                            {
                                "id": "alpha",
                                "title": "Alpha slice",
                                "source_heading": "Alpha",
                                "start_heading": "Alpha",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            arguments = [
                "--source",
                str(source),
                "--spec",
                str(spec),
                "--output",
                str(output),
            ]
            self.assertEqual(generate_source_slices.main(arguments), 0)
            source.write_text(
                "# Root\n\n## Alpha\n\nchanged body\n", encoding="utf-8"
            )
            self.assertEqual(
                generate_source_slices.main([*arguments, "--check"]),
                1,
            )


if __name__ == "__main__":
    unittest.main()
