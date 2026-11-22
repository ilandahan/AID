"""
T16 WS-E (reports/T16-acceptance.md, T16-34..T16-62): docs, commands, agents, skills, rules,
llms files and repo hygiene match the 3.0.8 run-2 fixes.

WHY THIS TEST:
- PROBLEM: the second release-gate run found docs that described a different product than
  the hooks enforce (the clone route "unchanged", `/aid <sub>` commands that do not exist,
  phases numbered 1-7, a PRD path no other command reads, `.env.test` holding keys), and
  commands that let the agent skip what the user must see (phase-approve summary) or
  run what only the user may run (breather mark.mjs, gate.mjs --resolve).
- COST OF FAILURE: users trust a gate that is not registered, agents follow instructions
  the gate refuses, and secrets end up in plaintext files.
- SUCCESS: every statement below is pinned to the file that makes it.
"""
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]


def read(rel):
    return (REPO / rel).read_text(encoding="utf-8")


def flat(rel):
    """Text with whitespace collapsed, so a phrase may wrap across lines."""
    return " ".join(read(rel).split())


_SKIP_DIRS = {".git", "node_modules", "memory-system", "testing", "tests", "storybook-preview"}


def doc_files():
    """Tracked text docs outside memory-system/ and the test trees. Uses git when REPO is a
    work tree (so local untracked folders do not count), else walks the tree (a copy)."""
    out = subprocess.run(["git", "ls-files"], cwd=str(REPO), capture_output=True, text=True)
    if out.returncode == 0 and out.stdout.strip() and (REPO / ".git").exists():
        rels = [r for r in out.stdout.splitlines() if r.split("/")[0] not in _SKIP_DIRS]
    else:
        rels = []
        for d, dirs, files in os.walk(REPO):
            dirs[:] = [x for x in dirs if x not in _SKIP_DIRS]
            for f in files:
                rels.append(str((Path(d) / f).relative_to(REPO)).replace("\\", "/"))
    keep = [r for r in rels if re.search(r"\.(md|txt|yaml|yml)$", r) or r.startswith(".well-known/")]
    return [r for r in keep if (REPO / r).is_file()]


def gh_slug(heading):
    """GitHub's anchor for a markdown heading."""
    s = heading.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def anchors(path):
    text = path.read_text(encoding="utf-8")
    return {gh_slug(m.group(1)) for m in re.finditer(r"(?m)^#{1,6}\s+(.+?)\s*$", text)}


# --- T16-34 / T16-59: security docs match T16 --------------------------------------------

def test_t16_34_both_routes_register_the_same_gates():
    sm, rd, ins = flat("docs/SECURITY-MODEL.md"), flat("README.md"), flat("INSTALLATION.md")
    for name, text in (("INSTALLATION", ins), ("README", rd)):
        assert "The clone route is unchanged" not in text, name
        assert "route still works unchanged" not in text, name
        assert 'onFailure: "block"' in text and "same gates" in text, name
        assert "link-project" in text and "absolute path" in text, name
    assert "## Both install routes run the same gates" in read("docs/SECURITY-MODEL.md")
    assert "scripts/link-settings.mjs" in sm and 'onFailure: "block"' in sm
    assert re.search(r"SessionStart, PreToolUse .{0,80}PostToolUse \(ExitPlanMode\) and Stop", sm)
    assert "Everything on this page holds for a linked project" in sm
    assert "AID's hooks come from project settings: deploy them in managed settings instead" not in sm


def test_t16_34_state_json_refused_in_every_folder_with_its_residual():
    sm = flat("docs/SECURITY-MODEL.md")
    # T16 B1: the write tools refuse it in every folder; shell writes everywhere only when the
    # text names the path, in every form only inside AID (RV-B1-01 removed the overclaim).
    assert re.search(r"A project `\.aid/state\.json` is refused in every folder, AID project or "
                     r"not, to the Write, Edit, MultiEdit and NotebookEdit tools", sm)
    assert "are refused in every form inside an AID project; outside one they are refused only " \
           "when the command text itself names `.aid/state.json`" in sm
    assert not re.search(r"AID project or not: to the Write, Edit, MultiEdit and NotebookEdit "
                         r"tools, and to Bash and PowerShell writes", sm)
    assert "`.aid/state.json` written through a name built at run time, outside AID projects" in sm


def test_t16_34_resolve_is_asked_and_non_exact_spellings_outside_aid_are_a_limit():
    sm = flat("docs/SECURITY-MODEL.md")
    assert '`node "<plugin>/skills/pipeline-orchestrator/gate.mjs" --resolve "<what was decided>"`' in sm
    assert "never runs it itself" in sm and "leading `!`" in sm
    assert "Outside AID projects a non-exact spelling is not caught" in sm


def test_t16_34_arithmetic_forms_are_caught_and_a1_list_unchanged():
    sm = flat("docs/SECURITY-MODEL.md")
    assert "Bash arithmetic is not mistaken for a heredoc" in sm
    for form in ("`$(( ))`", "`(( ))`", "`$[ ]`", "`${x:off:len}`", "`a[1<<2]=1`", "`let`",
                 "`declare -i`"):
        assert form in sm, form
    assert "the list of forms that are not caught is unchanged" in sm


