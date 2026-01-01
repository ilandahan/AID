/**
 * @file services/MCPClient/types.ts
 * @description Type definitions for MCP Client
 */

import type { MCPResponse } from '../../types';

export interface MCPClientConfig {
  endpoint: string;
  timeout?: number;
  retryAttempts?: number;
  retryDelay?: number;
  requireAuth?: boolean;
}

export interface ConnectionState {
  isConnected: boolean;
  lastPing?: Date;
  serverInfo?: {
    name: string;
    version: string;
    capabilities: string[];
  };
}

export interface PendingRequest {
  resolve: (value: MCPResponse) => void;
  reject: (error: Error) => void;
  timeout: ReturnType<typeof setTimeout>;
}

export type ConnectionListener = (state: ConnectionState) => void;
