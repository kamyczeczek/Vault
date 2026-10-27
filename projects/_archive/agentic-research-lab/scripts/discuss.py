#!/usr/bin/env python3
"""discuss.py — "chat with an expert" as a file convention, not a session API.

The file IS the conversation, the state, the transcript, and the artifact.
There is no session id, no slug to thread, and no hidden state: the human
opens a markdown file in INBOX/ideas/, argues in it, and the agent edits
that same file in place. This follows 01_plain_text_as_interface — "the
filesystem IS the state management system" — and inverts the old
idea_session.py state machine, which hid the thinking behind a timestamped
slug and a 6-step CLI.

Three ideas drive the design:

1. FILE = STATE. `new` writes a file. Every other subcommand takes a path
   (or defaults to the single most recently modified idea file). Nothing is
   remembered between invocations except the file on disk.

2. STANCE PER TURN. Red-teaming is an EXPERT, not a retrieval query. The
   old workflow asked BM25 for "failure modes limitations counterargument"
   and got topically adjacent chunks, which it then silently dropped
   (idea_session.py:147) while the board printed "counter: EMPTY" — the
   agent was told no counter-evidence existed when three had been found.
   Here the human picks who speaks next, and the expert says so in prose:
   the librarian can honestly report "the corpus is silent on this" without
   that being a broken query. The red-teamer must cite a real refuting
   chunk or concede the claim is unrefuted.

3. OUTCOME IS A DECISION, NOT A RULE. A discussion may end `learned`
   (a node, no rule), `wrong` (a kill/scar), or `unresolved` (a named
   experiment). Only `unresolved` may stage a proposed candidate. The old
   pipeline could only ever emit one shape — a proposed rule — which is
   what pressured every session toward manufacturing a Rule it never earned.

File format (frontmatter + markdown, human-editable at all times):

    ---
    id: <slug>
    thesis: <one line>
    stance: synth            # who speaks next
    status: open             # open | learned | wrong | unresolved
    ---
    # <thesis>

    ## c1 — <claim text>
    - support: `chunk_a`, `chunk_b`
    - counter: `chunk_c`           (or: counter: (none — unrefuted))
    - note: <expert's prose>

    ## red-team — 2026-09-28
    <prose attack, or a concession>

    ## decision
    - value: unresolved
    - why: <reason>
    - next: <named experiment>

Subcommands
  new "<thesis>"            create INBOX/ideas/<slug>.md
  open [PATH]               print the board (defaults to latest idea)
  stance <name>             set who speaks next
  claim "<text>"            add a claim; runs two-sided retrieval
  annotate --claim cN       attach expert prose to a claim
  attack "<text>"           record a red-team turn (must exist in a file)
  concede "<text>"          record an honest non-refutation
  decide <learned|wrong|unresolved> "<why>" [--next TEXT]
  stage --rule R --target T seal the file, verify chain, write candidate
  close                     verify + seal without staging (aborted)

The human only ever reads the file. `stage` is the only command that
writes outside INBOX/ideas/, and it refuses unless the decision is
`unresolved` with a named next experiment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDEAS = ROOT / "INBOX" / "ideas"
CANDIDATES = ROOT / "reflection" / "candidates"

if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
if str(ROOT / "knowledge" / "graph") not in sys.path:
    sys.path.insert(0, str(ROOT / "knowledge" / "graph"))

from session_store import (  # noqa: E402
    append_event,
    finish_session,
    start_session,
    verify_chain,
)
import agent_trace  # noqa: E402

RETRIEVAL_LIMIT = 3
STANCES = ("red-teamer", "methodologist", "librarian", "synth")
DECISIONS = ("learned", "wrong", "unresolved")

# Graph must exist before "the corpus is silent" can be claimed. ask.query
# returns [] both when the corpus genuinely has nothing AND when graph.db
# is missing — conflating them would let a broken index masquerade as a
# red-team concession, which is precisely the kind of unverifiable
# self-critique 00_07_critic_external_tool_verification warns about.
GRAPH_DB = ROOT / "knowledge" / "graph" / "graph.db"


class DiscussError(RuntimeError):
    """A guard refused. The file is never half-written on these."""


# ------------------------------------------------------------------ parsing


def _slug(text: str) -> str:
    words = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    words = re.sub(r"-{2,}", "-", words)
    return words[:40].rstrip("-") or "idea"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _reject_stray_path(args: argparse.Namespace) -> None:
    """Refuse when a filename was passed as the last word of free text.

    `-p FILE.md` is the only way to target a file. The previous
    `attack "text" FILE.md` form was accepted by argparse, buried the filename
    in the recorded prose, and applied the edit to the most recent idea file
    while reporting success. Silently editing the wrong file in a
    file-is-the-state workflow loses the note permanently.
    """
    if args.path is not None:
        return
    text = getattr(args, "text", None) or getattr(args, "why", None) or []
    tail = text[-1] if text else ""
    if tail.lower().endswith(".md"):
        raise DiscussError(
            f"'{tail}' looks like a file, not prose. Target files with "
            f"-p/--path FILE.md; this command would otherwise edit the most "
            f"recent idea file and lose this note.")


def _resolve(path_arg: str | None) -> Path:
    """A path, or the most recently modified idea file. The file is the
    session: an agent should never have to remember a slug."""
    if path_arg:
        p = Path(path_arg)
        if not p.is_absolute():
            p = ROOT / p
        if not p.exists():
            raise DiscussError(f"no such idea file: {p}")
        return p
    if not IDEAS.exists():
        raise DiscussError(f"no ideas yet — run `new \"<thesis>\"` (dir: {IDEAS})")
    files = sorted(IDEAS.glob("*.md"), key=lambda f: f.stat().st_mtime)
    if not files:
        raise DiscussError(f"no idea files in {IDEAS} — run `new` first")
    return files[-1]


def _parse(path: Path) -> dict:
    """Frontmatter + body. The human may edit any of this at any time."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise DiscussError(f"{path.name}: missing YAML frontmatter")
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    fm.setdefault("id", path.stem)
    fm.setdefault("stance", "synth")
    fm.setdefault("status", "open")
    return {
        "fm": fm,
        "body": m.group(2),
        "claims": _parse_claims(m.group(2)),
        "decision": _parse_decision(m.group(2)),
        "attacks": _parse_section(m.group(2), "red-team"),
        "text": text,
    }


