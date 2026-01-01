/**
 * @file plugin/aid-pairing.ts
 * @description AID server pairing and authentication
 */

import { authService } from '../services';
import { logger } from '../Logger';
import {
  AID_CONFIG,
  STORAGE_KEYS,
  RETRY_CONFIG,
  HEARTBEAT_CONFIG,
  getMCPEndpoint,
} from '../config';
import { mcpClient, settings, updateSettings, setMCPClient } from './state';
import { connectMCP } from './mcp-connection';

// ============================================
// Constants
// ============================================

const AID_TOKEN_KEY = 'aid_jwt_token';

// ============================================
// State
// ============================================

let aidServerEndpoint = AID_CONFIG.DEFAULT_ENDPOINT;
let heartbeatTimer: number | null = null;
let currentToken: string | null = null;

// ============================================
// Endpoint Management
// ============================================

/**
 * Get the current AID server endpoint
 */
export function getAIDEndpoint(): string {
  return aidServerEndpoint;
}

/**
 * Set a custom AID server endpoint
 */
export async function setAIDEndpoint(endpoint: string): Promise<void> {
  aidServerEndpoint = endpoint;
  try {
    await figma.clientStorage.setAsync(STORAGE_KEYS.CUSTOM_ENDPOINT, endpoint);
    logger.info('AID endpoint updated:', endpoint);
  } catch (e) {
    logger.warn('Could not save custom endpoint to storage:', e);
  }
}

/**
 * Load custom endpoint from storage if set
 */
export async function loadCustomEndpoint(): Promise<void> {
  try {
    const customEndpoint = await figma.clientStorage.getAsync(STORAGE_KEYS.CUSTOM_ENDPOINT);
    if (customEndpoint) {
      aidServerEndpoint = customEndpoint;
      logger.info('Loaded custom endpoint from storage:', customEndpoint);
    }
  } catch (e) {
    logger.warn('Could not load custom endpoint from storage:', e);
  }
}

// ============================================
// Utility Functions
// ============================================

/**
 * Sleep for async operations
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Fetch with timeout (Figma plugin compatible - no AbortController)
 */
async function fetchWithTimeout(
  url: string,
  options: RequestInit = {},
  timeoutMs: number = 5000
): Promise<Response> {
  const fetchPromise = fetch(url, options);

  const timeoutPromise = new Promise<Response>((_, reject) => {
    setTimeout(() => {
      reject(new Error(`Request timeout after ${timeoutMs}ms`));
    }, timeoutMs);
  });

  return Promise.race([fetchPromise, timeoutPromise]);
}

// ============================================
// Pairing Functions
// ============================================

/**
 * Pair with AID server using a code
 */
