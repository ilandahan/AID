"""
T14 (T14-agentic-layer-acceptance.md): AID 3.1, the agentic layer.

WHY: no phase, role or gate in AID asked whether an agent is the right solution shape, on
whose behalf it acts, what it may never do, how we know it is good enough (evals), what it
did (traces), or how it is rolled out safely. These tests check that each phase and role now
carries its agentic step, under the shared names, and that the gates check them.
"""
import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
SK = REPO / "skills"
SEVEN_A = ["7A.1 Charter", "7A.2 Tools & Permissions", "7A.3 Context & Data",
           "7A.4 Failure Modes & Guardrails", "7A.5 Why-Chain", "7A.6 Eval Plan",
           "7A.7 Telemetry & Traces", "7A.8 Rollout & Kill Switch"]
LADDER = ["Process change", "automation", "Single LLM call", "Workflow", "Agent", "Multi-agent"]


def text(*parts):
    """Concatenated, whitespace-normalised, lower-cased text of the given files."""
    out = []
    for rel in parts:
        p = REPO / rel
        out.append(p.read_text(encoding="utf-8"))
    return " ".join(" ".join(out).split()).lower()


def skill(name):
    files = [f"skills/{name}/SKILL.md"]
    if (SK / name / "SKILL.extended.md").exists():
        files.append(f"skills/{name}/SKILL.extended.md")
    files += [str(p.relative_to(REPO)) for p in (SK / name / "references").glob("*.md")] \
        if (SK / name / "references").is_dir() else []
    return text(*files)


# --- T14-1: PRD -------------------------------------------------------------------------

PRD_TEMPLATE = "skills/aid-prd/references/prd-template-extended.md"


def test_t14_1_prd_template_has_solution_shape_with_the_ladder():
    t = (REPO / PRD_TEMPLATE).read_text(encoding="utf-8")
    assert re.search(r"^#+\s*1\.5\s+Solution Shape", t, re.M), "§1.5 Solution Shape heading"
    low = " ".join(t.split()).lower()
    for level, name in enumerate(LADDER):
        assert name.lower() in low, name
    assert "lowest" in low and "multi-agent" in low


@pytest.mark.parametrize("q", ["enumerat", "vary", "cost", "reversible", "unstructured", "latency", "approve"])
def test_t14_1_prd_template_has_the_six_intake_questions(q):
    low = " ".join((REPO / PRD_TEMPLATE).read_text(encoding="utf-8").split()).lower()
    sec = low[low.index("1.5 solution shape"):]
    assert q in sec[:6000], q


def test_t14_1_prd_template_has_section_7a_with_all_subsections():
    t = (REPO / PRD_TEMPLATE).read_text(encoding="utf-8")
    assert re.search(r"^##\s*7A\.?\s+Agentic Design", t, re.M), "## 7A. Agentic Design"
    for sub in SEVEN_A:
        assert re.search(r"^###\s*" + re.escape(sub), t, re.M), sub


def test_t14_1_prd_template_scales_every_section_by_level_and_never_na():
    low = " ".join((REPO / PRD_TEMPLATE).read_text(encoding="utf-8").split()).lower()
    sec = low[low.index("7a. agentic design") if "7a. agentic design" in low else low.index("7a agentic design"):]
    assert sec.count("scaling by level") >= 8 or sec.count("by level") >= 8
    assert "n/a" in sec and ("not n/a" in sec or "no section is n/a" in sec or "never n/a" in sec
                              or "no \"n/a\"" in sec or "never \"n/a\"" in sec)


@pytest.mark.parametrize("item", ["golden set", "red-team", "never-do", "threshold", "judge", "human label"])
def test_t14_1_eval_plan_items(item):
    low = " ".join((REPO / PRD_TEMPLATE).read_text(encoding="utf-8").split()).lower()
    sec = low[low.index("7a.6 eval plan"):low.index("7a.7 telemetry")]
    assert item in sec, item


@pytest.mark.parametrize("item", ["shadow", "human approval", "autonomous", "kill switch", "on-call", "entry", "exit"])
def test_t14_1_rollout_items(item):
    low = " ".join((REPO / PRD_TEMPLATE).read_text(encoding="utf-8").split()).lower()
    sec = low[low.index("7a.8 rollout"):]
    assert item in sec[:5000], item


def test_t14_1_success_metrics_need_a_guardrail():
    low = " ".join((REPO / PRD_TEMPLATE).read_text(encoding="utf-8").split()).lower()
    assert "north star" in low and "guardrail" in low


