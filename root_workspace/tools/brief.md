---
name: brief
job: pytanie decyzyjne -> 4-sekcyjny brief-konteksowy (<=8K)
run: python tools/brief.py
in: pytanie + tools/out/precedents.db
out: brief.md (stdout lub --out)
test: --selftest — <=8K, 4 sekcje, zero "powinienes/rozważ", cytaty [id]
depends: precedents.db (kontrakt precedent.json, nie modul)
contract: brief.md (4 sekcje, cytaty [id] "quote")
---

# brief

Buduje **kontekst**, nie rekomendacje. Zero werdyktu — decydent czyta
precedensy i pyta dalej. Limit 8K jest twardy (ucinany, nie ostrzegany).

## Run

    python tools/brief.py "Czy wydzielic nowy projekt?" --top 4
