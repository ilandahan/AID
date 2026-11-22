"""
T15 WS-A gate core (T15-acceptance.md, T15-1 .. T15-11).

WHY THESE TESTS:
- PROBLEM: the 3.0.8 release gate found that the phase gates let the agent write Claude Code
  capability folders before Phase 4 (R-01), ran human-confirmed aid_session.py calls without
  a prompt outside AID projects (R-02, R-13), never recognised a second installed plugin root
  (G9-X3), let the agent forge QA verdict markers (R-07), read phase 99 as "past every gate",
  and kept quiet at SessionStart about gates lowered to log/warn (R-14).
- COST OF FAILURE: an agent changes the AID phase, records its own QA pass or installs
  hooks into ~/.claude/settings.json without the user ever being asked.
- SUCCESS: the real hook, spawned through hooks/hook-runner.mjs as Claude Code runs it, gives
  the decisions the contract names.

Harness (contract section 4): fake HOME/USERPROFILE/AID_HOME; CLAUDE_PROJECT_DIR and
CLAUDE_CONFIG_DIR unset unless a test sets them. <R> = the live plugin root (this checkout).
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
sys.path.insert(0, str(REPO / 'hooks'))
import aid_guard  # noqa: E402

pytestmark = pytest.mark.skipif(shutil.which('node') is None, reason='node is needed for hook-runner.mjs')

LEVELS = ('block', 'warn', 'log')
SUBS = {'approve': 'approve', 'advance': 'advance', 'jump': 'jump developer 5',
        'init': 'init developer 4', 'memory-sync': 'memory-sync', 'memory-apply': 'memory-apply abc123',
        'reset': 'reset', 'qa-pass': 'qa-pass T-1 --note "ok"'}


def _marker_above(p):
    return any((d / '.aid' / 'state.json').is_file() or (d / '.aid' / 'hooks' / 'config.json').is_file()
               for d in [p] + list(p.parents))


@pytest.fixture
def base(tmp_path):
    """A directory with no AID marker above it (same rule as test_aid_hooks.clean_tmp)."""
    if not _marker_above(tmp_path):
        yield tmp_path
        return
    alt = Path(tempfile.mkdtemp(prefix='aid-t15-', dir=tmp_path.anchor))
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
    """An AID project P (or, aid=False, a plain folder) plus a fake home H."""

    def __init__(self, root, phase=1, level='block', aid=True):
        self.P, self.H = root / 'proj', root / 'home'
        self.P.mkdir(parents=True, exist_ok=True)
        (self.H / '.claude').mkdir(parents=True, exist_ok=True)
        self.env = {}
        if aid:
            for d in ('.aid/hooks', '.claude', 'docs'):
                (self.P / d).mkdir(parents=True, exist_ok=True)
            (self.P / '.claude' / 'settings.json').write_text('{}', encoding='utf-8')
            self.state(phase)
            self.level(level)

    def state(self, phase):
        (self.P / '.aid' / 'state.json').write_text(json.dumps({'current_phase': phase}), encoding='utf-8')

    def level(self, level):
        (self.P / '.aid' / 'hooks' / 'config.json').write_text(json.dumps(
            {'enforcement': {'phase_gate_write': level, 'phase_gate_bash': level}}), encoding='utf-8')

    def _payload(self, tool, tool_input):
        # A fresh session id per call: each call takes its own first-use baseline, so a test
        # may change the level between calls without tripping layer B.
        return {'session_id': uuid.uuid4().hex, 'cwd': str(self.P), 'tool_name': tool,
                'tool_input': tool_input}

    def bash(self, cmd, tool='Bash'):
        return decision(run('phase-gate-bash', self.P, self.H, self._payload(tool, {'command': cmd}), self.env))

    def ps(self, cmd):
        return self.bash(cmd, tool='PowerShell')

    def write(self, path, tool='Write'):
        return decision(run('phase-gate-write', self.P, self.H,
                            self._payload(tool, TOOL_INPUT[tool](path)), self.env))

    def session_start(self, sid='s1'):
        out = run('session-start', self.P, self.H, {'session_id': sid, 'source': 'startup',
                                                    'cwd': str(self.P)}, self.env)
        return json.loads(out) if out else {}


def _cases(base):
    """Non-AID folder plus an AID project at phase 0, 1 and 4 at every level."""
    yield 'non-AID', Where(base / 'n', aid=False)
    for phase in (0, 1, 4):
        for level in LEVELS:
            yield 'p{}/{}'.format(phase, level), Where(base / 'p{}{}'.format(phase, level), phase, level)


# --- T15-1 .claude capability folders before Phase 4 ------------------------------------

CAP_DIRS = ('skills', 'agents', 'commands', 'output-styles', 'rules', 'hooks')


@pytest.mark.parametrize('tool', sorted(TOOL_INPUT))
def test_t15_1_write_tools_cannot_fill_capability_dirs_before_phase_4(base, tool):
    for phase in (0, 3):
        w = Where(base / str(phase), phase)
        for d in CAP_DIRS:
            target = '.claude/{}/x/{}'.format(d, 'a.ipynb' if tool == 'NotebookEdit' else 'SKILL.md')
            v = w.write(target, tool)
            assert v[0] == 'DENY', (phase, target, v)
        assert w.write(str(w.P / '.claude' / 'Skills' / 'y.md'), tool)[0] == 'DENY'


def test_t15_1_mkdir_into_capability_dirs_is_denied(base):
    w = Where(base, 1)
    for d in CAP_DIRS:
        v = w.bash('mkdir -p .claude/{}/x'.format(d))
        assert v[0] == 'DENY', (d, v)


@pytest.mark.parametrize('cmd', ['echo x > .claude/agents/a.md', 'cp a .claude/commands/b.md',
                                 'mv a .claude/skills/b.md', 'touch .claude/rules/r.md'])
def test_t15_1_redirect_cp_mv_touch_into_capability_dirs_are_denied(base, cmd):
    w = Where(base, 2)
    assert w.bash(cmd)[0] == 'DENY', cmd
    assert w.write('.claude/agents/a.md')[0] == 'DENY'


def test_t15_1_plans_and_plain_claude_files_stay_writable(base):
    w = Where(base, 1)
    for p in ('.claude/plans/x.md', '.claude/notes.md'):
        assert w.write(p) == ('ALLOW', None), p
    assert w.write('.claude/skills/x/SKILL.md')[0] == 'DENY'


def test_t15_1_phase_4_writes_capability_dirs_and_log_relaxes_the_rule(base):
    w = Where(base, 4)
    for d in ('skills', 'agents', 'commands', 'output-styles', 'rules'):
        assert w.write('.claude/{}/x.md'.format(d)) == ('ALLOW', None), d
    assert w.bash('mkdir -p .claude/skills/x') == ('ALLOW', None)
    assert w.write('.claude/hooks/x.sh')[0] == 'DENY'           # still a control file
    w.state(1)
    w.level('log')
    assert w.write('.claude/skills/x/SKILL.md') == ('ALLOW', None)   # a phase rule: relaxed at log
    assert w.write('.claude/hooks/x.sh')[0] == 'DENY'           # control files: every level
    w.state(1)
    w.level('block')
    assert w.write('.claude/skills/x/SKILL.md')[0] == 'DENY'


# --- T15-2 the gate asks for confirmed subcommands, any folder ---------------------------

@pytest.mark.parametrize('sub', sorted(SUBS))
def test_t15_2_confirmed_subcommands_are_asked_everywhere(base, sub):
    cmd = 'python "{}" {}'.format(S, SUBS[sub])
    for label, w in _cases(base):
        v = w.bash(cmd)
        assert v[0] == 'ASK', (label, cmd, v)
        assert sub in v[1] and 'must confirm' in v[1], (label, v)


def test_t15_2_init_in_a_fresh_folder_and_memory_sync_outside_aid(base):
    w = Where(base, aid=False)
    for cmd in ('python "{}" init developer 4'.format(S), 'python3 "{}" memory-sync'.format(S),
                'py "{}" reset --all'.format(S.replace('/', '\\'))):
        assert w.bash(cmd)[0] == 'ASK', cmd
    assert list(w.P.iterdir()) == []                              # the gate created nothing


@pytest.mark.parametrize('sub', ['start developer 1', 'review 1 PASS', 'roles'])
def test_t15_2_unconfirmed_canonical_calls_stay_silent(base, sub):
    for label, w in (('non-AID', Where(base / 'n', aid=False)), ('p1', Where(base / 'a', 1))):
        assert w.bash('python "{}" {}'.format(S, sub)) == ('ALLOW', None), (label, sub)


def test_t15_2_a_foreign_aid_session_is_asked_outside_aid_and_denied_inside(base):
    fake = base / 'elsewhere' / 'hooks'
    fake.mkdir(parents=True)
    (fake / 'aid_session.py').write_text('print(1)\n', encoding='utf-8')
    cmd = 'python "{}/aid_session.py" approve'.format(str(fake).replace('\\', '/'))
    v = Where(base / 'n', aid=False).bash(cmd)
    assert v[0] == 'ASK' and 'approve' in v[1] and 'confirm' in v[1], v
    # Review R1-C5: really vary the level. AC-23's refusal of a foreign script before Phase 4
    # is a phase rule: DENY at block; relaxed at warn/log, where the user is still asked.
    for level in LEVELS:
        v = Where(base / level, 1, level).bash(cmd)
        assert v[0] == ('DENY' if level == 'block' else 'ASK'), (level, v)


# --- T15-3 non-canonical confirmed calls are denied everywhere ---------------------------

T15_3_FORMS = ['PYTHON "{s}" approve', 'python "{s}" "approve"', 'python "{s}"  approve',
               'python "{s}" approve; echo x', 'python "{s}" ap""prove', 'python "{s}" reset > out.txt']


@pytest.mark.parametrize('form', T15_3_FORMS)
def test_t15_3_non_canonical_confirmed_calls_are_denied(base, form):
    cmd = form.format(s=S)
    want = aid_guard.confirmed_form_verdict(cmd)
    assert want, cmd
    for label, w in _cases(base):
        v = w.bash(cmd)
        assert v[0] == 'DENY' and want in v[1], (label, cmd, v)
    w = Where(base / 'p5', 5, 'log')
    assert w.bash(cmd)[0] == 'DENY'


# Review R1-C1: the shell builds the script name or the subcommand only at run time. Such a
# call can be a confirmed subcommand and is never in the asked spelling, so it is denied.
# The folder part is quoted (R holds a space and an apostrophe); the glob stays unquoted so
# bash really expands it.
T15_3_UNRESOLVED = ['python "{s}" $(echo approve)', 'python "{s}" `echo approve`', 'python "{s}" $X',
                    'python "{s}" ${{A}}pprove', 'python "{r}/hooks/"aid_ses*.py approve',
                    'python "{r}/hooks/"aid_sess?on.py init developer 4', 'python "{r}/hooks/"aid_[s]ession.py approve',
                    'python "{r}/hooks/"aid_{{session,x}}.py approve', 'S=aid_session; python "{r}/hooks/"$S.py approve',
                    'xargs python "{s}" < f', 'python $(cat f) approve',
                    'bash -c "python \\"{s}\\" \\$X"',
                    # Review R2-C2: interpreter one-liners and child processes with list
                    # arguments, and ANSI-C quoting anywhere in the script path.
                    'python3 -c "import subprocess; subprocess.run([\\"python\\", r\\"{s}\\", \\"init\\", '
                    '\\"developer\\", \\"4\\"])"',
                    'python3 -c "import runpy,sys; sys.argv=[\\"x\\",\\"approve\\"]; '
                    'runpy.run_path(r\\"{s}\\", run_name=\\"__main__\\")"',
                    'node -e "require(\\"child_process\\").execFileSync(\\"python\\",[\\"{s}\\",\\"approve\\"])"',
                    "python $'{rq}/hooks/aid\\x5fsession.py' reset",
                    # Review R3-C3: wrappers, interpreter options, `$(which python)` and a
                    # subcommand held in a variable, with the script in a variable.
                    'S="{s}"; timeout 60 python "$S" approve', 'S="{s}"; nice -n 5 python "$S" approve',
                    'S="{s}"; winpty python "$S" approve', 'S="{s}"; uv run python "$S" approve',
                    'S="{s}"; $(which python) "$S" approve', 'S="{s}"; python -X utf8 "$S" approve',
                    'S="{s}"; python -W ignore "$S" init developer 4', 'S="{s}"; C=approve; python "$S" "$C"']


# Review R3-C1: a trailing comment holding an apostrophe must not read as an open quote that
# turns the whole run-time-built check off (bash ignores the comment and runs the call).
T15_3_COMMENTED = ['python "{s}" $(echo approve) # don\'t', 'python "{s}" $X #\'',
                   'python "{r}/hooks/"aid_ses*.py approve #\'',
                   "python $'{rq}/hooks/aid\\x5fsession.py' reset #'",
                   'S=aid_session; python "{r}/hooks/$S.py" qa-pass T-1 # it\'s',
                   'S="{s}"; python "$S" approve # don\'t']


@pytest.mark.parametrize('form', T15_3_COMMENTED)
def test_t15_3_a_trailing_comment_cannot_hide_a_run_time_built_call(base, form):
    cmd = form.format(s=S, r=R, rq=R.replace("'", "\\'"))
    assert aid_guard.confirmed_form_verdict(cmd), cmd
    for label, w in (('non-AID', Where(base / 'n', aid=False)), ('p1/log', Where(base / 'a', 1, 'log')),
                     ('p4/block', Where(base / 'b', 4, 'block')), ('p5/warn', Where(base / 'c', 5, 'warn'))):
        v = w.bash(cmd)
        assert v[0] == 'DENY', (label, cmd, v)


def test_t15_3_unparsable_text_naming_the_session_fails_closed():
    """R3-C1: an unterminated quote (bash runs nothing) never turns the check off when the
    text names aid_session or builds a word after python; comments and $# still parse."""
    assert aid_guard._unresolved_session_call('python "{}" $(echo approve) "oops'.format(S))
    assert aid_guard._unresolved_session_call("python $S approve 'oops")
    assert aid_guard._shell_segments("echo $# done # it's") == [['echo', '$#', 'done']]
    assert aid_guard.session_ask_verdict("ls 2>&1 | grep x # it's fine") == (None, None)