def _parse_claims(body: str) -> list[dict]:
    claims = []
    for m in re.finditer(
        r"^## (c\d+)\s+—\s+(.*?)\n((?:^- .*\n|  .*\n)*)", body, re.M
    ):
        cid, text, block = m.group(1), m.group(2).strip(), m.group(3)
        support = _ids_in(block, "support")
        counter = _ids_in(block, "counter")
        claim = {"id": cid, "text": text, "support": support, "counter": counter,
                 "note": _note_in(block)}
        # The old board printed "EMPTY" whenever counter was dropped. Here an
        # absent counter is an explicit, quotable concession — and the
        # difference between "retrieved nothing" and "not yet attacked" is
        # recorded rather than conflated.
        claim["counter_empty"] = not counter
        claims.append(claim)
    return claims


def _ids_in(block: str, key: str) -> list[str]:
    m = re.search(rf"^- {key}:\s*(.*)$", block, re.M)
    if not m:
        return []
    raw = m.group(1)
    if "(none" in raw or raw.strip() in ("", "-"):
        return []
    return re.findall(r"`([^`]+)`", raw)


def _note_in(block: str) -> str | None:
    m = re.search(r"^- note:\s*(.+)$", block, re.M)
    return m.group(1).strip() if m else None


def _parse_section(body: str, name: str) -> list[str]:
    m = re.search(rf"^## {re.escape(name)}\b(.*?)(?=^## |\Z)", body, re.M | re.S)
    if not m:
        return []
    return [ln.strip() for ln in m.group(1).splitlines() if ln.strip()]


