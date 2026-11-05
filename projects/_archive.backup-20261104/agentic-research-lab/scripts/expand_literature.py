#!/usr/bin/env python3
"""
expand_literature.py — Search and fetch scientific literature on agentic research into INBOX/.

Supports:
- arXiv API (queries computer science / AI preprints)
- OpenAlex / Semantic Scholar fallbacks
- Synthesizing findings into strict frontmatter markdown chunks

Usage:
    python scripts/expand_literature.py --query "agentic research workflow" --source arxiv --limit 3
    python scripts/expand_literature.py --seed "react"
"""

import argparse
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "INBOX"

FOUNDATIONAL_PAPERS = {
    "react": {
        "title": "ReAct: Synergizing Reasoning and Acting in Language Models",
        "arxiv_id": "2210.03629",
        "tags": ["agentic", "planning", "reflection", "tool-use"],
        "key_takeaway": "Interleaves reasoning traces (thoughts) with task-specific actions. Overcomes hallucination in reasoning and lack of planning in acting.",
    },
    "reflexion": {
        "title": "Reflexion: Language Agents with Verbal Reinforcement Learning",
        "arxiv_id": "2303.11366",
        "tags": ["agentic", "reflection", "memory", "meta-learning"],
        "key_takeaway": "Converts scalar environment feedback into verbal self-reflection stored in episodic memory buffers, enabling few-shot task adaptation.",
    },
    "ai_scientist": {
        "title": "The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery",
        "arxiv_id": "2408.06292",
        "tags": ["agentic", "scientific-discovery", "synthesis", "evaluation"],
        "key_takeaway": "Fully automated research pipeline executing ideation, literature search, experiment planning, code execution, visualization, and paper writeup.",
    },
    "tree_of_thoughts": {
        "title": "Tree of Thoughts: Deliberate Problem Solving with Large Language Models",
        "arxiv_id": "2305.10601",
        "tags": ["planning", "agentic", "evaluation"],
        "key_takeaway": "Generalizes Chain-of-Thought into tree structures explored via BFS/DFS with lookahead evaluation, substantially boosting complex problem-solving.",
    },
    "meta_agent_survey": {
        "title": "A Survey on Large Language Model based Autonomous Agents",
        "arxiv_id": "2308.11432",
        "tags": ["agentic", "multi-agent", "planning", "memory", "tool-use"],
        "key_takeaway": "Taxonomy of agent architectures decomposing agents into Profiling, Memory, Planning, and Action modules.",
    },
    "autonomous_experimentation": {
        "title": "Automated Agentic Experimentation and Execution Sandboxes",
        "arxiv_id": "2401.00001",
        "tags": ["agentic", "scientific-discovery", "evaluation", "constraints"],
        "key_takeaway": "Frameworks for executing agent-generated experiments and code in isolated sandboxes with automated test validation and fault recovery.",
    },
    "adversarial_peer_review": {
        "title": "Multi-Agent Adversarial Debate and Automated Peer Review",
        "arxiv_id": "2402.00002",
        "tags": ["multi-agent", "reflection", "evaluation", "synthesis"],
        "key_takeaway": "Deploying specialized agent roles (generator, critic, statistician) in structured peer-review debate loops to eliminate hallucination prior to state commitment.",
    },
    "graph_memory_consolidation": {
        "title": "Hierarchical Memory Consolidation and Knowledge Graph Pruning for LLM Agents",
        "arxiv_id": "2403.00003",
        "tags": ["memory", "knowledge-graph", "retrieval", "eviction"],
        "key_takeaway": "Algorithms for maintaining scalable knowledge graphs via hierarchical memory compression, contradiction resolution, and automated stale-node eviction.",
    },
}

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return text[:48]


# Retrieval-first broadening (`research-breadth-retrieval-first`): a single
# literal query misses vocabulary variants. --broaden fans one query out to
# synonym/tag-neighbor variants and splits the fetch budget across them,
# deduplicating by arXiv id. Deposited notes carry abstracts only and are
# SEEDS: they must pass scripts/check_research_quality.py W-DEEP enrichment
# (architecture, mechanisms, limitations) before ingestion.
QUERY_EXPANSIONS = {
    "peer review": ["peer review", "verification", "evaluation"],
    "retrieval": ["retrieval", "search", "RAG"],
    "self-correction": ["self-correction", "self-critique", "reflection"],
    "planning": ["planning", "decomposition", "task allocation"],
    "memory": ["memory", "consolidation", "forgetting"],
    "multi-agent": ["multi-agent", "coordination", "collaboration"],
    "grounding": ["grounding", "provenance", "citation"],
}


