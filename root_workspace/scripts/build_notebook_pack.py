#!/usr/bin/env python3
"""Build a NotebookLM-ready .txt pack: workspace context + recent sessions + expert slot.

ICM fit: this script is factory (generator, committed under scripts/).
Its OUTPUTS are derived — never committed; write under scripts/out/
(gitignored context-pack dir) or another scratch path.

Composition (three skills, one pack):
- icm-architect ... the pack is a knowledge bundle: catalog header, then
  shelves (workspace / sessions / grill / expert). One home per fact, links
  not copies, token-capped shelves.
- grill-with-docs .. grilling (relentless frontier questions) + domain-modeling
  (glossary + ADR capture). The pack carries the interview, not just the data.
- agent-reach ..... the expert shelf is a SLOT the user fills later with
  primary sources via agent-reach. This script never fetches the web; it only
  leaves the shelf with fill instructions + citation shape.

Usage:
  python.exe scripts/build_notebook_pack.py --scope root --sessions 5 -o scripts/out/notebook-root.txt
  python.exe scripts/build_notebook_pack.py --scope project --project knowledge-retrieval --sessions 5 -o scripts/out/notebook-kr.txt
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import build_context_txt as ctx
from agent_sessions import get_all_sessions

SECRET_RE = ctx.SECRET_RE
MAX_SESSION_CHARS_DEFAULT = 15_000


def _section(title: str, body: str) -> str:
    bar = "=" * 70
    return f"\n{bar}\n{title}\n{bar}\n{body.rstrip()}\n"


def _header(scope: str, project: str, n_sessions: int, level: int) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    target = "root_workspace" if scope == "root" else f"project:{project}"
    return (
        "# NotebookLM pack — workspace + session memory + expert slot\n"
        f"- Generated : {now} by scripts/build_notebook_pack.py (factory, derived output)\n"
        f"- Scope     : {target} @ L{level} + {n_sessions} latest sessions\n"
        f"- Purpose   : DEBUG + structural decisions / ADR\n"
        "- How to use: upload this .txt to Gemini Notebook (NotebookLM) as one source, "
        "then add expert sources (docs/papers/URLs via agent-reach) as further sources. "
        "Ask NotebookLM to answer from workspace + sessions first, expert second.\n"
        "- Recall rule (debug-with-memory): memory answers 'have we seen this before?', "
        "never 'what is broken right now'. Current logs/tests win for the present.\n"
        "- Zero-hit rule: no hit in this pack is NOT proof the topic is new — "
        "the FTS5 index falls back AND->OR and the pack holds only 5 sessions.\n"
    )


def _workspace_part(scope: str, project: str, level: int) -> str:
    if level == 0:
        body = ctx.l0_router()
    elif level == 1:
        body = ctx.l1_brief(scope, project)
    else:
        body = ctx.l2_standard(scope, project)
    return _section(
        f"SHELF A — WORKSPACE CONTEXT (scope={scope} level=L{level})",
        ctx.redact(body),
    )


def _grill_part(scope: str, project: str) -> str:
    target = "root workspace" if scope == "root" else f"project {project}"
    body = f"""This shelf is the grill-with-docs interview carried INTO NotebookLM.
Answer these against Shelf A (workspace) + Shelf B (sessions) + Shelf D (expert) before deciding.

## Round 1 — debug framing (grilling: frontier first)
Q1 — Symptom in one sentence: what EXACTLY fails for {target}?
Recommended: paste the literal error line + exit code, not a paraphrase.

Q2 — Repro: minimal steps, starting state, flakiness (always / sometimes / once)?
Recommended: smallest command sequence that reproduces; name what changed since it last worked.

Q3 — Expected vs actual: what should happen per the contract (CONTEXT.md / entry file)?
Recommended: cite the exact contract line; if no contract covers it, say so — that IS a finding.

Q4 — What did session memory already try? (Shelf B + debug-with-memory survey)
Recommended: list applied/rejected past fixes with chunk ids; a zero-hit is logged as gap, not proof.

## Round 2 — decision framing (domain-modeling: sharpen then record)
Q5 — Which term is overloaded here? (check GLOSSARY.md first, narrow locally, never redefine)
Recommended: name the canonical term + what it does NOT mean.

Q6 — Options + rejected alternatives: what are the genuine candidates and why does each lose?
Recommended: 2-3 options with one-line kill reason each; 'do nothing' counts as an option.

