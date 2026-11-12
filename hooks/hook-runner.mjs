/**
 * Stable exec-form entrypoint for the plugin's hooks.
 * No shell interpolation, generated code, downloads, or npm install is needed.
 * Implementations remain bundled beside this file for source/security review.
 * Node is already required by AID; Python and Git Bash requirements are unchanged.
 */
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const hooks = {
  'session-start': ['python', 'aid_hooks.py', '--event', 'SessionStart'],
  'phase-gate-write': ['python', 'aid_hooks.py', '--event', 'PreToolUse', '--action', 'phase_gate_write'],
  'phase-gate-bash': ['python', 'aid_hooks.py', '--event', 'PreToolUse', '--action', 'phase_gate_bash'],
  'plan-approved': ['bash', 'plan-execution-pipeline.sh'],
  'stop-pipeline': ['bash', 'dev-pipeline-gate.sh'],
  'stop-qa': ['python', 'validate-qa-gate.py'],
};
const spec = hooks[process.argv[2]];
if (!spec || process.argv.length !== 3) {
  console.error('AID hook runner: expected a known hook name.');
  process.exit(2);
}
const [runtime, file, ...args] = spec;
const script = fileURLToPath(new URL(file, import.meta.url));
const candidates = runtime === 'python' ? ['python3', 'python'] : ['bash'];
for (const executable of candidates) {
  // Git Bash accepts forward-slash Windows paths, without shell quoting.
  const path = runtime === 'bash' ? script.replaceAll('\\', '/') : script;
  const result = spawnSync(executable, [path, ...args], {
    stdio: 'inherit', shell: false, windowsHide: true,
  });
  if (result.error?.code === 'ENOENT') continue;
  if (result.error) {
    console.error(`AID hook runner: ${result.error.message}`);
    process.exit(1);
  }
  process.exit(result.status ?? 1);
}
console.error(`AID hook runner: required ${runtime} runtime not found on PATH.`);
process.exit(1);
