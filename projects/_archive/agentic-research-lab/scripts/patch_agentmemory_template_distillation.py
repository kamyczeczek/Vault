"""Patch @agentmemory dist builds for template-based distillation (no LLM required).

Three env-gated patches, applied idempotently to index.mjs + src-*.mjs in every
npx cache dir, with .orig backups and node --check verification.

Env (set in .pi/agent/mcp.json, agentmemory server block):
  AGENTMEMORY_TEMPLATE_SUMMARIZE=true   # deterministic session summaries when no LLM provider
  AGENTMEMORY_TEMPLATE_SEMANTIC=true    # deterministic semantic facts from summaries when no LLM provider
  AGENTMEMORY_SEMANTIC_MIN_SUMMARIES=1  # lower the semantic tier floor (default 5)

Re-run is safe: each patch checks a marker string first.
"""
from __future__ import annotations

import glob
import os
import re
import shutil
import subprocess
import sys

MARKER = "AGENTMEMORY_TEMPLATE_DISTILLATION_PATCH_V1"
T = "\t"  # source files are tab-indented

P1_OLD = (
    T + 'if (provider.name === "noop") {\n'
    + T + T + 'logger.info("Summarize skipped — no LLM provider configured", { sessionId });\n'
    + T + T + "return {\n"
    + T + T + T + 'success: false,\n'
    + T + T + T + 'error: "no_provider",\n'
    + T + T + T + 'reason: "No LLM provider key set; Summarize is a no-op. Set ANTHROPIC_API_KEY (or GEMINI/OPENROUTER/MINIMAX) in ~/.agentmemory/.env to enable."\n'
    + T + T + "};\n"
    + T + "}"
)

P1_NEW = (
    T + 'if (provider.name === "noop") {\n'
    + T + T + 'if (process.env.AGENTMEMORY_TEMPLATE_SUMMARIZE === "true") {\n'
    + T + T + T + "// " + MARKER + ": deterministic summary when no LLM provider\n"
    + T + T + T + "const tNow = new Date().toISOString();\n"
    + T + T + T + "const intents = [];\n"
    + T + T + T + "const toolCounts = {};\n"
    + T + T + T + "const tFiles = new Set();\n"
    + T + T + T + "const tConcepts = new Set();\n"
    + T + T + T + "let tErrors = 0;\n"
    + T + T + T + "for (const o of compressed) {\n"
    + T + T + T + T + 'const tt = String(o.title || "unknown").slice(0, 60);\n'
    + T + T + T + T + "toolCounts[tt] = (toolCounts[tt] || 0) + 1;\n"
    + T + T + T + T + "if (Array.isArray(o.files)) for (const fl of o.files) if (fl) tFiles.add(String(fl).slice(0, 120));\n"
    + T + T + T + T + "if (Array.isArray(o.concepts)) for (const c of o.concepts) if (c) tConcepts.add(String(c));\n"
    + T + T + T + T + 'if (o.title === "prompt_submit" || o.type === "conversation") {\n'
    + T + T + T + T + T + 'const intent = String(o.subtitle || o.narrative || "").trim().slice(0, 120);\n'
    + T + T + T + T + T + "if (intent && !intents.includes(intent)) intents.push(intent);\n"
    + T + T + T + T + "}\n"
    + T + T + T + T + 'const narr = String(o.narrative || "").slice(0, 400);\n'
    + T + T + T + T + 'if (o.origin && o.origin.channel === "tool" && /failed|error|reject|exit code [1-9]/i.test(narr)) tErrors++;\n'
    + T + T + T + "}\n"
    + T + T + T + "const topTools = Object.entries(toolCounts).sort((a, b) => b[1] - a[1]).slice(0, 4).map((e) => e[0] + \" x\" + e[1]);\n"
    + T + T + T + "const tSummary = {\n"
    + T + T + T + T + "sessionId,\n"
    + T + T + T + T + "project: session.project || \"unknown\",\n"
    + T + T + T + T + "title: intents.length ? String(intents[0]).slice(0, 100) : (\"Session \" + sessionId).slice(0, 100),\n"
    + T + T + T + T + "narrative: \"Template summary (no LLM): \" + compressed.length + \" observations in \" + (session.project || \"unknown\") + \". Tools: \" + (topTools.join(\", \") || \"none\") + \". Errors seen: \" + tErrors + \". Files: \" + ([...tFiles].slice(0, 6).join(\", \") || \"none\") + \".\",\n"
    + T + T + T + T + "keyDecisions: intents.slice(0, 5),\n"
    + T + T + T + T + "filesModified: [...tFiles].slice(0, 20),\n"
    + T + T + T + T + "concepts: [...tConcepts].slice(0, 10),\n"
    + T + T + T + T + "observationCount: compressed.length,\n"
    + T + T + T + T + 'method: "template",\n'
    + T + T + T + T + "createdAt: tNow,\n"
    + T + T + T + T + "updatedAt: tNow\n"
    + T + T + T + "};\n"
    + T + T + T + "const tValidation = validateOutput(SummaryOutputSchema, {\n"
    + T + T + T + T + "title: tSummary.title,\n"
    + T + T + T + T + "narrative: tSummary.narrative,\n"
    + T + T + T + T + "keyDecisions: tSummary.keyDecisions,\n"
    + T + T + T + T + "filesModified: tSummary.filesModified,\n"
    + T + T + T + T + "concepts: tSummary.concepts\n"
    + T + T + T + '}, "mem::summarize-template");\n'
    + T + T + T + "if (!tValidation.valid) {\n"
    + T + T + T + T + 'logger.warn("Template summary validation failed", { sessionId, errors: tValidation.result.errors });\n'
    + T + T + T + T + "return { success: false, error: \"template_validation_failed\" };\n"
    + T + T + T + "}\n"
    + T + T + T + "await kv.set(KV.summaries, sessionId, tSummary);\n"
    + T + T + T + 'await safeAudit(kv, "compress", "mem::summarize", [sessionId], {\n'
    + T + T + T + T + "title: tSummary.title,\n"
    + T + T + T + T + "observationCount: compressed.length,\n"
    + T + T + T + T + 'method: "template"\n'
    + T + T + T + "});\n"
    + T + T + T + 'logger.info("Session summarized (template, no LLM)", { sessionId, title: tSummary.title, intents: intents.length });\n'
    + T + T + T + "return { success: true, summary: tSummary, qualityScore: 0, method: \"template\" };\n"
    + T + T + "}\n"
    + T + T + 'logger.info("Summarize skipped — no LLM provider configured", { sessionId });\n'
    + T + T + "return {\n"
    + T + T + T + "success: false,\n"
    + T + T + T + 'error: "no_provider",\n'
    + T + T + T + 'reason: "No LLM provider key set; Summarize is a no-op. Set ANTHROPIC_API_KEY (or GEMINI/OPENROUTER/MINIMAX) in ~/.agentmemory/.env to enable."\n'
    + T + T + "};\n"
    + T + "}"
)

