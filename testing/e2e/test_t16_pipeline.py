"""
T16 WS-C: pipeline hooks + pipeline-orchestrator skill (T16-21 .. T16-25).

WHY THIS TEST:
- PROBLEM: the escalation messages told the agent to run `gate.mjs --resolve` itself (a
  decision only the user makes); hook reasons carried UTF-8 arrows/dashes that Windows python
  turned into mojibake; the freshness Stop gate blocked in Phase 5; the pipeline skill ingests
  PR/Jira/web text without naming the untrusted-content rule; and the hook runner's python
  probes (5 s each, three of them) could outlast the 10 s PreToolUse timeout.
- COST OF FAILURE: an agent clears its own escalation, unreadable block reasons, blocked
  turns in QA, prompt injection from ingested content, a gate that is killed instead of
  answering.
- SUCCESS: each behaviour is pinned by running the REAL hook / script in place.

Harness: hooks run under the bash first on PATH (Git Bash on Windows) from a prelude script,
with HOME/USERPROFILE pointing at a temp folder and CLAUDE_PROJECT_DIR / SKIP_* unset. Probe
projects live at the drive root (outside the user profile, whose ~/.aid/state.json would make
every folder under it an AID project).
"""
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOKS = REPO_ROOT / 'hooks'
GATE_HOOK = HOOKS / 'dev-pipeline-gate.sh'
PLAN_HOOK = HOOKS / 'plan-execution-pipeline.sh'
RUNNER = HOOKS / 'hook-runner.mjs'
SKILL_DIR = REPO_ROOT / 'skills' / 'pipeline-orchestrator'
GATE_MJS = SKILL_DIR / 'gate.mjs'
BASH = shutil.which('bash') or 'bash'
NODE = shutil.which('node')


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

BASE_PRELUDE = 'unset CLAUDE_PROJECT_DIR CLAUDE_CONFIG_DIR SKIP_PIPELINE_GATE SKIP_UI_GATE DEV_GATE_BUDGET\n'


@pytest.fixture
def probe(tmp_path):
    """A probe dir at the drive root (outside C:/Users/<me>), removed afterwards."""
    d = Path(tempfile.mkdtemp(prefix='aid-t16-', dir=Path(tmp_path).anchor))
    try:
        yield d
    finally:
        shutil.rmtree(str(d), ignore_errors=True)


def _run(hook, project, payload, prelude=''):
    home = project.parent / (project.name + '-home')
    home.mkdir(parents=True, exist_ok=True)
    runner = project / '_t16_run.sh'
    with open(runner, 'w', newline='\n') as f:
        f.write(BASE_PRELUDE)
        f.write(f'export HOME={shlex.quote(_fwd(home))}\n')
        f.write(f'export USERPROFILE={shlex.quote(_fwd(home))}\n')
        f.write(prelude + '\n')
        f.write(f'exec "$BASH" {shlex.quote(_fwd(hook))}\n')
    try:
        r = subprocess.run([BASH, '_t16_run.sh'], input=json.dumps(payload).encode('utf-8'),
                           capture_output=True, timeout=300, cwd=str(project))
    finally:
        shutil.rmtree(str(home), ignore_errors=True)
    assert r.returncode != 127, f'hook never ran: {r.stderr!r}'
    # Raw bytes -> str exactly as Claude Code would read them (UTF-8).
    r.stdout = r.stdout.decode('utf-8', 'replace')
    r.stderr = r.stderr.decode('utf-8', 'replace')
    return r


def _git(project, files=None):
    project.mkdir(parents=True, exist_ok=True)
    for rel, text in (files or {}).items():
        p = project / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')
    subprocess.run(['git', 'init', '-q'], cwd=str(project), timeout=60)
    (project / '.git' / 'info').mkdir(parents=True, exist_ok=True)
    with open(project / '.git' / 'info' / 'exclude', 'a') as f:
        f.write('_t16_run.sh\n')
    return project


def _decision(stdout):
    s = stdout.strip()
    return json.loads(s) if s else {}


def _gate(project, sid='s1'):
    return _run(GATE_HOOK, project, {'session_id': sid, 'cwd': str(project)})


# ---------------------------------------------------------------- T16-21

BANG_RE = re.compile(r'! node "([^"]+)" --resolve "<what was decided>"')


