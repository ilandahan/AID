/**
 * Nano Banana Pro API Integration
 *
 * A TypeScript client for Google's Nano Banana Pro (Gemini 3 Pro Image)
 * Specialized for AID methodology visual artifacts:
 * - Research slides and presentation graphics (Discovery Phase)
 * - Data schemas, ERDs, and flowcharts (Tech Spec Phase)
 * - System architecture diagrams (Tech Spec Phase)
 *
 * @example
 * ```typescript
 * import { createNanoBananaClient, isNanoBananaEnabled, AIDPromptTemplates } from '@/lib/nano-banana-pro';
 *
 * // Check if enabled before using
 * if (isNanoBananaEnabled()) {
 *   const client = createNanoBananaClient();
 *
 *   // Generate system architecture diagram
 *   const prompt = AIDPromptTemplates.systemArchitecture({
 *     title: 'E-Commerce Platform',
 *     layers: [
 *       { name: 'Client', components: [{ name: 'Web App' }, { name: 'Mobile App' }] },
 *       { name: 'API', components: [{ name: 'API Gateway' }] },
 *     ],
 *     dataStores: [{ name: 'PostgreSQL', type: 'sql' }],
 *   });
 *
 *   const result = await client.generateFromText(prompt, { aspectRatio: '16:9' });
 * }
 * ```
 */

import { NanoBananaProClient } from './client';
import type { NanoBananaProConfig, ApiProvider } from './types';

// Client
export { NanoBananaProClient } from './client';

/**
 * Check if Nano Banana Pro is enabled and configured
 * Returns true only if ENABLE_NANO_BANANA=true and required keys are set
 */
export function isNanoBananaEnabled(): boolean {
  const enabled = process.env.ENABLE_NANO_BANANA === 'true';
  if (!enabled) return false;

  const provider = process.env.NANO_BANANA_PROVIDER as ApiProvider | undefined;

  switch (provider) {
    case 'google':
      return !!process.env.GOOGLE_AI_API_KEY;
    case 'aimlapi':
      return !!process.env.AIML_API_KEY;
    case 'vertex':
      return !!process.env.VERTEX_PROJECT_ID && !!process.env.VERTEX_LOCATION;
    default:
      return false;
  }
}

/**
 * Create a Nano Banana Pro client from environment variables
 * Throws if not properly configured - use isNanoBananaEnabled() to check first
 */
export function createNanoBananaClient(): NanoBananaProClient {
  const provider = process.env.NANO_BANANA_PROVIDER as ApiProvider;

  if (!provider) {
    throw new Error(
      'NANO_BANANA_PROVIDER not set. Set to "google", "aimlapi", or "vertex"'
    );
  }

  let config: NanoBananaProConfig;

  switch (provider) {
    case 'google':
      if (!process.env.GOOGLE_AI_API_KEY) {
        throw new Error('GOOGLE_AI_API_KEY not set');
      }
      config = {
        provider: 'google',
        apiKey: process.env.GOOGLE_AI_API_KEY,
      };
      break;

    case 'aimlapi':
      if (!process.env.AIML_API_KEY) {
        throw new Error('AIML_API_KEY not set');
      }
      config = {
        provider: 'aimlapi',
        apiKey: process.env.AIML_API_KEY,
      };
      break;

    case 'vertex':
      if (!process.env.VERTEX_PROJECT_ID || !process.env.VERTEX_LOCATION) {
        throw new Error('VERTEX_PROJECT_ID and VERTEX_LOCATION must be set');
      }
      config = {
        provider: 'vertex',
        apiKey: '', // Not used for Vertex
        vertex: {
          projectId: process.env.VERTEX_PROJECT_ID,
          location: process.env.VERTEX_LOCATION,
          accessToken: process.env.VERTEX_ACCESS_TOKEN,
        },
      };
      break;

    default:
      throw new Error(
        `Invalid NANO_BANANA_PROVIDER: ${provider}. Use "google", "aimlapi", or "vertex"`
      );
  }

  return new NanoBananaProClient(config);
}

// Prompt Builders
export {
  // Primary - AID methodology templates
  AIDPromptTemplates,
  // Legacy - UI/UX templates
  WireframePromptBuilder,
  PromptTemplates,
  createIterationPrompt,
  createVariationPrompt,
} from './prompts';

// Brand configuration type
export type { BrandConfig } from './prompts';

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
