"""
T17 WS-A gate + hooks (T17-acceptance.md, T17-1 .. T17-13).

WHY THESE TESTS:
- PROBLEM: the third 3.0.8 gate run found that a direct `"<S>" approve` / `"<P>" --resolve`
  (the script as the command word, run through its shebang or file association) skipped the
  confirmation the python / node call gets (R-01, R-03); a non-ASCII project path broke every
  hook (R-04); hook text told the agent to prefer project reviewers over the plugin's (R-05);
  the hook audit log kept URL, flag and JSON-quoted secrets (R-06/R-07); SessionStart crashed
  on the context.json shapes the agents wrote (G1-15); and several lows (U-03, U-08, U-09,
  U-17, U-26).
- COST OF FAILURE: an agent changes the AID phase, records a QA pass or resolves an escalation
  with no prompt; AID stops working for users whose path is not ASCII; secrets land on disk.
- SUCCESS: the real hooks, spawned through hooks/hook-runner.mjs as Claude Code runs them,
  give the verdicts the contract names.

Harness (contract section 4): fake HOME/USERPROFILE/AID_HOME; probe projects at the drive
root on Windows (outside the real profile) and in the temp dir elsewhere; CLAUDE_PROJECT_DIR,
CLAUDE_CONFIG_DIR and CLAUDE_PLUGIN_ROOT unset unless a test sets them. <R> = the live plugin
root, <S> = <R>/hooks/aid_session.py, <P> = <R>/skills/pipeline-orchestrator/gate.mjs.
Token-shaped and secret-shaped values are built at run time through function calls (U-17).
Many hook spawns per test: they run in a small thread pool (each spawn is independent).
"""
import ast
import hashlib
import json
import os
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
HOOKS = REPO / 'hooks'
RUNNER = HOOKS / 'hook-runner.mjs'
R = str(REPO).replace('\\', '/')
S = R + '/hooks/aid_session.py'
P = R + '/skills/pipeline-orchestrator/gate.mjs'
NT = os.name == 'nt'

sys.path.insert(0, str(HOOKS))
from aid_hooks import AID_RULES  # noqa: E402  (the hook prints it verbatim)

# gitleaks curl-auth-user / HOL: never write the curl user:pass shape literally (T17 CI).
CURL = "cu" + "rl"

pytestmark = pytest.mark.skipif(shutil.which('node') is None, reason='node is needed for hook-runner.mjs')
needs_bash = pytest.mark.skipif(shutil.which('bash') is None, reason='bash is needed for the .sh hooks')

