#!/usr/bin/env node
// ---------------------------------------------------------------------------------
// AID - project-mode hook registration (T16 I-9, owner decision E1)
//
// WHY: a project linked with link-project.sh/.bat must get the same enforcement as the
// plugin. Before T16 the linker copied a settings.json that registered only the legacy
// Stop/PostToolUse shell lines and no PreToolUse gate at all, so a clone + link install
// ran with no phase gate.
// WHAT: reads .claude-plugin/plugin.json `hooks` (the one source of truth) and merges each
// hook into <target>/.claude/settings.json, with ${CLAUDE_PLUGIN_ROOT} replaced by the
// AID install's absolute real path (forward slashes). The exec form (command + args, no
// shell) means paths with spaces and apostrophes need no quoting.
// CONNECTION: called by link-project.sh and link-project.bat (they never write hook JSON
// themselves). No dependencies.
//
// Usage: node scripts/link-settings.mjs <target-project> <aid-install>
// Exit 0 on success (prints what it did); != 0 with the reason, the file left untouched.
// ---------------------------------------------------------------------------------
import fs from 'node:fs';
import path from 'node:path';

const EVENTS = ['SessionStart', 'PreToolUse', 'PostToolUse', 'Stop'];
const RUNNER_TAIL = '/hooks/hook-runner.mjs';
// Legacy AID entries (pre-T16 settings.json) -> the runner hook that replaces them.
const LEGACY = [
  [/\.claude\/hooks\/plan-execution-pipeline\.sh/, 'plan-approved'],
  [/\.claude\/hooks\/dev-pipeline-gate\.sh/, 'stop-pipeline'],
  [/\.claude\/hooks\/validate-qa-gate\.py/, 'stop-qa'],
];
const BOMS = [
  [Buffer.from([0xff, 0xfe]), 'utf16le'],
  [Buffer.from([0xfe, 0xff]), 'utf16be'],
  [Buffer.from([0xef, 0xbb, 0xbf]), 'utf8'],
];

function die(msg) {
  process.stderr.write('[ERROR] link-settings: ' + msg + '\n');
  process.exit(1);
}

function decode(buf, codec) {
  if (codec === 'utf16be') {
    const sw = Buffer.from(buf);
    sw.swap16();
    return sw.toString('utf16le');
  }
  return buf.toString(codec);
}

function encode(text, codec) {
  if (codec === 'utf16be') return Buffer.from(text, 'utf16le').swap16();
  return Buffer.from(text, codec);
}

// Same encodings as aid_guard.read_settings (AC-44): UTF-8 with or without BOM,
// UTF-16 LE/BE with BOM. The writer keeps the file's own BOM and codec.
function readSettings(file) {
  const raw = fs.readFileSync(file);
  const hit = BOMS.find(([b]) => raw.subarray(0, b.length).equals(b));
  const bom = hit ? hit[0] : Buffer.alloc(0);
  const codec = hit ? hit[1] : 'utf8';
  const text = decode(raw.subarray(bom.length), codec);
  return { data: JSON.parse(text), bom, codec, raw };
}

const isObj = (v) => v !== null && typeof v === 'object' && !Array.isArray(v);

// An entry is AID's by its runner path (any AID install's hooks/hook-runner.mjs) plus its
// hook name (args[1]); a legacy shell line is AID's by the script it runs.
function aidName(hook, names) {
  if (!isObj(hook)) return null;
  const args = hook.args;
  if (Array.isArray(args) && typeof args[0] === 'string' && typeof args[1] === 'string') {
    const runner = args[0].replace(/\\/g, '/');
    if ((runner.endsWith(RUNNER_TAIL) || runner === RUNNER_TAIL.slice(1)) && names.has(args[1])) {
      return args[1];
    }
  }
  if (typeof hook.command === 'string') {
    const cmd = hook.command.replace(/\\/g, '/');
    for (const [re, name] of LEGACY) if (re.test(cmd)) return name;
  }
  return null;
}

