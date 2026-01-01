/**
 * @file services/MCPClient/pipeline.ts
 * @description Quality pipeline operations for MCP Client
 */

import type { MCPResponse } from '../../types';
import type {
  ComponentAuditRequest,
  AuditResult,
  MetadataGapAnalysis,
  GeneratedMetadata,
  ComponentQualityReport,
  ExportPayload,
} from '../../types';
import type { MCPClientConfig, PendingRequest } from './types';
import { sendRequest } from './request';

type SendRequestFn = (method: string, params: unknown) => Promise<MCPResponse>;

/**
 * Create a bound sendRequest function for pipeline operations
 */
export function createSendRequest(
  config: MCPClientConfig,
  requestIdRef: { value: number },
  pendingRequests: Map<number, PendingRequest>
): SendRequestFn {
  return (method: string, params: unknown) =>
    sendRequest(method, params, config, requestIdRef, pendingRequests);
}

/**
 * Audit a component for quality issues
 */
export async function auditComponent(
  componentData: ComponentAuditRequest,
  send: SendRequestFn
): Promise<AuditResult> {
  const response = await send('tools/call', {
    name: 'audit_component',
    arguments: {
      component: componentData.component,
      tokens: componentData.tokens || [],
      variants: componentData.variants || [],
      checks: componentData.checks || ['naming', 'structure', 'visual', 'accessibility', 'variants'],
      skill: 'component-metadata',
    },
  });

  if (response.error) {
    throw new Error(response.error.message);
  }

  return response.result as AuditResult;
}

/**
 * Analyze metadata gaps
 */
export async function analyzeMetadata(
  componentData: ComponentAuditRequest,
  send: SendRequestFn
): Promise<MetadataGapAnalysis> {
  console.log('[MCP] analyzeMetadata called');
  console.log('[MCP] Component name:', componentData.component?.name);
  console.log('[MCP] existingDescription length:', componentData.existingDescription?.length || 0);
  console.log('[MCP] variants count:', componentData.variants?.length || 0);

  const response = await send('tools/call', {
    name: 'analyze_metadata',
    arguments: {
      component: componentData.component,
      existingDescription: componentData.existingDescription,
      variants: componentData.variants || componentData.component?.variants || [],
      skill: 'component-metadata',
    },
  });

  if (response.error) {
    console.error('[MCP] analyzeMetadata error:', response.error);
    throw new Error(response.error.message);
  }

  console.log('[MCP] analyzeMetadata response:', JSON.stringify(response.result).substring(0, 200));
  return response.result as MetadataGapAnalysis;
}

/**
 * Generate metadata suggestions
 */
export async function generateMetadata(
  componentData: ComponentAuditRequest,
  send: SendRequestFn
): Promise<GeneratedMetadata> {
  const response = await send('tools/call', {
    name: 'generate_metadata',
    arguments: {
      component: componentData.component,
      tokens: componentData.tokens,
      variants: componentData.variants,
      skill: 'component-metadata',
    },
  });

  if (response.error) {
    throw new Error(response.error.message);
  }

  return response.result as GeneratedMetadata;
}

/**
 * Generate full quality report
 */
export async function generateReport(
  componentData: ComponentAuditRequest,
  send: SendRequestFn
): Promise<ComponentQualityReport> {
  const response = await send('tools/call', {
    name: 'generate_report',
    arguments: {
      component: componentData.component,
      auditResult: componentData.auditResult,
      metadataAnalysis: componentData.metadataAnalysis,
      generatedMetadata: componentData.generatedMetadata,
      existingDescription: componentData.existingDescription,
      tokens: componentData.tokens,
      variants: componentData.variants,
    },
  });

  if (response.error) {
    throw new Error(response.error.message);
  }

  return response.result as ComponentQualityReport;
}

/**
 * Run full quality pipeline
 */
export async function runQualityPipeline(
  componentData: ComponentAuditRequest,
  send: SendRequestFn
): Promise<{
  audit: AuditResult;
  metadata: MetadataGapAnalysis;
  generated: GeneratedMetadata;
  report: ComponentQualityReport;
  exportReady: boolean;
}> {
  const audit = await auditComponent(componentData, send);
  const metadata = await analyzeMetadata(componentData, send);
  const generated = await generateMetadata(componentData, send);
  const report = await generateReport(
    { ...componentData, auditResult: audit, metadataAnalysis: metadata },
    send
  );

  return {
    audit,
    metadata,
    generated,
    report,
    exportReady: report.overallScore >= 90,
  };
}

/**
 * Export component to AID pipeline
 */
export async function exportToAID(
  payload: ExportPayload,
  send: SendRequestFn
): Promise<{
  success: boolean;
  componentId: string;
  message: string;
  error?: string;
  files?: string[];
  componentDir?: string;
  // Cloud export - ZIP as base64
  zipBase64?: string;
  downloadFilename?: string;
  downloadSize?: number;
  isCloudExport?: boolean;
  componentName?: string;
  relativePath?: string;
}> {
  // Verify score threshold
  if (payload.qualityCertification.score < 90) {
    return {
      success: false,
      componentId: payload.component.name,
      message: 'Export blocked',
      error: `Score ${payload.qualityCertification.score} is below required 90. Fix issues before export.`,
    };
  }

  const response = await send('tools/call', {
    name: 'export_to_aid',
    arguments: {
      component: payload.component,
      metadata: payload.metadata,
      tokens: payload.tokens,
      content: payload.content,
      certification: payload.qualityCertification,
      figma: payload.figma,
    },
  });

  if (response.error) {
    return {
      success: false,
      componentId: payload.component.name,
      message: 'Export failed',
      error: response.error.message,
    };
  }

  // Extract files list from server response
  const result = response.result || {};

  return {
    success: true,
    componentId: payload.component.name,
    message: 'Component exported to AID pipeline successfully',
    files: result.files || [],
    componentDir: result.react?.componentDir || '',
    // Cloud export fields - ZIP as base64
    zipBase64: result.zipBase64,
    downloadFilename: result.downloadFilename,
    downloadSize: result.downloadSize,
    isCloudExport: result.isCloudExport || false,
    componentName: result.componentName,
    relativePath: result.relativePath,
  };
}