def _decision_block(body: str) -> re.Match | None:
    """Match ONLY the machine-readable `## decision` block.

    The heading must be bare. Observed live: this used `^## decision\b`, and
    because `\b` matches between "decision" and the following space the same
    pattern also matched `## decision rationale` -- so a `decide --force` meant
    to update one field deleted 73 lines of recorded reasoning along with the
    old decision. The file is the only state, so that was unrecoverable
    without a `git revert`.
    """
    return re.search(r"^## decision[ \t]*$\n(.*?)(?=^## |\Z)", body,
                     re.M | re.S)


def _replace_decision(body: str, block: str) -> str:
    """Swap the bare `## decision` block for `block`, in place.

    In place, not strip-and-append: the machine block has to stay directly above
    `## decision rationale` so a forced rewrite changes three lines instead of
    relocating half the record. Any duplicate bare blocks are removed.
    """
    # Drop EVERY bare block, not just the first: a hand-edited file can hold
    # two, and leaving the second would keep a contradictory decision in the
    # file while the parser reports the new one.
    spans = [m.span() for m in re.finditer(
        r"^## decision[ \t]*$\n.*?(?=^## |\Z)", body, re.M | re.S)]
    if spans:
        keep, prev = [], 0
        for start, end in spans:
            keep.append(body[prev:start])
            prev = end
        keep.append(body[prev:])
        body = "".join(keep).rstrip()
        body += "\n\n" + block.rstrip() + "\n"
    else:
        body = body.rstrip() + "\n\n" + block.rstrip() + "\n"
    return body


def _parse_decision(body: str) -> dict | None:
    sec = _decision_block(body)
    if not sec:
        return None
    d: dict[str, str] = {}
    for key in ("value", "why", "next"):
        m = re.search(rf"^- {key}:\s*(.*)$", sec.group(1), re.M)
        d[key] = m.group(1).strip() if m else None
    return d if d.get("value") else None


def _render(fm: dict, body: str) -> str:
    order = ["id", "thesis", "stance", "status"]
    lines = ["---"]
    for k in order:
        if fm.get(k):
            lines.append(f"{k}: {fm[k]}")
    for k in sorted(set(fm) - set(order)):
        if fm[k]:
            lines.append(f"{k}: {fm[k]}")
    lines.append("---")
    return "\n".join(lines) + "\n" + body


def _write(path: Path, fm: dict, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render(fm, body), encoding="utf-8")


# ---------------------------------------------------------------- retrieval


def _graph_available() -> bool:
    return GRAPH_DB.exists()


def _retrieve(fm: dict, query: str, side: str, claim_id: str) -> list[str]:
    """One retrieval with a typed trace event. Returns [] only if the
    graph is genuinely reachable and has nothing, or raises if the graph
    is missing — an unreachable index is not an empty corpus."""
    from ask import query as graph_query  # imported late: tests patch this

    if not _graph_available():
        raise DiscussError(
            f"graph.db missing at {GRAPH_DB} — build it before discussing. "
            "An unreachable index must not be reported as 'corpus silent'."
        )
    try:
        rows = graph_query(query, limit=RETRIEVAL_LIMIT)
    except Exception as e:  # noqa: BLE001 — surface, never paper over
        agent_trace.emit("retrieval", run_id=fm.get("run_id", ""),
                         query=query[:200], status="failed", error=str(e))
        raise DiscussError(f"retrieval failed: {e}") from e
    ids = [r["id"] for r in rows]
    agent_trace.emit("retrieval", run_id=fm.get("run_id", ""),
                     query=query[:200], side=side, claim_id=claim_id,
                     chunk_ids=ids, status="ok" if ids else "empty")
    return ids


