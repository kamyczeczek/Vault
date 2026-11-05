"""Fetch genuine ETTh1 (transformer temperature, hourly, OT column).
Tries: (1) HuggingFace dataset discovery API, (2) GitHub ETDataset mirrors.
Writes data/ETTh1_h1.csv (columns: date, OT). Prints source used."""
import json, urllib.request, sys, time, pathlib

UA = {"User-Agent": "Mozilla/5.0 (benchmark research)"}
ROOT = pathlib.Path(__file__).resolve().parent

def get(url, timeout=90, binary=False):
    req = urllib.request.Request(url, headers=UA)
    d = urllib.request.urlopen(req, timeout=timeout).read()
    return d if binary else json.loads(d)

def hf_discover():
    import urllib.parse
    print("[hf] searching datasets named ETT...")
    try:
        items = get("https://huggingface.co/api/datasets?search=ett&limit=20")
        ids = [it.get("id") for it in items][:8]
        ids = [i for i in ids if "ett" in i.lower()] + [i for i in ids if "ett" not in i.lower()]
        print("[hf] candidates:", ids)
    except Exception as e:
        print("[hf] search failed:", repr(e)[:150]); return None
    for did in ids:
        try:
            tree = get(f"https://huggingface.co/api/datasets/{did}/tree/main?recursive=true", timeout=30)
        except Exception as e:
            print(f"[hf] tree fail {did}:", repr(e)[:100]); continue
        files = [t["path"] for t in tree if t["path"].lower().endswith((".csv", ".parquet"))]
        print(f"[hf] {did}: {len(files)} tabular files -> {files[:5]}")
        good = [p for p in files if "ett" in p.lower() or "h1" in p.lower()] or (files[:1] if len(files) == 1 else [])
        if not good:
            continue
        for p in good[:3]:
            url = f"https://huggingface.co/datasets/{did}/resolve/main/{urllib.parse.quote(p, safe='/')}"
            try:
                raw = get(url, binary=True)
            except Exception as e:
                print("[hf] download fail", did, p, repr(e)[:100]); continue
            ok = parse_to_etth1(raw, did + ":" + p)
            if ok:
                return ok
    return None

def parse_to_etth1(raw, source):
    import pandas as pd, io
    try:
        df = pd.read_csv(io.BytesIO(raw))
    except Exception:
        try:
            df = pd.read_parquet(io.BytesIO(raw))
        except Exception as e:
            print("[hf] parse fail:", repr(e)[:100]); return None
    cols = {c.lower(): c for c in df.columns}
    temp_col = None
    for cand in ("ot", "oiltemp", "temperature", "hufl"):
        if cand in cols:
            temp_col = cols[cand]; break
    if temp_col is None:
        num = [c for c in df.columns if df[c].dtype.kind in "fi" and c.lower() != "iot"]
        if not num:
            print("[hf] no numeric temp column in", source, list(df.columns)[:8]); return None
        temp_col = num[0]
    s = pd.to_numeric(df[temp_col], errors="coerce").dropna().to_numpy(dtype=float)
    if len(s) < 8640:
        print(f"[hf] {source}: {temp_col} n={len(s)} (<8640, not ETTh1 hourly?) skip")
        return None
    dates = df.iloc[:len(s)].index
    out = pd.DataFrame({"date": dates[:len(s)], "OT": s[:len(s)]})
    p = ROOT / "data" / "ETTh1_h1.csv"
    out.to_csv(p, index=False)
    print(f"[hf] SAVED {p}  source={source}  col={temp_col}  n={len(s)}  mean={s.mean():.2f} std={s.std():.2f}")
    return out

def github_try():
    urls = [
        "https://raw.githubusercontent.com/zhouhaoyi/ETDataset/main/ETT.csv",
        "https://github.com/zhouhaoyi/ETDataset/raw/master/ETT.csv",
        "https://raw.githubusercontent.com/laumaitre/ETDataset/main/ETT-small/ETT.csv",
    ]
    import io, pandas as pd
    for u in urls:
        try:
            print("[gh] trying", u)
            raw = get(u, timeout=120, binary=True)
            df = pd.read_csv(io.BytesIO(raw))
            print("[gh] cols:", list(df.columns)[:10], "rows:", len(df))
            # ETT.csv: columns hufl hull mull mufl lull lufl iot ot + date; rows prefixed with "ETTh1a" etc.
            if "ETTh1" not in str(df.columns) and "ETTh1" in str(df.iloc[:, 0]) or "ETTh1" in str(df.columns):
                mask = df.astype(str).apply(lambda c: c.str.startswith("ETTh1") if c.name in df.columns[:1] else False).any(axis=1) if "ETTh1" not in str(df.columns) else df.iloc[:, 0].astype(str).str.startswith("ETTh1")
                sub = df[mask]
                s = pd.to_numeric(sub["OT"], errors="coerce").dropna().to_numpy(float)
                if len(s) >= 8640:
                    out = pd.DataFrame({"date": sub.iloc[:, 0].tolist(), "OT": s})
                    p = ROOT / "data" / "ETTh1_h1.csv"
                    out.to_csv(p, index=False)
                    print(f"[gh] SAVED {p} n={len(s)} mean={s.mean():.2f} std={s.std():.2f}")
                    return out
        except Exception as e:
            print("[gh] fail:", repr(e)[:140])
    return None

def main():
    t0 = time.time()
    res = hf_discover() or github_try()
    if res is None:
        print("FETCH_FAILED — will use project ETT analog")
        sys.exit(1)
    print(f"DONE in {time.time()-t0:.0f}s")

if __name__ == "__main__":
    main()
