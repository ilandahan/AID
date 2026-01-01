/**
 * @file metadataGenerator.js
 * @description Generates component metadata using Claude AI with fallback templates.
 *              Follows SKILL.md format for structured component documentation.
 * @related
 *   - ../index.js - Main server, calls generateMetadata()
 *   - ../utils/claudeClient.js - Anthropic SDK wrapper for AI calls
 *   - ../resources/SKILL.md - Metadata format specification
 * @created 2025-12-23
 */

const claudeClient = require('../utils/claudeClient');
const fs = require('fs');
const path = require('path');

// Cache SKILL.md content
let skillPromptCache = null;

/**
 * Load SKILL.md content for Claude prompts
 */
function loadSkillPrompt() {
  if (skillPromptCache) {
    return skillPromptCache;
  }

  try {
    const skillPath = path.join(__dirname, '../resources/SKILL.md');
    skillPromptCache = fs.readFileSync(skillPath, 'utf-8');
    return skillPromptCache;
  } catch (error) {
    console.warn('[MetadataGenerator] SKILL.md not found, using inline format');
    return getInlineSkillFormat();
  }
}

/**
 * Inline fallback if SKILL.md file not available
 */
function getInlineSkillFormat() {
  return `
## Metadata Format

### Structure

\`\`\`yaml
[Primary description - 2-3 sentences]

---
tags: [search keywords]
notes: [usage guidelines]
ariaLabel: [accessibility label]
category: [button|navigation|form|layout|feedback|data-display|overlay]
level: [atom|molecule|organism|template|page]
priority: [critical|high|medium|low]

tokens:
  colors: [hex values]
  spacing: [padding, margin, gap]
  radius: [border-radius]
  typography: [font specs]

states:
  default: [description]
  hover: [description]
  focus: [description]
  disabled: [description]

variants:
  [Name]: [description]

dos:
  - [recommended practice]

donts:
  - [anti-pattern to avoid]

a11y:
  - [accessibility requirement]
\`\`\`
`;
}

/**
 * Generate metadata for a component using Claude AI
 * @param {Object} componentData - Component data from plugin
 * @returns {Promise<Object>} Generated metadata
 */
async function generateMetadata(componentData) {
  // Check if Claude is available
  if (!claudeClient.isAvailable()) {
    return generateFallbackMetadata(componentData);
  }

  try {
    const skillPrompt = loadSkillPrompt();
    const metadata = await claudeClient.generateMetadata(componentData, skillPrompt);

    // Generate property descriptions from component.properties
    // (Claude doesn't know about Figma property definitions, so we add them here)
    const { component, tokens: localTokens } = componentData;
    const category = metadata.category || classifyCategory(component?.name || 'Untitled');
    const propertyDescriptions = generatePropertyDescriptions(
      component?.properties || [],
      component?.name || 'Untitled',
      category
    );

    // CRITICAL FIX: Append property descriptions to formattedDescription
    // so they get saved to Figma and detected on re-analysis
    let formattedDescription = metadata.formattedDescription || metadata.description || '';
    if (propertyDescriptions && Object.keys(propertyDescriptions).length > 0) {
      formattedDescription = appendPropertyDescriptionsToFormatted(formattedDescription, propertyDescriptions);
      console.log('[MetadataGenerator] Appended property descriptions to formattedDescription');
    }

    // DUAL TOKEN EXTRACTION: Merge Claude tokens with locally extracted tokens
    // Primary: Claude's response tokens (semantic understanding)
    // Fallback: Local extraction from Figma node (accurate raw values)
    const mergedTokens = mergeTokens(metadata.tokens, localTokens);
    if (mergedTokens) {
      console.log('[MetadataGenerator] Tokens merged:', Object.keys(mergedTokens).join(', '));
    }

    return {
      success: true,
      ...metadata,
      formattedDescription,  // Override with property descriptions included
      propertyDescriptions,  // Also keep the separate object for UI display
      tokens: mergedTokens,  // Merged tokens (Claude primary, local fallback)
      source: 'claude'
    };
  } catch (error) {
    console.error('[MetadataGenerator] Claude error:', error.message);
    // Fall back to template-based generation
    return generateFallbackMetadata(componentData);
  }
}

/**
 * Append property descriptions to an existing formatted description
 * This ensures property descriptions are saved to Figma and detected on re-analysis
 * @param {string} formatted - Existing formatted description
 * @param {Object} propertyDescriptions - Property descriptions to append
 * @returns {string} Updated formatted description with properties section
 */
