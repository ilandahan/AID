"""
T13 (T13-acceptance.md): docs and hygiene.

WHY: LF-only .bat files can lose labels on Windows (A-40); counts drifted (A-41); nested
SKILL.md files looked like skills but were never loaded (A-42); plugin users never got the
WHY/phase rules from CLAUDE.md (A-52); several docs pointed at files and commands that do
not exist; /phase used an 8-phase scheme; verify-run.sh exited 0 even when a check failed.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "hooks"))


def tracked(pattern):
    out = subprocess.run(["git", "ls-files", pattern], cwd=str(REPO), capture_output=True, text=True).stdout
    return [REPO / p for p in out.split()]


# --- T13-1 (A-40) -----------------------------------------------------------

@pytest.mark.parametrize("bat", tracked("*.bat"), ids=lambda p: p.name)
def test_t13_1_bat_files_are_crlf(bat):
    data = bat.read_bytes()
    assert data.count(b"\n") == data.count(b"\r\n") and data.count(b"\n") > 0, bat.name


# --- T13-2 (A-41) -----------------------------------------------------------

COUNTS = {
    "commands": len(tracked("commands/*.md")),
    "skills": len([p for p in tracked("skills/*/SKILL.md") if len(p.relative_to(REPO).parts) == 3]),
    "agents": len(tracked("agents/*.md")),
}
COUNT_FILES = ["README.md", "CLAUDE.md", ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
               ".well-known/llms.txt", "llms-full.txt"]


@pytest.mark.parametrize("rel", COUNT_FILES)
def test_t13_2_counts_match_the_repo(rel):
    text = (REPO / rel).read_text(encoding="utf-8")
    bad = []
    for m in re.finditer(r"(?<![~\d])(\d+) (?:slash |review |expertise )?(commands|skills|agents|sub-agents)\b", text):
        kind = "agents" if m.group(2) in ("agents", "sub-agents") else m.group(2)
        if int(m.group(1)) != COUNTS[kind]:
            bad.append("{} {} (actual {})".format(m.group(1), m.group(2), COUNTS[kind]))
    assert bad == [], (rel, bad)


# --- T13-3 (A-42) -----------------------------------------------------------

KNOWN_FIELDS = {"name", "description", "allowed-tools", "disable-model-invocation", "user-invocable",
                "paths", "model", "hooks", "argument-hint", "license", "metadata"}


def test_t13_3_no_nested_skill_md():
    nested = [str(Path(p).relative_to(REPO)) for p in glob.glob(str(REPO / "skills" / "*" / "*" / "**" / "SKILL.md"),
                                                               recursive=True)]
    assert nested == [], nested


@pytest.mark.parametrize("skill", [p for p in tracked("skills/*/SKILL.md") if len(p.relative_to(REPO).parts) == 3],
                         ids=lambda p: p.parent.name)
def test_t13_3_skill_frontmatter_uses_known_fields(skill):
    text = skill.read_text(encoding="utf-8").replace("\r\n", "\n")
    head = text[4:text.index("\n---\n", 4)]
    keys = {m.group(1) for m in re.finditer(r"^([A-Za-z_-]+):", head, re.M)}
    assert keys <= KNOWN_FIELDS, keys - KNOWN_FIELDS


def test_t13_3_renamed_quick_references_exist():
    refs = REPO / "skills" / "memory-system" / "references"
    found = sorted(p.parent.name for p in refs.glob("*/*/QUICK-REFERENCE.md"))
    assert len(found) == 11, found


# --- T13-4 (A-52) -----------------------------------------------------------

def _session_start(cwd, home):
    env = dict(os.environ, HOME=str(home), USERPROFILE=str(home), AID_HOME=str(Path(home) / ".aid"))
    env.pop("CLAUDE_PROJECT_DIR", None)
    env.pop("CLAUDE_CONFIG_DIR", None)
    p = subprocess.run([sys.executable, str(REPO / "hooks" / "aid_hooks.py"), "--event", "SessionStart"],
                       input=json.dumps({"session_id": "s1", "source": "startup", "cwd": str(cwd)}),
                       capture_output=True, text=True, cwd=str(cwd), env=env, timeout=60)
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout)["hookSpecificOutput"].get("additionalContext", "") if p.stdout.strip() else ""


def test_t13_4_aid_projects_get_the_rules_at_session_start(tmp_path):
    proj, home = tmp_path / "p", tmp_path / "h"
    (proj / ".aid" / "hooks").mkdir(parents=True)
    (proj / ".aid" / "hooks" / "config.json").write_text("{}", encoding="utf-8")
    (proj / ".aid" / "state.json").write_text('{"current_phase": 1}', encoding="utf-8")
    home.mkdir()
    ctx = _session_start(proj, home)
    assert "AID RULES" in ctx and "WHY first" in ctx and "later phase" in ctx, ctx[:400]


def test_t13_4_other_folders_get_no_rules(tmp_path):
    other, home = tmp_path / "o", tmp_path / "h"
    other.mkdir()
    home.mkdir()
    assert "AID RULES" not in _session_start(other, home)


def test_t13_4_rules_block_is_short():
    import aid_hooks
    assert len(aid_hooks.AID_RULES) < 1200


# --- T13-5 (danglers) ---------------------------------------------------------

def _shipped_md():
    for d in ("agents", "agent-assets", "skills", "commands", "rules", "docs", "memory-system", "integrations"):
        for p in (REPO / d).rglob("*.md"):
            yield p
    for name in ("CLAUDE.md", "README.md", "llms-full.txt", "llms.txt", ".well-known/llms.txt"):
        if (REPO / name).exists():
            yield REPO / name


def test_t13_review_no_reference_to_the_renamed_files():
    """WHY (T13 review r1): llms-full.txt and /aid-status still named the old nested files."""
    old = re.compile(r"(?:roles|phases)/(?:[a-z-]+|\{(?:role|phase)\}|\*)/SKILL\.md"
                     r"|standards/(?:code-review|test-driven)/SKILL\.md"
                     r"|^\s*-\s*(?:developer|development)/SKILL\.md")
    hits = ["{}:{}".format(p.relative_to(REPO), n)
            for p in _shipped_md()
            for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1)
            if old.search(line)]
    assert hits == [], hits


def test_t13_review_link_project_names_the_files_the_scripts_copy():
    text = (REPO / "commands" / "link-project.md").read_text(encoding="utf-8")
    assert ".mcp.json.mac" in text and ".mcp.json.windows" in text
    assert "**Copy .mcp.json.example** to target" not in text


@pytest.mark.parametrize("needle", ["AGENT-PROMPT.md", "docs/tech-specs", "/aid export", "AGENT.md#phase-gate",
                                    "docs/PRD.md"])
def test_t13_5_no_dangling_reference(needle):
    hits = ["{}:{}".format(p.relative_to(REPO), n)
            for p in _shipped_md()
            for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1)
            if needle in line]
    assert hits == [], hits


def test_t13_5_mcp_example_exists_and_holds_no_secrets():
    text = (REPO / ".mcp.json.example").read_text(encoding="utf-8")
    data = json.loads(text)
    assert isinstance(data.get("mcpServers"), dict) and data["mcpServers"]
    assert not re.search(r"(gh[pousr]_|github_pat_|sk-|AKIA|glpat-|xox[abprs]-)[A-Za-z0-9]", text)
    assert ".mcp.json.example" in (REPO / "commands" / "link-project.md").read_text(encoding="utf-8")


# --- T13-6 (phase.md) ---------------------------------------------------------

def test_t13_6_phase_command_uses_phases_0_to_5():
    text = (REPO / "commands" / "phase.md").read_text(encoding="utf-8")
    assert re.search(r"\b0\b.{0,40}Discovery", text, re.S) and re.search(r"\b5\b.{0,40}QA", text, re.S)
    assert not re.search(r"(?i)phase\s+[6-8]\b", text), "phases above 5"
    assert ".aid/state.json" in text


# --- T13-7 (verify-run.sh) ----------------------------------------------------

def _posix_bash():
    if os.name == "nt":
        git = shutil.which("git")
        here = Path(git).resolve() if git else None
        for cand in ([here.parents[1] / "bin" / "bash.exe", here.parents[2] / "bin" / "bash.exe"] if here else []):
            if cand.is_file():
                return str(cand)
        return None
    return shutil.which("bash")


@pytest.mark.skipif(_posix_bash() is None, reason="no POSIX bash available")
@pytest.mark.parametrize("over_cap", [False, True])
def test_t13_7_verify_run_exit_code_matches_its_summary(tmp_path, over_cap):
    """The exit code is 1 exactly when the summary counts a FAIL, including the cap checks
    printed by the embedded Python block."""
    pipe = tmp_path / ".aid" / "pipeline"
    (pipe / "t1").mkdir(parents=True)
    (pipe / "t1" / "brief.md").write_text("ORIGINAL_REQUEST\nSTATED_WHY\nfrozen_at: x\n", encoding="utf-8")
    (pipe / "state.json").write_text(json.dumps({
        "step_history": ["AR_DESIGN", "AR_FUNCTION", "AR_ACCEPTANCE"],
        "iterations": {"code_review": 9 if over_cap else 1}}), encoding="utf-8")
    p = subprocess.run([_posix_bash(), (REPO / "skills" / "autoresearch" / "verify-run.sh").as_posix(),
                        tmp_path.as_posix()], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=120)
    m = re.search(r"Summary: (\d+) PASS / (\d+) WARN / (\d+) FAIL", p.stdout)
    assert m, p.stdout[-800:]
    fails = int(m.group(3))
    assert fails == len(re.findall(r"^  FAIL ", p.stdout, re.M)), p.stdout
    assert p.returncode == (1 if fails else 0), (p.returncode, fails)
    if over_cap:
        assert "FAIL  code_review=9 exceeds cap" in p.stdout and p.returncode == 1