@pytest.mark.parametrize('form', T15_3_UNRESOLVED)
def test_t15_3_run_time_built_session_calls_are_denied(base, form):
    cmd = form.format(s=S, r=R, rq=R.replace("'", "\\'"))
    want = aid_guard.confirmed_form_verdict(cmd)
    assert want, cmd
    for label, w in (('non-AID', Where(base / 'n', aid=False)), ('p4/block', Where(base / 'a', 4, 'block')),
                     ('p5/block', Where(base / 'b', 5, 'block')), ('p4/log', Where(base / 'c', 4, 'log'))):
        v = w.bash(cmd)
        assert v[0] == 'DENY' and want in v[1], (label, cmd, v)


def test_t15_3_expanded_init_cannot_self_init_a_fresh_folder(base):
    """G1-11 via expansion: `$(echo init) developer 4` must not create .aid/ unasked."""
    cmd = 'python "{}" $(echo init) developer 4'.format(S)
    for label, w in (('non-AID', Where(base / 'n', aid=False)), ('p4/block', Where(base / 'a', 4, 'block'))):
        assert w.bash(cmd)[0] == 'DENY', label
    assert list((base / 'n' / 'proj').iterdir()) == []


@pytest.mark.parametrize('cmd', ['ls *.py', 'python x.py $FILE', 'for f in *.py; do python $f; done',
                                 'python manage.py init', 'git reset --hard', 'echo $HOME'])
