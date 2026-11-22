"""
WHY THESE TESTS (T16-26..T16-33, release gate 3.0.8 run 2):
- R-05 / E7: secrets whose NAME has a prefix or suffix (AWS_SECRET_ACCESS_KEY=, client_secret:,
  GITHUB_TOKEN=) and PEM private-key blocks reached feedback and memory unredacted.
- g8-memory-apply-mangle: memory-apply kept a trailing "**" after stripping the leading one and
  wrote an empty "- Why: " line.
- L3b-2c: two reports saved in the same second overwrote each other.
- g8-improve-stat: an approved sync never moved analysed feedback to processed/.
- S2-05g / audit s4: memory-system docs named commands that do not exist (/aid skill,
  "/aid <sub>") and anchors that do not resolve.
- Audit s4 info (I-15): URL redaction swallowed trailing punctuation; a legacy 16-hex SHA-1 id
  was accepted for a NEW queue entry.
Token-shaped strings are built at run time: no file holds a scanner match.
"""
import json
import re
import time
from datetime import datetime
from pathlib import Path

import pytest

from memory_system.analysis import dashboard, memory_sync
from memory_system.feedback import collector
from memory_system.recommendations import generator
from memory_system.redact import redact
from memory_system.subagent import LearningSubAgent

MS = Path(__file__).resolve().parents[1]          # memory-system/
REPO = MS.parent

_V = "Zq9" + "x" * 37                                # 40 run-time chars, no vendor prefix
_PK = "PRIV" + "ATE KEY"


def _secret_lines():
    """(text, secret value) pairs: every I-14 example."""
    return [
        ("AWS_SECRET_ACCESS_KEY=" + _V, _V),
        ("aws_secret_access_key=" + _V, _V),
        ("export DB_PASSWORD=" + "hunter2db", "hunter2db"),
        ("client_secret: " + "cs-value-1", "cs-value-1"),
        ("ATLASSIAN_API_TOKEN=" + "atl-val-22", "atl-val-22"),
        ("GITHUB_TOKEN=" + "gt-val-333", "gt-val-333"),
        ("STR" + "IPE_SECRET=" + "st-val-444", "st-val-444"),   # vendor name built at run time
        ("X_API_KEY=" + "xk-val-555", "xk-val-555"),
        ("SSH_PRIVATE_KEY=" + "sk-val-666", "sk-val-666"),
        ('api_key: "' + "yaml-val-77" + '"', "yaml-val-77"),
    ]


def _pem(label="RSA "):
    return ("-----BEGIN " + label + _PK + "-----\nMIIBOgIBAAJBAKj34GkxFhD90vcNLYLInFEX\n"
            "-----END " + label + _PK + "-----")


# --------------------------------------------------------------------------- T16-26
@pytest.mark.parametrize("text, value", _secret_lines())
def test_t16_26_named_secret_redacted_on_write(text, value):
    out = redact("note: " + text + " end")
    assert value not in out, out
    assert "[token]" in out


@pytest.mark.parametrize("text, value", _secret_lines())
def test_t16_26_named_secret_redacted_on_read(aid_home, text, value):
    """The /aid-improve reader (collector.load_pending_feedback, behind memory-feedback)
    redacts a pending file that was written raw."""
    pend = aid_home / "feedback" / "pending"
    pend.mkdir(parents=True)
    (pend / "raw.json").write_text(json.dumps({
        "id": "raw-1", "timestamp": "2026-11-19T10:00:00Z", "session_id": "s1",
        "context": {"phase": "4-development", "role": "developer", "interaction_type": "phase-gate"},
        "feedback": {"rating": 3, "verbal": "worked: x. improve: " + text}}), encoding="utf-8")
    entries = collector.load_pending_feedback()
    assert len(entries) == 1
    assert value not in json.dumps(entries), entries


def test_t16_26_write_path_saves_no_secret(aid_home):
    text = " ".join(t for t, _ in _secret_lines())
    path = collector.save_feedback_entry(collector.create_feedback_entry(
        "s1", "4-development", "developer", "phase-gate", feedback={"rating": 3, "verbal": text}))
    raw = path.read_text(encoding="utf-8")
    for _, value in _secret_lines():
        assert value not in raw


