"""Semantic chunking of clean book topics.

Phase 0.4 of book retrieval pipeline.
Produces data/chunks.json.
Target checkpoint: 600-900 chunks, prose dominating, types classified.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

INPUT = "data/book_structure_clean.json"
OUTPUT = "data/chunks.json"


def classify(text: str) -> str:
    text = text.strip()
    if re.search(r"(?:>|\*\*|^)\s*(?:Tip \d+|Exercise \d+|Challenge)", text):
        return "definition"
    if text.startswith("```") or (re.search(r"\b(def |class |function |public |private |const |let |var )\w+", text) and any(c in text for c in "{}:;()")):
        return "code"
    if re.match(r"^[-*]\s", text, re.MULTILINE):
        return "list"
    if text.startswith(">") or text.startswith('"'):
        return "quote"
    return "prose"


def split_semantic(text: str, max_chars: int = 800) -> list[str]:
    paragraphs = re.split(r"\n\s*\n", text)
    result = []
    buffer = ""
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if len(buffer) + len(p) < max_chars:
            buffer += "\n\n" + p if buffer else p
        else:
            if buffer:
                result.append(buffer)
            buffer = p
    if buffer:
        result.append(buffer)
    return result


def chunk_semantic(input_path: str = INPUT, output_path: str = OUTPUT) -> list[dict]:
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    chunks = []
    chunk_id = 0

    for chapter in data["chapters"]:
        for topic in chapter["topics"]:
            if topic.get("damaged"):
                continue
            units = split_semantic(topic["text"], max_chars=800)
            for unit in units:
                if len(unit.strip()) < 30:
                    continue
                chunk_id += 1
                chunks.append({
                    "id": f"ch_{chunk_id:04d}",
                    "text": unit,
                    "chapter": chapter["number"],
                    "topic": topic["number"],
                    "topic_title": topic["title"],
                    "type": classify(unit),
                    "page_book": topic["page_start"],
                    "damaged": False
                })

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"Chunków: {len(chunks)}")
    type_counts = Counter(c["type"] for c in chunks)
    print(f"Rozkład typów: {dict(type_counts)}")

    if chunks:
        lens = sorted(len(c["text"]) for c in chunks)
        median_len = lens[len(lens) // 2]
        print(f"Mediana długości: {median_len} znaków (min={lens[0]}, max={lens[-1]})")

    return chunks


if __name__ == "__main__":
    chunk_semantic()
