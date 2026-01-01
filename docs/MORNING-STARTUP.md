# AID Morning Startup - Quick Reference

## 🌅 Before Opening Claude Code

```bash
# 1. Start Docker (if not running)
open -a Docker    # macOS
# or click Docker Desktop icon

# 2. Open Figma (if doing UI work)
# → Enable Dev Mode (Shift+D)
# → Enable MCP server in inspect panel

# 3. Verify (optional)
./scripts/startup-check.sh
```

## ☕ In Claude Code

```
# One command to rule them all:
/good-morning
```

This will:
- ✅ Check Docker
- ✅ Check MCPs (Figma, Jira, GitHub)
- ✅ Load project state
- ✅ Show yesterday's progress
- ✅ Ask where to continue

---

## 🔧 Manual Checks (if needed)

### Docker
```bash
docker ps                    # See running containers
docker-compose up -d         # Start services
```

### Figma MCP
```bash
curl http://127.0.0.1:3845/mcp   # Should respond if active
```
If not working: Open Figma → Dev Mode → Enable MCP

### Jira
```bash
echo $JIRA_API_TOKEN         # Should show token
# or
echo $ATLASSIAN_API_TOKEN
```

### Chrome DevTools
```bash
# Start Chrome with debug port
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# Test connection
curl http://localhost:9222/json
```

---

## 📍 Continuing Work

### If state exists:
```
/good-morning
→ Shows where you left off
→ Pick: continue / new task / update
```

### If no state:
```
/aid-init              # Initialize phases
/phase                 # See current phase
```

### Quick resume:
```
/phase                 # Where am I?
/gate-check            # What's needed?
```

---

## 🚨 Common Issues

| Issue | Solution |
|-------|----------|
| Docker not running | Start Docker Desktop |
| Figma MCP not connecting | Re-enable in Figma Dev Mode |
| Jira not working | Check API token in env |
| "Phase violation" | You're trying to do work from a later phase |

---

## 📋 Daily Flow

```
Morning:
  /good-morning → Check systems → Continue task

During work:
  /phase → See status
  /gate-check → Check phase requirements

End of task:
  Update Jira status
  /phase-approve (if phase complete)
  /phase-advance (move to next)

End of day:
  Commit work
  State is saved in .aid/state.json
```
