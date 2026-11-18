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
  [confirmed] = Claude Code asks the user first: SessionStart installs permission ask rules
  for exactly these calls (aid_guard.ASK_RULES), and the phase gate refuses any other
  spelling of them. Menus and numbering come from references/role-phase-terminology.json.
"""

import argparse
import json
import os
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
FEEDBACK_DIR = Path.home() / ".aid" / "feedback" / "pending"

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


PHASE_NAMES = ["Discovery", "PRD", "Tech Spec", "Impl Plan", "Development", "QA & Ship"]


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


def set_phase(state, phase, role=None, role_display=None):
    """One place that moves the phase, so the flat keys, current_session and phase_name
    never disagree (A-18: readers used current_session, the writer only flat keys)."""
    state["current_phase"] = phase
    state["phase"] = phase
    state["phase_name"] = PHASE_NAMES[phase]
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
        entry["note"] = args.note
    state.setdefault("subagent_review", {})["phase_{}".format(args.phase)] = entry
    save_json(STATE_FILE, state)
    print("Review recorded: phase {} {}".format(args.phase, args.status))


def cmd_approve(args):
    """approve: the human sign-off for the current phase (human-confirmed, T3-4)."""
    state = require_state()
    state["phase_approved"] = True
    state["feedback_provided"] = True
    state["phase_approved_at"] = now_iso()
    if args.note:
        state["phase_approval_note"] = args.note
    save_json(STATE_FILE, state)
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
    set_phase(state, new_phase, role=role, role_display=state["role_display"])
    save_json(STATE_FILE, state)

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
    review = {"status": args.review, "timestamp": ts}
    if args.review_note:
        review["note"] = args.review_note

    feedback = {
        "timestamp": ts,
        "role": state.get("role"),
        "phase": state.get("current_phase", state.get("phase")),
        "phase_display": state.get("phase_display"),
        "rating": args.rating,
        "worked_well": args.worked or "",
        "to_improve": args.improve or "",
        "duration_minutes": duration,
        "subagent_review": review,
    }
    fb_path = FEEDBACK_DIR / (ts.replace(":", "-") + ".json")
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
    print(f"Feedback saved: {fb_path}")


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

    args = p.parse_args()
    STATE_FILE = project_state_file()
    args.fn(args)


if __name__ == "__main__":
    main()
