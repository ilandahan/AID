---
name: memory-system
description: AID Memory System for session feedback, learning cycles, and skill improvement. Manages state, feedback collection, and improvement analysis. Load for /aid-init, /aid-start, /aid-status, /aid-end, /aid-improve, /aid-memory, /aid-reset.
---

# Memory System Skill

## Triggers
Load when the user invokes any of these; otherwise do not load.

| Command | Description |
|---|---|
| `/aid-init` | Initialize AID system / memory system (first time setup) |
| `/aid-start [role] [phase]` | Start a work session |
| `/aid-status` | Show current session state |
| `/aid-end` | Complete phase gate, collect feedback |
| `/aid-improve` | Run improvement analysis (spawns sub-agent) |
| `/aid-memory` | Manage memory entries |
| `/aid-reset` | Reset memory system (clear state & feedback) |

## Enums
Roles: `product-manager` (pm), `developer` (dev), `qa-engineer` (qa), `tech-lead` (lead), `data-scientist` (ds)

Phases: `discovery` (Phase 0), `prd` (Phase 1), `tech-spec` (Phase 2), `breakdown` (Phase 3), `development` (Phase 4), `qa-ship` (Phase 5)

## Sub-Agent: Memory Analysis
On `/aid-improve`, spawn the **memory-analysis-agent**:

```
Task(
  subagent_type: "aid:memory-analysis-agent",   # fallback: "memory-analysis-agent";
                                               # tools: Read, Grep, Glob (no Write)
  model: "inherit",
  prompt: [the inputs below, filled in; the agent brings its own prompt],
  description: "Memory system improvement analysis"
)
```

Pass:
```
{{FEEDBACK_DATA}} - The output of `aid_session.py memory-feedback` (the feedback,
                    redacted, as JSON). Never paste raw pending files: files written
                    before redaction existed may hold unredacted text.
{{CURRENT_SKILLS}} - Section headers from skills/memory-system/references/
{{TREND_DATA}} - Contents of ~/.aid/metrics/trends.json
{{MEMORY_ENTRIES}} - Current AID:* entries in AID's local memory ($AID_HOME/memory/slots.json)
```

Agent returns:
```json
{
  "suggestions": [...],
  "memory_candidates": [...],
  "trends_analysis": {...}
}
```

## Session Start Flow (`/aid-start`)
1. Check AID directory:
```
IF ~/.aid/ does not exist:
  → Run /aid-init flow
  → Create directory structure
  → Initialize with defaults
  → Display: "🚀 AID Memory System initialized!"
```
2. Load state: read `~/.aid/state.json`; check `pending_feedback_count`; check `sessions_since_last_improvement`.
3. Check improvement suggestion:
```
IF pending feedback >= threshold:
  Display:
  "📊 I have {pending} feedback items waiting for analysis.
   Would you like to review insights and improve skills?
   [Yes, let's improve] [No, continue working]"
```
4. Determine role & phase:
```
IF /aid-start <role> <phase> provided:
  → Use provided values
ELIF state.last_session exists:
  → Suggest: "Continue as {last_role} in {last_phase}?"
ELSE:
  → Ask for role and phase
```
5. Load skills from `skills/memory-system/references/`, in order:
```
1. roles/{role}/QUICK-REFERENCE.md
2. roles/{role}/cumulative.md
3. phases/{phase}/QUICK-REFERENCE.md
4. phases/{phase}/cumulative.md
```
6. Begin (state is already written):
```
Do not edit ~/.aid/state.json yourself: aid_session.py start/end updates it
(the session role, phase, start time and active flag are set by
`aid_session.py start`, which /aid-start runs).

Greet user and ask what they're working on.
```

## Session Work Flow
Track revisions (internal counter):
```
revision_triggers = [
  "fix", "change", "update", "wrong", "missing", "add",
  "incorrect", "error", "should be", "not right", "revise"
]

On each user message containing trigger:
  revision_count += 1
  Note what needed fixing for feedback
```

Note patterns (internal):
```
positive_triggers = ["great", "perfect", "exactly", "good", "excellent"]

On positive trigger:
  Note what worked well for feedback
```

