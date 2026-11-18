"""
The ONE place the memory system finds its data directory (T8-3, INV-1).

WHY: every module used to hard-code ``~/.aid`` at import time, so ``$AID_HOME`` (which the
phase gates and tests use) was ignored and test runs wrote to the real home folder.
"""

import os
from pathlib import Path


def aid_home() -> Path:
    """``$AID_HOME`` when set, else ``~/.aid``. Read on every call, never cached."""
    env = os.environ.get("AID_HOME")
    return Path(env) if env else Path(os.path.expanduser("~")) / ".aid"


def feedback_dir() -> Path:
    return aid_home() / "feedback"


def pending_dir() -> Path:
    return feedback_dir() / "pending"


def processed_dir() -> Path:
    return feedback_dir() / "processed"


def memory_dir() -> Path:
    return aid_home() / "memory"


def recommendations_dir() -> Path:
    return aid_home() / "recommendations"


def reports_dir() -> Path:
    return aid_home() / "reports"
