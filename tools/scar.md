---
name: scar
job: append/query trybow porazek (najmniejsze narzedzie)
run: python tools/scar.py
in: scar add "..." / scar query "..."
out: tools/out/scars.jsonl (append-only, jeden JSON na linie)
test: --selftest — add + query round-trip, sonda top-1
depends: none
contract: scars.jsonl (id, text, tags, date)
---

# scar

Prywatna pamiec porazek. Dodajesz jednym zdaniem, pytasz slowami
kluczowymi. Bez taksonomii z gory — tagi rosna z uzyciem, nie z planu.

## Run

    python tools/scar.py add "metryka przechodzi, meritum nie" --tag metric
