/**
 * Nano Banana Pro Prompt Builders
 * Specialized prompts for wireframes, UI design, and mockups
 */

import {
  WireframeOptions,
  ScreenSpec,
  DesignSystem,
  DeviceFrame,
  WireframeStyle,
} from './types';

// ============================================
// Design System Descriptions
// ============================================

const DESIGN_SYSTEM_STYLES: Record<DesignSystem, string> = {
  ios18: `
    - Apple iOS 18 design language
    - SF Pro font family, Dynamic Type support
    - Rounded corners (12-16px radius)
    - Subtle shadows and translucent materials
    - System colors with vibrancy effects
    - Haptic-ready button states`,
  material3: `
    - Google Material Design 3 (Material You)
    - Roboto/Google Sans typography
    - Dynamic color theming
    - Elevated surfaces with tonal colors
    - Large touch targets (48dp minimum)
    - Motion design with spring physics`,
  fluent: `
    - Microsoft Fluent Design System
    - Segoe UI Variable font
    - Acrylic and Mica backgrounds
    - Subtle reveal effects
    - Depth through shadow and light
    - Responsive typography scale`,
  'ant-design': `
    - Ant Design System
    - Clean, enterprise-focused aesthetics
    - 4px grid system
    - Consistent spacing and sizing
    - Clear information hierarchy
    - Form-focused components`,
  chakra: `
    - Chakra UI design principles
    - Accessible by default
    - Consistent spacing scale
    - Theme-able color modes
    - Responsive utility classes
    - Composable components`,
  custom: `
    - Modern, clean aesthetics
    - Consistent visual hierarchy
    - Appropriate contrast ratios
    - Balanced white space
    - Clear call-to-action elements`,
};

const DEVICE_FRAME_SPECS: Record<DeviceFrame, string> = {
  'iphone-16': 'iPhone 16 frame (6.1" display, 2556x1179px, Dynamic Island)',
  'iphone-16-pro': 'iPhone 16 Pro frame (6.3" display, 2622x1206px, Dynamic Island)',
  'iphone-15': 'iPhone 15 frame (6.1" display, 2556x1179px, Dynamic Island)',
  'pixel-9': 'Google Pixel 9 frame (6.3" display, 2424x1080px)',
  'samsung-s24': 'Samsung Galaxy S24 frame (6.2" display, 2340x1080px)',
  'ipad-pro': 'iPad Pro 12.9" frame (2732x2048px)',
  'macbook-pro': 'MacBook Pro 14" frame (3024x1964px)',
  'desktop-1920': 'Desktop browser at 1920x1080px',
  'desktop-1440': 'Desktop browser at 1440x900px',
  none: 'No device frame, design only',
};

const FIDELITY_DESCRIPTIONS: Record<WireframeStyle, string> = {
  'low-fidelity': `
    - Basic shapes and placeholders
    - Grayscale only
    - Hand-drawn/sketchy appearance
    - Focus on layout and flow
    - No detailed styling`,
  'mid-fidelity': `
    - Defined shapes and components
    - Limited color palette
    - Basic typography hierarchy
    - Component boundaries visible
    - Some interactive states`,
  'high-fidelity': `
    - Pixel-perfect design
    - Full color scheme applied
    - Actual typography and icons
    - Real content or realistic placeholders
    - All states and interactions shown`,
  sketch: `
    - Hand-drawn aesthetic
    - Rough, artistic style
    - Conceptual visualization
    - Creative interpretation
    - Expressive linework`,
  polished: `
    - Production-ready quality
    - Export-ready assets
    - Perfect alignment and spacing
    - Optimized for development handoff
    - Includes all necessary states`,
};

// ============================================
// Prompt Builder Class
// ============================================

export class WireframePromptBuilder {
  private options: WireframeOptions;

  constructor(options: WireframeOptions = {}) {
    this.options = {
      designSystem: 'custom',
      deviceFrame: 'none',
      style: 'high-fidelity',
      colorScheme: 'light',
      includePlaceholders: true,
      includeAnnotations: false,
      ...options,
    };
  }

