#!/usr/bin/env python3
"""
skill_router.py — Intelligent automatic skill selector for workspace tasks.
Three-phase router (decompose, select, iterate) following ICM, Unlazy, and Ralph Loop principles.
"""
import sys
import re

SKILL_CATALOG = {
    "bug": "skills/poteto-mode-lite/playbooks/bug-fix",
    "investigation": "skills/poteto-mode-lite/playbooks/investigation",
    "feature": "skills/poteto-mode-lite/playbooks/feature",
    "refactor": "skills/poteto-mode-lite/playbooks/refactor",
    "implement": "implement",
    "agent-reach": "agent-reach",
    "research": "research",
    "tdd": "tdd",
    "icm-architect": "icm-architect",
    "improve-codebase-architecture": "improve-codebase-architecture",
    "code-review": "code-review",
    "diagnosing-bugs": "diagnosing-bugs",
    "domain-modeling": "domain-modeling",
    "git-guardrails-claude-code": "git-guardrails-claude-code",
    "grill-with-docs": "grill-with-docs",
    "prototype": "prototype",
    "to-tickets": "to-tickets",
    "triage": "triage",
    "unlazy": "unlazy",
}

def decompose_task(task_desc: str) -> list[str]:
    # Phase 1: decompose (icm-architect style)
    parts = re.split(r"[;.\n]+", task_desc)
    steps = [p.strip() for p in parts if p.strip()]
    if not steps:
        steps = [task_desc.strip()]
    return steps

def select_skill_for_step(step_desc: str) -> str:
    # Phase 2: select (unlazy style)
    desc_lower = step_desc.lower()
    if re.search(r"(?:research|investigate|study|explore the topic)", desc_lower):
        return SKILL_CATALOG["research"]
    if re.search(r"(?:improve codebase architecture|architecture improvement|structural refactor|architectural overhaul)", desc_lower):
        return SKILL_CATALOG["improve-codebase-architecture"]
    if re.search(r"(?:bug|fix|diagnos|debug|regression|reproduce|blank)", desc_lower):
        return SKILL_CATALOG["bug"]
    if re.search(r"(?:search|literature|paper|expand|survey|evaluate)", desc_lower):
        return SKILL_CATALOG["agent-reach"]
    if re.search(r"(?:refactor|architecture|clean|deepen)", desc_lower):
        return SKILL_CATALOG["refactor"]
    if re.search(r"(?:implement|build|code|feature|export)", desc_lower):
        return SKILL_CATALOG["implement"]
    if re.search(r"(?:test|spec|verify|assert|tdd)", desc_lower):
        return SKILL_CATALOG["tdd"]
    if re.search(r"(?:triage|triag)", desc_lower):
        return SKILL_CATALOG["triage"]
    if re.search(r"(?:code.review|review the diff|review diff)", desc_lower):
        return SKILL_CATALOG["code-review"]
    if re.search(r"(?:root cause|flaky|mysterious failure)", desc_lower):
        return SKILL_CATALOG["diagnosing-bugs"]
    if re.search(r"(?:prototype|spike|proof.of.concept)", desc_lower):
        return SKILL_CATALOG["prototype"]
    if re.search(r"(?:ticket|work item)", desc_lower):
        return SKILL_CATALOG["to-tickets"]
    if re.search(r"(?:domain.model|ubiquitous language)", desc_lower):
        return SKILL_CATALOG["domain-modeling"]
    if re.search(r"(?:grill|sharpen the|interrogate the)", desc_lower):
        return SKILL_CATALOG["grill-with-docs"]
    if re.search(r"(?:unlazy|compress context|shrink context)", desc_lower):
        return SKILL_CATALOG["unlazy"]
    if re.search(r"(?:git guardrail|pre.commit|commit gate)", desc_lower):
        return SKILL_CATALOG["git-guardrails-claude-code"]
    return SKILL_CATALOG["icm-architect"]

def route_task_verbose(task_desc: str) -> dict:
    steps_raw = decompose_task(task_desc)
    steps = []
    for s in steps_raw:
        skill = select_skill_for_step(s)
        handoff = {
            "what": s,
            "state": "READY",
            "next": f"execute using {skill}"
        }
        steps.append({
            "step": s,
            "skill": skill,
            "handoff": handoff
        })

    handoff_summary = f"what: {task_desc} | state: READY | next: execute {len(steps)} steps"
    return {
        "steps": steps,
        "handoff": handoff_summary
    }

def route_task(task_desc: str) -> str:
    verbose = route_task_verbose(task_desc)
    if verbose["steps"]:
        return verbose["steps"][0]["skill"]
    return "icm-architect"

def main():
    if len(sys.argv) < 2:
        print("Usage: python skill_router.py \"<task description>\"")
        return 1
    task = sys.argv[1]
    verbose = route_task_verbose(task)
    primary_skill = verbose["steps"][0]["skill"] if verbose["steps"] else "icm-architect"
    print(f"[skill-router] Task: '{task}' -> Selected Skill / Playbook: '{primary_skill}'")
    print(f"[ralph-loop handoff] what: {task} | state: READY | next: {len(verbose['steps'])} steps planned")
    return 0

if __name__ == "__main__":
    sys.exit(main())