def test_t14_1_why_chain_rule_in_prd_and_why_skill():
    for low in (skill("aid-prd"), skill("why-driven-decision")):
        assert "why-chain" in low and "requirement" in low and "eval" in low and "metric" in low
        assert "opinion" in low


def test_t14_1_prd_skill_checklist_names_the_sections():
    low = text("skills/aid-prd/SKILL.md")
    assert "1.5" in low and "7a" in low and "guardrail" in low


# --- T14-0, 2-6: phases and roles ---------------------------------------------------------

@pytest.mark.parametrize("name, needles", [
    ("aid-discovery", ["solution shape", "vary", "cost of an error"]),
    ("aid-tech-spec", ["agent architecture", "permission", "trace", "eval harness", "kill switch",
                       "cost", "fallback"]),
    ("system-architect", ["least privilege", "kill switch", "trace"]),
    ("aid-impl-plan", ["golden set", "eval", "red-team", "telemetry", "rollout", "kill switch",
                       "definition of done"]),
    ("aid-development", ["eval", "before", "trace", "version", "regression"]),
    ("test-driven", ["eval", "golden set", "threshold", "judge"]),
    ("aid-qa-ship", ["release gate", "red-team", "shadow", "kill switch", "drift", "escalation rate"]),
    ("role-product-manager", ["charter", "why-chain", "guardrail"]),
    ("role-tech-lead", ["solution shape", "lowest", "permission"]),
    ("role-developer", ["eval", "trace", "version"]),
    ("role-qa-engineer", ["golden set", "red-team", "judge"]),
    ("role-data-scientist", ["judge", "calibrat", "drift"]),
])
def test_t14_phase_and_role_skills_carry_their_agentic_step(name, needles):
    low = skill(name)
    missing = [n for n in needles if n not in low]
    assert missing == [], (name, missing)


def test_t14_multi_agent_needs_one_of_four_justifications():
    low = skill("aid-prd") + skill("aid-tech-spec")
    for j in ("permission", "contaminat", "parallel", "team"):
        assert j in low, j


def test_t14_untrusted_content_is_linked_from_failure_modes_or_qa():
    low = skill("aid-prd") + skill("role-qa-engineer")
    assert "untrusted-content" in low


# --- T14-7: gates and reviewers -----------------------------------------------------------

CRITERIA = sorted((SK / "reflection" / "criteria").glob("phase-*.yaml"))


@pytest.mark.parametrize("path", CRITERIA, ids=lambda p: p.name)
def test_t14_7_reflection_criteria_stay_valid_yaml(path):
    yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("phase, needles", [
    ("phase-0-discovery.yaml", ["solution shape"]),
    ("phase-1-prd.yaml", ["7a", "why-chain", "guardrail"]),
    ("phase-2-tech-spec.yaml", ["trace", "kill switch"]),
    ("phase-3-impl-plan.yaml", ["eval"]),
    ("phase-4-development.yaml", ["eval"]),
    ("phase-5-qa-ship.yaml", ["release gate", "kill switch"]),
])
def test_t14_7_reflection_criteria_check_the_agentic_layer(phase, needles):
    low = text(f"skills/reflection/criteria/{phase}")
    missing = [n for n in needles if n not in low]
    assert missing == [], (phase, missing)


@pytest.mark.parametrize("agent, needles", [
    ("phase-review-agent", ["solution shape", "7a", "eval", "kill switch"]),
    ("prd-validator", ["1.5", "7a.1", "7a.8", "why-chain", "guardrail", "n/a"]),
    ("phase2-techspec-pm-reviewer", ["7a", "trace"]),
])
def test_t14_7_reviewer_agents_check_it(agent, needles):
    low = text(f"agents/{agent}.md")
    missing = [n for n in needles if n not in low]
    assert missing == [], (agent, missing)


# --- T14-8: docs ----------------------------------------------------------------------------

def test_t14_8_docs_describe_the_agentic_layer():
    assert "agentic projects" in text("README.md") and "3.1" in text("README.md")
    assert "7a" in text("docs/PHASE-GATES.md") and "solution shape" in text("docs/PHASE-GATES.md")


# --- Review round 1: exact wording, consistency, canonical rules ---------------------------

LADDER_ROWS = {0: "Process change", 1: "Deterministic automation", 2: "Single LLM call",
               3: "Workflow", 4: "Agent", 5: "Multi-agent"}
