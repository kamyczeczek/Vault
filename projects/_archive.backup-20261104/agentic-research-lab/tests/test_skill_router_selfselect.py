from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[0].parent
sys.path.insert(0, str(ROOT))

import skill_router


class TestSkillRouterSelfSelect(unittest.TestCase):
    def test_poteto_mode_lite_skill_exists(self) -> None:
        skill_path = ROOT / "skills" / "poteto-mode-lite" / "SKILL.md"
        self.assertTrue(skill_path.exists(), f"poteto-mode-lite SKILL.md missing at {skill_path}")
        content = skill_path.read_text(encoding="utf-8")
        for pb in ["investigation", "bug-fix", "feature", "refactor"]:
            self.assertIn(pb, content.lower(), f"Playbook {pb} missing in poteto-mode-lite SKILL.md")
        self.assertIn("prove-it-works", content.lower())

    def test_manifest_includes_poteto_mode_lite(self) -> None:
        manifest_path = ROOT / "skills" / "MANIFEST.md"
        self.assertTrue(manifest_path.exists())
        content = manifest_path.read_text(encoding="utf-8")
        self.assertIn("poteto-mode-lite", content)

    def test_route_task_verbose_structure(self) -> None:
        task = "fix the blank-input bug; reproduce first"
        result = skill_router.route_task_verbose(task)
        self.assertIsInstance(result, dict)
        self.assertIn("steps", result)
        self.assertIn("handoff", result)
        steps = result["steps"]
        self.assertTrue(len(steps) >= 1)
        for step in steps:
            self.assertIn("step", step)
            self.assertIn("skill", step)

    def test_four_sample_tasks(self) -> None:
        samples = [
            ("fix the blank-input bug; reproduce first", "bug"),
            ("implement new feature for export", "implement"),
            ("search literature on agent evaluation", "agent-reach"),
            ("refactor codebase architecture", "refactor"),
        ]
        for task, expected_keyword in samples:
            verbose = skill_router.route_task_verbose(task)
            skills = [s["skill"] for s in verbose["steps"]]
            combined = " ".join(skills).lower()
            self.assertIn(expected_keyword, combined, f"Task '{task}' did not select expected keyword '{expected_keyword}', got skills: {skills}")


if __name__ == "__main__":
    unittest.main()
