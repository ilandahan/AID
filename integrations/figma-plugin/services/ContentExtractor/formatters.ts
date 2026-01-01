/**
 * @file services/ContentExtractor/formatters.ts
 * @description Export formatters for different output formats
 */

import type { ExtractedComponent, ExportFormat } from './types';
import { toVariableName, toCamelCase, escapeString } from './utils';

/**
 * Generate TypeScript content file
 */
export function toTypeScript(components: ExtractedComponent[]): string {
  let output = '// Auto-generated content from Figma\n';
  output += '// Generated at: ' + new Date().toISOString() + '\n\n';

  for (const component of components) {
    const varName = toVariableName(component.name);

    // Generate interface
    output += `export interface ${varName}Content {\n`;
    for (const [key] of Object.entries(component.defaultContent)) {
      output += `  ${toCamelCase(key)}: string;\n`;
    }
    output += '}\n\n';

    // Generate default content
    output += `export const ${varName}Content: ${varName}Content = {\n`;
    for (const [key, value] of Object.entries(component.defaultContent)) {
      output += `  ${toCamelCase(key)}: "${escapeString(value)}",\n`;
    }
    output += '};\n\n';
  }

  return output;
}

/**
 * Generate JSON content file
 */
export function toJSON(components: ExtractedComponent[]): string {
  const content: Record<string, unknown> = {};

  for (const component of components) {
    const key = toVariableName(component.name);
    content[key] = {
      _meta: {
        name: component.name,
        type: component.type,
        description: component.description,
        properties: component.properties.map(p => p.name),
        variantCount: component.variants.length
      },
      content: component.defaultContent
    };
  }

  return JSON.stringify(content, null, 2);
}

/**
 * Generate CSV content file
 */
export function toCSV(components: ExtractedComponent[]): string {
  const rows: string[][] = [['Component', 'Property', 'Value']];

  for (const component of components) {
    for (const [key, value] of Object.entries(component.defaultContent)) {
      rows.push([component.name, key, value]);
    }
  }

  return rows.map(row =>
    row.map(cell => `"${cell.replace(/"/g, '""')}"`).join(',')
  ).join('\n');
}

/**
 * Generate all export formats
 */
export function exportAllFormats(components: ExtractedComponent[]): ExportFormat {
  return {
    typescript: toTypeScript(components),
    json: toJSON(components),
    csv: toCSV(components)
  };
}
