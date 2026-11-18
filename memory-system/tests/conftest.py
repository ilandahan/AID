"""Every test runs with its own AID_HOME/HOME, so nothing touches the real ~/.aid (T8-5)."""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture(autouse=True)
def aid_home(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.setenv("AID_HOME", str(home / ".aid"))
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    monkeypatch.chdir(tmp_path)
    from memory_system.feedback import collector
    collector._CONTEXT.clear()
    collector.default_names.cache_clear()
    yield home / ".aid"
    collector._CONTEXT.clear()
    collector.default_names.cache_clear()
