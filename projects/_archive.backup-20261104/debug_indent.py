from pathlib import Path
path = Path("bench.py")
lines = path.read_text(encoding="utf-8").splitlines()
for idx, l in enumerate(lines[490:520], start=491):
    print(f"{idx:3d}: {l}")
