"""
Tests for hooks/aid_guard.py -- the v2 phase-gate decision logic (T1, round 4).

WHY THIS TEST:
- PROBLEM: three review rounds beat every Bash text-parsing defence of allow-listed tools
  that can write or run code. Round 4 denies those tools outright before Phase 4 and keeps
  only a flat grammar of read-only commands (T1-acceptance.md).
- COST OF FAILURE: code runs before Phase 4, the agent disables its own gates (bypass), or
  ordinary Phase 0-3 work is blocked (false denial).
- SUCCESS: every acceptance criterion (test_ac_<id>_*) holds when the REAL hook is spawned
  with stdin JSON the way Claude Code runs it; the older direct-function lists still hold.
"""
import hashlib
import itertools
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(REPO_ROOT, 'hooks'))
import aid_guard as g  # noqa: E402

HOOK = os.path.join(REPO_ROOT, 'hooks', 'aid_hooks.py')
RULES = {'code_execute_min_phase': 4, 'code_write_min_phase': 4,
         'allowed_write_prefixes': ['docs/', '.aid/', '.claude/', 'features/', 'testing/', 'tests/']}
WIN = os.name == 'nt'
OWNER = '# owner decision 2026-11-16: deny outright before Phase 4'


@pytest.fixture
def root(tmp_path):
    (tmp_path / '.aid' / 'hooks').mkdir(parents=True)
    (tmp_path / '.claude').mkdir()
    (tmp_path / 'docs').mkdir()
    return str(tmp_path)


# Code execution before Phase 4 -- every one of these ran code past the v1 gate.
RUNNER_BYPASSES = [
    'node x.js', 'git status && node x.js', "bash -c 'node x.js'", "echo 'node x.js' | bash",
    'echo bm9kZSB4Lmpz | base64 -d | sh', 'bash docs/run.sh', 'source docs/run.sh', '. docs/run.sh',
    'find . -maxdepth 0 -exec node x.js \\;', "git -c alias.r='!node x.js' r", 'env -u FOO node x.js',
    'exec -a foo node x.js', 'timeout -s KILL 5 node x.js', "$'node' x.js", 'N=node; $N x.js',
    '/usr/bin/nod? x.js', 'coproc node x.js', "trap 'node x.js' EXIT",
    "cat <<EOF\n'\nEOF\nnode x.js\n#'", 'cat <<EOF\n$(node x.js)\nEOF',
    "awk 'BEGIN{system(\"node x.js\")}'", "perl -e 'system(1)'", 'pytest', 'python -m pytest',
    'pnpm dev', 'yarn dev', 'pnpx vite', 'npm restart', 'npm run dev', 'npx vite', 'ruby x.rb',
    'go run .', 'make dev', 'cmd /c node x.js', 'powershell -Command "node x.js"', 'start node x.js',
    'nodemon x.js', "GIT_PAGER='node x' git log", "NODE_OPTIONS='--require ./x.js' npm ls",
    './docs/git status', "sed 's/x/node x.js/e' f", 'sort --compress-program=node f',
    'git grep -Onode x', 'git clone -u node x y', 'git push --receive-pack=node', 'python x.py',
    'py -3 x.py', 'node -e 1', 'echo $(node x.js)', 'echo "`node x.js`"', 'git config core.pager node',
    'python hooks/aid_session.py start dev 1',     # the PROJECT's copy, not the plugin's
]

# Writes before Phase 4 into source, .git, or AID control files.
WRITE_BYPASSES = [
    'echo {} > .claude/settings.json', 'echo {} >| .claude/settings.json',
    'cd .claude && echo {} > settings.json', 'f=.claude/settings.json; echo {} > $f',
    'echo {} > .claude/setting?.json', 'echo {} > "$PWD/.claude/settings.json"',
    'cp docs/settings.json .claude/', 'cp docs/settings.json .claude', 'mv docs/settings.local.json .claude',
    'mv .claude .claude-off', 'rm -rf .claude', 'rm -rf .aid', 'dd if=x of=.claude/settings.json',
    'curl -o .claude/settings.json http://example.invalid/x', 'git checkout -- .claude/settings.json',
    'sort -o .claude/settings.json docs/x', 'tee .claude/settings.json < docs/x',
    'echo {} | tee .CLAUDE/Settings.json', 'echo {} > ".claude\\settings.json"',
    'echo x > .aid/hooks/config.json', "sed -i 's/block/log/' .aid/hooks/config.json",
    "cat > src/app.ts <<'EOF'\nx\nEOF", 'cp docs/a.ts src/', 'cp docs/x .git/hooks/pre-commit',
    'touch src/new.ts', 'mkdir src/x', 'echo x > ~/proj/notes.md',
]

# Ordinary Phase 0-3 commands that must keep working.
LEGIT = [
    'git status', 'ls -la', 'grep -rn python .', 'grep -rn "node " docs', 'node --version',
    'mkdir -p docs/a', 'head -n 5 README.md',
    "git commit -m \"$(cat <<'EOF'\nAdd docs\n\nPython 3.12 is now required. Don't panic (really).\nEOF\n)\"",
    'cat .claude/settings.json', 'git --no-pager log -1', 'wc -l src/app.js', 'ls 2>&1',
    'ls > /dev/null', 'git commit -m "fix .claude/settings.json handling"',
    'cat .aid/hooks/config.json', 'echo hi', 'git diff HEAD~1 -- src/',
    'git add docs/ && git commit -m docs',
]
# Former LEGIT entries this contract now denies (AC-52).
LEGIT_FLIPPED = [  # owner decision 2026-11-16: deny outright before Phase 4
    'npm install', 'npm install x', 'npm uninstall t', 'npm help run', 'pip install requests',
    'python -m pip install requests', 'py -m pip install requests',
    "cat > docs/notes.md <<'EOF'\n# Notes\nnode is the runtime we use.\nEOF",
    "cat > docs/notes.md <<'EOF'\nDon't stop\nnode x.js\nEOF",
    'sed -n 1p .claude/settings.json', 'sed -n "/deny/p" .claude/settings.json',
    'cp .claude/settings.json docs/settings.backup.json', "echo '> .claude/settings.json' >> docs/notes.md",
    '[ -d docs ] && echo yes', '[[ -f x ]]', 'if [ -d docs ]; then ls docs; fi',
    'for f in docs/*.md; do wc -l "$f"; done', 'command -v node', "find . -name '*.md' | xargs grep -l x",
    "gh pr create --title t --body \"$(cat <<'EOF'\nbody\nEOF\n)\"", 'gh pr view 3',
    "cd docs && cat > notes.md <<'EOF'\nx\nEOF", 'git -C docs status', 'rg -n foo', 'test -f x',
    'set -euo pipefail', 'git config --get user.name',
]


@pytest.mark.parametrize('command', RUNNER_BYPASSES)
def test_runner_bypass_is_refused_before_phase_4(root, command):
    assert g.evaluate_bash(command, root, root, 1, RULES), f'{command!r} runs code before Phase 4'


@pytest.mark.parametrize('command', WRITE_BYPASSES)
def test_write_bypass_is_refused_before_phase_4(root, command):
    assert g.evaluate_bash(command, root, root, 1, RULES), f'{command!r} writes where it must not'


@pytest.mark.parametrize('command', LEGIT)
def test_ordinary_command_is_allowed_before_phase_4(root, command):
    assert g.evaluate_bash(command, root, root, 1, RULES) is None, (
        f'{command!r} is ordinary Phase 0-3 work: {g.evaluate_bash(command, root, root, 1, RULES)}')


@pytest.mark.parametrize('command', LEGIT_FLIPPED)
def test_flipped_former_allow_is_denied_before_phase_4(root, command):
    assert g.evaluate_bash(command, root, root, 1, RULES), command


@pytest.mark.parametrize('command', [
    'echo {} > .claude/settings.json', 'rm -rf .claude', 'cp docs/settings.json .claude/',
    "python -c \"open('.claude/settings.json','w').write('{}')\"",
    "node -e \"require('fs').writeFileSync('.aid/hooks/config.json','{}')\"",
    "sed -i 's/block/log/' .aid/hooks/config.json", 'git checkout -- .claude/settings.json',
])
def test_control_files_stay_protected_in_phase_5(root, command):
    assert g.evaluate_bash(command, root, root, 5, RULES)