def test_t16_34_execution_relevant_claude_paths_before_phase_4():
    sm = flat("docs/SECURITY-MODEL.md")
    assert "`.claude/{skills,agents,commands,output-styles,rules,hooks,workflows,routines,agent-memory}/`" in sm
    for name in ("`launch.json`", "`scheduled_tasks.json`", "`loop.md`", "`CLAUDE.md`", "`AGENTS.md`"):
        assert name in sm, name
    assert "From Phase 4 on these are ordinary project folders and files" in sm


def test_t16_34_run_time_script_operand_residual():
    sm = flat("docs/SECURITY-MODEL.md")
    assert re.search(r"An interpreter with a script operand built at run time is refused in every "
                     r"folder \(accepted false denial\)", sm)
    assert '`python "$SCRIPT" "$INPUT"`' in sm and "`$DOCKER $CMD $IMAGE`" in sm


def test_t16_34_residuals_from_ws_a_are_documented():
    sm = flat("docs/SECURITY-MODEL.md")
    # A1: run-time-built names outside AID, for Bash and PowerShell writes.
    assert re.search(r"outside AID projects\.\*\* .{0,200}a Bash or PowerShell write whose target "
                     r"name is built at run time", sm)
    # A2 class: non-exact --resolve spellings outside AID.
    assert "**Non-exact `gate.mjs --resolve` spellings, outside AID projects.**" in sm
    # T16-7: the three residual false denials.
    for form in ('`python "$SCRIPT" "$INPUT"`', '`py -3 "$TOOL" "$ARG"`',
                 '`for f in *.py; do python "$f" "$OUT"; done`'):
        assert form in sm, form
    # PowerShell refuses control-file reads too.
    assert "**PowerShell reads of control files are refused (accepted false denial).**" in sm
    assert "`Test-Path .aid`" in sm
    # aid_session inside $( ) / backticks: a CONFIRMED subcommand is denied in every folder.
    assert re.search(r"An `aid_session\.py` call with a confirmed subcommand .{0,200}inside a "
                     r"command substitution, `\$\(\.\.\.\)` or backticks .{0,120}is denied in "
                     r"every folder", sm)


def test_t16_34_substitution_rule_names_only_confirmed_subcommands():
    """E-R1-1: the doc said ANY aid_session.py call inside $( ) is denied everywhere, with
    `status` as the example; the gate denies only confirmed subcommands there."""
    sm = flat("docs/SECURITY-MODEL.md")
    assert "whatever its subcommand" not in sm
    assert '``echo "$(python "<plugin>/hooks/aid_session.py" status)"``' not in sm
    assert '``echo "$(python "<plugin>/hooks/aid_session.py" approve)"``' in sm
    for sub in ("approve", "advance", "jump", "init", "init --repair", "memory-sync",
                "memory-apply", "reset", "qa-pass"):
        assert re.search(r"confirmed subcommand \(.{0,160}`" + re.escape(sub) + "`", sm), sub
    assert re.search(r"Read-only subcommands such as `status` are not affected by this rule", sm)


def test_t16_34_residual_wording_matches_the_gate():
    """R1-07, E-R1-4, E-R1-5: residual bullets must not overstate or understate the gate."""
    sm = flat("docs/SECURITY-MODEL.md")
    # R1-07: run-time-built state.json names are not caught in an AID project from Phase 4/log/warn.
    assert "Inside an AID project the Bash allow-list (before Phase 4) and the control-file check still apply" not in sm
    assert re.search(r"From Phase 4, or at `log` or `warn`, it is not caught there either", sm)
    assert "Inside an AID project every other spelling is denied" not in sm
    assert re.search(r"Inside an AID project the gate denies the other spellings it can parse", sm)
    # E-R1-4: the run-time script operand rule is a Bash rule; PowerShell bare variables differ.
    assert re.search(r"From the Bash tool, `python \"\$SCRIPT\" \"\$INPUT\"`", sm)
    assert "`python $env:SCRIPT $env:INPUT`" in sm and "(#the-powershell-tool)" in sm
    # E-R1-5: PowerShell control-file reads are refused at every phase and level.
    assert "(from Phase 4 in an AID project)" not in sm
    assert re.search(r"In an AID project, at every phase and level, any PowerShell command that "
                     r"names a control file is refused, reads included", sm)
    assert "`Get-Content .aid\\state.json`" in sm


def test_t16_34_resolve_ask_wording_is_best_effort_not_absolute():
    """R2-E1: a gate.mjs --resolve call inside a `case` arm runs without a prompt in an AID
    project from Phase 4 or at log/warn, so the page must not say every other spelling is
    denied at every phase and level."""
    sm = flat("docs/SECURITY-MODEL.md")
    assert "every other spelling that runs it" not in sm
    assert re.search(r"--resolve .{0,600}Inside an AID project the gate denies the other "
                     r"spellings it can parse \(chained, a `\$\(\.\.\.\)` argument.{0,200}"
                     r"best effort, and a spelling it cannot parse \(for example inside a "
                     r"`case` arm\) is not caught", sm)


