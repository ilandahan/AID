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

Usage:
  aid_session.py start <role> <phase> [--role-desc TEXT] [--phase-desc TEXT]
      role:  pm | lead | developer | qa | data-scientist | other  (or menu number 1-5)
      phase: 0-5
  aid_session.py end --rating N [--worked TEXT] [--improve TEXT]
      [--review passed|partial|failed|skipped] [--review-note TEXT]
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Windows consoles default to cp1252, which cannot print the ✅ in the greeting.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
TERMS_FILE = HERE.parent / "references" / "role-phase-terminology.json"
STATE_FILE = Path.cwd() / ".aid" / "state.json"
FEEDBACK_DIR = Path.home() / ".aid" / "feedback" / "pending"

# Menu numbers from the /aid-start prompt. 5 = "Other" -> developer terminology.
ROLE_MENU = {"1": "pm", "2": "lead", "3": "developer", "4": "qa", "5": "other"}
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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def cmd_start(args):
    terms = load_json(TERMS_FILE)
    if not terms:
        sys.exit(f"cannot read {TERMS_FILE}")

    raw = args.role.strip().lower()
    role = ROLE_MENU.get(raw) or ROLE_ALIASES.get(raw)
    if not role:
        sys.exit(f"unknown role '{args.role}' (use pm|lead|developer|qa|data-scientist|other or 1-5)")
    term_role = "developer" if role == "other" else role

    phase_key = str(args.phase).strip()
    if phase_key not in terms["phases"][term_role]:
        sys.exit(f"unknown phase '{args.phase}' (use 0-5)")
    phase = terms["phases"][term_role][phase_key]

    role_info = terms["roles"][term_role]
    skills = [terms["roleSkillMapping"][term_role]] + list(phase.get("skills", []))
    for s in terms.get("commonSkills", []):
        if s not in skills:
            skills.append(s)

    state = load_json(STATE_FILE, {}) or {}
    state.update({
        "role": role,
        "role_display": args.role_desc or role_info["name"],
        "phase": int(phase_key),
        "current_phase": int(phase_key),
        "phase_display": phase["name"],
        "phase_description": args.phase_desc or phase["description"],
        "session_start": now_iso(),
        "status": "active",
        "skills_loaded": skills,
    })
    # phase_name is the role-neutral name aid_hooks.py prints in gate messages.
    state["phase_name"] = ["Discovery", "PRD", "Tech Spec", "Impl Plan", "Development", "QA & Ship"][int(phase_key)]
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
    state = load_json(STATE_FILE, {}) or {}
    if not state:
        sys.exit(f"no active session: {STATE_FILE} missing (run /aid-start first)")

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
    save_json(STATE_FILE, state)

    print("✅ Session ended\n")
    print(f"Role:  {state.get('role_display')}   Phase: {phase_n}. {state.get('phase_display')}")
    if duration is not None:
        print(f"Duration: {duration} min")
    print(f"Rating: {args.rating}/5")
    print(f"Sub-agent review: {args.review}")
    print(f"Feedback saved: {fb_path}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("start")
    s.add_argument("role")
    s.add_argument("phase")
    s.add_argument("--role-desc", default=None, help="custom description when role is 'other'")
    s.add_argument("--phase-desc", default=None, help="custom description when phase is 'other'")
    s.set_defaults(fn=cmd_start)

    e = sub.add_parser("end")
    e.add_argument("--rating", type=int, required=True, choices=range(1, 6))
    e.add_argument("--worked", default=None)
    e.add_argument("--improve", default=None)
    e.add_argument("--review", default="skipped", choices=["passed", "partial", "failed", "skipped"])
    e.add_argument("--review-note", default=None)
    e.set_defaults(fn=cmd_end)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
