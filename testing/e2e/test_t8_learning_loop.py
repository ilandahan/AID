"""
T8 (T8-acceptance.md): learning-loop privacy, end to end through the REAL writer
(hooks/aid_session.py) and the memory_system CLI, in an isolated HOME/AID_HOME.

WHY: feedback was stored verbatim (A-07: a client name, an e-mail and a project path sat in
~/.aid/feedback/pending/), --sync-memory wrote memory with no confirmation, and the
memory-analysis agent had Write access to skill files (A-45).
"""
import fnmatch
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SESSION = REPO_ROOT / "hooks" / "aid_session.py"
MEMORY = REPO_ROOT / "memory-system"
sys.path.insert(0, str(REPO_ROOT / "hooks"))
import aid_guard  # noqa: E402

SECRETS = ("jane.doe", "acme.example", "c:/clients", "secret-proj", "x.py:42", "payroll", "acmecorp")
LEAK_TEXT = ("AcmeCorp payroll repo, ping jane.doe@acme.example, "
             "see C:/clients/acme/secret-proj/x.py:42")


@pytest.fixture
def env(tmp_path):
    """Project .../acme/secret-proj with git remote github.com/acmecorp/payroll, own home."""
    proj = tmp_path / "acme" / "secret-proj"
    (proj / ".aid" / "hooks").mkdir(parents=True)
    (proj / ".aid" / "hooks" / "config.json").write_text("{}", encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(proj)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(proj), "remote", "add", "origin",
                    "https://github.com/acmecorp/payroll.git"], check=True, capture_output=True)
    home = tmp_path / "home"
    home.mkdir()
    e = dict(os.environ, HOME=str(home), USERPROFILE=str(home), AID_HOME=str(home / ".aid"),
             PYTHONIOENCODING="utf-8")
    e.pop("CLAUDE_PROJECT_DIR", None)
    return proj, home / ".aid", e


