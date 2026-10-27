---
type: Concept
title: open_questions
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Open Questions — Commission 2: Knowledge Architecture (2026-09-03)

Reason recorded per item: missing source, harness gate, or out-of-scope design decision.

1. **How large is the always-on slice allowed to be?** Anthropic: "smallest set of high-signal tokens" (no number). Chroma: every always-on token is a length-amplified distractor (no ceiling given for curated invariants vs raw haystack). GCC's measured ~400 tok is the only concrete anchor, but from a single small corpus, not a protocol-invariant block. **User/03_plan arbitration** — this is the size question behind how much of the h720 protocol invariants belongs in `.jcode/prompt-overlay.md` vs `ask.py`.
2. **Does Jcode ever get a prompt-time context-injection hook?** Currently: observers + one gate only (bundled `docs/HOOKS.md`). The bundled docs describe turn hooks as future lifecycle authority for Herdr ("Do not enable this authority from turn hooks alone. It needs explicit Jcode events…") — suggesting the event surface may grow, but no documented `UserPromptSubmit`-equivalent exists today. **Out of scope** (upstream Jcode decision; the hibiscus session in `C:\Users\Mateusz` is the live probe against omp, not Jcode).
3. **What is the omp-vs-Jcode split for the two brains?** The ts-brain.ts extension fires only under omp; Jcode sessions get brain context only via memory recall (the standing fresh-session recall test in `PROGRESS.md` open decisions) and `ask.py`. No source found prescribes a cross-harness knowledge layer; the workspace's prompt-overlay + memory is the de-facto answer for Jcode. **Unresolved** — depends on (2) and on whether omp remains the subagent harness.
4. **GCC's "code does the retrieval" claim is layer-specific** (findings §6 secondary contradiction): holds for the graph layer (hook-walked SQL), not the RAG layer (model must call `search.py`). Whether the workspace's `ask.py` (FTS5, model-driven tool call) should gain a *code-driven* recall path (workspace equivalent of `recall_hook.py`) is a design decision blocked on (2) — under Jcode there is no prompt-time channel to hang it on.
5. **Digest/write-side pattern has no Jcode-native counterpart yet.** GCC's digest (session → distilled note → indexed; dials `max_turns 30` / `max_chars 15000` / `min_turns 5`) is a Claude Code hook build. The workspace's analog today is manual (reflections, PROGRESS.md). Jcode observers *could* host it (session_end → distill), but no source evaluates that mapping. **Open** — would be the natural first Jcode observer-hook use.
6. **The shipsolid "One Model, Many Minds" memory-isolation pattern could not be fetched** (404 this session). Its relevance (persona/specialist memory isolation as a multi-brain management pattern) rests on the search snippet only; primary content unresolved. **Missing source.**
7. **Keyword routing vs embedding routing for the dispatcher.** `ask.py` uses deterministic keyword scoring (workspace doctrine; GCC's prompt-router uses shape rules — both no-LLM). Both brains' `ask.py` do FTS5 retrieval *inside* a brain, but the *inter-brain* hop is lexical. Whether a small embedding hop (GCC's RAG leg uses bge-small via fastembed) would improve inter-brain routing is untested here. **Open**, not needed for the current decision.
8. **Fresh-session native-memory recall test (standing, pre-existing).** `PROGRESS.md` open decisions: the ts-brain.ts cutover trigger is "a future session successfully answers leaderboard/protocol questions from native memory alone." This commission adds the mechanism fact (memory recall is one turn behind and embedding-driven) but does not run the test. **Unresolved — carried.**

---
## Reopen 2026-09-16 — resolution and new questions

### CLOSED by the 2026-09-16 web pass (findings §7)
4. **GCC's "code does the retrieval" claim is layer-specific.** RESOLVED as
   *not a contradiction* (findings §7.8 item 2): the two layers sit at
   opposite ends of the capability axis. Pandey (arXiv 2603.11513) measured
   that axis directly — models ≤7B fail 85–100% of the time to use even
   oracle retrieval, dominant failure mode "irrelevant generation." Strong
   models use retrieved context fine; small ones do not, and the graph layer
   is what rescues them. The workspace's `ask.py` is the RAG half *by
   design*, and the orchestrator is a strong model — the right end of the
   axis for a model-driven tool call.
7. **Keyword vs embedding routing for the dispatcher.** PARTIALLY RESOLVED —
   the answer is *corpus-scale-dependent*, and the workspace is in the
   regime where keyword+RRF is right. Pandey: RRF k=60 hybrid
   *underperformed* pure dense at 500K passages (hit@5 14.9% vs 16.3%, "BM25
   signal adds noise at this corpus scale"); Yuan et al. (ICLR 2026) found
   hybrid+rerank the best retrieval method at LoCoMo scale (77.2% vs 73.4
   cosine, 57.1 BM25). At hundreds of chunks the lexical leg is what rescues
   vocabulary mismatch. Kept as a partial close: no universal rule exists,
   and a scale crossing (corpus growing ~10×) is the trigger to re-measure.

### NEW (open, with reasons)
9. **Is GCC's distil-at-write-time spend justified?** Yuan et al. (ICLR 2026)
   measured write strategy worth only 3–8 points vs retrieval's 14–23, and
   that the *cheapest* write (raw chunks, zero LLM calls) matched or beat
   Mem0-style extraction and MemGPT-style summaries. GCC's distil pays one
   `claude -p` call per note. GCC mitigates by keeping the raw chunk
   fully indexed *alongside* the distilled entry (lossless write +
   supplementary query-shaped index — the configuration Yuan et al. do not
   test). **Why unresolved:** the mitigation is an argument, not a
   measurement. Settling it needs a write-side A/B on a corpus with a golden
   question set — which is an implementation/build action, not a research
   one. Routed to `03_plan`; research records the tension, does not resolve
   it by fiat.
10. **Does the Haiku result replicate at all at n>1?** The load-bearing GCC
    datum is one question, one corpus, three models, run live in a terminal.
    Pandey confirms the *mechanism* at scale (360M–8B, 1,000 questions,
    oracle design), which is strong support, but a mechanism being real does
    not mean GCC's specific one-question flip is not noise. **Why
    unresolved:** GCC publishes no question set, no seed, no per-run variance.
    The README says "Reproduce both yourself" but the corpus is tiny and the
    answer is known to the reader — a clean replication needs a blinded
    multi-question harness. Out of scope for research; flagged as the single
    highest-value external check someone could run.
11. **The 213★ figure in §2.1 is unverified, not confirmed.** The 2026-09-16
    fetch of the live README shows no star count in the retrieved text. The
    repo is verified public and real; the popularity figure is not.
    **Why unresolved:** the Jina/Exa fetches return README prose, not the
    repo sidebar metadata. A `gh repo view` call would settle it in one line;
    left open rather than guessed, and recorded as a correction in §7.8.
