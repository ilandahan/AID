"""
T15 WS-F: scripts and installers (T15-46..T15-49).

WHY THIS FILE:
- PROBLEM: /start-project and scripts/init-project.sh exited 1 under Git Bash on
  Windows (G9-04/G9-04h). An installed AID's `.claude/` holds relative mirror links
  (`agents -> ../agents`); `cp -r` copied them as links, Git Bash cannot create a link
  whose relative target does not exist at the destination, and `set -e` stopped the
  script. In link mode the failed MSYS `ln -s` left a half-copied `.claude/`, so the
  copy fallback nested into `.claude/.claude`.
- The script also wrote `.aid/state.json` itself (T3: `aid_session.py` is the only
  writer), used `sed -i`, and generated secret placeholders in `.env.example`.
- The installers created a token `.env` and ran `npm install` (no lockfile pinning).
- COST OF FAILURE: a new user's first command fails; tokens end up in a plaintext file.
- SUCCESS: the tests below pass on Git Bash (Windows) and bash (Linux).
"""
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
INIT_SCRIPT = REPO_ROOT / 'scripts' / 'init-project.sh'
SECRET_KEY = re.compile(r'(TOKEN|API_KEY|SECRET|PASSWORD|_PAT)\s*=', re.I)


def _posix_bash():
    """Git Bash on Windows (System32 bash.exe is WSL, which cannot see these paths)."""
    if os.name == 'nt':
        git = shutil.which('git')
        here = Path(git).resolve() if git else None
        for cand in ([here.parents[1] / 'bin' / 'bash.exe',
                      here.parents[2] / 'bin' / 'bash.exe'] if here else []):
            if cand.is_file():
                return str(cand)
        return None
    return shutil.which('bash')


BASH = _posix_bash()
needs_bash = pytest.mark.skipif(BASH is None, reason='no POSIX bash available')

# The tree commands/start-project.md documents ("What Gets Created").
DOCUMENTED_FILES = [
    '.aid/context.json', 'CLAUDE.md', 'docs/prd/PRD.md', 'docs/tech-spec/TECH-SPEC.md',
    'src/app/layout.tsx', 'src/app/page.tsx', '.env.example', '.gitignore',
    'package.json', 'tsconfig.json', 'README.md', '.claude/settings.json',
]
DOCUMENTED_DIRS = [
    '.claude', 'skills', 'src/components/atoms', 'src/components/molecules',
    'src/components/organisms', 'src/components/templates', 'src/hooks', 'src/utils',
    'src/types', 'src/styles', 'tests/unit', 'tests/integration', 'tests/e2e',
]


def _fake_installed_aid(root):
    """A minimal installed AID: real script, and `.claude/` mirror links like install.sh makes."""
    aid = root / 'aid'
    (aid / 'scripts').mkdir(parents=True)
    shutil.copy(INIT_SCRIPT, aid / 'scripts' / 'init-project.sh')
    (aid / 'CLAUDE.md').write_text('# fixture\n', encoding='utf-8')
    for name, rel in (('skills', 'x/SKILL.md'), ('agents', 'a.md'),
                      ('commands', 'c.md'), ('hooks', 'h.py')):
        (aid / name / rel).parent.mkdir(parents=True, exist_ok=True)
        (aid / name / rel).write_text('fixture\n', encoding='utf-8')
    claude = aid / '.claude'
    (claude / 'templates').mkdir(parents=True)
    (claude / 'templates' / 't.txt').write_text('t\n', encoding='utf-8')
    (claude / 'settings.json').write_text('{}\n', encoding='utf-8')
    (claude / 'settings.local.json').write_text('{"permissions":{"allow":["Bash"]}}\n',
                                                 encoding='utf-8')
    try:
        for name in ('agents', 'commands', 'hooks', 'skills'):
            os.symlink('../' + name, claude / name, target_is_directory=True)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f'cannot create the mirror symlinks here: {exc}')
    return aid


def _run_init(script, cwd, home, *args):
    env = dict(os.environ, HOME=str(home), USERPROFILE=str(home))
    env.pop('CLAUDE_PROJECT_DIR', None)
    env.pop('CLAUDE_CONFIG_DIR', None)
    return subprocess.run([BASH, Path(script).as_posix(), *args], cwd=str(cwd), env=env,
                          capture_output=True, text=True, encoding='utf-8',
                          errors='replace', timeout=600)


