"""
T16 WS-B (T16-acceptance.md T16-16..T16-20): aid_session.py init creates context.json,
the phase display fields follow the phase, improvement-run statistics (I-11), the read-only
`status` subcommand (I-10) and prefixed secrets kept out of state and feedback (E7).

Every test runs the REAL script in a subprocess with its own HOME, USERPROFILE and AID_HOME,
CLAUDE_PROJECT_DIR / CLAUDE_CONFIG_DIR unset unless the test sets them. Probe projects live
at the drive root (tempfile.mkdtemp(dir=anchor)): a folder under a user profile whose
~/.aid/state.json exists would sit inside that profile's state.

WHY: /aid-init could not create state or context.json through an allowed writer (g1-aid-init,
G1-09), advance left the previous phase's label in state (G4-14), /aid-improve recorded no
run statistics (g8-improve-stat), /aid-status guessed from files (g8-aid-status), and a
prefixed secret such as DB_PASSWORD=... reached state and feedback verbatim (R-05).
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SESSION = REPO_ROOT / "hooks" / "aid_session.py"
RUNNER = REPO_ROOT / "hooks" / "hook-runner.mjs"
TERMS = json.loads((REPO_ROOT / "references" / "role-phase-terminology.json").read_text(encoding="utf-8"))
ALLOWED_TARGET = "skills/memory-system/references/roles/developer/cumulative.md"
ISO = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d")


def _env(home, **extra):
    e = dict(os.environ, HOME=str(home), USERPROFILE=str(home), AID_HOME=str(Path(home) / ".aid"),
             PYTHONIOENCODING="utf-8")
    for k in ("CLAUDE_PROJECT_DIR", "CLAUDE_CONFIG_DIR"):
        e.pop(k, None)
    e.update(extra)
    return e


def run(script, cwd, home, *args, **env):
    p = subprocess.run([sys.executable, str(script)] + list(args), cwd=str(cwd), env=_env(home, **env),
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    return p.returncode, p.stdout + p.stderr


def sess(cwd, home, *args, **env):
    return run(SESSION, cwd, home, *args, **env)


@pytest.fixture
def probe(tmp_path):
    """An empty folder at the drive root (no AID marker above it) and a fake home H."""
    d = Path(tempfile.mkdtemp(prefix="aid-t16-", dir=Path(tmp_path).anchor if os.name == "nt" else None))
    H = tmp_path / "H"
    H.mkdir()
    yield d, H
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def proj(probe):
    """The probe folder made an AID project (marker .aid/hooks/config.json)."""
    P, H = probe
    (P / ".aid" / "hooks").mkdir(parents=True)
    (P / ".aid" / "hooks" / "config.json").write_text("{}", encoding="utf-8")
    return P, H


def state_of(P):
    return json.loads((P / ".aid" / "state.json").read_text(encoding="utf-8"))


CONTEXT_KEYS = ["$schema", "version", "last_updated", "current_task", "current_step", "progress",
                "session_notes", "blockers"]


# ---------------------------------------------------------------------------
# T16-16: init is the one bootstrap and creates context.json (I-10)
# ---------------------------------------------------------------------------

def test_t16_16_init_creates_state_and_context_in_the_target(probe):
    T, H = probe
    rc, out = sess(T, H, "init", "1", "0", CLAUDE_PROJECT_DIR=str(T))
    assert rc == 0, out
    st = state_of(T)
    assert st["current_phase"] == 0 and st["role"] and st["phase_display"] and st["skills_loaded"]
    ctx = json.loads((T / ".aid" / "context.json").read_text(encoding="utf-8"))
    assert list(ctx) == CONTEXT_KEYS, ctx
    assert ctx["$schema"] == "aid-context-v1" and ctx["version"] == "1.0"
    assert ISO.match(ctx["last_updated"]), ctx
    assert ctx["current_task"] is None and ctx["current_step"] is None
    assert ctx["progress"] == {"steps_completed": [], "steps_pending": []}
    assert ctx["session_notes"] == [] and ctx["blockers"] == []


def test_t16_16_existing_context_is_byte_identical_after_init(probe):
    T, H = probe
    (T / ".aid").mkdir()
    mine = b'{"current_task": "my notes", "weird":  [1,2]}\r\n'
    (T / ".aid" / "context.json").write_bytes(mine)
    rc, out = sess(T, H, "init", "1", "0", CLAUDE_PROJECT_DIR=str(T))
    assert rc == 0, out
    assert (T / ".aid" / "state.json").is_file()
    assert (T / ".aid" / "context.json").read_bytes() == mine


def test_t16_16_repair_leaves_context_alone(proj):
    P, H = proj
    (P / ".aid" / "state.json").write_text("{not json", encoding="utf-8")
    mine = b'{"current_task": "keep me"}\n'
    (P / ".aid" / "context.json").write_bytes(mine)
    rc, out = sess(P, H, "init", "developer", "2", "--repair")
    assert rc == 0, out
    assert state_of(P)["current_phase"] == 2
    assert (P / ".aid" / "context.json").read_bytes() == mine


def test_t16_16_init_in_a_subfolder_never_writes_an_ancestor(proj):
    """Guard (INV-2): cwd = CLAUDE_PROJECT_DIR = T inside an initialized project P. The
    ancestor's state is not rewritten and no context.json appears there."""
    P, H = proj
    assert sess(P, H, "init", "developer", "1")[0] == 0
    if (P / ".aid" / "context.json").exists():
        (P / ".aid" / "context.json").unlink()
    before = (P / ".aid" / "state.json").read_bytes()
    T = P / "sub" / "target"
    T.mkdir(parents=True)
    sess(T, H, "init", "1", "0", CLAUDE_PROJECT_DIR=str(T))
    assert (P / ".aid" / "state.json").read_bytes() == before
    assert not (P / ".aid" / "context.json").exists()


