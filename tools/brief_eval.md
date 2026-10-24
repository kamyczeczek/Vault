---
name: brief_eval
job: retrospektywa — czy brief poprawia decyzje (5 historycznych ADR-ow)
run: python tools/brief_eval.py
in: 5 ADR-ow z precedents.db
out: tools/out/verdict.json
test: --selftest — metryka pre-registered, wynik deterministyczny (2 przebiegi)
depends: precedents.db (kontrakt precedent.json, nie modul)
contract: verdict.json (metric, bar, n, hits, pass, cases)
---

# brief_eval

Jedno pytanie: trafienie top-1 >= 3/5 przy baseline losowym 1/5?
Metryka zapisana PRZED testem (stala METRIC). Bez LLM — ranking
deterministyczny. Nie odpowiada "czy graf wygrywa", tylko "czy brief trafia".
