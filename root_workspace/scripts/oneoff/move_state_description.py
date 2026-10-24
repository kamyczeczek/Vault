import shutil
from pathlib import Path

root = Path(__file__).resolve().parent.parent
src = root / "state_description"
dst = root / "handoff" / "state_description"

if src.exists():
    dst.parent.mkdir(exist_ok=True)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.move(str(src), str(dst))
    print(f"Moved {src} to {dst}")
else:
    print(f"{src} does not exist")
