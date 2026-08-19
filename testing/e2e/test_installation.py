"""
AID Installation Verification Tests
Validates that the AID system is properly installed and configured.
"""
import json
import os
import subprocess
import pytest

# Anchor to the repo, not the caller's cwd: os.getcwd() made these tests pass or
# fail based on the directory pytest was launched from.
REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
AID_DIR = os.path.join(REPO_ROOT, '.aid')
CLAUDE_DIR = os.path.join(REPO_ROOT, '.claude')

# state.json / context.json are per-project runtime files (gitignored), created
# by link-project.sh or /aid-init. node_modules needs `npm install`. On a fresh
# clone none exist yet, so these checks have nothing to verify - skip with a
# reason instead of reporting a red suite for an un-set-up repo.
NOT_INITIALIZED = not os.path.isfile(os.path.join(AID_DIR, 'state.json'))
NO_NODE_MODULES = not os.path.isdir(os.path.join(REPO_ROOT, 'node_modules'))

needs_init = pytest.mark.skipif(
    NOT_INITIALIZED,
    reason="project not initialized - run ./link-project.sh or /aid-init first",
)
needs_npm = pytest.mark.skipif(
    NO_NODE_MODULES, reason="dependencies not installed - run `npm install` first"
)


class TestAIDInstallation:
    """Verify AID directory structure and core files."""

    def test_aid_directory_exists(self):
        assert os.path.isdir(AID_DIR), ".aid directory not found"

    @needs_init
    def test_state_file_exists(self):
        state_path = os.path.join(AID_DIR, 'state.json')
        assert os.path.isfile(state_path), ".aid/state.json not found"

    @needs_init
    def test_state_file_valid_json(self):
        state_path = os.path.join(AID_DIR, 'state.json')
        with open(state_path, 'r') as f:
            data = json.load(f)
        assert 'current_phase' in data
        assert 'phase_name' in data

    @needs_init
    def test_context_file_exists(self):
        context_path = os.path.join(AID_DIR, 'context.json')
        assert os.path.isfile(context_path), ".aid/context.json not found"

    def test_pipeline_config_exists(self):
        config_path = os.path.join(AID_DIR, 'pipeline', 'config.json')
        assert os.path.isfile(config_path), ".aid/pipeline/config.json not found"

    def test_pipeline_config_valid(self):
        config_path = os.path.join(AID_DIR, 'pipeline', 'config.json')
        with open(config_path, 'r') as f:
            data = json.load(f)
        assert 'max_iterations' in data
        assert 'test_commands' in data
        assert 'thresholds' in data


class TestPluginStructure:
    """
    Components live at the repository root, which is where Claude Code looks when this
    repo is loaded as a plugin (`claude plugin install aid@AID`).

    .claude/ still holds settings.json, and install.sh mirrors the component dirs into
    .claude/ as links so the repo also works as a plain project. Those mirrors are
    per-machine and gitignored, so they are NOT asserted here - a fresh clone has none.
    """

    def test_plugin_manifest_exists(self):
        p = os.path.join(REPO_ROOT, '.claude-plugin', 'plugin.json')
        assert os.path.isfile(p), '.claude-plugin/plugin.json missing - not a plugin'
        with open(p, encoding='utf-8') as f:
            manifest = json.load(f)
        for key in ('name', 'version', 'description'):
            assert manifest.get(key), f'plugin.json has no "{key}"'

    def test_marketplace_manifest_exists(self):
        """Without this the repo cannot be added with `claude plugin marketplace add`."""
        p = os.path.join(REPO_ROOT, '.claude-plugin', 'marketplace.json')
        assert os.path.isfile(p), '.claude-plugin/marketplace.json missing'
        with open(p, encoding='utf-8') as f:
            mkt = json.load(f)
        names = [e.get('name') for e in mkt.get('plugins', [])]
        assert 'aid' in names, f'marketplace does not list the aid plugin: {names}'

    def test_settings_json_stays_under_claude(self):
        """It is project config, and it is what link-project copies into a project."""
        assert os.path.isfile(os.path.join(CLAUDE_DIR, 'settings.json'))

    @pytest.mark.parametrize('component', ['commands', 'skills', 'agents', 'rules',
                                           'references', 'hooks'])
    def test_component_dir_is_at_repo_root(self, component):
        d = os.path.join(REPO_ROOT, component)
        assert os.path.isdir(d), f'{component}/ not found at the repository root'
        assert os.listdir(d), f'{component}/ is empty'

    def test_every_agent_definition_carries_its_prompt_inline(self):
        """
        AGENT-PROMPT.md files are gone: a plugin agent's cwd is the user's project, so an
        external asset path resolves against their code. The prompt is inlined instead,
        under an `## Agent prompt` heading.
        """
        agents_dir = os.path.join(REPO_ROOT, 'agents')
        thin = []
        for fn in sorted(os.listdir(agents_dir)):
            if not fn.endswith('.md'):
                continue
            body = open(os.path.join(agents_dir, fn), encoding='utf-8').read()
            if '## Agent prompt' not in body or len(body) < 1500:
                thin.append(f'{fn} ({len(body)} bytes)')
        assert not thin, f'agent definitions with no inlined prompt: {thin}'


@needs_npm
class TestNodeDependencies:
    """Verify Node.js dependencies are installed."""

    def test_node_modules_exists(self):
        node_modules = os.path.join(REPO_ROOT, 'node_modules')
        assert os.path.isdir(node_modules), "node_modules not found — run npm install"

    def test_cucumber_installed(self):
        result = subprocess.run(
            'npx cucumber-js --version', cwd=REPO_ROOT,
            capture_output=True, text=True, timeout=30, shell=True
        )
        assert result.returncode == 0 or 'not been tested' in result.stderr

    def test_typescript_installed(self):
        result = subprocess.run(
            'npx tsc --version', cwd=REPO_ROOT,
            capture_output=True, text=True, timeout=30, shell=True
        )
        assert result.returncode == 0
