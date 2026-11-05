#!/usr/bin/env python3
"""spawn_recursive.py — deterministic recursive reflection (route deterministically, spawn leaves).
Precomputes splits from graph.db (no model), then spawns one small `omp launch`
per leaf with a closed prompt (only its chunk bodies). Each leaf fits in the
300s background cap, so recursive fan-out stays runnable. Merge is deterministic
python.

Usage:
  python pipeline/06_reflect/spawn_recursive.py --dry-run
  python pipeline/06_reflect/spawn_recursive.py --model omniroute/opencode-zen/muse-spark-1.2-contributor-free
  python pipeline/06_reflect/spawn_recursive.py --limit 12 --depth 1 --topic icm --topic reflection
"""
from __future__ import annotations
import argparse, json, sqlite3, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "knowledge" / "graph" / "graph.db"
TOPICS_MD = ROOT / "knowledge" / "topics.md"
CORPUS = ROOT / "knowledge" / "corpus"
LEAVES_DIR = ROOT / "pipeline" / "06_reflect" / "leaves"
REF_DIGESTS = ROOT / "reflection" / "digests"
REF_CANDIDATES = ROOT / "reflection" / "candidates"
EXT = ROOT / ".omp" / "extensions" / "workspace-research.ts"
OMP_EXE = Path("C:/Users/Mateusz/.bun/bin/omp.exe")

def load_topics() -> list[str]:
    if not TOPICS_MD.exists():
        return []
    out=[]
    for line in TOPICS_MD.read_text(encoding="utf-8").splitlines():
        line=line.strip()
        if line.startswith("- "):
            out.append(line[2:].strip())
    return sorted(set(out))

def query_ids(tags: list[str], limit: int) -> list[str]:
    conn = sqlite3.connect(DB)
    where = " AND ".join(["tags LIKE ?" for _ in tags]) if tags else "1"
    params = [f'%"{t}"%' for t in tags]
    rows = conn.execute(f"SELECT id FROM nodes WHERE {where} ORDER BY id LIMIT ?", (*params, limit)).fetchall()
    conn.close()
    return [r[0] for r in rows]

def read_chunk_body(chunk_id: str) -> str:
    # find corpus file whose stem == id or whose front-matter id == chunk_id
    for p in sorted(CORPUS.glob("*.md")):
        if p.stem == chunk_id:
            txt = p.read_text(encoding="utf-8", errors="ignore")
            # strip front-matter
            if txt.startswith("---"):
                idx = txt.find("\n---\n", 3)
                if idx != -1:
                    txt = txt[idx+5:]
            return txt.strip()[:4000]
    # fallback: scan for id in front-matter
    for p in sorted(CORPUS.glob("*.md")):
        head = p.read_text(encoding="utf-8", errors="ignore")[:2000]
        if f"id: {chunk_id}" in head:
            txt = p.read_text(encoding="utf-8", errors="ignore")
            if txt.startswith("---"):
                idx = txt.find("\n---\n", 3)
                if idx != -1:
                    txt = txt[idx+5:]
            return txt.strip()[:4000]
    return "(not found)"

def build_leaf_prompt(topic: str, tags: list[str], ids: list[str]) -> str:
    bodies="\n\n".join(f"### {cid}\n{read_chunk_body(cid)}" for cid in ids)
    return f"""You are a leaf reflection agent. You already have the graph digest auto-injected.
LEAF TOPIC: {topic}  (routed deterministically: tags={tags} → {len(ids)} chunks, ids={ids})

TASK: Reflect ONLY on the {len(ids)} chunks below. Every claim must cite one of these ids.
Do not query further. Do not read other corpus files.

CHUNKS (ground truth, truncated to 4k each):
{bodies}

OUTPUT (write exactly these two files, no other writes):
1. reflection/digests/{topic}.md — sections: Claim / Evidence (cite among {ids}) / Decision / Next bet. One claim per leaf.
2. reflection/candidates/{topic}.jsonl — one JSON object: {{"id":"{topic}","state":"proposed","claim":"...","evidence":[...subset of {ids}...],"bet":"..."}}

When both files are written, reply exactly: DONE {topic}
"""

