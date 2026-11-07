---
flag: a7-lockbox-decision-registered-2026-11-07
since: 2026-11-07
owner: mateusz
agent: agnes-code
model: sapiens/agnes-3.0-flash
---

`a7-lockbox-decision-registered-2026-11-07` — 2026-11-07: zarejestrowano decyzję A7
(§8 remedy Lockboxa benchmark-core v2) jako **wariant (b) teraz + wariant (c) przed
finalną promocją**; Faza 2 odblokowana na Dev.

## Wykonane

- `handoff/decisions/benchmark-core-a7-lockbox.md` utworzone (`status: decided`,
  `decided_at: 2026-11-07`, owner `mateusz`): wariant (a) odrzucony (6 nietkniętych
  zadań = znikoma moc), 42-zadaniowy stary Lockbox → diagnostyka post-hoc bez twierdzenia
  konfirmacyjnego, nowy ślepy Lockbox spoza `fev-bench-100` przed promocją Championa.
- Wpis **A7 dopisany do `projects/research/benchmark-core/ledger.jsonl`** przez
  `projects/_archive/benchmark-core-apply-a7.py` (skrypt w `_archive/`, per precedens A6 —
  tooling jednorazowy nazywający zakres Lockboxa nie może wkradać się do runtime
  skanowanego przez `audit_v2`): łańcuch SHA-256 zweryfikowany, manifest SHA bez zmian
  (`34b35abc…b42da`).
- Wiersz **A7 dodany do rejestru §15** `PROTOCOL.md` (tabela + update "A1–A7").
- `handoff/decisions/index.md` uzupełnione o wpisy.

## Stan dowodowy

- Dev incumbent = **NLinear** (vs SNaive +14,88%, dolne 98,33% CI +3,75% — przechodzi);
  komparator **DLinear** (+12,08%, dolne CI −0,63% — nie przechodzi); MDE 0,178
  (`results/phase1b_dev_analysis.json`, commit `cd087c3`).
- Zakaz używania Lockboxa z §15 (post-A6) **obowiązuje dalej do czasu rejestracji
  wariantu (c)**; budżet (3 użycia, α = 0,01667) dotyczy świeżego Lockboxa.

not checked: pokrycie GIFT-Eval z fev-bench (część zbiorów może pokrywać się z
fev-bench-100 — do potwierdzenia przed jakimikolwiek wyborami danych do wariantu (c));
guard `bench.py --fev-full` zweryfikowany wyłącznie testem subprocess
(`test_benchmark_protocol.py::test_fev_full_guard_exits_before_data_access`), treść flagi
`fev-full-guard-implemented.md` nieprzeczytana.

## Następny krok

**Faza 2** (populacja startowa N ≤ 8, Champion = NLinear, budżet 20 min/metodę na Dev,
dashboard) — może ruszać od razu; nie wymaga decyzji A7-c. Przed jakąkolwiek finalną
promocją: wariant (c) = nowy, ślepy Lockbox ze świeżych danych spoza `fev-bench-100`
(przed wyborem danych: potwierdzić brak pokrycia GIFT-Eval).
