import { readFileSync, existsSync } from "fs";
import { resolve } from "path";

export default function initTsBrainExtension(pi: { on: (ev: string, h: (e: unknown) => unknown) => void; registerCommand?: (n: string, c: { description: string; handler: () => void }) => void }) {
  const getDigest = (): string => {
    const digestPath = resolve(process.cwd(), "../internal/digest.md");
    if (!existsSync(digestPath)) {
      return "(digest not yet built — run `python brain/internal/build_reflection_index.py && python brain/internal/gen_digest.py`)";
    }
    try {
      return readFileSync(digestPath, "utf-8").trim().slice(0, 4000);
    } catch {
      return "(digest file unreadable)";
    }
  };

  const buildTsContext = (): string => {
    const lines: string[] = [];
    lines.push("# [AUTO-INJECTED: ts-brain worker] Time Series Knowledge Brain");
    lines.push("");
    lines.push("This worker session has graph knowledge injected. Query deterministically:");
    lines.push("- `python brain/internal/ask.py \"<question>\" --limit 5`");
    lines.push("- `python brain/internal/ask.py rejected --limit 5`");
    lines.push("");
    lines.push("--- Scar digest (live) ---");
    lines.push(getDigest());
    lines.push("");
    lines.push("File contract: write results to an agreed file; orchestrator reads files only.");
    return lines.join("\n");
  };

  pi.on("before_agent_start", (event: unknown) => {
    const ev = event as { systemPrompt: string[] };
    return { systemPrompt: [...ev.systemPrompt, buildTsContext()] };
  });

  if (pi.registerCommand) {
    pi.registerCommand("ts-brain-query", {
      description: "Query the ts-brain knowledge store",
      handler: () => {
        const question = "What is the locked H=720 evaluation protocol?";
        try {
          const { execSync } = require("child_process");
          const out = execSync(`python brain/internal/ask.py "${question}" --limit 3`, { encoding: "utf-8" });
          console.log(out);
        } catch (err: unknown) {
          const msg = err instanceof Error ? err.message : String(err);
          console.error(`[ts-brain] Query failed:`, msg);
        }
      },
    });
  }

  return {
    name: "ts-brain",
    version: "1.0.0",
    description: "Isolated ts-brain worker extension (brain/worker only)",
    getContext: buildTsContext,
  };
}
