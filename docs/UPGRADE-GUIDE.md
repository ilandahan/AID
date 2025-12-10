# AID Upgrade Guide

## מדריך עדכון למשתמשים קיימים

---

## הבנת המבנה

```
your-workspace/
├── AID/                      ← ה-METHODOLOGY (כלים, פקודות, skills)
│   ├── .claude/commands/
│   ├── skills/
│   ├── docs/
│   ├── scripts/
│   └── ...
│
└── my-project/               ← הפרויקט שלך (הקוד שכתבת)
    ├── .aid/                 ← State של הפרויקט
    │   ├── state.json
    │   └── context.json
    ├── src/
    ├── docs/
    │   ├── PRD.md
    │   └── TECH-SPEC.md
    └── ...
```

**חשוב להבין:**
- **AID** = התבנית/הכלים (מתעדכן מהריפו)
- **my-project** = הקוד שלך (לא נוגעים!)

---

## תרחיש 1: הפרויקט בתוך תיקיית AID

אם המבנה שלך נראה ככה:
```
AID/
├── skills/
├── docs/
├── my-project/        ← הפרויקט שלך בתוך AID
│   ├── src/
│   └── ...
└── ...
```

### מה לעשות:

```bash
# 1. גבה את הפרויקט שלך
cp -r AID/my-project ~/backup-my-project

# 2. פרוס את ה-ZIP החדש לתיקייה זמנית
unzip AID-with-tests.zip -d /tmp/aid-update

# 3. העתק רק את קבצי ה-methodology (לא את הפרויקט!)
cp -r /tmp/aid-update/.claude AID/
cp -r /tmp/aid-update/skills AID/
cp -r /tmp/aid-update/docs AID/
cp -r /tmp/aid-update/scripts AID/
cp -r /tmp/aid-update/templates AID/
cp /tmp/aid-update/CLAUDE.md AID/
cp /tmp/aid-update/README.md AID/
cp /tmp/aid-update/.gitignore AID/

# 4. הפרויקט שלך לא נפגע!
ls AID/my-project  # עדיין שם
```

### קבצים שבטוח להעתיק (לא יפגעו בפרויקט):

| תיקייה/קובץ | מה זה | בטוח? |
|-------------|-------|-------|
| `.claude/commands/` | פקודות slash | ✅ כן |
| `skills/` | Claude skills | ✅ כן |
| `docs/` (של AID) | דוקומנטציה של המתודולוגיה | ✅ כן |
| `scripts/` | סקריפטים | ✅ כן |
| `templates/` | תבניות | ✅ כן |
| `CLAUDE.md` | הוראות ל-Claude | ✅ כן |
| `.gitignore` | Git ignore | ✅ כן |

### קבצים שלא לגעת בהם:

| תיקייה/קובץ | מה זה | לגעת? |
|-------------|-------|-------|
| `my-project/` | הקוד שלך | ❌ לא! |
| `.aid/` (בפרויקט) | State של הפרויקט | ❌ לא! |
| `node_modules/` | Dependencies | ❌ לא! |
| `.env` | משתני סביבה | ❌ לא! |

---

## תרחיש 2: הפרויקט בתיקייה נפרדת (מומלץ)

אם המבנה שלך נראה ככה:
```
~/projects/
├── AID/               ← המתודולוגיה
└── my-project/        ← הפרויקט שלך (נפרד)
```

### מה לעשות:

```bash
# פשוט החלף את כל תיקיית AID
rm -rf AID
unzip AID-with-tests.zip
mv ai-fullstack-repo AID  # אם ה-ZIP מכיל תיקייה עוטפת

# הפרויקט שלך בכלל לא הושפע
```

---

## סקריפט עדכון אוטומטי

שמור את זה כ-`upgrade-aid.sh`:

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
echo "  ✓ .claude/commands/"
cp -r "$SOURCE_DIR/.claude" "$AID_DIR/"

echo "  ✓ skills/"
cp -r "$SOURCE_DIR/skills" "$AID_DIR/"

