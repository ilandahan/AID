"""
T17 WS-B memory-system tests (reports/T17-acceptance.md T17-14, T17-18, T17-19).

WHY THESE TESTS:
- PROBLEM: the redactor missed JSON-quoted secret names, CLI-flag secrets, `mysql -p<V>`,
  `curl -u user:pass` and credentials in non-http URLs (audit R-06, R-07), so such values
  reached pending feedback and memory verbatim. Recommendations targeted skills that do not
  exist ("aid-spec", "role-pm") and could never be applied (L3c-2d); the dashboard showed a
  made-up "Debate Rate: 100%" with no decision data (L3c-2e).
- COST OF FAILURE: a database password or token persisted in ~/.aid and copied into memory;
  a learning loop that queues dead proposals; a misleading quality metric.
- SUCCESS: every I-20 form is redacted on write and on read, the negatives are untouched, the
  redactor stays linear; every generated proposal names a real skill and an allowed file;
  "n/a" without data.

Secret-shaped values are built at run time with "".join([...]) (U-17: no constant-folded
literal in the .pyc).
"""
import json
import time
from pathlib import Path

import pytest

from memory_system.redact import redact
from memory_system.feedback import collector
from memory_system.recommendations import generator
from memory_system.analysis import dashboard as dashboard_mod

REPO = Path(__file__).resolve().parents[2]


def _v():
    """A secret-shaped value, built at run time."""
    return "".join(["s3", "Cr", "et", "Va", "lue", "9x"])


def _i20_cases(v):
    """(input, expected) pairs: every I-20 example from the contract."""
    return [
        # rule 7: any URL scheme with userinfo
        ("psql postgres://u:" + v + "@db/x", "psql [url]"),
        ("postgresql://u:" + v + "@db:5432/x", "[url]"),
        ("mysql://root:" + v + "@h/db", "[url]"),
        ("mongodb://u:" + v + "@h/db", "[url]"),
        ("mongodb+srv://u:" + v + "@cluster0.example.net/db", "[url]"),
        ("redis-cli -u redis://:" + v + "@h", "redis-cli -u [url]"),
        ("amqp://u:" + v + "@broker/vh", "[url]"),
        # rule 4: curl user:pass
        ("curl -u admin:" + v + " https://h", "curl -u admin:[token] [url]"),
        ("curl --user admin:" + v + " x", "curl --user admin:[token] x"),
        ("curl --user=admin:" + v + " x", "curl --user=admin:[token] x"),
        # rule 3: short password flags
        ("mysql -p" + v + " db", "mysql -p[token] db"),
        ("mysqldump -u root -p" + v + " db", "mysqldump -u root -p[token] db"),
        ("sshpass -p " + v + " ssh h", "sshpass -p [token] ssh h"),
        # R1-04 (fix cycle 1): attached quoted mysql values, attached and quoted sshpass values
        ("mysql -u root -p'" + v + "' db", "mysql -u root -p'[token]' db"),
        ('mysql -u root -p"' + v + '" db', 'mysql -u root -p"[token]" db'),
        ("mysqldump -p'two " + v + "' db", "mysqldump -p'[token]' db"),
        ("sshpass -p'" + v + "' ssh h", "sshpass -p'[token]' ssh h"),
        ("sshpass -p" + v + " ssh h", "sshpass -p[token] ssh h"),
        ('sshpass -p "two ' + v + '" ssh h', 'sshpass -p "[token]" ssh h'),
        # rule 2: CLI flags
        ("tool --password " + v, "tool --password [token]"),
        ("tool --password=" + v, "tool --password=[token]"),
        ("tool --token=" + v, "tool --token=[token]"),
        ("tool --api-key " + v, "tool --api-key [token]"),
        ("tool --client-secret " + v, "tool --client-secret [token]"),
        ("tool --pass " + v, "tool --pass [token]"),
        # rule 1: quoted names, quoted values with spaces
        ('{"password": "' + v + '"}', '{"password": "[token]"}'),
        ("{'api_key':'" + v + "'}", "{'api_key':'[token]'}"),
        ('"DB_PASSWORD"="' + v + '"', '"DB_PASSWORD"="[token]"'),
        ('password="two ' + v + '"', 'password="[token]"'),
        # rule 5: exact name pass
        ("pass=" + v, "pass=[token]"),
        ("PASS: " + v, "PASS: [token]"),
        # rule 6: Authorization with any scheme word
        ("Authorization: Token " + v, "Authorization: Token [token]"),
        ("Authorization: Digest " + v, "Authorization: Digest [token]"),
    ]


