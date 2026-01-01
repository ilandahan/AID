"""
AID MCP Integration Sanity Tests

E2E tests to verify MCP server integrations work:
1. Environment variables are set
2. MCP configuration is valid
3. Basic connectivity tests (where possible)

Note: These tests verify configuration, not full integration.
Full MCP testing requires running MCP servers.

Run with: pytest testing/e2e/test_mcp_sanity.py -v
"""

import pytest
import os
import json
import subprocess
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import urlparse

# ============================================
# Configuration
# ============================================

PROJECT_ROOT = Path(__file__).parent.parent.parent


# ============================================
# Fixtures
# ============================================

@pytest.fixture(scope="module")
def mcp_config() -> Dict[str, Any]:
    """Load MCP configuration."""
    mcp_path = PROJECT_ROOT / ".mcp.json"
    if mcp_path.exists():
        with open(mcp_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


@pytest.fixture(scope="module")
def env_vars() -> Dict[str, Optional[str]]:
    """Get all relevant environment variables."""
    return {
        "ATLASSIAN_SITE_URL": os.environ.get("ATLASSIAN_SITE_URL"),
        "ATLASSIAN_USER_EMAIL": os.environ.get("ATLASSIAN_USER_EMAIL"),
        "ATLASSIAN_API_TOKEN": os.environ.get("ATLASSIAN_API_TOKEN"),
        "GITHUB_PERSONAL_ACCESS_TOKEN": os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN"),
        "FIGMA_API_KEY": os.environ.get("FIGMA_API_KEY"),
    }


# ============================================
# MCP Configuration Tests
# ============================================

class TestMcpConfigStructure:
    """Test MCP configuration file structure."""

    def test_mcp_json_exists(self):
        """.mcp.json file exists."""
        mcp_path = PROJECT_ROOT / ".mcp.json"
        assert mcp_path.exists(), ".mcp.json not found - copy from .mcp.json.example"

    def test_mcp_json_valid_json(self, mcp_config):
        """MCP configuration is valid JSON."""
        assert mcp_config is not None
        assert isinstance(mcp_config, dict)

    def test_mcp_servers_key_exists(self, mcp_config):
        """mcpServers key exists in configuration."""
        assert "mcpServers" in mcp_config, "mcpServers key not found"

    def test_filesystem_server_configured(self, mcp_config):
        """Filesystem MCP server is configured."""
        servers = mcp_config.get("mcpServers", {})
        assert "filesystem" in servers, "filesystem server not configured"

        fs_server = servers["filesystem"]
        assert "command" in fs_server
        assert "args" in fs_server

    def test_chrome_devtools_configured(self, mcp_config):
        """Chrome DevTools MCP server is configured."""
        servers = mcp_config.get("mcpServers", {})
        assert "chrome-devtools" in servers, "chrome-devtools server not configured"

    def test_jira_server_configured(self, mcp_config):
        """Jira MCP server is configured."""
        servers = mcp_config.get("mcpServers", {})
        assert "jira" in servers, "jira server not configured"

        jira = servers["jira"]
        assert "env" in jira, "jira server missing env configuration"

    def test_confluence_server_configured(self, mcp_config):
        """Confluence MCP server is configured."""
        servers = mcp_config.get("mcpServers", {})
        assert "confluence" in servers, "confluence server not configured"

    def test_figma_server_configured(self, mcp_config):
        """Figma MCP server is configured."""
        servers = mcp_config.get("mcpServers", {})
        assert "figma" in servers, "figma server not configured"

    def test_github_server_configured(self, mcp_config):
        """GitHub MCP server is configured."""
        servers = mcp_config.get("mcpServers", {})
        assert "github" in servers, "github server not configured"


class TestMcpSecurityConfiguration:
    """Test MCP configuration security."""

    def test_no_hardcoded_atlassian_token(self, mcp_config):
        """Atlassian token is not hardcoded."""
        config_str = json.dumps(mcp_config)

        # Real Atlassian tokens start with ATATT
        assert "ATATT3xFfGF0" not in config_str, \
            "Hardcoded Atlassian API token detected! Use ${ATLASSIAN_API_TOKEN}"

    def test_no_hardcoded_github_token(self, mcp_config):
        """GitHub token is not hardcoded."""
        config_str = json.dumps(mcp_config)

        # GitHub PATs start with github_pat_ or ghp_
        has_env_ref = "${GITHUB_PERSONAL_ACCESS_TOKEN}" in config_str
        has_raw_token = "github_pat_11AH5I5CQ" in config_str

        assert not has_raw_token or has_env_ref, \
            "Hardcoded GitHub token detected! Use ${GITHUB_PERSONAL_ACCESS_TOKEN}"

    def test_no_hardcoded_figma_key(self, mcp_config):
        """Figma API key is not hardcoded."""
        config_str = json.dumps(mcp_config)

        # Figma keys start with figd_
        has_env_ref = "${FIGMA_API_KEY}" in config_str
        has_raw_key = "figd_kLf2Untj" in config_str

        assert not has_raw_key or has_env_ref, \
            "Hardcoded Figma API key detected! Use ${FIGMA_API_KEY}"

    def test_uses_environment_variables(self, mcp_config):
        """MCP config uses environment variable references."""
        config_str = json.dumps(mcp_config)

        # Should find ${VAR_NAME} patterns
        expected_vars = [
            "${ATLASSIAN_API_TOKEN}",
            "${GITHUB_PERSONAL_ACCESS_TOKEN}",
            "${FIGMA_API_KEY}"
        ]

        for var in expected_vars:
            assert var in config_str, f"Missing environment variable reference: {var}"


# ============================================
# Environment Variable Tests
# ============================================

class TestAtlassianEnvVars:
    """Test Atlassian environment variables."""

    def test_atlassian_site_url_set(self, env_vars):
        """ATLASSIAN_SITE_URL is set."""
        assert env_vars["ATLASSIAN_SITE_URL"] is not None, \
            "ATLASSIAN_SITE_URL not set"

    def test_atlassian_site_url_valid(self, env_vars):
        """ATLASSIAN_SITE_URL has valid format."""
        url = env_vars["ATLASSIAN_SITE_URL"]
        if url:
            assert url.startswith("https://"), \
                "ATLASSIAN_SITE_URL should start with https://"
            assert ".atlassian.net" in url, \
                "ATLASSIAN_SITE_URL should be an Atlassian URL"

    def test_atlassian_email_set(self, env_vars):
        """ATLASSIAN_USER_EMAIL is set."""
        assert env_vars["ATLASSIAN_USER_EMAIL"] is not None, \
            "ATLASSIAN_USER_EMAIL not set"

    def test_atlassian_email_valid(self, env_vars):
        """ATLASSIAN_USER_EMAIL is a valid email."""
        email = env_vars["ATLASSIAN_USER_EMAIL"]
        if email:
            assert "@" in email, "ATLASSIAN_USER_EMAIL should be a valid email"

    def test_atlassian_token_set(self, env_vars):
        """ATLASSIAN_API_TOKEN is set."""
        assert env_vars["ATLASSIAN_API_TOKEN"] is not None, \
            "ATLASSIAN_API_TOKEN not set"

    def test_atlassian_token_not_empty(self, env_vars):
        """ATLASSIAN_API_TOKEN is not empty."""
        token = env_vars["ATLASSIAN_API_TOKEN"]
        if token:
            assert len(token) > 20, "ATLASSIAN_API_TOKEN seems too short"


class TestGitHubEnvVars:
    """Test GitHub environment variables."""

    def test_github_token_set(self, env_vars):
        """GITHUB_PERSONAL_ACCESS_TOKEN is set."""
        assert env_vars["GITHUB_PERSONAL_ACCESS_TOKEN"] is not None, \
            "GITHUB_PERSONAL_ACCESS_TOKEN not set"

    def test_github_token_format(self, env_vars):
        """GITHUB_PERSONAL_ACCESS_TOKEN has valid format."""
        token = env_vars["GITHUB_PERSONAL_ACCESS_TOKEN"]
        if token:
            valid_prefixes = ["github_pat_", "ghp_", "gho_", "ghu_"]
            assert any(token.startswith(p) for p in valid_prefixes), \
                f"GITHUB_PERSONAL_ACCESS_TOKEN has invalid format (should start with {valid_prefixes})"


class TestFigmaEnvVars:
    """Test Figma environment variables."""

    def test_figma_key_set(self, env_vars):
        """FIGMA_API_KEY is set."""
        assert env_vars["FIGMA_API_KEY"] is not None, \
            "FIGMA_API_KEY not set"

    def test_figma_key_format(self, env_vars):
        """FIGMA_API_KEY has valid format."""
        key = env_vars["FIGMA_API_KEY"]
        if key:
            assert key.startswith("figd_"), \
                "FIGMA_API_KEY should start with 'figd_'"


# ============================================
# Connectivity Tests (Optional - require network)
# ============================================

class TestAtlassianConnectivity:
    """Test Atlassian API connectivity."""

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.skipif(
        not os.environ.get("ATLASSIAN_API_TOKEN"),
        reason="ATLASSIAN_API_TOKEN not set"
    )
    def test_atlassian_api_reachable(self, env_vars):
        """Atlassian API is reachable with credentials."""
        import base64

        site_url = env_vars["ATLASSIAN_SITE_URL"]
        email = env_vars["ATLASSIAN_USER_EMAIL"]
        token = env_vars["ATLASSIAN_API_TOKEN"]

        if not all([site_url, email, token]):
            pytest.skip("Atlassian credentials not fully configured")

        # Test the myself endpoint
        url = f"{site_url}/rest/api/3/myself"
        auth_str = base64.b64encode(f"{email}:{token}".encode()).decode()

        try:
            response = requests.get(
                url,
                headers={
                    "Authorization": f"Basic {auth_str}",
                    "Content-Type": "application/json"
                },
                timeout=10
            )

            assert response.status_code == 200, \
                f"Atlassian API returned {response.status_code}: {response.text[:200]}"

            data = response.json()
            assert "accountId" in data or "displayName" in data, \
                "Unexpected response from Atlassian API"

        except requests.exceptions.RequestException as e:
            pytest.fail(f"Failed to connect to Atlassian API: {e}")


class TestGitHubConnectivity:
    """Test GitHub API connectivity."""

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.skipif(
        not os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN"),
        reason="GITHUB_PERSONAL_ACCESS_TOKEN not set"
    )
    def test_github_api_reachable(self, env_vars):
        """GitHub API is reachable with token."""
        token = env_vars["GITHUB_PERSONAL_ACCESS_TOKEN"]

        if not token:
            pytest.skip("GitHub token not configured")

        try:
            response = requests.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                timeout=10
            )

            assert response.status_code == 200, \
                f"GitHub API returned {response.status_code}: {response.text[:200]}"

            data = response.json()
            assert "login" in data, "Unexpected response from GitHub API"

        except requests.exceptions.RequestException as e:
            pytest.fail(f"Failed to connect to GitHub API: {e}")


