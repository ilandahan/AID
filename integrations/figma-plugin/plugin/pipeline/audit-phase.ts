/**
 * @file plugin/pipeline/audit-phase.ts
 * @description Phase 1: Audit - Local and server audit logic
 */

import { ComponentAuditor, nodeAnalyzer } from '../../services';
import { logger } from '../../Logger';
import { currentState, mcpClient } from '../state';
import { sendToUI, sendError, sendPipelineStep } from '../ui-messaging';

// ============================================
// Phase 1: Local Audit (fallback when no MCP)
// ============================================

/**
 * Run local audit using ComponentAuditor
 * Shows progress feedback for deep inspection
 */
export function runLocalAudit(): void {
  if (!currentState.selectedNode) {
    sendError('No component selected');
    return;
  }

  const node = currentState.selectedNode;
  const isComponentSet = node.type === 'COMPONENT_SET';
  const variantCount = isComponentSet
    ? (node as ComponentSetNode).children.filter((c) => c.type === 'COMPONENT').length
    : 0;

  // Show progress for deep inspection
  if (isComponentSet && variantCount > 0) {
    figma.notify(`🔍 Deep inspecting ${variantCount} variants...`, { timeout: 2000 });
    sendPipelineStep('audit', 'running', `Inspecting ${variantCount} variants`);
  } else {
    figma.notify('🔍 Running local audit...');
    sendPipelineStep('audit', 'running', 'Analyzing component');
  }

  // Extract tokens during local audit too (needed for metadata generation)
  try {
    const nodeInfo = nodeAnalyzer.extractNodeInfo(node);
    currentState.tokens = nodeAnalyzer.extractTokens(nodeInfo);
    logger.debug('[PLUGIN] Local audit extracted', currentState.tokens?.length || 0, 'tokens');
  } catch (tokenError) {
    logger.debug('[PLUGIN] Token extraction failed:', tokenError);
    currentState.tokens = [];
  }

  // Run audit with deep inspection
  const audit = ComponentAuditor.runLocalAudit(node);
  currentState.audit = audit;

  // Show completion with issue count
  const issueCount = audit.issues?.length || 0;
  const message =
    issueCount > 0
      ? `Audit complete: ${audit.score}/100 (${issueCount} issues found)`
      : `Audit complete: ${audit.score}/100 ✓`;

  sendToUI({ type: 'AUDIT_COMPLETE', audit });
  sendPipelineStep('audit', 'complete', message);
  figma.notify(message);
}

// ============================================
// Phase 1: Server Audit (via MCP)
// ============================================

/**
 * Run server audit via MCP connection
 */
export async function runServerAudit(): Promise<void> {
  if (!currentState.selectedNode) {
    sendError('No component selected');
    return;
  }

  if (!mcpClient || !mcpClient.isConnected()) {
    sendError('Not connected to server. Please pair first.');
    return;
  }

  const node = currentState.selectedNode;
  const isComponentSet = node.type === 'COMPONENT_SET';
  const variantCount = isComponentSet
    ? (node as ComponentSetNode).children.filter((c) => c.type === 'COMPONENT').length
    : 0;

  try {
    // Show progress for deep inspection
    if (isComponentSet && variantCount > 0) {
      figma.notify(`🔍 Deep inspecting ${variantCount} variants via server...`, {
        timeout: 3000,
      });
      sendPipelineStep(
        'audit',
        'running',
        `Sending ${variantCount} variants to server`
      );
    } else {
      figma.notify('🔍 Running server audit...');
      sendPipelineStep('audit', 'running', 'Sending to server');
    }

    // Prepare data for server audit
    const auditRequest = ComponentAuditor.prepareForMCP(currentState.selectedNode);

    // Extract tokens
    const nodeInfo = nodeAnalyzer.extractNodeInfo(currentState.selectedNode);
    currentState.tokens = nodeAnalyzer.extractTokens(nodeInfo);
    auditRequest.tokens = currentState.tokens;

    // Add existing description
    if ('description' in currentState.selectedNode) {
      auditRequest.existingDescription =
        (currentState.selectedNode as ComponentSetNode).description || '';
    }

    // Run server audit
    const audit = await mcpClient.auditComponent(auditRequest);
    currentState.audit = audit;

    // Show completion with issue count
    const issueCount = audit.issues?.length || 0;
    const message =
      issueCount > 0
        ? `Audit complete: ${audit.score}/100 (${issueCount} issues found)`
        : `Audit complete: ${audit.score}/100 ✓`;

    sendToUI({ type: 'AUDIT_COMPLETE', audit });
    sendPipelineStep('audit', 'complete', message);
    figma.notify(message);
  } catch (error) {
    sendPipelineStep('audit', 'error', 'Audit failed');
    sendError(
      `Audit failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}

// ============================================
// Deep Inspection Helper
// ============================================

/**
 * Run deep inspection and return issues for merging with server audit
 */
export function runDeepInspection(node: SceneNode): {
  issues: any[];
  score: number;
} {
  logger.debug('[PLUGIN] Running local deep inspection...');

  const isComponentSet = node.type === 'COMPONENT_SET';
  const variantCount = isComponentSet
    ? (node as ComponentSetNode).children.filter((c) => c.type === 'COMPONENT').length
    : 0;

  if (isComponentSet && variantCount > 0) {
    figma.notify(`🔍 Deep inspecting ${variantCount} variants...`, { timeout: 2000 });
  }

  const localAudit = ComponentAuditor.runLocalAudit(node);
  const deepInspectionIssues = localAudit.issues || [];
  logger.debug('[PLUGIN] Deep inspection found', deepInspectionIssues.length, 'issues');

  return {
    issues: deepInspectionIssues,
    score: localAudit.score || 100,
  };
}

/**
 * Merge server audit with deep inspection issues, removing duplicates
 */
export function mergeAuditResults(
  serverAudit: any,
  deepInspection: { issues: any[]; score: number }
): any {
  const mergedIssues = [...(serverAudit.issues || []), ...deepInspection.issues];

  // Deduplicate by message
  const seenMessages = new Set<string>();
  const uniqueIssues = mergedIssues.filter((issue) => {
    const key = `${issue.message}-${issue.location || ''}`;
    if (seenMessages.has(key)) return false;
    seenMessages.add(key);
    return true;
  });

  return {
    ...serverAudit,
    issues: uniqueIssues,
    // Use lower score (more conservative)
    score: Math.min(serverAudit.score || 100, deepInspection.score),
  };
}