def _claim_block(claim: dict) -> str:
    def fmt(ids: list[str]) -> str:
        return ", ".join(f"`{i}`" for i in ids) if ids else "(none — unrefuted)"

    lines = [f"## {claim['id']} — {claim['text']}",
             f"- support: {fmt(claim['support'])}",
             f"- counter: {fmt(claim['counter'])}"]
    if claim.get("note"):
        lines.append(f"- note: {claim['note']}")
    lines.append("")
    return "\n".join(lines)


def _upsert_claim(body: str, claim: dict) -> str:
    """Replace this claim's block in place, or append it. Idempotent so a
    human can reorder or hand-edit freely without breaking the parser."""
    block = _claim_block(claim)
    pat = re.compile(rf"^## {re.escape(claim['id'])}\b.*?(?=^## |\Z)", re.M | re.S)
    if pat.search(body):
        return pat.sub(block + "\n", body)
    return body.rstrip() + "\n\n" + block


def _section(body: str, name: str) -> str:
    return f"## {name}\n"


def _append_section(body: str, name: str, text: str) -> str:
    entry = f"### {_now()}\n" + text.rstrip() + "\n"
    if re.search(rf"^## {re.escape(name)}\b", body, re.M):
        pat = re.compile(rf"^## {re.escape(name)}\b(.*?)(?=^## |\Z)", re.M | re.S)
        m = pat.search(body)
        body = body[: m.start()] + f"## {name}\n" + (m.group(1).rstrip() + "\n\n" + entry + "\n") + body[m.end():]
    else:
        body = body.rstrip() + f"\n\n## {name}\n" + entry + "\n"
    return body


# ---------------------------------------------------------------- commands


def _ledger_id(fm: dict) -> str:
    return fm.get("sid") or f"discuss-{fm.get('id', 'unknown')}"


def _record(fm: dict, event_type: str, payload: dict) -> None:
    sid = _ledger_id(fm)
    if not fm.get("sid"):
        fm["sid"] = start_session("agentic-research-lab", agent_kind="discuss",
                                  model="discuss", session_id=sid)
    append_event(sid, event_type, payload,
                 actor_id="user" if event_type == "user_message" else "agent")


def cmd_new(args: argparse.Namespace) -> None:
    thesis = " ".join(args.text).strip()
    if not thesis:
        raise DiscussError("empty thesis")
    slug = _slug(thesis)
    path = IDEAS / f"{slug}.md"
    if path.exists():
        path = IDEAS / f"{slug}-{time.strftime('%H%M%S')}.md"
    fm = {
        "id": path.stem,
        "thesis": thesis,
        "stance": "synth",
        "status": "open",
        "run_id": agent_trace.new_run_id("discuss"),
        "graph_generation": agent_trace.generation_id(),
        "sid": start_session("agentic-research-lab", agent_kind="discuss",
                             model="discuss", session_id=f"discuss-{path.stem}"),
        "created": _now(),
    }
    body = (
        f"# {thesis}\n\n"
        "The expert edits THIS file. Claims are added with `claim`, each\n"
        "retrieved against the corpus on both sides. Pick who speaks next with\n"
        "`stance`. End with `decide learned|wrong|unresolved`.\n\n"
        "## claims\n\n"
    )
    _write(path, fm, body)
    _record(fm, "user_message", {"thesis": thesis})
    _write(path, fm, body)  # persist the sid assigned by start_session
    print(f"created {path.relative_to(ROOT)}")
    print(f"ledger {fm['sid']} | run {fm['run_id']} | graph gen {fm['graph_generation']}")
    print(f"next: python scripts/discuss.py claim \"<sub-claim>\"  (add 3-5 claims)")


