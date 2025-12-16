# /aid end

End current phase and collect feedback.

## Purpose

Complete the current phase, collect user feedback for the learning system.

## Flow

1. **Summarize Work**:
   ```
   Phase Summary: Development
   
   Work completed:
   - Implemented user authentication
   - Added API endpoints for login/logout
   - Created unit tests (85% coverage)
   
   Duration: 3h 20m
   ```

2. **Ask for Rating**:
   ```
   How would you rate this session? (1-5)
   
   1 = Poor - Many issues
   2 = Below average - Some problems
   3 = Average - Met basic expectations
   4 = Good - Exceeded expectations
   5 = Excellent - Outstanding results
   ```

3. **Ask What Worked**:
   ```
   What worked well in this session?
   (Examples: clear explanations, good code structure, helpful suggestions)
   ```

4. **Ask What Could Improve**:
   ```
   What could be improved?
   (Examples: more detail needed, different approach, missing context)
   ```

5. **Save Feedback**:
   Save to `~/.aid/feedback/pending/{timestamp}.json`:
   ```json
   {
     "timestamp": "2024-01-15T12:20:00Z",
     "role": "developer",
     "phase": "development",
     "rating": 4,
     "worked_well": "Clear code structure, good test coverage",
     "to_improve": "Could explain architectural decisions more",
     "duration_minutes": 200
   }
   ```

6. **Confirm & Next**:
   ```
   ✅ Feedback saved
   
   Options:
   1. Continue to next phase (Tech Spec → Development)
   2. Start new session with different role/phase
   3. End for now
   ```

## Usage

```
/aid end
```

## Notes

- Feedback is stored locally, never sent externally
- Need 3+ feedback items before `/aid improve` works
- Feedback is anonymized before any analysis
- See `memory-system/docs/AGENT.md#phase-gate` for details