# ---------------------------------------------------------------------------
# T16-17: phase display fields follow the phase (G4-14)
# ---------------------------------------------------------------------------

def _newest_approve_entry(H):
    files = sorted((H / ".aid" / "feedback" / "pending").glob("approve-*.json"),
                   key=lambda f: f.stat().st_mtime_ns)
    return json.loads(files[-1].read_text(encoding="utf-8"))


def _consistent(st):
    return (st["status"] == "active") == (st["current_session"].get("active") is True)


@pytest.mark.parametrize("role,term_role", [("1", None), ("other", "developer")])
def test_t16_17_phase_display_follows_every_advance(proj, role, term_role):
    P, H = proj
    rc, out = sess(P, H, "init", role, "0", "--phase-desc", "my custom phase text")
    assert rc == 0, out
    st = state_of(P)
    terms = TERMS["phases"][term_role or st["role"]]
    assert st["phase_description"] == "my custom phase text"
    for n in range(6):
        st = state_of(P)
        assert st["current_phase"] == n
        assert st["phase_display"] == terms[str(n)]["name"], (n, st["phase_display"])
        if n:
            assert st["phase_description"] == terms[str(n)]["description"], n
        assert st["status"] == "active" and _consistent(st), st
        assert sess(P, H, "review", str(n), "PASS")[0] == 0
        assert _consistent(state_of(P))
        rc, out = sess(P, H, "approve", "--note", "rating 4")
        assert rc == 0, out
        assert _consistent(state_of(P))
        fb = _newest_approve_entry(H)
        assert fb["phase"] == n and fb["phase_display"] == terms[str(n)]["name"], fb
        if n < 5:
            rc, out = sess(P, H, "advance")
            assert rc == 0, out
    rc, out = sess(P, H, "end", "--rating", "4")
    assert rc == 0, out
    st = state_of(P)
    assert st["status"] != "active" and st["current_session"]["active"] is False


# ---------------------------------------------------------------------------
# T16-18: improvement-run statistics (I-11)
# ---------------------------------------------------------------------------

