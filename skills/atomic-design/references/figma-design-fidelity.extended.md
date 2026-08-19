# Figma Design Fidelity - Zero Deviation Policy

## 🚨 הכלל המרכזי: אין סטייה מהעיצוב

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   🔒 FIGMA IS THE SINGLE SOURCE OF TRUTH                                │
│                                                                         │
│   כל ערך עיצובי חייב להגיע ישירות מ-Figma.                              │
│   אין להמציא, לנחש, לעגל, או "לשפר" שום ערך.                            │
│                                                                         │
│   If Figma says 12px → Code says 12px                                   │
│   If Figma says #3B82F6 → Code says #3B82F6                             │
│   If Figma says 400 weight → Code says 400 weight                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## מטרת המסמך

מסמך זה מגדיר את הכללים לשמירה על נאמנות מוחלטת לעיצוב ב-Figma.
**אין חריגות** - כל סטייה מהעיצוב נחשבת כבאג קריטי.

---

## Extraction Before Implementation (חובה)

### סדר העבודה הנכון

```
┌──────────────────────────────────────────────────────────────┐
│  1. STOP - אל תכתוב שום קוד עיצובי                           │
│           │                                                  │
│           ▼                                                  │
│  2. EXTRACT - חלץ את הערכים מ-Figma                          │
│           │                                                  │
│           ▼                                                  │
│  3. DOCUMENT - תעד את הערכים שחולצו                          │
│           │                                                  │
│           ▼                                                  │
│  4. IMPLEMENT - ממש בדיוק לפי הערכים                         │
│           │                                                  │
│           ▼                                                  │
│  5. VERIFY - השווה את התוצאה ל-Figma                         │
└──────────────────────────────────────────────────────────────┘
```

### מה לחלץ מ-Figma

| קטגוריה | פרטים לחילוץ | דוגמה |
|---------|--------------|-------|
| **מידות** | Width, Height | `width: 320px`, `height: 48px` |
| **ריווח פנימי** | Padding (all sides) | `padding: 12px 24px` |
| **ריווח חיצוני** | Margin, Gap | `gap: 16px` |
| **צבעים** | Fill, Stroke, Background | `background: #3B82F6` |
| **טיפוגרפיה** | Font, Size, Weight, Line-height | `font-size: 16px; font-weight: 500` |
| **אפקטים** | Shadow, Blur, Opacity | `box-shadow: 0 4px 6px rgba(0,0,0,0.1)` |
| **גבולות** | Border radius, Border width | `border-radius: 8px` |
| **Layout** | Auto-layout direction, alignment | `flex-direction: column` |

---

## Figma MCP Commands - חילוץ ערכים

### לפני כתיבת כל קומפוננטה

```typescript
// 1. קבל את המפרט המלא של האלמנט
const nodeSpec = await figma.get_node(file_key, node_id);

// 2. חלץ ערכים ספציפיים
// Colors
fill: nodeSpec.fills[0].color  // #RRGGBB
stroke: nodeSpec.strokes[0].color

// Dimensions
width: nodeSpec.absoluteBoundingBox.width
height: nodeSpec.absoluteBoundingBox.height

// Auto-layout (padding, gap)
paddingTop: nodeSpec.paddingTop
paddingRight: nodeSpec.paddingRight
paddingBottom: nodeSpec.paddingBottom
paddingLeft: nodeSpec.paddingLeft
itemSpacing: nodeSpec.itemSpacing  // gap

// Typography
fontFamily: nodeSpec.style.fontFamily
fontSize: nodeSpec.style.fontSize
fontWeight: nodeSpec.style.fontWeight
lineHeight: nodeSpec.style.lineHeightPx

// Effects
cornerRadius: nodeSpec.cornerRadius
effects: nodeSpec.effects  // shadows, blurs
```

### דוגמה מלאה: חילוץ Button מ-Figma

```
Figma Selection: "Button/Primary/Default"

Extracted Values:
├── Dimensions
│   ├── width: auto (hug contents)
│   └── height: 48px
│
├── Padding
│   ├── paddingTop: 12px
│   ├── paddingRight: 24px
│   ├── paddingBottom: 12px
│   └── paddingLeft: 24px
│
├── Visual
│   ├── background: #3B82F6
│   ├── borderRadius: 8px
│   └── shadow: none
│
├── Typography
│   ├── fontFamily: "Inter"
│   ├── fontSize: 16px
│   ├── fontWeight: 500
│   ├── lineHeight: 24px
│   └── color: #FFFFFF
│
└── States (from variants)
    ├── hover: background: #2563EB
    ├── active: background: #1D4ED8
    └── disabled: background: #E5E7EB, color: #9CA3AF
```

---

## Verification Checklist - בדיקת התאמה

### לפני Delivery של כל קומפוננטה

```markdown
## Figma Fidelity Verification

Component: [Button/Primary]
Figma Frame: [Link to Figma frame]
Date Extracted: [YYYY-MM-DD]

### Dimensions ✓
- [ ] Width matches Figma: ___px / auto
- [ ] Height matches Figma: ___px / auto
- [ ] Min/Max constraints match

### Spacing ✓
- [ ] Padding-top: ___px
- [ ] Padding-right: ___px
- [ ] Padding-bottom: ___px
- [ ] Padding-left: ___px
- [ ] Gap (if applicable): ___px

### Colors ✓
- [ ] Background: #______
- [ ] Text color: #______
- [ ] Border color: #______
- [ ] Hover state colors match
- [ ] Disabled state colors match

### Typography ✓
- [ ] Font family: ______
- [ ] Font size: ___px
- [ ] Font weight: ___
- [ ] Line height: ___px / ___ (ratio)
- [ ] Letter spacing: ___

### Effects ✓
- [ ] Border radius: ___px
- [ ] Box shadow: ______
- [ ] Opacity: ___%

### Responsive ✓
- [ ] Mobile layout matches Figma mobile frame
- [ ] Tablet layout matches Figma tablet frame
- [ ] Desktop layout matches Figma desktop frame
```