SIX_QUESTIONS = ["Can every path be enumerated in advance?",
                 "How much does the problem vary from case to case?",
                 "What does an error cost, and is it reversible?",
                 "Does it need judgement over unstructured input?",
                 "What latency and cost budget is there?",
                 "Who must approve actions?"]
SHIPPED = [p for d in ("skills", "agents", "docs") for p in (REPO / d).rglob("*.md")] + \
          [REPO / "README.md", REPO / "CLAUDE.md"] + sorted((SK / "reflection" / "criteria").glob("*.yaml"))


def test_t14_review_ladder_levels_pair_with_their_exact_names():
    t = (REPO / PRD_TEMPLATE).read_text(encoding="utf-8")
    for n, name in LADDER_ROWS.items():
        assert re.search(r"^\|\s*" + str(n) + r"\s*\|\s*" + re.escape(name), t, re.M), (n, name)


@pytest.mark.parametrize("q", SIX_QUESTIONS)
def test_t14_review_six_questions_verbatim(q):
    assert q in (REPO / PRD_TEMPLATE).read_text(encoding="utf-8"), q


def test_t14_review_7a_names_are_identical_everywhere():
    """A '7A.n <name>' mention anywhere must use the canonical name for n."""
    canon = {s.split(" ", 1)[0]: s.split(" ", 1)[1] for s in SEVEN_A}
    bad = []
    for p in SHIPPED:
        for m in re.finditer(r"7A\.([1-8])\s+([A-Z][A-Za-z&\- ]{3,40})", p.read_text(encoding="utf-8", errors="replace")):
            key = "7A." + m.group(1)
            first = canon[key].split()[0]
            if m.group(2).split()[0] in ("Charter", "Tools", "Context", "Failure", "Why-Chain", "Eval",
                                         "Telemetry", "Rollout") and not m.group(2).startswith(first):
                bad.append("{}: {} {}".format(p.relative_to(REPO), key, m.group(2)[:30]))
    assert bad == [], bad


def test_t14_review_rollout_stage_names_are_canonical():
    hits = ["{}".format(p.relative_to(REPO)) for p in SHIPPED
            if re.search(r"(?i)shadow\s*(→|->)\s*review\s*(→|->)\s*automatic", p.read_text(encoding="utf-8", errors="replace"))]
    assert hits == [], hits


def test_t14_review_canonical_judge_and_red_team_rules():
    low = " ".join((REPO / PRD_TEMPLATE).read_text(encoding="utf-8").split()).lower()
    sec = low[low.index("7a.6 eval plan"):low.index("7a.7 telemetry")]
    assert "kappa" in sec and "0.7" in sec and "50" in sec, "judge: kappa >= 0.7 on >= 50 cases"
    assert "critical" in sec and "ln(0.05)" in sec
    stale = []
    for p in SHIPPED:
        low_p = " ".join(p.read_text(encoding="utf-8", errors="replace").split()).lower()
        if re.search(r"100% red-team|≥\s*90% agreement|minimum \[?e\.g\. 90%", low_p):
            stale.append(str(p.relative_to(REPO)))
    assert stale == [], stale


def test_t14_review_no_stale_eight_section_tech_spec():
    hits = []
    for p in [REPO / "agents" / n for n in ("phase2-techspec-pm-reviewer.md", "phase2-techspec-synthesizer.md",
                                            "phase2-requirements-tracer.md")]:
        t = p.read_text(encoding="utf-8")
        if re.search(r"all 8 template sections|8-section|\"gate_items_total\":\s*8\b|8/8", t):
            hits.append(p.name)
    assert hits == [], hits


def test_t14_review_prd_skill_template_uses_the_real_headings():
    for rel in ("skills/aid-prd/SKILL.md", "skills/aid-prd/SKILL.extended.md"):
        t = (REPO / rel).read_text(encoding="utf-8")
        assert "1.5 Solution Shape" in t and re.search(r"7A\.", t), rel
        assert "## 5A." not in t, rel


def test_t14_review_research_report_has_the_shape_hypothesis():
    assert "solution shape hypothesis" in text("skills/pre-prd-research/SKILL.extended.md")
    assert "solution shape" in text("skills/pre-prd-research/SKILL.md")


def test_t14_review_raci_is_one_table_in_prd_and_roles():
    for rel in ("skills/aid-prd/SKILL.md", "skills/role-product-manager/SKILL.md", "skills/role-tech-lead/SKILL.md"):
        low = text(rel)
        assert "pm proposes" in low and "tech lead decides" in low, rel


