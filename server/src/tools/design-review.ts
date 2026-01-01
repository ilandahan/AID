/**
 * @file design-review.ts
 * @description MCP tool implementations for design review.
 * Uses SKILL.md format for validation and ENRICHMENT_TEMPLATE for output.
 *
 * @related
 *   - ../claude/client.ts - Claude API calls
 *   - ../claude/prompt-builder.ts - Prompt construction
 *   - ../claude/skill-loader.ts - Skill loading
 *   - ../../SKILL.md - Component metadata format
 *   - ../../ENRICHMENT_TEMPLATE.json - Output structure
 */

import { getClaudeClient, type AuditResult, type MetadataAnalysis, type GeneratedMetadata, type QualityReport } from '../claude/client.js';
import { loadSkills, getEnrichmentStructure, type SkillContext } from '../claude/skill-loader.js';
import {
  buildAuditPrompt,
  buildAnalysisPrompt,
  buildGenerationPrompt,
  buildFormattedOutputPrompt,
  buildReportPrompt,
  type ComponentData
} from '../claude/prompt-builder.js';
import { type Locale, t } from '../i18n/messages.js';

// Cache for loaded skills
let skillsCache: SkillContext | null = null;

function getSkills(): SkillContext {
  if (!skillsCache) {
    skillsCache = loadSkills();
  }
  return skillsCache;
}

/**
 * Audit a component for quality issues
 * Uses SKILL.md validation rules
 */
export async function auditComponent(
  component: ComponentData,
  checks: string[] = ['naming', 'structure', 'visual', 'accessibility', 'metadata'],
  locale: Locale = 'en'
): Promise<AuditResult> {
  const skills = getSkills();
  const claude = getClaudeClient();

  const prompt = buildAuditPrompt(component, skills, locale);
  const result = await claude.auditComponent(prompt);

  // Localize issue messages if needed
  if (locale !== 'en') {
    result.issues = result.issues.map(issue => ({
      ...issue,
      message: localizeIssueMessage(issue, locale)
    }));
  }

  return result;
}

/**
 * Analyze metadata completeness
 */
export async function analyzeMetadata(
  component: ComponentData,
  locale: Locale = 'en'
): Promise<MetadataAnalysis> {
  const skills = getSkills();
  const claude = getClaudeClient();

  const prompt = buildAnalysisPrompt(component, skills, locale);
  const result = await claude.analyzeMetadata(prompt);

  return result;
}

/**
 * Generate metadata suggestions using SKILL.md format
 */
export async function generateMetadata(
  component: ComponentData,
  locale: Locale = 'en'
): Promise<GeneratedMetadata> {
  const skills = getSkills();
  const claude = getClaudeClient();

  // Generate metadata
  const prompt = buildGenerationPrompt(component, skills, locale);
  const metadata = await claude.generateMetadata(prompt);

  // Generate formatted output for Figma
  const formatPrompt = buildFormattedOutputPrompt(metadata, locale);
  const formatted = await claude.generateFormatted(formatPrompt);
  metadata.formattedDescription = formatted;

  return metadata;
}

/**
 * Generate complete quality report using ENRICHMENT_TEMPLATE structure
 */
export async function generateReport(
  component: ComponentData,
  audit: AuditResult,
  metadata: MetadataAnalysis,
  generated: GeneratedMetadata,
  locale: Locale = 'en'
): Promise<QualityReport> {
  const skills = getSkills();
  const claude = getClaudeClient();

  const prompt = buildReportPrompt(
    component,
    audit,
    metadata,
    generated,
    skills,
    locale
  );

  const report = await claude.generateReport(prompt);

  return report;
}

/**
 * Run the complete quality pipeline
 */
export async function runQualityPipeline(
  component: ComponentData,
  locale: Locale = 'en'
): Promise<{
  audit: AuditResult;
  metadata: MetadataAnalysis;
  generated: GeneratedMetadata;
  report: QualityReport;
  exportReady: boolean;
}> {
  // Step 1: Audit
  const audit = await auditComponent(component, undefined, locale);

  // Step 2: Analyze metadata
  const metadata = await analyzeMetadata(component, locale);

  // Step 3: Generate suggestions
  const generated = await generateMetadata(component, locale);

  // Step 4: Generate report
  const report = await generateReport(component, audit, metadata, generated, locale);

  return {
    audit,
    metadata,
    generated,
    report,
    exportReady: audit.scores.overall >= 90
  };
}