---

## Common Mistakes to Avoid - טעויות נפוצות

### ❌ טעות: עיגול ערכים

```css
/* Figma shows: 13px */

/* ❌ WRONG - עיגלת לערך "נוח" */
padding: 12px;  /* Changed from 13px */

/* ✅ CORRECT - הערך המדויק */
padding: 13px;  /* Exact Figma value */
```

### ❌ טעות: "שיפור" צבעים

```css
/* Figma shows: #3B82F6 */

/* ❌ WRONG - "שיפרת" את הצבע */
background: #3F85F7;  /* "Slightly better" */

/* ✅ CORRECT - הצבע המדויק */
background: #3B82F6;  /* Exact Figma value */
```

### ❌ טעות: החלטות עיצוביות עצמאיות

```css
/* Figma doesn't show a shadow */

/* ❌ WRONG - הוספת אפקט "כי זה נראה יותר טוב" */
box-shadow: 0 2px 4px rgba(0,0,0,0.1);

/* ✅ CORRECT - אם אין ב-Figma, אין בקוד */
box-shadow: none;
```

### ❌ טעות: התאמות responsive "הגיוניות"

```css
/* Figma mobile shows: padding: 16px */

/* ❌ WRONG - "הגיוני" להקטין ל-12px במובייל */
@media (max-width: 768px) {
  padding: 12px;  /* "Logical" adjustment */
}

/* ✅ CORRECT - בדוק מה Figma Mobile frame מראה */
@media (max-width: 768px) {
  padding: 16px;  /* Exact Figma mobile value */
}
```

---

## Token Synchronization - סנכרון טוקנים

### כאשר Figma מתעדכן

```
Scenario: Designer changed primary color
Old: #3B82F6
New: #2563EB

Action Flow:
1. Detect change (manual check or webhook)
2. Update tokens/colors.json
   - semantic.primary: "#2563EB"
3. Regenerate CSS variables
4. Verify all components still match Figma
5. Commit: "sync: Update primary color from Figma [#2563EB]"
```

### Token File Update Process

```json
// tokens/colors.json - BEFORE
{
  "semantic": {
    "primary": "#3B82F6"
  }
}

// tokens/colors.json - AFTER (from Figma update)
{
  "semantic": {
    "primary": "#2563EB"
  }
}
```

---

## Visual Regression Testing

### Automated Comparison

```typescript
// Using visual regression tool (e.g., Percy, Chromatic)

describe('Button Component', () => {
  it('matches Figma design - Primary variant', () => {
    render(<Button variant="primary">Click me</Button>);

    // Visual snapshot comparison
    expect(screen).toMatchFigmaDesign('button-primary');
  });

  it('matches Figma design - All states', () => {
    const states = ['default', 'hover', 'active', 'disabled'];

    states.forEach(state => {
      expect(renderButtonState(state)).toMatchFigmaDesign(`button-${state}`);
    });
  });
});
```

### Manual Comparison Technique

```
1. Screenshot from Figma (Cmd/Ctrl + Shift + C on selected frame)
2. Screenshot from browser (same dimensions)
3. Use diff tool (e.g., Figma plugin "Design Compare")
4. Difference should be 0% (pixel-perfect)
```

---

## Handling Figma Ambiguities

### When Figma Is Unclear

```
Situation: Figma shows a value that seems inconsistent

DO NOT: Make assumptions or "fix" it yourself

DO: Ask the designer
    "In Figma frame [X], the button padding is 13px.
    Is this intentional or should it be 12px to match the 4px grid?"

ONLY AFTER designer confirms → Update Figma OR implement as-is
```

### When Values Seem "Wrong"

```
Situation: Figma shows font-weight: 450 (non-standard value)

DO NOT: Change to nearest standard value (400 or 500)

DO:
1. Check if Inter Variable font supports weight 450
2. If yes → Implement exactly: font-weight: 450
3. If no → Ask designer for fallback value
```

---

## Summary: The Golden Rules

| כלל | פירוש |
|-----|-------|
| **1. Extract First** | לעולם אל תתחיל לקודד לפני שחילצת ערכים מ-Figma |
| **2. No Interpretation** | אין לפרש - רק להעתיק ערכים כמו שהם |
| **3. Document Everything** | תעד כל ערך שחולץ וממתי |
| **4. Verify Always** | בדוק התאמה ויזואלית לפני delivery |
| **5. Ask When Unsure** | אם משהו לא ברור - שאל את המעצב |
| **6. Figma Wins** | אם יש סתירה - Figma תמיד צודק |

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│  FIGMA FIDELITY QUICK CHECK                                     │
│                                                                 │
│  Before writing any style:                                      │
│  □ Did I extract the value from Figma?                          │
│  □ Is the value exactly as shown (no rounding)?                 │
│  □ Did I check all states (hover, active, disabled)?            │
│  □ Did I check responsive variations?                           │
│                                                                 │
│  Before delivery:                                               │
│  □ Visual comparison shows 0% difference                        │
│  □ All breakpoints match Figma frames                           │
│  □ Token values are up-to-date with Figma                       │
│  □ Figma link documented in code/commit                         │
└─────────────────────────────────────────────────────────────────┘
```
