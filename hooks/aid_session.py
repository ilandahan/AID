#!/usr/bin/env python3
"""
aid_session.py - one-shot session state writer for /aid-start and /aid-end.

WHY THIS EXISTS:
/aid-start used to have Claude Read every SKILL.md for the role+phase (up to 12
files, ~120KB) before it could write .aid/state.json, and /aid-end blocked on a
sub-agent review before saving anything. Users waited 5-10 minutes for a JSON
write. This script does the deterministic part (resolve terminology -> write
state / feedback) in one Bash call, so the command spends its tool calls on the
user, not on file plumbing.

CONNECTIONS:
- CALLED BY: commands/aid-start.md (Step 6-7), commands/aid-end.md (Step 7-8)
- READS:  references/role-phase-terminology.json (sibling of hooks/)
- WRITES: .aid/state.json (project-local), ~/.aid/feedback/pending/<ts>.json

Usage (T3: this script is the ONLY writer of .aid/state.json, a protected file):
  aid_session.py roles                  print the role menu
  aid_session.py phases <role>          print that role's phase menu
  aid_session.py init <role> <phase>    first state for a project that has none (any phase)
  aid_session.py init <role> <phase> --repair   rewrite a malformed state.json   [confirmed]
  aid_session.py start <role> <phase>   the current phase or an earlier one (no state = init)
  aid_session.py jump <role> <phase>    move FORWARD to a later phase              [confirmed]
      role:  pm | lead | developer | qa | data-scientist | other, or a menu number
      phase: 0-5;  start/jump/init also take [--role-desc TEXT] [--phase-desc TEXT]
  aid_session.py review <phase> PASS|PARTIAL|FAIL [--note TEXT]   record a phase review
  aid_session.py approve [--note TEXT]  human sign-off for the current phase       [confirmed]
  aid_session.py advance                approved phase -> next phase               [confirmed]
  aid_session.py end --rating N [--worked TEXT] [--improve TEXT]
      [--review passed|partial|failed|skipped] [--review-note TEXT]
  aid_session.py memory-preview [--days N]  what a memory sync would add, and the queue
  aid_session.py memory-feedback [--days N] the feedback, redacted, as JSON (input for the analysis agent)
  aid_session.py memory-sync [--days N]     write those entries to $AID_HOME/memory    [confirmed]
  aid_session.py memory-queue              queue the analysis agent's proposals from
                                            <project>/.aid/improve/proposals.json
  aid_session.py memory-apply <id>          append ONE queued proposal to its learnings file [confirmed]
  aid_session.py memory-reject <id>         drop a queued proposal
  aid_session.py reset [--all]              delete AID runtime data under $AID_HOME (RESET_ENTRIES;
                                            --all adds memory/; never integrity/)        [confirmed]
  aid_session.py qa-pass <task_id> [--note TEXT]   record a QA pass for .aid/qa/<task_id>.yaml
                                            (phase 4-5; read by the QA Stop gate)          [confirmed]
  aid_session.py status [--format text|json]  project, session, feedback, improvement stats,
                                            memory slots and queue length (read-only)
  aid_session.py checklist [--phase N] [--format text|json]  phase summary + approval checklist
                                            (read-only; approve prints the same block first)
  T16: init also creates .aid/context.json when absent (never overwrites it); memory-sync and
  memory-apply update $AID_HOME/metrics/improvement.json.
  T8: feedback text is redacted before it is written (memory_system/redact.py, best effort).
  [confirmed] = Claude Code asks the user first: SessionStart installs permission ask rules
  for exactly these calls (aid_guard.ASK_RULES), and the phase gate refuses any other
  spelling of them. Menus and numbering come from references/role-phase-terminology.json.
"""

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# Windows consoles default to cp1252, which cannot print the ✅ in the greeting.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
TERMS_FILE = HERE.parent / "references" / "role-phase-terminology.json"
STATE_FILE = Path.cwd() / ".aid" / "state.json"   # replaced in main() by project_state_file()


def project_state_file():
    """
    T3 A2 / INV-2: the SAME project root the phase gates use (aid_hooks.resolve_project_root),
    never the cwd on its own. A call from P/docs must write P/.aid/state.json; bootstrapping
    P/docs/.aid/state.json would create a nearer root the gates then trust (T3 review BLOCKER).
    With no AID root yet, a new project is created at $CLAUDE_PROJECT_DIR, else the cwd.
    """
    sys.path.insert(0, str(HERE))
    import aid_hooks                      # noqa: E402  (bundled beside this file)
    root = aid_hooks.resolve_project_root({})
    if not aid_hooks.is_aid_root(root):
        env_dir = os.environ.get("CLAUDE_PROJECT_DIR")
        root = Path(env_dir) if env_dir and os.path.isdir(env_dir) else Path.cwd()
    return Path(root) / ".aid" / "state.json"
MEMORY_PKG = HERE.parent / "memory-system"


def feedback_dir():
    """T8-3: $AID_HOME, else ~/.aid (the feedback dir used to ignore $AID_HOME)."""
    home = os.environ.get("AID_HOME")
    return (Path(home) if home else Path.home() / ".aid") / "feedback" / "pending"


def _memory_system():
    """The bundled memory_system package (memory-system/ beside hooks/)."""
    if str(MEMORY_PKG) not in sys.path:
        sys.path.insert(0, str(MEMORY_PKG))
    import memory_system                   # noqa: F401  (bundled with the plugin)
    from memory_system.feedback import collector
    # T8 review r1: the reader removes the names of THIS project (the gates' root), not
    # only of the cwd.
    collector.set_context(os.getcwd(), str(STATE_FILE.parent.parent))
    return memory_system