@pytest.mark.parametrize("label", ["RSA ", "", "OPENSSH ", "EC "])
def test_t16_26_pem_block_becomes_placeholder(label):
    out = redact("before\n" + _pem(label) + "\nafter")
    assert out == "before\n[private-key]\nafter"


def test_t16_26_pem_block_without_end_is_cut_to_end_of_text():
    out = redact("key:\n-----BEGIN " + _PK + "-----\nMIIBOgIBAAJBAKj34GkxFhD90vcNLY")
    assert out == "key:\n[private-key]"


@pytest.mark.parametrize("text", [t for t, _ in _secret_lines()] + [_pem(), "rating 4",
                                  "see https://x.example/a."])
def test_t16_26_idempotent(text):
    once = redact(text)
    assert redact(once) == once


def test_t16_26_kept_behaviour():
    assert redact("rating 4") == "rating 4"
    assert redact("max_tokens=100") == "max_tokens=[token]"          # accepted over-redaction
    assert redact("password=abc, next") == "password=[token], next"
    assert redact("see notes in C:/a/b/notes.txt, then") == "see notes in [path], then"


@pytest.mark.parametrize("hostile", ["_" * 100000, "token" * 20000, "a." * 50000,
                                     "_token" * 16000, "a=" * 50000, 'token= "' + "a" * 99990,
                                     "x" * 99990 + "=1"],
                         ids=["underscores", "tokens", "dots", "prefixed", "assignments",
                              "open-quote", "long-name"])
def test_t16_26_name_rule_stays_linear(hostile):
    t0 = time.time()
    redact(hostile)
    assert time.time() - t0 < 2.0


# --------------------------------------------------------------------------- T16-27
_SUG_001 = {   # the documented SUG-001 shape (agents/memory-analysis-agent.md)
    "id": "SUG-001", "type": "skill_update", "confidence": 0.85,
    "target": {"file": "skills/memory-system/references/roles/developer/cumulative.md",
               "section": "High-Confidence Patterns"},
    "content": "- **Ask about data flow early**: \"Who else touches this data?\" prevents "
               "stakeholder misses (Evidence: 4 sessions, 4.3 avg rating)",
    "evidence": {"pattern_id": "PAT-P01", "occurrences": 4}}


def _apply(tmp_path, monkeypatch, suggestion):
    refs = tmp_path / "refs"
    target = refs / "roles" / "developer" / "cumulative.md"
    target.parent.mkdir(parents=True)
    target.write_text("# Dev\n", encoding="utf-8")
    monkeypatch.setattr(generator, "REFS_ROOT", refs)
    ids = generator.queue_proposals({"suggestions": [suggestion]})["queued"]
    assert len(ids) == 1
    assert generator.apply_recommendation(ids[0], refs_root=refs)["ok"]
    return target.read_text(encoding="utf-8").split("# Dev\n", 1)[1]


def test_t16_27_sug001_keeps_balanced_bold_and_writes_no_empty_why(aid_home, tmp_path, monkeypatch):
    added = _apply(tmp_path, monkeypatch, _SUG_001)
    assert "**Ask about data flow early**:" in added, added
    for line in added.splitlines():
        assert line.count("**") % 2 == 0, line
    assert "Why:" not in added, added


def test_t16_27_rationale_still_written(aid_home, tmp_path, monkeypatch):
    added = _apply(tmp_path, monkeypatch, dict(_SUG_001, rationale="seen in 4 sessions"))
    assert "  - Why: seen in 4 sessions\n" in added


@pytest.mark.parametrize("value, want", [
    ("- **Ask** first", "**Ask** first"),
    ("**x** and **y**", "**x** and **y**"),
    ("## **dangling bold", "dangling bold"),
    ("* item", "item"),
    ("> # heading", "heading"),
])
def test_t16_27_one_line_bold(value, want):
    assert generator._one_line(value) == want


# --------------------------------------------------------------------------- T16-28
class _Frozen(datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2026, 11, 19, 10, 13, 49)


def test_t16_28_same_second_reports_get_two_files(aid_home, monkeypatch):
    monkeypatch.setattr(dashboard, "datetime", _Frozen)
    agent = LearningSubAgent(days=7)
    first = agent.save_report(days=7, format="markdown")      # --analyze --save
    second = agent.save_report(days=7, format="markdown")     # --dashboard --save
    third = agent.save_report(days=7, format="markdown")
    assert first.name == "quality-report_2026-11-19_101349.md"
    assert second.name == "quality-report_2026-11-19_101349-2.md"
    assert third.name == "quality-report_2026-11-19_101349-3.md"
    assert all(p.is_file() and p.stat().st_size for p in (first, second, third))


