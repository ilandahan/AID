"""
T17 WS-B (reports/T17-acceptance.md T17-15, T17-16, T17-17, T17-20, T17-21): F5 secrets stay
out of project state and pending feedback end to end, init writes the one context.json schema
(I-21), the read-only `checklist` subcommand and the block `approve` prints (I-22), gate.mjs
records the review result and the cost (I-23), and the pipeline skill resolves reviewers and
criteria plugin-first (I-19).

Every test runs the REAL script in a subprocess with its own HOME, USERPROFILE and AID_HOME;
CLAUDE_PROJECT_DIR / CLAUDE_CONFIG_DIR / CLAUDE_PLUGIN_ROOT are unset unless the test sets
them. Probe projects live at the drive root on Windows (outside the user profile) and under
tmp_path elsewhere.

WHY:
- PROBLEM: `end --improve "psql postgres://u:<pw>@db"` stored the password (R-06/R-07);
  agents wrote three context.json shapes (G1-15/16); /phase-approve restated a checklist the
  code did not know and skipped Phase 0 (G4-10); pipeline cost was prompt-only and never
  recorded (G5-X1); the skill let a project's files replace the plugin's reviewers (R-05).
- COST OF FAILURE: secrets on disk, a SessionStart crash, an approval of the wrong items, an
  unbounded spend, a weakened review.
- SUCCESS: the assertions below.

Secret-shaped values are built at run time with "".join([...]) (U-17).
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SESSION = REPO_ROOT / "hooks" / "aid_session.py"
GATE = REPO_ROOT / "skills" / "pipeline-orchestrator" / "gate.mjs"
SKILL_DIR = REPO_ROOT / "skills" / "pipeline-orchestrator"


def _env(home, **extra):
    e = dict(os.environ, HOME=str(home), USERPROFILE=str(home), AID_HOME=str(Path(home) / ".aid"),
             PYTHONIOENCODING="utf-8")
    for k in ("CLAUDE_PROJECT_DIR", "CLAUDE_CONFIG_DIR", "CLAUDE_PLUGIN_ROOT"):
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
    """An empty folder (drive root on Windows, tmp_path elsewhere) and a fake home H."""
    d = Path(tempfile.mkdtemp(prefix="aid-t17-", dir=Path(tmp_path).anchor if os.name == "nt" else str(tmp_path)))
    H = tmp_path / "H"
    H.mkdir()
    yield d, H
    shutil.rmtree(d, ignore_errors=True)


def state_of(P):
    return json.loads((P / ".aid" / "state.json").read_text(encoding="utf-8"))


def _v():
    return "".join(["s3", "Cr", "et", "Va", "lue", "9x"])


def _all_i20_forms(v):
    return " ; ".join([
        "psql postgres://u:" + v + "@db/x", "redis-cli -u redis://:" + v + "@h",
        "mongodb+srv://u:" + v + "@c.example.net/x", "amqp://u:" + v + "@b/vh",
        "curl -u admin:" + v + " https://h", "curl --user=admin:" + v + " x",
        "mysql -p" + v + " db", "sshpass -p " + v + " ssh h",
        # R1-04 (fix cycle 1): quoted attached mysql values, attached sshpass values
        "mysql -u root -p'" + v + "' db", 'mysql -u root -p"' + v + '" db', "sshpass -p" + v + " ssh h",
        "tool --password " + v, "tool --token=" + v, "tool --api-key " + v, "tool --pass " + v,
        '{"password": "' + v + '"}', "{'api_key':'" + v + "'}", 'password="two ' + v + '"',
        "pass=" + v, "Authorization: Token " + v])


def _dir_digest(root):
    h = hashlib.sha256()
    for p in sorted(Path(root).rglob("*")):
        h.update(p.relative_to(root).as_posix().encode())
        if p.is_file():
            h.update(p.read_bytes())
    return h.hexdigest()


# ---------------------------------------------------------------------------
# T17-15: F5 secrets never reach state or pending feedback
# ---------------------------------------------------------------------------

def test_t17_15_secrets_stay_out_of_state_and_pending_feedback(probe):
    P, H = probe
    v = _v()
    forms = _all_i20_forms(v)
    assert sess(P, H, "init", "developer", "4", CLAUDE_PROJECT_DIR=str(P))[0] == 0
    (P / ".aid" / "qa").mkdir(parents=True, exist_ok=True)
    (P / ".aid" / "qa" / "T-1.yaml").write_text("criteria: [x]\n", encoding="utf-8")
    for args in (["review", "4", "PASS", "--note", forms], ["qa-pass", "T-1", "--note", forms],
                 ["approve", "--note", "rating 4 " + forms]):
        rc, out = sess(P, H, *args)
        assert rc == 0, (args[0], out)
    rc, out = sess(P, H, "end", "--rating", "3", "--improve", forms, "--worked", forms,
                   "--review-note", forms)
    assert rc == 0, out
    assert "Feedback saved (redacted)" in out
    state_text = (P / ".aid" / "state.json").read_text(encoding="utf-8")
    assert v not in state_text
    pending = sorted((H / ".aid" / "feedback" / "pending").glob("*.json"))
    assert len(pending) == 2, pending                     # approve + end
    for f in pending:
        assert v not in f.read_text(encoding="utf-8"), f.name
    end_fb = [json.loads(f.read_text(encoding="utf-8")) for f in pending if not f.name.startswith("approve-")][0]
    assert "[token]" in end_fb["to_improve"] and "[url]" in end_fb["to_improve"]


def test_t17_15_redacted_line_only_when_the_text_was_redacted(probe, tmp_path):
    """Without memory-system the free text is not stored, and the script must not claim it
    was saved redacted."""
    P, H = probe
    plugin = tmp_path / "plugin"
    shutil.copytree(REPO_ROOT / "hooks", plugin / "hooks",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (plugin / "references").mkdir()
    shutil.copy2(REPO_ROOT / "references" / "role-phase-terminology.json", plugin / "references")
    lone = plugin / "hooks" / "aid_session.py"
    assert run(lone, P, H, "init", "developer", "4", CLAUDE_PROJECT_DIR=str(P))[0] == 0
    rc, out = run(lone, P, H, "end", "--rating", "3", "--improve", "tool --password " + _v())
    assert rc == 0, out
    assert "Feedback saved (redacted)" not in out
    assert "redaction unavailable" in out
    fb = json.loads(next((H / ".aid" / "feedback" / "pending").glob("*.json")).read_text(encoding="utf-8"))
    assert fb["to_improve"] == "[not stored: redaction unavailable]"


# ---------------------------------------------------------------------------
# T17-16: init writes the one schema (I-10 / I-21)
# ---------------------------------------------------------------------------

I21_TYPES = {"$schema": str, "version": str, "last_updated": str, "current_task": type(None),
             "current_step": type(None), "progress": dict, "session_notes": list, "blockers": list}

RUN3_SHAPES = [
    {"current_task": {"id": "T1", "title": "Add tagging to notes", "current_step": "x", "progress": 40},
     "current_step": "Implement tags"},
    {"current_task": {"id": "T1", "title": "t"}, "blockers": ["Docker check denied"]},
    {"current_task": "T1", "current_step": {"name": "s"}, "blockers": {"a": 1}, "progress": "40%"},
]


def test_t17_16_init_writes_the_i21_document(probe):
    P, H = probe
    rc, out = sess(P, H, "init", "1", "0", CLAUDE_PROJECT_DIR=str(P))
    assert rc == 0, out
    ctx = json.loads((P / ".aid" / "context.json").read_text(encoding="utf-8"))
    assert list(ctx) == list(I21_TYPES)
    for k, t in I21_TYPES.items():
        assert isinstance(ctx[k], t), k
    assert ctx["$schema"] == "aid-context-v1" and ctx["version"] == "1.0"
    assert ctx["progress"] == {"steps_completed": [], "steps_pending": []}
    assert ctx["session_notes"] == [] and ctx["blockers"] == []


def test_t17_16_context_schema_doc_has_the_same_key_set():
    doc = REPO_ROOT / "skills" / "context-tracking" / "references" / "context-schema.md"
    text = doc.read_text(encoding="utf-8") if doc.is_file() else ""
    blocks = [b for b in re.findall(r"```json\n(.*?)```", text, re.S) if '"current_task"' in b]
    if "aid-context-v1" not in text or not blocks:
        pytest.skip("WS-C T17-26 (context-schema.md rewrite) has not landed")
    example = json.loads(blocks[0])
    assert set(example) == set(I21_TYPES)


@pytest.mark.parametrize("shape", range(len(RUN3_SHAPES)))
def test_t17_16_existing_context_is_byte_identical_after_init_and_repair(probe, shape):
    P, H = probe
    (P / ".aid").mkdir()
    ctx = P / ".aid" / "context.json"
    raw = json.dumps(RUN3_SHAPES[shape], indent=2).encode("utf-8")
    ctx.write_bytes(raw)
    rc, out = sess(P, H, "init", "developer", "1", CLAUDE_PROJECT_DIR=str(P))
    assert rc == 0, out
    assert ctx.read_bytes() == raw
    (P / ".aid" / "state.json").write_text("{not json", encoding="utf-8")
    rc, out = sess(P, H, "init", "developer", "1", "--repair")
    assert rc == 0, out
    assert ctx.read_bytes() == raw


# ---------------------------------------------------------------------------
# T17-17: the checklist subcommand; approve prints it (I-22)
# ---------------------------------------------------------------------------

def _items(phase):
    """PHASE_CHECKLISTS read from the source (importing aid_session would reconfigure this
    process's stdout)."""
    import ast
    tree = ast.parse(SESSION.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "PHASE_CHECKLISTS"
                                                for t in node.targets):
            return ast.literal_eval(node.value)[phase]
    raise AssertionError("PHASE_CHECKLISTS not found in aid_session.py")


PHASE0_ITEMS = ["Research folder `docs/research/YYYY-MM-DD-<project>/` exists",
                "`research-report.md` states the problem",
                "Stakeholders and success metrics identified",
                "Go / no-go decision recorded"]


def _to_phase(P, H, n):
    assert sess(P, H, "init", "developer", "0", CLAUDE_PROJECT_DIR=str(P))[0] == 0
    for _ in range(n):
        assert sess(P, H, "approve")[0] == 0
        assert sess(P, H, "advance")[0] == 0


def test_t17_17_phase0_has_the_four_new_items():
    assert _items(0) == PHASE0_ITEMS


def test_t17_17_phases_1_to_5_are_the_phase_approve_items_verbatim():
    """I-22: phases 1-5 are commands/phase-approve.md:94-118 at 11371b8, verbatim."""
    git = shutil.which("git")
    p = subprocess.run([git, "-C", str(REPO_ROOT), "show", "11371b8:commands/phase-approve.md"],
                       capture_output=True, text=True, encoding="utf-8") if git else None
    if p is None or p.returncode != 0:
        pytest.skip("commit 11371b8 is not available in this checkout")
    section = p.stdout.split("## Phase Checklists", 1)[1].split("\n## ", 1)[0]
    blocks = re.split(r"\n### Phase (\d):[^\n]*\n", section)
    found = {int(blocks[i]): re.findall(r"^- \[ \] (.+)$", blocks[i + 1], re.M)
             for i in range(1, len(blocks), 2)}
    assert sorted(found) == [1, 2, 3, 4, 5]
    for n in range(1, 6):
        assert _items(n) == found[n], n


@pytest.mark.parametrize("phase", range(6))
def test_t17_17_checklist_text_and_json_for_every_phase(probe, phase):
    P, H = probe
    _to_phase(P, H, phase)
    folder = {0: "docs/research", 1: "docs/prd", 2: "docs/tech-spec", 3: "docs/implementation-plan"}
    if phase in folder:
        (P / folder[phase] / "sub").mkdir(parents=True)
        (P / folder[phase] / "sub" / "a.md").write_text("x", encoding="utf-8")
    else:
        (P / ".aid" / "qa").mkdir(parents=True, exist_ok=True)
        for t in ("T-1", "T-2"):
            (P / ".aid" / "qa" / (t + ".yaml")).write_text("c: 1\n", encoding="utf-8")
        assert sess(P, H, "qa-pass", "T-1")[0] == 0
    before = _dir_digest(P)
    rc, out = sess(P, H, "checklist")
    assert rc == 0, out
    lines = out.splitlines()
    assert lines[0] == "## Phase {} Summary".format(phase)
    assert lines[1].startswith("Phase: {} (".format(phase)) and "| Approved: no | Feedback: no" in lines[1]
    assert lines[3] == "## Phase {} Checklist".format(phase)
    assert lines[4:] == ["- [ ] " + i for i in _items(phase)]
    if phase in folder:
        assert lines[2] == "Documents: {}/sub/a.md".format(folder[phase])
    else:
        assert lines[2] == "Documents: T-1 (qa_passed: yes), T-2 (qa_passed: no)"
    rc, js = sess(P, H, "checklist", "--format", "json", "--phase", str(phase))
    assert rc == 0, js
    data = json.loads(js)
    assert data["phase"] == phase and data["checklist"] == _items(phase)
    assert {"phase", "phase_name", "role", "approved", "feedback", "documents"} <= set(data["summary"])
    assert _dir_digest(P) == before, "checklist writes nothing"


def test_t17_17_other_phase_and_none_found(probe):
    P, H = probe
    _to_phase(P, H, 0)
    rc, out = sess(P, H, "checklist", "--phase", "2")
    assert rc == 0, out
    assert out.splitlines()[2] == "Documents: none found"
    assert "## Phase 2 Checklist" in out


def test_t17_17_no_state_exits_1_with_the_init_hint(probe):
    P, H = probe
    before = _dir_digest(P)
    rc, out = sess(P, H, "checklist")
    assert rc == 1
    assert "AID is not initialized here (run /aid-init)" in out
    assert _dir_digest(P) == before


def test_t17_17_approve_prints_the_block_before_it_writes(probe):
    P, H = probe
    _to_phase(P, H, 1)
    rc, expected = sess(P, H, "checklist")
    assert rc == 0
    rc, out = sess(P, H, "approve", "--note", "rating 4 fine")
    assert rc == 0, out
    assert out.startswith(expected.rstrip("\n")), out
    assert out.index("## Phase 1 Checklist") < out.index("approved.")
    assert state_of(P)["phase_approved"] is True


# ---------------------------------------------------------------------------
# T17-20: gate.mjs records the review result and the cost (I-23), from python
# ---------------------------------------------------------------------------

NODE = shutil.which("node")


def _gate(root, home, *args):
    p = subprocess.run([NODE, str(GATE), *args, "--root", str(root)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=_env(home), timeout=60)
    return p.returncode, p.stdout + p.stderr


@pytest.fixture
def pipe_root(tmp_path):
    if not NODE:
        pytest.skip("node is not installed")
    root = tmp_path / "proj"
    (root / ".aid" / "pipeline").mkdir(parents=True)
    cfg = {"max_iterations": {"code_review": 5, "test_review": 5, "visual_qa": 5, "phase_gate_reexamine": 5},
           "thresholds": {"code_review_pass": 9.5, "test_review_pass": 9.5, "visual_qa_pass": 7,
                          "auto_fail_on_critical_security": True}}
    (root / ".aid" / "pipeline" / "config.json").write_text(json.dumps(cfg), encoding="utf-8")
    home = tmp_path / "H"
    home.mkdir()
    return root, home


def _pstate(root):
    return json.loads((root / ".aid" / "pipeline" / "state.json").read_text(encoding="utf-8"))


USAGE = json.dumps({"input_tokens": 4000, "output_tokens": 2000})
USD = 4000 / 1e6 * 5 + 2000 / 1e6 * 25


def test_t17_20_usage_is_recorded_and_accumulates(pipe_root):
    root, home = pipe_root
    rc, out = _gate(root, home, "--step", "CODE_REVIEW", "--scores", '{"overall":9.6}', "--usage", USAGE)
    assert rc == 0, out
    s = _pstate(root)
    assert s["last_review_result"]["step"] == "CODE_REVIEW"
    assert s["last_review_result"]["result"] == "PASS"
    assert s["cost"]["total_input_tokens"] == 4000
    assert abs(s["cost"]["estimated_cost_usd"] - USD) < 1e-12
    assert s["cost"]["per_step"]["CODE_REVIEW"]["estimated"] is False
    _gate(root, home, "--step", "CODE_REVIEW", "--scores", '{"overall":9.6}', "--usage", USAGE)
    s = _pstate(root)
    assert s["cost"]["total_output_tokens"] == 4000
    assert abs(s["cost"]["estimated_cost_usd"] - 2 * USD) < 1e-12


def test_t17_20_no_usage_is_estimated(pipe_root):
    root, home = pipe_root
    assert _gate(root, home, "--step", "TEST_REVIEW", "--scores", '{"overall":9.6}')[0] == 0
    s = _pstate(root)
    assert s["cost"]["per_step"]["TEST_REVIEW"]["estimated"] is True and s["cost"]["estimated_cost_usd"] > 0


@pytest.mark.parametrize("bad", ["[1]", '{"input_tokens":-5,"output_tokens":1}', "nope"])
def test_t17_20_bad_usage_and_dry_run_write_nothing(pipe_root, bad):
    root, home = pipe_root
    rc, out = _gate(root, home, "--step", "CODE_REVIEW", "--scores", '{"overall":9.6}', "--usage", bad)
    assert rc == 3, out
    assert not (root / ".aid" / "pipeline" / "state.json").exists()
    rc, out = _gate(root, home, "--step", "CODE_REVIEW", "--scores", '{"overall":9.6}', "--usage", USAGE,
                    "--dry-run")
    assert rc == 0, out
    assert not (root / ".aid" / "pipeline" / "state.json").exists()


def test_t17_20_skill_md_has_no_prompt_only_cost_step():
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "**Update cost tracking**" not in text
    assert "Extract token counts from the sub-agent's response metadata" not in text
    assert "--usage" in text and "No agent writes `cost` or `last_review_result` itself" in text


# ---------------------------------------------------------------------------
# T17-21: the pipeline skill resolves reviewers and criteria plugin-first (I-19)
# ---------------------------------------------------------------------------

BANNED = [re.compile(r"(?i)project-first"),
          re.compile(r"(?i)overrides it"),
          re.compile(r"(?i)project[^.\n]{0,60}\boverrides\b"),
          re.compile(r"(?i)\(fallback:?\s*[`\"]?[a-z-]+-agent"),
          re.compile(r"Accepted risk \(T10 A3\)")]


def _skill_md_files():
    return [p for p in SKILL_DIR.rglob("*.md")
            if "test-data-factories" not in p.name and "tdd-patterns" not in p.name]


def test_t17_21_no_banned_phrase_under_the_pipeline_skill():
    hits = []
    for p in _skill_md_files():
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            for rx in BANNED:
                if rx.search(line):
                    hits.append("{}:{}: {}".format(p.relative_to(REPO_ROOT).as_posix(), n, line.strip()[:120]))
    assert not hits, "\n".join(hits)


def test_t17_21_spawns_plugin_names_and_additive_criteria():
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    for agent in ("code-review-agent", "test-review-agent", "visual-qa-agent", "qa-validator-agent"):
        assert 'subagent_type: "aid:{}"'.format(agent) in text, agent
    for m in re.finditer(r'subagent_type: "([^"]+)"', text):
        assert m.group(1).startswith("aid:"), m.group(0)
    assert "this linked project's .claude/agents is AID's linked folder" in text
    assert "project files may only add criteria, never replace the plugin's agents or criteria" in text
    assert "F4 (2026-11-20)" in text
    assert "may only add criteria" in text
    ext = (SKILL_DIR / "SKILL.extended.md").read_text(encoding="utf-8")
    assert "`aid:code-review-agent`" in ext and "`aid:qa-validator-agent`" in ext


def test_t17_21_code_standards_step_appends_project_criteria():
    """
    WHY THIS TEST (C-R1-01, fix cycle 1):
    - PROBLEM: the step that builds {{CODE_STANDARDS}} said "(project .claude/skills/code-review/
      SKILL.md if present)", which reads as using the project file INSTEAD of the plugin standard.
    - SUCCESS: the plugin STANDARD.md is always read and a project file is only appended after it.
    """
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    step = [ln for ln in text.splitlines() if "{{CODE_STANDARDS}}" in ln and "STANDARD.md" in ln]
    assert len(step) == 1, step
    assert "append its criteria after it (never in place of it)" in step[0], step[0]
    assert "SKILL.md` if present)" not in step[0], step[0]


# --- T17-36 (pipeline skill part, WS-B): npx is pinned or no-install -------------------------

_NPX_OK = re.compile(r"npx (--no-install |-y [@\w/.-]+@\d[\w.]*|[@\w/.-]+@\d[\w.]*)")


def _bare_npx(text):
    return [m.start() for m in re.finditer(r"\bnpx ", text) if not _NPX_OK.match(text, m.start())]


def test_t17_36_pipeline_default_test_commands_use_no_install():
    """
    WHY THIS TEST:
    - PROBLEM: a bare `npx playwright test` default fetches and runs a registry package when the
      project has none installed (U-18).
    - SUCCESS: every npx in config.default.json test_commands is --no-install or exactly pinned,
      and the SKILL tables document the same default.
    """
    cfg = json.loads((SKILL_DIR / "config.default.json").read_text(encoding="utf-8"))
    cmds = cfg["test_commands"]
    assert cmds["e2e"] == "npx --no-install playwright test", cmds
    assert all(not _bare_npx(v) for v in cmds.values()), cmds
    assert "| `test_commands.e2e` | `npx --no-install playwright test` |" in (
        SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "`npx --no-install playwright test` (e2e)" in (
        SKILL_DIR / "SKILL.extended.md").read_text(encoding="utf-8")


def test_t17_36_no_bare_npx_under_the_pipeline_skill():
    hits = []
    for p in sorted(SKILL_DIR.rglob("*")):
        if p.is_file() and p.suffix in (".md", ".json"):
            text = p.read_text(encoding="utf-8")
            for pos in _bare_npx(text):
                hits.append("{}: {}".format(p.relative_to(REPO_ROOT).as_posix(),
                                            text[pos:pos + 60].splitlines()[0]))
    assert not hits, "\n".join(hits)