Q7 — Reversibility: is this easy to undo (edit) or hard (migration/gate/process)?
Recommended: state the undo cost; hard-to-reverse + surprising + real tradeoff => ADR required.

## Capture contract (domain-modeling output shape)
- Resolved term -> GLOSSARY or project CONTEXT.md ## Language (narrow, never redefine).
- Hard decision -> docs/adr/NNNN-slug.md (context / options / decision / consequences).
- Rejected paths stay in the session record so the next debug finds them.
"""
    return _section("SHELF C — GRILL (questions to answer in NotebookLM)", body)


def _expert_slot() -> str:
    body = """SLOT FOR THE USER — fill later with agent-reach output. This pack ships WITHOUT web sources on purpose.

How to fill (agent-reach skill):
1. Run: agent-reach doctor --json  (pick the live backend per platform from active_backend).
2. Collect PRIMARY sources first: official docs, papers (DOI/arXiv), source code, first-party specs.
   Then discussion: GitHub issues/PRs, Reddit threads, technical articles.
3. Paste each source as: title / URL + access date / exact claim / confidence (verified|inferred|speculative) / limitation.
4. In NotebookLM add them as SEPARATE sources (not pasted here) when possible — keeps citations clean.
   If you must paste here, append under '--- pasted expert notes ---' below.

Source quality bar (research skill): no marketing copy, no unverified social claims,
no outdated docs without a date, no AI-aggregator farms. Contradictions get flagged, not smoothed.

--- pasted expert notes ---
(empty — user fills)
"""
    return _section("SHELF D — EXPERT SLOT (user fills via agent-reach)", body)


def _sessions_part(n: int, max_chars: int) -> tuple[str, list[str]]:
    sessions = get_all_sessions(limit_per_agent=10)
    latest = sessions[:n]
    ids = [f"{s.agent}::{s.id}" for s in latest]
    buf: list[str] = []
    buf.append(f"Latest {len(latest)} sessions, newest first (truncated to {max_chars} chars each).")
    buf.append("Full transcripts live in agent stores; provenance (agent/id/date/raw_path) heads each item.")
    for i, s in enumerate(latest, 1):
        text = s.text_markdown or "(empty transcript)"
        text = ctx.redact(text)
        if len(text) > max_chars:
            text = text[:max_chars] + f"\n[... truncated {len(text) - max_chars} chars: use agent_sessions.py export {s.agent} {s.id} for full] ..."
        buf.append(
            f"\n--- session {i}/{len(latest)}: {s.agent} :: {s.id} ---\n"
            f"title    : {s.title}\n"
            f"date     : {s.updated_at or s.created_at}\n"
            f"model    : {s.model or '-'}\n"
            f"raw_path : {s.raw_path}\n"
            f"messages : {s.message_count}\n\n{text}"
        )
    return _section(f"SHELF B — LAST {len(latest)} SESSIONS (recall, not inspect)", "\n".join(buf)), ids


def main() -> int:
    ap = argparse.ArgumentParser(description="Build NotebookLM .txt pack.")
    ap.add_argument("--scope", choices=["root", "project"], default="root")
    ap.add_argument("--project", default="")
    ap.add_argument("--sessions", type=int, default=5)
    ap.add_argument("--level", type=int, choices=[0, 1, 2], default=1)
    ap.add_argument("--max-session-chars", type=int, default=MAX_SESSION_CHARS_DEFAULT)
    ap.add_argument("-o", "--output", default="")
    args = ap.parse_args()

    if args.scope == "project" and not args.project:
        ap.error("--project <name> required with --scope project")
    proj_dir = ROOT / "projects" / "research" / args.project if args.project else None
    if proj_dir is not None and not proj_dir.is_dir():
        ap.error(f"unknown project: {args.project}")

    parts = [_header(args.scope, args.project, args.sessions, args.level)]
    parts.append(_workspace_part(args.scope, args.project, args.level))
    shelf_b, ids = _sessions_part(args.sessions, args.max_session_chars)
    parts.append(shelf_b)
    parts.append(_grill_part(args.scope, args.project))
    parts.append(_expert_slot())
    text = "\n".join(parts)
    footer = (
        f"\n{'=' * 70}\n[token estimate: ~{ctx.tok_estimate(text)} | "
        f"scope={args.scope} level=L{args.level} sessions={','.join(ids)}]\n"
    )
    text += footer

    if args.output:
        out = Path(args.output)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"wrote {out} (~{ctx.tok_estimate(text)} tokens)")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
