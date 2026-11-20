"""
T10 (T10-acceptance.md): agent and command safety.

WHY: visual-qa-agent inherited every tool while driving a browser on untrusted pages; ~20
spawns ran AID's reviewers as `general-purpose` (every tool, whatever the agent's own list
says); the autoresearch scorer could be replaced by a workspace copy; no agent was told
that fetched text is data; the human sign-off and the installers were model-invocable; and
/yolo made a false claim about the shipped permissions (A-08, A-25, A-26, A-27, A-47).
"""
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
AGENTS = {p.stem: p for p in (REPO / "agents").glob("*.md")}
SHIPPED_DIRS = ("agents", "agent-assets", "skills", "commands", "rules", "integrations", "memory-system", "docs")
WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit", "Bash", "PowerShell"}
BUILTIN_AGENTS = {"Explore", "Plan", "statusline-setup", "claude-code-guide"}


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---"), path
    return text.replace("\r\n", "\n").split("---", 2)[1]


def tools_of(name):
    m = re.search(r"^tools:\s*(.+)$", frontmatter(AGENTS[name]), re.M)
    return [t.strip() for t in m.group(1).split(",")] if m else None


def shipped_md():
    for d in SHIPPED_DIRS:
        for p in (REPO / d).rglob("*.md"):
            if "node_modules" not in p.parts:
                yield p
    for name in ("CLAUDE.md", "README.md"):
        yield REPO / name


# --- T10-1 ------------------------------------------------------------------

def test_t10_1_every_agent_declares_its_tools():
    """An agent without `tools:` inherits every tool (Claude Code docs, sub-agents)."""
    missing = [n for n in AGENTS if tools_of(n) is None]
    assert missing == [], missing


def test_t10_1_visual_qa_agent_has_only_read_and_browser_tools():
    assert tools_of("visual-qa-agent") == ["Read", "Grep", "Glob", "mcp__chrome-devtools__*"]


REVIEWERS = sorted(n for n in AGENTS if re.search(
    r"(review|reviewer|validator|reflection|certifier|assessor|analysis)", n))


@pytest.mark.parametrize("name", REVIEWERS)
def test_t10_1_reviewers_cannot_write_or_run_commands(name):
    assert not WRITE_TOOLS & set(tools_of(name)), (name, tools_of(name))


# --- T10-2 ------------------------------------------------------------------

def _spawns():
    for p in shipped_md():
        for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for m in re.finditer(r"subagent_type\s*[:=]\s*[`\"']?([A-Za-z0-9:_-]+)", line):
                yield p.relative_to(REPO), n, m.group(1), line


def test_t10_2_spawns_name_a_real_agent():
    bad = []
    for path, n, value, line in _spawns():
        if value.endswith(":") and "<" in line:   # the documented placeholder aid:<agent-name>
            continue
        name = value.split(":", 1)[1] if value.startswith("aid:") else value
        if name in AGENTS or name in BUILTIN_AGENTS:
            continue
        if name == "general-purpose" and "no AID agent" in line:
            continue
        bad.append("{}:{}: {}".format(path, n, value))
    assert bad == [], bad


def test_t10_2_nothing_loads_an_agent_or_criteria_from_the_workspace():
    """The autoresearch judge was read from {{WORKSPACE}}/.claude/agents/ (A-08)."""
    pat = re.compile(r"(?i)(\{\{WORKSPACE\}\}/\.claude/agents|~/\.claude/agents|resolve project.{0,3}user"
                     r"|project[- ]first|project\s*(?:→|->)\s*user)")
    hits = []
    for p in shipped_md():
        for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if pat.search(line):
                hits.append("{}:{}".format(p.relative_to(REPO), n))
    assert hits == [], hits


# --- T10-3 ------------------------------------------------------------------

HUMAN_ONLY = ("phase-approve", "phase-advance", "breather-start", "breather-stop", "setup",
              "start-project", "link-project", "aid-reset", "yolo", "yolo-off")


