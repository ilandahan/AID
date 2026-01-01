/**
 * @file plugin/pipeline/metadata-phase.ts
 * @description Phase 2 & 3: Metadata analysis and generation
 */

import { ComponentAuditor, scoringEngine } from '../../services';
import { logger } from '../../Logger';
import { currentState, mcpClient } from '../state';
import { sendToUI, sendError, sendPipelineStep } from '../ui-messaging';

// ============================================
// Shared Helpers
// ============================================

/**
 * Inject local tokens into generated metadata if server returned none.
 * This ensures tokens always reach the UI for the Dev Info tab.
 * @param generated - The generated metadata from server
 * @param localTokens - The locally extracted tokens from Figma
 * @returns The generated metadata with tokens injected if needed
 */
export function injectTokensIfNeeded(generated: any, localTokens: any[]): any {
  if (!localTokens || localTokens.length === 0) {
    return generated;
  }

  const hasTokens =
    generated.tokens &&
    (Array.isArray(generated.tokens)
      ? generated.tokens.length > 0
      : Object.keys(generated.tokens).length > 0);

  if (!hasTokens) {
    logger.debug(
      '[PLUGIN] 🎨 Injecting local tokens into generated (server returned none):',
      localTokens.length
    );
    generated.tokens = localTokens;
  } else {
    logger.debug('[PLUGIN] 🎨 Server returned tokens, using those');
  }

  return generated;
}

// ============================================
// Phase 2: Metadata Analysis
// ============================================

/**
 * Analyze existing metadata on the component
 */
