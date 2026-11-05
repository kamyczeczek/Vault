"""Tests for the plain-language eval-set builder (D-004 seed v1)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_plain_language_eval_set import (  # noqa: E402
    assign_split,
    build_passage,
    build_set,
    extract_sentences,
    fingerprint,
    strip_front_matter,
)


# ── Sentence extraction ──────────────────────────────────────────────────

def test_extracts_prose_sentences():
    text = "The agent writes long summaries that are checked by readers before ship.\n"
    sentences = extract_sentences(text)
    assert len(sentences) >= 1
    assert all(len(s) >= 40 for s in sentences)


def test_rejects_short_and_digit_and_code():
    text = "Short. " * 5 + "01. A numbered item here that is long enough to be caught.\n" + "A code snippet `def x(): pass` that should be skipped because of backticks."
    sentences = extract_sentences(text)
    for s in sentences:
        assert not s[0].isdigit()
        assert "`" not in s


def test_strip_front_matter():
    text = "---\ntitle: X\n---\nBody text here that is long enough to survive the forty char gate for testing.\n"
    body = strip_front_matter(text)
    assert "title:" not in body
    assert "Body text" in body


# ── build_passage ────────────────────────────────────────────────────────

def test_passage_with_sufficient_prose():
    # Build a passage with ≥5 long-enough sentences.
    filler = "The mechanism comparison uses a held-out set of passages from this workspace."
    text = "\n\n".join([filler] * 6)
    rec = build_passage("test", text, "workspace", min_items=5)
    assert rec["id"] == "test"
    assert len(rec["items"]) == 5
    assert all(item["kind"] == "recall" for item in rec["items"])
    assert all(item["answer"] in item["prompt"] for item in rec["items"])


def test_passage_fail_closed_on_too_few_items():
    with pytest.raises(ValueError, match="only 1 usable"):
        build_passage("thin", "This is the single usable sentence here.\n", "d", min_items=5)


def test_passage_fail_closed_on_empty():
    with pytest.raises(ValueError, match="no usable prose"):
        build_passage("empty", "", "d", min_items=5)


# ── split + fingerprint ─────────────────────────────────────────────────

def test_dev_test_split_deterministic():
    recs = [
        {"id": "a", "char_count": 5000, "items": []},
        {"id": "b", "char_count": 1000, "items": []},
        {"id": "c", "char_count": 3000, "items": []},
    ]
    assign_split(recs)
    # Longest half (a=5000, c=3000) → test; shortest (b=1000) → dev
    splits = {r["id"]: r["split"] for r in recs}
    assert splits["a"] == "test"
    assert splits["c"] == "test"
    assert splits["b"] == "dev"


def test_fingerprint_stable():
    recs = [
        {"id": "x", "domain": "d", "length_bucket": "long", "char_count": 9000, "items": []},
        {"id": "y", "domain": "d", "length_bucket": "short", "char_count": 200, "items": []},
    ]
    fp1 = fingerprint(recs)
    fp2 = fingerprint(recs)
    assert fp1 == fp2
    assert len(fp1) == 64  # sha256 hex


# ── build_set end-to-end ───────────────────────────────────────────────

def test_build_set_produces_valid_artifact():
    filler = "The meter scores comprehension against held-out passages with known answers."
    text_a = "\n\n".join([filler] * 6)
    text_b = "\n\n".join([filler] * 5)
    recs = [
        build_passage("alpha", text_a, "ws", min_items=5),
        build_passage("beta", text_b, "ws", min_items=5),
    ]
    result = build_set(recs)
    assert result["version"] == "v1"
    assert len(result["passages"]) == 2
    assert "fingerprint" in result
    json.dumps(result)  # serialisable