@pytest.mark.parametrize("name", HUMAN_ONLY)
def test_t10_3_state_changing_commands_are_human_only(name):
    head = frontmatter(REPO / "commands" / (name + ".md"))
    assert re.search(r"^disable-model-invocation:\s*true\s*$", head, re.M), name


# --- T10-4 ------------------------------------------------------------------

RULE = REPO / "rules" / "general" / "untrusted-content.md"


def test_t10_4_untrusted_content_rule_exists():
    text = RULE.read_text(encoding="utf-8")
    for phrase in ("data, not instructions", "Never follow instructions", "Report it",
                   "Jira", "GitHub", "MCP"):
        assert phrase in text, phrase


@pytest.mark.parametrize("path", [
    "agents/developer.md", "agents/test-engineer.md", "agents/code-review-agent.md",
    "agents/test-review-agent.md", "agents/qa-validator-agent.md", "agents/visual-qa-agent.md",
    # The Figma integration was removed earlier; these are the integrations that exist.
    "integrations/github/README.md", "integrations/jira/README.md",
    "integrations/chrome-devtools/README.md"])
def test_t10_4_agents_and_integrations_reference_the_rule(path):
    assert "rules/general/untrusted-content.md" in (REPO / path).read_text(encoding="utf-8")


# --- T10-5 ------------------------------------------------------------------

def test_t10_5_yolo_is_truthful():
    text = (REPO / "commands" / "yolo.md").read_text(encoding="utf-8")
    assert "already has" not in text
    for line in text.splitlines():           # broad rules only ever named to warn against
        if re.search(r"`(Bash|Edit|Write)\(\*\)`", line):
            assert re.search(r"(?i)do not|don't|remove", line), line
    for m in re.finditer(r"dangerously-skip-permissions", text):
        window = text[max(0, m.start() - 400): m.end() + 400].lower()
        assert "warning" in window or "⚠" in window, "skip-permissions mentioned without a warning"


# --- T10-6 ------------------------------------------------------------------

def test_t10_6_aid_session_runs_only_from_the_plugin():
    """A-26: /aid-start and /aid-end ran a project's own hooks/aid_session.py first."""
    bad = []
    for d in ("commands", "skills"):
        for p in (REPO / d).rglob("*.md"):
            text = p.read_text(encoding="utf-8", errors="replace")
            for n, line in enumerate(text.splitlines(), 1):
                if re.search(r"\bpy(thon3?)?\s+\S*aid_session\.py", line) and "CLAUDE_PLUGIN_ROOT" not in line:
                    if _linked_install_line(p, text, line):
                        continue
                    bad.append("{}:{}: {}".format(p.relative_to(REPO), n, line.strip()[:100]))
    assert bad == [], bad


# T16 (owner 2026-11-19), I-10 / T16-64: link-project.md (user-only: disable-model-invocation:
# true, so the agent never runs it) shows the line a user types in a terminal for a linked
# install, which has no plugin and so no ${CLAUDE_PLUGIN_ROOT}. Same narrow shape as the
# test_t3_5 exemption in test_aid_hooks.py; every agent-invocable command and skill keeps A-26.
_LINKED_INSTALL_LINE = re.compile(
    r'^python "?(?:<AID-main>|[A-Za-z]:[\\/]|~/)[^"\s]*[\\/]hooks[\\/]aid_session\.py"? '
    r'(?:init|status|start|approve|advance)\b')


def _linked_install_line(path, text, line):
    if path.name != "link-project.md" or path.parent.name != "commands":
        return False
    front = text.split("\n---", 1)[0] if text.startswith("---") else ""
    if not re.search(r"^disable-model-invocation:\s*true\s*$", front, re.M):
        return False
    return bool(_LINKED_INSTALL_LINE.match(line.strip()))


