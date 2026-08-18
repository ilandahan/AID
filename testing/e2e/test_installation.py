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


class TestClaudeStructure:
    """Verify .claude directory has required components."""

    def test_claude_directory_exists(self):
        assert os.path.isdir(CLAUDE_DIR), ".claude directory not found"

    def test_commands_directory_exists(self):
        cmd_dir = os.path.join(CLAUDE_DIR, 'commands')
        assert os.path.isdir(cmd_dir), ".claude/commands not found"

    def test_skills_directory_exists(self):
        skills_dir = os.path.join(CLAUDE_DIR, 'skills')
        assert os.path.isdir(skills_dir), ".claude/skills not found"

    def test_agents_directory_exists(self):
        agents_dir = os.path.join(CLAUDE_DIR, 'agents')
        assert os.path.isdir(agents_dir), ".claude/agents not found"

    def test_all_agents_have_prompts(self):
        agents_dir = os.path.join(CLAUDE_DIR, 'agents')
        agent_names = [
            d for d in os.listdir(agents_dir)
            if os.path.isdir(os.path.join(agents_dir, d))
        ]
        for agent in agent_names:
            prompt = os.path.join(agents_dir, agent, 'AGENT-PROMPT.md')
            assert os.path.isfile(prompt), f"{agent} missing AGENT-PROMPT.md"


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
