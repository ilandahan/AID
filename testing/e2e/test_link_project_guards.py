"""
AID Link-Project Safety Tests

WHY THIS TEST:
- PROBLEM: link-project deletes the target's .claude/<dir> before recreating it.
  When the target resolved to the AID install itself, target == source, so AID
  deleted its own skills/agents/commands/references/rules. On Windows the
  `xcopy /I` fallback then recreated the folders EMPTY, so a total content loss
  looked like a successful link.
- COST OF FAILURE: irreversible loss of the framework's content, silently.
- SUCCESS: every destructive path refuses to run, the content survives, and
  linking a legitimate project still works.

Every test EXECUTES the real script against a throwaway fixture tree. Nothing
here points the script at this repo: if a guard regresses, the fixture dies
instead of your skills.
"""
import json
import os
import re
import shlex
import shutil
import subprocess

import pytest

# testing/e2e/<this file> -> repo root is three levels up.
REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
LINK_SCRIPT = os.path.join(REPO_ROOT, 'link-project.sh')

# The directories link-project removes before recreating. 'hooks' is included because
# the settings.json that link-project copies declares Stop/PostToolUse hooks by the
# path .claude/hooks/* - if hooks are not installed, every linked project gets a
# settings file pointing at scripts that do not exist.
LINKED_DIRS = ['commands', 'skills', 'agents', 'references', 'rules', 'hooks']

SENTINEL = 'do-not-delete-me\n'


def _posix_bash():
    """T16 (owner 2026-11-19): link-project now needs node (it registers the AID hooks,
    I-9), and the System32 bash.exe is WSL, which has no node here and cannot run the
    Windows one on these paths. On Windows use Git Bash, with native symlinks so `ln -s`
    links instead of copying (MSYS copies by default)."""
    if os.name == 'nt':
        git = shutil.which('git')
        here = os.path.realpath(git) if git else None
        for up in (2, 3):
            if not here:
                break
            root = here
            for _ in range(up):
                root = os.path.dirname(root)
            cand = os.path.join(root, 'bin', 'bash.exe')
            if os.path.isfile(cand):
                return cand
    return 'bash'


BASH = _posix_bash()
BASH_ENV = dict(os.environ, MSYS='winsymlinks:nativestrict') if os.name == 'nt' else None


def _make_aid_fixture(root):
    """Build a minimal but realistic AID install with detectable content.

    WHY a fixture instead of the real repo: the failure mode under test is
    deletion. Aiming a possibly-broken guard at the real skills/ would
    reproduce the original data loss every time the guard regressed.

    Component dirs sit at the AID ROOT (commands/, skills/, ...) because that is
    what a plugin layout requires and therefore what link-project reads from. The
    link TARGET is still the project's .claude/<name>.
    """
    os.makedirs(os.path.join(root, '.claude'), exist_ok=True)
    for name in LINKED_DIRS:
        d = os.path.join(root, name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, 'sentinel.md'), 'w') as f:
            f.write(SENTINEL)

    with open(os.path.join(root, 'CLAUDE.md'), 'w') as f:
        f.write('# fixture\n')
    with open(os.path.join(root, '.claude', 'settings.json'), 'w') as f:
        f.write('{}\n')
    for template in ('.mcp.json.mac', '.mcp.json.windows'):
        shutil.copy(os.path.join(REPO_ROOT, template), os.path.join(root, template))
    # T16 (owner 2026-11-19): link-project now registers the hooks through
    # scripts/link-settings.mjs (reads .claude-plugin/plugin.json, I-9) and creates the state
    # through hooks/aid_session.py init (I-10), so the fixture carries those real files.
    for rel in (os.path.join('.claude-plugin', 'plugin.json'),
                os.path.join('scripts', 'link-settings.mjs'),
                # T17 (owner 2026-11-20): both linkers add the I-26 .gitignore lines through it.
                os.path.join('scripts', 'ensure-gitignore.mjs'),
                os.path.join('references', 'role-phase-terminology.json')):
        os.makedirs(os.path.dirname(os.path.join(root, rel)), exist_ok=True)
        shutil.copy(os.path.join(REPO_ROOT, rel), os.path.join(root, rel))
    for name in os.listdir(os.path.join(REPO_ROOT, 'hooks')):
        if name.endswith(('.py', '.mjs')):
            shutil.copy(os.path.join(REPO_ROOT, 'hooks', name), os.path.join(root, 'hooks', name))
    shutil.copy(LINK_SCRIPT, os.path.join(root, 'link-project.sh'))
    shutil.copy(os.path.join(REPO_ROOT, 'link-project.bat'),
                os.path.join(root, 'link-project.bat'))
    return root


