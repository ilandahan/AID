/**
 * @file services/ComponentAuditor/metadata-analysis.ts
 * @description Local metadata analysis for completeness checking
 */

import type { MetadataGapAnalysis, VariantInfo } from '../../types';

/**
 * Analyze metadata completeness locally
 */
export function analyzeMetadataLocal(node: SceneNode, description?: string): MetadataGapAnalysis {
  const componentName = node.name;
  const presentFields: string[] = [];
  const missingFields: string[] = [];
  const incompleteFields: string[] = [];

  // Check required fields in description
  if (description && description.length > 0) {
    presentFields.push('description');

    // Check for structured metadata
    if (description.includes('---')) {
      if (description.includes('tags:')) presentFields.push('tags');
      else missingFields.push('tags');

      if (description.includes('notes:')) presentFields.push('notes');
      else missingFields.push('notes');

      if (description.includes('category:')) presentFields.push('category');
      else missingFields.push('category');

      if (description.includes('level:')) presentFields.push('level');
      else missingFields.push('level');

      if (description.includes('ariaLabel:')) presentFields.push('ariaLabel');
      if (description.includes('a11y:')) presentFields.push('a11y');
      if (description.includes('tokens:')) presentFields.push('tokens');
      if (description.includes('dos:')) presentFields.push('dos');
      if (description.includes('donts:')) presentFields.push('donts');
    } else {
      // Has description but no structured metadata
      missingFields.push('tags', 'notes', 'category', 'level');
      incompleteFields.push('description (missing structured metadata)');
    }
  } else {
    missingFields.push('description', 'tags', 'notes', 'category', 'level');
  }

  // Check properties (variant property definitions)
  let totalProperties = 0;
  let propertiesWithDesc = 0;
  const propertiesMissingDesc: string[] = [];

  if (node.type === 'COMPONENT_SET' && 'componentPropertyDefinitions' in node) {
    const defs = (node as ComponentSetNode).componentPropertyDefinitions;
    for (const [propName, def] of Object.entries(defs)) {
      const propDef = def as { type: string; defaultValue?: string | boolean; variantOptions?: string[] };
      if (propDef.type === 'VARIANT') {
        totalProperties++;
        const cleanName = propName.replace(/#\d+:\d+$/, '');
        if (description && description.includes(`${cleanName}:`)) {
          propertiesWithDesc++;
        } else {
          propertiesMissingDesc.push(cleanName);
        }
      }
    }
  }

  // Check variants
  let totalVariants = 0;
  let variantsWithDesc = 0;
  const variantsMissingDesc: VariantInfo[] = [];

  if (node.type === 'COMPONENT_SET') {
    for (const child of node.children) {
      if (child.type === 'COMPONENT') {
        totalVariants++;
        const variantDesc = (child as ComponentNode).description;
        if (variantDesc && variantDesc.length > 0) {
          variantsWithDesc++;
        } else {
          variantsMissingDesc.push({
            name: child.name,
            nodeId: child.id,
            properties: {},
            hasDescription: false
          });
        }
      }
    }
  }

  // Calculate completeness score
  const requiredFields = ['description', 'tags', 'notes', 'category', 'level'];
  const presentRequired = requiredFields.filter(f => presentFields.includes(f)).length;
  const variantScore = totalVariants > 0 ? (variantsWithDesc / totalVariants) * 100 : 100;
  const fieldScore = (presentRequired / requiredFields.length) * 100;
  const completenessScore = Math.round((fieldScore * 0.6) + (variantScore * 0.4));

  return {
    componentName,
    completenessScore,
    componentSetLevel: {
      present: presentFields,
      missing: missingFields,
      incomplete: incompleteFields
    },
    variantLevel: {
      total: totalVariants,
      withDescription: variantsWithDesc,
      missingDescription: variantsMissingDesc
    },
    propertyLevel: {
      total: totalProperties,
      withDescription: propertiesWithDesc,
      missingDescription: propertiesMissingDesc
    },
    accessibilityMetadata: {
      hasAriaLabel: presentFields.includes('ariaLabel'),
      hasA11yNotes: presentFields.includes('a11y'),
      hasFocusStates: false, // Checked in audit
      hasContrastInfo: false
    }
  };
}
