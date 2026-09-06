---
description: "Start a work session: pick a role and phase, load the matching skills"
---

# /aid start

Start a new work session with the AID Memory System.

## Purpose

Begin a tracked work session. Selects role FIRST, then shows phase options with role-specific terminology.

## Terminology Reference

Load role-specific phase names and descriptions from:
`references/role-phase-terminology.json`

## Flow

### Step 1: Check Existing Session

Load project-local `.aid/state.json` (NOT `~/.aid/state.json` — that file is global to the
user and shared across every AID project on the machine; reading it here leaks another
project's role/phase/session-count into this one).
- If active session exists, ask to continue or start new

```
Welcome back!

Last session:
- Role: [Previous Role]
- Phase: [Previous Phase Name]

Continue this session? (y/n)
```

### Step 2: Select Role (FIRST)

Print the role menu. Do not type it from memory and do not use AskUserQuestion (it caps at
4 options; there are more roles than that):

```bash
# Resolve the script path (repo → project mirror → installed plugin). Repeated in each
# step on purpose: every Bash call is a fresh shell, so $f does not survive between them.
f=; for c in hooks/aid_session.py .claude/hooks/aid_session.py "$(ls -d "$HOME"/.claude/plugins/cache/AID/aid/*/ 2>/dev/null | sort -V | tail -1)hooks/aid_session.py"; do [ -f "$c" ] && f=$c && break; done
python "$f" roles
```

Show the output verbatim and wait for the user's number.

### Step 3: Select Phase (SECOND - with Role-Specific Terminology)

Print that role's phases. Phase names and descriptions differ per role, and the script
supplies the right set:

```bash
f=; for c in hooks/aid_session.py .claude/hooks/aid_session.py "$(ls -d "$HOME"/.claude/plugins/cache/AID/aid/*/ 2>/dev/null | sort -V | tail -1)hooks/aid_session.py"; do [ -f "$c" ] && f=$c && break; done
python "$f" phases <role>     # role name, or the number the user just picked
```

Show the output verbatim and wait for the user's number.

**Why both menus are generated, never written here:** they used to be hand-copied into this
file, one block per role. The copy drifted from
`references/role-phase-terminology.json` - `data-scientist` was a fully defined role with
six phases and its own skills, yet no menu offered it, and slot 5 selected "Other" instead.
Generating both menus means every role and phase in the terminology file is always on offer,
and the number the user types selects exactly what the menu showed.

### Step 4: Handle "Other" Selections

**If "Other" role selected:**
- Ask: "Please describe your role for this session:"
- Record response in session state
- Use Developer phase terminology as default

**If "Other" phase selected:**
- Ask: "Please describe what you're working on:"
- Record response in session state
- Determine closest matching phase number (0-5) for skill loading

### Step 5: Write State and Greet (ONE Bash call)

Run the session writer. It resolves role + phase against
`references/role-phase-terminology.json`, writes project-local `.aid/state.json`
(role, phase, skills_loaded, session_start), and prints the greeting:

```bash
f=; for c in hooks/aid_session.py .claude/hooks/aid_session.py "$(ls -d "$HOME"/.claude/plugins/cache/AID/aid/*/ 2>/dev/null | sort -V | tail -1)hooks/aid_session.py"; do [ -f "$c" ] && f=$c && break; done
python "$f" start <role> <phase>
# role:  pm | lead | developer | qa | data-scientist | other, or the menu number
# phase: 0-5
# "Other" role/phase: add --role-desc "..." / --phase-desc "..." with the user's words
```

Show its output to the user verbatim. That output is the greeting; do not compose another.

**Do NOT read SKILL.md files here.** Skills are registered by the plugin and load on
demand when the work calls for them. Reading 6-12 skill files up front is what made
`/aid-start` take minutes: each Read was a model round trip before the state file
was ever written. `skills_loaded` in state.json is the record of which skills apply.

## Usage

```
/aid start
```

Or with parameters (using role-specific phase names or numbers):
```
/aid start developer 4
/aid start pm "Product Requirements"
```

## Quick Reference

| Role | Phase 0 | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 |
|------|---------|---------|---------|---------|---------|---------|
| PM | Market Research | PRD | Solution Review | Roadmap | UAT | Launch |
| Lead | Tech Research | Tech Requirements | Architecture | Sprint Planning | Code Review | Deployment |
| Dev | Spike & Research | Feature Spec | Technical Design | Task Breakdown | Coding | Bug Fixes |
| QA | Test Strategy | Coverage Plan | Test Framework | Test Cases | Execution | Certification |
| Data Scientist | EDA | Feasibility | Experiment Planning | ML Arch & Pipeline | Development & Validation | Deploy & Monitoring |

Generated from `references/role-phase-terminology.json`; run `aid_session.py roles` for the
authoritative list.

## Notes

- Role is selected FIRST, then phase (allows terminology to be customized)
- Every role and every phase in the terminology file is offered - the menus are generated from it, so nothing can be silently missing
- All 6 phases (0-5) are shown, plus an "Other" option
- Phase names and descriptions are role-specific
- Skills are loaded based on role+phase combination
- Session state persists across conversations
- Use `/aid status` to check current state
- See `memory-system/docs/AGENT.md` for full behavior spec