def test_t15_3_ordinary_globs_and_variables_stay_allowed_outside_aid(base, cmd):
    assert Where(base, aid=False).bash(cmd) == ('ALLOW', None), cmd


# Review R2-C1 (INV-4): the hook runs in every repo, so these ordinary commands must not be
# read as an aid_session call: no python interpreter runs a run-time-built script there.
@pytest.mark.parametrize('cmd', ['git commit -m "[aid] init project"', "git log --grep='[aid] reset'",
                                 'grep -n "aid_session" hooks/*.py', 'pytest tests/test_[a-z]*.py -k approve',
                                 'python tools/gen_{a,b}.py init',
                                 # Review R3-C2: a literal script name, an option value, a
                                 # subcommand short of its arguments, a heredoc commit message.
                                 'python "$HOME/tools/db.py" init', 'python "$(pwd)/manage.py" reset',
                                 'python ${SCRIPT_DIR}/setup_env.py --mode init',
                                 'python $(which pytest) -k approve', 'python "$VIRTUAL_ENV/bin/pytest" -k reset',
                                 'python3 $SCRIPT jump',
                                 "git commit -m \"$(cat <<'EOF'\naid_session: fix init under python 3.12\nEOF\n)\"",
                                 'node -e "console.log(1)" && grep -n approve hooks/aid_session.py'])
def test_t15_3_ordinary_commands_are_not_session_calls(base, cmd):
    assert aid_guard.session_ask_verdict(cmd) == (None, None), cmd
    for label, w in (('non-AID', Where(base / 'n', aid=False)), ('p4/block', Where(base / 'a', 4, 'block'))):
        assert w.bash(cmd) == ('ALLOW', None), (label, cmd)


# Owner amendment A1, R4-C1: an arithmetic `<<` read as a heredoc start hid every later line
# from the run-time-built check, so the next line ran approve unasked (and created .aid/).
T15_3_ARITH = ['echo $((1<<2))\npython "{s}" $(echo approve)',
               '(( y = 1 << 2 ))\npython "{s}" $(echo approve)',
               'x=$(( (3 << 1) + 1 )); echo $x\npython "{s}" `echo approve`',
               # a heredoc that never finds its delimiter line fails closed
               'cat <<NOPE\npython "{s}" $(echo approve)',
               'cat <<-EOF\n\tEOFX\npython "{s}" $X']