function appendPropertyDescriptionsToFormatted(formatted, propertyDescriptions) {
  if (!propertyDescriptions || Object.keys(propertyDescriptions).length === 0) {
    return formatted;
  }

  // Check if properties section already exists
  if (formatted.includes('\nproperties:')) {
    console.log('[MetadataGenerator] Properties section already exists, skipping append');
    return formatted;
  }

  // Build properties section in YAML format
  let propertiesSection = '\nproperties:\n';
  for (const [propName, propDesc] of Object.entries(propertyDescriptions)) {
    propertiesSection += `  ${propName}: "${propDesc}"\n`;
  }

  // Append to formatted description
  return formatted.trimEnd() + propertiesSection;
}

/**
 * Merge tokens from Claude's response with locally extracted tokens from Figma
 * Strategy: Claude tokens are PRIMARY (semantic understanding), local tokens are FALLBACK (accurate raw values)
 * This ensures tokens are ALWAYS populated - never empty in Dev Info tab
 *
 * @param {Object|null} claudeTokens - Tokens from Claude's response (may be object or undefined)
 * @param {Array|null} localTokens - Token array extracted locally from Figma node
 * @returns {Object|null} Merged tokens object
 */
function mergeTokens(claudeTokens, localTokens) {
  // Extract local tokens into formatted object
  const localFormatted = extractTokenInfo(localTokens);

  // If Claude returned tokens (as object with colors, spacing, etc.)
  const hasClaudeTokens = claudeTokens && typeof claudeTokens === 'object' &&
    (claudeTokens.colors || claudeTokens.spacing || claudeTokens.typography ||
     claudeTokens.radius || claudeTokens.shadows);

  // If neither source has tokens, return null
  if (!hasClaudeTokens && !localFormatted) {
    console.log('[MetadataGenerator] No tokens from either source');
    return null;
  }

  // If only Claude tokens exist, use them
  if (hasClaudeTokens && !localFormatted) {
    console.log('[MetadataGenerator] Using Claude tokens only');
    return claudeTokens;
  }

  // If only local tokens exist, use them
  if (!hasClaudeTokens && localFormatted) {
    console.log('[MetadataGenerator] Using local Figma tokens only (Claude returned none)');
    return localFormatted;
  }

  // MERGE: Claude is primary, local fills in gaps
  console.log('[MetadataGenerator] Merging Claude + local tokens');
  const merged = { ...localFormatted };  // Start with local as base

  // Claude's values override local for each category (primary source)
  if (claudeTokens.colors) merged.colors = claudeTokens.colors;
  if (claudeTokens.spacing) merged.spacing = claudeTokens.spacing;
  if (claudeTokens.typography) merged.typography = claudeTokens.typography;
  if (claudeTokens.radius) merged.radius = claudeTokens.radius;
  if (claudeTokens.shadows) merged.shadows = claudeTokens.shadows;

  return merged;
}

/**
 * Generate fallback metadata without AI
 * Uses templates and component analysis
 */
function generateFallbackMetadata(componentData) {
  const { component, tokens, variants } = componentData;
  const name = component.name || 'Untitled';
  const type = component.type || 'COMPONENT';

  // Classify level
  const level = classifyLevel(component, variants);

  // Classify category
  const category = classifyCategory(name);

  // Generate description
  const description = generateDescription(name, type, variants);

  // Generate tags
  const tags = generateTags(name, category, level);

  // Extract token info
  const tokenInfo = extractTokenInfo(tokens);

  // Generate variant descriptions (for variant OPTIONS like Size=Full)
  const variantData = generateVariantDescriptions(variants, name, category);

  // Generate property descriptions (for PROPERTIES like Size, Style, State)
  // Use component.properties (property definitions) NOT variants (variant instances)
  const propertyDescriptions = generatePropertyDescriptions(component.properties || [], name, category);

  // Generate accessibility metadata BEFORE building formatted description
  const ariaLabel = generateAriaLabel(name);
  const a11yGuidelines = generateA11y(category);

  // Build formatted description (now includes all a11y fields)
  const formattedDescription = buildFormattedDescription({
    description,
    tags,
    category,
    level,
    tokens: tokenInfo,
    variants: variantData.enrichedVariants,
    properties: propertyDescriptions,
    ariaLabel,
    a11y: a11yGuidelines
  });

  // Generate states and specs objects for UI accessibility display
  const states = {
    default: 'Base appearance when not interacting',
    hover: 'Appearance when cursor hovers over element',
    focus: 'Visible focus indicator for keyboard navigation',
    active: 'Appearance during click/tap interaction',
    disabled: 'Appearance when element is not interactive'
  };

  const specs = {
    contrast: 'Ensure 4.5:1 minimum contrast ratio for text',
    touchTarget: 'Minimum 44x44px touch target for interactive elements',
    spacing: 'Follow design system spacing tokens'
  };

  return {
    success: true,
    description,
    formattedDescription,
    tags: tags.join(', '),
    notes: `Use this ${level} for ${category} purposes.`,
    ariaLabel,  // Use pre-generated value
    category,
    level,
    priority: 'medium',
    dos: generateDos(category, level),
    donts: generateDonts(category, level),
    a11y: a11yGuidelines,  // Use pre-generated value
    states,  // Added for UI Focus States display
    specs,   // Added for UI Contrast Info display
    variants: variantData.variantNames,
    variantCount: variants?.length || 0,  // Include variant count for UI stats
    variantDescriptions: variantData.variantDescriptions,
    propertyDescriptions: propertyDescriptions,
    tokens: tokenInfo,  // Include extracted design tokens
    source: 'fallback'
  };
}

