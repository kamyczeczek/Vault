#!/usr/bin/env python3
"""
autonomous_retriever.py — Intelligent multi-query literature retrieval
with deduplication and source-quality scoring.

Wraps existing expand_literature.py infrastructure and adds:
- Query decomposition from a single question
- Parallel fan-out across arXiv + Jina Reader web fetches
- Source quality ranking
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "INBOX"
EXPAND_SCRIPT = ROOT / "scripts" / "expand_literature.py"

# Heuristics for decomposing a research question into sub-queries
DECOMPOSITION_TEMPLATES = [
    "{q} architecture",
    "{q} survey review",
    "{q} implementation",
    "{q} empirical evaluation",
    "{q} methodology",
]

QUALITY_SCORES = {
    "arxiv": 1.0,
    "jina": 0.8,
    "web": 0.5,
    "blog": 0.3,
}


@dataclass
class RetrieverResult:
    question: str
    sub_queries: list[str]
    papers: list[dict]       # {"title","url","source_type","quality","snippet"}
    coverage_estimate: float  # 0..1
    no_adequate_sources: bool


def decompose_query(question: str) -> list[str]:
    """Split a question into canonical sub-queries for academic search."""
    q = question.strip().rstrip("?").strip()
    queries = {q}  # original
    for tpl in DECOMPOSITION_TEMPLATES:
        candidate = tpl.format(q=q)
        if candidate not in queries:
            queries.add(candidate)
    # Also add synonym-expanded versions from expand_literature logic
    synonyms = _expand_synonyms(q)
    for s in synonyms:
        if s not in queries:
            queries.add(s)
    return list(queries)


def _expand_synonyms(query: str) -> list[str]:
    """Vocabulary expansion based on known synonym clusters."""
    expansions = {
        "autonomous research": ["autonomous scientific discovery", "self-directed research agent"],
        "knowledge gap": ["knowledge gap detection", "information gap agent"],
        "literature review": ["literature search agent", "scientific paper discovery"],
        "research loop": ["autonomous research loop", "iterative research agent"],
        "agent memory": ["agent episodic memory", "verbal reinforcement learning memory"],
        "reflection": ["agent self-reflection", "reflective agent architecture"],
        "tool use": ["tool use in agents", "LLM tool calling"],
        "planning": ["task decomposition planning", "multi-step agent planning"],
    }
    result = []
    q_lower = query.lower()
    for key, variants in expansions.items():
        if key in q_lower:
            for v in variants:
                result.append(v)
    return result


def compute_relevance_score(title: str, summary: str, target_question: str) -> float:
    """Compute a domain relevance score (0.0 - 1.0) for AI/agentic research papers."""
    text = f"{title} {summary}".lower()

    # Must have at least one primary domain term
    core_ai_terms = ["agent", "llm", "language model", "reasoning", "multi-agent", "autonomous research", "scientific discovery", "knowledge gap"]
    if not any(term in text for term in core_ai_terms):
        return 0.1  # Low relevance penalty for non-AI/agent domain papers

    # Irrelevant domain penalties (e.g., traffic, physical autonomous vehicles, wireless networks)
    irrelevant_signals = ["vehicle", "traffic", "lane changing", "cyber-defense", "wireless", "power grid", "peer-evaluation measures"]
    if any(sig in text for sig in irrelevant_signals):
        return 0.1

    # Bonus for specific methodology terms matching the question
    q_words = [w.lower() for w in re.findall(r'\w+', target_question) if len(w) > 3]
    matches = sum(1 for w in q_words if w in text)
    word_overlap_ratio = matches / max(1, len(q_words))

    return min(1.0, 0.5 + 0.5 * word_overlap_ratio)


def _relevance_score(query: str, title: str, content: str) -> float:
    """Score an already-fetched candidate against the complete question."""
    return compute_relevance_score(title, content, query)


def fetch_arxiv(query: str, limit: int = 3, target_question: str = "") -> list[dict]:
    """Fetch candidates and attach relevance before they enter the pipeline."""
    encoded = urllib.parse.quote(f"all:{query}")
    url = f"http://export.arxiv.org/api/query?search_query={encoded}&start=0&max_results={limit}&sortBy=relevance&sortOrder=descending"
    results = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AgenticResearchLab/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8")
        import xml.etree.ElementTree as ET
        root = ET.fromstring(content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
            summary = entry.find("atom:summary", ns).text.strip().replace("\n", " ")
            id_url = entry.find("atom:id", ns).text.strip()
            authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)]

            rel_score = compute_relevance_score(title, summary, target_question or query)
            final_quality = QUALITY_SCORES["arxiv"] * rel_score

            results.append({
                "title": title,
                "url": id_url,
                "source_type": "arxiv",
                "quality": final_quality,
                "relevance": round(rel_score, 2),
                "snippet": summary[:500],
                "authors": authors[:5],
            })
    except Exception as e:
        print(f"[arxiv fetch error for '{query}']: {e}", file=sys.stderr)
    return results


def fetch_via_jina(url: str) -> Optional[str]:
    """Fetch a URL via Jina Reader, return extracted text or None."""
    try:
        jina_url = f"https://r.jina.ai/{url}"
        req = urllib.request.Request(jina_url, headers={"User-Agent": "AgenticResearchLab/1.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None


def get_existing_corpus_titles() -> set[str]:
    """Return a set of lowercased titles already in knowledge/corpus/."""
    import sqlite3
    corp_path = ROOT / "knowledge" / "graph" / "graph.db"
    existing: set[str] = set()
    if corp_path.exists():
        try:
            conn = sqlite3.connect(corp_path)
            rows = conn.execute(
                "SELECT DISTINCT n.natural_id FROM nodes n "
                "JOIN node_tags nt ON nt.node_id=n.node_id "
                "WHERE nt.tag IN ('agentic','research','retrieval','autonomous') "
                "LIMIT 500"
            ).fetchall()
            for r in rows:
                nid = r[0] or ""
                # natural_id is like "00_deep_analysis_popular_autoresearch_projects"
                # strip leading numeric slug
                m = re.search(r"\d+_(.+)", nid)
                if m:
                    existing.add(m.group(1).lower())
            conn.close()
        except Exception:
            pass
    # Also scan corpus md frontmatter
    corpus_dir = ROOT / "knowledge" / "corpus"
    if corpus_dir.exists():
        for f in corpus_dir.glob("*.md"):
            text = f.read_text(encoding="utf-8", errors="replace")
            m = re.search(r'^title:\s*"(.+)"', text, re.MULTILINE)
            if m:
                existing.add(m.group(1).lower().strip())
    return existing


def deduplicate(papers: list[dict], existing_titles: set[str] | None = None) -> list[dict]:
    """Deduplicate among ourselves AND against the live corpus."""
    seen: set[str] = set()
    corpus_titles = existing_titles or get_existing_corpus_titles()
    unique = []
    for p in papers:
        key = p["title"].lower().strip()
        # Skip if exact duplicate in corpus
        if key in corpus_titles:
            continue
        # Skip if we've already seen it
        if key in seen:
            continue
        seen.add(key)
        unique.append(p)
    return unique


def _filter_expand_inbox(query: str, existing_titles: set[str]) -> list[dict]:
    """Filter INBOX files produced by expand_literature — skip duplicates and low-relevance."""
    results = []
    for f in INBOX.glob("*.md"):
        # Only consider files that look like they came from expand (have source: arxiv field)
        content = f.read_text(encoding="utf-8")
        src_match = re.search(r'^source:\s*"([^"]+)"', content, re.MULTILINE)
        title_match = re.search(r'^title:\s*"([^"]+)"', content, re.MULTILINE)
        if not src_match or "arxiv" not in (src_match.group(1) or ""):
            continue
        title = title_match.group(1) if title_match else f.name
        key = title.lower().strip()
        if key in existing_titles:
            continue
        rel = _relevance_score(query, title, content)
        if rel < 0.15:
            continue
        results.append({
            "title": title,
            "url": src_match.group(1),
            "source_type": "arxiv",
            "quality": QUALITY_SCORES["arxiv"] * rel,
            "relevance": round(rel, 2),
            "snippet": content[:500],
        })
    return results


def run_expand_script(query: str, limit: int = 3, broaden: bool = True) -> list[dict]:
    """Delegate to expand_literature.py and parse its output files."""
    # Pre-filter: only run expand if there aren't already relevant INBOX files
    existing_titles = get_existing_corpus_titles()
    prev_hits = _filter_expand_inbox(query, existing_titles)
    if len(prev_hits) >= 2:
        print(f"  [expand] {len(prev_hits)} relevant paper(s) already in INBOX for this query — skipping re-fetch", file=sys.stderr)
        return prev_hits
    cmd = [sys.executable, str(EXPAND_SCRIPT), "--query", query, "--limit", str(limit)]
    if broaden:
        cmd.append("--broaden")
    subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT), timeout=60)
    return _filter_expand_inbox(query, existing_titles)


def retrieve(
    question: str,
    *,
    max_papers: int = 8,
    min_quality: float = 0.5,
) -> RetrieverResult:
    sub_queries = decompose_query(question)
    all_papers: list[dict] = []

    # Strategy 1: Direct arXiv API per sub-query
    for sq in sub_queries[:4]:
        all_papers.extend(fetch_arxiv(sq, limit=2, target_question=question))

    # Strategy 2: Leverage expand_literature.py for broader synthesis
    all_papers.extend(run_expand_script(question, limit=2, broaden=True))

    # Deduplicate against ourselves AND existing corpus
    all_papers = deduplicate(all_papers)

    # Filter by quality AND relevance — reject papers that don't match the query
    MIN_RELEVANCE = 0.25
    filtered = [p for p in all_papers if p["quality"] >= min_quality and p.get("relevance", 0) >= MIN_RELEVANCE]
    filtered.sort(key=lambda p: (-p.get("relevance", 0), -p["quality"], p["title"]))
    filtered = filtered[:max_papers]

    # Estimate coverage: use relevance-weighted average
    if filtered:
        avg_rel = sum(p.get("relevance", 0) for p in filtered) / len(filtered)
        avg_qual = sum(p["quality"] for p in filtered) / len(filtered)
        coverage = min(1.0, avg_rel * avg_qual * (len(filtered) / max_papers) * 2)
    else:
        coverage = 0.0

    return RetrieverResult(
        question=question,
        sub_queries=sub_queries,
        papers=filtered,
        coverage_estimate=round(coverage, 2),
        no_adequate_sources=coverage < 0.4,
    )


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("question", help="Research question to retrieve for")
    parser.add_argument("--max-papers", type=int, default=8)
    parser.add_argument("--min-quality", type=float, default=0.5)
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    result = retrieve(args.question, max_papers=args.max_papers, min_quality=args.min_quality)
    if args.json:
        print(json.dumps({
            "question": result.question,
            "sub_queries": result.sub_queries,
            "coverage_estimate": result.coverage_estimate,
            "no_adequate_sources": result.no_adequate_sources,
            "papers": result.papers,
        }, indent=2))
    else:
        print(f"Question: {result.question}")
        print(f"Sub-queries tried: {len(result.sub_queries)}")
        print(f"Papers found: {len(result.papers)}")
        print(f"Coverage estimate: {result.coverage_estimate}")
        print(f"No adequate sources: {result.no_adequate_sources}")
        print()
        for i, p in enumerate(result.papers, 1):
            print(f"  [{i}] ({p['source_type']}, q={p['quality']}) {p['title']}")
            print(f"      {p['url']}")
    return 0 if not result.no_adequate_sources else 1


if __name__ == "__main__":
    sys.exit(main())
