# 📍 איפה בדיוק למלא בפיגמה

## מפת השדות המלאה

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FIGMA INTERFACE                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐  ┌─────────────────┐  ┌────────────────────┐  │
│  │   LAYERS PANEL   │  │     CANVAS      │  │   RIGHT PANEL      │  │
│  │   (שמאל)         │  │     (מרכז)       │  │   (ימין)           │  │
│  ├──────────────────┤  │                 │  ├────────────────────┤  │
│  │                  │  │                 │  │                    │  │
│  │  📁 Component Set│  │   ┌─────────┐   │  │  DESIGN TAB        │  │
│  │  │               │  │   │         │   │  │  ───────────       │  │
│  │  ├─ 🔷 Variant 1 │  │   │ Button  │   │  │                    │  │
│  │  │   │           │  │   │         │   │  │  Component         │  │
│  │  │   ├─ 🖼️ Icon  │◄─┼───┤  [Icon] │   │  │  ┌──────────────┐  │  │
│  │  │   │           │  │   │         │   │  │  │ 📝 Description│◄─┼──── ⭐ HERE!
│  │  │   └─ 📝 Label │◄─┼───┤  Label  │   │  │  │              │  │  │
│  │  │               │  │   │         │   │  │  │ Add desc...  │  │  │
│  │  ├─ 🔷 Variant 2 │  │   └─────────┘   │  │  └──────────────┘  │  │
│  │  │               │  │                 │  │                    │  │
│  │  └─ 🔷 Variant 3 │  │                 │  │  Variant           │  │
│  │                  │  │                 │  │  ┌──────────────┐  │  │
│  │  ▲               │  │                 │  │  │ Type: Primary│◄─┼──── ⭐ AND HERE!
│  │  │               │  │                 │  │  │ Size: Large  │  │  │
│  │  שמות הlayers    │  │                 │  │  │ State: Default│  │  │
│  │                  │  │                 │  │  └──────────────┘  │  │
│  └──────────────────┘  └─────────────────┘  └────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1️⃣ Component Description (הכי חשוב!)

### איך מגיעים:
```
1. בחר קומפוננטה בCanvas או ב-Layers
2. פאנל ימין → Design tab
3. מצא "Component" section
4. לחץ על "Add description" או ערוך את הקיים
```

### מה לכתוב שם:

```
Primary action button for main CTAs throughout the app.

---
tags: button, cta, primary, interactive
notes: Max 2 per page. Use danger for destructive actions.
ariaLabel: 
external: lucide-react
```

### צילום מסך וירטואלי:

```
┌─────────────────────────────────────┐
│ Component                       ▼   │
├─────────────────────────────────────┤
│ 🔷 Button                           │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Primary action button for main  │ │
│ │ CTAs throughout the app.        │ │
│ │                                 │ │
│ │ ---                             │ │
│ │ tags: button, cta, primary      │ │
│ │ notes: Max 2 per page           │ │
│ │ ariaLabel:                      │ │
│ │ external: lucide-react          │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Documentation ↗                     │
└─────────────────────────────────────┘
```

---

## 2️⃣ Variant Properties

### איך מגיעים:
```
1. בחר את ה-Component Set (המסגרת הסגולה)
2. פאנל ימין → Design tab
3. מצא "Current variant" או "Properties"
4. לחץ ⚙️ ליד כל property לעריכה
```

### Properties מומלצים:

| Property Name | Values | מה זה נותן |
|--------------|--------|-----------|
| `Type` | `Primary, Secondary, Ghost, Danger` | `variant` prop |
| `Size` | `SM, MD, LG` | `size` prop |
| `State` | `Default, Hover, Active, Focus, Disabled` | CSS states |
| `Show Icon` | `true, false` | `showIcon` boolean prop |

### צילום מסך וירטואלי:

```
┌─────────────────────────────────────┐
│ Current variant                     │
├─────────────────────────────────────┤
│                                     │
│ Type          ┌─────────────┐  ⚙️   │
│               │ Primary   ▼ │       │
│               └─────────────┘       │
│                                     │
│ Size          ┌─────────────┐  ⚙️   │
│               │ MD        ▼ │       │
│               └─────────────┘       │
│                                     │
│ State         ┌─────────────┐  ⚙️   │
│               │ Default   ▼ │       │
│               └─────────────┘       │
│                                     │
│ + Add property                      │
└─────────────────────────────────────┘
```

---

## 3️⃣ Layer Names (בפאנל Layers)

### איך משנים שם:
```
1. פאנל שמאל (Layers)
2. Double-click על שם ה-layer
3. שנה לשם משמעותי
```

### שמות שהפלאגין מזהה:

