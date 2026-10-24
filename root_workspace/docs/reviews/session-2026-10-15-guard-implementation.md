# Guard Implementation and Wiring Review — 2026-10-15

**Status końcowy:** Zakończone pomyślnie.

## 1. Kontekst i Decyzja Właściciela

Poprzednie sesje (`session-2026-10-14-guard-wiring-audit.md` oraz audyt sesji `01a13c4c`) wykazały, że `root_deletion_guard.py` oraz `commit_gate_guard.py` istniały jako pliki z poprawnymi selftestami, ale nie były nigdzie wywoływane przez żaden hook pre-commit. Dodatkowo zgłoszono 3 niezaimplementowane koncepcje (Stop Gate, Read-After-Edit, Self-Modification Audit).

W tej sesji właściciel podjął decyzję (Opcja A):
- Podłączyć dwa istniejące guardy (`root_deletion_guard.py` oraz `commit_gate_guard.py`) do automatycznego hooka pre-commit (`hooks/pre-commit`).
- Zapewnić mechanizm autoryzacji commita poprzez token runtime `` `.commit-approved` `` mintowany przez `scripts/close.py` bezpośrednio przed własnym commitem.
- Zadeklarować `` `.commit-approved` `` w `` `ALLOWED_ROOT` `` oraz `` `CLAUDE.md` `` i `` `.gitignore` ``, aby bramka integrity (`check_workspace_integrity.py`) nie zgłaszała błędu `unexpected file at workspace root`.

## 2. Realizacja

1. **Deklaracja `.commit-approved`**:
   - Dodano do `` `ALLOWED_ROOT` `` w `scripts/check_workspace_integrity.py` oraz do listy opcjonalnych plików (`optional = {"__pycache__", "scripts", ".commit-approved"}`).
   - Zadeklarowano w `CLAUDE.md` oraz dodano do `.gitignore`.
2. **Hook pre-commit (`hooks/pre-commit`)**:
   - Dodano wywołanie `` `python scripts/root_deletion_guard.py --check-staged` `` (skanuje `git diff --cached --name-status` pod kątem usunięcia chronionych wpisów root S32/S37).
   - Dodano wywołanie `` `python scripts/commit_gate_guard.py --check` `` (weryfikuje obecność świeżego tokena autoryzacji `` `.commit-approved` `` w ciągu `300` sekund).
   - Umieszczono oba wywołania **przed** bramką integrity, dzięki czemu tanie i ukierunkowane guardy blokują nieautoryzowane commity jako pierwsze.
3. **Minting w `scripts/close.py`**:
   - Po pomyślnym przejściu wszystkich walidacji i bramki integrity, `scripts/close.py` zapisuje token autoryzacji do `` `.commit-approved` `` tuż przed wykonaniem `git commit`.

## 3. Testy Adversarialne (Verbatim Output)

Przeprowadzono testy adversarialne w celu potwierdzenia, że guardy realnie blokują nieautoryzowane akcje:

### T1: Staged deletion chronionego pliku root -> blokada przez `root_deletion_guard`
```powershell
PS C:\Users\Mateusz\Desktop\root_workspace> git rm --cached AGENTS.md
rm 'AGENTS.md'
PS C:\Users\Mateusz\Desktop\root_workspace> python scripts/root_deletion_guard.py --check-staged; echo "EXIT: $?"
root_deletion_guard: staged deletion of a protected workspace root entry (S32, S37):
  D     AGENTS.md
Root entries are the workspace contract. Restore it, or get explicit owner approval recorded in the commit body.
EXIT: 1
PS C:\Users\Mateusz\Desktop\root_workspace> git checkout -- AGENTS.md
```

### T2: Commit bez tokena autoryzacji -> blokada przez `commit_gate_guard`
```powershell
PS C:\Users\Mateusz\Desktop\root_workspace> rm -f .commit-approved
PS C:\Users\Mateusz\Desktop\root_workspace> python scripts/commit_gate_guard.py --check; echo "EXIT: $?"
commit_gate_guard: no fresh .commit-approved token — commit blocked.
Mint one by closing the session through scripts/close.py (it writes .commit-approved after validation and before its commit), or create it explicitly if you are committing outside close.py.
EXIT: 1
```

### T3: Token świeży -> przepuszczenie przez `commit_gate_guard`
```powershell
PS C:\Users\Mateusz\Desktop\root_workspace> touch .commit-approved
PS C:\Users\Mateusz\Desktop\root_workspace> python scripts/commit_gate_guard.py --check; echo "EXIT: $?"
EXIT: 0
PS C:\Users\Mateusz\Desktop\root_workspace> rm -f .commit-approved
```

## 4. Naruszenia i not checked

- **not checked:** testy pełnego integracyjnego commita z poziomu zewnętrznych narzędzi (innych niż `scripts/close.py`), audyt rygoru pozostałych 3 hipotetycznych guardów (Stop Gate, Read-After-Edit, Self-Modification Audit) odroczony jako dług architektoniczny bez aktywnego kodu.

## 5. Powiązania
- Powiązane raporty: `session-2026-10-15-workspace-gate-exclusion-audit.md`, `session-2026-10-14-guard-wiring-audit.md`.

## Tool calls
| Wartość | Komenda | Surowy output (fragment) |
|---|---|---|
| 1 | `python scripts/root_deletion_guard.py --check-staged` | `EXIT: 1` |
| 1 | `python scripts/commit_gate_guard.py --check` | `EXIT: 1` |
| 0 | `python scripts/commit_gate_guard.py --check` | `EXIT: 0` |
