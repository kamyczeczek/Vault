---
name: token-hygiene
description: Behavioral guardrails for token efficiency in this workspace (measured against its own transcripts). Load to apply the hygiene rules to current work.
disable-model-invocation: true
---

# Token Hygiene — DevSkills

Behavioral guardrails measured against this workspace's own transcripts.
Evidence: `TOKEN-EFFICIENCY.md`, `scripts/pi_cache_forensics.py`.
Re-measure after any change: `python3 scripts/pi_cache_forensics.py --since 7d`.

## The rule that matters more than all others

Context is re-paid on every turn. A 30K-token context at turn 350 is re-processed
350 times. Everything below is "make the context smaller and shorter."

## Anti-SubRetrv — check context before re-reading

Before calling `read` on a file:

1. **Is it already in this conversation?** Look at previous tool results. If the
   relevant section is visible, do not re-read.
2. **Do you know the lines you need?** If yes, `read` with `offset`/`limit` —
   never the whole file. Target: under 100 lines per read on source files.
3. **Is it in an indexed repo?** Use `search_symbols` → `get_symbol_source`
   instead (D16). 1,300 chars vs 7,669 measured on `audit_map_state`.

Re-read ratio in history: 1.17×. Target: 1.0. A second read of the same
`file:offset` range in the same session is a bug unless the file changed on
disk between reads.

## Anti-ReTest — gate test runs on a source change

Before running a test suite or verification command:

- **Did a source file change since the last identical run?** No → do not run it.
- **Is the previous run visible in this session and green?** No source delta
  means the result is identical; re-running burns tokens to learn nothing.

Gate test runs on a confirmed code delta. The only exception: verifying a fix
for a failure you just introduced.

## Persist helpers as scripts, not one-off snippets

If a bash/Powershell snippet is more than ~3 lines and likely reusable, write it
to `scripts/<name>.py` (or `.sh`) and run the file. Two benefits:

- Next session reads the file in one `read` call, no regeneration.
- The output is identical every run — no drift in the "did I do the same thing
  last time?" question.

This workspace already does this for `pi_cache_forensics.py`,
`pi_context_growth.py`, `mcp_call.py`. Follow that pattern.

## Scope elision — no blind whole-file reads

For source code in indexed repos, never `read` a file to find a symbol. Use:

```
search_symbols(query=...)         → file::name#kind ids
get_symbol_source(symbol_id=...)  → exact function/class body
```

For source code not in an indexed repo, or for config/markdown files:

```
grep -n "pattern" file      → line numbers
read file offset=X limit=Y  → only the relevant block
```

Whole-file reads are reserved for: files under ~80 lines, files you are
creating with `write`, and files where structural context matters more than
content (a new project's `CLAUDE.md` on first contact).

## Delta edits, not rewrites

- **`write`**: new files only. Re-writing an existing file costs O(N) tokens on
  every pass; the edit tool costs O(Δ).
- **`edit`**: all modifications to existing files, including multi-spot changes
  (use multiple `edits[]` entries in one call, not sequential single-spot
  edits).
- **`edit`'s `oldText` must match uniquely.** If it does not match, stop and
  re-read the target region before retrying — do not widen the match
  heuristically.

## Batch independent calls — one tool message, not five

When you need to do several things that don't depend on each other's output:

```javascript
// Inside codemode, one call instead of five
const [a, b, c, d, e] = await Promise.allSettled([
  tools.memory_search({ query: "..." }),
  tools.bash({ command: "git status --porcelain | head -20" }),
  tools.bash({ command: "grep -n 'def main' scripts/foo.py" }),
  tools.read({ path: "AGENTS.md" }),
  tools.bash({ command: "ls -1 scripts/ | head -20" }),
]);
```

Each separate tool call is a separate entry in the history array; each entry
is re-processed on every subsequent turn. Batching five independent calls into
one `codemode` invocation reduces the history by four messages and one
full-context re-process per subsequent turn.

**Do not batch dependent calls** — if call B needs call A's output, they must
be separate. This only applies to genuinely independent operations.

## Bash output caps

Every `bash` / `powershell` call in this workspace defaults to the pi hard cap
(50 KB / 2000 lines). Do not fight it by re-running; instead, shape the
command to return only what you need:

```
head -n 30          # first N lines
tail -n 30          # last N lines
wc -l               # just the count
grep -n "pattern"   # just the matches
| grep -i error     # filter at the shell level
```

If a command genuinely produces more than you can work with, the useful part
is in a file; `read` the file with offset/limit instead.

## Command preflight

Before running a Windows shell command, reject these patterns and rewrite the
operation as a small checked-in helper script:

- inline `python -c` or `powershell -Command`, especially with nested quotes or
  repository paths;
- Unix-only filters such as `head` or `tail` in PowerShell;
- pipelines where the displayed exit code belongs to the pipeline rather than
  the command being verified.

Use PowerShell-native selectors, or persist a Python/PowerShell helper and run
it directly. Capture the real exit code before formatting output.

For source inspection, use symbol retrieval first: query the symbol in
`scripts/check_workspace_integrity.py` (for example, `check_r13_report_citations`)
and retrieve that function body once, rather than grepping several literals in
the same source region.

## The one thing this skill does not cover

Bash/test/git output is 59.4% of tool output. No rule here touches it except
the batching rule above and the command-shaping habit. The `jCodeMunch` symbol
tools (D16) handle source-file reads (12.1% of tool output). The 59.4% is
addressed by batching + command caps, not by a new tool.
