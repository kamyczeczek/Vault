with open("bench.py", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace('"bigdict_elm", "amr_fbs" in P_dict', '"bigdict_elm" in P_dict and "amr_fbs" in P_dict')

with open("bench.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Fixed membership check in bench.py")
