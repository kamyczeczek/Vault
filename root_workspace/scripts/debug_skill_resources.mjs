// Verify which skill resources pi resolves for the workspace, with enabled flags.
import { SettingsManager } from "file:///C:/Users/Mateusz/AppData/Local/hermes/node/node_modules/@earendil-works/pi-coding-agent/dist/core/settings-manager.js";
import { DefaultPackageManager } from "file:///C:/Users/Mateusz/AppData/Local/hermes/node/node_modules/@earendil-works/pi-coding-agent/dist/core/package-manager.js";
import { getAgentDir } from "file:///C:/Users/Mateusz/AppData/Local/hermes/node/node_modules/@earendil-works/pi-coding-agent/dist/config.js";

const cwd = process.argv[2] ?? process.cwd();
const sm = SettingsManager.create(cwd, getAgentDir(), { projectTrusted: true });
const pm = new DefaultPackageManager({ cwd, agentDir: getAgentDir(), settingsManager: sm });
const resolved = await pm.resolve(() => {});
for (const r of resolved.skills ?? []) {
  console.log(`${r.enabled ? "ON " : "OFF"}  [${r.metadata?.scope ?? "?"}/${r.metadata?.origin ?? "?"}] ${r.path}`);
}
console.log("--- trusted:", sm.isProjectTrusted(), "projectSettings skills:", JSON.stringify(sm.getProjectSettings().skills));
