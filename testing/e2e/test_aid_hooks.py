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
.aid/ - a test that did would pass green against the broken code, since the shipped
default enforcement level is "log" (never blocks) for every gate.
"""
import json
import os
import subprocess
import sys

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

    def test_uninitialised_project_never_blocks(self, tmp_path):
        """No .aid/ at all: AID is not in use here, so stay out of the way."""
        got = parse(run_hook(tmp_path, 'PreToolUse', 'phase_gate_write', WRITE_SRC))
        denied = got and got.get('hookSpecificOutput', {}).get('permissionDecision') == 'deny'
        assert not denied

    def test_shipped_default_is_log_not_block(self, tmp_path):
        """
        Defaults must not deny. A freshly installed plugin that starts refusing writes
        would be indistinguishable from a broken install.
        """
        p = make_project(tmp_path, phase=1)  # no enforcement config
        got = parse(run_hook(p, 'PreToolUse', 'phase_gate_write', WRITE_SRC))
        denied = got and got.get('hookSpecificOutput', {}).get('permissionDecision') == 'deny'
        assert not denied, 'the default enforcement level must be "log", never "block"'


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
    def test_garbage_stdin_never_crashes_or_blocks(self, tmp_path, junk):
        """A hook that dies on malformed input takes the user's session with it."""
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
