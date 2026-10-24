#!/usr/bin/env python3
"""Przelaczanie providera Cline (aplikacja/CLI) miedzy 4 providerami goose.

Cline trzyma JEDEN aktywny endpoint OpenAI-compatible naraz, wiec "wszystkie
modele jak w goose" oznacza: kazdy z 4 providerow goose jest jednym poleceniem
stad. Modele/bazy/klucze czytane sa ZAWSZE z zywej konfiguracji goose
(config.yaml + custom_providers/*.json + secrets.yaml) — nic nie jest
kopiowane na stale (klucze nigdy nie trafiaja do repo).

Uzycie:
  python agents/cline-switch-provider.py --list
  python agents/cline-switch-provider.py nara|omniroute|9router|google-ai-studio [model]

Jezeli podano [model], uzyty jest on zamiast modelu z goose config.yaml
(przydatne, gdy router wystawia wiecej modeli niz wpisany w goose).

Wymaga ZAMKNIETEJ aplikacji Cline (nadpisuje pliki przy wyjsciu).
Docelowo aktualizuje: providers.json, globalState.json, secrets.json,
models.json w %USERPROFILE%/.cline/data. Poprzedni stan laduje w
agents/backup/cline-data-<znacznik czasu>/.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

import yaml

WORKSPACE = Path(__file__).resolve().parent.parent
CLINE_DATA = Path.home() / ".cline" / "data"
GOOSE_CFG = Path.home() / "AppData" / "Roaming" / "Block" / "goose" / "config" / "config.yaml"
GOOSE_SECRETS = Path.home() / "AppData" / "Roaming" / "Block" / "goose" / "config" / "secrets.yaml"
CUSTOM_PROVIDERS = Path.home() / ".config" / "goose" / "custom_providers"

CLINE_FILES = ["globalState.json", "secrets.json",
               "settings/providers.json", "settings/models.json"]


def load_goose_providers() -> dict:
    cfg = yaml.safe_load(GOOSE_CFG.read_text(encoding="utf-8")) or {}
    secrets = yaml.safe_load(GOOSE_SECRETS.read_text(encoding="utf-8")) or {}
    out = {}
    for name, entry in (cfg.get("providers") or {}).items():
        cp_file = CUSTOM_PROVIDERS / f"{name}.json"
        if not cp_file.exists():
            continue
        cp = json.loads(cp_file.read_text(encoding="utf-8"))
        key_env = cp.get("api_key_env", "")
        key = secrets.get(key_env) or os.environ.get(key_env)
        model = (entry or {}).get("model", "")
        ctx = 262144
        for m in cp.get("models", []):
            if m.get("name") == model:
                ctx = m.get("context_limit", ctx)
                break
        out[name] = {"base": cp.get("base_url", ""), "model": model,
                     "key_env": key_env, "key": key, "ctx": ctx,
                     "enabled": bool((entry or {}).get("enabled", True))}
    return out


def switch(name: str, providers: dict, model_override: str = "") -> None:
    if name not in providers:
        sys.exit(f"Nieznany provider '{name}'. Dostepne: {', '.join(sorted(providers))}")
    sel = providers[name]
    if not sel["key"]:
        sys.exit(f"Brak klucza {sel['key_env']} w secrets.yaml ani w env — nie przełączam.")
    model = model_override or sel["model"]
    if not model or not sel["base"]:
        sys.exit(f"Provider '{name}' nie ma modelu/bazy w konfiguracji goose.")

    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    bak = WORKSPACE / "agents" / "backup" / f"cline-data-{stamp}"
    bak.mkdir(parents=True, exist_ok=True)
    for f in CLINE_FILES:
        src = CLINE_DATA / f
        if src.exists():
            shutil.copy2(src, bak / f.replace("/", "__"))

    base, model, key, ctx = sel["base"], model, sel["key"], sel["ctx"]

    pp = CLINE_DATA / "settings" / "providers.json"
    p = json.loads(pp.read_text(encoding="utf-8"))
    slot = p["providers"].setdefault("openai-compatible", {"settings": {}})
    slot["settings"].update({"provider": "openai-compatible", "apiKey": key,
                             "model": model, "baseUrl": base, "headers": {},
                             "reasoning": {"enabled": False}})
    slot["updatedAt"] = datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    p["lastUsedProvider"] = "openai-compatible"
    pp.write_text(json.dumps(p, indent=2, ensure_ascii=False), encoding="utf-8")

    gp = CLINE_DATA / "globalState.json"
    g = json.loads(gp.read_text(encoding="utf-8"))
    g["openAiBaseUrl"] = base
    g["openAiModelId"] = model
    g["planModeOpenAiModelId"] = model
    g["actModeOpenAiModelId"] = model
    gp.write_text(json.dumps(g, indent=2, ensure_ascii=False), encoding="utf-8")

    sp = CLINE_DATA / "secrets.json"
    sec = json.loads(sp.read_text(encoding="utf-8"))
    sec["openAiApiKey"] = key
    sp.write_text(json.dumps(sec, indent=2, ensure_ascii=False), encoding="utf-8")

    mp = CLINE_DATA / "settings" / "models.json"
    m = json.loads(mp.read_text(encoding="utf-8"))
    entry = m["providers"].setdefault("openai-compatible", {"provider": {}, "models": {}})
    entry["provider"].update({"name": "OpenAI Compatible", "baseUrl": base,
                              "defaultModelId": model})
    entry["models"] = {model: {"id": model, "name": model, "contextWindow": ctx,
                               "maxInputTokens": ctx,
                               "capabilities": ["streaming", "tools", "images"]}}
    mp.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Cline -> {name}: {model} @ {base} (klucz {sel['key_env']}, len={len(key)})")
    print(f"Backup poprzedniego stanu: {bak}")


def main() -> None:
    providers = load_goose_providers()
    if len(sys.argv) == 2 and sys.argv[1] == "--list":
        cfg = yaml.safe_load(GOOSE_CFG.read_text(encoding="utf-8")) or {}
        active = cfg.get("active_provider", "?")
        for name in sorted(providers):
            s = providers[name]
            mark = " [aktywny w goose]" if name == active else ""
            key_state = f"klucz {s['key_env']}: {'OK' if s['key'] else 'BRAK'}"
            print(f"{name}{mark}: {s['model']} @ {s['base']} ({key_state})")
        return
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    switch(sys.argv[1], providers, sys.argv[2] if len(sys.argv) == 3 else "")


if __name__ == "__main__":
    main()
