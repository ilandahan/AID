/**
 * @file prompt-builder.ts
 * @description Builds prompts for Claude using loaded skills.
 * Constructs audit, analysis, and generation prompts.
 *
 * @related
 *   - ./skill-loader.ts - Loads skill content
 *   - ../tools/design-review.ts - Uses these prompts
 *   - ../../SKILL.md - Component metadata format
 */

import {
  SkillContext,
  extractMetadataFormat,
  extractExamples
} from './skill-loader.js';
import type { Locale } from '../i18n/messages.js';

export interface ComponentData {
  name: string;
  type: 'COMPONENT' | 'COMPONENT_SET' | 'INSTANCE';
  description?: string;
  variants?: VariantInfo[];
  tokens?: TokenInfo[];
  structure?: StructureInfo;
  figmaUrl?: string;
}

export interface VariantInfo {
  name: string;
  properties: Record<string, string>;
  description?: string;
}

export interface TokenInfo {
  name: string;
  value: string;
  category: 'color' | 'spacing' | 'typography' | 'borderRadius' | 'shadow';
  cssVariable?: string;
}

export interface StructureInfo {
  hasAutoLayout: boolean;
  layerNames: string[];
  depth: number;
  childCount: number;
}

/**
 * Build the audit prompt for component quality review
 */
export function buildAuditPrompt(
  component: ComponentData,
  skills: SkillContext,
  locale: Locale = 'en'
): string {
  const metadataFormat = extractMetadataFormat(skills.componentMetadata);
  const examples = extractExamples(skills.componentMetadata);

  const languageInstruction = locale === 'he'
    ? 'Respond with issue messages in Hebrew. Keep technical terms in English.'
    : 'Respond in English.';

  return `You are a design system quality auditor using the Component Metadata Skill.

${languageInstruction}

## Component Metadata Format (from SKILL.md)

${metadataFormat}

## Component Being Reviewed

Name: ${component.name}
Type: ${component.type}
Existing Description: ${component.description || 'MISSING'}
Variants: ${component.variants ? JSON.stringify(component.variants, null, 2) : 'None'}
Structure: ${component.structure ? JSON.stringify(component.structure, null, 2) : 'Unknown'}
Tokens: ${component.tokens ? JSON.stringify(component.tokens, null, 2) : 'None extracted'}

## Quality Checks to Perform

### 1. Naming Convention (25 points max)
- Component name follows "Category / Type / Name" format
- Variant properties use PascalCase (Size, State, Style)
- Layer names are semantic (Label, Icon, Container - not Text 1, Frame 2)
- No typos in common terms

### 2. Structure (20 points max)
- Auto Layout usage (required for responsive)
- No unnecessary wrapper frames
- Consistent hierarchy across variants

### 3. Visual Consistency (15 points max)
- Font sizes consistent (no minor variations like 13.6px, 13.7px)
- Border radius uniform across variants
- Colors from design system tokens

### 4. Accessibility (25 points max)
- Focus state present (visible focus ring)
- Disabled state present
- Touch target minimum 44x44px
- ARIA label for icon-only components

### 5. Metadata Completeness (15 points max)
Required fields per SKILL.md:
- description (2-3 sentences)
- tags (searchable keywords)
- notes (usage guidelines)
- category (button|navigation|form|layout|feedback|data-display|overlay)
- level (atom|molecule|organism|template|page)

## Example of Good Metadata

${examples[0] || 'No example available'}

## Your Task

Analyze this component and return ONLY valid JSON (no markdown, no explanation):

{
  "scores": {
    "overall": 0-100,
    "naming": 0-25,
    "structure": 0-20,
    "visual": 0-15,
    "accessibility": 0-25,
    "metadata": 0-15
  },
  "issues": [
    {
      "id": "unique-id",
      "category": "naming|structure|visual|accessibility|metadata",
      "severity": "error|warning|info",
      "message": "Description of the issue",
      "location": "Component/Layer path",
      "suggestion": "How to fix it",
      "autoFixable": true|false
    }
  ],
  "exportReady": true|false,
  "blockers": ["List of blocking issues preventing export"]
}`;
}

/**
 * Build the metadata analysis prompt
 */
export function buildAnalysisPrompt(
  component: ComponentData,
  skills: SkillContext,
  locale: Locale = 'en'
): string {
  const metadataFormat = extractMetadataFormat(skills.componentMetadata);

  const languageInstruction = locale === 'he'
    ? 'Respond in Hebrew for user-facing messages. Keep metadata field names in English.'
    : 'Respond in English.';

  return `You are analyzing metadata completeness for a Figma component.

${languageInstruction}

## Required Metadata Format (from SKILL.md)

${metadataFormat}

## Component Data

Name: ${component.name}
Type: ${component.type}
Existing Description: ${component.description || 'NONE'}
Variants: ${component.variants?.map(v => v.name).join(', ') || 'None'}

## Your Task

Analyze the metadata completeness and return ONLY valid JSON:

{
  "componentName": "${component.name}",
  "completenessScore": 0-100,
  "componentSetLevel": {
    "present": ["list of fields that exist"],
    "missing": ["list of required fields missing"],
    "incomplete": ["list of fields that exist but are incomplete"]
  },
  "variantLevel": {
    "total": number,
    "withDescription": number,
    "missingDescription": [{ "name": "variant name", "properties": {} }]
  },
  "recommendations": [
    "Specific recommendation for improvement"
  ]
}`;
}

