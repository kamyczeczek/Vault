#!/usr/bin/env python3
"""Render a markdown review bundle (REVIEW.md, GATES.md, HANDOFF) to a single
self-contained HTML file for human approval.

Source of truth stays markdown (diffable, grepable, gate-checkable); HTML is
a read-only view, never committed. Stdlib only, no shell calls, CRLF-safe.

Usage:
    python scripts/render_review.py INPUT.md [-o OUTPUT.html] [--title T]
    python scripts/render_review.py --selftest

Supported markdown subset: headings, fenced code, tables (incl. GATES
checkbox rows), bullet/ordered lists, `- [ ]`/`- [x]` checkboxes,
blockquotes, hr, paragraphs; inline `code`, **bold**, *italic*,
[text](url). Anything else degrades to a paragraph — never a crash.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

CSS = (
    "body{font-family:Segoe UI,system-ui,sans-serif;max-width:60em;margin:2em auto;"
    "padding:0 1em;color:#1a1a1a;background:#fff;line-height:1.55}"
    "pre{background:#f4f4f4;padding:1em;overflow-x:auto;border-radius:6px}"
    "code{background:#f4f4f4;padding:.1em .3em;border-radius:4px}"
    "pre code{background:none;padding:0}"
    "table{border-collapse:collapse;margin:1em 0;width:100%}"
    "th,td{border:1px solid #ccc;padding:.4em .7em;text-align:left}"
    "th{background:#f0f0f0}blockquote{border-left:3px solid #888;margin:1em 0;"
    "padding:.2em 1em;color:#444}.meta{color:#666;font-size:.9em}"
    "h1{border-bottom:2px solid #333}h2{border-bottom:1px solid #ccc}"
)

FENCE = re.compile(r"^(`{3,})(\w*)\s*$")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
UL = re.compile(r"^(\s*)[-*]\s+(.*)$")
OL = re.compile(r"^(\s*)\d+[.)]\s+(.*)$")
CHECK = re.compile(r"^\[([ xX])\]\s+(.*)$")
TABLE_SEP = re.compile(r"^\s*\|?(\s*:?-+:?\s*\|)+\s*$")
HR = re.compile(r"^\s*([-*_]\s*){3,}$")
QUOTE = re.compile(r"^>\s?(.*)$")


def inline(text: str) -> str:
    """Escape HTML then apply inline markdown spans."""
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text
    )
    return text


def table_row(cells: list[str], header: bool = False) -> str:
    tag = "th" if header else "td"
    tds = "".join(f"<{tag}>{inline(c.strip())}</{tag}>" for c in cells)
    return f"<tr>{tds}</tr>"


def split_row(line: str) -> list[str]:
    return [c for c in line.strip().strip("|").split("|")]


def render(md_text: str, title: str = "Review", banner_html: str = "",
           extra_css: str = "") -> str:
    lines = md_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out: list[str] = []
    i = 0
    n = len(lines)
    in_list: str | None = None  # "ul" | "ol" | None

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            out.append(f"</{in_list}>")
            in_list = None

    while i < n:
        line = lines[i]
        m = FENCE.match(line)
        if m:
            close_list()
            fence, lang = m.group(1), m.group(2)
            buf: list[str] = []
            i += 1
            while i < n and not lines[i].startswith(fence):
                buf.append(lines[i])
                i += 1
            i += 1  # consume closing fence (or EOF)
            code = html.escape("\n".join(buf))
            cls = f' class="language-{html.escape(lang)}"' if lang else ""
            out.append(f"<pre><code{cls}>{code}</code></pre>")
            continue
        hm = HEADING.match(line)
        if hm:
            close_list()
            level = len(hm.group(1))
            out.append(f"<h{level}>{inline(hm.group(2))}</h{level}>")
            i += 1
            continue
        if HR.match(line):
            close_list()
            out.append("<hr>")
            i += 1
            continue
        qm = QUOTE.match(line)
        if qm:
            close_list()
            buf = [qm.group(1)]
            i += 1
            while i < n and QUOTE.match(lines[i]):
                buf.append(QUOTE.match(lines[i]).group(1))  # type: ignore[union-attr]
                i += 1
            out.append(f"<blockquote>{'<br>'.join(inline(b) for b in buf)}</blockquote>")
            continue
        # table: header row + separator row
        if "|" in line and i + 1 < n and TABLE_SEP.match(lines[i + 1]):
            close_list()
            out.append("<table>")
            out.append(table_row(split_row(line), header=True))
            i += 2
            while i < n and "|" in lines[i] and lines[i].strip():
                out.append(table_row(split_row(lines[i])))
                i += 1
            out.append("</table>")
            continue
        um = UL.match(line)
        om = OL.match(line)
        if um or om:
            kind = "ul" if um else "ol"
            if in_list != kind:
                close_list()
                out.append(f"<{kind}>")
                in_list = kind
            body = (um or om).group(2)  # type: ignore[union-attr]
            cm = CHECK.match(body)
            if cm:
                checked = " checked" if cm.group(1).lower() == "x" else ""
                out.append(
                    f'<li><input type="checkbox" disabled{checked}> '
                    f"{inline(cm.group(2))}</li>"
                )
            else:
                out.append(f"<li>{inline(body)}</li>")
            i += 1
            continue
        if not line.strip():
            close_list()
            i += 1
            continue
        close_list()
        out.append(f"<p>{inline(line.strip())}</p>")
        i += 1
    close_list()
    body = "\n".join(out)
    safe_title = html.escape(title)
    banner = f"{banner_html}\n" if banner_html else ""
    css = CSS + extra_css
    return (
        "<!DOCTYPE html>\n<html lang=\"pl\">\n<head>\n<meta charset=\"utf-8\">\n"
        f"<title>{safe_title}</title>\n<style>{css}</style>\n</head>\n<body>\n"
        f"{banner}{body}\n</body>\n</html>\n"
    )


def render_file(src: Path, dst: Path | None, title: str | None) -> Path:
    text = src.read_text(encoding="utf-8")
    if title is None:
        m = HEADING.search(text)
        title = m.group(2).strip() if m else src.stem
    out_path = dst or src.with_suffix(".html")
    out_path.write_text(render(text, title), encoding="utf-8")
    return out_path


def selftest() -> int:
    sample = (
        "# Gates: demo\n\n- [x] done thing\n- [ ] open thing\n\n"
        "| A | B |\n|---|---|\n| 1 | 2 |\n\n```python\nprint('<x>')\n```\n\n"
        "> note here\n\nSome **bold** and `code` and [link](https://example.com).\n"
    )
    doc = render(sample, "Demo")
    probes = [
        "<h1>Gates: demo</h1>",
        "<table>",
        "<th>A</th>",
        "checked",
        "<pre><code",
        "&lt;x&gt;",
        "<blockquote>",
        "<strong>bold</strong>",
        '<a href="https://example.com">link</a>',
        "<style>",
    ]
    missing = [p for p in probes if p not in doc]
    if missing:
        print(f"SELFTEST FAIL: missing {missing}")
        return 1
    # CRLF input must render identically
    if render(sample.replace("\n", "\r\n"), "Demo") != doc:
        print("SELFTEST FAIL: CRLF divergence")
        return 1
    print(f"SELFTEST OK ({len(probes)} probes, CRLF-stable)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("input", nargs="?",
                    help="markdown file to render, or a run dir holding REVIEW.md")
    ap.add_argument("-o", "--output", default=None, help="output html path")
    ap.add_argument("--title", default=None, help="page title override")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.input:
        ap.error("input file required (or --selftest)")
    src = Path(args.input)
    if src.is_dir():  # run dir: render its REVIEW.md
        src = src / "REVIEW.md"
    if not src.is_file():
        print(f"no such file: {src}", file=sys.stderr)
        return 2
    dst = Path(args.output) if args.output else None
    written = render_file(src, dst, args.title)
    print(f"wrote {written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
