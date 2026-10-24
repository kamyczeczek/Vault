---
flag: graphrag-falsifier-v2-qrefusal
since: 2026-10-10
owner: mateusz
agent: pi
model: nara/muse-spark-1.3-contributor-free
origin: session-close
---

`graphrag-falsifier-v2-qrefusal` — 2026-10-10: Faza 6 Q-refusal EXECUTED protokołem z close-ritual-probed (oracle-first: oczekiwania w proof/falsifier-v2/plan.json PRZED query; żywy eksperyment na archiwum read-only; sprzątanie). Wynik: ODMOWA z 5 niezależnymi dowodami braku pokrycia — resolve(R13/CRLF)=0, FTS 'SCARS.md'=0 dokumentów, body top-1 FTS (reflection_rule_of_scars, 10 347 znaków) 0 trafień R13/CRLF/SCARS.md/AGENTS.md/sesja 04, korpus to literatura (top sources: podręczniki), kontrola pozytywna VERA Q1 (seed w top-3) dowodzi żywotności narzędzia. Dwa ustalenia poboczne: (1) surowy FTS stawia adjacent-but-wrong na top-1 w obu pytaniach — warstwa dowodowa musi stać NAD rankingiem; (2) research-engine/kg.py martwy (FileNotFoundError, ścieżka projects/research/agentic-research-lab nie istnieje) — precedens 'istnieje kg.py' fałszywy co do używalności, naprawa należy do sesji research-engine. Dowód: pilots/graphrag/proof/falsifier-v2/{plan.json,trace.md,answer.md}; stan w progress.md/findings.md/task_plan.md (Q-refusal done, Q-ground zablokowane). Q-ground czeka na ludzkie oczekiwanie SEVerA spoza grafu (węzeł istnieje, arXiv:2603.25111v2) — pytanie do człowieka niedostępne w tej sesji.
not checked: Q-ground + kontrola bez narzędzia (goły model o SEVerA) — oba DEFERRED na ludzkie oczekiwanie, jawnie nie przemilczane; odpowiedź FTS z --neighbors/--expand na Q-refusal (inny tryb seeda niż testowany); krawędzie SCARRED_FROM/DERIVED_FROM wokół reflection_rule_of_scars (czy graf łączy go z czymś o workspace); R15/R16 po plikach pilota (projects/ ignorowane, MAP projektu przebudowany, ale niepotwierdzone bramą KR); proof/produkt-x z Fazy 5 (nie re-weryfikowany).
