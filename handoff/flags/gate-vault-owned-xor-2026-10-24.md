---
type: Concept
flag: gate-vault-owned-xor-2026-10-24
since: 2026-10-24
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
title: gate-vault-owned-xor-2026-10-24
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`gate-vault-owned-xor-2026-10-24` — 2026-10-24: bramka przestaje traktować `.git`, `.obsidian`, `.smart-env` i `Notes` jako wpisy workspace'u. Nowy zbiór `VAULT_OWNED` + R1b egzekwuje dokładnie jedno miejsce (ROOT albo VAULT — „oba" i „żaden" to FAIL); R1 nie zgłasza ich już jako stray w żadnym z dwóch miejsc, bo miejsce jest własnością R1b. `CLAUDE.md` deklaruje cztery wiersze `../` (bez tego druga połowa kontraktu R1 nie istnieje), a `test_gate_allowlist_parity.py` sprawdza teraz także deklarację vault-owned. To zaostrzenie, nie wyciszenie: przed migracją wszystkie cztery leżą w ROOT i XOR przechodzi, po migracji w VAULT i XOR nadal przechodzi — nie ma okna z czerwoną bramką. Stub `root_workspace\.obsidian` (untracked, pusta karta) usunięty przed commitem, żeby `.obsidian` występował tylko w vaulcie.

not checked:
- R16 advisory: ten commit dotyka `scripts/**`, a `queries.jsonl` w `_scratch/sessions/05_store` jest starszy niż 30 min — ostrzeżenie zostaje otwarte do czasu realnego zapytania do pamięci sesji.
- czy inne skrypty czytają `ALLOWED_ROOT` i zakładają w nim `.git` — sprawdzone tylko `test_gate_allowlist_parity.py`; pełny przegląd należy do commita `_repo_rel()`.
