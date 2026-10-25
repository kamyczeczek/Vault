"""Smoke probe for the DSH zstd store (NOT a pytest test: no assertions).

Run: python scripts/smoke_zstd.py
Prints whether the zstandard module is available and whether a DSH
session archive decompresses. The tracked parser under test is
`scripts/agent_sessions.py` (load_deepseek_sessions).
"""
from pathlib import Path
import json

dsh_sessions = Path.home() / ".dsh" / "sessions"
zstd_files = list(dsh_sessions.glob("**/*.zstd"))
print(f"Found {len(zstd_files)} zstd files")

try:
    import zstandard as zstd
    print("zstandard module available")
    if zstd_files:
        p = zstd_files[0]
        print("Reading:", p)
        dctx = zstd.ZstdDecompressor()
        with p.open("rb") as f:
            data = dctx.decompress(f.read(), max_output_size=1024*1024*10)
        lines = data.decode("utf-8", errors="ignore").splitlines()
        print(f"Decompressed {len(lines)} lines")
        for line in lines[:3]:
            try:
                print(json.loads(line))
            except Exception as e:
                print("Line parse error:", e, line[:100])
except ImportError:
    print("zstandard module NOT available")
except Exception as e:
    print("Error reading zstd:", e)
