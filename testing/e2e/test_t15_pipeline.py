"""
T15 WS-C: pipeline hooks + pipeline-orchestrator skill (T15-18 .. T15-25).

WHY THIS TEST:
- PROBLEM: the pipeline hooks run in every git repo (D4). They pointed the agent at a
  ~/.claude/skills copy the plugin never installs, taught the agent the bypass switches,
  blocked forever on a stale `running` run, counted AID's own .aid/ files as changed
  source, missed a pretty-printed open escalation, wrote a marker named by an unchecked
  session id, and fell back to a predictable temp dir.
- COST OF FAILURE: an escalation resolved with a script nobody controls, an agent that
  switches its own gate off, turns blocked for no reason, a file written outside its
  folder, a temp dir another local user can pre-create.
- SUCCESS: each behaviour is pinned by running the REAL hook, in place, so its own
  location (the plugin root) is the one under test.

Harness: hooks run under the bash first on PATH (Git Bash on Windows, as hook-runner.mjs
does), from a prelude script written in the fixture, with HOME/USERPROFILE pointing at a
temp folder and CLAUDE_PROJECT_DIR / SKIP_* unset.
"""
import json
import os
import re
import shlex
import shutil
import subprocess
import time

import pytest

REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
HOOKS = os.path.join(REPO_ROOT, 'hooks')
PLAN_HOOK = os.path.join(HOOKS, 'plan-execution-pipeline.sh')
GATE_HOOK = os.path.join(HOOKS, 'dev-pipeline-gate.sh')
SKILL_DIR = os.path.join(REPO_ROOT, 'skills', 'pipeline-orchestrator')
BASH = shutil.which('bash') or 'bash'


def _fwd(p):
    return str(p).replace('\\', '/')


def _bash_has(tool):
    try:
        r = subprocess.run([BASH, '-c', f'command -v {tool}'],
                           capture_output=True, text=True, timeout=60)
        return r.returncode == 0 and r.stdout.strip() != ''
    except Exception:
        return False


HAS_NODE = _bash_has('node')
HAS_PY = _bash_has('python')
needs_node = pytest.mark.skipif(not HAS_NODE, reason="node is not on PATH in the hooks' bash")
needs_runtime = pytest.mark.skipif(not (HAS_NODE or HAS_PY),
                                   reason="neither node nor python in the hooks' bash")

BASE_PRELUDE = 'unset CLAUDE_PROJECT_DIR SKIP_PIPELINE_GATE SKIP_UI_GATE DEV_GATE_BUDGET\n'


def _run(hook, project, payload, prelude='', home=None, timeout=300):
    """Run `hook` IN PLACE (its own path), cwd = project. Returns CompletedProcess."""
    home = home or (project.parent / (project.name + '-home'))
    os.makedirs(str(home), exist_ok=True)
    runner = os.path.join(str(project), '_t15_run.sh')
    with open(runner, 'w', newline='\n') as f:
        f.write(BASE_PRELUDE)
        f.write(f'export HOME={shlex.quote(_fwd(home))}\n')
        f.write(f'export USERPROFILE={shlex.quote(_fwd(home))}\n')
        f.write(prelude + '\n')
        f.write(f'exec "$BASH" {shlex.quote(_fwd(hook))}\n')
    r = subprocess.run([BASH, '_t15_run.sh'], input=json.dumps(payload),
                       capture_output=True, text=True, timeout=timeout, cwd=str(project))
    assert r.returncode != 127, f'hook never ran: {r.stderr}'
    return r


def _git(project, files=None):
    project.mkdir(parents=True, exist_ok=True)
    for rel, text in (files or {}).items():
        p = project / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    subprocess.run(['git', 'init', '-q'], cwd=str(project), timeout=60)
    # the runner script must not count as a changed source file
    (project / '.git' / 'info').mkdir(parents=True, exist_ok=True)
    with open(project / '.git' / 'info' / 'exclude', 'a') as f:
        f.write('_t15_run.sh\nshim/\nmkdir.log\n')
    return project


def _gate(project, payload=None, prelude=''):
    payload = payload if payload is not None else {'session_id': 's1', 'cwd': str(project)}
    return _run(GATE_HOOK, project, payload, prelude)


def _plan(project, sid='s1', prelude='', home=None):
    payload = {'tool_name': 'ExitPlanMode', 'cwd': str(project), 'session_id': sid,
               'tool_response': {'plan': '## Plan\nAdd a login form and tests.'}}
    return _run(PLAN_HOOK, project, payload, prelude, home=home)


