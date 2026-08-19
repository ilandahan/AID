# Design Deviation Rules - Zero Tolerance Policy

## 🚫 מדיניות אפס סטיות

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   ❌ NO CREATIVE FREEDOM IN IMPLEMENTATION                              │
│                                                                         │
│   המפתח הוא לא מעצב.                                                    │
│   תפקיד המפתח הוא לתרגם את העיצוב לקוד - לא לשפר אותו.                  │
│                                                                         │
│   "אני חושב שזה ייראה יותר טוב ככה" = ❌ FORBIDDEN                       │
│   "Figma מראה X, אז הקוד יהיה X" = ✅ CORRECT                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## סוגי סטיות אסורות

### 1. סטיות "אסתטיות"

| פעולה אסורה | דוגמה | למה אסור |
|-------------|-------|----------|
| שינוי צבעים | `#3B82F6` → `#3F85F7` | המעצב בחר בצבע ספציפי מסיבה |
| עיגול ערכים | `13px` → `12px` | "נוח יותר" לא רלוונטי |
| הוספת אפקטים | הוספת shadow שלא קיים | זו החלטה עיצובית |
| שינוי fonts | Inter → System fonts | פוגע בזהות המותג |
| שינוי spacing | `24px` → `20px` | משבש את הריתמוס הויזואלי |

### 2. סטיות "טכניות"

| פעולה אסורה | דוגמה | הפתרון הנכון |
|-------------|-------|--------------|
| "אופטימיזציה" של ערכים | שימוש ב-rem במקום px כשהמעצב ציין px | שאל את המעצב איזו יחידה מועדפת |
| "סטנדרטיזציה" | שינוי font-weight 450 ל-500 | בדוק אם הפונט תומך ב-450 |
| "תיקון" inconsistencies | יישור padding לא אחיד | דווח למעצב - אל תתקן לבד |

### 3. סטיות "responsive"

| פעולה אסורה | דוגמה | הפתרון הנכון |
|-------------|-------|--------------|
| המצאת breakpoints | הוספת breakpoint ב-480px | בדוק אילו breakpoints מוגדרים ב-Figma |
| "התאמות הגיוניות" | הקטנת padding במובייל | חלץ ערכים מ-Figma Mobile frame |
| שינוי layout | שינוי מ-grid ל-flex | ממש את ה-layout כפי שנראה ב-Figma |

---

## תהליך עבודה: כאשר משהו "לא נראה נכון"

```
┌─────────────────────────────────────────────────────────────────┐
│  WORKFLOW: כאשר נראה לך שמשהו "שגוי" ב-Figma                     │
│                                                                 │
│  1. STOP - אל תשנה שום דבר                                      │
│        │                                                        │
│        ▼                                                        │
│  2. DOCUMENT - צלם את מה שנראה לך בעייתי                        │
│        │                                                        │
│        ▼                                                        │
│  3. ASK - שאל את המעצב                                          │
│        │   "שמתי לב שב-[frame] ה-padding הוא 13px.              │
│        │    זה מכוון או צריך להיות 12px?"                       │
│        │                                                        │
│        ▼                                                        │
│  4. WAIT - המתן לתשובה לפני שממשיך                               │
│        │                                                        │
│        ▼                                                        │
│  5. IMPLEMENT - ממש לפי ההנחיה של המעצב                         │
│        │                                                        │
│        ▼                                                        │
│  6. DOCUMENT - תעד את ההחלטה בקוד ובמערכת                       │
└─────────────────────────────────────────────────────────────────┘
```

### תבנית שאלה למעצב

```markdown
## Design Clarification Request

**Component:** [Button/Primary]
**Figma Frame:** [link]
**Property:** padding-top
**Current Value:** 13px
**Expected Value (Grid-aligned):** 12px

**Question:**
האם ה-13px מכוון או שמדובר בטעות?
אם מכוון - אוודא שהטוקן יהיה 13px.
אם טעות - אעדכן את הקוד אחרי שתתקן ב-Figma.

**Screenshot:** [attached]
```

---

## Exception Handling - מתי מותר לחרוג?

### התשובה הקצרה: כמעט אף פעם

### החריגים היחידים המותרים:

#### 1. Bug טכני בפלטפורמה

```css
/* Figma shows: backdrop-filter: blur(10px) */
/* Safari bug: requires -webkit- prefix */

/* ✅ ALLOWED - תוספת טכנית לא ויזואלית */
.modal {
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px); /* Safari support */
}
```

#### 2. Accessibility Override (נדיר מאוד)

```css
/* Figma shows: color contrast 3.5:1 */
/* WCAG AA requires: 4.5:1 minimum */

/* ❌ WRONG - לשנות לבד */
color: #000;  /* "Fixed" contrast */

/* ✅ CORRECT - לדווח למעצב */
/*
 * ACCESSIBILITY ISSUE REPORTED
 * Figma contrast: 3.5:1
 * Required: 4.5:1
 * Awaiting designer update
 * Jira: DESIGN-123
 */
color: var(--color-text-secondary);  /* Current Figma value */
```

