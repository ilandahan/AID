"""
Autoresearch frozen-harness guard (skills/autoresearch/bin/check-harness-immutable.mjs)

WHY THIS TEST:
- PROBLEM: three review rounds patched path SPELLINGS one at a time and an absolute path to the
  real checkout or the plugin cache still let the agent edit its own harness. The guard now
  protects files by ROLE (R1-R10 in reports/T6-acceptance.md) wherever they live.
- COST OF FAILURE: an autoresearch pass edits its rubric, scorer prompt, acceptance baseline or
  the guard itself, the score rises while the work does not, and the human commits code that
  was never validated.
- SUCCESS: the real script, spawned the way Claude Code runs it (node + stdin JSON), denies
  every AC attack form with the nested PreToolUse shape and allows the legitimate writes.
Each MUST acceptance criterion has tests named test_ac_<n>_...
"""
import json
import os
import re
import shutil
import subprocess

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GUARD = os.path.join(REPO_ROOT, 'skills', 'autoresearch', 'bin', 'check-harness-immutable.mjs')

pytestmark = pytest.mark.skipif(shutil.which('node') is None, reason='node not installed')

HARNESS = [  # checkout harness set H, relative to the checkout root
    'skills/autoresearch/SKILL.md',
    'skills/autoresearch/program.ar-function.md',
    'skills/autoresearch/bin/check-harness-immutable.mjs',
    'skills/reflection/SKILL.md',
    'skills/reflection/criteria/phase-4b-code-function.yaml',
    'agents/reflection-agent.md',
    'agents/phase4-intent-validator.md',
    'agents/phase5-acceptance-validator.md',
]
NON_HARNESS = ['skills/other-skill/SKILL.md', 'hooks/aid_guard.py', 'agents/developer.md']
PROJECT_FILES = [
    '.claude/settings.json', '.claude/settings.local.json', '.mcp.json', 'criteria/x.YAML',
    '.aid/context.json', '.aid/state.json', '.aid/pipeline/config.json',
    '.aid/pipeline/state.json', '.aid/pipeline/outer-counters.sidecar',
    '.aid/pipeline/T6/brief.md', '.aid/pipeline/T6/config.frozen.json',
    '.aid/pipeline/autoresearch/T6/config.json',
    '.aid/pipeline/autoresearch/T6/results.tsv', '.aid/qa/T6.yaml', 'src/a.js',
]
TOOLS = ['Write', 'Edit']


def _link_dir(link, target):
    if os.name == 'nt':
        import _winapi
        _winapi.CreateJunction(str(target), str(link))
    else:
        os.symlink(str(target), str(link), target_is_directory=True)


