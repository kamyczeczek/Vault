"""Deterministic, oracle-first builder for the plain-language eval set.

Reads passage files, strips YAML front-matter, extracts the longest prose
sentences, and emits a fingerprinted JSON artifact. Fail-closed: a passage
yielding fewer than --min-items usable sentences raises ValueError.

Usage (from the ARL repo root):

    python scripts/build_plain_language_eval_set.py \
        knowledge/eval_sets/plain_language_v1.json \
        --passages \
            docs/research/trustworthy-agent-tests.md \
            docs/research/plain-language-meter.md \
            reflection/digests/decision_graphs_workflow.md \
        --min-items 5

The output JSON is the *single source of truth* for the eval set; do not
hand-edit it. Regenerate instead.
"""
from __future__ import annotations

import argparse
import json
import re
from hashlib import sha256
from pathlib import Path


# ── Constants ────────────────────────────────────────────────────────────
_FRONT_MATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)
_SENTENCE_RE = re.compile(r"[^.!?\n]+[.!?]+")
# A "usable" prose sentence: at least 40 chars, at most 400, no leading digit
# (avoids numbered-list fragments), no backtick (avoids inline-code dumps).
_MIN_LEN = 40
_MAX_LEN = 400


def strip_front_matter(text: str) -> str:
    return _FRONT_MATTER_RE.sub("", text, count=1)


def extract_sentences(text: str) -> list[str]:
    """Split *text* into sentences; return only usable prose sentences."""
    prose = strip_front_matter(text)
    out: list[str] = []
    for match in _SENTENCE_RE.finditer(prose):
        s = match.group(0).strip()
        if len(s) < _MIN_LEN or len(s) > _MAX_LEN:
            continue
        if s[0].isdigit():
            continue
        if "`" in s:
            continue
        out.append(s)
    return out


def build_passage(
    passage_id: str,
    text: str,
    domain: str,
    min_items: int,
) -> dict:
    """Build one passage record. Raises ValueError if too few usable items."""
    sentences = extract_sentences(text)
    if not sentences:
        raise ValueError(
            f"{passage_id}: no usable prose sentences found (need ≥1, got 0)"
        )
    if len(sentences) < min_items:
        raise ValueError(
            f"{passage_id}: only {len(sentences)} usable sentence(s), "
            f"need ≥{min_items} (raise --min-items gate or add longer prose)"
        )
    # Oracle-first: take the top-N longest sentences, deterministically
    # ordered by (length desc, original position). No model in the loop.
    ranked = sorted(
        enumerate(sentences),
        key=lambda t: (-len(t[1]), t[0]),
    )
    top = ranked[:min_items]
    items = [
        {
            "prompt": f"What does the source state: {sent}?",
            "answer": sent,
            "kind": "recall",
        }
        for _, sent in top
    ]
    char_count = len(strip_front_matter(text).strip())
    if char_count < 500:
        bucket = "short"
    elif char_count < 3000:
        bucket = "medium"
    else:
        bucket = "long"
    return {
        "id": passage_id,
        "domain": domain,
        "length_bucket": bucket,
        "char_count": char_count,
        "items": items,
    }


def assign_split(passages: list[dict]) -> None:
    """Deterministic dev/test split by char_count.

    The ceil-fraction of the set with the largest char_count goes to `test`
    (the harder, longer passages are the held-out set); the remainder to `dev`.
    Ties break by id so the split is reproducible regardless of input order.
    """
    order = sorted(passages, key=lambda p: (-p["char_count"], p["id"]))
    test_count = -(-len(order) // 2)  # ceil
    for i, p in enumerate(order):
        p["split"] = "test" if i < test_count else "dev"


def fingerprint(passages: list[dict]) -> str:
    canonical = json.dumps(
        [{k: v for k, v in p.items() if k != "split"} for p in passages],
        sort_keys=True,
        ensure_ascii=False,
    )
    return sha256(canonical.encode("utf-8")).hexdigest()


def build_set(
    passages: list[dict],
) -> dict:
    assign_split(passages)
    return {
        "version": "v1",
        "fingerprint": fingerprint(passages),
        "passages": passages,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", help="Path to write the JSON eval set")
    parser.add_argument(
        "--passages",
        nargs="+",
        required=True,
        help="Markdown passage files (one passage per file)",
    )
    parser.add_argument(
        "--domain",
        default="workspace",
        help="Domain label for all passages (default: workspace)",
    )
    parser.add_argument(
        "--min-items",
        type=int,
        default=5,
        help="Minimum usable sentences per passage (default: 5)",
    )
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[1]
    out_path = root / args.output

    records: list[dict] = []
    for p in args.passages:
        path = root / p
        if not path.is_file():
            raise SystemExit(f"passage not found: {path}")
        text = path.read_text(encoding="utf-8")
        pid = path.stem
        rec = build_passage(pid, text, args.domain, args.min_items)
        records.append(rec)

    result = build_set(records)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out_path.relative_to(root)}: {len(records)} passages, fingerprint {result['fingerprint'][:12]}…")


if __name__ == "__main__":
    main()