/**
 * Classify the atomic design level
 *
 * Priority order:
 * 1. Variant complexity (many variants = higher complexity regardless of name)
 * 2. Name-based patterns
 * 3. Child count fallback
 */
function classifyLevel(component, variants) {
  const variantCount = variants?.length || component.variantCount || 0;
  const childCount = component.childCount || 0;
  const name = (component.name || '').toLowerCase();

  // FIRST: Check variant complexity - ComponentSets with many variants are complex
  // regardless of their name (e.g., "Button" with 16 variants is not an atom)
  if (variantCount >= 10) return 'organism';
  if (variantCount >= 5) return 'molecule';

  // SECOND: Name-based classification (only for simpler components)
  if (/^(icon|button|input|label|badge|chip|avatar|divider)/i.test(name)) {
    // Even "atom" patterns can be molecules if they have several variants
    if (variantCount >= 3) return 'molecule';
    return 'atom';
  }
  if (/^(card|form-field|list-item|menu-item|search|dropdown)/i.test(name)) {
    return 'molecule';
  }
  if (/^(header|footer|sidebar|modal|dialog|form|table|nav)/i.test(name)) {
    return 'organism';
  }
  if (/^(page|layout|template|view)/i.test(name)) {
    return 'template';
  }

  // THIRD: Complexity-based fallback for unrecognized names
  if (variantCount === 0 && childCount <= 3) return 'atom';
  if (variantCount <= 4 && childCount <= 10) return 'molecule';
  return 'organism';
}

/**
 * Classify the component category
 */
function classifyCategory(name) {
  const nameLower = name.toLowerCase();

  if (/button|btn|cta/i.test(nameLower)) return 'button';
  if (/nav|menu|link|breadcrumb/i.test(nameLower)) return 'navigation';
  if (/input|form|field|select|checkbox|radio|textarea/i.test(nameLower)) return 'form';
  if (/card|grid|flex|container|row|column|stack/i.test(nameLower)) return 'layout';
  if (/alert|toast|notification|message|error|success/i.test(nameLower)) return 'feedback';
  if (/table|list|chart|graph|stat|metric/i.test(nameLower)) return 'data-display';
  if (/modal|dialog|popup|overlay|drawer/i.test(nameLower)) return 'overlay';

  return 'layout';
}

/**
 * Generate a description for the component
 */
function generateDescription(name, type, variants) {
  const baseName = name.split('/').pop();
  const variantCount = variants?.length || 0;

  let description = `${baseName} component for use in the design system.`;

  if (type === 'COMPONENT_SET' && variantCount > 0) {
    description += ` Includes ${variantCount} variant(s) for different states and sizes.`;
  }

  return description;
}

/**
 * Generate search tags
 */
function generateTags(name, category, level) {
  const baseName = name.split('/').pop().toLowerCase();
  const words = baseName.split(/[-_\s]+/);

  return [
    ...words,
    category,
    level,
    'component',
    'figma'
  ].filter((v, i, a) => a.indexOf(v) === i); // Unique
}

/**
 * Generate ARIA label
 */