def test_t16_28_existing_report_is_not_overwritten(aid_home, monkeypatch):
    monkeypatch.setattr(dashboard, "datetime", _Frozen)
    reports = aid_home / "reports"
    reports.mkdir(parents=True)
    old = reports / "quality-report_2026-11-19_101349.json"
    old.write_text("KEEP", encoding="utf-8")
    new = dashboard.save_dashboard(days=7, format="json")
    assert old.read_text(encoding="utf-8") == "KEEP"
    assert new.name == "quality-report_2026-11-19_101349-2.json"
    json.loads(new.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- T16-29
def _seed_feedback(aid_home, n=5):
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


def test_t16_29_dry_run_moves_nothing(aid_home):
    _seed_feedback(aid_home)
    result = LearningSubAgent(days=30).sync_to_memory(days=30, approve=False)
    assert not result.get("processed")
    assert len(list((aid_home / "feedback" / "pending").glob("*.json"))) == 5
    assert not list((aid_home / "feedback" / "processed").glob("*.json"))


def test_t16_29_approved_sync_moves_analysed_entries(aid_home):
    _seed_feedback(aid_home)
    result = LearningSubAgent(days=30).sync_to_memory(days=30, approve=True)
    assert sorted(result["processed"]) == ["fb-{}".format(i) for i in range(5)], result
    assert not list((aid_home / "feedback" / "pending").glob("*.json"))
    assert len(list((aid_home / "feedback" / "processed").glob("*.json"))) == 5
    # A second approved sync has nothing left to move.
    assert LearningSubAgent(days=30).sync_to_memory(days=30, approve=True)["processed"] == []


def test_t16_29_entries_outside_the_window_stay_pending(aid_home):
    _seed_feedback(aid_home, n=4)
    pend = aid_home / "feedback" / "pending"
    old = json.loads((pend / "fb0.json").read_text(encoding="utf-8"))
    old.update(id="fb-old", timestamp="2020-01-01T00:00:00Z")
    (pend / "old.json").write_text(json.dumps(old), encoding="utf-8")
    result = memory_sync.sync_memory_from_feedback(days=30, approve=True)
    assert "fb-old" not in result["processed"] and len(result["processed"]) == 4
    assert (pend / "old.json").is_file()


# --------------------------------------------------------------------------- T16-30
def _doc_files():
    return sorted(MS.rglob("*.md")) + [MS / "templates" / "config.yaml"]


_COMMANDS = {p.stem for p in (REPO / "commands").glob("*.md")}
_SKILLS = {p.name for p in (REPO / "skills").iterdir() if p.is_dir()}
# A slash reference: /aid..., or a `/name` code span that starts a word.
_AID_REF = re.compile(r"(?<![\w.$}/~`-])`?/aid(?P<rest>[ -][a-z][a-z-]*|(?![\w-]))")
_CODE_REF = re.compile(r"(?:^|(?<=[\s(|]))`/(?P<name>[a-z][a-z0-9-]*)(?![\w<-])")   # not `/aid-<name>`


def test_t16_30_slash_references_resolve():
    bad = []
    for f in _doc_files():
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            where = "{}:{}".format(f.relative_to(REPO), n)
            for m in _AID_REF.finditer(line):
                rest = m.group("rest")
                if not rest.startswith("-") or "aid" + rest not in _COMMANDS:
                    bad.append("{}: /aid{}".format(where, rest))
            for m in _CODE_REF.finditer(line):
                name = m.group("name")
                if name not in _COMMANDS and name not in _SKILLS:
                    bad.append("{}: /{}".format(where, name))
    assert bad == [], bad


def test_t16_30_no_skill_command_documented():
    for f in _doc_files():
        text = f.read_text(encoding="utf-8")
        assert not re.search(r"/aid[ -]skill", text), f
        assert "/aid improve" not in text, f


# --------------------------------------------------------------------------- T16-31
def _slug(heading):
    s = re.sub(r"[^\w\- ]", "", heading.strip().lower())
    return s.replace(" ", "-")


def _anchors(path):
    text = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.S)
    seen, out = {}, set(re.findall(r'<a id="([^"]+)"', text))
    for h in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", text, flags=re.M):
        s = _slug(h)
        out.add(s if s not in seen else "{}-{}".format(s, seen[s]))
        seen[s] = seen.get(s, 0) + 1
    return out


