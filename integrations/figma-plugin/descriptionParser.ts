/**
 * @file descriptionParser.ts
 * @description Parser for structured metadata in Figma component description fields.
 *              Extracts tags, notes, aria labels, and custom fields from YAML-like format.
 * @created 2024-12
 * @related
 *   - ./ComponentAuditor.ts - Uses parsed metadata for auditing
 *   - ../types/index.ts - Type definitions for metadata
 *
 * @format
 *   Expected description format:
 *   ```
 *   Main description text here.
 *   ---
 *   tags: button, primary, interactive
 *   notes: Additional notes
 *   ariaLabel: Click to submit
 *   category: button
 *   level: atom
 *   ```
 */

export interface ParsedDescription {
  description: string;
  tags: string[];
  notes: string;
  ariaLabel: string | null;
  external: string[];
  customFields: Record<string, string>;
}

/**
 * Parse Figma component description field
 * 
 * Expected format:
 * ```
 * Main description text here.
 * Can be multiple lines.
 * 
 * ---
 * tags: button, cta, primary
 * notes: Usage guidelines here
 * ariaLabel: Close dialog
 * external: lucide-react, framer-motion
 * customField: custom value
 * ```
 */
export function parseComponentDescription(rawDescription: string | undefined): ParsedDescription {
  const result: ParsedDescription = {
    description: '',
    tags: [],
    notes: '',
    ariaLabel: null,
    external: [],
    customFields: {},
  };
  
  if (!rawDescription) {
    return result;
  }
  
  // Split by separator (--- or ===)
  const parts = rawDescription.split(/\n[-=]{3,}\n/);
  
  // First part is always the description
  result.description = parts[0].trim();
  
  // If there's a second part, parse the metadata
  if (parts.length > 1) {
    const metadataSection = parts[1];
    const lines = metadataSection.split('\n');
    
    for (const line of lines) {
      const trimmedLine = line.trim();
      if (!trimmedLine) continue;
      
      // Parse key: value format
      const colonIndex = trimmedLine.indexOf(':');
      if (colonIndex === -1) continue;
      
      const key = trimmedLine.substring(0, colonIndex).trim().toLowerCase();
      const value = trimmedLine.substring(colonIndex + 1).trim();
      
      switch (key) {
        case 'tags':
        case 'tag':
          result.tags = value.split(',').map(t => t.trim()).filter(Boolean);
          break;
          
        case 'notes':
        case 'note':
        case 'usage':
          result.notes = value;
          break;
          
        case 'arialabel':
        case 'aria-label':
        case 'aria':
          result.ariaLabel = value || null;
          break;
          
        case 'external':
        case 'dependencies':
        case 'deps':
          result.external = value.split(',').map(d => d.trim()).filter(Boolean);
          break;
          
        default:
          // Store as custom field
          result.customFields[key] = value;
          break;
      }
    }
  }
  
  return result;
}

/**
 * Format metadata back to Figma description format
 */
export function formatComponentDescription(data: Partial<ParsedDescription>): string {
  const lines: string[] = [];
  
  // Main description
  if (data.description) {
    lines.push(data.description);
  }
  
  // Check if we have any metadata
  const hasMetadata = 
    (data.tags && data.tags.length > 0) ||
    data.notes ||
    data.ariaLabel ||
    (data.external && data.external.length > 0) ||
    (data.customFields && Object.keys(data.customFields).length > 0);
  
  if (hasMetadata) {
    lines.push('');
    lines.push('---');
    
    if (data.tags && data.tags.length > 0) {
      lines.push(`tags: ${data.tags.join(', ')}`);
    }
    
    if (data.notes) {
      lines.push(`notes: ${data.notes}`);
    }
    
    if (data.ariaLabel) {
      lines.push(`ariaLabel: ${data.ariaLabel}`);
    }
    
    if (data.external && data.external.length > 0) {
      lines.push(`external: ${data.external.join(', ')}`);
    }
    
    if (data.customFields) {
      for (const [key, value] of Object.entries(data.customFields)) {
        lines.push(`${key}: ${value}`);
      }
    }
  }
  
  return lines.join('\n');
}

/**
 * Extract description from Figma node
 */
export function getNodeDescription(node: SceneNode): string | undefined {
  if ('description' in node) {
    return (node as ComponentNode | ComponentSetNode).description;
  }
  return undefined;
}

// ============================================
// Alternative: JSON in Description
// ============================================

/**
 * Parse JSON metadata from description
 * 
 * Format:
 * ```
 * Main description here
 * 
 * <!-- metadata
 * {
 *   "tags": ["button", "cta"],
 *   "notes": "Max 2 per page",
 *   "ariaLabel": "Close"
 * }
 * -->
 * ```
 */
export function parseJSONDescription(rawDescription: string | undefined): ParsedDescription {
  const result: ParsedDescription = {
    description: '',
    tags: [],
    notes: '',
    ariaLabel: null,
    external: [],
    customFields: {},
  };
  
  if (!rawDescription) {
    return result;
  }
  
  // Look for JSON block in HTML comment
  const jsonMatch = rawDescription.match(/<!--\s*metadata\s*([\s\S]*?)-->/);
  
  if (jsonMatch) {
    // Extract description (everything before the comment)
    const descriptionPart = rawDescription.substring(0, rawDescription.indexOf('<!--')).trim();
    result.description = descriptionPart;
    
    try {
      const metadata = JSON.parse(jsonMatch[1].trim());
      
      if (metadata.tags) result.tags = metadata.tags;
      if (metadata.notes) result.notes = metadata.notes;
      if (metadata.ariaLabel) result.ariaLabel = metadata.ariaLabel;
      if (metadata.external) result.external = metadata.external;
      
      // Copy any other fields as custom
      for (const [key, value] of Object.entries(metadata)) {
        if (!['tags', 'notes', 'ariaLabel', 'external'].includes(key)) {
          result.customFields[key] = String(value);
        }
      }
    } catch (e) {
      console.warn('Failed to parse JSON metadata:', e);
    }
  } else {
    // No JSON found, use simple format
    return parseComponentDescription(rawDescription);
  }
  
  return result;
}
