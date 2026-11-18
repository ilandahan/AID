> Human-readable companion to SKILL.md. The LLM loads SKILL.md only.

# Memory System Skill

## Overview

The **AID Memory System** is how the methodology learns from use. Every work session
ends with a small feedback record, redacted (best effort); those records accumulate; a
periodic improvement cycle reads them and proposes concrete updates to the skill learnings
files and to AID's local memory (`$AID_HOME/memory/slots.json`, not Claude's built-in
memory). AID's own write commands run only after the user confirms them. The result is that the same mistake does not have to be corrected twice.

This skill covers three things: the **state** that tracks where a session is, the
**feedback collection** that happens at a phase gate, and the **improvement analysis**
that turns collected feedback into skill changes.

Load this skill whenever working with AID Memory System commands (`/aid-start`,
`/aid-end`, `/aid-improve`, and the rest).

---

## When to Load This Skill

Load when the user invokes any of:

| Command | Why the skill is needed |
|---------|-------------------------|
| `/aid-init` | Initialize memory system |
| `/aid-start` | Start work session |
| `/aid-end` | End phase with feedback |
| `/aid-improve` | Run improvement analysis |
| `/aid-status` | Check current state |
| `/aid-memory` | Manage memory entries |
| `/aid-reset` | Reset memory system |

---

## Quick Reference

### Commands

| Command | Description |
|---------|-------------|
| `/aid-init` | Initialize AID system (first time setup) |
| `/aid-start [role] [phase]` | Start a session |
| `/aid-status` | Show current session state |
| `/aid-end` | Complete phase gate, collect feedback |
| `/aid-improve` | Run improvement analysis (spawns sub-agent) |
| `/aid-reset` | Reset memory system (clear state & feedback) |

### Roles

Each role has its own reference material and its own accumulated learnings, so
feedback from a PM session improves the PM guidance rather than being averaged
across everyone.

- `product-manager` (pm)
- `developer` (dev)
- `qa-engineer` (qa)
- `tech-lead` (lead)
- `data-scientist` (ds)

### Phases

- `discovery` (Phase 0)
- `prd` (Phase 1)
- `tech-spec` (Phase 2)
- `breakdown` (Phase 3)
- `development` (Phase 4)
- `qa-ship` (Phase 5)

---

## Session Start Flow

What happens when the user says `/aid-start`. The steps are ordered so that a
first-time user is bootstrapped automatically and a returning user is offered
continuity instead of being asked to re-enter everything.

### Step 1: Check AID Directory

If the system has never been initialised, `/aid-start` does not fail — it runs the
`/aid-init` flow first.

```
IF ~/.aid/ does not exist:
  → Run /aid-init flow
  → Create directory structure
  → Initialize with defaults
  → Display: "🚀 AID Memory System initialized!"
```

### Step 2: Load State

```
Read ~/.aid/state.json
Check pending_feedback_count
Check sessions_since_last_improvement
```

### Step 3: Check Improvement Suggestion

Feedback that is never analysed is wasted, so session start is the natural moment to
surface a backlog — before new work begins rather than in the middle of it.

```
IF pending feedback >= threshold:
  Display:
  "📊 I have {pending} feedback items waiting for analysis.
   Would you like to review insights and improve skills?
   [Yes, let's improve] [No, continue working]"
```

### Step 4: Determine Role & Phase

```
IF /aid-start <role> <phase> provided:
  → Use provided values
ELIF state.last_session exists:
  → Suggest: "Continue as {last_role} in {last_phase}?"
ELSE:
  → Ask for role and phase
```

### Step 5: Load Skills

Both the base reference and the cumulative learnings are loaded, for the role and for
the phase — the cumulative files are where past improvement cycles land.

```
Load from skills/memory-system/references/:
1. roles/{role}/SKILL.md
2. roles/{role}/cumulative.md
3. phases/{phase}/SKILL.md
4. phases/{phase}/cumulative.md
```

### Step 6: Update State & Begin

```
Update ~/.aid/state.json with:
- current_session.active = true
- current_session.role = role
- current_session.phase = phase
- current_session.started_at = now()

Greet user and ask what they're working on.
```

---

## Session Work Flow

During the session, two lightweight internal counters run. Neither is shown to the
user as it happens; both exist so that the feedback collected at the phase gate is
grounded in what actually occurred rather than in end-of-session recollection.

### Track Revisions (Internal Counter)

A revision is a signal that the first attempt missed. Counting them gives the
improvement cycle a quantitative measure alongside the subjective rating.

```
revision_triggers = [
  "fix", "change", "update", "wrong", "missing", "add",
  "incorrect", "error", "should be", "not right", "revise"
]

On each user message containing trigger:
  revision_count += 1
  Note what needed fixing for feedback
```

### Note Patterns (Internal)

```
positive_triggers = ["great", "perfect", "exactly", "good", "excellent"]

On positive trigger:
  Note what worked well for feedback
```

---

## Phase Gate Flow (Feedback Collection)

Runs when the user says `/aid-end`, or when phase completion is otherwise detected.

### Step 1: Display Summary

Show what the phase produced, so the rating that follows is given against a concrete
recap rather than a vague impression.