def _bash_abs(cwd, rel):
    """Ask the shell itself for the absolute form of `rel`.

    WHY not build the path in Python: `bash` on Windows may be git-bash (/c/...)
    or WSL (/mnt/c/...), and a native C:\\ path loses its backslashes in argv.
    Hardcoding either prefix makes the test pass or fail based on which bash is
    first on PATH, not on whether the guard works.
    """
    out = subprocess.run(
        [BASH, '-c', f'cd "{rel}" && pwd'],
        capture_output=True, text=True, cwd=cwd, timeout=60, env=BASH_ENV,
    )
    assert out.returncode == 0, f"could not resolve {rel}: {out.stderr}"
    return out.stdout.strip()


def _run_link(aid_root, target_rel, home=None, timeout=120):
    """Run the real link-project.sh with a target RELATIVE to the AID root.

    Relative targets keep this shell-agnostic and exercise a realistic spelling
    ('.' is exactly how someone nukes their own install). stdin is closed so a
    prompt cannot hang the suite.

    WHY `home` is assigned inside the shell rather than via subprocess env:
    under WSL, Windows environment variables are not inherited unless listed in
    WSLENV, so an injected HOME silently never arrives and the home guard looks
    broken when it is fine.
    """
    prefix = f'HOME={shlex.quote(home)} ' if home else ''
    command = f'{prefix}./link-project.sh {shlex.quote(target_rel)} --force'
    result = subprocess.run(
        [BASH, '-c', command],
        capture_output=True, text=True, timeout=timeout, env=BASH_ENV,
        stdin=subprocess.DEVNULL, cwd=aid_root,
    )
    # 127 == bash never found the script. Fail loudly instead of letting it look
    # like a refusal.
    assert result.returncode != 127, (
        f"link-project.sh was not executed at all: {result.stderr}"
    )
    return result


def _read_via_bash(cwd, rel_path):
    """Read a file through the shell that created the link.

    WHY not open() it from Python: a symlink made by WSL bash is not resolvable
    by Windows Python (WinError 1920). Reading it back in the same shell tests
    whether the link actually works for its user, instead of testing which
    Python happens to run the suite.
    """
    out = subprocess.run(
        [BASH, '-c', f'cat {shlex.quote(rel_path)}'],
        capture_output=True, text=True, cwd=cwd, timeout=60, env=BASH_ENV,
    )
    return out.stdout


def _sentinels_intact(root):
    """True only if every linked dir still holds its sentinel content."""
    for name in LINKED_DIRS:
        p = os.path.join(root, name, 'sentinel.md')
        if not os.path.isfile(p):
            return False
        with open(p) as f:
            if f.read() != SENTINEL:
                return False
    return True


class TestRefusesDestructiveTargets:
    """Execute the attack: point link-project at things it must not touch."""

    def test_refuses_to_link_aid_to_itself(self, tmp_path):
        aid = _make_aid_fixture(str(tmp_path / 'aid'))

        # '.' is exactly how someone points the linker at its own install.
        result = _run_link(aid, '.')

        assert result.returncode != 0, (
            "link-project accepted the AID install as its own target; "
            f"stdout:\n{result.stdout}"
        )
        # Proves the refusal came from the guard, not from a failure to launch.
        assert '[ERROR]' in result.stdout, (
            f"expected an explicit refusal on stdout, got:\n{result.stdout}"
        )
        assert _sentinels_intact(aid), (
            "AID deleted its own .claude content when targeting itself — "
            "this is the original data-loss bug"
        )

    def test_refuses_to_link_into_home(self, tmp_path):
        aid = _make_aid_fixture(str(tmp_path / 'aid'))
        fake_home = tmp_path / 'home'
        (fake_home / '.claude' / 'skills').mkdir(parents=True)
        precious = fake_home / '.claude' / 'skills' / 'user-global-skill.md'
        precious.write_text(SENTINEL)

        result = _run_link(aid, '../home', home=_bash_abs(aid, '../home'))

        assert result.returncode != 0, (
            f"link-project accepted the home directory; stdout:\n{result.stdout}"
        )
        assert '[ERROR]' in result.stdout, (
            f"expected an explicit refusal on stdout, got:\n{result.stdout}"
        )
        assert precious.read_text() == SENTINEL, (
            "link-project destroyed the user's global ~/.claude/skills content"
        )

    def test_missing_source_does_not_delete_target_content(self, tmp_path):
        """The delete must never run when there is nothing to put back."""
        aid = _make_aid_fixture(str(tmp_path / 'aid'))
        shutil.rmtree(os.path.join(aid, 'skills'))

        target = tmp_path / 'project'
        (target / '.claude' / 'skills').mkdir(parents=True)
        existing = target / '.claude' / 'skills' / 'project-skill.md'
        existing.write_text(SENTINEL)

        _run_link(aid, '../project')

        assert existing.is_file() and existing.read_text() == SENTINEL, (
            "link-project deleted the project's skills while AID had no skills "
            "to replace them with"
        )


