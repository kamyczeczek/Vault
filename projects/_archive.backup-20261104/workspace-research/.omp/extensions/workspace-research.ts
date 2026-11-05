import { execSync } from "child_process";
import { readFileSync, existsSync, readdirSync } from "fs";
import { resolve } from "path";

export default function initWorkspaceResearchExtension(pi: { on: (ev: string, h: (e: unknown) => unknown) => void; registerCommand?: (n: string, c: { description: string; handler: () => void }) => void }) {
  function getGraphFingerprint(): string {
    const candidates = [
      resolve(process.cwd(), "knowledge/graph/.graph_fingerprint"),
      resolve(process.cwd(), "../../projects/workspace-research/knowledge/graph/.graph_fingerprint"),
    ];
    for (const p of candidates) {
      if (existsSync(p)) { try { return readFileSync(p, "utf-8").trim(); } catch {} }
    }
    return "";
  }

  function currentFingerprintFromDigest(): string {
    const candidates = [
      resolve(process.cwd(), "knowledge/graph/GRAPH-DIGEST.md"),
      resolve(process.cwd(), "../../projects/workspace-research/knowledge/graph/GRAPH-DIGEST.md"),
    ];
    for (const p of candidates) {
      if (existsSync(p)) {
        try {
          const first = readFileSync(p, "utf-8").split("\n")[2] || "";
          const m = first.match(/fingerprint:\s*([0-9a-f]{12})/);
          if (m) return m[1];
        } catch {}
      }
    }
    return "";
  }

  function getGraphDigest(): string {
    const candidates = [
      resolve(process.cwd(), "knowledge/graph/GRAPH-DIGEST.md"),
      resolve(process.cwd(), "../../projects/workspace-research/knowledge/graph/GRAPH-DIGEST.md"),
    ];
    const BUDGET = 2000; // W2: progressive-disclosure cap; drill down via ask.py --tag
    for (const p of candidates) {
      if (existsSync(p)) {
        try {
          const raw = readFileSync(p, "utf-8").trim();
          if (raw.length <= BUDGET) return raw;
          // header + finger + budget'd tail; agent pulls bodies via ask.py --raw
          return raw.slice(0, BUDGET) + "\n... [truncated to " + BUDGET + " chars — query graph via `python knowledge/graph/ask.py --tag <t> --limit N` or `--raw`]";
        } catch {}
      }
    }
  }

  function getOpenCandidates(): string {
    const candidates = [
      resolve(process.cwd(), "reflection/candidates"),
      resolve(process.cwd(), "../../projects/workspace-research/reflection/candidates"),
    ];
    for (const p of candidates) {
      if (existsSync(p)) { try { return readdirSync(p).filter((f: string) => f.endsWith(".jsonl")).map((f: string) => `- ${f}`).join("\n") || "(no candidates yet)"; } catch {} }
    }
    return "(no candidates yet)";
  }

  function getTopics(): string {
    const p = resolve(process.cwd(), "knowledge/topics.md");
    try { return readFileSync(p, "utf-8").trim().slice(0, 2000); } catch { return "(topics missing)"; }
  }

  function getContext(): string {
    const fp = getGraphFingerprint();
    const digestFp = currentFingerprintFromDigest();
    const stale = fp && digestFp && fp !== digestFp
      ? `\n⚠️ STALE_DIGEST: .graph_fingerprint=${fp} but GRAPH-DIGEST fingerprint=${digestFp} — run \`python knowledge/graph/watch.py --once\` before routing (refuses determinism).`
      : "";
    const lines: string[] = [];
    lines.push("# [AUTO-INJECTED: workspace-research worker] Context-Engineering & ICM Knowledge Base" + stale);
    lines.push("");
    lines.push("## Pipeline Contract (ICM rules):");
    lines.push("- Knowledge as files: every finding => markdown chunk in knowledge/corpus/ (front-matter id/title/tags).");
    lines.push("- Graph backbone: the brain is a DERIVED index (FTS5 SQLite) rebuilt from corpus by build_graph.py.");
    lines.push("- Progressive disclosure: only fingerprint+counts+topics injected by default; pull bodies via `python knowledge/graph/ask.py --tag <t> --limit N --raw`.");
    lines.push("- Reflection is spawned: isolated agent, graph-injected, writes to reflection/ only.");
    lines.push("- Determinism: corpus is the source of truth; never hand-edit graph.db / GRAPH-DIGEST.md.");
    lines.push("");
    lines.push("## Fingerprint:");
    lines.push(fp ? `fingerprint: ${fp}${stale}` : "(fingerprint missing — run build_graph.py)");
    lines.push("");
    lines.push("## Topics:");
    lines.push(getTopics());
    lines.push("");
    lines.push("## Open Reflection Candidates:");
    lines.push(getOpenCandidates());
    lines.push("");
    lines.push("--- Knowledge Graph (budgeted, auto-injected — query for bodies) ---");
    lines.push(getGraphDigest());
    lines.push("");
    lines.push("Brain tools: `python knowledge/graph/ask.py \"<question>\" [--tag <t> ...] [--limit N] [--raw]`.");
    lines.push("Graph rebuild: `python knowledge/graph/build_graph.py`.");
    lines.push("Reflection spawn: `python pipeline/06_reflect/spawn.py --topic <slug>`.");
    return lines.join("\n");
  }

  pi.on("before_agent_start", (event: unknown) => {
    const ev = event as { systemPrompt: string[] };
    return { systemPrompt: [...ev.systemPrompt, getContext()] };
  });

  if (pi.registerCommand) {
    pi.registerCommand("workspace-research-query", {
      description: "Query the workspace-research knowledge graph",
      handler: () => {
        const q = "What are the ICM determinism rules?";
        try {
          const out = execSync(`python knowledge/graph/ask.py "${q}"`, { encoding: "utf-8" });
          console.log(out);
        } catch (err: unknown) {
          const msg = err instanceof Error ? err.message : String(err);
          console.error(`[workspace-research] Query failed:`, msg);
        }
      },
    });
    pi.registerCommand("workspace-research-graph", {
      description: "Rebuild the workspace-research knowledge graph",
      handler: () => {
        try {
          const out = execSync(`python knowledge/graph/build_graph.py`, { encoding: "utf-8" });
          console.log(out);
        } catch (err: unknown) {
          const msg = err instanceof Error ? err.message : String(err);
          console.error(`[workspace-research] Graph build failed:`, msg);
        }
      },
    });
  }

  return { name: "workspace-research", version: "1.0.0", description: "Workspace-Research worker extension (auto-injects project graph + corpus)", getContext };
}