/**
 * Export component to AID (only if score >= 90)
 */
export async function exportToAID(
  component: ComponentData,
  report: QualityReport,
  locale: Locale = 'en'
): Promise<{
  success: boolean;
  componentId: string;
  message: string;
  error?: string;
  payload?: Record<string, unknown>;
}> {
  const score = report.qualityReport.overallScore;

  if (score < 90) {
    return {
      success: false,
      componentId: component.name,
      message: t(locale, 'export.blocked'),
      error: t(locale, 'export.pointsNeeded', { points: 90 - score })
    };
  }

  // Build export payload using ENRICHMENT_TEMPLATE structure
  const skills = getSkills();
  const enrichmentStructure = getEnrichmentStructure(skills);

  const payload = {
    component: {
      componentId: component.name.replace(/\s+/g, '-').toLowerCase(),
      componentName: component.name,
      displayName: toPascalCase(component.name),
      description: report.generatedMetadata.description,
      level: report.generatedMetadata.level,
      category: report.generatedMetadata.category,
      props: [], // Would be populated from component analysis
      variants: component.variants?.map(v => ({
        name: v.name,
        options: Object.values(v.properties),
        defaultOption: Object.values(v.properties)[0],
        description: report.generatedMetadata.variants[v.name] || ''
      })) || [],
      states: Object.keys(report.generatedMetadata.states),
      accessibility: {
        role: inferRole(report.generatedMetadata.category),
        ariaLabel: report.generatedMetadata.ariaLabel,
        keyboardInteraction: inferKeyboardInteraction(report.generatedMetadata.category)
      },
      tags: report.generatedMetadata.tags,
      notes: report.generatedMetadata.notes
    },
    tokens: component.tokens || [],
    figmaMetadata: {
      fileKey: component.figmaUrl?.match(/file\/([^/]+)/)?.[1] || 'unknown',
      nodeId: component.name,
      exportedAt: new Date().toISOString(),
      pluginVersion: '2.0.0',
      figmaUrl: component.figmaUrl
    },
    qualityCertification: {
      score: score,
      auditedAt: new Date().toISOString(),
      passedChecks: report.qualityReport.scores
    }
  };

  return {
    success: true,
    componentId: component.name,
    message: t(locale, 'export.ready'),
    payload
  };
}

// Helper functions

function localizeIssueMessage(issue: { category: string; message: string }, locale: Locale): string {
  // Map known issue patterns to i18n keys
  const issueKeyMap: Record<string, string> = {
    'Component name should follow': 'issue.naming.wrongFormat',
    'Missing Focus state': 'issue.a11y.missingFocus',
    'Missing Disabled state': 'issue.a11y.missingDisabled',
    'Missing component description': 'issue.metadata.missingDescription',
    'Touch target': 'issue.a11y.smallTouchTarget',
    'Auto Layout': 'issue.structure.noAutoLayout'
  };

  for (const [pattern, key] of Object.entries(issueKeyMap)) {
    if (issue.message.includes(pattern)) {
      return t(locale, key);
    }
  }

  return issue.message;
}

function toPascalCase(str: string): string {
  return str
    .split(/[\s\/\-_]+/)
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join('');
}

function inferRole(category: string): string {
  const roleMap: Record<string, string> = {
    button: 'button',
    navigation: 'navigation',
    form: 'form',
    layout: 'region',
    feedback: 'alert',
    'data-display': 'table',
    overlay: 'dialog'
  };
  return roleMap[category] || 'generic';
}

function inferKeyboardInteraction(category: string): string[] {
  const interactionMap: Record<string, string[]> = {
    button: ['Enter', 'Space'],
    navigation: ['Enter', 'Arrow keys'],
    form: ['Tab', 'Enter'],
    overlay: ['Escape', 'Tab']
  };
  return interactionMap[category] || ['Tab'];
}
