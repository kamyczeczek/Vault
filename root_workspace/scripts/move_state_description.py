"""Shim for migrated move_state_description.py.
Original script moved to scripts/oneoff/move_state_description.py.
"""
from pathlib import Path
import runpy

target = Path(__file__).resolve().parent / "oneoff" / "move_state_description.py"
print(f"Executing migrated one-off script: {target}")
runpy.run_path(str(target), run_name="__main__")
