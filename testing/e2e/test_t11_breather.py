"""
T11 (T11-acceptance.md): breather disclosure, integrity pin and opt-in install.

WHY: breather's session-start instructions tell Claude to fetch today's calendar events
through any connected calendar connector, in every project, and no doc said so (A-06). Its
hook code ships as an 85 KB base64 blob with no recorded upstream version or hashes, and
the installers put it into the user-wide ~/.claude without asking (A-14).
"""
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
BREATHER = REPO / "integrations" / "breather"
LOCK = json.loads((BREATHER / "PAYLOAD.lock.json").read_text(encoding="utf-8"))


def payload():
    text = (BREATHER / "install.mjs").read_text(encoding="utf-8")
    m = re.search(r'const PAYLOAD = "([A-Za-z0-9+/=]+)";', text)
    assert m, "PAYLOAD not found in install.mjs"
    return json.loads(base64.b64decode(m.group(1)))


# --- T11-2: pin -------------------------------------------------------------

def test_t11_2_lock_names_the_upstream_commit():
    assert LOCK["upstream"] == "https://github.com/ilandahan/breather"
    assert re.fullmatch(r"[0-9a-f]{40}", LOCK["commit"])


def test_t11_2_installer_bytes_match_the_pin():
    assert hashlib.sha256((BREATHER / "install.mjs").read_bytes()).hexdigest() == LOCK["install_mjs_sha256"]


def test_t11_2_every_embedded_file_matches_the_pin():
    files = payload()
    assert sorted(files) == sorted(LOCK["files"]), "embedded file set changed"
    for rel, content in files.items():
        assert hashlib.sha256(content.encode("utf-8")).hexdigest() == LOCK["files"][rel], rel


# --- T11-1: disclosure ------------------------------------------------------

def test_t11_1_payload_still_does_what_the_docs_disclose():
    """If upstream ever drops or changes the calendar pull, the docs must be revisited."""
    text = "\n".join(payload().values())
    assert "CALENDAR (auto)" in text and "TODAY'S events" in text


@pytest.mark.parametrize("rel", ["README.md", "SECURITY.md", "integrations/breather/README.md",
                                 "commands/breather-start.md", "commands/setup.md"])
def test_t11_1_calendar_access_is_disclosed(rel):
    low = " ".join((REPO / rel).read_text(encoding="utf-8").split()).lower()   # ignore wrapping
    assert "breather" in low and "calendar" in low, rel
    assert "every" in low and "project" in low, rel           # user-wide scope
    assert "uninstall" in low or "/breather-stop" in low, rel  # how to keep it off
    # T11 review r1: the timing, the mail-scope caveat and the automatic fetch are stated.
    assert "first session of each day" in low and "on each" in low and "prompt" in low, rel
    assert "may also have access to your mail" in low, rel
    assert "without asking you" in low, rel


def test_t11_review_breather_readme_lists_everything_it_does():
    low = " ".join((REPO / "integrations" / "breather" / "README.md").read_text(encoding="utf-8").split()).lower()
    for item in ("4 hooks", "statusline", "bak-", "before any other", "handoff", "powershell",
                 "state/breather", "no network calls"):
        assert item in low, item


@pytest.mark.parametrize("rel", ["commands/breather-start.md", "commands/breather-stop.md"])
def test_t11_review_commands_never_run_a_project_local_installer(rel):
    """WHY (T11 review r1, A-26 class): a `./integrations/breather/install.mjs` fallback ran a
    repository's own script with write access to ~/.claude/settings.json."""
    text = (REPO / rel).read_text(encoding="utf-8")
    assert "./integrations/breather/install.mjs" not in text
    assert "${CLAUDE_PLUGIN_ROOT}/integrations/breather/install.mjs" in text


# --- T11-3: opt-in ----------------------------------------------------------

def test_t11_3_install_sh_runs_breather_only_after_a_yes_or_the_flag():
    text = (REPO / "install.sh").read_text(encoding="utf-8")
    body = text[text.index("setup_breather() {"):]
    body = body[:body.index("\n}\n")]
    assert "--with-breather" in text and "[y/N]" in body and "[ -t 0 ]" in body
    assert body.index("return 0") < body.index("if node integrations/breather/install.mjs")


def test_t11_3_install_bat_runs_breather_only_after_a_yes_or_the_flag():
    text = (REPO / "install.bat").read_text(encoding="utf-8")
    assert '"/breather"' in text and "[y/N]" in text and 'set "BREATHER_ANSWER=N"' in text
    assert text.index("goto :breather_done") < text.index("call node integrations\\breather\\install.mjs")


def test_t11_3_setup_asks_first():
    text = (REPO / "commands" / "setup.md").read_text(encoding="utf-8")
    step = text[text.index("**Offer breather**"):]
    assert "Ask the user first" in step and "default is No" in step
    assert step.index("Ask the user first") < step.index("node integrations/breather/install.mjs")


def _posix_bash():
    """Git Bash on Windows (System32 bash.exe is WSL, which cannot see this HOME), else bash."""
    if os.name == "nt":
        git = shutil.which("git")
        here = Path(git).resolve() if git else None
        for cand in ([here.parents[1] / "bin" / "bash.exe", here.parents[2] / "bin" / "bash.exe"] if here else []):
            if cand.is_file():
                return str(cand)
        return None
    return shutil.which("bash")


@pytest.mark.skipif(_posix_bash() is None, reason="no POSIX bash available")
def test_t11_3_non_interactive_install_writes_nothing_to_claude_home(tmp_path):
    """Run only the breather step of install.sh, with no terminal: it must skip."""
    text = (REPO / "install.sh").read_text(encoding="utf-8")
    start = text.index("WITH_BREATHER=0")
    end = text.index("\n}\n", text.index("setup_breather() {")) + 3
    script = tmp_path / "step10.sh"
    script.write_text("set -e\nlog_info(){ echo \"$1\"; }\nlog_success(){ echo \"$1\"; }\n"
                      "log_warning(){ echo \"$1\"; }\n" + text[start:end] + "\nsetup_breather\n",
                      encoding="utf-8", newline="\n")
    home = tmp_path / "home"
    home.mkdir()
    env = dict(os.environ, HOME=str(home), USERPROFILE=str(home))
    p = subprocess.run([_posix_bash(), script.as_posix()], cwd=str(REPO), env=env, stdin=subprocess.DEVNULL,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
    assert p.returncode == 0, p.stderr
    assert "skipped" in p.stdout
    assert not (home / ".claude").exists()
