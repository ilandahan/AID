# Reflection Agent Integration

## Architecture

Main Claude generates draft → checks conditions → spawns sub-agent → processes response → displays output with QC box.

Sub-agent receives only: draft, phase, criteria. Returns JSON evaluation. No conversation history.

## Task Tool Integration

```
Task(subagent_type: "general-purpose", model: "opus", prompt: <rendered AGENT-PROMPT.md>, description: "Quality evaluation")
```

**Variables to render:**
| Variable | Source |
|----------|--------|
| `{{PHASE_NUMBER}}` | `.aid/state.json` |
| `{{PHASE_NAME}}` | `.aid/state.json` |
| `{{OUTPUT_TYPE}}` | Detected (code, prd, spec) |
| `{{USER_REQUEST_SUMMARY}}` | First 200 chars |
| `{{PHASE_CRITERIA_YAML}}` | `criteria/phase-N-*.yaml` |
| `{{DRAFT_OUTPUT}}` | Output to evaluate |

## Response Processing

- Pass (score >= 7): Display output + QC box
- Fail + revisions < 3: Apply guidance, re-evaluate
- Fail + revisions >= 3: Display with warning
- Error/timeout: Fallback to self-reflection

## State Updates

Write evaluation results to `.aid/context.json` under `reflection_tracking`.

## Fallback

If sub-agent fails, use `.claude/skills/reflection/SKILL.md` for self-evaluation. Show fallback note in QC box.