export async function pairWithAID(code: string): Promise<void> {
  try {
    const response = await fetchWithTimeout(
      `${getAIDEndpoint()}${AID_CONFIG.AUTH.PAIR}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
      },
      10000
    );

    const result = await response.json();

    if (result.success) {
      currentToken = result.token;

      // Try to store the JWT token
      try {
        await figma.clientStorage.setAsync(AID_TOKEN_KEY, result.token);
      } catch (storageError) {
        logger.warn('Could not save token to storage, session-only mode:', storageError);
      }

      // Update auth service with JWT
      await authService.authenticateWithJWT(result.token, getAIDEndpoint());

      // Connect to MCP with the token
      updateSettings({ mcpEndpoint: getMCPEndpoint(getAIDEndpoint()) });
      await connectMCP(settings.mcpEndpoint);

      // Start heartbeat to keep session alive
      startHeartbeat(result.token);

      figma.ui.postMessage({ type: 'AID_PAIRED', token: result.token });
      figma.notify('Successfully paired with AID!');
    } else {
      figma.ui.postMessage({ type: 'AID_PAIR_FAILED', error: result.error });
    }
  } catch (error) {
    logger.error('AID pairing failed:', error);
    figma.ui.postMessage({
      type: 'AID_PAIR_FAILED',
      error: error instanceof Error ? error.message : 'Connection failed',
    });
  }
}

// ============================================
// Token Validation
// ============================================

/**
 * Validate token with server using exponential backoff retry
 */
async function validateTokenWithRetry(
  token: string
): Promise<'valid' | 'invalid' | 'network_error'> {
  for (let attempt = 0; attempt < RETRY_CONFIG.MAX_RETRIES; attempt++) {
    try {
      logger.debug(`Token validation attempt ${attempt + 1}/${RETRY_CONFIG.MAX_RETRIES}`);

      const response = await fetchWithTimeout(
        `${getAIDEndpoint()}${AID_CONFIG.AUTH.VALIDATE}`,
        { headers: { Authorization: `Bearer ${token}` } },
        5000
      );

      if (response.ok) {
        logger.debug('[PLUGIN] Token validated successfully');
        return 'valid';
      }

      if (response.status === 401) {
        logger.debug('[PLUGIN] Token is invalid/expired (401)');
        return 'invalid';
      }

      logger.warn(`Server error ${response.status}, will retry`);
      throw new Error(`Server error: ${response.status}`);
    } catch (error) {
      const isLastAttempt = attempt >= RETRY_CONFIG.MAX_RETRIES - 1;

      if (isLastAttempt) {
        logger.error('[PLUGIN] All validation attempts failed:', error);
        return 'network_error';
      }

      const delay = Math.min(
        RETRY_CONFIG.BASE_DELAY_MS * Math.pow(2, attempt),
        RETRY_CONFIG.MAX_DELAY_MS
      );
      logger.debug(`Retrying in ${delay}ms...`);
      await sleep(delay);
    }
  }

  return 'network_error';
}

/**
 * Connect to MCP with retry logic
 */
async function connectMCPWithRetry(token: string): Promise<boolean> {
  for (let attempt = 0; attempt < RETRY_CONFIG.MAX_RETRIES; attempt++) {
    try {
      logger.debug(`MCP connection attempt ${attempt + 1}/${RETRY_CONFIG.MAX_RETRIES}`);

      updateSettings({ mcpEndpoint: getMCPEndpoint(getAIDEndpoint()) });
      await connectMCP(settings.mcpEndpoint);

      logger.debug('[PLUGIN] MCP connected successfully');
      return true;
    } catch (error) {
      const isLastAttempt = attempt >= RETRY_CONFIG.MAX_RETRIES - 1;

      if (isLastAttempt) {
        logger.error('[PLUGIN] All MCP connection attempts failed:', error);
        return false;
      }

      const delay = Math.min(
        RETRY_CONFIG.BASE_DELAY_MS * Math.pow(2, attempt),
        RETRY_CONFIG.MAX_DELAY_MS
      );
      logger.debug(`Retrying MCP connection in ${delay}ms...`);
      await sleep(delay);
    }
  }

  return false;
}

// ============================================
// Heartbeat Management
// ============================================

/**
 * Start heartbeat to keep session alive and detect disconnections
 */
export function startHeartbeat(token: string): void {
  stopHeartbeat();

  logger.debug('[PLUGIN] Starting heartbeat (30s interval)');

  let consecutiveFailures = 0;

  heartbeatTimer = setInterval(async () => {
    try {
      const response = await fetchWithTimeout(
        `${getAIDEndpoint()}${AID_CONFIG.AUTH.PING}`,
        { headers: { Authorization: `Bearer ${token}` } },
        3000
      );

      if (response.ok) {
        const data = await response.json();
        logger.debug(`Heartbeat OK - session remaining: ${data.remainingHuman}`);

        consecutiveFailures = 0;

        // Ensure MCP client stays connected
        if (mcpClient && !mcpClient.isConnected()) {
          logger.debug('[PLUGIN] Heartbeat detected MCP disconnected, reconnecting...');
          await connectMCPWithRetry(token);
          figma.ui.postMessage({ type: 'MCP_CONNECTED' });
        }

        // Warn if token expiring soon (< 1 hour)
        if (data.remainingSec < 3600) {
          figma.ui.postMessage({
            type: 'AID_SESSION_EXPIRING',
            remainingSec: data.remainingSec,
            remainingHuman: data.remainingHuman,
          });
        }
      } else {
        consecutiveFailures++;
        logger.warn(
          `Heartbeat failed (${consecutiveFailures}/${HEARTBEAT_CONFIG.MAX_FAILURES_BEFORE_RECONNECT})`
        );

        if (consecutiveFailures >= HEARTBEAT_CONFIG.MAX_FAILURES_BEFORE_RECONNECT) {
          figma.ui.postMessage({ type: 'AID_CONNECTION_LOST' });
        }
      }
    } catch (error) {
      consecutiveFailures++;
      logger.warn(
        `Heartbeat failed (${consecutiveFailures}/${HEARTBEAT_CONFIG.MAX_FAILURES_BEFORE_RECONNECT}):`,
        error
      );

      if (consecutiveFailures >= HEARTBEAT_CONFIG.MAX_FAILURES_BEFORE_RECONNECT) {
        figma.ui.postMessage({ type: 'AID_CONNECTION_LOST' });

        if (mcpClient) {
          mcpClient.disconnect();
        }
      }
    }
  }, HEARTBEAT_CONFIG.INTERVAL_MS) as unknown as number;
}

/**
 * Stop heartbeat timer
 */
export function stopHeartbeat(): void {
  if (heartbeatTimer !== null) {
    clearInterval(heartbeatTimer);
    heartbeatTimer = null;
    logger.debug('[PLUGIN] Heartbeat stopped');
  }
}

// ============================================
// Token Check
// ============================================

/**
 * Check stored AID token with resilient validation
 */
export async function checkAIDToken(): Promise<void> {
  try {
    // Initialize authService from storage first
    logger.debug('[PLUGIN] Initializing authService from storage...');
    const authInitialized = await authService.initialize();
    logger.debug('[PLUGIN] AuthService initialized:', authInitialized);

    // Try to read token from storage
    let token: string | undefined;
    try {
      token = await figma.clientStorage.getAsync(AID_TOKEN_KEY);
    } catch (storageError) {
      logger.warn('Could not read token from storage:', storageError);
      figma.ui.postMessage({ type: 'AID_TOKEN_INVALID' });
      return;
    }

    if (!token) {
      logger.debug('[PLUGIN] No stored token found');
      figma.ui.postMessage({ type: 'AID_TOKEN_INVALID' });
      return;
    }

    // Trust local token first - show UI immediately
    logger.debug('[PLUGIN] Found stored token, showing UI while validating...');
    currentToken = token;
    figma.ui.postMessage({ type: 'AID_TOKEN_VALIDATING', token });

    // Check if authService already has valid config from storage
    if (authInitialized && authService.isAuthenticated()) {
      logger.debug('[PLUGIN] AuthService already authenticated from storage');
      const mcpConnected = await connectMCPWithRetry(token);
      if (mcpConnected) {
        startHeartbeat(token);
        figma.ui.postMessage({ type: 'AID_TOKEN_VALID', token });
        return;
      }
    }

    // Validate with server in background (with retry)
    const validationResult = await validateTokenWithRetry(token);

    if (validationResult === 'valid') {
      await authService.authenticateWithJWT(token, getAIDEndpoint());
      await connectMCPWithRetry(token);
      startHeartbeat(token);
      figma.ui.postMessage({ type: 'AID_TOKEN_VALID', token });
    } else if (validationResult === 'invalid') {
      logger.debug('[PLUGIN] Token expired, clearing and showing pairing screen');
      try {
        await figma.clientStorage.deleteAsync(AID_TOKEN_KEY);
      } catch (e) {
        /* ignore */
      }
      currentToken = null;
      figma.ui.postMessage({ type: 'AID_TOKEN_INVALID' });
    } else {
      // Network error - trust local token
      logger.debug('[PLUGIN] Network error during validation, trusting local token');

      if (!authService.isAuthenticated()) {
        await authService.authenticateWithJWT(token, getAIDEndpoint());
      }
      const mcpConnected = await connectMCPWithRetry(token);

      if (mcpConnected) {
        startHeartbeat(token);
        figma.ui.postMessage({ type: 'AID_TOKEN_VALID', token });
      } else {
        figma.ui.postMessage({ type: 'AID_CONNECTION_RECONNECTING', token });
      }
    }
  } catch (error) {
    logger.error('Token check failed:', error);
    figma.ui.postMessage({ type: 'AID_CONNECTION_RECONNECTING' });
  }
}

// ============================================
// Disconnect
// ============================================

/**
 * Disconnect from AID server
 */
export async function disconnectFromAID(): Promise<void> {
  stopHeartbeat();
  currentToken = null;

  try {
    await figma.clientStorage.deleteAsync(AID_TOKEN_KEY);
  } catch (e) {
    /* ignore storage errors */
  }

  await authService.logout();

  if (mcpClient) {
    await mcpClient.disconnect();
    setMCPClient(null);
  }

  figma.ui.postMessage({ type: 'AID_TOKEN_INVALID' });
  figma.notify('Disconnected from AID');
}