def _assert_bang_line(text):
    m = BANG_RE.search(text)
    assert m, f'no `! node "<gate.mjs>" --resolve "<what was decided>"` line in: {text}'
    gate = m.group(1)
    assert '\\' not in gate and '.claude/skills' not in gate, gate
    assert os.path.isfile(gate), gate
    assert os.path.normcase(os.path.normpath(gate)) == os.path.normcase(str(GATE_MJS))
    # Every runnable resolve line is a user `!` line; none is addressed to the agent bare.
    for hit in re.finditer(r'node "[^"]*gate\.mjs" --resolve', text):
        assert text[max(0, hit.start() - 2):hit.start()] == '! ', text
    low = text.lower()
    assert 'never run it' in low, f'the agent is not told never to run the line: {text}'
    assert 'show' in low, f'the agent is not told to show the line to the user: {text}'


ESC_OPEN = json.dumps({'status': 'open', 'step': 'CODE_REVIEW', 'why': 'below threshold'}, indent=2)


@needs_runtime
def test_t16_21_open_escalation_reason_hands_user_a_bang_line(probe):
    project = _git(probe / 'p', {'.aid/pipeline/ESCALATION.json': ESC_OPEN})
    out = _decision(_gate(project).stdout)
    assert out.get('decision') == 'block', out  # the Stop hook still blocks while open
    _assert_bang_line(out['reason'])


@needs_runtime
def test_t16_21_unparseable_escalation_reason_hands_user_a_bang_line(probe):
    project = _git(probe / 'p', {'.aid/pipeline/ESCALATION.json': '{"status": "open", oops'})
    out = _decision(_gate(project).stdout)
    assert out.get('decision') == 'block', out
    _assert_bang_line(out['reason'])


def test_t16_21_gate_mjs_how_to_resolve_is_a_bang_line(probe):
    if not NODE:
        pytest.skip('node not available')
    root = probe / 'r'
    (root / '.aid' / 'pipeline').mkdir(parents=True)
    (root / '.aid' / 'pipeline' / 'state.json').write_text(json.dumps(
        {'pipeline_status': 'running', 'iterations': {'code_review': 5}}))
    (root / '.aid' / 'pipeline' / 'config.json').write_text(json.dumps(
        {'max_iterations': {'code_review': 5}, 'thresholds': {'code_review_pass': 9.5}}))
    home = probe / 'home'
    home.mkdir()
    subprocess.run([NODE, str(GATE_MJS), '--step', 'CODE_REVIEW', '--scores', '{"overall":7.9}',
                    '--root', str(root)], capture_output=True, text=True, timeout=120,
                   env={**os.environ, 'HOME': str(home), 'USERPROFILE': str(home)})
    esc = json.loads((root / '.aid' / 'pipeline' / 'ESCALATION.json').read_text(encoding='utf-8'))
    _assert_bang_line(esc['how_to_resolve'])


def test_t16_21_skill_tree_never_tells_the_agent_to_run_resolve():
    """Every `--resolve` mention in the skill's docs is the user's `!` line."""
    bad = []
    for p in SKILL_DIR.rglob('*.md'):
        for n, line in enumerate(p.read_text(encoding='utf-8').splitlines(), 1):
            if '--resolve' in line and '! node "' not in line:
                bad.append(f'{p.relative_to(REPO_ROOT)}:{n}: {line.strip()}')
    assert not bad, 'agent-facing --resolve text without the user ! line:\n' + '\n'.join(bad)
    text = (SKILL_DIR / 'SKILL.md').read_text(encoding='utf-8')
    assert ('! node "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-orchestrator/gate.mjs" '
            '--resolve "<what was decided>"') in text
    assert 'never run it yourself' in text.lower()


# ---------------------------------------------------------------- T16-22

def _freshness_project(probe, phase=None, state_text=None, brief_tamper=False):
    files = {'src/a.go': 'package a\n'}
    if phase is not None:
        files['.aid/state.json'] = json.dumps({'current_phase': phase})
    if state_text is not None:
        files['.aid/state.json'] = state_text
    files['.aid/pipeline/state.json'] = json.dumps(
        {'pipeline_status': 'running', 'current_step': 'DEVELOP', 'session_id': 's1'})
    if brief_tamper:
        files['.aid/pipeline/t1/brief.md'] = 'frozen brief\n'
        files['.aid/pipeline/t1/brief.sha256'] = hashlib.sha256(b'other').hexdigest() + '\n'
    project = _git(probe / 'p', files)
    now = time.time()
    st = project / '.aid' / 'pipeline' / 'state.json'
    os.utime(str(st), (now - 600, now - 600))          # recent (not stale) but older than source
    os.utime(str(project / 'src' / 'a.go'), (now, now))
    return project


