"""Session B content scorer for the Phase 2 KG ablation.

The pilot (flag phase2_result) proved the pipeline but not hypothesis B:
its "solved" criterion needs an oracle chunk ID, which the OFF arm cannot
know, so OFF loses by definition. This scorer replaces that half with a
non-tautological content criterion:

  * benchmark/content_criterion.json: per-task facts extracted ONLY from
    the task's oracle chunks (oracle-first), each a case-insensitive regex
    over the answer text.
  * echo guard: a fact whose pattern matches the task question is not a
    content fact (the answer would score by reflecting the prompt).
  * no LLM judge; every output is a pure function of
    (records, criterion, tasks, mapping).

Rescores existing blind transcripts in place, zero new LLM cost:

    python scripts/score_ablation_content.py rescore
    python scripts/score_ablation_content.py build-check
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CRITERION = ROOT / "benchmark" / "content_criterion.json"
TASKS = ROOT / "benchmark" / "tasks.json"
ABLA_DIR = ROOT / "scripts" / "_scratch" / "ablation"
OUT = ABLA_DIR / "content_verdict.json"


def load_criterion() -> dict:
    with open(CRITERION, encoding="utf-8") as fh:
        return json.load(fh)


def load_tasks() -> dict[str, dict]:
    with open(TASKS, encoding="utf-8") as fh:
        return {t["id"]: t for t in json.load(fh)["tasks"]}


def match_fact(text: str, pattern: str) -> bool:
    """True when the fact's regex is found in the answer text."""
    return re.search(pattern, text or "", flags=0) is not None


def score_answer_content(answer: str, facts: list[dict]) -> dict:
    """One answer against one task's fact set: matched ids + fraction."""
    matched = [f["id"] for f in facts if match_fact(answer, f["pattern"])]
    total = len(facts)
    return {"matched": matched, "total": total,
            "fraction": (len(matched) / total) if total else None}


def per_task_fractions(records: list[dict], criterion: dict,
                       tasks: dict[str, dict]) -> list[dict]:
    """Per-task fraction for one arm; a missing record scores 0, not a crash."""
    answered = {r["task_id"]: r.get("answer", "") for r in records}
    out = []
    for tid, entry in criterion["tasks"].items():
        res = score_answer_content(answered.get(tid, ""), entry["facts"])
        res["task_id"] = tid
        out.append(res)
    return out


def _family_avg(fractions: list[dict], tasks: dict[str, dict], family: str) -> dict:
    rows = [f for f in fractions
            if tasks.get(f["task_id"], {}).get("family") == family
            and f["fraction"] is not None]
    n = len(rows)
    return {"n": n, "avg": (sum(f["fraction"] for f in rows) / n) if n else None}


def score_arm_content(records: list[dict], criterion: dict,
                      tasks: dict[str, dict]) -> dict:
    """Macro average over tasks + per-family breakdown for one arm."""
    fractions = per_task_fractions(records, criterion, tasks)
    scored = [f for f in fractions if f["fraction"] is not None]
    macro = (sum(f["fraction"] for f in scored) / len(scored)) if scored else 0.0
    families: dict[str, dict] = {}
    fams_present = {tasks.get(t, {}).get("family")
                    for t in criterion["tasks"] if t in tasks}
    for fam in sorted(f for f in fams_present if f):
        entry = _family_avg(fractions, tasks, fam)
        if entry["n"]:
            families[fam] = entry
    return {"macro": macro, "n_tasks": len({r["task_id"] for r in records}),
            "families": families, "per_task": fractions}


def compare(arms: dict[str, list[dict]], criterion: dict,
            tasks: dict[str, dict],
            mapping: dict[str, dict[str, str]]) -> dict:
    """Split the two blind arms into ON/OFF and score both."""
    split: dict[str, list[dict]] = {"ON": [], "OFF": []}
    for label, records in arms.items():
        for rec in records:
            arm = mapping[rec["task_id"]][label]
            split[arm].append(rec)
    on = score_arm_content(split["ON"], criterion, tasks)
    off = score_arm_content(split["OFF"], criterion, tasks)
    return {"arms": {"ON": on, "OFF": off}}