echo "  ✓ docs/ (methodology docs only)"
# Be careful with docs - only copy AID docs, not project docs
for doc in PHASE-GATES.md MORNING-STARTUP.md WORK-CONTEXT-TRACKER.md TEST-SCENARIOS.md; do
    if [ -f "$SOURCE_DIR/docs/$doc" ]; then
        cp "$SOURCE_DIR/docs/$doc" "$AID_DIR/docs/"
    fi
done

echo "  ✓ scripts/"
cp -r "$SOURCE_DIR/scripts" "$AID_DIR/"

echo "  ✓ templates/"
cp -r "$SOURCE_DIR/templates" "$AID_DIR/"

echo "  ✓ CLAUDE.md"
cp "$SOURCE_DIR/CLAUDE.md" "$AID_DIR/"

echo "  ✓ .gitignore"
cp "$SOURCE_DIR/.gitignore" "$AID_DIR/"

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "           ✅ UPGRADE COMPLETE"
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

### איך להשתמש:

```bash
chmod +x upgrade-aid.sh
./upgrade-aid.sh ~/Downloads/AID-with-tests.zip ./AID
```

---

## אתחול Phase Gates בפרויקט קיים

אחרי העדכון, אם הפרויקט שלך עדיין לא מאותחל עם Phase Gates:

```bash
cd my-project

# הרץ את Claude Code
claude

# אתחל (יצור .aid/state.json ו-.aid/context.json)
/aid-init
```

**אם כבר יש לך PRD ו-Tech Spec:**

```bash
# Claude ישאל באיזה שלב אתה
# תגיד לו: "יש לי כבר PRD ו-Tech Spec, אני בשלב 4 Development"
```

Claude יתאים את ה-state.json לשלב הנכון.

---

## מבנה עבודה מומלץ

```
~/dev/
├── AID/                          ← Clone של הריפו (methodology)
│   ├── .claude/commands/
│   ├── skills/
│   ├── docs/
│   └── ...
│
└── projects/
    ├── project-a/                ← פרויקט 1
    │   ├── .aid/                 ← State של פרויקט זה
    │   ├── src/
    │   └── ...
    │
    └── project-b/                ← פרויקט 2
        ├── .aid/                 ← State של פרויקט זה
        └── ...
```

### Symbolic Links (אופציונלי - מתקדם)

```bash
# במקום להעתיק, צור קישורים
cd my-project
ln -s ../AID/.claude .claude
ln -s ../AID/skills skills
```

כך כשתעדכן את AID, כל הפרויקטים יקבלו את העדכון אוטומטית.

---

## שאלות נפוצות

### ש: מה קורה ל-.aid/state.json שלי?
**ת:** לא נוגעים בו! הוא בתיקיית הפרויקט שלך, לא בתיקיית AID.

### ש: מה קורה לקוד שכתבתי?
**ת:** לא נוגעים בו! רק מעדכנים את הכלים (skills, commands).

### ש: איך אני יודע באיזה שלב אני?
**ת:** הרץ `/phase` או תסתכל ב-.aid/state.json

### ש: מה אם יש לי שינויים מקומיים ב-skills?
**ת:** הם יידרסו. אם עשית התאמות אישיות, גבה אותן קודם.

---

## בדיקה אחרי עדכון

```bash
# וודא שהכל עובד
./scripts/test-methodology.sh

# בדוק שהפקודות זמינות
claude
/good-morning  # צריך לעבוד
/phase         # צריך להראות את השלב שלך
```

---

## סיכום - מה בטוח ומה לא

| פעולה | בטוח? |
|-------|-------|
| העתקת `.claude/commands/` | ✅ |
| העתקת `skills/` | ✅ |
| העתקת `scripts/` | ✅ |
| העתקת `templates/` | ✅ |
| העתקת `CLAUDE.md` | ✅ |
| מחיקת הפרויקט שלך | ❌ |
| מחיקת `.aid/` של הפרויקט | ❌ |
| מחיקת `src/` | ❌ |
| מחיקת `node_modules/` | ⚠️ (אפשר לשחזר עם npm install) |