function generateAriaLabel(name) {
  const baseName = name.split('/').pop();
  return baseName.replace(/[-_]/g, ' ').replace(/([A-Z])/g, ' $1').trim();
}

/**
 * Extract token information
 * Tokens from client have 'category' field (color, spacing, typography, borderRadius, shadow)
 */
function extractTokenInfo(tokens) {
  if (!tokens || tokens.length === 0) {
    return null;
  }

  const info = {};

  // Support both 'type' and 'category' fields for compatibility
  const getCategory = (t) => t.category || t.type;

  const colors = tokens.filter(t => getCategory(t) === 'color');
  if (colors.length > 0) {
    info.colors = colors.map(t => t.value).join(', ');
  }

  const spacing = tokens.filter(t => getCategory(t) === 'spacing');
  if (spacing.length > 0) {
    info.spacing = spacing.map(t => `${t.name}: ${t.value}`).join(', ');
  }

  const typography = tokens.filter(t => getCategory(t) === 'typography');
  if (typography.length > 0) {
    info.typography = typography.map(t => t.value).join(', ');
  }

  // Add border radius support
  const radius = tokens.filter(t => getCategory(t) === 'borderRadius');
  if (radius.length > 0) {
    info.radius = radius.map(t => t.value).join(', ');
  }

  // Add shadow support
  const shadows = tokens.filter(t => getCategory(t) === 'shadow');
  if (shadows.length > 0) {
    info.shadows = shadows.map(t => t.value).join(', ');
  }

  return Object.keys(info).length > 0 ? info : null;
}

/**
 * Build formatted description in SKILL.md format
 * Includes all accessibility metadata fields that componentAuditor checks for
 */
function buildFormattedDescription(data) {
  let output = `${data.description}\n\n---\n`;

  output += `tags: ${data.tags.join(', ')}\n`;
  output += `notes: Use appropriately in ${data.category} contexts\n`;
  output += `category: ${data.category}\n`;
  output += `level: ${data.level}\n`;
  output += `priority: medium\n`;

  // ACCESSIBILITY METADATA - Required by componentAuditor for score calculation
  // ariaLabel field (checked by: present.includes('ariaLabel'))
  if (data.ariaLabel) {
    output += `ariaLabel: ${data.ariaLabel}\n`;
  }

  // a11y guidelines (checked by: present.includes('a11y'))
  if (data.a11y && data.a11y.length > 0) {
    output += `a11y:\n`;
    data.a11y.forEach(guideline => {
      output += `  - ${guideline}\n`;
    });
  }

  // States section with focus info (checked by: description.includes('states:') && /focus\s*:/i.test(description))
  output += `\nstates:\n`;
  output += `  default: Base appearance when not interacting\n`;
  output += `  hover: Appearance when cursor hovers over element\n`;
  output += `  focus: Visible focus indicator for keyboard navigation\n`;
  output += `  active: Appearance during click/tap interaction\n`;
  output += `  disabled: Appearance when element is not interactive\n`;

  // Specs section with contrast info (checked by: description.includes('specs:') && /contrast\s*:/i.test(description))
  output += `\nspecs:\n`;
  output += `  contrast: Ensure 4.5:1 minimum contrast ratio for text\n`;
  output += `  touchTarget: Minimum 44x44px touch target for interactive elements\n`;
  output += `  spacing: Follow design system spacing tokens\n`;

  if (data.tokens) {
    output += `\ntokens:\n`;
    if (data.tokens.colors) output += `  colors: ${data.tokens.colors}\n`;
    if (data.tokens.spacing) output += `  spacing: ${data.tokens.spacing}\n`;
    if (data.tokens.typography) output += `  typography: ${data.tokens.typography}\n`;
  }

  // Properties section (e.g., Size, Style, State)
  if (data.properties && Object.keys(data.properties).length > 0) {
    output += `\nproperties:\n`;
    for (const [propName, propDesc] of Object.entries(data.properties)) {
      output += `  ${propName}: "${propDesc}"\n`;
    }
  }

  // Variants section (e.g., Size=Full, Style=Primary)
  if (data.variants && data.variants.length > 0) {
    output += `\nvariants:\n`;
    data.variants.forEach(v => {
      // Use enriched variant with description, or fallback
      const name = v.name || v;
      const desc = v.description || 'Variant option';
      output += `  - ${name}: "${desc}"\n`;
    });
  }

  return output;
}

/**
 * Generate dos based on category and level
 */
