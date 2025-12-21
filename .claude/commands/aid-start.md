# /aid start

Start a new work session with the AID Memory System.

## Purpose

Begin a tracked work session. Selects role and phase, loads relevant skills.

## Flow

1. **Check State**: Load `~/.aid/state.json`
   - If active session exists, ask to continue or start new

2. **Select Role**:
   ```
   Select your role:
   1. PM (Product Manager)
   2. Developer
   3. QA
   4. Lead
   ```

3. **Select Phase**:
   ```
   Select current phase:
   0. Discovery (Research & Validation)
   1. PRD (Requirements)
   2. Tech Spec (Architecture)
   3. Implementation Plan (Task Breakdown)
   4. Development (Code & Tests)
   5. QA & Ship (Deploy & Release)
   ```

4. **Load Skills**:
   - Read `memory-system/skills/roles/{role}/SKILL.md`
   - Read `memory-system/skills/phases/{phase}/SKILL.md`
   - Apply guidelines from both
   - For Phase 0: Also load `pre-prd-research`, `aid-discovery`

5. **Update State**:
   ```json
   {
     "role": "developer",
     "phase": 4,
     "phase_name": "Development",
     "session_start": "2024-01-15T09:00:00Z",
     "status": "active"
   }
   ```

6. **Greet User**:
   ```
   Session started

   Role: Developer
   Phase: 4 (Development)
   Skills loaded: developer, development

   Ready to work! Use /aid end when completing this phase.
   ```

## Phase 0 Special Handling

When user selects Phase 0 (Discovery):
```
Session started

Role: PM
Phase: 0 (Discovery)
Skills loaded:
- pre-prd-research (Business Analysis, Brainstorming, Problem-Solving)
- aid-discovery (Research methodology)
- nano-banana-visual (Optional - for diagrams)

Output folder: docs/research/YYYY-MM-DD-[project]/

Use /discovery [project-name] to create research folder structure.
Use /gate-check to see Phase 0 → 1 requirements.
Use /aid end when research is complete.
```

## Usage

```
/aid start
```

Or with parameters:
```
/aid start developer development
/aid start pm discovery
```

## Returning Session

If previous session exists:
```
Welcome back!

Last session:
- Role: Developer
- Phase: 4 (Development)
- Duration: 2h 15m
- Tasks completed: 3

Continue this session? (y/n)
```

## Phase Selection Reference

| Phase | Name | Focus | Primary Role |
|-------|------|-------|--------------|
| 0 | Discovery | Research & Validation | PM |
| 1 | PRD | Requirements | PM |
| 2 | Tech Spec | Architecture | Lead |
| 3 | Implementation Plan | Task Breakdown | Lead |
| 4 | Development | Code & Tests | Developer |
| 5 | QA & Ship | Deploy & Release | QA |

## Notes

- Skills are loaded automatically based on role+phase
- Session state persists across conversations
- Use `/aid status` to check current state
- Phase 0 (Discovery) is new - use `/discovery` to start research
- See `memory-system/docs/AGENT.md` for full behavior spec
