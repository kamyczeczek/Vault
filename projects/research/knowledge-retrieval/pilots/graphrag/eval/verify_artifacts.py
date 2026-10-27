"""Deterministyczna weryfikacja artefaktów sesji.
Uruchomienie: python eval/verify_artifacts.py

Exit code:
  0 = OK (wszystkie artefakty istnieją, hashe się zgadzają)
  1 = FAILED (brak pliku, hash niezgodny)
  2 = FALSE_DONE (manifest deklaruje plik, którego nie ma)
"""
import sys
import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "eval" / "artifact_manifest.json"

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    if not MANIFEST.exists():
        print(f"FAIL: brak manifestu: {MANIFEST}")
        return 1
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors = []
    for entry in m.get("artifacts", []):
        p = ROOT / entry["path"]
        if not p.exists():
            errors.append(f"FALSE_DONE: brak pliku {p}")
            continue
        actual = sha256(p)
        if actual != entry["sha256"]:
            errors.append(f"HASH MISMATCH: {p}")
    if errors:
        for e in errors:
            print(e)
        return 2 if any("FALSE_DONE" in e for e in errors) else 1
    print(f"OK: {len(m['artifacts'])} artefaktów zweryfikowanych")
    return 0

if __name__ == "__main__":
    sys.exit(main())