def _assert_documented_project(proj, out):
    for rel in DOCUMENTED_FILES:
        assert (proj / rel).is_file(), f'{rel} missing\n{out}'
    for rel in DOCUMENTED_DIRS:
        assert (proj / rel).is_dir(), f'{rel}/ missing\n{out}'
    assert not (proj / '.claude' / '.claude').exists(), 'copy fallback nested .claude/.claude'
    # T3: aid_session.py is the only writer of .aid/state.json.
    assert not (proj / '.aid' / 'state.json').exists(), 'init-project.sh wrote .aid/state.json'
    json.loads((proj / '.aid' / 'context.json').read_text(encoding='utf-8'))
    assert '/aid-start' in out, 'the script must end by telling the user to run /aid-start'


@needs_bash
@pytest.mark.parametrize('mode', ['link', 'copy'])
def test_t15_46_init_project_from_installed_copy(tmp_path, mode):
    """The G9-04 repro: an installed AID whose .claude/ holds relative mirror links."""
    aid = _fake_installed_aid(tmp_path)
    work, home = tmp_path / 'work', tmp_path / 'home'
    work.mkdir()
    home.mkdir()
    extra = ['--copy'] if mode == 'copy' else []
    r = _run_init(aid / 'scripts' / 'init-project.sh', work, home,
                  't15demo', '--no-deps', '--no-git', *extra)
    out = r.stdout + r.stderr
    assert r.returncode == 0, out
    proj = work / 't15demo'
    _assert_documented_project(proj, out)
    # The mirrored content is reachable (copied with links followed, or linked).
    assert (proj / '.claude' / 'agents' / 'a.md').is_file(), out
    assert (proj / 'skills' / 'x' / 'SKILL.md').is_file(), out
    if mode == 'copy':
        assert not (proj / '.claude' / 'settings.local.json').exists(), \
            "the AID install's machine-local permissions were copied into the project"


@needs_bash
@pytest.mark.parametrize('mode', ['link', 'copy'])
def test_t15_46_init_project_from_repo_checkout(tmp_path, mode):
    work, home = tmp_path / 'work', tmp_path / 'home'
    work.mkdir()
    home.mkdir()
    extra = ['--copy'] if mode == 'copy' else []
    r = _run_init(INIT_SCRIPT, work, home, 't15demo', '--no-deps', '--no-git', *extra)
    out = r.stdout + r.stderr
    assert r.returncode == 0, out
    _assert_documented_project(work / 't15demo', out)


@needs_bash
def test_t15_46_generated_env_example_has_no_secret_placeholders(tmp_path):
    work, home = tmp_path / 'work', tmp_path / 'home'
    work.mkdir()
    home.mkdir()
    r = _run_init(INIT_SCRIPT, work, home, 't15demo', '--no-deps', '--no-git', '--copy')
    assert r.returncode == 0, r.stdout + r.stderr
    text = (work / 't15demo' / '.env.example').read_text(encoding='utf-8')
    for line in text.splitlines():
        if line.strip().startswith('#'):
            continue
        assert not SECRET_KEY.search(line), f'secret placeholder in .env.example: {line}'
        assert not re.search(r'://[^/\s:@]+:[^/\s@]+@', line), f'credential in URL: {line}'


@needs_bash
@pytest.mark.parametrize('name', ['../t15-escaped', 'a b', 'x;y', 'x$(id)'])
def test_t15_46_rejects_unsafe_project_name(tmp_path, name):
    """The name becomes a folder and is written into JSON: only a plain name is accepted."""
    work, home = tmp_path / 'work', tmp_path / 'home'
    work.mkdir()
    home.mkdir()
    before = sorted(p.name for p in tmp_path.iterdir())
    r = _run_init(INIT_SCRIPT, work, home, name, '--no-deps', '--no-git', '--copy')
    assert r.returncode != 0, r.stdout + r.stderr
    assert list(work.iterdir()) == [], 'a project folder was created for an invalid name'
    assert sorted(p.name for p in tmp_path.iterdir()) == before, 'wrote outside the cwd'


def test_t15_46_no_sed_in_place_in_scripts():
    for path in (REPO_ROOT / 'scripts').glob('*.sh'):
        for n, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if line.strip().startswith('#'):
                continue
            assert not re.search(r'\bsed\s+(-[A-Za-z]*\s+)*-i', line), f'{path.name}:{n}: {line}'


def test_t15_46_init_project_does_not_write_state_json():
    text = INIT_SCRIPT.read_text(encoding='utf-8')
    code = '\n'.join(l for l in text.splitlines() if not l.strip().startswith('#'))
    assert not re.search(r'>\s*\.aid/state\.json', code)
    assert '/aid-start' in code


# --- T15-47 installers -----------------------------------------------------------

