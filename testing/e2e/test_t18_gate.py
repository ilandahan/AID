"""
T18 (3.0.8 release gate run 4, NEW-PS-relbackslash / R01-PS-2): a PowerShell relative
backslash spelling of a confirmed aid_session call gets the verdict of its forward-slash form.

WHY THIS TEST:
- PROBLEM: `.\\aid_session.py approve` (and its python twin) was silently allowed outside AID,
  while `python ./aid_session.py approve` was asked. The gate lexed PowerShell text with the
  bash lexer, where a backslash is an escape, so `.\\aid_session.py` read as `.aid_session.py`.
- COST OF FAILURE: an agent writes a phase-5 .aid/state.json with no prompt to the user.
- SUCCESS: in every place (non-AID and AID p0/p1/p4/p5 at every level) the backslash form has
  the forward-slash form's verdict class, and outside AID it is never a silent allow.
"""
import pytest

from test_t17_gate import EVERY, base, _w, many, verdict_class  # noqa: F401  (base is a fixture)

# (backslash form, forward-slash form) - PowerShell runs both the same on Windows.
T18_PS = [
    ('.\\aid_session.py approve', './aid_session.py approve'),
    ('python .\\aid_session.py approve', 'python ./aid_session.py approve'),
    ('& .\\aid_session.py approve', '& ./aid_session.py approve'),
    ('python .\\hooks\\aid_session.py init developer 5', 'python ./hooks/aid_session.py init developer 5'),
    ('py hooks\\aid_session.py qa-pass T-1', 'py hooks/aid_session.py qa-pass T-1'),
]


@pytest.mark.parametrize('place', EVERY)
def test_t18_ps_backslash_session_call_gets_the_forward_slash_verdict(base, place):  # noqa: F811
    w = _w(base, place)
    got = many([(w, 'PowerShell', c) for pair in T18_PS for c in pair])
    for n, (back, fwd) in enumerate(T18_PS):
        vb, vf = got[2 * n], got[2 * n + 1]
        assert verdict_class(vb) == verdict_class(vf), (place, back, vb, fwd, vf)
        if place == 'non-AID':
            assert vb[0] != 'ALLOW', (back, vb)


# T18 narrow audit finding 1: a direct call in a carried line (su -c, git alias, script -c)
# gets its python twin's verdict, as eval and sh -c already do (docs: "in every folder").
T18_CARRIED = [
    ('su -c "./aid_session.py init developer 5"', 'su -c "python ./aid_session.py init developer 5"'),
    ('git -c alias.x="!./aid_session.py approve" x', 'git -c alias.x="!python ./aid_session.py approve" x'),
    ('script -qc "./aid_session.py approve"', 'script -qc "python ./aid_session.py approve"'),
    ('runuser -c "./aid_session.py qa-pass T-1"', 'runuser -c "python ./aid_session.py qa-pass T-1"'),
]


@pytest.mark.parametrize('place', EVERY)
def test_t18_direct_call_in_a_carried_line_gets_the_twins_verdict(base, place):  # noqa: F811
    w = _w(base, place)
    got = many([(w, 'Bash', c) for pair in T18_CARRIED for c in pair])
    for n, (direct, twin) in enumerate(T18_CARRIED):
        vd, vt = got[2 * n], got[2 * n + 1]
        assert verdict_class(vd) == verdict_class(vt), (place, direct, vd, twin, vt)
        if place == 'non-AID':
            assert vd[0] != 'ALLOW', (direct, vd)
