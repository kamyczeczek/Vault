#!/usr/bin/env python3
"""Copy the generated did_sessions.md into the Google Drive for desktop folder.

Google Drive for desktop syncs a local folder, so overwriting the local copy
updates the same file on Drive: same fileId, same share link. No API, no OAuth,
no Cloud project, no token that can expire — the sync client does the work.

Target resolution order:
    --target DIR  >  DID_SESSIONS_TARGET  >  auto-detect (a drive root that
    holds a folder named like the synced "My Drive")

Exit codes: 0 ok, 2 target unresolved, 3 source missing, 4 copy/verify failed.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = (
    ROOT / "scripts" / "_scratch" / "sessions" / "02_products" / "did_sessions.md"
)

# Google Drive for desktop names the synced root after the UI language, so the
# detector accepts the common ones rather than assuming English.
DRIVE_DIR_NAMES = (
    "My Drive",
    "Mój Dysk",
    "Mi unidad",
    "Mon Drive",
    "Il mio Drive",
    "Mein Drive",
)

EXIT_OK = 0
EXIT_TARGET = 2
EXIT_SOURCE = 3
EXIT_COPY = 4


def fail(code: int, message: str) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)
    raise SystemExit(code)


def md5_of(path: Path, chunk: int = 1 << 20) -> str:
    digest = hashlib.md5()
    with open(path, "rb") as handle:
        while block := handle.read(chunk):
            digest.update(block)
    return digest.hexdigest()


def drive_roots():
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        root = Path(f"{letter}:\\")
        if root.is_dir():
            yield root


def candidates():
    """Every folder that looks like a Google Drive for desktop mount."""
    found = []
    for root in drive_roots():
        for name in DRIVE_DIR_NAMES:
            folder = root / name
            if folder.is_dir():
                found.append(folder)
    return found


def resolve_target(cli_value: str | None, filename: str | None = None) -> Path:
    for candidate in (cli_value, os.environ.get("DID_SESSIONS_TARGET")):
        if candidate and candidate.strip():
            return Path(candidate.strip())
    found = candidates()
    if len(found) == 1:
        return found[0]
    if not found:
        fail(
            EXIT_TARGET,
            "nie znalazłem folderu Google Drive dla komputerów. Zainstaluj program "
            "i zaloguj się, potem sprawdź: python scripts\\sync_did_sessions.py --detect "
            '(albo podaj cel: --target "G:\\My Drive" albo zmienna DID_SESSIONS_TARGET)',
        )
    if filename:
        with_file = [f for f in found if (f / filename).is_file()]
        if len(with_file) == 1:
            return with_file[0]
    listed = "\n".join(f"    {folder}" for folder in found)
    fail(
        EXIT_TARGET,
        "znalazłem kilka kandydatów — wskaż jeden:\n"
        f"{listed}\n"
        '    (--target "..." albo zmienna DID_SESSIONS_TARGET)',
    )


def sync(source: Path, target_dir: Path, dry_run: bool = False) -> Path:
    if not target_dir.is_dir():
        fail(
            EXIT_TARGET,
            f"cel nie jest folderem: {target_dir}\n"
            "    Rozpoznaj go: python scripts\\sync_did_sessions.py --detect",
        )
    destination = target_dir / source.name
    if dry_run:
        print(f"[dry-run] źródło:  {source}")
        print(f"[dry-run] cel:     {destination}")
        return destination

    expected = md5_of(source)
    try:
        shutil.copyfile(source, destination)
    except OSError as exc:
        fail(
            EXIT_COPY,
            f"nie mogę zapisać {destination}: {exc}\n"
            "    Sprawdź, że program Google Drive dla komputerów działa i że plik "
            "nie jest zablokowany (np. otwarty w edytorze).",
        )

    # A streamed Drive file can lag a beat behind the local write; verify with retry.
    for attempt in range(5):
        try:
            if md5_of(destination) == expected:
                return destination
        except OSError:
            pass
        if attempt + 1 < 5:
            time.sleep(1)

    fail(
        EXIT_COPY,
        "zapisane bajty nie zgadzają się ze źródłem — nie potwierdzono synchronizacji\n"
        f"    źródło: {source} (md5={expected})\n"
        f"    cel:    {destination} (md5={md5_of(destination) if destination.exists() else 'brak'})",
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Skopiuj did_sessions.md do folderu Google Drive dla komputerów (ten sam plik, ten sam link)."
    )
    parser.add_argument("file", nargs="?", default=str(DEFAULT_SOURCE), help="plik źródłowy")
    parser.add_argument("--target", default=None, help="folder docelowy na Drive")
    parser.add_argument(
        "--detect",
        action="store_true",
        help="tylko pokaż dyski i rozpoznane foldery Google Drive, nic nie kopiuj",
    )
    parser.add_argument("--dry-run", action="store_true", help="pokaż plan bez kopiowania")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.detect:
        print("Dyski i rozpoznane foldery Google Drive dla komputerów:")
        for root in drive_roots():
            marks = [name for name in DRIVE_DIR_NAMES if (root / name).is_dir()]
            print(f"    {root} {'-> ' + ', '.join(marks) if marks else ''}")
        found = candidates()
        print(f"Cel zostałby rozpoznany jako: {found[0] if len(found) == 1 else '(niejednoznaczny)'}")
        return EXIT_OK

    source = Path(args.file)
    if not source.is_file():
        fail(EXIT_SOURCE, f"brak pliku źródłowego: {source}")

    target_dir = resolve_target(args.target, source.name)
    destination = sync(source, target_dir, args.dry_run)
    if args.dry_run:
        return EXIT_OK

    print(f"[ok] skopiowano: {destination}")
    print(f"     {source.stat().st_size} B, md5={md5_of(destination)}")
    print("     Program Google Drive dla komputerów zsynchronizuje to w tle —")
    print("     ten sam plik, ten sam link, bez nowego adresu.")
    return EXIT_OK


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        fail(EXIT_COPY, "przerwane przez użytkownika")
