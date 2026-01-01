/**
 * @file claudeClient.js
 * @description Wrapper for Anthropic SDK to generate component metadata using Claude AI.
 *              Handles API calls, response parsing, and availability checks.
 * @related
 *   - ../services/metadataGenerator.js - Calls generateMetadata() and isAvailable()
 *   - ../resources/SKILL.md - Format spec used in prompts
 * @created 2025-12-23
 */

const Anthropic = require('@anthropic-ai/sdk');

let client = null;

function getClient() {
  if (!client) {
    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      throw new Error('ANTHROPIC_API_KEY environment variable is required');
    }
    client = new Anthropic({ apiKey });
  }
  return client;
}

/**
 * Generate component metadata using Claude
 * @param {Object} componentData - Component data from Figma plugin
 * @param {string} skillPrompt - SKILL.md content for formatting
 * @returns {Promise<Object>} Generated metadata
 */
async function generateMetadata(componentData, skillPrompt) {
  const anthropic = getClient();

  const prompt = buildMetadataPrompt(componentData, skillPrompt);

  try {
    const response = await anthropic.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 2000,
      messages: [{
        role: 'user',
        content: prompt
      }]
    });

    return parseMetadataResponse(response);
  } catch (error) {
    console.error('[Claude] Error generating metadata:', error.message);
    throw error;
  }
}

/**
 * Build the prompt for metadata generation
 */
function buildMetadataPrompt(componentData, skillPrompt) {
  const { component, tokens, variants } = componentData;

  return `You are a design system expert. Generate comprehensive metadata for a Figma component following this exact format:

${skillPrompt}

## Component Information

**Name:** ${component.name}
**Type:** ${component.type}
**Variant Count:** ${component.variantCount || 0}
**Existing Description:** ${component.description || 'None'}

**Design Tokens:**
${JSON.stringify(tokens || [], null, 2)}

**Variants:**
${JSON.stringify(variants || [], null, 2)}

## Task

Generate a complete metadata description following the SKILL.md format. Include:
1. A 2-3 sentence primary description
2. tags (comma-separated keywords)
3. notes (usage guidelines)
4. ariaLabel (accessibility label)
5. category (button|navigation|form|layout|feedback|data-display|overlay)
6. level (atom|molecule|organism|template|page)
7. tokens (extracted from design tokens above)
8. states (default, hover, focus, disabled if applicable)
9. variants (if any)
10. dos (2-3 recommended practices)
11. donts (2-3 anti-patterns to avoid)
12. a11y (accessibility requirements)

Return ONLY the formatted metadata, no explanations. Use the exact YAML-like format from the SKILL.md.`;
}

/**
 * Parse Claude's response into structured metadata
 */
function parseMetadataResponse(response) {
  const content = response.content[0]?.text || '';

  // Extract description (before ---)
  const parts = content.split('---');
  const description = parts[0].trim();
  const metadataSection = parts[1] || '';

  // Parse key-value pairs
  const metadata = {
    description,
    formattedDescription: content,
    tags: extractField(metadataSection, 'tags'),
    notes: extractField(metadataSection, 'notes'),
    ariaLabel: extractField(metadataSection, 'ariaLabel'),
    category: extractField(metadataSection, 'category'),
    level: extractField(metadataSection, 'level'),
    priority: extractField(metadataSection, 'priority') || 'medium'
  };

  // Extract arrays
  metadata.dos = extractList(metadataSection, 'dos');
  metadata.donts = extractList(metadataSection, 'donts');
  metadata.a11y = extractList(metadataSection, 'a11y');
  metadata.states = extractList(metadataSection, 'states');

  // Extract variants and variant descriptions
  const variantData = extractVariants(metadataSection);
  metadata.variants = variantData.variants;
  metadata.variantDescriptions = variantData.variantDescriptions;

  return metadata;
}

/**
 * Extract a simple field value
 */
function extractField(text, fieldName) {
  const regex = new RegExp(`^${fieldName}:\\s*(.+)$`, 'mi');
  const match = text.match(regex);
  return match ? match[1].trim() : null;
}

/**
 * Extract a list of items
 */
function extractList(text, fieldName) {
  const items = [];
  const regex = new RegExp(`${fieldName}:[\\s\\S]*?(?=\\n\\w|$)`, 'i');
  const match = text.match(regex);

  if (match) {
    const listText = match[0];
    const itemRegex = /^\s*-\s*(.+)$/gm;
    let itemMatch;
    while ((itemMatch = itemRegex.exec(listText)) !== null) {
      items.push(itemMatch[1].trim());
    }
  }

  return items;
}

/**
 * Extract variants and their descriptions from metadata text
 * Handles formats like:
 *   - primary: "Primary button for main actions"
 *   - secondary: "Secondary variant"
 * Or simple list:
 *   - primary
 *   - secondary
 */
function extractVariants(text) {
  const variants = [];
  const variantDescriptions = {};

  // Find the variants section
  const regex = /variants:[\s\S]*?(?=\n\w+:|$)/i;
  const match = text.match(regex);

  if (match) {
    const variantSection = match[0];
    // Match "- variantName: description" or "- variantName"
    const itemRegex = /^\s*-\s*([^:\n]+)(?::\s*["']?([^"'\n]+)["']?)?$/gm;
    let itemMatch;

    while ((itemMatch = itemRegex.exec(variantSection)) !== null) {
      const variantName = itemMatch[1].trim();
      const variantDesc = itemMatch[2]?.trim() || '';

      if (variantName && variantName !== 'variants') {
        variants.push(variantName);
        if (variantDesc) {
          variantDescriptions[variantName] = variantDesc;
        }
      }
    }
  }

  return { variants, variantDescriptions };
}

/**
 * Check if Claude API is available
 */
function isAvailable() {
  return !!process.env.ANTHROPIC_API_KEY;
}

module.exports = {
  generateMetadata,
  isAvailable
};
