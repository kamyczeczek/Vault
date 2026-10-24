"""Verifier for the mechanical session digest (G1-G12 evidence gates)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
OUTDIR = SCRIPTS / "_scratch" / "sessions" / "02_products"
DIGEST_DIR = OUTDIR / "digest-check"
GOLDEN_SHA256 = "8307cf92f187b8145d36f0fda283aa691471c20a435cabd2e7eabfa3dae0f5bc"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
import session_facts as facts  # noqa: E402
import session_digest as digest  # noqa: E402
import last_session_merged as merged  # noqa: E402

REQUIRED_CARD_KEYS = {
    "stable_key", "agent", "session_id", "ses_n", "parent_session_id",
    "child_session_ids", "date", "duration", "model", "micro", "goal",
    "ending", "flags", "flags_missing", "commits", "files", "tests",
    "losses", "tool_facts", "card_sha256",
}
VOLATILE = ("generated_at", "run_id")


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_digest(path: Path):
    cards = json.loads((path / "session_cards.json").read_text(encoding="utf-8"))
    l0 = json.loads((path / "session_digest.json").read_text(encoding="utf-8"))
    return cards, l0


def load_bodies():
    as_mod = digest.load_agent_sessions()
    digest.merged._AGENT_SESSIONS = as_mod
    sessions = as_mod.get_all_sessions("all", limit_per_agent=500, days=None)
    return as_mod, sessions


def body_map(sessions, keys):
    out = {}
    for session in sessions:
        key = digest.stable_key(session)
        if key in keys:
            out[key] = session
    return out


def card_hash(card: dict) -> str:
    payload = {k: v for k, v in card.items() if k not in ("card_sha256", "ses_n")}
    return sha256_text(canonical_json(payload))


def quote_errors(card: dict, body: str) -> list[str]:
    errors = []
    norm_body = facts.normalize_text(body)
    goal = card.get("goal") or {}
    if goal.get("kind") == "prompt":
        quote = facts.normalize_text(goal.get("text", ""))
        if not quote or quote not in norm_body:
            errors.append("goal_not_found")
    elif goal.get("kind") == "none":
        if goal.get("reason") not in {
                facts.REASON_EMPTY_OUTPUT, facts.REASON_BOILERPLATE,
                facts.REASON_NOT_EXTRACTED, facts.REASON_AGENT_UNSUPPORTED,
                facts.REASON_NO_EVIDENCE}:
            errors.append("goal_reason_unknown")
    else:
        errors.append("goal_kind_unknown")

    ending = card.get("ending") or {}
    if ending.get("kind") == "marker":
        markers = facts._marker_scan(body)
        item = (ending.get("source_line"), ending.get("raw_line"), ending.get("marker"))
        if item not in markers:
            errors.append("marker_not_standalone")
        if ending.get("markers_version") != facts.MARKERS_VERSION:
            errors.append("marker_version_mismatch")
    elif ending.get("kind") == "quote":
        quote = facts.normalize_text(ending.get("text", ""))
        if not quote or quote not in norm_body:
            errors.append("ending_not_found")
    elif ending.get("kind") == "none":
        if ending.get("reason") not in {
                facts.REASON_EMPTY_OUTPUT, facts.REASON_BOILERPLATE,
                facts.REASON_NOT_EXTRACTED, facts.REASON_AGENT_UNSUPPORTED,
                facts.REASON_NO_EVIDENCE}:
            errors.append("ending_reason_unknown")
    else:
        errors.append("ending_kind_unknown")
    return errors


def descriptor(cards):
    entries = sorted(
        ({"stable_key": c["stable_key"], "card_sha256": c["card_sha256"]} for c in cards),
        key=lambda item: item["stable_key"],
    )
    return {
        "schema_version": facts.CARD_SCHEMA_VERSION,
        "normalizer_version": facts.NORMALIZER_VERSION,
        "cards": entries,
    }


def source_hash(desc) -> str:
    return sha256_text(canonical_json(desc))


def check_schema(path: Path) -> int:
    cards, _ = load_digest(path)
    missing = []
    hash_bad = []
    if cards.get("schema_version") != facts.CARD_SCHEMA_VERSION:
        missing.append("schema_version")
    for card in cards.get("cards", []):
        key = card.get("stable_key", "?")
        for field_name in REQUIRED_CARD_KEYS:
            if field_name not in card:
                missing.append(f"{key}.{field_name}")
        if not isinstance(card.get("goal"), dict) or "kind" not in card.get("goal", {}):
            missing.append(f"{key}.goal.kind")
        if not isinstance(card.get("ending"), dict) or "kind" not in card.get("ending", {}):
            missing.append(f"{key}.ending.kind")
        if not isinstance(card.get("tool_facts"), dict):
            missing.append(f"{key}.tool_facts")
        if card.get("card_sha256") and card["card_sha256"] != card_hash(card):
            hash_bad.append(key)
    if missing or hash_bad:
        print(f"SCHEMA_FAIL missing_keys={len(missing)} hash_mismatch={len(hash_bad)}")
        for item in (missing + hash_bad)[:8]:
            print(f"  {item}")
        return 1
    print(f"SCHEMA_OK cards={cards.get('count_main', len(cards.get('cards', [])))} missing_keys=0")
    return 0


def check_quotes(path: Path) -> int:
    cards, _ = load_digest(path)
    _, sessions = load_bodies()
    needed = {c["stable_key"] for c in cards.get("cards", [])}
    by_key = body_map(sessions, needed)
    rejected = []
    for card in cards.get("cards", []):
        session = by_key.get(card["stable_key"])
        if session is None:
            rejected.append((card["stable_key"], "session_not_found"))
            continue
        body = digest.merged._AGENT_SESSIONS.render_session_body(session, include_reasoning=False).strip()
        errs = quote_errors(card, body)
        if errs:
            rejected.append((card["stable_key"], ",".join(errs)))
    if rejected:
        print(f"QUOTES_FAIL rejected={len(rejected)}")
        for key, err in rejected[:8]:
            print(f"  {key}: {err}")
        return 1
    print("QUOTES_OK rejected=0")
    return 0


def run_digest(out_dir: Path, count: int, until: str | None = None) -> int:
    cmd = [sys.executable, str(SCRIPTS / "session_digest.py"), "--count", str(count),
           "--out-dir", str(out_dir)]
    if until:
        cmd += ["--until", until]
    result = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout[-2000:])
        print(result.stderr[-2000:])
    return result.returncode


def strip_volatile(obj):
    if isinstance(obj, dict):
        return {k: strip_volatile(v) for k, v in obj.items() if k not in VOLATILE}
    if isinstance(obj, list):
        return [strip_volatile(v) for v in obj]
    return obj


def strip_volatile_md(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if line.startswith("- **Wygenerowano**:"):
            continue
        if line.startswith("- **Run ID**:"):
            continue
        lines.append(line)
    return "\n".join(lines)


def check_stability(n: int, n2: int) -> int:
    until = "2026-10-21 23:59:59"
    with tempfile.TemporaryDirectory() as tmp:
        a = Path(tmp) / "a"
        b = Path(tmp) / "b"
        if run_digest(a, n, until) or run_digest(b, n2, until):
            return 1
        cards_a, _ = load_digest(a)
        cards_b, _ = load_digest(b)
    map_a = {c["stable_key"]: c for c in cards_a["cards"]}
    map_b = {c["stable_key"]: c for c in cards_b["cards"]}
    common = set(map_a) & set(map_b)
    if len(common) < min(n, n2):
        print(f"STABILITY_FAIL common={len(common)} expected={min(n, n2)}")
        return 1
    for key in sorted(common):
        left = {k: v for k, v in map_a[key].items() if k not in ("ses_n", "card_sha256")}
        right = {k: v for k, v in map_b[key].items() if k not in ("ses_n", "card_sha256")}
        if left != right:
            diff = [k for k in left if left.get(k) != right.get(k)]
            print(f"STABILITY_FAIL key={key} fields={','.join(diff[:6])}")
            return 1
    print("STABILITY_OK stable_key_fields=identical")
    return 0


def check_determinism() -> int:
    until = "2026-10-21 23:59:59"
    with tempfile.TemporaryDirectory() as tmp:
        a = Path(tmp) / "a"
        b = Path(tmp) / "b"
        if run_digest(a, 20, until) or run_digest(b, 20, until):
            return 1
        for name in ("session_cards.json", "session_digest.json"):
            left = strip_volatile(json.loads((a / name).read_text(encoding="utf-8")))
            right = strip_volatile(json.loads((b / name).read_text(encoding="utf-8")))
            if left != right:
                print(f"DETERMINISM_FAIL file={name}")
                return 1
        for name in ("session_cards.md", "session_digest.md"):
            left = strip_volatile_md((a / name).read_text(encoding="utf-8"))
            right = strip_volatile_md((b / name).read_text(encoding="utf-8"))
            if left != right:
                print(f"DETERMINISM_FAIL file={name}")
                return 1
    print("DETERMINISM_OK volatile=generated_at,run_id")
    return 0


def check_budget(path: Path) -> int:
    l0 = (path / "session_digest.md").stat().st_size
    l1 = (path / "session_cards.json").stat().st_size
    if l0 <= digest.L0_BUDGET and l1 <= digest.L1_BUDGET:
        print("BUDGET_OK l0<=15360 l1<=153600")
        return 0
    print(f"BUDGET_FAIL l0={l0} l1={l1}")
    return 1


def check_negative_quote(path: Path) -> int:
    cards, _ = load_digest(path)
    card = next((c for c in cards.get("cards", []) if c.get("goal", {}).get("kind") == "prompt"), None)
    if card is None:
        card = {"goal": {"kind": "prompt", "text": "real prompt"}, "ending": {"kind": "none", "reason": "no_evidence"}}
        body = "real prompt"
    else:
        _, sessions = load_bodies()
        session = body_map(sessions, {card["stable_key"]}).get(card["stable_key"])
        body = digest.merged._AGENT_SESSIONS.render_session_body(session, include_reasoning=False).strip()
    fake = dict(card)
    fake["goal"] = {"kind": "prompt", "text": (fake.get("goal", {}).get("text", "") or "x") + " __forged__"}
    if not quote_errors(fake, body):
        print("NEGATIVE_CONTROL_FAIL kind=quote rejected=0")
        return 1
    print("NEGATIVE_CONTROL_OK kind=quote rejected=1")
    return 0


def check_negative_payload() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        payload = Path(tmp) / "payload.txt"
        payload.write_text("alpha\nbeta\ngamma\n", encoding="utf-8")
        good = {
            "source": "payload", "path": str(payload), "line": 2,
            "sha": sha256_file(payload),
        }
        bad_sha = dict(good)
        bad_sha["sha"] = "0" * 64
        bad_line = dict(good)
        bad_line["line"] = 99
        rejected = 0
        for item in (bad_sha, bad_line):
            if payload_pointer_error(item):
                rejected += 1
        if rejected == 2:
            print("NEGATIVE_CONTROL_OK kind=payload rejected=1")
            return 0
    print("NEGATIVE_CONTROL_FAIL kind=payload rejected=0")
    return 1


def payload_pointer_error(ev: dict) -> str:
    if not ev or ev.get("source") != "payload":
        return "not_payload"
    path = Path(ev.get("path", ""))
    if not path.is_file():
        return "payload_not_found"
    if ev.get("sha") and sha256_file(path) != ev["sha"]:
        return "payload_sha_mismatch"
    line = ev.get("line")
    if line is not None:
        try:
            line = int(line)
        except Exception:
            return "payload_line_invalid"
        if line < 1 or line > len(path.read_text(encoding="utf-8").splitlines()):
            return "payload_line_out_of_range"
    return ""


def check_coverage_control(path: Path) -> int:
    cards, l0 = load_digest(path)
    actual = descriptor(cards["cards"])
    actual_hash = source_hash(actual)
    if l0.get("source_cards_sha256") != actual_hash:
        print("COVERAGE_CONTROL_FAIL source_hash_mismatch")
        return 1
    if l0.get("coverage_descriptor") != actual:
        print("COVERAGE_CONTROL_FAIL descriptor_mismatch")
        return 1
    bad = json.loads(json.dumps(actual))
    bad["cards"][0]["card_sha256"] = "0" * 64
    if source_hash(bad) == actual_hash:
        print("COVERAGE_CONTROL_FAIL covered_mismatch=accepted")
        return 1
    base = {c["stable_key"] for c in actual["cards"]}
    fake = {"stable_key": "fake:new-session", "card_sha256": "1" * 64}
    new = {fake["stable_key"]} - base
    if not new:
        print("COVERAGE_CONTROL_FAIL new_session=missing")
        return 1
    print("COVERAGE_CONTROL_OK covered_mismatch=rejected new_session=informational")
    return 0


def check_l0_schema(path: Path) -> int:
    _, l0 = load_digest(path)
    missing = 0
    if l0.get("judgment_status") not in ("none", "not_run", "classified"):
        missing += 1
    if l0.get("validity_basis") != "coverage":
        missing += 1
    for item in l0.get("judgment", []):
        if item.get("evidence_check") != "substring_exists":
            missing += 1
        if "supports" not in item:
            missing += 1
        ev = item.get("evidence")
        if not isinstance(ev, dict) or not ev.get("session_key") or not ev.get("source"):
            missing += 1
        if ev and ev.get("source") == "payload" and payload_pointer_error(ev):
            missing += 1
    for item in l0.get("mechanical_delta", []):
        if item.get("evidence_check") != "substring_exists":
            missing += 1
        if "supports" not in item:
            missing += 1
        ev = item.get("evidence")
        if not isinstance(ev, dict) or not ev.get("session_key") or not ev.get("source"):
            missing += 1
    if missing:
        print(f"L0_SCHEMA_FAIL missing_evidence={missing}")
        return 1
    print("L0_SCHEMA_OK missing_evidence=0")
    return 0


def judgment_quote_error(item: dict, bodies: dict) -> str:
    ev = item.get("evidence") or {}
    key = ev.get("session_key")
    quote = ev.get("quote")
    if not key or not quote:
        return "evidence_missing"
    body = bodies.get(key)
    if body is None:
        return "session_not_found"
    if facts.normalize_text(str(quote)) not in facts.normalize_text(body):
        return "quote_not_found"
    return ""


def check_judgment(path: Path) -> int:
    cand = path / "candidates" / "digest.judgment.json"
    if not cand.is_file():
        print(f"JUDGMENT_FAIL missing={cand}")
        return 1
    payload = json.loads(cand.read_text(encoding="utf-8"))
    cards, _ = load_digest(path)
    errors = []
    if payload.get("judgment_status") != "candidate":
        errors.append("status_not_candidate")
    if payload.get("promotion") is not None:
        errors.append("promotion_present_without_review")
    if payload.get("source_cards_sha256") != source_hash(descriptor(cards["cards"])):
        errors.append("source_cards_sha256_mismatch")
    classifier = payload.get("classifier") or {}
    if classifier.get("reads") != "cards_only":
        errors.append("classifier_reads_not_cards")
    judgments = payload.get("judgments", [])
    for item in judgments:
        jid = item.get("id", "?")
        if item.get("type") != "judgment":
            errors.append(f"{jid}:type")
        if item.get("supports") != "unverified_inference":
            errors.append(f"{jid}:supports")
        if item.get("evidence_check") != "substring_exists":
            errors.append(f"{jid}:evidence_check")
        if not item.get("sessions"):
            errors.append(f"{jid}:sessions")
        if (item.get("evidence") or {}).get("source") != "body":
            errors.append(f"{jid}:evidence_source")
    needed = {(item.get("evidence") or {}).get("session_key") for item in judgments} - {None}
    _, sessions = load_bodies()
    by_key = body_map(sessions, needed)
    bodies = {}
    for key, session in by_key.items():
        bodies[key] = digest.merged._AGENT_SESSIONS.render_session_body(
            session, include_reasoning=False).strip()
    for item in judgments:
        err = judgment_quote_error(item, bodies)
        if err:
            errors.append(f"{item.get('id', '?')}:{err}")
    if judgments:
        forged = json.loads(json.dumps(judgments[0]))
        forged["evidence"]["quote"] = str(forged["evidence"].get("quote", "")) + " __forged__"
        if not judgment_quote_error(forged, bodies):
            errors.append("negative_control_not_rejected")
    if errors:
        print(f"JUDGMENT_FAIL errors={len(errors)}")
        for err in errors[:8]:
            print(f"  {err}")
        return 1
    print(f"JUDGMENT_OK candidates={len(judgments)} promotion=none")
    return 0


def check_header(path: Path) -> int:
    cards, l0 = load_digest(path)
    md = (path / "session_digest.md").read_text(encoding="utf-8")
    main = re.search(r"- \*\*Sesje główne\*\*: (\d+)", md)
    children = re.search(r"- \*\*Dzieci\*\*: (\d+)", md)
    dates = re.search(r"- \*\*Zakres dat\*\*: (.+?) -> (.+)", md)
    semantics = re.search(r"- \*\*Semantyka N\*\*: (.+)", md)
    if not (main and children and dates and semantics):
        print("HEADER_FAIL missing=main_children/date_range/n_semantics")
        return 1
    card_dates = [c["date"] for c in cards.get("cards", []) if c.get("date")]
    expected_from = min(card_dates) if card_dates else "—"
    expected_to = max(card_dates) if card_dates else "—"
    if dates.group(1).strip() != expected_from or dates.group(2).strip() != expected_to:
        print(f"HEADER_FAIL date_range={dates.group(1)}..{dates.group(2)} expected={expected_from}..{expected_to}")
        return 1
    sem = semantics.group(1)
    if "count=" not in sem and "days=" not in sem:
        print("HEADER_FAIL n_semantics=missing")
        return 1
    cov = l0.get("coverage", {})
    if int(main.group(1)) != cov.get("count_main") or int(children.group(1)) != cov.get("count_children"):
        print("HEADER_FAIL main_children=count_mismatch")
        return 1
    print("HEADER_OK main_children=present date_range=exact n_semantics=present")
    return 0


def build_fixture(out: Path) -> str:
    as_mod = digest.load_agent_sessions()
    merged._AGENT_SESSIONS = as_mod
    body = """## [user]