function generateDos(category, level) {
  const dos = [];

  if (level === 'atom') {
    dos.push('Use consistently across the application');
    dos.push('Keep styling minimal and reusable');
  }

  if (category === 'button') {
    dos.push('Use clear, action-oriented labels');
    dos.push('Maintain consistent sizing');
  }

  if (category === 'form') {
    dos.push('Provide clear labels and error states');
    dos.push('Ensure keyboard accessibility');
  }

  return dos.length > 0 ? dos : ['Follow design system guidelines', 'Test across viewports'];
}

/**
 * Generate donts based on category and level
 */
function generateDonts(category, level) {
  const donts = [];

  if (level === 'atom') {
    donts.push('Avoid adding complex logic');
    donts.push('Do not override base styles inline');
  }

  if (category === 'button') {
    donts.push('Avoid multiple primary buttons in one section');
    donts.push('Do not use without proper contrast');
  }

  if (category === 'form') {
    donts.push('Never submit without validation');
    donts.push('Avoid placeholder-only labels');
  }

  return donts.length > 0 ? donts : ['Do not use outside intended context', 'Avoid breaking accessibility'];
}

/**
 * Generate a11y requirements based on category
 */
function generateA11y(category) {
  const a11y = ['Ensure 4.5:1 contrast ratio for text'];

  if (category === 'button' || category === 'form') {
    a11y.push('44x44px minimum touch target');
    a11y.push('Visible focus indicator required');
  }

  if (category === 'navigation') {
    a11y.push('Support keyboard navigation');
    a11y.push('Announce current page state');
  }

  return a11y;
}

/**
 * Generate variant descriptions based on variant properties
 * Creates meaningful descriptions for each variant option
 *
 * Handles TWO input formats:
 * - Format A (property definitions): { name: "Size", options: ["Small", "Large"] }
 * - Format B (variant instances): { name: "Size=Small", properties: {"Size": "Small"} }
 */
function generateVariantDescriptions(variants, componentName, category) {
  const variantNames = [];
  const variantDescriptions = {};
  const enrichedVariants = [];

  if (!variants || variants.length === 0) {
    return { variantNames, variantDescriptions, enrichedVariants };
  }

  // Description templates based on property names
  const descriptionTemplates = {
    size: {
      'full': 'Full-width variant, spans container width',
      'large': 'Large size variant for prominent display',
      'medium': 'Standard medium size for general use',
      'small': 'Compact small size for dense layouts',
      'xs': 'Extra small for minimal footprint',
      'xl': 'Extra large for maximum impact',
      'default': (value) => `${capitalize(value)} size variant`
    },
    style: {
      'primary': 'Primary style for main actions and emphasis',
      'secondary': 'Secondary style for supporting actions',
      'outline': 'Outline/bordered style variant',
      'outlined': 'Outlined style with transparent background',
      'ghost': 'Ghost/transparent style for subtle presence',
      'link': 'Link-styled variant without button appearance',
      'destructive': 'Destructive/danger style for critical actions',
      'default': (value) => `${capitalize(value)} style variant`
    },
    state: {
      'default': 'Default/rest state appearance',
      'rest': 'Rest state when not interacting',
      'hover': 'Hover state when cursor is over element',
      'focus': 'Focus state for keyboard navigation',
      'active': 'Active/pressed state during interaction',
      'disabled': 'Disabled state when not interactive',
      'loading': 'Loading state during async operations',
      'error': 'Error state for validation failures',
      'default': (value) => `${capitalize(value)} interaction state`
    },
    variant: {
      'default': (value) => `${capitalize(value)} variant option`
    },
    type: {
      'default': (value) => `${capitalize(value)} type variant`
    },
    // Common property names in Figma
    'property 1': {
      'default': (value) => `${capitalize(value)} variant option`
    },
    'property 2': {
      'default': (value) => `${capitalize(value)} variant option`
    }
  };

  /**
   * Generate description for a single variant
   */
  function getVariantDescription(propName, optionValue) {
    const propNameLower = propName.toLowerCase();
    const optionLower = optionValue.toLowerCase();

    const template = descriptionTemplates[propNameLower];

    if (template) {
      if (template[optionLower]) {
        return template[optionLower];
      } else if (template['default']) {
        return template['default'](optionValue);
      }
    }

    // Generic description for unknown properties
    return `${capitalize(optionValue)} ${propName} variant for ${category} component`;
  }

  for (const variant of variants) {
    const variantName = variant.name || '';
    const options = variant.options || [];

    // Format B: Variant instance with name like "Property 1=Jira"
    if (variantName.includes('=') && options.length === 0) {
      const [propName, optionValue] = variantName.split('=');
      const variantKey = variantName; // Already in "Property=Value" format

      if (propName && optionValue) {
        variantNames.push(variantKey);

        const description = getVariantDescription(propName, optionValue);

        variantDescriptions[variantKey] = description;
        enrichedVariants.push({
          name: variantKey,
          property: propName,
          value: optionValue,
          description
        });
      }
    }
    // Format A: Property definition with options array
    else if (options.length > 0) {
      for (const option of options) {
        const variantKey = `${variantName}=${option}`;
        variantNames.push(variantKey);

        const description = getVariantDescription(variantName, option);

        variantDescriptions[variantKey] = description;
        enrichedVariants.push({
          name: variantKey,
          property: variantName,
          value: option,
          description
        });
      }
    }
  }

  console.log('[MetadataGenerator] Generated variant descriptions:', {
    inputCount: variants.length,
    outputCount: Object.keys(variantDescriptions).length,
    keys: Object.keys(variantDescriptions)
  });

  return { variantNames, variantDescriptions, enrichedVariants };
}