def redactor():
    """T8-1: redact() bound to this project's names, or None when the package is missing
    (the caller then stores no free text at all: fail closed)."""
    try:
        _memory_system()
        from memory_system.redact import context_names, redact
    except ImportError:
        return None
    names = context_names(os.getcwd(), str(STATE_FILE.parent.parent))
    return lambda text: redact(text, names) if text else text


def _clean(red, text):
    if not text:
        return text
    return red(text) if red else "[not stored: redaction unavailable]"

# Menu numbers are DERIVED from the terminology file, never hardcoded. The menus used to be
# hand-copied into commands/aid-start.md, and the copy drifted: data-scientist was a fully
# defined role with six phases and its own skills, yet no menu ever offered it, and slot 5
# showed "Other" instead. Deriving the numbering here keeps what is printed and what is
# parsed in step by construction, so a role added to the JSON appears in the menu.
ROLE_ALIASES = {
    "product-manager": "pm", "product_manager": "pm", "pm": "pm",
    "tech-lead": "lead", "techlead": "lead", "lead": "lead",
    "dev": "developer", "developer": "developer",
    "qa": "qa", "qa-engineer": "qa",
    "ds": "data-scientist", "data-scientist": "data-scientist",
    "other": "other",
}


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_json(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def save_json(path, data):
    """Atomic write (T3-2): a temp file renamed over the target, so a crash or a concurrent
    reader never sees half a state file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    # mkstemp: a fixed "state.json.tmp" name could be pre-created as a directory (mkdir is
    # allowed before Phase 4) and break every write (T3 review NIT).
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        os.replace(tmp, str(path))
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def ensure_context_file():
    """T16-16 (E2, G1-09; I-10): `init` also creates <root>/.aid/context.json, the file
    /context reads, when it is absent. Exclusive create: an existing context.json (the
    user's work notes) is never overwritten, also not by `init --repair`."""
    path = STATE_FILE.parent / "context.json"
    data = {"$schema": "aid-context-v1", "version": "1.0", "last_updated": now_iso(),
            "current_task": None, "current_step": None,
            "progress": {"steps_completed": [], "steps_pending": []},
            "session_notes": [], "blockers": []}
    try:
        fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        return
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=2) + "\n")


PHASE_NAMES = ["Discovery", "PRD", "Tech Spec", "Impl Plan", "Development", "QA & Ship"]

# T17-17 (G4-10, I-22): the ONE source of the phase-approval checklist items. Phases 1-5 are
# commands/phase-approve.md:94-118 at 11371b8, verbatim; phase 0 is new. /phase-approve runs
# `checklist` and reproduces its output instead of restating the items.
PHASE_CHECKLISTS = {
    0: ["Research folder `docs/research/YYYY-MM-DD-<project>/` exists",
        "`research-report.md` states the problem",
        "Stakeholders and success metrics identified",
        "Go / no-go decision recorded"],
    1: ["Requirements documented in `docs/prd/`",
        "User stories defined",
        "Acceptance criteria specified",
        "Scope agreed upon"],
    2: ["Technical specification in `docs/tech-spec/`",
        "Database schema designed",
        "API endpoints defined",
        "Architecture decisions documented"],
    3: ["Jira Epic created",
        "Stories broken down",
        "Tasks estimated",
        "Sprint planned"],
    4: ["All features implemented",
        "Tests passing",
        "Code reviewed",
        "Documentation updated"],
    5: ["QA testing complete",
        "No critical bugs",
        "Performance acceptable",
        "Ready for deployment"],
}
PHASE_FOLDERS = {0: "docs/research", 1: "docs/prd", 2: "docs/tech-spec", 3: "docs/implementation-plan"}


def read_state():
    """
    T3-2: (state_dict_or_None, problem_or_None). None/None = no state.json yet (a project
    that has not started). A file that exists but is not a JSON object with an integer
    current_phase 0-5 is malformed: every subcommand but `init --repair` refuses.
    """
    if not STATE_FILE.exists():
        return None, None
    try:
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return None, "cannot read {}: {}".format(STATE_FILE, e)
    if not isinstance(state, dict):
        return None, "{} is not a JSON object".format(STATE_FILE)
    phase = state.get("current_phase", state.get("phase"))
    if isinstance(phase, bool) or not isinstance(phase, int) or not 0 <= phase <= 5:
        return None, "{} has no valid current_phase (0-5): {!r}".format(STATE_FILE, phase)
    return state, None


def require_state():
    state, problem = read_state()
    if problem:
        sys.exit(problem + ". Run `init <role> <phase> --repair` (the user will be asked to confirm).")
    if state is None:
        sys.exit("no AID state yet: {} is missing (run /aid-start first)".format(STATE_FILE))
    return state


def phase_terms(role, phase):
    """T16-17 (G4-14): the terminology entry {name, description} for a role's phase.
    'other' and unknown roles use the developer terms, as the menus do. None when the
    terminology file cannot be read (the caller then keeps the generic PHASE_NAMES)."""
    phases = (load_json(TERMS_FILE) or {}).get("phases")
    if not isinstance(phases, dict):
        return None
    table = phases.get(role) if isinstance(phases.get(role), dict) else phases.get("developer")
    entry = table.get(str(phase)) if isinstance(table, dict) else None
    return entry if isinstance(entry, dict) else None