def _four_places(base):
    return (('non-AID', Where(base / 'n', aid=False)), ('p1/log', Where(base / 'a', 1, 'log')),
            ('p4/block', Where(base / 'b', 4, 'block')), ('p5/warn', Where(base / 'c', 5, 'warn')))


@pytest.mark.parametrize('form', T15_3_ARITH)
def test_t15_3_arithmetic_shift_or_open_heredoc_cannot_hide_a_session_call(base, form):
    """
    WHY THIS TEST:
    - PROBLEM: R4-C1 (BLOCKER): `$((1<<2))` / `(( 1 << 2 ))` was lexed as a heredoc whose
      delimiter never came, so the call on the next line was never judged.
    - COST OF FAILURE: the agent changes the AID phase with no prompt, in every folder.
    - SUCCESS: the call is denied in a plain folder and in AID projects at every level.
    """
    cmd = form.format(s=S)
    assert aid_guard.confirmed_form_verdict(cmd), cmd
    for label, w in _four_places(base):
        v = w.bash(cmd)
        assert v[0] == 'DENY', (label, cmd, v)
    assert not (base / 'n' / 'proj' / '.aid').exists()


def test_t15_3_lexer_reads_arithmetic_and_real_heredocs():
    """R4-C1 at the lexer: a shift is a shift, a heredoc body is not a command, and a heredoc
    with no delimiter line is unparsable (None) so the callers fail closed."""
    assert aid_guard._shell_segments('echo $((1<<2))\necho y') == [['echo', '$((1<<2))'], ['echo', 'y']]
    assert aid_guard._shell_segments('(( n = 1 << 3 )); echo $n') == [['((', 'n', '=', '1', '<<', '3', '))'],
                                                                    ['echo', '$n']]
    assert aid_guard._shell_segments('x=$(( (3 << 1) + 1 )); echo $x') == [['x=$(( (3 << 1) + 1 ))'],
                                                                         ['echo', '$x']]
    assert aid_guard._shell_segments('cat <<EOF\npython x approve\nEOF\necho done') == [['cat', '<<EOF'],
                                                                                    ['echo', 'done']]
    assert aid_guard._lex('cat <<EOF\nno end') is None
    assert aid_guard._lex('cat <<EOF') is None


@pytest.mark.parametrize('cmd', ['echo $((1<<2))', '(( n = 1 << 3 )); echo $n', 'echo $(( 8 >> 1 ))',
                                 'cat <<EOF\nhello\nEOF\necho done', 'cat <<EOF > notes.txt\nhello\nEOF',
                                 "python - <<'PY'\nprint(1 << 2)\nPY"])
def test_t15_3_ordinary_shifts_and_heredocs_stay_allowed(base, cmd):
    assert aid_guard.session_ask_verdict(cmd) == (None, None), cmd
    for label, w in (('non-AID', Where(base / 'n', aid=False)), ('p4/block', Where(base / 'a', 4, 'block'))):
        assert w.bash(cmd) == ('ALLOW', None), (label, cmd)


# Owner amendment A1, R4-C3: no new false denials against HEAD 2db6933. The every-folder
# check judges only interpreter script operands (last path component aid_session.py) and
# run-time-built operands in an interpreter's script position; never prose, commit messages,
# echo/printf/grep text or heredoc bodies that only name aid_session. Inside AID the T3/T7
# deny of text naming aid_session with a T3 subcommand stays, exactly as HEAD had it.
# Each row: (tool, command, HEAD verdict outside AID, HEAD verdict at Phase 4 / block),
# measured by running HEAD 2db6933's hook on the same commands.
T15_FALSE_DENIAL_CORPUS = [
    ('Bash', 'git commit -m "aid_session: fix init"', 'ALLOW', 'ALLOW'),
    # T16 B1 (owner amendment, 2026-11-19): T16-14 reverted to 5f8f199: text naming
    # aid_session plus a confirmed word is an accepted false denial at Phase 4 (DENY).
    ('Bash', 'git commit -m "aid_session approve flow"', 'ALLOW', 'DENY'),    # T16 B1
    ('Bash', 'cat <<EOF\nthe aid_session approve step is described here\nEOF', 'ALLOW', 'DENY'),    # T16 B1
    ('Bash', 'grep -n aid_session.py approve docs/', 'ALLOW', 'DENY'),    # T16 B1
    ('Bash', 'echo "run aid_session.py approve to sign off"', 'ALLOW', 'DENY'),    # T16 B1
    ('Bash', 'printf \'%s\\n\' "aid_session.py reset"', 'ALLOW', 'ALLOW'),
    ('Bash', 'git log --oneline --grep "aid_session init"', 'ALLOW', 'DENY'),    # T16 B1
    ('Bash', 'rg "aid_session.py qa-pass" docs', 'ALLOW', 'ALLOW'),
    ('Bash', 'python -m pytest tests/test_aid_session.py -k approve', 'ALLOW', 'DENY'),    # T16 B1
    ('Bash', 'git diff hooks/aid_session.py', 'ALLOW', 'ALLOW'),
    ('Bash', 'cat hooks/aid_session.py | head -n 5', 'ALLOW', 'ALLOW'),
    ('Bash', 'npm test', 'ALLOW', 'ALLOW'),
    ('Bash', 'pytest -k approve tests/', 'ALLOW', 'ALLOW'),
    ('Bash', 'python manage.py migrate', 'ALLOW', 'ALLOW'),
    ('Bash', 'git status', 'ALLOW', 'ALLOW'),
    ('Bash', 'ls -la hooks/', 'ALLOW', 'ALLOW'),
    ('Bash', 'echo $((1<<2))', 'ALLOW', 'ALLOW'),
    ('Bash', '(( n = 1 << 3 )); echo $n', 'ALLOW', 'ALLOW'),
    ('Bash', 'cat <<EOF > notes.txt\nhello\nEOF', 'ALLOW', 'ALLOW'),
    ('Bash', 'node -e "console.log(1)"', 'ALLOW', 'ALLOW'),
    ('Bash', "git commit -m \"$(cat <<'EOF'\naid_session: fix init under python 3.12\nEOF\n)\"", 'ALLOW', 'ALLOW'),
    ('PowerShell', "python (Join-Path $PWD 'manage.py') reset", 'ALLOW', 'ALLOW'),
    ('PowerShell', 'python $env:SCRIPT reset', 'ALLOW', 'ALLOW'),
    ('PowerShell', 'git commit -m "aid_session: fix init"', 'ALLOW', 'DENY'),
    ('PowerShell', 'Get-Content hooks/aid_session.py | Select-String approve', 'ALLOW', 'DENY'),
    ('PowerShell', 'python manage.py migrate', 'ALLOW', 'ALLOW'),
    ('PowerShell', 'npm test', 'ALLOW', 'ALLOW'),
]


