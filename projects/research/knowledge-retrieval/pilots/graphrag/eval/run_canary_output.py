import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
output_path = ROOT / "extended_eval_canary_output.txt"
extended_eval_script = ROOT / "extended_eval.py"

res = subprocess.run([sys.executable, str(extended_eval_script)], capture_output=True, text=True, encoding="utf-8")
combined = f"STDOUT:\n{res.stdout}\n\nSTDERR:\n{res.stderr}\n\nEXIT CODE: {res.returncode}\n"
output_path.write_text(combined, encoding="utf-8")
print(f"Finished running extended_eval.py, exit code {res.returncode}. Written to {output_path}")
