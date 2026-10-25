# Token efficiency — measured findings

> D13. Evidence for the guardrails in `AGENTS.md`. Regenerate before trusting a number.

Numbers from `scripts/pi_token_audit.py`, `pi_context_growth.py`, `pi_cache_forensics.py`
over 29 sessions (60d), 69.5M tokens total. Regenerate with:

```bash
python3 scripts/pi_token_audit.py --since 60d
python3 scripts/pi_cache_forensics.py --since 60d
python3 scripts/pi_context_growth.py --latest --cwd <project>
```

## Where the tokens go

| class | tokens | share |
|---|---|---|
| input (full price) | 15.3M | 21.8% |
| cache read | 54.2M | 77.5% |
| cache write | 0 | 0% |
| output | 480K | 0.7% |

Cache hit ratio 78.0%. Target is >90%.

## What actually breaks the prefix cache

Attribution uses pi's own counters: a turn with `cacheRead == 0` and `input > 2000`
re-processed the whole prefix at full price.

| cause | turns | full-price tokens | share |
|---|---|---|---|
| provider with no cache at all | 242 | 3.98M | 61.2% |
| thinking-level change mid-session | 25 | 812K | 12.5% |
| model switch | 23 | 502K | 7.7% |
| compaction | 5 | 362K | 5.6% |
| context_edit | 3 | 202K | 3.1% |

Hit ratio per model, same session, no switching:

| model | hit ratio | turns |
|---|---|---|
| agnes-3-flash | 88.6% | 605 |
| space-bunny-alpha-bynara | 91.7% | 22 |
| gemini/gemini-3.5-flash-lite | 72.8% | 283 |
| oc/nemotron-3.5-lightning-free | **0.0%** | 250 |

## Findings

1. **Caching is a property of the model, not the task.** One model held 90.3% for 363
   consecutive turns in a single session. Stability beats cleverness.
2. **A non-caching provider is the single largest waste source.** `oc/*` re-paid the full
   prefix 250 times, 4.0M tokens. Never route to a provider that reports `cacheRead: 0`.
3. **cacheWrite is 0 in every session.** This provider tier has no write-side accounting,
   so cold prefixes are invisible in cost data. Detect them via `cacheRead == 0`.
4. **Thinking-level changes invalidate the prefix.** 25 cold prefixes, 812K tokens.
5. **Tool output is 11.7× assistant output** (1.71M chars vs 146K chars). Tool output is
   the main context filler and gets re-paid every turn. This is the biggest untapped lever.

## Decision: no model routing (D13)

Per user, specific model availability is not stable, so architect/editor model delegation
is off the table. Rule instead: **one model for the whole session, never switch.** Roles
are documentation, not routing. When a model stops being available, pick another at session
start — do not switch mid-session.

Rejected alternatives:

- *Config-driven role→model map with fallbacks.* Adds a file to maintain on every
  availability change, and role separation only pays if the cheap model is actually
  available. Stability of one model already yields 88–90% hit ratio.
- *Runtime cache-ratio guard.* A pi extension watching `cacheRead` could flag degradation,
  but the first turn of a bad session is already paid, and the guard needs model IDs to
  compare against. The measurement scripts already answer "was it worth it" after the fact.

## jCodeMunch (D16) — symbol-level retrieval

Verified: `jgravelle/jcodemunch-mcp`, 2,721 stars, 365 forks, pushed 2026-09-30,
Python + tree-sitter, MIT-adjacent (`NOASSERTION`). Installed v1.108.319 via
`uv tool install`; wired into `~/.pi/agent/mcp.json` as `jcodemunch` with
`exposure: codemode` and only `menu`/`route`/`set_tool_tier` declared.

**Claims verified locally** (repo `kamyczeczek/agentic-research-lab`):

| check | result |
|---|---|
| `search_symbols` → 3 hits | 629 chars (~180 tok) |
| `get_symbol_source` on `audit_map_state` | 1,300 chars (~372 tok) |
| same file via plain `read` | 7,669 chars — **5.9× reduction** |
| `find_importers` | works (34 tok) |
| `get_call_hierarchy` | works, 1 caller / 28 callees, 3,069 chars |
| server tool surface | 6 of 94 tools, 1,050 of 27,782 schema tokens |

**The 90-tool objection does not hold.** pi's `codemode` exposure means MCP tool
schemas are not declared to the model, so they never enter the system prefix at
all. Independently, jCodeMunch's own `counter` surface shows 6 of 94 tools
visible, and its docs state the schema block is paid ~once per cache lifetime
then at cache-read rates, not per request — reading that as a per-request saving
overstates it by ~10×.

**The real ceiling, measured on this workspace's own history.** Tool output
breaks down as: `bash` 59.4%, `read` 27.1%, `codemode` 6.3%, `powershell` 5.2%.
Of the `read` share, source files are 12.1% of *all* tool output; docs another
12.1%. So symbol-level retrieval addresses **12.1% of tool output**, and at a
70% cut on those reads saves 8.5%. The advertised 96.5% / 28.3× is a per-read
figure; as a share of this agent's real context it is much smaller, because
shell/test/git output dominates and jCodeMunch does not touch it. **Shipping the
server without capping `bash` output buys ~8%, not ~96%.**

**Operational facts.** Repo resolution is by git remote name
(`kamyczeczek/agentic-research-lab`), not folder path. The CLI requires
absolute paths — relative ones fail. `get_symbol_source` needs a
`file::name#kind` symbol id; `path` + `symbol` is rejected. `menu` costs 5,139
chars (~1,469 tok) per call, so it is a discovery call, not a per-symbol call.