@pytest.mark.parametrize('tool,cmd,outside,p4', T15_FALSE_DENIAL_CORPUS)
def test_t15_3_no_new_false_denials_against_head(base, tool, cmd, outside, p4):
    """
    WHY THIS TEST:
    - PROBLEM: R4-C3 (MAJOR): the every-folder gate denied commit messages, heredoc prose,
      grep text and PowerShell `(Join-Path ...)` / `$env:` operands that HEAD allowed.
    - COST OF FAILURE: the hook runs in every repo; false denials block ordinary work.
    - SUCCESS: the same verdict as HEAD 2db6933 outside AID and at Phase 4 / block.
    """
    for label, w, want in (('non-AID', Where(base / 'n', aid=False), outside),
                           ('p4/block', Where(base / 'a', 4, 'block'), p4)):
        v = w.bash(cmd, tool=tool)
        assert v[0] == want, (label, tool, cmd, v)
    assert aid_guard.session_ask_verdict(cmd, powershell=tool == 'PowerShell') == (None, None), cmd


def test_t15_2_the_qa_gate_reason_command_is_asked(base):
    """WS-B request (I-1, I-7): the QA Stop gate tells the agent to run qa-pass; that exact
    command, with the note filled in, must reach the user as an "ask", never a deny/allow."""
    import re
    w = Where(base / 'q', 4)
    (w.P / '.aid' / 'qa').mkdir(parents=True)
    (w.P / '.aid' / 'qa' / 'T-2.yaml').write_text('x: 1\n', encoding='utf-8')
    (w.P / '.aid' / 'context.json').write_text('{"current_task": {"id": "T-2"}}', encoding='utf-8')
    env = dict(os.environ, HOME=str(w.H), USERPROFILE=str(w.H), AID_HOME=str(w.H / '.aid'))
    env.pop('CLAUDE_PROJECT_DIR', None)
    p = subprocess.run([sys.executable, str(REPO / 'hooks' / 'validate-qa-gate.py')],
                       input=json.dumps({'cwd': str(w.P)}), capture_output=True, text=True,
                       cwd=str(w.P), env=env, timeout=60)
    out = json.loads(p.stdout)
    assert out.get('decision') == 'block', p.stdout
    m = re.search(r'python "[^"]+" qa-pass T-2 --note "<short summary>"', out['reason'])
    assert m, out['reason']
    cmd = m.group(0).replace('<short summary>', 'all 3 criteria pass. tests green')
    assert cmd.startswith('python "{}" '.format(S)), cmd
    for label, wh in [('p4', w)] + list(_cases(base / 'c')):
        v = wh.bash(cmd)
        assert v[0] == 'ASK' and 'qa-pass' in v[1], (label, cmd, v)


# --- T15-4 PowerShell ----------------------------------------------------------------

def test_t15_4_powershell_canonical_confirmed_call_is_asked(base):
    for label, w in [('non-AID', Where(base / 'n', aid=False))] + [
            ('p{}/{}'.format(p, lv), Where(base / '{}{}'.format(p, lv), p, lv)) for p in (1, 4) for lv in LEVELS]:
        for sub in ('approve', 'qa-pass T-1', 'reset'):
            v = w.ps('python "{}" {}'.format(S, sub))
            assert v[0] == 'ASK' and 'confirm' in v[1], (label, sub, v)


@pytest.mark.parametrize('cmd', ['python "{s}" review 1 PASS', 'PYTHON "{s}" approve',
                                 'python "{s}" ap`prove', "& python ('aid_sess'+'ion.py') approve",
                                 'python "{s}" approve; Get-Date'])
def test_t15_4_other_powershell_session_calls_keep_t7_4_in_aid(base, cmd):
    for phase in (1, 4, 5):
        for level in ('block', 'log'):
            v = Where(base / '{}{}'.format(phase, level), phase, level).ps(cmd.format(s=S))
            assert v[0] == 'DENY', (phase, level, cmd, v)


def test_t15_4_powershell_outside_aid(base):
    w = Where(base, aid=False)
    for cmd in ('PYTHON "{s}" approve', 'python "{s}" ap`prove', 'python "{s}"  advance',
                "& python ('aid_sess'+'ion.py') approve", 'python "{s}" "reset"'):
        assert w.ps(cmd.format(s=S))[0] == 'DENY', cmd
    for cmd in ('Get-ChildItem', 'python "{s}" review 1 PASS', 'npm test', 'python x.py $args'):
        assert w.ps(cmd.format(s=S)) == ('ALLOW', None), cmd


# Review R2-C3: a subcommand ([char] join, $env:) or a script path (Get-ChildItem wildcard)
# built at run time. In an AID project from Phase 4 the path form does not name aid_session,
# so T7-4 cannot see it; the hook is the only layer for the PowerShell tool.
@pytest.mark.parametrize('cmd', ['python "{s}" $([char]105+\'nit\') developer 4', 'python "{s}" $env:X',
                                 "python (Get-ChildItem '{pq}/hooks/aid_s*.py').FullName qa-pass T-1",
                                 "python (Get-ChildItem '{pq}/hooks/aid_s*.py').FullName jump developer 5"])
