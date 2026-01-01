/**
 * @file services/MCPClient/legacy.ts
 * @description Legacy component operations (deprecated, kept for compatibility)
 */

import type { MCPResponse } from '../../types';
import type { ComponentPayload, DesignToken, EnrichedComponentData } from '../../types';

type SendRequestFn = (method: string, params: unknown) => Promise<MCPResponse>;

/**
 * @deprecated Use exportToAID instead
 * Send a component to the backend for code generation
 */
export async function sendComponent(
  payload: ComponentPayload,
  send: SendRequestFn
): Promise<{
  success: boolean;
  componentId: string;
  generatedFiles?: string[];
  error?: string;
}> {
  const response = await send('tools/call', {
    name: 'generate_component',
    arguments: {
      component: payload.component,
      tokens: payload.tokens,
      metadata: payload.figmaMetadata,
    },
  });

  if (response.error) {
    return {
      success: false,
      componentId: payload.component.componentId,
      error: response.error.message,
    };
  }

  const result = response.result as Record<string, unknown>;
  return {
    success: true,
    componentId: payload.component.componentId,
    generatedFiles: result.files as string[],
  };
}

/**
 * Send design tokens to the backend
 */
export async function sendTokens(
  tokens: DesignToken[],
  format: 'css' | 'json' | 'tailwind',
  send: SendRequestFn
): Promise<{
  success: boolean;
  outputPath?: string;
  error?: string;
}> {
  const response = await send('tools/call', {
    name: 'generate_tokens',
    arguments: {
      tokens,
      format,
    },
  });

  if (response.error) {
    return {
      success: false,
      error: response.error.message,
    };
  }

  const result = response.result as Record<string, unknown>;
  return {
    success: true,
    outputPath: result.path as string,
  };
}

/**
 * Send batch of components
 */
export async function sendBatch(
  payloads: ComponentPayload[],
  send: SendRequestFn,
  onProgress?: (completed: number, total: number) => void
): Promise<{
  successful: string[];
  failed: Array<{ componentId: string; error: string }>;
}> {
  const successful: string[] = [];
  const failed: Array<{ componentId: string; error: string }> = [];

  for (let i = 0; i < payloads.length; i++) {
    const payload = payloads[i];

    try {
      const result = await sendComponent(payload, send);

      if (result.success) {
        successful.push(result.componentId);
      } else {
        failed.push({
          componentId: result.componentId,
          error: result.error || 'Unknown error',
        });
      }
    } catch (error) {
      failed.push({
        componentId: payload.component.componentId,
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }

    if (onProgress) {
      onProgress(i + 1, payloads.length);
    }
  }

  return { successful, failed };
}

/**
 * Validate component before sending
 */
export async function validateComponent(
  component: EnrichedComponentData,
  send: SendRequestFn
): Promise<{
  valid: boolean;
  errors: string[];
  warnings: string[];
}> {
  const response = await send('tools/call', {
    name: 'validate_component',
    arguments: { component },
  });

  if (response.error) {
    return {
      valid: false,
      errors: [response.error.message],
      warnings: [],
    };
  }

  const result = response.result as Record<string, unknown>;
  return {
    valid: result.valid as boolean,
    errors: (result.errors as string[]) || [],
    warnings: (result.warnings as string[]) || [],
  };
}