@needs_runtime
def test_t16_22_freshness_block_reason_is_ascii(probe):
    project = _freshness_project(probe, brief_tamper=True)
    out = _decision(_gate(project).stdout)
    assert out.get('decision') == 'block', out
    reason = out['reason']
    assert 'WARNING' in reason and 'MODIFIED mid-run' in reason, reason
    assert reason.isascii(), reason
    assert '\u00e2' not in reason, reason
    assert 'CODE_REVIEW -> TDD -> TEST_REVIEW' in reason, reason


@needs_node
def test_t16_22_plan_hook_texts_are_ascii(probe):
    project = probe / 'p'
    project.mkdir()
    payload = {'tool_name': 'ExitPlanMode', 'cwd': str(project), 'session_id': 's1',
               'tool_response': {'plan': '## Plan\nAdd a login form and tests.'}}
    out = json.loads(_run(PLAN_HOOK, project, payload).stdout)
    ctx = out['hookSpecificOutput']['additionalContext']
    for text in (ctx, out['systemMessage']):
        assert text.isascii() and '\u00e2' not in text, text
    out = json.loads(_run(PLAN_HOOK, project, payload,
                          prelude='export SKIP_PIPELINE_GATE=1').stdout)
    assert out['systemMessage'].isascii(), out


@needs_node
@pytest.mark.parametrize('aid', [False, True], ids=['non-aid', 'aid'])
def test_t16_4_plan_hook_bootstraps_config_with_the_write_tool(probe, aid):
    """
    WHY THIS TEST:
    - PROBLEM: T16-4 denies a Bash write to .aid/pipeline/config.json; the plan hook told the
      agent to BOOTSTRAP it "by copying" the default, i.e. a Bash cp the gate now denies.
    - COST OF FAILURE: every first pipeline run hits a deny and stalls (or tries a workaround).
    - SUCCESS: the hook tells the agent to create the file with the Write tool (allowed when absent).
    """
    project = probe / 'p'
    (project / '.aid' if aid else project).mkdir(parents=True)
    payload = {'tool_name': 'ExitPlanMode', 'cwd': str(project), 'session_id': 's1',
               'tool_response': {'plan': '## Plan\nAdd a login form and tests.'}}
    ctx = json.loads(_run(PLAN_HOOK, project, payload).stdout)['hookSpecificOutput']['additionalContext']
    step1 = next(line for line in ctx.splitlines() if line.startswith('1. INITIALIZE'))
    assert 'Write tool' in step1, step1
    assert 'by copying' not in step1, step1
    assert 'config.default.json' in step1, step1


def test_t16_4_skill_bootstraps_config_with_the_write_tool():
    """The orchestrator skill's bootstrap step matches the hook: Write tool, never a Bash copy."""
    text = (SKILL_DIR / 'SKILL.md').read_text(encoding='utf-8')
    step = next(line for line in text.splitlines()
                if line.startswith('1. Read `.aid/pipeline/config.json`'))
    assert 'with the Write tool' in step, step
    assert 'copy the plugin' not in step, step
    ext = (SKILL_DIR / 'SKILL.extended.md').read_text(encoding='utf-8')
    sect = ext[ext.index('### Config File Missing'):ext.index('### Test Command Not Found')]
    assert 'Write tool' in sect, sect


@pytest.mark.parametrize('hook', sorted(p.name for p in HOOKS.glob('*.sh')))
def test_t16_22_hook_source_text_outside_comments_is_ascii(hook):
    """Every line a hook can emit is ASCII: only full-line comments may carry other text."""
    bad = []
    for n, line in enumerate((HOOKS / hook).read_text(encoding='utf-8').splitlines(), 1):
        if line.lstrip().startswith('#'):
            continue
        if not line.isascii():
            bad.append(f'{hook}:{n}: {line.strip()[:100]}')
    assert not bad, '\n'.join(bad)


# ---------------------------------------------------------------- T16-23

@needs_runtime
def test_t16_23_phase4_freshness_still_blocks(probe):
    out = _decision(_gate(_freshness_project(probe, phase=4)).stdout)
    assert out.get('decision') == 'block', out


@needs_runtime
@pytest.mark.parametrize('phase', [5, '5'], ids=['int', 'str'])
def test_t16_23_phase5_freshness_is_a_message(probe, phase):
    out = _decision(_gate(_freshness_project(probe, phase=phase)).stdout)
    assert out.get('decision') != 'block', out
    msg = out.get('systemMessage', '')
    assert 'Phase 5' in msg and '/pipeline' in msg, out
    assert msg.isascii(), msg


