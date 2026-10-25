#!/usr/bin/env python3
"""Small OpenAI-compatible DeepSeek harness with append-only session logging.

The harness deliberately does not inspect DeepSeek Desktop cookies or IndexedDB.
Provider credentials are read from environment variables and never written to logs.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

HOME = Path.home() / ".deepseek-harness"
CONFIG = HOME / "config.json"
SESSIONS = HOME / "sessions"

DEFAULT_PROVIDERS = {
    "omniroute": {"base_url": "http://localhost:20128/v1", "model": "openai/cx/gpt-5.6-luna-low", "api_key_env": "OMNIROUTE_API_KEY", "api": "chat"},
    "nara": {"base_url": "https://api.nara.ai/v1", "model": "agnes-3-flash", "api_key_env": "NARA_API_KEY", "api": "chat"},
    "9router": {"base_url": "https://api.9router.com/v1", "model": "kr/claude-haiku-4.5", "api_key_env": "ROUTER9_API_KEY", "api": "chat"},
    "google-ai-studio": {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai", "model": "gemini-3.7-flash", "api_key_env": "GOOGLE_AI_STUDIO_API_KEY", "api": "chat"},
}


def ensure_config() -> dict:
    HOME.mkdir(parents=True, exist_ok=True)
    SESSIONS.mkdir(parents=True, exist_ok=True)
    if not CONFIG.exists():
        CONFIG.write_text(json.dumps({"providers": DEFAULT_PROVIDERS, "active_provider": "omniroute"}, indent=2), encoding="utf-8")
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def log_event(path: Path, session_id: str, provider: str, model: str, role: str, content: str) -> None:
    event = {"session_id": session_id, "timestamp": datetime.now(timezone.utc).isoformat(), "provider": provider, "model": model, "role": role, "content": content}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def request_completion(provider: str, settings: dict, messages: list[dict]) -> str:
    key = os.environ.get(settings["api_key_env"], "")
    if not key:
        raise SystemExit(f"Missing environment variable: {settings['api_key_env']}")
    url = settings["base_url"].rstrip("/") + "/chat/completions"
    body = json.dumps({"model": settings["model"], "messages": messages}).encode()
    req = Request(url, data=body, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urlopen(req, timeout=180) as response:
        data = json.load(response)
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise RuntimeError(f"Unexpected response from provider {provider}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="DeepSeek-compatible agent harness")
    parser.add_argument("prompt", nargs="?", help="user prompt")
    parser.add_argument("--provider", default=None)
    parser.add_argument("--session", default=None)
    parser.add_argument("--system", default="You are a helpful coding agent.")
    parser.add_argument("--list-providers", action="store_true")
    args = parser.parse_args()
    config = ensure_config()
    if args.list_providers:
        for name, item in config["providers"].items():
            print(f"{name}: {item['model']} ({item['api']})")
        return 0
    if not args.prompt:
        parser.error("prompt is required unless --list-providers is used")
    provider = args.provider or config["active_provider"]
    settings = config["providers"][provider]
    sid = args.session or uuid.uuid4().hex
    path = SESSIONS / f"{sid}.jsonl"
    messages = [{"role": "system", "content": args.system}, {"role": "user", "content": args.prompt}]
    log_event(path, sid, provider, settings["model"], "user", args.prompt)
    answer = request_completion(provider, settings, messages)
    log_event(path, sid, provider, settings["model"], "assistant", answer)
    print(answer)
    return 0


if __name__ == "__main__":
    sys.exit(main())