```
📁 Button                    ← שם הקומפוננטה
├── 📁 Content               ← children prop (ReactNode)
│   ├── 🖼️ Icon             ← icon prop (ReactNode)
│   └── 📝 Label            ← label prop (string)
├── 📝 Helper Text          ← helperText prop (string)
└── 🔴 Error Icon           ← מוצג רק ב-error state
```

### טבלת שמות → Props:

| שם Layer | סוג Prop שנוצר | דוגמה |
|----------|---------------|-------|
| `Label` | `label: string` | `"Click me"` |
| `Title` | `title: string` | `"Card Title"` |
| `Description` | `description: string` | `"Some text"` |
| `Placeholder` | `placeholder: string` | `"Enter..."` |
| `Helper Text` | `helperText: string` | `"Optional"` |
| `Error` / `Error Text` | `error: string` | `"Required"` |
| `Icon` | `icon: ReactNode` | `<IconCheck />` |
| `Leading Icon` | `leadingIcon: ReactNode` | - |
| `Trailing Icon` | `trailingIcon: ReactNode` | - |
| `Content` | `children: ReactNode` | - |
| `Children` | `children: ReactNode` | - |
| `Header` | `header: ReactNode` | - |
| `Footer` | `footer: ReactNode` | - |
| `Actions` | `actions: ReactNode` | - |

---

## 4️⃣ Component Properties (Figma החדש)

### איך מוסיפים:
```
1. בחר קומפוננטה
2. פאנל ימין → Properties
3. לחץ + → בחר סוג Property
```

### סוגי Properties:

```
┌─────────────────────────────────────┐
│ Properties                      +   │
├─────────────────────────────────────┤
│                                     │
│ 🔘 Show Icon          [✓]           │  ← Boolean
│    Type: Boolean                    │
│                                     │
│ 📝 Label              [Button]      │  ← Text
│    Type: Text                       │
│                                     │
│ 🔄 Icon               [icon-check]  │  ← Instance Swap
│    Type: Instance swap              │
│                                     │
└─────────────────────────────────────┘
```

### מה כל סוג נותן:

| סוג Property | מה נוצר | דוגמה בקוד |
|-------------|---------|------------|
| **Boolean** | `boolean` prop | `showIcon?: boolean` |
| **Text** | `string` prop + default | `label: string = "Button"` |
| **Instance Swap** | `ReactNode` prop | `icon?: ReactNode` |
| **Variant** | `enum` prop | `variant: 'primary' \| 'secondary'` |

---

## 5️⃣ Auto Layout Settings

### איך מגדירים:
```
1. בחר frame/component
2. פאנל ימין → Auto Layout (או Shift+A)
3. הגדר padding ו-gap
```

### מה מחולץ:

```
┌─────────────────────────────────────┐
│ Auto layout                    ↔️   │
├─────────────────────────────────────┤
│                                     │
│ Direction:    [→ Horizontal]        │  ← flex-direction
│                                     │
│ Gap:          [8]                   │  ← gap: 8px
│                                     │
│ Padding:                            │
│   ↑ [12]                           │  ← padding-top
│ ← [24]    [24] →                   │  ← padding-left/right
│   ↓ [12]                           │  ← padding-bottom
│                                     │
└─────────────────────────────────────┘
```

---

## 📋 סיכום - איפה כל שדה

| שדה בקוד | איפה בפיגמה | דוגמה |
|----------|-------------|-------|
| `displayName` | שם הקומפוננטה | `Button / Primary` |
| `description` | Component → Description | `"Primary button..."` |
| `tags` | בתוך Description | `tags: button, cta` |
| `notes` | בתוך Description | `notes: Max 2 per page` |
| `ariaLabel` | בתוך Description | `ariaLabel: Close` |
| `external` | בתוך Description | `external: lucide-react` |
| `variants` | Variant Properties | `Type, Size` |
| `states` | Variant Property "State" | `Default, Hover...` |
| `props` (string) | Text layer names | `Label, Title` |
| `props` (node) | Frame layer names | `Icon, Content` |
| `props` (boolean) | Boolean Property | `Show Icon` |
| `tokens.spacing` | Auto Layout | Padding, Gap |
| `tokens.color` | Fill colors | `#3b82f6` |
| `tokens.radius` | Corner Radius | `8` |

---

## ✅ Checklist מהיר

```
□ שם קומפוננטה: "Category / Variant / Size"
□ Description עם metadata (tags, notes, etc.)
□ Variant Properties: Type, Size, State
□ שמות layers: Label, Icon, Content
□ Auto Layout: padding, gap
□ Boolean properties: Show Icon, etc.
```
