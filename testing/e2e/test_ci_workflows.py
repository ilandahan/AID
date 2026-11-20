"""
WHY THIS TEST:
- PROBLEM: CI workflows are a supply-chain surface (audit A-34, A-53, A-31). A tag-pinned
  action, a write-scoped token, persisted checkout credentials or a scanner set never to
  fail would silently reopen those findings.
- COST OF FAILURE: a compromised action runs with repo credentials, or real findings ship.
- SUCCESS: every workflow pins actions by SHA, uses a read-only token, does not persist
  checkout credentials, the scanner gates on high, and ci.yml runs the repo's tests.
"""
import re
from pathlib import Path

import pytest
import yaml

WF_DIR = Path(__file__).resolve().parents[2] / '.github' / 'workflows'
WORKFLOWS = sorted(WF_DIR.glob('*.yml'))
SHA_PIN = re.compile(r'^[\w.-]+/[\w./-]+@[0-9a-f]{40}$')


def _load(path):
    return yaml.safe_load(path.read_text(encoding='utf-8'))


def _steps(wf):
    for job in wf['jobs'].values():
        yield from job.get('steps', [])


def test_ci_workflow_exists():
    assert (WF_DIR / 'ci.yml') in WORKFLOWS


@pytest.mark.parametrize('path', WORKFLOWS, ids=lambda p: p.name)
def test_every_action_pinned_to_full_sha(path):
    uses = [s['uses'] for s in _steps(_load(path)) if 'uses' in s]
    assert uses, f'{path.name} has no actions'
    bad = [u for u in uses if not SHA_PIN.match(u)]
    assert not bad, f'not pinned to a 40-hex SHA: {bad}'


@pytest.mark.parametrize('path', WORKFLOWS, ids=lambda p: p.name)
def test_token_is_read_only(path):
    wf = _load(path)
    assert wf.get('permissions') == {'contents': 'read'}
    for name, job in wf['jobs'].items():
        perms = job.get('permissions', {})
        assert all(v in ('read', 'none') for v in perms.values()), name


@pytest.mark.parametrize('path', WORKFLOWS, ids=lambda p: p.name)
def test_checkout_does_not_persist_credentials(path):
    checkouts = [s for s in _steps(_load(path)) if s.get('uses', '').startswith('actions/checkout@')]
    assert checkouts
    for s in checkouts:
        assert s.get('with', {}).get('persist-credentials') is False


def test_scanner_fails_on_high_severity():
    wf = _load(WF_DIR / 'hol-plugin-scanner.yml')
    scanner = [s for s in _steps(wf) if 'ai-plugin-scanner-action' in s.get('uses', '')]
    assert scanner and scanner[0]['with']['fail_on_severity'] == 'high'


def test_ci_runs_repo_tests_and_supply_chain_checks():
    wf = _load(WF_DIR / 'ci.yml')
    runs = '\n'.join(s.get('run', '') for s in _steps(wf))
    assert 'pytest testing/e2e' in runs
    assert 'AID_HOME=' in runs
    assert 'node --test' in runs
    assert 'npm ci --ignore-scripts' in runs
    assert 'npm audit --audit-level=high' in runs
    assert 'gitleaks' in runs and '--redact' in runs and 'sha256sum -c' in runs


# --- T15-44 (item 36): storybook audit, version-bump guard, Windows Git Bash job ---------

def _ci_jobs():
    return _load(WF_DIR / 'ci.yml')['jobs']


def test_t15_44_storybook_preview_is_audited():
    steps = [s for job in _ci_jobs().values() for s in job.get('steps', [])]
    hits = [s for s in steps if s.get('working-directory') == 'storybook-preview'
            and 'npm audit --audit-level=high' in s.get('run', '')]
    assert hits, 'no npm audit step in storybook-preview'


