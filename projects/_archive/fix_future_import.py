with open("bench.py", "r", encoding="utf-8") as f:
    text = f.read()

# remove all future imports
text = text.replace("from __future__ import annotations\n", "")

# put it at the very top
text = "from __future__ import annotations\n" + text

with open("bench.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Moved future import to top of bench.py")
