/**
 * @file aidExporter.js
 * @description Exports validated components to the AID project structure.
 *              Enforces score >= 90 requirement and organizes by atomic level.
 * @related
 *   - ../index.js - Main server, calls exportComponent()
 *   - ./componentAuditor.js - Provides validation scores
 *   - ./scoringEngine.js - Provides export readiness check
 * @created 2025-12-23
 */

const fs = require('fs');
const path = require('path');
const { generateReactComponent, generateReactComponentContents } = require('./reactGenerator');
const { createZip } = require('./zipExporter');

// Default output path (can be overridden by env)
const OUTPUT_PATH = process.env.AID_PROJECT_PATH || path.join(__dirname, '../../output');

// Whether to generate React component files (in addition to JSON)
const GENERATE_REACT = process.env.AID_GENERATE_REACT !== 'false';

// Check if running in cloud environment (Cloud Run sets K_SERVICE env var)
const IS_CLOUD_ENVIRONMENT = process.env.NODE_ENV === 'production' || !!process.env.K_SERVICE;

/**
 * Export a component to the AID pipeline
 * In cloud environment: Returns file contents for download
 * In local environment: Writes files to disk
 * @param {Object} payload - Export payload from plugin
 * @returns {Object} Export result with file contents (cloud) or file paths (local)
 */
async function exportComponent(payload) {
  const { component, metadata, tokens, content, certification } = payload;

  // Validate export requirements
  const validation = validateExport(payload);
  if (!validation.valid) {
    return {
      success: false,
      error: 'validation_failed',
      message: validation.message,
      issues: validation.issues
    };
  }

  try {
    // Generate component ID
    const componentId = generateComponentId(component);

    // Determine level - priority: component.level (from audit) > metadata.level > classify
    const level = component?.level || metadata?.level || classifyLevel(component);
    console.log('[AIDExporter] Level determination:', {
      'component.level': component?.level,
      'metadata.level': metadata?.level,
      'classifyLevel': classifyLevel(component),
      'final': level
    });

    // Build export data
    const exportData = buildExportData({
      componentId,
      component,
      metadata,
      tokens,
      content,
      certification
    });

    // Cloud environment: Create ZIP and return download URL
    if (IS_CLOUD_ENVIRONMENT) {
      console.log('[AIDExporter] Running in CLOUD environment - creating ZIP for download');
      return await exportToCloud(exportData, componentId, level, component);
    }

    // Local environment: Write to disk
    console.log('[AIDExporter] Running in LOCAL environment - writing to disk');
    return exportToDisk(exportData, componentId, level, component);

  } catch (error) {
    console.error('[AIDExporter] Export error:', error);
    return {
      success: false,
      error: 'export_failed',
      message: error.message
    };
  }
}

/**
 * Export for cloud environment - creates ZIP and returns it as base64
 * This avoids instance affinity issues on Cloud Run by returning data directly
 */
async function exportToCloud(exportData, componentId, level, component) {
  const fileContents = {};
  let componentName = componentId;

  // Add JSON export data
  const jsonFilename = `${componentId}.json`;
  fileContents[jsonFilename] = JSON.stringify(exportData, null, 2);

  // Generate React component contents
  if (GENERATE_REACT) {
    console.log('[AIDExporter] Generating React component contents...');
    const reactResult = generateReactComponentContents(exportData);

    if (reactResult.success) {
      // Merge React file contents
      Object.assign(fileContents, reactResult.fileContents);
      componentName = reactResult.componentName;
      console.log(`[AIDExporter] ✅ Generated React files:`, Object.keys(reactResult.fileContents));
    }
  }

  const files = Object.keys(fileContents);
  const relativePath = `components/${level}/${componentName}`;

  // Create ZIP as base64 (avoids Cloud Run instance affinity issues)
  console.log('[AIDExporter] 📦 Creating ZIP as base64 for cloud download...');
  const zipResult = await createZipAsBase64(fileContents, componentName, relativePath, level);

  console.log('[AIDExporter] ✅ ZIP created as base64:', zipResult.filename, `(${zipResult.size} bytes)`);

  return {
    success: true,
    componentId,
    componentName,
    level,
    relativePath,
    message: `Successfully generated ${component.name}`,
    files,
    // ZIP as base64 for direct download
    zipBase64: zipResult.base64,
    downloadFilename: zipResult.filename,
    downloadSize: zipResult.size,
    isCloudExport: true
  };
}