def _code_lines(path, comment):
    return [l for l in path.read_text(encoding='utf-8').splitlines()
            if l.strip() and not l.strip().upper().startswith(comment)]


@pytest.mark.parametrize('name,comment', [('install.sh', '#'), ('install.bat', 'REM')])
def test_t15_47_installer_creates_no_env_file(name, comment):
    path = REPO_ROOT / name
    code = '\n'.join(_code_lines(path, comment))
    assert not re.search(r'\b(cp|copy)\s+"?\.env\.example"?\s+"?\.env"?', code), \
        f'{name} still copies .env.example to .env'
    assert 'INSTALLATION.md' in code and 'keystore' in code.lower(), \
        f'{name} must point at the INSTALLATION.md keystore table'


@pytest.mark.parametrize('name,comment', [('install.sh', '#'), ('install.bat', 'REM')])
def test_t15_47_installer_uses_npm_ci(name, comment):
    lines = _code_lines(REPO_ROOT / name, comment)
    runs = [l for l in lines if not re.match(r'\s*(echo|log_\w+)\b', l, re.I)]
    assert not [l for l in runs if re.search(r'\bnpm\s+install\b', l)], \
        f'{name} still runs npm install'
    assert len([l for l in runs if re.search(r'\bnpm\s+ci\b', l)]) >= 2, \
        f'{name} must run npm ci for the root and storybook-preview'


def test_t15_47_init_project_npm_install_is_the_documented_exception():
    text = INIT_SCRIPT.read_text(encoding='utf-8')
    assert re.search(r'^\s*npm install', text, re.M)
    assert re.search(r'#.*npm ci.*\n#.*lockfile', text) or \
        re.search(r'#[^\n]*no package-lock\.json', text), \
        'the npm install exception (no lockfile in a new project) must be documented'


def test_t15_47_install_bat_stays_crlf():
    data = (REPO_ROOT / 'install.bat').read_bytes()
    assert data.count(b'\n') == data.count(b'\r\n'), 'install.bat has LF-only lines'


# --- T15-48 /start-project ---------------------------------------------------------

def test_t15_48_start_project_calls_the_plugin_script():
    text = (REPO_ROOT / 'commands' / 'start-project.md').read_text(encoding='utf-8')
    assert 'bash "${CLAUDE_PLUGIN_ROOT}/scripts/init-project.sh" <project-name>' in text
    assert './scripts/init-project.sh' not in text
    assert re.search(r'Claude Code asks you to confirm', text)
    assert '0-5' in text
    assert '8 phases' not in text and '/phase 5' not in text and '/phase 1' not in text
    assert '/aid-start' in text


def test_t15_48_start_project_does_not_promise_prompt_in_bypass_mode():
    """R2-E3: no ask RULE covers init-project.sh, only the hook's ask, and Claude Code
    does not document that a hook's ask prompts under bypassPermissions. The confirm
    promise must carry the same caveat as yolo.md / breather-start.md."""
    text = ' '.join((REPO_ROOT / 'commands' / 'start-project.md')
                    .read_text(encoding='utf-8').split())
    assert '--dangerously-skip-permissions' in text
    assert re.search(r'(?i)do not count on a prompt in (that|this) mode', text)


# --- T15-49 linker guard and settings template -------------------------------------

def test_t15_49_settings_template_has_no_bare_edit_or_write():
    data = json.loads((REPO_ROOT / '.claude' / 'settings.json').read_text(encoding='utf-8'))
    allow = data['permissions']['allow']
    for tool in ('Edit', 'Write', 'MultiEdit', 'NotebookEdit'):
        assert tool not in allow, f'bare {tool} allowed in the settings template'
    scoped = [r for r in allow if re.match(r'(Edit|Write)\(', r)]
    assert scoped and all(re.fullmatch(r'(Edit|Write)\(/[^)\s]+\)', r) for r in scoped), allow


def test_t15_49_gitignore_template_matches_d3_report_path():
    text = (REPO_ROOT / '.claude' / 'templates' / 'gitignore-aid-patterns.txt').read_text(
        encoding='utf-8')
    rules = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith('#')]
    assert '.aid/qa/reports/' in rules
    assert not [r for r in rules if 'review' in r], 'old *-review-*.json marker pattern left'


def test_t15_49_link_guard_lists_include_mcp_json_example():
    src = (REPO_ROOT / 'testing' / 'e2e' / 'test_link_project_guards.py').read_text(
        encoding='utf-8')
    lists = re.findall(r"parametrize\('template',\s*\[([^\]]*)\]", src)
    assert len(lists) >= 3
    assert all("'.mcp.json.example'" in l for l in lists), lists
