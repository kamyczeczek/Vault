with open("bench.py", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace("from amr_fbs import", "from members.amr_fbs import")

with open("bench.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Fixed amr_fbs import in bench.py")
