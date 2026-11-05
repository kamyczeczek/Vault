#!/usr/bin/env python3
"""Canonical parser for accepted rules in reflection/memory.md.

One parser, one canonical-schema definition, one set of rejection rules.  Both
the lesson adapter (``apply_rules.py``) and meta-learning (``apply_meta_learning.py``)
must read memory through this module so a rule cannot be applied by one consumer
and rejected by the other.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field as dataclass_field
from pathlib import Path
from typing import Callable, Iterator


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MEMORY_FILE = ROOT / "reflection" / "memory.md"
CANONICAL_FIELDS = ("Rule", "Evidence", "Target", "Action")

_HEADER_RE = re.compile(r"^###\s+(?P<id>[^\s—][^—]*?)\s+—\s+(?P<state>[\w-]+)\s*$")
_LEGACY_RE = re.compile(r"^\s*-\s*(?:claim|evidence)\s*:", re.MULTILINE | re.IGNORECASE)
_EVIDENCE_ID_RE = re.compile(r"`([^`]+)`")


@dataclass(frozen=True)
class Rejection:
    """A rule block the canonical parser refused, with the reason."""

    rule_id: str
    reason: str
    detail: str

    def message(self) -> str:
        return f"[!] Rejected memory rule '{self.rule_id}': {self.reason} {self.detail}".rstrip()


@dataclass(frozen=True)
class MemoryRule:
    """A canonical accepted rule, parsed once and shared by all consumers."""

    id: str
    rule: str
    evidence: tuple[str, ...]
    evidence_text: str
    target: str
    action: str
    raw_block: str = ""
    title_key: str = dataclass_field(default="", compare=False)

    @property
    def action_text(self) -> str:
        return " ".join(line.strip() for line in self.action.splitlines() if line.strip())

    def fingerprint(self) -> tuple[str, tuple[str, ...]]:
        """Identity for duplicate detection: normalized action plus evidence ids."""
        return (self.action_text.casefold(), self.evidence or (self.evidence_text.casefold(),))

    def as_dict(self) -> dict[str, object]:
        """Legacy shape consumed by apply_rules.match_rules."""
        return {
            "id": self.id,
            "name": self.rule,
            "claim": "",
            "action": self.action_text,
            "evidence": list(self.evidence),
            "target": self.target,
            "raw_block": self.raw_block,
        }


def _field(body: str, name: str) -> str | None:
    match = re.search(rf"^{re.escape(name)}:\s*(.+)$", body, re.MULTILINE)
    return match.group(1).strip() if match else None


def is_legacy_record(body: str) -> bool:
    """True for the obsolete ``- claim:``/``- evidence:`` representation."""
    return bool(_LEGACY_RE.search(body))


def _blocks(content: str) -> Iterator[tuple[str, str, str]]:
    for block in re.split(r"\n(?=###\s+)", content.strip()):
        lines = block.strip().splitlines()
        if not lines or not lines[0].startswith("###"):
            continue
        yield lines[0], "\n".join(lines[1:]).strip(), block.strip()


def iter_accepted_rules(
    memory_file: Path = DEFAULT_MEMORY_FILE,
    *,
    on_rejection: Callable[[Rejection], None] | None = None,
) -> Iterator[MemoryRule]:
    """Yield each canonical accepted rule; report every rejection to on_rejection.

    Rejection reasons, in precedence order: legacy record shape, non-accepted
    state, blank canonical field, evidence without a backticked citation id.
    """
    if not memory_file.exists():
        return
    for header_line, body, raw_block in _blocks(memory_file.read_text(encoding="utf-8")):
        label = re.match(r"^###\s+(.+?)\s+—", header_line)
        label = label.group(1).strip() if label else "unknown"

        if is_legacy_record(body):
            if on_rejection:
                on_rejection(Rejection(label, "legacy '- claim: / - evidence:' record cannot become an action.", ""))
            continue

        header = _HEADER_RE.match(header_line)
        if not header or header.group("state") != "accepted":
            continue
        rule_id = header.group("id").strip()

        values = {name: _field(body, name) for name in CANONICAL_FIELDS}
        missing = [name for name, value in values.items() if not value or not value.strip()]
        if missing:
            if on_rejection:
                on_rejection(Rejection(rule_id, "missing or blank canonical field(s): "
                                       f"{', '.join(missing)}; it will not be applied.", ""))
            continue

        evidence_text = values["Evidence"]
        evidence = tuple(item.strip(" `") for item in _EVIDENCE_ID_RE.findall(evidence_text))
        if not evidence:
            if on_rejection:
                on_rejection(Rejection(rule_id, "Evidence has no citation ids; it will not be applied.", ""))
            continue

        yield MemoryRule(
            id=rule_id,
            rule=values["Rule"].strip(),
            evidence=evidence,
            evidence_text=evidence_text,
            target=values["Target"].strip(),
            action=values["Action"].strip(),
            raw_block=raw_block,
            title_key=" ".join(values["Rule"].split()).casefold(),
        )


def parse_accepted_rules(
    memory_file: Path = DEFAULT_MEMORY_FILE,
    *,
    dedupe: bool = False,
    on_rejection: Callable[[Rejection], None] | None = None,
) -> list[MemoryRule]:
    """Parse canonical accepted rules, optionally dropping duplicate rules.

    ``dedupe`` rejects a repeat of an already-seen rule title or of an already
    seen (action, evidence) pair, so a rule cannot be applied twice.
    """
    rules: list[MemoryRule] = []
    if not dedupe:
        return list(iter_accepted_rules(memory_file, on_rejection=on_rejection))

    seen_titles: set[str] = set()
    seen_fingerprints: set[tuple[str, tuple[str, ...]]] = set()
    for rule in iter_accepted_rules(memory_file, on_rejection=on_rejection):
        if rule.title_key in seen_titles:
            if on_rejection:
                on_rejection(Rejection(rule.rule, "duplicate rule title; skipping it to prevent re-application.", ""))
            continue
        fingerprint = rule.fingerprint()
        if fingerprint in seen_fingerprints:
            if on_rejection:
                on_rejection(Rejection(rule.rule, "duplicate Action and evidence; skipping it to prevent re-application.", ""))
            continue
        seen_titles.add(rule.title_key)
        seen_fingerprints.add(fingerprint)
        rules.append(rule)
    return rules
