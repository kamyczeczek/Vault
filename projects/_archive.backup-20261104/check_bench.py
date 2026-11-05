with open("bench.py", "r", encoding="utf-8") as f:
    text = f.read()

# Let's see where amr_fbs is added to singleton dict
print("amr_fbs in bench.py:", "amr_fbs" in text)
