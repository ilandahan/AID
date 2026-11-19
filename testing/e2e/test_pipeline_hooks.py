"""
AID Pipeline Hook Tests (plan-execution-pipeline.sh, dev-pipeline-gate.sh)

WHY THIS TEST:
- PROBLEM: both hooks were ported from a personal user-level setup. One POSTed the
  approved plan to a localhost dashboard and, when absent, told the user their plan
  "was NOT SAVED to the plan store"; the other pointed at a private "Start the Day"
  view. Neither exists for anyone else.
- COST OF FAILURE: adopters get alarming warnings about infrastructure they never had,
  and a Stop hook that can block a turn is the worst place for a phantom dependency.
- SUCCESS: no localhost/dashboard coupling ships; the ExitPlanMode hook extracts the
  plan and stays silent for other tools; the Stop gate blocks real compile failures,
  allows clean code, and can never loop.

Every test executes the real hook with a real payload. Payloads are built with
json.dump, never shell printf - an escaped \\n in a printf format becomes a literal
newline and produces invalid JSON, which reads exactly like "the hook found no plan".
"""
import json
import os
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
SETTINGS = os.path.join(REPO_ROOT, '.claude', 'settings.json')

SHIPPED_HOOKS = ['plan-execution-pipeline.sh', 'dev-pipeline-gate.sh',
                 'validate-qa-gate.py', 'qa-gate.sh']


def _run(hook, payload, cwd, env=None, timeout=300):
    """Execute a hook against `cwd` as its project directory.

    WHY the script is copied next to the fixture and invoked by RELATIVE name:
    bash on Windows may be git-bash (/c/...) or WSL (/mnt/c/...), and a native
    C:\\ path loses its backslashes in argv, so the script is simply "not found"
    (exit 127) - which looks identical to a hook that ran and stayed silent.
    A relative name sidesteps every path-translation question. Hooks take their
    project root from the payload's `cwd`, so their location does not matter.
    """
    name = os.path.basename(hook)
    local = os.path.join(str(cwd), name)
    if not os.path.exists(local):
        shutil.copy(hook, local)

    if name.endswith('.sh'):
        # Env vars are assigned INSIDE the shell, not via subprocess env: under WSL,
        # Windows environment variables are not inherited unless listed in WSLENV, so
        # an injected SKIP_PIPELINE_GATE silently never arrives and the bypass looks
        # broken when it is fine.
        prefix = ''.join(f'{k}={v} ' for k, v in (env or {}).items())
        cmd = ['bash', '-c', f'{prefix}./{name}']
    else:
        cmd = ['python', name]

    result = subprocess.run(
        cmd, input=json.dumps(payload), capture_output=True, text=True,
        timeout=timeout, cwd=str(cwd),
    )
    assert result.returncode != 127, f'{name} was never executed: {result.stderr}'
    return result


class TestHooksCarryNoPrivateInfrastructure:
    """Regression guard for the de-personalisation. Cheap, and it cannot decay."""

    @pytest.mark.parametrize('hook', SHIPPED_HOOKS)
    def test_no_localhost_or_dashboard_coupling(self, hook):
        path = os.path.join(HOOKS, hook)
        with open(path, encoding='utf-8', errors='replace') as f:
            text = f.read()

        banned = {
            '127.0.0.1': 'calls a service on the developer machine',
            'localhost': 'calls a service on the developer machine',
            '4664': 'hardcoded private dashboard port',
            '/api/plan/approved': 'private dashboard endpoint',
            'CC_LOOP_PORT': 'private dashboard config',
            'Start the Day': 'private dashboard UI reference',
            'plan store': 'private plan-store feature adopters do not have',
        }
        found = [f'{k} ({why})' for k, why in banned.items() if k in text]
        assert not found, f"{hook} still references private infrastructure: {found}"

    @pytest.mark.parametrize('hook', SHIPPED_HOOKS)
    def test_no_personal_paths(self, hook):
        path = os.path.join(HOOKS, hook)
        with open(path, encoding='utf-8', errors='replace') as f:
            text = f.read().lower()
        for marker in ('users\\iland', 'users/iland', "ilans' local files", 'melingo'):
            assert marker not in text, f"{hook} contains a personal path: {marker}"


