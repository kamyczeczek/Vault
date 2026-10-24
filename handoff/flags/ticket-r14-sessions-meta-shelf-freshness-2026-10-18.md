---
flag: ticket-r14-sessions-meta-shelf-freshness-2026-10-18
since: 2026-10-18
owner: mateusz
agent: opencode
model: opencode/glm-5.3-flash-free
origin: owner-recommendation after r18-parser-scope-fix-2026-10-18 (8af7e77)
---

`ticket-r14-sessions-meta-shelf-freshness` — 2026-10-18: Ticket otwarty decyzją ownera (łańcuch E4 zamknięty na `8af7e77`).

Stan: `ingest_curated_shelf` zmienia `sessions_meta` (`updated_at`), co sztucznie świeżuje R14 — pierwszy raz, gdy indeks będzie realnie stary, R14 może powiedzieć „OK", bo shelf-only refresh zaktualizował metadane sesji bez realnej treści. Stan pochodzi z `review-debt-named-s80-2026-10-17` (not checked, pkt ostatni; nie sprawdzono, czy maskuje realny lag).

Next step: sprawdzić, czy `ingest_curated_shelf` powinien w ogóle dotykać `sessions_meta`. Jeśli nie — usunąć ten efekt (shelf-only refresh aktualizuje wyłącznie wiersze curated). Jeśli tak — udokumentować, dlaczego, i dać R14 drugi, niemożliwy do sfingowania sygnał świeżości (np. hash treściźródłowych). Wymagany pomiar przed/po (`scripts/pi_cache_forensics.py --since` lub równoważny), nie inferencja.

Scope: `scripts/ingest_brain.py` / shelf ingest + świeżość R14. Nie dotyczy digestów i tego, że sesje nie istnieją.
