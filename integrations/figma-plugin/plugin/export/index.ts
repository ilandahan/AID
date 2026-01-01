/**
 * @file plugin/export/index.ts
 * @description Export functionality - handles component export to AID system
 */

import { ContentExtractor } from '../../services';
import { logger } from '../../Logger';
import { currentState, mcpClient } from '../state';
import { sendToUI, sendError } from '../ui-messaging';
import type { AtomicLevel, AIDExportPayload } from '../types';

// ============================================
// Export to AID
// ============================================

// NOTE: Component classification logic is on the SERVER (single source of truth)
// The plugin uses currentState.audit.level and currentState.audit.destinationPath
// from the server response instead of duplicating classification logic here

/**
 * Export component to AID design system
 */
export async function exportToAID(
  level?: AtomicLevel,
  componentName?: string
): Promise<void> {
  if (!currentState.selectedNode) {
    sendError('No component selected');
    return;
  }

  // Check score threshold (70 minimum per documentation)
  const score =
    currentState.report?.overallScore || currentState.audit?.score || 0;
  if (score < 70) {
    sendError(`Export blocked: Score ${score}/100 (minimum: 70)`);
    return;
  }

  if (!mcpClient || !mcpClient.isConnected()) {
    sendError('MCP connection required for export');
    return;
  }

  try {
    // Get level and path from SERVER (single source of truth)
    // Falls back to provided value or 'molecule' if server hasn't responded yet
    const classifiedLevel = level || currentState.audit?.level || 'molecule';
    const name = componentName || currentState.selectedNode.name;
    const destinationPath = currentState.audit?.destinationPath || `src/components/molecules/${name}/`;

    figma.notify(`Exporting ${name} as ${classifiedLevel.toUpperCase()} to AID...`);

    // Build export payload
    const payload: AIDExportPayload = {
      component: {
        name: name,
        type: currentState.selectedNode.type,
        description: currentState.generated?.description || '',
        level: classifiedLevel,
        destinationPath: destinationPath,
      },
      metadata: currentState.generated || ({} as any),
      tokens: currentState.tokens,
      content: extractContentData(),
      qualityCertification: {
        score: score,
        auditedAt: new Date(),
        passedChecks: currentState.audit?.suggestions || [],
      },
      figma: {
        fileKey: figma.fileKey || 'unknown',
        nodeId: currentState.selectedNode.id,
        exportedAt: new Date(),
      },
      filesToCreate: {
        component: `${destinationPath}${name.replace(/[^a-zA-Z0-9]/g, '')}.tsx`,
        styles: `${destinationPath}${name.replace(/[^a-zA-Z0-9]/g, '')}.module.css`,
        test: `${destinationPath}${name.replace(/[^a-zA-Z0-9]/g, '')}.test.tsx`,
        index: `${destinationPath}index.ts`,
      },
    };

    const result = await mcpClient.exportToAID(payload);

    if (result.success) {
      sendToUI({
        type: 'EXPORT_SUCCESS',
        format: 'AID',
        files: result.files,
        componentDir: result.componentDir,
        // Cloud export fields - ZIP as base64
        zipBase64: result.zipBase64,
        downloadFilename: result.downloadFilename,
        downloadSize: result.downloadSize,
        isCloudExport: result.isCloudExport,
        componentName: result.componentName,
        relativePath: result.relativePath
      });

      if (result.isCloudExport) {
        figma.notify(
          `✅ ${name} ready! Click Download in the plugin.`
        );
      } else {
        figma.notify(
          `✅ Exported ${name} as ${classifiedLevel.toUpperCase()} to AID Design System!`
        );
      }
    } else {
      sendError(result.error || 'Export failed');
    }
  } catch (error) {
    sendError(
      `Export failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}

// ============================================
// Content Export (JSON, TypeScript, CSV)
// ============================================

/**
 * Export content in various formats
 */
export function exportContent(format: 'json' | 'typescript' | 'csv'): void {
  if (!currentState.selectedNode) {
    sendError('No component selected');
    return;
  }

  try {
    const components = ContentExtractor.extractFromSelection();

    if (components.length === 0) {
      sendError('No content to export');
      return;
    }

    let content: string;
    let filename: string;

    switch (format) {
      case 'typescript':
        content = ContentExtractor.toTypeScript(components);
        filename = 'content.ts';
        break;
      case 'json':
        content = ContentExtractor.toJSON(components);
        filename = 'content.json';
        break;
      case 'csv':
        content = ContentExtractor.toCSV(components);
        filename = 'content.csv';
        break;
    }

    // Send content to UI for clipboard copy
    figma.ui.postMessage({
      type: 'CONTENT_EXPORTED',
      content,
      format,
      filename,
    });

    sendToUI({ type: 'EXPORT_SUCCESS', format });
    figma.notify(`Exported as ${format.toUpperCase()}`);
  } catch (error) {
    sendError(
      `Export failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}

/**
 * Extract content data from current selection
 */
export function extractContentData(): Record<string, string> {
  if (!currentState.selectedNode) return {};

  const components = ContentExtractor.extractFromSelection();
  if (components.length === 0) return {};

  return components[0].defaultContent;
}