def test_t14_review_release_gate_uses_the_held_out_split():
    for name in ("role-qa-engineer", "aid-development", "test-driven"):
        assert "held-out" in skill(name), name


def test_t14_review_lethal_trifecta_and_phase5_exit():
    assert "untrusted content" in skill("aid-prd") and "exfiltration" in skill("aid-prd")
    assert "exfiltration" in text("skills/aid-tech-spec/references/agent-architecture.md")
    low = skill("aid-qa-ship")
    assert "shadow live" in low or "shadow stage live" in low


# SKILL.md budget: none may grow above max(200, its 3.0.8 length).
BUDGET_308 = {"aid-discovery": 90, "aid-prd": 163, "aid-tech-spec": 114, "aid-impl-plan": 255,
              "aid-development": 160, "aid-qa-ship": 191, "test-driven": 239, "system-architect": 211,
              "why-driven-decision": 125, "role-product-manager": 65, "role-tech-lead": 98,
              "role-developer": 94, "role-qa-engineer": 260, "role-data-scientist": 237,
              "pre-prd-research": 163}


@pytest.mark.parametrize("name", sorted(BUDGET_308))
def test_t14_review_skill_md_within_budget(name):
    n = len((SK / name / "SKILL.md").read_text(encoding="utf-8").splitlines())
    assert n <= max(200, BUDGET_308[name]), (name, n)


# --- Amendment A9: the Phase 1 flow ----------------------------------------------------------

PHASE1_AGENTS = ("phase1-solution-shaper", "phase1-charter-drafter", "phase1-eval-planner")


@pytest.mark.parametrize("name", PHASE1_AGENTS)
def test_t14_a9_phase1_agents_exist_read_only(name):
    t = (REPO / "agents" / (name + ".md")).read_text(encoding="utf-8").replace("\r\n", "\n")
    head = t.split("---", 2)[1]
    assert re.search(r"^name:\s*" + re.escape(name) + r"\s*$", head, re.M)
    assert re.search(r"^tools:\s*Read, Grep, Glob\s*$", head, re.M), "draft-only agents are read-only"
    assert "rules/general/untrusted-content.md" in t


def test_t14_a9_solution_shaper_asks_the_six_questions_and_drafts_seed_evals():
    t = (REPO / "agents" / "phase1-solution-shaper.md").read_text(encoding="utf-8")
    for q in SIX_QUESTIONS:
        assert q in t, q
    low = " ".join(t.split()).lower()
    assert "seed eval" in low and "20" in low and "lowest" in low


def test_t14_a9_prd_command_fans_out_in_one_message():
    t = (REPO / "commands" / "prd.md").read_text(encoding="utf-8")
    low = " ".join(t.split()).lower()
    for a in ("prd-research-aggregator", "prd-writer", *PHASE1_AGENTS, "prd-validator"):
        assert "aid:" + a in t, a
    assert "parallel" in low and "one message" in low
    assert "seed-evals-" in low and "why-shape-brief" in low and "shaping session" in low
    assert "prd-template-extended.md" in t
    agg, fan = t.index("aid:prd-research-aggregator"), t.index("aid:phase1-solution-shaper")
    assert agg < fan < t.index("aid:prd-validator"), "aggregator, then fan-out, then validator"


def test_t14_a9_why_skill_has_the_agentic_lens_and_brief():
    low = skill("why-driven-decision")
    for q in SIX_QUESTIONS:
        assert q.lower() in low, q
    assert "why-shape-brief" in low and "hypothesis" in low
    assert "on whose behalf" in low and "never" in low


def test_t14_a9_prd_skill_describes_the_flow():
    low = skill("aid-prd")
    assert "shaping session" in low and "adr" in low and "seed-evals-" in low
    assert "in parallel" in low


def test_t14_a9_golden_set_does_not_block_design():
    low = skill("role-qa-engineer") + skill("aid-tech-spec")
    assert "in parallel" in low and "phase 5" in low
    assert "phase 4" in skill("role-data-scientist")


# --- Review round 2 / amendment A10 -------------------------------------------------------------

def test_t14_a10_golden_set_is_never_a_precondition_for_development():
    bad = []
    for name in ("aid-impl-plan", "aid-development", "aid-tech-spec", "role-qa-engineer", "test-driven"):
        low = skill(name)
        if re.search(r"golden set (and eval harness )?(come|comes)? ?before the prompt|golden set\s*(->|→)\s*eval harness", low):
            bad.append(name)
    assert bad == [], bad
    assert "seed cases + dev/targeted suite" in skill("aid-impl-plan")