def set_phase(state, phase, role=None, role_display=None, phase_desc=None):
    """One place that moves the phase, so the flat keys, current_session and phase_name
    never disagree (A-18: readers used current_session, the writer only flat keys).
    T16-17 (G4-14): it also sets phase_display / phase_description for the new phase and
    status "active" (current_session.active is True), so advance never leaves the previous
    phase's label behind. A custom phase_desc applies only to the call that passes it."""
    state["current_phase"] = phase
    state["phase"] = phase
    state["phase_name"] = PHASE_NAMES[phase]
    terms = phase_terms(role or state.get("role"), phase)
    if terms:
        state["phase_display"] = terms.get("name") or PHASE_NAMES[phase]
        state["phase_description"] = phase_desc or terms.get("description", "")
    elif phase_desc:
        state["phase_description"] = phase_desc
    state["status"] = "active"
    session = state.get("current_session") if isinstance(state.get("current_session"), dict) else {}
    session.update({"active": True, "role": role or session.get("role") or state.get("role"),
                    "phase": phase, "started": session.get("started") or now_iso()})
    if role_display:
        session["role_display"] = role_display
    state["current_session"] = session


def load_terms():
    terms = load_json(TERMS_FILE)
    if not terms:
        sys.exit(f"cannot read {TERMS_FILE}")
    return terms


def role_order(terms):
    """Role ids in menu order. 'Other' is always the slot after the last real role."""
    return list(terms["roles"].keys())


def resolve_role(raw, terms):
    """Menu number or name -> role id. None if unrecognised."""
    raw = str(raw).strip().lower()
    order = role_order(terms)
    if raw.isdigit():
        n = int(raw)
        if 1 <= n <= len(order):
            return order[n - 1]
        return "other" if n == len(order) + 1 else None
    return ROLE_ALIASES.get(raw)


def cmd_roles(args):
    terms = load_terms()
    order = role_order(terms)
    print("What is your role today?\n")
    for i, rid in enumerate(order, 1):
        r = terms["roles"][rid]
        print(f"{i}. **{r['name']}**\n   {r['description']}\n")
    print(f"{len(order) + 1}. **Other** (describe your role)\n")
    print(f"Enter role number (1-{len(order) + 1}):")


def cmd_phases(args):
    terms = load_terms()
    role = resolve_role(args.role, terms)
    if not role:
        sys.exit(f"unknown role '{args.role}'")
    term_role = "developer" if role == "other" else role
    phases = terms["phases"][term_role]
    label = terms["roles"][term_role]["name"]
    if role == "other":
        label += " terminology"
    print(f"What phase are you working on? ({label})\n")
    for key in sorted(phases, key=int):
        p = phases[key]
        print(f"{key}. **{p['name']}**\n   {p['description']}\n")
    other = len(phases)
    print(f"{other}. **Other** (describe your work)\n")
    print(f"Enter phase number (0-{other}):")


def cmd_start(args):
    """start: the current phase or an earlier one. Never creates the state (T3 A2: the
    first state is `init`, which the user confirms)."""
    state, problem = read_state()
    if problem:
        sys.exit(problem + ". Run `init <role> <phase> --repair` (the user will be asked to confirm).")
    if state is None:
        sys.exit("no AID state yet ({} is missing): this project starts with `init <role> "
                 "<phase>`, which the user confirms.".format(STATE_FILE))
    if True:
        want = str(args.phase).strip()
        if want.isdigit() and int(want) > state["current_phase"]:
            sys.exit("phase {} is ahead of the project's current phase {}. Moving forward needs "
                     "the user's confirmation: run `jump {} {}` instead, or finish this phase and "
                     "use /phase-approve and /phase-advance.".format(
                         want, state["current_phase"], args.role, want))
    _begin(args, state)


def cmd_init(args):
    """init: only for a project with no state yet; --repair rewrites a malformed one
    (human-confirmed through the ask rules)."""
    state, problem = read_state()
    if args.repair:
        if not problem:
            sys.exit("--repair is only for a malformed {}; it reads fine.".format(STATE_FILE))
        _begin(args, None)
        return
    if problem or state is not None:
        sys.exit("{} already exists; use start (or jump to move forward).".format(STATE_FILE))
    _begin(args, None)


def cmd_jump(args):
    """jump: move FORWARD (human-confirmed through the ask rules, T3-4)."""
    state = require_state()
    want = str(args.phase).strip()
    if not (want.isdigit() and int(want) > state["current_phase"]):
        sys.exit("jump only moves forward (current phase {}); use start for this phase or an "
                 "earlier one.".format(state["current_phase"]))
    _begin(args, state)


def cmd_review(args):
    """review: record a phase review (advisory; G2: the one key both writer and reader use)."""
    state = require_state()
    # Same vocabulary as `end --review` (passed/partial/failed), so the one key has one format.
    entry = {"status": {"PASS": "passed", "PARTIAL": "partial", "FAIL": "failed"}[args.status],
             "timestamp": now_iso()}
    if args.note:
        entry["note"] = _clean(redactor(), args.note)     # T15-12 (R-09): redacted like feedback
    state.setdefault("subagent_review", {})["phase_{}".format(args.phase)] = entry
    save_json(STATE_FILE, state)
    print("Review recorded: phase {} {}".format(args.phase, args.status))


