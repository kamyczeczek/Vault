# Gates: session digest — mechaniczny run + walidator

OWNS: scripts/session_digest.py, scripts/session_facts.py,
scripts/verify_session_digest.py, scripts/test_session_facts.py,
scripts/last_session_merged.py, docs/sessions/**, GLOSSARY.md,
docs/wayfinder-session-digest.md, docs/session-digest-GATES.md,
brain/decisions/ADR-005-session-digest-fact-judgment.md

Scope: jeden task **T7** — L1 karty + szkielet L0 + walidator evidence,
bez `--classify` i bez promocji. Bramki są zapisane przed buildem; żadna
`CHECK` nie została uruchomiona, więc `EVIDENCE: pending` znaczy „unmet”,
nie „passed”.

## G1 — run mechaniczny kończy się sukcesem

- [x] G1: `--count 100` pisze karty, szkielet L0 i JSON; exit 0.
  CHECK: python scripts/session_digest.py --count 100 --out-dir scripts/_scratch/sessions/02_products/digest-check
  EXPECT: DIGEST_WRITTEN cards=100 l0=session_digest.md cards_json=session_cards.json
  EVIDENCE: 2026-10-22 — `DIGEST_WRITTEN cards=100 ...`; `COVERAGE main=100 children=105 total_cards=100`; exit 0.

## G2 — schema L1 i wymagane klucze

- [x] G2: JSON parsuje się, ma `schema_version` i wymagane klucze w każdej karcie.
  CHECK: python scripts/verify_session_digest.py --schema scripts/_scratch/sessions/02_products/digest-check
  EXPECT: SCHEMA_OK cards=100 missing_keys=0
  EVIDENCE: 2026-10-22 — `SCHEMA_OK cards=100 missing_keys=0`.

## G3 — cytaty mechaniczne są substringami

- [x] G3: każde `goal.text` / `ending.text` jest substringiem body po normalizacji albo `kind: none`.
  CHECK: python scripts/verify_session_digest.py --quotes scripts/_scratch/sessions/02_products/digest-check
  EXPECT: QUOTES_OK rejected=0
  EVIDENCE: 2026-10-22 — `QUOTES_OK rejected=0` na 100 kartach.

## G4 — stabilny klucz niezależny od N

- [x] G4: ta sama sesja ma identyczne pola mechaniczne przy N=100 i N=110; różni się tylko `ses_n` i pola zmienne.
  CHECK: python scripts/verify_session_digest.py --stability --n 100 --n2 110
  EXPECT: STABILITY_OK stable_key_fields=identical
  EVIDENCE: 2026-10-22 — `STABILITY_OK stable_key_fields=identical` (N=100 vs 110, common keys).

## G5 — determinizm poza polami zmiennymi

- [x] G5: dwa runy na tym samym wejściu są byte-identical poza `generated_at` i `run_id`; lista pól zmiennych jest w schemacie, nie w głowie autora.
  CHECK: python scripts/verify_session_digest.py --determinism
  EXPECT: DETERMINISM_OK volatile=generated_at,run_id
  EVIDENCE: 2026-10-22 — `DETERMINISM_OK volatile=generated_at,run_id` (JSON + MD po usunięciu dwóch pól).

## G6 — budżet rozmiaru

- [x] G6: L0 ≤15 KB, L1 ≤150 KB dla 100 sesji; liczby zmierzone, nie założone.
  CHECK: python scripts/verify_session_digest.py --budget scripts/_scratch/sessions/02_products/digest-check
  EXPECT: BUDGET_OK l0<=15360 l1<=153600
  EVIDENCE: 2026-10-22 — `l0=788/15360`, `l1=99277/153600`; `BUDGET_OK`.

## G7 — negative control: fałszywy cytat

- [x] G7: wstrzyknięty fałszywy cytat jest odrzucany; kontrola jest częścią CI, nie jednorazowym testem.
  CHECK: python scripts/verify_session_digest.py --negative-control quote
  EXPECT: NEGATIVE_CONTROL_OK kind=quote rejected=1
  EVIDENCE: 2026-10-22 — `NEGATIVE_CONTROL_OK kind=quote rejected=1` (quote + `__forged__`).

## G8 — refaktor nie zmienia merged; integrity przechodzi

- [x] G8: output `last_session_merged.py` na fixture jest byte-identical przed/po wydzieleniu ekstraktorów; `check_workspace_integrity.py` kończy OK.
  CHECK: python scripts/verify_session_digest.py --refactor-safety
  EXPECT: REFACTOR_SAFETY_OK merged=identical integrity=OK
  EVIDENCE: 2026-10-22 — `REFACTOR_SAFETY_OK merged=identical integrity=OK`; porównanie fixture po usunięciu dwóch linii zmiennych (`Wygenerowano`, `Zapisano do`), reszta bajt w bajt.

## G9 — negative control: fałszywy payload-pointer

- [x] G9: pointer z błędnym `path`/`line`/`sha` jest odrzucany; walidator sprawdza payload, nie tylko body.
  CHECK: python scripts/verify_session_digest.py --negative-control payload
  EXPECT: NEGATIVE_CONTROL_OK kind=payload rejected=1
  EVIDENCE: 2026-10-22 — `NEGATIVE_CONTROL_OK kind=payload rejected=1` (bad sha + bad line).

## G10 — coverage hash i starzenie

- [x] G10: digest deklaruje `source_cards_sha256`; zmiana karty w coverage → `COVERED_CARDS_MISMATCH` i exit 1; nowa sesja poza coverage jest tylko informacyjna.
  CHECK: python scripts/verify_session_digest.py --coverage-control
  EXPECT: COVERAGE_CONTROL_OK covered_mismatch=rejected new_session=informational
  EVIDENCE: 2026-10-22 — `COVERAGE_CONTROL_OK covered_mismatch=rejected new_session=informational`.

## G11 — schema L0: każde judgment ma evidence

- [x] G11: każde `judgment` ma `evidence_check`, `supports`, `evidence`; brak → fail. W MVP `judgments=0`.
  CHECK: python scripts/verify_session_digest.py --l0-schema scripts/_scratch/sessions/02_products/digest-check
  EXPECT: L0_SCHEMA_OK missing_evidence=0
  EVIDENCE: 2026-10-22 — `L0_SCHEMA_OK missing_evidence=0` (`judgment=[]`, `judgment_status=not_run`).

## G12 — nagłówek L0: main/children, daty, semantyka N

- [x] G12: nagłówek podaje osobno sesje główne i dzieci, dokładny zakres dat i semantykę N (`count` vs `days`).
  CHECK: python scripts/verify_session_digest.py --header scripts/_scratch/sessions/02_products/digest-check
  EXPECT: HEADER_OK main_children=present date_range=exact n_semantics=present
  EVIDENCE: 2026-10-22 — `HEADER_OK main_children=present date_range=exact n_semantics=present`.

## G13 — `--classify`: cards-only, evidence, brak promocji

- [x] G13: `--classify` czyta tylko karty, każdy judgment ma cytat z body, `promotion: null`, a sfabrykowany cytat jest odrzucany.
  CHECK: python scripts/session_digest.py --classify --out-dir scripts/_scratch/sessions/02_products/judgment-check && python scripts/verify_session_digest.py --judgment scripts/_scratch/sessions/02_products/judgment-check
  EXPECT: CLASSIFY_WRITTEN promotion=none + JUDGMENT_OK promotion=none (candidates>0)
  EVIDENCE: 2026-10-22 — `CLASSIFY_WRITTEN candidates=6 promotion=none` (open_threads=4, contradictions=2); `JUDGMENT_OK candidates=6 promotion=none`; forged quote rejected; `scripts/test_session_classify.py` 7/7. Wrapper: `scripts\session_digest.bat N [--classify]`.
  NOTE: `--classify`/L0 is a candidate generator, not an analysis layer —
  A/B 2026-10-23: L1-only answered 0/4; `did` answered 4/4 at lower cost
  (`handoff/flags/session-digest-ab-2026-10-23.md`).

## G14 — A/B analysis layer: L1-only vs `did`

- [x] G14: na tych samych 3 sesjach (review/promocja, classify, commit) L1-only
  nie odpowiada na pytanie o `--classify`, a `did` odpowiada pełniej i taniej.
  CHECK: komendy odtworzenia w `handoff/flags/session-digest-ab-2026-10-23.md`.
  EXPECT: `did >= L1-only` przy niższym koszcie.
  EVIDENCE: 2026-10-23 — L1-only 0/4 (3 913 B); `did` 4/4 + 3 extra (180 308 B);
  L1+body 4/4 (270 040 B); L0 781 B, `_brak_`.

---

## Zasady wykonania

- Negatywne kontrole (G7, G9, G10) są bramkami, nie adnotacjami; muszą failować
  na złym wejściu i przechodzić na dobrym.
- G8 jest jedynym miejscem, w którym wolno dotknąć `last_session_merged.py`;
  bez byte-identical na fixture refaktor jest cofnięty, nie „prawie gotowy”.
- G6 mierzy faktyczny rozmiar; jeśli L1 >150 KB, tnij `files`/`commits`
  przed cytatami — nie zmieniaj progu.
- Nie zmieniaj żadnej bramki, żeby commit przeszedł. Jeśli bramka jest
  niemożliwa, dodaj `ABANDON: G<n> <powód>` i zgłoś to jako handoff.
- Po buildzie: `python scripts/check_workspace_integrity.py` i
  `git diff --check` przed commitem.