**Rejected.** Installing the PreToolUse/PostToolUse enforcement hooks: they
rewrite client settings files and a global `CLAUDE.md`, which conflicts with the
workspace rule that config ≠ working config, and pi has no such hook surface —
the prompt rule in `AGENTS.md` is the enforcement that actually applies here.
`jDocMunch` (the markdown/docs companion): the doc-read share is 12.1% and
mostly small files, so it is a later candidate, not a first one.

## Verified non-issues (2026-09-30) — do not re-investigate

- **Prompt head is already byte-stable.** `~/.pi/agent/extensions/custom-header.ts`
  is static ASCII + static hints, no timestamp / session-id / env at the head. The
  pi system-prompt sections (`preamble`,`tools`,`rules`,`docs`,`project_context`,
  `skills`,`cwd`) are static per `cwd`. Phase-1.1 ("freeze the head") is already
  satisfied; there is nothing to remove.
- **Mid-session prefix resets do not measurably cost us.** Across 29 sessions only
  **1** has a second (mid-session) `system` message — the mechanism that would
  invalidate the KV prefix within a session. That session was cold anyway
  (`input=0 cacheRead=0` on every turn), so nothing was lost. Tool-schema order
  varies *between* sessions (5→7→10 tools as MCP connects / tools activate) but
  that is not an in-session cache break.
- **`settings.json` compaction does not truncate tool output.**
  `keepRecentTokens` / `reserveTokens` control *history* summarization when the
  window fills. bash / read / powershell already carry a **hard 50 KB / 2000-line
  cap per call**, hard-coded in pi and not exposed in settings. There is no
  `settings.json` knob that shrinks a bash stream; editing it does not touch the
  59.4% bash share. The only levers on that share are the two already in
  `AGENTS.md`: fewer calls (batch via codemode) and shell-level filtering
  (`head`/`tail`/`wc`/`grep` inside the command).

## Hermes runtime levers (2026-10-02, from official docs + source, D17)

Docs: https://hermes-agent.nousresearch.com/docs (pages cited per lever).
Local config: `C:\Users\Mateusz\AppData\Local\hermes\config.yaml`
(backup `config.yaml.bak-20261002`; verified: only `prompt_caching` + `auxiliary` touched).

| lever | doc claim | local state |
|---|---|---|
| `auxiliary.compression` — cheap model for context summaries / micro-compaction | "single most important knob"; a fast chat model summarizes at ~1/50th the cost of the main model | **LEFT DEFAULT (`auto` = session's main model)** — user rule: never pin a model in config; everything runs on the model of the session. The 1/50 lever only materializes if a cheap model is available at session start |
| `prompt_caching.cache_ttl` | `1h` tier amortizes across >5-min turn gaps; 2× write cost; applies to Anthropic-wire tiers only (chat_completions ignore it) | **SET** `1h` (was `5m`) — TTL, not a model; kept |
| mid-session `/model` switch resets the prefix cache | Hermes confirms the switch when context > `model.switch_context_confirm_tokens` (default 100K) | default active; matches our pi rule "one model per session" |
| subagent delegation isolates context; child skips context files (`skip_context_files`) | "massively reducing your main conversation's token usage" | in use; closes open item "subagent delegation convention" below |
| micro-compaction absorbs tool-heavy exchanges; `scripts/micro_compaction_report.py` measures net tokens saved | sample: 75,251 → 69,818 tokens per pass | not yet measured here — run the report after a tool-heavy session |
| Tool Search bridge (`tools.tool_search`) defers large tool schemas | 3,300-tool server ≈ 32K schema tokens/turn flat; bridge = 3 tools + on-demand schema | our jcodemunch `codemode` exposure in pi is the analogous lever; hermes side not needed |
| `providers.<n>.session_affinity_header` | proxies without it re-send whole history each turn | **OPEN** — needs nara/omniroute support check (external, untestable here) |
| per-task metering | `state.db` `sessions` + `session_model_usage` tables carry per-task input/cache_read/output/reasoning/cost/end_reason | script: `scripts/hermes_per_task.py` (G1/G2) |

Per-task baseline (146 sessions, state.db): cache hit 86.4%, 3.8M avg in+cache_read per
session, heavy-tailed: top-10 marathon sessions (400–750 msgs) are 40–110M each,
normal tasks 0.1–0.5M. `new_session`-ended tasks hit 0.95 vs `cli_close` 0.82 —
fresh single-model sessions are the cheap unit of work.

## Open work

- [x] Confirm whether 78.0% can exceed 90% on a single stable model — 2026-10-02:
      30d re-measure holds 80.1% overall; `new_session` tasks on a single model
      hit 0.95 (state.db, `scripts/hermes_per_task.py`), so a single-model
      session CAN exceed 90%; the drag is mid-session model/thinking churn.
- [x] Subagent delegation convention — closed 2026-10-02 by the Hermes lever in
      § Hermes runtime levers: `delegate_task` children skip context files and
      only their summary enters the parent; use it for exploration, batch
      independent children.
- [ ] Determine whether `oc/*` providers can be excluded automatically —
      still open; related: nara/omniroute `session_affinity_header` support
      check (D17 § Open) and running `scripts/micro_compaction_report.py`
      after a tool-heavy Hermes session to measure the auxiliary-model savings.