def test_t15_4_powershell_run_time_built_calls_are_denied_everywhere(base, cmd):
    cmd = cmd.format(s=S, pq=R.replace("'", "''"))
    for label, w in (('non-AID', Where(base / 'n', aid=False)), ('p1/log', Where(base / 'a', 1, 'log')),
                     ('p4/block', Where(base / 'b', 4, 'block')), ('p5/warn', Where(base / 'c', 5, 'warn'))):
        assert w.ps(cmd)[0] == 'DENY', (label, cmd)


# Review R3-C4: the script path from a Get-ChildItem wildcard (or a variable) run through a
# call operator on Get-Command, Start-Process, a python option, a subcommand variable or a
# parenthesised [char] subcommand. None of them names aid_session, so T7-4 cannot see them.
_PS_GCI = "$s = (Get-ChildItem '{pq}/hooks/aid_s*.py').FullName; "


@pytest.mark.parametrize('cmd', [_PS_GCI + '& (Get-Command python) $s qa-pass T-1',
                                 _PS_GCI + "Start-Process -NoNewWindow -Wait python -ArgumentList $s,'qa-pass','T-1'",
                                 _PS_GCI + '& python.exe -X utf8 $s jump developer 5',
                                 _PS_GCI + "$c = 'qa-' + 'pass'; python $s $c T-1",
                                 _PS_GCI + "python $s ([char]113+'a-pass') T-1",
                                 '$s = $env:S; & (Get-Command python) $s qa-pass T-1',
                                 "$s = $env:S; Start-Process python -ArgumentList $s,'approve'"])
def test_t15_4_powershell_built_script_paths_are_denied_everywhere(base, cmd):
    cmd = cmd.format(pq=R.replace("'", "''"))
    for label, w in (('non-AID', Where(base / 'n', aid=False)), ('p1/log', Where(base / 'a', 1, 'log')),
                     ('p4/block', Where(base / 'b', 4, 'block')), ('p5/warn', Where(base / 'c', 5, 'warn'))):
        assert w.ps(cmd)[0] == 'DENY', (label, cmd)
    assert Where(base / 'd', aid=False).ps('Start-Process notepad -ArgumentList a.txt') == ('ALLOW', None)


# --- T15-5 every installed plugin root ------------------------------------------------

def _fake_root(d, name='aid'):
    (d / 'hooks').mkdir(parents=True, exist_ok=True)
    (d / '.claude-plugin').mkdir(parents=True, exist_ok=True)
    (d / 'hooks' / 'aid_session.py').write_text('print(1)\n', encoding='utf-8')
    (d / '.claude-plugin' / 'plugin.json').write_text(json.dumps({'name': name}), encoding='utf-8')
    return d


def _config_dir(base, project=None):
    """Fake CLAUDE_CONFIG_DIR with a cache copy, a directory marketplace, and decoys."""
    C = base / 'cfg'
    cache = _fake_root(C / 'plugins' / 'cache' / 'M' / 'aid' / '9.9.9')
    _fake_root(C / 'plugins' / 'cache' / 'N' / 'aid' / '1.0.0', name='not-aid')
    dm = _fake_root(base / 'dirmarket')
    inside = _fake_root(project / 'vendor' / 'aid') if project else None
    (C / 'plugins' / 'known_marketplaces.json').write_text(json.dumps({
        'dm': {'source': {'source': 'directory', 'path': str(dm)}, 'installLocation': str(dm)}}),
        encoding='utf-8')
    (C / 'plugins' / 'installed_plugins.json').write_text(json.dumps({'version': 2, 'plugins': {
        'aid@inside': [{'installPath': str(inside or dm)}]}}), encoding='utf-8')
    return C, cache, dm, inside


def _fwd(p):
    return str(p).replace('\\', '/')


def test_t15_5_installed_plugin_roots_follows_i5(base, monkeypatch):
    P = base / 'proj'
    P.mkdir()
    C, cache, dm, inside = _config_dir(base, P)
    monkeypatch.setenv('CLAUDE_CONFIG_DIR', str(C))
    monkeypatch.setenv('HOME', str(base / 'home'))
    monkeypatch.setenv('USERPROFILE', str(base / 'home'))
    roots = aid_guard.installed_plugin_roots(str(P))
    key = lambda p: aid_guard._key(os.path.realpath(str(p))).rstrip('/')   # noqa: E731
    assert roots[0] == key(REPO)
    assert key(cache) in roots and key(dm) in roots
    assert key(inside) not in roots                                   # inside the project
    assert key(C / 'plugins' / 'cache' / 'N' / 'aid' / '1.0.0') not in roots   # name is not aid


@pytest.mark.parametrize('sub', ['start developer 1', 'review 1 PASS', 'roles', 'approve', 'reset'])
def test_t15_5_a_non_live_installed_root_is_asked_for_every_subcommand(base, sub):
    for phase in (0, 1, 4, 5):
        w = Where(base / str(phase), phase)
        C, cache, dm, _ = _config_dir(base / str(phase))
        w.env = {'CLAUDE_CONFIG_DIR': str(C)}
        for root in (cache, dm):
            v = w.bash('python "{}/hooks/aid_session.py" {}'.format(_fwd(root), sub))
            assert v[0] == 'ASK' and 'confirm' in v[1], (phase, root, sub, v)
    w = Where(base / 'n', aid=False)
    C, cache, dm, _ = _config_dir(base / 'n')
    w.env = {'CLAUDE_CONFIG_DIR': str(C)}
    assert w.bash('python "{}/hooks/aid_session.py" {}'.format(_fwd(cache), sub))[0] == 'ASK'