def _pending_entries(H, n=3):
    d = H / ".aid" / "feedback" / "pending"
    d.mkdir(parents=True, exist_ok=True)
    for i in range(n):
        ts = "2026-11-1{}T10:00:0{}+00:00".format(i + 1, i)
        (d / (ts.replace(":", "-") + ".json")).write_text(json.dumps({
            "timestamp": ts, "role": "developer", "phase": 4, "phase_display": "Implementation",
            "rating": 2, "worked_well": "short answers", "to_improve": "too verbose, shorter please",
            "duration_minutes": 30, "subagent_review": {"status": "skipped", "timestamp": ts}}),
            encoding="utf-8")


def _improvement(H):
    return H / ".aid" / "metrics" / "improvement.json"


def test_t16_18_approved_memory_sync_records_a_run(proj):
    P, H = proj
    _pending_entries(H)
    rc, out = sess(P, H, "memory-preview")
    assert rc == 0, out
    assert not _improvement(H).exists(), "a preview writes nothing"
    rc, out = sess(P, H, "memory-sync")
    assert rc == 0, out
    stats = json.loads(_improvement(H).read_text(encoding="utf-8"))
    assert set(stats) == {"last_improvement_run", "runs", "feedback_processed", "skills_updated"}
    assert ISO.match(stats["last_improvement_run"]) and stats["runs"] == 1
    processed = len(list((H / ".aid" / "feedback" / "processed").glob("*.json")))
    assert stats["feedback_processed"] == processed and stats["skills_updated"] == 0
    assert sess(P, H, "memory-sync")[0] == 0
    assert json.loads(_improvement(H).read_text(encoding="utf-8"))["runs"] == 2
    rc, out = sess(P, H, "reset")
    assert rc == 0, out
    assert not (H / ".aid" / "metrics").exists()


