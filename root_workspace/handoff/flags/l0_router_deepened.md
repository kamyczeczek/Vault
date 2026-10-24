---
flag: l0_router_deepened
since: 2026-10-04
owner: opencode
agent: opencode
model: opencode/space-bunny-free
origin: root L0 porządki (3 commity: fca9f7a, 1704578, b0817d1)
---

`l0_router_deepened` — 2026-10-04: Root L0 router pogłębiony w trzech commitach.
(1) 4 dated scars (Windows tooling, executable, verification-tool, metric-design)
wyjęte z `AGENTS.md §Rules` do `SCARS.md`; router zostaje z jednym pointerem,
`handoff/CONTEXT.md` ma trigger, `ALLOWED_ROOT` + tabela CLAUDE.md zaktualizowane
w tym samym commicie (R1, obie połowy). (2) Zduplikowany blok
`## Token efficiency skill` usunięty — to implementacja candidate 4 z audytu v7,
raport dostał adnotację `[RESOLVED 2026-10-04]`. (3) `## Projects + grades` w
routerze nie istniał w worktree; dodano wiersz `Project grades →
CONTEXT-MAP.md §Grades` zamiast kopii. Nagłówek: 1129 słów × ~1.3 = ~1468
tokenów, więc `<2K tokens` jest prawdziwe i nie był edytowany.

Trigger dla `SCARS.md` jest **konwencją, nie mechanizmem** (precedens:
`scripts/memory/CONTEXT.md`, `AGENTS.md:33`) — hook enforcement: TODO. Ten sam
problem co `gate_has_no_automatic_caller`: pre-commit hook istnieje w `hooks/`,
ale `core.hooksPath` jest lokalny i nie wersjonowany, więc świeży clone go nie ma.

**Next step:** albo ustawić `core.hooksPath` jako krok każdego clone'a (dokument
jest w CLAUDE.md), albo dopisać wywołanie triggera do `hooks/pre-commit` —
obecny hook robi whitespace + integrity gate, nie czyta SCARS.md.