def cmd_open(args: argparse.Namespace) -> None:
    path = _resolve(args.path)
    st = _parse(path)
    fm, body = st["fm"], st["body"]
    print(f"=== {fm.get('id')} ===")
    print(f"thesis: {fm.get('thesis')}")
    print(f"stance: {fm.get('stance')}  | status: {fm.get('status')}")
    for c in st["claims"]:
        print(f"  {c['id']} {c['text']}")
        print(f"      support: {', '.join(c['support']) or '(none)'}")
        print(f"      counter: {', '.join(c['counter']) or '(none — unrefuted)'}")
        if c.get("note"):
            print(f"      note: {c['note']}")
    for a in st["attacks"]:
        print(f"  red-team: {a[:100]}")
    if st["decision"]:
        d = st["decision"]
        print(f"decision: {d.get('value')} — {d.get('why')}")
        if d.get("next"):
            print(f"  next: {d['next']}")


def cmd_stance(args: argparse.Namespace) -> None:
    path = _resolve(args.path)
    st = _parse(path)
    st["fm"]["stance"] = args.name
    _write(path, st["fm"], st["body"])
    print(f"stance: {args.name}")


def cmd_claim(args: argparse.Namespace) -> None:
    path = _resolve(args.path)
    _reject_stray_path(args)
    st = _parse(path)
    text = " ".join(args.text).strip()
    if not text:
        raise DiscussError("empty claim")
    cid = f"c{len(st['claims']) + 1}"
    # TWO-SIDED, and the counter is kept. The old script retrieved counters
    # then wrote "counter": [] (idea_session.py:147), so the evidence set
    # and the board were both support-only. Here both sides are persisted.
    support = _retrieve(st["fm"], f"{text} evidence", "support", cid)
    counter = _retrieve(st["fm"],
                        f"{text} failure modes limitations counterargument",
                        "counter", cid)
    claim = {"id": cid, "text": text, "support": support, "counter": counter}
    st["body"] = _upsert_claim(st["body"], claim)
    _record(st["fm"], "insight",
            {"claim_id": cid, "claim": text, "support": support, "counter": counter})
    _write(path, st["fm"], st["body"])
    print(f"{cid}: {text}")
    print(f"  support: {', '.join(support) or '(none)'}")
    print(f"  counter: {', '.join(counter) or '(none — corpus silent, not a refutation)'}")


def cmd_annotate(args: argparse.Namespace) -> None:
    path = _resolve(args.path)
    _reject_stray_path(args)
    st = _parse(path)
    target = next((c for c in st["claims"] if c["id"] == args.claim), None)
    if not target:
        raise DiscussError(f"no such claim {args.claim} — have "
                           + ", ".join(c["id"] for c in st["claims"]))
    target["note"] = " ".join(args.text).strip()
    st["body"] = _upsert_claim(st["body"], target)
    _record(st["fm"], "agent_message", {"claim_id": args.claim, "note": target["note"]})
    _write(path, st["fm"], st["body"])
    print(f"annotated {args.claim}")


def cmd_attack(args: argparse.Namespace) -> None:
    path = _resolve(args.path)
    _reject_stray_path(args)
    st = _parse(path)
    text = " ".join(args.text).strip()
    if not text:
        raise DiscussError("empty attack")
    cited = re.findall(r"`([^`]+)`", text)
    st["body"] = _append_section(st["body"], "red-team", text)
    _record(st["fm"], "agent_message", {"attack": text, "cited": cited})
    _write(path, st["fm"], st["body"])
    print(f"red-team recorded ({len(cited)} cited chunk ids)")


def cmd_concede(args: argparse.Namespace) -> None:
    path = _resolve(args.path)
    _reject_stray_path(args)
    st = _parse(path)
    text = " ".join(args.text).strip()
    st["body"] = _append_section(st["body"], "red-team",
                                 "CONCESSION: " + text)
    _record(st["fm"], "agent_message", {"concession": text})
    _write(path, st["fm"], st["body"])
    print("concession recorded — the claim stands unrefuted, by the record")