## Phase Gate Flow (`/aid-end` or phase completion detected)
1. Display summary:
```
📋 Phase Summary: {phase_display_name}

Completed deliverables:
• {deliverable_1}
• {deliverable_2}

Revisions made: {revision_count}
```
2. Request rating (MANDATORY):
```
📊 Quality Rating (1-5):

1 ⭐ - Poor, needs significant improvement
2 ⭐⭐ - Below average, missing important elements
3 ⭐⭐⭐ - Acceptable, worked but room for improvement
4 ⭐⭐⭐⭐ - Good, almost perfect
5 ⭐⭐⭐⭐⭐ - Excellent, exactly what I needed

MUST get rating before proceeding
```
3. Request qualitative feedback (optional): What worked well? What could be improved? Additional notes?
4. Save feedback: Do NOT write a feedback JSON file yourself. `/aid-end` saves it with ONE Bash call,
`python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" end --rating <1-5> --worked "..." --improve "..."`
(see `commands/aid-end.md` for the exact shape). The script redacts the text (best effort)
and writes `$AID_HOME/feedback/pending/` (default `~/.aid/feedback/pending/`). The only
other writer is `aid_session.py approve` (via `/phase-approve`), which stores its rating as a
pending entry too.
5. State: nothing to do by hand.
```
Do not edit ~/.aid/state.json yourself: aid_session.py start/end updates it
(session statistics and the active flag are updated by `aid_session.py end`).
```

## Improvement Flow (`/aid-improve`)
Follow `commands/aid-improve.md` exactly. Each command is ONE Bash call in exactly the shape
shown there (lower-case `python`, single spaces, no `;`, `&&`, pipes or redirects). Never retry
in another spelling and never work around a refusal or a declined prompt. If
`${CLAUDE_PLUGIN_ROOT}` was not replaced by a real path, this is not a plugin install; do not
substitute another path.

1. Preview (writes nothing, no prompt): `python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" memory-preview`
2. Get the feedback, redacted, as JSON (writes nothing, no prompt):
   `python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" memory-feedback`. Use this output as
   `{{FEEDBACK_DATA}}`; never open raw pending files. If it has fewer than 3 entries, stop
   unless the user passed `--force`.
3. Spawn the analysis agent (below). It only PROPOSES: it returns JSON and writes no files.
4. Save that JSON to `.aid/improve/proposals.json` with the Write tool, then queue it
   (redacted, no prompt): `python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" memory-queue`
   (no argument: it reads `<project>/.aid/improve/proposals.json` itself).
   A proposal whose target is not an allowed file is skipped.
5. Show the queue and let the user pick.
6. For each proposal the user picks:
   - apply: `python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" memory-apply <id>`. Claude
     Code asks the user to confirm. It only APPENDS to
     `skills/memory-system/references/roles/<role>/cumulative.md` or
     `.../phases/<phase>/cumulative.md`; anything else is refused.
   - drop: `python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" memory-reject <id>` (no prompt).
   Skill-wide recommendations (no learnings file) are shown but cannot be applied by the tool.
7. If the user wants the memory entries: `python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" memory-sync`.
   Claude Code asks the user to confirm. It writes AID's local memory,
   `$AID_HOME/memory/slots.json`; nothing is sent to Claude's built-in memory. In
   `-p`/headless sessions it is denied.

AID's own write commands (`memory-sync`, `memory-apply`) run only after you confirm
them in Claude Code's prompt. `memory-apply` is also used by `/aid-recommendations`.
Before Phase 4 the phase gate also refuses other writes outside the project. From
Phase 4 on, AID does not stop other code from editing these files.

## Feedback Privacy (redaction is best effort)
Redaction is best effort. Feedback text is redacted before it is written and again whenever
it is read. E-mails, URLs, absolute paths, `file.ext:line` references, common secret tokens,
the project's own names (cwd and project-root folder names, git remote owner and repo) and
the OS user name are replaced with `[email]`, `[url]`, `[path]`, `[file-ref]`, `[token]`,
`[project]` or `[user]`. A person's or company's name written as plain words is NOT caught unless it is one
of those project names, and very generic folder names (docs, app, src, ...) are not removed.
So when you condense the user's answers:

NEVER include in feedback:
- ❌ Project name or identifier
- ❌ Company name
- ❌ Domain-specific terms
- ❌ Code snippets
- ❌ User names

ALWAYS include:
- ✅ Role (product-manager, developer, etc.)
- ✅ Phase (discovery, prd, etc.)
- ✅ Rating (1-5)
- ✅ Revision count
- ✅ Generic methodology feedback

## State Files
| File | Purpose |
|---|---|
| `~/.aid/state.json` | Current session state |
| `~/.aid/config.yaml` | User configuration |
| `~/.aid/feedback/pending/` | Unprocessed feedback |
| `~/.aid/feedback/processed/` | Archived feedback |
| `~/.aid/metrics/trends.json` | Historical trends |

## Error Handling
| Error | Action |
|---|---|
| Missing ~/.aid/ | Run /aid-init automatically |
| Missing skill files | Use defaults, log warning |
| Corrupted project `.aid/state.json` | Do not edit it. Run `aid_session.py init <role> <phase> --repair` (the user confirms) |
| User skips rating | Gently insist, then save as null |

## Related
- Agent: `../../agents/memory-analysis-agent.md`
- References: `skills/memory-system/references/`
- Commands: `../../commands/aid-*.md`
