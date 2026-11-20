"""
T17 WS-D: install, link-project and scripts (T17-acceptance.md, T17-40 .. T17-44).

WHY THESE TESTS:
- PROBLEM: link-project.sh printed "[LINK]" for what Git Bash had silently copied (MSYS
  copies by default), so a project looked linked and never saw an AID update
  (g9-link-sh-silent-copy). link-project.sh and link-project.bat each appended `.mcp.json`
  in their own spelling and missed the other's, so a project linked with both got it twice,
  and the hook audit log `.aid/audit/` was never ignored (g9-link-gitignore-dup, U-10).
  `init-project.sh --copy` handed a new project AID's legacy shell hook lines and no phase
  gate (U-13). Two T16 tests depended on the checkout path and on a race (U-04, U-19).
  `read` without -r dropped the backslashes of a typed Windows path (U-24).
- COST OF FAILURE: a stale, unprotected project that claims to be linked; an audit log that
  ends up in git; a CI-only red test.
- SUCCESS: the printed label is what is on disk; each I-26 line exists once whatever mix of
  linkers ran; a copied scaffold registers the runner hooks; the tests hold on any checkout.

Harness: the real scripts, fake HOME/USERPROFILE/AID_HOME, CLAUDE_PROJECT_DIR /
CLAUDE_CONFIG_DIR / CLAUDE_PLUGIN_ROOT unset, probe projects under a drive-root temp dir on
Windows (a ~/.aid/state.json would make every folder below the profile an AID project).
"""
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
LINK_SH = REPO / 'link-project.sh'
LINK_BAT = REPO / 'link-project.bat'
INIT_SCRIPT = REPO / 'scripts' / 'init-project.sh'
HELPER = REPO / 'scripts' / 'ensure-gitignore.mjs'
NODE = shutil.which('node')
I26 = ['.mcp.json', '.aid/audit/']
COPY_NOTE = 'a copy: AID updates will not reach it; re-run link-project after updating AID'


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
needs_bash = pytest.mark.skipif(BASH is None or NODE is None, reason='needs a POSIX bash and node')
needs_bat = pytest.mark.skipif(os.name != 'nt' or NODE is None, reason='link-project.bat runs on Windows')
needs_node = pytest.mark.skipif(NODE is None, reason='needs node')


def _marker_above(p):
    return any((d / '.aid' / 'state.json').is_file() or (d / '.aid' / 'hooks' / 'config.json').is_file()
               for d in [p] + list(p.parents))


def _is_link(path):
    try:
        st = os.lstat(path)
    except OSError:
        return False
    if stat.S_ISLNK(st.st_mode):
        return True
    return bool(getattr(st, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0))