function main() {
  const [targetArg, aidArg] = process.argv.slice(2);
  if (!targetArg || !aidArg) die('usage: node link-settings.mjs <target-project> <aid-install>');
  if (!fs.existsSync(targetArg) || !fs.statSync(targetArg).isDirectory()) {
    die('target is not a folder: ' + targetArg);
  }
  let aidReal;
  try {
    aidReal = fs.realpathSync.native(aidArg).replace(/\\/g, '/');
  } catch (e) {
    die('cannot resolve the AID install path ' + aidArg + ': ' + e.message);
  }
  const plugin = path.join(aidArg, '.claude-plugin', 'plugin.json');
  let pluginHooks;
  try {
    pluginHooks = JSON.parse(fs.readFileSync(plugin, 'utf8')).hooks;
  } catch (e) {
    die('cannot read ' + plugin + ': ' + e.message);
  }
  if (!isObj(pluginHooks)) die(plugin + ' has no hooks object');

  // The generated groups: plugin.json's, with only ${CLAUDE_PLUGIN_ROOT} in args replaced.
  const want = {};          // event -> [{matcher?, hooks: [...]}]
  const byName = {};        // hook name -> {event, matcher, hook}
  for (const event of EVENTS) {
    const groups = pluginHooks[event];
    if (!Array.isArray(groups)) continue;
    want[event] = groups.map((g) => {
      const out = {};
      if ('matcher' in g) out.matcher = g.matcher;
      out.hooks = g.hooks.map((h) => {
        const copy = JSON.parse(JSON.stringify(h));
        copy.args = (copy.args || []).map((a) => a.split('${CLAUDE_PLUGIN_ROOT}').join(aidReal));
        byName[copy.args[1]] = { event, matcher: g.matcher, hook: copy };
        return copy;
      });
      return out;
    });
  }
  const names = new Set(Object.keys(byName));

  const settingsDir = path.join(targetArg, '.claude');
  const file = path.join(settingsDir, 'settings.json');
  let data, bom = Buffer.alloc(0), codec = 'utf8', before = null;
  if (fs.existsSync(file)) {
    try {
      ({ data, bom, codec, raw: before } = readSettings(file));
    } catch (e) {
      die(file + ' cannot be parsed, so it was not changed (' + e.message +
          '). Fix or remove it, then run link-project again.');
    }
    if (!isObj(data)) die(file + ' is not a JSON object, so it was not changed.');
    if ('hooks' in data && !isObj(data.hooks)) die(file + ': "hooks" is not an object, so it was not changed.');
  } else {
    // A new file starts from the AID settings template's permissions block.
    data = {};
    try {
      const tmpl = JSON.parse(fs.readFileSync(path.join(aidArg, '.claude', 'settings.json'), 'utf8'));
      if (isObj(tmpl.permissions)) data.permissions = tmpl.permissions;
    } catch (e) {
      // No template: hooks only.
    }
  }

  const hooks = data.hooks || (data.hooks = {});
  const placed = new Set();
  for (const event of EVENTS) {
    if (!want[event]) continue;
    const groups = hooks[event];
    if (groups !== undefined && !Array.isArray(groups)) {
      die(file + ': hooks.' + event + ' is not a list, so it was not changed.');
    }
    const kept = [];
    for (const g of groups || []) {
      if (!isObj(g) || !Array.isArray(g.hooks)) { kept.push(g); continue; }
      let touched = false;
      const out = [];
      for (const h of g.hooks) {
        const name = aidName(h, names);
        if (!name) { out.push(h); continue; }
        touched = true;
        const spec = byName[name];
        // Replace in place only once, in the event and matcher plugin.json gives it: a
        // narrowed matcher would weaken the gate, so that copy is replaced, not kept.
        if (spec.event === event && g.matcher === spec.matcher && !placed.has(name)) {
          out.push(spec.hook);
          placed.add(name);
        }
      }
      if (touched && out.length === 0) continue;   // the group held only AID entries
      kept.push(touched ? Object.assign({}, g, { hooks: out }) : g);
    }
    for (const g of want[event]) {
      const missing = g.hooks.filter((h) => !placed.has(h.args[1]));
      if (!missing.length) continue;
      missing.forEach((h) => placed.add(h.args[1]));
      kept.push(Object.assign({}, g, { hooks: missing }));
    }
    hooks[event] = kept;
  }

  const eol = before && decode(before.subarray(bom.length), codec).includes('\r\n') ? '\r\n' : '\n';
  const text = JSON.stringify(data, null, 2).replace(/\n/g, eol) + eol;
  const bytes = Buffer.concat([bom, encode(text, codec)]);
  if (before && before.equals(bytes)) {
    process.stdout.write('  [SKIP] .claude/settings.json already registers the AID hooks\n');
    return;
  }
  fs.mkdirSync(settingsDir, { recursive: true });
  const tmp = file + '.aid-tmp';
  fs.writeFileSync(tmp, bytes);
  fs.renameSync(tmp, file);
  process.stdout.write('  [OK] .claude/settings.json registers the AID hooks (' + aidReal + ')\n');
}

main();
