"""
hooks/hook-runner.mjs fail-safe tests (audit A-03, D-11, A-37).

WHY THIS TEST:
- PROBLEM: Claude Code blocks only on exit 2 (or a JSON deny). The runner used to exit 1
  (non-blocking) when Python/bash was missing, when python3 was the Windows Store stub
  (exit 9009), or when WSL bash from System32 won the PATH lookup (rc 127), so the
  PreToolUse phase gates silently failed OPEN.
- COST OF FAILURE: every phase gate is bypassed on a machine with a broken runtime.
- SUCCESS: gates exit 2 on any runner failure, stubs are skipped for a working
  interpreter, System32/WindowsApps bash is refused in favour of Git Bash, and
  prototype keys are not hook names.

Every test spawns the real runner with node and a controlled PATH. Tests that need a
fake child copy the runner next to a stub aid_hooks.py / dev-pipeline-gate.sh, because
the runner resolves its scripts relative to its own location.
"""
import json
import os
import shutil
import subprocess
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUNNER = os.path.join(REPO_ROOT, 'hooks', 'hook-runner.mjs')
PLUGIN_JSON = os.path.join(REPO_ROOT, '.claude-plugin', 'plugin.json')
NODE = shutil.which('node')
WIN = os.name == 'nt'
EXE = '.exe' if WIN else ''
PY_DIR = os.path.dirname(sys.executable)
SYSTEM32 = os.path.join(os.environ.get('SystemRoot', r'C:\Windows'), 'System32')
GIT_BASH = next((p for p in (
    os.path.join(os.environ.get('ProgramW6432', os.environ.get('ProgramFiles', '')), 'Git', 'bin', 'bash.exe'),
    os.path.join(os.environ.get('ProgramFiles', ''), 'Git', 'usr', 'bin', 'bash.exe'),
) if os.path.isfile(p)), None)

pytestmark = pytest.mark.skipif(NODE is None, reason='node not on PATH')


def run(runner, args, cwd, path, payload=None, **env_extra):
    env = dict(os.environ, PATH=path, **env_extra)
    return subprocess.run([NODE, str(runner), *args], cwd=str(cwd), env=env,
                          input=json.dumps(payload or {}), capture_output=True, text=True, timeout=60)


def fake_hooks(tmp_path, py_body=None, sh_body=None):
    """Copy the runner into tmp/hooks with stub child scripts."""
    hooks = tmp_path / 'hooks'
    hooks.mkdir()
    runner = hooks / 'hook-runner.mjs'
    shutil.copy(RUNNER, runner)
    if py_body is not None:
        (hooks / 'aid_hooks.py').write_text(py_body, encoding='utf-8')
        (hooks / 'validate-qa-gate.py').write_text(py_body, encoding='utf-8')
    if sh_body is not None:
        (hooks / 'dev-pipeline-gate.sh').write_text(sh_body, encoding='utf-8', newline='\n')
    return runner


def stub_exe(directory, name, exit_code):
    """An executable `name` that exits `exit_code` whatever it is asked to run.

    Windows spawn without a shell resolves only .exe, so the stub is a copy of node.exe
    plus a NODE_OPTIONS preload that exits when the process is named like the stub.
    Returns extra env for the spawned runner.
    """
    directory.mkdir(exist_ok=True)
    if not WIN:
        stub = directory / name
        stub.write_text('#!/bin/sh\nexit {}\n'.format(exit_code))
        stub.chmod(0o755)
        return {}
    shutil.copy(NODE, directory / (name + EXE))
    pre = directory / 'stub-preload.cjs'
    pre.write_text(
        "if (require('path').basename(process.execPath).toLowerCase() === '%s')"
        " process.exit(%d);\n" % ((name + EXE).lower(), exit_code), encoding='utf-8')
    return {'NODE_OPTIONS': '--require "{}"'.format(pre.as_posix())}


# --- Python resolution -------------------------------------------------------------

def test_no_python_on_path_gate_fails_closed(tmp_path):
    empty = tmp_path / 'empty'
    empty.mkdir()
    for gate in ('phase-gate-write', 'phase-gate-bash'):
        r = run(RUNNER, [gate], tmp_path, str(empty))
        assert r.returncode == 2, (gate, r.returncode, r.stderr)
        assert 'no working Python' in r.stderr and 'fails closed' in r.stderr


def test_no_python_on_path_non_gate_is_non_blocking_but_explains(tmp_path):
    empty = tmp_path / 'empty'
    empty.mkdir()
    for hook in ('session-start', 'stop-qa'):
        r = run(RUNNER, [hook], tmp_path, str(empty))
        assert r.returncode == 1, (hook, r.returncode, r.stderr)
        assert 'no working Python' in r.stderr