def _safe_rmtree(root):
    """Remove a probe tree without descending into links (they point at THIS checkout)."""
    root = str(root)
    if not os.path.exists(root) and not _is_link(root):
        return
    if _is_link(root):
        try:
            os.rmdir(root)
        except OSError:
            os.unlink(root)
        return
    if os.path.isdir(root):
        for name in os.listdir(root):
            _safe_rmtree(os.path.join(root, name))
        os.chmod(root, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
        os.rmdir(root)
    else:
        os.chmod(root, stat.S_IWRITE | stat.S_IREAD)
        os.unlink(root)


@pytest.fixture
def base(tmp_path):
    """A drive-root temp dir (Windows) with no AID marker above it."""
    alt = Path(tempfile.mkdtemp(prefix='aid-t17-', dir=tmp_path.anchor if os.name == 'nt' else str(tmp_path)))
    if _marker_above(alt):
        _safe_rmtree(alt)
        pytest.skip('no directory without an AID marker ancestor is available')
    (alt / 'home' / '.claude').mkdir(parents=True)
    (alt / 'proj').mkdir()
    yield alt
    _safe_rmtree(alt)


def _env(home, path_prefix=None):
    env = dict(os.environ, HOME=str(home), USERPROFILE=str(home), AID_HOME=str(Path(home) / '.aid'))
    for k in ('CLAUDE_PROJECT_DIR', 'CLAUDE_CONFIG_DIR', 'CLAUDE_PLUGIN_ROOT', 'MSYS'):
        env.pop(k, None)
    if path_prefix is not None:
        env['PATH'] = str(path_prefix) + os.pathsep + env.get('PATH', '')
    return env


def _run(cmd, cwd, env, stdin=None):
    p = subprocess.run(cmd, cwd=str(cwd), env=env, input=stdin,
                       stdin=None if stdin is not None else subprocess.DEVNULL,
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
    return p.returncode, p.stdout + p.stderr


def link_sh(target, home, path_prefix=None):
    if path_prefix is None:
        return _run([BASH, LINK_SH.as_posix(), Path(target).as_posix(), '--force'], REPO, _env(home))
    # Git Bash's launcher puts /usr/bin first on PATH, so the prefix is set inside bash.
    inner = ('d="$1"; shift; if command -v cygpath >/dev/null 2>&1; then d="$(cygpath -u "$d")"; fi; '
             'PATH="$d:$PATH"; export PATH; exec bash "$@"')
    return _run([BASH, '-c', inner, 'link', str(path_prefix), LINK_SH.as_posix(),
                 Path(target).as_posix(), '--force'], REPO, _env(home))


def link_bat(target, home):
    return _run([str(LINK_BAT), str(target), '--force'], REPO, _env(home))


def _ignore_lines(target):
    return (Path(target) / '.gitignore').read_bytes()


def _assert_each_once(raw):
    lines = [l.rstrip(b'\r') for l in raw.split(b'\n')]
    for want in I26:
        assert lines.count(want.encode()) == 1, (want, raw)


# --- T17-40 link-project.sh reports links and copies honestly -------------------------------

LABEL = re.compile(r'^\s*\[(LINK|COPY)\] (\.claude/\w+|CLAUDE\.md)\b', re.M)


def _labels(out):
    return LABEL.findall(out)


def _label_path(target, label):
    return Path(target) / label


@needs_bash
def test_t17_40_printed_label_equals_what_is_on_disk(base):
    """Whatever the machine's symlink privilege gives, [LINK] only for a real symlink."""
    T, H = base / 'proj', base / 'home'
    rc, out = link_sh(T, H)
    assert rc == 0, out
    labels = _labels(out)
    assert {lbl for _, lbl in labels} == {'.claude/commands', '.claude/skills', '.claude/agents',
                                          '.claude/references', '.claude/rules', '.claude/hooks',
                                          'CLAUDE.md'}, out
    for kind, lbl in labels:
        p = _label_path(T, lbl)
        assert p.exists(), (lbl, out)
        assert (kind == 'LINK') == os.path.islink(str(p)), (kind, lbl, out)
        if kind == 'COPY':
            assert COPY_NOTE in out, out
    links = sum(1 for k, _ in labels if k == 'LINK')
    assert 'Symbolic links (auto-update from AID): {}'.format(links) in out, out
    copies = len(labels) - links
    if copies:
        assert re.search(r'^Copies \(AID updates will NOT reach them.*: {}$'.format(copies), out, re.M), out


@needs_bash
def test_t17_40_a_copying_ln_is_reported_as_copy(base):
    """Git Bash without native links: `ln -s` copies and exits 0 (simulated by a copying `ln`
    first on PATH). Every item is labelled [COPY], and the summary counts it as a copy."""
    T, H = base / 'proj', base / 'home'
    fake = base / 'fakebin'
    fake.mkdir()
    ln = fake / 'ln'
    ln.write_bytes(b'#!/bin/sh\n# a copying ln, like MSYS without winsymlinks\n'
                   b'[ "$1" = "-s" ] && shift\ncp -R "$1" "$2"\n')
    ln.chmod(0o755)
    rc, out = link_sh(T, H, path_prefix=fake)
    assert rc == 0, out
    labels = _labels(out)
    assert len(labels) == 7, out
    for kind, lbl in labels:
        assert kind == 'COPY', (lbl, out)
        assert not os.path.islink(str(_label_path(T, lbl))), lbl
    assert out.count(COPY_NOTE) == 7, out
    assert 'Symbolic links (auto-update from AID): 0' in out, out
    assert re.search(r'^Copies \(AID updates will NOT reach them.*: 7$', out, re.M), out


# --- T17-41 .gitignore lines are added once (I-26) -------------------------------------------

@needs_bash
def test_t17_41_sh_then_sh_no_final_newline(base):
    T, H = base / 'proj', base / 'home'
    (T / '.gitignore').write_bytes(b'node_modules')     # no final newline
    for _ in range(2):
        rc, out = link_sh(T, H)
        assert rc == 0, out
    assert _ignore_lines(T) == b'node_modules\n.mcp.json\n.aid/audit/\n'
    assert out.count('gitignore-aid-patterns.txt') == 1, out


@needs_bash
def test_t17_41_init_project_then_link_project(base):
    work, H = base / 'work', base / 'home'
    work.mkdir()
    rc, out = _run([BASH, INIT_SCRIPT.as_posix(), 't17demo', '--no-git', '--no-deps', '--copy'],
                   work, _env(H))
    assert rc == 0, out
    T = work / 't17demo'
    before = _ignore_lines(T)
    assert b'.aid/audit/\n' in before, before
    rc, out = link_sh(T, H)
    assert rc == 0, out
    after = _ignore_lines(T)
    _assert_each_once(after)
    assert after.startswith(before), 'init-project lines were changed'
    assert after[len(before):] == b'.mcp.json\n', after[len(before):]


@needs_bash
@needs_bat
@pytest.mark.parametrize('order', [('sh', 'bat'), ('bat', 'sh'), ('bat', 'bat')], ids='-'.join)
@pytest.mark.parametrize('initial,eol', [(b'node_modules', b'\n'),
                                         (b'node_modules\r\ndist\r\n', b'\r\n')], ids=['lf', 'crlf'])
def test_t17_41_any_mix_of_linkers_adds_each_line_once(base, order, initial, eol):
    T, H = base / 'proj', base / 'home'
    (T / '.gitignore').write_bytes(initial)
    for which in order:
        rc, out = (link_sh if which == 'sh' else link_bat)(T, H)
        assert rc == 0, (which, out)
    raw = _ignore_lines(T)
    _assert_each_once(raw)
    lines = raw.split(b'\n')
    assert b'' not in [l.rstrip(b'\r') for l in lines[:-1]], ('a blank line was inserted', raw)
    if eol == b'\r\n':
        assert raw.count(b'\n') == raw.count(b'\r\n'), ('LF-only line in a CRLF file', raw)
    else:
        assert b'\r' not in raw, ('CR in an LF file', raw)


HELPER_CASES = [
    # (initial bytes or None for no file, expected bytes after)
    (None, b'.mcp.json\n.aid/audit/\n'),
    (b'', b'.mcp.json\n.aid/audit/\n'),
    (b'node_modules', b'node_modules\n.mcp.json\n.aid/audit/\n'),
    (b'node_modules\r\n', b'node_modules\r\n.mcp.json\r\n.aid/audit/\r\n'),
    (b'a\r\n.mcp.json \t\r\n', b'a\r\n.mcp.json \t\r\n.aid/audit/\r\n'),
    (b'\xef\xbb\xbf.mcp.json\n.aid/audit/', b'\xef\xbb\xbf.mcp.json\n.aid/audit/'),
    (b'# x\n/.aid/audit/\n', b'# x\n/.aid/audit/\n.mcp.json\n.aid/audit/\n'),
]


@needs_node
@pytest.mark.parametrize('initial,expected', HELPER_CASES)
def test_t17_41_helper_rules(tmp_path, initial, expected):
    """I-26 line rules: trailing CR/spaces/tabs ignored, final newline added first, the file's
    own line ending, no blank line, nothing rewritten; a second run changes nothing."""
    gi = tmp_path / '.gitignore'
    if initial is not None:
        gi.write_bytes(initial)
    for _ in range(2):
        p = subprocess.run(['node', str(HELPER), str(tmp_path), *I26], capture_output=True, text=True,
                           timeout=60)
        assert p.returncode == 0, p.stderr
        assert gi.read_bytes() == expected
    assert 'gitignore-aid-patterns.txt' in p.stdout


# --- T17-42 no legacy hook entries in shipped templates (U-13) ------------------------------

LEGACY = re.compile(r'bash \.claude/hooks/|\.claude/hooks/validate-qa-gate\.py')


def test_t17_42_templates_and_scripts_carry_no_legacy_hook_entry():
    hits = []
    for root in (REPO / '.claude' / 'templates', REPO / 'scripts'):
        for p in root.rglob('*'):
            if not p.is_file():
                continue
            for n, line in enumerate(p.read_text(encoding='utf-8', errors='replace').splitlines(), 1):
                s = line.strip()
                if s.startswith(('#', '//')):
                    continue
                if LEGACY.search(line):
                    hits.append('{}:{}: {}'.format(p.relative_to(REPO), n, s))
    assert hits == [], hits


@needs_bash
def test_t17_42_copied_scaffold_registers_the_runner_hooks(base):
    """init-project.sh --copy copies AID's .claude/ (whose settings.json still holds the legacy
    lines, an owner-action control file); the scaffold then registers plugin.json's hooks."""
    work, H = base / 'work', base / 'home'
    work.mkdir()
    rc, out = _run([BASH, INIT_SCRIPT.as_posix(), 't17demo', '--no-git', '--no-deps', '--copy'],
                   work, _env(H))
    assert rc == 0, out
    data = json.loads((work / 't17demo' / '.claude' / 'settings.json').read_text(encoding='utf-8'))
    flat = json.dumps(data)
    assert not LEGACY.search(flat), flat
    assert data['hooks'].get('PreToolUse'), data['hooks']
    for g in data['hooks']['PreToolUse']:
        for h in g['hooks']:
            assert h['args'][0].endswith('/hooks/hook-runner.mjs'), h


# --- T17-43 Windows path tests are checkout-independent and race-free (U-04, U-19) ---------

def test_t17_43_t16_69_uses_the_import_time_value(monkeypatch):
    """U-19: test_t16_69 must not re-run _cucumber_runnable(); node_modules may change between
    test_installation's import and the check. Simulate that change."""
    sys.path.insert(0, str(HERE))
    import test_installation
    import test_t15_docs
    import test_t16_scripts
    then = test_installation._CUCUMBER_SKIP
    later = None if then is not None else '@cucumber/cucumber is not installed'
    monkeypatch.setattr(test_t15_docs, '_cucumber_runnable', lambda: later)
    test_t16_scripts.test_t16_69_cucumber_check_uses_the_engines_skip()


PLAIN_COPY_DIRS = ('.claude-plugin', 'hooks', 'scripts', 'memory-system', 'references',
                   'commands', 'skills', 'agents', 'rules')
PLAIN_COPY_FILES = ('link-project.sh', 'link-project.bat', 'CLAUDE.md', '.mcp.json.mac',
                    '.mcp.json.windows', os.path.join('.claude', 'settings.json'),
                    os.path.join('testing', 'e2e', 'test_t16_scripts.py'))


@needs_bash
@pytest.mark.skipif(os.name != 'nt', reason='the apostrophe-path assertion is Windows-only')
def test_t17_43_t16_63_passes_from_a_plain_checkout(base):
    """U-04: test_t16_63 run from a checkout whose path has no space or apostrophe."""
    plain = base / 'plainaid'
    skip = shutil.ignore_patterns('__pycache__', 'node_modules', '.pytest_cache', 'tests')
    for d in PLAIN_COPY_DIRS:
        shutil.copytree(str(REPO / d), str(plain / d), ignore=skip)
    for f in PLAIN_COPY_FILES:
        (plain / f).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(REPO / f), str(plain / f))
    assert "'" not in str(plain) and ' ' not in str(plain)
    e2e = plain / 'testing' / 'e2e'
    p = subprocess.run([sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider',
                        'test_t16_scripts.py::test_t16_63_link_registers_plugin_hooks_and_they_gate[sh]'],
                       cwd=str(e2e), env=dict(_env(base / 'home'), PYTHONDONTWRITEBYTECODE='1'),
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=900)
    assert p.returncode == 0, (p.stdout + p.stderr)[-3000:]
    assert '1 passed' in p.stdout, p.stdout[-2000:]


# --- T17-44 read -r in link-project.sh (U-24) ------------------------------------------------

def test_t17_44_every_read_in_link_project_sh_has_r():
    text = LINK_SH.read_text(encoding='utf-8')
    reads = re.findall(r'^\s*read\b([^\n]*)', text, re.M)
    assert reads, 'no read found'
    for args in reads:
        assert re.match(r'\s+-r\b', args), args
    sc = shutil.which('shellcheck')
    if sc:
        p = subprocess.run([sc, '-S', 'info', '-i', 'SC2162', str(LINK_SH)], capture_output=True, text=True)
        assert p.returncode == 0, p.stdout


@needs_bash
def test_t17_44_a_typed_path_keeps_its_backslashes(base):
    """The typed project path is taken literally. The folder does not exist, so the script
    stops at its existence check and writes nothing."""
    typed = '/no-such-aid-t17\\sub\\dir'
    rc, out = _run([BASH, LINK_SH.as_posix()], REPO, _env(base / 'home'), stdin=typed + '\n')
    assert rc != 0, out
    assert 'Target Project:   ' + typed in out, out
