from pathlib import Path
path = Path("bench.py")
text = path.read_text(encoding="utf-8")
text = text.replace("\n        fits = {", "\n    fits = {")
path.write_text(text, encoding="utf-8")
print("Fixed indentation of fits = {")