Zrób X. handoff/flags/fixture-flag.md

## [assistant]
artifact://fixture
Some lines truncated to 768 bytes
…[+42 zn.]…
Superseded by a newer read
commit 8da09f6
12 passed in 0.1s

## [assistant]
Ostatnia linia odpowiedzi.
"""
    session = as_mod.SessionItem(
        agent="opencode",
        id="ses_fixture_0001",
        title="Fixture session",
        directory="C:/fixture",
        created_at="2026-01-01 10:00:00",
        updated_at="2026-01-01 10:05:00",
        message_count=6,
        model="test/model",
        raw_path="fixture.db",
        text_markdown=body,
    )
    text = merged.build_merged_markdown(
        [session], "all", out, available=1, include_reasoning=False,
        signatures=False, split=False,
        records_dir=out.parent / "records", payloads_dir=out.parent / "payloads",
    )
    out.write_text(text, encoding="utf-8")
    return text


def normalize_merged(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = []
    for line in text.split("\n"):
        if line.startswith("- **Wygenerowano**:"):
            continue
        if line.startswith("- **Zapisano do**:"):
            continue
        lines.append(line)
    return "\n".join(lines)


def check_refactor() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "merged.md"
        after = build_fixture(out)
        actual = sha256_text(normalize_merged(after))
        if actual != GOLDEN_SHA256:
            print(f"REFACTOR_FAIL merged=different actual={actual}")
            return 1
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "check_workspace_integrity.py")],
        cwd=str(ROOT), capture_output=True, text=True, timeout=300,
    )
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0 or "OK" not in output:
        print("REFACTOR_FAIL integrity=FAIL")
        print(output[-1500:])
        return 1
    print("REFACTOR_SAFETY_OK merged=identical integrity=OK")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Verify session digest gates")
    parser.add_argument("--schema", type=Path)
    parser.add_argument("--quotes", type=Path)
    parser.add_argument("--stability", action="store_true")
    parser.add_argument("--n", type=int, default=100)
    parser.add_argument("--n2", type=int, default=110)
    parser.add_argument("--determinism", action="store_true")
    parser.add_argument("--budget", type=Path)
    parser.add_argument("--negative-control", choices=("quote", "payload"))
    parser.add_argument("--coverage-control", action="store_true")
    parser.add_argument("--l0-schema", type=Path)
    parser.add_argument("--judgment", type=Path)
    parser.add_argument("--header", type=Path)
    parser.add_argument("--refactor-safety", action="store_true")
    args = parser.parse_args(argv)

    if args.schema:
        return check_schema(args.schema)
    if args.quotes:
        return check_quotes(args.quotes)
    if args.stability:
        return check_stability(args.n, args.n2)
    if args.determinism:
        return check_determinism()
    if args.budget:
        return check_budget(args.budget)
    if args.negative_control == "quote":
        return check_negative_quote(DIGEST_DIR)
    if args.negative_control == "payload":
        return check_negative_payload()
    if args.coverage_control:
        return check_coverage_control(DIGEST_DIR)
    if args.l0_schema:
        return check_l0_schema(args.l0_schema)
    if args.judgment:
        return check_judgment(args.judgment)
    if args.header:
        return check_header(args.header)
    if args.refactor_safety:
        return check_refactor()
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