def test_t15_44_version_bump_guard():
    jobs = _ci_jobs()
    guard = [j for j in jobs.values()
             if any("--match 'v*'" in s.get('run', '') for s in j.get('steps', []))]
    assert len(guard) == 1, 'no version bump guard job'
    job = guard[0]
    checkout = [s for s in job['steps'] if s.get('uses', '').startswith('actions/checkout@')][0]
    assert checkout['with'].get('fetch-depth') == 0          # tags and history are needed
    run = '\n'.join(s.get('run', '') for s in job['steps'])
    assert 'plugin.json' in run and 'exit 1' in run           # fails when the version was not bumped
    assert '::notice::' in run and 'exit 0' in run            # skips with a notice when there is no tag


def test_t15_44_windows_job_runs_init_project_tests_under_git_bash():
    win = [j for j in _ci_jobs().values() if j.get('runs-on') == 'windows-latest']
    assert win, 'no windows-latest job'
    job = win[0]
    assert job.get('defaults', {}).get('run', {}).get('shell') == 'bash'
    run = '\n'.join(s.get('run', '') for s in job['steps'])
    assert 'testing/e2e/test_t15_scripts.py' in run and 'HOME=' in run


# --- T16-51: the version-bump guard fires before the first v* tag (A-24) -----------------

def _guard_script():
    jobs = _ci_jobs()
    job = [j for j in jobs.values()
           if any("--match 'v*'" in s.get('run', '') for s in j.get('steps', []))][0]
    return '\n'.join(s['run'] for s in job['steps'] if "--match 'v*'" in s.get('run', ''))


def _git(cwd, *args):
    import subprocess
    p = subprocess.run(['git', '-c', 'user.name=t16', '-c', 'user.email=t16@example.invalid',
                        '-c', 'commit.gpgsign=false', '-c', 'init.defaultBranch=main', *args],
                       cwd=str(cwd), capture_output=True, text=True)
    assert p.returncode == 0, (args, p.stderr)
    return p.stdout


def test_t16_51_version_guard_compares_with_origin_main_when_untagged(tmp_path):
    """No v* tag: a shipped change without a plugin.json bump against origin/main fails;
    the same change with a bump passes. Before T16 the guard skipped with a notice."""
    import json
    import shutil
    import subprocess
    import sys
    bash = shutil.which('bash')
    if not bash or not shutil.which('git'):
        pytest.skip('bash and git are needed')
    # python3 may be absent (or the Windows Store stub): run the guard with this interpreter.
    script = _guard_script().replace('python3', '"{}"'.format(sys.executable.replace('\\', '/')))
    (tmp_path / 'guard.sh').write_text(script, encoding='utf-8', newline='\n')
    origin, work = tmp_path / 'origin', tmp_path / 'work'
    origin.mkdir()
    _git(origin, 'init', '-q')
    (origin / '.claude-plugin').mkdir()
    (origin / '.claude-plugin' / 'plugin.json').write_text(json.dumps({'version': '1.0.0'}))
    (origin / 'hooks').mkdir()
    (origin / 'hooks' / 'a.txt').write_text('a\n')
    _git(origin, 'add', '-A')
    _git(origin, 'commit', '-q', '-m', 'base')
    _git(tmp_path, 'clone', '-q', str(origin), str(work))

    import os
    # Git Bash would rewrite the `origin/main:<path>` argument as a Windows path.
    env = dict(os.environ, MSYS_NO_PATHCONV='1', MSYS2_ARG_CONV_EXCL='*')

    def run_guard():
        return subprocess.run([bash, str(tmp_path / 'guard.sh')], cwd=str(work),
                              capture_output=True, text=True, env=env)

    (work / 'hooks' / 'a.txt').write_text('changed\n')
    _git(work, 'commit', '-q', '-am', 'shipped change, no bump')
    p = run_guard()
    assert p.returncode == 1 and '::error::' in p.stdout, p.stdout + p.stderr
    (work / '.claude-plugin' / 'plugin.json').write_text(json.dumps({'version': '1.0.1'}))
    _git(work, 'commit', '-q', '-am', 'bump')
    p = run_guard()
    assert p.returncode == 0 and 'version guard ok' in p.stdout, p.stdout + p.stderr


# --- T16-57: CI Python deps are pinned with hashes (FR-36) ---------------------------------

