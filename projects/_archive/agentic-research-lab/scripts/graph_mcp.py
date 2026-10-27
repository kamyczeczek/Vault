"""FastMCP wrapper: knowledge graph as goose tool (Phase 2b)."""

from fastmcp import FastMCP
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASK = ROOT / "knowledge" / "graph" / "ask.py"
ROUTE = ROOT / "pipeline" / "06_reflect" / "route.py"

mcp = FastMCP("graph")


@mcp.tool()
def query_graph(question: str, limit: int = 5) -> str:
    """Query the knowledge graph for chunks matching a question. Returns chunk IDs, titles, snippets."""
    r = subprocess.run(
        [sys.executable, str(ASK), question, "--limit", str(limit)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return r.stdout if r.returncode == 0 else f"ERROR (rc={r.returncode}): {r.stderr.strip()}"


@mcp.tool()
def route_tags(tags: list[str], limit: int = 12) -> str:
    """Deterministic tag-intersection routing. Returns chunk IDs matching ALL given tags."""
    args = [sys.executable, str(ROUTE)] + [f"--tag={t}" for t in tags] + ["--limit", str(limit)]
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
    return r.stdout if r.returncode == 0 else f"ERROR (rc={r.returncode}): {r.stderr.strip()}"


if __name__ == "__main__":
    mcp.run()