class TestNoPersonalPathsAnywhere:
    """
    WHY REPO-WIDE, not just the hooks: the hook-only scan passed while
    pipeline-orchestrator/config.default.json still hardcoded
    "bundle_dir": "C:/Users/Iland/.claude/skills/autoresearch". A leak that lives one
    directory outside the scan is invisible to it, so scan everything that ships.
    """

    # Specific enough not to fire on ordinary English: good-morning.md legitimately
    # says "Start the day by checking systems", which is not the dashboard view.
    MARKERS = ['users/iland', 'users\\iland', "ilans' local files", 'melingo',
               'cc_loop_port', "start the day view", "dashboard's start the day"]

    SCAN_EXTS = ('.md', '.json', '.yaml', '.yml', '.sh', '.bat',
                 '.py', '.mjs', '.js', '.ts', '.txt')
    SKIP_DIRS = {'node_modules', '.git', '__pycache__', '.pytest_cache'}

    @classmethod
    def _candidate_files(cls, repo_root):
        """Relative paths of every file that could ship from `repo_root`.

        In a git checkout that is tracked + untracked-but-not-ignored files: a
        gitignored file (.aid/pipeline/state.json, .claude/settings.local.json,
        plan-store files the running session writes) can never be committed or
        packaged, so a local path inside it is not a leak. A brand-new file that
        is merely untracked IS still scanned - it is one `git add` from shipping.
        Outside git (tarball, archive) fall back to walking everything.
        """
        if os.path.isdir(os.path.join(repo_root, '.git')) or os.path.isfile(
                os.path.join(repo_root, '.git')):
            r = subprocess.run(
                ['git', '-C', repo_root, 'ls-files', '-z', '--cached',
                 '--others', '--exclude-standard'],
                capture_output=True, timeout=120)
            if r.returncode == 0:
                rels = [p for p in r.stdout.decode('utf-8', 'replace').split('\0') if p]
                return [p for p in rels
                        if not (set(p.split('/')[:-1]) & cls.SKIP_DIRS)]
        rels = []
        for root, dirs, files in os.walk(repo_root):
            dirs[:] = [d for d in dirs if d not in cls.SKIP_DIRS]
            for fn in files:
                rels.append(os.path.relpath(os.path.join(root, fn), repo_root))
        return rels

    @classmethod
    def _offenders(cls, repo_root):
        offenders = []
        for rel in cls._candidate_files(repo_root):
            if os.path.splitext(rel)[1].lower() not in cls.SCAN_EXTS:
                continue
            # This test file necessarily names the markers it hunts for.
            if rel.replace('\\', '/').endswith('testing/e2e/test_pipeline_hooks.py'):
                continue
            try:
                with open(os.path.join(repo_root, rel), encoding='utf-8',
                          errors='replace') as f:
                    text = f.read().lower()
            except OSError:
                continue
            for m in cls.MARKERS:
                if m in text:
                    offenders.append(f'{rel}: {m}')
        return offenders

    def test_gitignored_runtime_state_is_not_scanned_but_untracked_files_are(
            self, tmp_path):
        # A session's own gitignored state (plan store, settings.local.json) holds
        # absolute local paths by design; it cannot ship. A new untracked file can.
        if shutil.which('git') is None:
            pytest.skip('git not available')
        repo = str(tmp_path)
        subprocess.run(['git', 'init', '-q', repo], check=True, timeout=60)
        marker = 'C:/' + 'Users' + '/' + 'iland' + '/proj'
        with open(os.path.join(repo, '.gitignore'), 'w') as f:
            f.write('local-state/\nsettings.local.json\n')
        os.makedirs(os.path.join(repo, 'local-state'))
        for rel in ('local-state/state.json', 'settings.local.json'):
            with open(os.path.join(repo, rel), 'w') as f:
                f.write(json.dumps({'cwd': marker}))
        with open(os.path.join(repo, 'new-skill.md'), 'w') as f:
            f.write('see ' + marker + '\n')
        found = self._offenders(repo)
        assert found == ['new-skill.md: users/iland'], found

    def test_no_personal_paths_in_shipped_files(self):
        offenders = self._offenders(REPO_ROOT)
        assert not offenders, (
            'personal machine paths / private tooling references would ship:\n  '
            + '\n  '.join(offenders)
        )


