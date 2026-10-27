import json, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "eval" / "artifact_manifest.json"

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

m = json.loads(MANIFEST.read_text(encoding="utf-8"))
for entry in m.get("artifacts", []):
    p = ROOT / entry["path"]
    if p.exists():
        entry["sha256"] = sha256(p)
        print(f"Updated {entry['path']} -> {entry['sha256']}")

MANIFEST.write_text(json.dumps(m, indent=4), encoding="utf-8")
print("Manifest updated.")
