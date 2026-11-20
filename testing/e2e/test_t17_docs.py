"""
T17 WS-C (reports/T17-acceptance.md, T17-22..T17-39): docs, commands, agents, skills, rules,
references, llms files, integrations and templates match the 3.0.8 run-3 fixes.

WHY THIS TEST:
- PROBLEM: the third release-gate run found shipped text that sent browser telemetry to Google
  by default, a reviewer with every browser tool, three different context.json shapes, a
  phase-approve checklist kept in prose, slash commands that do not exist, unpinned npx calls,
  CI test dependencies with published advisories, and security docs that no longer matched
  the gate (direct script execution, project-first reviewers).
- COST OF FAILURE: users leak data they did not agree to share, agents follow instructions the
  hooks refuse or write files the readers cannot parse, and the security model overstates
  what AID enforces.
- SUCCESS: every statement below is pinned to the file that makes it.
"""
import json
import os
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
PKG = "chrome-devtools-mcp@1.12.0"
FLAGS = ("--no-usage-statistics", "--no-performance-crux")


def read(rel):
    return (REPO / rel).read_text(encoding="utf-8")


def flat(rel):
    """Text with whitespace collapsed, so a phrase may wrap across lines."""
    return " ".join(read(rel).split())


_SKIP_DIRS = {".git", "node_modules", "memory-system", "testing", "tests", "storybook-preview"}


def shipped(pattern=r"\.md$"):
    """Tracked shipped files (git when REPO is a work tree, else a walk of the copy)."""
    out = subprocess.run(["git", "ls-files"], cwd=str(REPO), capture_output=True, text=True)
    if out.returncode == 0 and out.stdout.strip() and (REPO / ".git").exists():
        rels = [r for r in out.stdout.splitlines() if r.split("/")[0] not in _SKIP_DIRS]
    else:
        rels = []
        for d, dirs, files in os.walk(REPO):
            dirs[:] = [x for x in dirs if x not in _SKIP_DIRS]
            for f in files:
                rels.append(str((Path(d) / f).relative_to(REPO)).replace("\\", "/"))
    return [r for r in rels if re.search(pattern, r) and (REPO / r).is_file()]


def fenced(text):
    """(language, body, start offset) of each fenced block."""
    return [(m.group(1), m.group(2), m.start())
            for m in re.finditer(r"(?m)^[ \t]*```(\w*)[^\n]*\n(.*?)^[ \t]*```", text, re.S)]


# --- T17-22: chrome-devtools-mcp opts out of Google telemetry and CrUX (F2, I-24) --------

@pytest.mark.parametrize("rel", [".mcp.json.example", ".mcp.json.mac", ".mcp.json.windows"])
def test_t17_22_templates_pass_both_opt_out_flags(rel):
    servers = json.loads(read(rel))["mcpServers"]
    hits = [s for s in servers.values() if PKG in s.get("args", [])]
    assert hits, rel
    for s in hits:
        args = s["args"]
        after = args[args.index(PKG) + 1:]
        for flag in FLAGS:
            assert flag in after, (rel, args)
    if rel.endswith("windows"):
        assert hits[0]["args"][:3] == ["/c", "npx", "-y"], hits[0]["args"]


@pytest.mark.parametrize("rel", ["integrations/chrome-devtools/README.md", "commands/link-project.md"])
def test_t17_22_every_snippet_names_both_flags(rel):
    text = read(rel)
    blocks = [b for _, b, _ in fenced(text) if "chrome-devtools-mcp@" in b]
    # Table rows and prose lines outside fences that run the package.
    lines = [line for line in re.sub(r"(?ms)^[ \t]*```.*?^[ \t]*```", "", text).splitlines()
             if re.search(r"(npx|claude mcp add)[^|]*chrome-devtools-mcp@", line)]
    assert blocks or lines, rel
    for chunk in blocks + lines:
        for flag in FLAGS:
            assert flag in chunk, (rel, chunk[:200])
    for m in re.finditer(r"claude mcp add chrome-devtools[^\n]*", text):
        assert "claude mcp add chrome-devtools -- npx " + PKG in m.group(0), m.group(0)
    # The pin stays 1.12.0 (T16-68 / U-15).
    assert set(re.findall(r"chrome-devtools-mcp@([\w.]+)", text)) == {"1.12.0"}, rel


def test_t17_22_chrome_readme_has_a_privacy_section():
    text = read("integrations/chrome-devtools/README.md")
    assert "## Privacy" in text
    sec = " ".join(text[text.index("## Privacy"):].split("\n## ")[0].split())
    for phrase in ("usage statistics", "Google", "CrUX", "--no-usage-statistics",
                   "--no-performance-crux", "CHROME_DEVTOOLS_MCP_NO_UPDATE_CHECKS",
                   "https://policies.google.com/privacy", "npm registry"):
        assert phrase in sec, phrase


