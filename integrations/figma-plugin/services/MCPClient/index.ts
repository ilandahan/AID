/**
 * @file services/MCPClient/index.ts
 * @description MCP (Model Context Protocol) client for communication with the AID backend.
 *              Handles JSON-RPC requests, retry logic, and the 4-phase quality pipeline API.
 * @created 2024-12
 * @refactored 2024-12 - Extracted modules for better maintainability
 */

import type { MCPResponse } from '../../types';
import type {
  ComponentPayload,
  DesignToken,
  EnrichedComponentData,
  ComponentAuditRequest,
  AuditResult,
  MetadataGapAnalysis,
  GeneratedMetadata,
  ComponentQualityReport,
  ExportPayload,
} from '../../types';

import type { MCPClientConfig, ConnectionState, PendingRequest, ConnectionListener } from './types';
import { sendRequest } from './request';
import * as connection from './connection';
import * as pipeline from './pipeline';
import * as tools from './tools';
import * as legacy from './legacy';

// Re-export types
export type { MCPClientConfig, ConnectionState } from './types';

export class MCPClient {
  private config: MCPClientConfig;
  private state: ConnectionState = { isConnected: false };
  private requestIdRef = { value: 0 };
  private pendingRequests: Map<number, PendingRequest> = new Map();
  private connectionListeners: ConnectionListener[] = [];

  constructor(config: MCPClientConfig) {
    this.config = {
      timeout: 30000,
      retryAttempts: 3,
      retryDelay: 1000,
      ...config,
    };
  }

  // ============================================
  // Connection Management
  // ============================================

  async connect(): Promise<boolean> {
    return connection.connect(
      this.config, this.state, this.requestIdRef,
      this.pendingRequests, () => this.notifyConnectionChange()
    );
  }

  async disconnect(): Promise<void> {
    connection.disconnect(this.state, this.pendingRequests, () => this.notifyConnectionChange());
  }

  isConnected(): boolean {
    return this.state.isConnected;
  }

  getConnectionState(): ConnectionState {
    return { ...this.state };
  }

  async ping(): Promise<boolean> {
    return connection.ping(this.config, this.state, this.requestIdRef, this.pendingRequests);
  }

  onConnectionChange(callback: ConnectionListener): () => void {
    return connection.onConnectionChange(callback, this.connectionListeners);
  }

  private notifyConnectionChange(): void {
    connection.notifyConnectionChange(this.state, this.connectionListeners);
  }

  // ============================================
  // Request Helper
  // ============================================

  private async send(method: string, params: unknown): Promise<MCPResponse> {
    return sendRequest(method, params, this.config, this.requestIdRef, this.pendingRequests);
  }

  // ============================================
  // Tool Operations
  // ============================================

  async callTool(name: string, args: Record<string, unknown>): Promise<unknown> {
    return tools.callTool(name, args, (m, p) => this.send(m, p));
  }

  async listTools(): Promise<Array<{ name: string; description: string; inputSchema: unknown }>> {
    return tools.listTools((m, p) => this.send(m, p));
  }

  async getResource(uri: string): Promise<unknown> {
    return tools.getResource(uri, (m, p) => this.send(m, p));
  }

  async listResources(): Promise<Array<{ uri: string; name: string; description?: string; mimeType?: string }>> {
    return tools.listResources((m, p) => this.send(m, p));
  }

  // ============================================
  // Quality Pipeline (Phase 1-4)
  // ============================================

  async auditComponent(componentData: ComponentAuditRequest): Promise<AuditResult> {
    return pipeline.auditComponent(componentData, (m, p) => this.send(m, p));
  }

  async analyzeMetadata(componentData: ComponentAuditRequest): Promise<MetadataGapAnalysis> {
    return pipeline.analyzeMetadata(componentData, (m, p) => this.send(m, p));
  }

  async generateMetadata(componentData: ComponentAuditRequest): Promise<GeneratedMetadata> {
    return pipeline.generateMetadata(componentData, (m, p) => this.send(m, p));
  }

  async generateReport(componentData: ComponentAuditRequest): Promise<ComponentQualityReport> {
    return pipeline.generateReport(componentData, (m, p) => this.send(m, p));
  }

  async runQualityPipeline(componentData: ComponentAuditRequest): Promise<{
    audit: AuditResult;
    metadata: MetadataGapAnalysis;
    generated: GeneratedMetadata;
    report: ComponentQualityReport;
    exportReady: boolean;
  }> {
    return pipeline.runQualityPipeline(componentData, (m, p) => this.send(m, p));
  }

  async exportToAID(payload: ExportPayload): Promise<{
    success: boolean;
    componentId: string;
    message: string;
    error?: string;
  }> {
    return pipeline.exportToAID(payload, (m, p) => this.send(m, p));
  }

  // ============================================
  // Legacy Operations (deprecated)
  // ============================================

  /** @deprecated Use exportToAID instead */
  async sendComponent(payload: ComponentPayload): Promise<{
    success: boolean;
    componentId: string;
    generatedFiles?: string[];
    error?: string;
  }> {
    return legacy.sendComponent(payload, (m, p) => this.send(m, p));
  }

  async sendTokens(tokens: DesignToken[], format: 'css' | 'json' | 'tailwind'): Promise<{
    success: boolean;
    outputPath?: string;
    error?: string;
  }> {
    return legacy.sendTokens(tokens, format, (m, p) => this.send(m, p));
  }

  async sendBatch(
    payloads: ComponentPayload[],
    onProgress?: (completed: number, total: number) => void
  ): Promise<{
    successful: string[];
    failed: Array<{ componentId: string; error: string }>;
  }> {
    return legacy.sendBatch(payloads, (m, p) => this.send(m, p), onProgress);
  }

  async validateComponent(component: EnrichedComponentData): Promise<{
    valid: boolean;
    errors: string[];
    warnings: string[];
  }> {
    return legacy.validateComponent(component, (m, p) => this.send(m, p));
  }

  // ============================================
  // Configuration
  // ============================================

  setEndpoint(endpoint: string): void {
    this.config.endpoint = endpoint;
  }

  getEndpoint(): string {
    return this.config.endpoint;
  }
}

/**
 * Factory function for creating client instances
 */
export function createMCPClient(endpoint: string): MCPClient {
  return new MCPClient({
    endpoint,
    requireAuth: true,
  });
}

export default MCPClient;
