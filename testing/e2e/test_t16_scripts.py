"""
T16 WS-F: install, link-project and scaffold (T16-acceptance.md, T16-63 .. T16-70).

WHY THESE TESTS:
- PROBLEM: a clone + link-project install registered no PreToolUse gate at all: the
  settings.json it copied only named legacy Stop/PostToolUse shell lines (audit R-01, high).
  link-project.sh/.bat and the installers wrote `.aid/state.json` themselves, although
  `hooks/aid_session.py` is meant to be its only writer (functional g9, medium). The
  /start-project scaffold pinned `next ^14`, which resolves to versions with high/critical
  advisories (R-06).
- COST OF FAILURE: a project that looks protected runs with no phase gate; state written in
  a shape the session code never produced; a new project starts with known-vulnerable deps.
- SUCCESS: the real link-project, run from this checkout (a path with spaces and an
  apostrophe) into a drive-root temp project, registers plugin.json's hooks with absolute
  paths, and the registered commands, spawned exactly as written, gate the project.

Harness: fake HOME/USERPROFILE/AID_HOME; CLAUDE_PROJECT_DIR and CLAUDE_CONFIG_DIR unset. Probe
projects live under a drive-root temp dir: a ~/.aid/state.json makes every folder below the
user profile an AID project.
"""
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
R = os.path.realpath(str(REPO)).replace('\\', '/')
LINK_SH = REPO / 'link-project.sh'
LINK_BAT = REPO / 'link-project.bat'
INIT_SCRIPT = REPO / 'scripts' / 'init-project.sh'
PLUGIN = json.loads((REPO / '.claude-plugin' / 'plugin.json').read_text(encoding='utf-8'))
EVENTS = ('SessionStart', 'PreToolUse', 'PostToolUse', 'Stop')
NODE = shutil.which('node')


def _posix_bash():
    """Git Bash on Windows (System32 bash.exe is WSL, which cannot see these paths)."""
    if os.name == 'nt':
        git = shutil.which('git')
        here = Path(git).resolve() if git else None
        for cand in ([here.parents[1] / 'bin' / 'bash.exe',
                      here.parents[2] / 'bin' / 'bash.exe'] if here else []):
            if cand.is_file():
                return str(cand)
        return None
    return shutil.which('bash')


BASH = _posix_bash()
needs_bash = pytest.mark.skipif(BASH is None or NODE is None, reason='needs a POSIX bash and node')
needs_bat = pytest.mark.skipif(os.name != 'nt' or NODE is None, reason='link-project.bat runs on Windows')


def _marker_above(p):
    return any((d / '.aid' / 'state.json').is_file() or (d / '.aid' / 'hooks' / 'config.json').is_file()
               for d in [p] + list(p.parents))


def _is_link(path):
    """A symlink or a Windows junction: removed as a link, never descended into (the links
    point at THIS checkout)."""
    try:
        st = os.lstat(path)
    except OSError:
        return False
    if stat.S_ISLNK(st.st_mode):
        return True
    return bool(getattr(st, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0))