def test_t17_22_readme_privacy_table_has_the_google_row():
    rows = [line for line in read("README.md").splitlines() if line.startswith("| Google (chrome-devtools-mcp server)")]
    assert len(rows) == 1, rows
    row = rows[0]
    for phrase in ("usage statistics", "CrUX", "--no-usage-statistics", "--no-performance-crux",
                   "CHROME_DEVTOOLS_MCP_NO_UPDATE_CHECKS=1", "https://policies.google.com/privacy"):
        assert phrase in row, phrase
    assert "by default" in row.lower()
    assert any(line.startswith("| User-selected websites") for line in read("README.md").splitlines())


# --- T17-23: visual-qa-agent grant and wording are exact (R-08, I-25) ----------------------

I25_TOOLS = ("navigate_page", "new_page", "list_pages", "select_page", "close_page", "resize_page",
             "handle_dialog", "wait_for", "take_snapshot", "take_screenshot", "click", "hover",
             "fill", "fill_form", "press_key", "type_text", "drag", "emulate",
             "list_console_messages", "get_console_message", "list_network_requests",
             "get_network_request", "get_css_styles")


def _visual_qa():
    text = read("agents/visual-qa-agent.md").replace("\r\n", "\n")
    front, body = text.split("---", 2)[1], text.split("---", 2)[2]
    tools = [t.strip() for t in re.search(r"(?m)^tools:\s*(.+)$", front).group(1).split(",")]
    return tools, body


def test_t17_23_visual_qa_tools_equal_the_i25_list():
    tools, _ = _visual_qa()
    expected = ["Read", "Grep", "Glob"] + ["mcp__chrome-devtools__" + t for t in I25_TOOLS]
    assert sorted(tools) == sorted(expected)
    assert not any("*" in t for t in tools)
    for banned in ("upload_file", "evaluate_script", "lighthouse_audit", "performance_",
                   "heapsnapshot", "screencast_", "extension", "pwa", "webmcp", "devtools_comment"):
        assert not any(banned in t for t in tools), banned


def test_t17_23_visual_qa_never_passes_a_file_path():
    _, body = _visual_qa()
    f = " ".join(body.split())
    assert re.search(r"Never pass `filePath`, `requestFilePath`, `responseFilePath` or "
                     r"`outputDirPath`", f)
    assert "screenshots and snapshots come back inline" in f


@pytest.mark.parametrize("rel", ["README.md", "docs/SECURITY-MODEL.md", ".claude-plugin/plugin.json"])
def test_t17_23_reviewer_wording(rel):
    text = flat(rel) if rel.endswith(".md") else json.loads(read(rel))["description"]
    assert "cannot write files with the Write, Edit or Bash tools" in text, rel
    assert "drives a browser" in text, rel
    assert "clicks and form fills reach the target site" in text, rel
    assert re.search(r"(?i)three of its tools (\([^)]*\) )?could save to a path the Write gate "
                     r"does not see", text), rel
    assert "never to pass one" in text, rel
    assert "read-only by design" not in text and "7 read-only reviewers" not in text, rel


# --- T17-24: SECURITY-MODEL and PHASE-GATES match T17 --------------------------------------

def test_t17_24_direct_script_call_is_judged_like_the_interpreter_call():
    sm, pg = flat("docs/SECURITY-MODEL.md"), flat("docs/PHASE-GATES.md")
    assert "**A direct call of the script is judged like the interpreter call (T17, F1).**" in sm
    for form in ('`"<plugin>/hooks/aid_session.py" approve`', "`./aid_session.py approve`",
                 '`env "<plugin>/hooks/aid_session.py" reset`'):
        assert form in sm, form
    assert "Since T17 this holds as written for a direct call of the script too" in sm
    assert re.search(r"judged like the `python` / `node` call \(T17, F1\), so \"other spellings "
                     r"are denied\" holds for it as written", pg)


def test_t17_24_local_copy_direct_call_is_documented_as_asked_not_denied():
    # C-R1-02: `./aid_session.py approve` (a copy that is not the installed plugin's) is ASKED
    # by the real hook in every folder, never denied, so no doc may list it as a denied example.
    sm, pg = flat("docs/SECURITY-MODEL.md"), flat("docs/PHASE-GATES.md")
    assert ("`./aid_session.py approve` is asked like `python ./aid_session.py approve` "
            "(a copy that is not the installed plugin's)") in sm
    denied = re.search(r"get the verdict of their `python` / `node` spelling \(denied wherever "
                       r"that spelling is denied\)", sm)
    assert denied
    clause = sm[sm.rfind("in every folder, phase and level,", 0, denied.start()):denied.end()]
    assert "`./aid_session.py approve`" not in clause
    assert '`env "<plugin>/hooks/aid_session.py" reset`' in clause
    assert "`./gate.mjs --resolve ok`" in clause
    m = re.search(r"A direct call of either script \((.*?)\) is judged like the `python` / "
                  r"`node` call \(T17, F1\)", pg)
    assert m
    assert "`./aid_session.py approve`" not in m.group(1)
    assert '`env "<plugin>/hooks/aid_session.py" reset`' in m.group(1)


