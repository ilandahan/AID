"""
T21 docs: the pipeline $ brake is code, and the shipped text says so.

WHY THIS TEST:
- PROBLEM: SKILL.md told the agent to stop at cost_limits.max_per_run_usd; T21 moved that into
  gate.mjs (running total = max(cost-ledger.json, state.cost), ESCALATE at the limit) and made the
  ledger a control file. Docs that still describe an agent-obeyed limit, or name a ledger path or
  limit key the code does not use, mislead the user about what stops a run.
- COST OF FAILURE: a user trusts a brake the docs misdescribe, or an agent keeps "deciding" a stop
  the gate already made.
- SUCCESS: each claim is pinned to the file that makes it, and the cheap ones are checked against
  the code: the limit keys exist in config.default.json, the ledger path is in gate.mjs and in
  aid_guard.PROTECTED_SUFFIXES (not DENY_RULES), and a real gate run escalates as documented.
"""
import importlib.util
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GATE = REPO / "skills/pipeline-orchestrator/gate.mjs"
LEDGER = ".aid/pipeline/cost-ledger.json"


def read(rel):
    return (REPO / rel).read_text(encoding="utf-8")


def flat(rel):
    return " ".join(read(rel).split())


def _guard():
    spec = importlib.util.spec_from_file_location("aid_guard_t21docs", str(REPO / "hooks/aid_guard.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_t21_skill_says_the_gate_enforces_the_brake():
    f = flat("skills/pipeline-orchestrator/SKILL.md")
    assert "### Cost Limits (enforced by gate.mjs, T21)" in f
    assert "sets the running total to `max(ledger, state.cost)`" in f
    assert "Returns ESCALATE (exit 2) whatever the score" in f
    assert "`cost_brake: true`" in f
    assert "Prints `gate: cost warning:" in f
    assert "a new task does not reset it" in f
    # the old agent-obeyed wording is gone
    assert "Continue? (y/n)" not in f
    assert "If cost limit hit during iteration" not in f


def test_t21_security_model_lists_the_ledger_and_its_limit():
    f = flat("docs/SECURITY-MODEL.md")
    assert "the pipeline's cost ledger `.aid/pipeline/cost-ledger.json`" in f
    assert "deliberately not in the layer A deny rules" in f
    assert "from Phase 4 code (a Node or Python script) can still edit or delete it" in f
    assert "`--root` pointing elsewhere starts a new ledger there" in f


def test_t21_pipeline_status_names_the_brake_total():
    f = flat("commands/pipeline-status.md")
    assert "from `max(cost ledger, cost.estimated_cost_usd)` (T21;" in f
    # T21b: both homes are named, and match the paths gate.mjs uses
    assert "`.git/aid/<project key>/cost-ledger.json`" in f and "`.aid/pipeline/cost-ledger.json`" in f
    assert 'dir, "aid", key, "cost-ledger.json"' in read("skills/pipeline-orchestrator/gate.mjs")


def test_t21_documented_names_match_the_code():
    lim = json.loads(read("skills/pipeline-orchestrator/config.default.json"))["cost_limits"]
    assert lim["warn_at_usd"] == 25 and lim["max_per_run_usd"] == 50   # the defaults SKILL.md states
    assert f'const LEDGER_FILE = "{LEDGER}";' in read("skills/pipeline-orchestrator/gate.mjs")
    g = _guard()
    assert "/" + LEDGER in g.PROTECTED_SUFFIXES
    assert not any("cost-ledger" in r for r in g.DENY_RULES)


def _gate(root):
    return subprocess.run(
        ["node", str(GATE), "--step", "CODE_REVIEW", "--scores", '{"overall":9.6}',
         "--usage", '{"input_tokens":10000,"output_tokens":2000}', "--root", str(root)],
        capture_output=True, text=True, encoding="utf-8", timeout=60)


def test_t21_gate_behaves_as_documented(tmp_path):
    cfg = json.loads(read("skills/pipeline-orchestrator/config.default.json"))
    cfg["cost_limits"].update(warn_at_usd=0.05, max_per_run_usd=0.15)   # each call costs $0.10
    pipe = tmp_path / ".aid" / "pipeline"
    pipe.mkdir(parents=True)
    (pipe / "config.json").write_text(json.dumps(cfg), encoding="utf-8")

    r1 = _gate(tmp_path)                                  # $0.10: warns only
    assert r1.returncode == 0, r1.stdout + r1.stderr
    assert "gate: cost warning: $0.10" in r1.stdout
    assert not (pipe / "ESCALATION.json").exists()

    # zeroing state.cost does not lower the total: the ledger still holds $0.10
    st = json.loads((pipe / "state.json").read_text(encoding="utf-8"))
    st["cost"]["estimated_cost_usd"] = 0
    (pipe / "state.json").write_text(json.dumps(st), encoding="utf-8")

    r2 = _gate(tmp_path)                                  # $0.20 >= $0.15: brake
    assert r2.returncode == 2, r2.stdout + r2.stderr
    assert "ESCALATE (cost brake: $0.20" in r2.stdout
    esc = json.loads((pipe / "ESCALATION.json").read_text(encoding="utf-8"))
    assert esc["status"] == "open" and esc["cost_brake"] is True