/**
 * Create ZIP as base64 string (no file storage needed)
 */
async function createZipAsBase64(fileContents, componentName, relativePath, level) {
  const archiver = require('archiver');
  const { PassThrough } = require('stream');

  return new Promise((resolve, reject) => {
    const chunks = [];
    const passThrough = new PassThrough();

    passThrough.on('data', chunk => chunks.push(chunk));
    passThrough.on('end', () => {
      const buffer = Buffer.concat(chunks);
      const base64 = buffer.toString('base64');

      resolve({
        base64,
        filename: `${componentName}.zip`,
        size: buffer.length
      });
    });
    passThrough.on('error', reject);

    const archive = archiver('zip', { zlib: { level: 9 } });
    archive.on('error', reject);
    archive.pipe(passThrough);

    // Build folder structure: {level}/{componentName}/files
    const folderPath = `${level}/${componentName}`;

    for (const [filename, content] of Object.entries(fileContents)) {
      archive.append(content, { name: `${folderPath}/${filename}` });
    }

    // Add README
    const readme = `# ${componentName}

Exported from Figma AID Plugin

## Atomic Level: ${level.toUpperCase()}

## Installation

Copy the \`${level}\` folder to your project:
\`\`\`
src/components/${level}/${componentName}/
\`\`\`

## Import
\`\`\`tsx
import { ${componentName} } from '@/components/${level}/${componentName}';
\`\`\`

## Files
${Object.keys(fileContents).map(f => `- ${f}`).join('\n')}

Generated: ${new Date().toISOString()}
`;
    archive.append(readme, { name: `${folderPath}/README.md` });

    archive.finalize();
  });
}

/**
 * Export for local environment - writes to disk
 */
async function exportToDisk(exportData, componentId, level, component) {
  const outputDir = path.join(OUTPUT_PATH, 'components', level);

  // Ensure directory exists
  await ensureDirectory(outputDir);

  // Write JSON component file
  const filePath = path.join(outputDir, `${componentId}.json`);
  await writeJsonFile(filePath, exportData);

  // Update index file
  await updateComponentIndex(level, componentId, component.name);

  console.log(`[AIDExporter] Exported ${component.name} to ${filePath}`);

  // Generate React component files if enabled
  let reactResult = null;
  if (GENERATE_REACT) {
    console.log('[AIDExporter] GENERATE_REACT is enabled, generating React component...');
    try {
      reactResult = await generateReactComponent(exportData, outputDir);
      console.log(`[AIDExporter] ✅ Generated React component: ${reactResult.componentName}`);
      console.log(`[AIDExporter] 📁 Generated files:`, reactResult.files);
      console.log(`[AIDExporter] 📂 Component directory: ${reactResult.componentDir}`);
    } catch (reactError) {
      console.error('[AIDExporter] ❌ React generation error:', reactError);
    }
  }

  return {
    success: true,
    componentId,
    filePath: filePath.replace(OUTPUT_PATH, ''),
    level,
    message: `Successfully exported ${component.name}`,
    react: reactResult,
    files: reactResult ? [
      `${componentId}.json`,
      ...reactResult.files
    ] : [`${componentId}.json`],
    componentDir: reactResult?.componentDir,
    isCloudExport: false
  };
}

/**
 * Validate export requirements
 */
function validateExport(payload) {
  const issues = [];

  // Check component data
  if (!payload.component) {
    issues.push('Missing component data');
  }

  if (!payload.component?.name) {
    issues.push('Component name is required');
  }

  // Check certification/score
  const score = payload.certification?.score || payload.score || 0;
  if (score < 90) {
    issues.push(`Score ${score} is below export threshold (90)`);
  }

  // Check for blocking issues
  if (payload.certification?.hasBlockingIssues) {
    issues.push('Component has blocking issues that must be resolved');
  }

  return {
    valid: issues.length === 0,
    message: issues.length > 0 ? issues.join('; ') : null,
    issues
  };
}

/**
 * Generate a unique component ID
 */