def _decision(stdout):
    s = stdout.strip()
    return json.loads(s) if s else {}


# Shim dir with only the named tools (each a wrapper around the real binary), so a run
# can lose node/python while keeping what bash needs.
def _shim_prelude(tools, extra=''):
    names = ' '.join(tools)
    return (
        'mkdir -p shim\n'
        f'for t in {names}; do p=$(command -v "$t") || continue; '
        'printf \'#!%s\\nexec "%s" "$@"\\n\' "$BASH" "$p" > "shim/$t"; chmod +x "shim/$t"; done\n'
        + extra +
        'export PATH="$PWD/shim"\n'
        'command -v node >/dev/null 2>&1 && echo T15-NODE-PRESENT >&2\n'
        'command -v python >/dev/null 2>&1 && echo T15-PYTHON-PRESENT >&2\n'
    )


CORE_TOOLS = ['tr', 'grep', 'sed', 'head', 'cat', 'dirname', 'git', 'sort', 'cut',
              'stat', 'date', 'ls', 'rm', 'mkdir', 'sha256sum', 'mktemp', 'chmod']

# ---------------------------------------------------------------- T15-18

SKILL_PATH_PATTERNS = re.compile(
    r'\$HOME/\.claude/skills|~/\.claude/skills|\$\{HOME\}/\.claude/skills|%USERPROFILE%')


def _wsc_text_files():
    out = []
    for root, _dirs, files in os.walk(SKILL_DIR):
        for fn in files:
            if os.path.splitext(fn)[1].lower() in ('.md', '.json', '.mjs', '.js', '.sh', '.yaml', '.yml', '.txt'):
                out.append(os.path.join(root, fn))
    for fn in os.listdir(HOOKS):
        if fn.endswith('.sh') or fn.endswith('.mjs'):
            out.append(os.path.join(HOOKS, fn))
    return out


def _is_comment(line):
    s = line.strip()
    return s.startswith('#') or s.startswith('//') or s.startswith('*') or s.startswith('/*')


def test_t15_18_no_user_level_skill_path_outside_comments():
    hits = []
    for path in _wsc_text_files():
        is_md = path.endswith('.md')
        with open(path, encoding='utf-8', errors='replace') as f:
            for n, line in enumerate(f, 1):
                if not is_md and _is_comment(line):
                    continue
                if SKILL_PATH_PATTERNS.search(line):
                    hits.append(f'{os.path.relpath(path, REPO_ROOT)}:{n}: {line.strip()[:120]}')
    assert not hits, 'user-level skill paths remain:\n  ' + '\n  '.join(hits)


def test_t15_18_config_bundle_dir_is_the_plugin():
    with open(os.path.join(SKILL_DIR, 'config.default.json'), encoding='utf-8') as f:
        cfg = json.load(f)
    assert cfg['autoresearch']['bundle_dir'] == '${CLAUDE_PLUGIN_ROOT}/skills/autoresearch'


def test_t15_18_skill_uses_i7_gate_invocation():
    with open(os.path.join(SKILL_DIR, 'SKILL.md'), encoding='utf-8') as f:
        text = f.read()
    assert 'node "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-orchestrator/gate.mjs"' in text
    assert '${CLAUDE_PLUGIN_ROOT}/skills/pipeline-orchestrator/config.default.json' in text


def test_t15_18_plan_hook_no_user_level_claim():
    with open(PLAN_HOOK, encoding='utf-8') as f:
        assert 'USER LEVEL' not in f.read()


@needs_runtime
def test_t15_18_escalation_reason_names_own_gate_mjs(tmp_path):
    project = _git(tmp_path / 'p', {'.aid/pipeline/ESCALATION.json':
                                    json.dumps({'status': 'open', 'step': 'CODE_REVIEW',
                                                'why': 'below threshold'}, indent=2)})
    r = _gate(project)
    out = _decision(r.stdout)
    assert out.get('decision') == 'block', r.stdout + r.stderr
    m = re.search(r'node "([^"]+)" --resolve', out['reason'])
    assert m, out['reason']
    gate = m.group(1)
    assert '\\' not in gate and '.claude/skills' not in gate, gate
    assert os.path.isabs(gate) or re.match(r'^[A-Za-z]:/', gate), gate
    assert os.path.isfile(gate), gate
    assert os.path.normcase(os.path.normpath(gate)) == os.path.normcase(
        os.path.join(SKILL_DIR, 'gate.mjs'))