def test_t16_34_every_folder_behaviours_need_the_plugin():
    """R2-E2: the clone route registers hooks only in linked projects' settings.json, so the
    every-folder behaviours hold only with the plugin."""
    sm, pg = flat("docs/SECURITY-MODEL.md"), flat("docs/PHASE-GATES.md")
    assert "Everything on this page holds for both routes" not in sm
    assert re.search(r"The every-folder behaviours .{0,250}need the plugin: on the clone route "
                     r"only linked projects run AID hooks", sm)
    sec = sm[sm.index("## Hooks that act outside AID projects"):][:600]
    assert "needs the plugin install" in sec and "only linked projects run AID hooks" in sec
    sec = pg[pg.index("### Hooks that act outside AID projects"):][:600]
    assert "once the plugin is installed" in sec and "only linked projects run AID hooks" in sec


def test_t16_34_outside_aid_residuals_name_module_runners_and_command_line_words():
    """R2-E3 / R3-D2 (T16 (owner 2026-11-19), pin text changed by T16-34): since R2-04 module
    runners and command-line-carrying words are DENIED in every folder, so the docs must list
    them with the every-folder denials, not as forms that run without a prompt."""
    sm = flat("docs/SECURITY-MODEL.md")
    m = re.search(r"Two more groups of spellings are denied in every folder, phase and level, "
                  r"with the exact form to use: (.{0,700}?)\.( |$)", sm)
    assert m, "every-folder denial of module runners / command-line words missing"
    for form in ("`python -m cProfile`", "`runpy`", "`coverage run`", "`pipx run`",
                 "`git -c alias.<name>=!...`", "`script -c`", "`su -c`", "`make --eval`", "`env -S`"):
        assert form in m.group(1), form
    assert "Two more forms run a confirmed call without a prompt" not in sm
    assert "5f8f199" not in sm
    # What still gets through outside AID projects is named.
    for form in ('`env -iS "python <plugin>/hooks/aid_session.py approve"`', '`sh -lc "..."`',
                 "`coverage3 run`"):
        assert form in sm, form
    # The later-operand rule (R2-04) is documented as a false denial.
    assert '(`python <script> "<plugin>/hooks/aid_session.py" approve`) is denied in every folder' in sm


def test_t16_34_state_json_archive_and_unknown_cd_false_denials():
    """R3-D3 / R4-D1 (T16 B1): tar/zip of .aid/state.json is refused in every folder; a bare
    state.json write after an unresolved cd is refused only inside AID projects (outside it is
    allowed since B1), so the docs must not say "every folder" for it."""
    sm = flat("docs/SECURITY-MODEL.md")
    assert "Reading it stays allowed. |" not in sm
    assert "Reading it with the Read tool or a read-only command" in sm
    for form in ("`tar czf b.tgz .aid/state.json`", "`zip b.zip .aid/state.json`",
                 '`cd "$D" && echo x > state.json`', "`popd`"):
        assert form in sm, form
    assert re.search(r"Archiving `\.aid/state\.json` is refused in every folder \(accepted false "
                     r"denial\)\.\*\* A Bash command that is not read-only and names "
                     r"`\.aid/state\.json`", sm)
    assert "is refused in every folder, so a project that is not an AID project" not in sm
    m = re.search(r"\*\*Inside AID projects, bare `state\.json` writes after an unknown `cd`.{0,1600}?"
                  r"Outside AID projects these commands are allowed\.", sm)
    assert m, "inside-AID false-denial item missing"
    # T16 B1: the accepted false denials (T16-10 / T16-14 reverted to HEAD).
    for form in ("`cd .aid && ls`", "`cd ~/.aid && ls`", '`echo "run aid_session approve later"`',
                 '`git log --grep "aid_session approve"`', '`git commit -m "aid_session approve flow"`'):
        assert form in m.group(0), form


def test_t16_b1_state_json_residual_outside_aid_is_documented():
    """T16 B1 (E2 bounded): outside AID projects, writes reached through a cwd change, a shell
    -c body or interpreter code are an accepted residual; the docs must name it."""
    sm = flat("docs/SECURITY-MODEL.md")
    m = re.search(r"\*\*`\.aid/state\.json` written through a folder change, a shell `-c` body or "
                  r"interpreter code, outside AID projects\.\*\*(.{0,1500}?)- \*\*", sm)
    assert m, "B1 residual item missing"
    for form in ("`cd .aid && echo x > state.json`", "`env -C .aid touch state.json`",
                 "`sh -c 'cd .aid && echo x > state.json'`", "`echo x > .aid/state.json`"):
        assert form in m.group(1), form
    for rel in ("README.md", "docs/PHASE-GATES.md"):
        assert "a change of folder, a shell `-c` body or interpreter code" in flat(rel), rel


@pytest.mark.parametrize("rel", ["README.md", "INSTALLATION.md"])
def test_t16_b1_clone_route_caveat_for_folders_not_linked(rel):
    """R4-D2 (T16 B1): the every-folder refusal needs the plugin; on the clone route a folder
    that is not linked runs no AID hooks."""
    assert "a folder that is not linked runs no AID hooks" in flat(rel), rel
    if rel == "README.md":
        f = flat(rel)
        para = f[f.index("**Both install routes register the same gates.**"):]
        para = para[:para.index("AID's gates are a guardrail")]
        assert "a folder that is not linked runs no AID hooks" in para
        sec = f[f.index("### Hook scope outside AID projects"):][:500]
        assert "a folder that is not linked runs none of them" in sec