def main()->int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=12)
    ap.add_argument("--depth", type=int, default=1, choices=[1,2], help="1=one leaf per topic, 2=split large topics by second tag (ADAPT)")
    ap.add_argument("--threshold", type=int, default=4, help="ADAPT: if intersection < threshold, expand via SHARES_TAG one hop")
    ap.add_argument("--topic", action="append", default=None, help="restrict to these topic tags (repeatable)")
    ap.add_argument("--model", default="omniroute/opencode-zen/muse-spark-1.2-contributor-free")
    ap.add_argument("--max-topics", type=int, default=4)
    args=ap.parse_args()

    # W1 hard gate: refuse stale digest (same as spawn.py)
    watch = subprocess.run([sys.executable, str(ROOT / "knowledge" / "graph" / "watch.py"), "--once"],
                           text=True, capture_output=True)
    fp_file = ROOT / "knowledge" / "graph" / ".graph_fingerprint"
    digest_fp = ""
    for line in (ROOT / "knowledge" / "graph" / "GRAPH-DIGEST.md").read_text(encoding="utf-8").splitlines() if (ROOT / "knowledge" / "graph" / "GRAPH-DIGEST.md").exists() else []:
        if "fingerprint:" in line:
            m = __import__("re").search(r"fingerprint:\s*([0-9a-f]{12})", line)
            if m: digest_fp = m.group(1); break
    live_fp = fp_file.read_text(encoding="utf-8").strip() if fp_file.exists() else ""
    if live_fp and digest_fp and live_fp != digest_fp:
        print(f"STALE_DIGEST: .graph_fingerprint={live_fp} vs GRAPH-DIGEST {digest_fp} — run build_graph.py", file=sys.stderr)
        return 1
    if watch.returncode != 0:
        print(f"watch.py failed: {watch.stderr}", file=sys.stderr)
        return 1


    topics = args.topic if args.topic else load_topics()
    topics = sorted(set(topics))[:args.max_topics]

    # deterministically precompute splits (no model) — ADAPT one level
    leaves: list[tuple[str, list[str], list[str]]] = []  # (leaf_topic, tags, ids)
    for t in topics:
        ids = query_ids([t], args.limit)
        if not ids:
            print(f"skip {t}: no chunks")
            continue
        if len(ids) < args.threshold:
            # ADAPT: thin intersection → one-hop SHARES_TAG expansion (deterministic, ORDER BY id)
            conn = sqlite3.connect(DB)
            rows = conn.execute("SELECT dst FROM edges WHERE src IN ({}) AND kind='SHARES_TAG'".format(",".join("?"*len(ids))), ids).fetchall()
            conn.close()
            expanded = sorted(set(ids) | {r[0] for r in rows})[:args.limit]
            print(f"expand {t}: {len(ids)} → {len(expanded)} via SHARES_TAG")
            ids = expanded
        if args.depth==2 and len(ids)>=args.limit:
            conn=sqlite3.connect(DB)
            rows=conn.execute(f"SELECT tags FROM nodes WHERE {' AND '.join(['tags LIKE ?']*1)}", (f'%"{t}"%',)).fetchall()
            conn.close()
            from collections import Counter
            cnt=Counter()
            for (js,) in rows:
                try: tags=json.loads(js)
                except: tags=[]
                for x in tags:
                    if x!=t: cnt[x]+=1
            for co,_ in cnt.most_common(2):
                sub_ids=query_ids([t, co], args.limit)
                if 2 <= len(sub_ids) < len(ids):
                    leaves.append((f"{t}__{co}", [t, co], sub_ids))
            if not any(l[0].startswith(t+"__") for l in leaves):
                leaves.append((t, [t], ids))
        else:
            leaves.append((t, [t], ids))

    print(f"planned {len(leaves)} leaves (depth={args.depth}, limit={args.limit}):")
    for topic, tags, ids in leaves:
        print(f"  {topic}: tags={tags}  ids={ids[:6]}{' ...' if len(ids)>6 else ''}")

    if args.dry_run:
        return 0

    LEAVES_DIR.mkdir(parents=True, exist_ok=True)
    REF_DIGESTS.mkdir(parents=True, exist_ok=True)
    REF_CANDIDATES.mkdir(parents=True, exist_ok=True)

    processes=[]
    for topic, tags, ids in leaves:
        prompt = build_leaf_prompt(topic, tags, ids)
        prompt_path = LEAVES_DIR / f"{topic}.prompt"
        prompt_path.write_text(prompt, encoding="utf-8")
        cmd = [str(OMP_EXE), "launch", "--model", args.model,
               "--cwd", str(ROOT), "--extension", str(EXT),
               "-p", f"@{prompt_path}"]
        # W3: close the verification loop — run the agent then validate
        p = subprocess.Popen(cmd)
        processes.append((topic, p))

    # poll — each leaf is scoped to ≤12 chunks so it fits the 300s cap
    for topic, p in processes:
        ret = p.wait()
        print(f"leaf {topic} exit={ret}")
        time.sleep(0.5)

    # W3: post-merge closure gate — fail the checkpoint if any digest is ungrounded
    gate = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_reflection.py")],
                          text=True, capture_output=True, cwd=str(ROOT))
    print(gate.stdout.rstrip())
    if gate.stderr: print(gate.stderr.rstrip(), file=sys.stderr)
    if gate.returncode != 0:
        print("REFLECTION_GATE_FAILED — digests missing citations or unknown ids", file=sys.stderr)
        return gate.returncode

    # merge: concat candidates into rollup
    rollup = LEAVES_DIR / "rollup.jsonl"
    with open(rollup, "w", encoding="utf-8") as out:
        for topic, _, _ in leaves:
            cand = REF_CANDIDATES / f"{topic}.jsonl"
            if cand.exists():
                for line in cand.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        out.write(line+"\n")
    print(f"rollup: {rollup}  lines={sum(1 for _ in open(rollup,encoding='utf-8')) if rollup.exists() else 0}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