def collect_checklist(state, phase):
    """T17-17 (I-22): the phase summary and checklist, read-only. Phase folders list their files;
    phases 4-5 list the .aid/qa/*.yaml task ids with their QA pass state."""
    root = STATE_FILE.parent.parent
    current = state["current_phase"]
    if phase in PHASE_FOLDERS:
        folder = root / PHASE_FOLDERS[phase]
        docs = sorted(p.relative_to(root).as_posix() for p in folder.rglob("*") if p.is_file()) \
            if folder.is_dir() else []
    else:
        passed = state.get("qa_passed") if isinstance(state.get("qa_passed"), dict) else {}
        qa = STATE_FILE.parent / "qa"
        docs = ["{} (qa_passed: {})".format(p.stem, "yes" if p.stem in passed else "no")
                for p in sorted(qa.glob("*.yaml"))] if qa.is_dir() else []
    return {"phase": phase,
            "summary": {"phase": phase, "phase_name": PHASE_NAMES[phase],
                        "role": state.get("role_display") or state.get("role") or "-",
                        "approved": phase == current and state.get("phase_approved") is True,
                        "feedback": phase == current and state.get("feedback_provided") is True,
                        "documents": docs},
            "checklist": list(PHASE_CHECKLISTS[phase])}


def checklist_text(data):
    s = data["summary"]
    n = data["phase"]
    yn = lambda b: "yes" if b else "no"           # noqa: E731
    lines = ["## Phase {} Summary".format(n),
             "Phase: {} ({}) | Role: {} | Approved: {} | Feedback: {}".format(
                 n, s["phase_name"], s["role"], yn(s["approved"]), yn(s["feedback"])),
             "Documents: {}".format(", ".join(s["documents"]) or "none found"),
             "## Phase {} Checklist".format(n)]
    lines += ["- [ ] " + item for item in data["checklist"]]
    return "\n".join(lines)


def cmd_checklist(args):
    """checklist: read-only (not confirmed, not in I-1). Writes nothing."""
    sys.dont_write_bytecode = True
    state, problem = read_state()
    if problem:
        print(problem)
        sys.exit(1)
    if state is None:
        print("AID is not initialized here (run /aid-init)")
        sys.exit(1)
    phase = state["current_phase"] if args.phase is None else args.phase
    data = collect_checklist(state, phase)
    if args.format == "json":
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(checklist_text(data))


def cmd_approve(args):
    """approve: the human sign-off for the current phase (human-confirmed, T3-4)."""
    state = require_state()
    # T17-17 (I-22): the same Summary + Checklist block, before anything is written, so a
    # human `!` run always shows what is being signed off.
    print(checklist_text(collect_checklist(state, state["current_phase"])) + "\n")
    state["phase_approved"] = True
    state["feedback_provided"] = True
    state["phase_approved_at"] = now_iso()
    red = redactor()
    if args.note:
        state["phase_approval_note"] = _clean(red, args.note)   # T15-12 (R-09)
    save_json(STATE_FILE, state)
    # T8 D5: the /phase-approve rating reaches the learning loop as a REDACTED pending entry.
    m = re.search(r"\brating\s*([1-5])\b", args.note or "", re.I)
    ts = now_iso()
    save_json(feedback_dir() / ("approve-" + ts.replace(":", "-") + ".json"), {
        "source": "phase-approve", "timestamp": ts, "role": _clean(red, state.get("role")),
        "phase": state.get("current_phase"), "phase_display": _clean(red, state.get("phase_display")),
        "rating": int(m.group(1)) if m else None, "note": _clean(red, args.note or "")})
    print("✅ Phase {} ({}) approved.".format(state["current_phase"], PHASE_NAMES[state["current_phase"]]))


def cmd_advance(args):
    """advance: approved phase -> next phase, approval reset (human-confirmed, T3-4)."""
    state = require_state()
    phase = state["current_phase"]
    if state.get("phase_approved") is not True:
        sys.exit("phase {} ({}) is not approved yet: run /phase-approve first.".format(
            phase, PHASE_NAMES[phase]))
    if phase >= 5:
        sys.exit("phase 5 (QA & Ship) is the last phase.")
    set_phase(state, phase + 1)
    state["phase_approved"] = False
    state["feedback_provided"] = False
    state.pop("phase_approved_at", None)
    state.pop("phase_approval_note", None)
    save_json(STATE_FILE, state)
    print("✅ Advanced to phase {} ({}).".format(phase + 1, PHASE_NAMES[phase + 1]))


def _begin(args, state):
    terms = load_terms()

    role = resolve_role(args.role, terms)
    if not role:
        names = "|".join(role_order(terms))
        sys.exit(f"unknown role '{args.role}' (use {names}|other, or a menu number)")
    term_role = "developer" if role == "other" else role

    phase_key = str(args.phase).strip()
    if phase_key not in terms["phases"][term_role]:
        valid = ", ".join(sorted(terms["phases"][term_role], key=int))
        sys.exit(f"unknown phase '{args.phase}' (use {valid})")
    phase = terms["phases"][term_role][phase_key]

    role_info = terms["roles"][term_role]
    skills = [terms["roleSkillMapping"][term_role]] + list(phase.get("skills", []))
    for s in terms.get("commonSkills", []):
        if s not in skills:
            skills.append(s)

    state = dict(state or {})
    new_phase = int(phase_key)
    if state.get("current_phase") != new_phase:
        # An approval belongs to the phase it was given in; carrying it to another phase
        # would let /phase-advance skip that phase's sign-off.
        state["phase_approved"] = False
        state["feedback_provided"] = False
        state.pop("phase_approved_at", None)
        state.pop("phase_approval_note", None)
    state.update({
        "role": role,
        "role_display": args.role_desc or role_info["name"],
        "phase_display": phase["name"],
        "phase_description": args.phase_desc or phase["description"],
        "session_start": now_iso(),
        "status": "active",
        "skills_loaded": skills,
    })
    state["current_session"] = {}            # a new session, not a continuation
    set_phase(state, new_phase, role=role, role_display=state["role_display"],
              phase_desc=args.phase_desc)
    save_json(STATE_FILE, state)
    if args.fn is cmd_init:
        ensure_context_file()

    print("✅ Session started\n")
    print(f"Role:  {state['role_display']}")
    print(f"Phase: {phase_key}. {phase['name']}")
    print(f"       {state['phase_description']}\n")
    print("Skills loaded:")
    for s in skills:
        print(f"  • {s}")
    print("\nReady to work! Use /aid-end when finishing this session.")


