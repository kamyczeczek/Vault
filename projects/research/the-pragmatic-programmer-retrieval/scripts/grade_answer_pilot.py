"""Deterministic grading for the answer-layer pilot (2026-10-18).

Two counts are reported per pre-registered terms (S56, handoff/pilot-answer-layer-2026-10-18/preregistration.md):
- strict: case-insensitive substring of the registered (English) stem;
- semantic: the stem concept present in the Polish translation/inflection
  (documented post-hoc equivalence judgment by the parent; reported separately
  so the pre-registered count is never silently adjusted).
"""
from __future__ import annotations

import json
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parents[4] / "handoff" / "pilot-answer-layer-2026-10-18"
TERMS: dict[str, list[str]] = {
    "q001": ["don't repeat yourself", "dupl", "knowl", "intent"],
    "q002": ["dispos", "lean but complet", "skeleton", "tracer"],
    "q003": ["mixin", "deleg", "interfac", "coupl", "protoc"],
    "q004": ["easier to chang", "special case", "decoupl", "guide"],
    "q005": ["board it up", "as soon as", "don't leave"],
    "q006": ["precondit", "postcondit", "invariant", "caller"],
    "q007": ["observer", "coupl", "callback", "synchron"],
    "q008": ["dead program", "catch and release", "crash"],
    "q009": ["turn on", "overhead", "assertion"],
    "q010": ["dupl", "interdepend", "minimiz", "components"],
    "q011": ["binary chop", "divide and conquer", "half"],
    "q012": ["blackboard", "actor", "facts"],
    "q013": ["coincid", "accident", "deliber"],
    "q015": ["starter kit", "version control", "regress", "automat"],
}
# semantic (PL) equivalence judgments, made post-hoc and labelled as such
SEMANTIC_EQ: dict[str, dict[str, str]] = {
    "q001": {"knowl": "wiedzy", "intent": "intencji"},
    "q002": {"dispos": "kod jednorazowy", "lean but complet": "lean, ale kompletny", "skeleton": "szkielet"},
    "q003": {"interfac": "interfejsy", "coupl": "sprzężeniem", "protoc": "protokoły"},
    "q004": {"special case": "szczególny przypadek", "guide": "prowadnica"},
    "q005": {"board it up": "zabandykuj", "as soon as": "od razu", "don't leave": "nie zostawiaj"},
    "q007": {},
    "q008": {"dead program": "pozwolić programowi umrzeć"},
    "q009": {"turn on": "włączonych", "assertion": "asercji"},
    "q010": {"interdepend": "współzależności", "minimiz": "minimalizowaniu", "components": "komponentami"},
    "q011": {"divide and conquer": "dziel i zwyciężaj", "half": "na pół"},
    "q012": {"actor": "aktorów", "facts": "fakty"},
    "q013": {"accident": "przypadkowych", "deliber": "świadomego"},
    "q015": {},
    "q006": {},
}
REFUSAL = "BRAK W KSIĄŻCE"


def norm(s: str) -> str:
    return unicodedata.normalize("NFKD", s).lower()


def grade() -> dict:
    data = json.loads((HERE / "answers-raw.json").read_text(encoding="utf-8"))
    answers = {k: v for k, v in data["answers"].items()}
    rows = []
    strict_ok = sem_ok = ref_ok = 0
    for qid, terms in sorted(TERMS.items()):
        a = norm(answers.get(qid, ""))
        refused = REFUSAL in a
        strict = [{"t": t, "p": (not refused) and norm(t) in a} for t in terms]
        sem = []
        for t in terms:
            ok = (not refused) and (norm(t) in a or norm(SEMANTIC_EQ.get(qid, {}).get(t, "§")) in a)
            sem.append({"t": t, "p": ok})
        if not refused and all(x["p"] for x in strict):
            strict_ok += 1
        if not refused and all(x["p"] for x in sem):
            sem_ok += 1
        rows.append({"qid": qid, "refused": refused, "terms_strict": strict, "terms_semantic": sem})
    refusals = []
    for qid in [f"u00{i}" for i in range(1, 9)] + ["canary"]:
        refusals.append({"qid": qid, "refusal": norm(REFUSAL) in norm(answers.get(qid, ""))})
        refusals[-1]["answer_len"] = len(answers.get(qid, ""))
    ref_ok = sum(1 for r in refusals if r["refusal"])
    report = {
        "strict_pass": strict_ok, "semantic_pass": sem_ok, "answerable_denominator": len(TERMS),
        "threshold_answerable": 10, "refusals": refusals, "refusal_ok": ref_ok, "unanswerable_n": 8,
        "threshold_refusal": 6, "rows": rows,
    }
    (HERE / "grading-results.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"strict={strict_ok}/{len(TERMS)} semantic={sem_ok}/{len(TERMS)} refusal={ref_ok}/8+canary")
    for r in rows:
        ms = "".join(("+" if x["p"] else "-") for x in r["terms_strict"])
        ss = "".join(("+" if x["p"] else "-") for x in r["terms_semantic"])
        print(f"{r['qid']}: strict[{ms}] semantic[{ss}]")


if __name__ == "__main__":
    grade()
