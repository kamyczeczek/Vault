#!/usr/bin/env python3
"""Tolerant reader for pi's models.json.

pi writes models.json with trailing commas and stray tab lines on some
platforms, which makes the file unparseable by stdlib json. This loader
normalises those artifacts before parsing so reflection code can depend on
the file without a repair step each time.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path


def _path() -> Path:
    return Path(os.path.expanduser("~")) / ".pi" / "agent" / "models.json"


def load_models(path: Path | None = None) -> dict:
    """Load models.json tolerating trailing commas and whitespace-only lines."""
    p = path or _path()
    text = p.read_text(encoding="utf-8")
    # Strip trailing commas before } or ]
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    # Drop lines that are only whitespace (pi emits stray tab lines)
    text = "\n".join(line for line in text.splitlines() if line.strip())
    return json.loads(text)


def resolve_endpoint(provider: str | None = None, model: str | None = None) -> tuple[str, str, str]:
    """Return (api_key, base_url, model_id) from the current session's config.

    Reads PI_PROVIDER / PI_MODEL from the environment when set, falling back
    to the first model under the provider.
    """
    data = load_models()
    prov_name = provider or os.environ.get("PI_PROVIDER") or "omniroute"
    prov = data.get("providers", {}).get(prov_name)
    if not prov:
        raise SystemExit(f"provider '{prov_name}' not found in pi models.json")
    api_key = prov.get("apiKey", "")
    base_url = prov.get("baseUrl", "").rstrip("/")
    if not base_url.endswith("/v1"):
        base_url += "/v1"
    model_id = model or os.environ.get("PI_MODEL") or prov["models"][0]["id"]
    return api_key, base_url, model_id