@pytest.mark.skipif(os.name != 'nt', reason='link-project.bat only runs on Windows')
class TestWindowsLinkerRefusesSelfTarget:
    """
    WHY A SEPARATE WINDOWS TEST:
    The .bat is the script Windows users actually run, and it carries the same
    bug in two places (the junction branch and the xcopy fallback). Verified by
    reproduction: with the guard removed, this fixture loses all five
    directories and the script still prints "Project Linked Successfully" -
    `xcopy /I` recreates each folder EMPTY, so total content loss reports as
    success. The .sh tests cannot cover that path.
    """

    def test_bat_refuses_to_link_aid_to_itself(self, tmp_path):
        aid = _make_aid_fixture(str(tmp_path / 'aid'))

        result = subprocess.run(
            [os.path.join(aid, 'link-project.bat'), '.', '--force'],
            capture_output=True, text=True, timeout=120,
            stdin=subprocess.DEVNULL, cwd=aid,
        )

        assert result.returncode != 0, (
            f"link-project.bat accepted its own install as target;"
            f" stdout:\n{result.stdout}"
        )
        assert '[ERROR]' in result.stdout, (
            f"expected an explicit refusal on stdout, got:\n{result.stdout}"
        )
        assert _sentinels_intact(aid), (
            "link-project.bat deleted AID's own .claude content - the xcopy "
            "fallback leaves the folders empty and still reports success"
        )

    def test_bat_links_a_real_project(self, tmp_path):
        """Regression: the Windows guard must not break Windows linking."""
        aid = _make_aid_fixture(str(tmp_path / 'aid'))
        target = tmp_path / 'project'
        target.mkdir()

        result = subprocess.run(
            [os.path.join(aid, 'link-project.bat'), str(target), '--force'],
            capture_output=True, text=True, timeout=120,
            stdin=subprocess.DEVNULL, cwd=aid,
        )

        assert result.returncode == 0, (
            f"linking a normal project failed on Windows:\n{result.stdout}"
        )
        # Junction or copy - either way the content must be reachable, which is
        # what "one source of truth" means to the person using it.
        for name in LINKED_DIRS:
            sentinel = target / '.claude' / name / 'sentinel.md'
            assert sentinel.is_file(), f".claude/{name} not usable at target"
            assert sentinel.read_text() == SENTINEL

    def test_bat_gitignores_mcp_json_once(self, tmp_path):
        """Windows linker: same .gitignore contract as link-project.sh."""
        aid = _make_aid_fixture(str(tmp_path / 'aid'))
        target = tmp_path / 'project'
        target.mkdir()
        (target / '.gitignore').write_bytes(b'node_modules')  # no trailing newline

        for _ in range(2):
            result = subprocess.run(
                [os.path.join(aid, 'link-project.bat'), str(target), '--force'],
                capture_output=True, text=True, timeout=120,
                stdin=subprocess.DEVNULL, cwd=aid,
            )
            assert result.returncode == 0, result.stdout

        lines = [l.strip() for l in (target / '.gitignore').read_text().splitlines()]
        # T17 (owner 2026-11-20): I-26 also adds .aid/audit/, and no blank line is inserted.
        assert lines == ['node_modules', '.mcp.json', '.aid/audit/'], lines

    def test_bat_propagates_aid_updates_to_linked_project(self, tmp_path):
        """
        WHY THIS TEST:
        - PROBLEM: the point of linking is ONE source of truth - update AID and
          every linked project follows. A junction delivers that; a silent copy
          looks identical on day one and then quietly goes stale forever.
        - SUCCESS: an edit and a brand-new skill both appear in the project with
          no re-link.
        """
        aid = _make_aid_fixture(str(tmp_path / 'aid'))
        target = tmp_path / 'project'
        target.mkdir()

        subprocess.run(
            [os.path.join(aid, 'link-project.bat'), str(target), '--force'],
            capture_output=True, text=True, timeout=120,
            stdin=subprocess.DEVNULL, cwd=aid,
        )

        # Edit an existing file in AID.
        source_file = os.path.join(aid, 'skills', 'sentinel.md')
        with open(source_file, 'w') as f:
            f.write('UPDATED-IN-AID\n')
        assert (target / '.claude' / 'skills' / 'sentinel.md').read_text() == \
            'UPDATED-IN-AID\n', (
                "project did not see the AID edit - it was copied, not linked, "
                "so linked projects will silently go stale"
            )

        # Add a whole new skill in AID.
        os.makedirs(os.path.join(aid, 'skills', 'brand-new-skill'))
        with open(os.path.join(aid, 'skills', 'brand-new-skill',
                               'SKILL.md'), 'w') as f:
            f.write('new\n')
        assert (target / '.claude' / 'skills' / 'brand-new-skill' /
                'SKILL.md').is_file(), (
            "project did not pick up a new skill added to AID"
        )


