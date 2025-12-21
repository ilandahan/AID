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
   1. Discovery
   2. PRD
   3. Tech Spec
   4. Development
   5. QA & Ship
   ```

4. **Load Skills**:
   - Read `memory-system/skills/roles/{role}/SKILL.md`
   - Read `memory-system/skills/phases/{phase}/SKILL.md`
   - Apply guidelines from both

5. **Update State**:
   ```json
   {
     "role": "developer",
     "phase": "development",
     "session_start": "2024-01-15T09:00:00Z",
     "status": "active"
   }
   ```

6. **Greet User**:
   ```
   ✅ Session started
   
   Role: Developer
   Phase: Development
   Skills loaded: developer, development
   
   Ready to work! Use /aid end when completing this phase.
   ```

## Usage

```
/aid start
```

Or with parameters:
```
/aid start developer development
```

## Returning Session

If previous session exists:
```
Welcome back!

Last session:
- Role: Developer
- Phase: Development
- Duration: 2h 15m
- Tasks completed: 3

Continue this session? (y/n)
```

## Notes

- Skills are loaded automatically based on role+phase
- Session state persists across conversations
- Use `/aid status` to check current state
- See `memory-system/docs/AGENT.md` for full behavior spec
