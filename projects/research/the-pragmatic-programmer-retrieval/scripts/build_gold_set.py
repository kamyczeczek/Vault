"""Parse gold set questions from starter/pragmatic_programmer_gold_set.txt into eval/gold_set_hard.json.

Phase 2.1 of book retrieval pipeline.
Produces eval/gold_set_hard.json with 30 curated benchmark questions (Q1–Q30).
"""
from __future__ import annotations

import json
import re
import sys
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.fingerprint import canonical_index_fingerprint

SOURCE_FILE = "starter/pragmatic_programmer_gold_set.txt"
OUTPUT_FILE = "eval/gold_set_hard.json"


def parse_gold_set(source_path: str = SOURCE_FILE, output_path: str = OUTPUT_FILE) -> dict:
    with open(source_path, encoding="utf-8") as f:
        content = f.read()

    # Match each Q section: ## Q<n> — ... up to next ## Q or end of file
    q_pattern = re.compile(
        r"##\s*Q(\d+)\s*—\s*([^\n]+)\n(.*?)(?=\n##\s*Q|\Z)",
        re.DOTALL
    )

    questions = []

    for match in q_pattern.finditer(content):
        q_num = int(match.group(1))
        header_desc = match.group(2).strip()
        body = match.group(3).strip()

        # Extract Pytanie
        q_text_match = re.search(r"\*\*Pytanie:\*\*\s*\n+>\s*(.+?)(?=\n\n\*\*|\n\*\*|\Z)", body, re.DOTALL)
        if not q_text_match:
            continue
        question_text = re.sub(r"\n>\s*", " ", q_text_match.group(1)).strip()

        # Extract Odpowiedź referencyjna
        ans_match = re.search(r"\*\*Odpowiedź referencyjna:\*\*\s*\n+>\s*(.+?)(?=\n\n\*\*|\n\*\*|\Z)", body, re.DOTALL)
        ref_ans = re.sub(r"\n>\s*", " ", ans_match.group(1)).strip() if ans_match else ""

        # Extract Źródło
        src_match = re.search(r"\*\*Źródło:\*\*\s*(.+?)(?=\n|\Z)", body)
        source_str = src_match.group(1).strip() if src_match else ""

        # Extract Typ
        type_match = re.search(r"\*\*Typ:\*\*\s*(.+?)(?=\n|\Z)", body)
        type_str = type_match.group(1).strip() if type_match else ""

        # Extract Trudność
        diff_match = re.search(r"\*\*Trudność:\*\*\s*(.+?)(?=\n|\Z)", body)
        diff_str = diff_match.group(1).strip() if diff_match else ""

        # Parse chapter and topics numbers from source if possible
        chap_match = re.search(r"Rozdział\s+(\d+)", source_str, re.IGNORECASE)
        chapter = int(chap_match.group(1)) if chap_match else None

        topic_matches = re.findall(r"Topic(?:s)?\s+([\d,\s+i]+)", source_str, re.IGNORECASE)
        topics = []
        if topic_matches:
            for tm in topic_matches:
                nums = re.findall(r"\d+", tm)
                topics.extend(int(n) for n in nums)

        questions.append({
            "id": f"q{q_num:03d}",
            "header": header_desc,
            "question": question_text,
            "reference_answer": ref_ans,
            "source_raw": source_str,
            "chapter": chapter,
            "topics": list(dict.fromkeys(topics)),
            "type": type_str,
            "difficulty": diff_str
        })

    fingerprint = sha256(json.dumps(questions, sort_keys=True).encode()).hexdigest()
    book_struct_path = Path(__file__).resolve().parent.parent / "data/book_structure.json"
    index_fingerprint = canonical_index_fingerprint(book_struct_path)

    output = {
        "gold_set_id": "gs_hard_v1",
        "book": "The Pragmatic Programmer, 20th Anniversary Edition",
        "questions_count": len(questions),
        "fingerprint": f"sha256:{fingerprint}",
        "index_fingerprint": f"sha256:{index_fingerprint}",
        "questions": questions
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Wyodrębniono {len(questions)} pytań do {output_path}.")
    print(f"Fingerprint gold setu: {fingerprint[:16]}...")

    return output


if __name__ == "__main__":
    parse_gold_set()