def cmd_decide(args: argparse.Namespace) -> None:
    path = _resolve(args.path)
    _reject_stray_path(args)
    st = _parse(path)
    why = " ".join(args.why).strip()
    if not why:
        raise DiscussError("decision needs a why")
    if args.value == "unresolved" and not args.next:
        raise DiscussError("decide unresolved must name the next experiment: --next TEXT")
    # A decision is a record, not scratch. Overwriting one silently discards
    # the why and the next experiment - and since the file is the only state,
    # that is unrecoverable. Observed live: a second `decide learned` wiped an
    # honest `unresolved` and took its --next with it.
    prev = st.get("decision")
    if prev and not args.force:
        raise DiscussError(
            f"a decision is already recorded: {prev.get('value')} - "
            f"{prev.get('why')}. Pass --force to replace it deliberately."
        )
    # Only the bare machine block goes. `## decision rationale` is human
    # prose, not state, and is exactly the thing a forced rewrite used to
    # take with it.
    block = f"## decision\n- value: {args.value}\n- why: {why}\n"
    if args.next:
        block += f"- next: {args.next}"
    body = _replace_decision(st["body"], block)
    st["fm"]["status"] = args.value
    st["body"] = body
    _record(st["fm"], "decision",
            {"value": args.value, "why": why, "next": args.next})
    _write(path, st["fm"], st["body"])
    print(f"decision: {args.value}")


def cmd_stage(args: argparse.Namespace) -> None:
    path = _resolve(args.path)
    st = _parse(path)
    fm, d = st["fm"], st["decision"]
    if not st["claims"]:
        raise DiscussError("stage refused: no claims")
    if not st["attacks"]:
        raise DiscussError("stage refused: no red-team turn — a decision "
                           "without an attack is self-endorsement")
    if not d:
        raise DiscussError("stage refused: no decision — run `decide` first")
    if d.get("value") != "unresolved":
        raise DiscussError(f"stage refused: decision is '{d.get('value')}' — only "
                           "an 'unresolved' discussion may stage a candidate. "
                           "learned → add a graph node; wrong → record a kill.")
    if not d.get("next"):
        raise DiscussError("stage refused: unresolved with no named next experiment")
    evidence = sorted({i for c in st["claims"] for i in c["support"] + c["counter"]})
    if not evidence:
        raise DiscussError("stage refused: no retrieved chunk ids — evidence is never invented")

    rule, target = args.rule.strip(), args.target.strip()
    action = f"Discussion {fm.get('id')}: unresolved — {d.get('why')}. Next: {d.get('next')}"
    plan = json.dumps({"claims": st["claims"], "decision": d},
                      ensure_ascii=False, sort_keys=True)
    record = {
        "id": f"discuss-{fm.get('id')}",
        "state": "proposed",
        "Rule": rule,
        "Evidence": ", ".join(f"`{e}`" for e in evidence),
        "Target": target,
        "Action": action,
        "provenance": {
            "run_id": fm.get("run_id"),
            "graph_generation": fm.get("graph_generation"),
            "plan_version": hashlib.sha256(plan.encode()).hexdigest()[:12],
            "fingerprint": fm.get("graph_generation"),
        },
        "revision_notes": f"v1: discuss {fm.get('id')}; {len(st['claims'])} claims, "
                          f"{sum(1 for c in st['claims'] if c['counter_empty'])} unrefuted",
        "falsification": "Evict when: (a) the named next experiment resolves the "
                         "question and the Rule is not needed, or (b) no evidence id "
                         "resolves to content supporting the Rule.",
    }
    out = CANDIDATES / f"discuss_{fm.get('id')}.jsonl"
    out.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")

    fm["status"] = "unresolved"
    fm["staged_candidate"] = str(out.relative_to(ROOT)).replace("\\", "/")
    _write(path, fm, st["body"])
    _record(fm, "agent_message", {"staged_candidate": record["id"]})
    _write(path, fm, st["body"])

    # A broken chain must stop the seal, not be printed beside it. An audit
    # trail you seal through without reading is not an audit trail.
    ok, msg = verify_chain(_ledger_id(fm))
    if not ok:
        raise DiscussError(
            f"stage refused: ledger chain failed verification \u2014 {msg}. "
            f"The candidate is written at {out.relative_to(ROOT)} but this "
            "discussion is NOT sealed; repair the ledger and re-stage."
        )
    finish_session(_ledger_id(fm), "completed")
    agent_trace.emit("artifact", run_id=fm.get("run_id", ""),
                     artifact=fm["staged_candidate"],
                     candidate_id=record["id"], status="ok")
    print(f"staged {fm['staged_candidate']} (id {record['id']}, {len(evidence)} evidence ids)")
    print(f"[chain] {msg} | session sealed")
    print("next: python scripts/check_citation_integrity.py")


