---
type: Concept
title: trace-qground
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# trace-qground.md — Faza 6, Q-ground (executed 2026-10-10, agent pi)

Oracle-first: ludzkie oczekiwanie wklejone przez człowieka w sesji review
(abstrakt arXiv:2603.25111v2, spoza grafu), wpisane do CONTRACT.md + plan.json
PRZED jakimkolwiek query tej sesji na graph.db. Baza wyłącznie read-only.

## Krok 0 — pytanie + SCOPE (jak Q-refusal)
„Czym jest SEVerA i jak się ma do self-evolving agents?"
SCOPE: testowany jest ARL retriever + `nodes.body`, nie pilot `graphrag.py`
(D-005 wariant B nadal obowiązuje).

## Krok 1 — seed FTS (ask.py, limit 5)
Top-1: `00_severa_verified_synthesis_of_self_evolving_agent` — EXACT title match,
source URL `http://arxiv.org/abs/2603.25111v2` = arXiv ID z ludzkiego oracle.
Top-2..4: dokumenty adjacent o self-evolving agents (survey, world models,
experience graphs) — trafny klaster, nie szum. Przeciwieństwo Q-refusal:
tam top-1 był zastępcą, tu top-1 jest odpowiedzią.

## Krok 2 — węzeł (resolve + metadata)
- id: `00_severa_verified_synthesis_of_self_evolving_agent`, tier 1,
  path `knowledge/corpus/00_severa_....md`, family jw., body 2 158 znaków.
- Autorzy w body: Banerjee/Xu/Ie/Zhang/Peng = autorzy z oracle. MATCH.
- Krawędzie: 1× SEQUENCE → `00_skillopt`, reszta PART_OF (bulk, setki).
  Brak DERIVED_FROM. Uczciwie: pokrycie krawędziowe treści jest zerowe —
  dowodem treści jest body + proweniencja, nie triple semantyczne.

## Krok 3 — zgodność body z ludzkim oracle (claim-by-claim)
| Oracle (człowiek) | Body (graf) | Werdykt |
|---|---|---|
| self-evolving: planner LLM syntezuje program, tuning per task, BRAK gwarancji formalnych → ryzyko na unseen inputs | „no formal guarantees of safety or correctness… executed autonomously on unseen inputs… reliability and security concerns" | MATCH (cytat) |
| FGGM: formalny kontrakt (FOL) + rejection sampler + verified fallback, output spełnia kontrakt dla dowolnego inputu/parametrów | „specify a formal output contract… using first-order logic… rejection sampler with a verified fallback, ensuring every returned output satisfies the contract for any input and parameter setting" | MATCH (cytat) |
| Three-stage: Search / Verification (dowód dla WSZYSTKICH parametrów → redukcja do unconstrained) / Learning (GRPO-style, soft objective) | „Search synthesizes candidate parametric programs… Verification proves correctness… for all parameter values, reducing the problem to unconstrained learning… Learning applies scalable gradient-based optimization, including GRPO-style fine-tuning" | MATCH (cytat) |
| Ewaluacja: zero violations + lepsza performance (regression, Dafny, math, τ²-bench); constraints przycinają przestrzeń | „achieves zero constraint violations while improving performance over unconstrained and SOTA baselines… steer synthesis toward higher-quality agents" + „Dafny program verification, symbolic math synthesis… ($τ^2$-bench)" | MATCH, 1 różnica: oracle wymienia też „constrained symbolic regression" i „symbolic mathematical expression synthesis" — body-kondensat mówi „symbolic math synthesis", regresji nie wymienia. Kondensat korpusu, nie sprzeczność — jawnie nazwane, nie przemilczane. |

## Krok 4 — kontrola bez narzędzia: NIEWYKONALNA w tej sesji (finding protokołowy)
Kontrola wymaga odpowiedzi modelu BEZ dostępu do grafu. Ta sesja widziała
węzeł SEVerA już w poprzedniej sesji (resolve + body_head 400 znaków) i pełne
body w tej — odpowiedź „gołego modelu" ode mnie teraz byłaby skażona z definicji
(CONTRACT.md: „kontrola zwróci szczegóły korpusu → skażona"). Nie uruchamiam
skażonej kontroli żeby „odhaczyć" — to byłby teatr, nie dowód.
Lekcja protokołowa: kontrola-without-tool musi biec PIERWSZA, przed jakimkolwiek
query na grafie, w świeżej sesji. Do tego czasu pełne „grounding udowodniony"
(nie) — stoi: Q-ground MATCH + Q-refusal ODMOWA + kontrola pozytywna VERA Q1;
brakuje: kontrola negatywna gołego modelu.
