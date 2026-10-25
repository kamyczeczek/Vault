---
type: Concept
title: session-8-exclusion-analysis
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

# Session 8 — Exclusion Analysis

- **`ses_eb2d1e180`** = sesja 6 o answer-layer EN pilot na Tier 3 — **test hygiene** (świeża sesja robocza sesji 6, wykluczenie OK).
- **`ses_ebce63c7`** = sesja planowania (CRLF fix, cache rerank, zadania 4-7) — **test hygiene** (sesja robocza, brak treści relewantnej do FTS5 unicode61 decision, wykluczenie OK).
- **`01a14af3`** = sesja ratunkowa po E4 (security) — **test hygiene** (sesja naprawcza bezpieczeństwa, brak treści o FTS5 unicode61 decision, wykluczenie OK).

**Klasyfikacja końcowa:** Wszystkie trzy wykluczone sesje to **test hygiene (noise)**. Nie zawierają odpowiedzi na query „FTS5 unicode61", jedynie słowa kluczowe w logach lub nagłówkach. Jedyną oczekiwaną odpowiedzią pozostaje `fe3a511b`. Fix z sesji 7 jest w pełni poprawny (brak gaming).
