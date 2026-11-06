---
flag: raw-sessions-github-push-2026-11-06
since: 2026-11-06
owner: mateusz
agent: opencode
model: nvidia/stepfun-ai/step-5-preview
origin: user request (m00003): "chciałbym by skrypt scripts/raw_sessions_drive.bat robił push przeszłości N sesji do github"
---

`raw-sessions-github-push-2026-11-06` — 2026-11-06: `scripts/raw_sessions_drive.bat`
po eksporcie (N najnowszych sesji, domyślnie 5) pushuje `raw_sessions.md` do
**osobnego, prywatnego** repo archiwum `kamyczeczek/raw-sessions` (domyślnie
`main`; nadpisywany plik = okno N sesji, historia w git). Sync do Google Drive
został bez zmian i działa obok. Nowy helper `scripts/push_sessions_github.py`
(stdlib-only): clone-or-init `scripts/_scratch/sessions-github/` (gitignored) →
fast-forward do remote → kopiuj → `scan_secrets.py` jako bramka → commit tylko
gdy treść nowa → push. Repo: `--repo` > env `SESSIONS_GITHUB_REPO` > default.
Exit codes: 0 ok (również "nic do pushowania"), 2 repo, 3 źródło, 4 git, 5 sekrety.

## Wykonane
- Repo `kamyczeczek/raw-sessions` utworzone jako PRIVATE (`gh repo create
  --private --add-readme`); eksport NIGDY nie trafia do publicznego Vault.
- Bramka sekretów: `scan_secrets.py` odpala się na kopii w clone'ie przed
  `git add`; hit = exit 5 i brak commita (wiadomość mówi wprost, by bramki nie
  omijać). Zweryfikowano: sztuczny plik z `sk-nry-…` → `SECRETS_FOUND=1`, RC=5,
  bez push. Oczyszczony eksport (226 KB) → `SECRETS_CLEAN`.
- Weryfikacja E2E: `cmd /c scripts\raw_sessions_drive.bat 3` → 171 KB eksport →
  Drive `md5=836acdcf…` → `PUSHED: raw_sessions.md -> … [main]`, RC=0; commit
  `4c1f9587` "chore: refresh raw sessions export (3 sessions)" na remote.
- Idempotentność: ponowny push tego samego pliku → `EXPORT_UNCHANGED … nic do
  pushowania` (brak pustych commitów).
- `scripts/index.md` uzupełniony o `push_sessions_github.py`.

## Usterka naprawiona po drodze (pre-existing, nie spowodowana przeze mnie)
`.gitattributes` miał `* text=auto eol=lf`, więc `.bat` checkoutuje się z LF, a
`cmd.exe` na LF **zjada pierwszy znak każdej linii** (`'hcp' is not recognized`,
`'etlocal'`, `'cho'`). Dowód, że plik był LF i przed edycją:
`git ls-files --eol` → `i/lf`. Czyli `raw_sessions_drive.bat` był niedziałający
wcześniej — a „weryfikacja" z flagi `raw-sessions-dsh-included-2026-11-06`
(`python scripts/raw_sessions_drive.bat 3`) nie mogła się udać jako Python
(`SyntaxError: invalid syntax`, odtworzone). Fix: targeted rule
`scripts/raw_sessions_drive.bat text eol=crlf` (blob w repo zostaje
LF-normalized, checkout CRLF) + renormalizacja worktree. `git diff --check`
czysty; diff .bat = tylko moje 15 linii.

## Ryzyka / not checked
not checked: push z maszyny bez zapisanych credentiali GitHub; zachowanie przy
nieśledzonym stanie clone'u; repo z domyślnym branchem innym niż `main`
(wykrywane dynamicznie przez `ls-remote --symref`, ścieżka niepokryta testem);
test jednostkowy `push_sessions_github.py` (weryfikacja tylko E2E).
- Inne `.bat` w repo (`raw_sessions.bat`, `session_brief.bat`,
  `session_digest.bat`) mają ten sam defect LF — NIE naprawione (poza zakresem
  tego zlecenia; kwalifikują się do tego samego leczenia `eol=crlf`).
- Nie przetestowano: push z maszyny bez zapisanych credentiali GitHub
  (git-credential-manager); zachowanie przy niepustym, nieśledzonym stanie
  clone'u (skrypt hard-resetuje do FETCH_HEAD — udokumentowane single-writer);
  repo z domyślnym branchem innym niż `main` póki co (wykrywane dynamicznie
  przez `ls-remote --symref`, ścieżka niepokryta testem).

## Następny krok
Dodać regułę `eol=crlf` dla pozostałych `.bat` (osobny commit) albo potwierdzić,
że tylko ten jeden ma być naprawiony.