@pytest.mark.parametrize('command', ['node x.js', 'npm run dev', 'python x.py && pytest',
                                     'cat > src/app.ts <<EOF\nx\nEOF', 'make dev'])
def test_phase_5_runs_code_freely(root, command):
    assert g.evaluate_bash(command, root, root, 5, RULES) is None


def test_extra_allowed_commands_extend_the_list(root):
    assert g.evaluate_bash('make lint', root, root, 1, RULES)
    assert g.evaluate_bash('make lint', root, root, 1, RULES, [['make', 'lint']]) is None
    assert g.evaluate_bash('make dev', root, root, 1, RULES, [['make', 'lint']])


@pytest.mark.parametrize('suffix', ['settings.json::$DATA', 'settings.json.', 'settings.json ',
                                    'SETTINGS.JSON'])
@pytest.mark.skipif(not WIN, reason='Windows path forms')
def test_windows_write_tool_path_forms_are_protected(root, suffix):
    path = os.path.join(root, '.claude', suffix)
    assert g.write_target_verdict(path, root, root, 5, RULES, literal=True)
    assert g.write_target_verdict('\\\\?\\' + os.path.join(root, '.claude', 'settings.json'),
                                  root, root, 5, RULES, literal=True)


def test_write_tool_allows_docs_and_plans(root, tmp_path, monkeypatch):
    home = tmp_path / 'home'
    monkeypatch.setenv('CLAUDE_CONFIG_DIR', str(home / '.claude'))
    assert g.write_target_verdict(os.path.join(root, 'docs', 'spec.md'), root, root, 1, RULES, literal=True) is None
    assert g.write_target_verdict(str(home / '.claude' / 'plans' / 'p.md'), root, root, 1, RULES, literal=True) is None
    assert g.write_target_verdict(os.path.join(root, 'src', 'a.ts'), root, root, 1, RULES, literal=True)
    assert g.write_target_verdict(os.path.join(root, 'docs', '..', 'src', 'a.ts'), root, root, 1, RULES, literal=True)


# ---------------------------------------------------------------------------
# Layers A and B, driven through the real hook (AC-41 regressions)
# ---------------------------------------------------------------------------

def _hook(project, event, action, payload, home):
    env = dict(os.environ, HOME=str(home), USERPROFILE=str(home), AID_HOME=str(home / '.aid'))
    env.pop('CLAUDE_PROJECT_DIR', None)
    env.pop('CLAUDE_CONFIG_DIR', None)
    args = [sys.executable, HOOK, '--event', event] + (['--action', action] if action else [])
    p = subprocess.run(args, input=json.dumps(payload), capture_output=True, text=True,
                       cwd=str(project), env=env, timeout=60)
    assert p.returncode == 0, p.stderr[-400:]
    return p.stdout


def _block_project(tmp_path, phase=1):
    proj = tmp_path / 'proj'
    (proj / '.aid' / 'hooks').mkdir(parents=True)
    (proj / '.aid' / 'state.json').write_text(json.dumps({'current_phase': phase}), encoding='utf-8')
    (proj / '.aid' / 'hooks' / 'config.json').write_text(json.dumps(
        {'enforcement': {'phase_gate_write': 'block', 'phase_gate_bash': 'block'}}), encoding='utf-8')
    return proj


def test_session_start_installs_deny_rules_additively(tmp_path):
    proj = _block_project(tmp_path)
    (proj / '.claude').mkdir()
    (proj / '.claude' / 'settings.json').write_text(json.dumps(
        {'permissions': {'deny': ['Read(./.env)']}, 'model': 'x'}), encoding='utf-8')
    _hook(proj, 'SessionStart', None, {'source': 'startup', 'session_id': 's1', 'cwd': str(proj)}, tmp_path / 'h')
    data = json.loads((proj / '.claude' / 'settings.json').read_text(encoding='utf-8'))
    assert 'Read(./.env)' in data['permissions']['deny'] and data['model'] == 'x'
    assert all(r in data['permissions']['deny'] for r in g.DENY_RULES)


def test_ac_41_config_changed_mid_session_fails_closed(tmp_path):
    proj, home = _block_project(tmp_path, phase=5), tmp_path / 'h'
    _hook(proj, 'SessionStart', None, {'source': 'startup', 'session_id': 's1', 'cwd': str(proj)}, home)
    ok = {'tool_name': 'Bash', 'tool_input': {'command': 'ls'}, 'session_id': 's1', 'cwd': str(proj)}
    assert '"deny"' not in _hook(proj, 'PreToolUse', 'phase_gate_bash', ok, home)
    # The agent (e.g. via python in Phase 5) switches its gates to log:
    (proj / '.aid' / 'hooks' / 'config.json').write_text(json.dumps(
        {'enforcement': {'phase_gate_write': 'log', 'phase_gate_bash': 'log'}}), encoding='utf-8')
    assert '"deny"' in _hook(proj, 'PreToolUse', 'phase_gate_bash', ok, home)
    # A NEW session (human restarted Claude Code) accepts the change.
    _hook(proj, 'SessionStart', None, {'source': 'startup', 'session_id': 's2', 'cwd': str(proj)}, home)
    assert '"deny"' not in _hook(proj, 'PreToolUse', 'phase_gate_bash', dict(ok, session_id='s2'), home)


def test_ac_41_removed_deny_rules_fail_closed(tmp_path):
    proj, home = _block_project(tmp_path, phase=5), tmp_path / 'h'
    _hook(proj, 'SessionStart', None, {'source': 'startup', 'session_id': 's1', 'cwd': str(proj)}, home)
    (proj / '.claude' / 'settings.json').write_text('{}', encoding='utf-8')
    ok = {'tool_name': 'Bash', 'tool_input': {'command': 'ls'}, 'session_id': 's1', 'cwd': str(proj)}
    assert '"deny"' in _hook(proj, 'PreToolUse', 'phase_gate_bash', ok, home)


def test_ac_41_compact_keeps_the_baseline(tmp_path):
    proj, home = _block_project(tmp_path, phase=5), tmp_path / 'h'
    _hook(proj, 'SessionStart', None, {'source': 'startup', 'session_id': 's1', 'cwd': str(proj)}, home)
    (proj / '.aid' / 'hooks' / 'config.json').write_text('{}', encoding='utf-8')
    _hook(proj, 'SessionStart', None, {'source': 'compact', 'session_id': 's1', 'cwd': str(proj)}, home)
    ok = {'tool_name': 'Bash', 'tool_input': {'command': 'ls'}, 'session_id': 's1', 'cwd': str(proj)}
    assert '"deny"' in _hook(proj, 'PreToolUse', 'phase_gate_bash', ok, home)


def test_gate_applies_from_a_subfolder(tmp_path):
    """Design review MAJOR 4: `cd src` used to make the gate lose the project."""
    proj, home = _block_project(tmp_path), tmp_path / 'h'
    (proj / 'src').mkdir()
    payload = {'tool_name': 'Bash', 'tool_input': {'command': 'node x.js'}, 'cwd': str(proj / 'src')}
    assert '"deny"' in _hook(proj / 'src', 'PreToolUse', 'phase_gate_bash', payload, home)


# ---------------------------------------------------------------------------
# T1 review round 2: bypasses and false denials found by the second adversarial review
# ---------------------------------------------------------------------------

@pytest.fixture
def root2(tmp_path):
    for d in ('.aid/hooks', '.claude', 'docs/fake', 'docs/fakeaid', 'src'):
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    (tmp_path / 'src' / 'app.js').write_text('x', encoding='utf-8')
    return str(tmp_path)


