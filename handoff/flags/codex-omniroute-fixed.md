---
type: Concept
flag: codex-omniroute-fixed
since: 2026-10-09
owner: Mateusz
agent: laguna-s-2.1
model: laguna-s-2.1
title: codex-omniroute-fixed
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`codex-omniroute-fixed` — 2026-10-09: Codex CLI non-functional due to OmniRoute proxy not running + broken `OMNIROUTE_API_KEY` env var. Two root causes fixed:

1. **OmniRoute server was not running** — no listener on `localhost:20128`. Started OmniRoute v3.8.50 daemon (`omniroute serve --no-open --daemon`). Server PID 13016, listening on 0.0.0.0:20128.

2. **`OMNIROUTE_API_KEY` was broken** — Windows User environment variable contained the literal string `"OMNIROUTE_API_KEY"` (17 chars, the variable name, not an actual key) instead of a valid API key. Fixed by setting it to `sk_omniroute` (OmniRoute's sentinel key for local instances with `REQUIRE_API_KEY=false`, per source: `src/lib/db/apiKeys.ts:264` `isConfiguredEnvApiKey` + `src/shared/utils/featureFlags.ts` `REQUIRE_API_KEY` default `"false"`).

Verification:
- `codex doctor` → **22 ok · 6 notes · 3 warn · 0 fail** (auth ✓, reachability ✓)
- `codex exec "What is 2+2?"` → returns `4` (model `cx/gpt-5.6-luna-medium` via `omniroute`, 13,237 tokens used)
- `omniroute models` → lists 2091 models from the local gateway
- `omniroute setup-codex` → generated 2091 profile files in `~/.codex/*.config.toml`

Notes:
- **Non-OpenAI models CAN be used** — `setup-codex` generated profiles covering all providers (gemini/, mistral/, dva/claude-, deepseek/, nara/). Use `--profile <plain-name>` to select. The `oc/` prefix routes through OpenCode provider (requires separate OpenCode API key); use direct provider prefixes (gemini/, mistral/, nara/) for provider-native auth.
- **nara/laguna-s-2.1** — profile created at `~/.codex/nara-laguna-s-2-1.config.toml` but OmniRoute reports: "Model 'laguna-s-2.1' is not available in the active live catalog for provider 'nara'". Nara provider connection (using `NARA_API_KEY`) is active but doesn't offer this model. Use `openrouter-poolside-laguna-s-2-1-free` instead (verified working).
- The `STORAGE_ENCRYPTION_KEY` warning from installation `.env` is harmless.
- The broken Python `codex_cli` v1.0.1 (not OpenAI) is NOT installed.
- `muse-spark-1.3-contributor-free` profile exists as `oc-muse-spark-1-2-contributor-free.config.toml`.
- OmniRoute server must be running before Codex — no automatic startup configured (TODO: scheduled task).
- Some providers (dva/claude) may have server-side config issues (e.g. `DEVIN_AGENTIC_HOME`).

Status: ✅ COMPLETE — Codex CLI is now functional with OmniRoute.
