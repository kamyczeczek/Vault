#!/usr/bin/env python3
"""One-command human review of a run: verify evidence, render HTML, open it.

Replaces the 5-6 step manual chain (find REVIEW.md -> run verify -> read
output -> render -> find HTML -> open in browser -> hand-type verdict).
The re-verification result is baked into the HTML as a banner by the
launcher itself, so it cannot be hand-mistyped by the agent.

Usage:
    python scripts/review.py <run-dir> [--no-open]
    python scripts/review.py <run-dir> --decide PASS [--note "..."]
    python scripts/review.py --selftest

<run-dir> is `.dgc-evidence/runs/<run-id>/` holding REVIEW.md. The HTML
lands beside it as REVIEW.html. --decide writes DECISION.json (machine-
readable verdict) beside REVIEW.md and re-renders the HTML to show it.
Stdlib only.
"""
from __future__ import annotations

import argparse
import datetime
import html
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import render_review  # noqa: E402

BANNER_CSS = (
    ".vbanner{padding:.8em 1em;border-radius:8px;margin:0 0 1em 0;font-weight:bold}"
    ".vbanner.ok{background:#e6f4ea;border:2px solid #1e8e3e;color:#0d652d}"
    ".vbanner.bad{background:#fce8e6;border:2px solid #c5221f;color:#a50e0e}"
    ".vbanner.verdict{background:#e8f0fe;border:2px solid #1a73e8;color:#174ea6}"
    ".decide-cmd{background:#f4f4f4;padding:1em;border-radius:6px}"
)


def git_head() -> str:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, cwd=ROOT, timeout=10)
        return r.stdout.strip() or "?"
    except Exception:
        return "?"


def resolve_review(target: str) -> tuple[Path, Path]:
    """Return (run_dir, review_md). Accepts a run dir or a REVIEW.md path."""
    p = Path(target)
    if p.is_file():
        return p.parent, p
    review = p / "REVIEW.md"
    if review.is_file():
        return p, review
    print(f"no REVIEW.md in {p} (expected {review})", file=sys.stderr)
    raise SystemExit(2)


def run_verify(review: Path) -> tuple[int, str]:
    """Run verify_review_evidence.py with repo root as pytest cwd."""
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_review_evidence.py"),
         str(review), "--root", str(ROOT)],
        capture_output=True, text=True, cwd=ROOT, timeout=600)
    tail = (r.stdout or "").strip().splitlines()
    # last lines joined: banner classifies on the whole blob,
    # displays only the final line
    return r.returncode, "\n".join(tail[-8:]) if tail else "(no output)"


def verdict_block(run_dir: Path) -> str:
    dec = run_dir / "DECISION.json"
    if dec.is_file():
        try:
            d = json.loads(dec.read_text(encoding="utf-8"))
            v = html.escape(str(d.get("verdict", "?")))
            note = html.escape(str(d.get("note", "")))
            when = html.escape(str(d.get("time", "")))
            extra = f" — {note}" if note else ""
            return (f'<div class="vbanner verdict">WERDYKT: {v}'
                    f'<span style="font-weight:normal"> ({when}{extra})</span></div>')
        except Exception:
            return '<div class="vbanner bad">DECISION.json unreadable</div>'
    cmd = f"python scripts/review.py {run_dir} --decide PASS|FAIL|BLOCKED"
    return (f'<div class="decide-cmd">Brak werdyktu. Po ocenie zapisz go jedną komendą:<br>'
            f'<code>{html.escape(cmd)}</code> (+ opcjonalnie <code>--note "..."</code>)</div>')


def build_banner(rc: int, blob: str) -> str:
    if rc != 0 and "no verifiable pytest claims found" in blob:
        return ('<div class="vbanner ok">RE-WERYFIKACJA: PASS '
                '(research-only — brak claimów pytest, verify nie ma czego '
                'sprawdzać).</div>')
    cls = "ok" if rc == 0 else "bad"
    word = "PASS" if rc == 0 else "FAIL"
    last = html.escape(blob.strip().splitlines()[-1]) if blob.strip() else "?"
    return (f'<div class="vbanner {cls}">RE-WERYFIKACJA: {word} '
            f'(verify rc={rc}) — {last}</div>')