def test_t15_5_lookalike_roots_get_the_existing_rules(base):
    w = Where(base, 1)
    C, cache, dm, inside = _config_dir(base / 'c', w.P)
    w.env = {'CLAUDE_CONFIG_DIR': str(C)}
    look = _fake_root(w.P / 'plugins' / 'cache' / 'x' / 'aid' / '1')
    notaid = C / 'plugins' / 'cache' / 'N' / 'aid' / '1.0.0'
    for root in (inside, look, notaid):
        v = w.bash('python "{}/hooks/aid_session.py" start developer 1'.format(_fwd(root)))
        assert v[0] == 'DENY', (root, v)


def test_t15_5_plugin_registries_are_control_files(base):
    for phase in (0, 4, 5):
        for level in LEVELS:
            w = Where(base / '{}{}'.format(phase, level), phase, level)
            C = base / '{}{}'.format(phase, level) / 'cfg'
            w.env = {'CLAUDE_CONFIG_DIR': str(C)}
            for f in ('known_marketplaces.json', 'installed_plugins.json'):
                for target in (C / 'plugins' / f, w.H / '.claude' / 'plugins' / f):
                    for tool in ('Write', 'Edit'):
                        v = w.write(str(target), tool)
                        assert v[0] == 'DENY' and 'control file' in v[1], (phase, level, target, v)


# --- T15-6 breather installer and init-project.sh --------------------------------------

def _script_forms(root):
    r = _fwd(root)
    b = r.replace('/', '\\')
    return [('node "{}/integrations/breather/install.mjs"'.format(r), 'calendar'),
            ('node "{}\\integrations\\breather\\install.mjs" --snooze=30'.format(b), 'calendar'),
            ('bash "{}/scripts/init-project.sh" t15demo --no-deps --no-git'.format(r), 'new project folder'),
            ('bash "{}\\scripts\\init-project.sh" t15demo'.format(b), 'new project folder')]


def test_t15_6_plugin_scripts_are_asked_in_every_phase_and_folder(base):
    C, cache, _, _ = _config_dir(base / 'c')
    env = {'CLAUDE_CONFIG_DIR': str(C)}
    places = [Where(base / 'n', aid=False)] + [
        Where(base / '{}{}'.format(p, lv), p, lv) for p in (0, 1, 4, 5) for lv in ('block', 'log')]
    for w in places:
        w.env = env
        for root in (REPO, cache):
            for cmd, what in _script_forms(root):
                v = w.bash(cmd)
                assert v[0] == 'ASK' and what in v[1], (w.P, cmd, v)


@pytest.mark.parametrize('form', ['bash ./scripts/init-project.sh t15demo',
                                  'bash "{r}/scripts/init-project.sh" t15demo; echo x',
                                  'bash "{r}/scripts/init-project.sh" t15demo > log.txt',
                                  'bash "{p}/scripts/init-project.sh" t15demo',
                                  'node ./integrations/breather/install.mjs'])
def test_t15_6_other_forms_get_the_existing_rules(base, form):
    w = Where(base, 1)
    cmd = form.format(r=R, p=_fwd(w.P))
    assert w.bash(cmd)[0] == 'DENY', cmd


def test_t15_6_powershell_plugin_scripts_are_asked_in_every_phase_and_folder(base):
    """
    WHY THIS TEST:
    - PROBLEM: docs review NEW-1 (D2): the exact plugin-root breather installer / init-project
      call was asked from the Bash tool only; from the PowerShell tool it was silently allowed
      outside AID and from Phase 4 (or at log/warn), and denied before Phase 4.
    - COST OF FAILURE: hooks land in ~/.claude/settings.json, or a project folder is created,
      without the user being asked, just by choosing the other shell tool.
    - SUCCESS: the exact form (A2), for every installed root, is ASK in every folder, phase
      and level, the same as the Bash tool.
    """
    C, cache, dm, _ = _config_dir(base / 'c')
    env = {'CLAUDE_CONFIG_DIR': str(C)}
    places = [Where(base / 'n', aid=False)] + [
        Where(base / '{}{}'.format(p, lv), p, lv) for p in (0, 1, 4, 5) for lv in LEVELS]
    for w in places:
        w.env = env
        for root in (REPO, cache, dm):
            for cmd, what in _script_forms(root):
                v = w.ps(cmd)
                assert v[0] == 'ASK' and what in v[1], (w.P, root, cmd, v)
    for cmd, _ in _script_forms(REPO):
        assert aid_guard.session_ask_verdict(cmd, powershell=True)[0] == 'ask', cmd


@pytest.mark.parametrize('form,outside,p1,p4', [
    ('node ./integrations/breather/install.mjs', 'ALLOW', 'DENY', 'ALLOW'),
    ('node "{r}/integrations/breather/install.mjs"; Get-Date', 'ALLOW', 'DENY', 'ALLOW'),
    ('bash "{r}/scripts/init-project.sh" t15demo > log.txt', 'ALLOW', 'DENY', 'ALLOW'),
    ('bash "{p}/scripts/init-project.sh" t15demo', 'ALLOW', 'DENY', 'ALLOW'),
    ('git commit -m "breather: fix install.mjs; init-project.sh too"', 'ALLOW', 'DENY', 'ALLOW'),
    ('node "{r}/integrations/breather/install.mjs"; Remove-Item .aid/state.json', 'ALLOW', 'DENY', 'DENY'),
])
def test_t15_6_powershell_other_forms_keep_their_verdict(base, form, outside, p1, p4):
    """A2: only the exact plugin-root form is asked; control files stay denied."""
    for label, w, want in (('non-AID', Where(base / 'n', aid=False), outside),
                           ('p1/block', Where(base / 'a', 1, 'block'), p1),
                           ('p4/block', Where(base / 'b', 4, 'block'), p4)):
        cmd = form.format(r=R, p=_fwd(w.P))
        v = w.ps(cmd)
        assert v[0] == want, (label, cmd, v)


# --- T15-7 QA markers are control files ------------------------------------------------

QA_MARKERS = ['.aid/qa/T-1.qa-passed', '.aid/qa/T-1-review.json', '.aid/qa/T-1-review-2.json',
              '.aid/qa/sub/T-1-REVIEW-1.JSON']