R2_DENY_ALL_PHASES = [
    'uniq docs/in.txt .claude/settings.json', 'git log -1 --output=.claude/settings.json',
    'cp --target-directory=.claude docs/settings.json', 'cp -t.claude docs/settings.json',
    'cp -r docs/fake/. .claude/', 'cp -rT docs/fakeaid .aid', 'cp -l .claude/settings.json docs/s.json',
    'cd .claude && (cd ../docs) ; echo {} > settings.json',
    'cd .claude; cd ../docs/nope 2>/dev/null; echo {} > settings.json',
    'git -C .claude/x mv -f ../../docs/s.json ../settings.json',
    'cd; echo {} > .claude/settings.json',
]
R2_DENY_PRE4 = [
    'HOME=docs/h; git status', 'PATH=docs:$PATH; ls', 'set -a; GIT_CONFIG_COUNT=1; git status',
    "PS4='$(touch x)'; set -x; ls", 'npm --userconfig ls run evil', 'npm --loglevel x run evil',
    'echo x | xargs --process-slot-var echo node evil.js', 'xargs rg --pre prog pat',
    'git clone --config core.fsmonitor=x . docs/c', "printf -v 'a[$(touch x)]' x",
    "read 'a[$(touch x)]' <<< x", "[ -v 'a[$(touch x)]' ]", 'cat <<\\EOF\nEOF\ntouch MARK\n\\EOF',
    'git checkout feature -- src/app.js', 'git restore --source=HEAD src/app.js',
    'git worktree add ../outside', 'git clean -fdx', 'gh api repos/o/r/issues -ftitle=x',
    'gh api repos/o/r/issues --field=title=x', 'gh api x -XPOST', 'export PATH=docs:$PATH',
    'git diff --output=src/out.txt',
]
# Former R2_ALLOW_PRE4 entries this contract now denies (AC-52).
R2_FLIPPED = [  # owner decision 2026-11-16: deny outright before Phase 4
    'echo $((1+2))', 'for ((i=0;i<3;i++)); do echo $i; done',
    'case x in a) echo a;; *) echo other;; esac', 'case $f in *.md|*.txt) echo doc;; esac',
    'export FOO=1', 'ls | xargs --max-args 1 grep foo', "printf '%s\\n' x", "echo $'\\t'",
    'git clean -n', 'git restore docs/x.md', 'git checkout main', 'declare -a arr',
    'read -r line <<< x', '[ -d docs ]', 'uniq docs/a.txt', '(cd docs && ls) && ls',
    'npm install --save-dev x', 'npm i -D x', 'pip install -U requests',
]


@pytest.mark.parametrize('phase', [1, 5])
@pytest.mark.parametrize('command', R2_DENY_ALL_PHASES)
def test_r2_control_file_bypass_refused_every_phase(root2, command, phase):
    assert g.evaluate_bash(command, root2, root2, phase, RULES), f'{command!r} (phase {phase})'


@pytest.mark.parametrize('command', R2_DENY_PRE4 + R2_FLIPPED)
def test_r2_code_or_write_bypass_refused_before_phase_4(root2, command):
    assert g.evaluate_bash(command, root2, root2, 1, RULES), command


def test_r2_local_pip_shadow_refused(root2):
    open(os.path.join(root2, 'docs', 'pip.py'), 'w').close()
    assert g.evaluate_bash('cd docs && python -m pip --version', root2, root2, 1, RULES)


# ===========================================================================
# T1 acceptance criteria (T1-acceptance.md), executed through the REAL hook
# ===========================================================================

BLOCK = {'enforcement': {'phase_gate_write': 'block', 'phase_gate_bash': 'block'}}
_SID = itertools.count()


def _marker_above(p):
    return any((d / '.aid' / 'state.json').is_file() or (d / '.aid' / 'hooks' / 'config.json').is_file()
               for d in [p] + list(p.parents))


def clean_base(tmp):
    """
    A directory with no AID project marker on its ancestor path (common harness). On a
    machine whose real ~/.aid/state.json sits above the temp dir, fall back to a fresh
    directory at the drive root. Returns (base, dir_to_remove_or_None).
    """
    tmp = Path(tmp)
    if not _marker_above(tmp):
        return tmp, None
    alt = Path(tempfile.mkdtemp(prefix='aid-t1-', dir=tmp.anchor))
    if _marker_above(alt):
        shutil.rmtree(alt, ignore_errors=True)
        pytest.skip('no directory without an AID marker ancestor is available')
    return alt, alt


def _project(p):
    for d in ('.aid/hooks', '.claude', 'docs'):
        (p / d).mkdir(parents=True, exist_ok=True)
    subprocess.run(['git', 'init', '-q', str(p)], check=True, capture_output=True)
    (p / '.claude' / 'settings.json').write_text('{}', encoding='utf-8')
    return p


@pytest.fixture(scope='module')
def world(tmp_path_factory):
    base, cleanup = clean_base(tmp_path_factory.mktemp('t1ac'))
    h = base / 'home'
    h.mkdir()
    w = SimpleNamespace(P=_project(base / 'proj'), P2=_project(base / "ilan's local files" / 'proj'), H=h)
    yield w
    if cleanup:
        shutil.rmtree(cleanup, ignore_errors=True)


def run_hook(proj, home, action, payload, env=None):
    """Spawn hooks/aid_hooks.py exactly as Claude Code does. Returns (verdict, reason, json)."""
    full = dict(os.environ, HOME=str(home), USERPROFILE=str(home), AID_HOME=str(Path(home) / '.aid'))
    full.pop('CLAUDE_PROJECT_DIR', None)
    full.pop('CLAUDE_CONFIG_DIR', None)
    full.update(env or {})
    p = subprocess.run([sys.executable, HOOK, '--event', 'PreToolUse', '--action', action],
                       input=json.dumps(payload), capture_output=True, text=True,
                       cwd=str(proj), env=full, timeout=60)
    assert p.returncode == 0, p.stderr[-400:]
    out = p.stdout.strip()
    if not out:
        return 'ALLOW', None, None
    d = json.loads(out)
    hso = d.get('hookSpecificOutput', {})
    if hso.get('permissionDecision') == 'deny':
        assert hso.get('hookEventName') == 'PreToolUse' and hso.get('permissionDecisionReason'), d
        return 'DENY', hso['permissionDecisionReason'], d
    return 'ALLOW', None, d


def _setup(proj, phase, config):
    (proj / '.aid' / 'state.json').write_text(json.dumps({'current_phase': phase}), encoding='utf-8')
    (proj / '.aid' / 'hooks' / 'config.json').write_text(json.dumps(config), encoding='utf-8')


def bash(w, cmd, phase=1, proj=None, cwd=None, config=BLOCK, env=None):
    proj = proj or w.P
    _setup(proj, phase, config)
    # A fresh session id per call: each call gets its own layer-B baseline, so tests that
    # change the config do not trip the integrity check of another test.
    payload = {'session_id': 's{}'.format(next(_SID)), 'cwd': str(cwd or proj),
               'tool_name': 'Bash', 'tool_input': {'command': cmd}}
    return run_hook(proj, w.H, 'phase_gate_bash', payload, env)


def write(w, path, phase=1, proj=None, env=None, cwd=None):
    proj = proj or w.P
    _setup(proj, phase, BLOCK)
    payload = {'session_id': 's{}'.format(next(_SID)), 'cwd': str(cwd or proj),
               'tool_name': 'Write', 'tool_input': {'file_path': str(path)}}
    return run_hook(proj, w.H, 'phase_gate_write', payload, env)


def assert_deny(w, cmd, **kw):
    v = bash(w, cmd, **kw)
    assert v[0] == 'DENY', '{!r} must be denied (phase {})'.format(cmd, kw.get('phase', 1))
    # A deny from the fail-closed crash path would hide a broken gate.
    assert 'could not evaluate' not in v[1], v[1]
    return v[1]


def assert_allow(w, cmd, **kw):
    v = bash(w, cmd, **kw)
    assert v[0] == 'ALLOW', '{!r} must be allowed: {}'.format(cmd, v[1])


# --- A. Grammar -------------------------------------------------------------

AC1_DENY = ["x='a[$(touch pw)]'; (( x ))", "x='a[$(touch pwned_dbl)]'; [[ $x -eq 1 ]]",
            "x='$(touch pwned_P)'; echo ${x@P}", 'echo "$HOME"', 'ls $(pwd)', 'ls `pwd`',
            "$'ls'", 'echo $((1+1))', 'grep "foo$" docs/a.md']
AC2_DENY = ['read -r PATH < docs/p; ls', 'declare -n x=PATH; x=docs:/usr/bin; ls',
            'PATH=docs:/usr/bin ls', 'x=1', "printf -v PATH '%s' docs", 'export PATH=docs']
AC3_DENY = ['case a in a) (./docs/evil.sh) ;; esac', '(ls)', '{ ls; }', 'ls &',
            'for f in docs/*; do cat $f; done', 'if true; then ls; fi', 'f() { ls; }; f',
            'diff <(ls) docs/a', 'cat docs/{a,b}.md', 'ls x{,y}']
