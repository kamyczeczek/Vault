"""Extract structured chapters and topics from The Pragmatic Programmer PDF.

Phase 0.1 of book retrieval pipeline.
Produces data/book_structure.json.
Target checkpoint: 9 chapters, 53 topics.
"""
from __future__ import annotations

import html
import json
import re
from hashlib import sha256
from pathlib import Path

import pymupdf
import pymupdf4llm

PDF_PATH = "pragmatic-programmer.pdf"
OUTPUT = "data/book_structure.json"
PAGE_OFFSET = 0  # In this edition PDF page matches book page (verified p.42 Topic 3, p.75 Topic 8)


def clean_title(title: str) -> str:
    """Clean HTML entities and deduplicate repeated titles from PDF TOC."""
    t = html.unescape(title).strip()
    # Handle concatenated duplicates e.g. "It’s Your LifeIt’s Your Life"
    half = len(t) // 2
    if half > 3 and t[:half] == t[half:]:
        t = t[:half]
    return t.strip()


def extract_structure(pdf_path: str = PDF_PATH, output_path: str = OUTPUT) -> dict:
    doc = pymupdf.open(pdf_path)
    toc = doc.get_toc()

    # Parse chapters and topics from TOC as ground truth hierarchy
    chapters_meta = []
    # TOC has: [lvl, title, page]
    # Filter only main 9 chapters
    chap_re = re.compile(r"^(\d+)\.\s*(.+)$")
    topic_re = re.compile(r"^Topic\s+(\d+)\.?\s*(.+)$")

    for lvl, raw_title, page in toc:
        clean_t = clean_title(raw_title)
        cm = chap_re.match(clean_t)
        if lvl == 1 and cm and int(cm.group(1)) <= 9:
            chap_num = int(cm.group(1))
            chap_name = cm.group(2).strip()
            chapters_meta.append({
                "number": chap_num,
                "title": chap_name,
                "page_start": page,
                "topics": []
            })
        elif lvl == 2 and "Topic " in clean_t and chapters_meta:
            tm = topic_re.match(clean_t)
            if tm:
                topic_num = int(tm.group(1))
                topic_title = tm.group(2).strip()
                # Deduplicate if topic title got doubled
                half = len(topic_title) // 2
                if half > 3 and topic_title[:half] == topic_title[half:]:
                    topic_title = topic_title[:half].strip()

                chapters_meta[-1]["topics"].append({
                    "number": topic_num,
                    "title": topic_title,
                    "page_start": page,
                    "text": ""
                })

    # Build topic page index lookup: (page -> (chapter_idx, topic_idx))
    all_topics = []
    for c_idx, chap in enumerate(chapters_meta):
        for t_idx, top in enumerate(chap["topics"]):
            all_topics.append((top["page_start"], c_idx, t_idx))

    all_topics.sort(key=lambda x: x[0])

    # Convert PDF pages to markdown
    print("Extracting markdown pages via pymupdf4llm...")
    pages = pymupdf4llm.to_markdown(pdf_path, page_chunks=True, write_images=False)

    for page_data in pages:
        p_num = page_data["metadata"]["page_number"]
        text = page_data["text"]

        if not text.strip() or re.fullmatch(r"\d+", text.strip()):
            continue

        # Find which topic this page belongs to
        # It belongs to the latest topic with page_start <= p_num
        current_top = None
        for p_start, c_idx, t_idx in all_topics:
            if p_start <= p_num:
                current_top = (c_idx, t_idx)
            else:
                break

        # Stop if we went past the last topic (e.g. into Postface or Index)
        postface_page = 469
        if p_num >= postface_page:
            continue

        if current_top is not None:
            c_idx, t_idx = current_top
            # Check that page is within chapter bounds
            chapters_meta[c_idx]["topics"][t_idx]["text"] += text + "\n\n"

    # Clean text whitespace
    for c in chapters_meta:
        for t in c["topics"]:
            t["text"] = t["text"].strip()

    fingerprint = sha256(json.dumps(chapters_meta, sort_keys=True).encode()).hexdigest()

    output = {
        "book": "The Pragmatic Programmer, 20th Anniversary Edition",
        "pdf_pages": len(pages),
        "page_offset": PAGE_OFFSET,
        "fingerprint": f"sha256:{fingerprint}",
        "chapters": chapters_meta
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    total_chapters = len(chapters_meta)
    total_topics = sum(len(c["topics"]) for c in chapters_meta)

    print(f"Rozdziałów: {total_chapters}")
    print(f"Topiców: {total_topics}")
    print(f"Fingerprint: {fingerprint[:16]}...")

    return output


if __name__ == "__main__":
    extract_structure()
