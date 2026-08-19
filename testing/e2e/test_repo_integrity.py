"""
AID Repository Integrity Tests

WHY THIS TEST:
Each assertion here corresponds to a defect that shipped silently, where documentation
promised something the repo did not contain. The pattern in every case was the same: a
reference pointing at a path that did not exist, with nothing failing when it was wrong.

- `python -m memory_system` was documented four times with no such package present.
- `scripts/init-project.sh` was invoked by package.json and /start-project, was absent,
  AND was gitignored.
- install.sh ran 25 `cp -r skills/<name>` lines against a directory v2.1 deleted, each
  ending `|| true`, reporting "Skills installed (24 skills)" regardless.
- The autoresearch skill was invoked 26 times by pipeline-orchestrator and did not exist.
- learning-mode carried three files byte-identical to their own .extended.md siblings.
- settings.json pre-approved a bare "Bash", auto-approving any shell command.
"""
import json
import os
import subprocess

import pytest

REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
# Components live at the repository root so Claude Code can load this repo as a plugin.
SKILLS = os.path.join(REPO_ROOT, 'skills')


def _run(cmd, cwd, timeout=120):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)


class TestMemorySystem:
    """The documented CLI must actually run."""

    def test_package_is_present(self):
        pkg = os.path.join(REPO_ROOT, 'memory-system', 'memory_system')
        assert os.path.isdir(pkg), 'memory-system/memory_system package is missing'
        assert os.path.isfile(os.path.join(pkg, '__main__.py')), (
            'no __main__.py, so `python -m memory_system` cannot work'
        )

    @pytest.mark.parametrize('doc', ['AGENT.md', 'COMMANDS.md', 'IMPROVEMENT-FLOW.md',
                                     'MEMORY.md'])
    def test_referenced_docs_exist(self, doc):
        """/aid-start, /aid-init, /aid-improve and /aid-memory each cite one of these."""
        path = os.path.join(REPO_ROOT, 'memory-system', 'docs', doc)
        assert os.path.isfile(path), f'memory-system/docs/{doc} is cited by a command'

    def test_cli_status_runs(self):
        """Executes the real CLI. Documentation that cannot run is not documentation."""
        result = _run(['python', '-m', 'memory_system', '--status'],
                      cwd=os.path.join(REPO_ROOT, 'memory-system'))
        assert result.returncode == 0, (
            f'`python -m memory_system --status` failed:\n{result.stderr[:600]}'
        )
        assert 'Status' in result.stdout, f'unexpected output: {result.stdout[:200]}'


class TestInitProjectScript:
    def test_exists_and_is_valid_shell(self):
        path = os.path.join(REPO_ROOT, 'scripts', 'init-project.sh')
        assert os.path.isfile(path), (
            'scripts/init-project.sh is missing, but package.json "new-project" and '
            '/start-project both invoke it'
        )
        r = _run(['bash', '-n', './init-project.sh'],
                 cwd=os.path.join(REPO_ROOT, 'scripts'))
        assert r.returncode == 0, f'syntax error: {r.stderr}'

    def test_is_not_gitignored(self):
        """It was previously excluded by an unanchored `scripts/` rule."""
        r = _run(['git', 'check-ignore', '-q', 'scripts/init-project.sh'], cwd=REPO_ROOT)
        # check-ignore exits 0 when the path IS ignored.
        assert r.returncode != 0, (
            'scripts/init-project.sh is gitignored, so it will not ship'
        )

    def test_package_json_entry_resolves(self):
        with open(os.path.join(REPO_ROOT, 'package.json'), encoding='utf-8') as f:
            scripts = json.load(f).get('scripts', {})
        for name, cmd in scripts.items():
            for token in cmd.split():
                if token.startswith('./') and (token.endswith('.sh') or
                                               token.endswith('.bat')):
                    assert os.path.isfile(os.path.join(REPO_ROOT, token[2:])), (
                        f'package.json "{name}" runs {token}, which does not exist'
                    )


class TestAutoresearchSkill:
    """Invoked by pipeline-orchestrator for AR_DESIGN / AR_FUNCTION / AR_ACCEPTANCE."""

    @pytest.mark.parametrize('rel', [
        'SKILL.md', 'SKILL.extended.md',
        'program.ar-design.md', 'program.ar-function.md', 'program.ar-acceptance.md',
        'verify-run.sh', 'bin/check-harness-immutable.sh',
    ])
    def test_asset_present(self, rel):
        assert os.path.isfile(os.path.join(SKILLS, 'autoresearch', rel)), \
            f'autoresearch/{rel} is missing'

    @pytest.mark.parametrize('rel', ['verify-run.sh', 'bin/check-harness-immutable.sh'])
    def test_shell_assets_are_valid(self, rel):
        r = _run(['bash', '-n', f'./{rel}'], cwd=os.path.join(SKILLS, 'autoresearch'))
        assert r.returncode == 0, f'{rel} syntax error: {r.stderr}'

    @pytest.mark.parametrize('name', ['phase-4a-code-design.yaml',
                                      'phase-4b-code-function.yaml'])
    def test_criteria_parse(self, name):
        yaml = pytest.importorskip('yaml')
        path = os.path.join(SKILLS, 'reflection', 'criteria', name)
        assert os.path.isfile(path), f'{name} is missing'
        data = yaml.safe_load(open(path, encoding='utf-8'))
        for key in ('phase', 'name', 'criteria', 'threshold'):
            assert key in data, f'{name} has no "{key}"'
        assert data['criteria'], f'{name} defines no criteria'

    def test_pipeline_config_carries_autoresearch_block(self):
        with open(os.path.join(REPO_ROOT, '.aid', 'pipeline', 'config.json'),
                  encoding='utf-8') as f:
            cfg = json.load(f)
        ar = cfg.get('autoresearch')
        assert ar, '.aid/pipeline/config.json has no autoresearch block'
        for key in ('kpi_target', 'ar_design', 'ar_function', 'ar_acceptance'):
            assert key in ar, f'autoresearch config missing "{key}"'