function generateComponentId(component) {
  const name = component.name || 'untitled';
  const baseName = name
    .split('/')
    .pop()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');

  const nodeId = component.nodeId || '';
  const suffix = nodeId ? `-${nodeId.replace(':', '-')}` : '';

  return `${baseName}${suffix}`;
}

/**
 * Classify component level if not provided
 */
function classifyLevel(component) {
  const name = (component.name || '').toLowerCase();

  if (/^(icon|button|input|label|badge|chip|avatar|divider)/i.test(name)) {
    return 'atoms';
  }
  if (/^(card|form-field|list-item|menu-item|search|dropdown)/i.test(name)) {
    return 'molecules';
  }
  if (/^(header|footer|sidebar|modal|dialog|form|table|nav)/i.test(name)) {
    return 'organisms';
  }
  if (/^(page|layout|template|view)/i.test(name)) {
    return 'templates';
  }

  return 'molecules';
}

/**
 * Build the export data structure
 */
function buildExportData(data) {
  const { componentId, component, metadata, tokens, content, certification } = data;

  return {
    $schema: 'aid-component-v1',
    version: '1.0',
    id: componentId,
    name: component.name,
    type: component.type,
    nodeId: component.nodeId,

    metadata: {
      description: metadata?.description || '',
      formattedDescription: metadata?.formattedDescription || '',
      tags: metadata?.tags || '',
      notes: metadata?.notes || '',
      ariaLabel: metadata?.ariaLabel || '',
      category: metadata?.category || 'layout',
      level: metadata?.level || 'molecule',
      priority: metadata?.priority || 'medium'
    },

    tokens: tokens || [],

    variants: component.variants || [],

    content: content || {},

    certification: {
      score: certification?.score || 0,
      exportedAt: new Date().toISOString(),
      auditPassed: certification?.auditPassed || false,
      metadataComplete: certification?.metadataComplete || false
    },

    figma: {
      fileKey: component.fileKey || null,
      nodeId: component.nodeId,
      exportedFrom: 'aid-figma-plugin'
    }
  };
}

/**
 * Ensure directory exists
 */
async function ensureDirectory(dirPath) {
  try {
    await fs.promises.mkdir(dirPath, { recursive: true });
  } catch (error) {
    if (error.code !== 'EEXIST') {
      throw error;
    }
  }
}

/**
 * Write JSON file
 */
async function writeJsonFile(filePath, data) {
  const content = JSON.stringify(data, null, 2);
  await fs.promises.writeFile(filePath, content, 'utf-8');
}

/**
 * Update the component index for a level
 */
async function updateComponentIndex(level, componentId, componentName) {
  const indexPath = path.join(OUTPUT_PATH, 'components', level, '_index.json');

  let index = { components: [] };

  // Load existing index if it exists
  try {
    const content = await fs.promises.readFile(indexPath, 'utf-8');
    index = JSON.parse(content);
  } catch (error) {
    // Index doesn't exist yet, use empty
  }

  // Add or update component entry
  const existingIndex = index.components.findIndex(c => c.id === componentId);
  const entry = {
    id: componentId,
    name: componentName,
    updatedAt: new Date().toISOString()
  };

  if (existingIndex >= 0) {
    index.components[existingIndex] = entry;
  } else {
    index.components.push(entry);
  }

  // Sort by name
  index.components.sort((a, b) => a.name.localeCompare(b.name));

  // Write index
  await writeJsonFile(indexPath, index);
}

/**
 * List exported components
 */
async function listExportedComponents(level = null) {
  const componentsDir = path.join(OUTPUT_PATH, 'components');

  try {
    const levels = level ? [level] : await fs.promises.readdir(componentsDir);
    const components = [];

    for (const lvl of levels) {
      const levelDir = path.join(componentsDir, lvl);
      const stat = await fs.promises.stat(levelDir);

      if (stat.isDirectory()) {
        const indexPath = path.join(levelDir, '_index.json');
        try {
          const content = await fs.promises.readFile(indexPath, 'utf-8');
          const index = JSON.parse(content);
          components.push(...index.components.map(c => ({ ...c, level: lvl })));
        } catch {
          // No index for this level
        }
      }
    }

    return components;
  } catch (error) {
    console.error('[AIDExporter] Error listing components:', error);
    return [];
  }
}

module.exports = {
  exportComponent,
  listExportedComponents,
  validateExport
};