  /**
   * Build a prompt for converting a sketch to UI
   */
  sketchToUI(description: string): string {
    return `Transform this rough wireframe sketch into a ${this.options.style} UI design.

## Design System
${DESIGN_SYSTEM_STYLES[this.options.designSystem || 'custom']}

## Device Context
${DEVICE_FRAME_SPECS[this.options.deviceFrame || 'none']}

## Fidelity Level
${FIDELITY_DESCRIPTIONS[this.options.style || 'high-fidelity']}

## Color Scheme
- Mode: ${this.options.colorScheme}
${this.options.primaryColor ? `- Primary color: ${this.options.primaryColor}` : ''}

## Content Handling
${this.options.includePlaceholders
  ? '- Generate realistic placeholder images for image areas\n- Use realistic sample text for content areas'
  : '- Use simple gray boxes for image placeholders\n- Use lorem ipsum for text areas'}

## Transformation Rules
- Interpret sketched shapes as proper UI components
- Convert rough rectangles into styled buttons
- Transform lines into readable text blocks
- Maintain the layout intent from the sketch
- Apply consistent padding and margins
- Ensure proper visual hierarchy

## Screen Description
${description}

${this.options.includeAnnotations
  ? '## Annotations\nInclude component labels and spacing annotations for developer reference.'
  : ''}

Generate a polished, professional UI mockup that faithfully interprets the sketch while applying modern design standards.`;
  }

