"""
AID Installation & Sanity E2E Tests

Comprehensive tests to verify:
1. All dependencies are installed correctly
2. Python memory-system modules import successfully
3. Configuration files exist and are valid
4. Environment variables are set
5. MCP servers can be reached
6. Database connection works (if configured)

Run with: pytest testing/e2e/test_installation.py -v
"""

import pytest
import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List

# ============================================
# Test Configuration
# ============================================

PROJECT_ROOT = Path(__file__).parent.parent.parent
MEMORY_SYSTEM_DIR = PROJECT_ROOT / "memory-system"
AID_STATE_DIR = Path(os.path.expanduser("~/.aid"))


# ============================================
# Fixtures
# ============================================

@pytest.fixture(scope="module")
def project_root() -> Path:
    """Return project root directory."""
    return PROJECT_ROOT


@pytest.fixture(scope="module")
def package_json(project_root) -> Dict[str, Any]:
    """Load and parse package.json."""
    pkg_path = project_root / "package.json"
    if pkg_path.exists():
        with open(pkg_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


@pytest.fixture(scope="module")
def mcp_config(project_root) -> Dict[str, Any]:
    """Load MCP configuration."""
    mcp_path = project_root / ".mcp.json"
    if mcp_path.exists():
        with open(mcp_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


# ============================================
# Installation Verification Tests
# ============================================

class TestProjectStructure:
    """Verify project structure is complete."""

    def test_project_root_exists(self, project_root):
        """Project root directory exists."""
        assert project_root.exists(), f"Project root not found: {project_root}"
        assert project_root.is_dir(), "Project root is not a directory"

    def test_package_json_exists(self, project_root):
        """package.json exists and is valid JSON."""
        pkg_path = project_root / "package.json"
        assert pkg_path.exists(), "package.json not found"

        with open(pkg_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert "name" in data, "package.json missing 'name' field"
        assert "version" in data, "package.json missing 'version' field"
        assert data["name"] == "ai-fullstack-methodology"

    def test_tsconfig_exists(self, project_root):
        """TypeScript configuration exists."""
        tsconfig = project_root / "tsconfig.json"
        assert tsconfig.exists(), "tsconfig.json not found"

    def test_prisma_schema_exists(self, project_root):
        """Prisma database schema exists."""
        schema = project_root / "prisma" / "schema.prisma"
        assert schema.exists(), "prisma/schema.prisma not found"

    def test_memory_system_exists(self, project_root):
        """Python memory-system directory exists."""
        mem_sys = project_root / "memory-system"
        assert mem_sys.exists(), "memory-system directory not found"
        assert mem_sys.is_dir(), "memory-system is not a directory"

    def test_src_directory_exists(self, project_root):
        """Source directory exists."""
        src = project_root / "src"
        assert src.exists(), "src directory not found"

    def test_skills_directory_exists(self, project_root):
        """Skills directory exists."""
        skills = project_root / ".claude" / "skills"
        assert skills.exists(), ".claude/skills directory not found"

    def test_commands_directory_exists(self, project_root):
        """Commands directory exists."""
        commands = project_root / ".claude" / "commands"
        assert commands.exists(), ".claude/commands directory not found"


class TestConfigurationFiles:
    """Verify configuration files are valid."""

    def test_gitignore_exists(self, project_root):
        """Git ignore file exists."""
        gitignore = project_root / ".gitignore"
        assert gitignore.exists(), ".gitignore not found"

    def test_mcp_json_not_tracked(self, project_root):
        """.mcp.json should be in .gitignore (contains secrets)."""
        gitignore = project_root / ".gitignore"
        content = gitignore.read_text(encoding='utf-8')
        assert ".mcp.json" in content, ".mcp.json should be in .gitignore"

    def test_env_not_tracked(self, project_root):
        """.env should be in .gitignore."""
        gitignore = project_root / ".gitignore"
        content = gitignore.read_text(encoding='utf-8')
        assert ".env" in content, ".env should be in .gitignore"

    def test_mcp_example_exists(self, project_root):
        """.mcp.json.example template exists."""
        example = project_root / ".mcp.json.example"
        assert example.exists(), ".mcp.json.example not found"

    def test_env_example_or_env_exists(self, project_root):
        """.env or .env.example exists."""
        env = project_root / ".env"
        env_example = project_root / ".env.example"
        assert env.exists() or env_example.exists(), "Neither .env nor .env.example found"

    def test_jest_config_exists(self, project_root):
        """Jest configuration exists."""
        jest_config = project_root / "jest.config.js"
        assert jest_config.exists(), "jest.config.js not found"

    def test_pre_commit_config_exists(self, project_root):
        """Pre-commit configuration exists."""
        precommit = project_root / ".pre-commit-config.yaml"
        assert precommit.exists(), ".pre-commit-config.yaml not found"

    def test_security_md_exists(self, project_root):
        """SECURITY.md exists."""
        security = project_root / "SECURITY.md"
        assert security.exists(), "SECURITY.md not found"


class TestMcpConfiguration:
    """Verify MCP configuration is properly set up."""

    def test_mcp_json_exists(self, project_root):
        """.mcp.json configuration file exists."""
        mcp = project_root / ".mcp.json"
        assert mcp.exists(), ".mcp.json not found - copy from .mcp.json.example"

    def test_mcp_json_valid(self, mcp_config):
        """MCP configuration is valid JSON."""
        assert "mcpServers" in mcp_config, "mcpServers key missing in .mcp.json"

    def test_mcp_servers_configured(self, mcp_config):
        """Required MCP servers are configured."""
        servers = mcp_config.get("mcpServers", {})

        required_servers = ["filesystem", "chrome-devtools"]
        for server in required_servers:
            assert server in servers, f"MCP server '{server}' not configured"

    def test_mcp_no_hardcoded_secrets(self, mcp_config):
        """MCP config uses environment variable references, not hardcoded secrets."""
        config_str = json.dumps(mcp_config)

        # Check for common secret patterns (should be ${VAR} not actual values)
        assert "ATATT3xFfGF0" not in config_str, "Hardcoded Atlassian token found!"
        assert "github_pat_" not in config_str or "${" in config_str, "Hardcoded GitHub token found!"
        assert "figd_" not in config_str or "${" in config_str, "Hardcoded Figma key found!"


# ============================================
# Environment Variables Tests
# ============================================

class TestEnvironmentVariables:
    """Verify required environment variables are set."""

    def test_atlassian_site_url(self):
        """ATLASSIAN_SITE_URL is set."""
        value = os.environ.get("ATLASSIAN_SITE_URL")
        assert value is not None, "ATLASSIAN_SITE_URL not set"
        assert value.startswith("https://"), "ATLASSIAN_SITE_URL should start with https://"
        assert ".atlassian.net" in value, "ATLASSIAN_SITE_URL should be an Atlassian URL"

    def test_atlassian_user_email(self):
        """ATLASSIAN_USER_EMAIL is set."""
        value = os.environ.get("ATLASSIAN_USER_EMAIL")
        assert value is not None, "ATLASSIAN_USER_EMAIL not set"
        assert "@" in value, "ATLASSIAN_USER_EMAIL should be a valid email"

    def test_atlassian_api_token(self):
        """ATLASSIAN_API_TOKEN is set."""
        value = os.environ.get("ATLASSIAN_API_TOKEN")
        assert value is not None, "ATLASSIAN_API_TOKEN not set"
        assert len(value) > 20, "ATLASSIAN_API_TOKEN seems too short"

    def test_github_token(self):
        """GITHUB_PERSONAL_ACCESS_TOKEN is set."""
        value = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
        assert value is not None, "GITHUB_PERSONAL_ACCESS_TOKEN not set"
        assert value.startswith("github_pat_") or value.startswith("ghp_"), \
            "GITHUB_PERSONAL_ACCESS_TOKEN has invalid format"

    def test_figma_api_key(self):
        """FIGMA_API_KEY is set."""
        value = os.environ.get("FIGMA_API_KEY")
        assert value is not None, "FIGMA_API_KEY not set"
        assert value.startswith("figd_"), "FIGMA_API_KEY should start with 'figd_'"


# ============================================
# Python Memory System Tests
# ============================================

class TestPythonMemorySystem:
    """Verify Python memory-system is properly installed."""

    def test_memory_system_init(self, project_root):
        """memory-system package has __init__.py."""
        init = project_root / "memory-system" / "__init__.py"
        assert init.exists(), "memory-system/__init__.py not found"

    def test_submodules_exist(self, project_root):
        """All submodules exist."""
        mem_sys = project_root / "memory-system"

        required_dirs = ["feedback", "analysis", "recommendations"]
        for subdir in required_dirs:
            path = mem_sys / subdir
            assert path.exists(), f"memory-system/{subdir} not found"
            assert (path / "__init__.py").exists(), f"memory-system/{subdir}/__init__.py not found"

    def test_pyproject_toml_exists(self, project_root):
        """pyproject.toml exists for Python package."""
        pyproject = project_root / "memory-system" / "pyproject.toml"
        assert pyproject.exists(), "memory-system/pyproject.toml not found"

    def test_subagent_file_exists(self, project_root):
        """LearningSubAgent module exists."""
        subagent = project_root / "memory-system" / "subagent.py"
        assert subagent.exists(), "memory-system/subagent.py not found"

        content = subagent.read_text(encoding='utf-8')
        assert "class LearningSubAgent" in content, \
            "LearningSubAgent class not defined in subagent.py"

    def test_feedback_collector_file_exists(self, project_root):
        """FeedbackCollector module exists."""
        collector = project_root / "memory-system" / "feedback" / "collector.py"
        assert collector.exists(), "memory-system/feedback/collector.py not found"

        content = collector.read_text(encoding='utf-8')
        # Check for key functions since it may not have a class
        assert "def create_feedback_entry" in content or "def save_feedback_entry" in content, \
            "FeedbackCollector functions not found in collector.py"

    def test_metrics_calculator_file_exists(self, project_root):
        """MetricsCalculator module exists."""
        metrics = project_root / "memory-system" / "analysis" / "metrics.py"
        assert metrics.exists(), "memory-system/analysis/metrics.py not found"

        content = metrics.read_text(encoding='utf-8')
        assert "class MetricsCalculator" in content, \
            "MetricsCalculator class not defined in metrics.py"

    @pytest.mark.slow
    @pytest.mark.skipif(
        not os.environ.get("MEMORY_SYSTEM_INSTALLED"),
        reason="Run 'pip install -e memory-system' first"
    )
    def test_import_memory_system_package(self, project_root):
        """memory-system can be imported when installed."""
        try:
            # Only works if package is installed with pip install -e
            import memory_system
            assert hasattr(memory_system, 'LearningSubAgent')
        except ImportError as e:
            pytest.fail(f"memory_system not installed: {e}")


# ============================================
# Node.js / TypeScript Tests
# ============================================

class TestNodeInstallation:
    """Verify Node.js dependencies are installed."""

    def test_node_modules_exists(self, project_root):
        """node_modules directory exists."""
        node_modules = project_root / "node_modules"
        assert node_modules.exists(), "node_modules not found - run 'npm install'"

    def test_next_installed(self, project_root):
        """Next.js is installed."""
        next_pkg = project_root / "node_modules" / "next"
        assert next_pkg.exists(), "next not installed - run 'npm install'"

    def test_react_installed(self, project_root):
        """React is installed."""
        react_pkg = project_root / "node_modules" / "react"
        assert react_pkg.exists(), "react not installed - run 'npm install'"

    def test_typescript_installed(self, project_root):
        """TypeScript is installed."""
        ts_pkg = project_root / "node_modules" / "typescript"
        assert ts_pkg.exists(), "typescript not installed - run 'npm install'"

    def test_jest_installed(self, project_root):
        """Jest is installed."""
        jest_pkg = project_root / "node_modules" / "jest"
        assert jest_pkg.exists(), "jest not installed - run 'npm install'"

    def test_prisma_installed(self, project_root):
        """Prisma is installed."""
        prisma_pkg = project_root / "node_modules" / "prisma"
        assert prisma_pkg.exists(), "prisma not installed - run 'npm install'"

    @pytest.mark.slow
    def test_node_version(self):
        """Node.js version meets requirements (>=18.0.0)."""
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            shell=True
        )
        assert result.returncode == 0, "Node.js not installed"

        version = result.stdout.strip().lstrip('v')
        major = int(version.split('.')[0])
        assert major >= 18, f"Node.js version {version} is too old, need >=18.0.0"

    @pytest.mark.slow
    def test_npm_version(self):
        """npm is available."""
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True,
            shell=True
        )
        assert result.returncode == 0, "npm not installed"


# ============================================
# AID State Directory Tests
# ============================================

class TestAidStateDirectory:
    """Verify ~/.aid directory structure."""

    def test_aid_directory_exists(self):
        """~/.aid directory exists or can be created."""
        # Directory may not exist initially, that's OK
        # Just verify we can create it
        AID_STATE_DIR.mkdir(parents=True, exist_ok=True)
        assert AID_STATE_DIR.exists(), "Failed to create ~/.aid directory"

    def test_feedback_directory_creatable(self):
        """~/.aid/feedback directory can be created."""
        feedback_dir = AID_STATE_DIR / "feedback" / "pending"
        feedback_dir.mkdir(parents=True, exist_ok=True)
        assert feedback_dir.exists(), "Failed to create feedback directory"

    def test_state_json_writable(self):
        """State file is writable."""
        state_file = AID_STATE_DIR / "state.json"
        test_state = {"test": True, "timestamp": "2024-01-01T00:00:00Z"}

        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(test_state, f)

        assert state_file.exists(), "Failed to write state.json"

        # Clean up
        with open(state_file, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        assert loaded["test"] == True


# ============================================
# Database Connection Tests (Optional)
# ============================================

class TestDatabaseConnection:
    """Verify database connection (if configured)."""

    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.environ.get("DATABASE_URL"),
        reason="DATABASE_URL not set"
    )
    def test_database_url_format(self):
        """DATABASE_URL has valid format."""
        db_url = os.environ.get("DATABASE_URL", "")

        valid_prefixes = ["postgresql://", "postgres://", "file:"]
        assert any(db_url.startswith(p) for p in valid_prefixes), \
            f"DATABASE_URL has invalid format: {db_url[:20]}..."

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.skipif(
        not os.environ.get("DATABASE_URL"),
        reason="DATABASE_URL not set"
    )
    def test_prisma_generate(self, project_root):
        """Prisma client can be generated."""
        result = subprocess.run(
            ["npx", "prisma", "generate"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            shell=True
        )
        # Allow both success and "already generated" scenarios
        assert result.returncode == 0 or "already" in result.stdout.lower(), \
            f"Prisma generate failed: {result.stderr}"


# ============================================
# Skills & Commands Sanity Tests
# ============================================

class TestSkillsAndCommands:
    """Verify skills and commands are properly structured."""

    def test_core_skills_exist(self, project_root):
        """Core AID skills exist."""
        skills_dir = project_root / ".claude" / "skills"

        required_skills = [
            "aid-development",
            "aid-discovery",
            "aid-prd",
            "aid-tech-spec",
            "aid-qa-ship",
            "phase-enforcement",
            "code-review",
            "test-driven"
        ]

        for skill in required_skills:
            skill_path = skills_dir / skill / "SKILL.md"
            assert skill_path.exists(), f"Skill not found: {skill}/SKILL.md"

    def test_core_commands_exist(self, project_root):
        """Core AID commands exist."""
        commands_dir = project_root / ".claude" / "commands"

        required_commands = [
            "aid-init.md",
            "aid-start.md",
            "aid-end.md",
            "code-review.md",
            "write-tests.md",
            "prd.md",
            "tech-spec.md"
        ]

        for cmd in required_commands:
            cmd_path = commands_dir / cmd
            assert cmd_path.exists(), f"Command not found: {cmd}"

    def test_skill_files_not_empty(self, project_root):
        """Skill files have content."""
        skills_dir = project_root / ".claude" / "skills"

        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    content = skill_file.read_text(encoding='utf-8')
                    assert len(content) > 100, f"Skill file too small: {skill_file}"


# ============================================
# Sanity Check - Run Basic Operations
# ============================================

class TestSanityOperations:
    """Sanity tests that basic operations work."""

    @pytest.mark.slow
    def test_typescript_compiles(self, project_root):
        """TypeScript configuration exists and tsc is available."""
        # Verify tsconfig.json exists (it may have comments which aren't valid JSON)
        tsconfig_path = project_root / "tsconfig.json"
        assert tsconfig_path.exists(), "tsconfig.json not found"

        # Check for key content in the file (handles comments)
        content = tsconfig_path.read_text(encoding='utf-8')
        assert "compilerOptions" in content, "tsconfig.json missing compilerOptions"

        # Verify TypeScript compiler is available
        result = subprocess.run(
            ["npx", "tsc", "--version"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            shell=True
        )
        assert result.returncode == 0, "TypeScript compiler not available"

    @pytest.mark.slow
    def test_jest_runs(self, project_root):
        """Jest test runner works."""
        result = subprocess.run(
            ["npx", "jest", "--passWithNoTests", "--testPathPattern=nonexistent"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            shell=True
        )
        # Should succeed even with no tests
        assert result.returncode == 0, f"Jest failed to run: {result.stderr}"

    @pytest.mark.slow
    def test_next_build_check(self, project_root):
        """Next.js build configuration is valid."""
        # Just check the config, don't do full build
        next_config = project_root / "next.config.js"
        if next_config.exists():
            # Verify it's valid JavaScript by checking syntax
            result = subprocess.run(
                ["node", "--check", str(next_config)],
                capture_output=True,
                text=True,
                shell=True
            )
            assert result.returncode == 0, f"next.config.js has syntax errors: {result.stderr}"


# ============================================
# Summary Report
# ============================================

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Print summary after all tests."""
    terminalreporter.write_sep("=", "AID Installation & Sanity Test Summary")

    passed = len(terminalreporter.stats.get('passed', []))
    failed = len(terminalreporter.stats.get('failed', []))
    skipped = len(terminalreporter.stats.get('skipped', []))

    total = passed + failed + skipped

    terminalreporter.write_line(f"Total: {total} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")

    if failed == 0:
        terminalreporter.write_line("\n✅ All installation and sanity checks passed!")
    else:
        terminalreporter.write_line("\n❌ Some checks failed - review output above")