class TestLegitimateLinkStillWorks:
    """Regression: the guards must not break the feature they wrap."""

    def test_links_a_real_project(self, tmp_path):
        aid = _make_aid_fixture(str(tmp_path / 'aid'))
        target = tmp_path / 'project'
        target.mkdir()

        result = _run_link(aid, '../project')

        assert result.returncode == 0, (
            f"linking a normal project failed:\n{result.stdout}\n{result.stderr}"
        )
        # Resolve content THROUGH the target path: passes for a symlink, a
        # junction or a copy, which differ by platform.
        for name in LINKED_DIRS:
            content = _read_via_bash(
                aid, f'../project/.claude/{name}/sentinel.md')
            assert content == SENTINEL, (
                f".claude/{name} is not readable through the linked target"
            )

    def test_propagates_aid_updates_to_linked_project(self, tmp_path):
        """Same one-source-of-truth promise, on the macOS/Linux path."""
        aid = _make_aid_fixture(str(tmp_path / 'aid'))
        target = tmp_path / 'project'
        target.mkdir()

        _run_link(aid, '../project')

        with open(os.path.join(aid, 'skills', 'sentinel.md'), 'w') as f:
            f.write('UPDATED-IN-AID\n')

        seen = _read_via_bash(aid, '../project/.claude/skills/sentinel.md')
        assert seen == 'UPDATED-IN-AID\n', (
            "project did not see the AID edit - it was copied, not symlinked, "
            f"so linked projects will silently go stale (saw: {seen!r})"
        )

    def test_linked_project_can_reach_every_hook_settings_declares(self):
        """
        WHY THIS TEST:
        - PROBLEM: link-project copies .claude/settings.json into the target, and that
          file declares Stop and PostToolUse hooks by the path .claude/hooks/*. hooks/
          was not in the linked directory list, so every linked project received a
          settings file pointing at scripts that were not there - a hook failure on
          every turn end, in a file the user never edited.
        - SUCCESS: each hook path settings.json names is present in the AID install, so
          linking it makes the path resolve in the target too.
        """
        with open(os.path.join(REPO_ROOT, '.claude', 'settings.json'),
                  encoding='utf-8') as f:
            settings = json.load(f)

        commands = [
            h.get('command', '')
            for event in settings.get('hooks', {}).values()
            for group in event for h in group.get('hooks', [])
        ]
        referenced = set(re.findall(r'\.claude/hooks/[\w.-]+', ' '.join(commands)))
        assert referenced, 'settings.json declares no hooks - expected at least one'

        for ref in sorted(referenced):
            component = ref.split('/')[1]          # e.g. 'hooks'
            leaf = ref.split('/', 2)[2]            # e.g. 'dev-pipeline-gate.sh'

            # settings.json names .claude/hooks/* because it is COPIED into the target,
            # where link-project makes .claude/hooks a link to AID's hooks/. So the file
            # that has to exist in AID is hooks/<leaf> at the repository root. AID's own
            # .claude/hooks mirror is created by install.sh and gitignored, so asserting
            # on it would fail on a fresh clone while the link contract is perfectly fine.
            source = os.path.join(REPO_ROOT, component, leaf)
            assert os.path.isfile(source), (
                f'settings.json points at {ref}; linking makes that resolve to '
                f'{component}/{leaf} in AID, which does not exist'
            )
            # The directory that must therefore be linked into target projects.
            assert component in LINKED_DIRS, (
                f'{ref} lives in a directory link-project does not install; '
                f'linked projects would get a settings file pointing at nothing'
            )

    def test_creates_project_state(self, tmp_path):
        aid = _make_aid_fixture(str(tmp_path / 'aid'))
        target = tmp_path / 'project'
        target.mkdir()

        result = _run_link(aid, '../project')

        # T16 (owner 2026-11-19): written by aid_session.py init, not by the script.
        assert (target / '.aid' / 'state.json').is_file(), result.stdout + result.stderr
        assert 'state.json created by aid_session.py init' in result.stdout, result.stdout
        assert (target / '.mcp.json').is_file()

    def test_gitignores_mcp_json_once(self, tmp_path):
        """The copied .mcp.json is per-user config: linking must keep it out of the
        project's git history, without duplicating the line on re-link and without
        gluing it onto a last line that has no trailing newline."""
        aid = _make_aid_fixture(str(tmp_path / 'aid'))
        target = tmp_path / 'project'
        target.mkdir()
        (target / '.gitignore').write_bytes(b'node_modules')  # no trailing newline

        _run_link(aid, '../project')
        _run_link(aid, '../project')

        lines = (target / '.gitignore').read_text().splitlines()
        # T17 (owner 2026-11-20): I-26 also adds .aid/audit/.
        assert lines == ['node_modules', '.mcp.json', '.aid/audit/'], lines


