---
type: Concept
flag: merged-session-loss-declarations-2026-10-19
since: 2026-10-19
owner: Mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
title: merged-session-loss-declarations-2026-10-19
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`merged-session-loss-declarations-2026-10-19` — 2026-10-19: target variant implemented. Default is now the split layout (`--monolith` opts out): a 31 KB `last_sessions_merged.md` index plus `sessions/ses-001..100.md` bodies, with negative legends (`brak exit: ≠ exit 0`; empty assistant = model text absent; preview is truncated), per-session `Straty` (`trunc msg 2,3,5 | artifact 6 | 768B 5 | superseded 1`), `Exit` (explicit vs unknown), `Artefakty` (`47/47 zweryfikowane`), and the source sha256. Verbatim budget is redistributed: 564 full (all 155 non-zero-exit calls + git diff/status/log/show + close/commit + tests), 30 gate tail-10, 107 flag/CONTEXT head+tail; successful reads and >10-hit glob/grep lose their preview. Sidecars: `tool_calls.jsonl` (1402 records; exit explicit 234 = `0:79, 1:152, 2:3`; 1168 missing, unknown not zero), `claims.jsonl` and `claims.tsv` (666 claims; 488 `open`, 178 `nie-weryfikowalne`; extraction only, no truth judgment), `index.tsv`, `artifacts/` (2240 files, all verified) and `artifacts/MANIFEST.tsv` + `MANIFEST.sha256`. Total 5040 KB; `.zst` index 8.7 KB. The 3 GB opencode DB is stream-hashed once per run (`sha256:d1d78234…;size=3051704320`), not per session. Verified: 100/100 session SHA, 0 bad out/args SHA, 0 bad claim refs, 2240/2240 manifest rows, 100 TOC links; tests 18. Next: decide whether `claims.tsv` gets an explicit evaluator pass (currently `open`/`nie-weryfikowalne` by design) and whether the 3 GB source hash should be cached across runs.

not checked:
- Claims are not judged: `open` means a tool association exists, not that the claim is true; `nie-weryfikowalne` means no support was found. A separate evaluator/human pass is still required.
- Full pre-trunc artifacts are not recovered: the loaders truncate before this layer, so `artifacts/` holds the truncated text, labelled `truncated`/`omitted_chars` in `tool_calls.jsonl`.
- `artifact://` targets are reported (16 refs) but not resolved/copied; there is no resolver for those external stores.
- Claim extraction is regex-only and assistant-block-only; claims in user prose or attached reports are not in `claims.jsonl`/`claims.tsv`.
- `Flaga (wzmianka)` can name a consulted flag, not the one the session closed.
- Cross-session dedup stays off: measured 31 spans / ~6 KB, not the estimated 80–120 KB.
- The source hash costs one full 3 GB read per run (~10 s); no cross-run cache. The deferred `--cap` and opencode `exit=`/renderer unification remain.
