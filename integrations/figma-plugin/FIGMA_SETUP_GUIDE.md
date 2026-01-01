# 🎨 הגדרות פיגמה להעשרה אוטומטית

מדריך להגדרת קומפוננטות בפיגמה כך שהפלאגין יחלץ את המידע באופן אוטומטי.

---

## 📋 מה הפלאגין מחלץ אוטומטית

| שדה | מקור בפיגמה | דוגמה |
|-----|-------------|-------|
| `componentId` | `node.id` | `1:234` |
| `componentName` | `node.name` | `Button / Primary / Large` |
| `displayName` | נוצר מהשם | `ButtonPrimary` |
| `fills/colors` | `node.fills` | `#3b82f6` |
| `strokes/borders` | `node.strokes` | `#e5e7eb` |
| `padding` | Auto Layout | `12px 24px` |
| `gap` | Auto Layout `itemSpacing` | `8px` |
| `borderRadius` | `node.cornerRadius` | `8px` |
| `fontSize` | TextNode | `14px` |
| `fontWeight` | TextNode | `600` |
| `shadows` | `node.effects` | `0 1px 2px rgba(0,0,0,0.05)` |
| `variants` | Component Set Properties | `primary, secondary, ghost` |
| `states` | Variant Property "State" | `hover, active, disabled` |

---

## ⚙️ הגדרות נדרשות בפיגמה

### 1️⃣ שם הקומפוננטה (חובה)

```
📁 Layers Panel
└── 🔷 Button / Primary / Large    ← השם הזה
```

**פורמט מומלץ:**
```
Category / Variant / Size
```

**דוגמאות טובות:**
- ✅ `Button / Primary / Large`
- ✅ `Input / Text / Default`
- ✅ `Card / Product / Horizontal`
- ✅ `Modal / Confirmation / Small`

**דוגמאות גרועות:**
- ❌ `button 1`
- ❌ `Component 23`
- ❌ `Frame 456`

---

### 2️⃣ Variant Properties (חובה לComponent Sets)

```
📁 Component Set: Button
├── 🔹 Type = Primary
├── 🔹 Size = Large  
└── 🔹 State = Default
```

**Properties מומלצים:**

| Property | ערכים | הופך ל... |
|----------|-------|-----------|
| `Type` או `Variant` | `Primary, Secondary, Ghost, Danger` | `variant` prop |
| `Size` | `SM, MD, LG` או `Small, Medium, Large` | `size` prop |
| `State` | `Default, Hover, Active, Focus, Disabled` | CSS states |

**איך מוסיפים:**
1. בחר את ה-Component Set
2. בפאנל ימין → Properties
3. לחץ ➕ → Add variant property

---

### 3️⃣ Auto Layout (מאוד מומלץ)

```
┌─────────────────────────────────┐
│  ←16px→  [Icon] ←8px→ Label  ←16px→  │
│     ↑                           │
│   12px                          │
│     ↓                           │
└─────────────────────────────────┘
```

**הגדרות שמחולצות:**

| הגדרה בפיגמה | מה מחולץ | CSS Variable |
|--------------|----------|--------------|
| Padding Left/Right | `padding-inline` | `--spacing-X-padding-x` |
| Padding Top/Bottom | `padding-block` | `--spacing-X-padding-y` |
| Item Spacing | `gap` | `--spacing-X-gap` |
| Direction | `flex-direction` | - |

---

### 4️⃣ שמות Layers (מומלץ)

הפלאגין מזהה props לפי שמות ה-layers:

```
📁 Button
├── 📝 Label          → label: string (prop)
├── 🖼️ Icon           → icon: ReactNode (prop)  
├── 📝 Helper Text    → helperText: string (prop)
└── 📁 Content        → children: ReactNode (prop)
```

**שמות מזוהים אוטומטית:**

| שם Layer | סוג Prop | תיאור |
|----------|----------|-------|
| `Label`, `Title`, `Text` | `string` | טקסט ראשי |
| `Subtitle`, `Description` | `string` | טקסט משני |
| `Placeholder` | `string` | placeholder לinput |
| `Helper`, `Helper Text` | `string` | טקסט עזרה |
| `Error`, `Error Text` | `string` | הודעת שגיאה |
| `Icon`, `Leading Icon` | `ReactNode` | אייקון |
| `Trailing Icon` | `ReactNode` | אייקון בסוף |
| `Content`, `Children` | `ReactNode` | תוכן דינמי |

---

### 5️⃣ Component Properties (אופציונלי - Figma הכי חדש)

