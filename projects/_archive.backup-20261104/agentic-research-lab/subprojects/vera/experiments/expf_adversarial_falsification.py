#!/usr/bin/env python3
"""
expf_adversarial_falsification.py — Experiment F: Multi-Agent Adversarial Falsification.

Dual-agent debate harness where:
- Proponent Agent constructs candidate rules from Experiment A findings
- Adversarial Critic attempts falsification via counterfactual ablation against graph.db
- Judge/Arbiter evaluates debate and decides promotion/rejection

Each candidate from vera_expa_findings.jsonl is tested against three falsification
strategies:
  F1: Counterfactual ablation — baseline query vs query after removing primary evidence nodes
  F2: Counter-evidence search — query orthogonal tag spaces for contradictions
  F3: Defect injection resilience — apply D1-D5 structural defects and measure drift

Verdict outcomes:
  - pass_falsification: survives all three strategies without claim degradation
  - fail_falsification: claim degrades under at least one strategy (evidence gap)
  - requires_revision: partial survival; needs stronger formulation

Usage:
  python subprojects/vera/experiments/expf_adversarial_falsification.py
  python subprojects/vera/experiments/expf_adversarial_falsification.py --candidate vera-expa-001
  python subprojects/vera/experiments/expf_adversarial_falsification.py --report
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "knowledge" / "graph" / "graph.db"
CANDIDATES_DIR = ROOT / "reflection" / "candidates"
RUNS_DIR = ROOT / "subprojects" / "vera" / "experiments" / "runs"
FINGERPRINT_FILE = ROOT / "knowledge" / "graph" / ".graph_fingerprint"
REVIEW_LOG = ROOT / "reflection" / "review_gate.jsonl"


def get_fingerprint() -> str:
    if FINGERPRINT_FILE.exists():
        return FINGERPRINT_FILE.read_text().strip()
    return "?"


def get_node_body(node_id: str, max_len: int = 800) -> str | None:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT body FROM nodes WHERE id = ?", (node_id,))
    row = cur.fetchone()
    conn.close()
    if row and row[0]:
        return row[0][:max_len]
    return None


def get_node_tags(node_id: str) -> set[str]:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT tag FROM node_tags WHERE node_id = ?", (node_id,))
    tags = {row[0] for row in cur.fetchall()}
    conn.close()
    return tags


def query_graph(question: str, limit: int = 5) -> list[dict]:
    """Run ask.py and return structured results."""
    cmd = [sys.executable, str(ROOT / "knowledge" / "graph" / "ask.py"), question, "--limit", str(limit)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=str(ROOT))
        if result.returncode == 0:
            return parse_ask_output(result.stdout)
    except Exception as e:
        print(f"[expf] ask.py error: {e}", file=sys.stderr)
    return []


def parse_ask_output(output: str) -> list[dict]:
    """Parse ask.py output with pipe-separated format: # id | "title" """
    results = []
    current = {}
    for line in output.splitlines():
        match = re.match(r"^# (\S+)\s*\|\s*\"", line)
        if match:
            if current.get("id"):
                results.append(current)
            current = {"id": match.group(1), "score": 0.0}
        elif line.startswith("path:") and current.get("id"):
            current["path"] = line.split(":", 1)[1].strip()
        elif line.strip().startswith("`") and current.get("id"):
            m = re.search(r"`([^`]+)`", line)
            if m and "evidence" not in current:
                current["evidence"] = m.group(1)
    if current.get("id"):
        results.append(current)
    return results


