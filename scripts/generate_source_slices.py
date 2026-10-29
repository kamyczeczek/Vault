#!/usr/bin/env python3
"""Generate reproducible retrieval slices from a Markdown source.

The source remains authoritative.  A slice is a derived navigation artifact
with an origin hash and line range; it must never be edited by hand.

Examples::

    python scripts/generate_source_slices.py
    python scripts/generate_source_slices.py --check
    python scripts/generate_source_slices.py --source kb/Notes/OKF-rag/okf-rag.md \
        --spec scripts/source_slice_specs/okf-rag.json \
        --output kb/Notes/OKF-rag/_slices/okf-rag
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCRIPT_VERSION = "1"
SCHEMA_VERSION = 1
# Obsidian/okf-enforcer may maintain a navigation index in every folder.  It
# is not owned by this generator and is deliberately allowed beside manifest.
EXTERNAL_AUXILIARY_FILES = {"index.md"}


class GenerationError(RuntimeError):
    """Raised when a source selector or generated tree is unsafe to use."""


@dataclass(frozen=True)
class SliceSelection:
    """One source range selected by a stable heading or text marker."""

    slice_id: str
    title: str
    source_heading: str
    start_heading: str | None = None
    start_marker: str | None = None
    end_heading: str | None = None
    end_marker: str | None = None
    start_occurrence: int | None = None
    end_occurrence: int | None = None


def sha256_bytes(value: bytes) -> str:
    """Return a lowercase SHA-256 digest."""
    return hashlib.sha256(value).hexdigest()


def yaml_string(value: str) -> str:
    """Encode a string as a portable, single-line YAML scalar."""
    return json.dumps(value, ensure_ascii=False)


def load_spec(path: Path) -> tuple[str, list[SliceSelection]]:
    """Load and validate the deterministic slice selection spec."""
    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GenerationError(f"cannot read spec {path}: {exc}") from exc

    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION:
        raise GenerationError(
            f"{path}: expected JSON schema_version={SCHEMA_VERSION}"
        )
    source = data.get("source")
    raw_slices = data.get("slices")
    if not isinstance(source, str) or not source:
        raise GenerationError(f"{path}: source must be a non-empty string")
    if not isinstance(raw_slices, list) or not raw_slices:
        raise GenerationError(f"{path}: slices must be a non-empty list")

    selections: list[SliceSelection] = []
    seen: set[str] = set()
    for index, raw in enumerate(raw_slices, start=1):
        if not isinstance(raw, dict):
            raise GenerationError(f"{path}: slices[{index}] must be an object")
        required = ("id", "title", "source_heading")
        if any(not isinstance(raw.get(key), str) or not raw[key] for key in required):
            raise GenerationError(
                f"{path}: slices[{index}] needs non-empty id, title, source_heading"
            )
        slice_id = raw["id"]
        if slice_id in seen:
            raise GenerationError(f"{path}: duplicate slice id {slice_id!r}")
        seen.add(slice_id)

        starts = [raw.get("start_heading"), raw.get("start_marker")]
        ends = [raw.get("end_heading"), raw.get("end_marker")]
        if sum(value is not None for value in starts) != 1:
            raise GenerationError(
                f"{path}: {slice_id}: choose exactly one start_heading/start_marker"
            )
        if sum(value is not None for value in ends) > 1:
            raise GenerationError(
                f"{path}: {slice_id}: choose at most one end_heading/end_marker"
            )
        if any(value is not None and (not isinstance(value, str) or not value) for value in starts + ends):
            raise GenerationError(f"{path}: {slice_id}: selectors must be strings")
        for field in ("start_occurrence", "end_occurrence"):
            value = raw.get(field)
            if value is not None and (
                isinstance(value, bool) or not isinstance(value, int) or value < 1
            ):
                raise GenerationError(
                    f"{path}: {slice_id}: {field} must be a positive integer"
                )

        selections.append(
            SliceSelection(
                slice_id=slice_id,
                title=raw["title"],
                source_heading=raw["source_heading"],
                start_heading=raw.get("start_heading"),
                start_marker=raw.get("start_marker"),
                end_heading=raw.get("end_heading"),
                end_marker=raw.get("end_marker"),
                start_occurrence=raw.get("start_occurrence"),
                end_occurrence=raw.get("end_occurrence"),
            )
        )
    return source, selections


def unique_heading_index(
    lines: list[str],
    title: str,
    label: str,
    occurrence: int | None = None,
) -> int:
    """Find exactly one Markdown heading with the given visible title."""
    pattern = re.compile(r"^#{1,6}\s+" + re.escape(title) + r"\s*$")
    matches = [index for index, line in enumerate(lines) if pattern.match(line)]
    if occurrence is None and len(matches) != 1:
        raise GenerationError(
            f"{label} {title!r} matched {len(matches)} headings; expected exactly 1"
        )
    if occurrence is not None and len(matches) < occurrence:
        raise GenerationError(
            f"{label} {title!r} matched {len(matches)} headings; "
            f"cannot select occurrence {occurrence}"
        )
    return matches[(occurrence or 1) - 1]


def unique_marker_index(
    lines: list[str],
    marker: str,
    label: str,
    after: int = -1,
    occurrence: int | None = None,
) -> int:
    """Find exactly one line containing marker after the supplied line index."""
    matches = [
        index
        for index, line in enumerate(lines)
        if index > after and marker in line
    ]
    if occurrence is None and len(matches) != 1:
        raise GenerationError(
            f"{label} {marker!r} matched {len(matches)} lines after {after}; expected exactly 1"
        )
    if occurrence is not None and len(matches) < occurrence:
        raise GenerationError(
            f"{label} {marker!r} matched {len(matches)} lines after {after}; "
            f"cannot select occurrence {occurrence}"
        )
    return matches[(occurrence or 1) - 1]


def resolve_range(lines: list[str], selection: SliceSelection) -> tuple[int, int]:
    """Resolve one selection to inclusive 1-based source lines."""
    if selection.start_heading is not None:
        start = unique_heading_index(
            lines,
            selection.start_heading,
            "start_heading",
            selection.start_occurrence,
        )
    else:
        assert selection.start_marker is not None
        start = unique_marker_index(
            lines,
            selection.start_marker,
            "start_marker",
            occurrence=selection.start_occurrence,
        )

    if selection.end_heading is not None:
        end = unique_heading_index(
            lines,
            selection.end_heading,
            "end_heading",
            selection.end_occurrence,
        )
    elif selection.end_marker is not None:
        end = unique_marker_index(
            lines,
            selection.end_marker,
            "end_marker",
            after=start,
            occurrence=selection.end_occurrence,
        )
    else:
        end = len(lines)

    if end <= start:
        raise GenerationError(
            f"{selection.slice_id}: end selector resolves before start selector"
        )
    return start, end


def render_slice(
    source_rel: str,
    source_hash: str,
    lines: list[str],
    selection: SliceSelection,
) -> tuple[str, dict[str, Any]]:
    """Render a slice and return its content plus manifest record."""
    start, end = resolve_range(lines, selection)
    excerpt = "\n".join(lines[start:end]).rstrip("\n") + "\n"
    slice_hash = sha256_bytes(excerpt.encode("utf-8"))
    source_lines = [start + 1, end]
    output_name = f"{selection.slice_id}.md"
    origin_locator = f"{source_rel}:{source_lines[0]}-{source_lines[1]}"

    content = "\n".join(
        [
            "---",
            "type: source-slice",
            f"title: {yaml_string(selection.title)}",
            "generated: true",
            f"origin: {yaml_string(source_rel)}",
            f"origin_hash: {source_hash}",
            f"source_lines: {json.dumps(source_lines)}",
            f"source_heading: {yaml_string(selection.source_heading)}",
            f"slice_hash: {slice_hash}",
            f"generator: {yaml_string(f'scripts/generate_source_slices.py@{SCRIPT_VERSION}')}",
            "---",
            "",
            "<!-- GENERATED FILE: do not edit by hand. -->",
            "",
            f"# {selection.title}",
            "",
            "## Source excerpt",
            "",
            excerpt.rstrip("\n"),
            "",
            "## Provenance",
            "",
            f"- Origin: `{origin_locator}`",
            f"- Origin hash: `{source_hash}`",
            "- Regenerate with `python scripts/generate_source_slices.py`.",
            "",
        ]
    )
    record = {
        "id": selection.slice_id,
        "path": output_name,
        "title": selection.title,
        "source_heading": selection.source_heading,
        "source_lines": source_lines,
        "slice_hash": slice_hash,
    }
    return content, record


def build_outputs(
    source_path: Path,
    spec_path: Path,
    output_dir: Path,
) -> tuple[dict[str, str], str]:
    """Build expected slice files and deterministic manifest text."""
    source_rel, selections = load_spec(spec_path)
    resolved_source = source_path.resolve()
    declared_source = Path(source_rel).resolve()
    if declared_source != resolved_source:
        raise GenerationError(
            f"spec source {source_rel!r} does not resolve to {source_path}"
        )
    try:
        raw = source_path.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise GenerationError(f"cannot read UTF-8 source {source_path}: {exc}") from exc

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.splitlines()
    source_hash = sha256_bytes(raw)
    files: dict[str, str] = {}
    records: list[dict[str, Any]] = []
    for selection in selections:
        content, record = render_slice(source_rel, source_hash, lines, selection)
        name = record["path"]
        if name in files:
            raise GenerationError(f"duplicate generated path {name}")
        files[name] = content
        records.append(record)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated": True,
        "generator": {
            "name": "scripts/generate_source_slices.py",
            "version": SCRIPT_VERSION,
        },
        "origin": {
            "path": source_rel,
            "hash": source_hash,
            "byte_count": len(raw),
            "line_count": len(lines),
        },
        "slices": records,
    }
    files["manifest.json"] = json.dumps(
        manifest, ensure_ascii=False, indent=2, sort_keys=False
    ) + "\n"
    return files, source_hash


def actual_files(output_dir: Path) -> set[str]:
    """Return all file paths below output_dir as POSIX relative paths."""
    if not output_dir.exists():
        return set()
    return {
        path.relative_to(output_dir).as_posix()
        for path in output_dir.rglob("*")
        if path.is_file()
    }


def compare_outputs(output_dir: Path, expected: dict[str, str]) -> list[str]:
    """Describe generated-tree drift without modifying it."""
    problems: list[str] = []
    expected_names = set(expected)
    actual = actual_files(output_dir)
    managed_actual = actual - EXTERNAL_AUXILIARY_FILES
    for extra in sorted(managed_actual - expected_names):
        problems.append(f"unexpected generated file: {output_dir / extra}")
    for missing in sorted(expected_names - actual):
        problems.append(f"missing generated file: {output_dir / missing}")
    for name in sorted(expected_names & actual):
        actual = (output_dir / name).read_text(encoding="utf-8")
        if actual != expected[name]:
            problems.append(f"stale generated file: {output_dir / name}")
    return problems


def write_outputs(output_dir: Path, expected: dict[str, str]) -> None:
    """Write only the exact generated files; never delete existing files."""
    existing = actual_files(output_dir)
    extra = sorted(existing - EXTERNAL_AUXILIARY_FILES - set(expected))
    if extra:
        joined = ", ".join(extra)
        raise GenerationError(
            f"refusing to write with unexpected files in {output_dir}: {joined}"
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, content in expected.items():
        path = output_dir / name
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            path.write_text(content, encoding="utf-8", newline="\n")


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("kb/Notes/OKF-rag/okf-rag.md"),
        help="workspace-relative Markdown source",
    )
    parser.add_argument(
        "--spec",
        type=Path,
        default=Path("scripts/source_slice_specs/okf-rag.json"),
        help="JSON selector specification",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("kb/Notes/OKF-rag/_slices/okf-rag"),
        help="generated output directory",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="check the generated tree without writing files",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Generate or check one deterministic source-slice tree."""
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        expected, source_hash = build_outputs(
            args.source, args.spec, args.output
        )
        if args.check:
            problems = compare_outputs(args.output, expected)
            if problems:
                for problem in problems:
                    print(f"FAIL: {problem}")
                return 1
            print(
                f"OK: {len(expected) - 1} slices + manifest current; "
                f"origin_hash={source_hash}"
            )
            return 0
        write_outputs(args.output, expected)
        print(
            f"wrote {len(expected) - 1} slices + manifest to {args.output}; "
            f"origin_hash={source_hash}"
        )
        return 0
    except GenerationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
