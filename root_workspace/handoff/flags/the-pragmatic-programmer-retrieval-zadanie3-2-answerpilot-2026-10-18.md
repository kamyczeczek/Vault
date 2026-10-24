---
flag: the-pragmatic-programmer-retrieval-zadanie3-2-answerpilot-2026-10-18
since: 2026-10-18
owner: mateusz
agent: opencode
model: opencode/glm-5.3-flash-free
origin: session-close
---

`the-pragmatic-programmer-retrieval-zadanie3-2-answerpilot-2026-10-18` — 2026-10-18: p95 Tier 3 zmierzone (108.2 ms ≤ 500 ms, commit `978d108`), luka 2/52 przeczytana i rozdzielona na dwa defekty (q010 = adnotacja/primary-assignment dla comparison, precedens T13/S64; q012 = granularność rankingu, osobny ticket; commit `f1d0601`), pilot answer-layer 0.5B odrzucony.

- **p95 Tier 3 (S56 pre-registered = 500 ms):** p50 = 88.0 ms, p95 = **108.2 ms** (skrypt eval); pomocniczo p99 = 117.9 ms, max = 393.8 ms (wrapper, zero zmian w repo). Ogon tani.
- **Luka any-vs-primary (2/52):** q010 (DRY vs Orthogonality) — chunk odpowiedzi jest w top-8 (#1), annotated topic 10, gold primary 9 → **adnotacja/primary-assignment przy comparison**, nie granularność; q012 (Aktorzy vs Blackboard) — chunki topic 35 ranked poza top-20 → **granularność rankingu**, osobny ticket.
- **Pilot answer-layer 0.5B (Qwen2.5-0.5B-Instruct, CPU, budżet A)** — odrzucony: metryka „Źródło: Topic N" tautologiczna (etykieta była w kontekście), 0.5B po polsku generuje nonsense, limit 2500 znaków = powtórka truncation artifact graphrag. `answer_pilot.py` usunięty (`23adb6d`).
- **Wniosek architektoniczny:** answer-layer = agent (nie lokalny model) czyta top-8 i układa odpowiedź; retrieval kończy się na chunkach.
- **Ticket na osobną sesję:** lekki pilot answer-layer — skrypt dumpuje top-8 chunków per pytanie do pliku (retrieval ~90 ms × 15 ≈ 1.5 s), agent czyta, checker weryfikuje obecność koniecznych terminów z gold chunka (nie kopiowanie etykiety) + refusal na 8 unanswerable; próbka 15 answerable + 8 unanswerable; top-8 w całości (bez cięcia); kryteria przed runem.

not checked:
- Advisory `MAP.md is stale` (z raportów 2026-10-14) — `build_project_map.py --check` przeszedł czysto w tej sesji, ale deklaracja dotyczy tylko jednorazowego odczytu.
- Ścieżka venv harnessu (`hermes-agent`) w `CONTEXT.md` §Environment — użyta zgodnie z zapisem i działa, ale formalnie nie re-weryfikowano driftu wersji zależności.
- Ta flaga nie zawiera wyniku lekkiego pilota answer-layer (izolacja świeżym podagentem) — to przedmiot następnej sesji, nie tej.