def get_counter_evidence(node_id: str, exclude_tags: set[str], limit: int = 5) -> list[str]:
    """Find nodes with overlapping edges but different tag profile."""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT n.id, n.title
        FROM nodes n
        JOIN edges e ON n.id = e.dst
        WHERE e.src = ?
        AND n.id != ?
        LIMIT 20
    """, (node_id, node_id))
    candidates = cur.fetchall()
    conn.close()

    results = []
    for nid, _ in candidates:
        tags = get_node_tags(nid)
        if not tags.intersection(exclude_tags):
            results.append(nid)
            if len(results) >= limit:
                break
    return results


def inject_defect(body: str, defect_type: str) -> str:
    """Apply structural defect to node body for testing fragility."""
    if defect_type == "D1_correlation_as_causation":
        return body + "\n\nNOTE: This correlation CAUSES the observed effect."
    elif defect_type == "D2_missing_negation":
        return re.sub(r'\bnot\b', ' ', body, flags=re.IGNORECASE)
    elif defect_type == "D3_quantifier_shift":
        return re.sub(r'\bsome\b', 'all', body, flags=re.IGNORECASE)
    elif defect_type == "D4_context_drop":
        paragraphs = body.split('\n\n')
        return '\n\n'.join(paragraphs[1:]) if len(paragraphs) > 1 else body
    elif defect_type == "D5_attribute_binding":
        return re.sub(r'(\w+) (enables|causes|leads to) (\w+)', r'\3 \2 \1', body)
    return body


class ProponentAgent:
    """Constructs arguments for candidate rules using evidence spans."""

    def __init__(self, candidate: dict):
        self.candidate = candidate
        self.evidence_ids = self._parse_evidence(candidate.get("Evidence", ""))
        self.nodes = {eid: get_node_body(eid) for eid in self.evidence_ids if get_node_body(eid)}

    def _parse_evidence(self, evidence_str: str) -> list[str]:
        return re.findall(r"`([^`]+)`", evidence_str)

    def build_argument(self) -> dict:
        argument = {
            "candidate_id": self.candidate.get("id"),
            "rule": self.candidate.get("Rule", ""),
            "evidence_summary": {},
            "supporting_spans": []
        }

        for eid in self.evidence_ids:
            body = self.nodes.get(eid, "")
            if body:
                lines = [l.strip() for l in body.split('\n') if l.strip()]
                argument["evidence_summary"][eid] = {"key_points": lines[:3]}
                argument["supporting_spans"].append({"chunk_id": eid, "span": lines[0] if lines else ""})

        return argument


class CriticAgent:
    """Attempts to falsify candidate claims via counterfactual ablation."""

    def __init__(self, candidate: dict, proponent_arg: dict):
        self.candidate = candidate
        self.proponent = proponent_arg
        self.falsification_results = {}

    def run_falsification_strategies(self) -> dict:
        evidence_ids = self.proponent["evidence_summary"].keys()
        rule_text = self.candidate.get("Rule", "")

        self.falsification_results["F1_counterfactual_ablation"] = self._test_ablation(evidence_ids, rule_text)
        self.falsification_results["F2_counter_evidence"] = self._test_counter_evidence(evidence_ids)
        self.falsification_results["F3_defect_injection"] = self._test_defect_resilience()

        return self.falsification_results

    def _query_term_diagnostics(self, all_tags: dict[str, set[str]]) -> dict:
        """Diagnose WHY ablation fragility happens, from the actual F1 mechanism.

        The baseline query is ``sorted(union-of-tags)[:6]``. Fragility happens
        when a removed node is the ONLY holder of a tag that lands in that
        top-6, so the query itself changes after removal. Load-bearing terms
        are the fix target: add a second node sharing each load-bearing tag,
        or pin the query terms. Pairwise tag overlap alone does NOT predict
        resilience — an 8-tag superset node covering a 3-tag node is resilient
        even though the pair looks redundant.
        """
        union: set[str] = set()
        for tags in all_tags.values():
            union.update(tags)
        top_terms = sorted(union)[:6]

        holders: dict[str, list[str]] = {}
        for term in top_terms:
            holders[term] = [nid for nid, tags in sorted(all_tags.items()) if term in tags]

        load_bearing = {t: h for t, h in holders.items() if len(h) == 1}
        covered = {t: h for t, h in holders.items() if len(h) >= 2}

        return {
            "baseline_top_terms": top_terms,
            "term_holders": holders,
            "load_bearing_terms": load_bearing,
            "covered_terms": covered,
            "fragility_risk": "high" if load_bearing else "low",
            "revision_advice": (
                "fragile: "
                + ", ".join(f"'{t}' held only by {h[0]}" for t, h in sorted(load_bearing.items()))
                + " is load-bearing — add a second node sharing that tag, or pin query terms"
                if load_bearing else
                "every baseline top term is held by >=2 nodes; removal cannot change the query"
            ),
        }

    def _test_ablation(self, node_ids: set[str], rule_text: str) -> dict:
        """Deterministic counterfactual ablation.

        For each evidence node, build a query from the OTHER nodes' tags and
        measure how much of the full-evidence baseline result set is retained.
        High retention = evidence is redundant/resilient.
        Low retention = removing that node changes what the query retrieves.
        """
        all_tags: dict[str, set[str]] = {nid: get_node_tags(nid) for nid in node_ids}

        # Build baseline query from ALL evidence nodes' tags (deterministic: sorted pick)
        baseline_tag_set: set[str] = set()
        for tags in all_tags.values():
            baseline_tag_set.update(tags)
        baseline_query = " ".join(sorted(baseline_tag_set)[:6])
        baseline = query_graph(baseline_query, limit=10)
        baseline_ids = {r.get("id") for r in baseline if r.get("id")}

        fragility_scores: dict[str, dict] = {}
        for removed_id in node_ids:
            # Build query from remaining nodes' tags only
            remaining_tag_set: set[str] = set()
            for nid, tags in all_tags.items():
                if nid != removed_id:
                    remaining_tag_set.update(tags)
            if remaining_tag_set:
                modified_query = " ".join(sorted(remaining_tag_set)[:6])
            else:
                modified_query = baseline_query

            try:
                after = query_graph(modified_query, limit=10)
                after_ids = {r.get("id") for r in after if r.get("id")}
                overlap = len(baseline_ids.intersection(after_ids))
                retention = overlap / max(len(baseline_ids), 1) if baseline_ids else 0.0

                fragility_scores[removed_id] = {
                    "lost_in_results": removed_id not in after_ids,
                    "evidence_retention": round(retention, 3),
                    "baseline_size": len(baseline_ids),
                    "after_size": len(after_ids),
                    "removed_query": modified_query[:80],
                }
            except Exception as exc:
                fragility_scores[removed_id] = {"error": str(exc)}

        valid = {k: v for k, v in fragility_scores.items() if "error" not in v}
        if not valid:
            return {"nodes_tested": len(node_ids), "avg_evidence_retention": 0.0,
                    "fragility_score": 1.0, "status": "unknown"}

        avg_retention = sum(v["evidence_retention"] for v in valid.values()) / len(valid)
        diagnostics = self._query_term_diagnostics(all_tags)
        return {
            "nodes_tested": len(valid),
            "avg_evidence_retention": round(avg_retention, 3),
            "fragility_score": round(1.0 - avg_retention, 3),
            "status": "resilient" if avg_retention > 0.7 else ("partial" if avg_retention > 0.4 else "fragile"),
            "per_node": fragility_scores,
            "cause_diagnostics": diagnostics,
        }

    def _test_counter_evidence(self, node_ids: set[str]) -> dict:
        """Search for contradicting evidence in orthogonal tag spaces."""
        all_tags = set()
        for nid in node_ids:
            all_tags.update(get_node_tags(nid))

        counter_evidence = []
        for nid in node_ids:
            counters = get_counter_evidence(nid, all_tags, limit=2)
            counter_evidence.extend(counters)

        # Query for contrast/contradict terms
        query = f"contrast OR contradicts OR limitation OR boundary {self.candidate.get('Rule', '')[:30]}"
        try:
            query_results = query_graph(query, limit=5)
        except:
            query_results = []

        return {
            "counter_nodes_found": len(counter_evidence),
            "contradictory_queries": len([r for r in query_results if r.get("score", 0) > 0.3]),
            "status": "contested" if counter_evidence or query_results else "uncontested"
        }

    def _test_defect_resilience(self) -> dict:
        """Test if claim survives structural defects in evidence."""
        defects = ["D1_correlation_as_causation", "D2_missing_negation",
                   "D3_quantifier_shift", "D4_context_drop", "D5_attribute_binding"]

        drift_scores = []
        for defect in defects:
            total_drift = 0
            for eid, summary in self.proponent["evidence_summary"].items():
                original = summary.get("key_points", [""])[0]
                defective = inject_defect(original, defect)
                orig_terms = set(re.findall(r'\b\w{4,}\b', original.lower()))
                def_terms = set(re.findall(r'\b\w{4,}\b', defective.lower()))
                drift = 1 - len(orig_terms.intersection(def_terms)) / max(len(orig_terms), 1)
                total_drift += drift

            avg_drift = total_drift / max(len(self.proponent["evidence_summary"]), 1)
            drift_scores.append(avg_drift)

        avg_resilience = sum(drift_scores) / max(len(drift_scores), 1)
        return {
            "defects_tested": len(defects),
            "avg_drift_score": round(avg_resilience, 3),
            "status": "resilient" if avg_resilience < 0.3 else ("partial" if avg_resilience < 0.6 else "fragile")
        }


class JudgeAgent:
    """Scores debate and renders verdict."""

    @staticmethod
    def judge(candidate: dict, proponent_arg: dict, critic_results: dict) -> dict:
        evidence_ids = re.findall(r"`([^`]+)`", candidate.get("Evidence", ""))
        resolved = sum(1 for eid in evidence_ids if JudgeAgent._resolve_id(eid))
        grounding = resolved / max(len(evidence_ids), 1)

        consistency_issues = JudgeAgent._check_consistency(proponent_arg)
        consistency = max(0, 1.0 - consistency_issues * 0.2)

        f1 = critic_results.get("F1_counterfactual_ablation", {}).get("status", "unknown")
        f2 = critic_results.get("F2_counter_evidence", {}).get("status", "unknown")
        f3 = critic_results.get("F3_defect_injection", {}).get("status", "unknown")

        verifiable = sum(1 for s in [f1, f2, f3] if s in ["fragile", "contested", "resilient", "partial"]) / 3

        scores = {
            "grounding_score": round(grounding, 3),
            "logical_consistency": round(consistency, 3),
            "external_verifiability": round(verifiable, 3)
        }

        verdict = JudgeAgent._render_verdict(scores, critic_results)

        return {
            "candidate_id": candidate.get("id"),
            "scores": scores,
            "verdict": verdict,
            "falsification_details": critic_results
        }

    @staticmethod
    def _resolve_id(node_id: str) -> bool:
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM nodes WHERE id = ?", (node_id,))
        count = cur.fetchone()[0]
        conn.close()
        return count > 0

    @staticmethod
    def _check_consistency(proponent_arg: dict) -> int:
        issues = 0
        seen = set()
        for span in proponent_arg.get("supporting_spans", []):
            eid = span.get("chunk_id", "")
            if eid in seen:
                issues += 1
            seen.add(eid)
        return issues

    @staticmethod
    def _render_verdict(scores: dict, critic_results: dict) -> str:
        grounding = scores["grounding_score"]
        consistency = scores["logical_consistency"]

        f1 = critic_results.get("F1_counterfactual_ablation", {}).get("status", "unknown")
        f3 = critic_results.get("F3_defect_injection", {}).get("status", "unknown")

        if grounding < 0.5 or consistency < 0.5:
            return "fail_falsification"

        if grounding >= 0.8 and consistency >= 0.8:
            fails = sum(1 for s in [f1, critic_results.get("F2_counter_evidence", {}).get("status")]
                       if s == "fragile")
            if fails == 0:
                return "pass_falsification"

        if f1 in ["fragile", "contested"] or f3 == "fragile":
            return "requires_revision"

        return "pass_falsification"


def load_candidate(candidate_id: str | None = None, file: str | None = None) -> list[dict]:
    if file:
        candidate_file = Path(file)
    else:
        candidate_file = CANDIDATES_DIR / "vera_expa_findings.jsonl"
    if not candidate_file.exists():
        print(f"[expf] ERROR: Candidate file not found: {candidate_file}", file=sys.stderr)
        return []

    candidates = []
    with open(candidate_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cand = json.loads(line.strip())
                if candidate_id is None or cand.get("id") == candidate_id:
                    candidates.append(cand)
    return candidates


def run_experiment(candidate_id: str | None = None, file: str | None = None) -> dict:
    candidates = load_candidate(candidate_id, file)
    if not candidates:
        print("[expf] ERROR: No candidates found", file=sys.stderr)
        return {}

    results = {
        "experiment": "F_adversarial_falsification",
        "timestamp": datetime.now().isoformat(),
        "fingerprint": get_fingerprint(),
        "candidates_tested": len(candidates),
        "verdicts": []
    }

    for candidate in candidates:
        print(f"\n{'='*60}")
        print(f"Candidate: {candidate.get('id')}")
        print(f"Rule: {candidate.get('Rule', '')[:80]}...")
        print('='*60)

        proponent = ProponentAgent(candidate)
        arg = proponent.build_argument()
        print(f"[Proponent] Evidence nodes: {len(arg['evidence_summary'])}")

        critic = CriticAgent(candidate, arg)
        falsification = critic.run_falsification_strategies()
        print(f"[Critic] F1 counterfactual: {falsification['F1_counterfactual_ablation']['status']}")
        print(f"[Critic] F2 counter-evidence: {falsification['F2_counter_evidence']['status']}")
        print(f"[Critic] F3 defect resilience: {falsification['F3_defect_injection']['status']}")

        judge_result = JudgeAgent.judge(candidate, arg, falsification)
        print(f"[Judge] Verdict: {judge_result['verdict']}")
        print(f"[Judge] Scores: G={judge_result['scores']['grounding_score']:.2f} C={judge_result['scores']['logical_consistency']:.2f} V={judge_result['scores']['external_verifiability']:.2f}")

        results["verdicts"].append({
            "candidate_id": candidate.get("id"),
            "rule": candidate.get("Rule", ""),
            "evidence_ids": re.findall(r"`([^`]+)`", candidate.get("Evidence", "")),
            "verdict": judge_result["verdict"],
            "scores": judge_result["scores"],
            "falsification": judge_result["falsification_details"]
        })

    return results


def write_results(results: dict) -> Path:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RUNS_DIR / f"EXPF_adversarial_falsification_{timestamp}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n[expf] Results written: {output_file}")
    return output_file


def log_review_gate(candidate_id: str, verdict: str, scores: dict) -> None:
    import subprocess
    metric_parts = [f"{k}={v:.3f}" for k, v in scores.items()]
    metrics = " ".join(metric_parts)
    cmd = [sys.executable, str(ROOT / "scripts" / "review_gate.py"),
           "--phase", "after", "--metric", metrics,
           "--label", candidate_id, "--out", str(REVIEW_LOG)]
    subprocess.run(cmd, capture_output=True, text=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", help="Specific candidate ID to test")
    parser.add_argument("--file", help="Candidate JSONL file to test (default: vera_expa_findings.jsonl)")
    parser.add_argument("--report", action="store_true", help="Show summary report")
    args = parser.parse_args()

    if args.report:
        runs = list(RUNS_DIR.glob("EXPF_*.json"))
        if not runs:
            print("No experiment F results found.")
            return 0
        latest = max(runs, key=lambda p: p.stat().st_mtime)
        print(f"\nLatest results: {latest}")
        with open(latest, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(json.dumps(data, indent=2))
        return 0

    print("="*60)
    print("Experiment F: Multi-Agent Adversarial Falsification")
    print("="*60)
    print(f"Fingerprint: {get_fingerprint()}")

    results = run_experiment(args.candidate, getattr(args, 'file', None))
    if not results.get("verdicts"):
        return 1

    write_results(results)

    for v in results["verdicts"]:
        log_review_gate(v["candidate_id"], v["verdict"], v["scores"])

    print("\n" + "="*60)
    print("EXPERIMENT F SUMMARY")
    print("="*60)
    verdicts = [v["verdict"] for v in results["verdicts"]]
    for vid, count in {v: verdicts.count(v) for v in set(verdicts)}.items():
        print(f"  {vid}: {count}")

    print(f"\nResults: {list(RUNS_DIR.glob('EXPF_*.json'))[-1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