def cmd_close(args: argparse.Namespace) -> None:
    path = _resolve(args.path)
    st = _parse(path)
    ok, msg = verify_chain(_ledger_id(st["fm"]))
    if not ok:
        raise DiscussError(
            f"close refused: ledger chain failed verification \u2014 {msg}. "
            "The file is left open; repair the ledger and re-close."
        )
    finish_session(_ledger_id(st["fm"]), "aborted")
    st["fm"]["status"] = "closed"
    _write(path, st["fm"], st["body"])
    print(f"[chain] {msg} | session aborted | file kept at {path.relative_to(ROOT)}")


def _path(p: argparse.ArgumentParser) -> None:
    """Declare the target file.

    It is an OPTION, not a trailing positional. As a positional declared after
    a `nargs='*'` text argument, argparse silently absorbed the file into the
    text — `attack "the attack" old.md` recorded a red-team turn whose prose
    ended in "old.md" and edited the WRONG file (the most recent one). Since
    every command defaults to the latest idea file, that failure is invisible:
    the command reports success.
    """
    p.add_argument("-p", "--path", default=None, metavar="FILE.md",
                   help="idea file (default: most recently modified)")


def main() -> int:
    ap = argparse.ArgumentParser(description="chat with an expert, as a file")
    sub = ap.add_subparsers(dest="command", required=True)
    p = sub.add_parser("new", help="create an idea file"); p.add_argument("text", nargs="+")
    p.set_defaults(func=cmd_new)
    p = sub.add_parser("open", help="print the board"); _path(p)
    p.set_defaults(func=cmd_open)
    p = sub.add_parser("stance", help="set who speaks next")
    p.add_argument("name", choices=STANCES); _path(p)
    p.set_defaults(func=cmd_stance)
    p = sub.add_parser("claim", help="add a claim + two-sided retrieval")
    p.add_argument("text", nargs="+"); _path(p)
    p.set_defaults(func=cmd_claim)
    p = sub.add_parser("annotate", help="attach expert prose to a claim")
    p.add_argument("--claim", required=True); p.add_argument("text", nargs="+")
    _path(p); p.set_defaults(func=cmd_annotate)
    p = sub.add_parser("attack", help="record a red-team turn")
    p.add_argument("text", nargs="+"); _path(p)
    p.set_defaults(func=cmd_attack)
    p = sub.add_parser("concede", help="record an honest non-refutation")
    p.add_argument("text", nargs="+"); _path(p)
    p.set_defaults(func=cmd_concede)
    p = sub.add_parser("decide", help="learned | wrong | unresolved")
    _path(p)
    p.add_argument("value", choices=DECISIONS); p.add_argument("why", nargs="*")
    p.add_argument("--next")
    p.add_argument("--force", action="store_true", help="replace an existing decision")
    p.set_defaults(func=cmd_decide)
    p = sub.add_parser("stage", help="seal and write a proposed candidate")
    p.add_argument("--rule", required=True); p.add_argument("--target", required=True)
    _path(p); p.set_defaults(func=cmd_stage)
    p = sub.add_parser("close", help="verify + seal without staging")
    _path(p); p.set_defaults(func=cmd_close)

    args = ap.parse_args()
    try:
        args.func(args)
    except DiscussError as e:
        print(f"refused: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
