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

    def test_no_personal_paths_in_shipped_files(self):
        offenders = []
        skip_dirs = {'node_modules', '.git', '__pycache__', '.pytest_cache'}
        for root, dirs, files in os.walk(REPO_ROOT):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for fn in files:
                if os.path.splitext(fn)[1].lower() not in (
                        '.md', '.json', '.yaml', '.yml', '.sh', '.bat',
                        '.py', '.mjs', '.js', '.ts', '.txt'):
                    continue
                path = os.path.join(root, fn)
                try:
                    with open(path, encoding='utf-8', errors='replace') as f:
                        text = f.read().lower()
                except OSError:
                    continue
                rel = os.path.relpath(path, REPO_ROOT)
                # This test file necessarily names the markers it hunts for.
                if rel.replace('\\', '/').endswith('testing/e2e/test_pipeline_hooks.py'):
                    continue
                for m in self.MARKERS:
                    if m in text:
                        offenders.append(f'{rel}: {m}')
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


def _ts_project(tmp_path, ts_source):
    """A throwaway git repo with one TypeScript file. Never the real repo."""
    (tmp_path / 'src').mkdir()
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


# tsc is only exercised when TypeScript is installed locally. npx would otherwise
# download it per run, making the result depend on the network rather than on the code.
_HAS_TSC = os.path.isfile(os.path.join(REPO_ROOT, 'node_modules', '.bin', 'tsc')) or \
    shutil.which('tsc') is not None
needs_tsc = pytest.mark.skipif(
    not _HAS_TSC, reason='TypeScript not installed locally - run `npm install` to enable'
)


@needs_tsc
class TestDevPipelineGateCompileCheck:
    def test_blocks_on_broken_typescript(self, tmp_path):
        project = _ts_project(tmp_path, 'const x: number = "not a number";\n')

        result = _run(GATE_HOOK, {'session_id': 's1', 'cwd': str(project)}, project)

        assert result.returncode == 0, result.stderr
        out = json.loads(result.stdout)
        assert out.get('decision') == 'block', (
            f'broken TypeScript did not block the stop: {result.stdout!r}'
        )
        assert 'TS2322' in out.get('reason', '') or 'tsc' in out.get('reason', ''), \
            'the block reason must carry the compiler error'

    def test_allows_clean_typescript(self, tmp_path):
        project = _ts_project(tmp_path, 'const x: number = 42;\nexport default x;\n')

        result = _run(GATE_HOOK, {'session_id': 's1', 'cwd': str(project)}, project)

        assert result.returncode == 0
        if result.stdout.strip():
            out = json.loads(result.stdout)
            assert out.get('decision') != 'block', (
                f'clean code was blocked: {result.stdout!r}'
            )
