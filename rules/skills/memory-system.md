# Memory System Rules

Rules for loading and using the AID Memory System skill.

---

## When to Load This Skill

Load `skills/memory-system/SKILL.md` when the user invokes:

| Command | Description |
|---------|-------------|
| `/aid-init` | Initialize memory system for project |
| `/aid-start` | Start work session (role + phase selection) |
| `/aid-end` | End phase and collect feedback |
| `/aid-improve` | Run improvement analysis (spawns sub-agent) |
| `/aid-status` | Check current state |
| `/aid-memory` | Manage memory entries |
| `/aid-reset` | Reset memory system |

---

## Automatic Loading

The memory system skill should be loaded automatically when:

1. User starts any AID session (`/aid-start`)
2. User ends any AID session (`/aid-end`)
3. User explicitly requests memory management

---

## Sub-Agent Spawning

When `/aid-improve` is invoked, spawn the memory analysis sub-agent:

```
Task(
  subagent_type: "aid:memory-analysis-agent",   # link-project route only: "memory-analysis-agent";
                                               # tools: Read, Grep, Glob (no Write)
  model: "inherit",
  prompt: [the inputs ({{FEEDBACK_DATA}} etc.), filled in; the agent brings its own prompt],
  description: "Memory system improvement analysis"
)
```

The agent only PROPOSES (JSON, no files). Queue, apply and memory writes follow
`commands/aid-improve.md`: `aid_session.py memory-queue`, then `memory-apply <id>` or
`memory-reject <id>` per proposal the user picks, then `memory-sync` if wanted. Claude Code
asks the user to confirm `memory-apply` and `memory-sync`. AID's own write commands (`memory-sync`, `memory-apply`) run only after you confirm
them in Claude Code's prompt. `memory-apply` is also used by `/aid-recommendations`.
Before Phase 4 the phase gate also refuses other writes outside the project. From
Phase 4 on, AID does not stop other code from editing these files. "Claude Memory" means AID's local memory,
`$AID_HOME/memory/slots.json`; nothing is sent to Claude's built-in memory.

### Data to Pass

| Variable | Source |
|----------|--------|
| `{{FEEDBACK_DATA}}` | The output of `aid_session.py memory-feedback` (the feedback, redacted, as JSON). Never paste raw pending files: files written before redaction existed may hold unredacted text. |
| `{{CURRENT_SKILLS}}` | Section headers from `skills/memory-system/references/` |
| `{{TREND_DATA}}` | Contents of `~/.aid/metrics/trends.json` |
| `{{MEMORY_ENTRIES}}` | Current AID:* entries in AID's local memory (`$AID_HOME/memory/slots.json`) |

---

## State Management

### State Files

| File | Purpose | Location |
|------|---------|----------|
| `state.json` | Phase tracking | `.aid/state.json` (project) |
| `context.json` | Work context | `.aid/context.json` (project) |
| `state.json` | Session state | `~/.aid/state.json` (user) |
| `feedback/pending/` | Unprocessed feedback | `$AID_HOME/feedback/pending/` (default `~/.aid/feedback/pending/`) |
| `feedback/processed/` | Archived feedback | `~/.aid/feedback/processed/` |

### Update Triggers

The project `.aid/state.json` is a protected control file. It is written only by
`hooks/aid_session.py`, through these commands:
- `/aid-start` (`init` for a new project and `jump` for a forward move, both confirmed by
  the user; `start` for the current or an earlier phase)
- `/setup` (`init`, which the user confirms)
- `/aid-end` (`end`, `review`)
- `/phase-approve` (`approve`, which the user confirms)
- `/phase-advance` (`advance`, which the user confirms)
- `/gate-check` (`review`)

Never edit the project `.aid/state.json` directly (Write, Edit, Bash or redirects); the
phase gates refuse it in every phase. Reading it is fine.

Update `.aid/context.json` when:
- New task begins
- Step completes
- Session ends

---

## Feedback Collection Rules

### MANDATORY

1. **Always collect rating (1-5)** at session end
2. **Track revision count** during session
3. **Never include project-specific data** (names, code, companies)
4. **Never write a feedback JSON file yourself.** The only writers are
   `aid_session.py end` (via `/aid-end`) and `aid_session.py approve` (via `/phase-approve`)

### OPTIONAL

1. What worked well
2. What could be improved
3. Additional notes

---

## Feedback Privacy (redaction is best effort)

Feedback text is redacted before it is written and again whenever it is read. E-mails,
URLs, absolute paths, `file.ext:line` references, common secret tokens, the project's own
names (cwd and project-root folder names, git remote owner and repo) and the OS user name are
replaced with placeholders. A person's or company's name written as plain words is NOT caught
unless it is one of those project names, so still leave these out.

### NEVER Include

- ❌ Project name or identifier
- ❌ Company name
- ❌ Domain-specific terms
- ❌ Code snippets
- ❌ User names

### ALWAYS Include

- ✅ Role (product-manager, developer, qa-engineer, tech-lead)
- ✅ Phase (discovery, prd, tech-spec, breakdown, development, qa-ship)
- ✅ Rating (1-5)
- ✅ Revision count
- ✅ Generic methodology feedback

---

## Improvement Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| Pending feedback | ≥ 5 | Suggest improvement run |
| Sessions since last improvement | ≥ 10 | Suggest improvement run |
| Average rating | < 3.5 | Flag for attention |

---

## Reference Loading

When session starts, load references from `skills/memory-system/references/`:

```
1. roles/{role}/QUICK-REFERENCE.md       - Role quick reference
2. roles/{role}/cumulative.md  - Role learnings
3. phases/{phase}/QUICK-REFERENCE.md     - Phase quick reference
4. phases/{phase}/cumulative.md - Phase learnings
```

---

## Error Handling

| Error | Action |
|-------|--------|
| Missing `~/.aid/` | Run `/aid-init` automatically |
| Missing skill files | Use defaults, log warning |
| Corrupted project `.aid/state.json` | Do not edit it. Run `aid_session.py init <role> <phase> --repair` (the user confirms) |
| User skips rating | Gently insist, then save as null |

---

## Related Files

| File | Purpose |
|------|---------|
| `agents/memory-analysis-agent.md` | Sub-agent prompt |
| `skills/memory-system/SKILL.md` | Skill definition |
| `skills/memory-system/references/` | Role/phase references |
| `commands/aid-*.md` | Memory system commands |