@pytest.mark.parametrize("rel", ["docs/PHASE-GATES.md", "README.md"])
def test_t16_34_hook_scope_lists_resolve_ask_and_state_json_refusal(rel):
    """E-R1-6: the every-folder lists in PHASE-GATES and README must name the gate.mjs
    --resolve ask and the every-folder refusal of a project .aid/state.json."""
    f = flat(rel)
    sec = f[f.index("utside AID projects"):]
    sec = sec[:sec.index("SECURITY-MODEL.md#hooks-that-act") if "#hooks-that-act" in sec else 3000]
    assert "`gate.mjs --resolve`" in sec, rel
    assert re.search(r"refuse a write to a project `\.aid/state\.json` in every folder", sec), rel


def test_t16_34_clone_route_says_phase_commands_need_the_plugin():
    """E-R1-2: a linked project has no ${CLAUDE_PLUGIN_ROOT}, so /aid-init etc. stop; the
    install docs must not send clone users to /aid-init without saying so."""
    ins, rd = flat("INSTALLATION.md"), flat("README.md")
    assert "(or `/aid-init`)" not in ins
    assert "# Open Claude Code and type: /aid-init" not in read("INSTALLATION.md")
    assert re.search(r"The gates are identical, but the phase commands are not", ins)
    assert '`! python "<AID>/hooks/aid_session.py" init <role> 0`' in ins
    assert "claude plugin install aid@AID" in ins
    assert re.search(r"The gates are identical, but AID's phase commands .{0,200}need the plugin", rd)
    # The commands really do refuse without the plugin root (the claim the docs rely on).
    for cmd in ("aid-init", "aid-start", "phase-approve", "phase-advance"):
        assert "was not replaced by a real path" in read("commands/{}.md".format(cmd)), cmd


def test_t16_35_aid_init_does_not_create_user_level_state_json():
    """E-R1-9: no AID code writes ~/.aid/state.json, and a state.json in a parent folder can
    make every folder under it look like an AID project. aid-init must not list it."""
    t = read("commands/aid-init.md")
    assert "- ~/.aid/state.json" not in t
    assert "├── state.json" not in t
    assert "Never create `~/.aid/state.json`" in t


def test_t16_37_aid_end_uses_the_i16_names():
    """E-R1-8: aid-end reviewed docs/prd/[feature].md, not the I-16 dated name."""
    t = read("commands/aid-end.md")
    assert "docs/prd/[feature].md" not in t and "docs/tech-spec/[feature].md" not in t
    assert "docs/prd/YYYY-MM-DD-<feature>.md" in t and "docs/tech-spec/YYYY-MM-DD-<feature>.md" in t


@pytest.mark.parametrize("rel", ["INSTALLATION.md", "README.md", "docs/SECURITY-MODEL.md"])
def test_t16_34_link_project_i9_is_documented_as_implemented(rel):
    f = flat(rel)
    assert "`node <AID>/scripts/link-settings.mjs <target> <AID>`" in f, rel
    assert re.search(r"exits? 1 before writing anything", f), rel
    assert "`aid_session.py init <role> 0`" in f and "`--role" in f, rel
    assert re.search(r"(?i)default (is )?`1`", f), rel
    assert re.search(r"exits? 0 with a warning", f), rel
    assert "`install.sh` and `install.bat` no longer create `.aid/state.json`" in f, rel


@pytest.mark.parametrize("rel", ["INSTALLATION.md", "docs/SECURITY-MODEL.md"])
def test_t16_59_minimum_claude_code_version_for_fail_closed(rel):
    text = flat(rel)
    assert "2.1.295" in text and "fail" in text.lower(), rel
    assert re.search(r"(?i)fail-closed.{0,120}2\.1\.295|2\.1\.295.{0,200}fail", text), rel


# --- T16-35: aid-init bootstraps through aid_session --------------------------------------

def test_t16_35_aid_init_bootstraps_through_aid_session():
    t = read("commands/aid-init.md")
    roles = t.index('python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" roles')
    phases = t.index('python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" phases <role>')
    init = t.index('python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" init <role> <phase>')
    assert roles < phases < init
    f = " ".join(t.split())
    assert "Never create or edit `.aid/state.json` yourself** (not with the Write, Edit" in f
    assert "Bash redirect" in f
    assert '! python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" init <role> <phase>' in t
    assert "`.aid/context.json`" in f and "Claude Code asks the user to confirm `init`" in f


# Same rule as test_aid_hooks.py::test_t3_5_no_markdown_tells_the_agent_to_write_state_json,
# applied per line: a line that names `.aid/state.json` next to a write verb must also carry a
# negation or name aid_session, so no single line reads as "write state.json yourself".
_STATE_WRITE = re.compile(
    r"(write|update|save|set|create|edit|sync|modify)[^|\n]*\.aid/state\.json|"
    r"\.aid/state\.json[^|\n]*(write|update|save|set |create|edit|sync|modify)", re.I)
_NEGATION = ("never", "not ", "don't", "only", "aid_session", "read-only", "created by", "refuse")


def test_t16_35_aid_init_no_line_reads_as_an_instruction_to_write_state_json():
    hits = []
    for n, line in enumerate(read("commands/aid-init.md").splitlines(), 1):
        low = line.lower()
        if "~/.aid/state.json" in low or not _STATE_WRITE.search(line):
            continue
        if not any(w in low for w in _NEGATION):
            hits.append("{}: {}".format(n, line.strip()))
    assert not hits, "\n".join(hits)


