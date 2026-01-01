# AID Upgrade Guide

## Upgrade Guide for Existing Users

---

## Understanding the Structure

```
your-workspace/
├── AID/                      ← THE METHODOLOGY (tools, commands, skills)
│   ├── .claude/commands/
│   ├── skills/
│   ├── docs/
│   ├── scripts/
│   └── ...
│
└── my-project/               ← YOUR PROJECT (the code you wrote)
    ├── .aid/                 ← This project's state
    │   ├── state.json
    │   └── context.json
    ├── src/
    ├── docs/
    │   ├── PRD.md
    │   └── TECH-SPEC.md
    └── ...
```

**Important to understand:**
- **AID** = The template/tools (updated from repo)
- **my-project** = Your code (don't touch!)

---

## Scenario 1: Project Inside AID Folder

If your structure looks like this:
```
AID/
├── skills/
├── docs/
├── my-project/        ← Your project inside AID
│   ├── src/
│   └── ...
└── ...
```

### What to do:

```bash
# 1. Backup your project
cp -r AID/my-project ~/backup-my-project

# 2. Extract new ZIP to temp folder
unzip AID-with-tests.zip -d /tmp/aid-update

# 3. Copy only methodology files (not the project!)
cp -r /tmp/aid-update/.claude AID/
cp -r /tmp/aid-update/skills AID/
cp -r /tmp/aid-update/docs AID/
cp -r /tmp/aid-update/scripts AID/
cp -r /tmp/aid-update/templates AID/
cp /tmp/aid-update/CLAUDE.md AID/
cp /tmp/aid-update/README.md AID/
cp /tmp/aid-update/.gitignore AID/

# 4. Your project is untouched!
ls AID/my-project  # Still there
```

### Files safe to copy (won't affect your project):

| Folder/File | What it is | Safe? |
|-------------|------------|-------|
| `.claude/commands/` | Slash commands | Yes |
| `skills/` | Claude skills | Yes |
| `docs/` (AID's) | Methodology documentation | Yes |
| `scripts/` | Scripts | Yes |
| `templates/` | Templates | Yes |
| `CLAUDE.md` | Claude instructions | Yes |
| `.gitignore` | Git ignore | Yes |

### Files NOT to touch:

| Folder/File | What it is | Touch? |
|-------------|------------|--------|
| `my-project/` | Your code | NO! |
| `.aid/` (in project) | Project state | NO! |
| `node_modules/` | Dependencies | NO! |
| `.env` | Environment variables | NO! |

---

## Scenario 2: Project in Separate Folder (Recommended)

If your structure looks like this:
```
~/projects/
├── AID/               ← The methodology
└── my-project/        ← Your project (separate)
```

### What to do:

```bash
# Simply replace the entire AID folder
rm -rf AID
unzip AID-with-tests.zip
mv ai-fullstack-repo AID  # If ZIP contains a wrapper folder

# Your project wasn't affected at all
```

---

## Automatic Upgrade Script

Save this as `upgrade-aid.sh`:

```bash
#!/bin/bash
#
# AID Methodology Upgrade Script
# Safe upgrade that preserves your project files
#

set -e

echo "═══════════════════════════════════════════════════════════"
echo "           AID METHODOLOGY UPGRADE"
echo "═══════════════════════════════════════════════════════════"

# Check if ZIP provided
if [ -z "$1" ]; then
    echo "Usage: ./upgrade-aid.sh <path-to-new-aid.zip>"
    exit 1
fi

ZIP_FILE="$1"
AID_DIR="${2:-.}"  # Default to current directory

echo ""
echo "Upgrading AID in: $AID_DIR"
echo "From ZIP: $ZIP_FILE"
echo ""

# Create backup of current methodology files
BACKUP_DIR="/tmp/aid-backup-$(date +%Y%m%d-%H%M%S)"
echo "Creating backup in $BACKUP_DIR..."
mkdir -p "$BACKUP_DIR"
cp -r "$AID_DIR/.claude" "$BACKUP_DIR/" 2>/dev/null || true
cp -r "$AID_DIR/skills" "$BACKUP_DIR/" 2>/dev/null || true
cp -r "$AID_DIR/docs" "$BACKUP_DIR/" 2>/dev/null || true
cp "$AID_DIR/CLAUDE.md" "$BACKUP_DIR/" 2>/dev/null || true

# Extract new version
TEMP_DIR="/tmp/aid-upgrade-temp"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"
unzip -q "$ZIP_FILE" -d "$TEMP_DIR"

# Find the extracted content (might be in a subdirectory)
if [ -d "$TEMP_DIR/ai-fullstack-repo" ]; then
    SOURCE_DIR="$TEMP_DIR/ai-fullstack-repo"
else
    SOURCE_DIR="$TEMP_DIR"
fi

echo ""
echo "Updating methodology files..."

# Update only methodology files (safe)
echo "  .claude/commands/"
cp -r "$SOURCE_DIR/.claude" "$AID_DIR/"

echo "  skills/"
cp -r "$SOURCE_DIR/skills" "$AID_DIR/"

echo "  docs/ (methodology docs only)"
# Be careful with docs - only copy AID docs, not project docs
for doc in PHASE-GATES.md MORNING-STARTUP.md WORK-CONTEXT-TRACKER.md TEST-SCENARIOS.md; do
    if [ -f "$SOURCE_DIR/docs/$doc" ]; then
        cp "$SOURCE_DIR/docs/$doc" "$AID_DIR/docs/"
    fi
done

echo "  scripts/"
cp -r "$SOURCE_DIR/scripts" "$AID_DIR/"

echo "  templates/"
cp -r "$SOURCE_DIR/templates" "$AID_DIR/"

echo "  CLAUDE.md"
cp "$SOURCE_DIR/CLAUDE.md" "$AID_DIR/"

echo "  .gitignore"
cp "$SOURCE_DIR/.gitignore" "$AID_DIR/"

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "           UPGRADE COMPLETE"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Backup saved to: $BACKUP_DIR"
echo ""
echo "New features available:"
echo "  /good-morning  - Morning startup routine"
echo "  /context       - Show work context"
echo "  /aid-test      - Run methodology tests"
echo "  /gate-check    - Check phase requirements"
echo ""
echo "Your project files were NOT touched."
echo ""
```

### How to use:

```bash
chmod +x upgrade-aid.sh
./upgrade-aid.sh ~/Downloads/AID-with-tests.zip ./AID
```

---

## Initializing Phase Gates in Existing Project

After the update, if your project isn't initialized with Phase Gates yet:

```bash
cd my-project

# Run Claude Code
claude

# Initialize (creates .aid/state.json and .aid/context.json)
/aid-init
```

**If you already have a PRD and Tech Spec:**

```bash
# Claude will ask what phase you're in
# Tell it: "I already have a PRD and Tech Spec, I'm in Phase 4 Development"
```

Claude will adjust state.json to the correct phase.

---

## Recommended Work Structure

```
~/dev/
├── AID/                          ← Clone of the repo (methodology)
│   ├── .claude/commands/
│   ├── skills/
│   ├── docs/
│   └── ...
│
└── projects/
    ├── project-a/                ← Project 1
    │   ├── .aid/                 ← This project's state
    │   ├── src/
    │   └── ...
    │
    └── project-b/                ← Project 2
        ├── .aid/                 ← This project's state
        └── ...
```

### Symbolic Links (optional - advanced)

```bash
# Instead of copying, create links
cd my-project
ln -s ../AID/.claude .claude
ln -s ../AID/skills skills
```

This way when you update AID, all projects get the update automatically.

---

## FAQ

### Q: What happens to my .aid/state.json?
**A:** Not touched! It's in your project folder, not in the AID folder.

### Q: What happens to the code I wrote?
**A:** Not touched! Only the tools (skills, commands) are updated.

### Q: How do I know what phase I'm in?
**A:** Run `/phase` or look at .aid/state.json

### Q: What if I have local changes to skills?
**A:** They will be overwritten. If you made custom changes, back them up first.

---

## Verification After Update

```bash
# Verify everything works
./scripts/test-methodology.sh

# Check commands are available
claude
/good-morning  # Should work
/phase         # Should show your phase
```

---

## Summary - What's Safe and What's Not

| Action | Safe? |
|--------|-------|
| Copy `.claude/commands/` | Yes |
| Copy `skills/` | Yes |
| Copy `scripts/` | Yes |
| Copy `templates/` | Yes |
| Copy `CLAUDE.md` | Yes |
| Delete your project | NO |
| Delete project's `.aid/` | NO |
| Delete `src/` | NO |
| Delete `node_modules/` | Warning (can restore with npm install) |