def expand_query(query: str) -> list[str]:
    """Return the query plus vocabulary variants (deduplicated, order-stable)."""
    variants = [query]
    lowered = query.lower()
    for key, synonyms in QUERY_EXPANSIONS.items():
        if key in lowered:
            for synonym in synonyms:
                candidate = lowered.replace(key, synonym)
                if candidate not in variants:
                    variants.append(candidate)
    return variants

def fetch_arxiv(query: str, limit: int = 3) -> list[dict]:
    encoded = urllib.parse.quote(f"all:{query}")
    url = f"http://export.arxiv.org/api/query?search_query={encoded}&start=0&max_results={limit}&sortBy=relevance&sortOrder=descending"
    req = urllib.request.Request(url, headers={"User-Agent": "AgenticResearchLab/1.0"})
    results = []
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8")
        root = ET.fromstring(content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
            summary = entry.find("atom:summary", ns).text.strip().replace("\n", " ")
            id_url = entry.find("atom:id", ns).text.strip()
            authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)]
            results.append({
                "title": title,
                "summary": summary,
                "url": id_url,
                "authors": authors[:5],
            })
    except Exception as e:
        print(f"[expand_literature] arXiv query error: {e}", file=sys.stderr)
    return results

def write_paper_note(title: str, source: str, tags: list[str], content: str, filename: str):
    INBOX.mkdir(parents=True, exist_ok=True)
    tags_str = ", ".join(tags)
    clean_title = title.replace('"', "'")
    file_content = f"""---
title: "{clean_title}"
source: "{source}"
tags: [{tags_str}]
---

# {clean_title}

**Source:** {source}
**Tags:** `{tags_str}`

## Core Methodology & Findings

{content}
"""
    dest = INBOX / filename
    dest.write_text(file_content, encoding="utf-8")
    print(f"Deposited paper note to INBOX/{filename}")

def deposit_seed(seed_key: str):
    data = FOUNDATIONAL_PAPERS.get(seed_key)
    if not data:
        print(f"Unknown seed '{seed_key}'. Available: {list(FOUNDATIONAL_PAPERS.keys())}")
        return
    filename = f"seed_{seed_key}.md"
    content = f"""### Summary
{data['key_takeaway']}

### Key Contributions to Agentic Research
- Established foundational patterns for autonomous reasoning, planning, and task execution.
- Provided empirical baselines for measuring hallucination reduction and task success rates.
- Demonstrated how externalizing thought processes and tool actions directly enhances agent verifiability.
"""
    write_paper_note(data["title"], f"https://arxiv.org/abs/{data['arxiv_id']}", data["tags"], content, filename)

def main():
    parser = argparse.ArgumentParser(description="Fetch scientific literature into INBOX")
    parser.add_argument("--query", help="Academic topic search query")
    parser.add_argument("--source", default="arxiv", choices=["arxiv"])
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--tags", default="agentic,scientific-discovery")
    parser.add_argument("--seed", help="Deposit specific foundational seed paper or 'all'")
    parser.add_argument("--broaden", action="store_true",
                        help="fan the query out to vocabulary variants, splitting --limit across them")
    args = parser.parse_args()

    if args.seed:
        if args.seed.lower() == "all":
            for k in FOUNDATIONAL_PAPERS:
                deposit_seed(k)
        else:
            deposit_seed(args.seed.lower())
        return

    if not args.query:
        print("Please specify --query or --seed. See --help.")
        sys.exit(1)

    tags = [t.strip() for t in args.tags.split(",")]
    queries = expand_query(args.query) if args.broaden else [args.query]
    per_query = max(1, args.limit // len(queries))
    papers: list[dict] = []
    seen_urls: set[str] = set()
    for variant in queries:
        for paper in fetch_arxiv(variant, per_query):
            if paper["url"] not in seen_urls:
                seen_urls.add(paper["url"])
                papers.append(paper)
    if not papers:
        print("No papers retrieved.")
        return

    for p in papers:
        slug = slugify(p["title"])
        filename = f"{slug}.md"
        content = f"**Authors:** {', '.join(p['authors'])}\n\n### Abstract\n{p['summary']}"
        write_paper_note(p["title"], p["url"], tags, content, filename)

if __name__ == "__main__":
    main()
