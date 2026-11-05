"""Small, deterministic harness primitives for the plain-language meter."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Any
import argparse
import json


@dataclass(frozen=True)
class ComprehensionItem:
    prompt: str
    answer: str
    kind: str = "recall"


def generate_items(source: str) -> list[ComprehensionItem]:
    """Build oracle-backed fixtures from explicit source sentences.

    Production item generation will use a model, but the oracle must remain
    source-derived and visible. This skeleton uses sentences as deterministic
    answerable recall items until that adapter is added.
    """
    sentences = [part.strip() for part in source.replace("!", ".").replace("?", ".").split(".") if part.strip()]
    return [ComprehensionItem(prompt=f"What does the source state: {sentence}?", answer=sentence) for sentence in sentences]


def _normalize_answer(value: str) -> str:
    return value.strip().casefold().rstrip(".!?")


def score_comprehension(items: list[ComprehensionItem], responses: list[str]) -> float:
    if not items or len(items) != len(responses):
        raise ValueError("items and responses must be non-empty and equally sized")
    return sum(_normalize_answer(response) == _normalize_answer(item.answer) for item, response in zip(items, responses)) / len(items)


def score_rubric(text: str) -> dict[str, int]:
    """Return the fixed rubric shape; model-backed scoring is a later adapter."""
    if not text.strip():
        raise ValueError("text must not be empty")
    return {"simplicity": 0, "informativeness": 0, "coherence": 0, "faithfulness": 0}


def score_fixture(source: str, responses: list[str]) -> dict[str, Any]:
    items = generate_items(source)
    return {
        "comprehension": score_comprehension(items, responses),
        "rubric": score_rubric(source),
        "items": items,
        "source_fingerprint": sha256(source.encode("utf-8")).hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Score a plain-language meter fixture")
    parser.add_argument("source")
    parser.add_argument("responses", nargs="+", help="answers in item order")
    args = parser.parse_args()
    result = score_fixture(args.source, args.responses)
    result["items"] = [item.__dict__ for item in result["items"]]
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