AC3_ALLOW = ["git log --format='%h {x}' -3", 'echo "{}"']
AC4_DENY = ['echo {} > .claude/settings.json', 'echo x > docs/a.md', 'echo x >> docs/a.md',
            "cat > docs/notes.md <<'EOF'\nnotes\nEOF", 'grep x < docs/a', 'echo x >| docs/a',
            "cat <<EOF\n'\nEOF\nnode x.js\n#'", 'echo x > nul', 'echo x >nul']
AC4_ALLOW = ['git status 2>&1', 'ls docs 2>/dev/null']
AC5_DENY = ['./docs/evil.sh', '/usr/bin/ls', '"ls"', 'l\\s', 'cat docs\\a.md', '/usr/bin/nod? x.js']
AC6_ALLOW = ['git status && git log --oneline -5', 'cat docs/a.md | grep foo | head -5', 'ls; pwd', 'ls\npwd']
AC15_DENY = ["echo 'a\\'; touch pw; echo '\\'", 'echo "\\\\"; touch pw; echo "\\\\"',
             'echo "\\"; touch pw; \\""', "echo 'it'\"'\"'s'; touch pw", 'echo "unterminated; touch pw',
             'ls\r\npwd',
             # bash reads \" as a quote char and runs touch (measured, Git Bash); a gate that
             # closed the string at \" would see touch inside quotes and allow it
             'echo "\\" A "; touch pw; " #"']
AC15_ALLOW = ["echo 'a\\'", 'echo "a\\\\b"', "grep -n 'x\"y' docs/a.md", 'echo "it\'s"']


@pytest.mark.parametrize('cmd', AC1_DENY)
def test_ac_1_expansions_denied(world, cmd):
    assert_deny(world, cmd)


def test_ac_1_dollar_in_double_quotes_names_single_quotes(world):
    assert 'single quotes' in assert_deny(world, 'grep "foo$" docs/a.md')
    assert_allow(world, "grep -n 'foo$' docs/a.md")


@pytest.mark.parametrize('cmd', AC2_DENY)
def test_ac_2_assignments_and_variable_builtins_denied(world, cmd):
    assert_deny(world, cmd)


@pytest.mark.parametrize('cmd', AC3_DENY)
def test_ac_3_compound_syntax_and_braces_denied(world, cmd):
    assert_deny(world, cmd)


@pytest.mark.parametrize('cmd', AC3_ALLOW)
def test_ac_3_quoted_braces_allowed(world, cmd):
    assert_allow(world, cmd)


@pytest.mark.parametrize('cmd', AC4_DENY)
def test_ac_4_redirections_denied(world, cmd):
    assert_deny(world, cmd)


@pytest.mark.parametrize('cmd', AC4_ALLOW)
def test_ac_4_devnull_and_2to1_allowed(world, cmd):
    assert_allow(world, cmd)


@pytest.mark.parametrize('cmd', AC5_DENY)
def test_ac_5_command_word_must_be_plain(world, cmd):
    assert_deny(world, cmd)


@pytest.mark.parametrize('cmd', AC6_ALLOW)
def test_ac_6_lists_and_pipelines_allowed(world, cmd):
    assert_allow(world, cmd)


@pytest.mark.parametrize('cmd', AC15_DENY)
def test_ac_15_quote_confusion_denied(world, cmd):
    assert_deny(world, cmd)


@pytest.mark.parametrize('cmd', AC15_ALLOW)
def test_ac_15_quoting_allowed(world, cmd):
    assert_allow(world, cmd)


# --- B. Command table ---------------------------------------------------------

AC7_ALLOW = ['ls -la', 'ls docs/*.md', 'cat .claude/settings.json', 'grep -rn python .',
             'head -n 20 docs/a.md', 'wc -l docs/*.md', 'diff docs/a docs/b', 'jq . .aid/state.json',
             'echo hello', 'which node']
AC8_DENY = ['cp docs/a docs/b', 'mv docs/a docs/b', 'rm docs/a', 'touch docs/a', 'tee docs/a',
            'sed -n 1p docs/a', 'sort docs/a', 'uniq docs/a', 'find docs', 'xargs cat', 'rg foo',
            'tree', 'file docs/a', 'date', 'ln -s a b', 'dd if=a of=b', 'curl -o x u',
            'test -f a', '[ -f a ]', 'env ls', 'timeout 5 ls', 'nice ls', 'nohup ls', 'command ls',
            'exec ls', 'bash -c ls', 'sh docs/x.sh', 'awk 1 docs/a', 'perl -e 1',
            'npm install', 'npm ci', 'npm install x', 'npm uninstall t', 'npm help run', 'npx vite',
            'pnpm install', 'yarn', 'pip install requests', 'python -m pip install requests',
            'py -m pip install requests', 'python x.py', 'node x.js', 'make dev', 'go run .',
            'pytest', 'cd docs', 'pushd docs']
AC9_DENY = ['cp --target=.claude docs/settings.json', 'mv --targ=.claude docs/settings.local.json',
            'sort --out=.claude/settings.local.json docs/x', 'sort --compress-prog=docs/x.sh docs/a',
            'sed -n --in-pl 1p .claude/settings.json', 'cp -b --suffix=.local.json docs/x .claude/settings',
            'tee .claude/settings.local.js{on,}',
            "printf '%s\\n' . -maxdepth 0 -exec touch pwned_xargs ';' | xargs find",
            'echo -o .claude/settings.local.json docs/x | xargs sort']


@pytest.mark.parametrize('cmd', AC7_ALLOW)
def test_ac_7_read_only_table_allowed(world, cmd):
    assert_allow(world, cmd)


@pytest.mark.parametrize('cmd', AC8_DENY)
def test_ac_8_everything_else_denied(world, cmd):
    assert_deny(world, cmd)


@pytest.mark.parametrize('cmd', AC9_DENY)
def test_ac_9_option_spelling_and_stdin_siblings_denied(world, cmd):
    assert_deny(world, cmd)


@pytest.mark.parametrize('cmd', ['node --version', 'python --version', 'git --version'])
def test_ac_10_version_probe_allowed(world, cmd):
    assert_allow(world, cmd)


@pytest.mark.parametrize('cmd', ['node --version x.js', 'node -e 1', 'python -c 1'])
def test_ac_10_other_runner_forms_denied(world, cmd):
    assert_deny(world, cmd)


# --- C. git -------------------------------------------------------------------

AC11_ALLOW = ['git status', 'git status --porcelain', 'git log --oneline -5', 'git log -n 5 --stat',
              'git diff', 'git diff --stat HEAD~1', 'git show HEAD', 'git rev-parse HEAD', 'git ls-files',
              'git blame docs/a.md', 'git branch', 'git branch -a', 'git add docs/a.md',
              'git add .claude/settings.json', "git commit -m 'Add PRD'", 'git --no-pager log -3']
AC12_DENY = ["git clone -u'touch pw; git-upload-pack' . docs/z",
             "git clone --upload-pa='touch pw; git-upload-pack' . docs/z2", 'git clone --templ=docs/tpl . docs/z3',
             'git log -1 --outp=.claude/settings.local.json', 'git log --output=docs/x',
             'git log -1 {--output=.claude/settings.local.json,}', 'git diff {--output=.claude/settings.local.json,}',
             'git status {--porcelain,--zz}', 'git diff --ext-diff', "git -c alias.r='!node x.js' r",
             'git -C docs status', 'git --git-dir=docs/gd status', 'git init -q --separate-git-dir=docs/gd docs/w',
             'git checkout -- .claude/settings.json', 'git worktree add docs/w', 'git config core.fsmonitor x',
             'git r', 'git branch -D main']


@pytest.mark.parametrize('cmd', AC11_ALLOW)
def test_ac_11_git_table_allowed(world, cmd):
    assert_allow(world, cmd)


@pytest.mark.parametrize('cmd', AC12_DENY)
def test_ac_12_git_attacks_denied(world, cmd):
    assert_deny(world, cmd)


def test_ac_13_git_only_in_root_repo(world):
    w = world.P / 'docs' / 'w'
    for d in ('objects', 'refs'):
        (w / d).mkdir(parents=True, exist_ok=True)
    (w / 'HEAD').write_text('ref: refs/heads/main\n', encoding='utf-8')
    (w / 'config').write_text('[core]\n\tfsmonitor = touch pwned\n\tbare = true\n', encoding='utf-8')
    assert_deny(world, 'git status', cwd=w)
    assert_deny(world, 'git status', cwd=world.P / 'docs')
    assert_allow(world, 'git status', cwd=world.P)
    assert_allow(world, 'git status', proj=world.P2, cwd=world.P2)