```
📋 Phase Summary: {phase_display_name}

Completed deliverables:
• {deliverable_1}
• {deliverable_2}

Revisions made: {revision_count}
```

### Step 2: Request Rating (MANDATORY)

The rating is the one non-optional input. Without it there is no trend line, and
trend data is what distinguishes a one-off bad session from a systematic weakness.

```
📊 Quality Rating (1-5):

1 ⭐ - Poor, needs significant improvement
2 ⭐⭐ - Below average, missing important elements
3 ⭐⭐⭐ - Acceptable, worked but room for improvement
4 ⭐⭐⭐⭐ - Good, almost perfect
5 ⭐⭐⭐⭐⭐ - Excellent, exactly what I needed

MUST get rating before proceeding
```

### Step 3: Request Qualitative Feedback (Optional)

```
What worked well? (optional)
What could be improved? (optional)
Additional notes? (optional)
```

### Step 4: Save Feedback

Do NOT write a feedback JSON file yourself. `/aid-end` saves it with ONE Bash call,
`python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" end --rating <1-5> --worked "..." --improve "..."`
(see `commands/aid-end.md` for the exact shape). The script redacts the text (best effort)
and writes `$AID_HOME/feedback/pending/` (default `~/.aid/feedback/pending/`). The only
other writer is `aid_session.py approve` (via `/phase-approve`), which stores its rating as a
pending entry too.

### Step 5: Update State

```
Update ~/.aid/state.json:
- statistics.total_sessions += 1
- statistics.pending_feedback_count += 1
- statistics.sessions_since_last_improvement += 1
- current_session.active = false
```

---

## Improvement Flow (/aid-improve)

The learning cycle. It is deliberately a separate, explicit command rather than
something that happens silently: skill files change as a result, and those changes
go through human approval: Claude Code asks the user to confirm AID's own write commands.

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

---

## Sub-Agent: Memory Analysis

`/aid-improve` delegates the analysis to the **memory-analysis-agent**. The agent runs
in isolation, which is the point: it evaluates the feedback record on its own terms,
without the conversational context that produced it.

```
Task(
  subagent_type: "aid:memory-analysis-agent",   # fallback: "memory-analysis-agent";
                                               # tools: Read, Grep, Glob (no Write)
  model: "inherit",
  prompt: [Read ../../agents/memory-analysis-agent.md],
  description: "Memory system improvement analysis"
)
```

### What to Pass to Agent

```
{{FEEDBACK_DATA}} - The output of `aid_session.py memory-feedback` (the feedback,
                    redacted, as JSON). Never paste raw pending files: files written
                    before redaction existed may hold unredacted text.
{{CURRENT_SKILLS}} - Section headers from skills/memory-system/references/
{{TREND_DATA}} - Contents of ~/.aid/metrics/trends.json
{{MEMORY_ENTRIES}} - Current AID:* entries in AID's local memory ($AID_HOME/memory/slots.json)
```

### What Agent Returns

```json
{
  "suggestions": [...],
  "memory_candidates": [...],
  "trends_analysis": {...}
}
```

---

## Feedback Privacy (redaction is best effort)

Feedback is about the **methodology**, not about the project. Keep records free of
anything project-specific so that accumulated learnings stay portable and safe to
carry across work.

Redaction is best effort. Feedback text is redacted before it is written and again whenever
it is read. E-mails, URLs, absolute paths, `file.ext:line` references, common secret tokens,
the project's own names (cwd and project-root folder names, git remote owner and repo) and
the OS user name are replaced with `[email]`, `[url]`, `[path]`, `[file-ref]`, `[token]`,
`[project]` or `[user]`. A person's or company's name written as plain words is NOT caught unless it is one
of those project names, and very generic folder names (docs, app, src, ...) are not removed.
So when you condense the user's answers:

### NEVER include in feedback:

- ❌ Project name or identifier
- ❌ Company name
- ❌ Domain-specific terms
- ❌ Code snippets
- ❌ User names

### ALWAYS include:

- ✅ Role (product-manager, developer, etc.)
- ✅ Phase (discovery, prd, etc.)
- ✅ Rating (1-5)
- ✅ Revision count
- ✅ Generic methodology feedback

---

## State Files

| File | Purpose |
|------|---------|
| `~/.aid/state.json` | Current session state |
| `~/.aid/config.yaml` | User configuration |
| `~/.aid/feedback/pending/` | Unprocessed feedback |
| `~/.aid/feedback/processed/` | Archived feedback |
| `~/.aid/metrics/trends.json` | Historical trends |

---

## Error Handling

The memory system should never be the thing that blocks work. Each failure mode
degrades to something usable rather than stopping the session.

| Error | Action |
|-------|--------|
| Missing `~/.aid/` | Run `/aid-init` automatically |
| Missing skill files | Use defaults, log warning |
| Corrupted project `.aid/state.json` | Do not edit it. Run `aid_session.py init <role> <phase> --repair` (the user confirms) |
| User skips rating | Gently insist, then save as null |

---

## Related

- Agent: `../../agents/memory-analysis-agent.md`
- References: `skills/memory-system/references/`
- Commands: `../../commands/aid-*.md`
</content>
</invoke>
