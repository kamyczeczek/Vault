with open("bench.py", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace("        fits = {", "    fits = {")

with open("bench.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Fixed line 495 indentation.")
