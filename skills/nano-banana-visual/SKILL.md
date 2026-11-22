---
name: nano-banana-visual
description: "[OPTIONAL] AI-powered visual generation using Google Nano Banana Pro. For user flows, architecture diagrams, mockups."
---

# Nano Banana Pro Visual Integration

OPTIONAL SKILL - AID works without this. Apply only when a visual artifact is requested (see When to Use); otherwise skip.

## Setup
Non-secret settings: `ENABLE_NANO_BANANA=true`, `NANO_BANANA_PROVIDER=google`.
The provider key is a secret: never write it to `.env` or any file. Keep it in the OS
keystore (macOS `security add-generic-password -s aid-nano-banana -a "$USER" -w`, Linux
`secret-tool store --label="AID Nano Banana" service aid-nano-banana`, Windows
`cmdkey /generic:aid-nano-banana /user:you /pass`) and export it into the shell
(`security find-generic-password -s aid-nano-banana -w`, `secret-tool lookup service aid-nano-banana`,
`Get-StoredCredential -Target aid-nano-banana`). See SKILL.extended.md.

## When to Use
| Phase | Trigger | Output |
|---|---|---|
| Discovery | "Create stakeholder map" | Diagram |
| PRD | "Create user flow" | Flow diagram |
| Tech Spec | "Create architecture" | System diagram |
| Development | "Create mockup" | Screen mockup |

## Quick Start
Text prompt (user flow, architecture, infographic):
```typescript
const result = await client.generateFromText(`
Create user flow for checkout:
1. Cart Review
2. Shipping
3. Payment
4. Confirmation

Style: Clean, modern
`);
```

Screen mockup:
```typescript
const builder = new WireframePromptBuilder({
  designSystem: 'material3',
  primaryColor: '#3B82F6',
});

const prompt = builder.generateScreen({
  name: 'Dashboard',
  components: [
    { type: 'header', position: 'top' },
    { type: 'card', description: 'Stats' },
    { type: 'list', description: 'Activity' },
  ],
});
```

Ready-made prompt bodies per phase: `references/prompt-library.md`

## File Organization
```
docs/visuals/
  discovery/stakeholder-map.png
  prd/user-flow.png
  tech-spec/architecture.png
  design/mockup.png
```

## API Methods
| Method | Description |
|---|---|
| generateFromText(prompt) | Image from text |
| editImage(base64, instruction) | Edit image |
| wireframeToUI(sketch, description) | Sketch to UI |

## Options
| Option | Values |
|---|---|
| aspectRatio | 1:1, 16:9, 9:16 |
| resolution | 1K, 2K, 4K |
| numImages | 1-4 |
