"""Guardrails, budgets, and population manager for benchmark-core v2.

Compliant with PROTOCOL.md:
- Section 4: Three decision gates (Gate 1 Entry, Gate 2 Promotion, Gate 3 Lockbox).
- Section 5: Population capacity N <= 8, conditional eviction, roles (champion, anchor, challenger, experiment).
- Section 6: Compute budget (20 min wall-clock per method, 30s timeout -> r=100, max 2% failures).
- Section 10: Automatic STOP conditions (Success, Lockbox burn x3, Dev stagnation x6, Global 20 cycles).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple


POPULATION_CAPACITY = 8
MAX_TOTAL_CYCLES = 20
MAX_STAGNATION_CYCLES = 6
MAX_LOCKBOX_EVALS = 3

DEV_WALL_TIMEOUT_SECONDS = 1200.0  # 20 minutes
TASK_TIMEOUT_SECONDS = 30.0
MAX_FAILURE_RATE = 0.02  # 2% max failures (e.g. 14 out of 741 fits)
TIMEOUT_PENALTY_R = 100.0

PROTECTED_ROLES = {"champion", "anchor"}


class PopulationManager:
    """Manages the active population of models according to Section 5."""

    def __init__(self, models: Optional[List[Dict[str, Any]]] = None):
        self.models: List[Dict[str, Any]] = models or []

    def get_champion(self) -> Optional[Dict[str, Any]]:
        for m in self.models:
            if "champion" in m.get("roles", []):
                return m
        return None

    def get_anchors(self) -> List[Dict[str, Any]]:
        return [m for m in self.models if "anchor" in m.get("roles", [])]

    def validate_cycle_card(self, cycle_card: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate a preregistered cycle card before execution."""
        candidate_name = cycle_card.get("candidate_name")
        if not candidate_name:
            return False, "Cycle card missing candidate_name"

        if any(m["name"] == candidate_name for m in self.models):
            return False, f"Candidate '{candidate_name}' already exists in active population"

        hypothesis = cycle_card.get("hypothesis")
        if not hypothesis:
            return False, "Cycle card missing hypothesis"

        falsifier = cycle_card.get("falsifier")
        if not falsifier:
            return False, "Cycle card missing falsifier"

        # Check population eviction requirement if at capacity
        if len(self.models) >= POPULATION_CAPACITY:
            replaces = cycle_card.get("replaces")
            if not replaces:
                return False, f"Population is at capacity ({POPULATION_CAPACITY}); cycle card must specify 'replaces'"

            target = next((m for m in self.models if m["name"] == replaces), None)
            if target is None:
                return False, f"Specified 'replaces' target '{replaces}' not found in active population"

            for role in target.get("roles", []):
                if role in PROTECTED_ROLES:
                    return False, f"Cannot evict protected method '{replaces}' with role '{role}'"

        return True, "VALID"

    def apply_adoption(self, candidate_name: str, roles: List[str], replaces: Optional[str] = None) -> None:
        """Adopt a candidate into population, conditionally evicting replaces if specified."""
        if len(self.models) >= POPULATION_CAPACITY:
            if not replaces:
                raise ValueError("Cannot adopt without replaces when at capacity")
            self.models = [m for m in self.models if m["name"] != replaces]

        # If candidate becomes champion, demote old champion to challenger
        if "champion" in roles:
            for m in self.models:
                if "champion" in m.get("roles", []):
                    m["roles"] = [r for r in m["roles"] if r != "champion"]
                    if not m["roles"]:
                        m["roles"] = ["challenger"]

        self.models.append({
            "name": candidate_name,
            "roles": roles,
        })


def check_gate1_entry(
    cycle_card_valid: bool,
    wall_elapsed_seconds: float,
    failed_fits: int,
    total_fits: int,
) -> Tuple[bool, str]:
    """Gate 1: Entry into population (every cycle)."""
    if not cycle_card_valid:
        return False, "FAIL: Invalid cycle card"

    if wall_elapsed_seconds > DEV_WALL_TIMEOUT_SECONDS:
        return False, f"FAIL: Wall clock {wall_elapsed_seconds:.1f}s exceeded 20m budget ({DEV_WALL_TIMEOUT_SECONDS}s)"

    failure_rate = (failed_fits / total_fits) if total_fits > 0 else 0.0
    if failure_rate > MAX_FAILURE_RATE:
        return False, f"FAIL: Failure rate {failure_rate:.1%} exceeds {MAX_FAILURE_RATE:.1%} ({failed_fits}/{total_fits})"

    return True, "GATE1_ENTRY_PASS"


def check_gate2_promotion(
    cluster_bootstrap_result: Dict[str, Any],
    domain_gmeans: Dict[str, float],
    task_ratios: Dict[str, float],
) -> Tuple[bool, List[str]]:
    """Gate 2: Promotion to Champion on Dev.

    1. Cluster bootstrap 1-sided 95% lower CI > 0.
    2. No domain gmean deterioration > 5% (gmean <= 1.05).
    3. At most 1 task point deterioration > 20% (r <= 1.20).
    """
    reasons = []

    # 1. Bootstrap CI
    lower_ci = cluster_bootstrap_result.get("one_sided_lower_ci", -1.0)
    if lower_ci <= 0.0:
        reasons.append(f"Cluster bootstrap lower 95% CI is not strictly positive: {lower_ci:.4f}")

    # 2. Hard domain filters (max +5% gmean deterioration)
    for dom, gmean_r in domain_gmeans.items():
        if gmean_r > 1.05:
            reasons.append(f"Domain '{dom}' deteriorated by >5%: gmean ratio = {gmean_r:.4f}")

    # 3. Max 1 task deterioration > +20%
    severe_tasks = [t for t, r in task_ratios.items() if r > 1.20]
    if len(severe_tasks) > 1:
        reasons.append(f"{len(severe_tasks)} tasks deteriorated by >20% (max 1 allowed): {severe_tasks}")

    passes = (len(reasons) == 0)
    return passes, reasons


def check_gate3_lockbox(
    lockbox_bootstrap_result: Dict[str, Any],
) -> Tuple[bool, str]:
    """Gate 3: Lockbox Confirmation.

    Alpha = 0.01667 (98.33% 1-sided CI).
    """
    lower_ci = lockbox_bootstrap_result.get("one_sided_lower_ci", -1.0)
    if lower_ci > 0.0:
        return True, "GATE3_LOCKBOX_PASS"
    return False, f"GATE3_LOCKBOX_FAIL: 98.33% CI lower bound {lower_ci:.4f} <= 0"


def check_stop_conditions(
    lockbox_passed: bool,
    lockbox_eval_count: int,
    consecutive_stagnation_cycles: int,
    total_cycle_count: int,
) -> Tuple[bool, str]:
    """Check Section 10 STOP rules."""
    if lockbox_passed:
        return True, "STOP: Success confirmed on Lockbox"

    if lockbox_eval_count >= MAX_LOCKBOX_EVALS:
        return True, f"STOP: Lockbox burned ({MAX_LOCKBOX_EVALS} evaluations reached)"

    if consecutive_stagnation_cycles >= MAX_STAGNATION_CYCLES:
        return True, f"STOP: Dev stagnation ({MAX_STAGNATION_CYCLES} consecutive cycles without promotion)"

    if total_cycle_count >= MAX_TOTAL_CYCLES:
        return True, f"STOP: Global cycle budget reached ({MAX_TOTAL_CYCLES} cycles)"

    return False, "CONTINUE"
