---
type: Concept
flag: workspace-gate-exclusion-audit-2026-10-15
since: 2026-10-15
owner: Mateusz
agent: pi-bolt
model: default
title: workspace-gate-exclusion-audit-2026-10-15
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`workspace-gate-exclusion-audit-2026-10-15` — 2026-10-15: Audyt naprawy eval z `66fdb50`. Werdykt: exclusion case'u `workspace gate` nie byl gamingiem (expected `01a0f9c0-113b` to jedyna sesja, ktora *definiuje* bramke — zrodlo `main()` z lista `check_rN_*`; cztery wykluczone sesje ja tylko odwoluja, wywoluja lub weryfikuja), ale tez nie byl udokumentowanym dryfem: reguła wykluczenia nie zostala zapisana i zostala zastosowana niespojnie — heading `# Import ALLOWED_ROOT from check_workspace_integrity.py` nosza trzy sesje z tej samej nocy, wykluczono najstarsza (`01a13bb8`), dwie nowsze zostawiono, a `01a13bc5` siedzi w oknie na ranku 3. Dodatkowo okno metryki zmalejo z 5 do 4 (bo `01a13bd8` zajmuje dwa sloty), wiec case deklaruje `hit@5`, a mierzy `hit@4`. Pomiar: pre `66fdb50` MRR 0.622 (14/15), post 0.689 (15/15); cala delta to 1.0/15, zadny inny case sie nie ruszyl. **Revert nie jest potrzebny.** `agent_commit.py` istnieje w archiwum ARL (`projects/_archive/agentic-research-lab/scripts/agent_commit.py`, `unstage()` linia 58) i dokumenty roota atrybuent go poprawnie — brak over-claimu, brak akcji.

not checked:
- Czy trzy wykluczone sesje z czesciowymi opisami (`01a13bd8`, `01a13bb8`, `01a13271`) powinny uchodzic za *pelne* odpowiedzi — wymaga decyzji wlasciciela o definicji case'u.
- Czy `fe3a511b` zmienila definicje bramki (widac ja w liscie `modified`, diffa nie czytano).
- Hartacja case'u (regula zamiast listy ID) — nie wdrazano.
- Wdrozenie Opcji A guardow — decyzja podjeta, nie zaimplementowana.

Next: hartacja case'u `workspace gate` — zapisac regule (implementacja vs. referencja) i zastosowac ja konsekwentnie do wszystkich rodzenstw, albo porzucic liste na rzecz innego kryterium; bez doklejania kolejnych `exclude_session_ids`. Osobno: wdrozenie Opcji A.