/**
 * Generate descriptions for variant PROPERTIES (not values)
 * Properties are things like "Size", "Style", "State"
 * @param {Array} variants - Variant property array
 * @param {string} componentName - Name of the component
 * @param {string} category - Component category
 * @returns {Object} Property descriptions keyed by property name
 */
function generatePropertyDescriptions(properties, componentName, category) {
  const propertyDescriptions = {};

  console.log('[METADATA] generatePropertyDescriptions called with:', {
    propertiesCount: properties?.length || 0,
    properties: JSON.stringify(properties?.slice(0, 5) || []),
    componentName,
    category
  });

  if (!properties || properties.length === 0) {
    console.log('[METADATA] No properties to generate descriptions for');
    return propertyDescriptions;
  }

  // Description templates for common property NAMES
  const propertyTemplates = {
    'size': 'Controls the overall dimensions and scale of the component',
    'style': 'Defines the visual appearance and styling variant',
    'state': 'Represents the current interaction or behavioral state',
    'type': 'Specifies the functional type or purpose of the component',
    'variant': 'Selects between different visual or functional variations',
    'theme': 'Controls the color scheme and theming of the component',
    'color': 'Sets the primary color variant of the component',
    'icon': 'Determines which icon is displayed (if any)',
    'disabled': 'Indicates whether the component is in a disabled state',
    'loading': 'Shows if the component is in a loading state',
    'selected': 'Indicates the selection state of the component',
    'active': 'Shows if the component is currently active',
    'expanded': 'Controls the expanded/collapsed state',
    'orientation': 'Sets horizontal or vertical layout direction',
    'alignment': 'Controls content alignment within the component',
    'density': 'Adjusts the spacing density (compact, normal, comfortable)',
    'elevation': 'Controls the shadow/elevation level',
    'rounded': 'Adjusts the border radius/roundness',
    'subject': 'Indicates the subject or topic category of the component'
  };

  for (const prop of properties) {
    // Property definitions from client have: name, type, defaultValue, variantOptions
    const propName = prop.name || '';
    const propNameLower = propName.toLowerCase();

    // Only generate descriptions for VARIANT type properties (not BOOLEAN, TEXT, etc.)
    if (prop.type !== 'VARIANT') continue;

    // Find matching template or generate generic description
    let description = propertyTemplates[propNameLower];

    if (!description) {
      // Generate based on variantOptions if available
      const options = prop.variantOptions || [];
      if (options.length > 0) {
        const optionList = options.slice(0, 3).join(', ');
        const moreText = options.length > 3 ? ` and ${options.length - 3} more` : '';
        description = `Selects the ${propName} option (${optionList}${moreText})`;
      } else {
        description = `Controls the ${propName} property of the ${category} component`;
      }
    }

    propertyDescriptions[propName] = description;
    console.log(`[METADATA] Generated description for property "${propName}": ${description}`);
  }

  console.log('[METADATA] Final propertyDescriptions:', JSON.stringify(propertyDescriptions));
  return propertyDescriptions;
}

/**
 * Capitalize first letter of string
 */
function capitalize(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

module.exports = {
  generateMetadata,
  generateFallbackMetadata
};