  /**
   * Build a prompt for generating a new screen design
   */
  generateScreen(spec: ScreenSpec): string {
    const componentsList = spec.components?.map(c =>
      `- ${c.type}: ${c.description}${c.position ? ` (${c.position})` : ''}${c.size ? `, ${c.size}` : ''}`
    ).join('\n') || '';

    return `Create a ${this.options.style} UI design for a mobile/web screen.

## Screen: ${spec.name}
${spec.description}

${spec.flowContext ? `## User Flow Context\n${spec.flowContext}\n` : ''}

## Design System
${DESIGN_SYSTEM_STYLES[this.options.designSystem || 'custom']}

## Device Context
${DEVICE_FRAME_SPECS[this.options.deviceFrame || 'none']}

## Color Scheme
- Mode: ${this.options.colorScheme}
${this.options.primaryColor ? `- Primary color: ${this.options.primaryColor}` : ''}

${componentsList ? `## Required Components\n${componentsList}\n` : ''}

## Quality Standards
${FIDELITY_DESCRIPTIONS[this.options.style || 'high-fidelity']}

Generate a professional, modern UI design that would be suitable for production use.`;
  }

  /**
   * Build a prompt for creating a user flow diagram
   */
  generateUserFlow(
    flowName: string,
    screens: string[],
    description: string
  ): string {
    return `Create a visual user flow diagram showing the navigation between screens.

## Flow Name: ${flowName}
${description}

## Screens in Flow
${screens.map((s, i) => `${i + 1}. ${s}`).join('\n')}

## Visual Style
- Clean, professional diagram style
- Clear directional arrows between screens
- Consistent screen thumbnail sizes
- Labels for each screen and transition
- Color coding for different action types
${this.options.primaryColor ? `- Use ${this.options.primaryColor} as accent color` : ''}

## Layout
- Logical left-to-right or top-to-bottom flow
- Clear visual hierarchy
- Adequate spacing between elements
- Decision points clearly marked

Generate a clear, easy-to-understand user flow diagram.`;
  }

  /**
   * Build a prompt for creating a component library preview
   */
  generateComponentLibrary(
    componentTypes: string[],
    brandDescription?: string
  ): string {
    return `Create a UI component library showcase with the following components.

## Components to Include
${componentTypes.map(c => `- ${c}`).join('\n')}

## Design System
${DESIGN_SYSTEM_STYLES[this.options.designSystem || 'custom']}

${brandDescription ? `## Brand Guidelines\n${brandDescription}\n` : ''}

## Color Scheme
- Mode: ${this.options.colorScheme}
${this.options.primaryColor ? `- Primary color: ${this.options.primaryColor}` : ''}

## Presentation Style
- Show each component in multiple states (default, hover, active, disabled)
- Organize in a clean grid layout
- Include clear labels
- Show size variations where applicable
- Demonstrate responsive behavior

Generate a comprehensive component library showcase suitable for a design system documentation.`;
  }
}

// ============================================
// AID Phase Prompt Templates (Primary Use Cases)
// ============================================

/**
 * Default consulting brand for professional visuals
 */
const DEFAULT_BRAND = {
  companyName: 'AID Consulting',
  tagline: 'AI-Driven Development',
  primaryColor: '#2563EB', // Blue
  accentColor: '#0F172A',  // Dark slate
};

/**
 * Brand configuration for visuals
 */
export interface BrandConfig {
  companyName?: string;
  tagline?: string;
  primaryColor?: string;
  accentColor?: string;
  showLogo?: boolean;
}

export const AIDPromptTemplates = {
  /**
   * Research Slide - Key findings presentation
   * Use in: Discovery Phase
   */
  researchSlide: (config: {
    title: string;
    keyFindings: string[];
    dataPoints?: Array<{ label: string; value: string; trend?: 'up' | 'down' | 'neutral' }>;
    sourceCount?: number;
    brand?: BrandConfig;
  }) => {
    const brand = { ...DEFAULT_BRAND, ...config.brand };
    return `Create a professional consulting research findings slide.

BRANDING:
- Company: "${brand.companyName}"
- Tagline: "${brand.tagline}"
- Logo placement: Top-left corner (simple text logo)
- Primary color: ${brand.primaryColor}
- Footer: Company name + confidential notice

Title: "${config.title}"

Key Findings:
${config.keyFindings.map((f, i) => `${i + 1}. ${f}`).join('\n')}

${config.dataPoints ? `Data Points:
${config.dataPoints.map(d => `- ${d.label}: ${d.value}${d.trend ? ` (${d.trend === 'up' ? '↑' : d.trend === 'down' ? '↓' : '→'})` : ''}`).join('\n')}` : ''}

${config.sourceCount ? `Sources: ${config.sourceCount} references` : ''}

Style:
- Clean white background
- Professional consulting slide design (McKinsey/BCG style)
- Company branding in header/footer
- Clear typography hierarchy
- Data visualizations where appropriate
- Presentation-ready (16:9 aspect ratio)

FONT REQUIREMENTS:
- Title: BOLD, 28pt minimum, black text
- Headings: BOLD, 20pt minimum
- Body text: 16pt minimum, high contrast
- Use simple sans-serif fonts only
- NO small or decorative fonts`;
  },

  /**
   * Stakeholder Map - Visual representation of stakeholders
   * Use in: Discovery Phase
   */
  stakeholderMap: (config: {
    projectName: string;
    coreTeam: string[];
    decisionMakers: string[];
    externalStakeholders: string[];
    brand?: BrandConfig;
  }) => {
    const brand = { ...DEFAULT_BRAND, ...config.brand };
    return `Create a professional consulting stakeholder map diagram.

BRANDING:
- Company: "${brand.companyName}" (top-left logo)
- Primary color: ${brand.primaryColor}
- Footer: "${brand.companyName} | Confidential"

Project: "${config.projectName}"

Core Team (Inner Ring - Blue):
${config.coreTeam.map(s => `- ${s}`).join('\n')}

Decision Makers (Middle Ring - Gold):
${config.decisionMakers.map(s => `- ${s}`).join('\n')}

External/Users (Outer Ring - Gray):
${config.externalStakeholders.map(s => `- ${s}`).join('\n')}

Style:
- Professional consulting diagram (McKinsey/BCG style)
- Concentric circles layout
- Color-coded by influence level
- Clear labels for each stakeholder
- Connection lines showing relationships
- White background, branded header/footer
- Legend in corner

FONT REQUIREMENTS:
- All labels: BOLD, 14pt minimum, black text
- Title: 24pt minimum
- Use simple sans-serif fonts only
- High contrast text on all backgrounds`;
  },

  /**
   * Data Schema / ERD - Entity Relationship Diagram
   * Use in: Tech Spec Phase
   */
  dataSchema: (config: {
    title: string;
    entities: Array<{
      name: string;
      fields: Array<{ name: string; type: string; key?: 'PK' | 'FK' }>;
    }>;
    relationships?: Array<{ from: string; to: string; type: '1:1' | '1:N' | 'N:M' }>;
    brand?: BrandConfig;
  }) => {
    const brand = { ...DEFAULT_BRAND, ...config.brand };
    return `Create a professional consulting Entity Relationship Diagram (ERD).

BRANDING:
- Company: "${brand.companyName}" (top-left)
- Document type: "Technical Specification"
- Primary color: ${brand.primaryColor}
- Footer: "${brand.companyName} | ${brand.tagline}"

Title: "${config.title}"

Entities:
${config.entities.map(e => `
${e.name}:
${e.fields.map(f => `  - ${f.name} (${f.type})${f.key ? ` [${f.key}]` : ''}`).join('\n')}`).join('\n')}

${config.relationships ? `Relationships:
${config.relationships.map(r => `- ${r.from} ${r.type} ${r.to}`).join('\n')}` : ''}

Style:
- Professional technical diagram
- Standard ERD notation (boxes for entities)
- Crow's foot notation for relationships
- Primary keys marked with key icon
- Foreign keys with dashed lines
- Color-coded by domain/module
- White background, branded header/footer

FONT REQUIREMENTS:
- Entity names: BOLD, 16pt minimum
- Field names: 14pt minimum, readable
- Title: 24pt minimum, black
- Use monospace or simple sans-serif fonts
- High contrast - dark text on light boxes`;
  },

  /**
   * Flowchart - Process or data flow
   * Use in: PRD or Tech Spec Phase
   */
  flowchart: (config: {
    title: string;
    steps: Array<{
      id: string;
      label: string;
      type: 'start' | 'end' | 'process' | 'decision' | 'io';
    }>;
    connections: Array<{ from: string; to: string; label?: string }>;
    brand?: BrandConfig;
  }) => {
    const brand = { ...DEFAULT_BRAND, ...config.brand };
    return `Create a professional consulting flowchart diagram.

BRANDING:
- Company: "${brand.companyName}" (top-left)
- Primary color: ${brand.primaryColor}
- Footer: "${brand.companyName} | Process Documentation"

Title: "${config.title}"

Steps:
${config.steps.map(s => `- ${s.id}: "${s.label}" [${s.type}]`).join('\n')}

Flow:
${config.connections.map(c => `- ${c.from} → ${c.to}${c.label ? ` (${c.label})` : ''}`).join('\n')}

Shape Legend:
- start/end: Rounded rectangles (green/red)
- process: Rectangles (blue)
- decision: Diamonds (orange)
- io: Parallelograms (gray)

Style:
- Professional consulting diagram
- Top-to-bottom or left-to-right flow
- Clear directional arrows
- Labels on decision branches (Yes/No)
- Consistent spacing
- White background, branded header/footer

FONT REQUIREMENTS:
- Step labels: BOLD, 14pt minimum, centered in shapes
- Title: 24pt minimum
- Branch labels (Yes/No): 12pt minimum, clear contrast
- Use simple sans-serif fonts only
- Dark text on light shape fills`;
  },

  /**
   * System Architecture - Cloud/Microservices diagram
   * Use in: Tech Spec Phase
   */
  systemArchitecture: (config: {
    title: string;
    layers: Array<{
      name: string;
      components: Array<{ name: string; icon?: string }>;
    }>;
    externalServices?: string[];
    dataStores?: Array<{ name: string; type: 'sql' | 'nosql' | 'cache' | 'queue' }>;
    brand?: BrandConfig;
  }) => {
    const brand = { ...DEFAULT_BRAND, ...config.brand };
    return `Create a professional consulting system architecture diagram.

BRANDING:
- Company: "${brand.companyName}" (top-left)
- Document type: "System Architecture"
- Primary color: ${brand.primaryColor}
- Footer: "${brand.companyName} | ${brand.tagline} | Confidential"

Title: "${config.title}"

${config.layers.map(layer => `
${layer.name.toUpperCase()} LAYER:
${layer.components.map(c => `- ${c.name}${c.icon ? ` (${c.icon})` : ''}`).join('\n')}`).join('\n')}

${config.dataStores ? `DATA STORES:
${config.dataStores.map(d => `- ${d.name} [${d.type}]`).join('\n')}` : ''}

${config.externalServices ? `EXTERNAL SERVICES:
${config.externalServices.map(s => `- ${s}`).join('\n')}` : ''}

Style:
- Professional consulting architecture diagram
- Layered architecture (clients at top, data at bottom)
- Standard cloud icons (AWS/GCP style)
- Solid arrows for sync calls
- Dashed arrows for async/events
- Color-coded by layer
- White background with subtle grid, branded header/footer

FONT REQUIREMENTS:
- Component names: BOLD, 14pt minimum
- Layer labels: BOLD, 16pt minimum
- Title: 24pt minimum
- Use simple sans-serif fonts only
- High contrast text on all components`;
  },

  /**
   * User Flow - Screen-to-screen navigation
   * Use in: PRD Phase
   */
  userFlow: (config: {
    flowName: string;
    screens: string[];
    description: string;
    brand?: BrandConfig;
  }) => {
    const brand = { ...DEFAULT_BRAND, ...config.brand };
    return `Create a professional consulting user flow diagram.

BRANDING:
- Company: "${brand.companyName}" (top-left)
- Document type: "User Experience Flow"
- Primary color: ${brand.primaryColor}
- Footer: "${brand.companyName} | Product Requirements"

Flow: "${config.flowName}"
${config.description}

Screens (in order):
${config.screens.map((s, i) => `${i + 1}. ${s}`).join('\n')}

Style:
- Professional consulting UX diagram
- Left-to-right flow
- Screen thumbnails as rounded rectangles
- Clear numbered sequence
- Directional arrows between screens
- Decision points marked as diamonds
- Error/alternate paths in red
- White background, branded header/footer

FONT REQUIREMENTS:
- Screen names: BOLD, 14pt minimum
- Step numbers: BOLD, 16pt
- Title: 24pt minimum
- Use simple sans-serif fonts only
- Dark text on light backgrounds`;
  },
};

// ============================================
// Pre-built Prompt Templates (UI/UX - Legacy)
// ============================================

export const PromptTemplates = {
  /**
   * Mobile app onboarding screen
   */
  mobileOnboarding: (appName: string, feature: string) => `
Create a modern mobile app onboarding screen for "${appName}".

Feature Highlight: ${feature}

Requirements:
- Full-screen illustration or graphic
- Concise headline (max 6 words)
- Brief description (max 2 lines)
- Primary CTA button
- Secondary skip option
- Page indicator dots
- iPhone 16 Pro frame

Style: iOS 18 design language with vibrant colors and smooth gradients.`,

  /**
   * Dashboard overview screen
   */
  dashboard: (metrics: string[]) => `
Design a modern analytics dashboard showing key metrics.

Metrics to Display:
${metrics.map(m => `- ${m}`).join('\n')}

Requirements:
- Clean header with navigation
- Metric cards with trend indicators
- At least one chart visualization
- Data table or list section
- Filter/date range controls
- Responsive layout for desktop (1440px)

Style: Clean, professional, data-focused design with good information density.`,

  /**
   * E-commerce product card
   */
  productCard: (productType: string) => `
Design a product card component for an e-commerce ${productType} store.

Requirements:
- High-quality product image area
- Product name and brand
- Price with optional sale price
- Star rating indicator
- Quick add to cart button
- Wishlist/favorite icon
- Stock status indicator

Style: Modern e-commerce aesthetic, clean and conversion-focused.`,

  /**
   * Settings/preferences screen
   */
  settingsScreen: (categories: string[]) => `
Design a settings screen for a mobile application.

Setting Categories:
${categories.map(c => `- ${c}`).join('\n')}

Requirements:
- Clear category organization
- Toggle switches for on/off settings
- Disclosure indicators for nested screens
- User profile section at top
- Search functionality
- Consistent row heights and spacing

Style: iOS 18 Settings app inspired, clean and scannable.`,

  /**
   * Authentication flow
   */
  authScreen: (type: 'login' | 'signup' | 'forgot-password') => `
Design a ${type} screen for a mobile application.

Requirements:
${type === 'login' ? `
- Email/username input field
- Password input with show/hide toggle
- Remember me checkbox
- Forgot password link
- Primary login button
- Social login options (Google, Apple)
- Sign up link` : type === 'signup' ? `
- Full name input
- Email input
- Password input with strength indicator
- Confirm password input
- Terms acceptance checkbox
- Primary signup button
- Social signup options
- Already have account link` : `
- Email input field
- Clear instructions text
- Send reset link button
- Back to login link
- Success state indication`}

Style: Modern, trustworthy, with clear visual hierarchy and accessible form design.`,

  /**
   * Empty state screen
   */
  emptyState: (context: string, action: string) => `
Design an empty state screen for when there is no ${context}.

Requirements:
- Friendly illustration (not too complex)
- Clear headline explaining the state
- Helpful description text
- Primary action button: "${action}"
- Optional secondary action
- Centered layout

Style: Friendly, encouraging, not depressing. Use subtle colors and simple illustration.`,

  /**
   * Error state screen
   */
  errorState: (errorType: '404' | '500' | 'offline' | 'generic') => `
Design an error state screen for ${errorType === '404' ? 'page not found' :
  errorType === '500' ? 'server error' :
  errorType === 'offline' ? 'no internet connection' : 'a generic error'}.

Requirements:
- Appropriate illustration for the error type
- Clear error message
- Helpful suggestion text
- Retry/refresh button
- Go home/back button
- Support link if applicable

Style: Calm, reassuring, not alarming. Maintain brand consistency.`,
};

// ============================================
// Helper Functions
// ============================================

/**
 * Create a prompt for iterating on an existing design
 */
export function createIterationPrompt(
  feedback: string,
  aspectToChange: string
): string {
  return `Based on the previous design, make the following changes:

Feedback: ${feedback}

Specific Changes Required:
${aspectToChange}

Guidelines:
- Maintain the overall design language and style
- Only modify the aspects mentioned in the feedback
- Keep consistent with the established color scheme
- Preserve the layout structure unless explicitly asked to change it

Generate an updated version incorporating this feedback.`;
}

/**
 * Create a prompt for A/B test variations
 */
export function createVariationPrompt(
  originalDescription: string,
  variationType: 'color' | 'layout' | 'copy' | 'cta'
): string {
  const variationInstructions: Record<string, string> = {
    color: 'Create a variation with a different color scheme while maintaining the layout',
    layout: 'Create a variation with a different layout arrangement while keeping the same content',
    copy: 'Create a variation with different headline and description text',
    cta: 'Create a variation with different call-to-action button text, size, or position',
  };

  return `Create an A/B test variation of the following design.

Original Design:
${originalDescription}

Variation Type: ${variationType}
${variationInstructions[variationType]}

Requirements:
- Make the variation noticeably different but equally professional
- Maintain brand consistency
- Keep the core functionality intact
- Suitable for testing user preferences

Generate the variation design.`;
}