@pytest.fixture
def plugin_copy(tmp_path):
    """A scratch copy of the plugin parts memory-apply needs, so a successful apply appends
    to the copy's learnings file, never to the repository's."""
    C = tmp_path / "plugin"
    shutil.copytree(REPO_ROOT / "hooks", C / "hooks",
                    ignore=shutil.ignore_patterns("__pycache__", "*.sh", "*.mjs"))
    shutil.copytree(REPO_ROOT / "references", C / "references")
    shutil.copytree(REPO_ROOT / "memory-system" / "memory_system", C / "memory-system" / "memory_system",
                    ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(REPO_ROOT / "skills" / "memory-system" / "references",
                    C / "skills" / "memory-system" / "references")
    return C


def test_t16_18_memory_apply_counts_skills_updated(proj, plugin_copy):
    P, H = proj
    script = plugin_copy / "hooks" / "aid_session.py"
    (P / ".aid" / "improve").mkdir()
    (P / ".aid" / "improve" / "proposals.json").write_text(json.dumps({"suggestions": [
        {"target": {"file": ALLOWED_TARGET}, "content": "Ask for the test command first", "priority": "high"},
        {"target": {"file": ALLOWED_TARGET}, "content": "Prefer short answers", "priority": "low"}]}),
        encoding="utf-8")
    rc, out = run(script, P, H, "memory-queue")
    assert rc == 0 and "Queued 2" in out, out
    queue = json.loads((H / ".aid" / "recommendations" / "queue.json").read_text(encoding="utf-8"))
    rc, out = run(script, P, H, "memory-apply", "0000000000")
    assert rc != 0 and "refused" in out
    rc, out = run(script, P, H, "memory-reject", queue[1]["id"])
    assert rc == 0, out
    assert not _improvement(H).exists(), "a refusal or a reject writes nothing"
    rc, out = run(script, P, H, "memory-apply", queue[0]["id"])
    assert rc == 0, out
    stats = json.loads(_improvement(H).read_text(encoding="utf-8"))
    assert stats["skills_updated"] == 1 and stats["runs"] == 0 and stats["last_improvement_run"] is None
    target = plugin_copy / ALLOWED_TARGET
    assert "Ask for the test command first" in target.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# T16-19: status subcommand (I-10)
# ---------------------------------------------------------------------------

def _tree_hash(*roots):
    h = hashlib.sha256()
    for root in roots:
        for f in sorted(Path(root).rglob("*")):
            h.update(str(f.relative_to(root)).encode("utf-8"))
            if f.is_file():
                h.update(f.read_bytes())
    return h.hexdigest()


def _slot_total():
    sys.path.insert(0, str(REPO_ROOT / "memory-system"))
    try:
        from memory_system.analysis.memory_sync import SLOT_ALLOCATION
    finally:
        sys.path.pop(0)
    return sum(SLOT_ALLOCATION.values())


def test_t16_19_status_json_reports_every_field_and_writes_nothing(proj):
    P, H = proj
    assert sess(P, H, "init", "developer", "2")[0] == 0
    aid = H / ".aid"
    _pending_entries(H, 2)
    (aid / "feedback" / "processed").mkdir(parents=True)
    (aid / "feedback" / "processed" / "old.json").write_text("{}", encoding="utf-8")
    (aid / "metrics").mkdir()
    (aid / "metrics" / "improvement.json").write_text(json.dumps(
        {"last_improvement_run": "2026-11-01T00:00:00+00:00", "runs": 4, "feedback_processed": 9,
         "skills_updated": 2}), encoding="utf-8")
    (aid / "recommendations").mkdir()
    (aid / "recommendations" / "queue.json").write_text(json.dumps([{"id": "a" * 16}]), encoding="utf-8")
    before = _tree_hash(P, aid)
    rc, out = sess(P, H, "status", "--format", "json")
    assert rc == 0, out
    st = json.loads(out)
    assert st["project"]["root"] == str(P) and st["project"]["phase"] == 2 and st["project"]["initialized"]
    s = st["session"]
    assert s["role"] == "developer" and s["phase_display"] == TERMS["phases"]["developer"]["2"]["name"]
    assert ISO.match(s["started"]) and s["active"] is True
    assert st["feedback"] == {"pending": 2, "processed": 1, "newest_pending": "2026-11-12T10:00:01+00:00"}
    assert st["improvement"] == {"last_improvement_run": "2026-11-01T00:00:00+00:00", "runs": 4,
                                 "feedback_processed": 9, "skills_updated": 2}
    assert st["memory"] == {"used": 0, "total": _slot_total()}
    assert st["recommendations"] == {"queued": 1}
    rc, text = sess(P, H, "status")
    assert rc == 0 and "Phase: 2" in text and "0/{} slots".format(_slot_total()) in text, text
    assert _tree_hash(P, aid) == before, "status wrote something"


def test_t16_19_status_in_a_non_aid_folder(probe):
    D, H = probe
    before = _tree_hash(D)
    rc, out = sess(D, H, "status", "--format", "json")
    assert rc == 0, out
    st = json.loads(out)
    assert st["project"] is None and st["session"] is None
    assert st["improvement"]["runs"] == 0 and st["feedback"]["pending"] == 0
    assert _tree_hash(D) == before and not (H / ".aid").exists()


def test_t16_19_status_json_keys_match_the_aid_status_command(proj):
    """commands/aid-status.md (WS-E) reads these exact keys from `status --format json`; an
    AID project without state.json is reported as not initialized (rc 0, no session)."""
    P, H = proj
    rc, out = sess(P, H, "status", "--format", "json")
    assert rc == 0, out
    st = json.loads(out)
    assert set(st) == {"project", "session", "feedback", "improvement", "memory", "recommendations"}
    assert st["project"]["root"] == str(P) and st["project"]["initialized"] is False
    assert st["project"]["phase"] is None and st["session"] is None
    assert not (P / ".aid" / "state.json").exists() and not (P / ".aid" / "context.json").exists()
    assert sess(P, H, "init", "1", "0")[0] == 0
    st = json.loads(sess(P, H, "status", "--format", "json")[1])
    assert {"root", "initialized", "phase", "phase_name"} <= set(st["project"])
    assert {"role", "phase_display", "started", "active"} <= set(st["session"])
    assert set(st["feedback"]) == {"pending", "processed", "newest_pending"}
    assert set(st["improvement"]) == {"last_improvement_run", "runs", "feedback_processed", "skills_updated"}
    assert set(st["memory"]) == {"used", "total"} and set(st["recommendations"]) == {"queued"}


@pytest.mark.skipif(shutil.which("node") is None, reason="node is needed for hook-runner.mjs")
@pytest.mark.parametrize("phase", [None, 0, 1, 4, 5])
def test_t16_19_canonical_status_call_is_allowed_silently(tmp_path, probe, phase):
    """Cross-check against WS-A (not a WS-A edit): status is not a confirmed subcommand, so
    the canonical call is neither asked nor denied, in a non-AID folder and at every phase."""
    D, H = probe
    (H / ".claude").mkdir()
    if phase is not None:
        (D / ".aid" / "hooks").mkdir(parents=True)
        (D / ".aid" / "hooks" / "config.json").write_text(json.dumps(
            {"enforcement": {"phase_gate_write": "block", "phase_gate_bash": "block"}}), encoding="utf-8")
        (D / ".aid" / "state.json").write_text(json.dumps({"current_phase": phase}), encoding="utf-8")
    R = str(REPO_ROOT).replace("\\", "/")
    for cmd in ('python "{}/hooks/aid_session.py" status'.format(R),
                'python "{}/hooks/aid_session.py" status --format json'.format(R)):
        payload = {"session_id": uuid.uuid4().hex, "cwd": str(D), "tool_name": "Bash",
                   "tool_input": {"command": cmd}}
        p = subprocess.run(["node", str(RUNNER), "phase-gate-bash"], input=json.dumps(payload),
                           capture_output=True, text=True, cwd=str(D), env=_env(H), timeout=60)
        assert p.returncode == 0, p.stderr[-600:]
        out = p.stdout.strip()
        decision = json.loads(out).get("hookSpecificOutput", {}).get("permissionDecision") if out else None
        assert decision not in ("deny", "ask"), (phase, cmd, out)


# ---------------------------------------------------------------------------
# T16-20: prefixed secrets never reach state or feedback (E7, end to end)
# ---------------------------------------------------------------------------

def _secret_value():
    """40 characters built at run time (no vendor prefix, never a literal in the repo)."""
    return "".join("Zq7" for _ in range(14))[:40]


def _leaky():
    return "fine aws_secret_access_key={} DB_PASSWORD=x client_secret: y".format(_secret_value())


LEAKS = lambda: (_secret_value(), "DB_PASSWORD=x", "client_secret: y")   # noqa: E731


def _redactor_landed():
    sys.path.insert(0, str(REPO_ROOT / "memory-system"))
    try:
        from memory_system.redact import redact
    except ImportError:
        return False
    finally:
        sys.path.pop(0)
    out = redact(_leaky(), ())
    return not any(s in out for s in LEAKS())


def test_t16_20_prefixed_secrets_never_reach_state_or_feedback(proj):
    if not _redactor_landed():
        pytest.skip("WS-D's I-14 redactor (prefixed key names) has not landed in memory_system.redact; "
                    "the Suite stage runs this test with both workstreams")
    P, H = proj
    assert sess(P, H, "init", "developer", "4")[0] == 0
    (P / ".aid" / "qa").mkdir()
    (P / ".aid" / "qa" / "T-1.yaml").write_text("criteria: [a]\n", encoding="utf-8")
    note = _leaky()
    for args in (("approve", "--note", note), ("review", "4", "PASS", "--note", note),
                 ("qa-pass", "T-1", "--note", note),
                 ("end", "--rating", "3", "--improve", note, "--worked", note, "--review-note", note)):
        rc, out = sess(P, H, *args)
        assert rc == 0, (args, out)
    texts = [(P / ".aid" / "state.json").read_text(encoding="utf-8")]
    files = list((H / ".aid" / "feedback" / "pending").glob("*.json"))
    assert len(files) >= 2
    texts += [f.read_text(encoding="utf-8") for f in files]
    for t in texts:
        for leak in LEAKS():
            assert leak not in t, (leak, t[:400])
