/**
 * @file code.ts
 * @description Main entry point for the Figma Atomic Design Extractor plugin.
 *              Coordinates the 4-phase quality pipeline: Audit → Analyze → Generate → Report.
 * @created 2024-12
 * @refactored 2024-12 - Extracted modules to ./plugin/
 */

import { nodeAnalyzer, ComponentAuditor } from './services';
import { logger } from './Logger';
import { UI_CONFIG } from './config';

// Import from refactored plugin modules
import {
  // State
  currentState,
  mcpClient,
  settings,
  // UI messaging
  sendToUI,
  sendError,
  sendPipelineStep,
  handleSelectionChange,
  selectNodeById,
  // Pipeline phases
  runServerAudit,
  analyzeMetadata,
  generateMetadata,
  applyMetadataToFigma,
  runDeepInspection,
  mergeAuditResults,
  injectTokensIfNeeded,
  // Export
  exportToAID,
  exportContent,
  // MCP connection
  connectMCP,
  disconnectMCP,
  stopHealthCheck,
  // AID pairing
  loadCustomEndpoint,
  pairWithAID,
  checkAIDToken,
  disconnectFromAID,
  stopHeartbeat,
  // Types
  type UIToPluginMessage,
  type PipelineResults,
} from './plugin';

// ============================================
// Full Pipeline
// ============================================

/**
 * Run the complete 4-phase quality pipeline:
 * 1. Audit - Check for style guide compliance
 * 2. Analyze - Examine existing metadata
 * 3. Generate - Create improved metadata with Claude
 * 4. Report - Generate quality report
 */
async function runFullPipeline(): Promise<void> {
  logger.debug('[PLUGIN] runFullPipeline() called');
  logger.debug(
    '[PLUGIN] selectedNode:',
    currentState.selectedNode?.name,
    currentState.selectedNode?.type
  );

  if (!currentState.selectedNode) {
    logger.debug('[PLUGIN] ERROR: No component selected');
    sendError('No component selected');
    return;
  }

  if (!mcpClient || !mcpClient.isConnected()) {
    logger.debug('[PLUGIN] ERROR: MCP not connected');
    sendError('MCP connection required for full pipeline');
    return;
  }

  try {
    // Prepare data
    logger.debug('[PLUGIN] Preparing audit request...');
    const auditRequest = ComponentAuditor.prepareForMCP(currentState.selectedNode);
    const nodeInfo = nodeAnalyzer.extractNodeInfo(currentState.selectedNode);
    auditRequest.tokens = nodeAnalyzer.extractTokens(nodeInfo);
    currentState.tokens = auditRequest.tokens;

    // Run deep inspection first
    const isComponentSet = currentState.selectedNode.type === 'COMPONENT_SET';
    const variantCount = isComponentSet
      ? (currentState.selectedNode as ComponentSetNode).children.filter(
          (c) => c.type === 'COMPONENT'
        ).length
      : 0;

    const deepInspection = runDeepInspection(currentState.selectedNode);

    // Log Figma data being sent
    logFigmaData(auditRequest);

    // Initialize pipeline steps
    sendPipelineStep(
      'audit',
      'running',
      isComponentSet ? `Inspecting ${variantCount} variants...` : 'Analyzing...'
    );
    sendPipelineStep('metadata', 'waiting');
    sendPipelineStep('generate', 'waiting');
    sendPipelineStep('report', 'waiting');

    // Step 1: Audit
    logger.debug('[PLUGIN] Step 1: Running server audit...');
    const serverAudit = await mcpClient.auditComponent(auditRequest);
    const audit = mergeAuditResults(serverAudit, deepInspection);
    currentState.audit = audit;

    const rawAuditScore = audit.score ?? 0;
    sendPipelineStep(
      'audit',
      'done',
      `${rawAuditScore}/100 (${audit.issues?.length || 0} issues)`
    );

    // Step 2: Analyze metadata
    logger.debug('[PLUGIN] Step 2: Analyzing metadata...');
    sendPipelineStep('metadata', 'running');
    const metadata = await mcpClient.analyzeMetadata(auditRequest);
    currentState.metadata = metadata;

    const metadataScore = (metadata as any).completenessScore ?? 0;
    const metadataContribution = (metadataScore * 0.3).toFixed(1);
    sendPipelineStep('metadata', 'done', `${metadataScore}/100 (×30% = ${metadataContribution})`);

    // Step 3: Generate suggestions
    logger.debug('[PLUGIN] Step 3: Generating metadata...');
    sendPipelineStep('generate', 'running');
    const generated = await mcpClient.generateMetadata(auditRequest);

    // Inject local tokens if server returned none (reusable helper)
    injectTokensIfNeeded(generated, currentState.tokens);

    currentState.generated = generated;
    sendPipelineStep('generate', 'done');

    // Step 4: Generate report
    logger.debug('[PLUGIN] Step 4: Generating report...');
    sendPipelineStep('report', 'running');
    const report = await mcpClient.generateReport({
      ...auditRequest,
      auditResult: audit,
      metadataAnalysis: metadata,
    });
    currentState.report = report;

    const finalScore = (report as any).overallScore ?? 0;
    sendPipelineStep('report', 'done', `Combined: ${finalScore}/100`);

    // Send pipeline complete
    logger.debug('[PLUGIN] Pipeline complete, sending results to UI');
    sendToUI({
      type: 'PIPELINE_COMPLETE',
      results: {
        audit,
        metadata,
        generated,
        report,
        exportReady: (report.overallScore || 0) >= 90,
      } as PipelineResults,
    });
  } catch (error) {
    handlePipelineError(error);
  }
}

