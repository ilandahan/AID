# Nano Banana Pro API Integration

TypeScript client for Google's Nano Banana Pro (Gemini 3 Pro Image) API.
Specialized for wireframe-to-UI conversion and design generation workflows.

## Installation

No additional packages required - uses native `fetch` API.

## Configuration

### Environment Variables

```bash
# For Google's direct API
GOOGLE_AI_API_KEY=your-google-ai-api-key

# OR for AI/ML API provider
AIML_API_KEY=your-aimlapi-key
```

### Get API Keys

**Google AI Studio:**
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with Google account
3. Click "Get API key" → Create new key
4. Copy and store securely

**AI/ML API:**
1. Go to [AI/ML API](https://aimlapi.com/)
2. Create account and get API key

## Usage

### Basic Text-to-Image

```typescript
import { NanoBananaProClient } from '@/lib/nano-banana-pro';

const client = new NanoBananaProClient({
  apiKey: process.env.GOOGLE_AI_API_KEY!,
  provider: 'google', // or 'aimlapi'
});

const result = await client.generateFromText(
  'A modern mobile banking app dashboard with account balance, recent transactions, and quick actions',
  {
    aspectRatio: '9:16',
    resolution: '2K',
    numImages: 1,
  }
);

// Save the image
const imageBase64 = result.images[0].base64;
```

### Wireframe to UI Conversion

```typescript
import { NanoBananaProClient } from '@/lib/nano-banana-pro';
import fs from 'fs';

const client = new NanoBananaProClient({
  apiKey: process.env.GOOGLE_AI_API_KEY!,
  provider: 'google',
});

// Read wireframe sketch
const sketchBase64 = fs.readFileSync('wireframe.png').toString('base64');

// Convert to high-fidelity UI
const result = await client.wireframeToUI(
  sketchBase64,
  'Login screen for a fitness tracking app with email, password, social login options, and forgot password link',
  { resolution: '2K' }
);
```

### Using Prompt Builder

```typescript
import {
  NanoBananaProClient,
  WireframePromptBuilder,
} from '@/lib/nano-banana-pro';

const client = new NanoBananaProClient({
  apiKey: process.env.GOOGLE_AI_API_KEY!,
  provider: 'google',
});

// Configure prompt builder
const builder = new WireframePromptBuilder({
  designSystem: 'ios18',
  deviceFrame: 'iphone-16-pro',
  style: 'high-fidelity',
  colorScheme: 'dark',
  primaryColor: '#007AFF',
});

// Generate screen design
const prompt = builder.generateScreen({
  name: 'Home Dashboard',
  description: 'Main dashboard showing user stats, recent activity, and quick actions',
  components: [
    { type: 'header', description: 'User greeting with avatar', position: 'top' },
    { type: 'card', description: 'Weekly progress stats', size: 'large' },
    { type: 'list', description: 'Recent activities', size: 'medium' },
    { type: 'navigation', description: 'Bottom tab bar', position: 'bottom' },
  ],
});

const result = await client.generateFromText(prompt, {
  aspectRatio: '9:16',
  resolution: '2K',
});
```

### Pre-built Templates

```typescript
import {
  NanoBananaProClient,
  PromptTemplates,
} from '@/lib/nano-banana-pro';

const client = new NanoBananaProClient({
  apiKey: process.env.GOOGLE_AI_API_KEY!,
  provider: 'google',
});

// Onboarding screen
const onboarding = await client.generateFromText(
  PromptTemplates.mobileOnboarding('FitTrack', 'Track your daily steps and calories')
);

// Dashboard
const dashboard = await client.generateFromText(
  PromptTemplates.dashboard(['Daily Active Users', 'Revenue', 'Conversion Rate', 'Churn'])
);

// Settings screen
const settings = await client.generateFromText(
  PromptTemplates.settingsScreen(['Account', 'Notifications', 'Privacy', 'Appearance', 'Help'])
);

// Empty state
const emptyState = await client.generateFromText(
  PromptTemplates.emptyState('orders', 'Start Shopping')
);

// Error page
const errorPage = await client.generateFromText(
  PromptTemplates.errorState('404')
);
```

### A/B Test Variations

```typescript
import {
  NanoBananaProClient,
  createVariationPrompt,
} from '@/lib/nano-banana-pro';

const client = new NanoBananaProClient({
  apiKey: process.env.GOOGLE_AI_API_KEY!,
  provider: 'google',
});

const originalDesign = 'E-commerce product page with hero image, price, and add to cart button';

// Generate color variation
const colorVariation = await client.generateFromText(
  createVariationPrompt(originalDesign, 'color')
);

// Generate layout variation
const layoutVariation = await client.generateFromText(
  createVariationPrompt(originalDesign, 'layout')
);
```

## API Reference

### NanoBananaProClient

| Method | Description |
|--------|-------------|
| `generateFromText(prompt, options?)` | Generate image from text prompt |
| `editImage(imageBase64, instruction, options?)` | Edit existing image (Google only) |
| `wireframeToUI(sketchBase64, description, options?)` | Convert wireframe to UI |
| `generateWithSafety(prompt, safetySettings, options?)` | Generate with custom safety (Google only) |

### GenerationConfig Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `aspectRatio` | string | '1:1' | 1:1, 16:9, 9:16, 4:3, 3:4, etc. |
| `resolution` | string | '1K' | 1K, 2K, or 4K |
| `numImages` | number | 1 | 1-4 images |
| `quality` | string | 'standard' | standard, high, highest |
| `temperature` | number | - | 0.0-1.0 |

### WireframeOptions

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `designSystem` | string | 'custom' | ios18, material3, fluent, ant-design, chakra |
| `deviceFrame` | string | 'none' | iphone-16, pixel-9, ipad-pro, etc. |
| `style` | string | 'high-fidelity' | low/mid/high-fidelity, sketch, polished |
| `colorScheme` | string | 'light' | light, dark, auto |
| `primaryColor` | string | - | Hex color code |

## Error Handling

```typescript
import { NanoBananaProClient, NanoBananaProError } from '@/lib/nano-banana-pro';

try {
  const result = await client.generateFromText('...');
} catch (error) {
  if (error instanceof NanoBananaProError) {
    console.error(`Error: ${error.message}`);
    console.error(`Code: ${error.code}`);
    console.error(`Status: ${error.statusCode}`);
  }
}
```

## Provider Comparison

| Feature | Google | AI/ML API |
|---------|--------|-----------|
| Image editing | ✅ | ❌ |
| Safety settings | ✅ | ❌ |
| Max images | 1 | 4 |
| Pricing | Per token | Per credit |

## Sources

- [Google AI Studio](https://aistudio.google.com/)
- [AI/ML API Docs](https://docs.aimlapi.com/api-references/image-models/google/gemini-3-pro-image-preview)
- [Nano Banana Pro Guide](https://apidog.com/blog/nano-banana-pro-api/)