def _touch(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write('x')


@pytest.fixture(scope='module')
def F(tmp_path_factory):
    """Fixture F from the acceptance doc, under a root with a space and an apostrophe."""
    root = tmp_path_factory.mktemp('t6') / "it's root"
    C = root / 'C'
    K = root / 'K'
    cache = K / 'plugins' / 'cache' / 'AID' / 'aid' / '9.9.9'
    for base in (C, cache):
        for rel in HARNESS + NON_HARNESS:
            _touch(str(base / rel))
    FH = root / 'FH'
    _touch(str(FH / '.claude' / 'settings.json'))
    (FH / 'notes').mkdir(parents=True)
    P = root / 'P'
    for rel in PROJECT_FILES:
        _touch(str(P / rel))
    (P / 'tests').mkdir()
    _link_dir(P / '.claude' / 'skills', C / 'skills')
    _link_dir(P / '.claude' / 'agents', C / 'agents')
    (root / 'scratchpad').mkdir()
    return {'root': str(root), 'C': str(C), 'K': str(cache), 'FH': str(FH), 'P': str(P)}


def _input(tool, path, key='file_path'):
    if tool == 'NotebookEdit':
        return {'notebook_path': path, 'new_source': 'x'}
    if tool == 'MultiEdit':
        return {key: path, 'edits': [{'old_string': 'a', 'new_string': 'b'}]}
    if tool == 'Edit':
        return {key: path, 'old_string': 'a', 'new_string': 'b'}
    return {key: path, 'content': 'x'}


def _run(stdin, env_extra=None, argv=None):
    env = {k: v for k, v in os.environ.items()
           if k not in ('CLAUDE_PROJECT_DIR', 'CLAUDE_PLUGIN_ROOT', 'AID_HARNESS_GUARD_TEST_THROW')}
    env.update(env_extra or {})
    return subprocess.run(argv or ['node', GUARD], input=stdin, capture_output=True, text=True,
                          timeout=30, env=env)


def _call(tool, path, cwd, env_extra=None, tool_input=None):
    payload = {'tool_name': tool, 'tool_input': tool_input or _input(tool, path),
               'hook_event_name': 'PreToolUse', 'session_id': 's'}
    if cwd is not None:
        payload['cwd'] = cwd
    return _run(json.dumps(payload), env_extra)


def _denied(r, path=None):
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip(), f'ALLOWED but expected DENY ({path})'
    hso = json.loads(r.stdout)['hookSpecificOutput']
    assert hso['hookEventName'] == 'PreToolUse'
    assert hso['permissionDecision'] == 'deny'
    assert hso['permissionDecisionReason'].startswith('[autoresearch]')
    return hso['permissionDecisionReason']


def _allowed(r, path=None):
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == '', f'{path} was blocked: {r.stdout}'


def _mixed(rel):
    """Form (e): mixed case plus `..` traversal through the link."""
    if rel.startswith('skills/'):
        return '.CLAUDE/Skills/x/../' + rel[len('skills/'):]
    return '.claude/AGENTS/x/../' + rel[len('agents/'):]


# ---------- A. score-deciding files denied in every natural form ----------

@pytest.mark.parametrize('tool', TOOLS)
@pytest.mark.parametrize('rel', HARNESS)
def test_ac_1_checkout_harness_matrix(F, rel, tool):
    """Every harness file is denied relative/absolute through the link, at the real checkout
    path (round-3 repro 1), in the plugin cache (round-3 repro 2) and mixed-case with `..`."""
    P = F['P']
    forms = [
        '.claude/' + rel,
        os.path.join(P, '.claude', rel),
        os.path.join(F['C'], rel),
        os.path.join(F['K'], rel),
        _mixed(rel),
    ]
    for fp in forms:
        _denied(_call(tool, fp, P), fp)


AC2_TARGETS = [
    '.aid/pipeline/config.json', '.aid/context.json', '.aid/state.json', '.aid/qa/T6.yaml',
    '.aid/qa/T7.yaml', '.aid/pipeline/T6/brief.md', '.mcp.json', 'criteria/x.YAML',
    '.claude/settings.json', '.claude/settings.local.json',
    '.claude/skills/other-skill/SKILL.md', '.claude/agents/developer.md',
]


def _case_sensitive(P):
    return not os.path.exists(os.path.join(P, '.AID'))


@pytest.mark.parametrize('tool', TOOLS)
@pytest.mark.parametrize('rel', AC2_TARGETS)
def test_ac_2_project_local_matrix(F, rel, tool):
    """Project-local score inputs (config, WHY fallback, qa baseline incl. a NEW qa file,
    frozen brief, MCP, rubric, settings, linked skills/agents) are denied in 3 forms."""
    P = F['P']
    head, rest = rel.split('/', 1) if '/' in rel else (rel, '')
    mixed = head.upper() + '/x/../' + rest if rest else rel.upper()
    forms = [rel, os.path.join(P, rel)]
    # On a case-sensitive FS `.AID/.../brief.md` is a different, new file; R10 rightly allows it.
    if not (rel.endswith('brief.md') and _case_sensitive(P)):
        forms.append(mixed)
    for fp in forms:
        _denied(_call(tool, fp, P), fp)


@pytest.mark.parametrize('plugin_root', [None, 'unrelated'])
def test_ac_3_guard_identity_from_role_not_env(F, tmp_path, plugin_root):
    """The real guard and SKILL.md are denied from an unrelated cwd, regardless of
    CLAUDE_PLUGIN_ROOT: identity comes from role R3."""
    env = {'CLAUDE_PLUGIN_ROOT': str(tmp_path)} if plugin_root else None
    for fp in (GUARD, os.path.join(REPO_ROOT, 'skills', 'autoresearch', 'SKILL.md')):
        _denied(_call('Write', fp, str(tmp_path), env), fp)


def test_ac_3_checkout_as_project(F):
    """AID dogfoods itself with cwd = checkout: ordinary source stays writable, harness not."""
    C = F['C']
    for fp in ('hooks/aid_guard.py', os.path.join(C, 'hooks', 'aid_guard.py')):
        _allowed(_call('Write', fp, C), fp)
    for fp in ('skills/autoresearch/SKILL.md', 'agents/reflection-agent.md'):
        _denied(_call('Write', fp, C), fp)


def test_ac_4_file_symlink_alias(F):
    """A file symlink with an innocent name pointing at a harness file is denied (realpath)."""
    P = F['P']
    link = os.path.join(P, 'src', 'innocent.txt')
    if not os.path.lexists(link):
        try:
            os.symlink(os.path.join(F['C'], 'skills', 'autoresearch', 'SKILL.md'), link)
        except OSError as e:
            pytest.skip(f'OS refused to create a file symlink: {e}')
    _denied(_call('Write', 'src/innocent.txt', P))


def test_ac_4_directory_link_alias(F):
    """A junction/dir symlink under src/ pointing at skills/autoresearch is denied (realpath
    walk runs on every OS)."""
    P = F['P']
    link = os.path.join(P, 'src', 'lib')
    if not os.path.lexists(link):
        _link_dir(link, os.path.join(F['C'], 'skills', 'autoresearch'))
    _denied(_call('Write', 'src/lib/SKILL.md', P))
    _denied(_call('Edit', 'src/lib/SKILL.md', P))


@pytest.mark.skipif(os.name != 'nt', reason='Win32 path aliases only exist on Windows')
@pytest.mark.parametrize('rel', ['.mcp.json.', '.mcp.json ', '.mcp.json::$DATA',
                                 'criteria/x.YAML.', 'criteria/x.YAML::$DATA',
                                 '.aid/pipeline/config.json.'])
def test_ac_5_windows_path_aliases(F, rel):
    """Trailing dot/space and the default NTFS stream all land on the protected file."""
    _denied(_call('Write', rel, F['P']), rel)


@pytest.mark.skipif(os.name != 'nt', reason='8.3 short names only exist on Windows')
def test_ac_5_windows_short_name(F):
    """An 8.3 short name of .aid (AID~1) resolves to the protected path."""
    import ctypes
    P = F['P']
    buf = ctypes.create_unicode_buffer(1024)
    ctypes.windll.kernel32.GetShortPathNameW(os.path.join(P, '.aid'), buf, 1024)
    short = os.path.basename(buf.value)
    if not short or short.lower() == '.aid':
        pytest.skip('8.3 short names are disabled on this volume')
    _denied(_call('Write', short + '/pipeline/config.json', P))


# ---------- B. guard switch-off files ----------

def test_ac_6_disable_all_hooks_settings(F):
    """disableAllHooks in any settings file would switch the guard off; denied by role R6,
    including the user-level file passed as an absolute path (no HOME lookup)."""
    P = F['P']
    for fp in ('.claude/settings.local.json', os.path.join(P, '.claude', 'settings.json'),
               os.path.join(F['FH'], '.claude', 'settings.json')):
        ti = {'file_path': fp, 'content': '{"disableAllHooks":true}'}
        _denied(_call('Write', fp, P, tool_input=ti), fp)
    _denied(_call('Edit', '.claude/settings.local.json', P))


# ---------- C. sibling tools: the real frontmatter wiring ----------

def _frontmatter_entries():
    import yaml
    with open(os.path.join(REPO_ROOT, 'skills', 'autoresearch', 'SKILL.md'), encoding='utf-8') as f:
        text = f.read()
    fm = yaml.safe_load(text.split('---', 2)[1])
    return fm['hooks']['PreToolUse']


def _matches(matcher, tool):
    if re.fullmatch(r'[A-Za-z0-9_]+', matcher):
        return matcher == tool
    return re.fullmatch(matcher, tool) is not None


@pytest.mark.parametrize('tool', ['Write', 'Edit', 'MultiEdit', 'NotebookEdit'])
def test_ac_7_frontmatter_dispatch(F, tool):
    """Emulate Claude Code dispatch: select entries by matcher, substitute
    ${CLAUDE_PLUGIN_ROOT}, spawn the declared command, expect DENY for every edit tool."""
    pytest.importorskip('yaml')
    entries = [e for e in _frontmatter_entries() if _matches(e['matcher'], tool)]
    assert entries, f'no PreToolUse entry matches {tool}'
    P = F['P']
    path = ('.claude/skills/autoresearch/x.ipynb' if tool == 'NotebookEdit'
            else '.claude/skills/autoresearch/SKILL.md')
    payload = json.dumps({'tool_name': tool, 'tool_input': _input(tool, path), 'cwd': P,
                          'hook_event_name': 'PreToolUse'})
    for entry in entries:
        for h in entry['hooks']:
            argv = [h['command']] + [a.replace('${CLAUDE_PLUGIN_ROOT}', REPO_ROOT)
                                     for a in h.get('args', [])]
            _denied(_run(payload, argv=argv), path)


# ---------- D. fail closed ----------

@pytest.mark.parametrize('stdin', [
    'not json', 'null', '{}',
    json.dumps({'tool_input': {'content': 'x'}}),
    json.dumps({'tool_input': {'file_path': ''}}),
    json.dumps({'tool_input': {'file_path': 'src/a\u0000.js'}}),
    json.dumps({'tool_input': {'file_path': 'src/a.js'}, 'cwd': {'x': 1}}),
])
def test_ac_8_malformed_input_denies(F, stdin):
    """Unreadable or ambiguous hook input must deny, never fall through to allow."""
    _denied(_run(stdin))


def test_ac_9_internal_error_denies(F):
    """An exception after stdin is read must deny with rc 0; a crash (rc 1, no stdout) is a
    non-blocking hook error and the write would go through."""
    _denied(_call('Write', 'src/a.js', F['P'], {'AID_HARNESS_GUARD_TEST_THROW': '1'}))


# ---------- E. legitimate work keeps working ----------

AC10_ALLOWED = [
    'src/a.js', 'src/new_dir/not_yet/b.ts', 'tests/test_x.py', 'src/x.test.ts',
    'src/skills/other.ts', 'docs/criteria.md', 'src/agents/helper.md',
    'docs/.claude-settings.json', 'src/settings.json', 'src/claude/settings.json',
    '.aid/pipeline/state.json', '.aid/pipeline/autoresearch/T6/results.tsv',
    '.aid/pipeline/autoresearch/T6/config.json',
    '.aid/pipeline/autoresearch/T6/snapshots/src/a.js', '.aid/pipeline/outer-counters.sidecar',
    '.aid/pipeline/T7/brief.md',
    # per-task stage records written after an AR pass in the same session (FIX_TEST_CODE,
    # SELF_REVIEW); R8 must not deny them
    '.aid/pipeline/T6/fix-1.json', '.aid/pipeline/T6/self-review-2.json',
    # frozen per-task config created once at a NEW pipeline kickoff (R10 existing-only)
    '.aid/pipeline/T7/config.frozen.json',
]

# T15 (owner 2026-11-19, T15-7 / I-4): these QA verdict markers were listed in AC10_ALLOWED as
# files "the stop-qa hook tells the agent to write" (old validate-qa-gate.py:161). The gate no
# longer reads or asks for them (I-3: only a state.json qa_passed record passes) and I-4 makes
# them control files. They are NOT AR-3 acceptance sources, so this autoresearch guard still
# does not deny them (R8/R9 unchanged; one protected set lives in aid_guard.is_protected,
# INV-1); the AID phase gate is the layer that denies them, asserted below.
AC10_QA_MARKERS = ['.aid/qa/T6-review.json', '.aid/qa/T6-review-1.json', '.aid/qa/T6.qa-passed']


@pytest.mark.parametrize('tool', TOOLS)
@pytest.mark.parametrize('rel', AC10_QA_MARKERS)
def test_ac_10_qa_markers_not_an_autoresearch_role(F, rel, tool):
    """The autoresearch guard has no QA-marker role; it must not grow a second protected set."""
    _allowed(_call(tool, rel, F['P']), rel)


def _aid_gate_write(project, home, tool, rel):
    runner = os.path.join(REPO_ROOT, 'hooks', 'hook-runner.mjs')
    env = {k: v for k, v in os.environ.items() if k not in ('CLAUDE_PROJECT_DIR', 'CLAUDE_CONFIG_DIR')}
    env.update(HOME=str(home), USERPROFILE=str(home), AID_HOME=os.path.join(str(home), '.aid'))
    payload = {'session_id': 's-qa-marker-' + tool, 'cwd': str(project), 'tool_name': tool,
               'hook_event_name': 'PreToolUse', 'tool_input': _input(tool, rel)}
    return subprocess.run(['node', runner, 'phase-gate-write'], input=json.dumps(payload),
                          capture_output=True, text=True, cwd=str(project), env=env, timeout=60)


@pytest.mark.parametrize('tool', TOOLS)
@pytest.mark.parametrize('rel', AC10_QA_MARKERS)
def test_ac_10_qa_markers_denied_by_aid_gate_t15(tmp_path, rel, tool):
    """T15 flip: the same paths, in an AID project at Phase 4 (block), are denied by the AID
    phase gate as control files, so the agent cannot forge a QA verdict."""
    project, home = tmp_path / 'proj', tmp_path / 'home'
    (project / '.aid' / 'hooks').mkdir(parents=True)
    (project / '.claude').mkdir()
    (project / '.claude' / 'settings.json').write_text('{}', encoding='utf-8')
    (project / '.aid' / 'state.json').write_text(json.dumps({'current_phase': 4}), encoding='utf-8')
    (project / '.aid' / 'hooks' / 'config.json').write_text(json.dumps(
        {'enforcement': {'phase_gate_write': 'block', 'phase_gate_bash': 'block'}}), encoding='utf-8')
    (home / '.claude').mkdir(parents=True)
    r = _aid_gate_write(project, home, tool, rel)
    assert r.returncode == 0, r.stderr[-600:]
    assert r.stdout.strip(), f'{rel} was ALLOWED by the AID gate; expected DENY (T15-7)'
    hso = json.loads(r.stdout)['hookSpecificOutput']
    assert hso['permissionDecision'] == 'deny', r.stdout
    assert 'control file' in hso['permissionDecisionReason'], r.stdout


@pytest.mark.parametrize('tool', TOOLS)
@pytest.mark.parametrize('rel', AC10_ALLOWED)
def test_ac_10_legitimate_writes_allowed(F, rel, tool):
    """Ordinary source, tests (TDD after AR_DESIGN), role look-alikes, runner-owned files and a
    NEW brief stay writable."""
    _allowed(_call(tool, rel, F['P']), rel)


@pytest.mark.parametrize('tool', TOOLS)
def test_ac_10_outside_project_non_role_files_allowed(F, tool):
    """Scratchpad and predictions.jsonl outside the project are not role files."""
    for fp in (os.path.join(F['root'], 'scratchpad', 'note.md'),
               os.path.join(F['FH'], 'notes', 'predictions.jsonl'),
               # /aid-end and /phase-approve write the user-level feedback queue
               os.path.join(F['FH'], '.aid', 'feedback', 'pending', '20261116.json')):
        _allowed(_call(tool, fp, F['P']), fp)


@pytest.mark.parametrize('tool', TOOLS)
def test_ac_10_per_task_frozen_config_still_denied(F, tool):
    """The per-task stage-record exception does not open the frozen per-task config."""
    rel = '.aid/pipeline/T6/config.frozen.json'
    forms = [rel]
    # On a case-sensitive FS the mixed-case path is a different, new file; R10 rightly allows it.
    if not _case_sensitive(F['P']):
        forms.append('.AID/Pipeline/T6/x/../CONFIG.FROZEN.json')
    for fp in forms:
        _denied(_call(tool, fp, F['P']), fp)


@pytest.mark.parametrize('tool', TOOLS)
def test_r9_new_yml_acceptance_source_denied(F, tool):
    """Narrowing R9 to *.yaml/*.yml keeps a NEW .yml acceptance source denied."""
    _denied(_call(tool, '.aid/qa/T8.yml', F['P']), '.aid/qa/T8.yml')


@pytest.mark.parametrize('name,target', [
    ('dang_qa.yaml', ('P', '.aid/qa/T9.yaml')),
    ('dang_settings.json', ('FH', '.claude/settings.local.json')),
])
def test_ac_4_dangling_symlink_to_missing_role_file(F, name, target):
    """A file symlink whose target does not exist yet is judged by the target's role: a Write
    through it would CREATE an acceptance source / settings file."""
    tgt = os.path.join(F[target[0]], *target[1].split('/'))
    assert not os.path.exists(tgt)
    link = os.path.join(F['P'], 'src', name)
    if not os.path.lexists(link):
        try:
            os.symlink(tgt, link)
        except OSError as e:
            pytest.skip(f'OS refused to create a file symlink: {e}')
    _denied(_call('Write', 'src/' + name, F['P']), name)
    # legitimate control: a dangling link to an ordinary missing source file stays writable
    ok = os.path.join(F['P'], 'src', 'dang_ok.js')
    if not os.path.lexists(ok):
        os.symlink(os.path.join(F['P'], 'src', 'not_yet.js'), ok)
    _allowed(_call('Write', 'src/dang_ok.js', F['P']), 'src/dang_ok.js')


@pytest.mark.parametrize('tool', ['MultiEdit', 'NotebookEdit'])
def test_ac_10_sibling_tools_allowed_on_ordinary_files(F, tool):
    """MultiEdit/NotebookEdit on ordinary source stay allowed: the guard reads notebook_path
    instead of failing closed on a NotebookEdit that has no file_path."""
    path = 'src/nb.ipynb' if tool == 'NotebookEdit' else 'src/a.js'
    _allowed(_call(tool, path, F['P']), path)


def test_ac_11_cwd_fallback_to_project_dir(F):
    """Without cwd the guard resolves against CLAUDE_PROJECT_DIR."""
    env = {'CLAUDE_PROJECT_DIR': F['P']}
    _allowed(_call('Write', 'src/a.js', None, env))
    _denied(_call('Write', '.mcp.json', None, env))


# ---------- F. honest messaging ----------

@pytest.mark.parametrize('rel', ['.aid/qa/T7.yaml', '.claude/skills/autoresearch/SKILL.md',
                                 '.claude/settings.json'])
def test_ac_12_reason_names_path_and_session(F, rel):
    """The deny reason names the blocked path and says the guard lasts the whole session."""
    reason = _denied(_call('Write', rel, F['P']))
    assert rel in reason
    assert 'session' in reason
