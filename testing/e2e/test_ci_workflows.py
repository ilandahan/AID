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
