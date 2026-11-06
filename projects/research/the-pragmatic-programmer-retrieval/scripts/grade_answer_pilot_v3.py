"""Session 6 deterministic grader (fresh grader — no history, no tuning).

Reads frozen terms from handoff/session-6/term-validation.json (pre-spawn validated),
raw answers from handoff/session-6/answers-raw.json. Match rule frozen in
handoff/session-6/preregistration.md: term in spaCy lemmas of the answer.
Pinned: spacy==3.8.16, en_core_web_sm==3.8.0.
"""
import json
from pathlib import Path

import spacy

ROOT = Path(__file__).resolve().parent.parent
SESSION = ROOT / "handoff" / "session-6"
MARKER = "NOT IN THE BOOK"
THRESHOLD_FRAC = 0.70

# Frozen term lists (pre-registration, identical to term-validation.json kept[]).
TERMS = {
    "q001": ["knowledge", "intent", "duplication"],
    "q002": ["tracer", "prototype", "skeleton", "disposable"],
    "q003": ["inheritance", "coupling", "delegation", "mixin", "interface"],
    "q004": ["value", "rule", "change", "principle"],
    "q005": ["broken", "window", "fix"],
    "q006": ["precondition", "postcondition", "invariant", "caller"],
    "q007": ["observer", "event", "coupling"],
    "q009": ["assertion", "turn", "production", "net"],
    "q010": ["duplication", "knowledge", "orthogonality"],
    "q011": ["binary", "chop", "half"],
    "q012": ["actor", "blackboard", "mailbox", "message"],
    "q013": ["coincidence", "accident", "luck"],
    "q014": ["requirement", "want", "surface"],
}
INPUT_MISSES = ["q008", "q015"]


def lemmatize(nlp, text: str) -> set:
    doc = nlp(text.lower())
    return {tok.lemma_ for tok in doc if not tok.is_stop and not tok.is_punct}


def main() -> None:
    nlp = spacy.load("en_core_web_sm")
    answers = json.loads((SESSION / "answers-raw.json").read_text(encoding="utf-8"))

    per_q, passed = {}, 0
    for qid, terms in TERMS.items():
        ans = answers[qid]
        lemmas = lemmatize(nlp, ans)
        refusal = MARKER in ans
        missing = [t for t in terms if t not in lemmas]
        ok = (not refusal) and not missing
        passed += ok
        per_q[qid] = {"refusal": refusal, "missing": missing, "result": "pass" if ok else "fail"}

    unanswerable = [f"u{i:03d}" for i in range(1, 9)]
    refusals = sum(1 for q in unanswerable if MARKER in answers[q])
    canary_ok = MARKER in answers["canary"]

    n = len(TERMS)
    threshold = -(-int(THRESHOLD_FRAC * 100 * n) // 100)  # ceil(0.70*n)
    result = {
        "spacy": spacy.__version__,
        "en_core_web_sm": spacy.util.get_package_version("en_core_web_sm"),
        "spawned_answerable": n,
        "input_stage_misses": INPUT_MISSES,
        "strict_passed": passed,
        "threshold": threshold,
        "threshold_rule": ">=70% of spawned, all required lemmas",
        "threshold_met": passed >= threshold,
        "unanswerable_refusals": refusals,
        "canary_refusal": canary_ok,
        "per_question": per_q,
    }
    (SESSION / "grading-results-v3.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
