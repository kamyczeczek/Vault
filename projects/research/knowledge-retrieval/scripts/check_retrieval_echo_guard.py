"""Mutacyjny gate: echo-guard dla retrieval benchmarku.

Weryfikuje, że retriever nie zwraca chunków, które są jedynie powtórzeniem
fragmentu pytania (echo pattern). Hermetyczny test — bez LLM, tylko FTS5.
"""
import argparse
import json
import random
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = ROOT / ".." / "agentic-research-lab" / "subprojects" / "vera" / "benchmark" / "QUESTIONS.md"
ASK_PY = ROOT / ".." / "agentic-research-lab" / "knowledge" / "graph" / "ask.py"
PYTHON = sys.executable


def parse_questions(path: Path) -> list[dict]:
    """Pars QUESTIONS.md — extract question blocks with id/question."""
    text = path.read_text(encoding="utf-8")
    blocks = re.split(r"\n### Q\d+\n", text)
    # First block is header; subsequent blocks are questions
    out = []
    for block in blocks[1:]:
        qid_m = re.search(r"^question: \"(.*?)\"", block, re.M)
        if not qid_m:
            continue
        qid = f"Q{len(out)+1}"
        question = qid_m.group(1)
        out.append({"id": qid, "question": question})
    return out


def echo_pattern(question: str, min_len: int = 20, max_len: int = 60) -> str:
    """Create an echo fragment from the question: a substring of the question itself."""
    q = question.strip().strip('"')
    # take a middle slice so it's not just the first word
    start = random.randint(0, max(0, len(q) - max_len))
    end = min(len(q), start + random.randint(min_len, max_len))
    fragment = q[start:end].strip()
    return fragment


def ask(query: str) -> tuple[int, str]:
    """Run ask.py and return (returncode, stdout)."""
    proc = subprocess.run(
        [PYTHON, str(ASK_PY), query, "--limit", "3"],
        cwd=ROOT.parent.parent,  # run from agentic-research-lab
        capture_output=True,
        text=True,
        timeout=120,
    )
    return proc.returncode, proc.stdout


def check_echo_guard(questions: list[dict], n_trials: int = 5, seed: int = 20261008) -> dict:
    """Run echo-guard trials: for each trial, pick a question, build echo fragment,
    run ask.py, check if the fragment appears in the returned text.
    Returns pass/fail summary.
    """
    rng = random.Random(seed)
    results = []
    for _ in range(n_trials):
        q = rng.choice(questions)
        fragment = echo_pattern(q["question"])
        rc, output = ask(fragment)
        detected = fragment.lower() in output.lower()
        results.append({
            "question_id": q["id"],
            "fragment": fragment,
            "rc": rc,
            "detected": detected,
            "output_len": len(output),
        })
    detected_count = sum(1 for r in results if r["detected"])
    return {
        "trials": results,
        "detected": detected_count,
        "total": n_trials,
        "pass": detected_count == 0,  # guard passes if NO echo is detected
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Echo-guard gate for retrieval benchmark.")
    parser.add_argument("--build-check", action="store_true", help="Validate setup without running")
    parser.add_argument("--trials", type=int, default=5, help="Number of echo trials")
    parser.add_argument("--seed", type=int, default=20261008, help="Random seed")
    args = parser.parse_args()

    if not QUESTIONS.exists():
        print(f"FAIL: QUESTIONS.md not found at {QUESTIONS}")
        return 1
    if not ASK_PY.exists():
        print(f"FAIL: ask.py not found at {ASK_PY}")
        return 1

    questions = parse_questions(QUESTIONS)
    if not questions:
        print("FAIL: no questions parsed from QUESTIONS.md")
        return 1

    if args.build_check:
        print(f"build-check OK: {len(questions)} questions loaded, ask.py present")
        return 0

    result = check_echo_guard(questions, n_trials=args.trials, seed=args.seed)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