def _safe_rmtree(root):
    root = str(root)
    if not os.path.exists(root) and not _is_link(root):
        return
    if _is_link(root):
        try:
            os.rmdir(root)
        except OSError:
            os.unlink(root)
        return
    if os.path.isdir(root):
        for name in os.listdir(root):
            _safe_rmtree(os.path.join(root, name))
        os.chmod(root, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
        os.rmdir(root)
    else:
        os.chmod(root, stat.S_IWRITE | stat.S_IREAD)
        os.unlink(root)


@pytest.fixture
def base(tmp_path):
    """A drive-root temp dir with no AID marker above it."""
    alt = Path(tempfile.mkdtemp(prefix='aid-t16f-', dir=tmp_path.anchor if os.name == 'nt' else None))
    if _marker_above(alt):
        _safe_rmtree(alt)
        pytest.skip('no directory without an AID marker ancestor is available')
    (alt / 'home' / '.claude').mkdir(parents=True)
    (alt / 'proj').mkdir()
    yield alt
    _safe_rmtree(alt)


def _env(home, path=None):
    env = dict(os.environ, HOME=str(home), USERPROFILE=str(home), AID_HOME=str(Path(home) / '.aid'))
    env.pop('CLAUDE_PROJECT_DIR', None)
    env.pop('CLAUDE_CONFIG_DIR', None)
    if path is not None:
        env['PATH'] = path
    return env


def link_sh(target, home, *extra, path=None):
    p = subprocess.run([BASH, LINK_SH.as_posix(), Path(target).as_posix(), '--force', *extra],
                       cwd=str(REPO), env=_env(home, path), stdin=subprocess.DEVNULL,
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
    return p.returncode, p.stdout + p.stderr


def link_bat(target, home, *extra, path=None):
    p = subprocess.run([str(LINK_BAT), str(target), '--force', *extra], cwd=str(REPO),
                       env=_env(home, path), stdin=subprocess.DEVNULL, capture_output=True,
                       text=True, encoding='utf-8', errors='replace', timeout=600)
    return p.returncode, p.stdout + p.stderr


LINKERS = [pytest.param(link_sh, marks=needs_bash, id='sh'),
           pytest.param(link_bat, marks=needs_bat, id='bat')]


def expected_hooks():
    """plugin.json's hooks, ${CLAUDE_PLUGIN_ROOT} -> this checkout's real path (I-9)."""
    out = {}
    for event in EVENTS:
        groups = json.loads(json.dumps(PLUGIN['hooks'][event]))
        for g in groups:
            for h in g['hooks']:
                h['args'] = [a.replace('${CLAUDE_PLUGIN_ROOT}', R) for a in h['args']]
        out[event] = groups
    return out


def settings(target):
    return json.loads((Path(target) / '.claude' / 'settings.json').read_text(encoding='utf-8'))


def decision(out):
    if not out.strip():
        return 'ALLOW', None
    hso = json.loads(out).get('hookSpecificOutput', {})
    d = hso.get('permissionDecision')
    if d in ('deny', 'ask'):
        return d.upper(), hso.get('permissionDecisionReason')
    return 'ALLOW', hso.get('additionalContext')


def spawn(hook, target, home, payload):
    """Run one registered hook exactly as Claude Code does: command + args, no shell."""
    p = subprocess.run([hook['command']] + hook['args'], input=json.dumps(payload), cwd=str(target),
                       env=_env(home), capture_output=True, text=True, encoding='utf-8',
                       errors='replace', timeout=120)
    return p.returncode, p.stdout, p.stderr


def registered(target, event, matcher=None):
    for g in settings(target)['hooks'][event]:
        if g.get('matcher') == matcher:
            return g['hooks']
    raise AssertionError('no {} group with matcher {!r}'.format(event, matcher))


def drive_registered_hooks(target, home):
    """T16-63: the registered commands gate the linked project (after the init of T16-64)."""
    sid = lambda: uuid.uuid4().hex     # noqa: E731  (a fresh first-use baseline per call)
    (start,) = registered(target, 'SessionStart')
    rc, out, err = spawn(start, target, home, {'session_id': sid(), 'source': 'startup', 'cwd': str(target)})
    assert rc == 0, err
    assert re.search(r'Phase:? 0\b', decision(out)[1] or ''), out

    (write,) = registered(target, 'PreToolUse', 'Write|Edit|MultiEdit|NotebookEdit')
    (bash,) = registered(target, 'PreToolUse', 'Bash|PowerShell')

    def call(hook, tool, tool_input):
        rc, out, err = spawn(hook, target, home, {'session_id': sid(), 'cwd': str(target),
                                                  'tool_name': tool, 'tool_input': tool_input})
        assert rc == 0, err
        return decision(out)

    assert call(write, 'Write', {'file_path': 'src/a.ts', 'content': 'x'})[0] == 'DENY'
    assert call(bash, 'Bash', {'command': 'npm test'})[0] == 'DENY'
    assert call(write, 'Write', {'file_path': '.aid/state.json', 'content': '{}'})[0] == 'DENY'
    approve = 'python "{}/hooks/aid_session.py" approve'.format(R)
    assert call(bash, 'Bash', {'command': approve})[0] == 'ASK'

    for hook in registered(target, 'Stop'):
        rc, out, err = spawn(hook, target, home, {'session_id': sid(), 'cwd': str(target),
                                                  'hook_event_name': 'Stop', 'stop_hook_active': False})
        assert rc == 0, (hook['args'], out, err)
        # No open escalation. (Other Stop checks, such as the language checks on the
        # project's changed files, may still speak; they are not what T16-63 tests.)
        assert 'escalat' not in out.lower(), (hook['args'], out)


# --- T16-63 link-project registers the plugin's gates (E1, R-01) ---------------------------

@pytest.mark.parametrize('link', LINKERS)
def test_t16_63_link_registers_plugin_hooks_and_they_gate(base, link):
    T, H = base / 'proj', base / 'home'
    rc, out = link(T, H)
    assert rc == 0, out
    data = settings(T)
    want = expected_hooks()
    for event in EVENTS:
        assert data['hooks'][event] == want[event], (event, data['hooks'].get(event))
    for g in data['hooks']['PreToolUse']:
        assert [(h['onFailure'], h['timeout']) for h in g['hooks']] == [('block', 10)], g
    if os.name == 'nt':
        # On the owner's machine the real AID path has spaces and an apostrophe, the hard quoting
        # case; a CI checkout (/home/runner/work/AID/AID) has neither.
        assert "'" in R and ' ' in R, 'the test must use the real AID path (spaces + apostrophe)'
    # The permissions block comes from the AID settings template.
    tmpl = json.loads((REPO / '.claude' / 'settings.json').read_text(encoding='utf-8'))
    assert data['permissions'] == tmpl['permissions']
    first = (T / '.claude' / 'settings.json').read_bytes()

    rc, out = link(T, H)
    assert rc == 0, out
    assert (T / '.claude' / 'settings.json').read_bytes() == first, 'second run changed settings.json'

    # T16-70 (G9 re-check): .mcp.json exists and is gitignored.
    assert (T / '.mcp.json').is_file()
    if shutil.which('git'):
        subprocess.run(['git', 'init', '-q', str(T)], check=True, capture_output=True, env=_env(H))
        ig = subprocess.run(['git', '-C', str(T), 'check-ignore', '-q', '.mcp.json'], env=_env(H))
        assert ig.returncode == 0, '.mcp.json is not gitignored in the linked project'

    drive_registered_hooks(T, H)


@pytest.mark.parametrize('link', LINKERS)
def test_t16_63_existing_settings_keep_user_entries_and_utf16(base, link):
    T, H = base / 'proj', base / 'home'
    (T / '.claude').mkdir()
    user_hook = {'type': 'command', 'command': 'echo user-stop-hook'}
    legacy = {'type': 'command', 'command': 'bash .claude/hooks/dev-pipeline-gate.sh'}
    old = {'model': 'user-choice',
           'permissions': {'allow': ['Bash(npm run lint)']},
           'hooks': {'Stop': [{'hooks': [user_hook]}, {'hooks': [legacy]}]}}
    s = T / '.claude' / 'settings.json'
    s.write_bytes(b'\xff\xfe' + json.dumps(old, indent=2).encode('utf-16-le'))
    rc, out = link(T, H)
    assert rc == 0, out
    raw = s.read_bytes()
    assert raw.startswith(b'\xff\xfe'), 'UTF-16 settings.json was rewritten in another encoding'
    data = json.loads(raw[2:].decode('utf-16-le'))
    assert data['model'] == 'user-choice'
    assert data['permissions'] == {'allow': ['Bash(npm run lint)']}
    stop = [h for g in data['hooks']['Stop'] for h in g['hooks']]
    assert user_hook in stop
    assert legacy not in stop, 'the legacy AID Stop line was not replaced by its runner equivalent'
    want = expected_hooks()
    for event in EVENTS:
        for g in want[event]:
            for h in g['hooks']:
                have = [x for grp in data['hooks'][event] if grp.get('matcher') == g.get('matcher')
                        for x in grp['hooks']]
                assert have.count(h) == 1, (event, h['args'][1], data['hooks'][event])
    rc, out = link(T, H)
    assert rc == 0, out
    assert s.read_bytes() == raw, 'second run changed an existing settings.json'


@pytest.mark.parametrize('link', LINKERS)
def test_t16_63_unparseable_settings_left_untouched(base, link):
    T, H = base / 'proj', base / 'home'
    (T / '.claude').mkdir()
    s = T / '.claude' / 'settings.json'
    s.write_bytes(b'{"permissions": oops\n')
    rc, out = link(T, H)
    assert rc != 0, out
    assert s.read_bytes() == b'{"permissions": oops\n'
    assert not (T / '.aid' / 'state.json').exists()


def _path_without(*names, keep=()):
    """A PATH holding only `keep` dirs, checked to contain none of `names`."""
    path = os.pathsep.join(str(k) for k in keep)
    for n in names:
        if shutil.which(n, path=path):
            pytest.skip('{} is in {}; cannot build a PATH without it'.format(n, path))
    return path


def _git_bash_dirs():
    b = Path(BASH).parent
    return [b, b.parent / 'usr' / 'bin', b.parent.parent / 'usr' / 'bin', b.parent / 'mingw64' / 'bin']


def _system_dirs():
    root = os.environ.get('SystemRoot', r'C:\Windows')
    return [Path(root) / 'System32']


@needs_bash
def test_t16_63_sh_without_node_writes_no_settings(base):
    T, H = base / 'proj', base / 'home'
    path = _path_without('node', keep=[d for d in _git_bash_dirs() if d.is_dir()])
    rc, out = link_sh(T, H, path=path)
    assert rc != 0, out
    assert 'node' in out.lower(), out
    assert not (T / '.claude').exists(), 'link-project wrote into the project without node'
    assert not (T / '.aid').exists()


@needs_bat
def test_t16_63_bat_without_node_writes_no_settings(base):
    T, H = base / 'proj', base / 'home'
    path = _path_without('node', keep=_system_dirs())
    rc, out = link_bat(T, H, path=path)
    assert rc != 0, out
    assert 'node' in out.lower(), out
    assert not (T / '.claude').exists(), 'link-project.bat wrote into the project without node'
    assert not (T / '.aid').exists()


def test_t16_63_link_bat_stays_crlf():
    data = LINK_BAT.read_bytes()
    assert data.count(b'\n') == data.count(b'\r\n'), 'link-project.bat has LF-only lines'


def test_t16_63_one_generator_and_no_hook_json_in_the_linkers():
    for script in (LINK_SH, LINK_BAT):
        text = script.read_text(encoding='utf-8')
        assert 'link-settings.mjs' in text, script.name
        for word in ('hook-runner', 'PreToolUse', 'SessionStart', 'onFailure'):
            assert word not in text, (script.name, word)
        assert not re.search(r'(cp|copy)\s+"[^"\n]*\.claude[\\/]settings\.json"', text), \
            '{} still copies the settings template'.format(script.name)


# --- T16-64 the linkers and installers write no state themselves (E3, I-10) ----------------

@pytest.mark.parametrize('link', LINKERS)
def test_t16_64_state_comes_from_aid_session_init(base, link):
    T, H = base / 'proj', base / 'home'
    rc, out = link(T, H, '--role', 'developer')
    assert rc == 0, out
    assert 'state.json created by aid_session.py init' in out, out
    state = json.loads((T / '.aid' / 'state.json').read_text(encoding='utf-8'))
    assert state['role'] == 'developer' and state['current_phase'] == 0, state
    assert state.get('phase_display') and isinstance(state.get('skills_loaded'), list), state
    assert '$schema' not in state, 'the old link-project heredoc shape'
    ctx = json.loads((T / '.aid' / 'context.json').read_text(encoding='utf-8'))
    assert ctx['$schema'] == 'aid-context-v1'


@needs_bash
def test_t16_64_default_role_is_the_first_menu_entry(base):
    T, H = base / 'proj', base / 'home'
    rc, out = link_sh(T, H)
    assert rc == 0, out
    terms = json.loads((REPO / 'references' / 'role-phase-terminology.json').read_text(encoding='utf-8'))
    state = json.loads((T / '.aid' / 'state.json').read_text(encoding='utf-8'))
    first = next(iter(terms['roles']))
    assert state['role'] == first or state['role_display'] == terms['roles'][first]['name'], state


@pytest.mark.parametrize('link', LINKERS)
def test_t16_64_without_python_no_state_and_the_command_is_printed(base, link):
    T, H = base / 'proj', base / 'home'
    keep = [Path(NODE).parent] + ([d for d in _git_bash_dirs() if d.is_dir()]
                                  if link is link_sh else _system_dirs())
    path = _path_without('python', 'python3', 'py', keep=keep)
    rc, out = link(T, H, path=path)
    assert rc == 0, out
    assert not (T / '.aid' / 'state.json').exists()
    assert not (T / '.aid' / 'context.json').exists()
    assert 'WARNING' in out, out
    assert re.search(r'aid_session\.py" init 1 0', out), out
    assert (T / '.claude' / 'settings.json').is_file(), 'the hooks are registered before the state step'


@pytest.mark.parametrize('link', LINKERS)
def test_t16_64_role_must_be_a_plain_word(base, link):
    T, H = base / 'proj', base / 'home'
    rc, out = link(T, H, '--role', 'a b')
    assert rc != 0, out
    assert not (T / '.aid' / 'state.json').exists()


@pytest.mark.parametrize('link', LINKERS)
def test_t16_64_nested_target_leaves_the_ancestor_alone(base, link):
    """WS-B note: in a subfolder of an initialized project, `init` resolves to the ancestor
    root (INV-2) and refuses ('already exists'). link-project then writes no state, neither
    in the subfolder nor in the ancestor, and prints the exact init command (I-10)."""
    P, H = base / 'proj', base / 'home'
    p = subprocess.run([sys.executable, str(REPO / 'hooks' / 'aid_session.py'), 'init', '1', '0'],
                       cwd=str(P), env=dict(_env(H), CLAUDE_PROJECT_DIR=str(P)),
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
    assert p.returncode == 0, p.stdout + p.stderr
    before = {p.name: p.read_bytes() for p in (P / '.aid').iterdir() if p.is_file()}
    assert 'state.json' in before
    T = P / 'sub'
    T.mkdir()
    rc, out = link(T, H)
    assert rc == 0, out
    assert not (T / '.aid' / 'state.json').exists(), out
    assert not (T / '.aid' / 'context.json').exists(), out
    assert {n: (P / '.aid' / n).read_bytes() for n in before} == before, 'the ancestor state changed'
    assert 'WARNING' in out and 'NOT created' in out, out
    assert re.search(r'aid_session\.py" init 1 0', out), out
    # R1-09: the printed init would fail the same way, so the output names the ancestor.
    flat = out.replace('\\', '/').lower()
    anc = os.path.realpath(str(P)).replace('\\', '/').lower()
    assert 'inside another aid project: ' + anc in flat, out


LINKED_DIRS = {'commands', 'skills', 'agents', 'references', 'rules', 'hooks'}


def test_t16_63_link_by_hand_doc_matches_the_scripts():
    """E-R1-3: the hand-link commands in link-project.md link the same root folders the
    scripts link (each exists in AID), never AID-main/.claude/<x>, and the state step is
    the exact aid_session.py init line, not /aid-start (which a linked project refuses)."""
    doc = (REPO / 'commands' / 'link-project.md').read_text(encoding='utf-8')
    assert 'AID-main/.claude/commands' not in doc and 'AID-main\\.claude\\commands' not in doc
    assert 'AID-main/.claude/skills' not in doc and 'AID-main\\.claude\\skills' not in doc
    by_hand = doc.split('## Linking by Hand', 1)[1].split('## Example Output', 1)[0]
    ln = set(re.findall(r'ln -s \S*AID-main/(\w+)\s+\.claude/(\w+)', by_hand))
    mk = set(re.findall(r'mklink /J "\.claude\\(\w+)"\s+"[^"]*AID-main\\(\w+)"', by_hand))
    assert {s for s, t in ln if s == t} == LINKED_DIRS, ln
    assert {s for t, s in mk if s == t} == LINKED_DIRS, mk
    for name in LINKED_DIRS:
        assert (REPO / name).is_dir(), name
    sh = LINK_SH.read_text(encoding='utf-8')
    assert set(re.findall(r'^create_dir_symlink "(\w+)"', sh, re.M)) == LINKED_DIRS
    assert re.search(r'aid_session\.py"? init <role> 0', by_hand), by_hand
    assert re.search(r'aid_session\.py init 1 0', by_hand), by_hand
    assert 'link-settings.mjs' in by_hand
    assert not re.search(r'state\s+with\s+`?/aid-start', by_hand), 'the state step points at /aid-start'


def _next_steps_say_plugin_or_aid_session(text):
    """R2-F2: in a linked (non-plugin) project ${CLAUDE_PLUGIN_ROOT} is not replaced, so
    /aid-start stops. The closing steps must not send the user there; they name the plugin
    install and the aid_session.py fallback instead."""
    assert not re.search(r'Run /aid-start', text), text[-800:]
    assert 'claude plugin install aid@AID' in text, text[-800:]
    assert re.search(r'aid_session\.py"? status', text), text[-800:]


@pytest.mark.parametrize('link', LINKERS)
def test_t16_63_next_steps_do_not_send_a_linked_project_to_aid_start(base, link):
    T, H = base / 'proj', base / 'home'
    rc, out = link(T, H)
    assert rc == 0, out
    tail = out[out.index('Next steps:'):]
    _next_steps_say_plugin_or_aid_session(tail)
    # link-project.bat runs with delayed expansion: a lone "!" in an echo is dropped.
    assert ' leading ,' not in tail and 'aid_session.py" status' in tail.replace('\\', '/'), tail


def test_t16_63_link_doc_example_and_table_match_the_linked_project():
    doc = (REPO / 'commands' / 'link-project.md').read_text(encoding='utf-8')
    example = doc.split('## Example Output', 1)[1].split('## Troubleshooting', 1)[0]
    _next_steps_say_plugin_or_aid_session(example)
    assert not re.search(r'All AID commands are now available', example), example
    assert not re.search(r'^\| All Commands \| /aid-start', example, re.M), example


STATE_WRITE = [re.compile(r'>\s*"?[^\s"]*state\.json'), re.compile(r'create_state_json'),
               re.compile(r'cat\s*>[^\n]*state\.json')]


def _shipped_scripts():
    files = [REPO / n for n in ('link-project.sh', 'link-project.bat', 'install.sh', 'install.bat')]
    files += [p for p in (REPO / 'scripts').rglob('*') if p.is_file()]
    return files


def test_t16_64_no_shipped_script_writes_state_json():
    hits = []
    for p in _shipped_scripts():
        for n, line in enumerate(p.read_text(encoding='utf-8', errors='replace').splitlines(), 1):
            s = line.strip()
            if s.startswith('#') or s.upper().startswith('REM') or s.startswith('//'):
                continue
            if any(rx.search(line) for rx in STATE_WRITE):
                hits.append('{}:{}: {}'.format(p.relative_to(REPO), n, s))
    assert hits == [], hits


# --- T16-65 scaffold dependencies (E8, R-06) -------------------------------------------------

FLOOR = {'next': (16, 4, 5), 'react': (19, 3, 1), 'react-dom': (19, 3, 1),
         '@testing-library/react': (16, 3, 3)}


def _scaffold_package_json():
    text = INIT_SCRIPT.read_text(encoding='utf-8')
    m = re.search(r'cat > package\.json << EOF\n(.*?)\nEOF', text, re.S)
    assert m, 'package.json heredoc not found in init-project.sh'
    return json.loads(m.group(1).replace('$PROJECT_NAME', 'probe'))


def test_t16_65_scaffold_pins_are_exact_and_past_the_floor():
    text = INIT_SCRIPT.read_text(encoding='utf-8')
    assert '^14' not in text
    pkg = _scaffold_package_json()
    deps = dict(pkg['dependencies'], **pkg['devDependencies'])
    for name, spec in deps.items():
        assert re.fullmatch(r'~?\d+\.\d+\.\d+', spec), (name, spec)
    for name, floor in FLOOR.items():
        got = tuple(int(x) for x in deps[name].lstrip('~').split('.'))
        assert got >= floor, (name, deps[name])
    assert '@testing-library/dom' in deps, '@testing-library/react 16 needs @testing-library/dom'
    assert int(deps['react'].lstrip('~').split('.')[0]) == 19
    # The verification is recorded next to the pins.
    assert re.search(r'#.*npm audit --audit-level=high', text) and '0 high' in text


def test_t16_65_init_project_warns_on_audit_findings_without_failing():
    text = INIT_SCRIPT.read_text(encoding='utf-8')
    block = text.split('# Install dependencies', 1)[1].split('# Print success', 1)[0]
    assert re.search(r'if ! npm audit --audit-level=high', block), block
    assert 'log_warning' in block.split('npm audit --audit-level=high', 1)[1], block
    assert 'exit' not in block.split('npm audit --audit-level=high', 1)[1], 'audit must not change the exit code'


@needs_bash
@pytest.mark.skipif(os.environ.get('AID_NET_TESTS') != '1', reason='network test: set AID_NET_TESTS=1')
def test_t16_65_generated_project_has_no_high_or_critical_advisory(tmp_path):
    work, home = tmp_path / 'work', tmp_path / 'home'
    work.mkdir()
    home.mkdir()
    p = subprocess.run([BASH, INIT_SCRIPT.as_posix(), 't16audit', '--no-git', '--no-deps', '--copy'],
                       cwd=str(work), env=_env(home), capture_output=True, text=True, timeout=600)
    assert p.returncode == 0, p.stdout + p.stderr
    proj = work / 't16audit'
    npm = shutil.which('npm') or 'npm'
    subprocess.run([npm, 'install', '--package-lock-only', '--ignore-scripts'], cwd=str(proj),
                   check=True, capture_output=True, timeout=600)
    a = subprocess.run([npm, 'audit', '--json'], cwd=str(proj), capture_output=True, text=True, timeout=300)
    v = json.loads(a.stdout)['metadata']['vulnerabilities']
    assert v['high'] == 0 and v['critical'] == 0, v


# --- T16-66 linker token wording (A-09 residual) -------------------------------------------

@pytest.mark.parametrize('script', [LINK_SH, LINK_BAT], ids=lambda p: p.name)
def test_t16_66_linker_says_tokens_come_from_the_environment(script):
    text = script.read_text(encoding='utf-8')
    assert 'preserving your tokens' not in text and '(your tokens)' not in text
    echoes = [l for l in text.splitlines() if l.strip().lower().startswith('echo')
              and '.mcp.json' in l and 'token' in l.lower()]
    assert echoes, script.name
    for line in echoes:
        assert 'environment variable' in line, line
    assert 'OS keystore' in text


# --- T16-67 Atlassian env names (A-33) -------------------------------------------------------
# Reproduced 2026-11-19: `npm pack @aashari/mcp-server-atlassian-jira@3.3.0` (and -confluence)
# -> dist/utils/transport.util.js reads config.get('ATLASSIAN_SITE_NAME'); ATLASSIAN_SITE_URL
# occurs nowhere in either package. The templates passed a variable the server never reads.

@pytest.mark.parametrize('template', ['.mcp.json.mac', '.mcp.json.windows', '.mcp.json.example'])
def test_t16_67_templates_pass_atlassian_site_name(template):
    servers = json.loads((REPO / template).read_text(encoding='utf-8'))['mcpServers']
    atl = [s for n, s in servers.items() if n in ('jira', 'confluence')]
    assert atl, template
    for s in atl:
        assert s['env'].get('ATLASSIAN_SITE_NAME') == '${ATLASSIAN_SITE_NAME:-}', s
        assert 'ATLASSIAN_SITE_URL' not in json.dumps(s), s


def test_t16_67_link_project_doc_and_installers_name_site_name():
    for rel in ('commands/link-project.md', 'install.sh', 'install.bat'):
        text = (REPO / rel).read_text(encoding='utf-8')
        assert 'ATLASSIAN_SITE_URL' not in text, rel
        assert 'ATLASSIAN_SITE_NAME' in text, rel


# --- T16-68 filesystem MCP pin (not reproduced: 2.4.0 is not 14 days old) ------------------

def test_t16_68_filesystem_pin_is_one_exact_version_everywhere():
    """Guard: the templates and both installers name the same exact server-filesystem pin."""
    pins = set()
    for rel in ('.mcp.json.mac', '.mcp.json.windows', 'install.sh', 'install.bat'):
        found = re.findall(r'@modelcontextprotocol/server-filesystem@(\d+\.\d+\.\d+)',
                           (REPO / rel).read_text(encoding='utf-8'))
        assert found, rel
        pins.update(found)
    assert len(pins) == 1, pins


# --- T16-69 test_cucumber_installed skips outside engines (FR-34) --------------------------

def test_t16_69_cucumber_check_uses_the_engines_skip():
    sys.path.insert(0, str(Path(__file__).parent))
    import test_installation
    import test_t15_docs
    fn = test_installation.TestNodeDependencies.test_cucumber_installed
    marks = [m for m in getattr(fn, 'pytestmark', []) if m.name == 'skipif']
    assert marks, 'test_cucumber_installed has no skipif'
    reason = test_t15_docs._cucumber_runnable()
    assert marks[0].args[0] == (reason is not None)
    if NODE:
        major = int(subprocess.run(['node', '-v'], capture_output=True, text=True).stdout.strip()
                    .lstrip('v').split('.')[0])
        if major == 23 and reason is not None and 'not installed' not in reason:
            assert 'engines' in marks[0].kwargs['reason'], marks[0].kwargs


# --- T16-70 template gitignore, start-project verification ---------------------------------

def test_t16_70_gitignore_template_ignores_the_hook_audit_log():
    text = (REPO / '.claude' / 'templates' / 'gitignore-aid-patterns.txt').read_text(encoding='utf-8')
    rules = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith('#')]
    assert '.aid/audit/' in rules


def _verify_step():
    text = (REPO / 'commands' / 'start-project.md').read_text(encoding='utf-8')
    return text.split('3. Verify the folder tree', 1)[1].split('\n4. ', 1)[0]


def test_t16_70_start_project_verification_uses_single_read_only_commands(base):
    step = _verify_step()
    cmds = re.findall(r'`(ls [^`]+)`', step)
    assert len(cmds) >= 2, step
    assert not re.search(r'\bfor\b[^\n`]*;\s*do\b', step), 'a loop in the verification step'
    if NODE is None:
        pytest.skip('node is needed for hook-runner.mjs')
    # Each command the step names is allowed by the Bash gate in an AID project at phase 0.
    P, H = base / 'proj', base / 'home'
    (P / '.aid').mkdir()
    (P / '.aid' / 'state.json').write_text(json.dumps({'current_phase': 0}), encoding='utf-8')
    runner = REPO / 'hooks' / 'hook-runner.mjs'
    for c in cmds:
        c = c.replace('[PROJECT_NAME]', 'my-app')
        p = subprocess.run(['node', str(runner), 'phase-gate-bash'], cwd=str(P), env=_env(H),
                           input=json.dumps({'session_id': uuid.uuid4().hex, 'cwd': str(P),
                                             'tool_name': 'Bash', 'tool_input': {'command': c}}),
                           capture_output=True, text=True, timeout=60)
        assert p.returncode == 0, p.stderr
        assert decision(p.stdout)[0] == 'ALLOW', (c, p.stdout)