# --- D. Narrow allowances and false-denial guards -----------------------------

@pytest.mark.parametrize('cmd', ['mkdir -p docs/a', 'mkdir -p .aid/qa'])
def test_ac_20_mkdir_allowed(world, cmd):
    assert_allow(world, cmd)


@pytest.mark.parametrize('cmd', ['mkdir -p src/x', 'mkdir -p .claude/hooks/x', 'mkdir -p .git/hooks',
                                 'mkdir -m 777 docs/a', 'mkdir -p ../outside', 'mkdir -p .cl?ude/x',
                                 'mkdir -p .cl*/hooks', 'mkdir -p {.git,docs}/x', 'mkdir -p docs/w/.git'])
def test_ac_20_mkdir_denied(world, cmd):
    assert_deny(world, cmd)


def test_ac_20_ac_35_device_names_are_real_files_for_mkdir_and_write(world):
    """
    WHY: `/dev/null`, `nul` are sinks only as shell redirect targets. Git Bash `mkdir -p nul`
    and Node `writeFileSync('nul')` create a real root-level `nul` (measured), outside the
    allowed prefixes before Phase 4.
    """
    for cmd in ['mkdir -p nul', 'mkdir -p NUL', 'mkdir -p docs/a nul']:
        assert_deny(world, cmd)
    for p in ['nul', 'NUL', '/dev/null', '\\dev\\null', '/dev/stdout']:
        assert write(world, p, phase=1)[0] == 'DENY', p
    # redirects to the sink still work, and Phase 5 writes are free
    assert_allow(world, 'ls 2>/dev/null')
    assert_allow(world, 'git status 2>&1')
    assert_allow(world, 'echo x > /dev/null', phase=5)
    assert write(world, str(world.P / 'src' / 'x.ts'), phase=5)[0] == 'ALLOW'
    assert write(world, str(world.P / 'docs' / 'x.md'), phase=1)[0] == 'ALLOW'


def test_ac_21_cd_to_project_root(world):
    assert_allow(world, 'cd "{}" && git status'.format(world.P))
    assert_allow(world, 'cd "{}" && git status'.format(world.P2), proj=world.P2, cwd=world.P2)
    assert_deny(world, 'cd docs && ls')
    assert_deny(world, 'cd .. && ls')


@pytest.mark.skipif(not WIN, reason='Windows drive-relative path form')
def test_ac_21_drive_relative_words_denied(world):
    """
    WHY: Git Bash reads `cd C:` as `cd C:/` (measured: mkdir then lands in /c/docs, git runs
    outside the root repo) and `mkdir C:docs/x` as a literal `C:docs` dir, while Win32 joins
    both onto cwd. normalize() refuses the form, so cd, mkdir and Write all deny it.
    """
    for cmd in ['cd C: && git status', 'cd C: && mkdir -p docs/x', 'cd "C:" && ls',
                'cd C:. && ls', 'mkdir -p C:docs/x']:
        assert_deny(world, cmd)
    assert write(world, 'C:docs/x.md', phase=1)[0] == 'DENY'
    assert_allow(world, 'cd "{}" && git status'.format(world.P))
    assert_allow(world, 'cd "{}" && git status'.format(world.P2), proj=world.P2, cwd=world.P2)
    assert write(world, str(world.P / 'docs' / 'x.md'), phase=1)[0] == 'ALLOW'


@pytest.mark.skipif(not WIN, reason='Windows UNC-backed project')
def test_ac_35_project_reached_through_unc_path_allows_docs(world, tmp_path):
    """
    WHY: the raw-form check (AC-35 corrected) resolves with a \\\\?\\ prefix; for a UNC
    target realpath returns \\\\?\\UNC\\host\\..., which must key as //host/... like the
    root does, or every pre-Phase-4 Write in such a project is falsely denied.
    """
    real = str(world.P).replace('/', '\\')
    drive, rest = os.path.splitdrive(real)
    link = tmp_path / 'uncl'
    try:
        os.symlink('\\\\localhost\\{}$'.format(drive[0].lower()) + rest, str(link), target_is_directory=True)
    except OSError:
        pytest.skip('symlinks not permitted')
    if not os.path.isdir(link):
        pytest.skip('administrative share \\\\localhost\\c$ not reachable')
    assert write(world, str(link / 'docs' / 'x.md'), phase=1, proj=link, cwd=link)[0] == 'ALLOW'
    assert write(world, str(link / 'src' / 'x.ts'), phase=1, proj=link, cwd=link)[0] == 'DENY'
    assert write(world, str(link / '.claude' / 'settings.json'), phase=5, proj=link, cwd=link)[0] == 'DENY'


def test_ac_21_failed_cd_cannot_hand_git_a_subfolder_repo(world):
    """
    WHY: Git Bash fails `cd "<P>."` / `cd "<P> "` (Windows-only trailing dot/space
    stripping, measured in review 3) and `;`, `||` or `|` then runs git in the session's
    subfolder cwd, i.e. in an agent-written repo whose config runs code (AC-13 bypass).
    """
    sub = world.P / 'docs' / 'w'
    sub.mkdir(parents=True, exist_ok=True)
    for cmd in ['cd "{P}.";git status', 'cd "{P} " ; git status', 'cd "{P}" || git status',
                'cd "{P}" ; git status', 'cd "{P}" | git status', 'cd "{P}/." || git status',
                'cd "{P}." && true ; git status', 'cd "{P}." && true || git status',
                'cd "{P}." && git status']:
        assert_deny(world, cmd.format(P=world.P), cwd=sub)
    assert_allow(world, 'cd "{}" && git status'.format(world.P), cwd=sub)
    assert_allow(world, 'cd "{}/." && git status | head -5'.format(world.P), cwd=sub)


def test_ac_10_version_probe_only_in_project_root(world):
    """
    WHY: yarn 1 runs the `yarn-path` file named in a .yarnrc in its cwd, even for
    `yarn --version` (measured in review 3). Before Phase 4 the agent can Write such a
    file under docs/, so a probe from a subfolder cwd would run agent-written code.
    """
    docs = world.P / 'docs'
    (docs / '.yarnrc').write_text('yarn-path "./evil.js"\n', encoding='utf-8')
    (docs / 'evil.js').write_text("require('fs').writeFileSync('../src_pwned.txt','x')\n", encoding='utf-8')
    for tool in ('yarn', 'node', 'npm'):
        assert_deny(world, tool + ' --version', cwd=docs)
        assert_allow(world, tool + ' --version', cwd=world.P)
    assert_allow(world, 'cd "{}" && yarn --version'.format(world.P), cwd=docs)


AC22_BODY = "Add PRD\n\nnode x.js\n$(touch pw)\nPython 3.12\n\tEOF\nEOF \n"
AC22_ALLOW = ["git commit -m \"$(cat <<'EOF'\n" + AC22_BODY + "EOF\n)\"",
              'git commit -m "$(cat <<"EOF"\n' + AC22_BODY + 'EOF\n)"',
              "git commit -a -m \"$(cat <<'MSG'\nfix\nMSG\n)\" && git log --oneline -1"]
