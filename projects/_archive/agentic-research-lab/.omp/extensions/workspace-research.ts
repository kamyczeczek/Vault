// .omp/extensions/workspace-research.ts
// Workspace-Research digest injector (agentic-research-lab).
//
// On `before_agent_start`, appends knowledge/graph/GRAPH-DIGEST.md (+ the live
// fingerprint and knowledge/topics.md) to the system prompt, so reflection
// agents reason over the derived index, never free recall. Used by
// pipeline/06_reflect/spawn.py via `omp launch --extension <this file>`.
//
// Fail-open by contract: a missing or unreadable digest must never block a
// launch (spawn.py already embeds the same digest inline in its prompt).
// Runtime telemetry must never prevent a valid launch either.
import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";
import { readFile } from "node:fs/promises";
import { join } from "node:path";

const DIGEST_REL = "knowledge/graph/GRAPH-DIGEST.md";
const TOPICS_REL = "knowledge/topics.md";
const FINGERPRINT_REL = "knowledge/graph/.graph_fingerprint";
const MAX_DIGEST_CHARS = 12000;
const MAX_TOPICS_CHARS = 2000;

async function readCapped(path: string, cap: number): Promise<string | null> {
  try {
    const text = await readFile(path, "utf-8");
    return text.length > cap ? text.slice(0, cap) + "\n…[truncated]" : text;
  } catch {
    return null;
  }
}

export default function workspaceResearch(pi: ExtensionAPI) {
  pi.on("before_agent_start", async (event, ctx) => {
    const [digest, topics, fingerprint] = await Promise.all([
      readCapped(join(ctx.cwd, DIGEST_REL), MAX_DIGEST_CHARS),
      readCapped(join(ctx.cwd, TOPICS_REL), MAX_TOPICS_CHARS),
      readCapped(join(ctx.cwd, FINGERPRINT_REL), 64),
    ]);
    if (!digest) {
      if (ctx.hasUI) {
        ctx.ui.notify("workspace-research: digest unreadable, skipping injection", "warning");
      }
      return;
    }
    const lines = [
      "--- workspace-research auto-injected context (GRAPH-DIGEST.md) ---",
      `fingerprint: ${(fingerprint ?? "unknown").trim()}`,
      digest,
    ];
    if (topics) {
      lines.push("--- knowledge/topics.md ---", topics);
    }
    return { systemPrompt: [...event.systemPrompt, lines.join("\n")] };
  });
}