class TestNoRealSecretsInTrackedTemplates:
    """
    WHY THIS TEST:
    - PROBLEM: .mcp.json is ignored but .mcp.json.windows/.mac are TRACKED, one
      character apart. A real Atlassian token was once filled into the tracked
      template and published.
    - SUCCESS: the shipped templates carry placeholders only.
    """

    # Provider-issued credential prefixes, matched at real token lengths so
    # placeholders like YOUR_ATLASSIAN_API_TOKEN cannot trip them.
    SECRET_PATTERNS = [
        r'ATATT[A-Za-z0-9_=\-]{20,}',
        r'sk-ant-[A-Za-z0-9_\-]{20,}',
        r'gh[p]_[A-Za-z0-9]{30,}',  # [p] keeps the literal prefix out of tracked files
        r'github_pat_[A-Za-z0-9_]{50,}',
        r'figd_[A-Za-z0-9_\-]{20,}',
        r'AIza[A-Za-z0-9_\-]{30,}',
        r'xox[baprs]-[A-Za-z0-9\-]{10,}',
        r'AKIA[0-9A-Z]{16}',
    ]

    @pytest.mark.parametrize('template', ['.mcp.json.windows', '.mcp.json.mac',
                                          '.mcp.json.example'])
    def test_template_has_no_real_credentials(self, template):
        path = os.path.join(REPO_ROOT, template)
        with open(path) as f:
            content = f.read()

        for pattern in self.SECRET_PATTERNS:
            match = re.search(pattern, content)
            assert match is None, (
                f"{template} contains what looks like a real credential "
                f"({match.group(0)[:4]}****). Use ${{VAR}} env expansion and load the "
                f"value from the OS keystore - never put it in a tracked template."
            )

    @pytest.mark.parametrize('template', ['.mcp.json.windows', '.mcp.json.mac',
                                          '.mcp.json.example'])
    def test_template_credentials_come_from_environment(self, template):
        """Every env value and header must be a ${VAR} reference, so the file a
        user copies never invites them to paste a token into it."""
        with open(os.path.join(REPO_ROOT, template)) as f:
            servers = json.load(f)['mcpServers']
        for name, server in servers.items():
            for field in ('env', 'headers'):
                for key, value in server.get(field, {}).items():
                    # Only a ${VAR} reference (optionally behind the auth scheme
                    # word) may remain: any literal left over is a pasted value.
                    literal = re.sub(r'\$\{[A-Z0-9_]+(:-)?\}', '', value)
                    literal = re.sub(r'^Bearer ', '', literal)
                    assert '${' in value and literal == '', (
                        f"{template}: {name}.{field}.{key} is a literal; "
                        f"use ${{{key}}} env expansion"
                    )

    @pytest.mark.parametrize('template', ['.mcp.json.windows', '.mcp.json.mac',
                                          '.mcp.json.example'])
    def test_template_npx_packages_are_pinned(self, template):
        """npx -y fetches whatever is newest and runs it with the user's tokens;
        every package must carry an exact x.y.z version."""
        with open(os.path.join(REPO_ROOT, template)) as f:
            servers = json.load(f)['mcpServers']
        for name, server in servers.items():
            args = server.get('args', [])
            if 'npx' not in [server.get('command')] + args:
                continue
            pkg = args[args.index('-y') + 1]
            assert re.fullmatch(r'(@[\w.-]+/)?[\w.-]+@\d+\.\d+\.\d+', pkg), (
                f"{template}: {name} runs unpinned package {pkg!r}"
            )
