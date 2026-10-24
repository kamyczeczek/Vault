"""Mechanical session digest: L1 cards + L0 skeleton.

Reads the same stores as `scripts/last_session_merged.py`, renders each
session body, and writes facts only. No interpretation and no model call.

`--classify` is a separate, strict second pass: it reads only the L1 cards,
writes `candidates/digest.judgment.{json,md}`, and never promotes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import uuid
from collections import Counter
from datetime import datetime, timedelta
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
AGENT_SESSIONS = SCRIPTS / "agent_sessions.py"
OUTDIR = SCRIPTS / "_scratch" / "sessions" / "02_products"
TOOL_CALLS = OUTDIR / "tool_calls.jsonl"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
import last_session_merged as merged  # noqa: E402
import session_facts as facts  # noqa: E402

L0_BUDGET = 15 * 1024
L1_BUDGET = 150 * 1024
JUDGMENT_SCHEMA_VERSION = "1.0"
CLASSIFIER_BACKEND = "rules"
CLASSIFIER_VERSION = 1
OPEN_MARKERS = frozenset({"blokada", "not_checked", "awaiting_owner"})


def load_agent_sessions():
    spec = spec_from_file_location("agent_sessions", AGENT_SESSIONS)
    if spec is None or spec.loader is None:
        sys.exit(f"Nie moge zaladowac {AGENT_SESSIONS}")
    module = module_from_spec(spec)
    sys.modules["agent_sessions"] = module
    spec.loader.exec_module(module)
    return module


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def stable_key(s) -> str:
    return f"{s.agent}:{s.id}"


def card_hash(card: dict) -> str:
    payload = {k: v for k, v in card.items() if k not in ("card_sha256", "ses_n")}
    return sha256_text(canonical_json(payload))


def parse_ts(val: str):
    return facts.parse_local_ts(val)


def select_sessions(sessions, count: int, days: int | None, until: str | None):
    cutoff = None
    if days is not None and days > 0:
        cutoff = datetime.now().replace(microsecond=0) - timedelta(days=days)
    until_dt = parse_ts(until) if until else None
    filtered = []
    for s in sessions:
        ts = parse_ts(s.updated_at or s.created_at)
        if until_dt is not None:
            if ts is None or ts > until_dt:
                continue
        if cutoff is not None:
            if ts is None or ts < cutoff:
                continue
        filtered.append(s)
    main = [s for s in filtered if not s.parent]
    children_by_parent: dict[str, list] = {}
    for s in filtered:
        if s.parent:
            children_by_parent.setdefault(s.parent, []).append(s)
    selected_main = main[:count]
    selected_keys = {stable_key(s) for s in selected_main}
    selected_children = []
    for s in selected_main:
        for child in children_by_parent.get(s.id, []):
            if stable_key(child) not in selected_keys:
                selected_children.append(child)
                selected_keys.add(stable_key(child))
    return selected_main, selected_children, len(filtered)


def load_tool_calls(path: Path | None):
    if path is None or not path.is_file():
        return None
    rows = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    stat = path.stat()
    meta = {
        "path": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
    }
    by_key = Counter()
    by_session = Counter()
    has_key = False
    for row in rows:
        key = row.get("key")
        if key:
            by_key[key] += 1
            has_key = True
        try:
            by_session[int(row.get("s"))] += 1
        except Exception:
            continue
    return {"by_key": by_key, "by_session": by_session, "has_key": has_key}, meta


def tool_facts(s, body: str, sidecar, sidecar_meta):
    body_calls = facts.tool_block_count(body)
    if sidecar is None:
        if body_calls == 0:
            return {"status": "none", "calls": 0}
        return {"status": "missing", "calls": body_calls}
    if sidecar["has_key"]:
        calls = int(sidecar["by_key"].get(stable_key(s), 0))
    else:
        calls = body_calls
    updated = parse_ts(s.updated_at or s.created_at)
    side_mtime = parse_ts(sidecar_meta["mtime"])
    if sidecar["has_key"]:
        fresh = updated is not None and side_mtime is not None and side_mtime >= updated
        status = "fresh" if fresh else "stale"
    else:
        status = "missing"
    if calls == 0 and body_calls == 0:
        status = "none"
    out = {"status": status, "calls": calls}
    if status != "none":
        out["sha256"] = sidecar_meta["sha256"]
        out["mtime"] = sidecar_meta["mtime"]
    return out


def evidence(body: str, quote: str, session_key: str):
    norm_body = facts.normalize_text(body)
    norm_quote = facts.normalize_text(quote)
    if not norm_quote or norm_quote not in norm_body:
        return None
    line = norm_body[: norm_body.find(norm_quote)].count("\n") + 1
    return {
        "session_key": session_key,
        "source": "body",
        "line": line,
        "sha": sha256_text(norm_body),
    }


def make_card(s, ses_n: int, body: str, sidecar, sidecar_meta, flags_dir: Path):
    key = stable_key(s)
    ids = []
    card = {
        "stable_key": key,
        "agent": s.agent,
        "session_id": s.id,
        "ses_n": ses_n,
        "parent_session_id": s.parent or "",
        "child_session_ids": [],
        "date": s.updated_at or s.created_at or "",
        "duration": facts.duration(s),
        "model": s.model or "",
        "micro": bool(s.message_count <= 4),
        "goal": facts.extract_goal(body, s.agent),
        "ending": facts.extract_ending(body, s.agent),
        "flags": ids,
        "flags_missing": facts.flags_missing(ids, flags_dir),
        "commits": [],
        "files": [],
        "tests": facts.extract_tests(body),
        "losses": facts.extract_losses(body),
        "tool_facts": tool_facts(s, body, sidecar, sidecar_meta),
    }
    card["card_sha256"] = card_hash(card)
    return card


def card_from_actions(s, body: str, sidecar, sidecar_meta, flags_dir: Path):
    card = make_card(s, 0, body, sidecar, sidecar_meta, flags_dir)
    try:
        regions = merged._scan_actions_regions(body.split("\n"))
    except Exception:
        regions = []
    flags = []
    commits = []
    file_counts = Counter()
    for region in regions:
        tool = (region.get("tool") or "").strip().lower()
        args = region.get("args") or ""
        out = region.get("out") or ""
        if tool in facts.WRITE_TOOLS or re.search(
                r"\b(?:git\s+(?:rm|mv)|Remove-Item|Move-Item|del\s|rm\s)", args):
            for flag in facts.FLAG_RE.findall(args):
                if flag not in flags:
                    flags.append(flag)
        for line in out.splitlines():
            if re.match(r"^\s*(?:D|deleted:)\s+handoff[/\\]flags[/\\]", line):
                for flag in facts.FLAG_RE.findall(line):
                    if flag not in flags:
                        flags.append(flag)
        for sha in facts.COMMIT_RX.findall(out):
            if sha not in commits:
                commits.append(sha)
        try:
            args_obj = json.loads(args) if args.startswith("{") else None
        except Exception:
            args_obj = None
        if tool in facts.WRITE_TOOLS and isinstance(args_obj, dict):
            for key in facts.PATH_KEYS:
                path = args_obj.get(key)
                if isinstance(path, str) and path.strip():
                    path = path.strip()
                    root = str(ROOT)
                    if path.startswith(root):
                        path = path[len(root):].lstrip("\\/")
                    file_counts[path] += 1
                    break
    card["flags"] = sorted(flags)
    card["flags_missing"] = facts.flags_missing(card["flags"], flags_dir)
    card["commits"] = sorted(commits)
    if file_counts:
        card["files"] = [p for p, _ in sorted(file_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]]
    else:
        card["files"] = facts.extract_files(body)
    card["card_sha256"] = card_hash(card)
    return card


def baseline_cards(path: Path | None):
    if path is None:
        return {}, None
    data = json.loads(path.read_text(encoding="utf-8"))
    cards = {}
    for card in data.get("cards", []):
        cards[card.get("stable_key", "")] = card
    return cards, data.get("source_cards_sha256")


def mechanical_delta(cards, baseline):
    out = []
    for card in cards:
        old = baseline.get(card["stable_key"])
        if not old:
            continue
        for field, kind in (("flags", "flag"), ("commits", "commit"), ("tests", "test")):
            previous = set(old.get(field, []))
            for value in card.get(field, []):
                if value in previous:
                    continue
                out.append({
                    "type": "mechanical_delta",
                    "kind": kind,
                    "session_key": card["stable_key"],
                    "value": value,
                    "evidence_check": "substring_exists",
                    "supports": None,
                })
    return out


def render_goal(goal: dict) -> str:
    if goal.get("kind") == "prompt":
        return f'"{goal.get("text", "")}"'
    reason = goal.get("reason") or facts.REASON_NO_EVIDENCE
    return f"none ({reason})"


def render_ending(ending: dict) -> str:
    if ending.get("kind") == "marker":
        return (f'marker `{ending.get("marker")}` @ {ending.get("source_line")}: '
                f'"{ending.get("raw_line", "")}"')
    if ending.get("kind") == "quote":
        return f'quote @ {ending.get("source_line")}: "{ending.get("text", "")}"'
    return f"none ({ending.get('reason') or facts.REASON_NO_EVIDENCE})"


def render_cards_md(payload: dict, coverage_sha: str) -> str:
    lines = [
        "# Session cards (L1)",
        "",
        f"- **Wygenerowano**: {payload['generated_at']}",
        f"- **Run ID**: `{payload['run_id']}`",
        f"- **Liczba kart**: {len(payload['cards'])} (main={payload['count_main']}, children={payload['count_children']})",
        f"- **Coverage SHA256**: `{coverage_sha}`",
        f"- **Normalizer**: `{facts.NORMALIZER_VERSION}`",
        "",
    ]
    for card in payload["cards"]:
        lines.append(f"## ses-{card['ses_n']:03d} — {card['agent']} — {card['date']}")
        lines.append(f"- **stable_key**: `{card['stable_key']}`")
        parent = card.get("parent_session_id") or "—"
        children = ", ".join(f"`{x}`" for x in card.get("child_session_ids", [])) or "—"
        lines.append(f"- **parent**: `{parent}` · **children**: {children}")
        lines.append(f"- **goal**: {render_goal(card['goal'])}")
        lines.append(f"- **ending**: {render_ending(card['ending'])}")
        lines.append(f"- **flags**: {', '.join(card['flags']) or '—'}")
        if card["flags_missing"]:
            lines.append(f"- **flags_missing**: {', '.join(card['flags_missing'])}")
        lines.append(f"- **commits**: {', '.join(card['commits']) or '—'}")
        lines.append(f"- **files**: {', '.join(card['files']) or '—'}")
        lines.append(f"- **tests**: {', '.join(card['tests']) or '—'}")
        losses = card["losses"]
        loss_text = ", ".join(f"{k}={v}" for k, v in losses.items() if v) or "—"
        lines.append(f"- **losses**: {loss_text}")
        tf = card["tool_facts"]
        lines.append(f"- **tool_facts**: {tf['status']} calls={tf['calls']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_l0_md(payload: dict, cards_payload: dict) -> str:
    cov = payload["coverage"]
    delta = payload.get("mechanical_delta", [])
    lines = [
        "# Session digest (L0)",
        "",
        f"- **Wygenerowano**: {payload['generated_at']}",
        f"- **Run ID**: `{payload['run_id']}`",
        f"- **Schema**: `{payload['schema_version']}`",
        f"- **Sesje główne**: {cov['count_main']}",
        f"- **Dzieci**: {cov['count_children']}",
        f"- **Zakres dat**: {cov['date_from'] or '—'} -> {cov['date_to'] or '—'}",
        f"- **Semantyka N**: {cov['n_semantics']}",
        f"- **Coverage SHA256**: `{payload['source_cards_sha256']}`",
        f"- **Nowe sesje od baseline**: {len(payload.get('new_sessions_since', []))}",
        f"- **Mechanical delta**: {len(delta)}",
        f"- **Judgment**: {len(payload.get('judgment', []))} ({payload['judgment_status']})",
        "",
        "## Decyzje",
        "_brak — judgment nie uruchomiony_",
        "",
        "## Sprzeczności",
        "_brak — judgment nie uruchomiony_",
        "",
        "## Otwarte wątki",
        "_brak — judgment nie uruchomiony_",
        "",
        "## Zmiany kierunku",
        "_brak — judgment nie uruchomiony_",
        "",
        "## Mechanical delta",
        "",
    ]
    if delta:
        for item in delta:
            lines.append(f"- `{item['kind']}` `{item['value']}` — {item['session_key']}")
    else:
        lines.append("_brak — baseline nie podany_")
    lines.append("")
    lines.append("## Karty")
    lines.append("")
    lines.append(f"Pełne karty: `session_cards.md` · JSON: `session_cards.json` · "
                 f"main={cov['count_main']}, children={cov['count_children']}")
    lines.append("")
    return "\n".join(lines)


def cards_descriptor(cards) -> dict:
    entries = sorted(
        ({"stable_key": c["stable_key"], "card_sha256": c["card_sha256"]} for c in cards),
        key=lambda item: item["stable_key"],
    )
    return {
        "schema_version": facts.CARD_SCHEMA_VERSION,
        "normalizer_version": facts.NORMALIZER_VERSION,
        "cards": entries,
    }


def ending_evidence(card: dict):
    ending = card.get("ending") or {}
    if ending.get("kind") == "marker" and ending.get("raw_line"):
        return ending["raw_line"], "ending.raw_line"
    if ending.get("kind") == "quote" and ending.get("text"):
        return ending["text"], "ending.text"
    return None, None


def make_judgment(section: str, text: str, card: dict, quote: str, field: str,
                  sessions: list[str], **extra) -> dict:
    item = {
        "type": "judgment",
        "section": section,
        "text": text,
        "supports": "unverified_inference",
        "evidence_check": "substring_exists",
        "evidence": {
            "session_key": card["stable_key"],
            "source": "body",
            "quote": quote,
            "card_field": field,
        },
        "sessions": sessions,
    }
    item.update(extra)
    return item


def classify_cards(cards, source_sha: str) -> dict:
    ordered = sorted(cards, key=lambda c: c["stable_key"])
    found = []
    skipped = []
    for card in ordered:
        marker = (card.get("ending") or {}).get("marker")
        quote, field = ending_evidence(card)
        if marker in OPEN_MARKERS:
            if not quote:
                skipped.append({"session_key": card["stable_key"], "section": "open_threads",
                                "reason": facts.REASON_NO_EVIDENCE})
                continue
            found.append(make_judgment(
                "open_threads",
                f"wątek otwarty: sesja `{card['stable_key']}` zakończona markerem `{marker}`",
                card, quote, field, [card["stable_key"]], marker=marker,
            ))
        elif marker == "stop_gate" and card.get("commits"):
            if not quote:
                skipped.append({"session_key": card["stable_key"], "section": "decisions",
                                "reason": facts.REASON_NO_EVIDENCE})
                continue
            found.append(make_judgment(
                "decisions",
                f"domknięcie: sesja `{card['stable_key']}` zakończona `stop_gate` "
                f"z commitami {', '.join(card['commits'][:3])}",
                card, quote, field, [card["stable_key"]], commits=list(card["commits"]),
            ))

    by_flag: dict[str, list] = {}
    for card in ordered:
        for flag in card.get("flags", []):
            by_flag.setdefault(flag, []).append(card)
    for flag in sorted(by_flag):
        group = by_flag[flag]
        open_cards = [c for c in group
                      if (c.get("ending") or {}).get("marker") in OPEN_MARKERS]
        closed_cards = [c for c in group
                        if c.get("commits")
                        and (c.get("ending") or {}).get("marker") not in OPEN_MARKERS]
        for left in open_cards:
            quote, field = ending_evidence(left)
            if not quote:
                skipped.append({"session_key": left["stable_key"], "section": "contradictions",
                                "reason": facts.REASON_NO_EVIDENCE, "flag": flag})
                continue
            for right in closed_cards:
                if right["stable_key"] == left["stable_key"]:
                    continue
                found.append(make_judgment(
                    "contradictions",
                    f"flaga `{flag}`: wątek otwarty w `{left['stable_key']}` "
                    f"(`{left['ending']['marker']}`), a `{right['stable_key']}` ma commity "
                    f"{', '.join(right['commits'][:3])}",
                    left, quote, field,
                    [left["stable_key"], right["stable_key"]], flag=flag,
                ))

    seen = set()
    unique = []
    for item in found:
        key = (item["section"], tuple(item["sessions"]), item.get("flag", ""), item["text"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    unique.sort(key=lambda i: (i["section"], tuple(i["sessions"]), i.get("flag", ""), i["text"]))
    for idx, item in enumerate(unique, 1):
        item["id"] = f"j-{idx:04d}"

    counts = Counter(item["section"] for item in unique)
    return {
        "schema_version": JUDGMENT_SCHEMA_VERSION,
        "judgment_status": "candidate",
        "promotion": None,
        "source_cards_sha256": source_sha,
        "classifier": {
            "backend": CLASSIFIER_BACKEND,
            "version": CLASSIFIER_VERSION,
            "reads": "cards_only",
            "model_calls": 0,
        },
        "judgments": unique,
        "not_checked": skipped,
        "counts": {section: counts.get(section, 0) for section in (
            "decisions", "contradictions", "open_threads", "direction_changes")},
    }


def render_judgment_md(payload: dict) -> str:
    classifier = payload["classifier"]
    lines = [
        "# Session judgment (candidate)",
        "",
        f"- **Wygenerowano**: {payload['generated_at']}",
        f"- **Run ID**: `{payload['run_id']}`",
        f"- **Schema**: `{payload['schema_version']}`",
        f"- **Status**: `{payload['judgment_status']}`",
        f"- **Classifier**: `{classifier['backend']}` v{classifier['version']} "
        f"({classifier['reads']}, {classifier['model_calls']} model calls)",
        f"- **Source cards SHA256**: `{payload['source_cards_sha256']}`",
        "- **Promotion**: none — wymaga review i osobnego commita",
        "",
    ]
    titles = (
        ("decisions", "Decyzje"),
        ("contradictions", "Sprzeczności"),
        ("open_threads", "Otwarte wątki"),
        ("direction_changes", "Zmiany kierunku"),
    )
    for section, title in titles:
        lines.append(f"## {title}")
        lines.append("")
        items = [j for j in payload["judgments"] if j["section"] == section]
        if not items:
            reason = "brak reguły w rules-v1" if section == "direction_changes" else "brak sygnału"
            lines.append(f"_brak — {reason}_")
        for item in items:
            ev = item["evidence"]
            lines.append(f"- `{item['id']}` {item['text']}")
            lines.append(f"  - evidence: `{ev['session_key']}` {ev['card_field']}: "
                         f"\"{ev['quote']}\"")
            lines.append(f"  - sessions: {', '.join(f'`{s}`' for s in item['sessions'])}")
        lines.append("")
    if payload["not_checked"]:
        lines.append("## Not checked")
        lines.append("")
        for item in payload["not_checked"]:
            lines.append(f"- `{item['session_key']}` {item['section']}: {item['reason']}")
        lines.append("")
    return "\n".join(lines)


def build_classify(args) -> int:
    out = Path(args.out_dir)
    cards_path = out / "session_cards.json"
    if not cards_path.is_file():
        print(f"CLASSIFY_NO_CARDS path={cards_path}")
        print(f"  run first: python scripts/session_digest.py --count {args.count} "
              f"--out-dir {out}")
        return 2
    cards_payload = json.loads(cards_path.read_text(encoding="utf-8"))
    cards = cards_payload.get("cards", [])
    coverage_sha = sha256_text(canonical_json(cards_descriptor(cards)))

    l0_path = out / "session_digest.json"
    digest_sha = None
    if l0_path.is_file():
        digest_sha = json.loads(l0_path.read_text(encoding="utf-8")).get("source_cards_sha256")
        if digest_sha and digest_sha != coverage_sha:
            print("CLASSIFY_STALE session_digest.json != session_cards.json; rerun mechanical digest")
            return 1

    payload = classify_cards(cards, coverage_sha)
    payload["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload["run_id"] = uuid.uuid4().hex[:12]
    if digest_sha:
        payload["source_digest_sha256"] = digest_sha

    cand_dir = out / "candidates"
    cand_dir.mkdir(parents=True, exist_ok=True)
    (cand_dir / "digest.judgment.json").write_text(
        canonical_json(payload) + "\n", encoding="utf-8", newline="\n")
    (cand_dir / "digest.judgment.md").write_text(
        render_judgment_md(payload), encoding="utf-8", newline="\n")

    counts = payload["counts"]
    print(f"CLASSIFY_WRITTEN candidates={len(payload['judgments'])} promotion=none")
    print(f"  sections decisions={counts['decisions']} "
          f"contradictions={counts['contradictions']} "
          f"open_threads={counts['open_threads']} "
          f"direction_changes={counts['direction_changes']}")
    print(f"  not_checked={len(payload['not_checked'])} coverage_sha256={coverage_sha}")
    return 0


def build(args) -> int:
    as_mod = load_agent_sessions()
    merged._AGENT_SESSIONS = as_mod
    limit = max(args.count * 3, 60)
    sessions = as_mod.get_all_sessions(args.agent, limit_per_agent=limit, days=None)
    main, children, available = select_sessions(sessions, args.count, args.days, args.until)
    if not main:
        sys.exit("Nie znaleziono sesji glownych dla podanych filtrow")

    sidecar = load_tool_calls(Path(args.tool_calls) if args.tool_calls else None)
    sidecar_data, sidecar_meta = sidecar if sidecar else (None, None)
    flags_dir = ROOT / "handoff" / "flags"

    bodies: dict[str, str] = {}
    cards = []
    ordered = list(main)
    child_map: dict[str, list[str]] = {}
    for child in children:
        child_map.setdefault(child.parent, []).append(stable_key(child))

    for idx, s in enumerate(ordered, 1):
        body = as_mod.render_session_body(s, include_reasoning=False).strip()
        if not body:
            body = ""
        bodies[stable_key(s)] = body
        card = card_from_actions(s, body, sidecar_data, sidecar_meta, flags_dir)
        card["ses_n"] = idx
        if s.id in child_map:
            card["child_session_ids"] = sorted(child_map[s.id])
        card["card_sha256"] = card_hash(card)
        cards.append(card)

    descriptor = cards_descriptor(cards)
    coverage_sha = sha256_text(canonical_json(descriptor))

    baseline, baseline_sha = baseline_cards(Path(args.baseline) if args.baseline else None)
    new_sessions = []
    if baseline:
        for card in sorted(cards, key=lambda c: c["stable_key"]):
            if card["stable_key"] not in baseline:
                new_sessions.append({"stable_key": card["stable_key"], "date": card["date"]})

    delta = mechanical_delta(cards, baseline)
    for item in delta:
        quote = item["value"]
        ev = evidence(bodies.get(item["session_key"], ""), quote, item["session_key"])
        if ev:
            item["evidence"] = ev
        else:
            item["evidence_check"] = "not_checked"
            item["not_checked"] = facts.REASON_NO_EVIDENCE

    dates_from = [c["date"] for c in cards if c["date"]]
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_id = uuid.uuid4().hex[:12]
    n_semantics = f"count={args.count}" if args.days is None else f"days={args.days};count={args.count}"
    if args.until:
        n_semantics += f";until={args.until}"

    cards_payload = {
        "schema_version": facts.CARD_SCHEMA_VERSION,
        "generated_at": generated_at,
        "run_id": run_id,
        "normalizer_version": facts.NORMALIZER_VERSION,
        "count_requested": args.count,
        "count_main": len(main),
        "count_children": len(children),
        "n_semantics": n_semantics,
        "cards": cards,
    }
    l0_payload = {
        "schema_version": facts.CARD_SCHEMA_VERSION,
        "generated_at": generated_at,
        "run_id": run_id,
        "normalizer_version": facts.NORMALIZER_VERSION,
        "judgment": [],
        "judgment_status": "not_run",
        "validity_basis": "coverage",
        "source_cards_sha256": coverage_sha,
        "coverage_descriptor": descriptor,
        "coverage": {
            "count_main": len(main),
            "count_children": len(children),
            "date_from": min(dates_from) if dates_from else "",
            "date_to": max(dates_from) if dates_from else "",
            "n_semantics": n_semantics,
        },
        "baseline": {
            "mode": "digest" if args.baseline else "none",
            "path": args.baseline or "",
            "source_cards_sha256": baseline_sha or "",
        },
        "new_sessions_since": new_sessions,
        "mechanical_delta": delta,
        "not_checked": [
            {"field": "losses.dup", "reason": facts.REASON_NOT_EXTRACTED},
        ],
    }

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "session_cards.json").write_text(canonical_json(cards_payload) + "\n", encoding="utf-8", newline="\n")
    (out / "session_cards.md").write_text(render_cards_md(cards_payload, coverage_sha), encoding="utf-8", newline="\n")
    (out / "session_digest.json").write_text(canonical_json(l0_payload) + "\n", encoding="utf-8", newline="\n")
    (out / "session_digest.md").write_text(render_l0_md(l0_payload, cards_payload), encoding="utf-8", newline="\n")

    l0_size = (out / "session_digest.md").stat().st_size
    l1_size = (out / "session_cards.json").stat().st_size
    status = "OK" if l0_size <= L0_BUDGET and l1_size <= L1_BUDGET else "OVER"
    print(f"DIGEST_WRITTEN cards={len(main)} l0=session_digest.md cards_json=session_cards.json")
    print(f"COVERAGE main={len(main)} children={len(children)} total_cards={len(cards)} sha256={coverage_sha}")
    print(f"BUDGET l0={l0_size}/{L0_BUDGET} l1={l1_size}/{L1_BUDGET} status={status}")
    return 0 if status == "OK" else 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Mechanical session digest (L0/L1)")
    parser.add_argument("count_pos", nargs="?", type=int, help="number of main sessions")
    parser.add_argument("--count", type=int, default=None, help="number of main sessions")
    parser.add_argument("--agent", default="all", help="agent filter")
    parser.add_argument("--days", type=int, default=None, help="alternative window in days")
    parser.add_argument("--until", default=None, help="freeze window: YYYY-MM-DD HH:MM:SS")
    parser.add_argument("--out-dir", default=str(OUTDIR / "session-digest"))
    parser.add_argument("--tool-calls", default=str(TOOL_CALLS))
    parser.add_argument("--no-tool-calls", action="store_true")
    parser.add_argument("--baseline", default=None)
    parser.add_argument("--classify", action="store_true",
                        help="card-only judgment candidate pass; never promotes")
    args = parser.parse_args(argv)
    if args.count is None:
        args.count = args.count_pos if args.count_pos is not None else 100
    if args.no_tool_calls:
        args.tool_calls = ""
    if args.classify:
        return build_classify(args)
    return build(args)


if __name__ == "__main__":
    raise SystemExit(main())