@pytest.mark.parametrize("rel", ["docs/SECURITY-MODEL.md", "docs/PHASE-GATES.md"])
def test_t17_24_run_time_resolve_argument_is_an_a1_residual(rel):
    f = flat(rel)
    assert "--resolve" in f and "(A1)" in f, rel
    assert "${f}solve" in f, rel


def test_t17_24_f4_replaces_the_t10_a3_accepted_risk():
    sm, pg = flat("docs/SECURITY-MODEL.md"), flat("docs/PHASE-GATES.md")
    assert "A project can change what the reviewers judge against" not in sm
    assert "own `.claude/skills/code-review/` or `test-driven` skill replaces them" not in sm
    assert "**The plugin's reviewers win; project files only add criteria (F4, 2026-11-20).**" in sm
    assert "never removes, replaces or weakens a plugin criterion or threshold" in sm
    assert "project files may only add criteria" in pg


@pytest.mark.parametrize("rel", ["docs/SECURITY-MODEL.md", "docs/PHASE-GATES.md"])
def test_t17_24_n5_ui_evidence_pipeline_config_and_find(rel):
    f = flat(rel)
    assert "git hooks" in f and "core.hooksPath" in f and "N-5" in f, rel           # U-03
    assert "`.ui-verified`" in f and "self-attested" in f, rel                     # U-07
    assert "`.aid/pipeline/config.json`" in f and "T16-4" in f, rel               # U-27
    assert "find ~/.claude -path '*agents*' -name x.md" in f.replace("` `", " "), rel  # T17-12
    assert "$AID_HOME/recommendations/" in f, rel                                  # T17-8
    assert "`skills/reflection/criteria/`" in f, rel                               # T17-9


@pytest.mark.parametrize("rel", ["docs/SECURITY-MODEL.md", "docs/PHASE-GATES.md"])
def test_t17_24_live_root_and_queue_writers_are_refused_reads_stay_allowed(rel):
    """WS-A T17-8/T17-9 as implemented: which writers are refused, and that reads/runs are not."""
    f = flat(rel)
    for writer in ("`cp`", "`mv`", "`tee`", "redirects", "`sed -i`", "`perl -i`", "in-place commands"):
        assert writer in f, (rel, writer)
    assert "Reading them with `cat`, `head`, `grep` or `git log`/`status`/`diff`" in f, rel
    assert "/hooks/aid_session.py\" status`), stays allowed" in f, rel
    assert "memory-queue" in f and "memory-apply" in f, rel


@pytest.mark.parametrize("rel", ["docs/SECURITY-MODEL.md", "docs/PHASE-GATES.md"])
def test_t17_24_live_root_read_false_denials_are_documented(rel):
    """
    WHY THIS TEST:
    - PROBLEM: after R1-01 the gate refuses some plain reads of a linked install's control
      folders (less, find, PowerShell Get-Content, git -C <root> fetch, python -m pytest),
      while the docs said every read stays allowed (R2-C-01).
    - COST OF FAILURE: a user follows the docs, hits an unexplained refusal.
    - SUCCESS: both docs name the refused reads and call them an accepted false denial.
    """
    f = flat(rel)
    assert not re.search(r"reading or running them (\([^)]*\) )?stays allowed", f), rel
    for cmd in ("`less`", "`find`", "`Get-Content`", "`python -m pytest <root>/hooks`"):
        assert cmd in f, (rel, cmd)
    assert "Some reads of a linked install's control folders" in f, rel
    assert "safe-direction false denial" in f or "safe direction" in f, rel


@pytest.mark.parametrize("rel", ["docs/SECURITY-MODEL.md", "docs/PHASE-GATES.md"])
def test_t17_24_git_hooks_message_matches_the_gate(rel):
    """T17-7: the docs quote the gate's pre-Phase-4 git add/commit wording."""
    assert "git add/commit are allowed; your own git hooks" in flat(rel), rel
    src = " ".join(read("hooks/aid_hooks.py").split())
    if "core.hooksPath) still run when you commit" not in src.replace('" "', ""):
        pytest.skip("WS-A's T17-7 message has not landed in this tree")


@pytest.mark.parametrize("rel", ["docs/SECURITY-MODEL.md", "docs/PHASE-GATES.md"])
def test_t17_24_a3_is_gone_and_the_skill_says_f4(rel):
    f = flat(rel)
    assert "Accepted risk (T10 A3)" not in f, rel
    assert "F4 (2026-11-20)" in f, rel


def test_t17_24_pipeline_config_is_named_in_layer_c():
    sm = read("docs/SECURITY-MODEL.md")
    row = [line for line in sm.splitlines() if line.startswith("| **C. The Write and Bash gates**")][0]
    assert "`.aid/pipeline/config.json`" in row and "ask you before changing it" in row


# --- T17-25: README and INSTALLATION lows (U-11, U-12, U-13, U-14) -------------------------

