"""
WHY THIS TEST (T8-3, T8-4): three writers produced three shapes, and the readers knew one.
/aid-end ratings were never counted, the hand-written shape crashed every command, and
generated recommendations were never queued.
"""
import json

from memory_system.feedback import collector
from memory_system.feedback.schema import normalize_entry
from memory_system.recommendations import generator

A = {"timestamp": "2026-11-18T10:00:00Z", "role": "developer", "phase": 2,
     "phase_display": "Technical Design", "rating": 4, "worked_well": "ping a@b.io",
     "to_improve": "more NFRs", "duration_minutes": 3}
D = {"context": {"role": "qa", "phase": "prd"}, "metrics": {"rating": 2},
     "qualitative": {"what_worked": "clear", "what_didnt": "verbose"}}
C = {"id": "abc", "timestamp": "2026-11-18T09:00:00Z", "session_id": "s1",
     "context": {"phase": "2-tech-spec", "role": "pm", "interaction_type": "decision"},
     "feedback": {"rating": 5, "verbal": "great", "skipped": False}}


def test_all_three_shapes_normalise_to_one():
    a, d, c = normalize_entry(A), normalize_entry(D), normalize_entry(C)
    assert (a["feedback"]["rating"], a["context"]["role"], a["context"]["phase"]) == (4, "developer", "Technical Design")
    assert "[email]" in a["feedback"]["verbal"] and "a@b.io" not in json.dumps(a)
    assert (d["feedback"]["rating"], d["context"]["role"]) == (2, "qa") and d["timestamp"]
    assert c["feedback"]["rating"] == 5 and c["id"] == "abc" and c["session_id"] == "s1"
    for e in (a, d, c):
        assert {"id", "timestamp", "session_id", "context", "feedback", "debate"} <= set(e)


def test_phase_approve_entry_is_a_phase_gate_rating():
    e = normalize_entry({"source": "phase-approve", "timestamp": "2026-11-18T10:00:00Z",
                         "role": "pm", "phase": 1, "rating": 4, "note": "rating 4 clear scope"})
    assert e["feedback"]["rating"] == 4 and e["context"]["interaction_type"] == "phase-gate"


def test_readers_count_every_shape_and_skip_garbage(aid_home):
    pend = aid_home / "feedback" / "pending"
    pend.mkdir(parents=True)
    for name, data in (("a", A), ("d", D), ("c", C)):
        (pend / f"{name}.json").write_text(json.dumps(data), encoding="utf-8")
    (pend / "bad.json").write_text("{not json", encoding="utf-8")
    entries = collector.load_pending_feedback()
    assert sorted(e["feedback"]["rating"] for e in entries) == [2, 4, 5]
    assert collector.get_feedback_stats()["total_entries"] == 4
    assert collector.load_feedback_by_session("s1")[0]["id"] == "abc"
    assert collector.mark_feedback_processed("a") and not (pend / "a.json").exists()


def test_saved_entries_are_redacted_before_they_are_written(aid_home):
    entry = collector.create_feedback_entry("s", "1", "pm", "decision",
                                            feedback={"rating": 3, "verbal": "mail x@y.io"})
    path = collector.save_feedback_entry(entry)
    assert "x@y.io" not in path.read_text(encoding="utf-8")


def _rec(target_skill="role-pm", change="Prefer business impact"):
    gen = generator.RecommendationGenerator({}, {}, [])
    return gen._create_recommendation("high", target_skill, "Role", "cur", change, "why", {})


def test_queue_dedupes_by_id_and_pending_lists_it(aid_home):
    generator.save_recommendations([_rec(), _rec()])
    generator.save_recommendations([_rec()])
    assert len(generator.load_recommendation_queue()) == 1


def test_apply_appends_only_to_an_allowed_learnings_file(aid_home, tmp_path):
    refs = tmp_path / "refs"
    (refs / "roles" / "product-manager").mkdir(parents=True)
    target = refs / "roles" / "product-manager" / "cumulative.md"
    target.write_text("# PM\n", encoding="utf-8")
    rec = _rec(change="Lead with impact, mail boss@corp.io")
    generator.save_recommendations([rec, _rec("learning-mode", "x")])
    result = generator.apply_recommendation(rec["id"][:8], refs_root=refs)
    assert result["ok"], result
    text = target.read_text(encoding="utf-8")
    assert "Lead with impact" in text and "boss@corp.io" not in text
    other = generator.load_recommendation_queue()[0]
    assert not generator.apply_recommendation(other["id"], refs_root=refs)["ok"]  # no target
    assert not generator.apply_recommendation("nope-nope", refs_root=refs)["ok"]


def test_targets_outside_the_allow_list_are_refused(tmp_path):
    refs = tmp_path / "refs"
    (refs / "roles" / "developer").mkdir(parents=True)
    (refs / "roles" / "developer" / "cumulative.md").write_text("x", encoding="utf-8")
    (refs / "roles" / "developer" / "SKILL.md").write_text("x", encoding="utf-8")
    assert generator.resolve_target("roles/developer/cumulative.md", refs)
    for bad in ("../x/cumulative.md", "roles/../../x/cumulative.md", "roles/developer/SKILL.md",
                str(refs / "roles" / "developer" / "cumulative.md"), "hooks/aid_guard.py",
                "roles/nobody/cumulative.md", None, 3):
        assert generator.resolve_target(bad, refs) is None, bad


def test_reject_moves_to_rejected_and_is_not_requeued(aid_home):
    rec = _rec()
    generator.save_recommendations([rec])
    assert generator.reject_recommendation(rec["id"])
    generator.save_recommendations([rec])
    assert generator.load_recommendation_queue() == []
