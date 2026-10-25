---
type: Concept
title: ADR-006-single-vault-single-repo
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# ADR-006: Jeden vault, jedno repo — `Desktop\vault` jest rootem, `root_workspace` podfolderem

## Status

Accepted (2026-10-24). Zastępuje w części D6 („root jest repozytorium git") i flagę
`vault-layout-root-2026-10-24`.

## Kontekst

Przez sesje 1, 9, 10 i 13 istniały dwa korzenie vaulta: `Desktop\vault` (utworzony
2026-10-24 16:39, prawdziwy vault — otwarty `Welcome.md`, graf) i
`root_workspace\.obsidian` (stub z 15:54, pusta karta). `.git` leżał w
`root_workspace`, więc vault i repozytorium miały różne granice: `Notes/`,
`.smart-env/` i `.obsidian/` były z definicji „poza repo", mimo że należą do vaulta.

## Decyzja

1. **Root vaulta = `Desktop\vault`.** `root_workspace` jest jego podfolderem i traci
   własne `.git`; repo obejmuje cały vault.
2. **Cztery wpisy są vault-owned**: `.git`, `.obsidian`, `.smart-env`, `Notes`.
   Każdy musi istnieć w **dokładnie jednym** z dwóch miejsc (`ROOT` albo `VAULT`) —
   bramka R1b egzekwuje XOR, więc stan „w obu" i „w żadnym" są błędem.
3. **Zagnieżdżony `.gitignore` zostaje** w `root_workspace` (wzorce są poprawne
   względem niego); vault-level `.gitignore` dostaje tylko wpisy vaulta.
4. **`Notes/` jest trackowane** w prywatnym repo — to jedyna nieodtwarzalna treść
   vaulta.
5. **`.smart-env/` jest odtwarzalne**: indeks embeddings nie jest migrowany, tylko
   generowany od nowa po instalacji pluginu Smart Connections (jego wykluczenia były
   pisane względem starego roota).

## Konsekwencje

- Każde wywołanie gita zwraca ścieżki względem **repo root**, a nie workspace'u;
  `git status --porcelain` i `--name-only` są repo-relative, `ls-files` i pathspecs —
  cwd-relative. `scripts/` normalizuje to przez `_repo_rel()`.
- Migracja jest osobnym commitem: przeniesienie `.git` czyni 686 plików rename'ami,
  więc historia baseline'u jest zachowana jako jeden commit, ale `--follow` może
  przestać działać.
- Nowy plik vaulta na poziomie `Desktop\vault` nie jest już widziany przez bramkę
  workspace'u; to świadoma granica, nie luka.
