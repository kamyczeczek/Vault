---
name: precedent_index
job: indeksuje precedensy architektoniczne do malego SQLite
run: python tools/precedent_index.py
in: projects/{_archive,research}/agentic-research-lab/docs/adr/*.md, SCARS.md
out: tools/out/precedents.db
test: --selftest — >=5 ADR-ow retrievable, kazdy z id/kind/quote/source_path
depends: none
contract: precedent.json (id, kind, title, quote, source_path, date)
---

# precedent_index

Indeksuje **tylko** precedensy: ADR-y, scars. Nie korpus.
Rozmiar celowo maly — to nie wyszukiwarka biblioteczna.

## Query

    python tools/precedent_index.py query --kind adr "session store"
