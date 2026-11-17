/** Skill-scoped PreToolUse(Write|Edit|MultiEdit|NotebookEdit) guard for /autoresearch.
 *
 * WHAT IT IS: a guardrail against a score-maximising agent using the four file-edit tools to
 * edit the files that decide its own AR score. It is NOT a sandbox.
 *
 * STRATEGY: protect files by ROLE, not by spelling or location. A file is protected because
 * of what it is (rubric, scorer prompt, AR program, settings, acceptance baseline), matched on
 * its trailing path segments wherever it lives: the project, a junction target, the real AID
 * checkout or the plugin cache. Every rule is checked on the lexical form AND the realpath
 * form, case-folded, so relative paths, `..`, case, links and absolute aliases all land on
 * the same role. The contract (R1-R10) lives in ROLES below.
 *
 * OUT OF SCOPE, and NOT reliably detected today: writes through Bash, python/node
 * subprocesses, git or MCP file tools. verify-run.sh step 8 fingerprints only the criteria
 * YAML and reflection-agent.md, and that hash is self-attested in the runner-writable
 * .aid/pipeline/state.json, so it is not a detector for what this guard misses.
 *
 * SESSION SCOPE: skill-frontmatter hooks stay active for the rest of the Claude Code session
 * after /autoresearch. AR passes therefore cannot edit skills/autoresearch/** or
 * skills/reflection/**; harness edits belong in a new session without /autoresearch.
 *
 * Any malformed input or internal error DENIES (fail closed). Deny uses the nested
 * PreToolUse shape; a bare top-level {permissionDecision} is ignored by Claude Code.
 */
import { basename, dirname, join, resolve } from 'node:path';
import { existsSync, lstatSync, readlinkSync, realpathSync } from 'node:fs';

const SESSION_NOTE = ' This guard stays active for the rest of this Claude Code session; ' +
  'make harness edits in a new session outside an autoresearch pass.';

// Role rules on the case-folded, forward-slash path. `except` lists runner-owned paths the
// rule does not cover; `existing` means the rule applies only when the file already exists.
const ROLES = [
  { id: 'R1 rubric', re: /\/criteria\/[^/]+\.ya?ml$/ },
  { id: 'R2 scorer prompt',
    re: /\/agents\/(reflection-agent|phase4-intent-validator|phase5-acceptance-validator)\.md$/ },
  { id: 'R3 autoresearch skill', re: /\/skills\/autoresearch\// },
  { id: 'R4 reflection skill', re: /\/skills\/reflection\// },
  { id: 'R5 linked skill/agent', re: /\/\.claude\/(skills|agents)\// },
  { id: 'R6 Claude settings', re: /\/\.claude\/settings(\.local)?\.json$/ },
  { id: 'R7 MCP config', re: /\/\.mcp\.json$/ },
  { id: 'R8 AID state/config', re: /\/\.aid\/.*\.json$/,
    // Runner state, AR results, the per-task stage records the agent must write later in the
    // same session (fix-<n>.json, self-review-<n>.json; config.frozen.json is R10's), the QA
    // gate's verdict files (.aid/qa/<id>-review*.json, from the stop-qa hook's flow) and the
    // user-level feedback queue. None of these is read by an AR scorer.
    except: [/\/\.aid\/pipeline\/state\.json$/, /\/\.aid\/pipeline\/autoresearch\//,
      /\/\.aid\/pipeline\/[^/]+\/[^/]+\.json$/, /\/\.aid\/qa\//, /\/\.aid\/feedback\//] },
  // AR-3 reads only .aid/qa/<id>.yaml (program.ar-acceptance.md:90); the QA-gate verdicts in
  // the same folder (<id>-review*.json, <id>.qa-passed) are not acceptance sources.
  { id: 'R9 acceptance source', re: /\/\.aid\/qa\/.*\.ya?ml$/ },
  // Freeze-once artifacts written at pipeline kickoff: creating one is legitimate, overwriting
  // it is not (pipeline-orchestrator/SKILL.md kickoff step 4).
  { id: 'R10 frozen brief/config', re: /\/\.aid\/pipeline\/[^/]+\/(brief\.md|config\.frozen\.json)$/,
    existing: true },
];

function decide(payload) {
  if (process.env.AID_HARNESS_GUARD_TEST_THROW === '1') throw new Error('test seam');
  const ti = payload?.tool_input;
  const raw = ti?.file_path ?? ti?.notebook_path;
  if (typeof raw !== 'string' || raw === '' || raw.includes('\0')) {
    return 'Blocked: hook input has no usable file_path/notebook_path.';
  }
  if (payload.cwd !== undefined && typeof payload.cwd !== 'string') {
    return 'Blocked: hook input cwd is not a string (' + raw + ').';
  }
  const base = payload.cwd || process.env.CLAUDE_PROJECT_DIR || process.cwd();
  const lexical = resolve(base, raw);
  if (process.platform === 'win32') {
    // Win32 aliases: a trailing '.'/' ' on a component is stripped by the OS and 'x::$DATA'
    // writes x itself, so `.mcp.json.` lands on .mcp.json. No legitimate write needs these.
    const parts = lexical.replaceAll('\\', '/').replace(/^[a-z]:/i, '').split('/');
    if (parts.some(c => c.includes(':') || /[. ]$/.test(c))) {
      return 'Blocked: ' + raw + ' uses a Windows path alias (trailing dot/space or ":" stream).';
    }
  }
  // Realpath of the nearest existing ancestor, on every OS: expands symlinks, junctions and
  // 8.3 short names. The catch is deliberately broad (ENOENT expected; EACCES etc. just walk
  // up): the lexical form is always checked too, so a failed resolve can only lose a form.
  // A link whose target does not exist yet (dangling) fails realpath, so it is followed by
  // hand: a Write through it CREATES the target, which must be judged by the target's role.
  let head = lexical, tail = '', real = lexical, hops = 0;
  while (true) {
    try { real = join(realpathSync.native(head), tail); break; } catch {}
    let target = null;
    try { if (lstatSync(head).isSymbolicLink()) target = readlinkSync(head); } catch {}
    if (target !== null) {
      if (++hops > 16) return 'Blocked: ' + raw + ' goes through a link chain that does not resolve.';
      head = resolve(dirname(head), target);
      continue;
    }
    const up = dirname(head);
    if (up === head) break;
    tail = join(basename(head), tail);
    head = up;
  }
  const forms = [lexical, real];
  // ponytail: case-fold on every OS; over-blocks a literal `.AID/` dir on case-sensitive FS (N9).
  const folded = forms.map(p => p.replaceAll('\\', '/').toLowerCase());
  const hit = ROLES.find(r => folded.some(p => r.re.test(p) && !r.except?.some(e => e.test(p)))
    && (!r.existing || forms.some(f => existsSync(f))));
  if (!hit) return null;
  return 'Blocked: ' + raw + ' is part of the FROZEN eval harness (' + hit.id + '). ' +
    'Editing it mid-pass makes the autoresearch score meaningless; edit only the target ' +
    'artifact.' + SESSION_NOTE;
}

let reason;
try {
  let input = '';
  for await (const chunk of process.stdin) input += chunk;
  reason = decide(JSON.parse(input));
} catch (e) {
  reason = 'Blocked: unreadable hook input or guard error (' + (e?.message || e) +
    '); refusing the write while the eval harness is frozen.';
}
if (reason) {
  console.log(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      permissionDecision: 'deny',
      permissionDecisionReason: '[autoresearch] ' + reason + (reason.includes('session') ? '' : SESSION_NOTE),
    },
  }));
}
