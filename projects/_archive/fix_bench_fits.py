from pathlib import Path
bench_path = Path("bench.py")
text = bench_path.read_text(encoding="utf-8")
old_block = '''    if _HAS_BIGDICT:
        fits["bigdict_elm", "amr_fbs"] = (fit_bigdict, pred_bigdict)'''

new_block = '''    if _HAS_BIGDICT:
        fits["bigdict_elm"] = (fit_bigdict, pred_bigdict)
        from amr_fbs import fit_amr_fbs, pred_amr_fbs
        fits["amr_fbs"] = (fit_amr_fbs, pred_amr_fbs)'''

assert old_block in text, "old_block not found"
text = text.replace(old_block, new_block)
bench_path.write_text(text, encoding="utf-8")
print("Successfully fixed bench.py fit registry.")
