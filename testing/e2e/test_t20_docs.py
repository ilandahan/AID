"""
T20 WS-D (3.1.1 backlog, HANDOFF 2026-11-22 items 1, 2, 4, 5, 7 and 3.1 audit lows a/b, plus the
SECURITY-MODEL redaction bullet): shipped command, agent and skill text says what the 3.0.9 gate
run and the 3.1 audit found missing.

WHY THIS TEST:
- PROBLEM: gate run 4 saw /aid:phase-approve skip the Summary and Checklist in its reply, context
  writers invent timestamps, /aid:aid-test --quick end without report.md, agent tests expect what
  the design cannot produce (a fixed reflection phrase, a test agent running the human-only gate,
  QA paths outside the test folder), gate-check list Phase 3 items the code does not check, and
  the PRD flow leave golden-set de-identification and a secret scanner unsaid.
- COST OF FAILURE: a human signs off on nothing shown, context files carry made-up times, agent
  tests fail for reasons that are not defects, and real data reaches the repository.
- SUCCESS: each statement below is pinned to the file that makes it; the gate-check table and
  the redaction bullet are checked against the code that defines them.
"""
import importlib.util
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def read(rel):
    return (REPO / rel).read_text(encoding="utf-8")


def flat(rel):
    """Text with whitespace collapsed, so a phrase may wrap across lines."""
    return " ".join(read(rel).split())


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, str(REPO / rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- #1 phase-approve: the Summary and Checklist are assistant text before the approve call ---

def test_t20_1_phase_approve_summary_is_reply_text_before_approve():
    f = flat("commands/phase-approve.md")
    assert ("write `## Phase N Summary` and `## Phase N Checklist` as assistant text in your reply"
            " BEFORE the `approve` call") in f
    assert "The `checklist` tool output alone does not count" in f


def test_t20_1_phase_approve_has_a_reply_example_block():
    t = read("commands/phase-approve.md")
    m = re.search(r"Example reply text \(before any `approve` call\):\s*```\n(.*?)```", t, re.S)
    assert m, "example block missing"
    block = m.group(1)
    assert "## Phase 2 Summary" in block and "## Phase 2 Checklist" in block
    assert "evidence:" in block and "not done:" in block


# --- #2 context writers: time only from the hook line, else null ---

def test_t20_2_context_writers_take_time_from_the_hook_line():
    for rel in ("commands/context-update.md", "commands/good-morning.md", "skills/context-tracking/SKILL.md"):
        f = flat(rel)
        assert "`Current time (UTC): ...`" in f, rel
        assert "Never invent a time" in f, rel
        assert "write `null`" in f, rel


def test_t20_2_good_morning_session_id_from_the_hook_line():
    f = flat("commands/good-morning.md")
    assert "`session_id` from the date in that line" in f


# --- #4 aid-test: the parent writes report.md when the sub-agent did not ---

def test_t20_4_aid_test_parent_writes_missing_report():
    f = flat("commands/aid-test.md")
    assert ("If `.aid/test-outputs/test-{timestamp}/report.md` does not exist, write it yourself"
            " from the result the sub-agent returned") in f
    assert "`--quick` included" in f


def test_t20_4_agent_and_command_name_the_same_report():
    """The sub-agent must write the file the command checks for (gate run 4: report.md missing)."""
    assert "COMPLETE-TEST-REPORT" not in read("agents/aid-test-agent.md")
    assert "/report.md" in read("agents/aid-test-agent.md")


# --- #3 docs half: memory lists come from the redacting CLI, never from slots.json ---

def test_t20_3_memory_lists_use_the_redacting_cli():
    f = flat("commands/aid-memory.md")
    assert "ONLY from the output of `python -m memory_system --memories`" in f
    assert "Never Read `slots.json` directly" in f
    for rel in ("skills/memory-system/SKILL.md", "skills/memory-system/SKILL.extended.md"):
        line = next(l for l in read(rel).splitlines() if l.startswith("{{MEMORY_ENTRIES}}"))
        assert "python -m memory_system --memories" in line and "never Read slots.json" in line, rel


# --- #5 test expectations match the design ---

def test_t20_5_reflection_test_does_not_require_a_fixed_phrase():
    f = flat("commands/test-reflection.md")
    assert "revision_guidance includes 'Add WHY header'" not in f
    assert "do not require a fixed phrase" in f
    # what the rubric actually scores (agents/reflection-agent.md Evaluation Criteria)
    rubric = flat("agents/reflection-agent.md")
    assert "| WHY Alignment | 3 |" in rubric and "| Completeness | 2 |" in rubric
    assert "`why_alignment` or `completeness`" in f


def test_t20_5_test_all_agents_lists_human_only_steps_as_not_run():
    f = flat("commands/test-all-agents.md")
    assert "- Phase gates enforced" not in f
    assert "Gate rules reported; human-only steps" in f and "listed as not run" in f


def test_t20_5_qa_template_paths_are_inside_the_test_folder():
    t = read("agents/aid-test-agent.md")
    paths = []
    for m in re.finditer(r"^files_to_review:\n((?:  - .*\n)+)", t, re.M):
        paths += re.findall(r'  - "([^"]+)"', m.group(1))
    assert paths, "no files_to_review lists"
    tree = re.search(r"├── phase-4/[^\n]*\n((?:│   [^\n]*\n)+)", t).group(1)
    for p in paths:
        assert p.startswith(".aid/test-outputs/test-{{TIMESTAMP}}/phase-4/"), p
        assert p.rsplit("/", 1)[1] in tree, p


# --- #7 gate-check Phase 3 table follows aid_session.PHASE_CHECKLISTS[3] ---

def test_t20_7_gate_check_phase3_matches_the_code():
    sys.path.insert(0, str(REPO / "hooks"))
    try:
        items = _load("aid_session_t20", "hooks/aid_session.py").PHASE_CHECKLISTS[3]
    finally:
        sys.path.pop(0)
    t = read("commands/gate-check.md")
    sec = re.search(r"### Phase 3: [^\n]*\n(.*?)\n### ", t, re.S).group(1)
    rows = [r.split("|")[1].strip() for r in sec.splitlines() if r.startswith("|")][2:]
    assert rows == list(items)


# --- 3.1 audit lows ---

def test_t20_a_golden_set_deidentification_is_a_pm_signoff():
    for rel in ("skills/aid-prd/SKILL.md", "skills/aid-prd/SKILL.extended.md"):
        f = flat(rel)
        assert "`tests/evals/golden/`" in f, rel
        assert ("golden-set de-identification is a PM sign-off item, as for SEED-EVALS"
                " (\"De-identification checked by: [PM], [date]\" at the top of each golden"
                " file") in f, rel


def test_t20_b_prd_suggests_a_precommit_secret_scanner():
    f = flat("commands/prd.md")
    assert ("Suggest a pre-commit secret scanner (for example gitleaks) over"
            " `docs/prd/SEED-EVALS-*.md` and `tests/evals/golden/`") in f


# --- SECURITY-MODEL: the redaction bullet names only spellings redact() still misses ---------

def _redaction_bullet():
    f = flat("docs/SECURITY-MODEL.md")
    start = f.index("**The audit log's secret redaction is best effort.**")
    return f[start:f.index("- **", start + 5)]


def test_t20_8_redaction_bullet_matches_the_redactor():
    redact = _load("redact_t20", "memory-system/memory_system/redact.py").redact
    v = "Zq" + "9xW" + "pLm4"            # digit + mixed case: secret-shaped
    low = "zq" + "xwplmkr"               # lower case only
    caught = {                            # dropped from the bullet: redact() catches them now
        "gpg --passphrase": f"gpg --batch --passphrase {v} -d f",
        "`Cookie:` header": f"curl -H 'Cookie: sid={v}' host",
        "`docker login -p <value>`": f"docker login -u me -p {v} reg",
        "`redis-cli -a <value>`": f"redis-cli -a {v} ping",
    }
    missed = {                            # still named in the bullet: redact() misses them
        "`docker login -pV`": f"docker login -u me -p{v}",
        "`openssl -kV`": f"openssl enc -k{v}",
        "`redis-cli -aV`": f"redis-cli -a{v} ping",
        "`token` / `api_key` / `mysql -p`": f"token {low}",
        "`password V`": f"password {v}",
        "`access_token V`": f"access_token {v}",
        "`curl -b`": f"curl -b sid={v} host",
        "`openssl -K`": f"openssl enc -K {v}",
        "`htpasswd -nb`": f"htpasswd -nb me {v}",
        "`REDISCLI_AUTH=V`": f"REDISCLI_AUTH={v}",
    }
    b = _redaction_bullet()
    for name, cmd in caught.items():
        assert v not in redact(cmd), name
        assert name not in b, name
    for name, cmd in missed.items():
        assert (v in redact(cmd)) or (low in redact(cmd)), name
        assert name in b, name