@needs_runtime
def test_t16_23_unreadable_state_keeps_blocking(probe):
    out = _decision(_gate(_freshness_project(probe, state_text='{"current_phase": 5,')).stdout)
    assert out.get('decision') == 'block', out


@needs_runtime
def test_t16_23_non_aid_repo_unchanged(probe):
    out = _decision(_gate(_freshness_project(probe)).stdout)  # .aid/pipeline but no .aid/state.json
    assert out.get('decision') == 'block', out


# ---------------------------------------------------------------- T16-24

def test_t16_24_pipeline_skill_names_untrusted_content_rule():
    text = (SKILL_DIR / 'SKILL.md').read_text(encoding='utf-8')
    assert 'rules/general/untrusted-content.md' in text
    assert (REPO_ROOT / 'rules' / 'general' / 'untrusted-content.md').is_file()
    # Referenced where the skill ingests outside text: PRs, Jira, web pages.
    para = [p for p in re.split(r'\n\s*\n', text) if 'rules/general/untrusted-content.md' in p]
    joined = ' '.join(para).lower()
    for word in ('jira', 'pull request', 'web'):
        assert word in joined, f'{word!r} not named next to the rule reference'
    visual = text[text.index('### visual-qa-agent'):text.index('### FIX_VISUAL')]
    assert 'untrusted-content.md' in visual, 'the browser step does not name the rule'


# ---------------------------------------------------------------- T16-25

def _pretool_timeout():
    hooks = json.loads((REPO_ROOT / '.claude-plugin' / 'plugin.json').read_text(encoding='utf-8'))['hooks']
    return min(h['timeout'] for entry in hooks['PreToolUse'] for h in entry['hooks'])


def test_t16_25_slow_python_probes_stay_under_the_hook_timeout(probe):
    """Every python candidate hangs on the `-c "import sys"` probe: the runner must still
    answer (fail closed, exit 2) well inside the PreToolUse timeout instead of being killed."""
    if not NODE:
        pytest.skip('node not available')
    slow = probe / 'slowpy'
    slow.mkdir()
    (slow / 'sitecustomize.py').write_text(
        'import sys, time\nif getattr(sys, "argv", None) == ["-c"]:\n    time.sleep(30)\n')
    home = probe / 'home'
    home.mkdir()
    env = {k: v for k, v in os.environ.items() if k not in ('CLAUDE_PROJECT_DIR', 'CLAUDE_CONFIG_DIR')}
    env.update(HOME=str(home), USERPROFILE=str(home), AID_HOME=str(home / '.aid'),
               PYTHONPATH=str(slow))
    payload = {'tool_name': 'Bash', 'tool_input': {'command': 'ls'}, 'cwd': str(probe)}
    t0 = time.monotonic()
    r = subprocess.run([NODE, str(RUNNER), 'phase-gate-bash'], input=json.dumps(payload),
                       capture_output=True, text=True, timeout=120, cwd=str(probe), env=env)
    elapsed = time.monotonic() - t0
    limit = _pretool_timeout()
    assert elapsed < limit - 2, f'runner took {elapsed:.1f}s against a {limit}s hook timeout'
    if r.returncode == 0:
        pytest.skip('a python candidate ignored PYTHONPATH (sitecustomize not loaded)')
    assert r.returncode == 2, (r.returncode, r.stderr)  # still fails closed
    assert 'no working Python' in r.stderr, r.stderr


def test_t16_25_normal_probe_still_runs_the_gate(probe):
    """Guard: with a normal python the runner still reaches the gate and allows `ls`."""
    if not NODE:
        pytest.skip('node not available')
    home = probe / 'home'
    home.mkdir()
    env = {k: v for k, v in os.environ.items() if k not in ('CLAUDE_PROJECT_DIR', 'CLAUDE_CONFIG_DIR')}
    env.update(HOME=str(home), USERPROFILE=str(home), AID_HOME=str(home / '.aid'))
    payload = {'tool_name': 'Bash', 'tool_input': {'command': 'ls'}, 'cwd': str(probe)}
    r = subprocess.run([NODE, str(RUNNER), 'phase-gate-bash'], input=json.dumps(payload),
                       capture_output=True, text=True, timeout=120, cwd=str(probe), env=env)
    assert r.returncode == 0, (r.returncode, r.stderr)
    assert '"deny"' not in r.stdout, r.stdout