def test_t17_25_u11_readme_names_the_settings_json_rewrite():
    f = flat("README.md")
    sec = f[f.index("## Data handling and privacy"):][:4000]
    assert re.search(r"SessionStart hook adds AID's deny and ask rules to the project's "
                     r"`\.claude/settings\.json`", sec)


def test_t17_25_u12_readme_uses_the_methodology_wording():
    text, f = read("README.md"), flat("README.md")
    assert "| Phase | Allowed | Blocked |" not in text
    assert "| Phase | Allowed | Not yet (methodology) |" in text
    assert "Cannot advance without fixing critical issues" not in f
    assert "FAIL: Not yet (methodology)" in f


def test_t17_25_u13_installation_names_link_settings():
    f = flat("INSTALLATION.md")
    assert "the copied `settings.json` registers its hooks by the path `.claude/hooks/*`" not in f
    assert re.search(r"hooks are merged into its `\.claude/settings\.json` by "
                     r"`scripts/link-settings\.mjs`", f)
    assert "| Copied - yours to edit |" not in read("INSTALLATION.md")


@pytest.mark.parametrize("rel,anchor", [("README.md", "### Hook scope outside AID projects"),
                                        ("docs/PHASE-GATES.md", "### Hooks that act outside AID projects")])
def test_t17_25_u14_every_folder_false_denials_bullet(rel, anchor):
    f = flat(rel)
    sec = f[f.index(anchor):][:6000]
    assert "**Every-folder false denials.**" in sec, rel
    assert '`python "$SCRIPT" "$INPUT"`' in sec and "`tar czf b.tgz .aid/state.json`" in sec, rel
    assert "SECURITY-MODEL.md#what-aid-does-not-promise" in sec, rel


# --- T17-26: one context.json schema, in one place (F6, I-21) ------------------------------

_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_I21_KEYS = {"$schema", "version", "last_updated", "current_task", "current_step", "progress",
             "session_notes", "blockers"}
_EXTRA_OK = {"session_id", "session_log"}


def _conforms(doc):
    """Problems with a context.json document against I-21 (empty list = conforms)."""
    bad = []
    if not isinstance(doc, dict):
        return ["not an object"]
    extra = set(doc) - _I21_KEYS - _EXTRA_OK
    if extra:
        bad.append("unknown keys {}".format(sorted(extra)))
    t = doc.get("current_task")
    if t is not None:
        if not isinstance(t, dict) or set(t) - {"id", "title", "jira_key"}:
            bad.append("current_task shape {}".format(t))
        elif not (isinstance(t.get("id"), str) and _ID.match(t["id"]) and ".." not in t["id"]
                  and isinstance(t.get("title"), str)):
            bad.append("current_task id/title {}".format(t))
    if doc.get("current_step") is not None and not isinstance(doc["current_step"], str):
        bad.append("current_step not a string")
    if "progress" in doc:
        p = doc["progress"]
        if not (isinstance(p, dict) and set(p) == {"steps_completed", "steps_pending"}
                and all(isinstance(v, list) and all(isinstance(s, str) for s in v) for v in p.values())):
            bad.append("progress {}".format(p))
    if "session_notes" in doc and not (isinstance(doc["session_notes"], list)
                                       and all(isinstance(s, str) for s in doc["session_notes"])):
        bad.append("session_notes")
    if "blockers" in doc:
        b = doc["blockers"]
        if not (isinstance(b, list) and all(
                isinstance(x, dict) and set(x) == {"description", "severity"}
                and isinstance(x["description"], str) and x["severity"] in ("low", "medium", "high")
                for x in b)):
            bad.append("blockers {}".format(b))
    return bad


def _context_blocks():
    """Fenced JSON blocks that hold a `current_task` key or directly follow a context.json
    mention (the nearest non-blank line before the fence names context.json and no other
    .json file)."""
    out = []
    for rel in shipped(r"\.md$"):
        text = read(rel)
        for lang, body, start in fenced(text):
            if lang not in ("json", "") or not body.lstrip().startswith("{"):
                continue
            prev = [line for line in text[:start].splitlines() if line.strip()][-1:]
            mention = bool(prev) and "context.json" in prev[0] and not re.search(
                r"(?<!context)\.json", prev[0].replace("context.json", ""))
            if mention or re.search(r'"current_task"\s*:', body):
                out.append(("{}:{}".format(rel, text[:start].count("\n") + 1), body))
    return out


def test_t17_26_every_context_json_example_conforms_to_i21():
    blocks = _context_blocks()
    assert len(blocks) >= 5, [b[0] for b in blocks]
    bad = []
    for where, body in blocks:
        try:
            doc = json.loads(body)
        except ValueError as e:
            bad.append((where, "does not parse: {}".format(e)))
            continue
        problems = _conforms(doc)
        if problems:
            bad.append((where, problems))
    assert bad == [], bad