def review_flow(run_dir: Path, review: Path, open_browser: bool) -> int:
    rc, summary = run_verify(review)
    mtime = datetime.datetime.fromtimestamp(
        review.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
    meta = (f'<p class="meta">run: <code>{html.escape(run_dir.name)}</code> · '
            f'HEAD: <code>{html.escape(git_head())}</code> · '
            f'REVIEW z: {html.escape(mtime)}</p>')
    banner = build_banner(rc, summary) + meta + verdict_block(run_dir)
    text = review.read_text(encoding="utf-8")
    doc = render_review.render(text, title=f"REVIEW {run_dir.name}",
                               banner_html=banner, extra_css=BANNER_CSS)
    out = review.with_suffix(".html")
    out.write_text(doc, encoding="utf-8")
    print(f"verify rc={rc}: {summary.strip().splitlines()[-1]}")
    print(f"wrote {out}")
    if open_browser:
        try:
            os.startfile(str(out))  # type: ignore[attr-defined]
        except Exception:
            print("(could not auto-open browser; open the file manually)")
    return 0


def decide_flow(run_dir: Path, verdict: str, note: str) -> int:
    review = run_dir / "REVIEW.md"
    if not review.is_file():
        print(f"no REVIEW.md in {run_dir}", file=sys.stderr)
        return 2
    dec = {"verdict": verdict,
           "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
           "note": note, "review": review.name}
    (run_dir / "DECISION.json").write_text(
        json.dumps(dec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"recorded {verdict} in {run_dir / 'DECISION.json'}")
    try:  # verdict changes worktree state -> refresh the generated snapshot
        import build_state
        build_state.build()
    except Exception as e:
        print(f"(STATE.md refresh skipped: {e})")
    return review_flow(run_dir, review, open_browser=False)


def selftest() -> int:
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        run = Path(td) / "run-x"
        run.mkdir()
        (run / "REVIEW.md").write_text(
            "# Review run-x\n\nProponowany werdykt: PASS.\n", encoding="utf-8")
        rc, _ = run_verify(run / "REVIEW.md")
        assert rc == 2, "empty REVIEW must verify-FAIL (no claims)"
        assert review_flow(run, run / "REVIEW.md", open_browser=False) == 0
        assert (run / "REVIEW.html").is_file()
        body = (run / "REVIEW.html").read_text(encoding="utf-8")
        assert "RE-WERYFIKACJA: PASS" in body and "research-only" in body
        assert "Brak werdyktu" in body
        assert decide_flow(run, "PASS", "ok") == 0
        d = json.loads((run / "DECISION.json").read_text(encoding="utf-8"))
        assert d["verdict"] == "PASS" and d["note"] == "ok", d
        body2 = (run / "REVIEW.html").read_text(encoding="utf-8")
        assert "WERDYKT: PASS" in body2, body2[-500:]
    print("SELFTEST OK (verify-banner + render + decide round-trip)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("run", nargs="?",
                    help="run dir (.dgc-evidence/runs/<id>/) or REVIEW.md path")
    ap.add_argument("--no-open", action="store_true",
                    help="do not open the browser")
    ap.add_argument("--decide", choices=["PASS", "FAIL", "BLOCKED"],
                    help="record a machine-readable verdict (DECISION.json)")
    ap.add_argument("--note", default="", help="note attached to the verdict")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.run:
        ap.error("run dir required (or --selftest)")
    run_dir, review = resolve_review(args.run)
    if args.decide:
        return decide_flow(run_dir, args.decide, args.note)
    return review_flow(run_dir, review, open_browser=not args.no_open)


if __name__ == "__main__":
    raise SystemExit(main())