P2_OLD = "if (summaries.length >= 5) {"
P2_NEW = "if (summaries.length >= (Number(process.env.AGENTMEMORY_SEMANTIC_MIN_SUMMARIES ?? 5))) { // " + MARKER

P3_OLD = (
    T + T + T + T + T + "}\n"
    + T + T + T + T + T + "results.semantic = {\n"
    + T + T + T + T + T + T + "newFacts,\n"
    + T + T + T + T + T + T + "totalSummaries: summaries.length\n"
    + T + T + T + T + T + "};"
)

P3_NEW = (
    T + T + T + T + T + "}\n"
    + T + T + T + T + T + 'if (newFacts === 0 && provider.name === "noop" && process.env.AGENTMEMORY_TEMPLATE_SEMANTIC === "true") {\n'
    + T + T + T + T + T + T + "// " + MARKER + ": deterministic semantic fallback (citation chain preserved)\n"
    + T + T + T + T + T + T + "for (const rs of recentSummaries) {\n"
    + T + T + T + T + T + T + T + "const facts = [];\n"
    + T + T + T + T + T + T + T + "if (Array.isArray(rs.keyDecisions)) for (const kd of rs.keyDecisions) {\n"
    + T + T + T + T + T + T + T + T + "const f = String(kd).trim();\n"
    + T + T + T + T + T + T + T + T + "if (f.length >= 8) facts.push(f);\n"
    + T + T + T + T + T + T + T + "}\n"
    + T + T + T + T + T + T + T + "if (facts.length === 0 && rs.title) facts.push(\"Session: \" + String(rs.title).trim().slice(0, 140));\n"
    + T + T + T + T + T + T + T + "const srcIds = rs.sessionId ? [rs.sessionId] : recentSummaries.map((x) => x.sessionId).filter(Boolean);\n"
    + T + T + T + T + T + T + T + "for (const fact of facts.slice(0, 6)) {\n"
    + T + T + T + T + T + T + T + T + "const dup = existingSemantic.find((s) => s.fact.toLowerCase() === fact.toLowerCase());\n"
    + T + T + T + T + T + T + T + T + "if (dup) {\n"
    + T + T + T + T + T + T + T + T + T + "dup.accessCount = (dup.accessCount || 1) + 1;\n"
    + T + T + T + T + T + T + T + T + T + "dup.lastAccessedAt = now;\n"
    + T + T + T + T + T + T + T + T + T + "dup.updatedAt = now;\n"
    + T + T + T + T + T + T + T + T + T + "await kv.set(KV.semantic, dup.id, dup);\n"
    + T + T + T + T + T + T + T + T + "} else {\n"
    + T + T + T + T + T + T + T + T + T + "const sem = {\n"
    + T + T + T + T + T + T + T + T + T + T + 'id: generateId("sem"),\n'
    + T + T + T + T + T + T + T + T + T + T + "fact,\n"
    + T + T + T + T + T + T + T + T + T + T + "confidence: 0.4,\n"
    + T + T + T + T + T + T + T + T + T + T + "sourceSessionIds: srcIds,\n"
    + T + T + T + T + T + T + T + T + T + T + "sourceMemoryIds: [],\n"
    + T + T + T + T + T + T + T + T + T + T + "accessCount: 1,\n"
    + T + T + T + T + T + T + T + T + T + T + "lastAccessedAt: now,\n"
    + T + T + T + T + T + T + T + T + T + T + "strength: 0.4,\n"
    + T + T + T + T + T + T + T + T + T + T + "createdAt: now,\n"
    + T + T + T + T + T + T + T + T + T + T + "updatedAt: now,\n"
    + T + T + T + T + T + T + T + T + T + T + 'method: "template"\n'
    + T + T + T + T + T + T + T + T + T + "};\n"
    + T + T + T + T + T + T + T + T + T + "await kv.set(KV.semantic, sem.id, sem);\n"
    + T + T + T + T + T + T + T + T + T + "newFacts++;\n"
    + T + T + T + T + T + T + T + T + "}\n"
    + T + T + T + T + T + T + T + "}\n"
    + T + T + T + T + T + T + "}\n"
    + T + T + T + T + T + "}\n"
    + T + T + T + T + T + "results.semantic = {\n"
    + T + T + T + T + T + T + "newFacts,\n"
    + T + T + T + T + T + T + "totalSummaries: summaries.length\n"
    + T + T + T + T + T + "};"
)


