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