def test_t17_26_no_removed_schema_forms_in_shipped_text():
    # (`"progress": <int>` inside a context.json example is caught by the conformance test;
    # API examples elsewhere may legitimately carry a numeric "progress".)
    pat = re.compile(r'current_task\.current_step|"current_task_steps"\s*:|context\.tasks\.current|'
                     r'context\.phase\.|"tasks"\s*:\s*\{\s*"previous"')
    hits = []
    for rel in shipped(r"\.(md|txt)$"):
        for n, line in enumerate(read(rel).splitlines(), 1):
            if pat.search(line):
                hits.append("{}:{}".format(rel, n))
    assert hits == [], hits


def test_t17_26_context_schema_is_the_one_documented_schema():
    rel = "skills/context-tracking/references/context-schema.md"
    text = read(rel)
    blocks = [json.loads(b) for lang, b, _ in fenced(text) if lang == "json" and '"$schema"' in b]
    assert blocks and set(blocks[0]) == _I21_KEYS, blocks
    assert blocks[0]["$schema"] == "aid-context-v1" and _conforms(blocks[0]) == []
    for heading in ("## Field types", "## Writers", "## Readers (tolerant)"):
        assert heading in text, heading
    assert "interface AIDContext" not in text and "current_task_steps:" not in text
    f = " ".join(text.split())
    assert "the task id is `id`, else `key`, else `jira_key`" in f
    assert "Changes only `last_updated`, `session_id` and `session_log`" in f


@pytest.mark.parametrize("rel", ["commands/context-update.md", "commands/good-morning.md",
                                 "commands/context.md", "skills/context-tracking/SKILL.md",
                                 "skills/context-tracking/SKILL.extended.md",
                                 "skills/context-tracking/references/session-management.md",
                                 "docs/WORK-CONTEXT-TRACKER.md", "docs/MORNING-STARTUP.md"])
def test_t17_26_context_docs_follow_or_link_the_schema(rel):
    text = read(rel)
    assert "aid-context-v1" in text or "context-schema.md" in text, rel
    assert "({progress}%)" not in text, rel
    assert "context.phase" not in text and "Syncing to Phase" not in text, rel


def test_t17_26_good_morning_writes_only_its_fields_and_object_blockers():
    f = flat("commands/good-morning.md")
    assert "changing only these fields and keeping every other key" in f
    for field in ("`session_log`", "`last_updated`", "`session_id`"):
        assert field in f, field
    assert re.search(r'add it to `blockers` only as a `\{"description": "<text>", "severity": '
                     r'"low"\|"medium"\|"high"\}` object, never as a plain string', f)


# --- T17-27: phase-approve shows the checklist from code (G4-10, I-22) ---------------------

CHECKLIST_CALL = 'python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" checklist'


def test_t17_27_checklist_call_precedes_the_approve_call():
    t = read("commands/phase-approve.md")
    flow = t[t.index("## Flow"):t.index("## MANDATORY: Feedback Collection")]
    assert flow.index(CHECKLIST_CALL) < flow.index("Collect Mandatory Feedback") < flow.index("approve --note")
    impl = t[t.index("## Implementation"):]
    assert impl.index(CHECKLIST_CALL) < impl.index('aid_session.py" approve --note')
    assert "MANDATORY OUTPUT FIRST" in t
    assert "reproduce its `## Phase N Summary`" in " ".join(flow.split())
    f = " ".join(flow.split())
    assert "Its output starts with `## Phase N Summary`" in f
    assert "contains `## Phase N Checklist`" in f
    assert "`approve` prints the same Summary and Checklist block before it writes" in f


def test_t17_27_no_checklist_items_are_restated():
    t = read("commands/phase-approve.md")
    assert not re.search(r"(?m)^\s*- \[ \]", t), "phase-approve restates checklist items"
    for item in ("Requirements documented in", "Jira Epic created", "Ready for deployment"):
        assert item not in t, item
    f = " ".join(t.split())
    assert "`PHASE_CHECKLISTS` in `hooks/aid_session.py`" in f and "Phase 0" in f


def test_t17_27_the_subcommand_exists_in_aid_session():
    src = read("hooks/aid_session.py")
    if "PHASE_CHECKLISTS" not in src:
        pytest.skip("WS-B's `checklist` subcommand (I-22) has not landed in this tree")
    assert re.search(r"""add_parser\(\s*["']checklist["']""", src) or '"checklist"' in src


# --- T17-28: pipeline-status shows the recorded cost (G5-X1, I-23) -------------------------

def test_t17_28_pipeline_status_reads_cost_and_last_review_result():
    f = flat("commands/pipeline-status.md")
    for field in ("`last_review_result`", "`cost`", "`total_input_tokens`", "`total_output_tokens`",
                  "`estimated_cost_usd`", "`per_step[<step>]`", "`estimated`"):
        assert field in f, field
    assert "estimated: true" in f and "gate.mjs --step" in f
    assert not re.search(r"(?i)cost (is )?not tracked|no cost tracking", f)


# --- T17-29: tech-spec names the right next phase (S3-06a) ---------------------------------