NEGATIVES = ["ssh -p 22 host", "psql -p 5432 db", "bypass=1", "pass_rate=0.9", "passes=3",
             "rating 4", "mysql -u root -p db"]


@pytest.mark.parametrize("i", range(len(_i20_cases("x"))))
def test_t17_14_write_path_redacts_every_i20_form(i):
    v = _v()
    text, expected = _i20_cases(v)[i]
    out = redact(text)
    assert v not in out, out
    assert out == expected
    assert redact(out) == out, "idempotent"


@pytest.mark.parametrize("text", NEGATIVES)
def test_t17_14_negatives_are_unchanged(text):
    assert redact(text) == text


def test_t17_14_read_path_redacts_old_pending_files(aid_home):
    """A pending file written before T17 (raw values) is redacted by the one reader that
    /aid-improve uses (aid_session.py memory-feedback -> load_feedback_by_date_range)."""
    v = _v()
    pending = aid_home / "feedback" / "pending"
    pending.mkdir(parents=True)
    raw = " | ".join(t for t, _ in _i20_cases(v))
    (pending / "old.json").write_text(json.dumps({
        "timestamp": "2026-11-19T10:00:00+00:00", "role": "developer", "phase": 4,
        "rating": 3, "to_improve": raw}), encoding="utf-8")
    entries = collector.load_pending_feedback()
    assert entries, "the pending entry is read"
    dumped = json.dumps(entries)
    assert v not in dumped
    assert "[token]" in dumped and "[url]" in dumped


def test_t17_14_hostile_input_is_linear():
    """100 kB of name characters (and other hostile shapes) finish well under a second."""
    for hostile in ("a" * 100_000, "a." * 50_000, "_-" * 50_000, "--" + "a" * 99_998,
                    "a:" * 50_000, 'password="' * 10_000, "mysql " * 16_000, "curl " * 20_000,
                    "--pass " * 14_000):
        t = time.perf_counter()
        redact(hostile)
        assert time.perf_counter() - t < 1.0, hostile[:20]


# ---------------------------------------------------------------------------
# T17-18: recommendations target real skills (L3c-2d)
# ---------------------------------------------------------------------------

SKILL_DIRS = {p.name for p in (REPO / "skills").iterdir() if p.is_dir()}


def _feedback(n=4, phase="tech-spec", role="developer", rating=2):
    return [{"timestamp": "2026-11-1{}T10:00:00+00:00".format(i), "role": role, "phase": phase,
             "phase_display": "Technical Design", "rating": rating, "to_improve": "unclear"}
            for i in range(n)]


@pytest.mark.parametrize("phase,skill", [(0, "aid-discovery"), (1, "aid-prd"), (2, "aid-tech-spec"),
                                         (3, "aid-impl-plan"), (4, "aid-development"),
                                         (5, "aid-qa-ship"), ("tech-spec", "aid-tech-spec"),
                                         ("2-tech-spec", "aid-tech-spec"), ("breakdown", "aid-impl-plan"),
                                         ("Technical Design", None)])
def test_t17_18_phase_maps_to_a_real_skill_dir(phase, skill):
    assert generator.phase_skill(phase) == skill
    if skill:
        assert skill in SKILL_DIRS
        assert generator.target_for(skill), skill


