#!/usr/bin/env python3
"""Migrate reflection candidates from legacy claim/evidence schema to canonical
Rule/Evidence/Target/Action schema.

Legacy fields: claim, evidence, evidence_ids, principle
Canonical fields: Rule, Evidence, Target, Action
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "reflection" / "candidates"

# Mapping for H-series heuristics
H_MAP = {
    "H1": {
        "Rule": "Self-correction loops MUST require external tool verification before any rewrite; intrinsic self-critique without an independent ground-truth channel degrades performance and can move correct answers toward incorrect critiques.",
        "Target": "self-correction loop",
        "Action": "Require external tool verification before any self-rewrite; if verification is unavailable, escalate to supervisor/human or halt with evidence rather than retry silently.",
    },
    "H2": {
        "Rule": "Agent error handling MUST attribute feedback to the earliest root-cause step, not to every symptom; correcting symptom steps wastes budget and fails to prevent recurrence.",
        "Target": "agent error handling",
        "Action": "Attribute feedback to the earliest root-cause step only; do not correct every symptom.",
    },
    "H3": {
        "Rule": "Durable lessons MUST be stored as pattern-level `(failure condition → reason → correction)` triples, not as failed trajectories or corrected answers. Transfer scales with abstraction level.",
        "Target": "agent learning system",
        "Action": "Store mistakes as (failure condition → reason → correction) triples; never store only failed trajectories or corrected answers.",
    },
    "H4": {
        "Rule": "Agent runtimes MUST install deterministic lifecycle hooks for infinite-loop detection, schema validation, and destructive-action blocking; prompt engineering alone is insufficient for these failure modes.",
        "Target": "agent runtime",
        "Action": "Install deterministic lifecycle hooks covering infinite-loop detection, schema validation, and destructive-action blocking before any side effect.",
    },
    "H5": {
        "Rule": "Verification tool choice MUST match the observed failure mode; search for factual QA, interpreter for code correctness, external detector for safety constraints. A non-observing tool collapses the loop to intrinsic self-correction.",
        "Target": "verification tool selection",
        "Action": "Match verification tool to failure mode: search for factual QA, interpreter for code correctness, external detector for safety constraints. Never use a non-observing tool.",
    },
}

# Mapping for other candidates
OTHER_MAP = {
    "agent-escalation-v1": {
        "Rule": "Agents MUST route unverified self-critique/self-correction, or Reflection-attributed failures, through an external verifier before accepting a revision; if verification is unavailable or Reflection is the attributed cause, escalate to a supervisor/human or halt with evidence rather than retry silently.",
        "Target": "agent self-correction",
        "Action": "Route unverified self-critique through an external verifier; escalate to supervisor/human or halt with evidence if verification is unavailable.",
    },
    "agent-escalation-evidence-format": {
        "Rule": "Escalation and review records MUST preserve the abstraction-level lesson as a (failure condition → reason → correction) triple, not only the raw trajectory or corrected answer.",
        "Target": "escalation and review records",
        "Action": "Preserve abstraction-level lessons as (failure condition → reason → correction) triples in escalation and review records.",
    },
    "agent-escalation-hook-intercept": {
        "Rule": "Agent runtimes MUST intercept corrective loops after tool-call or planning failures and escalate when two consecutive correction attempts do not change verifier state.",
        "Target": "agent runtime corrective loops",
        "Action": "Intercept corrective loops after tool-call or planning failures; escalate when two consecutive correction attempts do not change verifier state.",
    },
    "agent-sandboxing": {
        "Rule": "Agent correction paths MUST use an external verifier; intrinsic self-correction is prohibited because it measurably degrades performance.",
        "Target": "agent correction paths",
        "Action": "Use an external verifier for all agent correction paths; prohibit intrinsic self-correction.",
    },
    "agentforce-atlas-reasoning-engine": {
        "Rule": "Enterprise agent architectures (such as Salesforce Agentforce with Atlas) require deterministic reasoning engines, prompt builders, plan tracers, and audited action libraries rather than unconstrained zero-shot generation to ensure enterprise safety and verifiable execution.",
        "Target": "enterprise agent architecture",
        "Action": "Implement deterministic reasoning engines, prompt builders, plan tracers, and audited action libraries; do not rely on unconstrained zero-shot generation.",
    },
    "mandatory-deep-technical-analysis": {
        "Rule": "Ingested scientific papers and GitHub projects must undergo exhaustive technical analysis detailing exact algorithms, data structures, threat models, and architectural boundaries.",
        "Target": "ingested scientific papers and GitHub projects",
        "Action": "Perform exhaustive technical analysis detailing exact algorithms, data structures, threat models, and architectural boundaries; never reduce to superficial summaries.",
    },
    "design-first-planning": {
        "Rule": "Rigorous upfront design and explicit specification documents ('design-first planning') dramatically improve autonomous agent implementation success, enabling one-shot execution or clean 4-5 chunk decomposition.",
        "Target": "autonomous agent implementation",
        "Action": "Require rigorous upfront design and explicit specification documents before code execution; integrate automated design-document validation hooks into the ICM pipeline.",
    },
    "tree-search-branch-evaluation": {
        "Rule": "Multi-path code generation and agentic exploration must use tree-search branch evaluation with self-consistency checks before committing changes.",
        "Target": "multi-path code generation and agentic exploration",
        "Action": "Use tree-search branch evaluation with self-consistency checks before committing any changes.",
    },
    "defensive-failure-mode-hardening": {
        "Rule": "Workspace evolution scripts and validation gates must actively defend against metric gaming, circular citations, and ungrounded memory injection.",
        "Target": "workspace evolution scripts and validation gates",
        "Action": "Enforce explicit gate checks to prevent silent degradation and confabulation cascades.",
    },
    "maintainability-benchmarks": {
        "Rule": "Maintainability benchmarks for autonomous coding agents require repository-scale evaluation frameworks and strict skeletal specification (Skele-Code) to prevent architectural drift across multi-file modifications.",
        "Target": "autonomous coding agent maintainability benchmarks",
        "Action": "Implement multi-file repository evaluation harnesses incorporating test-first skeletal constraints for all autonomous agent coding workflows.",
    },
    "planner-executor-split": {
        "Rule": "Agent systems MUST separate planner and executor roles: the planner chooses strategy, decomposition, and retrieval; the executor grounds actions and generation. Do not delegate planning downward.",
        "Target": "agent system architecture",
        "Action": "Separate planner and executor roles; the planner chooses strategy, decomposition, and retrieval; the executor grounds actions and generation.",
    },
    "one-stage-one-job-modules": {
        "Rule": "Every agent module or subagent MUST own exactly one responsibility, with explicit input/output interfaces. Multi-role modules are a failure mode.",
        "Target": "agent modules and subagents",
        "Action": "Ensure every agent module or subagent owns exactly one responsibility with explicit input/output interfaces.",
    },
    "reusable-failure-triples": {
        "Rule": "Agent learning systems MUST store mistakes as (failure condition → reason → correction) triples, not as failed trajectories or corrected answers. Transfer scales with abstraction level.",
        "Target": "agent learning systems",
        "Action": "Store mistakes as (failure condition → reason → correction) triples; never store only failed trajectories or corrected answers.",
    },
    "deterministic-retrieval-separation": {
        "Rule": "Deterministic tag-intersection retrieval and agentic retrieval MUST remain separate tools. Do not mix them implicitly in prompts.",
        "Target": "retrieval tools",
        "Action": "Keep deterministic tag-intersection retrieval (route.py --tag) separate from external agentic retrieval; never mix them implicitly in prompts.",
    },
    "root-cause-targeted-correction": {
        "Rule": "When correcting agent failures, target the earliest root-cause step only, not every symptom. This yields the highest accuracy gains.",
        "Target": "agent failure correction",
        "Action": "Target the earliest root-cause step only when correcting agent failures; do not correct every symptom.",
    },
    "horizon-aware-plan-spec": {
        "Rule": "Plan specifications MUST be concrete for near actions and abstract for distant phases. Do not hardcode procedural details into far-horizon phases.",
        "Target": "plan specifications",
        "Action": "Make plan specifications concrete for near actions and abstract for distant phases; do not hardcode procedural details into far-horizon phases.",
    },
    "contract-driven-agent-handoffs": {
        "Rule": "Multi-agent pipelines require explicit verification contracts at each handoff boundary to prevent cross-agent hallucination compounding.",
        "Target": "multi-agent pipeline handoff boundaries",
        "Action": "Enforce gate scripts between every phase transition in multi-agent workflows.",
    },
    "dynamic-agent-lifecycle-scaling": {
        "Rule": "Dynamic activation and pruning of specialized sub-agents based on task phase reduces token overhead without information loss.",
        "Target": "agent lifecycle",
        "Action": "Implement task-scoped ephemeral agents that activate and prune based on task phase; terminate immediately upon artifact delivery.",
    },
    "automated-peer-review-loops": {
        "Rule": "Autonomous research systems and reflective agents must incorporate automated peer review and test-driven self-correction loops before committing findings.",
        "Target": "autonomous research systems and reflective agents",
        "Action": "Incorporate automated peer review and test-driven self-correction loops before committing any findings.",
    },
    "icm-methodology-hardening": {
        "Rule": "To guard against ICM implementation failures, workspace workflows must enforce automated write-read promotion gating, strict vocabulary routing, guarded re-stamping, and stage contract invariants.",
        "Target": "ICM workspace workflows",
        "Action": "Enforce automated write-read promotion gating, strict vocabulary routing, guarded re-stamping, and stage contract invariants.",
    },
    "verified-self-evolution-gates": {
        "Rule": "Agent self-modification of harness code or execution paths must be constrained by formal invariant checks.",
        "Target": "agent self-modification",
        "Action": "Constrain agent self-modification of harness code or execution paths by formal invariant checks; reject workflow self-updates that fail static analysis or regression checks.",
    },
    "live-frontier-state": {
        "Rule": "The workspace needs an external live frontier-state record for the current session, turn DAG, model requests, subagent parentage, and issue/verification state so context clearing does not erase the actionable frontier.",
        "Target": "workspace session state",
        "Action": "Pilot one vertical issue slice with an external frontier-state record; clear context for review and require the reviewer to resume from the record without conversation history.",
    },
}


def migrate_row(obj: dict) -> dict:
    cid = obj.get("id") or obj.get("candidate_id") or "?"

    # Check if already canonical
    if "Rule" in obj and "Evidence" in obj and "Target" in obj and "Action" in obj:
        # Already canonical, just clean up legacy fields
        new_obj = {k: v for k, v in obj.items() if k not in ("claim", "evidence", "evidence_ids", "principle")}
        return new_obj

    # Get mapping
    mapping = H_MAP.get(cid) or OTHER_MAP.get(cid)
    if not mapping:
        # Fallback: derive from claim
        claim = obj.get("claim", obj.get("principle", ""))
        evidence = obj.get("evidence", obj.get("evidence_ids", []))
        if isinstance(evidence, str):
            evidence = [evidence]
        evidence_str = ", ".join(f"`{e}`" for e in evidence)
        return {
            "id": cid,
            "state": obj.get("state", "proposed"),
            "Rule": claim,
            "Evidence": evidence_str,
            "Target": obj.get("topic", "workspace"),
            "Action": claim,
            "provenance": obj.get("provenance", {}),
            "why": obj.get("why", ""),
        }

    # Apply mapping
    evidence = obj.get("evidence", obj.get("evidence_ids", []))
    if isinstance(evidence, str):
        evidence = [evidence]
    evidence_str = ", ".join(f"`{e}`" for e in evidence)

    new_obj = {
        "id": cid,
        "state": obj.get("state", "proposed"),
        "Rule": mapping["Rule"],
        "Evidence": evidence_str,
        "Target": mapping["Target"],
        "Action": mapping["Action"],
        "provenance": obj.get("provenance", {}),
    }
    if obj.get("why"):
        new_obj["why"] = obj["why"]
    if obj.get("topic"):
        new_obj["topic"] = obj["topic"]
    if obj.get("bet"):
        new_obj["bet"] = obj["bet"]
    if obj.get("acceptance_criterion"):
        new_obj["acceptance_criterion"] = obj["acceptance_criterion"]

    return new_obj


def main() -> int:
    migrated = 0
    for jl in sorted(CANDIDATES.glob("*.jsonl")):
        lines = jl.read_text(encoding="utf-8").splitlines()
        new_lines = []
        changed = False
        for line in lines:
            if not line.strip():
                continue
            obj = json.loads(line)
            new_obj = migrate_row(obj)
            if new_obj != obj:
                changed = True
                migrated += 1
            new_lines.append(json.dumps(new_obj, ensure_ascii=False))
        if changed:
            jl.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            print(f"Migrated {jl.name}")

    print(f"\nTotal rows migrated: {migrated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
