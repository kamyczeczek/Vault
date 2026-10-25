---
type: Concept
title: ADR-007-git-baseline-and-remote
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# ADR-007: Baseline `59faa7d` zostaje; `697b9e3` dostaje tag, remote jest warunkiem trwałości

## Status

Accepted (2026-10-24).

## Kontekst

`.git` w `root_workspace` został opróżniony 2026-10-24 17:18–17:41 (0 plików, brak
remote'a), a zamiast odzyskiwania zrobiono `git init` i root-commit `59faa7d` (686
plików). Pierwsza próba, `697b9e3`, zawierała 5 plików i resztę jako intent-to-add;
została zdjęta z `HEAD` przez `update-ref -d HEAD`. Obiekt `697b9e3` **wciąż istnieje**
jako unreachable (osiągalny tylko przez reflog, `git diff 697b9e3 HEAD` = 682 pliki),
więc zniknie po wygaśnięciu refloga. Historia sprzed `git init` jest nieodwracalna na
tej maszynie.

## Decyzja

1. `59faa7d` jest przyjętym baseline'em; historia nie jest przepisywana.
2. `697b9e3` dostaje tag `archival-697b9e3` **przed** utworzeniem bundle'a (bundle
   `--all` pakuje wyłącznie refy — unreachable commit nie trafiłby do kopii).
3. Trwałość zapewnia **remote** `kamyczeczek/vault` (private); sam dysk lokalny nie
   jest zabezpieczeniem, o czym świadczy ten incydent.
4. Kopia awaryjna (`git bundle`) zostaje w `Desktop\`, poza repo.

## Konsekwencje

- Tag czyni `697b9e3` osiągalnym na stałe, więc `git gc` go nie usunie.
- Push do prywatnego remote'a jest jedynym elementem, którego nie da się zastąpić
  dyscypliną — bez niego powtórka incydentu jest kwestią czasu.