/**
 * Build the metadata generation prompt
 */
export function buildGenerationPrompt(
  component: ComponentData,
  skills: SkillContext,
  locale: Locale = 'en'
): string {
  const metadataFormat = extractMetadataFormat(skills.componentMetadata);
  const examples = extractExamples(skills.componentMetadata);

  const languageInstruction = locale === 'he'
    ? `Generate the primary description in Hebrew.
       Keep all field names (tags, notes, category, etc.) in English.
       Values like tags can be in English for searchability.`
    : 'Generate all content in English.';

  return `You are generating comprehensive metadata for a Figma component following the SKILL.md format.

${languageInstruction}

## Target Format (YAML)

${metadataFormat}

## Examples from Design System

${examples.slice(0, 2).join('\n\n---\n\n')}

## Component to Document

Name: ${component.name}
Type: ${component.type}
Variants: ${component.variants ? JSON.stringify(component.variants, null, 2) : 'None'}
Extracted Tokens: ${component.tokens ? JSON.stringify(component.tokens, null, 2) : 'None'}

## Your Task

Generate complete metadata following the SKILL.md format. Return ONLY valid JSON:

{
  "description": "2-3 sentence description of component purpose and usage",
  "tags": ["searchable", "keywords", "for", "finding", "component"],
  "notes": "Usage guidelines - when to use and when not to use",
  "ariaLabel": "Accessibility label for screen readers (if interactive)",
  "category": "button|navigation|form|layout|feedback|data-display|overlay",
  "level": "atom|molecule|organism|template|page",
  "priority": "critical|high|medium|low",
  "tokens": {
    "colors": ["#hex1", "#hex2"],
    "spacing": ["padding values"],
    "typography": ["font specs"]
  },
  "states": {
    "default": "Description of default state",
    "hover": "Description of hover state",
    "focus": "Description of focus state",
    "disabled": "Description of disabled state"
  },
  "variants": {
    "VariantName": "[What it is]. [When to use]. [Visual characteristics]."
  },
  "dos": [
    "Recommended practice 1",
    "Recommended practice 2"
  ],
  "donts": [
    "Anti-pattern to avoid 1",
    "Anti-pattern to avoid 2"
  ],
  "a11y": [
    "Accessibility requirement 1",
    "Accessibility requirement 2"
  ],
  "formattedDescription": "Full YAML-formatted metadata ready to paste into Figma"
}`;
}

/**
 * Build prompt for generating the formatted Figma description
 */
export function buildFormattedOutputPrompt(
  generatedMetadata: Record<string, unknown>,
  locale: Locale = 'en'
): string {
  const languageNote = locale === 'he'
    ? 'The description is in Hebrew. Keep field names in English.'
    : '';

  return `Convert this metadata to the SKILL.md YAML format for Figma:

${JSON.stringify(generatedMetadata, null, 2)}

${languageNote}

Output ONLY the formatted YAML text (no JSON wrapper, no markdown code blocks):

[Primary description]

---
tags: [comma, separated, tags]
notes: [usage notes]
...etc
`;
}

/**
 * Build the complete quality report prompt
 */
export function buildReportPrompt(
  component: ComponentData,
  auditResult: Record<string, unknown>,
  metadataAnalysis: Record<string, unknown>,
  generatedMetadata: Record<string, unknown>,
  skills: SkillContext,
  locale: Locale = 'en'
): string {
  const enrichmentStructure = skills.enrichmentTemplate;

  return `Generate a comprehensive quality report for this component.

## Component
${JSON.stringify(component, null, 2)}

## Audit Results
${JSON.stringify(auditResult, null, 2)}

## Metadata Analysis
${JSON.stringify(metadataAnalysis, null, 2)}

## Generated Metadata
${JSON.stringify(generatedMetadata, null, 2)}

## Output Structure (from ENRICHMENT_TEMPLATE)
${JSON.stringify(enrichmentStructure, null, 2)}

## Your Task

Combine all data into a final report. Return ONLY valid JSON following the ENRICHMENT_TEMPLATE structure with these additions:

{
  "component": { /* from ENRICHMENT_TEMPLATE */ },
  "tokens": [ /* extracted tokens */ ],
  "figmaMetadata": { /* Figma file info */ },
  "qualityReport": {
    "overallScore": number,
    "scores": { "naming": n, "structure": n, "visual": n, "accessibility": n, "metadata": n },
    "exportReady": boolean,
    "blockers": [],
    "issues": [],
    "actionItems": [
      { "priority": "critical|high|medium|low", "issue": "...", "howToFix": "..." }
    ]
  },
  "generatedMetadata": { /* the generated metadata */ },
  "formattedForFigma": "YAML string ready to paste"
}`;
}