#### 3. Missing State ב-Figma

```tsx
/* Figma shows: Button without focus state */

/* ❌ WRONG - להמציא focus state */
&:focus {
  outline: 2px solid blue;  /* Invented */
}

/* ✅ CORRECT - בקש מהמעצב להוסיף */
/*
 * TODO: Focus state not defined in Figma
 * Requested from designer - Jira: DESIGN-124
 * Using browser default until designed
 */
```

---

## Documentation Requirements - תיעוד חובה

### כל קומפוננטה חייבת לכלול:

```tsx
/**
 * Button Component
 *
 * @figma https://figma.com/file/xxx/Design-System?node-id=123
 * @extracted 2024-01-15
 * @designer Sarah Cohen
 *
 * Design Specs:
 * - Height: 48px (fixed)
 * - Padding: 12px 24px
 * - Border-radius: 8px
 * - Font: Inter 16px/500
 *
 * All values extracted from Figma - DO NOT MODIFY without designer approval.
 */
```

### בכל CSS Module:

```css
/**
 * Button Styles
 *
 * Source: Figma Design System v2.1
 * Frame: Components/Button/Primary
 * Last synced: 2024-01-15
 *
 * ⚠️ WARNING: All values are from Figma.
 * Do not modify without updating Figma first.
 */

.button {
  /* From Figma: padding */
  padding: 12px 24px;  /* Figma: paddingTop/Bottom: 12, paddingLeft/Right: 24 */

  /* From Figma: background */
  background: var(--color-primary);  /* Figma: fill #3B82F6 */

  /* From Figma: border-radius */
  border-radius: 8px;  /* Figma: cornerRadius: 8 */
}
```

---

## Code Review Checklist - בדיקה בקוד רביו

### מה לבדוק:

```markdown
## Design Fidelity Review

### Pre-merge Checklist:

1. **Figma Link Verification**
   - [ ] Figma link exists in component documentation
   - [ ] Link is accessible and correct

2. **Value Extraction**
   - [ ] All CSS values have Figma source comment
   - [ ] No "magic numbers" without source

3. **Token Usage**
   - [ ] Uses design tokens (not hardcoded values)
   - [ ] Token values match current Figma

4. **Visual Comparison**
   - [ ] Screenshot comparison shows match
   - [ ] All states verified (hover, active, disabled, focus)
   - [ ] Responsive breakpoints verified

5. **No Unauthorized Changes**
   - [ ] No "improved" colors
   - [ ] No "rounded" values
   - [ ] No added effects not in Figma
   - [ ] No removed properties from Figma

### Red Flags to Block PR:

❌ Hardcoded color: `color: #3B82F6;` instead of `var(--color-primary)`
❌ Rounded value: `padding: 12px` when Figma shows `13px`
❌ Missing Figma reference
❌ "Looks better this way" in commit message
❌ Unexplained deviation from design system
```

---

## Consequences of Deviation - השלכות

### למה חשוב לשמור על נאמנות?

```
1. CONSISTENCY
   └─► כל סטייה קטנה × מספר מפתחים × זמן = קאוס ויזואלי

2. TRUST
   └─► המעצב צריך לסמוך שמה שהוא מעצב - יופיע בפרודקשן

3. MAINTENANCE
   └─► כאשר כולם מממשים בדיוק מ-Figma, קל לעדכן

4. SCALABILITY
   └─► מערכת עיצוב עובדת רק כשכולם מקפידים עליה
```

### מה קורה כשיש סטיות:

```
Developer A: שינה padding מ-12px ל-10px כי "נראה צפוף"
Developer B: שינה את אותו כפתור ל-14px כי "צריך יותר מרווח"
Developer C: השאיר 12px כמו ב-Figma

תוצאה: 3 גרסאות שונות של אותו כפתור באפליקציה
```

---

## Summary: The Rules

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   THE DEVIATION RULES                                           │
│                                                                 │
│   1. אל תשנה - ממש בדיוק מה ש-Figma מראה                        │
│                                                                 │
│   2. אל תשפר - "שיפורים" הם סטיות                               │
│                                                                 │
│   3. אל תנחש - אם לא ברור, שאל                                  │
│                                                                 │
│   4. אל תעגל - 13px זה 13px, לא 12px                            │
│                                                                 │
│   5. אל תוסיף - אם זה לא ב-Figma, זה לא בקוד                    │
│                                                                 │
│   6. תעד - כל ערך צריך מקור מ-Figma                             │
│                                                                 │
│   7. אמת - בדוק ויזואלית לפני delivery                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference: What To Do

| מצב | פעולה |
|-----|-------|
| "הערך נראה לי מוזר" | שאל את המעצב |
| "אני חושב שזה ייראה יותר טוב" | לא רלוונטי - ממש מ-Figma |
| "המעצב טעה" | דווח - אל תתקן לבד |
| "חסר state ב-Figma" | בקש מהמעצב להוסיף |
| "לא בטוח איזה ערך לקחת" | שאל את המעצב |
| "רוצה לשנות משהו" | פתח בקשה למעצב לעדכן ב-Figma קודם |