def test_t17_18_generated_proposals_name_real_skills_and_files(aid_home):
    from memory_system.analysis.metrics import MetricsCalculator
    from memory_system.analysis.patterns import PatternDetector
    from memory_system.feedback.schema import normalize_entry
    raw = _feedback(4, phase="tech-spec") + _feedback(4, phase=2, role="pm", rating=1) \
        + _feedback(4, phase=1, role="qa", rating=5)
    entries = [normalize_entry(r, names=()) for r in raw]
    assert entries[0]["context"]["phase"] == "tech-spec", "phase is taken before phase_display"
    metrics = MetricsCalculator(entries).calculate_all_metrics()
    patterns = PatternDetector(entries).detect_all_patterns()
    recs = generator.RecommendationGenerator(metrics, patterns, entries).generate_all_recommendations()
    assert recs, "the fixture produces proposals"
    for r in recs:
        assert r["target_skill"] in SKILL_DIRS, r["target_skill"]
        assert r["target_file"] and generator.resolve_target(r["target_file"]), r


def test_t17_18_no_target_is_never_queued(aid_home):
    gen = generator.RecommendationGenerator({}, {}, [])
    dead = gen._create_recommendation("high", "learning-mode", "S", "c", "change", "why", {})
    assert dead["target_file"] is None
    generator.save_recommendations([dead])
    assert generator.load_recommendation_queue() == []


def test_t17_18_zero_gap_role_is_not_emitted():
    patterns = {"role_mismatch": {"patterns_found": True, "overall_average": 3.0, "mismatched_roles": [
        {"role": "pm", "average_rating": 3.0, "gap_from_overall": 0.0, "weak_topics": []},
        {"role": "qa", "average_rating": 3.05, "gap_from_overall": -0.05, "weak_topics": []},
        {"role": "pm", "average_rating": 2.0, "gap_from_overall": 1.0, "weak_topics": []}]}}
    recs = generator.RecommendationGenerator({}, patterns, [])._recommendations_from_roles()
    assert [r["target_skill"] for r in recs] == ["role-product-manager"]
    assert recs[0]["target_file"] == "roles/product-manager/cumulative.md"


# ---------------------------------------------------------------------------
# T17-19: Debate Rate is n/a without data (L3c-2e)
# ---------------------------------------------------------------------------

def _dash(acceptance):
    d = dashboard_mod.QualityDashboard.__new__(dashboard_mod.QualityDashboard)
    d.days = 30
    d.entries = []
    d.metrics = {"summary": {"total_entries": 1}, "decision_acceptance": acceptance,
                 "ratings_by_category": {"overall_average": 4.0}, "feedback_engagement": {},
                 "debate_outcomes": {}}
    return d


def test_t17_19_debate_rate_is_none_without_decisions():
    assert _dash({"rate": None, "total_decisions": 0})._generate_summary()["key_metrics"]["debate_rate"] is None
    assert _dash({"rate": 0.75})._generate_summary()["key_metrics"]["debate_rate"] == 0.25


def test_t17_19_analyze_and_dashboard_text_say_n_a(aid_home, capsys):
    """The --analyze text and the markdown dashboard: n/a with no decision data."""
    pending = aid_home / "feedback" / "pending"
    pending.mkdir(parents=True)
    for i, r in enumerate(_feedback(3, phase=4, rating=4)):
        (pending / "f{}.json".format(i)).write_text(json.dumps(r), encoding="utf-8")
    from memory_system import subagent
    import sys
    argv = sys.argv
    sys.argv = ["memory_system", "--analyze", "--days", "3650"]
    try:
        subagent.main()
    except SystemExit:
        pass
    finally:
        sys.argv = argv
    out = capsys.readouterr().out
    assert "Debate Rate: n/a" in out, out
    assert "Debate Rate: 100%" not in out
    md = dashboard_mod.QualityDashboard(days=3650).generate_markdown_report()
    assert "| Debate Rate | n/a |" in md
