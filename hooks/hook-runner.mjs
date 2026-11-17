/**
 * Stable exec-form entrypoint for the plugin's hooks.
 * No shell interpolation, generated code, downloads, or npm install is needed.
 * Implementations remain bundled beside this file for source/security review.
 * Node is already required by AID; Python and Git Bash requirements are unchanged.
 *
 * Fail-safe: Claude Code only blocks on exit 2, so for the PreToolUse gates every
 * runner failure (no runtime, stub runtime, spawn error, child exit outside {0,2})
 * exits 2. Other hooks stay non-blocking (exit 1) but say why on stderr.
 */
import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { delimiter, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const hooks = {
  'session-start': ['python', 'aid_hooks.py', '--event', 'SessionStart'],
  'phase-gate-write': ['python', 'aid_hooks.py', '--event', 'PreToolUse', '--action', 'phase_gate_write'],
  'phase-gate-bash': ['python', 'aid_hooks.py', '--event', 'PreToolUse', '--action', 'phase_gate_bash'],
  'plan-approved': ['bash', 'plan-execution-pipeline.sh'],
  'stop-pipeline': ['bash', 'dev-pipeline-gate.sh'],
  'stop-qa': ['python', 'validate-qa-gate.py'],
};
const name = process.argv[2];
// Own keys only: __proto__, constructor, toString are not hook names.
const spec = Object.hasOwn(hooks, name ?? '') ? hooks[name] : undefined;
if (!spec || process.argv.length !== 3) {
  console.error('AID hook runner: expected a known hook name.');
  process.exit(2);
}
const gate = name === 'phase-gate-write' || name === 'phase-gate-bash';
function fail(message) {
  console.error(`AID hook runner (${name}): ${message}` +
    (gate ? ' Blocking this tool call: the AID phase gate fails closed.' : ''));
  process.exit(gate ? 2 : 1);
}

const [runtime, file, ...args] = spec;
const script = fileURLToPath(new URL(file, import.meta.url));
const quiet = { stdio: 'ignore', shell: false, windowsHide: true, timeout: 5000 };

// The Windows Store python3/python stubs exit 9009 instead of ENOENT, so probe each
// candidate and take the first that really runs Python. Nothing is cached.
function resolvePython() {
  return [['python3'], ['python'], ['py', '-3']]
    .find(([exe, ...pre]) => spawnSync(exe, [...pre, '-c', 'import sys'], quiet).status === 0);
}

// On Windows, `bash` on PATH may be WSL (System32) or a WindowsApps stub, neither of
// which can see a C:/ script (rc 127). Prefer Git Bash and refuse those two.
function resolveBash() {
  if (process.platform !== 'win32') return ['bash'];
  const env = process.env;
  const sysRoot = (env.SystemRoot || env.windir || 'C:\\Windows').toLowerCase();
  const refused = (p) => p.toLowerCase().startsWith(sysRoot + '\\') || /\\windowsapps\\/i.test(p);
  const pathDirs = (env.PATH || env.Path || '').split(delimiter).filter(Boolean);
  const roots = [];
  for (const d of pathDirs) {
    // <git>\cmd, <git>\bin, <git>\mingw64\bin all hold git.exe.
    if (existsSync(join(d, 'git.exe'))) roots.push(d, dirname(d), dirname(dirname(d)));
  }
  for (const base of [env.GIT_INSTALL_ROOT, env.ProgramW6432, env.ProgramFiles, env['ProgramFiles(x86)']]) {
    if (base) roots.push(base === env.GIT_INSTALL_ROOT ? base : join(base, 'Git'));
  }
  const found = [
    ...roots.flatMap((r) => [join(r, 'bin', 'bash.exe'), join(r, 'usr', 'bin', 'bash.exe')]),
    ...pathDirs.map((d) => join(d, 'bash.exe')),
  ].find((p) => !refused(p) && existsSync(p));
  return found ? [found] : undefined;
}

const usable = runtime === 'python' ? resolvePython() : resolveBash();
if (!usable) {
  fail(runtime === 'python'
    ? 'no working Python found (tried python3, python, py -3; each must run `-c "import sys"`).'
    : 'Git Bash not found (WSL/System32 and WindowsApps bash are refused). Install Git for Windows.');
}
const [executable, ...prefix] = usable;
// Git Bash accepts forward-slash Windows paths, without shell quoting.
const path = runtime === 'bash' ? script.replaceAll('\\', '/') : script;
const result = spawnSync(executable, [...prefix, path, ...args], {
  stdio: 'inherit', shell: false, windowsHide: true,
});
if (result.error) fail(`could not run ${executable}: ${result.error.message}`);
const status = result.status;
if (gate && status !== 0 && status !== 2) fail(`${file} exited with ${status ?? result.signal}.`);
if (status === null) fail(`${file} was killed by ${result.signal}.`);
process.exit(status);
