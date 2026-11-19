"""
WHY THESE TESTS (T15-26..T15-30, release gate 3.0.8):
- L3-4c: two memory-sync runs duplicated every entry and filled the limited slots.
- L3-2g: --format json was accepted by every operation but honoured by two.
- L3-1e: path redaction swallowed the comma or period after a path.
- L3-4e: an allowed target with empty content was reported as "not an allowed file".
- item 36: the content id was SHA-1 cut to 64 bits; the docs named paths that do not exist.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

from memory_system.analysis import memory_sync
from memory_system.recommendations import generator
from memory_system.redact import redact

MS = Path(__file__).resolve().parents[1]          # memory-system/
REPO = MS.parent
ALLOWED = "skills/memory-system/references/roles/developer/cumulative.md"


def _seed_feedback(aid_home, n=5):
    """Feedback that makes the pattern detector propose memory entries."""
    pend = aid_home / "feedback" / "pending"
    pend.mkdir(parents=True, exist_ok=True)
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    for i in range(n):
        (pend / "fb{}.json".format(i)).write_text(json.dumps({
            "id": "fb-{}".format(i), "timestamp": now, "session_id": "s{}".format(i),
            "context": {"phase": "2-tech-spec", "role": "pm", "interaction_type": "decision"},
            "decision": {"topic": "db", "topic_category": "technology", "chosen": "pg"},
            "debate": {"occurred": True, "outcome": "changed", "learning": "prefers managed services"},
            "feedback": {"rating": 2, "verbal": "too verbose, be brief"}}), encoding="utf-8")


def _usage():
    return {c: u["used"] for c, u in memory_sync.get_current_memories()["usage"].items()}


# --------------------------------------------------------------------------- T15-26
def test_t15_26_second_sync_adds_nothing(aid_home):
    _seed_feedback(aid_home)
    first = memory_sync.sync_memory_from_feedback(approve=True)
    assert first.get("synced") and first["memories_added"], first
    counts = _usage()
    second = memory_sync.sync_memory_from_feedback(approve=True)
    assert second.get("memories_added", []) == [], second
    assert _usage() == counts
    # The dry run (memory-preview) plans nothing either.
    assert memory_sync.sync_memory_from_feedback(approve=False)["planned"] == []


def test_t15_26_add_memory_skips_normalised_duplicate(aid_home):
    mgr = memory_sync.MemorySlotManager()
    assert mgr.add_memory("context", "User prefers  short answers") is True
    assert mgr.add_memory("context", "user PREFERS short\tanswers ") is False
    assert mgr.add_memory("user_preferences", "User prefers short answers") is True
    assert len(mgr.get_memories("context")) == 1


def test_t15_26_plan_excludes_entries_already_in_memory(aid_home):
    _seed_feedback(aid_home)
    engine = memory_sync.MemorySyncEngine()
    planned = engine.plan()
    assert planned
    keys = [(p["category"], " ".join(p["content"].casefold().split())) for p in planned]
    assert len(keys) == len(set(keys)), "the plan itself holds no duplicates"
    first = planned[0]
    engine.slot_manager.add_memory(first["category"], first["content"].upper())
    assert all(p["content"] != first["content"] for p in engine.plan())


# --------------------------------------------------------------------------- T15-27
JSON_FLAGS = ["--status", "--pending", "--recommendations", "--memories", "--sync-memory",
              "--analyze", "--dashboard", "--stats"]


def _cli(aid_home, *flags):
    env = dict(os.environ, AID_HOME=str(aid_home), HOME=str(aid_home.parent),
               USERPROFILE=str(aid_home.parent), PYTHONPATH=str(MS), PYTHONIOENCODING="utf-8")
    env.pop("CLAUDE_PROJECT_DIR", None)
    p = subprocess.run([sys.executable, "-m", "memory_system", *flags], cwd=str(aid_home.parent),
                       env=env, capture_output=True, text=True, encoding="utf-8", timeout=120)
    return p.returncode, p.stdout, p.stderr


@pytest.mark.parametrize("seed", [False, True], ids=["empty", "with-feedback"])
@pytest.mark.parametrize("flag", JSON_FLAGS)
def test_t15_27_format_json_prints_one_document(aid_home, flag, seed):
    if seed:
        _seed_feedback(aid_home)
    rc, out, err = _cli(aid_home, flag, "--format", "json")
    assert rc == 0, err
    doc = json.loads(out)                       # the WHOLE output, no banner
    assert isinstance(doc, (dict, list))


def test_t15_27_dashboard_save_json_names_the_file(aid_home):
    _seed_feedback(aid_home)
    rc, out, err = _cli(aid_home, "--dashboard", "--save", "--format", "json")
    assert rc == 0, err
    assert Path(json.loads(out)["saved_to"]).is_file()


def test_t15_27_text_output_unchanged(aid_home):
    for flag, head in (("--status", "Sub-Agent Status"), ("--pending", "Pending Recommendations"),
                       ("--sync-memory", "Memory sync preview"), ("--analyze", "Running quality analysis")):
        rc, out, err = _cli(aid_home, flag)
        assert rc == 0 and out.startswith(head), (flag, out, err)


# --------------------------------------------------------------------------- T15-28
@pytest.mark.parametrize("text, want", [
    ("see C:/Users/jane/secret/notes.txt, rating 4", "see [path], rating 4"),
    ("at /home/u/a.txt.", "at [path]."),
    ("(see /home/u/a.txt)", "(see [path])"),
    ("x ~/notes/a.md; then", "x [path]; then"),
    (r"in C:\Users\jane\x.py: done", "in [path]: done"),
])
def test_t15_28_path_keeps_trailing_punctuation(text, want):
    assert redact(text) == want
    assert redact(want) == want                 # still idempotent


# --------------------------------------------------------------------------- T15-29
def test_t15_29_two_skip_reasons(aid_home):
    res = generator.queue_proposals({"suggestions": [
        {"target": {"file": ALLOWED}, "content": "   "},
        {"target": {"file": "../../etc/passwd"}, "content": "x"},
        {"target": {"file": ALLOWED}, "content": "Ask for NFRs early"},
    ]})
    assert res["skipped_empty"] == [ALLOWED]
    assert res["skipped_targets"] == ["../../etc/passwd"]
    assert len(res["queued"]) == 1


# --------------------------------------------------------------------------- T15-30
def _rec(text="Ask for NFRs early"):
    return {"target_skill": "memory-system", "target_file": "roles/developer/cumulative.md",
            "section": "Learnings", "proposed_change": text, "rationale": "r"}


def test_t15_30_content_id_is_sha256_32_hex():
    rid = generator._content_id(_rec())
    assert re.fullmatch(r"[0-9a-f]{32,}", rid)
    key = "|".join(str(_rec().get(k)) for k in
                   ("target_skill", "target_file", "section", "proposed_change", "rationale"))
    assert hashlib.sha256(key.encode("utf-8")).hexdigest().startswith(rid)


def _legacy_id(rec):
    key = "|".join(str(rec.get(k)) for k in
                   ("target_skill", "target_file", "section", "proposed_change", "rationale"))
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]


def _queue_legacy(aid_home, rec):
    rec = dict(rec, id=_legacy_id(rec), status="pending", priority="low")
    q = aid_home / "recommendations" / "queue.json"
    q.parent.mkdir(parents=True, exist_ok=True)
    q.write_text(json.dumps([rec]), encoding="utf-8")
    return rec["id"]


def test_t15_30_old_ids_still_apply(aid_home, tmp_path):
    refs = tmp_path / "refs"
    target = refs / "roles" / "developer" / "cumulative.md"
    target.parent.mkdir(parents=True)
    target.write_text("# Learnings\n", encoding="utf-8")
    old = _queue_legacy(aid_home, _rec())
    res = generator.apply_recommendation(old, refs_root=refs)
    assert res["ok"], res
    assert "Ask for NFRs early" in target.read_text(encoding="utf-8")


def test_t15_30_old_ids_still_reject_and_are_not_requeued(aid_home):
    old = _queue_legacy(aid_home, _rec("other text"))
    assert generator.reject_recommendation(old) is True
    assert generator.load_recommendation_queue() == []
    new = dict(_rec("other text"), id=generator._content_id(_rec("other text")))
    generator.save_recommendations([new])
    assert generator.load_recommendation_queue() == [], "rejected under its old id"


_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
_DANGLING = ("memory-system/skills/", "~/.aid/skills", "/aid improve")


def _md_files():
    return sorted(MS.rglob("*.md")) + sorted((REPO / "docs").glob("*.md"))


def test_t15_30_doc_references_resolve():
    bad = []
    for f in _md_files():
        text = f.read_text(encoding="utf-8")
        for m in _LINK.finditer(re.sub(r"```.*?```", "", text, flags=re.S)):
            target = m.group(1).split("#")[0]
            if target and not re.match(r"^[a-z][a-z0-9+.-]*:", target) and not (f.parent / target).exists():
                bad.append("{}: link {}".format(f.relative_to(REPO), m.group(1)))
        if f.is_relative_to(MS):
            bad += ["{}: {}".format(f.relative_to(REPO), d) for d in _DANGLING if d in text]
            # Every repo path into the memory-system references names a real file or folder.
            for p in re.findall(r"skills/memory-system/references/[\w./{}*-]*", text):
                p = p.rstrip(".`")
                p = p.replace("{role}", "developer").replace("{phase}", "prd")
                if "*" in p:
                    hits = list(REPO.glob(p))
                else:
                    hits = [REPO / p] if (REPO / p).exists() else []
                if not hits:
                    bad.append("{}: {}".format(f.relative_to(REPO), p))
    assert bad == []


def test_t15_30_migration_does_not_promise_automatic_updates():
    text = (MS / "docs" / "MIGRATION.md").read_text(encoding="utf-8")
    assert "automatically updated" not in text.lower()


def _reset_section():
    text = (MS / "docs" / "COMMANDS.md").read_text(encoding="utf-8")
    start = text.index('<a id="reset"></a>')
    end = text.find("\n## ", start)
    return text[start:end if end != -1 else len(text)]


def test_t15_30_commands_reset_anchor_describes_aid_session_reset():
    """
    WHY THIS TEST:
    - PROBLEM: commands/aid-reset.md links to COMMANDS.md#reset, which had no such anchor and
      described a manual "Type RESET" deletion that keeps nothing safe.
    - SUCCESS: the anchor exists and the section describes `aid_session.py reset [--all]`,
      keeping memory/ unless --all and never touching integrity/ or the project .aid/.
    """
    link = (REPO / "commands" / "aid-reset.md").read_text(encoding="utf-8")
    assert "COMMANDS.md#reset" in link
    sec = _reset_section()
    assert 'aid_session.py" reset' in sec and "reset --all" in sec
    assert "integrity/" in sec and "never" in sec.lower()
    assert ".aid/" in sec and "memory/" in sec
    assert "Type 'RESET'" not in sec
    # Every entry the command deletes is named in the doc.
    src = (REPO / "hooks" / "aid_session.py").read_text(encoding="utf-8")
    m = re.search(r"^RESET_ENTRIES = \(([^)]*)\)", src, re.M)
    assert m, "RESET_ENTRIES not found in hooks/aid_session.py"
    for name in re.findall(r'"([^"]+)"', m.group(1)):
        assert "`{}".format(name) in sec, name


def test_t15_30_docs_never_tell_the_agent_to_write_state_json():
    """
    WHY THIS TEST:
    - PROBLEM: INTEGRATION.md ("4. Update state.json") and AGENT.md ("# Update state.json"
      then save(state)) told the agent to write .aid/state.json itself. That file is
      protected: only aid_session.py writes it, so following the doc gets a denied write.
    - SUCCESS: neither doc tells the agent to update state.json; both name
      `aid_session.py start` as the writer.
    """
    for rel in ("memory-system/INTEGRATION.md", "memory-system/docs/AGENT.md"):
        text = (REPO / rel).read_text(encoding="utf-8")
        assert not re.search(r"^\s*(?:\d+\.\s*|#\s*)Update state\.json", text, re.M), rel
        assert "aid_session.py start" in text, rel
