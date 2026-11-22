"""
T21 guard surface: .aid/pipeline/cost-ledger.json is a control file.

WHY THESE TESTS:
- PROBLEM: the pipeline $ brake (cost_limits.max_per_run_usd) needs a running total the agent
  cannot lower. gate.mjs keeps it in .aid/pipeline/cost-ledger.json; if the agent's tools can
  write, delete or rename that file, the brake is a suggestion.
- COST OF FAILURE: an agent resets the ledger and a run spends past the user's limit.
- SUCCESS: through the real hooks (hook-runner.mjs), inside an AID project at every phase and
  level, Write/Edit/MultiEdit/NotebookEdit, Bash redirect/rm/mv and PowerShell Set-Content on
  the ledger are denied; a read is not. Outside AID the gates stay out of the way for it, as
  they do for .aid/pipeline/ESCALATION.json (aid_hooks.handle_phase_gate_write/_bash only
  judge .aid/state.json and aid_session/gate.mjs calls there); that is asserted, not assumed.
"""
from concurrent.futures import ThreadPoolExecutor

import pytest

from test_t17_gate import EVERY, POOL, TOOL_INPUT, base, _w, many  # noqa: F401  (base is a fixture)

LEDGER = '.aid/pipeline/cost-ledger.json'
SHORT = '.aid/pipeline/COST-L~1.JSO'   # its 8.3 short name
# The glob form is judged by _CONTROL_GLOB_TARGETS (the target may expand to the ledger).
BASH_WRITES = ['echo x > ' + LEDGER, 'rm ' + LEDGER, 'mv ' + LEDGER + ' x',
               'echo x > .aid/pipeline/cost-ledger.js?n',
               # Fix cycle 1: targets the guard cannot resolve; only PROTECTED_LITERALS sees them.
               'echo x > "$P/' + LEDGER + '"', 'P=.; echo x > $P/' + LEDGER,
               'echo x > $(echo ' + LEDGER + ')',
               'python -c "open(\'' + LEDGER + '\',\'w\').write(\'1\')"',
               'node -e "require(\'fs\').writeFileSync(\'' + LEDGER + '\',\'1\')"',
               'echo \'{"estimated_cost_usd":0}\' | dd of=' + LEDGER,
               'powershell -c "Remove-Item ' + LEDGER + '"',
               # Fix cycle 1: the 8.3 short name of the ledger (a `~` word is dynamic to the lexer).
               'echo x > .aid/pipeline/COST-L~1.JSO']
PS_WRITE = 'Set-Content -Path ' + LEDGER + ' -Value x'
PS_IO_WRITE = "[IO.File]::WriteAllText('" + LEDGER + "','1')"
PS_SHORT = ['Remove-Item ' + SHORT, 'Set-Content -Path ' + SHORT + ' -Value 0']
# Narrow audit: ordinary commands the reverted fix-2 checks (8.3 operand, xargs, git clean/stash)
# denied at p4/p5 although HEAD allowed them. They must stay allowed.
P4_NOT_DENIED = ['git reset --soft HEAD~1', 'git show HEAD~1:src/a.py', 'git log origin/main~3..HEAD',
                 'npm install @types/node@~20.0.0', 'cp a a~1', 'echo x > notes~1.txt',
                 'git clean -n', 'git clean -fd', 'git stash -u', 'echo ' + LEDGER + ' | xargs cat',
                 # T21b re-audit: an 8.3 path outside .aid/.claude (a Windows temp dir) is ordinary
                 'echo x > C:/Users/RUNNER~1/AppData/Local/Temp/out.txt', 'echo hi > logs/build~2.log']


@pytest.mark.parametrize('place', EVERY)
def test_t21_cost_ledger_is_a_control_file(base, place):  # noqa: F811
    w = _w(base, place)
    led = w.P / '.aid' / 'pipeline' / 'cost-ledger.json'
    led.parent.mkdir(parents=True, exist_ok=True)
    led.write_text('{"total_usd": 1}', encoding='utf-8')
    git_led = w.P / '.git' / 'aid' / '0123456789ab' / 'cost-ledger.json'   # T21b: <git-dir>/aid/<key>/
    tools = sorted(TOOL_INPUT)
    with ThreadPoolExecutor(POOL) as ex:
        writes = list(ex.map(lambda t: w.write(str(led), t), tools))
        writes += list(ex.map(lambda t: w.write(str(git_led), t), tools))
    tools = tools + tools
    ps = [PS_WRITE, PS_IO_WRITE] + PS_SHORT
    got = many([(w, 'Bash', c) for c in BASH_WRITES] + [(w, 'PowerShell', c) for c in ps]
               + [(w, 'Bash', 'cat ' + LEDGER)])
    want = 'ALLOW' if place == 'non-AID' else 'DENY'
    for t, v in zip(tools, writes):
        assert v[0] == want, (place, t, v)
    for c, v in zip(BASH_WRITES + ps, got[:-1]):
        assert v[0] == want, (place, c, v)
    assert got[-1][0] != 'DENY', (place, got[-1])


@pytest.mark.parametrize('place', [p for p in EVERY if p[:2] in ('p4', 'p5')])
def test_t21_guards_leave_ordinary_commands_alone(base, place):  # noqa: F811
    w = _w(base, place)
    led = w.P / '.aid' / 'pipeline' / 'cost-ledger.json'
    led.parent.mkdir(parents=True, exist_ok=True)
    led.write_text('{"total_usd": 1}', encoding='utf-8')
    for c, v in zip(P4_NOT_DENIED, many([(w, 'Bash', c) for c in P4_NOT_DENIED])):
        assert v[0] != 'DENY', (place, c, v)
