#!/usr/bin/env python3
"""
apply_meta_learning.py — Closes the research loop with regression protection.

Translates empirical agent research findings (promoted in reflection/memory.md)
into concrete upgrades to:
1. Stage contracts (e.g. stages/00_expand/CONTEXT.md, stages/04_reflect/CONTEXT.md)
2. Prompt templates and guidance rules
3. Verification checklists

Maintains an audit trail in reflection/meta_evolution_log.jsonl.

SkillOpt heuristic: validation gate prevents catastrophic regressions.
Ungated evolution collapsed 55.4% → 2.6%; gated stayed flat at 57.0%.
This script enforces no-regression application via quality_check.py baseline comparison.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from memory_rules import parse_accepted_rules

ROOT = Path(__file__).resolve().parent.parent
MEMORY_FILE = ROOT / "reflection" / "memory.md"
EVOLUTION_LOG = ROOT / "reflection" / "meta_evolution_log.jsonl"
STAGES_DIR = ROOT / "stages"
EVIDENCE_DIR = ROOT / ".unlazy" / "evidence"
BASELINE_FILE = EVIDENCE_DIR / "baseline.json"
BACKUP_DIR = ROOT / ".unlazy" / "backups"


def _atomic_write(path: Path, content: str) -> None:
    """Replace a file atomically on the same filesystem."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def run_quality_gates() -> dict | None:
    """Run quality_check.py --json and return parsed evidence."""
    try:
        proc = subprocess.run(
            [sys.executable, "scripts/quality_check.py", "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=300,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"    [-] Quality gates failed to run: {e}")
        return None

    evidence_path = EVIDENCE_DIR / "latest.json"
    if not evidence_path.exists():
        print("    [-] Quality gates did not produce evidence file")
        return None

    try:
        return json.loads(evidence_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("    [-] Quality gates evidence file is corrupt")
        return None


def gates_passed(evidence: dict) -> bool:
    """Check if all quality gates passed."""
    if not evidence:
        return False
    summary = evidence.get("summary", {})
    return summary.get("failed", 1) == 0


def detect_regression(current: dict, baseline: dict) -> list[str]:
    """Detect hard regressions: gates that were passing in baseline but failing now.

    SkillOpt heuristic: ungated evolution collapsed 55.4% → 2.6%.
    We flag only pass→fail transitions, not output drift on still-passing gates.
    Soft output changes are logged as warnings, not regressions.
    """
    regressions = []
    warnings = []
    current_gates = {g["id"]: g for g in current.get("gates", [])}
    baseline_gates = {g["id"]: g for g in baseline.get("gates", [])}

    for gate_id, baseline_gate in baseline_gates.items():
        current_gate = current_gates.get(gate_id)
        if not current_gate:
            regressions.append(f"{gate_id}: missing in current run")
            continue
        if baseline_gate.get("passed") and not current_gate.get("passed"):
            regressions.append(f"{gate_id}: was passing, now failing")
        elif not baseline_gate.get("passed") and current_gate.get("passed"):
            warnings.append(f"{gate_id}: was failing, now passing (improvement)")
        elif baseline_gate.get("passed") and current_gate.get("passed"):
            # Both pass — log soft changes as warnings, not regressions
            if baseline_gate.get("fingerprint") != current_gate.get("fingerprint"):
                warnings.append(f"{gate_id}: passed but output changed (soft drift, not regression)")

    if warnings:
        for w in warnings:
            print(f"    [!] {w}")

    return regressions


def backup_files() -> list[tuple[Path, Path]]:
    """Backup files that may be modified. Returns list of (original, backup) paths."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    backups = []

    potential_targets = [
        STAGES_DIR / "00_expand" / "CONTEXT.md",
        STAGES_DIR / "01_inbox" / "CONTEXT.md",
        STAGES_DIR / "03_graph" / "CONTEXT.md",
        STAGES_DIR / "04_reflect" / "CONTEXT.md",
        STAGES_DIR / "06_meta_evolve" / "CONTEXT.md",
        STAGES_DIR / "00_meta" / "CONTEXT.md",
        EVOLUTION_LOG,
    ]

    for target in potential_targets:
        if target.exists():
            backup = BACKUP_DIR / f"{timestamp}_{target.name}"
            shutil.copy2(target, backup)
            backups.append((target, backup))

    return backups


def restore_from_backup(backups: list[tuple[Path, Path]]) -> None:
    """Restore files from backup."""
    for original, backup in backups:
        if backup.exists():
            shutil.copy2(backup, original)
            print(f"    [!] Restored {original} from backup")


def save_baseline(evidence: dict) -> None:
    """Save current evidence as regression baseline."""
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    baseline = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "gates": evidence.get("gates", []),
        "summary": evidence.get("summary", {}),
    }
    _atomic_write(BASELINE_FILE, json.dumps(baseline, indent=2) + "\n")


def load_baseline() -> dict | None:
    """Load previous baseline if it exists."""
    if not BASELINE_FILE.exists():
        return None
    try:
        return json.loads(BASELINE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
def _is_document_only(target: str) -> bool:
    """Return whether a rule is informational rather than a stage contract update."""
    return target.casefold() in {"document", "documents", "documentation", "document-only"}



def parse_promoted_rules() -> list[dict]:
    """Parse only explicit canonical accepted rules, rejecting duplicates."""
    rules = parse_accepted_rules(MEMORY_FILE, dedupe=True,
                                 on_rejection=lambda r: print(r.message()))
    return [
        {
            "title": rule.rule,
            "evidence": rule.evidence_text,
            "target": rule.target,
            "action": rule.action_text,
        }
        for rule in rules
    ]

def log_evolution(action_type: str, rule: dict, status: str, detail: str):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action_type": action_type,
        "rule_title": rule.get("title", ""),
        "evidence": rule.get("evidence", ""),
        "status": status,
        "detail": detail,
    }
    with open(EVOLUTION_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def apply_rule(rule: dict, dry_run: bool = False) -> bool:
    missing = [
        name
        for name, key in (
            ("Rule", "title"),
            ("Evidence", "evidence"),
            ("Target", "target"),
            ("Action", "action"),
        )
        if not isinstance(rule.get(key), str) or not rule[key].strip()
    ]
    if missing:
        title = rule.get("title", "")
        print(
            f"[!] Rejected promoted rule '{title}': missing or blank canonical "
            f"field(s): {', '.join(missing)}; it will not be applied."
        )
        log_evolution("stage_update", rule, "skipped", f"Missing canonical fields: {', '.join(missing)}")
        return False

    target = rule["target"].lower()
    action = rule["action"]
    title = rule["title"]

    print(f"[*] Processing rule: {title}")
    print(f"    Target: {target}")
    print(f"    Action: {action}")

    target_file = None
    if "expand" in target:
        target_file = STAGES_DIR / "00_expand" / "CONTEXT.md"
    elif "reflect" in target:
        target_file = STAGES_DIR / "04_reflect" / "CONTEXT.md"
    elif "inbox" in target:
        target_file = STAGES_DIR / "01_inbox" / "CONTEXT.md"
    elif "graph" in target:
        target_file = STAGES_DIR / "03_graph" / "CONTEXT.md"
    elif "self-evolution" in target or "meta_evolve" in target or "meta-learning" in target:
        target_file = STAGES_DIR / "06_meta_evolve" / "CONTEXT.md"
    elif target in {"general", "multi-agent"}:
        target_file = STAGES_DIR / "00_meta" / "CONTEXT.md"
    if not target_file or not target_file.exists():
        print(f"    [-] No specific stage contract matched for target '{target}'. Retained as general rule.")
        log_evolution("stage_update", rule, "skipped", f"No stage contract for target: {target}")
        return False

    content = target_file.read_text(encoding="utf-8")
    rule_marker = f"<!-- meta-evolved: {title} -->"
    if rule_marker in content:
        print("    [-] Rule already integrated into stage contract.")
        return True

    addition = f"\n\n## Evolved Protocol Rule ({title})\n{rule_marker}\n- **Origin Evidence:** `{rule['evidence']}`\n- **Requirement:** {action}\n"
    if not dry_run:
        _atomic_write(target_file, content + addition)
        print(f"    [+] Successfully updated {target_file.name}")
        log_evolution("stage_update", rule, "applied", f"Appended rule to {target_file}")
    else:
        print(f"    [dry-run] Would append to {target_file}")

    return True

def main():
    parser = argparse.ArgumentParser(description="Apply meta-learning rules to evolve research workflow")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying contracts")
    parser.add_argument("--save-baseline", action="store_true", help="Save current quality gate state as regression baseline")
    parser.add_argument("--no-regression-check", action="store_true", help="Skip regression gate (not recommended)")
    args = parser.parse_args()

    # Baseline management
    if args.save_baseline:
        print("[apply_meta_learning] Saving quality gate baseline...")
        evidence = run_quality_gates()
        if evidence:
            save_baseline(evidence)
            passed = gates_passed(evidence)
            status = "PASS" if passed else "FAIL"
            print(f"[apply_meta_learning] Baseline saved: {status} ({evidence['summary']['passed']}/{evidence['summary']['total']} gates)")
            return 0
        else:
            print("[apply_meta_learning] Failed to capture quality gate state for baseline")
            return 1

    # Load baseline for regression check
    baseline = None if args.no_regression_check else load_baseline()
    if baseline is None and not args.no_regression_check:
        print("[apply_meta_learning] No regression baseline found. Run with --save-baseline first.")
        print("  This is a one-time setup: python scripts/apply_meta_learning.py --save-baseline")
        print("  To skip this check, use --no-regression-check")
        return 1

    # Pre-apply quality gate check
    print("[apply_meta_learning] Running pre-apply quality gates...")
    pre_evidence = run_quality_gates()
    if not gates_passed(pre_evidence):
        print("[apply_meta_learning] Pre-apply quality gates FAILED. Fix gates before applying meta-learning rules.")
        return 1
    print(f"[apply_meta_learning] Pre-apply gates passed: {pre_evidence['summary']['passed']}/{pre_evidence['summary']['total']}")

    # Detect baseline regression before applying
    if baseline and not args.no_regression_check:
        regressions = detect_regression(pre_evidence, baseline)
        if regressions:
            print(f"[apply_meta_learning] BASELINE REGRESSION DETECTED: {len(regressions)} gate(s) regressed")
            for r in regressions:
                print(f"  - {r}")
            print("[apply_meta_learning] Aborting to prevent SkillOpt-style collapse (55.4% → 2.6%)")
            log_evolution("baseline_check", {}, "blocked", f"Pre-apply regression: {'; '.join(regressions)}")
            return 2
        print("[apply_meta_learning] No baseline regression detected")

    # Backup files before modification
    backups = backup_files()
    if backups:
        print(f"[apply_meta_learning] Backed up {len(backups)} file(s) to {BACKUP_DIR}")

    # Apply rules
    rules = parse_promoted_rules()
    if not rules:
        print("[apply_meta_learning] No active rules found in reflection/memory.md.")
        print("Tip: Run reflection, promote candidates via scripts/promote_candidate.py, then re-run.")
        return 0

    print(f"[apply_meta_learning] Found {len(rules)} rule(s) in reflection/memory.md")
    applied_count = 0
    for r in rules:
        if apply_rule(r, dry_run=args.dry_run):
            applied_count += 1

    # Post-apply verification with auto-rollback on regression
    if not args.dry_run and not args.no_regression_check:
        print("\n[apply_meta_learning] Running post-apply quality gates...")
        post_evidence = run_quality_gates()

        if not gates_passed(post_evidence):
            print("[apply_meta_learning] POST-APPLY GATES FAILED — auto-rolling back")
            restore_from_backup(backups)
            log_evolution("auto_rollback", {}, "rolled_back", "Post-apply quality gates failed")
            print(f"[apply_meta_learning] Rollback complete. Review changes in {BACKUP_DIR}")
            return 3

        if baseline:
            post_regressions = detect_regression(post_evidence, baseline)
            if post_regressions:
                print(f"[apply_meta_learning] POST-APPLY REGRESSION — auto-rolling back")
                for r in post_regressions:
                    print(f"  - {r}")
                restore_from_backup(backups)
                log_evolution("auto_rollback", {}, "rolled_back", f"Post-apply regression: {'; '.join(post_regressions)}")
                print(f"[apply_meta_learning] Rollback complete. Review changes in {BACKUP_DIR}")
                return 3

        # Update baseline to new passing state
        save_baseline(post_evidence)
        print(f"[apply_meta_learning] Post-apply gates passed: {post_evidence['summary']['passed']}/{post_evidence['summary']['total']}")
        print("[apply_meta_learning] Baseline updated to new passing state")

    print(f"\nCompleted meta-learning pass: {applied_count}/{len(rules)} active rule(s) evaluated.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
