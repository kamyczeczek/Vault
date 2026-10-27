from pathlib import Path
bench_path = Path("bench.py")
text = bench_path.read_text(encoding="utf-8")
text = text.replace("from amr_fbs import", "from members.amr_fbs import")
bench_path.write_text(text, encoding="utf-8")
print("Updated import to members.amr_fbs")
