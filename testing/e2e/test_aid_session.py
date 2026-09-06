"""
aid_session.py behaviour tests.

WHY THIS FILE:
The /aid-start menus used to be hand-copied into commands/aid-start.md. The copy drifted
from references/role-phase-terminology.json: data-scientist was a fully defined role with
six phases and its own skills, but no menu ever offered it, and menu slot 5 selected
"Other" instead. These tests execute the real script against the real terminology file and
assert that EVERY role and phase defined there is both offered by the menu and selectable,
so the next role added to the JSON cannot go missing again.

Deliberately not asserting menu wording or exact skill lists - that is shape, and shape
assertions go green while the thing is broken. What is asserted is behaviour: the option is
listed, the number picks the thing the menu said it would, and state comes out matching.
"""
import json
import os
import subprocess
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(REPO, 'hooks', 'aid_session.py')
TERMS = os.path.join(REPO, 'references', 'role-phase-terminology.json')


def terminology():
    with open(TERMS, encoding='utf-8') as fh:
        return json.load(fh)


TERMS_DATA = terminology()
ROLE_IDS = list(TERMS_DATA['roles'].keys())
PHASE_KEYS = sorted(TERMS_DATA['phases']['developer'], key=int)
ROLE_PHASE = [(r, p) for r in ROLE_IDS for p in sorted(TERMS_DATA['phases'][r], key=int)]


def run(args, cwd=None):
    """Run aid_session.py. UTF-8 forced: role names contain an em dash."""
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    return subprocess.run(
        [sys.executable, SCRIPT] + args,
        cwd=cwd, env=env, capture_output=True, text=True, encoding='utf-8',
    )


@pytest.fixture()
def project(tmp_path):
    """An empty project dir plus an isolated HOME, so feedback never touches the real one."""
    (tmp_path / '.aid').mkdir()
    home = tmp_path / 'home'
    home.mkdir()
    os.environ['HOME'] = str(home)
    os.environ['USERPROFILE'] = str(home)
    yield tmp_path


def read_state(project):
    with open(project / '.aid' / 'state.json', encoding='utf-8') as fh:
        return json.load(fh)


class TestMenusOfferEverything:
    """The bug that started this file: a defined role that no menu ever showed."""

    def test_role_menu_lists_every_defined_role(self):
        out = run(['roles']).stdout
        for rid in ROLE_IDS:
            name = TERMS_DATA['roles'][rid]['name']
            assert name in out, f"role menu never offers {rid} ({name})"

    def test_role_menu_offers_other_after_the_last_real_role(self):
        out = run(['roles']).stdout
        assert f"{len(ROLE_IDS) + 1}. **Other**" in out

    @pytest.mark.parametrize("role", ROLE_IDS)
    def test_phase_menu_lists_every_phase_for_that_role(self, role):
        out = run(['phases', role]).stdout
        for key in sorted(TERMS_DATA['phases'][role], key=int):
            name = TERMS_DATA['phases'][role][key]['name']
            assert name in out, f"phase menu for {role} never offers {key} ({name})"


class TestMenuNumbersSelectWhatTheMenuShowed:
    """Numbering is derived, so what is printed and what is parsed cannot drift apart."""

    @pytest.mark.parametrize("number,expected", list(enumerate(ROLE_IDS, 1)))
    def test_role_number_resolves_to_the_listed_role(self, number, expected, project):
        assert run(['start', str(number), '0'], cwd=project).returncode == 0
        assert read_state(project)['role'] == expected

    def test_number_after_the_last_role_is_other(self, project):
        assert run(['start', str(len(ROLE_IDS) + 1), '0'], cwd=project).returncode == 0
        assert read_state(project)['role'] == 'other'

    def test_other_falls_back_to_developer_terminology(self, project):
        run(['start', 'other', '4'], cwd=project)
        expected = TERMS_DATA['phases']['developer']['4']['name']
        assert read_state(project)['phase_display'] == expected


class TestEveryCombinationStarts:

    @pytest.mark.parametrize("role,phase", ROLE_PHASE)
    def test_role_phase_pair_writes_usable_state(self, role, phase, project):
        result = run(['start', role, phase], cwd=project)
        assert result.returncode == 0, result.stderr
        state = read_state(project)
        assert state['role'] == role
        assert state['current_phase'] == int(phase)
        assert state['phase_display'] == TERMS_DATA['phases'][role][phase]['name']
        # The role skill and the common skills must always be present, whatever the phase.
        assert TERMS_DATA['roleSkillMapping'][role] in state['skills_loaded']
        for common in TERMS_DATA['commonSkills']:
            assert common in state['skills_loaded']
        # phase_name is what the enforcement hooks print in gate messages.
        assert state['phase_name']


class TestRejectsBadInput:

    def test_unknown_role_exits_nonzero(self, project):
        assert run(['start', 'nope', '0'], cwd=project).returncode != 0

    def test_role_number_past_other_is_rejected(self, project):
        assert run(['start', str(len(ROLE_IDS) + 2), '0'], cwd=project).returncode != 0

    def test_unknown_phase_exits_nonzero(self, project):
        assert run(['start', 'pm', '9'], cwd=project).returncode != 0

    def test_end_without_a_session_exits_nonzero(self, tmp_path):
        assert run(['end', '--rating', '3'], cwd=tmp_path).returncode != 0


class TestEndRecordsTheSession:

    def test_feedback_and_review_verdict_are_saved(self, project):
        run(['start', 'qa', '5'], cwd=project)
        result = run(['end', '--rating', '4', '--worked', 'w', '--improve', 'i',
                      '--review', 'partial', '--review-note', '2 ACs missing'], cwd=project)
        assert result.returncode == 0, result.stderr

        state = read_state(project)
        assert state['status'] == 'ended'
        review = state['subagent_review']['phase_5']
        assert review['status'] == 'partial'
        assert review['note'] == '2 ACs missing'

        pending = os.path.join(os.environ['HOME'], '.aid', 'feedback', 'pending')
        files = os.listdir(pending)
        assert len(files) == 1, "exactly one feedback file per /aid-end"
        with open(os.path.join(pending, files[0]), encoding='utf-8') as fh:
            feedback = json.load(fh)
        assert feedback['rating'] == 4
        assert feedback['role'] == 'qa'
        assert feedback['worked_well'] == 'w'
        assert feedback['to_improve'] == 'i'