REQ = WF_DIR.parent / 'requirements-ci.txt'


def test_t16_57_ci_installs_python_deps_from_hashed_requirements():
    steps = [s for job in _ci_jobs().values() for s in job.get('steps', [])]
    pip = [s['run'] for s in steps if 'pip install' in s.get('run', '')]
    assert pip, 'no pip install step'
    for run in pip:
        # T17 (owner 2026-11-20): T17-37 adds the hashed pip-audit tool file.
        assert ('--require-hashes -r .github/requirements-ci.txt' in run
                or '--require-hashes -r .github/requirements-audit.txt' in run), run
        assert not re.search(r'pip install\s+pytest', run), run
    text = REQ.read_text(encoding='utf-8')
    reqs = re.findall(r'(?m)^([A-Za-z0-9_.-]+)==(\S+) \\$', text)
    names = {n.lower() for n, _ in reqs}
    assert {'pytest', 'pyyaml', 'pluggy', 'iniconfig', 'packaging', 'pygments', 'colorama'} <= names
    blocks = re.split(r'(?m)^(?=[A-Za-z0-9_.-]+==)', text)[1:]
    for block in blocks:
        assert re.search(r'--hash=sha256:[0-9a-f]{64}', block), block


def test_t16_57_dependabot_has_a_pip_entry_with_cooldown():
    cfg = _load(WF_DIR.parent / 'dependabot.yml')
    pip = [u for u in cfg['updates'] if u['package-ecosystem'] == 'pip']
    assert pip and pip[0]['directory'] == '/.github'
    assert pip[0]['cooldown']['default-days'] == 7


# --- T17-37: CI test dependencies are advisory-free and audited (U-01) ----------------------

# Oldest fixed versions (OSV, 2026-11-20): GHSA-6w46-j5rx-g56g fixed in pytest 9.0.3,
# GHSA-5239-wwwm-4pmq fixed in pygments 2.20.0.
_T17_FLOORS = {'pytest': (9, 0, 3), 'pygments': (2, 20, 0)}
AUDIT_REQ = WF_DIR.parent / 'requirements-audit.txt'


def _pins(path):
    text = path.read_text(encoding='utf-8')
    return {n.lower(): v for n, v in re.findall(r'(?m)^([A-Za-z0-9_.-]+)==(\S+) \\\r?$', text)}


def _ver(v):
    return tuple(int(x) for x in re.findall(r'\d+', v)[:3])


def test_t17_37_ci_pins_are_at_or_above_the_fixed_versions():
    pins = _pins(REQ)
    for name, floor in _T17_FLOORS.items():
        assert name in pins, name
        assert _ver(pins[name]) >= floor, (name, pins[name], floor)


def test_t17_37_pip_audit_step_is_hash_pinned_and_audits_the_ci_pins():
    steps = [s for job in _ci_jobs().values() for s in job.get('steps', [])]
    audit = [s['run'] for s in steps if 'pip_audit' in s.get('run', '') or 'pip-audit ' in s.get('run', '')]
    assert audit, 'no pip-audit step'
    for run in audit:
        assert '-r .github/requirements-ci.txt' in run and '--require-hashes' in run, run
        assert '--strict' in run, run
    installs = [s['run'] for s in steps if '-r .github/requirements-audit.txt' in s.get('run', '')]
    assert installs and all('--require-hashes' in r for r in installs), installs
    pins = _pins(AUDIT_REQ)
    assert 'pip-audit' in pins, sorted(pins)
    blocks = re.split(r'(?m)^(?=[A-Za-z0-9_.-]+==)', AUDIT_REQ.read_text(encoding='utf-8'))[1:]
    assert blocks
    for block in blocks:
        assert re.search(r'--hash=sha256:[0-9a-f]{64}', block), block[:80]


def test_t17_37_every_uses_stays_sha_pinned():
    for path in WORKFLOWS:
        text = path.read_text(encoding='utf-8')
        for m in re.finditer(r'(?m)^\s*-?\s*uses:\s*(\S+)', text):
            assert SHA_PIN.match(m.group(1)), (path.name, m.group(1))
