"""Validate extracted topics and quarantine damaged text.

Phase 0.3 of book retrieval pipeline.
Checks for mojibake, excessive repeated lines, and length anomalies.
Produces data/book_structure_clean.json and data/damaged_chunks.json.
"""
from __future__ import annotations

import json
from pathlib import Path
import ftfy

INPUT = "data/book_structure.json"
OUTPUT_CLEAN = "data/book_structure_clean.json"
OUTPUT_DAMAGED = "data/damaged_chunks.json"


def is_damaged(text: str) -> list[str]:
    reasons = []
    lines = text.split("\n")
    # Repeated lines detector
    for line in lines:
        line_s = line.strip()
        if line_s and lines.count(line) > 20:
            reasons.append("repeated_line")
            break

    # Length bounds for a complete book topic
    if len(text.strip()) < 50:
        reasons.append("too_short")
    if len(text.strip()) > 35000:
        reasons.append("too_long")

    # Mojibake detector
    if "â€" in text or "\ufffd" in text:
        reasons.append("mojibake")

    return reasons


def validate_chunks(input_path: str = INPUT, clean_path: str = OUTPUT_CLEAN, damaged_path: str = OUTPUT_DAMAGED):
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    damaged = []

    for chapter in data["chapters"]:
        for topic in chapter["topics"]:
            text = ftfy.fix_text(topic["text"])
            topic["text"] = text
            reasons = is_damaged(text)
            if reasons:
                damaged.append({
                    "chapter": chapter["number"],
                    "topic": topic["number"],
                    "title": topic["title"],
                    "reasons": reasons,
                    "preview": text[:200]
                })
                topic["damaged"] = True
            else:
                topic["damaged"] = False

    Path(clean_path).parent.mkdir(parents=True, exist_ok=True)
    with open(clean_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with open(damaged_path, "w", encoding="utf-8") as f:
        json.dump(damaged, f, ensure_ascii=False, indent=2)

    print(f"Uszkodzonych Topiców: {len(damaged)}")
    for d in damaged[:10]:
        print(f"  Ch{d['chapter']} T{d['topic']} ({d['title']}): {d['reasons']}")

    return data, damaged


if __name__ == "__main__":
    validate_chunks()