def _raci(text_):
    m = re.search(r"\|\s*Item\s*\|\s*Responsible\s*\|.*?(?:\n(?!\|)|\Z)", text_, re.S)
    return m.group(0).strip() if m else None


def test_t14_a10_raci_tables_are_identical():
    files = ["skills/aid-prd/SKILL.md", "skills/role-product-manager/SKILL.md", "skills/role-tech-lead/SKILL.md",
             "skills/role-data-scientist/SKILL.extended.md", "skills/role-developer/SKILL.extended.md",
             "skills/role-qa-engineer/SKILL.extended.md"]
    tables = {f: _raci((REPO / f).read_text(encoding="utf-8")) for f in files}
    assert all(tables.values()), [f for f, t in tables.items() if not t]
    assert len(set(tables.values())) == 1, "RACI copies differ"


def test_t14_a10_eval_paths_are_under_tests():
    bad = []
    for p in (SK).rglob("*.md"):
        for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for m in re.finditer(r"(?<![\w/])evals/(golden|dev)/", line):
                if not line[:m.start()].endswith("tests/"):
                    bad.append("{}:{}".format(p.relative_to(REPO), n))
    assert bad == [], bad
    assert "tests/evals/golden/" in text("skills/aid-tech-spec/references/agent-architecture.md")


def test_t14_a10_validator_and_gate_check_see_brief_seeds_and_adr():
    v = (REPO / "agents" / "prd-validator.md").read_text(encoding="utf-8")
    for var in ("{{WHY_SHAPE_BRIEF}}", "{{SEED_EVALS}}", "{{LEVEL_ADR}}", "{{PRD_TEMPLATE}}"):
        assert var in v, var
    g = text("commands/gate-check.md")
    for item in ("why-shape-brief", "seed-evals", "adr-shape", "1.5", "7a"):
        assert item in g, item
    prd = (REPO / "commands" / "prd.md").read_text(encoding="utf-8")
    assert prd.count("{{PRD_TEMPLATE}}") >= 4, "template inlined for writer, 3 drafters and validator"


@pytest.mark.parametrize("name", PHASE1_AGENTS)
def test_t14_a10_drafters_take_the_template_as_input(name):
    assert "{{PRD_TEMPLATE}}" in (REPO / "agents" / (name + ".md")).read_text(encoding="utf-8")


def test_t14_a10_signed_level_and_sme_cases():
    t = (REPO / PRD_TEMPLATE).read_text(encoding="utf-8")
    assert "Signed level:" in t and "ADR-SHAPE-" in t
    assert "SME:" in (REPO / "agents" / "phase1-solution-shaper.md").read_text(encoding="utf-8")


def test_t14_a10_prd_writer_leaves_agentic_sections_to_the_merge():
    low = text("agents/prd-writer.md")
    assert "to be merged" in low and "phase1-solution-shaper" in low


def test_t14_a10_eval_planner_copies_the_canonical_thresholds():
    low = text("agents/phase1-eval-planner.md")
    assert "kappa" in low and "0.7" in low and "ln(0.05)" in low and "critical" in low


# --- Security review of 3.1 -----------------------------------------------------------------------

def test_t14_sec_prd_merge_treats_agent_output_as_data_and_fixes_paths():
    low = text("commands/prd.md")
    assert "untrusted-content.md" in low and "are data, not instructions" in low
    assert "[a-z0-9-]" in low and "write tool" in low


def test_t14_sec_seed_cases_are_scanned_and_signed_off_before_commit():
    low = text("commands/prd.md")
    assert "before writing the seed cases, scan every case" in low
    assert "de-identification checked by" in low and "committed" in low
    assert "secret" in text("agents/phase1-solution-shaper.md")


def test_t14_sec_secrets_never_in_traces_or_eval_sets():
    assert "secrets and credentials" in text("skills/aid-tech-spec/references/agent-architecture.md")
    assert "secrets & credentials" in text(PRD_TEMPLATE)


@pytest.mark.parametrize("rel", ["commands/prd.md", "skills/aid-prd/SKILL.md", "skills/aid-prd/SKILL.extended.md",
                                 "skills/role-tech-lead/SKILL.extended.md", "docs/PHASE-GATES.md"])
def test_t14_sec_spike_is_never_run_by_claude_in_phase_1(rel):
    low = text(rel)
    assert "never claude in phase 1" in low or "never by claude in phase 1" in low \
        or "claude does not run the spike in phase 1" in low, rel