def test_t16_35_context_points_to_aid_init_which_creates_context_json():
    assert re.search(r"/aid-init.{0,120}creates \.aid/context\.json", flat("commands/context.md"))


# --- T16-36: phase-approve shows summary and checklist first ------------------------------

def test_t16_36_summary_and_checklist_precede_the_approve_call():
    t = read("commands/phase-approve.md")
    f = " ".join(t.split())
    # T17 (owner 2026-11-20): T17-27 runs the read-only `checklist` call first, so the
    # summary must precede the approve call, not every Bash call.
    assert "Before the `approve` call, print `## Phase N Summary` and `## Phase N Checklist`" in f
    assert "You MUST show both sections" in f
    call = t.index('aid_session.py" approve')
    assert t.index("## Phase N Summary") < call and t.index("## Phase N Checklist") < call
    assert "Display Phase Summary and Checklist (MANDATORY)" in t


# --- T16-37: one PRD / tech-spec naming scheme --------------------------------------------

PRD_NAME = "docs/prd/YYYY-MM-DD-<feature>.md"
SPEC_NAME = "docs/tech-spec/YYYY-MM-DD-<feature>.md"


@pytest.mark.parametrize("rel,names", [
    ("commands/prd.md", (PRD_NAME,)),
    ("commands/tech-spec.md", (PRD_NAME, SPEC_NAME)),
    ("commands/gate-check.md", (PRD_NAME, SPEC_NAME)),
    ("commands/phase-advance.md", (PRD_NAME, SPEC_NAME)),
])
def test_t16_37_the_four_commands_agree(rel, names):
    text = read(rel)
    for name in names:
        assert name in text, (rel, name)


def test_t16_37_no_legacy_save_instruction():
    hits = []
    for rel in doc_files():
        if not rel.startswith(("commands/", "skills/", "agents/", "rules/", "docs/")) and \
                not rel.startswith(("llm", ".well-known/")):
            continue
        lines = (REPO / rel).read_text(encoding="utf-8", errors="replace").splitlines()
        for n, line in enumerate(lines, 1):
            ctx = " ".join(lines[max(0, n - 2):n + 1]).lower()   # the line and its neighbours
            if re.search(r"(PRD|TECH-SPEC)-<", line) and "legacy" not in ctx and "rename" not in ctx:
                hits.append("{}:{}".format(rel, n))
    assert hits == [], hits


def test_t16_37_gate_check_accepts_legacy_names_with_a_rename_note():
    f = flat("commands/gate-check.md")
    assert "`docs/prd/PRD-<feature>.md`" in f and "rename note" in f and "not as a failed check" in f


def test_t16_37_prd_next_step_is_phase_2():
    t = read("commands/prd.md")
    assert "Move to Phase 2: Technical Specification" in t
    assert "Move to Phase 3: Technical Specification" not in t


# --- T16-38: qa-ship loads its skills; scratch scripts in the project ---------------------

def test_t16_38_qa_ship_loads_its_skills_first_and_keeps_scratch_in_the_project():
    t = read("commands/qa-ship.md")
    f = " ".join(t.split())
    load = f.index("load these three skills with the Skill tool")
    assert load < f.index("## Process")
    for name in ("`aid-qa-ship`", "`cucumber-bdd`", "`test-driven`"):
        assert name in f, name
    assert "`.aid/qa/tmp/`" in f and "never in `%TEMP%`" in f
    assert ".aid/qa/tmp/" in read(".gitignore").splitlines()


# --- T16-39: agent test commands are consistent ------------------------------------------

def test_t16_39_story_without_acceptance_criteria_is_fail():
    t = read("commands/test-phase-review.md")
    assert "expected PARTIAL" not in t and "Should PARTIAL" not in t
    assert "Story Without Acceptance Criteria (Should FAIL)" in t
    agent = read("agents/phase-review-agent.md")
    assert "`[CRITICAL]` Each story has acceptance criteria" in agent
    assert "| ANY critical item fails | FAIL |" in agent


@pytest.mark.parametrize("rel", ["commands/test-reflection.md", "commands/test-qa-validator.md",
                                 "commands/test-phase-review.md"])
def test_t16_39_one_report_file_name(rel):
    t = read(rel)
    assert not re.search(r"[\w-]+-test-report\.md", t), rel
    assert "Generate report.md in the output folder above" in t, rel
    expected = t[t.index("## Expected Output"):]
    assert "/report.md" in expected, rel


def test_t16_39_parent_writes_the_per_agent_reports():
    f = flat("commands/test-all-agents.md")
    assert 'subagent_type: "general-purpose"' not in f
    assert "not asked to write any file" in f
    assert "You, the parent session, write every report file from the returned results" in f
    for agent in ("aid-test-agent", "reflection-agent", "qa-validator-agent", "phase-review-agent"):
        assert "Then write `{}/report.md` from the returned results".format(agent) in f, agent


# --- T16-40: aid-status reads real data ---------------------------------------------------

