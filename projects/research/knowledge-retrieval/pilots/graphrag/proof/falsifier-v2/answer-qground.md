---
type: Concept
title: answer-qground
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# answer-qground.md — Faza 6, Q-ground: SYNTEZA Z GRAFU (2026-10-10)

**Pytanie:** Czym jest SEVerA i jak się ma do self-evolving agents?

**Odpowiedź (wyłącznie z `nodes.body`, węzeł
`00_severa_verified_synthesis_of_self_evolving_agent`, tier 1,
source `http://arxiv.org/abs/2603.25111v2`):**

Self-evolving agents to paradygmat, w którym „a planner LLM synthesizes an
agent program that invokes parametric models" tunowane per task — ale „existing
self-evolving agent frameworks provide no formal guarantees of safety or
correctness", a „such programs are often executed autonomously on unseen
inputs", co „raises reliability and security concerns".

SEVerA (Self-Evolving Verified Agents, Banerjee/Xu/Ie/Zhang/Peng) odpowiada
formułując „agentic code generation as a constrained learning problem,
combining hard formal specifications with soft objectives capturing task
utility". Mechanizm: „We introduce Formally Guarded Generative Models (FGGM),
which allow the planner LLM to specify a formal output contract for each
generative model call using first-order logic. Each FGGM call wraps the
underlying model in a rejection sampler with a verified fallback, ensuring
every returned output satisfies the contract for any input and parameter
setting." Trzy etapy: „Search synthesizes candidate parametric programs
containing FGGM calls; Verification proves correctness with respect to hard
constraints for all parameter values, reducing the problem to unconstrained
learning; and Learning applies scalable gradient-based optimization, including
GRPO-style fine-tuning, to improve the soft objective while preserving
correctness." Wynik: „Across tasks, SEVerA achieves zero constraint violations
while improving performance over unconstrained and SOTA baselines" (Dafny
program verification, symbolic math synthesis, policy-compliant agentic tool
use, $τ^2$-bench) — „formal behavioral constraints not only guarantee
correctness but also steer synthesis toward higher-quality agents".

**Zgodność z ludzkim oracle:** MATCH claim-by-claim (4/4 bloki: ryzyko braku
gwarancji / FGGM / three-stage / zero-violations+tasks). 1 jawna różnica:
oracle wymienia „constrained symbolic regression", kondensat korpusu mówi
„symbolic math synthesis" bez regresji — kondensat, nie sprzeczność.

**Dowody:** ≥6 cytatów z `nodes.body` (powyżej), proweniencja (arXiv ID =
oracle, autorzy = oracle, tier 1), seed FTS top-1 exact. Pokrycie
krawędziowe: 0 triple semantycznych (tylko SEQUENCE + bulk PART_OF) —
dowód treściowy, nie grafowy; nazwane, nie ukryte.

**Confidence: wysoka** — 4/4 bloki oracle z cytatami, proweniencja zgodna,
seed exact. Nie kłamstwo skali (dowodów ≥6, kryterium: ≥2).

## Niewygodne prawdy (review 2026-10-10, dopisane po fakcie, bez zmiany wyniku)

1. **Oracle == źródło korpusu.** Węzeł w grafie to ingest tego samego abstraktu
   arXiv, który człowiek wkleił. MATCH 4/4 dowodzi PROWENIENCJI (graf ma to, co
   twierdzi że ma), nie groundingu (graf ma coś, czego model sam nie wie).
   Oba odczytania dają ten sam MATCH — rozstrzyga je tylko kontrola bez
   narzędzia. Q-refusal jest mocniejszy: jego oracle był z root SCARS.md,
   nie z korpusu ARL.
2. **Body ≠ graf.** Pokrycie krawędziowe = 0 (1x SEQUENCE, 0x DERIVED_FROM,
   0x SCARRED_FROM). Dowód przeszedł na warstwie dokumentowej (FTS + body =
   to samo co ask.py --raw), nie na warstwie grafu. Jak Q-refusal pokazał
   ranking-nie-relevance, tak Q-ground pokazuje body-nie-graf. Obie Fazy 6
   przeszły obok struktury, którą D-001 miał testować.

## Jawnie niewykonane
- Kontrola bez narzędzia (goły model): NIEWYKONALNA w tej sesji — sesja
  widziała węzeł SEVerA wcześniej, kontrola byłaby skażona z definicji.
  Musi biec pierwsza w świeżej sesji. Pełne „grounding udowodniony" czeka.
