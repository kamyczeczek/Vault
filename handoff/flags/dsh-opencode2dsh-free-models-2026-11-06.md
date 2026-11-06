---
flag: dsh-opencode2dsh-free-models-2026-11-06
since: 2026-11-06
owner: mateusz
agent: deepseek-harness
model: nvidia/stepfun-ai/step-5-preview
---

`flag` — 2026-11-06: darmowe modele OpenCode Zen są teraz dostępne w DeepSeek
Harness (DSH).

Przyczyna, dla której nie były: `@opencode2dsh/dsh-plugin` 0.3.14 był
zainstalowany w `node_modules` profilu desktop (instalacje 2026-11-04 ~22:09,
logi `.plugin-manager/logs/operation-1g8spJ|bODNgh|5vhunk/pnpm.log`), ale NIE
był wymieniony w `dsh.profile.bundles` w
`C:\Users\Mateusz\.dsh\profiles\desktop\package.json` — bundle patch pluginu
(kordis `insert` wiersza `id: opencode2dsh`) nigdy nie był komponowany, więc
cordis nie montował pluginu i dostawca `opencode2dsh` nie istniał w pickerze
modeli. Taki sam objaw miał dzisiejszy `dsh-opencode-free-models` 0.1.0
(instalacja 18:47, log `operation-zR36Bz`, też tylko w dependencies).

Zmiana: dopisano `"@opencode2dsh/dsh-plugin"` do tablicy `dsh.profile.bundles`
w `package.json` profilu desktop (backup: `package.json.bak-20261106-191418`,
`cordis.patch.yml.bak-20261106-191418` — ten drugi bez zmian). Walidacja przed
restartem: JSON parsuje się, bundle patch pluginu daje dokładnie jeden wiersz
`insert` (`id: opencode2dsh`, `name: @opencode2dsh/dsh-plugin`, `config: {}`),
`name` resolwi się z `node_modules` profilu. Mechanizm potwierdzony na
wzorcowym bundle `billion-context` (`dsh.bundle.patch.yml`: "mounted
automatically when the profile's package.json lists … in dsh.profile.bundles").

Obserwacja po zmianie: host DSH (PID 23768, start 19:00:33) podniósł warstwę
pluginu w ciągu ~26 s od edycji — `~/.opencode2dsh/adapter-status.json`
(napisaany 19:14:46 lokalnie) ma `status: ready`, `total: 80`, `exposed: 10`,
`lastError: ""`. Katalog models.dev cache: `agent-config.json.models.dev.json`.

Next step: potwierdź grupę `opencode2dsh` w pickerze modeli GUI; jeśli bieżąca
sesja jej nie widzi (rejestr providerów buduje się przy starcie hosta),
zrestartuj DSH całkowicie (quit + relaunch) i wybierz model `-free`.

not checked:
- widoczność grupy `opencode2dsh` w pickerze modeli w działającej sesji GUI
  (list_subagent_models po zmianie zwraca wciąż tylko `nvidia` — rejestr
  subagentów jest snapshotem z rozpoczęcia sesji 19:00, przed montażem pluginu);
- realne wywołanie modelu free end-to-end z DSH (lane anonimowa Zen, quota
  per-IP, ewentualne 429 przy kontencji);
- drugi plugin `dsh-opencode-free-models` 0.1.0 (panel UI, inny autor) —
  zainstalowany, niewiringowany; decyzja enable/remove niepodjęta.
