# Atomic Design Extractor - Figma Plugin

פלאגין לפיגמה שמחלץ קומפוננטות ומייצר Atomic Design System דרך MCP.

## 🎯 יכולות

- **ניתוח Nodes** - בוחן את הקומפוננטות הנבחרות ומסווג אותן לפי Atomic Design (Atom, Molecule, Organism, Template, Page)
- **תור המרה** - מנהל תור עם סדר עדיפויות לפי תלויות וסוג קומפוננטה
- **תוכנית עבודה** - בונה תוכנית שלבים לכל קומפוננטה עם אישור המשתמש
- **העשרת מטא-דאטה** - מוסיף props, variants, states, accessibility ועוד
- **חילוץ טוקנים** - מייצר Design Tokens מהקומפוננטות
- **שליחה ל-MCP** - שולח את הכל לבקאנד שבונה קוד

## 🏗️ ארכיטקטורה

```
figma-atomic-plugin/
├── manifest.json          # הגדרת הפלאגין
├── package.json           # תלויות ו-scripts
├── tsconfig.json          # הגדרות TypeScript
├── src/
│   ├── code.ts            # נקודת כניסה ראשית
│   ├── types/
│   │   └── index.ts       # כל הטיפוסים
│   └── services/
│       ├── NodeAnalyzer.ts      # ניתוח וסיווג nodes
│       ├── QueueManager.ts      # ניהול תור ההמרה
│       ├── MCPClient.ts         # תקשורת עם הבקאנד
│       ├── ComponentEnricher.ts # העשרת מטא-דאטה
│       └── index.ts             # ייצוא מאוחד
└── ui/
    └── ui.html            # ממשק המשתמש
```

## 🔄 זרימת העבודה

```
1. בחירת קומפוננטות בפיגמה
         ↓
2. ניתוח וסיווג אוטומטי (NodeAnalyzer)
         ↓
3. יצירת תוכנית עבודה לכל קומפוננטה
         ↓
4. אישור המשתמש (או דחייה עם סיבה)
         ↓
5. הוספה לתור לפי סדר עדיפויות (QueueManager)
         ↓
6. עיבוד התור:
   • חילוץ Design Tokens
   • העשרת מטא-דאטה (ComponentEnricher)
   • המרה לפורמט הבקאנד
         ↓
7. שליחה דרך MCP לבקאנד (MCPClient)
         ↓
8. הבקאנד מייצר קוד!
```

## 🚀 התקנה

```bash
# התקנת תלויות
npm install

# בנייה
npm run build

# פיתוח עם watch
npm run dev
```

## ⚙️ הגדרות

### MCP Endpoint
כתובת ברירת המחדל: `http://localhost:3845/mcp`

### פורמטים נתמכים
- **Framework**: React, Vue, HTML
- **Token Naming**: kebab-case, camelCase, snake_case
- **Export**: CSS Variables, JSON, Tailwind Config

## 📦 שימוש

### 1. בחירה וניתוח
1. בחרו קומפוננטות בפיגמה (Component, Component Set, או Frame)
2. הפלאגין יסווג אוטומטית כל קומפוננטה

### 2. תוכנית עבודה
לכל קומפוננטה נבנית תוכנית עם השלבים:
- **Extract Tokens** - חילוץ צבעים, טיפוגרפיה, מרווחים
- **Analyze Variants** - ניתוח וריאנטים (size, state, type)
- **Map Props** - מיפוי props לקוד
- **Generate Code** - יצירת הקומפוננטה
- **Create Stories** - Storybook (אופציונלי)

### 3. עיבוד התור
- התור ממיין אוטומטית לפי תלויות ורמה אטומית
- Atoms מעובדים ראשונים (הם הבסיס)
- אפשר לעצור/להמשיך בכל רגע

### 4. חיבור לבקאנד
1. הזינו את כתובת ה-MCP Endpoint
2. לחצו Connect
3. הפלאגין ישלח את הקומפוננטות אוטומטית

## 🔌 MCP Backend

הפלאגין מצפה לשרת MCP עם הכלים הבאים:

### generate_component
```json
{
  "name": "generate_component",
  "arguments": {
    "component": { /* EnrichedComponentData */ },
    "tokens": [ /* DesignToken[] */ ],
    "metadata": { /* FigmaMetadata */ }
  }
}
```

### generate_tokens
```json
{
  "name": "generate_tokens",
  "arguments": {
    "tokens": [ /* DesignToken[] */ ],
    "format": "css" | "json" | "tailwind"
  }
}
```

### validate_component
```json
{
  "name": "validate_component",
  "arguments": {
    "component": { /* EnrichedComponentData */ }
  }
}
```

## 📊 מבנה נתונים

### EnrichedComponentData
```typescript
{
  componentId: string;
  componentName: string;
  displayName: string;  // PascalCase
  description: string;
  level: 'atom' | 'molecule' | 'organism' | 'template' | 'page';
  category: string;     // button, input, card, etc.
  props: PropDefinition[];
  variants: VariantDefinition[];
  tokens: DesignToken[];
  states: string[];     // default, hover, active, disabled
  breakpoints: string[];
  dependencies: { internal: string[]; external: string[] };
  accessibility: { role, ariaLabel, keyboardInteraction };
}
```

### DesignToken
```typescript
{
  name: string;
  value: string | number;
  category: 'color' | 'typography' | 'spacing' | 'borderRadius' | 'shadow';
  cssVariable: string;
  tailwindClass?: string;
  semanticName?: string;
}
```

## 🎨 סיווג Atomic Design

| Level | דוגמאות | מאפיינים |
|-------|---------|----------|
| **Atom** | Button, Input, Icon, Badge | עד 3 ילדים, עומק 2 |
| **Molecule** | FormField, SearchBar, MenuItem | 2-6 ילדים, עומק 3 |
| **Organism** | Card, Header, Modal, Form | 3+ ילדים, עומק 2+ |
| **Template** | Layout, Dashboard, AuthLayout | מכיל Container/Layout |
| **Page** | HomePage, SettingsPage | מופע ספציפי של Template |

## 🔒 אבטחה

- הפלאגין תומך ב-retry עם exponential backoff
- Timeout ברירת מחדל: 30 שניות
- ניתן להגדיר domains מותרים ב-manifest

## 📝 License

MIT
