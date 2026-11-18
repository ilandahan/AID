"""
WHY THIS TEST (T8-1, A-07): session feedback was stored verbatim. A real run kept a client
name, an e-mail address and a project path in ~/.aid/feedback/pending/.
"""
import pytest

from memory_system.redact import redact, redact_obj

NAMES = {"secret-proj", "payroll", "acmecorp"}


@pytest.mark.parametrize("text, gone, label", [
    ("ping jane.doe@acme.example today", "jane.doe", "[email]"),
    ("see https://github.com/acmecorp/payroll/pull/3", "github.com", "[url]"),
    ("remote git@github.com:acmecorp/payroll.git", "github.com", "[url]"),
    ("file C:/clients/acme/secret-proj/x.py", "C:/clients", "[path]"),
    (r"file C:\Users\jane\proj\a.ts", "Users", "[path]"),
    (r"share \\srv\share\x", "srv", "[path]"),
    ("home /home/jane/work/x", "/home/jane", "[path]"),
    ("notes ~/notes/a.md", "notes/a.md", "[path]"),
    ("bug at src/app.ts:12", "app.ts:12", "[file-ref]"),
    ("token ghp_abcdefghijklmnopqrstuvwxyz0123", "ghp_", "[token]"),
    ("key sk-proj-ABCDEFGHIJKLMNOP12", "sk-proj", "[token]"),
    ("aws AKIAABCDEFGHIJKLMNOP", "AKIA", "[token]"),
    ("hash 0123456789abcdef0123456789abcdef01", "0123456789abcdef", "[token]"),
    ("the AcmeCorp payroll repo", "AcmeCorp", "[project]"),
    ("my secret proj and secretproj", "secret", "[project]"),
])
def test_sensitive_parts_are_replaced(text, gone, label):
    out = redact(text, NAMES)
    assert gone.lower() not in out.lower() and label in out, out


@pytest.mark.parametrize("text", [
    "clear scope, more NFRs next time", "rating 4", "PRD", "TDD worked well",
    "used /phase-approve and/or /gate-check", "v1.2.3 at 10:30, ratio 3:1, phase 4.5",
    "Phase 2 Tech Spec: API design was clear; JWT auth chosen", "README.md was good",
])
def test_methodology_text_survives(text):
    assert redact(text, NAMES) == text


def test_idempotent_and_non_strings_untouched():
    once = redact("jane@x.io at C:/a/b and src/x.py:3", NAMES)
    assert redact(once, NAMES) == once
    assert redact(None) is None and redact(4) == 4


def test_generic_folder_names_are_not_redacted():
    # A project folder called "docs" or "app" must not erase those words from feedback.
    assert redact("the docs app was fine", {"docs", "app", "src"}) == "the docs app was fine"


def test_redact_obj_walks_nested_values_and_keeps_timestamp():
    obj = {"timestamp": "2026-11-18T10:00:00Z", "a": ["x@y.io", {"b": "C:/p/q"}]}
    out = redact_obj(obj)
    assert out == {"timestamp": "2026-11-18T10:00:00Z", "a": ["[email]", {"b": "[path]"}]}


def test_the_os_user_name_becomes_user(monkeypatch):
    monkeypatch.setenv("USERNAME", "zelda")
    monkeypatch.setenv("USER", "zelda")
    from memory_system.redact import context_names
    assert redact("ask zelda about it", context_names()) == "ask [user] about it"