/**
 * Log Figma data being sent to server
 */
function logFigmaData(auditRequest: any): void {
  logger.debug('[PLUGIN] ========== FIGMA DATA BEING SENT ==========');
  logger.debug('[PLUGIN] component.name:', auditRequest.component?.name);
  logger.debug('[PLUGIN] component.type:', auditRequest.component?.type);
  logger.debug('[PLUGIN] component.nodeId:', auditRequest.component?.nodeId);
  logger.debug('[PLUGIN] component.hasAutoLayout:', auditRequest.component?.hasAutoLayout);
  logger.debug('[PLUGIN] component.hasStates:', auditRequest.component?.hasStates);
  logger.debug('[PLUGIN] component.width:', auditRequest.component?.width);
  logger.debug('[PLUGIN] component.height:', auditRequest.component?.height);
  logger.debug('[PLUGIN] component.childCount:', auditRequest.component?.childCount);
  logger.debug(
    '[PLUGIN] component.properties:',
    JSON.stringify(auditRequest.component?.properties?.map((p: any) => p.name))
  );
  logger.debug('[PLUGIN] component.variants count:', auditRequest.component?.variants?.length);
  logger.debug('[PLUGIN] component.children count:', auditRequest.component?.children?.length);
  logger.debug(
    '[PLUGIN] existingDescription:',
    auditRequest.existingDescription?.substring(0, 100) || 'NONE'
  );
  logger.debug('[PLUGIN] tokens count:', auditRequest.tokens?.length);
  logger.debug('[PLUGIN] tokens:', JSON.stringify(auditRequest.tokens?.slice(0, 3)));
  logger.debug('[PLUGIN] ==============================================');
}

/**
 * Handle pipeline errors by marking the failed step
 */