def test_t16_40_aid_status_uses_the_status_subcommand():
    t = read("commands/aid-status.md")
    assert 'python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" status' in t
    f = " ".join(t.split())
    assert "Do not guess from files" in f
    for field in ("Last run", "Skills updated", "Memory entries", "Pending", "Processed"):
        assert field in t, field
    assert not re.search(r"(?<![\w./-])/aid (status|start|init|improve)", t)


def test_t16_40_status_json_fields_are_described():
    f = flat("commands/aid-status.md")
    for key in ("`project`", "`session`", "`feedback`", "`pending`", "`processed`",
                "`newest_pending`", "`improvement`", "`last_improvement_run`", "`skills_updated`",
                "`memory`", "`used`", "`total`", "`recommendations`", "`queued`"):
        assert key in f, key


@pytest.mark.parametrize("rel", ["commands/aid-status.md", "commands/aid-memory.md"])
def test_t16_40_no_hard_coded_memory_slot_total(rel):
    t = read(rel)
    # memory-system's SLOT_ALLOCATION totals 30; the docs must not pin another total.
    assert not re.search(r"\d+/38\b", t), rel
    assert "<memory.used>/<memory.total>" in t, rel


def test_t16_40_aid_memory_categories_match_slot_allocation():
    src = (REPO / "memory-system/memory_system/analysis/memory_sync.py").read_text(encoding="utf-8")
    block = re.search(r"SLOT_ALLOCATION = \{(.*?)\}", src, re.S).group(1)
    alloc = {k: int(v) for k, v in re.findall(r'"(\w+)":\s*(\d+)', block)}
    t = read("commands/aid-memory.md")
    for cat, n in alloc.items():
        assert "{} (<used>/{} slots)".format(cat, n) in t, cat
        assert re.search(r"{}:\s+<used>/{}\b".format(cat, n), t), cat
    assert "= {} slots".format(sum(alloc.values())) in t


def _doc_anchor_refs(rel):
    """(target path, anchor) for markdown links (relative to the file) and backtick refs
    (relative to the repo root) that carry an #anchor."""
    p = REPO / rel
    text = p.read_text(encoding="utf-8")
    refs = []
    for m in re.finditer(r"\]\(([^)#\s]+\.md)#([^)\s]+)\)", text):
        refs.append(((p.parent / m.group(1)).resolve(), m.group(2)))
    for m in re.finditer(r"`([\w./-]+\.md)#([\w-]+)`", text):
        refs.append(((REPO / m.group(1)).resolve(), m.group(2)))
    return refs


def test_t16_40_aid_status_anchor_resolves():
    refs = _doc_anchor_refs("commands/aid-status.md")
    assert refs, "no anchored reference"
    for target, anchor in refs:
        assert target.is_file(), target
        assert anchor in anchors(target), (target, anchor)


# --- T16-41: "42 sub-agents (7 reviewers ...)" --------------------------------------------

def test_t16_41_sub_agent_wording():
    plugin = json.loads(read(".claude-plugin/plugin.json"))
    market = json.loads(read(".claude-plugin/marketplace.json"))
    llm = read("llm.txt").splitlines()[3]
    for name, text in (("plugin.json", plugin["description"]),
                       ("marketplace.json", market["plugins"][0]["description"]),
                       ("llm.txt:4", llm)):
        # T17 (owner 2026-11-20): I-25 wording replaces "read-only reviewers".
        assert "42 sub-agents (7 reviewers that cannot write files with the Write, Edit or Bash tools" in text, name
    for rel in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", "llm.txt",
                "README.md", "docs/SECURITY-MODEL.md"):
        assert "review sub-agents" not in read(rel), rel
    assert "7 reviewers" in read("README.md") and "The 7 reviewers" in read("docs/SECURITY-MODEL.md")


# --- T16-42: llms-full tree and versions --------------------------------------------------

def test_t16_42_versions_and_license_match_plugin_json():
    plugin = json.loads(read(".claude-plugin/plugin.json"))
    pkg = json.loads(read("package.json"))
    assert pkg["version"] == plugin["version"]
    assert pkg["license"] == plugin["license"]
    full = read("llms-full.txt")
    stated = re.findall(r"(?mi)^version:\s*(\S+)\s*$", full)
    assert len(stated) == 2 and set(stated) == {plugin["version"]}, stated


def test_t16_42_llms_full_tree_shows_real_paths():
    full = read("llms-full.txt")
    tree = full[full.index("PROJECT LAYOUT"):full.index("TECHNOLOGY STACK")]
    assert ".claude/" not in tree and "prisma/" not in tree and "src/" not in tree
    top = re.findall(r"(?m)^[├└]── ([^\s#]+)", tree)
    assert top, tree
    for name in top:
        assert (REPO / name.rstrip("/")).exists(), name
    assert re.search(r"memory-system/\s*\n.*references/\s*\n.*roles/.*\n.*phases/", tree)
    assert (REPO / "skills/memory-system/references/roles").is_dir()
    assert (REPO / "skills/memory-system/references/phases").is_dir()


# --- T16-43: QUICK-REFERENCE "Source:" links resolve ---------------------------------------

