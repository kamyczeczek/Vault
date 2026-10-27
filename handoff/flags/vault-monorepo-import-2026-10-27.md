---
flag: vault-monorepo-import-2026-10-27
since: 2026-10-27
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
---

`vault-monorepo-import-2026-10-27` — 2026-10-27: cały vault w jednym repo GitHub.
Stan: 12 zagnieżdżonych repo zastąpione plikami + `history.bundle` (każde odtwarzalne
przez `git clone history.bundle`); `.gitignore` zwężony do toolchainu, sekretów,
książek i plików >100 MB. `check_workspace_integrity._tracked_files` pyta teraz repo
nadrzędne, bo projekt bez własnego `.git` nie ma już „zera śledzonych plików”.
Next: push (~300 MB) i weryfikacja świeżego `git clone`.
not checked: push do GitHuba i świeży `git clone` — dopiero po tym commicie.
Książki z `library/` i archiwów zostają poza repo (świadoma decyzja, nie przeoczenie).