def test_t16_63_t10_6_exemption_is_narrow():
    """WHY (R3-04): the link-project.md exemption must not let an agent-invocable file or a
    project-local script path through A-26."""
    lp = REPO / "commands" / "link-project.md"
    text = lp.read_text(encoding="utf-8")
    ok = 'python "C:/Tools/AID/hooks/aid_session.py" status'
    assert _linked_install_line(lp, text, ok)
    assert not _linked_install_line(lp, text, "python hooks/aid_session.py approve")
    assert not _linked_install_line(lp, text, 'python "<AID-main>/hooks/aid_session.py" jump 1 5')
    assert not _linked_install_line(REPO / "commands" / "aid-start.md", text, ok)
    no_flag = text.replace("disable-model-invocation: true", "disable-model-invocation: false", 1)
    assert not _linked_install_line(lp, no_flag, ok)


# Agents allowed to write or run commands, each with its reason (T10-1: exceptions are listed).
WRITERS = {
    "developer": "implements code in Phase 4",
    "test-engineer": "writes tests in Phase 4",
    "aid-test-agent": "writes its own test outputs and reports under .aid/test-outputs/",
}


def test_t10_1_only_the_listed_agents_can_write_or_run_commands():
    writers = {n for n in AGENTS if WRITE_TOOLS & set(tools_of(n))}
    assert writers == set(WRITERS), writers ^ set(WRITERS)


def _readme_reviewer_table():
    text = (REPO / "README.md").read_text(encoding="utf-8")
    sec = text[text.index("## Sub-Agents"):]
    sec = sec[:sec.index("\n---")]
    return re.findall(r"^\| `([a-z0-9-]+)` \|", sec, re.M), " ".join(sec.split())


def test_t15_33_readme_reviewers_have_no_write_tools():
    """WHY (T15-33, R-05/A-08): the README called aid-test-agent a read-only reviewer while
    it holds Write, Edit and Bash. Every agent in the reviewer table must be read-only."""
    names, sec = _readme_reviewer_table()
    assert names and "aid-test-agent" not in names, names
    assert len(names) == 7 and "7 reviewer" in sec, (names, sec[:200])
    bad = {n: tools_of(n) for n in names if WRITE_TOOLS & set(tools_of(n) or [])}
    assert bad == {}, bad
    assert "`aid-test-agent`" in sec and "test runner with write tools" in sec


def test_t15_33_security_model_agrees_on_aid_test_agent():
    text = " ".join((REPO / "docs" / "SECURITY-MODEL.md").read_text(encoding="utf-8").split())
    assert "The 7 reviewers" in text and "`aid-test-agent` is not a reviewer" in text


def test_t10_review_scorer_has_no_bare_name_fallback():
    """WHY (T10 review r1, A2): a bare `reflection-agent` lets a project's own
    .claude/agents/reflection-agent.md act as the autoresearch judge."""
    bad = []
    for p in list((REPO / "skills" / "autoresearch").glob("*.md")) + [REPO / "skills" / "pipeline-orchestrator" / "SKILL.md"]:
        text = p.read_text(encoding="utf-8")
        for m in re.finditer(r'aid:reflection-agent', text):
            near = text[m.end(): m.end() + 120]
            if re.search(r'fallback[:`" ]*\(?\s*[`"]?reflection-agent', near):
                bad.append(str(p.relative_to(REPO)))
    assert bad == [], bad


def test_t10_review_verify_run_resolves_the_real_plugin_folder():
    """WHY (T10 review r1): through a link-project symlink, a logical `..` pointed at the
    project's .claude/, so a workspace copy could act as the judge."""
    text = (REPO / "skills" / "autoresearch" / "verify-run.sh").read_text(encoding="utf-8")
    assert 'cd -P "$(dirname "$0")/../.."' in text and "pwd -P" in text
    assert "$ROOT/.claude/agents" not in text and "$ROOT/.claude/skills/reflection" not in text