@needs_node
def test_t15_18_plan_hook_bootstrap_path_is_the_plugin(tmp_path):
    project = tmp_path / 'p'
    project.mkdir()
    r = _plan(project)
    ctx = json.loads(r.stdout)['hookSpecificOutput']['additionalContext']
    assert 'USER LEVEL' not in ctx and '.claude/skills' not in ctx, ctx
    # T16-4 flip: a Bash copy to .aid/pipeline/config.json is denied, so the bootstrap is a Write.
    m = re.search(r'BOOTSTRAP it with the Write tool \(read "([^"]+config\.default\.json)"', ctx)
    assert m and os.path.isfile(m.group(1)), ctx
    assert os.path.normcase(os.path.normpath(m.group(1))) == os.path.normcase(
        os.path.join(SKILL_DIR, 'config.default.json'))


def test_t15_18_gate_mjs_resolve_message_names_itself(tmp_path):
    if not shutil.which('node'):
        pytest.skip('node not available')
    root = tmp_path / 'r'
    (root / '.aid' / 'pipeline').mkdir(parents=True)
    (root / '.aid' / 'pipeline' / 'state.json').write_text(json.dumps(
        {'pipeline_status': 'running', 'iterations': {'code_review': 5}}))
    (root / '.aid' / 'pipeline' / 'config.json').write_text(json.dumps(
        {'max_iterations': {'code_review': 5}, 'thresholds': {'code_review_pass': 9.5}}))
    subprocess.run(['node', os.path.join(SKILL_DIR, 'gate.mjs'), '--step', 'CODE_REVIEW',
                    '--scores', '{"overall":7.9}', '--root', str(root)],
                   capture_output=True, text=True, timeout=120,
                   env={**os.environ, 'HOME': str(tmp_path), 'USERPROFILE': str(tmp_path)})
    esc = json.loads((root / '.aid' / 'pipeline' / 'ESCALATION.json').read_text())
    how = esc['how_to_resolve']
    assert '.claude/skills' not in how, how
    m = re.search(r'node "([^"]+)" --resolve', how)
    assert m and os.path.isfile(m.group(1)) and '\\' not in m.group(1), how


# ---------------------------------------------------------------- T15-19

@needs_node
def test_t15_19_plan_hook_context_has_no_bypass_hint(tmp_path):
    project = tmp_path / 'p'
    project.mkdir()
    out = json.loads(_plan(project).stdout)
    ctx = out['hookSpecificOutput']['additionalContext']
    assert 'SKIP_PIPELINE_GATE' not in ctx and 'SKIP_UI_GATE' not in ctx, ctx


def test_t15_19_ui_block_reason_has_no_bypass_hint(tmp_path):
    project = _git(tmp_path / 'p', {'src/a.css': 'a { color: red; }\n'})
    r = _gate(project)
    out = _decision(r.stdout)
    assert out.get('decision') == 'block', r.stdout
    assert 'a.css' in out['reason']
    assert 'SKIP_UI_GATE' not in out['reason'] and 'SKIP_PIPELINE_GATE' not in out['reason']
    assert 'SKIP_UI_GATE=1' in r.stderr, 'the human lost the UI bypass hint'


def test_t15_19_skill_markdown_has_no_bypass_hint():
    hits = []
    for root, _d, files in os.walk(SKILL_DIR):
        for fn in files:
            if fn.endswith('.md'):
                p = os.path.join(root, fn)
                with open(p, encoding='utf-8', errors='replace') as f:
                    t = f.read()
                if 'SKIP_PIPELINE_GATE' in t or 'SKIP_UI_GATE' in t:
                    hits.append(os.path.relpath(p, REPO_ROOT))
    assert not hits, hits
    with open(os.path.join(SKILL_DIR, 'SKILL.md'), encoding='utf-8') as f:
        assert 'stay advisory-only' in f.read().lower()


# ---------------------------------------------------------------- T15-20

