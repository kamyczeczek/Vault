#!/usr/bin/env python3
"""record_turn.py — append conversation turns to the hash-chained session log.

The recorder is the write seam for a `grill-with-docs` conversation. Every turn
becomes an event in `session_store`, so the conversation is captured as it
happens rather than reconstructed from memory afterwards.

`session_store.append_event` accepts any `event_type` string, which is what lets
the existing tests use `note` and `tool_result`. Unconstrained typing is fine for
a library and wrong for a ledger a future reader has to search, so the
vocabulary is pinned here, at the seam: a closed set the recorder validates
before anything is written. The library stays open; the recorder does not.

Text is accepted from an argument, a file, or stdin. Long turns and turns
containing quotes are the normal case, and shell quoting mangles both.

`session_store` binds its database at each call site rather than through a
global, so the recorder takes the path explicitly. That is what lets a test —
or a second ledger — write somewhere other than the live session log.
"""
from __future__ import annotations

import argparse

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "knowledge" / "graph"
SESSION_DB = GRAPH / "sessions.db"
if str(GRAPH) not in sys.path:
    sys.path.insert(0, str(GRAPH))

# A session id is the one value a caller is expected to capture in a shell:
# `SID=$(python scripts/record_turn.py start ...)`. Python translates \n to
# \r\n on Windows, and MSYS command substitution strips the \n but not the \r,
# so the captured id arrives with a trailing carriage return and every
# subsequent lookup misses. Emit bare \n so the id survives the round trip.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(newline="\n")

from session_store import (  # noqa: E402
    append_event,
    finish_session,
    start_session,
    verify_chain,
)

# The pinned ledger vocabulary. Each entry maps to the actor allowed to write it:
# the user speaks for themselves, the agent writes down everything else.
EVENT_TYPES: dict[str, str] = {
    "user_message": "user",
    "answer": "user",
    "agent_message": "agent",
    "question": "agent",
    "decision": "agent",
    "term": "agent",
    "insight": "agent",
    "open_question": "agent",
}

# Key under which the caller's turn text is stored, per event type. A reader
# searching the payload for "text" should not have to know which of three shapes
# a given turn used.
TEXT_KEY = {
    "question": "question",
    "answer": "answer",
    "decision": "decision",
    "term": "term",
    "insight": "insight",
    "open_question": "question",
}


class RecorderError(Exception):
    """A refusal that must reach the caller as a non-zero exit, not a stack trace."""


def read_text(args: argparse.Namespace) -> str:
    """Return the turn body from exactly one of --text, --text-file, or stdin.

    The two refusals are kept apart on purpose. A closed pipe, a missing file,
    and an interactive terminal all mean *nothing was supplied*; a file that
    exists but holds only whitespace means *an empty turn was supplied*. Both
    are rejected, but they are different mistakes and the caller needs to know
    which one it made.
    """
    if args.text is not None:
        body = args.text
    elif args.text_file is not None:
        try:
            body = Path(args.text_file).read_text(encoding="utf-8")
        except OSError as exc:
            raise RecorderError(f"no turn body: cannot read --text-file: {exc}") from exc
    elif sys.stdin is None or sys.stdin.isatty():
        raise RecorderError("no turn body: pass --text, --text-file, or pipe stdin")
    else:
        body = sys.stdin.read()
        if not body.strip():
            raise RecorderError("no turn body: stdin was piped but empty")
    if not body.strip():
        raise RecorderError("empty turn: an empty turn is not a record")
    return body.strip()


def validate(event_type: str, actor: str) -> str:
    """Return the actor permitted for `event_type`, or refuse the write."""
    if event_type not in EVENT_TYPES:
        raise RecorderError(
            f"unknown event type {event_type!r}; the ledger vocabulary is closed: "
            + ", ".join(sorted(EVENT_TYPES))
        )
    expected = EVENT_TYPES[event_type]
    if actor != expected:
        raise RecorderError(
            f"event type {event_type!r} is written by the {expected}, not the {actor}"
        )
    return actor


def _db(args: argparse.Namespace) -> Path:
    return Path(args.db) if args.db else SESSION_DB


def cmd_start(args: argparse.Namespace) -> int:
    sid = start_session(
        args.workspace, agent_kind=args.agent_kind, model=args.model,
        provider=args.provider, session_id=args.session_id, path=_db(args),
    )
    print(sid)
    return 0


def cmd_turn(args: argparse.Namespace) -> int:
    actor = validate(args.event_type, args.actor)
    body = read_text(args)
    payload: dict[str, object] = {TEXT_KEY.get(args.event_type, "text"): body}
    for flag, key in (("--decided-by", "decided_by"), ("--supersedes", "supersedes")):
        value = getattr(args, flag[2:].replace("-", "_"))
        if value:
            payload[key] = value
    if args.round is not None:
        payload["round"] = args.round
    if args.question_id:
        payload["question_id"] = args.question_id
    event_id = append_event(
        args.session, args.event_type, payload, actor_id=actor, path=_db(args)
    )
    print(event_id)
    return 0


def cmd_close(args: argparse.Namespace) -> int:
    """Verify before finishing, so a broken chain is never sealed as completed."""
    ok, message = verify_chain(args.session, path=_db(args))
    print(f"chain: {message}")
    if not ok:
        return 1
    if args.status == "verify":
        return 0
    finish_session(args.session, args.status, path=_db(args))
    print(f"session {args.session} {args.status}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start", help="open a session and print its id")
    start.add_argument("workspace")
    start.add_argument("--agent-kind", default="hermes")
    start.add_argument("--model", default="")
    start.add_argument("--provider", default="")
    start.add_argument("--session-id", help="use a known id instead of a fresh uuid")
    start.add_argument("--db", help="ledger path (default: the live session log)")

    start.set_defaults(func=cmd_start)

    turn = sub.add_parser("turn", help="append one turn")
    turn.add_argument("session")
    turn.add_argument("event_type", choices=sorted(EVENT_TYPES))
    turn.add_argument("--actor", choices=("user", "agent"), required=True)
    source = turn.add_mutually_exclusive_group()
    source.add_argument("--text")
    source.add_argument("--text-file")
    turn.add_argument("--round", type=int, help="grilling round this turn belongs to")
    turn.add_argument("--question-id", help="frontier question this turn answers")
    turn.add_argument("--decided-by", help="for a decision: who settled it")
    turn.add_argument("--supersedes", help="for a decision: the prior decision it replaces")
    turn.add_argument("--db", help="ledger path (default: the live session log)")

    turn.set_defaults(func=cmd_turn)

    close = sub.add_parser("close", help="verify the chain, then finish the session")
    close.add_argument("session")
    close.add_argument(
        "--status", default="completed",
        choices=("completed", "failed", "aborted", "branched", "verify"),
    )
    close.add_argument("--db", help="ledger path (default: the live session log)")
    close.set_defaults(func=cmd_close)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return args.func(args)
    except (RecorderError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
