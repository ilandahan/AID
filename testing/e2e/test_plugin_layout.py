"""
Plugin Layout Tests

WHY THIS TEST:
This repo has to satisfy two loaders from one copy of the files:

  - As a PLUGIN (`claude plugin install aid@AID`), Claude Code reads commands/, skills/
    and agents/ from the plugin root, and runs hooks declared in
    .claude-plugin/plugin.json via ${CLAUDE_PLUGIN_ROOT}.
  - As a PROJECT (opening Claude Code in this folder, or any of the projects already
    linked to .claude/<name>), Claude Code reads .claude/<name>.

install.sh bridges the two by mirroring the root dirs into .claude/ as symlinks or
junctions. That mirror is the load-bearing part of the arrangement and it cannot be
committed: core.symlinks defaults to false on Windows, so a committed symlink checks out
as a text file containing a path - a "directory" that is really a one-line file, which
git reports as clean.

So the mirror is created per-machine, and these tests EXECUTE the installer code that
creates it against a throwaway fixture. Nothing here runs the installer against this repo.
"""
import json
import os
import re
import subprocess

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPONENTS = ['commands', 'skills', 'agents', 'rules', 'references', 'hooks']
MANIFEST = os.path.join(REPO_ROOT, '.claude-plugin', 'plugin.json')


def _manifest():
    with open(MANIFEST, encoding='utf-8') as f:
        return json.load(f)


def _hook_commands(manifest):
    return [
        h.get('command', '')
        for event in manifest.get('hooks', {}).values()
        for group in event for h in group.get('hooks', [])
    ]


class TestPluginManifest:
    def test_declares_hooks(self):
        cmds = _hook_commands(_manifest())
        assert cmds, 'plugin.json declares no hooks - enforcement would not ship'

    def test_every_hook_script_exists(self):
        """A hook pointing at a missing script fails on every turn, in a file nobody edits."""
        missing = []
        for cmd in _hook_commands(_manifest()):
            for rel in re.findall(r'\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+)', cmd):
                if not os.path.isfile(os.path.join(REPO_ROOT, rel)):
                    missing.append(rel)
        assert not missing, f'plugin.json points at scripts that do not exist: {missing}'

    def test_plugin_root_is_always_quoted(self):
        """
        The most likely real-world install path contains a space
        (C:\\Users\\Someone\\My Projects\\...). An unquoted ${CLAUDE_PLUGIN_ROOT} splits
        into two arguments and the hook dies with 'No such file'.
        """
        unquoted = [c for c in _hook_commands(_manifest())
                    if '${CLAUDE_PLUGIN_ROOT}' in c
                    and not re.search(r'"[^"]*\$\{CLAUDE_PLUGIN_ROOT\}', c)]
        assert not unquoted, f'unquoted ${{CLAUDE_PLUGIN_ROOT}} breaks on paths with spaces: {unquoted}'

    def test_no_hardcoded_absolute_paths(self):
        for cmd in _hook_commands(_manifest()):
            assert not re.search(r'[A-Za-z]:[\\/]|/home/|/Users/', cmd), (
                f'hook command carries a machine-specific path: {cmd}'
            )

    def test_python_hooks_fall_back_from_python3_to_python(self):
        """Windows ships `python`, most Linux images ship only `python3`."""
        for cmd in _hook_commands(_manifest()):
            if '.py' not in cmd:
                continue
            assert 'python3' in cmd and re.search(r'\bpython\b', cmd), (
                f'python hook has no python3/python fallback: {cmd}'
            )