def add_tab(block: str) -> str:
    return "\n".join(("\t" + line) if line else line for line in block.split("\n"))


# The noop block in dist sits one indent level deeper than P1_OLD/P1_NEW as authored.
P1_MATCH = add_tab(P1_OLD)
P1_REPLACE = add_tab(P1_NEW)


def patch_file(path: str) -> tuple[str, str]:
    s = open(path, encoding="utf-8").read()
    if MARKER in s:
        return "SKIP", "already patched"
    problems = []
    for name, old, new in (("P1", P1_MATCH, P1_REPLACE), ("P2", P2_OLD, P2_NEW), ("P3", P3_OLD, P3_NEW)):
        if s.count(old) != 1:
            problems.append(f"{name}: anchor count={s.count(old)}")
        else:
            s = s.replace(old, new, 1)
    if problems:
        return "FAILED", "; ".join(problems)
    if not s.endswith("\n"):
        s += "\n"
    bak = path + ".orig"
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
    open(path, "w", encoding="utf-8", newline="").write(s)
    check = subprocess.run(["node", "--check", path], capture_output=True, text=True)
    if check.returncode != 0:
        shutil.move(bak, path)
        return "ROLLBACK", check.stderr.strip()[:300]
    return "PATCHED", "P1+P2+P3, syntax OK, backup at " + bak


def main() -> int:
    targets = sorted(
        f
        for f in glob.glob(
            os.path.expanduser(
                r"C:\Users\Mateusz\AppData\Local\npm-cache\_npx\**\@agentmemory\agentmemory\dist\*.mjs"
            ),
            recursive=True,
        )
        if re.search(r"(^|[\\/])(index|src-[^\\/]+)\.mjs$", f)
    )
    if not targets:
        print("no dist targets found")
        return 1
    rc = 0
    for t in targets:
        status, detail = patch_file(t)
        print(f"{status:9s} {t}\n          {detail}")
        if status in ("FAILED", "ROLLBACK"):
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
