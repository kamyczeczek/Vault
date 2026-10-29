"""Override tmp_path to avoid PermissionError on Windows.

pytest's built-in tmp_path iterates ``pytest-of-<user>`` inside ``%TEMP%``
to prune old test runs. On this machine the directory has broken ACLs,
causing PermissionError during collection. Using a plain TemporaryDirectory
side-steps the issue entirely.
"""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest


@pytest.fixture()
def tmp_path() -> Path:  # type: ignore[override]
    with TemporaryDirectory() as td:
        yield Path(td)
