"""Session 6 pre-spawn validation (fixes session-3 errors #1 and #3).

1. Input-stage check per multi-topic: len==1 -> any; len==2 -> all; >=3 -> >= ceil(n/2).
   Miss = do not spawn, report separately.
2. Term validation: every candidate EN lemma must be locatable (as spaCy lemma)
   in at least one top-8 chunk for that question; otherwise removed BEFORE spawn.
"""
import json
import math
from pathlib import Path

import spacy

ROOT = Path(__file__).resolve().parent.parent
DUMP = json.loads((ROOT / "handoff" / "session-6" / "dumps" / "dump.json").read_text(encoding="utf-8"))["index"]

CANDIDATES = {
    "q001": ["knowledge", "intent", "duplication", "representation"],
    "q002": ["tracer", "prototype", "skeleton", "disposable"],
    "q003": ["inheritance", "coupling", "delegation", "mixin", "interface"],
    "q004": ["value", "rule", "change", "principle"],
    "q005": ["broken", "window", "fix", "repair"],
    "q006": ["precondition", "postcondition", "invariant", "caller"],
    "q007": ["state", "observer", "publish", "subscribe", "event"],
    "q008": ["crash", "dead", "cripple", "damage"],
    "q009": ["assertion", "turn", "production", "net"],
    "q010": ["duplication", "knowledge", "interdependence", "orthogonality"],
    "q011": ["binary", "chop", "half"],
    "q012": ["actor", "blackboard", "mailbox", "message"],
    "q013": ["coincidence", "accident", "luck"],
    "q014": ["requirement", "discover", "want"],
    "q015": ["version", "control", "regression", "test", "starter"],
}


def lemmatize(text: str, nlp) -> set:
    doc = nlp(text.lower())
    return {tok.lemma_ for tok in doc if not tok.is_punct}


def main() -> None:
    nlp = spacy.load("en_core_web_sm")
    chunk_lemmas = {qid: lemmatize(" ".join(m["text"] for m in e["chunks"]), nlp) for qid, e in DUMP.items() if qid != "canary"}

    print("== INPUT-STAGE CHECK ==")
    hits, misses = [], []
    for qid in sorted(CANDIDATES):
        e = DUMP[qid]
        topics, gold = set(e["top8topics"]), e["gold_topics"]
        n = len(gold)
        if n == 1:
            ok = any(t in topics for t in gold)
        elif n == 2:
            ok = all(t in topics for t in gold)
        else:
            ok = sum(1 for t in gold if t in topics) >= math.ceil(n / 2)
        got = sorted(topics & set(gold))
        (hits if ok else misses).append(qid)
        print(f"{qid}: gold={gold} top8_topics={sorted(topics)} intersect={got} -> {'HIT' if ok else 'MISS'}")
    print(f"hits={len(hits)} {hits}")
    print(f"misses={len(misses)} {misses}")

    print("\n== TERM VALIDATION vs top-8 ==")
    validated = {}
    for qid, terms in CANDIDATES.items():
        kept, removed = [], []
        for t in terms:
            (kept if t in chunk_lemmas[qid] else removed).append(t)
        validated[qid] = {"kept": kept, "removed": removed}
        print(f"{qid}: kept={kept} removed={removed}")
    (ROOT / "handoff" / "session-6" / "term-validation.json").write_text(
        json.dumps({"input_stage_hits": hits, "input_stage_misses": misses, "terms": validated}, indent=1),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