def test_t15_20_no_user_memory_or_user_retro():
    hits = []
    for root, _d, files in os.walk(SKILL_DIR):
        for fn in files:
            p = os.path.join(root, fn)
            with open(p, encoding='utf-8', errors='replace') as f:
                t = f.read()
            for needle in ('MEMORY.md', 'skills/retro'):
                if needle in t:
                    hits.append(f'{os.path.relpath(p, REPO_ROOT)}: {needle}')
    assert not hits, hits
    for name in ('SKILL.md', 'SKILL.extended.md'):
        with open(os.path.join(SKILL_DIR, name), encoding='utf-8') as f:
            t = f.read()
        assert 'retro.md' in t and '/aid-end' in t and '/aid-improve' in t, name


# ---------------------------------------------------------------- T15-21

def _running_project(tmp_path, run_sid, state_age_s):
    project = _git(tmp_path / 'p', {'src/a.py': 'x = 1\n'})
    state = project / '.aid' / 'pipeline' / 'state.json'
    state.parent.mkdir(parents=True)
    st = {'pipeline_status': 'running', 'current_step': 'DEVELOP', 'task_id': 't'}
    if run_sid:
        st['session_id'] = run_sid
    state.write_text(json.dumps(st))
    old = time.time() - state_age_s
    os.utime(str(state), (old, old))
    return project


@needs_runtime
def test_t15_21_other_session_running_is_stale(tmp_path):
    project = _running_project(tmp_path, 'other-session', 120)
    r = _gate(project, {'session_id': 's1', 'cwd': str(project)})
    out = _decision(r.stdout)
    assert out.get('decision') != 'block', r.stdout
    assert '/pipeline-status' in out.get('systemMessage', '') and \
        '/pipeline' in out['systemMessage'], r.stdout


def test_t15_21_old_running_state_is_stale(tmp_path):
    project = _running_project(tmp_path, 's1', 7 * 3600)
    r = _gate(project, {'session_id': 's1', 'cwd': str(project)})
    out = _decision(r.stdout)
    assert out.get('decision') != 'block', r.stdout
    assert '/pipeline-status' in out.get('systemMessage', ''), r.stdout


def test_t15_21_same_session_fresh_run_still_blocks(tmp_path):
    project = _running_project(tmp_path, 's1', 120)
    r = _gate(project, {'session_id': 's1', 'cwd': str(project)})
    assert _decision(r.stdout).get('decision') == 'block', r.stdout


@needs_node
def test_t15_21_plan_hook_passes_session_id_to_init(tmp_path):
    project = tmp_path / 'p'
    project.mkdir()
    sid = '0f8fad5b-d9cb-469f-a165-70867728950e'
    ctx = json.loads(_plan(project, sid=sid).stdout)['hookSpecificOutput']['additionalContext']
    assert f'session_id={sid}' in ctx, ctx
    with open(os.path.join(SKILL_DIR, 'SKILL.md'), encoding='utf-8') as f:
        assert '"session_id"' in f.read()


# ---------------------------------------------------------------- T15-22

def test_t15_22_aid_outputs_are_not_changed_source(tmp_path):
    project = _git(tmp_path / 'p', {'.aid/pipeline/t/x.test.js': 'function (\n',
                                    '.aid/qa/a.tsx': 'export const A = () => <div/>;\n'})
    r = _gate(project)
    assert r.returncode == 0
    assert r.stdout.strip() == '', f'the gate reacted to AID outputs: {r.stdout!r}'


def test_t15_22_real_source_still_triggers_ui_check(tmp_path):
    project = _git(tmp_path / 'p', {'.aid/qa/a.tsx': 'x\n',
                                    'src/a.tsx': 'export const A = () => <div/>;\n'})
    out = _decision(_gate(project).stdout)
    assert out.get('decision') == 'block' and 'src/a.tsx' in out['reason'], out


# ---------------------------------------------------------------- T15-23

ESC_MULTI_OPEN = '{\n  "status":\n    "open",\n  "step": "CODE_REVIEW",\n  "why": "w"\n}\n'
ESC_ONE_LINE = '{"status": "open", "step": "CODE_REVIEW", "why": "w"}'
ESC_MULTI_RESOLVED = '{\n  "status":\n    "resolved",\n  "step": "CODE_REVIEW"\n}\n'


def _esc_project(tmp_path, text):
    return _git(tmp_path / 'p', {'.aid/pipeline/ESCALATION.json': text})


@needs_runtime
@pytest.mark.parametrize('text', [ESC_MULTI_OPEN, ESC_ONE_LINE], ids=['multiline', 'oneline'])
def test_t15_23_open_escalation_blocks(tmp_path, text):
    out = _decision(_gate(_esc_project(tmp_path, text)).stdout)
    assert out.get('decision') == 'block' and 'ESCALATED' in out['reason'], out