def sess(env, *args):
    proj, _, e = env
    p = subprocess.run([sys.executable, str(SESSION)] + list(args), cwd=str(proj), env=e,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    return p.returncode, p.stdout + p.stderr


def cli(env, *flags):
    _, _, e = env
    p = subprocess.run([sys.executable, "-m", "memory_system"] + list(flags), cwd=str(MEMORY), env=e,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    return p.returncode, p.stdout + p.stderr


def no_secrets(text):
    low = text.lower().replace("\\", "/")
    return [s for s in SECRETS if s in low]


def pending(aid):
    return sorted((aid / "feedback" / "pending").glob("*.json"))


def test_t8_1_end_redacts_before_writing(env):
    """The audit's own case. AcmeCorp is caught only because it is the git remote owner."""
    proj, aid, _ = env
    assert sess(env, "init", "developer", "2")[0] == 0
    rc, out = sess(env, "end", "--rating", "4", "--worked", LEAK_TEXT, "--improve", LEAK_TEXT,
                   "--review", "partial", "--review-note", LEAK_TEXT)
    assert rc == 0, out
    files = pending(aid)
    assert len(files) == 1
    text = files[0].read_text(encoding="utf-8")
    assert no_secrets(text) == [], text
    data = json.loads(text)
    assert data["rating"] == 4 and "[email]" in data["worked_well"] and "[path]" in data["to_improve"]


def test_t8_d5_phase_approve_rating_reaches_the_loop_redacted(env):
    proj, aid, _ = env
    assert sess(env, "init", "developer", "1")[0] == 0
    assert sess(env, "approve", "--note", "rating 2 payroll scope unclear")[0] == 0
    data = json.loads(pending(aid)[0].read_text(encoding="utf-8"))
    assert data["source"] == "phase-approve" and data["rating"] == 2
    assert "payroll" not in data["note"].lower()
    rc, out = cli(env, "--analyze", "--format", "json")
    assert rc == 0 and json.loads(out[out.index("{"):])["has_data"], out


def _old_unredacted_file(aid):
    pend = aid / "feedback" / "pending"
    pend.mkdir(parents=True, exist_ok=True)
    for i in range(4):
        (pend / "old{}.json".format(i)).write_text(json.dumps({
            "id": "old-{}".format(i), "timestamp": "2026-11-18T10:00:00Z", "session_id": "s",
            "context": {"phase": "2-tech-spec", "role": "pm", "interaction_type": "decision"},
            "decision": {"topic": "db", "topic_category": "technology", "chosen": "pg"},
            "debate": {"occurred": True, "outcome": "changed", "learning": LEAK_TEXT},
            "feedback": {"rating": 2, "verbal": "too verbose, be brief. " + LEAK_TEXT}}), encoding="utf-8")


GENERIC = ("jane.doe", "acme.example", "c:/clients", "x.py:42")


def test_t8_1_old_unredacted_files_are_redacted_when_read(env):
    """Read from an unrelated folder, the generic classes (e-mail, path, file:line) are
    always removed. The project's own names are removed when the reader knows the project
    ($CLAUDE_PROJECT_DIR or the cwd); a reader cannot know which project an old file came
    from otherwise. That limit is stated in the docs."""
    proj, aid, e = env
    _old_unredacted_file(aid)
    for flags in (["--analyze", "--format", "json"], ["--dashboard", "--save", "--format", "json"],
                  ["--sync-memory"], ["--recommendations"], ["--pending"]):
        rc, out = cli(env, *flags)
        assert rc == 0 and "Traceback" not in out, (flags, out[-800:])
        assert [s for s in no_secrets(out) if s in GENERIC] == [], (flags, no_secrets(out))
    for f in (aid / "recommendations").glob("*.json"):
        f.unlink()
    for f in (aid / "reports").glob("*"):
        f.unlink()
    known = (proj, aid, dict(e, CLAUDE_PROJECT_DIR=str(proj)))
    for flags in (["--analyze", "--format", "json"], ["--dashboard", "--save", "--format", "json"],
                  ["--sync-memory"], ["--recommendations"]):
        rc, out = cli(known, *flags)
        assert rc == 0 and no_secrets(out) == [], (flags, no_secrets(out))
    rc, out = sess(env, "memory-preview")
    assert rc == 0 and no_secrets(out) == [], out
    for f in aid.rglob("*.json"):
        if "feedback" not in f.parts:
            assert no_secrets(f.read_text(encoding="utf-8")) == [], f


def test_t8_2_preview_writes_nothing_and_sync_writes_redacted(env):
    proj, aid, _ = env
    _old_unredacted_file(aid)
    rc, out = sess(env, "memory-preview")
    assert rc == 0 and "nothing is written" in out, out
    rc, out = cli(env, "--sync-memory")
    assert rc == 0 and "Would add" in out, out
    assert not (aid / "memory").exists()
    rc, out = sess(env, "memory-sync")
    assert rc == 0 and "Memories added" in out, out
    slots = (aid / "memory" / "slots.json").read_text(encoding="utf-8")
    assert '"content"' in slots and no_secrets(slots) == []


def test_t8_2_queue_apply_reject_through_the_session_script(env, tmp_path):
    proj, aid, _ = env
    proposals = proj / ".aid" / "improve" / "proposals.json"
    proposals.parent.mkdir()
    proposals.write_text(json.dumps({"suggestions": [
        {"target": {"file": "skills/memory-system/references/roles/developer/cumulative.md"},
         "content": "Check team conventions first; ping jane.doe@acme.example", "priority": "high"},
        {"target": {"file": "skills/aid-prd/SKILL.md"}, "content": "rewrite the skill"},
        {"target": {"file": "../../hooks/aid_guard.py"}, "content": "x"}]}), encoding="utf-8")
    rc, out = sess(env, "memory-queue")
    assert rc == 0 and "Queued 1" in out and "SKILL.md" in out, out
    queue = json.loads((aid / "recommendations" / "queue.json").read_text(encoding="utf-8"))
    assert len(queue) == 1 and "jane.doe" not in json.dumps(queue)
    rc, out = sess(env, "memory-apply", "0000000000")
    assert rc != 0 and "refused" in out
    rc, out = sess(env, "memory-reject", queue[0]["id"])
    assert rc == 0, out
    assert json.loads((aid / "recommendations" / "queue.json").read_text(encoding="utf-8")) == []


def test_t8_2_memory_writes_are_confirmed_by_the_user():
    """The ask rules cover memory-sync and memory-apply; any other spelling is refused."""
    script = str(SESSION).replace("\\", "/")
    for cmd, confirmed in (('python "{}" memory-sync'.format(script), True),
                           ('python "{}" memory-apply 0123456789abcdef'.format(script), True),
                           ('python "{}" memory-preview'.format(script), False),
                           ('python "{}" memory-reject 0123456789abcdef'.format(script), False)):
        bare = cmd.replace('"', "")
        asked = any(fnmatch.fnmatchcase(bare, r[len("Bash("):-1]) for r in aid_guard.ASK_RULES)
        assert asked is confirmed, cmd
        assert aid_guard.confirmed_form_verdict(cmd) is None, cmd
    for bad in ('python "{}"  memory-sync', 'python "{}" memory-SYNC', 'python "{}" "memory-sync"',
                'PYTHON "{}" memory-apply 0123456789abcdef'):
        assert aid_guard.confirmed_form_verdict(bad.format(script)), bad


def test_t8_2_memory_system_cli_has_no_write_flag(env):
    rc, out = cli(env, "--help")
    assert rc == 0 and "--approve" not in out and "--apply" not in out


def test_t8_2_memory_analysis_agent_only_proposes():
    text = (REPO_ROOT / "agents" / "memory-analysis-agent.md").read_text(encoding="utf-8")
    front = text.split("---")[1]
    tools = re.search(r"^tools:\s*(.+)$", front, re.M).group(1)
    assert {t.strip() for t in tools.split(",")} == {"Read", "Grep", "Glob"}, tools
    assert "auto-apply" not in text.lower()


def test_t8_6_no_shipped_doc_claims_anonymisation():
    """WHY (A-07): ~15 docs said feedback was "anonymized"; the code redacted nothing. The
    docs now describe best-effort redaction, so the word must not come back."""
    skip = {"node_modules", ".git", ".aid", ".claude"}
    hits = []
    for path in REPO_ROOT.rglob("*.md"):
        if skip & set(path.relative_to(REPO_ROOT).parts):
            continue
        for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if re.search(r"(?i)anonymi[sz]", line):
                hits.append("{}:{}".format(path.relative_to(REPO_ROOT), n))
    assert hits == [], hits


def test_t8_3_status_counts_real_entries(env):
    proj, aid, _ = env
    assert sess(env, "init", "developer", "2")[0] == 0
    assert sess(env, "end", "--rating", "3")[0] == 0
    rc, out = cli(env, "--status")
    assert rc == 0 and "Feedback Entries: 1" in out, out


def test_t8_2_analysis_input_is_redacted(env):
    """The agent gets its feedback from memory-feedback, never from raw pending files."""
    proj, aid, _ = env
    _old_unredacted_file(aid)
    rc, out = sess(env, "memory-feedback")
    assert rc == 0 and no_secrets(out) == [], no_secrets(out)
    assert len(json.loads(out)) == 4


@pytest.mark.parametrize("phase", [0, 1, 3, 4])
def test_t8_review_every_improve_command_passes_the_phase_gate(phase):
    """WHY (T8 review r1 BLOCKER): `memory-queue .aid/improve/proposals.json` was refused
    before Phase 4 (no '/' in the plugin script's arguments), so /aid-improve stopped at step
    3. Every call aid-improve.md documents must pass the Bash gate in every phase."""
    doc = (REPO_ROOT / "commands" / "aid-improve.md").read_text(encoding="utf-8")
    script = str(SESSION).replace("\\", "/")
    calls = sorted(set(re.findall(r'python "\$\{CLAUDE_PLUGIN_ROOT\}/hooks/aid_session\.py" ([^\n`]+)', doc)))
    assert {c.split()[0] for c in calls} >= {"memory-preview", "memory-feedback", "memory-queue",
                                             "memory-apply", "memory-reject", "memory-sync"}, calls
    for call in calls:
        cmd = 'python "{}" {}'.format(script, call.replace("<id>", "0123456789abcdef").strip())
        reason = aid_guard.evaluate_bash(cmd, str(REPO_ROOT), str(REPO_ROOT), phase, {}, [])
        assert reason is None, (phase, cmd, reason)


def test_t8_review_reader_uses_the_project_not_only_the_cwd(env):
    """WHY (T8 review r1 MAJOR): read-time redaction knew only the cwd's names, so an old
    file read from a subfolder kept the project's names. aid_session passes its project."""
    proj, aid, e = env
    _old_unredacted_file(aid)
    (proj / "docs").mkdir()
    p = subprocess.run([sys.executable, str(SESSION), "memory-feedback"], cwd=str(proj / "docs"),
                       env=e, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    assert p.returncode == 0 and no_secrets(p.stdout) == [], no_secrets(p.stdout)
