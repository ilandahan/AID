# Atomic Design Extractor - Figma Plugin Listing

## Plugin Name
**Atomic Design Extractor**

---

## Tagline (80 characters max)
> AI-powered component auditor & React code generator for Atomic Design systems

**Character count: 76** ✅

### Alternative Taglines:
- `Export Figma components to production-ready React with AI quality scoring` (73 chars)
- `Transform Figma designs into Atomic Design System components instantly` (70 chars)
- `AI component auditor: Score, validate & export to React + Storybook` (68 chars)

---

## Short Description (160 characters)
> Audit your Figma components for design system quality, generate LLM-accessible metadata, and export production-ready React code with Storybook, tests, and tokens.

---

## Full Description

### Overview

**Atomic Design Extractor** bridges the gap between design and development by transforming your Figma components into production-ready code. Powered by AI analysis, it ensures your components meet design system quality standards before export.

### Key Features

#### 🔍 **AI-Powered Component Auditing**
Get instant quality scores (0-100) for any component or component set. The AI analyzer checks for:
- Auto-layout implementation
- Variant coverage (states, sizes, styles)
- Accessibility compliance
- Design token usage
- Naming conventions

#### 📊 **LLM-Accessible Metadata**
Generate rich, structured metadata that makes your components understandable by AI tools:
- Semantic descriptions
- Property documentation
- Accessibility notes
- Usage guidelines

#### 📦 **Complete Export Package**
Export components as a ready-to-use ZIP containing:
- `Component.tsx` - React component with TypeScript
- `Component.module.css` - CSS modules with design tokens
- `Component.stories.tsx` - Storybook documentation
- `Component.test.tsx` - Jest/RTL unit tests
- `Component.tokens.ts` - Design tokens
- `Component.types.ts` - TypeScript definitions
- `README.md` - Component documentation
- `metadata.json` - Full Figma context

#### 🎯 **Atomic Design Classification**
Automatically classifies components into atomic levels:
- ⚛️ **Atoms** - Basic building blocks (buttons, inputs)
- 🧬 **Molecules** - Simple groups (form fields, cards)
- 🦠 **Organisms** - Complex sections (headers, modals)
- 📐 **Templates** - Page layouts
- 📄 **Pages** - Complete pages

#### 🔐 **Secure Pairing**
Connect securely via one-time pairing codes generated from Claude Code. No passwords stored, JWT-based sessions with 24-hour expiry.

### How It Works

1. **Select** a component or component set in Figma
2. **Audit** to get quality score and improvement suggestions
3. **Generate** metadata to document your component
4. **Export** when score reaches 90+ to download production code

### Who Is This For?

- **Design System Teams** - Ensure component quality standards
- **Developers** - Get production-ready code from designs
- **Design Technologists** - Bridge design-to-dev handoff
- **Agencies** - Speed up client deliverables

### Requirements

- Figma Desktop or Web
- Claude Code CLI (for pairing)
- Internet connection (for AI analysis)

### Privacy & Security

- No design data stored on servers
- Analysis happens in real-time
- Secure JWT authentication
- GDPR compliant

---

## Categories

### Primary Category
**Developer Handoff** ⭐ (Best fit)

### Secondary Categories
1. **Design Systems**
2. **Code & Engineering**
3. **Utilities**

---

## Tags (Keywords)

```
react, atomic-design, component, export, code-generation, design-system,
storybook, typescript, developer-handoff, accessibility, a11y, tokens,
design-tokens, quality, audit, ai, metadata, documentation, testing
```

### Top 10 Recommended Tags:
1. `react`
2. `design-system`
3. `atomic-design`
4. `code-generation`
5. `storybook`
6. `developer-handoff`
7. `typescript`
8. `accessibility`
9. `design-tokens`
10. `component-library`

---

## Support & Links

| Field | Value |
|-------|-------|
| **Support Email** | support@theaid.ai |
| **Documentation** | https://docs.theaid.ai/figma-plugin |
| **Privacy Policy** | https://theaid.ai/privacy |
| **Terms of Service** | https://theaid.ai/terms |
| **Website** | https://theaid.ai |
| **GitHub** | https://github.com/theaid-ai/figma-plugin |

---

## Screenshots Recommendations

### Screenshot 1: Component Audit
- Show a component selected with the audit score displayed
- Highlight the score card (91/100) with green "Ready for Export"
- Caption: "AI-powered quality scoring for your components"

### Screenshot 2: Metadata Generation
- Show the Review tab with generated metadata
- Display property descriptions and accessibility notes
- Caption: "Auto-generate LLM-accessible documentation"

### Screenshot 3: Export Preview
- Show the Export tab with file tree
- Display all 9 files that will be created
- Caption: "Export complete React components with one click"

### Screenshot 4: Download Modal
- Show the ZIP download modal with atomic level badge
- Display the directory structure
- Caption: "Production-ready code package with Storybook & tests"

### Screenshot 5: Pairing Flow
- Show the pairing code entry screen
- Display connection status
- Caption: "Secure connection via Claude Code pairing"

---

## Cover Image Concept

**Recommended Design:**
- Left side: Figma component preview (button with variants)
- Center: Arrow or transformation visual
- Right side: Code editor with React/Storybook
- Bottom: Atomic level icons (atom → molecule → organism)
- Colors: Figma purple (#A259FF) + AID blue (#0C8CE9)
- Text overlay: "Design → Code in seconds"

---

## Icon Concept

**128×128 px icon design:**
- Atom symbol (⚛️) with code brackets `</>`
- Or: Component box with export arrow
- Colors: Gradient from Figma purple to AID blue
- Style: Minimal, recognizable at small sizes

---

## Publishing Notes

### Before Publishing:
- [ ] Test plugin in Figma Desktop
- [ ] Verify all 9 files export correctly
- [ ] Test pairing flow end-to-end
- [ ] Prepare icon (128×128 PNG)
- [ ] Prepare cover image (1920×960 PNG)
- [ ] Take 5 screenshots (1920×960 PNG each)
- [ ] Update manifest.json with final plugin ID

### Review Expectations:
- Figma review typically takes 1-5 business days
- They check for: security, functionality, UI quality, guideline compliance
- Network access must be justified (already done in manifest)

---

*Document generated for Atomic Design Extractor Figma Plugin*
*Last updated: January 2026*
