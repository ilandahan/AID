# AID Memory System

A learning system that helps Claude improve over time by collecting feedback, detecting patterns, and updating skills.

## Installation

Copy the `memory-system/` directory to your AID repository:

```bash
# From your AID repo root
cp -r /path/to/memory-system .
```

## Directory Structure

```
memory-system/           # Add to your AID repo
├── README.md           # This file
├── docs/               # Implementation documentation
│   ├── AGENT.md        # Agent behavior specification
│   ├── COMMANDS.md     # Command reference
│   ├── prompts.md      # UI prompt templates
│   ├── SUB-AGENT.md    # Analysis sub-agent spec
│   ├── IMPROVEMENT-FLOW.md
│   ├── MEMORY.md       # Claude Memory integration
│   ├── MEMORY-INIT.md  # Memory initialization
│   ├── USER-GUIDE.md   # End-user guide
│   ├── TROUBLESHOOTING.md
│   ├── MIGRATION.md    # Migration from existing AID
│   └── ERROR-HANDLING.md
├── skills/             # Skill templates
│   ├── roles/          # Role-specific skills
│   │   ├── pm/
│   │   ├── developer/
│   │   ├── qa/
│   │   └── lead/
│   └── phases/         # Phase-specific skills
│       ├── discovery/
│       ├── prd/
│       ├── tech-spec/
│       ├── development/
│       └── qa-ship/
├── templates/          # Runtime file templates
│   ├── config.yaml     # System configuration
│   ├── state.json      # Session state template
│   ├── trends.json     # Metrics template
│   └── memory-tracking.json
└── samples/            # Example files
    ├── feedback-sample.json
    └── analysis-sample.json
```

## Runtime Directory

The memory system creates a runtime directory at `~/.aid/` for user-specific data:

```
~/.aid/                 # Created at runtime (not in repo)
├── state.json          # Current session state
├── config.yaml         # User configuration
├── feedback/
│   ├── pending/        # Unprocessed feedback
│   └── processed/      # Analyzed feedback
├── skills/             # User's working skills (copied from repo)
├── metrics/
│   ├── trends.json
│   └── memory-tracking.json
└── logs/               # Error and debug logs
```

## Quick Start

### 1. Initialize

```
/aid init
```

This creates `~/.aid/` and copies skill templates.

### 2. Start Session

```
/aid start
```

Select your role and phase.

### 3. Work Normally

Claude applies relevant skills automatically.

### 4. End Phase

```
/aid end
```

Provide feedback on the session (1-5 rating + notes).

### 5. Run Improvement (Weekly)

```
/aid improve
```

Analyzes feedback, suggests skill updates, promotes insights to Claude Memory.

## Commands

| Command | Description |
|---------|-------------|
| `/aid init` | Initialize memory system |
| `/aid start` | Start new session |
| `/aid status` | Show current state |
| `/aid end` | End phase, collect feedback |
| `/aid improve` | Run improvement analysis |
| `/aid memory list` | Show Claude Memory entries |
| `/aid memory stats` | Memory usage statistics |
| `/aid skill view [name]` | View skill content |
| `/aid reset` | Full system reset |

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                     LEARNING LOOP                           │
│                                                             │
│  Work Session ──► Feedback ──► Analysis ──► Improvements   │
│       │              │            │              │          │
│       │              │            │              ▼          │
│       │              │            │         Skills Updated  │
│       │              │            │              │          │
│       │              │            │              ▼          │
│       │              │            └────► Memory Promoted    │
│       │              │                                      │
│       └──────────────┴────────── Next Session ◄────────────┘
└─────────────────────────────────────────────────────────────┘
```

1. **Feedback Collection**: At phase end, user rates (1-5) and describes what worked/didn't
2. **Pattern Detection**: Sub-agent clusters feedback, identifies recurring themes
3. **Skill Updates**: Suggestions to update role/phase skills based on patterns
4. **Memory Promotion**: High-value insights promoted to Claude Memory for cross-session learning

## Roles & Phases

**Roles:**
- PM (Product Manager)
- Developer
- QA
- Lead

**Phases:**
- Discovery
- PRD
- Tech Spec
- Development
- QA & Ship

Each combination has a skill file that Claude loads automatically.

## Claude Memory Integration

The system uses Claude Memory (30 slots) for persistent learning:

| Category | Slots | Purpose |
|----------|-------|---------|
| Universal | 5 | Cross-role insights |
| PM | 5 | PM-specific learnings |
| Developer | 5 | Dev-specific learnings |
| QA | 5 | QA-specific learnings |
| Lead | 3 | Leadership insights |
| Phase | 5 | Phase-specific patterns |
| Learned | 10 | Dynamic from feedback |

Entries follow format: `AID:{ROLE}:{PHASE}:{TYPE} {insight}`

## Starter Memory Entries

Initialize Claude Memory with these 20 entries:

**Universal (5):**
```
AID:ALL:ALL:WORKFLOW Always complete current phase before starting next
AID:ALL:ALL:CONTEXT Start each session by reading work_context.json
AID:ALL:ALL:DOCS Update documentation in real-time not at end
AID:ALL:ALL:HUMAN Get explicit approval before major decisions
AID:ALL:ALL:QUALITY Verify every artifact against requirements
```

**PM (5):**
```
AID:PM:DISCOVERY:SCOPE Define what's NOT included upfront
AID:PM:PRD:METRICS Add measurable success criteria to every feature
AID:PM:PRD:PRIORITY MUST/SHOULD/COULD for every requirement
AID:PM:ALL:STAKEHOLDER Document who decides what explicitly
AID:PM:ALL:TRADEOFF Present options with pros/cons not single solutions
```

**Developer (5):**
```
AID:DEV:TECH:DECISIONS Document why not just what for tech choices
AID:DEV:DEV:TDD Write test first then implement
AID:DEV:DEV:ATOMIC One logical change per commit
AID:DEV:ALL:DEBT Mark shortcuts with TODO-DEBT and track
AID:DEV:QA:EDGE Test edge cases not just happy path
```

**QA (5):**
```
AID:QA:QA:COVERAGE Every requirement needs at least one test
AID:QA:QA:DATA Use realistic data in tests
AID:QA:QA:NEGATIVE Test what should fail not just succeed
AID:QA:DEV:EARLY Start test planning in tech-spec phase
AID:QA:ALL:REGRESSION Keep regression suite fast and reliable
```

## Documentation

- [User Guide](docs/USER-GUIDE.md) - Complete usage instructions
- [Commands Reference](docs/COMMANDS.md) - All commands detailed
- [Agent Behavior](docs/AGENT.md) - How the agent works
- [Improvement Flow](docs/IMPROVEMENT-FLOW.md) - Learning cycle implementation
- [Memory Management](docs/MEMORY.md) - Claude Memory integration
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues & solutions
- [Migration Guide](docs/MIGRATION.md) - Adding to existing AID setup
- [Error Handling](docs/ERROR-HANDLING.md) - Error codes & recovery

## Privacy

- Feedback is stored locally in `~/.aid/`
- Only anonymized patterns promoted to Claude Memory
- No project names, file paths, or specific content in memory
- User controls what gets promoted (manual approval)

## Integration with AID Methodology

This memory system enhances the existing AID workflow:

1. **Phase Gates** - Feedback collection triggers at phase transitions
2. **Skill Loading** - Claude reads relevant skills at session start
3. **Context Tracking** - Maintains state across sessions
4. **Continuous Improvement** - Skills evolve based on actual usage

The memory system is **additive** - it doesn't change the core AID methodology, just adds learning capabilities.
