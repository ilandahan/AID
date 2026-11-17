"""
AID Hooks Dispatcher Tests (hooks/aid_hooks.py)

WHY THIS TEST:
aid_hooks.py is the phase-gate enforcement engine CLAUDE.md documents as CRITICAL. It
shipped for months emitting payloads Claude Code does not read:

  - output_deny() emitted {"hookSpecificOutput": {"decision": "deny", "reason": ...}}.
    PreToolUse denials are read from permissionDecision / permissionDecisionReason, and
    every hookSpecificOutput must name its event. So every phase-gate block was accepted
    as an allow: the gate never once stopped a write.
  - output_allow(context) omitted hookEventName, so injected context and every "warn"
    level message was silently discarded.

Nothing failed while this was broken, because the wrong shape and the right shape both
exit 0. These tests EXECUTE the hook and assert on the emitted JSON.

Every test injects its own .aid/ fixture in tmp_path and runs the hook with cwd set
there. The hook derives PROJECT_ROOT from cwd, so it must never read the repo's own
.aid/ - a test that did would depend on whatever config that checkout happens to hold.
Since 3.0.8 (T2) the shipped default is "block" for the two phase gates, "log" otherwise.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HOOK = os.path.join(REPO_ROOT, 'hooks', 'aid_hooks.py')


def make_project(tmp_path, phase, enforcement=None):
    """Build a minimal AID project. Returns its path."""
    aid = tmp_path / '.aid'
    (aid / 'hooks').mkdir(parents=True)
    (aid / 'state.json').write_text(json.dumps({'current_phase': phase}), encoding='utf-8')
    if enforcement:
        (aid / 'hooks' / 'config.json').write_text(
            json.dumps({'enforcement': enforcement}), encoding='utf-8')
    return tmp_path


def run_hook(project, event, action=None, payload=None):
    cmd = [sys.executable, HOOK, '--event', event]
    if action:
        cmd += ['--action', action]
    proc = subprocess.run(cmd, input=json.dumps(payload or {}), capture_output=True,
                          text=True, timeout=60, cwd=str(project))
    assert proc.returncode == 0, (
        f'hook exited {proc.returncode} - a failing hook must never block the user.\n'
        f'stderr: {proc.stderr[:500]}'
    )
    return proc.stdout.strip()


def _marker_above(p):
    return any((d / '.aid' / 'state.json').is_file() or (d / '.aid' / 'hooks' / 'config.json').is_file()
               for d in [p] + list(p.parents))


@pytest.fixture
def clean_tmp(tmp_path):
    """
    A directory with no AID project marker above it (AC-27 harness). On a machine whose
    real ~/.aid/state.json sits above the temp dir (tests run with a fake HOME, so it is
    not excluded as AID_HOME), use a fresh directory at the drive root instead.
    """
    if not _marker_above(tmp_path):
        yield tmp_path
        return
    alt = Path(tempfile.mkdtemp(prefix='aid-t1-', dir=tmp_path.anchor))
    if _marker_above(alt):
        shutil.rmtree(alt, ignore_errors=True)
        pytest.skip('no directory without an AID marker ancestor is available')
    yield alt
    shutil.rmtree(alt, ignore_errors=True)


def parse(out):
    """Hook output is either empty (silent allow) or one JSON object."""
    return json.loads(out) if out else None


WRITE_SRC = {'tool_name': 'Write',
             'tool_input': {'file_path': 'src/app.ts', 'content': 'export const a = 1'}}


class TestPhaseGateWriteBlocks:
    """The headline feature: refuse source writes before the coding phase."""

    def test_block_emits_the_schema_claude_code_reads(self, tmp_path):
        p = make_project(tmp_path, phase=1, enforcement={'phase_gate_write': 'block'})
        got = parse(run_hook(p, 'PreToolUse', 'phase_gate_write', WRITE_SRC))

        assert got is not None, 'blocking emitted nothing, so the write was allowed'
        hso = got.get('hookSpecificOutput')
        assert hso, f'no hookSpecificOutput in {got}'
        assert hso.get('hookEventName') == 'PreToolUse', (
            'missing/incorrect hookEventName - Claude Code cannot route the payload '
            'and discards it, turning the block into an allow'
        )
        assert hso.get('permissionDecision') == 'deny', (
            f"expected permissionDecision=deny, got {hso!r}"
        )
        assert hso.get('permissionDecisionReason'), 'a denial must explain itself'

    def test_the_old_broken_shape_is_gone(self, tmp_path):
        """Red-check: this is the exact payload that made the gate a no-op."""
        p = make_project(tmp_path, phase=1, enforcement={'phase_gate_write': 'block'})
        hso = parse(run_hook(p, 'PreToolUse', 'phase_gate_write', WRITE_SRC))['hookSpecificOutput']
        assert 'decision' not in hso, (
            'hookSpecificOutput.decision is not a field Claude Code reads for PreToolUse'
        )
        assert 'reason' not in hso, 'the reason field must be permissionDecisionReason'

    @pytest.mark.parametrize('path', ['docs/prd.md', '.aid/state.json',
                                      'testing/e2e/test_x.py', 'features/login.feature'])
    def test_allowed_prefixes_are_not_blocked(self, tmp_path, path):
        """Writing docs during Phase 1 is the whole point of Phase 1."""
        p = make_project(tmp_path, phase=1, enforcement={'phase_gate_write': 'block'})
        out = run_hook(p, 'PreToolUse', 'phase_gate_write',
                       {'tool_name': 'Write', 'tool_input': {'file_path': path}})
        got = parse(out)
        denied = got and got.get('hookSpecificOutput', {}).get('permissionDecision') == 'deny'
        assert not denied, f'{path} is an allowed prefix but was denied'

    def test_coding_phase_allows_source_writes(self, tmp_path):
        p = make_project(tmp_path, phase=4, enforcement={'phase_gate_write': 'block'})
        got = parse(run_hook(p, 'PreToolUse', 'phase_gate_write', WRITE_SRC))
        denied = got and got.get('hookSpecificOutput', {}).get('permissionDecision') == 'deny'
        assert not denied, 'Phase 4 is the coding phase; writes must pass'

    def test_uninitialised_project_never_blocks(self, clean_tmp):
        """No .aid/ at all: AID is not in use here, so stay out of the way."""
        got = parse(run_hook(clean_tmp,'PreToolUse', 'phase_gate_write', WRITE_SRC))
        denied = got and got.get('hookSpecificOutput', {}).get('permissionDecision') == 'deny'
        assert not denied

    def test_shipped_default_blocks_in_an_aid_project(self, tmp_path):
        """
        # T2 (owner 2026-11-16): default is block. Flipped from
        # test_shipped_default_is_log_not_block. Uninitialised projects stay untouched
        # (test_uninitialised_project_never_blocks / AC-27).
        """
        p = make_project(tmp_path, phase=1)  # no enforcement config
        got = parse(run_hook(p, 'PreToolUse', 'phase_gate_write', WRITE_SRC))
        assert got and got['hookSpecificOutput'].get('permissionDecision') == 'deny', (
            'default phase_gate_write must be "block"')


class TestContextInjection:
    """additionalContext is dropped without hookEventName - the second silent bug."""

    def test_warn_level_names_its_event(self, tmp_path):
        p = make_project(tmp_path, phase=1, enforcement={'phase_gate_write': 'warn'})
        got = parse(run_hook(p, 'PreToolUse', 'phase_gate_write', WRITE_SRC))
        assert got, 'warn emitted nothing, so the warning never reached Claude'
        hso = got['hookSpecificOutput']
        assert hso.get('hookEventName') == 'PreToolUse', (
            'without hookEventName the warning is silently discarded'
        )
        assert hso.get('additionalContext'), 'warn must carry the message'

    def test_session_start_injection_names_its_event(self, tmp_path):
        p = make_project(tmp_path, phase=2)
        got = parse(run_hook(p, 'SessionStart', payload={'session_id': 'test'}))
        if got is None:
            pytest.skip('this project state produces no SessionStart context')
        hso = got.get('hookSpecificOutput', {})
        assert hso.get('hookEventName') == 'SessionStart', (
            f'SessionStart context must name its event, got {hso!r}'
        )


class TestStopEvent:
    def test_stop_block_uses_top_level_decision(self, tmp_path):
        """
        Stop is the one event that does NOT use hookSpecificOutput: it reads a top-level
        {"decision": "block", "reason": ...}. This path was always correct - pin it so a
        well-meaning refactor does not "consistency-fix" it into the broken shape.
        """
        p = make_project(tmp_path, phase=4, enforcement={'quality_check_verifier': 'block'})
        got = parse(run_hook(p, 'Stop', 'quality_check', {'stop_hook_active': False}))
        if got is None:
            pytest.skip('no quality-check violation in this fixture')
        if 'decision' in got:
            assert got['decision'] == 'block'
            assert got.get('reason'), 'a Stop block must explain itself'


class TestRobustness:
    @pytest.mark.parametrize('junk', ['', 'not json', '[]', '{"tool_input": null}'])
    def test_garbage_stdin_never_crashes(self, tmp_path, junk):
        """A hook that dies on malformed input takes the user's session with it.
        In block mode the gate may DENY malformed input (fail closed), but it still
        exits 0 with a readable payload."""
        p = make_project(tmp_path, phase=1, enforcement={'phase_gate_write': 'block'})
        proc = subprocess.run(
            [sys.executable, HOOK, '--event', 'PreToolUse', '--action', 'phase_gate_write'],
            input=junk, capture_output=True, text=True, timeout=60, cwd=str(p))
        assert proc.returncode == 0, f'crashed on {junk!r}: {proc.stderr[:300]}'

    def test_every_output_is_valid_json_or_empty(self, tmp_path):
        p = make_project(tmp_path, phase=1, enforcement={'phase_gate_write': 'block'})
        for event, action in [('PreToolUse', 'phase_gate_write'),
                              ('PreToolUse', 'phase_gate_bash'),
                              ('PostToolUse', 'audit_log'),
                              ('SessionStart', None),
                              ('UserPromptSubmit', None)]:
            out = run_hook(p, event, action, {'tool_name': 'Bash',
                                              'tool_input': {'command': 'npm run dev'}})
            if out:
                json.loads(out)  # raises if the hook emitted garbage

# ---------------------------------------------------------------------------
# Phase-gate hardening: bypasses found in the audit (D-01..D-05, D-10, D-12).
# Each case EXECUTES the hook with the attack input and asserts the decision.
# ---------------------------------------------------------------------------

PLUGIN_SESSION = os.path.join(REPO_ROOT, 'hooks', 'aid_session.py')


def run_gate(project, action, tool_input, env=None):
    full_env = dict(os.environ)
    full_env.pop('CLAUDE_CONFIG_DIR', None)
    full_env.update(env or {})
    proc = subprocess.run(
        [sys.executable, HOOK, '--event', 'PreToolUse', '--action', action],
        input=json.dumps({'tool_name': 'Bash' if action == 'phase_gate_bash' else 'Write',
                          'tool_input': tool_input}),
        capture_output=True, text=True, timeout=60, cwd=str(project), env=full_env)
    assert proc.returncode == 0, proc.stderr[:500]
    got = parse(proc.stdout.strip())
    return bool(got) and got.get('hookSpecificOutput', {}).get('permissionDecision') == 'deny'


def bash_denied(project, command):
    return run_gate(project, 'phase_gate_bash', {'command': command})


BASH_BYPASSES = [
    'git status && node evil.js',          # allow-list prefix, then a chained runner
    'ls; python3 -c "print(1)"',
    'echo aid_session.py; node evil.js',   # old aid_session.py substring allow
    'cat evil.js | node',                  # "node " pattern needed a trailing space
    'node\tevil.js',                       # tab instead of space
    'echo $(node evil.js)',
    'echo "`node evil.js`"',
    'mkdir -p x\nnode evil.js',
    'git log || bash -c "node evil.js"',
    'FOO=1 timeout 5 node evil.js',
    'py -3 evil.py',
    'bun evil.ts', 'deno run evil.ts', 'tsx evil.ts', 'ts-node evil.ts',
    'pnpm exec tsx evil.ts', 'yarn exec evil', 'uv run evil.py',
    'python3.11 evil.py', 'C:/tools/node/node.exe evil.js',
    'npm --prefix app run dev',
    'python hooks/aid_session.py roles',   # the PROJECT's copy, not the plugin's
    'python "{plugin}" roles && node evil.js',
    'python "{plugin}" roles > .aid/hooks/config.json',
    './python "{plugin}" roles',
]

BASH_LEGIT = [
    'git status', 'ls -la', 'grep -rn "node " docs',
    'git commit -m "docs; node is mentioned here"', 'ls node_modules', 'mkdir -p docs/x',
    'python "{plugin}" roles',
]
# Former BASH_LEGIT entries the T1 acceptance contract now denies (AC-52, AC-8, AC-23).
BASH_FLIPPED = [  # owner decision 2026-11-16: deny outright before Phase 4
    'npm install', 'pip install requests',
    'python "${{CLAUDE_PLUGIN_ROOT}}/hooks/aid_session.py" start developer 1',
    'python "${{CLAUDE_PLUGIN_ROOT}}/hooks/aid_session.py" phases 3     # role name',
    'python "${{CLAUDE_PLUGIN_ROOT}}/hooks/aid_session.py" end --rating 4 --worked "tests & docs; fine"',
]


class TestBashGateHardening:
    @pytest.mark.parametrize('command', BASH_BYPASSES)
    def test_bypass_is_denied_in_block_mode(self, tmp_path, command):
        p = make_project(tmp_path, phase=1, enforcement={'phase_gate_bash': 'block'})
        (p / 'hooks').mkdir()
        (p / 'hooks' / 'aid_session.py').write_text('print("project code")', encoding='utf-8')
        assert bash_denied(p, command.format(plugin=PLUGIN_SESSION)), (
            f'{command!r} runs code before Phase 4 but the gate allowed it')

    @pytest.mark.parametrize('command', BASH_FLIPPED)
    def test_flipped_former_allow_is_denied(self, tmp_path, command):
        p = make_project(tmp_path, phase=1, enforcement={'phase_gate_bash': 'block'})
        assert bash_denied(p, command.format(plugin=PLUGIN_SESSION))

    @pytest.mark.parametrize('command', BASH_LEGIT)
    def test_legit_command_is_allowed(self, tmp_path, command):
        p = make_project(tmp_path, phase=1, enforcement={'phase_gate_bash': 'block'})
        assert not bash_denied(p, command.format(plugin=PLUGIN_SESSION)), (
            f'{command!r} is a legitimate Phase 1 command but was denied')

    def test_coding_phase_allows_runners(self, tmp_path):
        p = make_project(tmp_path, phase=4, enforcement={'phase_gate_bash': 'block'})
        assert not bash_denied(p, 'git status && node app.js')


class TestWriteGateHardening:
    @pytest.mark.parametrize('path', [
        'docs/../src/app.ts',                  # traversal out of an allowed prefix
        'docs/../../outside/app.ts',           # traversal out of the project
        'src/.claude/plans/app.ts',            # old ".claude/plans/" substring allow
        'src/.claude/plans/../../app.ts',
    ])
    def test_traversal_and_substring_writes_are_denied(self, tmp_path, path):
        proj = tmp_path / 'proj'
        proj.mkdir()
        p = make_project(proj, phase=1, enforcement={'phase_gate_write': 'block'})
        home = tmp_path / 'home'
        assert run_gate(p, 'phase_gate_write', {'file_path': path},
                        env={'HOME': str(home), 'USERPROFILE': str(home)})

    def test_real_plan_file_is_allowed(self, tmp_path):
        proj = tmp_path / 'proj'
        proj.mkdir()
        p = make_project(proj, phase=1, enforcement={'phase_gate_write': 'block'})
        home = tmp_path / 'home'
        plan = home / '.claude' / 'plans' / 'my-plan.md'
        assert not run_gate(p, 'phase_gate_write', {'file_path': str(plan)},
                            env={'HOME': str(home), 'USERPROFILE': str(home)})

    @pytest.mark.skipif(os.name != 'nt', reason='case-insensitive / backslash paths are Windows-only')
    @pytest.mark.parametrize('path', ['DOCS\\prd.md', 'Docs/prd.md', 'docs\\sub\\x.md'])
    def test_windows_spelling_of_allowed_prefix_is_allowed(self, tmp_path, path):
        p = make_project(tmp_path, phase=1, enforcement={'phase_gate_write': 'block'})
        assert not run_gate(p, 'phase_gate_write', {'file_path': path})


class TestFailClosed:
    """D-12: in block mode, a gate that cannot read its inputs must deny, not allow."""

    BLOCK = json.dumps({'enforcement': {'phase_gate_write': 'block', 'phase_gate_bash': 'block'}})
    LOG = json.dumps({'enforcement': {'phase_gate_write': 'log', 'phase_gate_bash': 'log'}})

    @staticmethod
    def _project(tmp_path, state_text, config_text=None):
        aid = tmp_path / '.aid'
        (aid / 'hooks').mkdir(parents=True)
        (aid / 'state.json').write_text(state_text, encoding='utf-8')
        if config_text is not None:
            (aid / 'hooks' / 'config.json').write_text(config_text, encoding='utf-8')
        return tmp_path

    @pytest.mark.parametrize('state', ['{not json', '[]', '{"current_phase": "one"}'])
    def test_malformed_state_denies_in_block_mode(self, tmp_path, state):
        p = self._project(tmp_path, state, self.BLOCK)
        assert run_gate(p, 'phase_gate_write', {'file_path': 'src/app.ts'})
        assert run_gate(p, 'phase_gate_bash', {'command': 'node app.js'})

    def test_malformed_state_still_allows_in_log_mode(self, tmp_path):
        p = self._project(tmp_path, '{not json', self.LOG)
        assert not run_gate(p, 'phase_gate_write', {'file_path': 'src/app.ts'})

    def test_malformed_config_fails_closed(self, tmp_path):
        p = self._project(tmp_path, '{"current_phase": 1}', '{broken')
        assert run_gate(p, 'phase_gate_bash', {'command': 'node app.js'})
        assert not run_gate(p, 'phase_gate_bash', {'command': 'git status'})

    @pytest.mark.parametrize('level', ['BLOCK', ' Block ', 'deny'])
    def test_level_is_case_insensitive_and_unknown_fails_closed(self, tmp_path, level):
        cfg = json.dumps({'enforcement': {'phase_gate_bash': level}})
        p = self._project(tmp_path, '{"current_phase": 1}', cfg)
        assert run_gate(p, 'phase_gate_bash', {'command': 'node app.js'})

    def test_null_tool_input_denies_in_block_mode(self, tmp_path):
        p = self._project(tmp_path, '{"current_phase": 1}', self.BLOCK)
        assert run_gate(p, 'phase_gate_bash', None)

    def test_deleting_state_does_not_switch_a_block_config_off(self, tmp_path):
        """Design review MAJOR 3: block config + no state.json = phase 0, still gated."""
        (tmp_path / '.aid' / 'hooks').mkdir(parents=True)
        (tmp_path / '.aid' / 'hooks' / 'config.json').write_text(self.BLOCK, encoding='utf-8')
        assert run_gate(tmp_path, 'phase_gate_bash', {'command': 'node app.js'})
        (tmp_path / '.aid' / 'state.json').write_text('{"current_phase": null}', encoding='utf-8')
        assert run_gate(tmp_path, 'phase_gate_bash', {'command': 'node app.js'})

    def test_project_without_aid_is_untouched(self, clean_tmp):
        """No .aid/ at all = AID not in use here: stay out of the way."""
        assert not run_gate(clean_tmp, 'phase_gate_bash', {'command': 'node app.js'})
        assert not run_gate(clean_tmp, 'phase_gate_write', {'file_path': 'src/app.ts'})


class TestProtectedPaths:
    """
    A-02: the agent being gated must not be able to switch its own gates off.
    Writes into the gate control files are denied in EVERY phase (also Phase 4+),
    through the Write tool and through Bash; reading them stays allowed.
    """

    PROTECTED_WRITES = [
        '.aid/hooks/config.json',
        '.aid/hooks/new.json',
        '.aid/pipeline/ESCALATION.json',
        '.claude/settings.json',
        '.claude/settings.local.json',
        '.claude/hooks/evil.sh',
        'docs/../.aid/hooks/config.json',      # traversal from an allowed prefix
    ]

    BASH_WRITES = [
        'echo {} > .aid/hooks/config.json',
        'echo {"current_phase":4} >.aid/hooks/config.json',
        'printf x >> .claude/settings.json',
        'cp /dev/null .aid/hooks/config.json',
        'rm -f .aid/hooks/config.json',
        'mv x.json .claude/settings.local.json',
        'git status && tee .aid/hooks/config.json < x',
        "sed -i 's/block/log/' .aid/hooks/config.json",
        'rm -rf .claude/hooks',
    ]

    BASH_READS = [
        'cat .aid/hooks/config.json',
        'grep block .aid/hooks/config.json',
        'ls .claude/hooks',
    ]
    # owner decision 2026-11-16: deny outright before Phase 4 (redirect to a file, AC-4)
    BASH_READS_FLIPPED = ['cat .claude/settings.json > docs/settings-copy.json']

    @pytest.mark.parametrize('command', BASH_READS_FLIPPED)
    def test_flipped_read_with_redirect_is_denied(self, tmp_path, command):
        p = make_project(tmp_path, phase=1, enforcement={'phase_gate_bash': 'block'})
        assert bash_denied(p, command)

    @pytest.mark.parametrize('phase', [1, 4])
    @pytest.mark.parametrize('path', PROTECTED_WRITES)
    def test_write_tool_cannot_change_gate_files(self, tmp_path, path, phase):
        p = make_project(tmp_path, phase=phase,
                         enforcement={'phase_gate_write': 'block', 'phase_gate_bash': 'block'})
        assert run_gate(p, 'phase_gate_write', {'file_path': path}), (
            f'Write to {path!r} in phase {phase} would let the agent disable its gates')

    def test_absolute_path_to_gate_file_is_denied(self, tmp_path):
        p = make_project(tmp_path, phase=4, enforcement={'phase_gate_write': 'block'})
        assert run_gate(p, 'phase_gate_write',
                        {'file_path': str(p / '.aid' / 'hooks' / 'config.json')})

    @pytest.mark.parametrize('phase', [1, 4])
    @pytest.mark.parametrize('command', BASH_WRITES)
    def test_bash_cannot_change_gate_files(self, tmp_path, command, phase):
        p = make_project(tmp_path, phase=phase,
                         enforcement={'phase_gate_write': 'block', 'phase_gate_bash': 'block'})
        assert bash_denied(p, command), (
            f'{command!r} in phase {phase} would let the agent disable its gates')

    @pytest.mark.parametrize('command', BASH_READS)
    def test_reading_gate_files_is_allowed(self, tmp_path, command):
        p = make_project(tmp_path, phase=1, enforcement={'phase_gate_bash': 'block'})
        assert not bash_denied(p, command)

    @pytest.mark.parametrize('path', ['.aid/state.json', '.aid/qa/T1.yaml', 'docs/prd.md',
                                      '.claude/plans/x.md', '.claude/commands/x.md'])
    def test_other_aid_and_claude_files_stay_writable(self, tmp_path, path):
        """.aid/state.json stays writable until T3 moves phase-approve/advance into aid_session.py."""
        p = make_project(tmp_path, phase=1, enforcement={'phase_gate_write': 'block'})
        assert not run_gate(p, 'phase_gate_write', {'file_path': path})

    def test_uninitialised_project_is_untouched(self, clean_tmp):
        """No .aid/state.json: AID is not in use here, so the gate stays out of the way."""
        assert not run_gate(clean_tmp, 'phase_gate_write', {'file_path': '.claude/settings.json'})


# ===========================================================================
# T1 acceptance criteria (T1-acceptance.md) for the hook plumbing: AC-27, AC-38..AC-42,
# AC-45, AC-48. Every case spawns hooks/aid_hooks.py with stdin JSON, as Claude Code does.
# ===========================================================================

sys.path.insert(0, os.path.join(REPO_ROOT, 'hooks'))
import aid_guard  # noqa: E402

BLOCK_CFG = {'enforcement': {'phase_gate_write': 'block', 'phase_gate_bash': 'block'}}


def spawn(cwd, event, action, home, payload=None, raw=None, project_dir=None):
    env = dict(os.environ, HOME=str(home), USERPROFILE=str(home), AID_HOME=str(Path(home) / '.aid'))
    env.pop('CLAUDE_PROJECT_DIR', None)
    if project_dir:
        env['CLAUDE_PROJECT_DIR'] = str(project_dir)
    env.pop('CLAUDE_CONFIG_DIR', None)
    args = [sys.executable, HOOK, '--event', event] + (['--action', action] if action else [])
    p = subprocess.run(args, input=raw if raw is not None else json.dumps(payload), capture_output=True,
                       text=True, cwd=str(cwd), env=env, timeout=60)
    assert p.returncode == 0, p.stderr[-400:]
    return p.stdout.strip()


def decision(out):
    """('DENY', reason) / ('ALLOW', additionalContext-or-None)."""
    if not out:
        return 'ALLOW', None
    hso = json.loads(out).get('hookSpecificOutput', {})
    if hso.get('permissionDecision') == 'deny':
        assert hso.get('hookEventName') == 'PreToolUse' and hso.get('permissionDecisionReason')
        return 'DENY', hso['permissionDecisionReason']
    return 'ALLOW', hso.get('additionalContext')


class AC(object):
    """Common-harness project P (git repo, block config) plus fake home H."""

    def __init__(self, base, config=BLOCK_CFG):
        self.P, self.H = base / 'proj', base / 'home'
        for d in ('.aid/hooks', '.claude', 'docs'):
            (self.P / d).mkdir(parents=True, exist_ok=True)
        self.H.mkdir(exist_ok=True)
        subprocess.run(['git', 'init', '-q', str(self.P)], check=True, capture_output=True)
        self.state(1)
        self.config(config)
        (self.P / '.claude' / 'settings.json').write_text('{}', encoding='utf-8')

    def state(self, phase):
        (self.P / '.aid' / 'state.json').write_text(json.dumps({'current_phase': phase}), encoding='utf-8')

    def config(self, cfg):
        (self.P / '.aid' / 'hooks' / 'config.json').write_text(
            cfg if isinstance(cfg, str) else json.dumps(cfg), encoding='utf-8')

    def level(self, level):
        self.config({'enforcement': {'phase_gate_write': level, 'phase_gate_bash': level}})

    def start(self, sid, source='startup'):
        out = spawn(self.P, 'SessionStart', None, self.H,
                    {'session_id': sid, 'source': source, 'cwd': str(self.P)})
        return json.loads(out)['hookSpecificOutput']['additionalContext'] if out else ''

    def bash(self, cmd, sid='s1'):
        return decision(spawn(self.P, 'PreToolUse', 'phase_gate_bash', self.H, {
            'session_id': sid, 'cwd': str(self.P), 'tool_name': 'Bash', 'tool_input': {'command': cmd}}))

    def write(self, path, sid='s1'):
        return decision(spawn(self.P, 'PreToolUse', 'phase_gate_write', self.H, {
            'session_id': sid, 'cwd': str(self.P), 'tool_name': 'Write', 'tool_input': {'file_path': path}}))

    def raw(self, action, text):
        return decision(spawn(self.P, 'PreToolUse', action, self.H, raw=text))


@pytest.fixture
def acp(clean_tmp):
    return AC(clean_tmp)


def test_ac_27_non_aid_project_is_left_alone(clean_tmp):
    D = clean_tmp / 'D'
    (D / '.aid' / 'hooks').mkdir(parents=True)
    (D / '.aid' / 'state.json').write_text('{"current_phase":1}', encoding='utf-8')
    (D / '.aid' / 'hooks' / 'config.json').write_text(json.dumps(BLOCK_CFG), encoding='utf-8')
    A = D / 'A'
    (A / '.aid' / 'audit').mkdir(parents=True)              # stray: no state, no config
    Q = A / 'q'
    Q.mkdir()
    subprocess.run(['git', 'init', '-q', str(Q)], check=True, capture_output=True)

    def bash(cmd):
        return decision(spawn(Q, 'PreToolUse', 'phase_gate_bash', D, {
            'session_id': 's1', 'cwd': str(Q), 'tool_name': 'Bash', 'tool_input': {'command': cmd}}))

    assert bash('node x.js')[0] == 'ALLOW'
    assert decision(spawn(Q, 'PreToolUse', 'phase_gate_write', D, {
        'session_id': 's1', 'cwd': str(Q), 'tool_name': 'Write',
        'tool_input': {'file_path': str(Q / 'src' / 'x.ts')}}))[0] == 'ALLOW'
    start = {'session_id': 's1', 'source': 'startup', 'cwd': str(Q)}
    spawn(Q, 'SessionStart', None, D, start)
    assert not (Q / '.claude' / 'settings.json').exists()
    assert not (D / '.claude' / 'settings.json').exists()
    assert not (Q / '.aid').exists()
    (Q / '.claude').mkdir()
    (Q / '.claude' / 'settings.json').write_text('{"x":1}', encoding='utf-8')
    spawn(Q, 'SessionStart', None, D, start)
    assert (Q / '.claude' / 'settings.json').read_bytes() == b'{"x":1}'
    assert not (Q / '.aid').exists()
    # Positive control (monorepo): an ancestor that IS an AID project still gates.
    (A / '.aid' / 'hooks').mkdir()
    (A / '.aid' / 'state.json').write_text('{"current_phase":1}', encoding='utf-8')
    (A / '.aid' / 'hooks' / 'config.json').write_text(json.dumps(BLOCK_CFG), encoding='utf-8')
    assert bash('node x.js')[0] == 'DENY'


def test_ac_27_home_dir_is_never_an_aid_root_when_aid_home_moves(clean_tmp):
    """Review T1-fix1 MAJOR: with AID_HOME moved elsewhere, the user-level ~/.aid/state.json
    made ~ an AID root, so every non-AID project under ~ was gated and SessionStart rewrote
    ~/.claude/settings.json. The home dir must never be an AID project."""
    D = clean_tmp / 'D'
    (D / '.aid' / 'hooks').mkdir(parents=True)
    (D / '.aid' / 'state.json').write_text('{"current_phase":1}', encoding='utf-8')
    (D / '.aid' / 'hooks' / 'config.json').write_text(json.dumps(BLOCK_CFG), encoding='utf-8')
    Q = D / 'q'
    Q.mkdir()
    env = dict(os.environ, HOME=str(D), USERPROFILE=str(D), AID_HOME=str(clean_tmp / 'elsewhere'))
    env.pop('CLAUDE_PROJECT_DIR', None)
    env.pop('CLAUDE_CONFIG_DIR', None)

    def run(event, action, payload):
        args = [sys.executable, HOOK, '--event', event] + (['--action', action] if action else [])
        p = subprocess.run(args, input=json.dumps(payload), capture_output=True, text=True,
                           cwd=str(Q), env=env, timeout=60)
        assert p.returncode == 0, p.stderr[-400:]
        return p.stdout.strip()

    assert decision(run('PreToolUse', 'phase_gate_bash', {
        'session_id': 's1', 'cwd': str(Q), 'tool_name': 'Bash',
        'tool_input': {'command': 'node x.js'}}))[0] == 'ALLOW'
    run('SessionStart', None, {'session_id': 's1', 'source': 'startup', 'cwd': str(Q)})
    assert not (D / '.claude' / 'settings.json').exists()


def test_ac_38_session_start_installs_deny_rules_and_nothing_else(acp):
    s = acp.P / '.claude' / 'settings.json'
    s.write_text(json.dumps({'permissions': {'deny': ['Bash(rm:*)']}, 'x': 1}), encoding='utf-8')
    acp.start('s1')
    data = json.loads(s.read_text(encoding='utf-8'))
    assert all(r in data['permissions']['deny'] for r in aid_guard.DENY_RULES)
    assert 'Bash(rm:*)' in data['permissions']['deny'] and data['x'] == 1
    assert set(data) == {'permissions', 'x'} and set(data['permissions']) == {'deny'}
    before = s.read_bytes()
    acp.start('s1')
    assert s.read_bytes() == before


@pytest.mark.parametrize('name', ['settings.json', 'settings.local.json'])
def test_ac_38_disable_all_hooks_is_kept_and_warned(acp, name):
    f = acp.P / '.claude' / name
    f.write_text(json.dumps({'disableAllHooks': True}), encoding='utf-8')
    out = acp.start('s1')
    assert json.loads(f.read_text(encoding='utf-8'))['disableAllHooks'] is True
    assert 'WARNING' in out and name in out and 'disableAllHooks' in out, out


def test_ac_39_malformed_settings_left_alone_with_warning(acp):
    s = acp.P / '.claude' / 'settings.json'
    s.write_text('{bad', encoding='utf-8')
    out = acp.start('s1')
    assert s.read_bytes() == b'{bad'
    assert 'WARNING' in out and 'could not install' in out, out


def _disable(acp, case, value=True):
    if case == 'project_disable':
        f = acp.P / '.claude' / 'settings.json'
        data = json.loads(f.read_text(encoding='utf-8'))
        if value is None:
            data.pop('disableAllHooks', None)
        else:
            data['disableAllHooks'] = value
        f.write_text(json.dumps(data), encoding='utf-8')
        return
    f = acp.P / '.claude' / 'settings.local.json'
    if value is None:
        f.unlink()
    elif case == 'local_disable':
        f.write_text(json.dumps({'disableAllHooks': value}), encoding='utf-8')
    else:
        f.write_text(json.dumps({'enabledPlugins': {'aid@AID': not value}}), encoding='utf-8')


@pytest.mark.parametrize('case', ['local_disable', 'local_plugin', 'project_disable'])
def test_ac_40_disabling_hooks_mid_session_denies_in_block_baseline(acp, case):
    acp.start('s1')
    assert acp.bash('ls')[0] == 'ALLOW'
    _disable(acp, case)
    for phase in (1, 5):
        acp.state(phase)
        v = acp.bash('ls')
        assert v[0] == 'DENY' and 'disabled' in v[1] and 'reloaded' in v[1], (phase, v)
        assert acp.write('docs/a.md')[0] == 'DENY', phase
    _disable(acp, case, None)
    assert acp.bash('ls')[0] == 'ALLOW'
    _disable(acp, case, False)
    assert acp.bash('ls')[0] == 'ALLOW'
    assert acp.write('docs/a.md')[0] == 'ALLOW'


def test_ac_41_deleted_baseline_is_not_re_trusted(acp):
    """
    WHY: Phase 4+ code could set the gate config to log AND delete the integrity dir in
    one command; with first-use trust the next call took a new baseline and allowed
    (review 3, MAJOR). A session SessionStart recorded must not be re-trusted.
    """
    import shutil
    acp.start('s1')
    acp.state(5)
    assert acp.bash('ls')[0] == 'ALLOW'
    acp.level('log')
    shutil.rmtree(acp.H / '.aid' / 'integrity')
    v = acp.bash('ls')
    assert v[0] == 'DENY' and 'disappeared' in v[1], v
    assert acp.write('docs/a.md')[0] == 'DENY'
    # Still deleted on the next call: no silent re-trust after the first deny.
    assert acp.bash('ls')[0] == 'DENY'
    # A session SessionStart never saw keeps first-use trust; a restart recovers.
    assert acp.bash('ls', sid='s9')[0] == 'ALLOW'
    acp.start('s2')
    assert acp.bash('ls', sid='s2')[0] == 'ALLOW'


def test_ac_40_warn_baseline_warns(acp):
    acp.level('warn')
    acp.start('s1')
    _disable(acp, 'local_disable')
    for phase in (1, 5):
        acp.state(phase)
        for v in (acp.bash('ls'), acp.write('docs/a.md')):
            assert v[0] == 'ALLOW' and 'AID ENFORCEMENT WARNING' in v[1] and 'disabled' in v[1], v


def test_ac_40_log_baseline_logs(acp):
    acp.level('log')
    acp.start('s1')
    _disable(acp, 'local_disable')
    audit = acp.P / '.aid' / 'audit' / 'tool-usage.jsonl'
    for phase in (1, 5):
        acp.state(phase)
        for call in (lambda: acp.bash('ls'), lambda: acp.write('docs/a.md')):
            n = len(audit.read_text(encoding='utf-8').splitlines()) if audit.exists() else 0
            assert call() == ('ALLOW', None)
            lines = audit.read_text(encoding='utf-8').splitlines()
            assert len(lines) == n + 1 and json.loads(lines[-1]).get('integrity') is True


def test_ac_42_weakening_between_sessions_is_reported(acp):
    acp.start('s1')
    acp.level('log')
    out = acp.start('s2')
    assert 'WARNING' in out, out
    assert 'phase_gate_bash went from block to log' in out and 'phase_gate_write went from block to log' in out
    assert 'weaker' not in acp.start('s3')                  # nothing changed
    acp.level('block')
    assert 'weaker' not in acp.start('s4')                  # stronger


AC45_DENY = [
    ('{not json', BLOCK_CFG, 'git status'), ('[1]', BLOCK_CFG, 'git status'),
    ('{"current_phase":"one"}', BLOCK_CFG, 'git status'), ('{"current_phase":1}', '{bad', 'node x.js'),
    ('{"current_phase":1}', {'enforcement': {'phase_gate_bash': 'BLOCK '}}, 'node x.js'),
    ('{"current_phase":1}', {'enforcement': {'phase_gate_bash': 'blokc'}}, 'node x.js'),
    ('{"current_phase":3}', dict(BLOCK_CFG, phase_gate_rules={'code_execute_min_phase': 'four'}), 'node x.js'),
    ('{"current_phase":3}', dict(BLOCK_CFG, phase_gate_rules={'code_execute_min_phase': '4'}), 'node x.js'),
]


@pytest.mark.parametrize('state,cfg,cmd', AC45_DENY)
def test_ac_45_fail_closed_inputs_deny(acp, state, cfg, cmd):
    (acp.P / '.aid' / 'state.json').write_text(state, encoding='utf-8')
    acp.config(cfg)
    assert acp.bash(cmd)[0] == 'DENY'


@pytest.mark.parametrize('action,raw', [
    ('phase_gate_bash', 'not json'), ('phase_gate_bash', '{"tool_name":"Bash","tool_input":null}'),
    ('phase_gate_bash', '{"tool_name":"Bash","tool_input":{"command":["node","x"]}}'),
    ('phase_gate_write', '{"tool_name":"Write","tool_input":{"file_path":123}}'),
    ('phase_gate_write', '{"tool_name":"Write","tool_input":{"file_path":"src/a\\u0000.ts"}}')])
def test_ac_45_malformed_stdin_denies(acp, action, raw):
    assert acp.raw(action, raw)[0] == 'DENY'


def test_ac_45_numeric_string_is_coerced_and_log_allows_garbage(acp):
    acp.config(dict(BLOCK_CFG, phase_gate_rules={'code_execute_min_phase': '4'}))
    acp.state(4)
    assert acp.bash('node x.js')[0] == 'ALLOW'
    acp.level('log')
    assert acp.raw('phase_gate_bash', 'not json')[0] == 'ALLOW'


def test_ac_48_deny_message_gives_a_way_forward(acp):
    v = acp.bash('npm install')
    assert v[0] == 'DENY'
    for part in ('Write tool', '/gate-check', '/phase-advance', 'extra_allowed_commands'):
        assert part in v[1], (part, v[1])
    assert 'package installs are allowed' not in v[1]


# ===========================================================================
# T1b (T1-acceptance.md section 7): AC-27ext, AC-38ext, AC-43 latch, AC-44 encoding,
# plus T1a follow-ups F1 (~user Write paths) and F2 (mkdir options).
# ===========================================================================

@pytest.mark.parametrize('where', ['project', 'home'])
def test_ac_27ext_session_start_in_non_aid_project_keeps_markers(clean_tmp, where):
    """
    WHY: SessionStart cleared .aid/markers before checking that AID is in use, so it
    deleted files in projects (and the home dir) that never opted into AID (AC-27ext).
    """
    D = clean_tmp / 'D'
    (D / '.aid' / 'hooks').mkdir(parents=True)
    (D / '.aid' / 'state.json').write_text('{"current_phase":1}', encoding='utf-8')
    (D / '.aid' / 'hooks' / 'config.json').write_text(json.dumps(BLOCK_CFG), encoding='utf-8')
    Q = D / 'q' if where == 'project' else D        # home: its .aid is AID_HOME, not a root
    marker = Q / '.aid' / 'markers' / 'x.marker'
    marker.parent.mkdir(parents=True)
    marker.write_bytes(b'keep me')
    spawn(Q, 'SessionStart', None, D, {'session_id': 's1', 'source': 'startup', 'cwd': str(Q)})
    assert marker.read_bytes() == b'keep me'
    assert sorted(p.name for p in marker.parent.iterdir()) == ['x.marker']
    assert not (Q / '.claude').exists()


def test_ac_38ext_config_only_root_gets_deny_rules(acp):
    """WHY: layer A was installed only when state.json existed, so a project configured
    with just .aid/hooks/config.json had no permission deny rules (AC-38ext)."""
    (acp.P / '.aid' / 'state.json').unlink()
    acp.start('s1')
    data = json.loads((acp.P / '.claude' / 'settings.json').read_text(encoding='utf-8'))
    assert all(r in data['permissions']['deny'] for r in aid_guard.DENY_RULES), data


def _latched(acp, level):
    acp.level(level)
    acp.state(5)
    acp.start('s1')
    assert acp.bash('ls') == ('ALLOW', None)
    (acp.P / '.aid').rename(acp.P / '.aid-off')        # what Phase 4+ Bash can do


def test_ac_43_latch_denies_after_aid_markers_disappear(acp):
    """
    WHY: renaming .aid mid-session made the project "non-AID", so every gate stepped
    aside (in-scope bypass: a mid-session change the next call does not deny).
    """
    _latched(acp, 'block')
    v = acp.bash('ls')
    assert v[0] == 'DENY' and 'disappeared mid-session' in v[1], v
    v = acp.write(str(acp.P / 'docs' / 'a.md'))
    assert v[0] == 'DENY' and 'disappeared mid-session' in v[1], v
    assert not (acp.P / '.aid').exists()                # the denial wrote nothing into P
    # AC-27 still holds: a session with no baseline here is a non-AID session.
    assert acp.bash('ls', sid='s2') == ('ALLOW', None)
    (acp.P / '.aid-off').rename(acp.P / '.aid')
    assert acp.bash('ls') == ('ALLOW', None)
    assert acp.write(str(acp.P / 'docs' / 'a.md')) == ('ALLOW', None)


def test_ac_43_latch_warn_baseline_warns(acp):
    _latched(acp, 'warn')
    for v in (acp.bash('ls'), acp.write(str(acp.P / 'docs' / 'a.md'))):
        assert v[0] == 'ALLOW' and 'AID ENFORCEMENT WARNING' in v[1] and 'disappeared' in v[1], v


def test_ac_43_latch_log_baseline_allows_and_skips_missing_audit(acp):
    _latched(acp, 'log')
    assert acp.bash('ls') == ('ALLOW', None)
    assert acp.write(str(acp.P / 'docs' / 'a.md')) == ('ALLOW', None)
    assert not (acp.P / '.aid').exists()                # audit dir gone: skipped, not recreated


def test_ac_43_latch_log_baseline_writes_audit_line_when_audit_dir_survives(acp):
    """
    WHY (T1b review 3 MAJOR): with only the markers deleted and .aid/audit kept,
    audit_log_entry bailed on aid_in_use() and the latched root logged nothing, although in
    log mode that line is the only trace AID was switched off (AC-43 -> AC-40).
    """
    _latched(acp, 'log')
    (acp.P / '.aid' / 'audit').mkdir(parents=True)      # markers gone, audit dir still there
    assert acp.bash('ls') == ('ALLOW', None)
    lines = [json.loads(l) for l in (acp.P / '.aid' / 'audit' / 'tool-usage.jsonl')
             .read_text(encoding='utf-8').splitlines() if l.strip()]
    assert any(e.get('integrity') is True for e in lines), lines


@pytest.mark.parametrize('source', ['resume', 'clear'])
def test_ac_43_user_session_start_releases_the_latch(acp, source):
    """
    WHY (T1b review 3 MAJOR, owner decision (a) 2026-11-17): --resume/--continue keep the
    session id, so a project the user de-initialised between sittings stayed denied for the
    rest of the conversation. A SessionStart the user caused ends the latch.
    """
    _latched(acp, 'block')
    assert acp.bash('ls')[0] == 'DENY'
    note = acp.start('s1', source)
    assert 'no longer gates it' in note, note
    assert acp.bash('ls') == ('ALLOW', None)
    assert acp.write(str(acp.P / 'src' / 'a.ts')) == ('ALLOW', None)
    assert not (acp.P / '.aid').exists()                # releasing wrote nothing into P (AC-27)
    # The baseline was kept: AID coming back mid-session is gated again with no false denial.
    (acp.P / '.aid-off').rename(acp.P / '.aid')
    assert acp.bash('ls') == ('ALLOW', None)
    assert acp.bash('node x.js')[0] == 'ALLOW'          # phase 5


@pytest.mark.parametrize('source', ['compact', None])
def test_ac_43_compact_or_unknown_session_start_keeps_the_latch(acp, source):
    """WHY: Claude Code fires SessionStart(compact) mid-session on its own, so an agent could
    rename .aid and wait for it; only startup/resume/clear (a user's act) release."""
    _latched(acp, 'block')
    acp.start('s1', source)
    v = acp.bash('ls')
    assert v[0] == 'DENY' and 'disappeared mid-session' in v[1], v


def _call(acp, action, cwd, tool_input, project_dir=None):
    return decision(spawn(cwd, 'PreToolUse', action, acp.H, {
        'session_id': 's1', 'cwd': str(cwd), 'tool_name': 'Bash' if action == 'phase_gate_bash' else 'Write',
        'tool_input': tool_input}, project_dir=project_dir))


def test_ac_43_latch_holds_for_claude_project_dir_with_cwd_outside(acp):
    """
    WHY (fix round 1 BLOCKER): the latch only covered the cwd walk. With
    CLAUDE_PROJECT_DIR=P (Claude Code sets it) and a cwd outside P, renaming .aid made the
    call non-AID and a Write to P/.claude/settings.json was allowed.
    """
    S = acp.P.parent / 'sibling'
    S.mkdir()
    _latched(acp, 'block')
    settings = str(acp.P / '.claude' / 'settings.json')
    v = _call(acp, 'phase_gate_write', S, {'file_path': settings}, project_dir=acp.P)
    assert v[0] == 'DENY' and 'disappeared mid-session' in v[1], v
    v = _call(acp, 'phase_gate_bash', S, {'command': 'ls'}, project_dir=acp.P)
    assert v[0] == 'DENY' and 'disappeared mid-session' in v[1], v
    (acp.P / '.aid-off').rename(acp.P / '.aid')
    assert _call(acp, 'phase_gate_bash', S, {'command': 'ls'}, project_dir=acp.P) == ('ALLOW', None)


@pytest.mark.parametrize('project_dir', [False, True])
def test_ac_43_latch_beats_a_fresh_nearer_aid_root(acp, project_dir):
    """
    WHY (fix round 1 BLOCKER): after renaming P/.aid, a new P/docs/.aid (log config) was a
    nearer AID root with no baseline, so it got first-use trust and the latch never ran.
    """
    _latched(acp, 'block')
    (acp.P / 'docs' / '.aid' / 'hooks').mkdir(parents=True)
    (acp.P / 'docs' / '.aid' / 'hooks' / 'config.json').write_text(
        json.dumps({'enforcement': {'phase_gate_write': 'log', 'phase_gate_bash': 'log'}}), encoding='utf-8')
    pd = acp.P if project_dir else None
    D = acp.P / 'docs'
    v = _call(acp, 'phase_gate_bash', D, {'command': 'ls'}, pd)
    assert v[0] == 'DENY' and 'disappeared mid-session' in v[1], v
    v = _call(acp, 'phase_gate_write', D, {'file_path': str(acp.P / '.claude' / 'settings.local.json')}, pd)
    assert v[0] == 'DENY', v
    # A nested AID project whose parent still IS an AID root is used as before (no latch).
    (acp.P / '.aid-off').rename(acp.P / '.aid')
    assert _call(acp, 'phase_gate_bash', D, {'command': 'node x.js'}, None) == ('ALLOW', None)


def test_ac_43_no_latch_on_a_root_the_session_only_visited(clean_tmp):
    """
    WHY (fix round 2 MAJOR): layer B writes a first-use baseline in any AID root the agent
    visits. The latch fired on that baseline, so after a visited fixture/sub-project lost its
    .aid legitimately (teardown, de-init), every call there was denied, even `cd` out.
    Only a root SessionStart recorded for this session may latch (AC-43 step 1).
    """
    W, H = clean_tmp / 'W', clean_tmp / 'home'
    F = W / 'fixtures' / 'F'
    for d in (W, H, F / '.aid' / 'hooks', F / 'docs'):
        d.mkdir(parents=True, exist_ok=True)
    subprocess.run(['git', 'init', '-q', str(W)], check=True, capture_output=True)
    (F / '.aid' / 'state.json').write_text('{"current_phase":5}', encoding='utf-8')
    (F / '.aid' / 'hooks' / 'config.json').write_text(json.dumps(BLOCK_CFG), encoding='utf-8')
    spawn(W, 'SessionStart', None, H, {'session_id': 's1', 'source': 'startup', 'cwd': str(W)}, project_dir=W)

    def call(action, cwd, tool_input):
        return decision(spawn(cwd, 'PreToolUse', action, H, {
            'session_id': 's1', 'cwd': str(cwd), 'tool_name': 'Bash' if action == 'phase_gate_bash' else 'Write',
            'tool_input': tool_input}, project_dir=W))

    assert call('phase_gate_bash', F, {'command': 'ls'}) == ('ALLOW', None)    # F's baseline is written
    shutil.rmtree(str(F / '.aid'))
    assert call('phase_gate_bash', F, {'command': 'ls'}) == ('ALLOW', None)
    assert call('phase_gate_bash', F, {'command': 'cd "{}"'.format(W)}) == ('ALLOW', None)
    assert call('phase_gate_write', F, {'file_path': str(F / 'x.ts')}) == ('ALLOW', None)
    assert call('phase_gate_bash', F / 'docs', {'command': 'ls'}) == ('ALLOW', None)


@pytest.mark.parametrize('rename', [False, True])
@pytest.mark.parametrize('bad', ['{bad', '[1]', '{"current_phase":"x"}'])
def test_inv3_broken_state_does_not_skip_layer_b(acp, rename, bad):
    """
    WHY (fix round 1 BLOCKER, INV-3): the gates read state.json before layer B, and a broken
    state fails closed at the CURRENT config's level. Deleting the block config (or renaming
    .aid and planting a fresh .aid/state.json) plus a broken state then allowed everything.
    """
    acp.state(5)
    acp.start('s1')
    assert acp.bash('ls') == ('ALLOW', None)
    if rename:
        (acp.P / '.aid').rename(acp.P / '.aid-off')
        (acp.P / '.aid').mkdir()
    else:
        (acp.P / '.aid' / 'hooks' / 'config.json').unlink()
    (acp.P / '.aid' / 'state.json').write_text(bad, encoding='utf-8')
    assert acp.bash('node x.js')[0] == 'DENY'
    assert acp.write(str(acp.P / '.claude' / 'settings.local.json'))[0] == 'DENY'
    assert acp.write(str(acp.P / 'src' / 'x.ts'))[0] == 'DENY'


def test_ac_44_unreadable_settings_file_denies(acp):
    """WHY (fix round 1 MAJOR): a settings file that exists but cannot be read (here a
    directory) counts as possibly disabling hooks under a block baseline."""
    acp.start('s1')
    d = acp.P / '.claude' / 'settings.local.json'
    d.mkdir()
    v = acp.bash('ls')
    assert v[0] == 'DENY' and 'settings.local.json' in v[1] and 'cannot be read' in v[1], v
    d.rmdir()
    assert acp.bash('ls') == ('ALLOW', None)


def _encode(obj_text, enc):
    if enc == 'utf-8-sig':
        return b'\xef\xbb\xbf' + obj_text.encode('utf-8')
    if enc == 'utf-16le':
        return b'\xff\xfe' + obj_text.encode('utf-16-le')
    return b'\xfe\xff' + obj_text.encode('utf-16-be')


AC44_ENCODINGS = ['utf-8-sig', 'utf-16le', 'utf-16be']


@pytest.mark.parametrize('enc', AC44_ENCODINGS)
@pytest.mark.parametrize('payload', [{'disableAllHooks': True}, {'enabledPlugins': {'aid@AID': False}}])
def test_ac_44_bom_settings_disable_is_detected(acp, enc, payload):
    """WHY: a settings file saved with a BOM (PowerShell's default) hid disableAllHooks
    from the json reader, so the mid-session disable was allowed (AC-44)."""
    acp.start('s1')
    (acp.P / '.claude' / 'settings.local.json').write_bytes(_encode(json.dumps(payload), enc))
    v = acp.bash('ls')
    assert v[0] == 'DENY' and 'settings.local.json' in v[1], v
    assert acp.write('docs/a.md')[0] == 'DENY'


@pytest.mark.parametrize('enc', AC44_ENCODINGS)
@pytest.mark.parametrize('text', ['{}', '{"disableAllHooks": false}', '{"enabledPlugins": {"aid@AID": true}}'])
def test_ac_44_bom_settings_harmless_content_allows(acp, enc, text):
    acp.start('s1')
    (acp.P / '.claude' / 'settings.local.json').write_bytes(_encode(text, enc))
    assert acp.bash('ls') == ('ALLOW', None)
    assert acp.write('docs/a.md') == ('ALLOW', None)


@pytest.mark.parametrize('raw', [b'{"disableAllHooks": "\xff"}', b'{bad', b'\xff\xfe{\x00'])
def test_ac_44_unreadable_settings_count_as_possibly_disabled(acp, raw):
    acp.start('s1')
    (acp.P / '.claude' / 'settings.local.json').write_bytes(raw)
    v = acp.bash('ls')
    assert v[0] == 'DENY' and 'settings.local.json' in v[1], v
    (acp.P / '.claude' / 'settings.local.json').write_text('{}', encoding='utf-8')
    assert acp.bash('ls') == ('ALLOW', None)


@pytest.mark.parametrize('enc', AC44_ENCODINGS)
def test_ac_44_bom_project_settings_keeps_layer_a_and_b(acp, enc):
    """
    WHY (T1 final review MINOR): only hooks_disabled decoded a BOM. Layer A and layer B
    read .claude/settings.json as plain UTF-8, so a BOM file holding every deny rule was
    judged "rules removed" (false DENY on every call), and SessionStart could not install
    layer A into a BOM file at all.
    """
    s = acp.P / '.claude' / 'settings.json'
    s.write_bytes(_encode('{"x": 1}', enc))
    acp.start('s1')                                     # layer A installs, keeps the encoding
    raw = s.read_bytes()
    assert raw[:2] == _encode('', enc)[:2], raw[:8]
    data = aid_guard.read_settings(s)[0]
    assert data['x'] == 1 and all(r in data['permissions']['deny'] for r in aid_guard.DENY_RULES)
    assert acp.bash('ls') == ('ALLOW', None)
    # Re-saved mid-session with a BOM, rules intact, flag false: still no false denial.
    s.write_bytes(_encode(json.dumps(dict(data, disableAllHooks=False)), enc))
    assert acp.bash('ls') == ('ALLOW', None)
    # Removing a rule from the BOM file is still caught.
    data['permissions']['deny'] = data['permissions']['deny'][1:]
    s.write_bytes(_encode(json.dumps(data), enc))
    v = acp.bash('ls')
    assert v[0] == 'DENY' and 'removed' in v[1], v


def test_ac_35_f1_write_tool_does_not_expand_tilde_user(acp):
    """
    WHY (F1): Claude Code's Write tool expands only "~", "~/" and "~\\"; "~<user>/..." is a
    literal relative dir. The gate expanded it to <home>/.claude/plans and allowed a write
    that lands in <P>/~<user>/... before Phase 4.
    """
    import getpass
    user = getpass.getuser()      # Windows expanduser maps ~<current user> to the (fake) home H
    for path in ('~{}/.claude/plans/evil.ts'.format(user), '~{}\\.claude\\plans\\evil.ts'.format(user)):
        assert acp.write(path)[0] == 'DENY', path
    for path in ('~/.claude/plans/p.md', '~\\.claude\\plans\\p.md'):
        assert acp.write(path) == ('ALLOW', None), path


def test_ac_20_f2_mkdir_options_denied_from_docs(acp):
    """WHY (F2): from cwd docs/, "-m"/"777" are allowed write targets, so only the option
    check stops mkdir -m 777; without it the command was allowed."""
    def bash(cmd):
        return decision(spawn(acp.P / 'docs', 'PreToolUse', 'phase_gate_bash', acp.H, {
            'session_id': 's1', 'cwd': str(acp.P / 'docs'), 'tool_name': 'Bash',
            'tool_input': {'command': cmd}}))
    for cmd in ('mkdir -m 777 x', 'mkdir --mode=777 x'):
        v = bash(cmd)
        assert v[0] == 'DENY' and 'option' in v[1], (cmd, v)
    assert bash('mkdir -p x') == ('ALLOW', None)


# ===========================================================================
# T2 (T2-acceptance.md): default enforcement = block, per-project override, notice.
# ===========================================================================

T2_NOTICE = 'AID phase gates block by default'


def _t2_gate_results(acp):
    assert acp.write(str(acp.P / 'src' / 'a.ts'))[0] == 'DENY'
    assert acp.bash('node x.js')[0] == 'DENY'
    assert acp.bash('npm test')[0] == 'DENY'
    assert acp.write(str(acp.P / 'docs' / 'a.md')) == ('ALLOW', None)
    assert acp.bash('git status') == ('ALLOW', None)
    assert acp.bash('ls') == ('ALLOW', None)


@pytest.mark.parametrize('cfg', [None, {}, {'enforcement': {}},
                                 {'phase_gate_rules': {'code_write_min_phase': 4}}])
def test_t2_1_2_unconfigured_aid_project_blocks(acp, cfg):
    """
    WHY (A-04, D-07/08): with no gate level configured the gates only logged, so an AID
    project that never wrote .aid/hooks/config.json had no phase gate at all.
    """
    c = acp.P / '.aid' / 'hooks' / 'config.json'
    if cfg is None:
        c.unlink()
    else:
        acp.config(cfg)
    acp.start('s1')
    _t2_gate_results(acp)


def test_t2_2_config_only_root_blocks(acp):
    """A root marked only by .aid/hooks/config.json (no state.json) is gated at phase 0."""
    acp.config({})
    (acp.P / '.aid' / 'state.json').unlink()
    acp.start('s1')
    assert acp.write(str(acp.P / 'src' / 'a.ts'))[0] == 'DENY'
    assert acp.bash('node x.js')[0] == 'DENY'


@pytest.mark.parametrize('level,expect', [('log', ('ALLOW', None)), ('LOG', ('ALLOW', None)),
                                          (' Warn ', 'warn'), ('warn', 'warn')])
def test_t2_3_project_can_lower_a_gate(acp, level, expect):
    acp.config({'enforcement': {'phase_gate_write': level}})
    acp.start('s1')
    v = acp.write(str(acp.P / 'src' / 'a.ts'))
    if expect == 'warn':
        assert v[0] == 'ALLOW' and 'AID ENFORCEMENT WARNING' in v[1], v
    else:
        assert v == expect, v
    assert acp.bash('node x.js')[0] == 'DENY'           # the other gate keeps the default


@pytest.mark.parametrize('bad', ['off', 'none', '', 1, None])
def test_t2_4_unknown_gate_level_blocks(acp, bad):
    acp.config({'enforcement': {'phase_gate_write': bad, 'phase_gate_bash': bad}})
    acp.start('s1')
    assert acp.write(str(acp.P / 'src' / 'a.ts'))[0] == 'DENY'
    assert acp.bash('node x.js')[0] == 'DENY'


def test_t2_5_other_hooks_still_default_to_log():
    import aid_hooks
    assert {k: v for k, v in aid_hooks.DEFAULT_ENFORCEMENT.items() if k not in aid_hooks.GATES} == {
        'quality_check_verifier': 'log', 'session_reminder': 'log',
        'context_injector': 'log', 'audit_logger': 'log'}
    cfg = {'enforcement': {'quality_check_verifier': 'off'}}
    assert aid_hooks.get_enforcement_level(cfg, 'quality_check_verifier') == 'log'


def test_t2_6_non_aid_project_stays_untouched_under_the_block_default(clean_tmp):
    Q = clean_tmp / 'Q'
    (Q / '.aid' / 'audit').mkdir(parents=True)          # stray: not an AID root
    H = clean_tmp / 'home'
    H.mkdir()
    for action, ti in (('phase_gate_write', {'file_path': str(Q / 'src' / 'a.ts')}),
                       ('phase_gate_bash', {'command': 'node x.js'})):
        assert decision(spawn(Q, 'PreToolUse', action, H, {
            'session_id': 's1', 'cwd': str(Q), 'tool_name': 'Write' if 'write' in action else 'Bash',
            'tool_input': ti})) == ('ALLOW', None)


def test_t2_7_lowering_from_the_default_is_reported_but_the_default_is_not(acp):
    (acp.P / '.aid' / 'hooks' / 'config.json').unlink()
    assert 'weaker' not in acp.start('s1')
    acp.level('log')
    out = acp.start('s2')
    assert 'phase_gate_write went from block to log' in out, out
    (acp.P / '.aid' / 'hooks' / 'config.json').unlink()  # back to the default: stronger
    assert 'weaker' not in acp.start('s3')


@pytest.mark.parametrize('cfg,shown', [(None, True), ({}, True),
                                       ({'enforcement': {'phase_gate_write': 'block'}}, True),
                                       (BLOCK_CFG, False),
                                       ({'enforcement': {'phase_gate_write': 'off', 'phase_gate_bash': None}}, True),
                                       ({'enforcement': {'phase_gate_write': 'log', 'phase_gate_bash': 'warn'}}, False)])
def test_t2_8_session_start_notice_until_both_gates_are_set(acp, cfg, shown):
    """WHY: users upgrading from the old log default must learn why calls are now
    denied. The note is for the user; it does not tell the agent to edit the config."""
    if cfg is None:
        (acp.P / '.aid' / 'hooks' / 'config.json').unlink()
    else:
        acp.config(cfg)
    out = acp.start('s1')
    assert (T2_NOTICE in out) is shown, out


@pytest.mark.parametrize('level', ['log', 'warn', 'LOG', 'off'])
@pytest.mark.parametrize('phase', [1, 5])
def test_t2_10_control_files_are_refused_at_every_level(acp, level, phase):
    """
    WHY (T2 docs review r1 MAJOR, owner decision 2026-11-17): the control-file refusal
    followed the gate level, so lowering phase_gate_write to warn/log (the docs' own
    example) let the agent rewrite .aid/hooks/config.json and ~/.claude/settings.json.
    Lowering a gate relaxes phase rules only.
    """
    acp.config({'enforcement': {'phase_gate_write': level, 'phase_gate_bash': level}})
    acp.state(phase)
    acp.start('s1')
    for target in (acp.P / '.aid' / 'hooks' / 'config.json', acp.P / '.claude' / 'settings.json',
                   acp.H / '.claude' / 'settings.json'):
        v = acp.write(str(target))
        assert v[0] == 'DENY' and 'control file' in v[1], (target, v)
    v = acp.bash('echo {} > .claude/settings.local.json')
    assert v[0] == 'DENY' and 'control file' in v[1], v
    # The phase rules themselves follow the lowered level ('off' is unknown, so block).
    expect = 'DENY' if level == 'off' and phase < 4 else 'ALLOW'
    assert acp.write(str(acp.P / 'src' / 'a.ts'))[0] == expect
    assert acp.bash('node x.js')[0] == expect


@pytest.mark.parametrize('where', ['home', 'stray', 'plain'])
def test_t2_8_notice_never_shown_outside_an_aid_project(clean_tmp, where):
    """WHY (T2 code review r1 MINOR): the notice must not reach projects that do not use
    AID (AC-27): the home dir whose .aid is AID_HOME, a stray .aid/audit, a plain dir."""
    H = clean_tmp / 'home'
    (H / '.aid' / 'hooks').mkdir(parents=True)
    (H / '.aid' / 'state.json').write_text('{"current_phase":1}', encoding='utf-8')
    Q = {'home': H, 'stray': clean_tmp / 'S', 'plain': clean_tmp / 'Q'}[where]
    Q.mkdir(exist_ok=True)
    if where == 'stray':
        (Q / '.aid' / 'audit').mkdir(parents=True)
    out = spawn(Q, 'SessionStart', None, H, {'session_id': 's1', 'source': 'startup', 'cwd': str(Q)})
    assert T2_NOTICE not in (out or ''), out


T2_DOCS = ['README.md', 'docs/PHASE-GATES.md', 'docs/SECURITY-MODEL.md']


@pytest.mark.parametrize('doc', T2_DOCS)
def test_t2_d5_docs_match_the_code(doc):
    """WHY (D-5): the docs tell users the default and how to override it; an example
    with a typo'd gate name or level would silently fall back to block or be ignored."""
    import re
    import aid_hooks
    text = Path(REPO_ROOT, doc).read_text(encoding='utf-8')
    assert 'block by default' in text, doc
    assert all(aid_hooks.DEFAULT_ENFORCEMENT[g] == 'block' for g in aid_hooks.GATES)
    examples = [json.loads(b) for b in re.findall(r'```json\n(.*?)```', text, re.S) if '"enforcement"' in b]
    assert examples, doc
    for ex in examples:
        for gate, level in ex['enforcement'].items():
            assert gate in aid_hooks.GATES and level in ('log', 'warn', 'block'), (doc, gate, level)


def test_t2_d1_security_model_lists_the_real_deny_rules():
    text = Path(REPO_ROOT, 'docs', 'SECURITY-MODEL.md').read_text(encoding='utf-8')
    for rule in aid_guard.DENY_RULES:
        assert '`{}`'.format(rule) in text, rule