def test_t15_7_qa_markers_refused_to_the_write_tool(base):
    for phase in (0, 4, 5):
        for level in LEVELS:
            w = Where(base / '{}{}'.format(phase, level), phase, level)
            for m in QA_MARKERS:
                v = w.write(m)
                assert v[0] == 'DENY' and 'control file' in v[1], (phase, level, m, v)


@pytest.mark.parametrize('cmd', ['touch .aid/qa/T-1.qa-passed', 'echo x > .aid/qa/T-1-review.json',
                                 'cp a .aid/qa/T-1.qa-passed',
                                 'python -c "open(\'.aid/qa/T-1.qa-passed\',\'w\')"'])
def test_t15_7_qa_markers_refused_to_bash_at_phase_4(base, cmd):
    assert Where(base, 4).bash(cmd)[0] == 'DENY', cmd


def test_t15_7_criteria_reports_and_reads_stay_allowed(base):
    w = Where(base, 4)
    for p in ('.aid/qa/T-1.yaml', '.aid/qa/reports/T-1-report-1.json', '.aid/qa/enforcement.log'):
        assert w.write(p) == ('ALLOW', None), p
    assert w.bash('cat .aid/qa/T-1.qa-passed') == ('ALLOW', None)
    w.state(1)
    for p in ('.aid/qa/T-1.yaml', '.aid/qa/reports/T-1-report-1.json'):
        assert w.write(p) == ('ALLOW', None), p
    assert w.write('.aid/qa/T-1.qa-passed')[0] == 'DENY'


# --- T15-8 the ASK set --------------------------------------------------------------

I1 = ('approve', 'advance', 'jump', 'init', 'memory-sync', 'memory-apply', 'reset', 'qa-pass')


def test_t15_8_ask_set_equals_i1():
    assert aid_guard.CONFIRMED_SUBCOMMANDS == I1
    want = tuple('Bash({} *aid_session.py {}*)'.format(i, s) for s in I1 for i in ('python', 'python3', 'py'))
    assert aid_guard.ASK_RULES == want and len(want) == 24


def test_t15_8_existing_project_gets_the_six_new_rules_additively(base):
    w = Where(base, 1)
    old = [r for r in aid_guard.ASK_RULES if ' reset' not in r and ' qa-pass' not in r]
    assert len(old) == 18
    s = w.P / '.claude' / 'settings.json'
    s.write_bytes(b'\xff\xfe' + json.dumps({'permissions': {'deny': list(aid_guard.DENY_RULES),
                                                            'ask': old + ['Bash(user own *)']}}).encode('utf-16-le'))
    ctx = w.session_start('s1')['hookSpecificOutput']['additionalContext']
    assert 'added 6 permission rules' in ctx, ctx
    raw = s.read_bytes()
    assert raw.startswith(b'\xff\xfe')                                  # encoding kept (AC-44)
    data = json.loads(raw[2:].decode('utf-16-le'))
    assert data['permissions']['ask'][:19] == old + ['Bash(user own *)']
    assert set(aid_guard.ASK_RULES) <= set(data['permissions']['ask'])
    assert 'AID added' not in w.session_start('s2')['hookSpecificOutput']['additionalContext']   # idempotent
    payload = {'session_id': 's2', 'cwd': str(w.P), 'tool_name': 'Bash', 'tool_input': {'command': 'ls'}}
    assert decision(run('phase-gate-bash', w.P, w.H, payload)) == ('ALLOW', None)
    data['permissions']['ask'].remove('Bash(py *aid_session.py qa-pass*)')
    s.write_bytes(b'\xff\xfe' + json.dumps(data).encode('utf-16-le'))
    v = decision(run('phase-gate-bash', w.P, w.H, payload))
    assert v[0] == 'DENY' and 'removed' in v[1], v


# --- T15-9 phase range 0-5 -----------------------------------------------------------

@pytest.mark.parametrize('phase', [99, 6, -1, True, '7'])
def test_t15_9_out_of_range_phase_fails_closed(base, phase):
    w = Where(base, 1)
    w.state(phase)
    assert w.write('src/x.ts')[0] == 'DENY'
    assert w.bash('npm test')[0] == 'DENY'


def test_t15_9_phase_5_still_allows(base):
    w = Where(base, 5)
    assert w.write('src/x.ts') == ('ALLOW', None)
    assert w.bash('npm test') == ('ALLOW', None)


# --- T15-10 Phase 4 literal list ------------------------------------------------------

def test_t15_10_phase_4_state_json_literal(base):
    w = Where(base, 4)
    assert w.bash('python -c "open(\'.aid/state.json\',\'w\')"')[0] == 'DENY'
    assert w.bash('cat .aid/state.json') == ('ALLOW', None)
    assert w.bash('python "{}" start developer 4'.format(S)) == ('ALLOW', None)


# --- T15-11 SessionStart names every non-block gate ----------------------------------

def test_t15_11_session_start_names_lowered_gates_every_time(base):
    w = Where(base, 1)
    (w.P / '.aid' / 'hooks' / 'config.json').write_text(json.dumps(
        {'enforcement': {'phase_gate_write': 'block', 'phase_gate_bash': 'log'}}), encoding='utf-8')
    for sid in ('s1', 's2'):                                  # unchanged since the last session
        out = w.session_start(sid)
        ctx = out['hookSpecificOutput']['additionalContext']
        assert 'phase_gate_bash: log' in out.get('systemMessage', ''), out
        assert 'phase_gate_bash: log' in ctx and 'phase_gate_write: block' not in ctx, ctx
    w.level('warn')
    out = w.session_start('s3')
    for g in ('phase_gate_write: warn', 'phase_gate_bash: warn'):
        assert g in out['systemMessage'] and g in out['hookSpecificOutput']['additionalContext']


def test_t15_11_no_notice_at_block_or_outside_aid(base):
    out = Where(base / 'a', 1).session_start()
    assert 'systemMessage' not in out and 'below block' not in out['hookSpecificOutput']['additionalContext']
    out = Where(base / 'n', aid=False).session_start()
    assert 'systemMessage' not in out
    assert 'below block' not in json.dumps(out)