class TestFigmaConnectivity:
    """Test Figma API connectivity."""

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.skipif(
        not os.environ.get("FIGMA_API_KEY"),
        reason="FIGMA_API_KEY not set"
    )
    def test_figma_api_reachable(self, env_vars):
        """Figma API is reachable with key."""
        key = env_vars["FIGMA_API_KEY"]

        if not key:
            pytest.skip("Figma key not configured")

        try:
            response = requests.get(
                "https://api.figma.com/v1/me",
                headers={"X-Figma-Token": key},
                timeout=10
            )

            assert response.status_code == 200, \
                f"Figma API returned {response.status_code}: {response.text[:200]}"

            data = response.json()
            assert "id" in data or "email" in data, \
                "Unexpected response from Figma API"

        except requests.exceptions.RequestException as e:
            pytest.fail(f"Failed to connect to Figma API: {e}")


# ============================================
# MCP Server Package Tests
# ============================================

class TestMcpPackages:
    """Test MCP server packages can be installed."""

    @pytest.mark.slow
    def test_npx_available(self):
        """npx command is available."""
        result = subprocess.run(
            ["npx", "--version"],
            capture_output=True,
            text=True,
            shell=True
        )
        assert result.returncode == 0, "npx not available"

    @pytest.mark.slow
    @pytest.mark.integration
    def test_filesystem_mcp_installable(self):
        """Filesystem MCP server package exists."""
        result = subprocess.run(
            ["npm", "view", "@modelcontextprotocol/server-filesystem", "version"],
            capture_output=True,
            text=True,
            shell=True
        )
        # If package exists, npm view will succeed
        assert result.returncode == 0 or "version" in result.stdout.lower(), \
            "Filesystem MCP package not found in npm registry"

    @pytest.mark.slow
    @pytest.mark.integration
    def test_github_mcp_installable(self):
        """GitHub MCP server package exists."""
        result = subprocess.run(
            ["npm", "view", "@modelcontextprotocol/server-github", "version"],
            capture_output=True,
            text=True,
            shell=True
        )
        assert result.returncode == 0 or "version" in result.stdout.lower(), \
            "GitHub MCP package not found in npm registry"


# ============================================
# Summary
# ============================================

class TestMcpSummary:
    """Summary tests for MCP configuration."""

    def test_all_required_servers_present(self, mcp_config):
        """All required MCP servers are configured."""
        servers = mcp_config.get("mcpServers", {})

        required = ["filesystem", "jira", "confluence", "figma", "github"]
        missing = [s for s in required if s not in servers]

        assert len(missing) == 0, f"Missing MCP servers: {missing}"

    def test_all_env_vars_set(self, env_vars):
        """All required environment variables are set."""
        required = [
            "ATLASSIAN_SITE_URL",
            "ATLASSIAN_USER_EMAIL",
            "ATLASSIAN_API_TOKEN",
            "GITHUB_PERSONAL_ACCESS_TOKEN",
            "FIGMA_API_KEY"
        ]

        missing = [v for v in required if not env_vars.get(v)]

        assert len(missing) == 0, f"Missing environment variables: {missing}"
