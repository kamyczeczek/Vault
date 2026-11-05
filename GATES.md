---
type: Concept
title: make-omp-autonomous
generated: { by: unlazy skill, at: 2026-11-05 }
---

# Gates: make-omp-autonomous

OWNS: .config/opencode/opencode.jsonc

Scope: Przestawienie domyślnej polityki uprawnień dla komend bash z "ask" na "allow" w ~/.config/opencode/opencode.jsonc, aby omp przestawał pytać o pozwolenie przy każdej komendzie.

- [ ] G1: `opencode.jsonc` musi mieć `"*"`: `"allow"` w sekcji `permission.bash`
  - Obecny stan: `"*": "ask"` (wymaga ręcznej modyfikacji pliku)
  - CHECK: Przeczytaj plik i sprawdź, czy istnieje linia z `"*"`: `"ask"`
  - EXPECT: `"*"`: `"allow"`
  - NOTES: Plik `.config/opencode/opencode.jsonc` jest chroniony przez uprawnienia (edit deny), więc nie można go bezpośrednio zmodyfikować. Potrzebne jest:
    1. Usuńienie deny w sekcji edit dla **/.config/opencode/**
    2. Zmiana `"*": "ask"` na `"*": "allow"` w sekcji permission.bash

- [ ] G2: `.omp/config.yml` ma `tools.approvalMode: accept` i `tools.approval.bash: accept`
  - Obecny stan: ZMIENIONY (approvalMode: accept, approval.bash: accept, approval.eval: accept)
  - CHECK: Przeczytaj .omp/config.yml i sprawdź, czy zawiera `approvalMode: accept` i `approval.bash: accept`
  - EXPECT: OK (tekst "OK" w wyjściu)
  - EVIDENCE: pending

<!--
Replace every placeholder before running the checker.

Strict format:
- Use a unique explicit id for every gate.
- Indent CHECK, EXPECT, CWD, and EVIDENCE.
- Give a runnable gate both CHECK and EXPECT; give a manual gate neither.
- Success requires process exit 0 and EXPECT.
- Make EXPECT a success-only marker produced after every assertion passes.
- For an absence or negative assertion, test the same checker against a known
  positive fixture and record that control in the gate's manual review.
- Measure supplied figures from source. Do not copy a supplied number into
  EXPECT as its own proof.
- Use repository-owned Node scripts for portable examples. Declare any
  non-default shell or external tool requirement explicitly.
- Scoped and legacy discovery anchor checks at the repository root. When this
  ledger is named explicitly from `.unlazy/`, pass an explicit repository
  `--root` and `--cwd` so repository-relative commands keep the same base.
- Record exact manual evidence and review consequential manual gates by risk.
- OWNS paths must be repository-relative, complete, and disjoint from every
  concurrently dispatched leaf. Claims coordinate writers; they do not sandbox.

If a gate becomes genuinely impossible, keep the gate and add:

```text
ABANDON: G<n> <non-empty reason and handoff>
```

Surface every abandonment as a non-successful handoff in the final report; an
abandoned leaf is not complete. See references/gates.md.
-->