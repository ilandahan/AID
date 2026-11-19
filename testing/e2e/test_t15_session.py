"""
T15 WS-B (T15-acceptance.md T15-12..T15-17): aid_session.py reset / qa-pass, redacted
review and approval notes, the QA Stop gate (validate-qa-gate.py) and memory-queue's two
skip reasons. Every test runs the REAL script in a subprocess, with its own HOME,
USERPROFILE and AID_HOME, and CLAUDE_PROJECT_DIR / CLAUDE_CONFIG_DIR unset.

WHY: notes were stored verbatim in state.json (R-09), /aid-reset had the agent `rm` folders
by hand (G9-08), and the QA gate let any agent-written marker file count as a QA pass (R-07)
while failing open on unreadable inputs (A-16).
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SESSION = REPO_ROOT / "hooks" / "aid_session.py"
QA_HOOK = REPO_ROOT / "hooks" / "validate-qa-gate.py"
ALLOWED_TARGET = "skills/memory-system/references/roles/developer/cumulative.md"


def _env(home, **extra):
    e = dict(os.environ, HOME=str(home), USERPROFILE=str(home), AID_HOME=str(home / ".aid"),
             PYTHONIOENCODING="utf-8")
    for k in ("CLAUDE_PROJECT_DIR", "CLAUDE_CONFIG_DIR"):
        e.pop(k, None)
    e.update(extra)
    return e


@pytest.fixture
def proj(tmp_path):
    """An AID project P (marker .aid/hooks/config.json) and a separate fake home H."""
    P, H = tmp_path / "P", tmp_path / "H"
    (P / ".aid" / "hooks").mkdir(parents=True)
    (P / ".aid" / "hooks" / "config.json").write_text("{}", encoding="utf-8")
    H.mkdir()
    return P, H


def sess(P, H, *args, cwd=None, **env):
    p = subprocess.run([sys.executable, str(SESSION)] + list(args), cwd=str(cwd or P),
                       env=_env(H, **env), capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=120)
    return p.returncode, p.stdout + p.stderr


def state_text(P):
    return (P / ".aid" / "state.json").read_text(encoding="utf-8")


def state_of(P):
    return json.loads(state_text(P))


def leaky_note():
    """An e-mail, a token built at run time (never a literal in the repo) and an absolute path."""
    token = "ghp_" + "a1B2" * 9
    return token, "ok jane.doe@acme.example {} see C:/Users/jane/secret/notes.txt rating 4".format(token)


# ---------------------------------------------------------------------------
# T15-12: review / approve / qa-pass notes are redacted
# ---------------------------------------------------------------------------

def _assert_clean(text, token):
    low = text.lower()
    assert "jane.doe@acme.example" not in low and token.lower() not in low
    assert "c:/users/jane" not in low.replace("\\", "/")


def test_t15_12_review_note_is_redacted(proj):
    P, H = proj
    assert sess(P, H, "init", "developer", "2")[0] == 0
    token, note = leaky_note()
    rc, out = sess(P, H, "review", "2", "PASS", "--note", note)
    assert rc == 0, out
    _assert_clean(state_text(P), token)
    assert "rating 4" in state_of(P)["subagent_review"]["phase_2"]["note"]


def test_t15_12_approve_note_is_redacted(proj):
    P, H = proj
    assert sess(P, H, "init", "developer", "2")[0] == 0
    token, note = leaky_note()
    rc, out = sess(P, H, "approve", "--note", note)
    assert rc == 0, out
    _assert_clean(state_text(P), token)
    assert "rating 4" in state_of(P)["phase_approval_note"]


def test_t15_12_qa_pass_note_is_redacted(proj):
    P, H = proj
    assert sess(P, H, "init", "developer", "4")[0] == 0
    (P / ".aid" / "qa").mkdir()
    (P / ".aid" / "qa" / "T-2.yaml").write_text("criteria:\n  - works\n", encoding="utf-8")
    token, note = leaky_note()
    rc, out = sess(P, H, "qa-pass", "T-2", "--note", note)
    assert rc == 0, out
    _assert_clean(state_text(P), token)
    assert "rating 4" in state_of(P)["qa_passed"]["T-2"]["note"]


# ---------------------------------------------------------------------------
# T15-13: reset
# ---------------------------------------------------------------------------

def _seed(aid):
    (aid / "feedback" / "pending").mkdir(parents=True)
    (aid / "feedback" / "pending" / "x.json").write_text("{}", encoding="utf-8")
    (aid / "recommendations").mkdir()
    (aid / "recommendations" / "queue.json").write_text("[]", encoding="utf-8")
    (aid / "metrics").mkdir()
    (aid / "memory").mkdir()
    (aid / "memory" / "slots.json").write_text("{}", encoding="utf-8")
    (aid / "integrity" / "abc").mkdir(parents=True)
    (aid / "state.json").write_text("{}", encoding="utf-8")
    (aid / "notes.txt").write_text("mine", encoding="utf-8")


def _names(aid):
    return sorted(p.name for p in aid.iterdir())


def test_t15_13_reset_keeps_memory_integrity_and_unknown(proj):
    P, H = proj
    aid = H / ".aid"
    _seed(aid)
    rc, out = sess(P, H, "reset")
    assert rc == 0, out
    assert _names(aid) == ["integrity", "memory", "notes.txt"], out
    assert (aid / "integrity" / "abc").is_dir() and (aid / "memory" / "slots.json").is_file()
    assert "kept" in out and "notes.txt" in out
    assert (P / ".aid" / "hooks" / "config.json").is_file()      # project .aid untouched


def test_t15_13_reset_all_also_removes_memory_never_integrity(proj):
    P, H = proj
    aid = H / ".aid"
    _seed(aid)
    rc, out = sess(P, H, "reset", "--all")
    assert rc == 0, out
    assert _names(aid) == ["integrity", "notes.txt"], out
    assert (aid / "integrity" / "abc").is_dir()


def test_t15_13_reset_rejects_abbreviations(proj):
    P, H = proj
    aid = H / ".aid"
    _seed(aid)
    rc, out = sess(P, H, "reset", "--al")
    assert rc != 0 and "--al" in out and "invalid choice" not in out, out
    assert "memory" in _names(aid) and "feedback" in _names(aid)


@pytest.mark.parametrize("where", ["home", "root", "project"])
def test_t15_13_reset_refuses_dangerous_aid_home(proj, where):
    P, H = proj
    _seed(H / ".aid")
    (H / "state.json").write_text("{}", encoding="utf-8")
    (P / "state.json").write_text("{}", encoding="utf-8")
    target = {"home": H, "root": Path(H.anchor), "project": P}[where]
    rc, out = sess(P, H, "reset", "--all", AID_HOME=str(target))
    assert rc != 0 and "refused" in out, out
    assert (H / "state.json").is_file() and (P / "state.json").is_file()
    assert _names(H / ".aid") == ["feedback", "integrity", "memory", "metrics", "notes.txt",
                                  "recommendations", "state.json"]


@pytest.mark.parametrize("inner", [".aid", "sub/aidhome"])
def test_t15_13_reset_refuses_aid_home_inside_a_project(proj, inner):
    """R1-C3 (I-2: reset never touches a project .aid/): an AID_HOME at <P>/.aid or
    anywhere under the AID project <P> is refused and nothing is deleted."""
    P, H = proj
    (P / ".aid" / "state.json").write_text("{}", encoding="utf-8")
    (P / ".aid" / "feedback").mkdir()
    target = P / inner
    target.mkdir(parents=True, exist_ok=True)
    (target / "state.json").write_text("{}", encoding="utf-8")
    for cwd in (P, H):
        rc, out = sess(P, H, "reset", "--all", cwd=cwd, AID_HOME=str(target))
        assert rc != 0 and "refused" in out, (cwd, out)
        assert (P / ".aid" / "state.json").is_file() and (P / ".aid" / "feedback").is_dir()
        assert (target / "state.json").is_file()


def _dir_link(link, target):
    try:
        os.symlink(str(target), str(link), target_is_directory=True)
    except (OSError, NotImplementedError):
        if os.name != "nt":
            raise
        import _winapi
        _winapi.CreateJunction(str(target), str(link))


def test_t15_13_reset_unlinks_links_without_following(proj, tmp_path):
    P, H = proj
    aid = H / ".aid"
    aid.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "keep.txt").write_text("precious", encoding="utf-8")
    _dir_link(aid / "feedback", outside)
    rc, out = sess(P, H, "reset")
    assert rc == 0, out
    assert not os.path.lexists(str(aid / "feedback"))
    assert (outside / "keep.txt").read_text(encoding="utf-8") == "precious"


# ---------------------------------------------------------------------------
# T15-14: qa-pass
# ---------------------------------------------------------------------------

def _qa_yaml(P, task="T-2", body="criteria:\n  - works\n"):
    (P / ".aid" / "qa").mkdir(parents=True, exist_ok=True)
    f = P / ".aid" / "qa" / (task + ".yaml")
    f.write_bytes(body.encode("utf-8"))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def test_t15_14_qa_pass_records_the_criteria_hash(proj):
    P, H = proj
    assert sess(P, H, "init", "developer", "4")[0] == 0
    digest = _qa_yaml(P)
    rc, out = sess(P, H, "qa-pass", "T-2", "--note", "ok")
    assert rc == 0, out
    rec = state_of(P)["qa_passed"]["T-2"]
    assert rec["criteria_sha256"] == digest and rec["note"] == "ok" and rec["at"]


def test_t15_14_qa_pass_refused_before_phase_4(proj):
    P, H = proj
    assert sess(P, H, "init", "developer", "3")[0] == 0
    _qa_yaml(P)
    before = state_text(P)
    rc, out = sess(P, H, "qa-pass", "T-2")
    assert rc != 0 and state_text(P) == before, out
    assert "invalid choice" not in out, out        # refused by qa-pass, not an unknown command


def test_t15_14_qa_pass_refused_without_criteria(proj):
    P, H = proj
    assert sess(P, H, "init", "developer", "4")[0] == 0
    before = state_text(P)
    rc, out = sess(P, H, "qa-pass", "T-2")
    assert rc != 0 and state_text(P) == before, out
    assert "invalid choice" not in out, out        # refused by qa-pass, not an unknown command


@pytest.mark.parametrize("bad", ["../x", "a/b", "-x", "a" * 65, "a..b"])
def test_t15_14_qa_pass_rejects_bad_task_ids(proj, bad):
    P, H = proj
    assert sess(P, H, "init", "developer", "4")[0] == 0
    _qa_yaml(P)
    before = state_text(P)
    rc, out = sess(P, H, "qa-pass", bad)
    assert rc != 0 and state_text(P) == before, out
    assert "invalid choice" not in out, out        # refused by qa-pass, not an unknown command


def test_t15_14_qa_pass_from_a_subfolder_writes_the_project_state(proj):
    P, H = proj
    assert sess(P, H, "init", "developer", "4")[0] == 0
    digest = _qa_yaml(P)
    (P / "docs").mkdir()
    rc, out = sess(P, H, "qa-pass", "T-2", cwd=P / "docs")
    assert rc == 0, out
    assert state_of(P)["qa_passed"]["T-2"]["criteria_sha256"] == digest
    assert not (P / "docs" / ".aid").exists()


# ---------------------------------------------------------------------------
# T15-15 / T15-16: the QA Stop gate
# ---------------------------------------------------------------------------

def gate(P, H, payload=None, cwd=None):
    p = subprocess.run([sys.executable, str(QA_HOOK)], input=json.dumps(payload or {"cwd": str(cwd or P)}),
                       capture_output=True, text=True, timeout=60, cwd=str(cwd or P), env=_env(H),
                       encoding="utf-8", errors="replace")
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout) if p.stdout.strip() else {}


def _gate_project(P, task=None, phase=4, state_extra=None):
    state = {"current_phase": phase}
    state.update(state_extra or {})
    (P / ".aid" / "state.json").write_text(json.dumps(state), encoding="utf-8")
    (P / ".aid" / "context.json").write_text(
        json.dumps({"current_task": task if task is not None else {"id": "T-2"}}), encoding="utf-8")
    return _qa_yaml(P)


@pytest.mark.parametrize("field", ["id", "key", "jira_key"])
def test_t15_15_gate_blocks_for_each_task_field(proj, field):
    P, H = proj
    _gate_project(P, {field: "T-2"})
    assert gate(P, H).get("decision") == "block"


def test_t15_15_gate_allows_only_a_matching_qa_passed_record(proj):
    P, H = proj
    digest = _gate_project(P, state_extra={"qa_passed": {"T-2": {"criteria_sha256": "0" * 64}}})
    assert gate(P, H).get("decision") == "block"          # stale / wrong hash
    _gate_project(P, state_extra={"qa_passed": {"T-2": {"criteria_sha256": digest}}})
    assert gate(P, H) == {}
    _qa_yaml(P, body="criteria:\n  - works\n  - and more\n")   # criteria changed
    assert gate(P, H).get("decision") == "block"


def test_t15_15_gate_allows_after_the_confirmed_qa_pass(proj):
    """End to end: the writer the reason names is what opens the gate."""
    P, H = proj
    assert sess(P, H, "init", "developer", "4")[0] == 0
    (P / ".aid" / "context.json").write_text(json.dumps({"current_task": {"id": "T-2"}}), encoding="utf-8")
    _qa_yaml(P)
    assert gate(P, H).get("decision") == "block"
    assert sess(P, H, "qa-pass", "T-2", "--note", "ok")[0] == 0
    assert gate(P, H) == {}


def test_t15_15_marker_files_do_not_pass(proj):
    P, H = proj
    _gate_project(P, state_extra={"current_task_qa": {"task_id": "T-2", "status": "passed"}})
    (P / ".aid" / "qa" / "T-2.qa-passed").write_text("", encoding="utf-8")
    (P / ".aid" / "qa" / "T-2-review.json").write_text('{"verdict":"PASS"}', encoding="utf-8")
    assert gate(P, H).get("decision") == "block"


def test_t15_15_reason_names_the_qa_pass_command_and_no_marker(proj):
    P, H = proj
    _gate_project(P)
    reason = gate(P, H)["reason"]
    script = SESSION.as_posix()
    assert 'python "{}" qa-pass T-2 --note "<short summary>"'.format(script) in reason, reason
    low = reason.lower()
    assert "write the verdict" not in low
    assert ".qa-passed" not in low and "-review" not in low
    assert not re.search(r"(write|create|save)[^\n]*\.aid/qa", low), reason


def test_t15_15_reason_states_the_note_charset_with_a_canonical_example(proj):
    """R1-C4: the note must match the canonical `"[A-Za-z0-9 ._:-]+"` form, so the reason
    says so and its example note is itself canonical (a natural summary with , / ( '
    would be denied as non-canonical and leave the agent stuck)."""
    P, H = proj
    _gate_project(P)
    reason = gate(P, H)["reason"]
    assert "letters" in reason and "digits" in reason and ". _ : -" in reason, reason
    m = re.search(r'for example:\s*--note "([^"]*)"', reason)
    assert m, reason
    assert re.fullmatch(r"[A-Za-z0-9 ._:-]+", m.group(1)), m.group(1)


def test_t15_15_unchanged_rules(proj):
    """Loop guard, Phase-4-only, null task and T7-7 root anchoring stay as they were."""
    P, H = proj
    _gate_project(P)
    assert gate(P, H, {"stop_hook_active": True, "cwd": str(P)}) == {}
    _gate_project(P, phase=5)
    assert gate(P, H) == {}
    _gate_project(P, phase=4)
    (P / ".aid" / "context.json").write_text('{"current_task": null}', encoding="utf-8")
    assert gate(P, H) == {}
    (P / ".aid" / "context.json").write_text('{"current_task": {"id": "T-2"}}', encoding="utf-8")
    (P / "docs").mkdir()
    assert gate(P, H, cwd=P / "docs").get("decision") == "block"
    assert not (P / "docs" / ".aid").exists()


def test_t15_16_no_bare_except():
    src = QA_HOOK.read_text(encoding="utf-8")
    assert not re.search(r"except\s*:", src)


@pytest.mark.parametrize("content", ["{not json", "[1, 2]"])
def test_t15_16_bad_state_blocks(proj, content):
    P, H = proj
    _gate_project(P)
    (P / ".aid" / "state.json").write_text(content, encoding="utf-8")
    out = gate(P, H)
    assert out.get("decision") == "block", out
    assert "state.json" in out["reason"] and "init --repair" in out["reason"]


@pytest.mark.parametrize("content", ["{not json", "[]", '{"current_task": "T-2"}'])
def test_t15_16_bad_context_blocks_at_phase_4(proj, content):
    P, H = proj
    _gate_project(P)
    (P / ".aid" / "context.json").write_text(content, encoding="utf-8")
    out = gate(P, H)
    assert out.get("decision") == "block", out
    assert "/context-update" in out["reason"]


@pytest.mark.parametrize("bad", ["../x", "a/b", "-x", "a" * 65])
def test_t15_16_bad_task_id_blocks(proj, bad):
    P, H = proj
    _gate_project(P, {"id": bad})
    out = gate(P, H)
    assert out.get("decision") == "block", out


def test_t15_16_missing_files_and_no_root_unchanged(proj, tmp_path):
    P, H = proj                       # AID root (hooks/config.json), no state, no context
    assert gate(P, H) == {}
    E = tmp_path / "empty"
    E.mkdir()
    assert gate(E, H) == {}
    assert list(E.iterdir()) == []


# ---------------------------------------------------------------------------
# T15-17: memory-queue reports both skip reasons
# ---------------------------------------------------------------------------

def test_t15_17_memory_queue_reports_empty_content_separately(proj):
    P, H = proj
    f = P / ".aid" / "improve" / "proposals.json"
    f.parent.mkdir(parents=True)
    f.write_text(json.dumps({"suggestions": [
        {"target": {"file": ALLOWED_TARGET}, "content": "   "},
        {"target": {"file": "skills/aid-prd/SKILL.md"}, "content": "rewrite"}]}), encoding="utf-8")
    rc, out = sess(P, H, "memory-queue")
    assert rc == 0, out
    lines = out.splitlines()
    not_allowed = [l for l in lines if l.startswith("Not queued, target is not an allowed")]
    empty = [l for l in lines if l.startswith("Not queued, empty content:")]
    assert len(not_allowed) == 1 and "SKILL.md" in not_allowed[0], out
    assert "cumulative.md" not in not_allowed[0], out
    assert len(empty) == 1 and "cumulative.md" in empty[0], out