def verdict(cmp_: dict) -> dict:
    """Pre-registered rule: ON wins only if its macro strictly exceeds OFF's
    AND it strictly out-scores OFF on >=2 of the 3 task families."""
    on, off = cmp_["arms"]["ON"], cmp_["arms"]["OFF"]
    families_on_wins = 0
    for fam, row in on["families"].items():
        o = off["families"].get(fam, {}).get("avg")
        if row["avg"] is not None and o is not None and row["avg"] > o:
            families_on_wins += 1
    on_wins = (on["macro"] > off["macro"] and families_on_wins >= 2)
    return {"outcome": "ON" if on_wins else "INCONCLUSIVE",
            "on_macro": on["macro"], "off_macro": off["macro"],
            "families_on_wins": families_on_wins,
            "rule": "on_macro > off_macro AND on strictly out-scores off "
                    "on >=2 of 3 families, else INCONCLUSIVE (n=9 pilot)"}


def check_criterion(criterion: dict, tasks: dict[str, dict]) -> list[str]:
    """Build-check: echo patterns, off-oracle sourcing, unknown tasks,
    duplicate fact ids, uncompilable regexes. Returns problem strings."""
    problems: list[str] = []
    seen: dict[str, str] = {}
    for tid, entry in criterion["tasks"].items():
        if tid not in tasks:
            problems.append(f"{tid}: task id absent from tasks.json")
            continue
        question = (tasks[tid].get("question") or "").lower()
        oracle = set(tasks[tid].get("oracle_ids", []))
        for fact in entry.get("facts", []):
            fid, src, pat = fact["id"], fact.get("source", ""), fact["pattern"]
            key = f"{tid}/{fid}"
            if key in seen:
                problems.append(f"{tid}: duplicate fact id {fid} "
                                f"(also in {seen[key]})")
                continue
            seen[key] = tid
            try:
                rx = re.compile(pat)
            except re.error as exc:
                problems.append(f"{tid} fact {fid}: pattern does not compile "
                                f"({exc})")
                continue
            if rx.search(question):
                problems.append(f"{tid} fact {fid}: echo — pattern "
                                f"'{pat}' matches the task question")
            if oracle and src not in oracle:
                problems.append(f"{tid} fact {fid}: source {src} is not an "
                                f"oracle chunk (oracle: {sorted(oracle)})")
    return problems


def rescore() -> int:
    """Score the sealed pilot transcripts against the content criterion."""
    criterion = load_criterion()
    tasks = load_tasks()
    problems = check_criterion(criterion, tasks)
    if problems:
        print("criterion build-check FAILED:")
        for p in problems:
            print(f"  {p}")
        return 1
    with open(ABLA_DIR / "mapping.json", encoding="utf-8") as fh:
        mapping = json.load(fh)
    arms = {label: json.loads((ABLA_DIR / f"arm_{label}.json").read_text(
        encoding="utf-8")) for label in ("A", "B")}
    cmp_ = compare(arms, criterion, tasks, mapping)
    result = {**cmp_, **verdict(cmp_)}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for name, arm in cmp_["arms"].items():
        print(f"== {name}: macro={arm['macro']:.3f} "
              f"(n={arm['n_tasks']})")
        for fam, row in arm["families"].items():
            print(f"   {fam}: avg={row['avg']:.3f} (n={row['n']})")
    v = verdict(cmp_)
    print(f"verdict: {v['outcome']} (on={v['on_macro']:.3f} "
          f"off={v['off_macro']:.3f}, families ON wins: "
          f"{v['families_on_wins']})")
    print(f"wrote {OUT}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Phase 2 session B content scorer.")
    group = parser.add_subparsers(dest="cmd", required=True)
    group.add_parser("rescore", help="score the sealed pilot transcripts")
    group.add_parser("build-check",
                     help="validate criterion against tasks.json")
    args = parser.parse_args(argv)
    if args.cmd == "rescore":
        return rescore()
    tasks = load_tasks()
    problems = check_criterion(load_criterion(), tasks)
    missing = set(tasks) - set(load_criterion()["tasks"])
    problems += [f"{t}: criterion omits task" for t in sorted(missing)]
    if problems:
        for p in problems:
            print(f"FAIL {p}")
        return 1
    print("build-check OK: criterion echo-free, oracle-sourced, "
          "all 9 tasks covered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
