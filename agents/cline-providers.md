---
type: Concept
title: cline-providers
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# Cline (aplikacja `Local\Cline` / CLI, config `~/.cline/data`, 2026-10-11)

Aktywny provider = **nara** (jak `active_provider` w goose
`%APPDATA%\Block\goose\config\config.yaml`).
Cline trzyma JEDEN aktywny endpoint OpenAI-compatible naraz — pliki:

- `~/.cline/data/settings/providers.json` — profil `openai-compatible`
  (`baseUrl` / `model` / `apiKey`, `lastUsedProvider`)
- `~/.cline/data/globalState.json` — `openAiBaseUrl`, `openAiModelId`,
  `planModeOpenAiModelId`, `actModeOpenAiModelId`
  (wyboru typu providera `planModeApiProvider`/`actModeApiProvider` nie ruszano)
- `~/.cline/data/secrets.json` — `openAiApiKey`
- `~/.cline/data/settings/models.json` — cache modelu (context window)

Klucze API pochodzą z tego samego źródła co goose (`secrets.yaml` / env) —
NIE wklejaj kluczy do tego pliku.

| Provider (goose) | baseUrl | model | Klucz z |
|---|---|---|---|
| **nara** (aktywny) | `https://router.bynara.id/v1` | `agnes-2.5-flash` (ctx 262144) | `NARA_API_KEY` |
| omniroute | `http://localhost:20128/v1` | `gemini/gemini-3.8-flash` | `OMNIROUTE_API_KEY` |
| 9router | `http://localhost:20128/v1` | `kr/claude-haiku-4.5` | `ROUTER9_API_KEY` |
| google-ai-studio | `https://generativelanguage.googleapis.com/v1beta/openai` | `gemini-3.7-flash` | `GOOGLE_AI_STUDIO_API_KEY` |

Modele/bazy z `~/.config/goose/custom_providers/*.json` + `providers:` w goose
`config.yaml`. Przełączenie providera = podmiana 4 plików powyżej + restart
aplikacji Cline. Backup sprzed zmiany: `agents/backup/cline-data-2026-10-11/`.

## Przełącznik (wszystkie 4 jak w goose)

Cline trzyma JEDEN aktywny endpoint naraz, więc 4 providery goose są
dostępne jednym poleceniem (przy ZAMKNIĘTEJ aplikacji Cline):

```powershell
python agents\cline-switch-provider.py --list       # pokaż 4 jak w goose
python agents\cline-switch-provider.py omniroute   # gemini/gemini-3.8-flash
python agents\cline-switch-provider.py nara        # agnes-2.5-flash (aktywny w goose)
python agents\cline-switch-provider.py 9router     # kr/claude-haiku-4.5
python agents\cline-switch-provider.py google-ai-studio  # gemini-3.7-flash
```

Skrypt czyta modele/bazy/klucze ZAWSZE z żywej konfiguracji goose
(`config.yaml` + `custom_providers/*.json` + `secrets.yaml`), więc zmiana
modelu w goose automatycznie obowiązuje przy następnym przełączeniu.
Przed każdym przełączeniem robi backup do `agents/backup/cline-data-<data>/`.
