"""
T15 WS-E (T15-acceptance.md, T15-31..T15-45): docs and commands match the 3.0.8 release gate.

WHY: the docs promised things the hooks did not do (memory confirmation "only in AID
projects", "folders without AID are never touched", "no phase can be skipped"), told users
to keep tokens in a plaintext .env, told the agent to write QA verdict files it must not
write, and carried stale counts. A user or reviewer who trusts these docs misjudges the
risk; an agent that follows them is refused or, worse, forges a QA pass.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import unquote

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]


def read(rel):
    return (REPO / rel).read_text(encoding="utf-8")


def flat(rel):
    """Text with whitespace collapsed, so a phrase may wrap across lines."""
    return " ".join(read(rel).split())


def tracked(*patterns):
    out = subprocess.run(["git", "ls-files", *patterns], cwd=str(REPO), capture_output=True,
                         text=True).stdout
    return [REPO / p for p in out.splitlines() if p and (REPO / p).is_file()]


def shipped_docs():
    """Every shipped doc, skill, agent, command and rule (text the agent or the user reads)."""
    pats = ["README.md", "CLAUDE.md", "INSTALLATION.md", "SECURITY.md", "llm.txt", "llms.txt",
            "llms-full.txt", ".well-known/*", "docs/*", "commands/*", "agents/*", "agent-assets/*",
            "rules/*", "skills/*", "integrations/*.md", "integrations/**/*.md", ".aid/qa/*"]
    return [p for p in tracked(*pats) if p.suffix in (".md", ".txt", ".yaml", ".yml", "")]


# --- T15-31: D1/D2/D3 in the security docs -----------------------------------

ASK_SET = ("approve", "advance", "jump", "init", "memory-sync", "memory-apply", "reset", "qa-pass")


@pytest.mark.parametrize("rel", ["docs/SECURITY-MODEL.md", "README.md"])
def test_t15_31_gate_asks_in_every_folder(rel):
    text = flat(rel)
    low = text.lower()
    assert "in every folder" in low, rel
    for sub in ASK_SET:
        assert "`{}`".format(sub) in text, (rel, sub)
    assert "breather installer" in low and "init-project.sh" in text, rel
    assert "second layer" in low, rel
    assert "-p" in text and "dontask" in low and "denied" in low, rel


def test_t15_31_no_only_inside_aid_projects_claim():
    pat = re.compile(r"(?i)only (inside|in) AID projects")
    hits = []
    for p in shipped_docs():
        for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if pat.search(line) and re.search(r"(?i)memory|confirm|ask", line):
                hits.append("{}:{}".format(p.relative_to(REPO), n))
    assert hits == [], hits


def test_t15_31_powershell_section_reflects_t15_4():
    text = flat("docs/SECURITY-MODEL.md")
    sec = text[text.index("### The PowerShell tool"):text.index("### Agents, commands")]
    assert "canonical" in sec and '"ask"' in sec, sec[:300]
    assert "Every other PowerShell command that mentions `aid_session` is refused in an AID project" in sec


def test_t15_31_residuals_documented():
    text = flat("docs/SECURITY-MODEL.md")
    # R-01: from Phase 4 the capability dirs are writable.
    assert re.search(r"From Phase 4, a project's `\.claude/skills`, `\.claude/agents` and "
                     r"`\.claude/commands` are writable", text)
    # A-38 (accepted): interpreters resolve from PATH.
    assert "Interpreters resolve from `PATH` (accepted)" in text


@pytest.mark.parametrize("rel", ["docs/SECURITY-MODEL.md", "README.md"])
def test_t15_31_ask_scope_as_built(rel):
    """WS-A as built: non-live installed roots, log/warn still asks, text-gate limit."""
    text = flat(rel)
    low = text.lower()
    # Any subcommand from an installed copy that is not the live one is asked.
    assert re.search(r"any `aid_session\.py` subcommand.{0,80}installed copy of the plugin "
                     r"that is not the live one", text), rel
    # In AID projects a confirmed call is still asked at log/warn (gate or baseline).
    assert re.search(r"still asked when the (gate|gate or the integrity baseline) is "
                     r"(lowered to |at )`log` or `warn`", text), rel
    # Run-time-built names ($'...', a variable) are denied; what a text gate cannot see is
    # indirection that leaves no trace (R2-E2).
    assert "outside aid projects" in low and "$'" in text and "variable" in low, rel
    assert "cannot see" in low, rel


@pytest.mark.parametrize("rel", ["docs/SECURITY-MODEL.md", "README.md"])
def test_t15_31_hidden_name_limit_covers_aid_projects_from_phase_4(rel):
    """E-1: a hidden script name is not asked in an AID project from Phase 4 on either."""
    text = flat(rel)
    assert re.search(r"(?i)outside AID projects, and in an AID project from Phase 4 on \(or from "
                     r"Phase 0 when `phase_gate_bash` is lowered to `log` or `warn`\), such a "
                     r"call is neither asked nor denied", text), rel
    assert "Before Phase 4 at `block`, the Bash allow-list refuses it" in text, rel
    assert "Outside AID projects the gate reads the command text only" not in text, rel


@pytest.mark.parametrize("rel", ["docs/SECURITY-MODEL.md", "README.md"])
def test_t15_31_run_time_built_names_are_denied_and_indirection_is_the_gap(rel):
    """R2-E2/R2-C4: after R1-C1 a run-time-built name is DENIED everywhere; the real gap is
    indirection that leaves no trace in the command (copy, wrapper, eval of a file)."""
    text = flat(rel)
    low = text.lower()
    # The caught `$s.py` example must not be used as an uncaught one any more.
    assert 's=aid_session; python "$s.py" reset' not in text, rel
    assert "a spelling that hides the script name" not in low, rel
    # R3-E1: the check is best effort; it denies the spellings it can parse.
    assert not re.search(r"script name or subcommand is built at run time.{0,120}is denied in "
                         r"every folder", text), rel
    assert re.search(r"check of run-time-built names is best effort", text), rel
    assert re.search(r"denies the run-time-built spellings it can parse, in every folder", text), rel
    # T15 A1 / R4-E1: timeout/winpty, two variables and a `#` comment are DENIED now; they
    # must not be listed as "not caught" any more.
    assert "Some wrapper and comment forms are not caught" not in text, rel
    assert "`#` comment that holds a quote" not in text, rel
    assert re.search(r"`timeout` or `winpty`", text), rel
    # T15 A1: exactly the accepted residual forms are named as not caught.
    nc = text[text.index("are not caught:"):]
    nc = nc[:nc.index("What ")]
    for form in A1_FORMS:
        assert form in nc, (rel, form)
    assert "accepted limit" in text, rel
    assert re.search(r"indirection that leaves no trace in the command", text), rel
    for word in ("copy of `aid_session.py`", "wrapper script", "`eval` of a file"):
        assert word in text, (rel, word)


def test_t15_31_powershell_run_time_built_names_and_gap():
    """R3-E2: the PowerShell bullet says parseable run-time-built names are refused in every
    folder, that some forms are missed, and that indirection is the gap."""
    text = flat("docs/SECURITY-MODEL.md")
    sec = text[text.index("### The PowerShell tool"):text.index("### Agents, commands")]
    assert "a command that builds the name at run time is not caught" not in sec
    # NEW-2: only a built SUBCOMMAND (and the literal path in a ( ) expression) is refused in
    # every folder; a built script name is not always caught.
    assert "script name or subcommand is built at run time" not in sec
    assert re.search(r"Refused in every folder: a confirmed call whose subcommand is built at "
                     r"run time \(`\$\(\.\.\.\)`, `\$env:`, `\[char\]`, a `\( \)` expression, a "
                     r"variable\), a script path written out inside a `\( \)` expression", sec)
    assert "Other run-time-built script names are not always caught" in sec
    # R4-E2: the Get-ChildItem wildcard form is DENIED now, so it is named as refused, not as
    # a form that is missed; the missed examples are the ones the gate really allows.
    assert "for example a name found with `Get-ChildItem`" not in sec
    assert re.search(r"Refused in every folder: .{0,400}and a script name found with "
                     r"`Get-ChildItem` and a wildcard", sec)
    assert re.search(r"Some forms are not caught outside AID projects, for example a script "
                     r"operand that is only a variable \(`python \$env:SCRIPT reset`\)", sec)
    assert re.search(r"indirection that leaves no trace in the command, such as a wrapper "
                     r"script or a copy of `aid_session\.py`", sec)
    # RR-1: the bare-variable operand is not refused by the "mentions aid_session" rule.
    assert "in an AID project the rule above refuses them" not in sec
    assert re.search(r"A bare variable operand does not name it: in an AID project it is "
                     r"refused only before Phase 4 at `block`", sec)


# RR-1..RR-4, RR-6: every security claim names where it holds (folder kind, phase, level) and
# never says "every form / every phase" where a probe of the real hook shows otherwise.
def test_t15_31_docs_do_not_overclaim_the_aid_project_net():
    sm, rd, pg = flat("docs/SECURITY-MODEL.md"), flat("README.md"), flat("docs/PHASE-GATES.md")
    # RR-2/RR-3: the old blanket claims are gone.
    assert "still denied in any of these forms, in every phase" not in sm
    assert "is still denied in these forms" not in rd
    for text in (sm, rd):
        assert re.search(r"the very next word is `approve`, `advance`, `jump`, `init`, "
                         r"`memory-sync` or `memory-apply`", text)
        assert re.search(r"with `reset` or `qa-pass`", text)
        assert "a script name held in a variable" in text
        assert re.search(r"`/dev/fd/N` or `python -` by a redirect or a pipe", text)
        # RR-6: the not-caught xargs pipe is the variable one; the literal pipe is denied.
        assert "`xargs` fed by a pipe with the script name in a variable" in text
        assert '`echo approve | xargs python "<plugin>/hooks/aid_session.py"`' in text
    # RR-4: the PowerShell refusal is scoped to text that names aid_session, with the caveat.
    assert "So is any `aid_session.py` call from the PowerShell tool" not in sm
    assert "So is any `aid_session.py` call from the PowerShell tool" not in pg
    assert "From PowerShell, only the exact canonical form" not in rd
    for text in (sm, rd, pg):
        assert re.search(r"(?i)every (other )?PowerShell command whose text names `aid_session`",
                         text)
        assert re.search(r"hidden in a variable \(`python \$env:SCRIPT reset`\)", text)
        assert re.search(r"from Phase 4 on, or (from Phase 0 )?at `log` or `warn`", text)


# --- T15 A1/A2: the documented verdicts are the real ones -----------------------
# WHY: R4-E1/R4-E2 found the docs listing as "not caught" forms the gate denies, and not
# naming the forms that really get through. These tests run the real hook for the forms the
# docs name, so the docs cannot drift from the gate again.

A1_FORMS = ("`pythonw`", "`pyw`", "`exec -a`", "`env -u`", "`sudo -u`", "`setsid`", "`flock`",
            "`chronic`", "`case`", "`xargs` fed by a pipe", "`-a`",
            "`eval` of a string built in a variable", "`/dev/stdin`", "`/dev/fd/N`", "`<( )`")

_R = str(REPO).replace("\\", "/")
_S = _R + "/hooks/aid_session.py"


def _marker_above(p):
    return any((d / ".aid" / "state.json").is_file() or (d / ".aid" / "hooks" / "config.json").is_file()
               for d in [p] + list(p.parents))


class _Gate(object):
    """A plain folder, AID projects at Phase 1 and Phase 4 (`block`), at Phase 1 and Phase 4
    with `phase_gate_bash` lowered to `log`, and at Phase 4 at `warn` (RR-5, NEW-4: the docs
    make claims per phase and level too)."""

    def __init__(self, root):
        self.home = root / "home"
        (self.home / ".claude").mkdir(parents=True)
        self.places = {"nonAID": root / "n", "p1": root / "p1", "p4": root / "p4",
                       "p1log": root / "p1log", "p4log": root / "p4log", "p4warn": root / "p4warn"}
        for name, p in self.places.items():
            p.mkdir()
            if name == "nonAID":
                continue
            for d in (".aid/hooks", ".claude", "docs"):
                (p / d).mkdir(parents=True, exist_ok=True)
            (p / ".claude" / "settings.json").write_text("{}", encoding="utf-8")
            (p / ".aid" / "state.json").write_text(json.dumps({"current_phase": int(name[1])}),
                                                   encoding="utf-8")
            level = next((lv for lv in ("log", "warn") if name.endswith(lv)), "block")
            (p / ".aid" / "hooks" / "config.json").write_text(json.dumps(
                {"enforcement": {"phase_gate_write": "block", "phase_gate_bash": level}}),
                encoding="utf-8")

    def verdicts(self, cmd, tool="Bash"):
        """{place: verdict} for every place, so a test states the whole row at once."""
        return {w: self.verdict(w, cmd, tool) for w in self.places}

    def verdict(self, where, cmd, tool="Bash"):
        cwd = self.places[where]
        env = dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home),
                   AID_HOME=str(self.home / ".aid"))
        env.pop("CLAUDE_PROJECT_DIR", None)
        env.pop("CLAUDE_CONFIG_DIR", None)
        payload = {"session_id": "docs-" + os.urandom(6).hex(), "cwd": str(cwd), "tool_name": tool,
                   "tool_input": {"command": cmd.replace("<S>", _S).replace("<R>", _R)}}
        p = subprocess.run(["node", str(REPO / "hooks" / "hook-runner.mjs"), "phase-gate-bash"],
                           input=json.dumps(payload), capture_output=True, text=True,
                           cwd=str(cwd), env=env, timeout=60)
        assert p.returncode == 0, p.stderr[-600:]
        out = p.stdout.strip()
        if not out:
            return "ALLOW"
        d = json.loads(out).get("hookSpecificOutput", {}).get("permissionDecision")
        return d.upper() if d in ("deny", "ask") else "ALLOW"


@pytest.fixture
def gate(tmp_path):
    if shutil.which("node") is None:
        pytest.skip("node is needed for hook-runner.mjs")
    root = tmp_path
    if _marker_above(root):
        root = Path(tempfile.mkdtemp(prefix="aid-t15d-", dir=tmp_path.anchor))
        if _marker_above(root):
            shutil.rmtree(root, ignore_errors=True)
            pytest.skip("no directory without an AID marker ancestor is available")
    yield _Gate(root)
    if root != tmp_path:
        shutil.rmtree(root, ignore_errors=True)


def _row(nonAID, p1, p4, lowered):
    """The whole verdict row; `lowered` is the verdict at p1/log, p4/log and p4/warn."""
    return {"nonAID": nonAID, "p1": p1, "p4": p4, "p1log": lowered, "p4log": lowered,
            "p4warn": lowered}


def _names_session(cmd):
    """RR-5: a pin for a form the docs say runs aid_session.py must really name it; a form
    that never names the script would pass for any unrelated python command."""
    return "aid_session.py" in cmd.replace("<S>", _S)


# Forms the docs list as not caught (T15 A1), written with the script path out and the very
# next word one of approve/advance/jump/init/memory-sync/memory-apply. SECURITY-MODEL and
# README: outside AID they run without a prompt; in an AID project the allow-list refuses
# them before Phase 4 at `block`, and the text check refuses them from Phase 4 and at `log`.
@pytest.mark.parametrize("cmd", [
    'pythonw "<S>" approve',
    'pyw "<S>" approve',
    'exec -a x python "<S>" approve',
    'env -u FOO python "<S>" approve',
    'sudo -u x python "<S>" approve',
    'setsid python "<S>" approve',
    'flock /tmp/l python "<S>" approve',
    'chronic python "<S>" approve',
    'case x in x) python "<S>" approve;; esac',
    'xargs -a /dev/null python "<S>" approve',
    'c="python <S> approve"; eval "$c"',
])
def test_t15_31_listed_residual_forms_with_the_path_written_out(gate, cmd):
    assert _names_session(cmd)
    assert gate.verdicts(cmd) == _row("ALLOW", "DENY", "DENY", "DENY"), cmd


# RR-2/RR-3: forms the docs say get through in an AID project from Phase 4 and at `log`,
# although the command text names aid_session.py and a confirmed subcommand: a variable-held
# name, the script fed to /dev/stdin, /dev/fd/N or `python -` by a redirect or a pipe, code
# built inside a `<( )`, and `reset`/`qa-pass` in the residual forms. Only the Phase 1
# `block` allow-list refuses them.
@pytest.mark.parametrize("cmd", [
    'S="<S>"; pythonw "$S" approve',
    'S="<S>"; echo approve | xargs python "$S"',
    'S="<S>"; xargs -a args.txt python "$S"',
    'S="<S>"; c="python $S approve"; eval "$c"',
    'S="<S>"; case x in x) python "$S" approve;; esac',
    'python /dev/stdin approve < "<S>"',
    'cat "<S>" | python /dev/stdin approve',
    'python /dev/fd/3 approve 3<"<S>"',
    'cat "<S>" | python - approve',
    'S="<S>"; python <(printf \'import sys,runpy\\nsys.argv=["%s","approve"]\\n'
    'runpy.run_path("%s")\' "$S" "$S")',
    'pythonw "<S>" reset',
    'chronic python "<S>" qa-pass',
])
def test_t15_31_listed_residual_forms_get_through_from_phase_4_and_at_log(gate, cmd):
    assert _names_session(cmd)
    assert gate.verdicts(cmd) == _row("ALLOW", "DENY", "ALLOW", "ALLOW"), cmd


def test_t15_31_process_substitution_followed_by_a_confirmed_word_is_denied(gate):
    """SECURITY-MODEL: a `<( )` followed by a confirmed subcommand is denied in every folder."""
    cmd = 'python <(cat "<S>") approve'
    assert set(gate.verdicts(cmd).values()) == {"DENY"}


# Forms the docs used to list as not caught and now name as denied (R4-E1/R4-E2).
@pytest.mark.parametrize("tool,cmd", [
    ("Bash", 'timeout 5 python "<S>" approve'),
    ("Bash", 'winpty python "<S>" approve'),
    ("Bash", 'S="<S>"; C=approve; python "$S" "$C"'),
    ("Bash", 'S="<S>"; python "$S" approve # it\'s'),
    ("Bash", 'S="<S>"; eval "python $S approve"'),
    ("Bash", 'echo approve | xargs python "<S>"'),
    ("PowerShell", "python (Get-ChildItem <R>/hooks/aid_sess*.py).FullName approve"),
])
def test_t15_31_forms_no_longer_listed_as_missed_are_denied(gate, tool, cmd):
    assert set(gate.verdicts(cmd, tool).values()) == {"DENY"}, cmd


def test_t15_31_powershell_bare_variable_operand_gets_through_from_phase_4_and_at_log(gate):
    """RR-1/RR-4: the bare-variable operand does not name aid_session, so in an AID project
    only the Phase 1 `block` rule (no PowerShell before Phase 4) refuses it."""
    cmd = "python $env:SCRIPT reset"
    assert gate.verdicts(cmd, "PowerShell") == _row("ALLOW", "DENY", "ALLOW", "ALLOW")


@pytest.mark.parametrize("cmd", [
    "python (Get-Command aid_session.py).Source reset",
    '$s="<S>"; python $s reset',
    'python "<S>" status',
    "Get-Content <S>",
])
def test_t15_31_powershell_naming_aid_session_is_refused_in_aid_at_every_level(gate, cmd):
    """The PowerShell bullet: in an AID project any PowerShell command whose text names
    aid_session (other than the canonical confirmed call) is refused in every phase and at
    every level, including the Get-Command form that is missed outside AID."""
    v = gate.verdicts(cmd, "PowerShell")
    del v["nonAID"]
    assert set(v.values()) == {"DENY"}, (cmd, v)


def test_t15_31_powershell_canonical_confirmed_call_is_asked_everywhere(gate):
    assert set(gate.verdicts('python "<S>" approve', "PowerShell").values()) == {"ASK"}


# NEW-2: the PowerShell bullet names what is refused everywhere (a built subcommand, the
# literal path or quoted parts inside a ( ) expression) and what gets through where.
@pytest.mark.parametrize("cmd", ['python "<S>" $([char]97+\'pprove\')',
                                 'python "<S>" ([char]97+\'pprove\')',
                                 'python ("<S>") approve',
                                 "python ('aid_sess'+'ion.py') approve"])
def test_t15_31_powershell_forms_documented_as_refused_everywhere(gate, cmd):
    sec = flat("docs/SECURITY-MODEL.md")
    sec = sec[sec.index("### The PowerShell tool"):sec.index("### Agents, commands")]
    assert '`python ("<plugin>/hooks/aid_session.py") approve`' in sec
    assert "`python ('aid_sess'+'ion.py') approve`" in sec
    assert set(gate.verdicts(cmd, "PowerShell").values()) == {"DENY"}, cmd


def test_t15_31_powershell_char_built_script_name_gets_through_as_documented(gate):
    """NEW-2: `[char]` inside a ( ) expression hides the script name: outside AID, and in an
    AID project from Phase 4 on or at log/warn, it runs without a prompt."""
    sec = flat("docs/SECURITY-MODEL.md")
    sec = sec[sec.index("### The PowerShell tool"):sec.index("### Agents, commands")]
    assert re.search(r'A name built with `\[char\]` inside a `\( \)` expression '
                     r'\(`python \("<plugin>/hooks/aid_"\+\[char\]115\+"ession\.py"\) approve`\) '
                     r'does not name it: it runs without a prompt outside AID projects, and in '
                     r'an AID project from Phase 4 on, or at `log` or `warn`; it is refused only '
                     r'before Phase 4 at `block`', sec)
    cmd = 'python ("<R>/hooks/aid_"+[char]115+"ession.py") approve'
    assert gate.verdicts(cmd, "PowerShell") == _row("ALLOW", "DENY", "ALLOW", "ALLOW")


def test_t15_31_powershell_variable_held_path_gets_through_only_outside_aid(gate):
    """NEW-2: `$s="<S>"; python $s approve` names aid_session, so in an AID project it is
    refused at every phase and level; outside AID it runs without a prompt."""
    sec = flat("docs/SECURITY-MODEL.md")
    sec = sec[sec.index("### The PowerShell tool"):sec.index("### Agents, commands")]
    assert re.search(r'Some forms are not caught outside AID projects, .{0,200}'
                     r'\(`\$s="<plugin>/hooks/aid_session\.py"; python \$s approve`\)', sec)
    assert gate.verdicts('$s="<S>"; python $s approve', "PowerShell") == \
        _row("ALLOW", "DENY", "DENY", "DENY")


# NEW-1 / NEW-3 (D2, A2): from the PowerShell tool the exact plugin-root form of the breather
# installer and init-project.sh is asked everywhere; other spellings are not.
def test_t15_6_docs_powershell_exact_form_of_the_two_scripts_is_asked(gate):
    sm, rd, pg = flat("docs/SECURITY-MODEL.md"), flat("README.md"), flat("docs/PHASE-GATES.md")
    sec = sm[sm.index("### The PowerShell tool"):sm.index("### Agents, commands")]
    assert "no PowerShell command runs before Phase 4 without a prompt" in sec
    assert re.search(r"except the canonical call of a confirmed `aid_session\.py` subcommand and "
                     r"the exact forms of the breather installer and `init-project\.sh`", sec)
    assert re.search(r"So does the exact form of the breather installer .{0,200}in every folder, "
                     r"phase and level, as from the Bash tool; other spellings of these two "
                     r"scripts are not asked", sec)
    assert "The same exact form is asked from the PowerShell tool" in sm
    assert "except the few that are asked" in rd
    for text in (sm, rd, pg):
        assert re.search(r"from the Bash (tool )?and (from )?the PowerShell tool", text)
    for cmd in ('node "<R>/integrations/breather/install.mjs"',
                'node "<R>/integrations/breather/install.mjs" --snooze=30',
                'bash "<R>/scripts/init-project.sh" demo --no-git'):
        assert set(gate.verdicts(cmd, "PowerShell").values()) == {"ASK"}, cmd
    for cmd in ('node <R>/integrations/breather/install.mjs; Get-Date',
                'bash "<R>/scripts/init-project.sh" demo > log.txt',
                'sh "<R>/scripts/init-project.sh"'):
        assert gate.verdicts(cmd, "PowerShell") == _row("ALLOW", "DENY", "ALLOW", "ALLOW"), cmd


# T15 A2: only the exact plugin-root form of the two scripts is asked.
def test_t15_6_docs_exact_form_only_for_breather_and_init_project(gate):
    for text in (flat("docs/SECURITY-MODEL.md"), flat("README.md")):
        assert re.search(r"(?i)exact form", text)
    assert "in that exact form only. Other spellings of these two scripts" in \
        flat("docs/SECURITY-MODEL.md")
    assert "only the exact form is asked; other spellings are not" in flat("README.md")
    for cmd in ('node "<R>/integrations/breather/install.mjs"', 'bash "<R>/scripts/init-project.sh"'):
        assert set(gate.verdicts(cmd).values()) == {"ASK"}, cmd
    # Not an unquoted path: _SCRIPT_CALL asks for a bare absolute path when the root has no
    # spaces, so that row would depend on where the repo is checked out (T15 review M1).
    for cmd in ('node "<R>/integrations/breather/install.mjs" > out.txt', 'sh "<R>/scripts/init-project.sh"',
                'bash "<R>/scripts/init-project.sh" && echo ok'):
        assert gate.verdicts(cmd) == _row("ALLOW", "DENY", "ALLOW", "ALLOW"), cmd


def test_t15_31_phase_gates_names_the_bash_gate_among_global_hooks():
    """R3-E4: PHASE-GATES counted two global hooks and left out the Bash gate."""
    text = flat("docs/PHASE-GATES.md")
    assert "but three of AID's hooks are not limited to them" in text
    assert "**The Bash gate (PreToolUse)** answers \"ask\" in every folder" in text


def test_t15_31_layer_a_names_the_mod_caveat():
    """R4-E3: a Claude Code mod can approve a call that the layer A rules would ask about."""
    assert re.search(r"a Claude Code mod that you install can approve a call", flat("docs/SECURITY-MODEL.md"))


@pytest.mark.parametrize("rel", ["commands/breather-stop.md", "commands/aid-reset.md"])
def test_t15_37_hook_ask_not_promised_in_bypass_mode(rel):
    """R3-E1/R3-E2 (R2-E3 carry-over): where the hook's ask is the only layer, the file must
    not promise a prompt under --dangerously-skip-permissions."""
    text = flat(rel)
    assert re.search(r"(?i)under `--dangerously-skip-permissions` Claude Code does not document "
                     r"that a hook's \"ask\" still prompts, so do not count on a prompt in that "
                     r"mode", text), rel
    if rel.endswith("aid-reset.md"):
        assert re.search(r"Outside AID projects, under `--dangerously-skip-permissions`", text)


def test_t15_31_denied_spellings_list_names_run_time_built():
    """R2-E2: SECURITY-MODEL lists run-time-built spellings among the denied forms."""
    text = flat("docs/SECURITY-MODEL.md")
    assert re.search(r"Any other spelling of a confirmed call \([^)]*built at run time\) is "
                     r"denied", text)


@pytest.mark.parametrize("rel", ["docs/SECURITY-MODEL.md", "README.md"])
def test_t15_31_non_live_root_ask_is_canonical_form_only(rel):
    """E-7: the non-live-root ask covers only the canonical single-command shape."""
    text = flat(rel)
    assert re.search(r"installed copy of the plugin that is not the live one.{0,140}canonical "
                     r"form.{0,4}one plain command, absolute script path", text), rel


@pytest.mark.parametrize("rel", ["docs/SECURITY-MODEL.md", "README.md", "commands/yolo.md"])
def test_t15_31_bypass_mode_hook_ask_not_promised(rel):
    """E-3: under bypassPermissions only ask RULES are documented to prompt."""
    text = flat(rel)
    assert "--dangerously-skip-permissions" in text, rel
    assert re.search(r"(?i)does not document whether a hook's \"ask\" does", text) or \
        re.search(r"(?i)but not whether a hook's \"ask\" does", text), rel
    assert re.search(r"(?i)do not count on a prompt in (that|this) mode", text), rel


# --- T15-32: real scope of the repo-wide hooks ---------------------------------

def test_t15_32_never_touched_claim_is_gone():
    files = tracked("README.md", "docs/*", "llm.txt", "llms.txt", "llms-full.txt", ".well-known/*")
    hits = [str(p.relative_to(REPO)) for p in files
            if "never touched" in p.read_text(encoding="utf-8", errors="replace").lower()]
    assert hits == [], hits


@pytest.mark.parametrize("rel", ["README.md", "docs/PHASE-GATES.md", "docs/SECURITY-MODEL.md"])
def test_t15_32_scope_is_stated(rel):
    text = flat(rel)
    assert re.search(r"dev-pipeline-gate \(Stop\)\*?\*? runs in every git repo", text), rel
    assert "node_modules/typescript/bin/tsc" in text, rel
    assert re.search(r"plan-execution-pipeline \(ExitPlanMode\)\*?\*? runs in every project", text), rel
    assert "~/.claude/.loop1-kickoff/<session_id>" in text, rel


def test_t15_32_readme_privacy_section_has_the_scope():
    text = read("README.md")
    sec = text[text.index("## Data handling and privacy"):text.index("## MCP Integrations")]
    assert "runs in every git repo" in " ".join(sec.split())


# --- T15-34: no plaintext token guidance ---------------------------------------

SECRET_KEY = re.compile(r"(TOKEN|API_KEY|SECRET|PASSWORD|_PAT)\s*=")


def test_t15_34_env_example_holds_no_secret_keys():
    text = read(".env.example")
    assert not SECRET_KEY.search(text), SECRET_KEY.findall(text)
    assert "NODE_ENV=" in text and "ATLASSIAN_SITE_URL=" in text     # non-secret settings kept
    assert "INSTALLATION.md" in text and "keystore" in text.lower()


@pytest.mark.parametrize("rel", ["README.md", "llms-full.txt"])
def test_t15_34_keystore_guidance_sso_first(rel):
    text = read(rel)
    for snippet in ("security add-generic-password", "find-generic-password", "cmdkey",
                    "Get-StoredCredential", "secret-tool"):
        assert snippet in text, (rel, snippet)
    i_sso, i_store, i_env = text.find("SSO"), text.find("security add-generic-password"), \
        text.lower().find("environment variable", text.find("security add-generic-password"))
    assert -1 < i_sso < i_store < i_env, (rel, i_sso, i_store, i_env)


@pytest.mark.parametrize("rel", ["README.md", "llms-full.txt", "skills/nano-banana-visual/SKILL.md",
                                 "skills/nano-banana-visual/SKILL.extended.md"])
def test_t15_34_no_env_token_block(rel):
    """A line that assigns a value to a token/key variable (outside a keystore load) is a
    plaintext-token instruction."""
    bad = [line for line in read(rel).splitlines()
           if re.match(r"^\s*(export\s+)?[A-Z_]*(TOKEN|API_KEY|SECRET|PASSWORD|_PAT)\s*=\s*\S", line)
           and "$(" not in line]
    assert bad == [], (rel, bad)


@pytest.mark.parametrize("rel", ["README.md", "llms-full.txt", "llm.txt", "INSTALLATION.md"])
def test_t15_34_no_add_your_tokens_phrase(rel):
    """E-2: no text tells the user to put tokens into a file."""
    assert "add your tokens" not in read(rel).lower(), rel


def test_t15_34_gitignore_comment_reworded():
    text = read(".gitignore")
    assert "contains YOUR tokens" not in text
    assert "keystore" in text


# --- T15-35 / T15-45: SECURITY.md -----------------------------------------------

def test_t15_35_security_md_channel():
    text = flat("SECURITY.md")
    low = text.lower()
    assert not re.search(r"(?i)\be-?mail\b", text), "SECURITY.md still tells reporters to e-mail"
    assert "security/advisories/new" in text and "private vulnerability advisory form" in low
    assert "owner is enabling" in low and "private vulnerability reporting" in low
    assert "minimal public issue" in low and "private contact channel" in low
    assert "do not include any details" in low


def test_t15_45_owner_actions_not_claimed_done():
    text = flat("SECURITY.md").lower()
    assert "pending with the owner" in text
    claims = re.compile(r"(?i)(dependabot (alerts|security updates) (are|is) (on|enabled)"
                        r"|token (was|has been|is) revoked|revoked the .{0,40}token)")
    hits = ["{}:{}".format(p.relative_to(REPO), n)
            for p in shipped_docs() + tracked(".github/*")
            for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1)
            if claims.search(line)]
    assert hits == [], hits


# --- T15-36: QA docs match D3 -----------------------------------------------------

QA_CALL = 'python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" qa-pass <TASK-ID> --note "<short summary>"'


def test_t15_36_readme_states_the_real_qa_guarantee():
    text = flat("README.md")
    assert "QA gate that blocks task completion until acceptance criteria pass" not in text
    assert ("keeps a task from ending until a QA pass is recorded with `aid_session.py qa-pass`, "
            "which the user confirms") in text
    assert "from Phase 4 project code can still write files" in text


def test_t15_36_development_skill_uses_qa_pass():
    text = read("skills/aid-development/SKILL.md")
    assert QA_CALL in text
    assert ".aid/qa/reports/" in text
    assert "-review-{N}.json" not in text


def test_t15_36_nothing_tells_the_agent_to_write_a_qa_marker():
    marker = re.compile(r"(?i)\.aid/qa/[^\s`\"')]*(\.qa-passed|-review[^\s`\"')]*\.json)")
    hits = ["{}:{}".format(p.relative_to(REPO), n)
            for p in shipped_docs()
            for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1)
            if marker.search(line)]
    assert hits == [], hits


def test_t15_36_example_task_and_gitignore():
    raw = read(".aid/qa/EXAMPLE-TASK.yaml")
    yaml.safe_load(raw)
    assert "-review-" not in raw and ".aid/qa/reports/EXAMPLE-TASK-report-1.json" in raw
    assert "qa-pass EXAMPLE-TASK" in raw
    gi = read(".gitignore")
    assert ".aid/qa/*-review-*.json" not in gi and ".aid/qa/reports/" in gi


# --- T15-37: commands call the new interfaces -------------------------------------

def test_t15_37_aid_reset_uses_the_reset_subcommand():
    text = read("commands/aid-reset.md")
    assert 'python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" reset' in text
    assert not re.search(r"\brm\s+-", text), "aid-reset still deletes by hand"
    assert "cd ~/.aid" not in text
    keep = text[text.index("## What it keeps"):text.index("## Flow")]
    assert "`memory/`" in keep and "--all" in keep and "`integrity/`" in keep and "`.aid/`" in keep


def test_t15_37_aid_reset_names_the_real_reset_entries():
    """The delete list is aid_session.RESET_ENTRIES (+ memory/ with --all), nothing more."""
    import ast
    src = read("hooks/aid_session.py")
    tree = ast.parse(src)
    entries = next(ast.literal_eval(n.value) for n in ast.walk(tree)
                   if isinstance(n, ast.Assign)
                   and any(getattr(t, "id", "") == "RESET_ENTRIES" for t in n.targets))
    text = read("commands/aid-reset.md")
    deletes = text[text.index("## What it deletes"):text.index("## What it keeps")]
    for name in entries:
        shown = name if "." in name else name + "/"
        assert "`{}`".format(shown) in deletes, name
    assert re.search(r"`memory/`.*only with `reset --all`", deletes)
    # reset keeps skills/ and config.yaml; the old "reset skills to defaults" line is gone.
    assert not re.search(r"(?i)reset\s+`?~/\.aid/skills/?`?\s+to defaults", text)
    keep = text[text.index("## What it keeps"):text.index("## Flow")]
    assert "kept" in keep


def test_t15_31_init_project_usage_is_valid_for_plugin_users():
    for rel in ("README.md", "llms-full.txt"):
        text = read(rel)
        assert "./scripts/init-project.sh my-app" not in text, rel
        flat_text = " ".join(text.split())
        assert "/start-project my-app" in flat_text, rel
        assert 'bash "${CLAUDE_PLUGIN_ROOT}/scripts/init-project.sh" my-app' in flat_text, rel
        assert "/aid-start" in flat_text, rel


def test_t15_37_context_update_shows_current_task_id():
    text = read("commands/context-update.md")
    blocks = re.findall(r"```json\n(.*?)```", text, re.S)
    assert blocks, "no JSON example"
    data = json.loads(blocks[0])
    assert isinstance(data["current_task"]["id"], str) and data["current_task"]["id"]


@pytest.mark.parametrize("rel", ["commands/breather-start.md", "commands/breather-stop.md"])
def test_t15_37_breather_commands_say_claude_code_asks(rel):
    text = flat(rel)
    assert "Claude Code asks the user before the installer runs" in text, rel
    assert 'node "${CLAUDE_PLUGIN_ROOT}/integrations/breather/install.mjs"' in text, rel


@pytest.mark.parametrize("rel", ["commands/breather-start.md", "commands/breather-stop.md"])
def test_t15_37_breather_commands_do_not_overstate_refusal(rel):
    """R2-E1: the gate asks only the exact form; other forms are not refused everywhere
    (outside AID projects and from Phase 4 on they run without a prompt)."""
    text = flat(rel)
    assert "any other form is refused" not in text.lower(), rel
    if rel.endswith("breather-start.md"):
        assert "only this exact form is asked" in text, rel
        assert re.search(r"Outside AID projects, and in an AID project from Phase 4 on, another "
                         r"form .{0,60}is not asked and may run without a prompt", text), rel


# --- T15-38: log/warn cost and SessionStart notice --------------------------------

@pytest.mark.parametrize("rel", ["docs/PHASE-GATES.md", "README.md", "docs/SECURITY-MODEL.md"])
def test_t15_38_log_warn_cost_documented(rel):
    text = flat(rel)
    assert "interpreter one-liners" in text, rel
    assert re.search(r"control files (stay|are) refused|control files stay refused", text), rel


def test_t15_38_phase_gates_level_table_carries_the_caveat():
    text = read("docs/PHASE-GATES.md")
    rows = [line for line in text.splitlines() if line.startswith("| `warn`") or line.startswith("| `log`")]
    assert len(rows) == 2 and all("interpreter one-liners" in r and "control files stay refused" in r
                                  for r in rows), rows


def test_t15_38_every_session_start_states_non_block_gates():
    for rel in ("docs/SECURITY-MODEL.md", "docs/PHASE-GATES.md"):
        text = flat(rel)
        assert re.search(r"Every (SessionStart|session start) in (a|such a) project", text), rel
        assert "whether or not it changed" in text, rel


# --- T15-39: the phase process is methodology -------------------------------------

def test_t15_39_phase_gates_reworded_as_guidance():
    text = flat("docs/PHASE-GATES.md")
    assert "No phase can be skipped" not in text
    assert "ALL of the following must be true" not in text
    assert "jump" in text and "confirm" in text
    assert "| Blocked |" not in read("docs/PHASE-GATES.md")
    assert "Jira work and deployment are not checked by any hook" in text


def test_t15_39_readme_phase_claim_is_methodology():
    """E-5: README matches PHASE-GATES.md: phases are the method, a confirmed jump skips."""
    text = flat("README.md")
    assert "No phase can be skipped" not in text
    assert "mandatory phases" not in text.lower()
    sec = text[text.index("## Phase Gate System"):][:600]
    assert "jump" in sec and "confirm" in sec and "before Phase 4" in sec, sec


def test_t15_39_llms_full_no_skipping_claim():
    """E-6: llms-full.txt no longer says 'no skipping'."""
    assert "(no skipping)" not in read("llms-full.txt")


def test_t15_39_gate_check_no_cannot_be_bypassed():
    text = read("commands/gate-check.md")
    assert "cannot be bypassed" not in text.lower()
    assert "Cannot Be Skipped" not in text


# --- T15-40: counts and badges ------------------------------------------------------

def _mcp_count():
    return len(json.loads(read(".mcp.json.example"))["mcpServers"])


def test_t15_40_badges_match_the_repo():
    text = read("README.md")
    skills = len([p for p in tracked("skills/*/SKILL.md") if len(p.relative_to(REPO).parts) == 3])
    m = re.search(r"badge/MCP-(\d+)", text)
    assert m and int(m.group(1)) == _mcp_count(), m and m.group(0)
    m = re.search(r"badge/Skills-(\d+)", text)
    assert m and int(m.group(1)) == skills, m and m.group(0)
    m = re.search(r"badge/Tests-([^)]*?)-[a-z]+\)", text)
    assert m and not re.search(r"\d", unquote(m.group(1))), m and m.group(0)


def test_t15_40_no_test_count_claims():
    hits = []
    for rel in ("README.md", "llm.txt", "llms.txt", "llms-full.txt", "CLAUDE.md"):
        for n, line in enumerate(read(rel).splitlines(), 1):
            if re.search(r"(?i)\b\d+ (pytest )?tests\b|\d+ of the \d+", line):
                hits.append("{}:{}".format(rel, n))
    assert hits == [], hits


def test_t15_40_commands_toc_and_rule_count():
    text = read("README.md")
    n_cmd = len(tracked("commands/*.md"))
    assert "Commands Reference ({} Commands)".format(n_cmd) in text
    n_rules = len(tracked("rules/*.md", "rules/**/*.md"))
    for rel in ("README.md", "llm.txt"):
        for m in re.finditer(r"(\d+) rule files", read(rel)):
            assert int(m.group(1)) == n_rules, (rel, m.group(0), n_rules)


def test_t15_40_llms_full_phase_count_is_six():
    """E-6: phases are numbered 0-5, so there are 6."""
    text = read("llms-full.txt")
    assert "- Phases: 6 (0-5)" in text
    assert not re.search(r"(?m)^- Phases: 5\s*$", text)


def test_t15_40_reviewer_count_is_seven():
    for rel in ("README.md", "llm.txt"):
        assert "8 reviewers" not in read(rel), rel
        assert "7 reviewers" in read(rel), rel


# --- T15-41: nano-banana ----------------------------------------------------------------

def test_t15_41_nano_banana_import_is_a_design_note():
    text = read("skills/nano-banana-visual/SKILL.extended.md")
    assert not re.search(r"^\s*import .*@/lib/nano-banana-pro", text, re.M)
    assert "Design note" in text
    assert ".env file" not in text and "keystore" in text


# --- T15-42: pre-commit downloads nothing unpinned --------------------------------------

def test_t15_42_precommit_npx_no_install():
    cfg = yaml.safe_load(read(".pre-commit-config.yaml"))
    entries = [h["entry"] for r in cfg["repos"] for h in r.get("hooks", []) if "entry" in h]
    npx = [e for e in entries if e.startswith("npx")]
    assert npx and all(e.startswith("npx --no-install ") for e in npx), npx
    assert any("eslint" in e for e in npx) and any("prettier" in e for e in npx)


# --- T15-43: cucumber profiles on a clean checkout -------------------------------------

def _cucumber_runnable():
    if not shutil.which("node") or not (REPO / "node_modules" / "@cucumber" / "cucumber").is_dir():
        return "@cucumber/cucumber is not installed"
    if not (REPO / "node_modules" / "ts-node").is_dir():
        return "ts-node is not installed"
    v = subprocess.run(["node", "-v"], capture_output=True, text=True).stdout.strip().lstrip("v")
    major, minor = (int(x) for x in v.split(".")[:2])
    if not ((major == 20 and minor >= 19) or (major == 22 and minor >= 12) or major >= 24):
        return "node {} is outside package.json engines".format(v)
    return None


def test_t15_43_steps_resolve_under_aid_health_root():
    steps = read("features/step-definitions/health-check.steps.ts")
    support = read("features/support/health-root.ts")
    assert "AID_HEALTH_ROOT" in support and "'skipped'" in support and "Before(" in support
    assert "healthRoot()" in steps and "process.cwd(), '.aid'" not in steps


@pytest.mark.skipif(_cucumber_runnable() is not None, reason=str(_cucumber_runnable()))
def test_t15_43_smoke_profile_passes_on_an_empty_root(tmp_path):
    env = dict(os.environ, AID_HEALTH_ROOT=str(tmp_path))
    npx = shutil.which("npx") or "npx"
    p = subprocess.run([npx, "--no-install", "cucumber-js", "--profile", "smoke"], cwd=str(REPO),
                       env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=180)
    out = p.stdout + p.stderr
    assert p.returncode == 0, out[-1500:]
    assert "failed" not in out.split("scenarios", 1)[-1][:60], out[-800:]
    assert "skipped" in out and "SKIPPED:" in out, out[-800:]


# --- T15-44: hygiene lows ------------------------------------------------------------------

def test_t15_44_gitleaksignore_is_lf_only():
    assert b"\r" not in (REPO / ".gitleaksignore").read_bytes()


def test_t15_44_yolo_description_and_ask_claim():
    text = read("commands/yolo.md")
    head = text.split("---", 2)[1]
    assert "skip confirmation prompts" not in head.lower()
    flat_text = " ".join(text.split())
    assert "in every folder" in flat_text and "second layer" in flat_text
    for sub in ("reset", "qa-pass", "memory-sync"):
        assert "`{}`".format(sub) in flat_text, sub


def test_t15_44_memory_system_skill_does_not_hand_edit_user_state():
    text = read("skills/memory-system/SKILL.md")
    assert not re.search(r"Update ~/\.aid/state\.json", text)
    assert text.count("aid_session.py start/end updates it") >= 2


def test_t15_44_no_memory_system_file_hand_edits_user_state():
    """E-4: SKILL.extended.md and every other memory-system skill file agree with SKILL.md."""
    hits = [str(p.relative_to(REPO)) for p in tracked("skills/memory-system/*",
                                                      "skills/memory-system/**")
            if p.suffix in (".md", ".txt", ".yaml", ".yml", ".json")
            and re.search(r"Update ~/\.aid/state\.json",
                          p.read_text(encoding="utf-8", errors="replace"))]
    assert hits == [], hits
    assert "aid_session.py start/end updates it" in read("skills/memory-system/SKILL.extended.md")