AC22_DENY = ['git commit -m "$(cat <<EOF\nmsg\nEOF\n)"',
             "git commit -m \"$(cat <<'EOF'\nmsg\nEOF\ntouch pw\nEOF\n)\"",
             "git commit -m \"$(cat <<-'EOF'\nmsg\n\tEOF\ntouch pw\nEOF\n)\"",
             "git commit -m \"$(cat <<-'EOF'\nmsg\nEOF\n)\"",
             "git commit -m \"$(cat <<'EOF'\r\nmsg\r\nEOF\r\n)\"",
             # mixed endings: Git Bash ends the body at "EOF\r" and runs touch (measured)
             "git commit -m \"$(cat <<'EOF'\nmsg\nEOF\r\ntouch pw\nEOF\n)\"",
             'git commit -m "$(cat docs/msg)"',
             "git commit -m \"$(cat <<'EOF'\nmsg\nEOF\n; touch pw)\"",
             "git commit -m \"$(cat <<'EOF'\nmsg\nEOF\n)\" && node x.js",
             "gh pr create --body \"$(cat <<'EOF'\nmsg\nEOF\n)\"",
             "echo \"$(cat <<'EOF'\nmsg\nEOF\n)\"",
             # inside $( ) bash 5.2 ends the body at a line starting with EOF and holding
             # ')' and runs touch (measured, Git Bash 5.2.26): fix round 1 BLOCKER
             "git commit -m \"$(cat <<'EOF'\nmsg\nEOF)\" ; touch pwA ; echo \"$(cat <<'EOF'\nEOF\n)\"",
             "git commit -m \"$(cat <<'EOF'\nmsg\nEOF )\" ; touch pw ; git commit -m \"$(cat <<'EOF'\nEOF\n)\"",
             "git commit -m \"$(cat <<'EOF'\nmsg\nEOF\t)\" ; touch pw ; git commit -m \"$(cat <<'EOF'\nEOF\n)\"",
             "git commit -m \"$(cat <<'EOF'\nmsg\nEOFx)\" && touch pwB && git commit -m \"$(cat <<'EOF'\nEOF\n)\"",
             # a '#' in the head comments out the heredoc opener in bash, so every "body"
             # line runs as a command (fix round 2 BLOCKER; test_ac_22_comment_head_runs_body)
             "git commit # -m \"$(cat <<'EOF'\ntouch pw\nEOF\n)\"",
             "git commit -a #x -m \"$(cat <<'EOF'\nnode x.js\nEOF\n)\"",
             "git commit -q -m x # -m \"$(cat <<'EOF'\ntouch pw\nEOF\n)\"",
             # the head goes through the git option table (fix round 2 MAJOR)
             "git commit --template=x -m \"$(cat <<'EOF'\nmsg\nEOF\n)\"",
             # nothing but ')"' may follow the delimiter: a later ')"' line must not
             # smuggle a command line in between (fix round 3 MINOR)
             "git commit -m \"$(cat <<'EOF'\nmsg\nEOF\n)\"\ntouch pw\n)\""]


@pytest.mark.parametrize('cmd', AC22_ALLOW)
def test_ac_22_commit_heredoc_idiom_allowed(world, cmd):
    assert_allow(world, cmd)


@pytest.mark.parametrize('cmd', AC22_DENY)
def test_ac_22_commit_heredoc_variants_denied(world, cmd):
    assert_deny(world, cmd)


def test_ac_22_comment_head_runs_body_in_bash(world, tmp_path):
    """The attack is real: bash runs the 'body' line when the head carries a comment.
    Uses `true` as the head so no git repo is touched; the gate shape is the same."""
    bash_exe = shutil.which('bash')
    if not bash_exe:
        pytest.skip('bash not available')
    script = "true # -m \"$(cat <<'EOF'\ntouch pw_body_ran\nEOF\n)\"\n"
    subprocess.run([bash_exe, '-c', script], cwd=str(tmp_path), capture_output=True, timeout=30)
    assert (tmp_path / 'pw_body_ran').exists()


def test_ac_22_idiom_head_gets_root_repo_check(world):
    """The idiom head runs through _pre4, so AC-13's root-repo check applies to it."""
    w = world.P / 'docs' / 'w'
    for d in ('objects', 'refs'):
        (w / d).mkdir(parents=True, exist_ok=True)
    (w / 'HEAD').write_text('ref: refs/heads/main\n', encoding='utf-8')
    (w / 'config').write_text('[core]\n\tfsmonitor = touch pwned\n\tbare = true\n', encoding='utf-8')
    idiom = "git commit -m \"$(cat <<'EOF'\nmsg\nEOF\n)\""
    assert_deny(world, idiom, cwd=w)
    assert_deny(world, idiom, cwd=world.P / 'docs')
    assert_allow(world, idiom, cwd=world.P)


R_FWD = REPO_ROOT.replace('\\', '/')
R_BACK = REPO_ROOT.replace('/', '\\')


@pytest.mark.parametrize('cmd', ['python "{}/hooks/aid_session.py" roles'.format(R_FWD),
                                 'python "{}\\hooks\\aid_session.py" start developer 1'.format(R_BACK),
                                 'py "{}/hooks/aid_session.py" end'.format(R_FWD)])
def test_ac_23_plugin_session_script_allowed(world, cmd):
    assert_allow(world, cmd)


@pytest.mark.parametrize('cmd', ['python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" roles',
                                 'python hooks/aid_session.py start dev 1',
                                 'python "{P}/hooks/aid_session.py" roles',   # the project's copy
                                 'python "{}/hooks/aid_session.py" roles; node x.js'.format(R_FWD),
                                 'python "{}/hooks/aid_session.py" "$(touch pw)"'.format(R_FWD),
                                 'python "{}/hooks/aid_session.py" roles > docs/x'.format(R_FWD)])
def test_ac_23_other_session_forms_denied(world, cmd):
    (world.P / 'hooks').mkdir(exist_ok=True)
    (world.P / 'hooks' / 'aid_session.py').write_text('print("project code")', encoding='utf-8')
    assert_deny(world, cmd.replace('{P}', str(world.P)))


def test_ac_24_extra_allowed_commands(world):
    cfg = dict(BLOCK, phase_gate_rules={'extra_allowed_commands': ['make lint', 'npm ci']})
    assert_allow(world, 'make lint', config=cfg)
    assert_allow(world, 'npm ci', config=cfg)
    for cmd in ('make dev', 'make lint; node x.js', 'make lint $(x)',
                # exact match: extra arguments can point the tool at agent-written code
                # ('npm ci --prefix docs' ran docs/package.json's preinstall, measured)
                'npm ci --prefix docs', 'make lint -f docs/evil.mk', 'make lint --eval=x'):
        assert_deny(world, cmd, config=cfg)
    star = dict(BLOCK, phase_gate_rules={'extra_allowed_commands': ['make lint *']})
    assert_allow(world, 'make lint -j4', config=star)        # opt-in prefix form
    assert_deny(world, 'make dev', config=star)


AC25_INPUTS = (AC1_DENY + AC2_DENY + AC3_DENY + AC4_DENY + AC5_DENY + AC8_DENY + AC9_DENY
               + AC12_DENY + AC15_DENY)


# T2-10 (owner 2026-11-17): flipped deliberately. These AC-25 inputs write an AID control
# file, and a control-file refusal is a DENY at every level; warn/log relax phase rules only.
AC25_CONTROL_FILE = {
    'echo {} > .claude/settings.json', 'sort --out=.claude/settings.local.json docs/x',
    'sed -n --in-pl 1p .claude/settings.json', 'git log -1 --outp=.claude/settings.local.json',
    'git log -1 {--output=.claude/settings.local.json,}', 'git diff {--output=.claude/settings.local.json,}',
    'git checkout -- .claude/settings.json'}


def test_ac_25_control_file_inputs_are_ac_inputs():
    assert AC25_CONTROL_FILE <= set(AC25_INPUTS)


@pytest.mark.parametrize('level', ['warn', 'log'])
@pytest.mark.parametrize('cmd', AC25_INPUTS)
def test_ac_25_warn_and_log_never_deny(world, cmd, level):
    cfg = {'enforcement': {'phase_gate_write': level, 'phase_gate_bash': level}}
    v = bash(world, cmd, config=cfg)
    if cmd in AC25_CONTROL_FILE:
        assert v[0] == 'DENY' and 'control file' in v[1], (cmd, level, v[1])
        return
    assert v[0] == 'ALLOW', (cmd, level, v[1])
    if level == 'warn':
        assert 'AID ENFORCEMENT WARNING' in v[2]['hookSpecificOutput']['additionalContext']


@pytest.mark.parametrize('phase', [4, 5])
@pytest.mark.parametrize('cmd', ['node x.js', 'npm test', 'python -m pytest', 'bash docs/run.sh',
                                 'cp src/a src/b', 'for f in src/*; do echo $f; done'])
def test_ac_26_phase_4_runs_code_freely(world, cmd, phase):
    assert_allow(world, cmd, phase=phase)


@pytest.mark.parametrize('phase', [4, 5])
@pytest.mark.parametrize('cmd', ['cd D: && npm test', 'npm test -- D:', 'npm run test:unit',
                                 'npm run build:prod', 'npx vitest -t a:b', 'python -m pytest -k t:1'])
def test_ac_26_colon_arguments_are_not_control_files(world, cmd, phase):
    """
    WHY: normalize() calls `D:` / `test:unit` SUSPICIOUS (drive-relative, NTFS stream). That
    is right for a write target, but a plain argument of npm/node is not one; refusing it
    blocked the most common Phase 4 commands. Writer operands keep the SUSPICIOUS denial.
    """
    assert_allow(world, cmd, phase=phase)
    assert_deny(world, 'echo {} > .claude/settings.json', phase=phase)


