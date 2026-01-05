/**
 * AID Figma Plugin Server
 * 
 * Provides:
 * - /auth/* - Authentication endpoints for plugin pairing
 * - /mcp - MCP endpoint for component analysis (placeholder)
 * - /health - Health check endpoint
 */

import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import archiver from 'archiver';
import { PassThrough } from 'stream';
import authRoutes from './auth/routes';

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors({
  origin: '*', // In production, restrict to Figma plugin domains
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: [
    'Content-Type',
    'Authorization',
    'X-Nonce',        // Added by Figma sandbox
    'X-Tenant-ID',    // AID tenant identification
    'X-Timestamp',    // Request signing timestamp
    'x-nonce'         // Lowercase variant for compatibility
  ]
}));

app.use(express.json());

// Request logging
app.use((req: Request, res: Response, next: NextFunction) => {
  console.log(`${new Date().toISOString()} ${req.method} ${req.path}`);
  next();
});

// Health check
app.get('/health', (req: Request, res: Response) => {
  res.json({ 
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});

// Auth routes
app.use('/auth', authRoutes);

// MCP endpoint - handles Model Context Protocol requests
app.post('/mcp', async (req: Request, res: Response) => {
  const { method, id, params } = req.body;

  console.log(`MCP request: ${method}`);

  // Handle MCP initialize handshake
  if (method === 'initialize') {
    return res.json({
      jsonrpc: '2.0',
      id,
      result: {
        protocolVersion: '2024-11-05',
        capabilities: {
          tools: { listChanged: false },
          resources: { listChanged: false }
        },
        serverInfo: {
          name: 'aid-figma-server',
          version: '1.0.0'
        }
      }
    });
  }

  // Handle initialized notification (no response needed, but acknowledge)
  if (method === 'notifications/initialized') {
    return res.json({
      jsonrpc: '2.0',
      id,
      result: {}
    });
  }

  if (method === 'tools/list') {
    return res.json({
      jsonrpc: '2.0',
      id,
      result: {
        tools: [
          {
            name: 'auditComponent',
            description: 'Audit a Figma component for design system quality',
            inputSchema: {
              type: 'object',
              properties: {
                nodeData: { type: 'object', description: 'Figma node data to audit' }
              },
              required: ['nodeData']
            }
          },
          {
            name: 'generateMetadata',
            description: 'Generate LLM-accessible metadata for a component',
            inputSchema: {
              type: 'object',
              properties: {
                nodeData: { type: 'object', description: 'Figma node data' }
              },
              required: ['nodeData']
            }
          },
          {
            name: 'exportToAID',
            description: 'Export component to AID design system',
            inputSchema: {
              type: 'object',
              properties: {
                nodeData: { type: 'object', description: 'Figma node data' },
                format: { type: 'string', enum: ['react', 'vue', 'html'] }
              },
              required: ['nodeData']
            }
          }
        ]
      }
    });
  }

  // Handle ping for connection health check
  if (method === 'ping') {
    return res.json({
      jsonrpc: '2.0',
      id,
      result: { pong: true }
    });
  }

  // Handle tools/call for actual tool execution
  if (method === 'tools/call') {
    const toolName = params?.name;
    const toolArgs = params?.arguments || {};

    console.log(`Tool call: ${toolName}`);
    console.log(`Tool args keys: ${Object.keys(toolArgs).join(', ')}`);

    // audit_component - Returns audit score based on component data
    // Plugin sends: { component, tokens, variants, checks, skill }
    // Plugin expects: { score, issues, recommendations, ... }
    if (toolName === 'audit_component' || toolName === 'auditComponent') {
      const component = toolArgs.component || {};
      const tokens = toolArgs.tokens || [];
      const variants = toolArgs.variants || [];
      const checks = toolArgs.checks || [];

      // Detect if this is a Component Set or a single Component
      const isComponentSet = component.type === 'COMPONENT_SET';

      // Calculate audit score based on component structure
      // For single components: base 80 (states/variants don't apply)
      // For component sets: base 70 (states/variants do apply)
      let score = isComponentSet ? 70 : 80;
      const issues: any[] = [];

      // Check for auto-layout (+10 points) - applies to both
      if (component.hasAutoLayout) {
        score += 10;
      } else {
        issues.push({
          severity: 'warning',
          category: 'structure',
          message: 'Missing auto-layout - required for responsive design',
          points: 10
        });
      }

      // Check for states - ONLY for Component Sets (+5 points)
      if (isComponentSet) {
        if (component.hasStates) {
          score += 5;
        } else {
          issues.push({
            severity: 'info',
            category: 'interaction',
            message: 'No interactive states (hover, disabled, focus) detected in variants',
            points: 5
          });
        }
      }

      // Check for variants - ONLY for Component Sets (+5 points)
      if (isComponentSet) {
        if (variants.length >= 3) {
          score += 5;
        } else if (variants.length > 0) {
          issues.push({
            severity: 'info',
            category: 'variants',
            message: `Only ${variants.length} variant(s) - consider adding more for flexibility`,
            points: 5
          });
        } else {
          issues.push({
            severity: 'info',
            category: 'variants',
            message: 'Component Set has no variants - add variant properties',
            points: 5
          });
        }
      }

      // Check for tokens (+5 points) - applies to both
      if (tokens.length > 0) {
        score += 5;
      } else {
        issues.push({
          severity: 'info',
          category: 'tokens',
          message: 'No design tokens extracted - ensure component uses styles/variables',
          points: 5
        });
      }

      // Check for proper naming convention with "/" (+5 points) - applies to both
      // But for single components that are variants, they use "=" format which is correct
      const isVariantName = component.name && component.name.includes('=');
      if (component.name && (component.name.includes('/') || isVariantName)) {
        score += 5;
      } else {
        issues.push({
          severity: 'info',
          category: 'naming',
          message: 'Name should use "/" for hierarchy (e.g., "Buttons/Primary")',
          points: 5
        });
      }

      // Cap at 100
      score = Math.min(100, score);

      // Generate recommendations based on issues
      const recommendations = issues.length > 0
        ? issues.map((i: any) => {
            if (i.severity === 'warning') return `⚠️ Fix: ${i.message} (+${i.points} points)`;
            return `💡 Improve: ${i.message} (+${i.points} points)`;
          })
        : ['✅ Component meets all quality standards'];

      console.log(`audit_component: type=${component.type}, isComponentSet=${isComponentSet}, score=${score}, issues=${issues.length}`);

      // Return in the exact format plugin expects (direct object)
      return res.json({
        jsonrpc: '2.0',
        id,
        result: {
          score: score,
          issues: issues,
          recommendations: recommendations,
          componentName: component.name || 'Unknown',
          analyzed: true
        }
      });
    }

    // analyze_metadata - Analyzes existing component metadata quality
    // Plugin sends: { component, existingDescription, variants, skill }
    // Plugin expects EXACT structure matching analyzeMetadataLocal():
    // { componentName, completenessScore, componentSetLevel, variantLevel, propertyLevel, accessibilityMetadata }
    if (toolName === 'analyze_metadata' || toolName === 'analyzeMetadata') {
      const component = toolArgs.component || {};
      const existingDescription = toolArgs.existingDescription || '';
      const variants = toolArgs.variants || [];
      const properties = component.properties || [];

      // Analyze which fields are present in the description (matching local analysis logic)
      const presentFields: string[] = [];
      const missingFields: string[] = [];
      const incompleteFields: string[] = [];

      if (existingDescription && existingDescription.length > 0) {
        presentFields.push('description');

        // Check for structured YAML format (starts with ---)
        if (existingDescription.includes('---')) {
          if (existingDescription.includes('tags:')) presentFields.push('tags');
          else missingFields.push('tags');

          if (existingDescription.includes('notes:')) presentFields.push('notes');
          else missingFields.push('notes');

          if (existingDescription.includes('category:')) presentFields.push('category');
          else missingFields.push('category');

          if (existingDescription.includes('level:')) presentFields.push('level');
          else missingFields.push('level');

          if (existingDescription.includes('ariaLabel:')) presentFields.push('ariaLabel');
          if (existingDescription.includes('a11y:')) presentFields.push('a11y');
          // Check for focus states and contrast info
          if (existingDescription.includes('focusStates:') || existingDescription.includes('focus:')) presentFields.push('focusStates');
          if (existingDescription.includes('contrast:') || existingDescription.includes('contrastInfo:')) presentFields.push('contrastInfo');
        } else {
          missingFields.push('tags', 'notes', 'category', 'level');
          incompleteFields.push('description (missing structured metadata)');
        }
      } else {
        missingFields.push('description', 'tags', 'notes', 'category', 'level');
      }

      // Also check for focus/contrast keywords anywhere in description (even without YAML)
      const hasFocusKeyword = existingDescription.toLowerCase().includes('focus') &&
                              (existingDescription.toLowerCase().includes('state') ||
                               existingDescription.toLowerCase().includes('ring') ||
                               existingDescription.toLowerCase().includes('outline'));
      const hasContrastKeyword = existingDescription.toLowerCase().includes('contrast') &&
                                 (existingDescription.toLowerCase().includes('ratio') ||
                                  existingDescription.toLowerCase().includes('4.5') ||
                                  existingDescription.toLowerCase().includes('3:1'));

      // Count properties (for COMPONENT_SET)
      let totalProperties = 0;
      let propertiesWithDesc = 0;
      const propertiesMissingDesc: string[] = [];

      properties.forEach((prop: any) => {
        if (prop.type === 'VARIANT') {
          totalProperties++;
          const cleanName = prop.name?.replace(/#\d+:\d+$/, '') || prop.name;
          if (existingDescription && existingDescription.includes(`${cleanName}:`)) {
            propertiesWithDesc++;
          } else {
            propertiesMissingDesc.push(cleanName);
          }
        }
      });

      // Count variants
      let totalVariants = variants.length;
      let variantsWithDesc = 0;
      const variantsMissingDesc: any[] = [];

      variants.forEach((v: any) => {
        if (v.hasDescription || (v.description && v.description.length > 0)) {
          variantsWithDesc++;
        } else {
          variantsMissingDesc.push({
            name: v.name || 'Unknown',
            nodeId: v.nodeId || v.id || '',
            properties: v.properties || {},
            hasDescription: false
          });
        }
      });

      // Calculate scores (matching local analysis formula)
      const requiredFields = ['description', 'tags', 'notes', 'category', 'level'];
      const presentRequired = requiredFields.filter(f => presentFields.includes(f)).length;
      const variantScore = totalVariants > 0 ? (variantsWithDesc / totalVariants) * 100 : 100;
      const fieldScore = (presentRequired / requiredFields.length) * 100;
      const completenessScore = Math.round(fieldScore * 0.6 + variantScore * 0.4);

      console.log(`analyze_metadata: completenessScore ${completenessScore}, present: [${presentFields.join(', ')}], missing: [${missingFields.join(', ')}]`);
      console.log(`analyze_metadata: variants ${variantsWithDesc}/${totalVariants}, properties ${propertiesWithDesc}/${totalProperties}`);

      // Return in EXACT format plugin expects (matching analyzeMetadataLocal)
      return res.json({
        jsonrpc: '2.0',
        id,
        result: {
          componentName: component.name || 'Component',
          completenessScore: completenessScore,
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
            hasFocusStates: presentFields.includes('focusStates') || hasFocusKeyword,
            hasContrastInfo: presentFields.includes('contrastInfo') || hasContrastKeyword
          }
        }
      });
    }

    // generate_metadata - Generates new metadata for component
    // Plugin sends: { component, tokens, variants, skill }
    // Plugin expects full metadata structure for UI display
    if (toolName === 'generate_metadata' || toolName === 'generateMetadata') {
      const component = toolArgs.component || {};
      const tokens = toolArgs.tokens || [];
      const variants = toolArgs.variants || [];
      const properties = component.properties || [];

      console.log(`generate_metadata: Processing ${tokens.length} tokens, ${variants.length} variants, ${properties.length} properties for ${component.name}`);

      // Determine atomic level based on component structure
      let atomicLevel = 'atom';
      if (component.type === 'COMPONENT_SET' || variants.length > 3) {
        atomicLevel = 'molecule';
      }
      if (component.childCount > 10 || variants.length > 10) {
        atomicLevel = 'organism';
      }

      // Generate category from component name
      const nameParts = (component.name || '').split('/');
      const category = nameParts.length > 1 ? nameParts[0].trim() : 'UI Components';

      // Generate tags from component name and properties
      const tags: string[] = [];
      if (component.name) {
        // Extract meaningful words from name
        const words = component.name.replace(/[^a-zA-Z0-9\s]/g, ' ').split(/\s+/).filter((w: string) => w.length > 2);
        tags.push(...words.slice(0, 5).map((w: string) => w.toLowerCase()));
      }
      if (component.hasStates) tags.push('interactive');
      if (component.hasAutoLayout) tags.push('responsive');
      if (variants.length > 0) tags.push('variants');

      // Generate property descriptions from component properties
      const propertyDescriptions: Record<string, string> = {};
      properties.forEach((prop: any) => {
        const propName = prop.name || 'unknown';
        let description = `${prop.type || 'unknown'} property`;
        if (prop.variantOptions && prop.variantOptions.length > 0) {
          description = `Options: ${prop.variantOptions.join(', ')}`;
        } else if (prop.defaultValue !== undefined) {
          description = `Default: ${prop.defaultValue}`;
        }
        propertyDescriptions[propName] = description;
      });

      // Generate description
      const description = `A ${atomicLevel}-level ${category.toLowerCase()} component with ${variants.length} variants and ${properties.length} configurable properties.`;

      // Generate accessibility info
      const ariaLabel = component.name ? component.name.split('/').pop()?.trim() || component.name : 'Component';
      const a11y: string[] = [];
      if (component.hasStates) {
        a11y.push('Supports keyboard interaction states');
      }
      if (properties.some((p: any) => p.name?.toLowerCase().includes('label'))) {
        a11y.push('Has configurable label for screen readers');
      }
      a11y.push('Ensure sufficient color contrast for text elements');

      // Generate variant descriptions as object (plugin expects { variantName: description })
      const variantDescriptions: Record<string, string> = {};
      variants.forEach((v: any) => {
        const variantName = v.name || 'Unknown';
        // Generate description from variant properties
        const propValues = Object.entries(v.properties || {})
          .map(([k, val]) => `${k}=${val}`)
          .join(', ');
        variantDescriptions[variantName] = propValues || `Variant of ${component.name || 'component'}`;
      });

      const notes = `Component has ${component.childCount || 0} child elements. ${component.hasAutoLayout ? 'Uses auto-layout for responsive sizing.' : ''}`;

      // Focus states info
      const focusStates = 'Use 2-3px focus ring with 3:1 contrast ratio for keyboard navigation';
      // Contrast info
      const contrastInfo = 'Ensure 4.5:1 ratio for normal text, 3:1 for large text';

      // Generate formattedDescription - this is the YAML that gets written to Figma
      // When this is applied to Figma and re-analyzed, it should be recognized as complete
      // CRITICAL: Include focusStates: and contrast: so they are detected on re-analysis
      let formattedDescription = `---
description: ${description}
tags: [${tags.join(', ')}]
notes: ${notes}
category: ${category}
level: ${atomicLevel}
ariaLabel: ${ariaLabel}
a11y:
${a11y.map(a => `  - ${a}`).join('\n')}
focusStates: ${focusStates}
contrast: ${contrastInfo}
---`;

      // Add property descriptions to the formatted output
      if (Object.keys(propertyDescriptions).length > 0) {
        formattedDescription += '\n\n## Properties\n';
        Object.entries(propertyDescriptions).forEach(([propName, propDesc]) => {
          formattedDescription += `${propName}: ${propDesc}\n`;
        });
      }

      // Return in the exact format plugin expects (direct object)
      // IMPORTANT: Plugin expects 'level' not 'atomicLevel', 'variantDescriptions' as object
      // IMPORTANT: Plugin expects 'formattedDescription' for Apply to Figma functionality
      return res.json({
        jsonrpc: '2.0',
        id,
        result: {
          // Core data
          tokens: tokens,
          componentName: component.name || 'Component',
          type: component.type || 'COMPONENT',
          variantCount: variants.length,

          // Metadata tab fields (plugin reads these in updateGenerated)
          description: description,
          tags: tags,
          notes: notes,
          category: category,
          level: atomicLevel,  // Plugin expects 'level' not 'atomicLevel'

          // Dev info fields
          propertyDescriptions: propertyDescriptions,
          ariaLabel: ariaLabel,
          a11y: a11y,
          // states.focus is used by UI to display Focus States value
          states: {
            focus: focusStates
          },
          specs: {
            contrast: contrastInfo,
            touchTarget: component.width && component.width >= 44 ? '44x44px minimum met' : 'Check touch target size (44x44px recommended)'
          },

          // Variant info - plugin expects variantDescriptions as { name: description } object
          variantDescriptions: variantDescriptions,
          variants: variants.map((v: any) => ({
            name: v.name,
            properties: v.properties || {}
          })),

          // CRITICAL: formattedDescription is what gets applied to Figma
          // When re-analyzed, the description should be recognized as having all required fields
          formattedDescription: formattedDescription,
          formattedForFigma: formattedDescription,

          generated: true,
          timestamp: new Date().toISOString()
        }
      });
    }

    // generate_report - Generates final combined report
    // Plugin sends: { component, auditResult, metadataAnalysis, generatedMetadata, existingDescription, tokens, variants }
    // Plugin expects: { overallScore, scores, exportReady, ... }
    if (toolName === 'generate_report' || toolName === 'generateReport') {
      const component = toolArgs.component || {};
      const auditResult = toolArgs.auditResult || {};
      const metadataAnalysis = toolArgs.metadataAnalysis || {};
      const tokens = toolArgs.tokens || [];
      const variants = toolArgs.variants || [];

      // Extract scores from results (now in direct format)
      const auditScore = auditResult.score || 0;
      const metadataScore = metadataAnalysis.completenessScore || metadataAnalysis.score || 0;

      // Calculate combined score (70% audit, 30% metadata)
      const combinedScore = Math.round((auditScore * 0.7) + (metadataScore * 0.3));

      console.log(`generate_report: Audit ${auditScore}, Metadata ${metadataScore}, Combined ${combinedScore}`);

      // Return in the exact format plugin expects (direct object)
      return res.json({
        jsonrpc: '2.0',
        id,
        result: {
          componentName: component.name || 'Component',
          overallScore: combinedScore,
          scores: {
            audit: auditScore,
            metadata: metadataScore,
            combined: combinedScore
          },
          tokenCount: tokens.length,
          variantCount: variants.length,
          exportReady: combinedScore >= 70,
          generated: true,
          timestamp: new Date().toISOString()
        }
      });
    }

    // export_to_aid / exportToAID - Exports component to AID design system
    if (toolName === 'export_to_aid' || toolName === 'exportToAID') {
      const component = toolArgs.component || toolArgs.nodeData || {};
      const metadata = toolArgs.metadata || {};
      const tokens = toolArgs.tokens || [];
      const content = toolArgs.content || {};
      const certification = toolArgs.certification || {};
      const figma = toolArgs.figma || {};

      const componentName = component.name || 'Component';
      const safeName = componentName.replace(/[^a-zA-Z0-9]/g, '');
      const level = component.level || 'molecule';
      const destinationPath = component.destinationPath || `src/components/${level}s/${safeName}/`;

      console.log(`export_to_aid: Exporting ${componentName} as ${level} to ${destinationPath}`);

      // Extract variant information for props generation
      const variants = metadata.variants || [];
      const propertyDescriptions = metadata.propertyDescriptions || {};
      const variantProps = Object.keys(propertyDescriptions);

      // Build props interface from variants
      const propsFromVariants = variantProps.map(prop => {
        const desc = propertyDescriptions[prop] || '';
        const optionsMatch = desc.match(/Options:\s*(.+)/);
        if (optionsMatch) {
          const options = optionsMatch[1].split(',').map((o: string) => o.trim());
          return { name: prop.toLowerCase(), type: options.map((o: string) => `'${o}'`).join(' | '), options };
        }
        return { name: prop.toLowerCase(), type: 'string', options: [] };
      });

      // Atomic level info for documentation
      const levelInfo: Record<string, { emoji: string; description: string; examples: string }> = {
        atom: { emoji: '⚛️', description: 'Basic building block', examples: 'buttons, inputs, labels, icons' },
        molecule: { emoji: '🧬', description: 'Simple component group', examples: 'form fields, search bars, cards' },
        organism: { emoji: '🦠', description: 'Complex UI section', examples: 'headers, forms, modals, navigation' },
        template: { emoji: '📐', description: 'Page layout structure', examples: 'page layouts, grids' },
        page: { emoji: '📄', description: 'Complete page with content', examples: 'home page, dashboard' }
      };
      const currentLevel = levelInfo[level] || levelInfo.molecule;

      // ============================================
      // FILE 1: Main Component (React TSX)
      // ============================================
      const propsInterface = propsFromVariants.length > 0
        ? propsFromVariants.map(p => `  /** ${propertyDescriptions[p.name.charAt(0).toUpperCase() + p.name.slice(1)] || p.name} */\n  ${p.name}?: ${p.type};`).join('\n')
        : '';

      const componentCode = `/**
 * ${componentName}
 *
 * ${currentLevel.emoji} Atomic Level: ${level.charAt(0).toUpperCase() + level.slice(1)}
 * ${currentLevel.description} - ${currentLevel.examples}
 *
 * @description ${metadata.description || 'A reusable component from Figma design system'}
 * @figma ${figma.fileKey ? 'https://figma.com/file/' + figma.fileKey + '?node-id=' + figma.nodeId : 'N/A'}
 * @score ${certification.score || 0}/100
 * @generated ${new Date().toISOString()}
 */

import React from 'react';
import styles from './${safeName}.module.css';
import { tokens } from './${safeName}.tokens';

export interface ${safeName}Props {
  /** Additional CSS class names */
  className?: string;
  /** Child elements */
  children?: React.ReactNode;
${propsInterface}
  /** Click handler */
  onClick?: () => void;
  /** Disabled state */
  disabled?: boolean;
  /** Accessible label */
  'aria-label'?: string;
}

/**
 * ${safeName} component
 *
 * @example
 * \`\`\`tsx
 * <${safeName}${propsFromVariants.length > 0 ? ` ${propsFromVariants[0].name}="${propsFromVariants[0].options?.[0] || 'default'}"` : ''}>
 *   Content here
 * </${safeName}>
 * \`\`\`
 */
export const ${safeName}: React.FC<${safeName}Props> = ({
  className,
  children,
${propsFromVariants.map(p => `  ${p.name} = '${p.options?.[0] || 'default'}',`).join('\n')}
  onClick,
  disabled = false,
  'aria-label': ariaLabel,
  ...props
}) => {
  const variantClasses = [
${propsFromVariants.map(p => `    ${p.name} ? styles[\`\${${p.name}}\`] : ''`).join(',\n')}
  ].filter(Boolean).join(' ');

  return (
    <div
      className={\`\${styles.root} \${variantClasses} \${disabled ? styles.disabled : ''} \${className || ''}\`}
      onClick={!disabled ? onClick : undefined}
      role="button"
      tabIndex={disabled ? -1 : 0}
      aria-label={ariaLabel}
      aria-disabled={disabled}
      {...props}
    >
      {children}
    </div>
  );
};

export default ${safeName};
`;

      // ============================================
      // FILE 2: CSS Module with Design Tokens
      // ============================================
      const cssTokens = tokens.filter((t: any) => t.cssVariable).map((t: any) =>
        `  ${t.cssVariable}: ${t.value};`
      ).join('\n');

      const stylesCode = `/**
 * ${componentName} Styles
 * ${currentLevel.emoji} Atomic Level: ${level}
 *
 * Generated by AID Figma Plugin
 * Design tokens extracted from Figma
 */

/* Design Tokens */
:root {
${cssTokens || '  /* No tokens extracted */'}
}

/* Base Component Styles */
.root {
  /* Layout */
  display: inline-flex;
  align-items: center;
  justify-content: center;

  /* Spacing - from Figma */
  padding: var(--spacing-${safeName.toLowerCase()}-padding, 16px 32px);
  gap: var(--spacing-${safeName.toLowerCase()}-gap, 8px);

  /* Visual */
  background: var(--color-${safeName.toLowerCase()}-bg, #0c8ce9);
  border-radius: var(--radius-${safeName.toLowerCase()}, 6px);

  /* Typography */
  font-family: var(--font-family-${safeName.toLowerCase()}, inherit);
  font-size: var(--font-size-${safeName.toLowerCase()}, 16px);

  /* Interaction */
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}

.root:hover:not(.disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-${safeName.toLowerCase()}-hover, 0 4px 12px rgba(0,0,0,0.15));
}

.root:focus-visible {
  outline: 2px solid var(--color-focus, #0066cc);
  outline-offset: 2px;
}

.root:active:not(.disabled) {
  transform: translateY(0);
}

/* Disabled State */
.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

/* Variant Styles */
${propsFromVariants.flatMap(p =>
  (p.options || []).map((opt: string) => `.${opt} {\n  /* ${p.name}: ${opt} styles */\n}`)
).join('\n\n')}
`;

      // ============================================
      // FILE 3: Barrel Export (index.ts)
      // ============================================
      const indexCode = `/**
 * ${componentName} - Public API
 * ${currentLevel.emoji} Atomic Level: ${level}
 */

// Component
export { ${safeName}, type ${safeName}Props } from './${safeName}';
export { default } from './${safeName}';

// Design Tokens
export { tokens, cssVariables } from './${safeName}.tokens';

// Types (if needed externally)
export type { ${safeName}Variant } from './${safeName}.types';
`;

      // ============================================
      // FILE 4: Unit Tests
      // ============================================
      const testCode = `/**
 * ${componentName} Tests
 * ${currentLevel.emoji} Atomic Level: ${level}
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ${safeName} } from './${safeName}';

describe('${safeName}', () => {
  // Rendering
  describe('rendering', () => {
    it('renders without crashing', () => {
      render(<${safeName}>Test</${safeName}>);
      expect(screen.getByText('Test')).toBeInTheDocument();
    });

    it('renders with custom className', () => {
      const { container } = render(<${safeName} className="custom">Test</${safeName}>);
      expect(container.firstChild).toHaveClass('custom');
    });

    it('renders children correctly', () => {
      render(<${safeName}><span data-testid="child">Child</span></${safeName}>);
      expect(screen.getByTestId('child')).toBeInTheDocument();
    });
  });

  // Accessibility
  describe('accessibility', () => {
    it('has correct role', () => {
      render(<${safeName}>Test</${safeName}>);
      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('supports aria-label', () => {
      render(<${safeName} aria-label="Custom label">Test</${safeName}>);
      expect(screen.getByLabelText('Custom label')).toBeInTheDocument();
    });

    it('is keyboard accessible', () => {
      render(<${safeName}>Test</${safeName}>);
      const element = screen.getByRole('button');
      expect(element).toHaveAttribute('tabIndex', '0');
    });

    it('removes from tab order when disabled', () => {
      render(<${safeName} disabled>Test</${safeName}>);
      const element = screen.getByRole('button');
      expect(element).toHaveAttribute('tabIndex', '-1');
    });
  });

  // Interaction
  describe('interaction', () => {
    it('calls onClick when clicked', () => {
      const handleClick = jest.fn();
      render(<${safeName} onClick={handleClick}>Test</${safeName}>);
      fireEvent.click(screen.getByRole('button'));
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('does not call onClick when disabled', () => {
      const handleClick = jest.fn();
      render(<${safeName} onClick={handleClick} disabled>Test</${safeName}>);
      fireEvent.click(screen.getByRole('button'));
      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  // Variants
  describe('variants', () => {
${propsFromVariants.map(p => `    it('renders ${p.name} variant correctly', () => {
      const { container } = render(<${safeName} ${p.name}="${p.options?.[0] || 'default'}">Test</${safeName}>);
      expect(container.firstChild).toHaveClass('${p.options?.[0] || 'default'}');
    });`).join('\n\n') || '    it.todo(\'add variant tests when variants are defined\');'}
  });

  // Snapshots
  describe('snapshots', () => {
    it('matches snapshot', () => {
      const { container } = render(<${safeName}>Test</${safeName}>);
      expect(container).toMatchSnapshot();
    });
  });
});
`;

      // ============================================
      // FILE 5: Storybook Stories
      // ============================================
      const storiesCode = `/**
 * ${componentName} Stories
 * ${currentLevel.emoji} Atomic Level: ${level}
 *
 * Storybook stories for visual testing and documentation
 */

import type { Meta, StoryObj } from '@storybook/react';
import { ${safeName} } from './${safeName}';

const meta: Meta<typeof ${safeName}> = {
  title: '${level.charAt(0).toUpperCase() + level.slice(1)}s/${safeName}',
  component: ${safeName},
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: \`
${currentLevel.emoji} **Atomic Level**: ${level.charAt(0).toUpperCase() + level.slice(1)}

${metadata.description || 'A reusable component from the design system.'}

**Figma**: ${figma.fileKey ? `[View in Figma](https://figma.com/file/${figma.fileKey}?node-id=${figma.nodeId})` : 'N/A'}

**Quality Score**: ${certification.score || 0}/100
        \`,
      },
    },
    design: {
      type: 'figma',
      url: '${figma.fileKey ? `https://figma.com/file/${figma.fileKey}?node-id=${figma.nodeId}` : ''}',
    },
  },
  argTypes: {
    children: {
      control: 'text',
      description: 'Content inside the component',
    },
${propsFromVariants.map(p => `    ${p.name}: {
      control: 'select',
      options: [${p.options?.map((o: string) => `'${o}'`).join(', ') || ''}],
      description: '${propertyDescriptions[p.name.charAt(0).toUpperCase() + p.name.slice(1)] || p.name}',
    },`).join('\n')}
    disabled: {
      control: 'boolean',
      description: 'Disable interaction',
    },
    onClick: {
      action: 'clicked',
      description: 'Click handler',
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

// Default story
export const Default: Story = {
  args: {
    children: '${componentName}',
  },
};

// Interactive story
export const Interactive: Story = {
  args: {
    children: 'Click me',
  },
  play: async ({ canvasElement }) => {
    // Add interaction tests here
  },
};

// Disabled state
export const Disabled: Story = {
  args: {
    children: 'Disabled',
    disabled: true,
  },
};

${propsFromVariants.map(p => `// ${p.name} variants
${(p.options || []).map((opt: string, i: number) => `export const ${p.name}${opt.charAt(0).toUpperCase() + opt.slice(1)}: Story = {
  args: {
    children: '${opt}',
    ${p.name}: '${opt}',
  },
};`).join('\n\n')}`).join('\n\n')}

// All variants showcase
export const AllVariants: Story = {
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', alignItems: 'flex-start' }}>
${propsFromVariants.length > 0
  ? propsFromVariants[0].options?.map((opt: string) =>
      `      <${safeName} ${propsFromVariants[0].name}="${opt}">${opt}</${safeName}>`
    ).join('\n') || `      <${safeName}>Default</${safeName}>`
  : `      <${safeName}>Default</${safeName}>`}
    </div>
  ),
};
`;

      // ============================================
      // FILE 6: Design Tokens (TypeScript)
      // ============================================
      const tokensCode = `/**
 * ${componentName} Design Tokens
 * ${currentLevel.emoji} Atomic Level: ${level}
 *
 * Extracted from Figma design system
 * These tokens ensure design consistency across the application
 */

export interface DesignToken {
  name: string;
  value: string;
  category: 'color' | 'spacing' | 'typography' | 'borderRadius' | 'shadow';
  cssVariable: string;
  rawValue?: unknown;
}

/**
 * Design tokens for ${componentName}
 */
export const tokens: DesignToken[] = ${JSON.stringify(tokens.map((t: any) => ({
  name: t.name,
  value: t.value,
  category: t.category,
  cssVariable: t.cssVariable,
})), null, 2)};

/**
 * CSS custom properties for use in stylesheets
 */
export const cssVariables = {
${tokens.map((t: any) => `  '${t.cssVariable}': '${t.value}'`).join(',\n') || '  // No tokens extracted'}
} as const;

/**
 * Token categories for filtering
 */
export const tokensByCategory = {
  color: tokens.filter(t => t.category === 'color'),
  spacing: tokens.filter(t => t.category === 'spacing'),
  typography: tokens.filter(t => t.category === 'typography'),
  borderRadius: tokens.filter(t => t.category === 'borderRadius'),
  shadow: tokens.filter(t => t.category === 'shadow'),
};

/**
 * Get a token value by name
 */
export function getToken(name: string): string | undefined {
  return tokens.find(t => t.name === name)?.value;
}
`;

      // ============================================
      // FILE 7: Types Definition
      // ============================================
      const typesCode = `/**
 * ${componentName} Type Definitions
 * ${currentLevel.emoji} Atomic Level: ${level}
 */

${propsFromVariants.map(p =>
  `export type ${safeName}${p.name.charAt(0).toUpperCase() + p.name.slice(1)} = ${p.type};`
).join('\n') || '// No variant types'}

export type ${safeName}Variant = {
${propsFromVariants.map(p => `  ${p.name}?: ${p.type};`).join('\n') || '  // No variants defined'}
};

export interface ${safeName}Theme {
  colors: {
    background: string;
    text: string;
    border: string;
    hover: string;
    disabled: string;
  };
  spacing: {
    padding: string;
    gap: string;
  };
  typography: {
    fontFamily: string;
    fontSize: string;
    fontWeight: number;
  };
  borderRadius: string;
}
`;

      // ============================================
      // FILE 8: README Documentation
      // ============================================
      const readmeCode = `# ${componentName}

${currentLevel.emoji} **Atomic Level**: ${level.charAt(0).toUpperCase() + level.slice(1)}

${metadata.description || 'A reusable component from the design system.'}

## Installation

This component is part of the design system. It should already be available in your project.

\`\`\`tsx
import { ${safeName} } from '@/components/${level}s/${safeName}';
\`\`\`

## Usage

### Basic Usage

\`\`\`tsx
<${safeName}>
  Content here
</${safeName}>
\`\`\`

${propsFromVariants.length > 0 ? `### With Variants

\`\`\`tsx
<${safeName} ${propsFromVariants.map(p => `${p.name}="${p.options?.[0] || 'default'}"`).join(' ')}>
  Styled content
</${safeName}>
\`\`\`
` : ''}

### With Click Handler

\`\`\`tsx
<${safeName} onClick={() => console.log('Clicked!')}>
  Click me
</${safeName}>
\`\`\`

### Disabled State

\`\`\`tsx
<${safeName} disabled>
  Disabled
</${safeName}>
\`\`\`

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| \`children\` | \`ReactNode\` | - | Content inside the component |
| \`className\` | \`string\` | - | Additional CSS classes |
${propsFromVariants.map(p => `| \`${p.name}\` | \`${p.type}\` | \`'${p.options?.[0] || 'default'}'\` | ${propertyDescriptions[p.name.charAt(0).toUpperCase() + p.name.slice(1)] || p.name} |`).join('\n')}
| \`disabled\` | \`boolean\` | \`false\` | Disable interaction |
| \`onClick\` | \`() => void\` | - | Click handler |
| \`aria-label\` | \`string\` | - | Accessible label |

## Accessibility

- ✅ Keyboard navigable (Tab, Enter, Space)
- ✅ Screen reader compatible with ARIA attributes
- ✅ Focus visible indicator
- ✅ Disabled state properly announced

## Design Tokens

This component uses the following design tokens:

| Token | Value | Usage |
|-------|-------|-------|
${tokens.slice(0, 10).map((t: any) => `| \`${t.cssVariable}\` | \`${t.value}\` | ${t.category} |`).join('\n') || '| - | - | No tokens |'}

## Figma

${figma.fileKey ? `[View in Figma](https://figma.com/file/${figma.fileKey}?node-id=${figma.nodeId})` : 'Figma link not available'}

**Quality Score**: ${certification.score || 0}/100

---

*Generated by AID Figma Plugin on ${new Date().toISOString()}*
`;

      // ============================================
      // File names for the ZIP
      // ============================================
      const fileNames = [
        `${safeName}.tsx`,
        `${safeName}.module.css`,
        `${safeName}.stories.tsx`,
        `${safeName}.test.tsx`,
        `${safeName}.tokens.ts`,
        `${safeName}.types.ts`,
        `index.ts`,
        `README.md`,
        `metadata.json`
      ];

      // Create actual ZIP file using archiver
      try {
        const zipBuffer = await new Promise<Buffer>((resolve, reject) => {
          const chunks: Buffer[] = [];
          const passthrough = new PassThrough();

          passthrough.on('data', (chunk) => chunks.push(chunk));
          passthrough.on('end', () => resolve(Buffer.concat(chunks)));
          passthrough.on('error', reject);

          const archive = archiver('zip', { zlib: { level: 9 } });
          archive.on('error', reject);
          archive.pipe(passthrough);

          // Add all files to the ZIP inside the component folder
          archive.append(componentCode, { name: `${safeName}/${safeName}.tsx` });
          archive.append(stylesCode, { name: `${safeName}/${safeName}.module.css` });
          archive.append(storiesCode, { name: `${safeName}/${safeName}.stories.tsx` });
          archive.append(testCode, { name: `${safeName}/${safeName}.test.tsx` });
          archive.append(tokensCode, { name: `${safeName}/${safeName}.tokens.ts` });
          archive.append(typesCode, { name: `${safeName}/${safeName}.types.ts` });
          archive.append(indexCode, { name: `${safeName}/index.ts` });
          archive.append(readmeCode, { name: `${safeName}/README.md` });

          // Add metadata.json for reference
          const metadataJson = JSON.stringify({
            componentName: safeName,
            originalName: componentName,
            level,
            destinationPath,
            atomicInfo: currentLevel,
            metadata,
            tokens,
            certification,
            figma,
            files: fileNames,
            generatedAt: new Date().toISOString()
          }, null, 2);
          archive.append(metadataJson, { name: `${safeName}/metadata.json` });

          archive.finalize();
        });

        const zipBase64 = zipBuffer.toString('base64');
        const downloadFilename = `${safeName}.zip`;

        console.log(`export_to_aid: Generated ZIP for ${componentName} with ${fileNames.length} files (${zipBuffer.length} bytes)`);

        // Return in the exact format plugin expects for cloud export
        return res.json({
          jsonrpc: '2.0',
          id,
          result: {
            success: true,
            componentName: safeName,
            relativePath: destinationPath,
            files: fileNames,
            // Plugin reads: result.react?.componentDir
            react: {
              componentDir: destinationPath
            },
            // Cloud export fields - actual ZIP file
            isCloudExport: true,
            zipBase64: zipBase64,
            downloadFilename: downloadFilename,
            downloadSize: zipBuffer.length,
            exported: true,
            timestamp: new Date().toISOString()
          }
        });
      } catch (zipError) {
        console.error('export_to_aid: ZIP creation failed:', zipError);
        return res.json({
          jsonrpc: '2.0',
          id,
          error: {
            code: -32000,
            message: `Failed to create ZIP: ${zipError}`
          }
        });
      }
    }

    // Unknown tool - return error
    console.log(`Unknown tool: ${toolName}`);
    return res.json({
      jsonrpc: '2.0',
      id,
      error: {
        code: -32601,
        message: `Unknown tool: ${toolName}`
      }
    });
  }

  // Unknown method
  return res.json({
    jsonrpc: '2.0',
    id,
    error: {
      code: -32601,
      message: `Method not found: ${method}`
    }
  });
});

// Error handler
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error('Server error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
app.listen(PORT, () => {
  console.log(`
  ╔════════════════════════════════════════════════════════╗
  ║           AID Figma Plugin Server                       ║
  ╠════════════════════════════════════════════════════════╣
  ║  Status:  Running                                       ║
  ║  Port:    ${PORT}                                          ║
  ║  Health:  http://localhost:${PORT}/health                  ║
  ║  Auth:    http://localhost:${PORT}/auth/*                  ║
  ║  MCP:     http://localhost:${PORT}/mcp                     ║
  ╚════════════════════════════════════════════════════════╝
  `);
});

export default app;
