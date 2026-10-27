---
type: Concept
title: answer
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# ODMOWA

**Pytanie:** Co powiedzial Jan Kowalski na spotkaniu 2026-09-15?

**Przyczyna:** Brak pokrycia body: FTS5 zwrócił wyników, ale żaden nie zawiera zdania z słowami kluczowymi 'Co powiedzial Jan Kowalski na spotkaniu 2026-09-15?'.

**Dowody braku pokrycia:**
- FTS5 zwróciło 10 wyników, ale 0 węzłów ma body coverage.
- Słowa kluczowe: powiedzial, jan, kowalski, spotkaniu, 2026-09-15


## Czego ten dowód NIE odróżnia

1. Nie odróżnia odpowiedzi z grafu od odpowiedzi z treningu modelu — model może znać część korpusu z treningu.
2. Nie mierzy trafności rankingowej FTS5 (tylko binary coverage).
3. Nie testuje jakości syntezy: cytat może być wyciągnięty poza kontekstem.