def test_t16_43_quick_reference_sources_resolve():
    files = sorted((REPO / "skills/memory-system/references").glob("*/*/QUICK-REFERENCE.md"))
    assert len(files) == 11
    links = []
    for p in files:
        line = p.read_text(encoding="utf-8").splitlines()[2]
        assert "**Source**" in line, p
        for rel in re.findall(r"`([^`]+)`", line):
            links.append((p, rel))
    assert len(links) == 12, links
    bad = [(str(p.relative_to(REPO)), rel) for p, rel in links if not (p.parent / rel).resolve().is_file()]
    assert bad == [], bad


# --- T16-44: every /aid reference outside memory-system resolves ---------------------------

def test_t16_44_aid_slash_references_resolve():
    cmds = {p.stem for p in (REPO / "commands").glob("*.md")}
    pat = re.compile(r"(?<![\w./-])/aid(?:([ -])([a-z][a-z-]*))")
    bad = []
    for rel in doc_files():
        for n, line in enumerate((REPO / rel).read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for m in pat.finditer(line):
                if m.group(1) == " " or "aid-" + m.group(2) not in cmds:
                    bad.append("{}:{} {}".format(rel, n, m.group(0)))
    assert bad == [], bad[:40]


# --- T16-45: phase numbering 0-5 everywhere -----------------------------------------------

@pytest.mark.parametrize("rel", ["integrations/chrome-devtools/README.md", "commands/jira-breakdown.md",
                                 ".well-known/llms.txt", "llms.txt", "skills/phase-enforcement/SKILL.extended.md"])
def test_t16_45_phases_are_0_to_5(rel):
    text = read(rel)
    assert not re.search(r"(?i)\bphases? [6-9]\b", text), rel
    assert not re.search(r"(?i)\b5-phase\b|\b5 phases\b", text), rel


def test_t16_45_phase_0_is_listed():
    wk = read(".well-known/llms.txt")
    assert "> 0. Discovery" in wk and "phases 0-5" in wk
    assert "Prisma" not in wk
    assert "Phase 0 Discovery" in read("llms.txt")
    assert "### Phase 4: Development" in read("integrations/chrome-devtools/README.md")
    assert "| 0 | Discovery |" in read("skills/phase-enforcement/SKILL.extended.md")
    assert "Phase 5: Development" not in read("commands/jira-breakdown.md")


# --- T16-46: no plaintext .env.test key guidance ------------------------------------------

@pytest.mark.parametrize("rel", ["rules/testing/test-security.md",
                                 "skills/role-qa-engineer/references/security-in-tests.md",
                                 "skills/role-qa-engineer/SKILL.extended.md"])
def test_t16_46_env_test_holds_no_secrets(rel):
    """Every code block that shows a .env.test / .env.example file holds settings only: no
    key, token, secret or password value and no credentials inside a URL. (Blocks that show
    a hard-coded secret as the BAD example are not env-file blocks.)"""
    text = read(rel)
    blocks = [b for b in re.findall(r"```[^\n]*\n(.*?)```", text, re.S)
              if ".env.test" in b or ".env.example" in b]
    assert blocks, rel
    bad = [line for b in blocks for line in b.splitlines()
           if (re.match(r"^\s*(//\s*)?(export\s+)?[A-Z_]*(KEY|TOKEN|SECRET|PASSWORD)\s*=", line)
               and "$(" not in line)
           or re.search(r"://[^/\s:@]+:[^/\s@]+@", line)]
    assert bad == [], (rel, bad)
    assert "testpassword" not in text and "Add real test/sandbox credentials there" not in text
    assert "keystore" in text.lower(), rel


# --- T16-47: Atlassian env names in docs (reproduced: the pinned 3.3.0 reads SITE_NAME) ----

@pytest.mark.parametrize("rel", [".env.example", "integrations/jira/README.md", "INSTALLATION.md",
                                 "README.md", "llms-full.txt", "commands/jira-breakdown.md"])
def test_t16_47_docs_name_atlassian_site_name(rel):
    text = read(rel)
    assert "ATLASSIAN_SITE_URL" not in text or "does not read" in text, rel
    assert "ATLASSIAN_SITE_NAME" in text, rel


def test_t16_47_jira_readme_keeps_oauth_first():
    t = read("integrations/jira/README.md")
    assert t.index("OAuth") < t.index("ATLASSIAN_SITE_NAME")
    assert "subdomain only" in t


# --- T16-48 / T16-56: .gitignore ------------------------------------------------------------

def test_t16_48_gitignore_token_wording():
    text = read(".gitignore")
    assert "Put real values in .mcp.json" not in text
    assert re.search(r"tokens are\s+(#\s*)?read from environment variables", text)
    assert "keystore" in text


def test_t16_56_aid_audit_is_gitignored():
    assert ".aid/audit/" in [line.strip() for line in read(".gitignore").splitlines()]


# --- T16-50: pre-commit hooks pinned to SHAs -------------------------------------------------

def test_t16_50_precommit_revs_are_full_shas():
    raw = read(".pre-commit-config.yaml")
    cfg = yaml.safe_load(raw)
    remote = [r for r in cfg["repos"] if r["repo"] != "local"]
    assert len(remote) == 4
    for r in remote:
        assert re.fullmatch(r"[0-9a-f]{40}", str(r["rev"])), r
    for line in raw.splitlines():
        if line.strip().startswith("rev:"):
            assert re.search(r"#\s*frozen: v\d", line), line
    assert any(r["repo"].endswith("astral-sh/ruff-pre-commit") for r in remote)
    ds = [h for r in remote for h in r["hooks"] if h["id"] == "detect-secrets"][0]
    assert "mcp\\.json\\.example" not in ds.get("exclude", "")


# --- T16-52: untrusted-content rule reaches commands, skills and agents ---------------------

@pytest.mark.parametrize("rel", ["commands/code-review.md", "commands/jira-breakdown.md",
                                 "commands/discovery.md", "skills/pre-prd-research/SKILL.md",
                                 "skills/aid-impl-plan/SKILL.md", "agents/memory-analysis-agent.md"])
def test_t16_52_references_untrusted_content_rule(rel):
    assert "rules/general/untrusted-content.md" in read(rel), rel


# --- T16-53: breather mark.mjs is run by the user with ! ------------------------------------

@pytest.mark.parametrize("rel", ["commands/breather-stop.md", "commands/breather-start.md", "README.md"])
def test_t16_53_mark_mjs_is_handed_to_the_user(rel):
    text = read(rel)
    hits = list(re.finditer(r"node ~/\.claude/hooks/breather/mark\.mjs", text))
    assert hits, rel
    for m in hits:
        assert text[m.start() - 2:m.start()] == "! ", (rel, text[m.start() - 40:m.end()])


# --- T16-54: HOL gate threshold ---------------------------------------------------------------

def test_t16_54_hol_min_score_100():
    wf = yaml.safe_load(read(".github/workflows/hol-plugin-scanner.yml"))
    step = [s for j in wf["jobs"].values() for s in j["steps"]
            if "ai-plugin-scanner-action" in s.get("uses", "")][0]
    assert step["with"]["min_score"] == 100
    assert step["with"]["fail_on_severity"] == "high"


# --- T16-55: verify-run.sh quoting (SC2295, reproduced with shellcheck 0.10.0) ---------------

def test_t16_55_verify_run_quotes_prefix_patterns():
    rel = "skills/autoresearch/verify-run.sh"
    text = read(rel)
    assert not re.search(r"\$\{\w+#\$\w+", text), re.findall(r"\$\{\w+#\$\w+[^}]*\}", text)
    sc = shutil.which("shellcheck")
    if sc:
        p = subprocess.run([sc, "-f", "gcc", str(REPO / rel)], capture_output=True, text=True)
        assert "SC2295" not in p.stdout, p.stdout


# --- T16-58: no doc cites the HOL score as enforcement evidence (guard) ----------------------

def test_t16_58_no_doc_cites_hol_score_as_evidence():
    hits = []
    for rel in doc_files():
        if rel.startswith(".github/"):
            continue
        for n, line in enumerate((REPO / rel).read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if re.search(r"\bHOL\b|hashgraph|plugin scanner", line, re.I) and re.search(r"(?i)score", line):
                hits.append("{}:{}".format(rel, n))
    assert hits == [], hits


# --- T16-60: breather README documents the reproduced installer limits ----------------------

def test_t16_60_breather_readme_documents_uninstall_and_claude_home():
    f = flat("integrations/breather/README.md")
    assert "Uninstall strips by substring." in f and "whose text contains `breather`" in f
    assert "`CLAUDE_HOME` moves the files, not the hook paths." in f
    assert "`node ~/.claude/hooks/breather/<file>.mjs`" in f
    assert "Upstream fix needed (owner action)" in f


# --- T16-61: chrome-devtools --no-sandbox is labelled CI-only (A-46, guard) ------------------

def test_t16_61_no_sandbox_is_labelled_ci_only():
    lines = read("integrations/chrome-devtools/README.md").splitlines()
    idx = [i for i, line in enumerate(lines) if "--no-sandbox" in line and line.strip().startswith("npx")]
    assert idx
    for i in idx:
        window = " ".join(lines[max(0, i - 8):i + 1])
        assert re.search(r"(?i)CI (containers )?only", window), window


# --- T16-62: observations from passing checks -----------------------------------------------

def test_t16_62_test_review_reads_the_plugin_copy():
    t = read("commands/test-review.md")
    for m in re.finditer(r"skills/test-driven/", t):
        assert t[:m.start()].endswith("${CLAUDE_PLUGIN_ROOT}/"), t[m.start() - 30:m.end() + 20]


def test_t16_62_aid_memory_names_the_exact_call():
    assert 'python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" memory-sync' in read("commands/aid-memory.md")


@pytest.mark.parametrize("rel", ["commands/aid-analyze.md", "commands/aid-dashboard.md"])
def test_t16_62_analyze_and_dashboard_load_the_memory_system_skill(rel):
    f = flat(rel)
    assert "load the `memory-system` skill with the Skill tool" in f, rel


def test_t16_62_setup_uses_the_absolute_breather_path():
    t = read("commands/setup.md")
    assert 'node "${CLAUDE_PLUGIN_ROOT}/integrations/breather/install.mjs"' in t
    assert "`node integrations/breather/install.mjs`" not in t


def test_t16_62_yolo_off_matches_the_t15_31_ask_wording():
    f = flat("commands/yolo-off.md")
    assert "AID's ask rules for phase changes and memory writes still prompt in every permission mode" not in f
    assert re.search(r"(?i)does not document whether a hook's \"ask\" does", f)
    assert re.search(r"(?i)do not count on a prompt in this mode", f)
