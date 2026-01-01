/**
 * @file config.ts
 * @description Configuration constants and environment settings for the Figma plugin.
 *              Centralizes all configurable values for easy modification.
 * @created 2024-12
 * @related
 *   - ./code.ts - Main plugin entry point, uses these config values
 *   - ./AuthService.ts - Uses auth-related config
 *   - ./MCPClient.ts - Uses MCP endpoint config
 */

// ============================================
// Environment Detection
// ============================================

/**
 * Detect if running in development mode.
 * In Figma plugins, we check the endpoint pattern.
 */
export const isDevelopment = (): boolean => {
  // In Figma plugin context, we can't access process.env
  // Development is determined by endpoint containing localhost
  return true; // Default to dev; will be overridden by actual endpoint check
};

// ============================================
// Server Configuration
// ============================================

/**
 * AID Server configuration.
 * These values can be overridden via plugin settings.
 */
export const AID_CONFIG = {
  /**
   * Default server endpoint - Cloud Run production server.
   * Change to LOCAL_ENDPOINT for local development.
   * @default PRODUCTION_ENDPOINT
   */
  DEFAULT_ENDPOINT: 'https://figma-plugin-server-983606191500.us-central1.run.app',

  /**
   * Local development endpoint.
   */
  LOCAL_ENDPOINT: 'http://localhost:3001',

  /**
   * Production server endpoint (GCP Cloud Run).
   */
  PRODUCTION_ENDPOINT: 'https://figma-plugin-server-983606191500.us-central1.run.app',

  /**
   * MCP endpoint path (appended to server URL).
   */
  MCP_PATH: '/mcp',

  /**
   * Auth endpoints
   */
  AUTH: {
    PAIR: '/auth/pair',
    VALIDATE: '/auth/jwt/validate',
    PING: '/auth/ping',
  },
} as const;

// ============================================
// Storage Keys
// ============================================

/**
 * Keys used for Figma client storage.
 * Centralized to avoid duplication and typos.
 */
export const STORAGE_KEYS = {
  /** JWT token for AID authentication */
  AID_JWT_TOKEN: 'aid_jwt_token',

  /** User's preferred server endpoint */
  CUSTOM_ENDPOINT: 'aid_custom_endpoint',

  /** Plugin settings */
  SETTINGS: 'atomic_extractor_settings',

  /** Auth configuration (from AuthService) */
  AUTH_CONFIG: 'atomic_extractor_auth',
} as const;

// ============================================
// Retry Configuration
// ============================================

/**
 * Configuration for resilient network operations.
 */
export const RETRY_CONFIG = {
  /** Maximum number of retry attempts */
  MAX_RETRIES: 3,

  /** Base delay between retries in milliseconds */
  BASE_DELAY_MS: 2000,

  /** Maximum delay between retries in milliseconds */
  MAX_DELAY_MS: 10000,

  /** Request timeout in milliseconds */
  REQUEST_TIMEOUT_MS: 5000,

  /** Pairing request timeout (longer for user interaction) */
  PAIRING_TIMEOUT_MS: 10000,
} as const;

// ============================================
// Heartbeat Configuration
// ============================================

/**
 * Configuration for connection health monitoring.
 */
export const HEARTBEAT_CONFIG = {
  /** Interval between heartbeat pings in milliseconds */
  INTERVAL_MS: 30000,

  /** Ping request timeout in milliseconds */
  TIMEOUT_MS: 3000,

  /** Number of consecutive failures before showing reconnection warning */
  MAX_FAILURES_BEFORE_RECONNECT: 2,

  /** Session expiry warning threshold in seconds (warn if < 1 hour remaining) */
  EXPIRY_WARNING_THRESHOLD_SEC: 3600,
} as const;

// ============================================
// Quality Pipeline Configuration
// ============================================

/**
 * Configuration for the quality audit pipeline.
 */
export const QUALITY_CONFIG = {
  /** Minimum score required for export (0-100) */
  EXPORT_THRESHOLD: 90,

  /**
   * Scoring weights for different audit categories.
   * Must sum to 1.0.
   */
  WEIGHTS: {
    consistency: 0.25,    // 25% - Naming and visual consistency
    metadata: 0.30,       // 30% - Documentation completeness
    accessibility: 0.25,  // 25% - A11y compliance
    structure: 0.20,      // 20% - Component structure
  },

  /**
   * Minimum scores per category before flagging issues.
   */
  MINIMUMS: {
    consistency: 70,
    metadata: 60,
    accessibility: 80,  // Higher because a11y is critical
    structure: 70,
  },
} as const;

// ============================================
// UI Configuration
// ============================================

/**
 * Plugin UI dimensions and settings.
 */
export const UI_CONFIG = {
  /** Default plugin window width */
  WIDTH: 400,

  /** Default plugin window height */
  HEIGHT: 680,

  /** Plugin window title */
  TITLE: 'Atomic Design Extractor',
} as const;

// ============================================
// Logging Configuration
// ============================================

import type { LogLevel } from './Logger';

/**
 * Logging configuration.
 */
export const LOG_CONFIG = {
  /** Default log level for development */
  DEV_LEVEL: 'debug' as LogLevel,

  /** Default log level for production */
  PROD_LEVEL: 'warn' as LogLevel,

  /** Enable timestamp in log messages */
  ENABLE_TIMESTAMP: false,
} as const;

// ============================================
// Helper Functions
// ============================================

/**
 * Get the full MCP endpoint URL.
 * @param baseUrl - Base server URL (defaults to development endpoint)
 * @returns Full MCP endpoint URL
 */
export function getMCPEndpoint(baseUrl: string = AID_CONFIG.DEFAULT_ENDPOINT): string {
  return `${baseUrl}${AID_CONFIG.MCP_PATH}`;
}

/**
 * Check if an endpoint is localhost (development mode).
 * @param endpoint - The endpoint URL to check
 * @returns True if the endpoint is localhost
 */
export function isLocalhostEndpoint(endpoint: string): boolean {
  return endpoint.includes('localhost') || endpoint.includes('127.0.0.1');
}