def test_ac_28_windows_path_false_denial_guards(world):
    for cmd in ['cat "C:\\Users\\x\\docs\\a.md"', 'cat "C:\\\\Users\\\\x\\\\docs\\\\a.md"',
                'ls "{}/docs"'.format(world.P2), "cat 'C:\\Users\\x\\docs\\a.md'"]:
        assert_allow(world, cmd)
    assert_allow(world, 'git status', proj=world.P2, cwd=world.P2)


# --- E. Phase 4+ best effort --------------------------------------------------

@pytest.mark.parametrize('cmd', ['echo {} > .claude/settings.json', 'echo {} > .claude/settings.local.json',
                                 'tee .aid/hooks/config.json < docs/x', 'cp docs/x .claude/settings.local.json',
                                 'rm -rf .claude', 'mv .claude .claude-off',
                                 "python -c \"open('.claude/settings.json','w').write('{}')\""])
def test_ac_30_literal_control_file_targets_denied_in_phase_5(world, cmd):
    assert_deny(world, cmd, phase=5)


@pytest.mark.parametrize('cmd', ['echo x > "$PWD/.claude/settings.local.json"',
                                 'tee "$CLAUDE_PROJECT_DIR/.aid/hooks/config.json"'])
def test_ac_31_variable_targets_keep_the_literal_check(world, cmd):
    assert_deny(world, cmd, phase=5)


@pytest.mark.parametrize('cmd', ['git add .claude/settings.json', 'git diff -- .claude/settings.json',
                                 'git log -p -- .aid/hooks/config.json', 'cat .claude/settings.json',
                                 'grep -n deny .claude/settings.json'])
def test_ac_33_reading_and_staging_control_files_allowed_in_phase_5(world, cmd):
    assert_allow(world, cmd, phase=5)


@pytest.mark.parametrize('cmd', ['git checkout -- .claude/settings.json', 'git restore .claude/settings.json',
                                 'git diff --output=.claude/settings.local.json',
                                 'git diff {--output=.claude/settings.local.json,}',
                                 'cat docs/x > .claude/settings.json'])
def test_ac_33_exemptions_do_not_cover_writes(world, cmd):
    assert_deny(world, cmd, phase=5)


# --- F. Write tool ------------------------------------------------------------

def _wpaths(w):
    P, H = str(w.P), w.H
    P_deny_1 = [P + '/docs/../src/app.ts', 'docs/../src/app.ts', 'C:/x/.claude/plans/../../evil.ts',
                P + '/docs/w/.git/config', P + '/docs/w/.GIT/config', P + '/docs/w/.git./config',
                P + '/docs/w/.git /config', P + '/docs/w/.git', P + '/src/app.ts']
    P_deny_5 = [P + '/.claude/settings.json', P + '/.CLAUDE/SETTINGS.JSON',
                '.aid/hooks/config.json', '.aid/pipeline/ESCALATION.json', '.aid/pipeline/escalation.json',
                '.claude/settings.local.json', '.claude/hooks/x.sh', str(H / '.claude' / 'settings.json'),
                P + '/.aid/state.json', '.aid/state.json']    # T3 (owner 2026-11-17): flipped from allow
    allow = [P + '/docs/spec.md', P + '/.claude/plans/x.ts', P + '/.aid/pipeline/state.json',
             str(H / '.claude' / 'plans' / 'p.md')]
    if WIN:
        B = P.replace('/', '\\')
        # Win32 drops a trailing dot/space, so these ARE settings.json there. On Linux and
        # macOS they are different files, and the gate rightly allows them at phase 5.
        P_deny_5 += [P + '/.claude/settings.json.', P + '/.claude/settings.json ']
        P_deny_1 += [B + '\\src\\app.ts', B + '\\docs\\..\\src\\app.ts']
        P_deny_5 += [B + '\\.claude\\settings.json', B + '\\.CLAUDE\\SETTINGS.JSON',
                     B + '\\.claude\\settings.json::$DATA', B + '\\CLAUDE~1\\settings.json', '\\\\?\\' + B + '\\.claude\\settings.json',
                     '.aid\\hooks\\config.json', '.aid\\pipeline\\ESCALATION.json', '.claude\\settings.local.json',
                     '.claude\\hooks\\x.sh']
        P_deny_5 += [B + '\\.aid\\state.json']                  # T3 (owner 2026-11-17): flipped
        allow += [B + '\\docs\\spec.md', B + '\\DOCS\\spec.md', B + '\\.aid\\pipeline\\state.json',
                  '/' + P[0].lower() + P[2:].replace('\\', '/') + '/docs/x.md']
    return P_deny_1, P_deny_5, allow


def test_ac_35_write_tool_path_forms(world, monkeypatch):
    deny1, deny5, allow = _wpaths(world)
    for p in deny1:
        assert write(world, p, phase=1)[0] == 'DENY', p
    for p in deny5:
        assert write(world, p, phase=5)[0] == 'DENY', p
    for p in allow:
        assert write(world, p, phase=1)[0] == 'ALLOW', p
    assert write(world, str(world.P2) + '/docs/spec.md', phase=1, proj=world.P2)[0] == 'ALLOW'
    monkeypatch.setenv('AID_HOME', str(world.H / '.aid'))
    baseline = g.integrity_dir(world.P) / 's1.json'
    assert write(world, baseline, phase=5)[0] == 'DENY', baseline


@pytest.mark.parametrize('is_win', [False, True])
def test_f3_protected_set_ignores_case_on_every_os(monkeypatch, is_win):
    """
    WHY (F3): the protected-path check folded case only on Windows. macOS file systems are
    case-insensitive by default, so a Phase 5 Write to `.CLAUDE/SETTINGS.JSON` reached the
    real control file there. IS_WIN=False forces the POSIX comparison on every CI runner.
    """
    monkeypatch.setattr(g, 'IS_WIN', is_win)
    for p in ('/u/p/.CLAUDE/SETTINGS.JSON', '/u/p/.Claude/Settings.Local.Json',
              '/u/p/.AID/HOOKS/config.json', '/u/p/.aid/pipeline/escalation.json',
              '/u/p/.CLAUDE/Hooks/x.sh', '/u/p/.Claude/PLUGINS/Cache/x.js'):
        assert g.is_protected(p), p
    for p in ('/u/p/.CLAUDE', '/u/p/.AID/Pipeline', '/u/p/.Claude/Plugins'):
        assert g.is_protected_or_parent(p), p
    for p in ('/u/p/docs/settings.json', '/u/p/.claude/plans/x.md', '/u/p/.aid/pipeline/state.json'):
        assert not g.is_protected(p), p


def test_ac_35_trailing_dot_or_space_denied_if_either_form_is_refused(world):
    """AC-35 corrected (§7): Windows drops a trailing dot/space, Node does not (it creates a
    real root-level 'docs ' directory). Deny if EITHER the stripped or the raw form is refused."""
    P = str(world.P)
    for p in (P + '/docs /x.ts', P + '/docs./x.ts', P + '/docs. /x.ts'):
        assert write(world, p, phase=1)[0] == 'DENY', p
    assert_deny(world, 'mkdir -p "docs /x"')
    # legitimate forms still pass
    assert write(world, P + '/docs/x.md', phase=1)[0] == 'ALLOW'
    assert write(world, P + '/docs/x.md', phase=5)[0] == 'ALLOW'
    assert write(world, P + '/src /x.ts', phase=5)[0] == 'ALLOW'
    assert_allow(world, 'mkdir -p docs/a')


def test_ac_35_hard_link_to_control_file_denied(world):
    """
    WHY: realpath does not reveal hard links. A Write to docs/hl.json that is a second name
    of .claude/settings.json rewrites the control file (measured on NTFS, fix round 3).
    """
    P = world.P
    target = P / 'docs' / 'hl.json'
    try:
        os.link(str(P / '.claude' / 'settings.json'), str(target))
    except OSError as e:
        pytest.skip('hard links not supported here: {}'.format(e))
    try:
        for phase in (1, 5):
            v, reason, _ = write(world, str(target), phase=phase)
            assert v == 'DENY' and 'hard link' in reason, (phase, reason)
        # a plain single-link file next to it still writes
        (P / 'docs' / 'single.md').write_text('x')
        assert write(world, str(P / 'docs' / 'single.md'), phase=5)[0] == 'ALLOW'
    finally:
        target.unlink()
        (P / 'docs' / 'single.md').unlink(missing_ok=True)