class TestComponentsAtRoot:
    @pytest.mark.parametrize('component', COMPONENTS)
    def test_component_present_and_non_empty(self, component):
        d = os.path.join(REPO_ROOT, component)
        assert os.path.isdir(d), f'{component}/ missing from the plugin root'
        assert os.listdir(d), f'{component}/ is empty'

    @pytest.mark.parametrize('component', COMPONENTS)
    def test_mirror_is_gitignored(self, component):
        """
        If a mirror were ever committed, a Windows clone would get a text file where a
        directory should be, and every skill/agent path under it would silently vanish.
        """
        r = subprocess.run(['git', 'check-ignore', '-q', '--no-index',
                            f'.claude/{component}'],
                           cwd=REPO_ROOT, capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, (
            f'.claude/{component} is not gitignored; the per-machine mirror could be '
            f'committed and would check out broken on Windows'
        )

    def test_settings_json_is_still_tracked(self):
        """It is project config and link-project copies it - it must not be ignored."""
        r = subprocess.run(['git', 'check-ignore', '-q', '--no-index',
                            '.claude/settings.json'],
                           cwd=REPO_ROOT, capture_output=True, text=True, timeout=60)
        assert r.returncode != 0, '.claude/settings.json must remain tracked'


class TestInstallerCreatesTheMirror:
    """Execute the installer's mirror step. Never against this repo."""

    @pytest.fixture(autouse=True)
    def _remove_junctions_after(self, tmp_path):
        """
        Tear down the links this test creates, before pytest tries to.

        WHY: pytest's tmp_path cleanup uses shutil.rmtree, which on Windows cannot
        traverse a junction (WinError 1920) - so the run ends in a teardown error and
        leaves garbage directories behind. Worse, a cleanup routine that DOES follow a
        junction deletes through it. Remove them with `rmdir`, which deletes the link and
        never the target.
        """
        yield
        claude = tmp_path / 'aid' / '.claude'
        if not claude.is_dir():
            return
        for c in COMPONENTS:
            link = claude / c
            if not os.path.lexists(str(link)):
                continue
            subprocess.run(['cmd', '/c', 'rmdir', str(link)],
                           capture_output=True, timeout=60)
            if os.path.lexists(str(link)):
                # A symlink (macOS/Linux, or Windows with Developer Mode) unlinks cleanly.
                try:
                    os.unlink(str(link))
                except OSError:
                    pass

    def _run_mirror(self, tmp_path):
        fixture = tmp_path / 'aid'
        fixture.mkdir()
        for c in COMPONENTS:
            d = fixture / c
            d.mkdir()
            (d / 'sentinel.md').write_text('mirror-me\n', encoding='utf-8')

        # Strip the `main "$@"` call so sourcing defines the functions without running
        # the whole 9-step installer (npm installs, MCP config, ...).
        src = open(os.path.join(REPO_ROOT, 'install.sh'), encoding='utf-8').read()
        lib = src.replace('main "$@"', ': # main disabled for test')
        (fixture / 'lib.sh').write_text(lib, encoding='utf-8', newline='\n')

        return subprocess.run(
            ['bash', '-c', 'source ./lib.sh && setup_claude_commands_and_skills'],
            cwd=str(fixture), capture_output=True, text=True, timeout=180,
            stdin=subprocess.DEVNULL,
        ), fixture

    def test_mirror_makes_components_readable_under_claude(self, tmp_path):
        result, fixture = self._run_mirror(tmp_path)
        assert result.returncode != 127, f'installer never ran: {result.stderr[:300]}'

        unreachable = []
        for c in COMPONENTS:
            # Read through the shell that made the link: a link created by WSL bash is
            # not resolvable by Windows Python (WinError 1920), so open() would report a
            # working mirror as broken.
            out = subprocess.run(['bash', '-c', f'cat ".claude/{c}/sentinel.md"'],
                                 cwd=str(fixture), capture_output=True, text=True,
                                 timeout=60)
            if out.stdout.strip() != 'mirror-me':
                unreachable.append(c)
        assert not unreachable, (
            f'.claude/ mirror does not expose {unreachable}; project mode and every '
            f'already-linked project would lose them.\ninstaller said:\n{result.stdout[-1500:]}'
        )

    def test_mirror_reflects_later_edits(self, tmp_path):
        """A copy would go stale; the whole point is one source of truth."""
        result, fixture = self._run_mirror(tmp_path)
        (fixture / 'skills' / 'sentinel.md').write_text('EDITED\n', encoding='utf-8')
        out = subprocess.run(['bash', '-c', 'cat ".claude/skills/sentinel.md"'],
                             cwd=str(fixture), capture_output=True, text=True, timeout=60)
        assert out.stdout.strip() == 'EDITED', (
            'the mirror is a copy, not a link - edits to the source will not reach '
            f'project mode.\ninstaller said:\n{result.stdout[-1200:]}'
        )

    def test_mirror_step_is_idempotent(self, tmp_path):
        """Re-running the installer must not destroy or duplicate anything."""
        _, fixture = self._run_mirror(tmp_path)
        src = open(os.path.join(REPO_ROOT, 'install.sh'), encoding='utf-8').read()
        (fixture / 'lib.sh').write_text(src.replace('main "$@"', ': # disabled'),
                                        encoding='utf-8', newline='\n')
        second = subprocess.run(
            ['bash', '-c', 'source ./lib.sh && setup_claude_commands_and_skills'],
            cwd=str(fixture), capture_output=True, text=True, timeout=180,
            stdin=subprocess.DEVNULL)
        out = subprocess.run(['bash', '-c', 'cat ".claude/skills/sentinel.md"'],
                             cwd=str(fixture), capture_output=True, text=True, timeout=60)
        assert out.stdout.strip() == 'mirror-me', (
            f'a second install broke the mirror:\n{second.stdout[-1200:]}'
        )