_ANCHOR_REF = re.compile(r"(?P<file>[\w./-]*\.md)?#(?P<anchor>[a-z0-9][\w-]*)")


def test_t16_31_anchors_resolve():
    bad = []
    for f in sorted(MS.glob("*.md")) + sorted((MS / "docs").glob("*.md")):
        for m in re.finditer(r"`[^`\n]*\.md#[^`\n]*`|\]\([^)\s]*#[^)\s]*\)", f.read_text(encoding="utf-8")):
            ref = _ANCHOR_REF.search(m.group(0))
            if not ref:
                continue
            name = ref.group("file")
            if not name:
                target = f
            elif name.startswith("memory-system/"):
                target = REPO / name
            else:
                target = f.parent / name
            if not target.is_file() or ref.group("anchor") not in _anchors(target):
                bad.append("{}: {}".format(f.relative_to(REPO), m.group(0)))
    assert bad == [], bad


def test_t16_31_integration_anchors_named_by_audit():
    text = (MS / "INTEGRATION.md").read_text(encoding="utf-8")
    refs = re.findall(r"`(memory-system/docs/\w+\.md)#([\w-]+)`", text)
    assert len(refs) >= 4
    for name, anchor in refs:
        assert anchor in _anchors(REPO / name), (name, anchor)


def test_t16_31_command_links_into_memory_docs_resolve():
    # WS-E request: commands/aid-status.md links COMMANDS.md#aid-status; the
    # '/aid-status' heading rename must keep that anchor (and every other
    # commands/*.md link into memory-system/docs).
    assert "aid-status" in _anchors(MS / "docs" / "COMMANDS.md")
    bad = []
    for f in sorted((REPO / "commands").glob("*.md")):
        for m in re.finditer(r"(memory-system/docs/\w[\w-]*\.md)#([a-z0-9][\w-]*)",
                             f.read_text(encoding="utf-8")):
            target = REPO / m.group(1)
            if not target.is_file() or m.group(2) not in _anchors(target):
                bad.append("{}: {}".format(f.name, m.group(0)))
    assert bad == [], bad


# --------------------------------------------------------------------------- T16-32
@pytest.mark.parametrize("text, want", [
    ("see https://x.example/a.", "see [url]."),
    ("see https://x.example/a, then", "see [url], then"),
    ("(see https://x.example/a)", "(see [url])"),
    ("is it https://x.example/a?", "is it [url]?"),
    ("https://x.example/wiki/A_(b)", "[url]"),
    ("clone git@example.org:owner/repo.git.", "clone [url]."),
])
def test_t16_32_url_keeps_trailing_punctuation(text, want):
    assert redact(text) == want


# --------------------------------------------------------------------------- T16-33
def _rec(text="Ask for NFRs early"):
    return {"priority": "low", "target_skill": "memory-system",
            "target_file": "roles/developer/cumulative.md", "section": "Learnings",
            "current_guidance": "", "proposed_change": text, "rationale": "r",
            "supporting_data": {}}


def test_t16_33_new_entry_never_keeps_a_legacy_id(aid_home, tmp_path):
    rec = _rec()
    legacy = generator._legacy_content_id(rec)
    generator.save_recommendations([dict(rec, id=legacy)])
    queue = generator.load_recommendation_queue()
    assert [r["id"] for r in queue] == [generator._content_id(rec)]
    refs = tmp_path / "refs"
    (refs / "roles" / "developer").mkdir(parents=True)
    (refs / "roles" / "developer" / "cumulative.md").write_text("# Dev\n", encoding="utf-8")
    assert not generator.apply_recommendation(legacy, refs_root=refs)["ok"]
    assert generator.apply_recommendation(generator._content_id(rec), refs_root=refs)["ok"]


def test_t16_33_migration_documents_the_sunset():
    text = (MS / "docs" / "MIGRATION.md").read_text(encoding="utf-8")
    assert "legacy SHA-1 sunset" in text
    assert "never accepted for a new entry" in text
