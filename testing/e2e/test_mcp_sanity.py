"""
MCP Server Sanity Tests
Validates that MCP server configurations are present and well-formed.
"""
import json
import os
import pytest


class TestMCPConfiguration:
    """Verify MCP configuration files exist and are valid."""

    def test_mcp_config_template_exists(self):
        """At least one MCP config template should exist."""
        has_windows = os.path.isfile('.mcp.json.windows')
        has_mac = os.path.isfile('.mcp.json.mac')
        assert has_windows or has_mac, "No MCP config template found (.mcp.json.windows or .mcp.json.mac)"

    @pytest.mark.skipif(
        not os.path.isfile('.mcp.json.windows'),
        reason="Windows MCP config not present"
    )
    def test_windows_mcp_config_valid_json(self):
        with open('.mcp.json.windows', 'r') as f:
            data = json.load(f)
        assert 'mcpServers' in data, "MCP config missing 'mcpServers' key"

    @pytest.mark.skipif(
        not os.path.isfile('.mcp.json.mac'),
        reason="Mac MCP config not present"
    )
    def test_mac_mcp_config_valid_json(self):
        with open('.mcp.json.mac', 'r') as f:
            data = json.load(f)
        assert 'mcpServers' in data, "MCP config missing 'mcpServers' key"
