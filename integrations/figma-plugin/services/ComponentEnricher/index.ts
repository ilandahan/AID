/**
 * @file services/ComponentEnricher/index.ts
 * @description Main ComponentEnricher class facade and singleton
 */

import type {
  FigmaNodeInfo,
  ComponentClassification,
  EnrichedComponentData,
  DesignToken,
} from '../../types';
import { parseComponentDescription } from '../../descriptionParser';
import { inferProps } from './props';
import { extractVariants, detectStates, detectBreakpoints } from './variants';
import { extractAccessibility, extractDependencies, generateDescription } from './accessibility';

// Re-export everything for external consumers
export * from './types';
export * from './config';
export * from './utils';
export * from './props';
export * from './variants';
export * from './accessibility';

/**
 * ComponentEnricher - Enriches Figma nodes with metadata for code generation
 *
 * This class orchestrates the various extraction and inference functions
 * to produce complete EnrichedComponentData from raw Figma node info.
 */
export class ComponentEnricher {
  /**
   * Enrich a Figma node with complete metadata
   */
  enrichComponent(
    nodeInfo: FigmaNodeInfo,
    classification: ComponentClassification,
    tokens: DesignToken[],
    rawDescription?: string
  ): EnrichedComponentData {
    // Parse description for metadata
    const parsedDesc = parseComponentDescription(rawDescription);

    // Infer props from node structure
    const inferredProps = inferProps(nodeInfo, classification);

    // Extract variants from component set
    const variants = extractVariants(nodeInfo);

    // Detect states
    const states = detectStates(nodeInfo, variants);

    // Detect breakpoints
    const breakpoints = detectBreakpoints(nodeInfo);

    // Extract accessibility info (merge with parsed ariaLabel)
    const accessibility = extractAccessibility(nodeInfo, classification);
    if (parsedDesc.ariaLabel) {
      accessibility.ariaLabel = parsedDesc.ariaLabel;
    }

    // Find dependencies (merge with external from description)
    const dependencies = extractDependencies(nodeInfo);
    if (parsedDesc.external.length > 0) {
      dependencies.external = [...new Set([...dependencies.external, ...parsedDesc.external])];
    }

    return {
      componentId: nodeInfo.id,
      componentName: nodeInfo.name,
      displayName: classification.suggestedName,
      description: parsedDesc.description || generateDescription(nodeInfo, classification),

      level: classification.level,
      category: classification.category,

      props: inferredProps,
      variants,

      tokens,

      states,
      breakpoints,

      dependencies,
      accessibility,

      // From parsed description
      tags: parsedDesc.tags,
      notes: parsedDesc.notes,
      customFields: parsedDesc.customFields,

      createdAt: new Date(),
      version: '1.0.0',
    };
  }
}

// Export singleton instance
export const componentEnricher = new ComponentEnricher();
