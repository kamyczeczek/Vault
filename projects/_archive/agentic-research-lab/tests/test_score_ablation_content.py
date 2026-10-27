"""Tests for scripts/score_ablation_content.py (Phase 2, session B).

Oracle-first: every fixture here carries its own expected value derived from
the criterion spec, not from the code. Two integration pins guard the real
`benchmark/content_criterion.json` against the failure classes it exists to
prevent: echo (a pattern that matches the task question) and sourcing (a fact
whose source chunk is outside the task's oracle_ids).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import score_ablation_content as sc  # noqa: E402

TASKS = {
    "t-drum": {
        "id": "t-drum",
        "family": "perf",
        "question": "What drum beats on which rhythm track?",
        "oracle_ids": ["00_oracle_a", "01_oracle_b"],
        "tags": ["icm"],
    },
    "t-critic": {
        "id": "t-critic",
        "family": "feature",
        "question": "Design a cheap pre-retrieval gate for FTS5 hits.",
        "oracle_ids": ["00_oracle_a"],
        "tags": ["icm"],
    },
}


def make_criterion() -> dict:
    return {
        "tasks": {
            "t-drum": {"facts": [
                {"id": "f1", "source": "00_oracle_a", "pattern": "(?i)syncopated"},
                {"id": "f2", "source": "01_oracle_b", "pattern": "(?i)polyrhythm"},
            ]},
            "t-critic": {"facts": [
                {"id": "g1", "source": "00_oracle_a", "pattern": "(?i)useful|redundant"},
            ]},
        }
    }


def test_clean_criterion_has_no_problems() -> None:
    self_problems = sc.check_criterion(make_criterion(), TASKS)
    assert self_problems == []


def test_echo_pattern_is_flagged() -> None:
    # "rhythm" occurs in the t-drum question -> an echo, not a content fact
    crit = make_criterion()
    crit["tasks"]["t-drum"]["facts"][0]["pattern"] = "(?i)rhythm"
    problems = sc.check_criterion(crit, TASKS)
    assert any("echo" in p and "t-drum" in p and "f1" in p for p in problems)


def test_source_outside_oracle_is_flagged() -> None:
    crit = make_criterion()
    crit["tasks"]["t-critic"]["facts"][0]["source"] = "99_not_oracle"
    problems = sc.check_criterion(crit, TASKS)
    assert any("source" in p and "99_not_oracle" in p for p in problems)


def test_unknown_task_id_is_flagged() -> None:
    crit = make_criterion()
    crit["tasks"]["t-ghost"] = {"facts": [
        {"id": "z1", "source": "00_oracle_a", "pattern": "(?i)x"},
    ]}
    problems = sc.check_criterion(crit, TASKS)
    assert any("t-ghost" in p for p in problems)


def test_duplicate_fact_id_is_flagged() -> None:
    crit = make_criterion()
    crit["tasks"]["t-drum"]["facts"].append(
        {"id": "f1", "source": "01_oracle_b", "pattern": "(?i)other"})
    problems = sc.check_criterion(crit, TASKS)
    assert any("duplicate" in p.lower() and "f1" in p for p in problems)


def test_uncompilable_pattern_is_flagged() -> None:
    crit = make_criterion()
    crit["tasks"]["t-drum"]["facts"][0]["pattern"] = "(?i)unclosed["
    problems = sc.check_criterion(crit, TASKS)
    assert any("f1" in p for p in problems)


def test_content_matching_is_case_insensitive_and_partial() -> None:
    got = sc.match_fact("The beat is SYNCOPATED here.", "(?i)syncopated")
    assert got


def test_content_matching_requires_substance_not_prose() -> None:
    assert not sc.match_fact("The drum is loud.", "(?i)syncopated")


def test_answer_score_is_matched_over_total() -> None:
    facts = make_criterion()["tasks"]["t-drum"]["facts"]
    res = sc.score_answer_content("A syncopated polyrhythm.", facts)
    assert res == {"matched": ["f1", "f2"], "total": 2, "fraction": 1.0}
    res2 = sc.score_answer_content("A loud drum.", facts)
    assert res2 == {"matched": [], "total": 2, "fraction": 0.0}


def test_macro_average_and_family_breakdown() -> None:
    crit = make_criterion()
    records = [
        {"task_id": "t-drum", "answer": "A syncopated polyrhythm."},
        {"task_id": "t-critic", "answer": "Hits scored as useful."},
    ]
    agg = sc.score_arm_content(records, crit, TASKS)
    # t-drum = 1.0, t-critic = 1.0 -> macro 1.0
    assert agg["macro"] == 1.0
    assert agg["families"]["perf"]["avg"] == 1.0
    assert agg["families"]["feature"]["avg"] == 1.0
    assert agg["families"]["perf"]["n"] == 1


def test_missing_task_in_arm_scores_zero() -> None:
    # An arm that answered nothing on a task gets fraction 0, not a crash.
    crit = make_criterion()
    records = [{"task_id": "t-drum", "answer": ""}]
    agg = sc.score_arm_content(records, crit, TASKS)
    assert agg["macro"] == 0.0
    assert agg["n_tasks"] == 1


def test_compare_splits_arms_by_mapping() -> None:
    crit = make_criterion()
    # ON answered both, OFF answered neither
    on = [
        {"task_id": "t-drum", "answer": "A syncopated polyrhythm."},
        {"task_id": "t-critic", "answer": "Scored useful."},
    ]
    off = [
        {"task_id": "t-drum", "answer": ""},
        {"task_id": "t-critic", "answer": ""},
    ]
    mapping = {
        "t-drum": {"A": "ON", "B": "OFF"},
        "t-critic": {"A": "ON", "B": "OFF"},
    }
    cmp_ = sc.compare({"A": on, "B": off}, crit, TASKS, mapping)
    assert cmp_["arms"]["ON"]["macro"] == 1.0
    assert cmp_["arms"]["OFF"]["macro"] == 0.0
    # ON out-scores OFF on both families -> rule: 2 of 3 -> ON wins
    verdict = sc.verdict(cmp_)
    assert verdict["outcome"] == "ON"


def test_verdict_requires_two_of_three_families() -> None:
    crit = make_criterion()
    crit["tasks"]["t-x"] = {"facts": [
        {"id": "h1", "source": "00_oracle_a", "pattern": "(?i)zephyr"},
    ]}
    on = [
        {"task_id": "t-drum", "answer": "syncopated polyrhythm"},
        {"task_id": "t-critic", "answer": "scored useful"},
        {"task_id": "t-x", "answer": ""},
    ]
    off = [
        {"task_id": "t-drum", "answer": ""},
        {"task_id": "t-critic", "answer": ""},
        {"task_id": "t-x", "answer": "a zephyr"},
    ]
    mapping = {
        "t-drum": {"A": "ON", "B": "OFF"},
        "t-critic": {"A": "ON", "B": "OFF"},
        "t-x": {"A": "ON", "B": "OFF"},
    }
    cmp_ = sc.compare({"A": on, "B": off}, crit, TASKS, mapping)
    # ON wins on perf+feature families but loses t-x's family -> 2 of 3 -> ON
    assert sc.verdict(cmp_)["outcome"] == "ON"
    # Equal macros -> never ON
    cmp_["arms"]["OFF"]["macro"] = cmp_["arms"]["ON"]["macro"]
    assert sc.verdict(cmp_)["outcome"] == "INCONCLUSIVE"


def test_real_criterion_passes_build_check() -> None:
    # Integration pin: the shipped criterion must be echo-free and well-sourced.
    with open(ROOT / "benchmark" / "content_criterion.json", encoding="utf-8") as fh:
        crit = json.load(fh)
    with open(ROOT / "benchmark" / "tasks.json", encoding="utf-8") as fh:
        tasks = {t["id"]: t for t in json.load(fh)["tasks"]}
    problems = sc.check_criterion(crit, tasks)
    assert problems == [], problems
    # Every task in tasks.json carries a fact set (no silent omission)
    missing = set(tasks) - set(crit["tasks"])
    assert not missing, f"criterion omits tasks: {sorted(missing)}"