def cmd_end(args):
    state = require_state()

    start = state.get("session_start")
    duration = None
    if start:
        try:
            t0 = datetime.fromisoformat(start.replace("Z", "+00:00"))
            duration = int((datetime.now(timezone.utc) - t0).total_seconds() // 60)
        except ValueError:
            pass

    ts = now_iso()
    red = redactor()                       # T8-1: redact BEFORE anything is written
    review = {"status": args.review, "timestamp": ts}
    if args.review_note:
        review["note"] = _clean(red, args.review_note)

    feedback = {
        "timestamp": ts,
        "role": _clean(red, state.get("role")),
        "phase": state.get("current_phase", state.get("phase")),
        "phase_display": _clean(red, state.get("phase_display")),
        "rating": args.rating,
        "worked_well": _clean(red, args.worked or ""),
        "to_improve": _clean(red, args.improve or ""),
        "duration_minutes": duration,
        "subagent_review": review,
    }
    fb_path = feedback_dir() / (ts.replace(":", "-") + ".json")
    save_json(fb_path, feedback)

    phase_n = state.get("current_phase", state.get("phase"))
    state.setdefault("subagent_review", {})[f"phase_{phase_n}"] = review
    state["status"] = "ended"
    state["session_end"] = ts
    if isinstance(state.get("current_session"), dict):
        state["current_session"]["active"] = False
    save_json(STATE_FILE, state)

    print("✅ Session ended\n")
    print(f"Role:  {state.get('role_display')}   Phase: {phase_n}. {state.get('phase_display')}")
    if duration is not None:
        print(f"Duration: {duration} min")
    print(f"Rating: {args.rating}/5")
    print(f"Sub-agent review: {args.review}")
    # T17-15: "redacted" only when the saved text is redact(text); without the redactor the
    # free text was not stored at all.
    if red:
        print(f"Feedback saved (redacted): {fb_path}")
    else:
        print(f"Feedback saved without free text (redaction unavailable): {fb_path}")


# ---------------------------------------------------------------------------
# T8 (amendment A1): the ONE entry point for writes to AID's learning memory. memory-sync
# and memory-apply are confirmed by the user (aid_guard.ASK_RULES); the memory_system CLI
# itself only previews.
# ---------------------------------------------------------------------------

def _queue_lines(queue):
    if not queue:
        return ["Proposal queue: empty"]
    lines = ["Proposal queue ({}):".format(len(queue))]
    for r in queue:
        lines.append("  {}  [{}] -> {}".format(str(r.get("id", ""))[:16], r.get("priority", "?"),
                                              r.get("target_file") or "(no learnings file; cannot be applied)"))
        lines.append("      {}".format(str(r.get("proposed_change", ""))[:300]))
    return lines


def cmd_memory_preview(args):
    _memory_system()
    from memory_system.subagent import LearningSubAgent, print_sync_result
    from memory_system.recommendations.generator import load_recommendation_queue
    print("Memory sync preview (nothing is written):")
    print_sync_result(LearningSubAgent(days=args.days).sync_to_memory(days=args.days, approve=False))
    print("\n".join([""] + _queue_lines(load_recommendation_queue())))


def cmd_memory_feedback(args):
    """T8: the analysis agent's input. Redacted entries from the one reader, so the agent
    never needs to open raw pending files (old ones may predate redaction)."""
    _memory_system()
    from datetime import timedelta
    from memory_system.feedback.collector import load_feedback_by_date_range
    end = datetime.now()
    entries = load_feedback_by_date_range((end - timedelta(days=args.days)).strftime("%Y-%m-%d"),
                                          end.strftime("%Y-%m-%d"))
    print(json.dumps(entries, indent=2, ensure_ascii=False))


def _improvement_file():
    return _aid_home() / "metrics" / "improvement.json"


def read_improvement():
    """I-11: the improvement-run statistics, with defaults for a missing or malformed file."""
    stats = {"last_improvement_run": None, "runs": 0, "feedback_processed": 0, "skills_updated": 0}
    data = load_json(_improvement_file())
    if isinstance(data, dict):
        for k in ("runs", "feedback_processed", "skills_updated"):
            v = data.get(k)
            if isinstance(v, int) and not isinstance(v, bool) and v >= 0:
                stats[k] = v
        if isinstance(data.get("last_improvement_run"), str):
            stats["last_improvement_run"] = data["last_improvement_run"]
    return stats


def record_improvement(run=False, processed=0, skills=0):
    """T16-18 (g8-improve-stat; I-11): written only by an approved memory-sync (run=True)
    and a successful memory-apply (skills=1). Previews, rejects and refusals write nothing."""
    stats = read_improvement()
    if run:
        stats["last_improvement_run"] = now_iso()
        stats["runs"] += 1
        stats["feedback_processed"] += processed
    stats["skills_updated"] += skills
    save_json(_improvement_file(), stats)


def cmd_memory_sync(args):
    _memory_system()
    from memory_system.subagent import LearningSubAgent, print_sync_result
    result = LearningSubAgent(days=args.days).sync_to_memory(days=args.days, approve=True)
    print_sync_result(result)
    if isinstance(result, dict) and not result.get("dry_run"):
        processed = result.get("processed", [])        # I-11: WS-D fills it; may be absent
        record_improvement(run=True, processed=len(processed) if isinstance(processed, list) else 0)


def cmd_memory_queue(args):
    _memory_system()
    from memory_system.recommendations.generator import queue_proposals
    # T8 review r1: the file is found from the PROJECT root, not passed: the phase gate
    # accepts no path argument before Phase 4, and a relative path would follow the cwd.
    path = STATE_FILE.parent / "improve" / "proposals.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        sys.exit("memory-queue: cannot read {}: {}".format(path, e))
    result = queue_proposals(data)
    print("Queued {} proposal(s): {}".format(len(result["queued"]), ", ".join(result["queued"]) or "-"))
    # T15-17 (L3-4e, I-8): two skip reasons. `skipped_empty` comes from memory_system; an
    # older memory_system put allowed-but-empty targets in skipped_targets, so those are
    # moved here by the same target check rather than being called "not allowed".
    from memory_system.recommendations.generator import resolve_target
    empty = [str(t) for t in result.get("skipped_empty", [])]
    skipped = []
    for t in result.get("skipped_targets", []):
        if t not in ("None", "") and resolve_target(t) is not None:
            if t not in empty:
                empty.append(t)
        else:
            skipped.append(t)
    named = [t for t in skipped if t not in ("None", "")]
    unnamed = len(skipped) - len(named)
    if named:
        print("Not queued, target is not an allowed learnings file: " + ", ".join(named))
    if empty:
        print("Not queued, empty content: " + ", ".join(empty))
    if unnamed:
        print("Not queued: {} proposal(s) with no target file (memory candidates come from "
              "memory-preview / memory-sync instead)".format(unnamed))


def cmd_memory_apply(args):
    _memory_system()
    from memory_system.recommendations.generator import apply_recommendation
    result = apply_recommendation(args.id)
    if not result["ok"]:
        sys.exit("memory-apply refused: " + result["reason"])
    record_improvement(skills=1)
    print("✅ Applied {} to {}".format(result["id"], result["target"]))


def cmd_memory_reject(args):
    _memory_system()
    from memory_system.recommendations.generator import reject_recommendation
    if not reject_recommendation(args.id):
        sys.exit("memory-reject: no single queued proposal has id {!r}".format(args.id))
    print("Rejected {}".format(args.id))


# ---------------------------------------------------------------------------
# T15 (D2, D3; I-2): reset and qa-pass. Both are confirmed by the user (aid_guard.ASK_RULES).
# ---------------------------------------------------------------------------

# Every runtime path AID code writes under $AID_HOME: state.json (user-level session),
# agent_state.json (memory_system subagent), feedback/ (aid_session end/approve,
# collector), recommendations/ (queue, applied, rejected), metrics/ (trends), reports/
# (dashboard). memory/ only with --all. integrity/ (layer B baseline) is never deleted:
# deleting it would weaken enforcement. Anything else is kept and printed as "kept".
RESET_ENTRIES = ("state.json", "agent_state.json", "feedback", "recommendations", "metrics", "reports")
RESET_ALL_ENTRIES = RESET_ENTRIES + ("memory",)
RESET_NEVER = ("integrity",)


def _aid_home():
    home = os.environ.get("AID_HOME")
    return Path(home) if home else Path.home() / ".aid"


def _norm(p):
    return os.path.normcase(os.path.realpath(str(p)))


def _is_link_or_junction(p):
    """A symlink or a Windows junction/reparse point: unlinked, never followed."""
    if os.path.islink(p):
        return True
    try:
        attrs = getattr(os.lstat(p), "st_file_attributes", 0)
    except OSError:
        return False
    return bool(attrs & 0x400)              # FILE_ATTRIBUTE_REPARSE_POINT


def _reset_refusal(home):
    """Why $AID_HOME must not be reset, or None. Refused when it resolves to (or contains)
    a user home, a filesystem/drive root, the current project root or the cwd."""
    target = _norm(home)
    if os.path.dirname(target) == target:
        return "it is a filesystem root"
    sys.path.insert(0, str(HERE))
    import aid_hooks                      # noqa: E402  (bundled beside this file)
    guarded = [("a user home folder", h) for h in (str(Path.home()), os.path.expanduser("~"),
                                                    aid_hooks._account_home()) if h]
    guarded += [("the current project root", aid_hooks.resolve_project_root({})),
                ("the current folder", os.getcwd())]
    for label, other in guarded:
        o = _norm(other)
        if o == target or o.startswith(target.rstrip(os.sep) + os.sep):
            return "it is (or contains) {}".format(label)
    # R1-C3 (I-2: reset never touches a project .aid/): refuse an AID_HOME at or under an
    # AID project root, e.g. <P>/.aid. A project root is any ancestor (or the folder itself)
    # whose .aid/ holds an AID marker; a user home is not one (its .aid/ IS the default
    # AID_HOME). aid_hooks.is_aid_root cannot be used: it excludes the AID_HOME .aid/.
    homes = {_norm(h) for _l, h in guarded[:3]}
    t = Path(target)
    for d in [t] + list(t.parents):
        if _norm(d) in homes:
            continue
        aid = d / ".aid"
        if (aid / "state.json").is_file() or (aid / "hooks" / "config.json").is_file():
            return "is inside the AID project {}".format(d)
    return None


def _remove(p):
    if _is_link_or_junction(p):
        try:
            os.unlink(p)
        except (IsADirectoryError, PermissionError, OSError):
            os.rmdir(p)                     # a Windows directory symlink or junction
    elif p.is_dir():
        import shutil
        shutil.rmtree(p)
    else:
        p.unlink()


def cmd_reset(args):
    home = _aid_home()
    problem = _reset_refusal(home)
    if problem:
        sys.exit("reset refused: AID_HOME {} {}; nothing was deleted.".format(home, problem))
    if not home.exists():
        print("Nothing to reset: {} does not exist.".format(home))
        return
    if not home.is_dir() or _is_link_or_junction(home):
        sys.exit("reset refused: AID_HOME {} is not a plain folder; nothing was deleted.".format(home))
    remove = RESET_ALL_ENTRIES if args.all else RESET_ENTRIES
    removed, failed = [], []
    for name in remove:
        p = home / name
        if not (p.exists() or os.path.lexists(p)):
            continue
        try:
            _remove(p)
            removed.append(name)
            print("Removed {}".format(p))
        except OSError as e:
            failed.append(name)
            print("Could not remove {}: {}".format(p, e))
    for entry in sorted(os.listdir(home)):
        if entry not in removed:
            print("kept {}".format(home / entry))
    print("Reset done ({} removed). Project .aid/ folders were not touched.".format(len(removed)))
    if failed:
        sys.exit(1)


TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def valid_task_id(task_id):
    return isinstance(task_id, str) and bool(TASK_ID_RE.match(task_id)) and ".." not in task_id


def cmd_qa_pass(args):
    """qa-pass: the human-confirmed QA verdict the QA Stop gate reads (D3, R-07)."""
    import hashlib
    if not valid_task_id(args.task_id):
        sys.exit("qa-pass: invalid task id {!r} (letters, digits, . _ -; max 64; no ..)".format(args.task_id))
    state = require_state()
    if state["current_phase"] not in (4, 5):
        sys.exit("qa-pass: the project is at phase {}; QA passes are recorded in phase 4 or 5."
                 .format(state["current_phase"]))
    criteria = STATE_FILE.parent / "qa" / (args.task_id + ".yaml")
    if not criteria.is_file():
        sys.exit("qa-pass: no QA criteria file {}".format(criteria))
    digest = hashlib.sha256(criteria.read_bytes()).hexdigest()
    passed = state.get("qa_passed") if isinstance(state.get("qa_passed"), dict) else {}
    passed[args.task_id] = {"at": now_iso(), "criteria_sha256": digest,
                            "note": _clean(redactor(), args.note or "") or ""}
    state["qa_passed"] = passed
    save_json(STATE_FILE, state)
    print("✅ QA pass recorded for {} (criteria sha256 {}).".format(args.task_id, digest[:12]))


# ---------------------------------------------------------------------------
# T16-19 (g8-aid-status; I-10): status, the read-only data source for /aid-status.
# Not a confirmed subcommand (not in I-1): it writes nothing.
# ---------------------------------------------------------------------------

def _feedback_counts():
    base = _aid_home() / "feedback"
    pending = sorted((base / "pending").glob("*.json")) if (base / "pending").is_dir() else []
    processed = list((base / "processed").glob("*.json")) if (base / "processed").is_dir() else []
    stamps = [d.get("timestamp") for d in (load_json(p) for p in pending)
              if isinstance(d, dict) and isinstance(d.get("timestamp"), str)]
    return {"pending": len(pending), "processed": len(processed),
            "newest_pending": max(stamps) if stamps else None}


def _memory_and_queue():
    """Memory slots used/total and the recommendation queue length, from memory-system.
    None for each when the package cannot be imported. Reading creates nothing."""
    try:
        _memory_system()
        from memory_system.analysis.memory_sync import MemorySlotManager
        from memory_system.recommendations.generator import load_recommendation_queue
    except ImportError:
        return None, None
    usage = MemorySlotManager().get_slot_usage()
    memory = {"used": sum(u["used"] for u in usage.values()),
              "total": sum(u["max"] for u in usage.values())}
    return memory, {"queued": len(load_recommendation_queue())}


def collect_status():
    sys.path.insert(0, str(HERE))
    import aid_hooks                      # noqa: E402  (bundled beside this file)
    root = STATE_FILE.parent.parent
    project = session = None
    if aid_hooks.is_aid_root(root):
        state, problem = read_state()
        project = {"root": str(root), "initialized": state is not None,
                   "phase": state["current_phase"] if state else None,
                   "phase_name": PHASE_NAMES[state["current_phase"]] if state else None}
        if problem:
            project["problem"] = problem
        if state:
            cs = state.get("current_session") if isinstance(state.get("current_session"), dict) else {}
            session = {"role": state.get("role"), "role_display": state.get("role_display"),
                       "phase_display": state.get("phase_display"),
                       "started": cs.get("started") or state.get("session_start"),
                       "active": cs.get("active") is True, "status": state.get("status")}
    memory, recs = _memory_and_queue()
    return {"project": project, "session": session, "feedback": _feedback_counts(),
            "improvement": read_improvement(), "memory": memory, "recommendations": recs}


def cmd_status(args):
    sys.dont_write_bytecode = True           # "writes nothing" includes __pycache__
    st = collect_status()
    if args.format == "json":
        print(json.dumps(st, indent=2, ensure_ascii=False))
        return
    p, s, fb, imp, mem, rec = (st[k] for k in ("project", "session", "feedback", "improvement",
                                               "memory", "recommendations"))
    if p is None:
        print("Project: not an AID project (not initialized)")
    elif not p["initialized"]:
        print("Project: {} (not initialized{})".format(p["root"], ": " + p["problem"] if p.get("problem") else ""))
    else:
        print("Project: {}  Phase: {}. {}".format(p["root"], p["phase"], p["phase_name"]))
    if s:
        print("Session: role {}  phase {}  started {}  {}".format(
            s["role_display"] or s["role"], s["phase_display"], s["started"],
            "active" if s["active"] else "not active"))
    print("Feedback: {} pending, {} processed (newest pending: {})".format(
        fb["pending"], fb["processed"], fb["newest_pending"] or "-"))
    print("Improvement: last run {}  runs {}  feedback processed {}  skills updated {}".format(
        imp["last_improvement_run"] or "never", imp["runs"], imp["feedback_processed"],
        imp["skills_updated"]))
    print("Memory: {}".format("{}/{} slots used".format(mem["used"], mem["total"]) if mem
                              else "unavailable (memory-system not found)"))
    print("Recommendations queued: {}".format(rec["queued"] if rec else "unavailable"))


def main():
    global STATE_FILE
    # T3 A2: no abbreviations (`--rep` must not act as --repair past the ask rules).
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
                                allow_abbrev=False)
    sub = p.add_subparsers(dest="cmd", required=True)
    _add = sub.add_parser
    sub.add_parser = lambda *a, **k: _add(*a, allow_abbrev=False, **k)

    r = sub.add_parser("roles", help="print the role menu (from the terminology file)")
    r.set_defaults(fn=cmd_roles)

    ph = sub.add_parser("phases", help="print the phase menu for a role")
    ph.add_argument("role")
    ph.set_defaults(fn=cmd_phases)

    for name, fn in (("start", cmd_start), ("jump", cmd_jump), ("init", cmd_init)):
        s = sub.add_parser(name)
        s.add_argument("role")
        s.add_argument("phase")
        s.add_argument("--role-desc", default=None, help="custom description when role is 'other'")
        s.add_argument("--phase-desc", default=None, help="custom description when phase is 'other'")
        if name == "init":
            s.add_argument("--repair", action="store_true",
                           help="rewrite a malformed state.json (the user is asked to confirm)")
        s.set_defaults(fn=fn, repair=False) if name != "init" else s.set_defaults(fn=fn)

    rv = sub.add_parser("review", help="record a phase review result")
    rv.add_argument("phase", type=int, choices=range(0, 6))
    rv.add_argument("status", type=str.upper, choices=["PASS", "PARTIAL", "FAIL"])
    rv.add_argument("--note", default=None)
    rv.set_defaults(fn=cmd_review)

    ap = sub.add_parser("approve", help="human sign-off for the current phase")
    ap.add_argument("--note", default=None)
    ap.set_defaults(fn=cmd_approve)

    ad = sub.add_parser("advance", help="move an approved phase to the next one")
    ad.set_defaults(fn=cmd_advance)

    e = sub.add_parser("end")
    e.add_argument("--rating", type=int, required=True, choices=range(1, 6))
    e.add_argument("--worked", default=None)
    e.add_argument("--improve", default=None)
    e.add_argument("--review", default="skipped", choices=["passed", "partial", "failed", "skipped"])
    e.add_argument("--review-note", default=None)
    e.set_defaults(fn=cmd_end)

    def days(value):
        d = int(value)
        if not 1 <= d <= 3650:
            raise argparse.ArgumentTypeError("--days must be 1-3650")
        return d

    for name, fn in (("memory-preview", cmd_memory_preview), ("memory-sync", cmd_memory_sync),
                     ("memory-feedback", cmd_memory_feedback)):
        m = sub.add_parser(name)
        m.add_argument("--days", type=days, default=30)
        m.set_defaults(fn=fn)
    mq = sub.add_parser("memory-queue")
    mq.set_defaults(fn=cmd_memory_queue)
    for name, fn in (("memory-apply", cmd_memory_apply), ("memory-reject", cmd_memory_reject)):
        m = sub.add_parser(name)
        m.add_argument("id")
        m.set_defaults(fn=fn)

    rs = sub.add_parser("reset", help="delete AID runtime data under $AID_HOME (keeps memory/ and integrity/)")
    rs.add_argument("--all", action="store_true", help="also delete memory/ (integrity/ is always kept)")
    rs.set_defaults(fn=cmd_reset)

    qp = sub.add_parser("qa-pass", help="record a QA pass for .aid/qa/<task_id>.yaml (phase 4-5)")
    qp.add_argument("task_id")
    qp.add_argument("--note", default=None)
    qp.set_defaults(fn=cmd_qa_pass)

    st = sub.add_parser("status", help="print project, session, feedback, improvement, memory "
                                       "and queue status (read-only)")
    st.add_argument("--format", choices=["text", "json"], default="text")
    st.set_defaults(fn=cmd_status)

    cl = sub.add_parser("checklist", help="print the phase summary and approval checklist (read-only)")
    cl.add_argument("--phase", type=int, choices=range(0, 6), default=None)
    cl.add_argument("--format", choices=["text", "json"], default="text")
    cl.set_defaults(fn=cmd_checklist)

    args = p.parse_args()
    STATE_FILE = project_state_file()
    args.fn(args)


if __name__ == "__main__":
    main()
