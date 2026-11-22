"""
T16 WS-A gate core (T16-acceptance.md, T16-1 .. T16-15).

WHY THESE TESTS:
- PROBLEM: the second 3.0.8 gate run found that an agent could write a project
  .aid/state.json in a folder that was not yet an AID project (g1-aid-init), resolve a
  pipeline escalation itself (R-04), hide a session call behind an arithmetic `<<` (R-02),
  fill .claude/ files Claude Code runs before Phase 4 (R-03), and that ordinary commands
  starting with a variable were denied (R-07). Gate messages misled about git and cd, and the
  hook audit log kept secrets.
- COST OF FAILURE: the agent changes the AID phase or a human-only pipeline decision with no
  prompt, or the gate blocks ordinary work in every repo.
- SUCCESS: the real hook, spawned through hooks/hook-runner.mjs as Claude Code runs it, gives
  the decisions the contract names.

Harness (contract section 4): fake HOME/USERPROFILE/AID_HOME; probe projects at the drive
root (outside the real profile, whose ~/.aid/state.json makes every folder under it an AID
project); CLAUDE_PROJECT_DIR and CLAUDE_CONFIG_DIR unset unless a test sets them. <R> = the
live plugin root (this checkout). Token-shaped strings are built at run time.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
RUNNER = REPO / 'hooks' / 'hook-runner.mjs'
R = str(REPO).replace('\\', '/')
S = R + '/hooks/aid_session.py'
G = R + '/skills/pipeline-orchestrator/gate.mjs'
sys.path.insert(0, str(REPO / 'hooks'))
import aid_guard  # noqa: E402

pytestmark = pytest.mark.skipif(shutil.which('node') is None, reason='node is needed for hook-runner.mjs')

LEVELS = ('block', 'warn', 'log')
EVERY = ['non-AID'] + ['p{}/{}'.format(p, lv) for p in (0, 1, 4, 5) for lv in LEVELS]


def _marker_above(p):
    return any((d / '.aid' / 'state.json').is_file() or (d / '.aid' / 'hooks' / 'config.json').is_file()
               for d in [p] + list(p.parents))


@pytest.fixture
def base(tmp_path):
    """A probe directory with no AID marker above it (drive root, contract section 4)."""
    # Drive root only on Windows (to leave C:/Users/<me>); on Linux/macOS / is not writable
    # and the temp dir has no AID marker above it anyway.
    alt = Path(tempfile.mkdtemp(prefix='aid-t16-', dir=Path(tmp_path).anchor if os.name == 'nt' else None))
    if _marker_above(alt):
        shutil.rmtree(alt, ignore_errors=True)
        pytest.skip('no directory without an AID marker ancestor is available')
    yield alt
    shutil.rmtree(alt, ignore_errors=True)


def run(hook, cwd, home, payload, env_extra=None):
    env = dict(os.environ, HOME=str(home), USERPROFILE=str(home), AID_HOME=str(Path(home) / '.aid'))
    env.pop('CLAUDE_PROJECT_DIR', None)
    env.pop('CLAUDE_CONFIG_DIR', None)
    env.update(env_extra or {})
    p = subprocess.run(['node', str(RUNNER), hook], input=json.dumps(payload), capture_output=True,
                       text=True, cwd=str(cwd), env=env, timeout=60)
    assert p.returncode == 0, (p.returncode, p.stderr[-600:])
    return p.stdout.strip()


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
    """An AID project P at a phase and level (or, place 'non-AID', a plain folder) + home H."""

    def __init__(self, root, place='p1/block'):
        self.P, self.H = root / 'proj', root / 'home'
        self.P.mkdir(parents=True, exist_ok=True)
        (self.H / '.claude').mkdir(parents=True, exist_ok=True)
        self.env = {}
        self.place = place
        if place != 'non-AID':
            phase, level = place[1:].split('/')
            for d in ('.aid/hooks', '.claude', 'docs'):
                (self.P / d).mkdir(parents=True, exist_ok=True)
            (self.P / '.claude' / 'settings.json').write_text('{}', encoding='utf-8')
            self.state(int(phase))
            self.level(level)

    def state(self, phase):
        (self.P / '.aid' / 'state.json').write_text(json.dumps({'current_phase': phase}), encoding='utf-8')

    def level(self, level):
        (self.P / '.aid' / 'hooks' / 'config.json').write_text(json.dumps(
            {'enforcement': {'phase_gate_write': level, 'phase_gate_bash': level}}), encoding='utf-8')

    def _payload(self, tool, tool_input):
        return {'session_id': uuid.uuid4().hex, 'cwd': str(self.P), 'tool_name': tool,
                'tool_input': tool_input}

    def bash(self, cmd, tool='Bash'):
        return decision(run('phase-gate-bash', self.P, self.H, self._payload(tool, {'command': cmd}), self.env))

    def ps(self, cmd):
        return self.bash(cmd, tool='PowerShell')

    def write(self, path, tool='Write'):
        return decision(run('phase-gate-write', self.P, self.H,
                            self._payload(tool, TOOL_INPUT[tool](path)), self.env))


def _w(base, place):
    return Where(base / place.replace('/', '_').replace('-', ''), place)


# --- T16-1 .aid/state.json refused to the Write tools in every folder ---------------------

@pytest.mark.parametrize('place', EVERY)
def test_t16_1_write_tools_refuse_project_state_in_every_folder(base, place):
    w = _w(base, place)
    for tool in sorted(TOOL_INPUT):
        v = w.write('.aid/state.json', tool)
        assert v[0] == 'DENY', (place, tool, v)
        assert 'aid_session.py' in v[1] and '/aid-init' in v[1] and S in v[1], v


@pytest.mark.parametrize('tool', sorted(TOOL_INPUT))
def test_t16_1_every_spelling_is_refused_outside_aid(base, tool):
    w = _w(base, 'non-AID')
    spellings = [str(w.P / '.aid' / 'state.json'), '.AID/STATE.JSON', 'sub/.aid/state.json',
                 'x/../.aid/state.json', 'new/dir/.aid/state.json']
    if os.name == 'nt':
        # Windows-only aliases (as in AC-35): Win32 drops trailing dots/spaces, '\' is a separator,
        # and an NTFS stream spelling names the file (R1-04). On Linux/macOS each of these is a
        # different file name, so the gate rightly allows it there.
        spellings += ['.aid/state.json.', '.aid./state.json ', '.aid/state.json::$DATA',
                      '.aid/STATE.json:alt', '.AID\\state.json:x:$DATA']
    for p in spellings:
        v = w.write(p, tool)
        assert v[0] == 'DENY', (p, tool, v)
    assert not (w.P / '.aid').exists()


def test_t16_1_other_files_and_the_user_state_stay_writable_outside_aid(base):
    w = _w(base, 'non-AID')
    for p in ('.aid/context.json', '.aid/notes.md', 'src/a.ts', '.aid/pipeline/state.json',
              str(w.H / '.aid' / 'state.json')):
        assert w.write(p) == ('ALLOW', None), p


# --- T16-2 .aid/state.json refused to Bash / PowerShell writes in every folder ------------

T16_2_BASH = ['echo {} > .aid/state.json', 'sed s/a/b/ tpl > .aid/state.json', 'cp t.json .aid/state.json',
              'tee .aid/state.json < t', 'mkdir -p .aid && cat t > .aid/state.json',
              'echo {} >> .AID/STATE.JSON', 'mv t.json .aid/state.json', 'ln -s t.json .aid/state.json',
              'touch .aid/state.json', 'install t.json .aid/state.json', 'dd if=t of=.aid/state.json',
              'sed -i s/a/b/ .aid/state.json', 'python -c "open(\'.aid/state.json\',\'w\')"',
              # R1-02: quote removal and a backslash spell the same literal name
              'echo x > ".aid/state".json', 'echo x > .aid/sta""te.json', "echo x > .aid/sta''te.json",
              'echo x > .aid/sta\\te.json', 'cp a ".aid/state.jso"n',
              # R1-06: a glob or a variable that expands to it
              'echo x > .aid/stat?.json', 'f=.aid/state.json; echo x > $f', 'echo x > $(echo .aid/state.json)',
              # R2-01 (fix cycle 2): unquoted brace expansion is static text, like quote removal
              'sed -i s/4/5/ .aid/state.{json,x}', 'sed -i s/4/5/ .aid/{state,x}.json', 'tee .aid/state.{json,x} < t',
              'tee .aid/{state.json,x} < t', 'tee .aid/state.js{on,} < t', 'dd of=.aid/state.{x,json} < t',
              'touch .aid/state.{json,x}']
# T16 B1 (E2 bounded): a write reached through a cwd change does not name .aid/state.json.
# Outside AID it is an accepted, documented residual (ALLOW); inside AID it stays refused.
T16_2_BASH_CD = ['mkdir -p .aid && cd .aid && echo {} > state.json', 'cd .aid && echo x > "state".json',
                 'pushd .aid; echo x > state.json', 'pushd .aid >/dev/null && cp ../t state.json',
                 'builtin cd .aid && echo x > state.json', 'command cd .aid && echo x > state.json',
                 'cd -P .aid && echo x > state.json', 'cd -- .aid && echo x > state.json',
                 'cd - && echo x > state.json']
T16_2_PS = ['Set-Content .aid\\state.json x', 'Add-Content -Path .aid/state.json -Value x',
            '"x" | Out-File .aid\\state.json', 'New-Item .aid\\state.json -Force',
            'Copy-Item t.json .aid\\state.json', 'Move-Item t.json .aid/state.json', 'echo x > .aid\\state.json',
            'echo x >> .aid/state.json',
            # R1-03: ./ and .\ segments, a cwd change, a move/copy into the folder, a backtick
            'Set-Content -Path ./.aid/./state.json x', 'sc .aid/./state.json x', 'echo x > .\\.aid\\.\\state.json',
            'Move-Item state.json .aid', 'Copy-Item state.json .aid\\', 'cd .aid; Set-Content state.json x',
            'Set-Content ".aid\\st`ate.json" x', 'Set-Content .aid\\sta*.json x']


@pytest.mark.parametrize('place', EVERY)
def test_t16_2_bash_and_powershell_state_writes_are_refused_in_every_folder(base, place):
    w = _w(base, place)
    for cmd in ('echo {} > .aid/state.json', 'cp t.json .aid/state.json'):
        assert w.bash(cmd)[0] == 'DENY', (place, cmd)
    assert w.ps('Set-Content .aid\\state.json x')[0] == 'DENY', place


@pytest.mark.parametrize('cmd', T16_2_BASH)
def test_t16_2_every_bash_writer_is_refused_outside_aid(base, cmd):
    w = _w(base, 'non-AID')
    v = w.bash(cmd)
    assert v[0] == 'DENY' and 'aid_session.py' in v[1], (cmd, v)


@pytest.mark.parametrize('cmd', T16_2_BASH_CD)
def test_t16_2_cd_forms_are_a_residual_outside_aid_and_refused_inside(base, cmd):
    # T16 B1: documented residual outside AID (no literal .aid/state.json in the text).
    assert _w(base, 'non-AID').bash(cmd) == ('ALLOW', None), cmd
    (base / 'nonAID' / 'proj' / '.aid').mkdir(exist_ok=True)
    assert _w(base, 'non-AID').bash(cmd) == ('ALLOW', None), cmd
    for place in ('p1/block', 'p4/block'):
        assert _w(base, place).bash(cmd)[0] == 'DENY', (place, cmd)


@pytest.mark.parametrize('cmd', T16_2_PS)
def test_t16_2_every_powershell_writer_is_refused_outside_aid(base, cmd):
    v = _w(base, 'non-AID').ps(cmd)
    assert v[0] == 'DENY', (cmd, v)


def test_t16_2_reads_and_the_canonical_init_keep_their_verdict(base):
    for place in ('non-AID', 'p4/block'):
        w = _w(base, place)
        for cmd in ('cat .aid/state.json', 'jq . .aid/state.json', 'git diff .aid/state.json'):
            assert w.bash(cmd) == ('ALLOW', None), (place, cmd)
        assert w.ps('Get-Content .aid\\state.json')[0] == ('ALLOW' if place == 'non-AID' else 'DENY')
        assert w.bash('python "{}" init developer 0'.format(S))[0] == 'ASK', place
    w = _w(base, 'non-AID')
    assert w.bash('echo x > notes.txt') == ('ALLOW', None)
    assert w.bash('echo x > .aid/context.json') == ('ALLOW', None)


# --- T16-3 gate.mjs --resolve is asked; other spellings denied inside AID ------------------

def _fake_root(d, name='aid'):
    (d / 'hooks').mkdir(parents=True, exist_ok=True)
    (d / '.claude-plugin').mkdir(parents=True, exist_ok=True)
    (d / 'hooks' / 'aid_session.py').write_text('print(1)\n', encoding='utf-8')
    (d / '.claude-plugin' / 'plugin.json').write_text(json.dumps({'name': name}), encoding='utf-8')
    return d


def _config_dir(base):
    C = base / 'cfg'
    cache = _fake_root(C / 'plugins' / 'cache' / 'M' / 'aid' / '9.9.9')
    return C, cache


@pytest.mark.parametrize('place', EVERY)
def test_t16_3_exact_resolve_is_asked_in_every_folder(base, place):
    w = _w(base, place)
    C, cache = _config_dir(base / 'c')
    w.env = {'CLAUDE_CONFIG_DIR': str(C)}
    fake = str(cache).replace('\\', '/') + '/skills/pipeline-orchestrator/gate.mjs'
    # <R> holds an apostrophe, so only the fake root (drive root) is single-quoted.
    for cmd in ('node "{}" --resolve "keep the threshold"'.format(G), "node '{}' --resolve 'ok'".format(fake),
                'node "{}" --resolve accepted'.format(G.replace('/', '\\')),
                'node "{}" --resolve ok'.format(fake)):
        for tool in ('Bash', 'PowerShell'):
            v = w.bash(cmd, tool)
            assert v[0] == 'ASK' and 'ESCALATION.json' in v[1] and 'must confirm' in v[1], (place, tool, cmd, v)


T16_3_DENY = ['node "{g}" --resolve x; echo y', 'node "{g}" --resolve "$(cat r)"',
              'cd "{r}/skills/pipeline-orchestrator" && node gate.mjs --resolve ok', 'node ./gate.mjs --resolve ok',
              'node "$G" --resolve ok', 'node "{g}" --root . --resolve ok', 'bun "{g}" --resolve ok',
              # R1-05: quote/backslash/glob spellings and other runtimes or package runners
              'node "{g}" --res\\olve ok', 'node "{g}" --reso""lve ok', 'node "{d}/gate.m"js --resolve ok',
              'node "{d}/g?te.mjs" --resolve ok', 'node "{d}/gat"*.mjs --resolve ok',
              'cd "{d}" && node g*.mjs --re""solve ok', 'tsx "{g}" --resolve ok', 'npx node "{g}" --resolve ok',
              'pnpm dlx tsx "{g}" --resolve ok', 'bunx "{g}" --resolve ok']


@pytest.mark.parametrize('form', T16_3_DENY)
def test_t16_3_other_resolve_spellings_are_denied_inside_aid(base, form):
    cmd = form.format(g=G, r=R, d=G.rsplit('/', 1)[0])
    for place in ('p1/log', 'p4/block', 'p4/log', 'p5/warn'):
        v = _w(base, place).bash(cmd)
        assert v[0] == 'DENY' and '! node "{}" --resolve'.format(G) in v[1], (place, cmd, v)
        assert 'never run it' in v[1], v


def test_t16_3_non_resolve_calls_and_reads_keep_their_verdict(base):
    w = _w(base, 'p4/block')
    assert w.bash('node "{}" --status'.format(G)) == ('ALLOW', None)
    assert w.bash('grep resolve "{}"'.format(G)) == ('ALLOW', None)
    assert _w(base, 'p1/block').bash('grep resolve "{}"'.format(G)) == ('ALLOW', None)


# --- T16-4 threshold edits in .aid/pipeline/config.json are asked ------------------------

@pytest.mark.parametrize('place', [p for p in EVERY if p != 'non-AID'])
def test_t16_4_existing_pipeline_config_is_asked_to_the_write_tools(base, place):
    w = _w(base, place)
    (w.P / '.aid' / 'pipeline').mkdir(parents=True)
    (w.P / '.aid' / 'pipeline' / 'config.json').write_text('{}', encoding='utf-8')
    for tool in ('Write', 'Edit', 'MultiEdit'):
        v = w.write('.aid/pipeline/config.json', tool)
        assert v[0] == 'ASK' and 'threshold' in v[1] and 'confirm' in v[1], (place, tool, v)


def test_t16_4_creating_it_and_reading_it_stay_allowed_bash_writes_are_denied(base):
    w = _w(base, 'p4/block')
    assert w.write('.aid/pipeline/config.json') == ('ALLOW', None)          # scaffolded when absent
    (w.P / '.aid' / 'pipeline').mkdir(parents=True)
    (w.P / '.aid' / 'pipeline' / 'config.json').write_text('{}', encoding='utf-8')
    for place in ('p4/block', 'p4/log', 'p5/warn'):
        w = _w(base / 'b', place)
        (w.P / '.aid' / 'pipeline').mkdir(parents=True, exist_ok=True)
        (w.P / '.aid' / 'pipeline' / 'config.json').write_text('{}', encoding='utf-8')
        for cmd in ('echo {} > .aid/pipeline/config.json', 'cp x.json .aid/pipeline/config.json',
                    'python -c "open(\'.aid/pipeline/config.json\',\'w\')"'):
            assert w.bash(cmd)[0] == 'DENY', (place, cmd)
        for cmd in ('cat .aid/pipeline/config.json', 'jq .thresholds .aid/pipeline/config.json'):
            assert w.bash(cmd) == ('ALLOW', None), (place, cmd)
    assert _w(base / 'c', 'p1/log').bash('echo {} > .aid/pipeline/config.json')[0] == 'DENY'


@pytest.mark.parametrize('place', ['p4/block', 'p4/log', 'p5/warn'])
def test_t16_4_glob_and_variable_control_targets_are_denied_inside_aid(base, place):
    """R1-06 (fix cycle 1): a glob or variable write target the shell expands to the state file
    or the pipeline config is the same write as the literal name (aid_session.py is the only
    state writer, E2); reads and ordinary globs keep their verdict."""
    w = _w(base, place)
    (w.P / '.aid' / 'pipeline').mkdir(parents=True, exist_ok=True)
    (w.P / '.aid' / 'pipeline' / 'config.json').write_text('{}', encoding='utf-8')
    for cmd in ('echo x > .aid/stat?.json', 'echo x > .aid/st*e.json', 'f=.aid/state.json; echo x > $f',
                'echo x > $(echo .aid/state.json)', 'echo x > .aid/pipeline/conf?g.json',
                'cp config.json .aid/pipeline/conf?g.json', 'cd .aid && echo x > stat?.json'):
        assert w.bash(cmd)[0] == 'DENY', (place, cmd)
    assert w.ps('Set-Content .aid\\sta*.json x')[0] == 'DENY', place
    for cmd in ('cat .aid/stat?.json', 'f=.aid/state.json; cat $f', 'python x.py .aid/*.json',
                'echo x > build/*.log'):
        assert w.bash(cmd) == ('ALLOW', None), (place, cmd)


# --- T16-5 arithmetic is never a heredoc --------------------------------------------------

T16_5_SPELLINGS = ['echo $[1<<2]', 'echo ${x:1<<1}', 'a[1<<2]=1', "let 'y=1<<2'", 'declare -i z=1<<2']
# The same spellings with the closing line the old lexer read as the heredoc delimiter.
T16_5_MATCHED = [('echo $[1<<2]', '2]'), ('echo ${x:1<<1}', '1}'), ('a[1<<2]=1', '2]=1'),
                 ('a[1 << 2]=1', '2]=1'), ('echo $[ 1 << 2 ]', '2')]


def _places4(base):
    return [_w(base, p) for p in ('non-AID', 'p1/log', 'p4/block', 'p5/warn')]


@pytest.mark.parametrize('spelling', T16_5_SPELLINGS + ['$((1<<2))', '(( y = 1 << 2 ))'])
def test_t16_5_contract_spellings_cannot_hide_a_session_call(base, spelling):
    cmd = '{}\npython "{}" $(echo approve)\n2]'.format(spelling, S)
    for w in _places4(base):
        v = w.bash(cmd)
        assert v[0] == 'DENY', (w.place, cmd, v)


@pytest.mark.parametrize('spelling,closer', T16_5_MATCHED)
def test_t16_5_a_matching_closing_line_cannot_hide_a_session_call(base, spelling, closer):
    cmd = '{}\npython "{}" $(echo approve)\n{}'.format(spelling, S, closer)
    for w in _places4(base):
        v = w.bash(cmd)
        assert v[0] == 'DENY', (w.place, cmd, v)


def test_t16_5_effect_check_init_creates_no_state(base):
    """The `init developer 5` variant is denied and nothing is written; bash itself shows that
    the line after the arithmetic `<<` really runs (it is not a heredoc body)."""
    w = _w(base, 'non-AID')
    v = w.bash('echo $[1<<2]\npython "{}" init developer 5\n2]'.format(S))
    assert v[0] == 'DENY', v
    assert not (w.P / '.aid' / 'state.json').exists()
    bash = shutil.which('bash')
    if bash:
        for sp, closer in T16_5_MATCHED[:3]:
            out = subprocess.run([bash, '-c', '{}\necho REACHED\n{}'.format(sp, closer)], capture_output=True,
                                 text=True, cwd=str(w.P), timeout=30).stdout
            assert 'REACHED' in out, (sp, out)


def test_t16_5_lexers_read_arithmetic_brackets():
    assert aid_guard._shell_segments('echo $[1<<2]\necho y\n2]') == [['echo', '$[1<<2]'], ['echo', 'y'], ['2]']]
    assert aid_guard._shell_segments('a[1<<2]=1\necho y') == [['a[1<<2]=1'], ['echo', 'y']]
    assert aid_guard._shell_segments('echo ${x:1<<1}\necho y') == [['echo', '${x:1<<1}'], ['echo', 'y']]
    assert aid_guard._shell_segments('declare -i z=1<<2\necho y\n2') == [['declare', '-i', 'z=1<<2'],
                                                                         ['echo', 'y'], ['2']]
    segs, _ = aid_guard.lex('echo $[1<<2]\nrm .aid/state.json\n2]')
    assert [w.text for w in segs[1].words] == ['rm', '.aid/state.json']
    # A real heredoc and an unbalanced bracket keep the old reading.
    assert aid_guard._shell_segments('cat <<EOF\nhello\nEOF\necho done') == [['cat', '<<EOF'], ['echo', 'done']]
    assert aid_guard._shell_segments('echo a[1') == [['echo', 'a[1']]


@pytest.mark.parametrize('cmd', ['echo $[1<<2]', 'echo ${x:1<<1}', 'a[1<<2]=1; echo ${a[4]}', "let 'y=1<<2'",
                                 'declare -i z=1<<2; echo $z', 'echo $[ 8 >> 1 ]'])
def test_t16_5_arithmetic_alone_stays_allowed(base, cmd):
    assert aid_guard.session_ask_verdict(cmd) == (None, None), cmd
    for w in (_w(base, 'non-AID'), _w(base, 'p4/block')):
        assert w.bash(cmd) == ('ALLOW', None), (w.place, cmd)


# --- T16-7 no variable-first-word false denial (corpus vs 5f8f199) -------------------------

R07_FORMS = ['$DOCKER $CMD $IMAGE', '"$JAVA_HOME/bin/java" -jar "$JAR" "$CONFIG"', '"$CC" $CFLAGS $SRC',
             '$EDITOR $FILE $LINE']

# (tool, command, 5f8f199 verdict non-AID, p4/block, p5/warn): measured by running the hook of
# a 5f8f199 copy (scratchpad/t16/pre-ws-a) on each command.
T16_7_CORPUS = [
    ('Bash', 'npm test', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'npm run build', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'npm ci', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'npx tsc --noEmit', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'pnpm install', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'yarn lint', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'pytest -q', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'pytest -k approve tests/', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'python manage.py migrate', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'python -m pytest -x', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'python3 setup.py --version', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'pip install -r requirements.txt', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'node index.js', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'node --test', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'go test ./...', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'cargo build --release', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'make', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'make test', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'ls -la', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'ls -la src/', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'cat README.md', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'head -n 20 package.json', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'tail -f log.txt', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'wc -l src/*.ts', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'grep -rn TODO src/', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'grep -n "approve" docs/*.md', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'find . -name "*.py"', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'find src -type f | wc -l', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'rg -n init src', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'jq .version package.json', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'echo hello', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'echo "$HOME"', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'echo $PATH', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'printf "%s\\n" a b', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'pwd', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'whoami', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'uname -a', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'which python', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'type node', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'du -sh .', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'df -h', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'sort data.txt | uniq -c', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'cut -d, -f1 data.csv', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'tr a-z A-Z < in.txt', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'diff a.txt b.txt', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'sed -n 1,10p src/a.ts', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', "awk '{print $1}' data.txt", 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'xargs -n1 echo < list.txt', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'mkdir -p build', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'touch build/.keep', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'cp src/a.ts src/b.ts', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'mv tmp.txt out.txt', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'rm -f build/x.o', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'rm -rf node_modules', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'chmod +x run.sh', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', './run.sh', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'bash scripts/build.sh', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'sh -c "echo hi"', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'curl -s https://example.com/health', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'tar czf out.tgz dist/', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git status', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git status --short', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git log --oneline -5', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git diff', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git diff --stat HEAD~1', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git add -A', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git add src/a.ts', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git commit -m "fix: x"', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git commit -am "wip"', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git push origin main', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git pull --rebase', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git checkout -b feature/x', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git switch main', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git stash', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git stash pop', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git rebase -i HEAD~3', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git branch -a', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git show HEAD', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git blame src/a.ts', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git fetch --all', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git tag v1.0.0', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git log --grep "init"', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git rev-parse HEAD', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git remote -v', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git clean -n', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git commit -m "$(cat <<\'EOF\'\nfeat: add parser\n\nDetails here.\nEOF\n)"', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git commit -m "$(cat <<\'EOF\'\nfix: the "quoted" path and "odd one\nEOF\n)"', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git commit -m "$(cat <<\'EOF\'\nchore: run python scripts/gen.py later\nEOF\n)"', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git commit -m "$(cat <<\'EOF\'\ndocs: init and approve steps\nEOF\n)"', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'cat <<EOF > notes.txt\nhello\nEOF', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', "cat <<'EOF'\n$HOME stays literal\nEOF", 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', "python - <<'PY'\nprint(1 << 2)\nPY", 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', "node <<'JS'\nconsole.log(1)\nJS", 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'echo $((1<<2))', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'echo $(( 8 >> 1 ))', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', '(( n = 1 << 3 )); echo $n', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'x=$(( (3 << 1) + 1 )); echo $x', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'echo $[1+2]', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'echo ${x:-default}', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'echo ${#arr[@]}', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'a[1]=5; echo ${a[1]}', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'let "y = 2 + 3"', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'declare -i z=5; echo $z', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'i=0; while [ $i -lt 3 ]; do i=$((i+1)); done', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'echo ${x:1:2}', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'echo $(( RANDOM % 10 ))', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'n=$((n+1))', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'arr+=(x)', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'echo ${PATH//:/ }', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'for f in *.py; do echo "$f"; done', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'for f in src/*.ts; do wc -l "$f"; done', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'for i in 1 2 3; do echo $i; done', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'while read line; do echo "$line"; done < list.txt', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'for f in *.json; do jq . "$f" > /dev/null; done', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'for d in */; do ls "$d"; done', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'if [ -f x ]; then echo yes; else echo no; fi', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'test -d build || mkdir build', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', '[ -n "$CI" ] && echo ci', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'case "$1" in a) echo a;; esac', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'cd src && ls', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'cd .. && pwd', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'cd "$HOME" && ls', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'cd /tmp; ls', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'cd - ', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'pushd src && popd', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'cd build && make', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'cd docs; cat index.md', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', '$DOCKER $CMD $IMAGE', 'DENY', 'DENY', 'DENY'),
    ('Bash', '"$JAVA_HOME/bin/java" -jar "$JAR" "$CONFIG"', 'DENY', 'DENY', 'DENY'),
    ('Bash', '"$CC" $CFLAGS $SRC', 'DENY', 'DENY', 'DENY'),
    ('Bash', '$EDITOR $FILE $LINE', 'DENY', 'DENY', 'DENY'),
    ('Bash', 'docker build -t app .', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'docker run --rm app', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'docker compose up -d', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'java -jar app.jar', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'javac Main.java', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'gcc -o out main.c', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'cc -O2 main.c', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'vim src/a.ts', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', '$MAKE -j4', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', '${TOOL} --help', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', '$(npm bin)/eslint src', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', '`which node` app.js', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', '"$NODE" server.js', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'env FOO=1 npm test', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'FOO=bar node app.js', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'timeout 60 npm test', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'nice -n 5 make', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'python tools/gen_{a,b}.py init', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'python x.py $FILE', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'python3 -c "print(1)"', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'node -e "console.log(1)"', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'ruby -e "puts 1"', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'perl -ne "print" file.txt', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'deno run main.ts', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'bun run dev', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'grep -n aid_session hooks/*.py', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'git diff hooks/aid_session.py', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'cat hooks/aid_session.py | head -n 5', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'rg "aid_session.py qa-pass" docs', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('PowerShell', 'npm test', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('PowerShell', 'git status', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('PowerShell', 'Get-ChildItem', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('PowerShell', 'Get-Content README.md', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('PowerShell', 'python manage.py migrate', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('PowerShell', 'Get-ChildItem -Recurse | Where-Object { $_.Length -gt 1kb }', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('PowerShell', 'npm test; if ($LASTEXITCODE) { exit 1 }', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('PowerShell', "python (Join-Path $PWD 'manage.py') reset", 'ALLOW', 'ALLOW', 'ALLOW'),
    ('PowerShell', 'python $env:SCRIPT reset', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('PowerShell', 'Set-Content src\\a.ts -Value x', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('PowerShell', 'Write-Host "hello"', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('PowerShell', '$env:FOO = "1"; npm test', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('PowerShell', 'dotnet build', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('PowerShell', '& $exe --help', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('PowerShell', 'Test-Path .aid', 'ALLOW', 'DENY', 'DENY'),
    ('PowerShell', 'Select-String -Path src\\*.ts -Pattern TODO', 'ALLOW', 'ALLOW', 'ALLOW'),
    # R2-03 (fix cycle 2): reading or backing up .aid files, and the user-level ~/.aid, are no
    # project state write (5f8f199 verdicts measured on scratchpad/t16/pre-ws-a).
    ('Bash', 'cp .aid/state.json bak/', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'cp .aid/state.json bak.json', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'cp -r .aid/* backup/', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'cp .aid/*.json bak/', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'rm -rf ~/.aid/*', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'cp ~/.aid/*.json bak/', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'cp ~/.aid/state.json bak.json', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('Bash', 'rm -f */state.json', 'ALLOW', 'ALLOW', 'ALLOW'),
    ('PowerShell', 'Copy-Item .aid\\* backup', 'ALLOW', 'ALLOW', 'ALLOW'),
    # R3-06 (fix cycle 3): a cd to a folder named by a variable, then an ordinary state.json
    # (5f8f199: allowed outside AID; inside AID the unknown folder may hold control files).
    ('Bash', 'cd "$TMPDIR" && echo \'{}\' > state.json', 'ALLOW', 'DENY', 'DENY'),
    ('Bash', 'cd "$D" && echo x > state.json', 'ALLOW', 'DENY', 'DENY'),
]


def test_t16_7_corpus_is_large_and_frozen():
    assert len(T16_7_CORPUS) >= 150
    assert {r[1] for r in T16_7_CORPUS if 'DENY' in r[2:]} >= set(R07_FORMS)


@pytest.mark.parametrize('tool,cmd,outside,p4,p5', T16_7_CORPUS)
def test_t16_7_no_new_false_denials_against_5f8f199(base, tool, cmd, outside, p4, p5):
    """Every command allowed at 5f8f199 is still allowed; the four R-07 forms flip to allow."""
    for place, head in (('non-AID', outside), ('p4/block', p4), ('p5/warn', p5)):
        want = 'ALLOW' if (head == 'ALLOW' or cmd in R07_FORMS) else head
        v = _w(base, place).bash(cmd, tool)
        assert v[0] == want, (place, tool, cmd, head, v)


@pytest.mark.parametrize('form', ['S="{s}"; $PY "$S" approve', 'S="{s}"; "$VENV/bin/python" "$S" $(echo approve)',
                                  'python "$SCRIPT" "$INPUT"', 'py -3 "$TOOL" "$ARG"',
                                  'for f in *.py; do python "$f" "$OUT"; done', 'python "{s}" $(echo approve)'])
def test_t16_7_interpreter_and_session_forms_stay_denied(base, form):
    cmd = form.format(s=S)
    for place in ('non-AID', 'p4/block', 'p5/warn'):
        assert _w(base, place).bash(cmd)[0] == 'DENY', (place, cmd)


# --- T16-6 execution-relevant .claude/ paths before Phase 4 --------------------------------

T16_6_WRITES = ['.claude/launch.json', '.claude/workflows/w.js', '.claude/routines/r.md',
                '.claude/scheduled_tasks.json', '.claude/loop.md', '.claude/agent-memory/a/MEMORY.md',
                '.claude/CLAUDE.md', '.claude/AGENTS.md', '.CLAUDE/Workflows./w.js']
T16_6_BASH = ['mkdir -p .claude/workflows', 'echo x > .claude/loop.md', 'cp a .claude/launch.json',
              'mv a .claude/routines/r.md', 'touch .claude/scheduled_tasks.json']


@pytest.mark.parametrize('phase', [0, 3])
def test_t16_6_exec_paths_are_denied_before_phase_4(base, phase):
    w = _w(base, 'p{}/block'.format(phase))
    for p in T16_6_WRITES:
        for tool in sorted(TOOL_INPUT):
            assert w.write(p, tool)[0] == 'DENY', (phase, p, tool)
    for cmd in T16_6_BASH:
        assert w.bash(cmd)[0] == 'DENY', (phase, cmd)


@pytest.mark.parametrize('place', ['p4/block', 'p1/log', 'p2/warn'])
def test_t16_6_exec_paths_at_phase_4_and_lowered_levels(base, place):
    w = _w(base, place)
    for p in T16_6_WRITES:
        assert w.write(p)[0] == 'ALLOW', (place, p)       # warn: allowed with a warning
    for cmd in T16_6_BASH:
        assert w.bash(cmd)[0] == 'ALLOW', (place, cmd)


def test_t16_6_plans_notes_and_root_mcp_guard(base):
    w = _w(base, 'p1/block')
    for p in ('.claude/plans/x.md', '.claude/notes.md'):
        assert w.write(p) == ('ALLOW', None), p
    assert w.write('.mcp.json')[0] == 'DENY'


# --- T16-8 the pre-Phase-4 message is accurate about git ----------------------------------

def test_t16_8_reason_does_not_call_git_add_commit_read_only(base):
    v = _w(base, 'p1/block').bash('npm test')
    assert v[0] == 'DENY'
    assert 'git status/log/diff/add/commit' not in v[1] and 'git status/log/diff/add' not in v[1], v[1]
    # T17 (owner 2026-11-20): T17-7 (U-03) rewords it: the user's own git hooks still run.
    assert 'git add/commit' in v[1] and 'your own git hooks' in v[1], v[1]


# --- T16-9 the cd reason names the real cause --------------------------------------------

def test_t16_9_each_cd_refusal_names_its_cause(base):
    w = _w(base, 'p1/block')
    root = str(w.P).replace('\\', '/')
    reasons = {}
    for key, cmd in (('first', 'ls && cd "{}"'.format(root)), ('target', 'cd docs && ls'),
                     ('op', 'cd "{}" && cat a; echo b'.format(root)), ('op2', 'cd "{}" || ls'.format(root)),
                     ('dot', 'cd "{}." && ls'.format(root))):
        v = w.bash(cmd)
        assert v[0] == 'DENY', (key, v)
        reasons[key] = v[1]
    assert 'only as the first command' in reasons['first']
    assert 'only to the project root' in reasons['target']
    assert '`;` (or a newline) after `cd <root> && ...`: a failed cd would not stop the rest' in reasons['op']
    assert '`||`' in reasons['op2']
    assert 'dot or space' in reasons['dot']
    assert len({r.split(' (allowed')[0][-120:] for r in reasons.values()}) == 5
    assert w.bash('cd "{}" && git status'.format(root)) == ('ALLOW', None)


# --- T16-10 read-only cd ~/.aid is not a control-file touch -------------------------------

@pytest.mark.parametrize('place', ['p4/block', 'p5/block'])
def test_t16_10_cd_into_aid_folders_is_an_accepted_false_denial(base, place):
    # T16 B1: T16-10 reverted to 5f8f199 (R4-01): inside AID a cd into ~/.aid or .aid stays
    # denied, an accepted false denial in the safe direction.
    w = _w(base, place)
    (w.H / '.aid' / 'feedback').mkdir(parents=True, exist_ok=True)
    for cmd in ('cd ~/.aid; ls feedback', 'cd .aid && ls'):
        assert w.bash(cmd)[0] == 'DENY', (place, cmd)    # T16 B1
    assert w.bash('ls .aid') == ('ALLOW', None), place
    for cmd in ('rm -r ~/.aid', 'mv .aid x', 'rm -r .claude', 'cd .aid && rm state.json'):
        assert w.bash(cmd)[0] == 'DENY', (place, cmd)


# --- T16-11 heredoc commit message with odd quotes ----------------------------------------

T16_11_MSG = ("git commit -m \"$(cat <<'EOF'\nfix: handle the \"quoted\" path and \"odd one\n"
              "run python $HOME/[x]{a,b}*.py ? here\nEOF\n)\"")


def test_t16_11_heredoc_commit_message_is_not_denied(base):
    assert aid_guard.session_ask_verdict(T16_11_MSG) == (None, None)
    for place in ('non-AID', 'p4/block'):
        assert _w(base, place).bash(T16_11_MSG) == ('ALLOW', None), place


def test_t16_11_session_call_inside_quoted_substitution_still_denied(base):
    cmd = 'echo "$(python "{}" $(echo approve))"'.format(S)
    for place in ('non-AID', 'p4/block'):
        assert _w(base, place).bash(cmd)[0] == 'DENY', place


# --- T16-12 pre-Phase-4 read-only text naming aid_session.py -----------------------------

def test_t16_12_read_only_commands_naming_the_script_run_before_phase_4(base):
    w = _w(base, 'p1/block')
    for cmd in ('grep -n init hooks/aid_session.py', 'git log -- hooks/aid_session.py', 'ls "{}"'.format(S)):
        assert w.bash(cmd) == ('ALLOW', None), cmd
    assert w.bash('python "{}" start developer 1'.format(S)) == ('ALLOW', None)        # canonical
    assert w.bash('python "{}" approve'.format(S))[0] == 'ASK'
    for cmd in ('python hooks/aid_session.py status', 'python "{}" $(echo approve)'.format(S),
                'cat hooks/aid_session.py | python', '$PY hooks/aid_session.py start'):
        assert w.bash(cmd)[0] == 'DENY', cmd


# --- T16-13 runner-run aid_session calls ---------------------------------------------------

@pytest.mark.parametrize('runner', ['uv', 'pdm', 'hatch', 'rye', 'pixi', 'poetry', 'pipenv'])
def test_t16_13_runner_run_confirmed_calls_are_denied(base, runner):
    cmd = '{} run "{}" approve'.format(runner, S)
    assert aid_guard.session_ask_verdict(cmd)[0] == 'deny', cmd
    for place in ('non-AID', 'p4/block', 'p5/log'):
        assert _w(base, place).bash(cmd)[0] == 'DENY', (place, cmd)


def test_t16_13_runner_run_ordinary_scripts_stay_allowed(base):
    for cmd in ('uv run pytest tests/test_aid_session.py -k approve', 'uv run "{}" status'.format(S),
                'poetry run python manage.py migrate'):
        assert _w(base, 'non-AID').bash(cmd) == ('ALLOW', None), cmd


# --- T16-14 in-AID prose naming aid_session plus a confirmed word -------------------------

def test_t16_14_prose_is_an_accepted_false_denial_inside_aid(base):
    # T16 B1: T16-14 reverted to 5f8f199 (R4-03): prose naming aid_session plus a confirmed
    # word stays denied inside AID, an accepted false denial in the safe direction.
    w = _w(base, 'p4/block')
    assert w.bash('echo "run aid_session approve later"')[0] == 'DENY'    # T16 B1
    # 5f8f199 judges the word right after the name: `aid_session: fix approve` is not a call.
    assert w.bash('git commit -m "aid_session: fix approve"') == ('ALLOW', None)
    for cmd in ('python "{}" ap""prove'.format(S), 'PYTHON "{}" approve'.format(S),
                'pythonw "{}" approve'.format(S), 'cd hooks && python aid_session.py approve',
                'python -m hooks.aid_session reset', 'x="$(python "{}" approve)"'.format(S),
                'echo `python hooks/aid_session.py reset`'):
        assert w.bash(cmd)[0] == 'DENY', cmd
    assert w.ps('git commit -m "aid_session: fix approve"')[0] == 'DENY'             # T7-4 stays


@pytest.mark.parametrize('form', [
    'python -m cProfile "{S}" approve', 'python -m pdb "{S}" approve', 'python -m trace --count "{S}" approve',
    'python -m profile "{S}" approve', 'python -m runpy "{S}" advance', 'python -m coverage run "{S}" approve',
    'coverage run "{S}" approve', 'git -c alias.x="!python {S} approve" x', 'script -qc "python {S} approve" /dev/null',
    'su -c "python {S} approve"', 'pipx run "{S}" approve', 'python -m cProfile "{S}" jump 1 5',
    'python x.py "{S}" approve', 'make -f /dev/null --eval="x:;python {S} approve" x'])
def test_t16_14_runner_modules_and_command_line_words_stay_denied_inside_aid(base, form):
    """R1-01 (fix cycle 1): T16-14 judges only interpreter script operands, but a script
    runner module (cProfile, pdb, runpy, trace, coverage, ...), a later operand that is the
    session script, or a command line carried in one word (git alias, script -qc, su -c,
    make --eval) still runs aid_session.py: every T3 actual-call deny stays (HEAD 5f8f199)."""
    cmd = form.format(S=S)
    for place in ('p4/block', 'p4/log', 'p5/warn'):
        assert _w(base, place).bash(cmd)[0] == 'DENY', (place, cmd)


def test_t16_14_runner_forms_running_other_files_stay_allowed(base):
    w = _w(base, 'p4/block')
    for cmd in ('python -m cProfile tools/bench.py approve', 'git -c core.pager=less log --grep approve'):
        assert w.bash(cmd) == ('ALLOW', None), cmd
    # T16 B1: T16-14 reverted: a confirmed word after the name is an accepted false denial.
    assert w.bash('coverage run -m pytest tests/test_aid_session.py -k approve')[0] == 'DENY'    # T16 B1


# T16-14 vs the T15 A1 residual (contract E5: "A1's residual list is unchanged otherwise"):
# the forms the docs list as not caught keep their 5f8f199 rows. Outside AID they run without
# a prompt; inside AID the T3 text check refuses them (p1 by the allow-list, p4 and log/warn
# by the text check) when the word after the script is a T3 subcommand.
A1_PLACES = ('non-AID', 'p1/block', 'p4/block', 'p1/log', 'p4/log', 'p4/warn')


def _a1_row(non_aid, p1, rest):
    return dict(zip(A1_PLACES, (non_aid, p1) + (rest,) * 4))


@pytest.mark.parametrize('cmd', [
    'pythonw "{S}" approve', 'pyw "{S}" approve', 'exec -a x python "{S}" approve',
    'env -u FOO python "{S}" approve', 'sudo -u x python "{S}" approve',
    'setsid python "{S}" approve', 'flock /tmp/l python "{S}" approve',
    'chronic python "{S}" approve', 'case x in x) python "{S}" approve;; esac',
    'xargs -a /dev/null python "{S}" approve', 'c="python {S} approve"; eval "$c"',
])
def test_t16_14_a1_residual_forms_keep_their_5f8f199_verdicts(base, cmd):
    cmd = cmd.format(S=S)
    got = {pl: _w(base, pl).bash(cmd)[0] for pl in A1_PLACES}
    assert got == _a1_row('ALLOW', 'DENY', 'DENY'), (cmd, got)


@pytest.mark.parametrize('cmd', ['S="{S}"; pythonw "$S" approve', 'pythonw "{S}" reset',
                                 'chronic python "{S}" qa-pass'])
def test_t16_14_a1_residual_forms_without_a_t3_word_after_the_path_get_through_from_p4(base, cmd):
    cmd = cmd.format(S=S)
    got = {pl: _w(base, pl).bash(cmd)[0] for pl in A1_PLACES}
    assert got == _a1_row('ALLOW', 'DENY', 'ALLOW'), (cmd, got)


def test_t16_14_pythonw_is_not_an_every_folder_interpreter():
    """The every-folder decision judges python/python3/py only (T15 A1); pythonw is A1."""
    assert aid_guard.session_ask_verdict('pythonw "{}" approve'.format(S)) == (None, None)
    assert aid_guard.session_ask_verdict('chronic python "{}" approve'.format(S)) == (None, None)


# --- T16-15 the hook audit log is redacted ------------------------------------------------

def test_t16_15_audit_log_keeps_no_secret(base):
    w = _w(base, 'p1/block')
    tok = ''.join(['gh', 'p_', 'A1b2C3d4' * 5])   # T17 (owner 2026-11-20): U-17, no folded literal
    pw = 'Hunter' + '2secret'
    v = w.bash('deploy --token {} DB_PASSWORD={}'.format(tok, pw))
    assert v[0] == 'DENY'
    w.write('src/{}.ts'.format(tok))
    log = (w.P / '.aid' / 'audit' / 'tool-usage.jsonl').read_text(encoding='utf-8')
    assert log.strip() and tok not in log and pw not in log, log


def test_t16_15_fallback_masks_key_rule_and_tokens(monkeypatch):
    import aid_hooks
    monkeypatch.setattr(aid_hooks, '_REDACT', [None])
    tok = ''.join(['gh', 'p_', 'Z9y8X7w6' * 5])   # T17 (owner 2026-11-20): U-17, no folded literal
    out = aid_hooks.audit_redact('x --token {} AWS_SECRET_ACCESS_KEY=abc client_secret: "q" ok'.format(tok))
    assert tok not in out and 'abc' not in out and '"q"' not in out and out.endswith(' ok'), out


# --- fix cycle 2 (R2-01 .. R2-05, R2-A1) ---------------------------------------------------

R2_BRACE_STATE = ['sed -i s/4/5/ .aid/state.{json,x}', 'tee .aid/{state.json,x} < t', 'dd of=.aid/state.{x,json} < t',
                  'touch .aid/state.{json,x}']


@pytest.mark.parametrize('place', ['p4/block', 'p5/warn', 'p1/log'])
def test_t16_2_brace_writes_of_control_files_are_denied_inside_aid(base, place):
    """R2-01: `{a,b}` is static text bash expands before the command runs, so a brace word
    that spells the state file or another control file is that file (state: every folder,
    T16-2; the others: the in-AID control-file check)."""
    w = _w(base, place)
    for cmd in R2_BRACE_STATE + ['touch .aid/hooks/conf{ig,x}.json', 'sed -i s/a/b/ .aid/{hooks,x}/config.json',
                                 'tee .aid/pipeline/ESCALATION.{json,x} < t', 'echo x > .aid/hooks/{config,x}.json']:
        v = w.bash(cmd)
        assert v[0] == 'DENY', (place, cmd, v)
    for cmd in ('touch src/{a,b}.ts', 'cat .aid/state.{json,x}', 'echo x > build/{a,b}.log'):
        assert w.bash(cmd) == ('ALLOW', None), (place, cmd)


def test_t16_2_brace_sed_effect_check(base):
    """R2-01 effect: in a project made by `aid_session.py init 1 4` the brace spelling is
    denied at p4/block and the state keeps phase 4; bash itself shows the same line rewrites
    current_phase (so the deny is what stops it)."""
    P, H = base / 'eff', base / 'effhome'
    P.mkdir()
    (H / '.claude').mkdir(parents=True)
    env = dict(os.environ, HOME=str(H), USERPROFILE=str(H), AID_HOME=str(H / '.aid'), CLAUDE_PROJECT_DIR=str(P))
    p = subprocess.run([sys.executable, S, 'init', '1', '4'], cwd=str(P), env=env, capture_output=True,
                       text=True, timeout=120)
    assert p.returncode == 0, p.stdout + p.stderr
    state = P / '.aid' / 'state.json'
    assert json.loads(state.read_text(encoding='utf-8'))['current_phase'] == 4
    cmd = 'sed -i \'s/"current_phase": 4/"current_phase": 5/\' .aid/state.{json,x}'
    payload = {'session_id': uuid.uuid4().hex, 'cwd': str(P), 'tool_name': 'Bash', 'tool_input': {'command': cmd}}
    v = decision(run('phase-gate-bash', P, H, payload))
    assert v[0] == 'DENY', v
    assert json.loads(state.read_text(encoding='utf-8'))['current_phase'] == 4
    bash = shutil.which('bash')
    if bash:
        copy = base / 'copy'
        (copy / '.aid').mkdir(parents=True)
        (copy / '.aid' / 'state.json').write_bytes(state.read_bytes())
        subprocess.run([bash, '-c', cmd], cwd=str(copy), capture_output=True, timeout=30)
        assert json.loads((copy / '.aid' / 'state.json').read_text(encoding='utf-8'))['current_phase'] == 5


def test_t16_2_cd_forms_are_tracked_and_ordinary_cd_writes_stay_allowed(base):
    """R2-02: pushd / builtin cd / command cd / cd -P / cd -- move into .aid like cd does; a
    cd elsewhere, and a state.json outside .aid, are not the project state file."""
    w = _w(base, 'non-AID')
    for cmd in ('cd src && echo x > state.json', 'pushd build && echo x > state.json', 'echo x > state.json',
                'cd -P src && echo x > state.json', 'builtin cd docs && cp t state.json'):
        assert w.bash(cmd) == ('ALLOW', None), cmd


def test_t16_2_backups_reads_and_user_level_paths_are_not_state_writes(base):
    """R2-03: only a write destination counts (redirect, cp/mv/ln/install target, tee/touch/
    sed -i files, dd of=): a cp/mv source, an rm operand and a bash `*` (which never matches a
    dot folder) do not; ~/.aid/state.json is the user-level file (T3 A5). The T15-10 literal
    rule still refuses a non-reading command naming .aid/state.json (contract T16-2)."""
    ok = ['cp .aid/state.json bak/', 'cp .aid/state.json bak.json', 'cp -r .aid/* backup/', 'cp .aid/*.json bak/',
          'rm -rf ~/.aid/*', 'cp ~/.aid/*.json bak/', 'cp ~/.aid/state.json bak.json', 'rm -f */state.json',
          'echo x > ~/.aid/state.json', 'sed s/a/b/ .aid/stat?.json']
    for place in ('non-AID', 'p4/block', 'p5/warn'):
        w = _w(base, place)
        for cmd in ok:
            assert w.bash(cmd) == ('ALLOW', None), (place, cmd)
        assert w.ps('Copy-Item .aid\\* backup') == ('ALLOW', None), place
        assert w.bash('tar czf b.tgz .aid/state.json')[0] == 'DENY', place
        assert w.ps('Copy-Item x .aid\\stat?.json')[0] == 'DENY', place
    # Deleting every file of a project's .aid folder deletes its control files: refused inside AID only.
    assert _w(base, 'non-AID').bash('rm -rf .aid/*') == ('ALLOW', None)
    assert _w(base, 'p4/block').bash('rm -rf .aid/*')[0] == 'DENY'


R2_04_FORMS = ['python -m runpy "{S}" approve', 'python -m pdb "{S}" approve', 'python -m cProfile "{S}" approve',
               'python -m coverage run "{S}" approve', 'coverage run "{S}" approve', 'pipx run "{S}" approve',
               'python -m memory_profiler "{S}" approve', 'python -m x.y "{S}" approve',
               'git -c alias.x="!python {S} approve" x', 'script -qc "python {S} approve" /dev/null',
               'su -c "python {S} approve"', 'make -f /dev/null --eval="x:;python {S} approve" x',
               'env -S "python {S} approve"']


@pytest.mark.parametrize('form', R2_04_FORMS)
def test_t16_13_runner_modules_and_carried_command_lines_are_denied_in_every_folder(base, form):
    """R2-04: a script-runner module, coverage/pipx, a later session operand, or a command line
    carried in one word runs aid_session.py with a confirmed subcommand: a non-canonical
    spelling, denied in every folder (D1, T15-3), like `uv run` (T16-13)."""
    cmd = form.format(S=S)
    assert aid_guard.session_ask_verdict(cmd)[0] == 'deny', cmd
    for place in ('non-AID', 'p4/block'):
        assert _w(base, place).bash(cmd)[0] == 'DENY', (place, cmd)


def test_t16_13_runpy_reset_and_qa_pass_are_denied_inside_aid(base):
    for sub in ('reset', 'qa-pass x'):
        cmd = 'python -m runpy "{}" {}'.format(S, sub)
        for place in ('p4/block', 'p5/warn', 'p1/log'):
            assert _w(base, place).bash(cmd)[0] == 'DENY', (place, cmd)


@pytest.mark.parametrize('place', ['p4/block', 'p5/warn'])
def test_t16_4_powershell_glob_deletes_of_control_files_are_denied_inside_aid(base, place):
    """R2-05: the PowerShell forms of the R1-06 glob deletes (PowerShell wildcards match dot names)."""
    w = _w(base, place)
    for cmd in ('Remove-Item .aid\\pipeline\\ESC*.json', 'Remove-Item .aid\\* -Recurse', 'ri .aid\\stat*.json',
                'del .aid\\*'):
        assert w.ps(cmd)[0] == 'DENY', (place, cmd)
    for cmd in ('Remove-Item build\\* -Recurse', 'del dist\\*.js'):
        assert w.ps(cmd) == ('ALLOW', None), (place, cmd)


def test_t16_6_session_start_names_linked_commands_and_control_files(base):
    """R2-A1: without CLAUDE_PLUGIN_ROOT (a link-project install) the SessionStart text gives the
    `! python "<AID>/hooks/aid_session.py" ...` lines; the phase restriction names the control
    files and the absolute SECURITY-MODEL path."""
    w = _w(base, 'p1/block')
    (w.P / '.aid' / 'state.json').write_text(json.dumps(
        {'current_phase': 1, 'status': 'active', 'role': 'developer'}), encoding='utf-8')
    payload = {'session_id': uuid.uuid4().hex, 'cwd': str(w.P), 'source': 'startup'}
    out = {}
    for mode, root in (('linked', ''), ('plugin', R)):
        o = run('session-start', w.P, w.H, payload, {'CLAUDE_PLUGIN_ROOT': root})
        out[mode] = json.loads(o)['hookSpecificOutput']['additionalContext']
    assert '! python "{}" approve'.format(S) in out['linked'], out['linked']
    assert '! python "{}" advance'.format(S) in out['linked']
    assert '! python "{}"'.format(S) not in out['plugin'], out['plugin']
    for text in out.values():
        assert '.aid/hooks/' in text and 'QA markers' in text and 'pipeline escalation' in text, text
        assert R + '/docs/SECURITY-MODEL.md' in text, text
    # R3-D4 (fix cycle 3): a `!` line the user types runs in bash mode, outside the hooks and
    # the ask rules: no confirmation prompt follows, so the text must not promise one.
    assert 'asks to confirm phase changes' not in out['linked'], out['linked']
    assert "typing the line is the user's confirmation" in out['linked'], out['linked']


# --- fix cycle 3 (R3-01 .. R3-03, R3-06) ---------------------------------------------------

R3_01_FORMS = ["cd .aid && bash -c 'echo x > state.json'", "cd .aid && bash -c 'rm state.json'",
               "cd .aid && sh -c 'cp ../t state.json'", "cd .aid && sh -c 'cp ../t hooks/config.json'",
               "cd .aid && python -c \"open('state.json','w')\"",
               "cd .aid && node -e \"require('fs').writeFileSync('state.json','{}')\"",
               "cd .claude && bash -c 'echo x > settings.json'", "cd .aid; bash -c 'echo x > state.json'",
               "pushd .aid && perl -e 'open(F,\">state.json\")'", 'cd "$X/.aid" && ./run',
               "cd .aid && x=$(bash -c 'echo x > state.json')"]


@pytest.mark.parametrize('place', ['p4/block', 'p5/warn', 'p1/log'])
def test_t16_10_cd_into_a_control_folder_then_a_runner_is_denied(base, place):
    """R3-01: T16-10 lets `cd .aid` read, but a shell or interpreter run after it writes the
    control files by bare names (state.json, settings.json): every command after a cd into a
    control folder that is not a read is refused, as at 5f8f199."""
    w = _w(base, place)
    for cmd in R3_01_FORMS:
        v = w.bash(cmd)
        assert v[0] == 'DENY', (place, cmd, v)
    # T16 B1: T16-10 reverted: a read after such a cd is an accepted false denial (5f8f199).
    for cmd in ('cd .aid && ls', 'cd ~/.aid; ls feedback', 'cd .aid && cat state.json | jq .',
                'cd .aid && git status', 'cd .aid && cd .. && npm test'):
        assert w.bash(cmd)[0] == 'DENY', (place, cmd)    # T16 B1


def _init_project(base, phase):
    P, H = base / 'eff', base / 'effhome'
    P.mkdir()
    (H / '.claude').mkdir(parents=True)
    env = dict(os.environ, HOME=str(H), USERPROFILE=str(H), AID_HOME=str(H / '.aid'), CLAUDE_PROJECT_DIR=str(P))
    p = subprocess.run([sys.executable, S, 'init', '1', str(phase)], cwd=str(P), env=env, capture_output=True,
                       text=True, timeout=120)
    assert p.returncode == 0, p.stdout + p.stderr
    return P, H


def _bash_verdict(P, H, cmd):
    payload = {'session_id': uuid.uuid4().hex, 'cwd': str(P), 'tool_name': 'Bash', 'tool_input': {'command': cmd}}
    return decision(run('phase-gate-bash', P, H, payload))


def test_t16_10_cd_python_effect_check(base):
    """R3-01 effect: in a project made by `init 1 4` (default block) the cd + python form that
    rewrites current_phase is denied; bash itself shows the same line moves the phase (so the
    deny is what stops it)."""
    P, H = _init_project(base, 4)
    state = P / '.aid' / 'state.json'
    code = "import json;p='state.json';s=json.load(open(p));s['current_phase']=5;json.dump(s,open(p,'w'))"
    assert _bash_verdict(P, H, 'cd .aid && python -c "{}"'.format(code))[0] == 'DENY'
    assert json.loads(state.read_text(encoding='utf-8'))['current_phase'] == 4
    copy = base / 'copy'
    (copy / '.aid').mkdir(parents=True)
    (copy / '.aid' / 'state.json').write_bytes(state.read_bytes())
    subprocess.run([sys.executable, '-c', code], cwd=str(copy / '.aid'), capture_output=True, timeout=60)
    assert json.loads((copy / '.aid' / 'state.json').read_text(encoding='utf-8'))['current_phase'] == 5


R3_02_FORMS = ['pypy3 "{S}" approve', 'pypy "{S}" approve', 'ipython "{S}" approve', 'coverage3 run "{S}" advance',
               'coverage-3.11 run "{S}" approve', 'python3-dbg "{S}" approve', 'graalpy "{S}" approve',
               'pytest "{S}" approve', 'coverage3 run -m hooks.aid_session approve', './x "{S}" approve',
               './pypy3 "{S}" advance', 'cd hooks && ./py aid_session.py approve']


@pytest.mark.parametrize('form', R3_02_FORMS)
def test_t16_14_any_command_word_running_the_script_is_a_call_inside_aid(base, form):
    """R3-02: an interpreter under any name (pypy3, ipython, coverage3, pytest, a copy of
    python.exe called ./x) runs the session script: inside AID the T3 text check counts every
    command word except a known non-runner (echo, printf, grep, git commit -m, cat, ls)."""
    cmd = form.format(S=S)
    for place in ('p4/block', 'p4/log', 'p5/warn'):
        v = _w(base, place).bash(cmd)
        assert v[0] == 'DENY', (place, cmd, v)


def test_t16_14_renamed_python_copy_effect_check(base):
    """R3-02 effect: a copy of python named pypy3 may be made, and the approve / advance call
    through it is then denied at p4 (block): the phase stays 4."""
    P, H = _init_project(base, 4)
    assert _bash_verdict(P, H, 'cp "$(command -v python)" ./pypy3.exe')[0] == 'ALLOW'
    for sub in ('approve', 'advance'):
        assert _bash_verdict(P, H, './pypy3 "{}" {}'.format(S, sub))[0] == 'DENY', sub
    assert json.loads((P / '.aid' / 'state.json').read_text(encoding='utf-8'))['current_phase'] == 4


def test_t16_14_prose_with_a_confirmed_word_after_the_name_is_an_accepted_false_denial(base):
    # T16 B1: T16-14 reverted to 5f8f199 (R4-03): text with a confirmed word right after
    # aid_session is denied inside AID; text without one stays allowed.
    w = _w(base, 'p4/block')
    for cmd in ('echo "run aid_session approve later"',
                'printf "%s\\n" "aid_session approve"', 'git log --grep "aid_session approve"'):
        assert w.bash(cmd)[0] == 'DENY', cmd    # T16 B1
    for cmd in ('grep -n approve hooks/aid_session.py', 'cat hooks/aid_session.py | grep approve',
                'git commit -m "aid_session: fix approve"'):
        assert w.bash(cmd) == ('ALLOW', None), cmd


R3_03_NON_AID = ['git mv state.json .aid/', 'git -C .aid mv ../state.json .',
                 "bash -c 'echo x > .aid/state.json'", "bash --rcfile /dev/null -c 'echo x > .aid/state.json'",
                 "bash -c -- 'echo x > .aid/state.json'", "bash --init-file x -O extglob -c 'cp t .aid/state.json'",
                 'git log -1 --output=.aid/state.json', 'git diff --output .aid/state.json']
# T16 B1 (E2 bounded): writes reached through a cwd change (cd, pushd, env -C) or a shell -c
# body that runs elsewhere name no .aid/state.json: outside AID an accepted residual.
R3_03_NON_AID_RESIDUAL = [
    "bash -c 'cd .aid && echo x > state.json'", 'bash -c "cd .aid; tee state.json < ../t"',
    "sh -c 'cd .aid && cp ../t state.json'", "bash -c 'pushd .aid; echo x > state.json'",
    "nohup bash -c 'cd .aid && echo x > state.json'", "cd .aid && bash -c 'echo x > state.json'",
    'env -C .aid tee state.json < t', 'env --chdir=.aid cp ../t state.json', 'cd .aid && echo x > state.json:x',
    'bash -c \'mkdir -p .aid && cd .aid && echo "{\\"current_phase\\": 5}" > state.json\'',
    "bash -o pipefail -ec 'cd .aid && echo x > state.json'", 'cd "$D/.aid" && echo x > state.json']


@pytest.mark.parametrize('cmd', R3_03_NON_AID)
def test_t16_2_shell_bodies_git_mv_and_git_output_outside_aid(base, cmd):
    """R3-03 / R4-02 / R4-04(1): a static `bash -c` body (after --rcfile F, --init-file F,
    -O opt or `--`), `git mv SRC DIR/` and `git log/diff --output` that write a literally
    named .aid/state.json are refused in a folder that is not an AID project."""
    w = _w(base, 'non-AID')
    (w.P / '.aid').mkdir(exist_ok=True)
    v = w.bash(cmd)
    assert v[0] == 'DENY' and 'aid_session.py' in v[1], (cmd, v)


@pytest.mark.parametrize('place', ['p1/block', 'p4/block', 'p1/log', 'p5/warn'])
def test_t16_2_git_output_and_shell_option_forms_are_denied_inside_aid(base, place):
    """R4-02: git log/diff/show --output[=]<f> is never an exempt read; R4-04(1): a shell's
    --rcfile F / --init-file F / -O opt / `--` do not hide the -c body."""
    w = _w(base, place)
    for cmd in ('git log -1 --output=.aid/state.json', 'git show --output .aid/state.json HEAD',
                'git -C .aid log -1 --format=x --output=state.json', 'git diff --output=.aid/hooks/config.json',
                "bash --rcfile /dev/null -c 'echo x > .aid/state.json'",
                "bash -c -- 'echo x > .aid/state.json'", "bash --init-file x -O extglob -c 'rm .aid/state.json'"):
        assert w.bash(cmd)[0] == 'DENY', (place, cmd)
    assert w.bash('git log -1 --oneline') == ('ALLOW', None), place


@pytest.mark.parametrize('cmd', R3_03_NON_AID_RESIDUAL)
def test_t16_2_cwd_change_forms_are_a_documented_residual_outside_aid(base, cmd):
    # T16 B1: accepted residual outside AID (like A1); inside AID the same form is refused.
    w = _w(base, 'non-AID')
    (w.P / '.aid').mkdir(exist_ok=True)
    assert w.bash(cmd) == ('ALLOW', None), cmd    # T16 B1
    assert _w(base, 'p4/block').bash(cmd)[0] == 'DENY', cmd


@pytest.mark.parametrize('place', ['p4/block', 'p5/warn', 'p1/log'])
def test_t16_2_shell_bodies_writing_control_files_are_denied_inside_aid(base, place):
    w = _w(base, place)
    for cmd in ("bash -c 'cd .aid && echo x > state.json'", "bash -c 'cd .claude && echo x > settings.local.json'",
                "sh -c 'cd .aid/hooks && echo {} > config.json'", 'env -C .claude tee settings.json < t'):
        v = w.bash(cmd)
        assert v[0] == 'DENY', (place, cmd, v)


def test_t16_2_ordinary_shell_bodies_and_cds_stay_allowed_outside_aid(base):
    """R3-03 / R3-06: no new false denial: state.json outside a .aid folder, a cd to a folder
    named by a variable (5f8f199 allowed it), git mv elsewhere."""
    w = _w(base, 'non-AID')
    for cmd in ("bash -c 'echo x > state.json'", 'env -C src cp ../t state.json', 'git mv a.json b/',
                "bash -ec 'cd build && echo x > state.json'", 'cd "$TMPDIR" && echo \'{}\' > state.json',
                'cd "$D" && echo x > state.json', "sh -c 'npm test'"):
        assert w.bash(cmd) == ('ALLOW', None), cmd
