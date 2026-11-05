#!/usr/bin/env python3
"""inspect_pdf.py — Local PDF native text inspector inspired by PDF Inspector principles.

Rapidly inspects PDF files to determine if text is natively extractable (avoiding unnecessary OCR)
and reports structural metrics (page count, text density, image presence).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def inspect_pdf(path: Path) -> dict:
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        num_pages = len(reader.pages)
        text_pages = 0
        total_chars = 0

        # Sample strategy (inspired by 8-page sampling in PDF Inspector)
        sample_indices = set([0, num_pages - 1])
        if num_pages > 2:
            step = max(1, num_pages // 7)
            for i in range(1, num_pages - 1, step):
                sample_indices.add(i)

        sampled_text_chars = 0
        for idx in sorted(sample_indices):
            if idx < num_pages:
                txt = reader.pages[idx].extract_text() or ""
                if len(txt.strip()) > 20:
                    sampled_text_chars += len(txt)

        for pg in reader.pages:
            txt = pg.extract_text() or ""
            total_chars += len(txt.strip())
            if len(txt.strip()) > 10:
                text_pages += 1

        is_native = text_pages > 0 and (total_chars / max(1, num_pages)) > 15
        doc_type = "text-based" if is_native and text_pages >= num_pages * 0.8 else ("mixed" if text_pages > 0 else "scanned/image-based")

        return {
            "path": str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path),
            "pages": num_pages,
            "text_pages": text_pages,
            "total_chars": total_chars,
            "doc_type": doc_type,
            "native_extractable": is_native
        }
    except Exception as e:
        return {"path": str(path), "error": str(e)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", nargs="?", help="PDF file or directory to inspect")
    args = ap.parse_args()

    target = Path(args.path) if args.path else ROOT / "INBOX"
    if not target.exists():
        print(f"Error: {target} does not exist", file=sys.stderr)
        return 1

    files = [target] if target.is_file() else sorted(target.glob("**/*.pdf"))
    if not files:
        print(f"No PDF files found at {target}", file=sys.stderr)
        return 0

    print(f"Inspecting {len(files)} PDF(s)...\n")
    for f in files:
        res = inspect_pdf(f)
        if "error" in res:
            print(f"❌ {res['path']}: ERROR — {res['error']}")
        else:
            icon = "📄" if res["native_extractable"] else "🖼️"
            print(f"{icon} {res['path']} ({res['pages']} pages) -> type: {res['doc_type']}, text pages: {res['text_pages']}/{res['pages']}, chars: {res['total_chars']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
