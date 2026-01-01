/**
 * @file services/ContentExtractor/types.ts
 * @description Type definitions for ContentExtractor
 */

/**
 * Extracted text content from a Figma text layer
 */
export interface ExtractedText {
  layerName: string;
  propertyName?: string;
  value: string;
  fontFamily?: string;
  fontSize?: number;
  fontWeight?: number;
}

/**
 * Extracted variant information from a component
 */
export interface ExtractedVariant {
  name: string;
  properties: Record<string, string>;
  texts: ExtractedText[];
}

/**
 * Extracted component with all its content and metadata
 */
export interface ExtractedComponent {
  name: string;
  type: 'COMPONENT' | 'COMPONENT_SET' | 'INSTANCE';
  description?: string;
  properties: ComponentPropertyDefinition[];
  variants: ExtractedVariant[];
  defaultContent: Record<string, string>;
}

/**
 * Component property definition
 */
export interface ComponentPropertyDefinition {
  name: string;
  type: 'TEXT' | 'BOOLEAN' | 'VARIANT' | 'INSTANCE_SWAP';
  defaultValue?: string | boolean;
  variantOptions?: string[];
}

/**
 * Export format container with all output formats
 */
export interface ExportFormat {
  typescript: string;
  json: string;
  csv: string;
}