class TestSettingsWiring:
    def test_both_stop_hooks_and_the_plan_hook_are_registered(self):
        with open(SETTINGS, encoding='utf-8') as f:
            settings = json.load(f)
        hooks = settings.get('hooks', {})

        stop_cmds = [h.get('command', '') for g in hooks.get('Stop', [])
                     for h in g.get('hooks', [])]
        assert any('validate-qa-gate.py' in c for c in stop_cmds), 'QA gate not wired'
        assert any('dev-pipeline-gate.sh' in c for c in stop_cmds), 'dev gate not wired'

        post = hooks.get('PostToolUse', [])
        assert any(g.get('matcher') == 'ExitPlanMode' for g in post), \
            'plan hook is not scoped to ExitPlanMode'
        plan_cmds = [h.get('command', '') for g in post for h in g.get('hooks', [])]
        assert any('plan-execution-pipeline.sh' in c for c in plan_cmds)

    @pytest.mark.parametrize('hook', [h for h in SHIPPED_HOOKS if h.endswith('.sh')])
    def test_shell_hooks_are_syntactically_valid(self, hook):
        # cwd + relative name, for the same path-translation reason as _run().
        r = subprocess.run(['bash', '-n', f'./{hook}'], cwd=HOOKS,
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, f"{hook} has a syntax error: {r.stderr}"


def _bash_has_node():
    """Does the SAME bash the hooks run under have node?

    git-bash and WSL bash resolve different PATHs - node is frequently present in one
    and absent in the other. The plan hook extracts the plan with node, so without it
    the hook can only take its (correct) degraded path. Probe rather than assume.
    """
    try:
        r = subprocess.run(['bash', '-c', 'command -v node'],
                           capture_output=True, text=True, timeout=60)
        return r.returncode == 0 and r.stdout.strip() != ''
    except Exception:
        return False


needs_node_in_bash = pytest.mark.skipif(
    not _bash_has_node(),
    reason='node is not on PATH in the bash that runs hooks (plan extraction needs it)',
)


class TestPlanExecutionHook:
    def test_ignores_other_tools(self, tmp_path):
        """It must be inert for every tool except ExitPlanMode."""
        result = _run(PLAN_HOOK, {'tool_name': 'Write', 'cwd': str(tmp_path)}, tmp_path)

        assert result.returncode == 0
        assert result.stdout.strip() == '', (
            f"hook fired on a non-ExitPlanMode tool: {result.stdout!r}"
        )

    @needs_node_in_bash
    @pytest.mark.parametrize('shape', ['tool_response', 'tool_input'])
    def test_captures_the_approved_plan(self, tmp_path, shape):
        """ExitPlanMode has been observed carrying the plan in either field."""
        plan = '## Plan\nAdd a login form and tests.'
        payload = {'tool_name': 'ExitPlanMode', 'cwd': str(tmp_path),
                   'session_id': 's1'}
        payload[shape] = {'plan': plan}

        result = _run(PLAN_HOOK, payload, tmp_path)

        assert result.returncode == 0, result.stderr
        out = json.loads(result.stdout)
        ctx = out['hookSpecificOutput']['additionalContext']
        assert out['hookSpecificOutput']['hookEventName'] == 'PostToolUse'
        assert 'INTENT GATE' in ctx, 'the intent gate instruction is missing'
        assert 'login form' in ctx, (
            f'the approved plan text was not captured from {shape}'
        )
        assert 'WARNING' not in ctx, 'a healthy run should not warn'

    def test_reports_failure_when_no_plan_text(self, tmp_path):
        """Fail-open, but stated - a silent hole in the brief is worse."""
        result = _run(PLAN_HOOK, {'tool_name': 'ExitPlanMode', 'cwd': str(tmp_path),
                                  'tool_input': {}}, tmp_path)

        assert result.returncode == 0
        out = json.loads(result.stdout)
        ctx = out['hookSpecificOutput']['additionalContext']
        assert 'WARNING' in ctx, 'a missing plan must be announced, not swallowed'
        assert 'INTENT GATE' in ctx, 'it must still let the work proceed'


_REPO_TS = os.path.join(REPO_ROOT, 'node_modules', 'typescript')


def _ts_project(tmp_path, ts_source, with_typescript=False):
    """A throwaway git repo with one TypeScript file. Never the real repo.

    with_typescript copies the repo's own TypeScript into the fixture's node_modules: the
    gate resolves tsc ONLY from the project it checks (never a global, never the plugin's
    install), so without it the gate says 'tsc NOT RUN' and can never block (D-13)."""
    (tmp_path / 'src').mkdir()
    if with_typescript:
        shutil.copytree(_REPO_TS, str(tmp_path / 'node_modules' / 'typescript'))
        (tmp_path / '.gitignore').write_text('node_modules/\n')
    (tmp_path / 'src' / 'sample.ts').write_text(ts_source)
    (tmp_path / 'tsconfig.json').write_text(
        json.dumps({'compilerOptions': {'strict': True, 'noEmit': True}}))
    subprocess.run(['git', 'init', '-q'], cwd=str(tmp_path), timeout=60)
    return tmp_path


class TestDevPipelineGate:
    _project = staticmethod(_ts_project)

    def test_bypasses_when_stop_hook_active(self, tmp_path):
        """Without this the gate would re-block forever."""
        project = self._project(tmp_path, 'const x: number = "bad";\n')

        result = _run(GATE_HOOK, {'session_id': 's1', 'cwd': str(project),
                                  'stop_hook_active': True}, project)

        assert result.returncode == 0
        assert result.stdout.strip() == '', (
            f'gate blocked while stop_hook_active was set: {result.stdout!r}'
        )

    def test_bypasses_on_skip_flag(self, tmp_path):
        project = self._project(tmp_path, 'const x: number = "bad";\n')

        result = _run(GATE_HOOK, {'session_id': 's1', 'cwd': str(project)},
                      project, env={'SKIP_PIPELINE_GATE': '1'})

        assert result.returncode == 0
        assert result.stdout.strip() == '', 'SKIP_PIPELINE_GATE=1 was not honoured'


# The gate tests below run under the bash FIRST ON PATH (what a user's shell resolves).
# subprocess's bare 'bash' on Windows is System32's WSL launcher, which re-expands the
# command line and usually has no node/python, so every language check would be skipped
# and the tests would prove nothing. A prelude script (not `bash -c`) carries env/PATH
# changes for the same re-expansion reason.
GATE_BASH = shutil.which('bash') or 'bash'


def _gate_bash_has(tool):
    try:
        r = subprocess.run([GATE_BASH, '-c', f'command -v {tool}'],
                           capture_output=True, text=True, timeout=60)
        return r.returncode == 0 and r.stdout.strip() != ''
    except Exception:
        return False


def _run_gate(project, prelude=''):
    """Run the gate in `project` under GATE_BASH; returns (result, seconds)."""
    shutil.copy(GATE_HOOK, os.path.join(str(project), 'dev-pipeline-gate.sh'))
    with open(os.path.join(str(project), 'run-gate.sh'), 'w', newline='\n') as f:
        f.write(prelude + '\nexec bash ./dev-pipeline-gate.sh\n')
    t0 = time.monotonic()
    result = subprocess.run([GATE_BASH, 'run-gate.sh'],
                            input=json.dumps({'session_id': 's1', 'cwd': str(project)}),
                            capture_output=True, text=True, timeout=300, cwd=str(project))
    return result, time.monotonic() - t0


def _git_project(tmp_path, files):
    for rel, text in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    subprocess.run(['git', 'init', '-q'], cwd=str(tmp_path), timeout=60)
    return tmp_path


# tsc is only exercised when TypeScript is installed in this repo (the fixture gets a copy,
# see _ts_project) and the gate's bash has node. A global tsc does not count: the gate
# never uses one, which is why the old `shutil.which('tsc')` precondition let
# test_blocks_on_broken_typescript run against a fixture the gate could not check (D-13).
_HAS_TSC = os.path.isfile(os.path.join(_REPO_TS, 'bin', 'tsc')) and _gate_bash_has('node')
needs_tsc = pytest.mark.skipif(
    not _HAS_TSC,
    reason="needs `npm install` (TypeScript in node_modules) and node in the gate's bash",
)
needs_gate_node = pytest.mark.skipif(not _gate_bash_has('node'),
                                     reason="node is not on PATH in the gate's bash")
needs_gate_python = pytest.mark.skipif(not _gate_bash_has('python'),
                                       reason="python is not on PATH in the gate's bash")


class TestDevPipelineGateHardening:
    @needs_gate_node
    def test_js_file_name_is_not_parsed_as_a_node_option(self, tmp_path):
        """
        WHY THIS TEST (A-19):
        - PROBLEM: changed-file names were passed bare to `node --check`, so a file named
          "--require=evil.js" became a node OPTION and loaded node_modules/evil.js.
        - COST OF FAILURE: arbitrary code runs on every Stop in any repo with the plugin.
        - SUCCESS: the payload never runs, and the oddly named file is syntax-checked.
        """
        project = _git_project(tmp_path, {
            '--require=evil.js': 'const ok = 1;\n',
            'node_modules/evil.js': "require('fs').writeFileSync('PWNED', 'x');\n",
            '.gitignore': 'node_modules/\nPWNED\n',
        })

        result, _ = _run_gate(project)

        assert not (project / 'PWNED').exists(), \
            f'a file name executed code through node options: {result.stdout!r}'
        assert result.returncode == 0, result.stderr
        assert '"decision":"block"' not in result.stdout.replace(' ', ''), result.stdout

    @needs_gate_node
    def test_broken_js_still_blocks_without_teaching_the_bypass(self, tmp_path):
        """
        WHY THIS TEST (A-19 regression + A-28):
        - PROBLEM: the "./" prefix must not stop real syntax errors from blocking, and the
          block reason used to end with "(or set SKIP_PIPELINE_GATE=1)" - read by the agent.
        - SUCCESS: still blocks; the bypass hint reaches stderr (human) and not the reason.
        """
        project = _git_project(tmp_path, {'src/bad.js': 'function (\n'})

        result, _ = _run_gate(project)

        out = json.loads(result.stdout)
        assert out.get('decision') == 'block', result.stdout
        assert 'bad.js' in out['reason']
        assert 'SKIP_PIPELINE_GATE' not in out['reason'], \
            'the block reason tells the agent how to switch the gate off'
        assert 'SKIP_PIPELINE_GATE=1' in result.stderr, 'the human lost the bypass hint'

    @needs_gate_python
    @pytest.mark.parametrize('prelude_extra', ['', 'export DEV_GATE_NO_TIMEOUT_BIN=1'],
                             ids=['timeout-binary', 'no-timeout-binary'])
    def test_slow_check_is_cut_off_and_reported_not_verified(self, tmp_path, prelude_extra):
        """
        WHY THIS TEST (A-20):
        - PROBLEM: checks had no time bound; one slower than the 120 s hook timeout got
          the hook cancelled and its output discarded - the gate failed open silently.
          Stock macOS has no `timeout` binary, so the no-timeout-binary case must be
          bounded too (the pure-bash watchdog).
        - SUCCESS: a hanging mypy is cut off by the shared budget and the message says
          NOT VERIFIED instead of "all language checks passed".
        Budget 10 leaves headroom for file listing + py_compile on a loaded box; which
        checks it cuts off besides mypy does not matter here.
        """
        project = _git_project(tmp_path, {
            'ok.py': 'x = 1\n',
            'stubs/mypy': '#!/usr/bin/env bash\nsleep 60\n',
        })
        os.chmod(str(project / 'stubs' / 'mypy'), 0o755)

        result, secs = _run_gate(
            project,
            'export PATH="$PWD/stubs:$PATH"\nexport DEV_GATE_BUDGET=10\n' + prelude_extra)

        assert secs < 30, f'the gate waited {secs:.0f}s for a hanging check'
        msg = json.loads(result.stdout)['systemMessage']
        assert 'NOT VERIFIED (time budget):' in msg, msg
        assert 'mypy' in msg.split('NOT VERIFIED (time budget):', 1)[1], msg
        assert 'all language checks passed' not in msg, msg

    def test_skipped_tsc_is_not_reported_as_passed(self, tmp_path):
        """
        WHY THIS TEST (A-43): with no local TypeScript the gate said "all language checks
        passed" although tsc never ran. It must say the check was skipped.
        """
        project = _ts_project(tmp_path, 'const x: number = "bad";\n')

        result, _ = _run_gate(project)

        msg = json.loads(result.stdout)['systemMessage']
        assert 'all language checks passed' not in msg, msg
        assert 'checks skipped: TS' in msg, msg


@needs_tsc
class TestDevPipelineGateCompileCheck:
    def test_blocks_on_broken_typescript(self, tmp_path):
        project = _ts_project(tmp_path, 'const x: number = "not a number";\n',
                              with_typescript=True)

        result, _ = _run_gate(project)

        assert result.returncode == 0, result.stderr
        out = json.loads(result.stdout)
        assert out.get('decision') == 'block', (
            f'broken TypeScript did not block the stop: {result.stdout!r}'
        )
        assert 'TS2322' in out.get('reason', ''), \
            'the block reason must carry the compiler error'

    def test_allows_clean_typescript(self, tmp_path):
        project = _ts_project(tmp_path, 'const x: number = 42;\nexport default x;\n',
                              with_typescript=True)

        result, _ = _run_gate(project)

        assert result.returncode == 0
        if result.stdout.strip():
            out = json.loads(result.stdout)
            assert out.get('decision') != 'block', (
                f'clean code was blocked: {result.stdout!r}'
            )