LEVELS = ('block', 'warn', 'log')
EVERY = ['non-AID'] + ['p{}/{}'.format(p, lv) for p in (0, 1, 4, 5) for lv in LEVELS]
IN_AID = EVERY[1:]
# Small: hook-runner.mjs gives its python probe 2 s, which a saturated machine can miss.
POOL = max(2, min(6, (os.cpu_count() or 2) // 2))


def secret(*parts):
    """A secret-shaped value built at run time (never a constant the compiler can fold)."""
    return ''.join(list(parts))


def _marker_above(p):
    return any((d / '.aid' / 'state.json').is_file() or (d / '.aid' / 'hooks' / 'config.json').is_file()
               for d in [p] + list(p.parents))


@pytest.fixture
def base(tmp_path):
    """A probe directory with no AID marker above it (drive root on Windows, contract 4)."""
    alt = Path(tempfile.mkdtemp(prefix='aid-t17-', dir=Path(tmp_path).anchor if NT else None))
    if _marker_above(alt):
        shutil.rmtree(alt, ignore_errors=True)
        pytest.skip('no directory without an AID marker ancestor is available')
    yield alt
    shutil.rmtree(alt, ignore_errors=True)


def _env(home, extra=None):
    env = dict(os.environ, HOME=str(home), USERPROFILE=str(home), AID_HOME=str(Path(home) / '.aid'))
    for k in ('CLAUDE_PROJECT_DIR', 'CLAUDE_CONFIG_DIR', 'CLAUDE_PLUGIN_ROOT'):
        env.pop(k, None)
    env.update(extra or {})
    return env


def run(hook, cwd, home, payload, env_extra=None, runner=RUNNER, raw=None):
    # Claude Code sends raw UTF-8 (not \\u escapes), which is what a non-ASCII path tests.
    data = raw if raw is not None else json.dumps(payload, ensure_ascii=False).encode('utf-8')
    p = subprocess.run(['node', str(runner), hook], input=data, capture_output=True,
                       cwd=str(cwd), env=_env(home, env_extra), timeout=120)
    assert p.returncode == 0, (hook, p.returncode, p.stderr[-600:])
    out = p.stdout.decode('utf-8').strip()      # I-18: the output is always decodable
    if out:
        json.loads(out)
    return out


def py_hook(args, cwd, home, payload, env_extra=None, hooks_dir=HOOKS):
    p = subprocess.run([sys.executable, str(Path(hooks_dir) / 'aid_hooks.py')] + list(args),
                       input=json.dumps(payload, ensure_ascii=False).encode('utf-8'), capture_output=True, cwd=str(cwd),
                       env=_env(home, env_extra), timeout=120)
    assert p.returncode == 0, (args, p.returncode, p.stderr[-600:])
    return p.stdout.decode('utf-8').strip()


def decision(out):
    """('ALLOW', None) for silence; ('DENY'|'ASK', reason); ('ALLOW', context) otherwise."""
    if not out:
        return 'ALLOW', None
    hso = json.loads(out).get('hookSpecificOutput', {})
    d = hso.get('permissionDecision')
    if d in ('deny', 'ask'):
        assert hso.get('hookEventName') == 'PreToolUse' and hso.get('permissionDecisionReason'), out
        return d.upper(), hso['permissionDecisionReason']
    return 'ALLOW', hso.get('additionalContext')


TOOL_INPUT = {
    'Write': lambda p: {'file_path': p, 'content': 'x'},
    'Edit': lambda p: {'file_path': p, 'old_string': 'a', 'new_string': 'b'},
    'MultiEdit': lambda p: {'file_path': p, 'edits': [{'old_string': 'a', 'new_string': 'b'}]},
    'NotebookEdit': lambda p: {'notebook_path': p, 'new_source': 'x'},
}


class Where(object):
    """An AID project at a phase and level (or, place 'non-AID', a plain folder) + home H."""

    def __init__(self, root, place='p1/block', name='proj'):
        self.P, self.H = root / name, root / 'home'
        self.P.mkdir(parents=True, exist_ok=True)
        (self.H / '.claude').mkdir(parents=True, exist_ok=True)
        self.env, self.place, self.runner = {}, place, RUNNER
        if place != 'non-AID':
            phase, level = place[1:].split('/')
            for d in ('.aid/hooks', '.claude', 'docs'):
                (self.P / d).mkdir(parents=True, exist_ok=True)
            (self.P / '.claude' / 'settings.json').write_text('{}', encoding='utf-8')
            self.state(int(phase))
            self.level(level)

    def state(self, phase, **extra):
        doc = {'current_phase': phase}
        doc.update(extra)
        (self.P / '.aid' / 'state.json').write_text(json.dumps(doc), encoding='utf-8')

    def level(self, level):
        (self.P / '.aid' / 'hooks' / 'config.json').write_text(json.dumps(
            {'enforcement': {'phase_gate_write': level, 'phase_gate_bash': level}}), encoding='utf-8')

    def _payload(self, tool, tool_input, cwd=None):
        return {'session_id': uuid.uuid4().hex, 'cwd': str(cwd or self.P), 'tool_name': tool,
                'tool_input': tool_input}

    def bash(self, cmd, tool='Bash', cwd=None):
        return decision(run('phase-gate-bash', self.P, self.H, self._payload(tool, {'command': cmd}, cwd),
                            self.env, self.runner))

    def ps(self, cmd):
        return self.bash(cmd, tool='PowerShell')

    def write(self, path, tool='Write'):
        return decision(run('phase-gate-write', self.P, self.H, self._payload(tool, TOOL_INPUT[tool](path)),
                            self.env, self.runner))

    def session_start(self):
        out = run('session-start', self.P, self.H, {'session_id': 's1', 'source': 'startup',
                                                    'cwd': str(self.P)}, self.env, self.runner)
        return json.loads(out) if out else {}


def _w(base, place, name='proj'):
    return Where(base / place.replace('/', '_').replace('-', ''), place, name)


def many(jobs):
    """Run [(where, tool, cmd)] in parallel; the verdicts in order."""
    with ThreadPoolExecutor(POOL) as ex:
        return list(ex.map(lambda j: j[0].bash(j[2], j[1]), jobs))


# The reason class of a verdict (I-17 oracle): which family of reason it is, not its text
# (the text quotes the command, which differs by the inserted interpreter).
_CLASS_KEYS = ('must confirm', 'ESCALATION.json', '! node', 'exact form', 'PowerShell', 'control file',
               'not an installed AID', 'another installed copy', 'Phase gate', 'ENFORCEMENT BLOCK',
               'ENFORCEMENT WARNING', 'never run it')


def verdict_class(v):
    return v[0], tuple(k for k in _CLASS_KEYS if k in (v[1] or ''))


# --- T17-1 a direct aid_session.py call is judged like the python call -------------------

T17_1_BASE = ['{X}"{S}" init developer 5', '{X}"{S}" approve', '{X}"{S}" reset --all', '{X}"{S}" qa-pass T-1',
              '{X}"{S}" memory-sync']
T17_1_PREFIXES = ['env ', 'exec ', 'nohup ', 'command ', 'time ', 'timeout 60 ', 'VAR=1 ']
T17_1_BASH = (T17_1_BASE + [p + c for p in T17_1_PREFIXES for c in T17_1_BASE]
              + ['{X}./aid_session.py approve', '{X}hooks/AID_SESSION.PY reset', '{X}"{S}" status', '{X}"{S}" roles']
              # R3-01 (T17): the & of a redirect is not a separator (2>&1, >&2, >/dev/null 2>&1).
              + ['{X}"{S}" qa-pass T-1 2>&1 | tee x.log', '{X}"{S}" reset --all >/dev/null 2>&1',
                 '{X}"{S}" approve >&2', 'x="$({X}"{S}" qa-pass T-1 2>&1)"', '{X}"{S}" init developer 5 2>&1']
              + (['{X}"{R}/hooks/aid_session.py." approve'] if NT else []))
T17_1_PS = T17_1_BASE + ['& {X}"{S}" init developer 5', '& {X}"{S}" qa-pass T-1', '{X}.\\aid_session.py approve',
                         '{X}"{S}" status', '{X}"{S}" roles']


def _pair(form, interp):
    return form.format(X='', S=S, R=R), form.format(X=interp + ' ', S=S, R=R)


@pytest.mark.parametrize('place', EVERY)
def test_t17_1_direct_session_calls_get_the_python_twins_verdict(base, place):
    w = _w(base, place)
    jobs, pairs = [], []
    for tool, corpus in (('Bash', T17_1_BASH), ('PowerShell', T17_1_PS)):
        for form in corpus:
            c, twin = _pair(form, 'python')
            pairs.append((tool, c, twin))
            jobs += [(w, tool, c), (w, tool, twin)]
    got = many(jobs)
    for n, (tool, c, twin) in enumerate(pairs):
        vc, vt = got[2 * n], got[2 * n + 1]
        assert verdict_class(vc) == verdict_class(vt), (place, tool, c, vc, twin, vt)


@pytest.mark.parametrize('place', EVERY)
def test_t17_1_exact_direct_form_is_asked_and_status_allowed(base, place):
    w = _w(base, place)
    cmds = ['"{}" {}'.format(S, s) for s in ('init developer 5', 'approve', 'reset --all', 'qa-pass T-1',
                                             'memory-sync')]
    got = many([(w, 'Bash', c) for c in cmds] + [(w, 'Bash', '"{}" status'.format(S)),
                                                 (w, 'Bash', '"{}" roles'.format(S))])
    for c, v in zip(cmds, got):
        assert v[0] == 'ASK' and 'must confirm' in v[1], (place, c, v)
    assert got[-2][0] == 'ALLOW' and got[-1][0] == 'ALLOW', (place, got[-2:])


T17_1_SHC = [('sh -c "\\"{S}\\" approve"', 'sh -c "python \\"{S}\\" approve"'),
             ('bash -c "\\"{S}\\" qa-pass T-1"', 'bash -c "python \\"{S}\\" qa-pass T-1"'),
             ('sh -c "\\"{P}\\" --resolve ok"', 'sh -c "node \\"{P}\\" --resolve ok"')]


@pytest.mark.parametrize('place', EVERY)
def test_t17_1_direct_call_in_a_shell_c_payload_gets_the_twins_verdict(base, place):
    """R1-03 (T17 fix cycle 1): the I-17 twin inside a double-quoted `sh -c` payload."""
    w = _w(base, place)
    pairs = [(c.format(S=S, P=P), t.format(S=S, P=P)) for c, t in T17_1_SHC]
    got = many([(w, 'Bash', x) for pair in pairs for x in pair])
    for n, (c, twin) in enumerate(pairs):
        vc, vt = got[2 * n], got[2 * n + 1]
        assert verdict_class(vc) == verdict_class(vt), (place, c, vc, twin, vt)
    assert got[0][0] == 'DENY' and 'exact form' in got[0][1], (place, got[0])


def test_t17_1_direct_twin_is_linear_in_the_command_length():
    """R1-05 (T17 fix cycle 1): the twin is built in linear time (the hook has 10 s)."""
    import time
    import aid_guard
    t = time.perf_counter()
    assert aid_guard.direct_exec_twin('echo ' + 'gate.mjs ' * 3000) == 'echo ' + 'gate.mjs ' * 3000
    chain = aid_guard.direct_exec_twin('; '.join(['./gate.mjs --x'] * 300))
    assert chain.count('node ./gate.mjs --x') == 300, chain[:200]
    mixed = aid_guard.direct_exec_twin('./gate.mjs ' + 'gate.mjs ' * 3000)
    assert mixed.startswith('node ./gate.mjs gate.mjs') and mixed.count('node ') == 1
    # R2-04 (T17 fix cycle 2): many names inside one quoted VAR= / env value (one word), and
    # many argument words before a direct call in a substitution.
    q = 'A="' + 'gate.mjs ' * 3000 + '" gate.mjs --resolve ok'
    assert aid_guard.direct_exec_twin(q) == q[:-len('gate.mjs --resolve ok')] + 'node gate.mjs --resolve ok'
    e = aid_guard.direct_exec_twin('env A="' + 'gate.mjs ' * 1000 + '" ./gate.mjs --resolve ok')
    assert e.endswith('" node ./gate.mjs --resolve ok') and e.count('node ') == 1
    s = aid_guard.direct_exec_twin('A="' + 'aid_session.py ' * 1000 + '" ./aid_session.py approve')
    assert s.endswith('" python ./aid_session.py approve') and s.count('python ') == 1
    d = aid_guard.direct_exec_twin('echo ' + 'gate.mjs ' * 1000 + '"$(./gate.mjs --resolve ok)"')
    assert d.endswith('"$(node ./gate.mjs --resolve ok)"') and d.count('node ') == 1
    assert time.perf_counter() - t < 3.0


# R2-01 (T17 fix cycle 2): a direct call inside a command substitution, whatever its quoting,
# in an eval payload and in a PowerShell call expression gets its twin (I-17).
T17_1_SUBST = [('Bash', 'x="$({X}"{S}" qa-pass T-1)"'), ('Bash', 'echo "$({X}"{S}" reset --all)"'),
               ('Bash', 'x="$({X}"{P}" --resolve ok)"'), ('Bash', 'printf "%s" "$({X}"{S}" approve)"'),
               ('Bash', 'echo "`{X}"{P}" --resolve ok`"'), ('Bash', 'eval "{X}\\"{P}\\" --resolve ok"'),
               ('Bash', 'eval "{X}\\"{S}\\" approve"')]


@pytest.mark.parametrize('place', EVERY)
def test_t17_1_direct_call_in_a_substitution_gets_the_twins_verdict(base, place):
    w = _w(base, place)
    if place != 'non-AID':
        esc = w.P / '.aid' / 'pipeline' / 'ESCALATION.json'
        esc.parent.mkdir(parents=True, exist_ok=True)
        esc.write_text(json.dumps({'status': 'open', 'step': 'CODE_REVIEW', 'why': 'below'}), encoding='utf-8')
    pairs = []
    for tool, form in T17_1_SUBST:
        interp = 'node' if '{P}' in form else 'python'
        pairs.append((tool, form.format(X='', S=S, P=P), form.format(X=interp + ' ', S=S, P=P)))
    # PowerShell: `& ("<P>")` is `& "<P>"`; its twin is the node call.
    pairs.append(('PowerShell', '& ("{}") --resolve ok'.format(P), '& node "{}" --resolve ok'.format(P)))
    got = many([(w, tool, x) for tool, c, t in pairs for x in (c, t)])
    for n, (tool, c, twin) in enumerate(pairs):
        vc, vt = got[2 * n], got[2 * n + 1]
        assert verdict_class(vc) == verdict_class(vt), (place, tool, c, vc, twin, vt)
        if place != 'non-AID':
            assert vc[0] != 'ALLOW', (place, tool, c, vc)


def test_t17_1_non_canonical_direct_forms_are_denied_where_python_is(base):
    for place in ('p1/block', 'p4/block', 'p5/log'):
        w = _w(base, place)
        v = w.bash('env "{}" reset'.format(S))
        assert v[0] == 'DENY' and 'exact form' in v[1], (place, v)
        assert w.bash('env python "{}" reset'.format(S))[0] == 'DENY'


# --- T17-2 a direct gate.mjs call is judged like the node call ----------------------------

def _fake_root(d, name='aid'):
    (d / 'hooks').mkdir(parents=True, exist_ok=True)
    (d / '.claude-plugin').mkdir(parents=True, exist_ok=True)
    (d / 'hooks' / 'aid_session.py').write_text('print(1)\n', encoding='utf-8')
    (d / '.claude-plugin' / 'plugin.json').write_text(json.dumps({'name': name}), encoding='utf-8')
    return d


T17_2_DENY = ['env "{P}" --resolve ok', 'exec "{P}" --resolve ok', '"{P}" --resolve ok; echo y',
              '"{P}" --root . --resolve ok']
T17_2_SAME = ['{X}"{P}" --resolve "ok"', '{X}"{P}" --check-escalation', "{X}\"{P}\" --step CODE_REVIEW --scores '{{}}'",
              'env {X}"{P}" --resolve ok', 'exec {X}"{P}" --resolve ok', '{X}"{P}" --resolve ok; echo y',
              '{X}"{P}" --root . --resolve ok', 'grep resolve "{P}"']


@pytest.mark.parametrize('place', EVERY)
def test_t17_2_direct_gate_calls_get_the_node_twins_verdict(base, place):
    w = _w(base, place)
    C = base / 'c' / 'cfg'
    cache = _fake_root(C / 'plugins' / 'cache' / 'M' / 'aid' / '9.9.9')
    w.env = {'CLAUDE_CONFIG_DIR': str(C)}
    fake = str(cache).replace('\\', '/') + '/skills/pipeline-orchestrator/gate.mjs'
    pairs, jobs = [], []
    for tool in ('Bash', 'PowerShell'):
        for form in T17_2_SAME:
            c, twin = form.format(X='', P=P), form.format(X='node ', P=P)
            pairs.append((tool, c, twin))
            jobs += [(w, tool, c), (w, tool, twin)]
    exact = ['"{}" --resolve "ok"'.format(P), '"{}" --resolve "ok"'.format(fake)]
    jobs += [(w, t, c) for t in ('Bash', 'PowerShell') for c in exact]
    got = many(jobs)
    for n, (tool, c, twin) in enumerate(pairs):
        assert verdict_class(got[2 * n]) == verdict_class(got[2 * n + 1]), (place, tool, c, got[2 * n], got[2 * n + 1])
    for v in got[2 * len(pairs):]:
        assert v[0] == 'ASK' and 'ESCALATION.json' in v[1], (place, v)
    assert got[2 * T17_2_SAME.index('grep resolve "{P}"')][0] == 'ALLOW'


def test_t17_2_other_direct_resolve_spellings_are_denied_inside_aid(base):
    jobs = []
    for place in IN_AID:
        w = _w(base, place)
        skill = w.P / 'skills' / 'pipeline-orchestrator'
        skill.mkdir(parents=True, exist_ok=True)
        jobs += [(w, 'Bash', f.format(P=P)) for f in T17_2_DENY]
        jobs.append((w, 'Bash', None))
    with ThreadPoolExecutor(POOL) as ex:
        got = list(ex.map(lambda j: j[0].bash(j[2]) if j[2] else
                          j[0].bash('./gate.mjs --resolve ok', cwd=j[0].P / 'skills' / 'pipeline-orchestrator'), jobs))
    for (w, _, c), v in zip(jobs, got):
        assert v[0] == 'DENY' and '! node "{}" --resolve'.format(P) in v[1], (w.place, c, v)


@needs_bash
def test_t17_2_effect_check_escalation_stays_open(base):
    w = _w(base, 'p4/block')
    esc = w.P / '.aid' / 'pipeline' / 'ESCALATION.json'
    esc.parent.mkdir(parents=True, exist_ok=True)
    esc.write_text(json.dumps({'status': 'open', 'step': 'CODE_REVIEW', 'why': 'below'}), encoding='utf-8')
    assert w.bash('env "{}" --resolve ok'.format(P))[0] == 'DENY'
    out = run('stop-pipeline', w.P, w.H, {'session_id': 's1', 'cwd': str(w.P)})
    assert json.loads(out)['decision'] == 'block' and 'ESCALATED' in out, out
    assert json.loads(esc.read_text(encoding='utf-8'))['status'] == 'open'


# --- T17-3 non-ASCII project paths ------------------------------------------------------

CP1252 = {'PYTHONIOENCODING': 'cp1252', 'PYTHONUTF8': '0'}


def _non_ascii_name():
    return 'aid-t17-' + ''.join(map(chr, (0x4a, 0x6f, 0x73, 0xe9))) + '-' + chr(0x65e5) + chr(0x672c)


def _na(base, phase=1, level='block'):
    w = Where(base, 'p{}/{}'.format(phase, level), name=_non_ascii_name())
    w.env = dict(CP1252)
    return w


def test_t17_3_gates_work_in_a_non_ascii_project(base):
    w = _na(base)
    jobs = [('w', str(w.P / 'docs' / 'prd.md')), ('w', str(w.P / '.claude' / 'plans' / 'p.md')),
            ('b', 'mkdir -p docs/x'), ('b', 'git status')]
    deny = [('w', str(w.P / 'src' / 'a.ts')), ('w', str(w.P / '.aid' / 'state.json')),
            ('w', str(w.P / '.aid' / 'hooks' / 'config.json'))]
    with ThreadPoolExecutor(POOL) as ex:
        got = list(ex.map(lambda j: w.write(j[1]) if j[0] == 'w' else w.bash(j[1]), jobs + deny))
    for j, v in zip(jobs, got):
        assert v[0] == 'ALLOW', (j, v)
    for j, v in zip(deny, got[len(jobs):]):
        assert v[0] == 'DENY', (j, v)


def test_t17_3_session_start_in_a_non_ascii_project(base):
    w = _na(base)
    w.state(1, phase_name='PRD', current_session={'active': True, 'role': 'developer'})
    ctx = w.session_start()['hookSpecificOutput']['additionalContext']
    assert 'AID RULES' in ctx and 'Phase: 1 (PRD)' in ctx, ctx


def test_t17_3_qa_gate_in_a_non_ascii_project(base):
    w = _na(base, 4)
    (w.P / '.aid' / 'qa').mkdir(parents=True, exist_ok=True)
    crit = w.P / '.aid' / 'qa' / 'T-1.yaml'
    crit.write_text('criteria: []\n', encoding='utf-8')
    (w.P / '.aid' / 'context.json').write_text(json.dumps({'current_task': {'id': 'T-1', 'title': 't'}}),
                                               encoding='utf-8')
    out = run('stop-qa', base, w.H, {'session_id': 's1', 'cwd': str(w.P)}, w.env)
    assert json.loads(out)['decision'] == 'block' and 'T-1' in json.loads(out)['reason'], out
    digest = hashlib.sha256(crit.read_bytes()).hexdigest()
    w.state(4, qa_passed={'T-1': {'criteria_sha256': digest}})
    assert run('stop-qa', base, w.H, {'session_id': 's1', 'cwd': str(w.P)}, w.env) == ''


@needs_bash
def test_t17_3_dev_pipeline_gate_resolves_a_non_ascii_cwd(base):
    w = _na(base, 4)
    esc = w.P / '.aid' / 'pipeline' / 'ESCALATION.json'
    esc.parent.mkdir(parents=True, exist_ok=True)
    esc.write_text(json.dumps({'status': 'open', 'step': 'TDD', 'why': 'x'}), encoding='utf-8')
    out = run('stop-pipeline', base, w.H, {'session_id': 's1', 'cwd': str(w.P)}, w.env)
    assert out and json.loads(out)['decision'] == 'block' and 'ESCALATED' in out, out


def test_t17_3_invalid_utf8_stdin_is_malformed_input(base):
    w = _w(base, 'p1/block')
    for hook in ('phase-gate-bash', 'phase-gate-write'):
        out = run(hook, w.P, w.H, None, CP1252, raw=b'{"cwd": "\xff\xfe\xfa", "tool_input": {"command": "ls"}}')
        v = decision(out)
        assert v[0] == 'DENY' and 'could not evaluate' in v[1], (hook, v)


# --- T17-4 hook text spawns the plugin's reviewers; criteria are additive ----------------

BANNED = (re.compile(r'project-first', re.I), re.compile(r'overrides it', re.I),
          re.compile(r'\bproject\b[^.\n]*\boverrides\b', re.I), re.compile(r'else the plugin', re.I))


@needs_bash
@pytest.mark.parametrize('route', ['plugin', 'link'])
def test_t17_4_plan_hook_names_the_plugin_reviewers(base, route):
    env = {'CLAUDE_PLUGIN_ROOT': R} if route == 'plugin' else {}
    payload = {'tool_name': 'ExitPlanMode', 'cwd': str(base), 'session_id': 's1',
               'tool_response': {'plan': '## Plan\nAdd a form.'}}
    out = run('plan-approved', base, base / 'home', payload, env)
    ctx = json.loads(out)['hookSpecificOutput']['additionalContext']
    assert 'project files may only add criteria' in ctx and 'project-first' not in ctx, ctx
    assert "else the plugin's" not in ctx
    if route == 'plugin':
        assert 'aid:<name>' in ctx
    else:
        assert "this linked project's .claude/agents is AID's linked folder" in ctx and 'aid:<name>' not in ctx


@pytest.mark.parametrize('route', ['plugin', 'link'])
def test_t17_4_qa_gate_spawns_the_plugin_agent(base, route):
    w = _w(base, 'p4/block')
    (w.P / '.aid' / 'qa').mkdir(parents=True, exist_ok=True)
    (w.P / '.aid' / 'qa' / 'T-1.yaml').write_text('c: 1\n', encoding='utf-8')
    (w.P / '.aid' / 'context.json').write_text(json.dumps({'current_task': {'id': 'T-1'}}), encoding='utf-8')
    env = {'CLAUDE_PLUGIN_ROOT': R} if route == 'plugin' else {}
    reason = json.loads(run('stop-qa', w.P, w.H, {'session_id': 's1', 'cwd': str(w.P)}, env))['reason']
    if route == 'plugin':
        assert 'subagent_type="aid:qa-validator-agent"' in reason, reason
    else:
        assert 'subagent_type="qa-validator-agent"' in reason, reason
        assert "this linked project's .claude/agents is AID's linked folder" in reason


def test_t17_4_no_banned_phrase_in_hook_text():
    hits = []
    for f in sorted(HOOKS.glob('*.py')):
        for node in ast.walk(ast.parse(f.read_text(encoding='utf-8'))):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                hits += ['{}: {}'.format(f.name, rx.pattern) for rx in BANNED if rx.search(node.value)]
                if 'subagent_type="qa-validator-agent"' in node.value:
                    hits.append('{}: bare qa-validator-agent spawn'.format(f.name))
    for f in sorted(HOOKS.glob('*.sh')):
        for n, line in enumerate(f.read_text(encoding='utf-8').splitlines(), 1):
            hits += ['{}:{}: {}'.format(f.name, n, rx.pattern) for rx in BANNED if rx.search(line)]
    assert not hits, hits


# --- T17-5 SessionStart / UserPromptSubmit never crash on context.json -------------------

INIT_DOC: dict = {'$schema': 'aid-context-v1', 'version': '1.0', 'last_updated': '2026-11-20T10:00:00Z',
            'current_task': None, 'current_step': None,
            'progress': {'steps_completed': [], 'steps_pending': []}, 'session_notes': [], 'blockers': []}
SHAPES = {
    'init': json.dumps(INIT_DOC),
    'run3-context-update': json.dumps({'current_task': {'id': 'T1', 'title': 'Add tagging to notes',
                                                        'current_step': 'x', 'progress': 40},
                                       'current_step': 'Implement tags'}),
    'run3-good-morning': json.dumps({'current_task': {'id': 'T1', 'title': 'Add tagging to notes'},
                                     'blockers': ['Docker check denied']}),
    'key': json.dumps({'current_task': {'key': 'T1', 'title': 'Add tagging to notes'}}),
    'jira_key': json.dumps({'current_task': {'jira_key': 'T1', 'title': 'Add tagging to notes'}}),
    'task-string': json.dumps({'current_task': 'T1', 'current_step': {'name': 's'}}),
    'blockers-dict': json.dumps({'blockers': {'description': 'x'}}),
    'blockers-mixed': json.dumps({'blockers': [1, None, {'severity': 'high', 'description': 'real'}]}),
    'progress-string': json.dumps({'progress': '40%'}),
    'list': json.dumps([1, 2]), 'string': json.dumps('hello'), 'invalid': '{"current_task": ',
    'bom': chr(0xFEFF) + json.dumps({'current_task': {'id': 'T1', 'title': 'x'}}), 'empty': '',
    # R1-02 (T17 fix cycle 1): json.load raises RecursionError (not ValueError) on these.
    'deep-array': '[' * 200000 + ']' * 200000,
    'deep-object': '{"current_task": ' + '{"a": ' * 50000 + '1' + '}' * 50000 + '}',
}


def _session_project(base, shape):
    w = _w(base, 'p1/block', name='s_' + shape.replace('-', '_'))
    w.state(1, phase_name='PRD', current_session={'active': True, 'role': 'developer'})
    (w.P / '.aid' / 'context.json').write_text(SHAPES[shape], encoding='utf-8')
    return w


def _errors(w):
    f = w.P / '.aid' / 'audit' / 'errors.log'
    return f.read_text(encoding='utf-8') if f.is_file() else ''


@pytest.mark.parametrize('shape', sorted(SHAPES))
def test_t17_5_session_start_survives_every_context_shape(base, shape):
    w = _session_project(base, shape)
    ctx = w.session_start()['hookSpecificOutput']['additionalContext']
    assert AID_RULES in ctx and '=== AID SESSION CONTEXT ===' in ctx, ctx
    assert 'Traceback' not in _errors(w) and 'Error' not in _errors(w), _errors(w)
    out = py_hook(['--event', 'UserPromptSubmit'], w.P, w.H, {'session_id': 's1', 'cwd': str(w.P)})
    assert out and '[AID: Phase 1' in out and 'Error' not in _errors(w), (out, _errors(w))


def test_t17_5_session_start_context_lines(base):
    lines = {}
    for shape in ('run3-context-update', 'run3-good-morning', 'key', 'jira_key', 'task-string', 'blockers-mixed'):
        lines[shape] = _session_project(base, shape).session_start()['hookSpecificOutput']['additionalContext']
    assert 'Current Task: T1 - Add tagging to notes' in lines['run3-context-update']
    assert 'Current Step: Implement tags' in lines['run3-context-update']
    assert '  - [?] Docker check denied' in lines['run3-good-morning']
    for shape in ('key', 'jira_key'):
        assert 'Current Task: T1 - Add tagging to notes' in lines[shape], lines[shape]
    assert 'Current Step: s' in lines['task-string'] and 'Current Task' not in lines['task-string']
    assert 'Blockers: 1' in lines['blockers-mixed'] and '  - [high] real' in lines['blockers-mixed']
    assert 'Current Task: ?' not in ''.join(lines.values())


def test_t17_5_user_prompt_submit_shows_the_task_id(base):
    w = _session_project(base, 'run3-context-update')
    out = py_hook(['--event', 'UserPromptSubmit'], w.P, w.H, {'session_id': 's1', 'cwd': str(w.P)})
    assert '| Task: T1]' in out, out


# --- T17-6 the hook audit log keeps no F5 secret ----------------------------------------

def _t17_6_commands(v):
    return ['psql postgres://u:{}@db/x'.format(v), 'redis-cli -u redis://:{}@h'.format(v),
            (CURL + ' -u admin:{} https://h').format(v), 'mysql -p{} db'.format(v), 'tool --password {}'.format(v),
            'echo \'{{"password": "{}"}}\''.format(v), 'cat x > .aid/state.json # DB_PASSWORD={}'.format(v)]


def _audit_run(w, hooks_dir, v):
    cmds = _t17_6_commands(v)
    runner = Path(hooks_dir) / 'hook-runner.mjs'
    for c in cmds:
        payload = w._payload('Bash', {'command': c})
        run('phase-gate-bash', w.P, w.H, payload, w.env, runner)
        py_hook(['--event', 'PostToolUse', '--action', 'audit_log'], w.P, w.H, payload, w.env, hooks_dir)
    log = (w.P / '.aid' / 'audit' / 'tool-usage.jsonl').read_text(encoding='utf-8')
    assert log.count('PostToolUse') == len(cmds) and '"PreToolUse"' in log, log
    assert v not in log, log


def _primary_redacts_f5():
    sys.path.insert(0, str(REPO / 'memory-system'))
    try:
        from memory_system.redact import redact
    except Exception:
        return False
    v = secret('Zq', '7w', 'Rk')
    return v not in redact('tool --password ' + v) and v not in redact('mysql -p' + v)


def test_t17_6_audit_log_keeps_no_secret(base):
    # WS-B (T17-14) has landed: the primary path runs unconditionally (no skip).
    assert _primary_redacts_f5(), 'memory_system.redact must cover the I-20 forms (T17-14)'
    _audit_run(_w(base, 'p4/block'), HOOKS, secret('Hun', 'ter', '2', 'Pw9'))


def _i20_forms(v):
    return ['x mongodb+srv://a:{}@h/y.'.format(v), (CURL + ' --user=admin:{} h').format(v),
            'MySQL -uroot -p{}'.format(v), 'sshpass -p {} ssh h'.format(v), 't --token={}'.format(v),
            't --api-key {}'.format(v), 't --client-secret {}'.format(v), 't --pass {}'.format(v),
            "'api_key':'{}'".format(v), '"DB_PASSWORD"="{}"'.format(v), 'password="two {}"'.format(v),
            'pass={}'.format(v), 'PASS: {}'.format(v), 'Authorization: Token {}'.format(v),
            'Authorization: Digest {}'.format(v)] + _t17_6_commands(v)


I20_UNCHANGED = ['ssh -p 22 h', 'psql -p 5432', 'bypass=1', 'pass_rate=0.9', 'passes=3', 'rating 4',
                 'mysql -p db', 't --password -x']


@pytest.mark.parametrize('route', ['primary', 'fallback'])
def test_t17_6_audit_redact_mirrors_the_i20_forms(monkeypatch, route):
    """The fallback (_FALLBACK_SECRETS) mirrors memory_system.redact for every I-20 form."""
    import aid_hooks
    monkeypatch.setattr(aid_hooks, '_REDACT', [None] if route == 'fallback' else [])
    v = secret('Zq', '7w', 'Rk', '41')
    for c in _i20_forms(v):
        out = aid_hooks.audit_redact(c)
        assert v not in out and out == aid_hooks.audit_redact(out), (route, c, out)
    for c in I20_UNCHANGED:
        assert aid_hooks.audit_redact(c) == c, (route, c)
    assert aid_hooks.audit_redact(CURL + ' -u admin:' + v + ' h') == CURL + ' -u admin:[token] h'
    assert aid_hooks.audit_redact('mysql -p' + v + ' db') == 'mysql -p[token] db'
    # R2-03 (T17 fix cycle 2): quoted or attached MySQL / sshpass passwords, on both routes.
    for c, want in (("mysql -u root -p'{}' db", "mysql -u root -p'[token]' db"),
                    ('mysql -u root -p"{}" db', 'mysql -u root -p"[token]" db'),
                    ("sshpass -p'{}' ssh h", "sshpass -p'[token]' ssh h"),
                    ('sshpass -p{} ssh h', 'sshpass -p[token] ssh h')):
        assert aid_hooks.audit_redact(c.format(v)) == want, (route, c)
    assert aid_hooks.audit_redact('{"password": "' + v + '"}') == '{"password": "[token]"}'


def test_t17_6_fallback_audit_log_keeps_no_secret(base):
    """memory_system unimportable: the hooks run from a copy with no memory-system/ beside it."""
    fake = base / 'fake-root' / 'hooks'
    shutil.copytree(str(HOOKS), str(fake), ignore=shutil.ignore_patterns('__pycache__'))
    assert not (fake.parent / 'memory-system').exists()
    _audit_run(_w(base, 'p4/block'), fake, secret('Hun', 'ter', '2', 'Pw9'))


# --- T17-7 the pre-Phase-4 git add/commit message ---------------------------------------

def test_t17_7_pre4_message_names_the_users_git_hooks(base):
    w = _w(base, 'p1/block')
    v = w.bash('npm test')
    assert v[0] == 'DENY' and 'run no project code' not in v[1], v
    assert ('git add/commit are allowed; your own git hooks (pre-commit, core.hooksPath) still run '
            'when you commit') in v[1], v
    assert w.bash('git add docs')[0] == 'ALLOW'


# --- T17-8 the recommendation queue is a control path -----------------------------------

@pytest.mark.parametrize('place', IN_AID)
def test_t17_8_recommendation_queue_is_protected(base, place):
    w = _w(base, place)
    q = w.H / '.aid' / 'recommendations' / 'queue.json'
    q.parent.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(POOL) as ex:
        got = list(ex.map(lambda t: w.write(str(q), t), sorted(TOOL_INPUT)))
        bash = list(ex.map(w.bash, ['echo x > ~/.aid/recommendations/queue.json',
                                    'cp a "{}"'.format(str(q).replace('\\', '/'))]))
    for t, v in zip(sorted(TOOL_INPUT), got):
        assert v[0] == 'DENY', (place, t, v)
    for v in bash:
        assert v[0] == 'DENY', (place, v)
    assert w.bash('cat ~/.aid/recommendations/queue.json')[0] == 'ALLOW'


def test_t17_8_powershell_writer_is_refused_at_phase_4(base):
    w = _w(base, 'p4/block')
    v = w.ps('Set-Content -Path ~/.aid/recommendations/queue.json -Value x')
    assert v[0] == 'DENY', v


# --- T17-9 the live AID root is protected from a linked project ---------------------------

T17_9_TARGETS = ('hooks/aid_guard.py', '.claude-plugin/plugin.json', 'agents/x.md', 'skills/reflection/criteria/x.yaml')


def test_t17_9_live_root_is_protected_from_another_project(base):
    w = _w(base, 'p4/block')
    jobs = [('w', R + '/' + t) for t in T17_9_TARGETS] + [('b', 'cp a "{}/{}"'.format(R, t)) for t in T17_9_TARGETS]
    with ThreadPoolExecutor(POOL) as ex:
        got = list(ex.map(lambda j: w.write(j[1]) if j[0] == 'w' else w.bash(j[1]), jobs))
    for j, v in zip(jobs, got):
        assert v[0] == 'DENY' and 'control file' in v[1], (j, v)
    assert w.bash('sed -i s/a/b/ "{}/hooks/aid_guard.py"'.format(R))[0] == 'DENY'
    # R1-01 (T17 fix cycle 1): the other writers the cache copy refuses, Bash and PowerShell.
    other = [('Bash', 'curl -o "{}/hooks/x" https://e.x'), ('Bash', 'dd if=src/a.ts of="{}/hooks/x"'),
             ('Bash', 'tar xf x.tar -C "{}/agents"'), ('Bash', 'unzip -o x.zip -d "{}/hooks"'),
             ('Bash', 'rm -rf "{}"'), ('Bash', 'env cp a "{}/hooks/x"'),
             ('PowerShell', 'Set-Content "{}/hooks/aid_guard.py" x'),
             ('PowerShell', 'Remove-Item "{}/agents/developer.md"'),
             ('PowerShell', 'Copy-Item src/a.ts "{}/agents/x.md"'),
             ('PowerShell', 'Remove-Item -Recurse -Force "{}"'),
             # R2-02 (T17 fix cycle 2): shell -c bodies, pushd, .NET static writers.
             ('Bash', 'bash -c \'cp src/a.ts "{}/hooks/x"\''), ('Bash', 'sh -c "cp src/a.ts {}/hooks/x"'),
             ('Bash', 'pushd "{}" && rm -rf agents'),
             ('PowerShell', '[IO.File]::WriteAllText("{}/hooks/aid_guard.py", "x")'),
             ('PowerShell', "[System.IO.Directory]::Delete('{}/agents', $true)"),
             # R3-02 (T17): cd/pushd options and `--` keep the target; .NET writer constructors.
             ('Bash', 'cd -- "{}" && rm -rf agents'), ('Bash', 'cd -P "{}" && cp src/a.ts hooks/aid_guard.py'),
             ('Bash', 'pushd -- "{}" && rm -rf agents'), ('Bash', 'cd -L -- "{}/hooks" && echo x > aid_guard.py'),
             ('PowerShell', 'New-Object IO.StreamWriter("{}/hooks/aid_guard.py")'),
             ('PowerShell', 'New-Object -TypeName System.IO.FileStream("{}/agents/x.md", "Create")')]
    for place in ('p4/block', 'p1/log', 'p5/warn'):
        wp = w if place == 'p4/block' else _w(base, place)
        got = many([(wp, tool, c.format(R)) for tool, c in other])
        for (tool, c), v in zip(other, got):
            assert v[0] == 'DENY' and 'control file' in v[1], (place, tool, c, v)
    # Reading or running a live-root file is not writing it (no new false denial).
    for c in ('cat "{}/hooks/aid_guard.py"'.format(R), 'grep -r x "{}/agents"'.format(R),
              'pythonw "{}" status'.format(S), 'node "{}/hooks/hook-runner.mjs" x'.format(R),
              'pushd "{}" && ls hooks'.format(R), 'cd -- "{}" && ls hooks'.format(R),
              'cd -P src && echo x > out.txt', 'echo done 2>&1 | tee x.log'):
        assert w.bash(c)[0] == 'ALLOW', c
    assert w.ps('[IO.File]::ReadAllText("{}/hooks/aid_guard.py")'.format(R))[0] == 'ALLOW'


def test_t17_9_the_live_root_as_the_project_is_unchanged(base):
    """AID's own repo (the project IS the live root): its hooks/ and agents/ stay writable."""
    root = base / 'liveproj'
    shutil.copytree(str(HOOKS), str(root / 'hooks'), ignore=shutil.ignore_patterns('__pycache__'))
    w = Where(base, 'p4/block', name='liveproj')
    w.runner = root / 'hooks' / 'hook-runner.mjs'
    for t in ('agents/x.md', 'skills/reflection/criteria/x.yaml', 'hooks/new_file.py'):
        assert w.write(str(root / t))[0] == 'ALLOW', t


# --- T17-10 SessionStart wording at log/warn --------------------------------------------

@pytest.mark.parametrize('level', LEVELS)
def test_t17_10_restriction_line_matches_the_level(base, level):
    w = _w(base, 'p1/' + level)
    w.state(1, phase_name='PRD', current_session={'active': True, 'role': 'developer'})
    ctx = w.session_start()['hookSpecificOutput']['additionalContext']
    line = next(l for l in ctx.splitlines() if 'PHASE RESTRICTION' in l)
    if level == 'block':
        assert 'NOT allowed until Phase 4' in line, line
    else:
        assert 'NOT allowed' not in line and 'NOT stopped' in line and ': ' + level in line, line


# --- T17-11 no constant-folded fake token in a .pyc --------------------------------------

def test_t17_11_no_gh_token_prefix_in_compiled_tests(tmp_path):
    # Named without the fine-grained PAT prefix: `github` + `_pat_` + text is a token shape
    # to secret scanners (the HOL scanner flagged the old name as a hardcoded secret).
    prefix = ''.join(['gh', 'p_']).encode('ascii')
    here = Path(__file__).resolve().parent
    files = [here / 'test_t16_gate.py'] + sorted(here.glob('test_t17_*.py'))
    for f in files:
        out = py_compile.compile(str(f), cfile=str(tmp_path / (f.stem + '.pyc')), doraise=True)
        assert prefix not in Path(out).read_bytes(), f.name


# --- T17-12 read-only find over user config dirs stays a safe-direction denial ------------

def test_t17_12_find_over_user_config_is_a_pinned_false_denial(base):
    w = _w(base, 'p4/block')
    got = many([(w, 'Bash', "find ~/.claude -path '*agents*' -name x.md"), (w, 'Bash', 'ls ~/.claude'),
                (w, 'Bash', 'ls ~/.aid'), (w, 'Bash', 'find src -name x')])
    assert got[0][0] == 'DENY', got[0]
    assert [v[0] for v in got[1:]] == ['ALLOW'] * 3, got


# --- T17-13 the gate allows the checklist call silently ----------------------------------

def test_t17_13_checklist_is_allowed_silently_everywhere(base):
    jobs = []
    for place in EVERY:
        w = _w(base, place)
        jobs += [(w, 'Bash', c) for c in ('python "{}" checklist'.format(S), 'python "{}" checklist --phase 0'.format(S),
                                          '"{}" checklist'.format(S))]
    for (w, _, c), v in zip(jobs, many(jobs)):
        assert v == ('ALLOW', None), (w.place, c, v)