function handlePipelineError(error: unknown): void {
  const steps = ['audit', 'metadata', 'generate', 'report'];
  for (const step of steps) {
    if (step === 'audit' && !currentState.audit) {
      sendPipelineStep(step, 'error');
      break;
    }
    if (step === 'metadata' && !currentState.metadata) {
      sendPipelineStep(step, 'error');
      break;
    }
    if (step === 'generate' && !currentState.generated) {
      sendPipelineStep(step, 'error');
      break;
    }
    if (step === 'report' && !currentState.report) {
      sendPipelineStep(step, 'error');
      break;
    }
  }
  sendError(`Pipeline failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
}

// ============================================
// Send Cached Results (for UI reconnection)
// ============================================

/**
 * Send any cached review results to the UI.
 * Called on INIT to restore state after reconnection.
 */
function sendCachedResults(): void {
  // If we have a complete pipeline result cached, send it
  if (
    currentState.audit &&
    currentState.metadata &&
    currentState.generated &&
    currentState.report
  ) {
    logger.debug('[PLUGIN] Sending cached pipeline results to UI');
    sendToUI({
      type: 'PIPELINE_COMPLETE',
      results: {
        audit: currentState.audit,
        metadata: currentState.metadata,
        generated: currentState.generated,
        report: currentState.report,
        exportReady: (currentState.report.overallScore || 0) >= 90,
      },
    });
    return;
  }

  // Otherwise send individual cached results
  if (currentState.audit) {
    logger.debug('[PLUGIN] Sending cached audit to UI');
    sendToUI({ type: 'AUDIT_COMPLETE', audit: currentState.audit });
  }

  if (currentState.metadata) {
    logger.debug('[PLUGIN] Sending cached metadata to UI');
    sendToUI({ type: 'METADATA_ANALYZED', metadata: currentState.metadata });
  }

  if (currentState.generated) {
    logger.debug('[PLUGIN] Sending cached generated metadata to UI');
    sendToUI({ type: 'METADATA_GENERATED', generated: currentState.generated });
  }

  if (currentState.report) {
    logger.debug('[PLUGIN] Sending cached report to UI');
    sendToUI({ type: 'REPORT_READY', report: currentState.report });
  }
}

// ============================================
// Message Handler
// ============================================

/**
 * Handle messages from the UI
 */
function handleUIMessage(msg: UIToPluginMessage): void {
  logger.debug('[PLUGIN] Received message from UI:', msg.type, msg);

  switch (msg.type) {
    case 'INIT':
      logger.debug('[PLUGIN] Handling INIT');
      handleSelectionChange();
      checkAIDToken();
      sendCachedResults();
      break;

    case 'RUN_AUDIT':
      logger.debug('[PLUGIN] Handling RUN_AUDIT');
      runServerAudit();
      break;

    case 'ANALYZE_METADATA':
      logger.debug('[PLUGIN] Handling ANALYZE_METADATA');
      analyzeMetadata();
      break;

    case 'GENERATE_METADATA':
      logger.debug('[PLUGIN] Handling GENERATE_METADATA');
      generateMetadata();
      break;

    case 'APPLY_METADATA_TO_FIGMA':
      logger.debug('[PLUGIN] Handling APPLY_METADATA_TO_FIGMA');
      applyMetadataToFigma();
      break;

    case 'EXPORT_TO_AID':
      logger.debug('[PLUGIN] Handling EXPORT_TO_AID, level:', msg.level);
      exportToAID(msg.level, msg.componentName);
      break;

    case 'EXPORT_CONTENT':
      logger.debug('[PLUGIN] Handling EXPORT_CONTENT, format:', msg.format);
      exportContent(msg.format);
      break;

    case 'RUN_FULL_PIPELINE':
      logger.debug('[PLUGIN] Handling RUN_FULL_PIPELINE');
      runFullPipeline();
      break;

    case 'CONNECT_MCP':
      logger.debug('[PLUGIN] Handling CONNECT_MCP, endpoint:', msg.endpoint);
      connectMCP(msg.endpoint);
      break;

    case 'DISCONNECT_MCP':
      logger.debug('[PLUGIN] Handling DISCONNECT_MCP');
      disconnectMCP();
      break;

    case 'AID_PAIR':
      logger.debug('[PLUGIN] Handling AID_PAIR');
      pairWithAID(msg.code);
      break;

    case 'CHECK_AID_TOKEN':
      logger.debug('[PLUGIN] Handling CHECK_AID_TOKEN');
      checkAIDToken();
      break;

    case 'AID_DISCONNECT':
      logger.debug('[PLUGIN] Handling AID_DISCONNECT');
      disconnectFromAID();
      break;

    // Note: STORE_TOKEN and PAIRING_SUCCESS handlers removed.
    // The UI now sends AID_PAIR message, which calls pairWithAID() in aid-pairing.ts.
    // That function handles the complete auth flow: API call → authService → MCP → heartbeat.

    case 'SELECT_NODE':
      logger.debug('[PLUGIN] Handling SELECT_NODE, nodeId:', msg.nodeId);
      selectNodeById(msg.nodeId);
      break;

    default:
      logger.debug('[PLUGIN] Unknown message type:', (msg as any).type);
  }
}

// ============================================
// Plugin Initialization
// ============================================

// Show UI
figma.showUI(__html__, {
  width: UI_CONFIG.WIDTH,
  height: UI_CONFIG.HEIGHT,
  title: UI_CONFIG.TITLE,
});

// Load custom endpoint if saved
loadCustomEndpoint();

// Listen for selection changes
figma.on('selectionchange', handleSelectionChange);

// Listen for UI messages
figma.ui.onmessage = handleUIMessage;

// Cleanup on close
figma.on('close', () => {
  stopHeartbeat();
  stopHealthCheck();
  if (mcpClient) {
    mcpClient.disconnect();
  }
  nodeAnalyzer.clearCache();
});

// Log plugin start
logger.info('Atomic Design Extractor v2.0 - Quality Pipeline started');
