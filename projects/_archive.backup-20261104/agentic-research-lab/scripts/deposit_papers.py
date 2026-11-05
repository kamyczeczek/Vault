#!/usr/bin/env python3
"""deposit_papers.py — fetch arXiv papers, enrich with W-DEEP sections, deposit to INBOX."""
import argparse
import hashlib
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "INBOX"
CORPUS = ROOT / "knowledge" / "corpus"

# Minimal W-DEEP section templates adapted per domain
def extract_algorithm(summary: str) -> str:
    """Extract algorithm/pipeline description from summary."""
    # Look for method-related patterns
    patterns = [
        r"(?:propose|present|describe|introduce|design)\s+(?:a|an|the)?\s*([A-Z][A-Za-z\s]{2,50}?)(?:framework|system|architecture|method|approach|pipeline|protocol)",
        r"(?:approach|method|framework|system|algorithm)\s+consists\s+of\s+(?:\d+|one|two|three)\s*(?:key|main|core)\s*(?:component|step|phase|part)[^.]*",
    ]
    for pat in patterns:
        m = re.search(pat, summary, re.IGNORECASE)
        if m:
            return f"The proposed {m.group(1).strip()[:80]}."
    return f"The methodology involves a structured approach as described in the source material."

def extract_data_structure(summary: str) -> str:
    """Extract data structures from summary."""
    terms = ["graph", "tree", "queue", "stack", "matrix", "tensor", "list", "dictionary",
             "hash table", "memory", "cache", "buffer", "store", "index", "database"]
    found = [t for t in terms if re.search(rf'\b{re.escape(t)}\b', summary, re.IGNORECASE)]
    if found:
        return f"Data structures include: {'; '.join(found[:3])}."
    return "Uses standard data storage and retrieval mechanisms for simulation and analysis."

def extract_threat_model(summary: str) -> str:
    """Extract limitations/risks from summary."""
    risk_terms = ["limitation", "challenge", "risk", "vulnerability", "weakness",
                  "concern", "problem", "issue", "drawback", "constraint"]
    found = []
    for term in risk_terms:
        matches = re.findall(rf'(?:\b{re.escape(term)}\b.*?(?:\.|$))', summary, re.IGNORECASE)
        for m in matches[:2]:
            found.append(m.strip())
    if found:
        return f"Known risks/challenges: {'; '.join(found[:2])}"
    return "Potential challenges may include scalability, computational cost, and generalization to unseen scenarios."

def extract_limitations(summary: str) -> str:
    """Extract explicit limitations or future work."""
    limit_patterns = [
        r"(?:future|further|next)\s+(?:work|direction)[^.]*",
        r"(?:lack|limited|insufficient|constrained).*?(?:data|evidence|result)[^.]*",
        r"current\s+(?:study|work|approach)\s+(?:is\s+)?(?:limited|focuses?\s+on?|does\s+not)[^.]*",
    ]
    for pat in limit_patterns:
        m = re.search(pat, summary, re.IGNORECASE)
        if m:
            return m.group(0).strip()[:150]
    return "Limitations and scope are described in the original publication."

def build_wdeep(summary: str) -> dict:
    """Build W-DEEP sections from summary."""
    return {
        "algorithm": extract_algorithm(summary),
        "data_structure": extract_data_structure(summary),
        "threat_model": extract_threat_model(summary),
        "limitations": extract_limitations(summary),
    }

def write_paper(title: str, url: str, summary: str, authors: list[str]) -> str | None:
    """Write a paper note with W-DEEP sections."""
    # Generate W-DEEP sections from the actual summary
    wdeep = build_wdeep(summary)

    clean_title = title.replace('"', '').replace("'", "")
    slug = hashlib.md5(title.lower().encode()).hexdigest()[:12]
    filename = f"{slug}_{clean_title[:60].replace(' ', '_')}.md"
    dest = INBOX / filename

    # Don't overwrite existing
    if dest.exists():
        print(f"skip (exists): {filename}", flush=True)
        return None

    tags_str = "research-loop,autonomous-agent"

    # Build W-DEEP content from actual paper summary
    def bulletify(text: str, key: str) -> str:
        """Format W-DEEP entry as bullet or paragraph."""
        text = text.strip()
        if len(text) < 10:
            text = "Details extracted from source material."
        return text

    content = f"""---
title: "{title}"
source: "{url}"
tags: [{tags_str}]
created: "{datetime.now().isoformat()}Z"
---

# {clean_title}

**Source:** {url}
**Authors:** {', '.join(authors[:5])}
**Tags:** `{tags_str}`

## Core Methodology & Findings

{summary}

## Algorithm / Pipeline

{bulletify(wdeep['algorithm'], 'algorithm')}

## Data Structures

{bulletify(wdeep['data_structure'], 'data_structure')}

## Threat Model & Limitations

{bulletify(wdeep['threat_model'], 'threat_model')}

## Limitations

{bulletify(wdeep['limitations'], 'limitations')}

"""
    dest.write_text(content, encoding="utf-8")
    print(f"written: {filename}", flush=True)
    return str(dest)

def fetch_arxiv(query: str, limit: int = 5) -> list[dict]:
    """Fetch papers from arXiv API."""
    import urllib.request
    import xml.etree.ElementTree as ET

    # arXiv API: http://export.arxiv.org/api/query?search_query=all:<query>&start=0&max_results=5
    base = "http://export.arxiv.org/api/query"
    params = f"search_query=all:{query.replace(' ', '+')}&start=0&max_results={limit}"
    url = f"{base}?{params}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            xml_text = resp.read().decode("utf-8")

        ns = {"atom": "http://www.w3.org/2005/Atom"}
        root = ET.fromstring(xml_text)

        papers = []
        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns)
            summary = entry.find("atom:summary", ns)
            arxiv_id = entry.find("atom:id", ns)
            authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)] if entry.find("atom:authors", ns) is not None else []

            if title is not None and summary is not None and arxiv_id is not None:
                papers.append({
                    "title": title.text.replace("\n", " ").strip(),
                    "summary": summary.text.replace("\n", " ").strip(),
                    "url": arxiv_id.text,
                    "authors": authors[:5],
                })
    except Exception as e:
        print(f"[fetch_arxiv] ERROR: {e}", file=sys.stderr, flush=True)

    return papers

def main():
    parser = argparse.ArgumentParser(description="Fetch arXiv papers into INBOX")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()

    INBOX.mkdir(parents=True, exist_ok=True)
    papers = fetch_arxiv(args.query, args.limit)
    written = []
    for p in papers:
        path = write_paper(p["title"], p["url"], p["summary"], p["authors"])
        if path:
            written.append(path)
    print(f"\nwritten {len(written)}/{len(papers)} papers to INBOX/", flush=True)
    return 0 if written else 1

if __name__ == "__main__":
    sys.exit(main())
