"""Pin documented routing behaviour of ARL skill_router.select_skill_for_step.

Lives in root (not in projects/_archive/) per the archive rule
("Never edit an archived file", projects/_archive/CLAUDE.md).
Imports skill_router via sys.path — read-only, no archive edit.
"""
import sys
from pathlib import Path

ARL = Path(__file__).resolve().parents[1] / "projects" / "_archive" / "agentic-research-lab"
sys.path.insert(0, str(ARL))

from skill_router import select_skill_for_step


def test_research_routing():
    assert select_skill_for_step("research the topic of caching") == "research"


def test_architecture_improvement_routing():
    assert (
        select_skill_for_step("architecture improvement of the parser")
        == "improve-codebase-architecture"
    )


def test_bug_routing():
    assert select_skill_for_step("fix the login regression") == (
        "skills/poteto-mode-lite/playbooks/bug-fix"
    )


def test_known_shadowing_study_the_architecture():
    # KNOWN SHADOWING: "study the architecture" -> research (matches "study"
    # before "architecture"). Documented, not fixed — owner decides.
    assert select_skill_for_step("study the architecture") == "research"
