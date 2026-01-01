/**
 * @file services/ComponentEnricher/types.ts
 * @description Type definitions for ComponentEnricher
 */

import type { PropDefinition } from '../../types';

/**
 * Internal representation of an inferred prop
 */
export interface InferredProp {
  name: string;
  type: PropDefinition['type'];
  required: boolean;
  defaultValue?: unknown;
  enumValues?: string[];
  description: string;
  source: 'text' | 'variant' | 'visibility' | 'slot' | 'interactive';
}

// Re-export types from main types file for convenience
export type {
  FigmaNodeInfo,
  FigmaNodeProperties,
  ComponentClassification,
  EnrichedComponentData,
  PropDefinition,
  VariantDefinition,
  DesignToken,
  AtomicLevel,
} from '../../types';
