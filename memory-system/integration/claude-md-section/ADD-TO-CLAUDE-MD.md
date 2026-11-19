# Memory System Section for CLAUDE.md

Add this section to your existing CLAUDE.md file.

---

## Memory System

AID includes a learning system that improves Claude's assistance over time by collecting feedback, detecting patterns, and updating skills.

### Quick Commands

| Command | Description |
|---------|-------------|
| `/aid init` | Initialize memory system (first time only) |
| `/aid start` | Start work session - select role & phase |
| `/aid status` | Show current state |
| `/aid end` | End phase and provide feedback |
| `/aid-improve` | Run learning cycle (weekly) |
| `/aid memory list` | Show AID's local memory entries |

### Session Flow

1. **Start**: `/aid start` → Select role (PM/Dev/QA/Lead) → Select phase → Skills loaded
2. **Work**: Claude applies loaded skills automatically
3. **End**: `/aid end` → Rate session (1-5) → Describe what worked/didn't
4. **Learn**: `/aid-improve` → Analyze feedback → Update skills → Promote to memory

### Skills Location

Claude loads skills based on role and phase:
- Role skills: `skills/memory-system/references/roles/{role}/QUICK-REFERENCE.md`
- Phase skills: `skills/memory-system/references/phases/{phase}/QUICK-REFERENCE.md`

At session start, read both relevant skill files and apply their guidelines.

### Runtime State

Session state stored in `~/.aid/state.json`:
- Current role and phase
- Session start time
- Task and step tracking

### Feedback Collection

At phase end (`/aid end`):
1. Summarize work completed
2. Ask for rating (1-5)
3. Ask: "What worked well?"
4. Ask: "What could be improved?"
5. Save with ONE call: `python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" end ...`
   (see `commands/aid-end.md`). It redacts the text (best effort) and writes
   `$AID_HOME/feedback/pending/`. Never write a feedback JSON file by hand.

### Improvement Cycle

When `/aid-improve` is called:
1. Analyze pending feedback (need 3+ items)
2. Detect patterns across sessions
3. Propose skill updates (the analysis agent only proposes)
4. The user applies chosen proposals and memory entries; Claude Code asks the user to
   confirm each write (`aid_session.py memory-apply <id>`, `aid_session.py memory-sync`)

### AID Local Memory Entries

AID uses a local file, `$AID_HOME/memory/slots.json` (default `~/.aid/memory/`), for
persistent cross-session learning. Nothing is sent to Claude's built-in memory.
Entry format: `AID:{ROLE}:{PHASE}:{TYPE} {insight}`

Categories and slots:
- Universal: 5 slots
- PM/Dev/QA: 5 slots each
- Lead: 3 slots
- Phase-specific: 5 slots
- Learned (dynamic): 10 slots

### Documentation

Full documentation: `memory-system/docs/`
- USER-GUIDE.md - Complete usage guide
- COMMANDS.md - All commands detailed
- TROUBLESHOOTING.md - Common issues

---