def test_ac_35_multi_link_non_control_file_reason_does_not_call_it_a_control_file(world):
    """
    WHY: a hard-linked ordinary file (e.g. a pnpm store link) is refused at Phase 5 because
    AID cannot see the other names. The reason must say exactly that and not claim the file
    is (or may be) a control file, and the Write gate must not send the agent to /phase-advance.
    """
    P = world.P
    a, a2 = P / 'src' / 'hl_a', P / 'src' / 'hl_a2'
    a.parent.mkdir(exist_ok=True)
    a.write_text('x')
    try:
        os.link(str(a), str(a2))
    except OSError as e:
        a.unlink()
        pytest.skip('hard links not supported here: {}'.format(e))
    try:
        for v, reason, _ in (write(world, str(a2), phase=5), bash(world, 'cp src/b src/hl_a2', phase=5)):
            assert v == 'DENY', reason
            assert 'cannot tell' in reason and 'may be an AID control file' not in reason, reason
            assert '/phase-advance' not in reason, reason
    finally:
        a2.unlink()
        a.unlink()


def test_ac_48_write_deny_message_matches_the_phase(world):
    """WHY: at Phase 4+ only control files are refused, so /phase-advance cannot help; before
    Phase 4 it is the way forward."""
    v = write(world, str(world.P) + '/.claude/settings.json', phase=5)
    assert v[0] == 'DENY' and '/phase-advance' not in v[1] and 'let the user make the change' in v[1], v[1]
    v = write(world, str(world.P) + '/src/app.ts', phase=1)
    assert v[0] == 'DENY' and '/phase-advance' in v[1], v[1]


@pytest.mark.parametrize('rel', ['docs/w/.GIT/config', 'docs/w/.git./config', 'docs/w/.git /config'])
def test_ac_35_git_component_spellings_on_case_insensitive_non_windows(root, rel, monkeypatch):
    """On Windows normalize() already folds case and trailing dots (the hook rows above);
    on macOS (case-insensitive, no folding in normalize) the component check must do it."""
    monkeypatch.setattr(g, 'IS_WIN', False)
    assert g.write_target_verdict(os.path.join(root, rel), root, root, 1, RULES, literal=True)


def test_ac_36_claude_config_dir_settings_protected(world):
    cfg = world.H / '.config' / 'claude'
    env = {'CLAUDE_CONFIG_DIR': str(cfg)}
    assert write(world, cfg / 'settings.json', phase=5, env=env)[0] == 'DENY'
    assert write(world, cfg / 'plans' / 'p.md', phase=1, env=env)[0] == 'ALLOW'
    # the plugin's own hook code and user hooks move with CLAUDE_CONFIG_DIR too
    for p in (cfg / 'plugins' / 'cache' / 'aid' / 'aid' / '1.0' / 'hooks' / 'aid_guard.py',
              cfg / 'hooks' / 'x.sh'):
        assert write(world, p, phase=5, env=env)[0] == 'DENY', p


@pytest.mark.skipif(not WIN, reason='Windows device / UNC path forms')
def test_ac_36_device_and_unc_forms_do_not_dodge_protection(world, monkeypatch):
    """\\\\?\\Volume{GUID}, \\\\?\\UNC and \\\\host\\c$ reach the real file on Windows
    but used to be joined onto cwd or compared as strings (fix round 2 BLOCKER)."""
    cfg = world.H / '.config' / 'claude'
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / 'settings.json').write_text('{}', encoding='utf-8')
    env = {'CLAUDE_CONFIG_DIR': str(cfg)}
    real = os.path.realpath(str(cfg / 'settings.json'))
    drive, rest = os.path.splitdrive(real)
    rest_b = rest.replace('/', '\\')
    vol = subprocess.run(['mountvol', drive + '\\', '/L'], capture_output=True, text=True).stdout.strip()
    forms = ['\\\\localhost\\{}$'.format(drive[0].lower()) + rest_b,
             '\\\\?\\UNC\\localhost\\{}$'.format(drive[0].lower()) + rest_b]
    if vol.startswith('\\\\?\\Volume{'):
        forms.append(vol.rstrip('\\') + rest_b)
    for p in forms:
        assert os.path.samefile(p, real), p          # the form really is the protected file
        assert write(world, p, phase=5, env=env)[0] == 'DENY', p
    # a relative-looking device form must not be joined onto cwd at phase 1 either
    src = os.path.realpath(str(world.P / 'src' / 'app.ts'))
    sd, srest = os.path.splitdrive(src)
    assert write(world, '\\\\?\\UNC\\localhost\\{}$'.format(sd[0].lower()) + srest.replace('/', '\\'),
                 phase=1, cwd=world.P / 'docs')[0] == 'DENY'
    # legitimate drive-letter device form of an allowed file still works
    assert write(world, '\\\\?\\' + str(world.P / 'docs' / 'spec.md').replace('/', '\\'), phase=1)[0] == 'ALLOW'


def test_ac_35_integrity_baseline_protected_under_moved_aid_home(world, monkeypatch):
    aid_home = world.H / 'aiddata'
    monkeypatch.setenv('AID_HOME', str(aid_home))
    baseline = g.integrity_dir(world.P) / 's1.json'
    assert write(world, baseline, phase=5, env={'AID_HOME': str(aid_home)})[0] == 'DENY'
    assert write(world, world.P / 'docs' / 'a.md', phase=5, env={'AID_HOME': str(aid_home)})[0] == 'ALLOW'


# --- K. Generated class families (AC-50) --------------------------------------

EXPANSIONS = ['$x', '${x}', '$(x)', '`x`', '$((1))', "$'x'", '${x@P}']
AC50_EXPANSION = ([('echo ' + e) for e in EXPANSIONS] + [('echo "' + e + '"') for e in EXPANSIONS]
                  + [e for e in EXPANSIONS] + [('echo a > ' + e) for e in EXPANSIONS])
BANNED = ['cp', 'mv', 'rm', 'touch', 'tee', 'sed', 'sort', 'uniq', 'find', 'xargs', 'rg', 'tree', 'file',
          'date', 'ln', 'dd', 'curl', 'test', '[', 'env', 'timeout', 'nice', 'nohup', 'command', 'exec',
          'bash', 'sh', 'awk', 'perl', 'npm', 'npx', 'pnpm', 'yarn', 'pip', 'python', 'py', 'node', 'make',
          'go', 'pytest', 'cd', 'pushd']
AC50_BANNED = [(b + ' ' + a).strip() for b in BANNED for a in ('', '--help', '-x', 'docs/a')]
GIT_SUBS = ['status', 'log', 'diff', 'show', 'rev-parse', 'ls-files', 'blame', 'branch', 'add', 'commit']
AC50_GIT = ['git {} {}'.format(s, o) for s in GIT_SUBS for o in ('--zz', '--out', '--outp', '-Z', '--output=docs/x')]
AC50_BRACE = (['git {} {{{},}}'.format(s, o) for s in GIT_SUBS for o in ('--output=docs/x', '--zz', '-Z')]
              + ['git {} a{{{},b}}'.format(s, o) for s in GIT_SUBS for o in ('--output=docs/x', '--zz', '-Z')]
              + ['cat docs/{a,b}', 'mkdir -p {docs,src}/x'])
QX = ['touch pw', 'node x.js', 'cp a b']
AC50_QUOTE = [f for x in QX for f in ("echo 'a\\'; " + x + "; echo '\\'", 'echo "\\\\"; ' + x + '; echo "\\\\"',
                                      'echo "\\"; ' + x + '; \\""', "echo 'it'\"'\"'s'; " + x,
                                      'echo "\\" A "; ' + x + '; " #"')]
AC50_QUOTE_ALLOW = ["echo 'a\\'", 'echo "a\\\\b"', 'echo "C:\\Users\\x"', "grep -n 'x\"y' docs/a.md"]


@pytest.mark.parametrize('cmd', AC50_EXPANSION + AC50_BANNED + AC50_GIT + AC50_BRACE + AC50_QUOTE)
def test_ac_50_generated_families_denied(world, cmd):
    assert_deny(world, cmd)


@pytest.mark.parametrize('cmd', AC50_QUOTE_ALLOW)
def test_ac_50_quote_family_allowed(world, cmd):
    assert_allow(world, cmd)