class TestSkillStructure:
    def test_every_skill_has_a_skill_md(self):
        missing = [d for d in sorted(os.listdir(SKILLS))
                   if os.path.isdir(os.path.join(SKILLS, d))
                   and not os.path.isfile(os.path.join(SKILLS, d, 'SKILL.md'))]
        assert not missing, f'skills with no SKILL.md: {missing}'

    def test_no_file_duplicates_its_own_extended_sibling(self):
        """learning-mode shipped three references/X.md byte-identical to X.extended.md."""
        dupes = []
        for root, dirs, files in os.walk(SKILLS):
            for fn in files:
                if not fn.endswith('.extended.md'):
                    continue
                ext = os.path.join(root, fn)
                base = fn[: -len('.extended.md')] + '.md'
                for other_root, _, other_files in os.walk(SKILLS):
                    if base in other_files:
                        cand = os.path.join(other_root, base)
                        if os.path.getsize(cand) != os.path.getsize(ext):
                            continue
                        with open(cand, 'rb') as a, open(ext, 'rb') as b:
                            if a.read() == b.read():
                                dupes.append(
                                    f'{os.path.relpath(cand, REPO_ROOT)} == '
                                    f'{os.path.relpath(ext, REPO_ROOT)}')
        assert not dupes, f'byte-identical duplicates: {dupes}'


class TestInstallersVerifyRatherThanSilentlyCopy:
    """
    The original defect: install.sh ran 25 `cp -r skills/<name> .claude/skills/` lines
    against a directory v2.1 had deleted, each ending `|| true`, and then reported
    "Skills installed (24 skills)" from a hardcoded number. Every copy did nothing and
    nothing failed.

    A root skills/ now exists again, deliberately - it is where a plugin's components
    must live. So the invariant worth pinning is not "no root skills/" (a shape) but
    "the installer's component step can actually fail and its counts come from disk"
    (the behaviour that was missing).
    """

    def _code_lines(self, installer):
        with open(os.path.join(REPO_ROOT, installer), encoding='utf-8',
                  errors='replace') as f:
            lines = f.read().splitlines()
        # Comments are excluded: both installers carry a comment EXPLAINING the old
        # broken command, and matching that would fail on the fix's own documentation.
        return [ln for ln in lines
                if not ln.lstrip().startswith('#')
                and not ln.lstrip().upper().startswith('REM ')]

    @pytest.mark.parametrize('installer', ['install.sh', 'install.bat'])
    def test_no_failure_suppressed_component_copies(self, installer):
        """`|| true` on a copy is how a no-op passes for a successful install."""
        offenders = [
            ln.strip() for ln in self._code_lines(installer)
            if ('cp -r' in ln or 'xcopy' in ln)
            and any(c in ln for c in ('skills', 'agents', 'commands', 'rules',
                                      'references', 'hooks'))
            and ('|| true' in ln or '2>/dev/null' in ln or '>nul 2>&1' in ln)
        ]
        assert not offenders, (
            f'{installer} copies components while suppressing failure: {offenders}'
        )

    def test_install_sh_counts_come_from_the_filesystem(self):
        """A hardcoded count cannot report a broken install."""
        text = '\n'.join(self._code_lines('install.sh'))
        assert 'skill_count=$(find skills' in text, (
            'install.sh must count skills by looking at skills/, not by asserting a number'
        )
        assert 'agent_count=$(find agents' in text, (
            'install.sh must count agents by looking at agents/'
        )

    def test_install_sh_reports_missing_components(self):
        text = '\n'.join(self._code_lines('install.sh'))
        assert 'is MISSING' in text, (
            'install.sh has no failure path for a missing component directory'
        )

    @pytest.mark.parametrize('component', ['commands', 'skills', 'agents', 'rules',
                                           'references', 'hooks'])
    def test_component_exists_where_the_installer_looks(self, component):
        assert os.path.isdir(os.path.join(REPO_ROOT, component)), (
            f'{component}/ missing from the repository root, where both the installer '
            f'and the plugin loader expect it'
        )


class TestPermissionDefaults:
    def test_bare_bash_is_not_pre_approved(self):
        with open(os.path.join(REPO_ROOT, '.claude', 'settings.json'),
                  encoding='utf-8') as f:
            allow = json.load(f).get('permissions', {}).get('allow', [])
        assert 'Bash' not in allow, (
            'a bare "Bash" entry auto-approves ANY shell command for every adopter; '
            'use scoped entries like "Bash(npm test:*)" instead'
        )
