---
flag: ticket-s76-parse-scars-leak-2026-10-18
since: 2026-10-18
owner: mateusz
agent: opencode
model: opencode/glm-5.3-flash-free
origin: owner-recommendation after r18-parser-scope-fix-2026-10-18 (8af7e77)
---

`ticket-s76-parse-scars-leak` — 2026-10-18: Ticket otwarty decyzją ownera (łańcuch E4 zamknięty na `8af7e77`).

Stan: `## S76 (candidate):` w `SCARS.md` jest nieparsowalny przez `ingest_brain.parse_scars` (regex `^##\s+S(\d+)\s*:` nie trafia w otaczający parenthetical), więc bulle S76 lądują w `brain/brain.db` jako śmieci (`id=1023/1024`, niesparowane bulle; potwierdzone w `review-debt-named-s80-2026-10-17`, pkt D).

Dlaczego teraz: S85 (korekta S84a) przeszła przez `parse_scars` poprawnie, więc leak dotyczy wyłącznie nagłówka S76 — ale R21 (następny recall blizn) będzie czytał błędne wnioski z `brain.db`, póki śmieci tam siedzą.

Next step: naprawić `parse_scars` w `scripts/ingest_brain.py` (tolerancja `(candidate)` w nagłówku — precedens: `^##\s+S(\d+)\s*:` vs `## S76 (candidate):`), rebuild `brain.db`, potem `ingest_brain.py --check` + `eval_brain.py --check` zielone i `id=1023/1024` znika. S76a (korekta w `SCARS.md`, jak S85 korygowało S84a) tylko jeśli build po fixie nadal pomija treść.

Scope: `parse_scars` + rebuild bazy. Nie dotyczy recallu, tokenizacji, bramek.