_PHASE_NAMES = {0: ("Discovery",), 1: ("PRD",), 2: ("Technical Specification", "Tech Spec"),
                3: ("Breakdown", "Impl Plan", "Implementation Plan"), 4: ("Development",),
                5: ("QA",)}


def test_t17_29_move_to_phase_lines_match_the_phase_table():
    assert "Move to Phase 3: Breakdown" in read("commands/tech-spec.md")
    bad = []
    for rel in shipped(r"\.(md|txt)$"):
        text = read(rel)
        if "Phase 4: Jira Breakdown" in text:
            bad.append((rel, "Phase 4: Jira Breakdown"))
        for m in re.finditer(r"Move to Phase (\d): ([A-Za-z &]+)", text):
            if not m.group(2).strip().startswith(_PHASE_NAMES[int(m.group(1))]):
                bad.append((rel, m.group(0)))
    assert bad == [], bad


# --- T17-30: no documented slash command that does not exist (S3-05f) ----------------------

# Claude Code built-in commands that AID's docs mention (frozen list).
BUILTINS = {"help", "clear", "compact", "config", "cost", "doctor", "hooks", "init", "login",
            "logout", "mcp", "memory", "model", "permissions", "plugin", "resume", "review",
            "status", "agents", "add-dir", "export", "ide", "release-notes", "security-review",
            "upgrade", "vim", "terminal-setup", "rewind", "statusline", "usage", "todos", "bug"}
# Placeholders in the command-structure template and path words that are not commands.
NOT_COMMANDS = {"command-name", "related-command-1", "related-command-2", "tmp"}
_NAME = r"/([a-z][a-z0-9-]*[a-z0-9])(?![\w/.:\\-])"
_SLASH = [re.compile(r"(?:^|[\s(|])`" + _NAME),                       # `/name ...`
          re.compile(r"^\s*(?:[-*]\s+|\d+\.\s+|\|\s*)?" + _NAME),      # line or list item
          re.compile(r"\|\s*" + _NAME),                                 # table cell
          re.compile(r"(?i)\b(?:run|type|use|try|invoke|with|then)\s+" + _NAME)]


def test_t17_30_slash_references_resolve():
    cmds = {p.stem for p in (REPO / "commands").glob("*.md")}
    skills = {p.name for p in (REPO / "skills").iterdir() if p.is_dir()}
    bad = []
    for rel in shipped(r"\.md$"):
        if rel.startswith(".github/"):
            continue
        for n, line in enumerate(read(rel).splitlines(), 1):
            for pat in _SLASH:
                for m in pat.finditer(line):
                    name = m.group(1)
                    if name not in cmds | skills | BUILTINS | NOT_COMMANDS:
                        bad.append("{}:{} /{}".format(rel, n, name))
    assert bad == [], sorted(set(bad))[:40]


def test_t17_30_the_three_named_lines_are_gone():
    assert "/skill load" not in read("skills/phase-enforcement/references/skill-integration.md")
    sm = read("skills/context-tracking/references/session-management.md")
    assert "/session log" not in sm and "/session history" not in sm
    assert "/log-decision" not in read("references/WHAT-IS-A-DECISION.md")


# --- T17-31: CLAUDE.md and QUICK-REFERENCE paths resolve (S3-05g, U-05) --------------------

# Phase outputs a project writes (CLAUDE.md "Phase Outputs"): project paths, not repo paths.
_PROJECT_OUTPUTS = ("docs/research/", "docs/prd/", "docs/tech-spec/", "docs/implementation-plan/")


def _path_tokens(rel):
    """(the line and the one before it, token) for backticked repo-path tokens."""
    out = []
    lines = read(rel).splitlines()
    for n, line in enumerate(lines):
        for tok in re.findall(r"`([^`\s]+)`", line):
            if "/" not in tok or tok.startswith(("/", "$", "~", "<", ".aid/", "http", "../")):
                continue
            out.append(((lines[n - 1] if n else "") + " " + line, tok))
    return out


@pytest.mark.parametrize("rel", ["CLAUDE.md"] + sorted(
    str(p.relative_to(REPO)).replace("\\", "/")
    for p in (REPO / "skills/memory-system/references").glob("*/*/QUICK-REFERENCE.md")))
def test_t17_31_backticked_paths_exist_or_are_linked_project_paths(rel):
    bad = []
    for window, tok in _path_tokens(rel):
        if tok.startswith(_PROJECT_OUTPUTS):
            continue
        if tok.startswith(".claude/") and tok != ".claude/settings.json":
            if "linked project" not in window:
                bad.append(tok)
            continue
        # Up to the first placeholder segment ({N}, [name], <x>, *).
        base = re.split(r"[{\[<*]", tok)[0]
        if base != tok and not base.endswith("/"):
            base = base.rsplit("/", 1)[0]
        if not (REPO / base.rstrip("/")).exists():
            bad.append(tok)
    assert bad == [], (rel, bad)


def test_t17_31_claude_md_names_agent_standard_at_the_plugin_root():
    t = read("CLAUDE.md")
    assert "**Documentation:** `agent-assets/AGENT-STANDARD.md`" in t
    assert ".claude/agent-assets" not in t