def test_store_stub_python3_exit_9009_falls_back_to_real_python(tmp_path):
    runner = fake_hooks(tmp_path, py_body="import sys\nprint('py-ok ' + sys.argv[-1])\n")
    stubs = tmp_path / 'stubbin'
    env = stub_exe(stubs, 'python3', 9009)
    path = os.pathsep.join([str(stubs), PY_DIR])
    r = run(runner, ['phase-gate-write'], tmp_path, path, **env)
    assert r.returncode == 0, (r.returncode, r.stderr)
    assert r.stdout.strip() == 'py-ok phase_gate_write'


def test_real_gate_still_allows_outside_an_aid_project(tmp_path):
    """Legit path: real runner + real aid_hooks.py, no .aid/ -> allow (exit 0)."""
    payload = {'hook_event_name': 'PreToolUse', 'tool_name': 'Write',
               'tool_input': {'file_path': str(tmp_path / 'a.md')}, 'cwd': str(tmp_path)}
    r = run(RUNNER, ['phase-gate-write'], tmp_path, os.environ.get('PATH', ''), payload)
    assert r.returncode == 0, (r.returncode, r.stderr)


@pytest.mark.parametrize('hook,child_exit,expected', [
    ('phase-gate-bash', 0, 0), ('phase-gate-bash', 2, 2),
    ('phase-gate-bash', 1, 2), ('phase-gate-bash', 3, 2),
    ('stop-qa', 1, 1), ('stop-qa', 3, 3),
])
def test_child_exit_codes(tmp_path, hook, child_exit, expected):
    runner = fake_hooks(tmp_path, py_body='raise SystemExit({})\n'.format(child_exit))
    r = run(runner, [hook], tmp_path, PY_DIR)
    assert r.returncode == expected, (r.returncode, r.stderr)
    if hook.startswith('phase-gate') and child_exit not in (0, 2):
        assert 'fails closed' in r.stderr


# --- bash resolution (Windows) -----------------------------------------------------

win_git = pytest.mark.skipif(not WIN or GIT_BASH is None, reason='Windows + Git for Windows only')


@win_git
def test_windowsapps_bash_first_on_path_is_refused_for_git_bash(tmp_path):
    runner = fake_hooks(tmp_path, sh_body='echo bash-ok\nexit 0\n')
    wapps = tmp_path / 'WindowsApps'
    env = stub_exe(wapps, 'bash', 127)
    r = run(runner, ['stop-pipeline'], tmp_path, os.pathsep.join([str(wapps), SYSTEM32]), **env)
    assert r.returncode == 0, (r.returncode, r.stderr)
    assert r.stdout.strip() == 'bash-ok'


@win_git
@pytest.mark.skipif(not os.path.isfile(os.path.join(SYSTEM32, 'bash.exe')), reason='no WSL bash.exe')
def test_system32_wsl_bash_first_on_path_is_refused_for_git_bash(tmp_path):
    runner = fake_hooks(tmp_path, sh_body='echo bash-ok\nexit 0\n')
    r = run(runner, ['stop-pipeline'], tmp_path, SYSTEM32)
    assert r.returncode == 0, (r.returncode, r.stderr)
    assert r.stdout.strip() == 'bash-ok'


@pytest.mark.skipif(not WIN, reason='Windows only')
def test_only_refused_bash_available_reports_git_bash_missing(tmp_path):
    runner = fake_hooks(tmp_path, sh_body='echo bash-ok\n')
    wapps = tmp_path / 'WindowsApps'
    env = stub_exe(wapps, 'bash', 0)
    nowhere = str(tmp_path / 'nowhere')
    env.update({'PROGRAMFILES': nowhere, 'PROGRAMW6432': nowhere, 'PROGRAMFILES(X86)': nowhere,
                'GIT_INSTALL_ROOT': nowhere})
    r = run(runner, ['stop-pipeline'], tmp_path, str(wapps), **env)
    assert r.returncode == 1, (r.returncode, r.stderr)
    assert 'Git Bash not found' in r.stderr
    assert 'bash-ok' not in r.stdout


# --- name allow-list ---------------------------------------------------------------

@pytest.mark.parametrize('args', [
    [], ['nope'], ['__proto__'], ['constructor'], ['toString'], ['hasOwnProperty'],
    ['phase-gate-write', '--extra'], ['session-start', 'x'],
])
def test_unknown_prototype_and_extra_args_rejected(tmp_path, args):
    r = run(RUNNER, args, tmp_path, os.environ.get('PATH', ''))
    assert r.returncode == 2, (args, r.returncode, r.stderr)
    assert 'expected a known hook name' in r.stderr


# --- plugin.json -------------------------------------------------------------------

def test_only_pretooluse_gates_declare_onfailure_block():
    hooks = json.load(open(PLUGIN_JSON, encoding='utf-8'))['hooks']
    for event, entries in hooks.items():
        for entry in entries:
            for h in entry['hooks']:
                is_gate = h['args'][-1] in ('phase-gate-write', 'phase-gate-bash')
                assert h.get('onFailure') == ('block' if is_gate else None), (event, h['args'][-1])
