"""T20 #3 (gate run 4 L4-04f): stored memory and queued proposals are redacted when SHOWN.

Memory written by 3.0.7 (before redaction) or edited by hand sits raw on disk. The CLI
(--memories, --pending, markdown and json) and aid_session.py memory-preview put it into
Claude's context, so each display passes it through memory_system.redact. Disk is unchanged.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

MS = Path(__file__).resolve().parents[1]
REPO = MS.parent

# Built at run time: no secret-shaped literal in the source.
SECRET = "gh" + "p_" + "Ab3dEf6hIj9kLm2nOp5qRs8tUv1wXy4zAb7c"
EMAIL = "legacy.user" + "@" + "example.org"
RAW = "Prefers short answers; contact {} with key {}".format(EMAIL, SECRET)


def _plant(aid_home):
    mem = aid_home / "memory"
    mem.mkdir(parents=True)
    (mem / "slots.json").write_text(json.dumps({"user_preferences": [
        {"content": RAW, "added_at": "2025-01-01T00:00:00Z", "metadata": {}}]}), encoding="utf-8")
    rec = aid_home / "recommendations"
    rec.mkdir(parents=True)
    (rec / "queue.json").write_text(json.dumps([{
        "id": "a1b2c3d4e5f60718", "priority": "high", "target_skill": "memory-system",
        "target_file": "skills/memory-system/references/learnings.md", "section": "Notes",
        "proposed_change": RAW, "rationale": RAW}]), encoding="utf-8")
    return [mem / "slots.json", rec / "queue.json"]


def _run(aid_home, argv):
    env = dict(os.environ, AID_HOME=str(aid_home), HOME=str(aid_home.parent),
               USERPROFILE=str(aid_home.parent), PYTHONPATH=str(MS), PYTHONIOENCODING="utf-8")
    env.pop("CLAUDE_PROJECT_DIR", None)
    p = subprocess.run([sys.executable, *argv], cwd=str(aid_home.parent), env=env,
                       capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert p.returncode == 0, p.stderr
    return p.stdout


CASES = {
    "memories-md": ["-m", "memory_system", "--memories"],
    "memories-json": ["-m", "memory_system", "--memories", "--format", "json"],
    "pending-md": ["-m", "memory_system", "--pending"],
    "pending-json": ["-m", "memory_system", "--pending", "--format", "json"],
    "memory-preview": [str(REPO / "hooks" / "aid_session.py"), "memory-preview"],
    # cycle 1: the JSON reports also carry the queue (pending_recommendations / pending_queue)
    "analyze-json": ["-m", "memory_system", "--analyze", "--format", "json"],
    "dashboard-json": ["-m", "memory_system", "--dashboard", "--format", "json"],
    "recommendations-json": ["-m", "memory_system", "--recommendations", "--format", "json"],
}
QUEUE_ONLY = {"analyze-json", "dashboard-json", "recommendations-json"}


def _plant_feedback():
    """Without feedback these reports return early and never show the queue."""
    from memory_system.feedback.collector import create_feedback_entry, save_feedback_entry
    for i in range(4):
        save_feedback_entry(create_feedback_entry(
            "s{}".format(i), "4-development", "developer", "decision",
            decision={"topic": "t", "chosen": "a", "alternatives": ["b"], "rationale": "r"},
            feedback={"rating": 3, "verbal": "ok"}))


@pytest.mark.parametrize("case", sorted(CASES))
def test_t20_3_displayed_memory_is_redacted(aid_home, case):
    files = _plant(aid_home)
    if case in QUEUE_ONLY:
        _plant_feedback()
    before = [f.read_bytes() for f in files]
    out = _run(aid_home, CASES[case])
    if case.endswith("json"):
        json.loads(out)                     # still one JSON document
    assert "Prefers short answers" in out   # the entry is shown ...
    assert SECRET not in out and EMAIL not in out
    assert "[token]" in out and "[email]" in out   # ... with placeholders
    if case == "recommendations-json":    # it appends new proposals; the planted one stays as is
        assert files[0].read_bytes() == before[0]
        assert json.loads(files[1].read_text(encoding="utf-8"))[0] == json.loads(before[1])[0]
    else:
        assert [f.read_bytes() for f in files] == before   # disk unchanged