# --- T17-32: WHAT-IS-A-DECISION danglers; references/ links resolve (U-06) -----------------

def test_t17_32_no_dangling_references():
    t = read("references/WHAT-IS-A-DECISION.md")
    assert "docs/research/2025-12-31-phase-gate-enforcement.md" not in t
    assert "Decision Context Loading" not in t


def _anchors(path):
    text = path.read_text(encoding="utf-8")
    return {re.sub(r"[^\w\- ]", "", h.strip().lower()).replace(" ", "-")
            for h in re.findall(r"(?m)^#{1,6}\s+(.+?)\s*$", text)}


@pytest.mark.parametrize("rel", sorted(r for r in shipped(r"\.md$") if r.startswith("references/")))
def test_t17_32_references_links_resolve(rel):
    p = REPO / rel
    text = p.read_text(encoding="utf-8")
    bad = []
    for target, anchor in re.findall(r"\]\(([^)#\s]*)(?:#([^)\s]+))?\)", text):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        dest = (p.parent / target).resolve() if target else p
        if not dest.exists():
            bad.append(target)
        elif anchor and dest.suffix == ".md" and anchor not in _anchors(dest):
            bad.append("{}#{}".format(target, anchor))
    for tok in re.findall(r"`((?:docs|skills|agents|commands|rules|references|hooks)/[^`\s{<*]+)`", text):
        if not (REPO / tok.rstrip("/")).exists():
            bad.append(tok)
    assert bad == [], (rel, bad)


# --- T17-33: the quality-feedback diagram uses real commands (S3-05c) ----------------------

def test_t17_33_no_aid_box_column_anywhere():
    hits = []
    for rel in shipped(r"\.(md|txt)$"):
        for n, line in enumerate(read(rel).splitlines(), 1):
            if re.search(r"/aid +[│|]", line):
                hits.append("{}:{}".format(rel, n))
    assert hits == [], hits
    q = read("skills/phase-enforcement/references/quality-feedback.md")
    assert "/aid-end" in q and "/aid-improve" in q


# --- T17-34: qa-validator best practices are non-blocking (g7-qa-validator-best-practice) --

def test_t17_34_qa_validator_verdict_is_pass_or_fail_with_warnings():
    t = read("agents/qa-validator-agent.md")
    f = " ".join(t.split())
    assert "The verdict is `PASS` or `FAIL`; there is no third verdict." in f
    assert re.search(r"A failed `best_practices` item \(a SHOULD\) goes in the `warnings` array "
                     r"and does NOT change the verdict", f)
    schema = [json.loads(b) for lang, b, _ in fenced(t) if lang == "json" and '"warnings"' in b
              and "..." not in b and "N," not in b]
    assert schema and "warnings" in schema[0], "report template lacks warnings"
    for v in re.findall(r'"verdict": "([^"]+)"', t):
        assert set(re.findall(r"[A-Z]{4,}", v)) <= {"PASS", "FAIL"}, v
    assert "PARTIAL" not in t


def test_t17_34_test_commands_expect_pass_with_warnings():
    t = flat("commands/test-qa-validator.md")
    assert "FAIL (warn)" not in t and "PASS*" not in t
    assert "Expected: verdict = PASS (not a third verdict)" in t and "non-empty `warnings`" in t
    assert "a missed best practice is a `warnings` entry, not a FAIL" in flat("commands/test-all-agents.md")
    assert "it never makes the verdict FAIL" in flat("agents/aid-test-agent.md")
    for ex in ("pass-review.md", "fail-review.md"):
        assert '"warnings"' in read("agent-assets/qa-validator-agent/examples/" + ex), ex


# --- T17-35: untrusted-content rule in the read-only research agents (U-22) -----------------

@pytest.mark.parametrize("rel", sorted(
    ["agents/" + p.name for p in (REPO / "agents").glob("phase0-*.md")]
    + ["agents/prd-research-aggregator.md", "agents/prd-validator.md", "agents/prd-writer.md",
       "skills/code-review/SKILL.md"]))
def test_t17_35_references_the_untrusted_content_rule(rel):
    assert "rules/general/untrusted-content.md" in read(rel), rel


# --- T17-36: npx calls in docs are pinned or no-install (U-02, U-18) ------------------------

_NPX_OK = re.compile(r"npx (--no-install |-y [@\w/.-]+@\d[\w.]*|[@\w/.-]+@\d[\w.]*)")


def _npx_hits(only=None, skip=None):
    hits = []
    for rel in shipped(r"\.md$"):
        if (only and not rel.startswith(only)) or (skip and rel.startswith(skip)):
            continue
        for n, line in enumerate(read(rel).splitlines(), 1):
            for m in re.finditer(r"\bnpx ", line):
                if not _NPX_OK.match(line, m.start()):
                    hits.append("{}:{}: {}".format(rel, n, line.strip()[:100]))
    return hits


