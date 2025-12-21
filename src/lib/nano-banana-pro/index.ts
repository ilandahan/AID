/**
 * Nano Banana Pro API Integration
 *
 * A TypeScript client for Google's Nano Banana Pro (Gemini 3 Pro Image)
 * Specialized for wireframe-to-UI and design generation workflows.
 *
 * @example
 * ```typescript
 * import { NanoBananaProClient, WireframePromptBuilder } from '@/lib/nano-banana-pro';
 *
 * const client = new NanoBananaProClient({
 *   apiKey: process.env.GOOGLE_AI_API_KEY!,
 *   provider: 'google',
 * });
 *
 * const result = await client.generateFromText(
 *   'A modern mobile banking app dashboard',
 *   { aspectRatio: '9:16', resolution: '2K' }
 * );
 * ```
 */

// Client
export { NanoBananaProClient } from './client';

// Prompt Builders
export {
  WireframePromptBuilder,
  PromptTemplates,
  createIterationPrompt,
  createVariationPrompt,
} from './prompts';

// Types
export type {
  // Config
  ApiProvider,
  NanoBananaProConfig,
  VertexAIConfig,

  // Request types
  AspectRatio,
  Resolution,
  ImageQuality,
  GenerationConfig,
  SafetySetting,

  // Response types
  GeneratedImage,
  GenerationResponse,

  // Wireframe types
  DesignSystem,
  DeviceFrame,
  WireframeStyle,
  WireframeOptions,
  UIComponentSpec,
  ScreenSpec,
} from './types';

// Error class
export { NanoBananaProError } from './types';
