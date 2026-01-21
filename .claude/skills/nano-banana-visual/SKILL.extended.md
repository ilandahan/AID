---
name: nano-banana-visual
description: "[OPTIONAL] AI-powered visual artifact generation using Google Nano Banana Pro. For creating professional user flows, architecture diagrams, screen mockups with Atomic Design."
optional: true
requires: "API key configured in .env file"
---

# Nano Banana Pro Visual Integration

> **OPTIONAL SKILL** - AID works fully without this. Enable only if you need AI-generated visuals.

Generate professional visual artifacts for AID phases using Google's Nano Banana Pro (Gemini 3 Pro Image).

## Setup (Environment Variables)

Configure in your `.env` file (copy from `.env.example`):

### Option 1: Google AI Studio (Easiest)
```env
ENABLE_NANO_BANANA=true
NANO_BANANA_PROVIDER=google
GOOGLE_AI_API_KEY=your-key-from-aistudio.google.com
```

### Option 2: AI/ML API
```env
ENABLE_NANO_BANANA=true
NANO_BANANA_PROVIDER=aimlapi
AIML_API_KEY=your-key-from-aimlapi.com
```

### Option 3: Google Vertex AI (Enterprise)
```env
ENABLE_NANO_BANANA=true
NANO_BANANA_PROVIDER=vertex
VERTEX_PROJECT_ID=your-gcp-project-id
VERTEX_LOCATION=us-central1
```

## Usage

```typescript
import { createNanoBananaClient, isNanoBananaEnabled } from '@/lib/nano-banana-pro';

// Always check if enabled first
if (isNanoBananaEnabled()) {
  const client = createNanoBananaClient();
  // Use client...
}
```

## When to Use

| AID Phase | Trigger | Output |
|-----------|---------|--------|
| Discovery | "Create stakeholder map" | Stakeholder diagram |
| PRD | "Create user flow" | Flow diagram |
| Tech Spec | "Create architecture diagram" | System architecture |
| Development | "Create screen mockup" | Atomic Design mockup |

## Phase Integration

```
Discovery  → Stakeholder Map, Problem Impact Visual
PRD        → User Flows, Journey Maps, Wireframes
Tech Spec  → Architecture, ERD, Sequence Diagrams
Development → Screen Mockups (with Atomic Design tokens)
```

---

## Quick Start

### Generate User Flow
```typescript
const result = await client.generateFromText(`
Create a user flow diagram for checkout process.

Flow Steps:
1. Cart Review
2. Shipping Info
3. Payment
4. Confirmation

Style: Clean, modern, color-coded arrows
`);

// Save image
fs.writeFileSync('user-flow.png', Buffer.from(result.images[0].base64!, 'base64'));
```

### Generate Architecture Diagram
```typescript
const result = await client.generateFromText(`
Create a microservices architecture diagram.

Components:
- Frontend: React, Next.js
- API Gateway: Kong
- Services: User, Order, Payment, Notification
- Database: PostgreSQL, Redis
- External: Stripe, SendGrid

Style: Cloud architecture, flat icons
`);
```

### Generate Screen Mockup
```typescript
import { WireframePromptBuilder } from '@/lib/nano-banana-pro';

const builder = new WireframePromptBuilder({
  designSystem: 'material3',
  deviceFrame: 'iphone-16',
  style: 'high-fidelity',
  primaryColor: '#3B82F6',
});

const prompt = builder.generateScreen({
  name: 'Dashboard',
  description: 'Main dashboard with stats and activity',
  components: [
    { type: 'header', description: 'Logo and user menu', position: 'top' },
    { type: 'card', description: 'Stats cards row', size: 'medium' },
    { type: 'list', description: 'Recent activity', size: 'large' },
  ],
});

const result = await client.generateFromText(prompt);
```

---

## Prompt Templates

See `references/prompt-library.md` for complete prompt templates:

- **Discovery**: Stakeholder maps, problem impact visuals
- **PRD**: User flows, journey maps, feature matrices
- **Tech Spec**: Architecture, ERD, sequence diagrams
- **Development**: Dashboard, forms, tables, empty states

---

## Integration with Atomic Design

When generating screen mockups, include design tokens:

```typescript
const prompt = `
Design Tokens (from your design system):
- Primary: #3B82F6
- Background: #F9FAFB
- Text: #111827
- Border: #E5E7EB
- Radius: 8px
- Font: Inter

Components (Atomic Design):
HEADER (Organism):
- Logo (Atom)
- Navigation (Molecule)
- User Menu (Molecule)

MAIN CONTENT:
- Stats Cards (Molecule)
- Activity List (Organism)
`;
```

After generating:
1. Identify Atoms, Molecules, Organisms in mockup
2. Map to existing components or create specs for new ones
3. Use `atomic-design` skill for implementation

---

## Quality Checklist

Before generating:
- [ ] Clear purpose defined
- [ ] Content/labels prepared (not placeholder)
- [ ] Design tokens ready (for mockups)

After generating:
- [ ] Visual is accurate
- [ ] Text is readable
- [ ] Ready to embed in documentation

---

## File Organization

```
project/docs/visuals/
├── discovery/
│   └── stakeholder-map.png
├── prd/
│   └── user-flow-checkout.png
├── tech-spec/
│   └── architecture.png
└── design/
    └── dashboard-mockup.png
```

---

## API Reference

### Client Methods

| Method | Description |
|--------|-------------|
| `generateFromText(prompt, options?)` | Generate image from text |
| `editImage(imageBase64, instruction, options?)` | Edit existing image |
| `wireframeToUI(sketchBase64, description, options?)` | Convert sketch to UI |

### Generation Options

| Option | Type | Default |
|--------|------|---------|
| `aspectRatio` | '1:1', '16:9', '9:16', etc. | '1:1' |
| `resolution` | '1K', '2K', '4K' | '1K' |
| `numImages` | 1-4 | 1 |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| AUTH_ERROR | Run `gcloud auth login` |
| API not enabled | `gcloud services enable aiplatform.googleapis.com` |
| No images generated | Check prompt clarity, try simpler request |
| Timeout | Increase timeout in config |
