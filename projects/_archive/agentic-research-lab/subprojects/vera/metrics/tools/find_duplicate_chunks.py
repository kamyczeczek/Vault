"""Eviction pass step 1: find duplicate-ingestion groups in the corpus.

A group = same slug suffix under >=2 different numeric prefixes where ALL
members have a numeric prefix (i.e., NN_slug files). Reports exact-hash matches
vs divergent content. Read-only.
"""
import collections
import hashlib
import pathlib

CORPUS = pathlib.Path("knowledge/corpus")
files = sorted(p.name for p in CORPUS.iterdir() if p.suffix == ".md")

suffixes = collections.defaultdict(list)
for f in files:
    base = f[:-3]
    if "_" in base and base.split("_", 1)[0].isdigit():
        suffix = base.split("_", 1)[1]
        suffixes[suffix].append(f)
    # non-prefixed files (e.g. reflection_rule_of_scars, bm25_...) are never duplicates by this rule

groups = {k: v for k, v in suffixes.items() if len(v) > 1}
print(f"corpus files: {len(files)}; multi-member suffix groups: {len(groups)}\n")
print("== EXACT-HASH pairs (definitive duplicates) ==")
exact = 0
for name, members in sorted(groups.items()):
    hashes = [hashlib.sha256((CORPUS / m).read_bytes()).hexdigest() for m in members]
    seen = {}
    for m, h in zip(members, hashes):
        if h in seen:
            exact += 1
            print(f"  {seen[h]!r} == {m!r}  ({name})")
        else:
            seen[h] = m
print(f"exact pairs: {exact}\n")
print("== DIVERGENT SMALL groups (2-3 members, non-sequential = re-ingestion suspects) ==")
for name, members in sorted(groups.items()):
    nums = [int(m.split("_", 1)[0]) for m in members]
    if 2 <= len(members) <= 3:
        sequential = all(b - a == 1 for a, b in zip(nums, nums[1:]))
        hashes = [hashlib.sha256((CORPUS / m).read_bytes()).hexdigest()[:10] for m in members]
        marker = "seq(parts)" if sequential else "NON-SEQ"
        print(f"  {marker:10s} {members}  hashes={hashes}")