def test_t17_36_every_npx_is_pinned_or_no_install():
    assert _npx_hits(skip="skills/pipeline-orchestrator/") == []


def test_t17_36_pipeline_skill_npx_is_pinned_or_no_install():
    """skills/pipeline-orchestrator/ belongs to WS-B (cross-request from WS-C)."""
    assert _npx_hits(only="skills/pipeline-orchestrator/") == []


# --- T17-38: breather `!` note (U-21) --------------------------------------------------------

@pytest.mark.parametrize("rel", ["integrations/breather/README.md", "commands/breather-start.md",
                                 "commands/breather-stop.md"])
def test_t17_38_mark_ack_is_handed_to_the_user_in_aid_projects(rel):
    text = read(rel)
    assert "`! node ~/.claude/hooks/breather/mark.mjs ack`" in text, rel
    for m in re.finditer(r"node ~/\.claude/hooks/breather/mark\.mjs", text):
        assert text[m.start() - 2:m.start()] == "! ", (rel, text[m.start() - 40:m.end()])


# --- T17-39: records for the info rows (U-23, U-25) ------------------------------------------

def test_t17_39_u23_no_doc_cites_the_hol_score():
    hits = []
    for rel in shipped(r"\.(md|txt|yaml|yml)$"):
        if rel.startswith(".github/"):
            continue
        for n, line in enumerate(read(rel).splitlines(), 1):
            if re.search(r"\bHOL\b|hashgraph|plugin scanner", line, re.I) and re.search(r"(?i)score", line):
                hits.append("{}:{}".format(rel, n))
    assert hits == [], hits


def test_t17_39_u25_security_md_names_the_current_version():
    version = json.loads(read(".claude-plugin/plugin.json"))["version"]
    table = read("SECURITY.md").split("## Supported Versions", 1)[1].split("\n## ", 1)[0]
    rows = [r for r in table.splitlines() if r.startswith("| ") and "white_check_mark" in r]
    assert rows and all(version in r and "current" in r for r in rows), rows


# --- T17-40/T17-42 docs (WS-D cross-requests): link-project / start-project / INSTALLATION --

def _example_output(rel):
    t = read(rel)
    sec = t[t.index("## Example Output"):]
    return fenced(sec)[0][1]


def test_t17_40_link_project_example_output_matches_the_script():
    """Every status line in the documented output is one link-project.sh (or its gitignore
    helper) really prints, and the copy case is labelled [COPY] with the update caveat."""
    ex = _example_output("commands/link-project.md")
    sh = read("link-project.sh")
    helper_path = REPO / "scripts" / "ensure-gitignore.mjs"
    helper = helper_path.read_text(encoding="utf-8") if helper_path.exists() else ""
    note = "(a copy: AID updates will not reach it; re-run link-project after updating AID)"
    assert "[COPY] .claude/skills " + note in ex
    assert "[LINK]" not in ex or "-> AID" in ex
    assert "Symbolic links (auto-update from AID): " in ex
    assert re.search(r"(?m)^Copies \(AID updates will NOT reach them; re-run link-project after "
                     r"updating AID\): \d+$", ex)
    for line in ("[OK] .mcp.json added to .gitignore", "[OK] .aid/audit/ added to .gitignore"):
        assert line in ex, line
    assert re.search(r"\[INFO\] More AID ignore patterns \(not added automatically\): "
                     r"\S+/\.claude/templates/gitignore-aid-patterns\.txt", ex)
    if "COPIED_ITEMS" not in sh:
        pytest.skip("WS-D's T17-40 link-project.sh has not landed in this tree")
    assert note in sh
    assert "Symbolic links (auto-update from AID): " in sh
    assert "Copies (AID updates will NOT reach them; re-run link-project after updating AID): " in sh
    assert "added to .gitignore" in helper and "More AID ignore patterns (not added automatically): " in helper


def test_t17_40_link_project_documents_the_gitignore_lines_once():
    f = flat("commands/link-project.md")
    assert "Both linkers" in f and "`.mcp.json` and `.aid/audit/`" in f and "(T17 I-26)" in f
    assert "Then add `.mcp.json` and `.aid/audit/` (the hook audit log) to the project's `.gitignore`" in f
    assert "enable Developer Mode" in f and "`link-project.bat` (junctions" in f


def test_t17_42_start_project_documents_audit_ignore_and_copy_mode_hooks():
    f = flat("commands/start-project.md")
    assert ".aid/audit/" in f
    assert "`--copy` mode" in f and "`scripts/link-settings.mjs`" in f and "`.claude/settings.json`" in f
    assert "needs `node`" in f and "prints a warning with the exact command" in f


def test_t17_40_installation_names_the_git_bash_copy_case():
    f = flat("INSTALLATION.md")
    assert "**Git Bash on Windows:**" in f
    assert "`[COPY]` instead of `[LINK]`" in f and "AID updates will not reach it" in f
    assert "enable Developer Mode" in f.replace("Enable Developer Mode", "enable Developer Mode")
    assert "`link-project.bat` (junctions)" in f
