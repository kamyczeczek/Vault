from pathlib import Path
bench_path = Path("bench.py")
text = bench_path.read_text(encoding="utf-8")
text = text.replace('"bigdict_elm", "amr_fbs" in P_dict', '"bigdict_elm" in P_dict and "amr_fbs" in P_dict')
bench_path.write_text(text, encoding="utf-8")
print("Fixed all occurrences in bench.py")
