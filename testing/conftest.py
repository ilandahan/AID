"""
AID Testing Framework - Pytest Configuration

This file contains shared fixtures and configuration for all tests.
"""

import pytest
import os
from typing import Generator, Any

# ============================================
# Configuration
# ============================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: Integration tests (moderate speed)")
    config.addinivalue_line("markers", "e2e: End-to-end tests (slow)")
    config.addinivalue_line("markers", "simulation: Simulation tests (very slow)")
    config.addinivalue_line("markers", "slow: Tests that take >5s to run")


# ============================================
# Fixtures - Database
# ============================================

@pytest.fixture(scope="function")
def test_db():
    """
    Provide a clean test database for each test.
    
    Uses transaction rollback for isolation.
    """
    # Setup: Create test database connection
    # For real implementation, use your ORM's test database setup
    db = {"connected": True, "data": {}}
    
    yield db
    
    # Teardown: Rollback/cleanup
    db["data"].clear()


@pytest.fixture(scope="function")
def test_redis():
    """
    Provide a clean Redis instance for each test.
    
    Uses a dedicated test database (db 15).
    """
    # For real implementation, connect to actual test Redis
    redis = {"connected": True, "data": {}}
    
    yield redis
    
    # Teardown: Flush test database
    redis["data"].clear()


# ============================================
# Fixtures - Test Data
# ============================================

@pytest.fixture
def sample_user() -> dict:
    """Provide realistic sample user data."""
    return {
        "name": "María García-López",
        "email": "maria.garcia@example.com",
        "bio": "Senior software engineer passionate about AI. 🚀",
        "phone": "+34-123-456-789",
        "preferences": {"language": "es", "timezone": "Europe/Madrid"}
    }


@pytest.fixture
def sample_users() -> list:
    """Provide multiple realistic sample users."""
    return [
        {
            "name": "María García-López",
            "email": "maria.garcia@example.com",
            "bio": "Senior software engineer passionate about AI. 🚀",
            "phone": "+34-123-456-789",
            "preferences": {"language": "es", "timezone": "Europe/Madrid"}
        },
        {
            "name": "李明",
            "email": "li.ming+test@example.co.uk",
            "bio": "",  # Edge case: empty bio
            "phone": None,  # Edge case: missing phone
            "preferences": {}
        },
        {
            "name": "O'Brien-Smith III",
            "email": "test.user@subdomain.example.org",
            "bio": "A" * 500,  # Edge case: max length
            "phone": "555.123.4567 ext 123",
            "preferences": {"language": "en", "timezone": "America/New_York"}
        }
    ]


@pytest.fixture
def sample_config() -> dict:
    """Provide sample configuration data."""
    return {
        "tenant_name": "acme_corp",
        "company_name": "ACME Corporation",
        "type": "sales",
        "integrations": {
            "shopify": {
                "enabled": True,
                "api_key": "test_key_123"
            }
        },
        "tools": ["product_lookup", "order_status", "inventory_check"]
    }


# ============================================
# Fixtures - HTTP/API
# ============================================

@pytest.fixture
def mock_api_response() -> dict:
    """Provide sample API response structure."""
    return {
        "status": "success",
        "data": {},
        "meta": {
            "timestamp": "2024-01-01T00:00:00Z",
            "version": "1.0"
        }
    }


# ============================================
# Fixtures - Environment
# ============================================

@pytest.fixture
def clean_env(monkeypatch):
    """Provide a clean environment without sensitive variables."""
    sensitive_vars = [
        "DATABASE_URL",
        "REDIS_URL",
        "API_SECRET_KEY",
        "ANTHROPIC_API_KEY"
    ]
    for var in sensitive_vars:
        monkeypatch.delenv(var, raising=False)
    
    yield
    
    # Environment restored automatically by monkeypatch


@pytest.fixture
def test_env(monkeypatch):
    """Set up test environment variables."""
    test_vars = {
        "NODE_ENV": "test",
        "DATABASE_URL": "postgresql://test:test@localhost:5432/test_db",
        "REDIS_URL": "redis://localhost:6379/15",
    }
    for key, value in test_vars.items():
        monkeypatch.setenv(key, value)
    
    yield test_vars


# ============================================
# Helpers
# ============================================

def assert_valid_user(user: dict) -> None:
    """Helper to validate user structure."""
    assert "name" in user
    assert "email" in user
    assert "@" in user["email"]


def assert_valid_response(response: dict) -> None:
    """Helper to validate API response structure."""
    assert "status" in response
    assert response["status"] in ["success", "error"]