@needs_runtime
def test_t15_23_unparseable_escalation_fails_closed(tmp_path):
    out = _decision(_gate(_esc_project(tmp_path, '{"status": "open", oops')).stdout)
    assert out.get('decision') == 'block', out
    assert 'ESCALATION.json' in out['reason'], out


@needs_runtime
def test_t15_23_multiline_resolved_does_not_block(tmp_path):
    r = _gate(_esc_project(tmp_path, ESC_MULTI_RESOLVED))
    assert _decision(r.stdout).get('decision') != 'block', r.stdout


@pytest.mark.parametrize('text,blocks', [(ESC_MULTI_OPEN, True), (ESC_MULTI_RESOLVED, False)],
                         ids=['open', 'resolved'])
def test_t15_23_no_node_no_python_falls_back_to_collapsed_grep(tmp_path, text, blocks):
    project = _esc_project(tmp_path, text)
    r = _gate(project, prelude=_shim_prelude(CORE_TOOLS))
    if 'T15-NODE-PRESENT' in r.stderr or 'T15-PYTHON-PRESENT' in r.stderr:
        pytest.skip('could not strip node/python from PATH')
    got = _decision(r.stdout).get('decision') == 'block'
    assert got == blocks, (r.stdout, r.stderr)


# ---------------------------------------------------------------- T15-24

@needs_node
def test_t15_24_traversal_session_id_writes_nothing_outside(tmp_path):
    project = tmp_path / 'p'
    project.mkdir()
    home = tmp_path / 'home'
    r = _plan(project, sid='../../escaped-g2', home=home)
    assert r.returncode == 0
    ctx = json.loads(r.stdout)['hookSpecificOutput']['additionalContext']
    assert 'INTENT GATE' in ctx
    assert 'escaped-g2' not in ctx
    found = [os.path.join(d, f) for d, _s, fs in os.walk(str(tmp_path)) for f in fs
             if f == 'escaped-g2']
    assert not found, f'marker escaped its folder: {found}'


@needs_node
def test_t15_24_uuid_session_id_creates_marker(tmp_path):
    project = tmp_path / 'p'
    project.mkdir()
    home = tmp_path / 'home'
    sid = '0f8fad5b-d9cb-469f-a165-70867728950e'
    r = _plan(project, sid=sid, home=home)
    assert r.returncode == 0
    assert (home / '.claude' / '.loop1-kickoff' / sid).is_file()


# ---------------------------------------------------------------- T15-25

def test_t15_25_no_predictable_temp_dir_when_mktemp_fails(tmp_path):
    project = tmp_path / 'p'
    project.mkdir()
    tmpdir = tmp_path / 'tmpdir'
    tmpdir.mkdir()
    shim = project / 'shim'
    shim.mkdir()
    # mktemp always fails; mkdir logs every path it is asked to create, then runs the real one.
    with open(shim / 'mktemp', 'w', newline='\n') as f:
        f.write('#!/bin/sh\nexit 1\n')
    with open(shim / 'mkdir', 'w', newline='\n') as f:
        f.write('#!/bin/sh\nprintf \'%s\\n\' "$*" >> "$T15_MKDIR_LOG"\n'
                'exec "$T15_REAL_MKDIR" "$@"\n')
    prelude = (
        'chmod +x shim/mktemp shim/mkdir\n'
        'export T15_REAL_MKDIR="$(command -v mkdir)"\n'
        'export T15_MKDIR_LOG="$PWD/mkdir.log"\n'
        f'export TMPDIR={shlex.quote(_fwd(tmpdir))}\n'
        'export PATH="$PWD/shim:$PATH"\n'
    )
    r = _plan(project, prelude=prelude)
    assert r.returncode == 0, r.stderr
    log = (project / 'mkdir.log').read_text() if (project / 'mkdir.log').exists() else ''
    assert 'cc-plan-hook' not in log, f'a predictable temp dir was created: {log!r}'
    assert not [p for p in os.listdir(str(tmpdir)) if p.startswith('cc-plan-hook')]
    out = json.loads(r.stdout)
    ctx = out['hookSpecificOutput']['additionalContext']
    assert 'WARNING' in ctx and 'INTENT GATE' in ctx, ctx
