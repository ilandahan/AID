/**
 * @file skill-loader.ts
 * @description Loads Claude skills from the .claude/skills directory.
 * Injects skill content into prompts for design review.
 *
 * @related
 *   - ../../.claude/skills/figma-design-review/SKILL.md - Design review skill
 *   - ../../SKILL.md - Component metadata format
 *   - ./prompt-builder.ts - Uses loaded skills in prompts
 */

import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Path to skills directory (relative to server/src/claude)
const SKILLS_BASE = join(__dirname, '..', '..', '..', '.claude', 'skills');
const PROJECT_ROOT = join(__dirname, '..', '..', '..');

export interface SkillContent {
  name: string;
  description: string;
  content: string;
}

export interface SkillContext {
  componentMetadata: SkillContent;
  designReview: SkillContent;
  atomicDesign: SkillContent;
  enrichmentTemplate: object;
  payloadSchema: object;
}

/**
 * Parse skill frontmatter (YAML-like header)
 */
function parseSkillFrontmatter(content: string): { name: string; description: string; body: string } {
  const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);

  if (!frontmatterMatch) {
    return { name: 'unknown', description: '', body: content };
  }

  const frontmatter = frontmatterMatch[1];
  const body = frontmatterMatch[2];

  const nameMatch = frontmatter.match(/name:\s*(.+)/);
  const descMatch = frontmatter.match(/description:\s*(.+)/);

  return {
    name: nameMatch ? nameMatch[1].trim() : 'unknown',
    description: descMatch ? descMatch[1].trim() : '',
    body: body.trim()
  };
}

/**
 * Load a skill file from the skills directory
 */
function loadSkillFile(skillPath: string): SkillContent | null {
  const fullPath = join(SKILLS_BASE, skillPath);

  if (!existsSync(fullPath)) {
    console.warn(`Skill file not found: ${fullPath}`);
    return null;
  }

  try {
    const content = readFileSync(fullPath, 'utf-8');
    const parsed = parseSkillFrontmatter(content);

    return {
      name: parsed.name,
      description: parsed.description,
      content: parsed.body
    };
  } catch (error) {
    console.error(`Error loading skill ${skillPath}:`, error);
    return null;
  }
}

/**
 * Load a JSON file from project root
 */
function loadJsonFile(fileName: string): object | null {
  const fullPath = join(PROJECT_ROOT, fileName);

  if (!existsSync(fullPath)) {
    console.warn(`JSON file not found: ${fullPath}`);
    return null;
  }

  try {
    const content = readFileSync(fullPath, 'utf-8');
    return JSON.parse(content);
  } catch (error) {
    console.error(`Error loading JSON ${fileName}:`, error);
    return null;
  }
}

/**
 * Load the component metadata skill (SKILL.md in project root)
 */
function loadComponentMetadataSkill(): SkillContent | null {
  const fullPath = join(PROJECT_ROOT, 'SKILL.md');

  if (!existsSync(fullPath)) {
    console.warn('Component metadata skill (SKILL.md) not found');
    return null;
  }

  try {
    const content = readFileSync(fullPath, 'utf-8');
    // This file doesn't have frontmatter, so we create metadata
    return {
      name: 'component-metadata',
      description: 'Standard format for documenting Figma components with comprehensive metadata',
      content: content
    };
  } catch (error) {
    console.error('Error loading component metadata skill:', error);
    return null;
  }
}

/**
 * Load all required skills for design review
 */
export function loadSkills(): SkillContext {
  const componentMetadata = loadComponentMetadataSkill();
  const designReview = loadSkillFile('figma-design-review/SKILL.md');
  const atomicDesign = loadSkillFile('atomic-design/SKILL.md');
  const enrichmentTemplate = loadJsonFile('ENRICHMENT_TEMPLATE.json');
  const payloadSchema = loadJsonFile('PAYLOAD_SCHEMA.json');

  if (!componentMetadata) {
    throw new Error('Required skill "component-metadata" (SKILL.md) not found');
  }

  if (!designReview) {
    throw new Error('Required skill "figma-design-review" not found');
  }

  return {
    componentMetadata,
    designReview: designReview!,
    atomicDesign: atomicDesign || {
      name: 'atomic-design',
      description: 'Atomic design methodology',
      content: '# Atomic Design\n\nLevels: atom, molecule, organism, template, page'
    },
    enrichmentTemplate: enrichmentTemplate || {},
    payloadSchema: payloadSchema || {}
  };
}

/**
 * Extract the metadata format section from SKILL.md
 */
export function extractMetadataFormat(skillContent: SkillContent): string {
  const content = skillContent.content;

  // Find the metadata format section
  const formatMatch = content.match(/## Metadata Format[\s\S]*?```yaml([\s\S]*?)```/);

  if (formatMatch) {
    return formatMatch[1].trim();
  }

  // Fallback: return the required fields section
  const requiredMatch = content.match(/### Required Fields[\s\S]*?```yaml([\s\S]*?)```/);

  if (requiredMatch) {
    return requiredMatch[1].trim();
  }

  return '';
}

/**
 * Extract examples from SKILL.md
 */
export function extractExamples(skillContent: SkillContent): string[] {
  const content = skillContent.content;
  const examples: string[] = [];

  // Find all YAML code blocks in the Examples section
  const examplesSection = content.match(/## Examples[\s\S]*?(?=## |$)/);

  if (examplesSection) {
    const yamlBlocks = examplesSection[0].matchAll(/```yaml([\s\S]*?)```/g);

    for (const match of yamlBlocks) {
      examples.push(match[1].trim());
    }
  }

  return examples;
}

/**
 * Get the enrichment template structure for populating reports
 */
export function getEnrichmentStructure(context: SkillContext): object {
  const template = context.enrichmentTemplate as Record<string, unknown>;

  // Extract the component structure from the template
  if (template.component) {
    return template.component;
  }

  return template;
}

/**
 * Validate that all required skills are loaded
 */
export function validateSkillContext(context: SkillContext): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!context.componentMetadata?.content) {
    errors.push('Component metadata skill is empty');
  }

  if (!context.designReview?.content) {
    errors.push('Design review skill is empty');
  }

  if (!context.enrichmentTemplate || Object.keys(context.enrichmentTemplate).length === 0) {
    errors.push('Enrichment template is missing or empty');
  }

  return {
    valid: errors.length === 0,
    errors
  };
}
