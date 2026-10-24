# Session 8 — Fix Decision (Pre-registered)

Wykluczenie sesji `01a14af3`, `ses_eb2d1e180`, oraz `ses_ebce63c7` z case „FTS decision" w `scripts/memory/eval_queries.json` jest **test hygiene**: sesje te nie zawierają odpowiedzi na query „FTS5 unicode61", a jedynie marginalne dopasowania słowne (noise). Jedyną poprawną odpowiedzią pozostaje `fe3a511b`.

Fix z sesji 7 jest poprawny. Decyzja: zatwierdzić i zacommitować `eval_queries.json` wraz z dokumentacją forensyczną.