```
📁 Component Properties
├── 🔘 Show Icon (Boolean) = true/false
├── 📝 Label (Text) = "Click me"
└── 🔄 Icon (Instance Swap) = icon-check
```

**סוגי Properties:**

| סוג | שימוש | הופך ל... |
|-----|-------|-----------|
| **Boolean** | הצג/הסתר אלמנט | `boolean` prop |
| **Text** | תוכן טקסט | `string` prop + default |
| **Instance Swap** | החלפת אייקון | `ReactNode` prop |
| **Variant** | סגנון | `enum` prop |

---

## 📝 דוגמה מלאה - כפתור

### מבנה בפיגמה:

```
📁 Component Set: Button
│
├── 🔹 Variant Properties:
│   ├── Type = Primary, Secondary, Ghost
│   ├── Size = SM, MD, LG  
│   └── State = Default, Hover, Active, Focus, Disabled
│
├── 🔷 Type=Primary, Size=MD, State=Default
│   └── 📁 Auto Layout (horizontal, gap: 8px, padding: 12px 24px)
│       ├── 🖼️ Icon (Instance: icon-placeholder)
│       └── 📝 Label (Text: "Button")
│
├── 🔷 Type=Primary, Size=MD, State=Hover
│   └── ...
│
└── ... (more variants)
```

### JSON שיוצא:

```json
{
  "component": {
    "componentId": "1:234",
    "componentName": "Button",
    "displayName": "Button",
    "level": "atom",
    "category": "button",
    
    "props": [
      {
        "name": "label",
        "type": "string",
        "required": true,
        "defaultValue": "Button",
        "description": "Button text content"
      },
      {
        "name": "icon",
        "type": "node",
        "required": false,
        "description": "Icon element"
      },
      {
        "name": "onClick",
        "type": "function",
        "required": false,
        "description": "Click handler"
      },
      {
        "name": "disabled",
        "type": "boolean",
        "required": false,
        "defaultValue": false
      }
    ],
    
    "variants": [
      {
        "name": "variant",
        "options": ["primary", "secondary", "ghost"],
        "defaultOption": "primary"
      },
      {
        "name": "size",
        "options": ["sm", "md", "lg"],
        "defaultOption": "md"
      }
    ],
    
    "states": ["default", "hover", "active", "focus", "disabled"],
    
    "accessibility": {
      "role": "button",
      "keyboardInteraction": ["Enter", "Space"]
    }
  },
  
  "tokens": [
    {
      "name": "button-primary-bg",
      "value": "#3b82f6",
      "category": "color",
      "cssVariable": "--color-button-primary-bg"
    },
    {
      "name": "button-padding",
      "value": "12px 24px",
      "category": "spacing",
      "cssVariable": "--spacing-button-padding"
    },
    {
      "name": "button-gap",
      "value": "8px",
      "category": "spacing",
      "cssVariable": "--spacing-button-gap"
    },
    {
      "name": "button-radius",
      "value": "8px",
      "category": "borderRadius",
      "cssVariable": "--radius-button"
    }
  ]
}
```

---

## ✅ צ'קליסט לפני חילוץ

- [ ] שם קומפוננטה בפורמט `Category / Variant / Size`
- [ ] Variant Properties מוגדרים (`Type`, `Size`, `State`)
- [ ] Auto Layout מופעל עם padding ו-gap
- [ ] שמות layers משמעותיים (`Label`, `Icon`, לא `Text 1`)
- [ ] צבעים מוגדרים כ-Solid fills (לא gradients לטוקנים)
- [ ] Corner radius מוגדר (לא mixed)
- [ ] Effects מוגדרים (shadows)

---

## 🔧 העשרה ידנית

שדות שצריך להוסיף ידנית בממשק הפלאגין:

| שדה | מתי צריך | דוגמה |
|-----|----------|-------|
| `description` | תמיד | "Primary action button for CTAs" |
| `notes` | guidelines | "Max 2 per page" |
| `tags` | לחיפוש | `["button", "cta", "primary"]` |
| `ariaLabel` | אייקון בלי טקסט | "Close dialog" |
| `external dependencies` | ספריות חיצוניות | `["lucide-react"]` |

---

## 🎯 טיפים

1. **השתמש ב-Styles** - צבעים וטיפוגרפיה כ-Styles יחולצו כטוקנים סמנטיים
2. **תן שמות באנגלית** - קל יותר להמיר לקוד
3. **הימנע מ-Mixed Values** - `cornerRadius` מעורב לא יחולץ
4. **השתמש ב-Auto Layout** - זה מה שהופך לפלקסבוקס בקוד
5. **State ב-Variants** - ולא כ-layers נפרדים