export async function analyzeMetadata(): Promise<void> {
  logger.debug('[PLUGIN] analyzeMetadata() called');

  if (!currentState.selectedNode) {
    logger.debug('[PLUGIN] ERROR: No component selected');
    sendError('No component selected');
    return;
  }

  logger.debug(
    '[PLUGIN] Selected node:',
    currentState.selectedNode.name,
    currentState.selectedNode.type
  );

  try {
    // For INSTANCE nodes, we need to get description from the main component
    // since instances don't inherit the description property
    let targetNode: SceneNode = currentState.selectedNode;
    let description: string | undefined;

    if (currentState.selectedNode.type === 'INSTANCE') {
      const instance = currentState.selectedNode as InstanceNode;
      const mainComponent = instance.mainComponent;

      if (mainComponent) {
        logger.debug('[PLUGIN] Instance detected - reading from main component');
        logger.debug('[PLUGIN] Main Component:', mainComponent.name);
        logger.debug('[PLUGIN] Main Component ID:', mainComponent.id);

        // Check if main component is part of a component set
        if (mainComponent.parent?.type === 'COMPONENT_SET') {
          const componentSet = mainComponent.parent as ComponentSetNode;
          description = componentSet.description;
          targetNode = componentSet;
          logger.debug('[PLUGIN] Reading from parent ComponentSet:', componentSet.name);
        } else {
          description = mainComponent.description;
          targetNode = mainComponent;
        }
      }
    } else if ('description' in currentState.selectedNode) {
      description = (currentState.selectedNode as ComponentNode | ComponentSetNode)
        .description;
    }

    logger.debug('[PLUGIN] Existing description length:', description?.length || 0);
    logger.debug('[PLUGIN] Description preview:', description?.substring(0, 100) || 'NONE');

    // Check MCP connection status
    const mcpConnected = mcpClient && mcpClient.isConnected();
    logger.debug('[PLUGIN] MCP connected:', mcpConnected);
    logger.debug('[PLUGIN] Analyzing target node:', targetNode.name, targetNode.type);

    // If connected to MCP, use Claude for deeper analysis
    if (mcpConnected) {
      figma.notify('Analyzing metadata with Claude...');

      // Use targetNode (main component for instances) for proper analysis
      const auditRequest = ComponentAuditor.prepareForMCP(targetNode);
      auditRequest.existingDescription = description;

      logger.debug('[PLUGIN] Calling mcpClient.analyzeMetadata...');
      const metadata = await mcpClient.analyzeMetadata(auditRequest);
      logger.debug(
        '[PLUGIN] Received metadata:',
        JSON.stringify(metadata).substring(0, 300)
      );

      currentState.metadata = metadata;

      sendToUI({ type: 'METADATA_ANALYZED', metadata });
      figma.notify(`Metadata analysis complete: ${metadata.completenessScore}%`);
    } else {
      // Local analysis fallback
      logger.debug('[PLUGIN] Using local analysis (MCP not connected)');
      figma.notify('Analyzing metadata locally...');

      // Use targetNode (main component for instances) for proper analysis
      const metadata = ComponentAuditor.analyzeMetadataLocal(
        targetNode,
        description
      );
      logger.debug(
        '[PLUGIN] Local metadata result:',
        JSON.stringify(metadata).substring(0, 300)
      );

      currentState.metadata = metadata;

      sendToUI({ type: 'METADATA_ANALYZED', metadata });
      figma.notify(`Metadata analysis complete: ${metadata.completenessScore}%`);
    }
  } catch (error) {
    logger.error('[PLUGIN] analyzeMetadata error:', error);
    sendError(
      `Metadata analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}

// ============================================
// Phase 3: Generate Metadata
// ============================================

/**
 * Generate metadata using Claude (requires MCP connection)
 */
export async function generateMetadata(): Promise<void> {
  logger.debug('═══════════════════════════════════════════════════════════════════');
  logger.debug('[PLUGIN] 🤖 GENERATE METADATA STARTED');
  logger.debug('═══════════════════════════════════════════════════════════════════');

  if (!currentState.selectedNode) {
    logger.debug('[PLUGIN] ❌ ERROR: No component selected');
    sendError('No component selected');
    return;
  }

  logger.debug('[PLUGIN] 📦 Component:', currentState.selectedNode.name);
  logger.debug('[PLUGIN] 📦 Type:', currentState.selectedNode.type);
  logger.debug('[PLUGIN] 📦 Node ID:', currentState.selectedNode.id);

  if (!mcpClient || !mcpClient.isConnected()) {
    logger.debug('[PLUGIN] ❌ ERROR: Claude connection required');
    sendError('Claude connection required for metadata generation');
    return;
  }

  logger.debug('[PLUGIN] ✅ Claude connection active');

  try {
    figma.notify('Generating metadata with Claude...');

    // Prepare request
    const auditRequest = ComponentAuditor.prepareForMCP(currentState.selectedNode);
    auditRequest.tokens = currentState.tokens;

    // Log what we're sending
    logger.debug('[PLUGIN] 📤 Request prepared:');
    logger.debug('    - Component:', auditRequest.component?.name);
    logger.debug('    - Properties count:', auditRequest.component?.properties?.length || 0);
    logger.debug('    - Variants count:', auditRequest.component?.variants?.length || 0);
    logger.debug('    - Children count:', auditRequest.component?.children?.length || 0);
    logger.debug('    - Tokens count:', auditRequest.tokens?.length || 0);

    // Generate with Claude
    logger.debug('[PLUGIN] 🔄 Calling Claude for metadata generation...');
    const generated = await mcpClient.generateMetadata(auditRequest);

    // Inject local tokens if server returned none
    injectTokensIfNeeded(generated, currentState.tokens);

    currentState.generated = generated;

    // Log what we received
    logGeneratedMetadata(generated);

    // Also generate full report if we have audit and metadata
    if (currentState.audit && currentState.metadata) {
      generateReportFromMetadata(generated);
    }

    logger.debug('[PLUGIN] Step 5: Sending METADATA_GENERATED...');
    sendToUI({ type: 'METADATA_GENERATED', generated });
    logger.debug('[PLUGIN] ✅ METADATA_GENERATED sent to UI');
    logger.debug('───────────────────────────────────────────────────────────────────');
    figma.notify('Metadata generated successfully!');
  } catch (error) {
    logger.debug(
      '[PLUGIN] ❌ EXCEPTION:',
      error instanceof Error ? error.message : 'Unknown error'
    );
    sendError(
      `Generation failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}

// ============================================
// Helper Functions
// ============================================

/**
 * Log generated metadata with defensive error handling
 */
function logGeneratedMetadata(generated: any): void {
  logger.debug('[PLUGIN] 📥 Metadata received from Claude:');
  if (generated) {
    try {
      const desc = generated.description;
      logger.debug(
        '    - Description:',
        typeof desc === 'string' ? desc.substring(0, 80) + '...' : String(desc || 'none')
      );
    } catch (e) {
      logger.debug('    - Description: [error logging]', e);
    }

    try {
      const tags = generated.tags;
      const tagsStr = Array.isArray(tags) ? tags.join(', ') : String(tags || 'none');
      logger.debug('    - Tags:', tagsStr);
    } catch (e) {
      logger.debug('    - Tags: [error logging]', e);
    }

    try {
      logger.debug('    - Category:', String(generated.category || 'none'));
    } catch (e) {
      logger.debug('    - Category: [error logging]', e);
    }

    try {
      logger.debug('    - Level:', String(generated.level || 'none'));
    } catch (e) {
      logger.debug('    - Level: [error logging]', e);
    }

    try {
      const formatted = generated.formattedDescription || generated.formattedForFigma;
      const len = typeof formatted === 'string' ? formatted.length : 0;
      logger.debug('    - Formatted length:', len);
    } catch (e) {
      logger.debug('    - Formatted: [error logging]', e);
    }

    // Log tokens for debugging
    try {
      const tokens = generated.tokens;
      if (Array.isArray(tokens)) {
        logger.debug('    - Tokens (array):', tokens.length, 'items');
      } else if (tokens && typeof tokens === 'object') {
        logger.debug('    - Tokens (object):', Object.keys(tokens).join(', '));
      } else {
        logger.debug('    - Tokens: none');
      }
    } catch (e) {
      logger.debug('    - Tokens: [error logging]', e);
    }
  } else {
    logger.debug('    ⚠️ No generated metadata returned!');
  }
}

/**
 * Generate report from metadata and send to UI
 */
function generateReportFromMetadata(generated: any): void {
  try {
    logger.debug('[PLUGIN] Step 2: Calling scoringEngine.generateReport...');
    const report = scoringEngine.generateReport(
      currentState.selectedNode!.name,
      currentState.selectedNode!.type as 'COMPONENT' | 'COMPONENT_SET' | 'INSTANCE',
      currentState.audit!,
      currentState.metadata!,
      generated
    );
    currentState.report = report;
    logger.debug('[PLUGIN] Step 3: Report generated, sending to UI...');
    sendToUI({ type: 'REPORT_READY', report });
    logger.debug('[PLUGIN] Step 4: REPORT_READY sent');
  } catch (reportError) {
    logger.debug(
      '[PLUGIN] ❌ Report generation error:',
      reportError instanceof Error ? reportError.message : String(reportError)
    );
  }
}
