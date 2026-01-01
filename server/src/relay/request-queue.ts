/**
 * @file request-queue.ts
 * @description Request queue for relaying Figma plugin requests to Claude Code.
 *
 * Flow:
 * 1. Figma plugin sends request → Server queues it
 * 2. Claude Code polls for pending requests
 * 3. Claude Code processes with skills → returns result
 * 4. Server returns result to waiting Figma plugin
 */

export interface QueuedRequest {
  id: string;
  type: 'audit' | 'analyze' | 'generate' | 'report' | 'pipeline' | 'export';
  component: Record<string, unknown>;
  locale: 'en' | 'he';
  createdAt: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  result?: unknown;
  error?: string;
}

// In-memory queue (use Redis in production)
let requestQueue = new Map<string, QueuedRequest>();
let requestResolvers = new Map<string, {
  resolve: (value: unknown) => void;
  reject: (error: Error) => void;
  timeout: NodeJS.Timeout;
}>();

const REQUEST_TIMEOUT_MS = 60000; // 60 seconds

/**
 * Clear all queued requests (for testing only)
 */
export function clearQueue(): void {
  // Clear all timeouts
  for (const resolver of requestResolvers.values()) {
    clearTimeout(resolver.timeout);
  }
  requestQueue = new Map();
  requestResolvers = new Map();
}

/**
 * Generate a unique request ID
 */
function generateRequestId(): string {
  return `req_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
}

/**
 * Queue a request from the Figma plugin
 * Returns a promise that resolves when Claude Code processes it
 */
export function queueRequest(
  type: QueuedRequest['type'],
  component: Record<string, unknown>,
  locale: 'en' | 'he' = 'en'
): Promise<unknown> {
  const id = generateRequestId();

  const request: QueuedRequest = {
    id,
    type,
    component,
    locale,
    createdAt: Date.now(),
    status: 'pending'
  };

  requestQueue.set(id, request);

  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      requestQueue.delete(id);
      requestResolvers.delete(id);
      reject(new Error('Request timed out - Claude Code did not respond'));
    }, REQUEST_TIMEOUT_MS);

    requestResolvers.set(id, { resolve, reject, timeout });
  });
}

/**
 * Get pending requests (called by Claude Code)
 */
export function getPendingRequests(): QueuedRequest[] {
  const pending: QueuedRequest[] = [];

  for (const request of requestQueue.values()) {
    if (request.status === 'pending') {
      pending.push(request);
    }
  }

  return pending;
}

/**
 * Mark a request as being processed
 */
export function markProcessing(requestId: string): boolean {
  const request = requestQueue.get(requestId);
  if (!request || request.status !== 'pending') {
    return false;
  }

  request.status = 'processing';
  return true;
}

/**
 * Complete a request with a result (called by Claude Code)
 */
export function completeRequest(requestId: string, result: unknown): boolean {
  const request = requestQueue.get(requestId);
  const resolver = requestResolvers.get(requestId);

  if (!request || !resolver) {
    return false;
  }

  request.status = 'completed';
  request.result = result;

  clearTimeout(resolver.timeout);
  resolver.resolve(result);

  // Cleanup
  requestResolvers.delete(requestId);
  setTimeout(() => requestQueue.delete(requestId), 5000);

  return true;
}

/**
 * Fail a request with an error (called by Claude Code)
 */
export function failRequest(requestId: string, error: string): boolean {
  const request = requestQueue.get(requestId);
  const resolver = requestResolvers.get(requestId);

  if (!request || !resolver) {
    return false;
  }

  request.status = 'failed';
  request.error = error;

  clearTimeout(resolver.timeout);
  resolver.reject(new Error(error));

  // Cleanup
  requestResolvers.delete(requestId);
  setTimeout(() => requestQueue.delete(requestId), 5000);

  return true;
}

/**
 * Get queue statistics
 */
export function getQueueStats(): {
  pending: number;
  processing: number;
  completed: number;
  failed: number;
} {
  let pending = 0, processing = 0, completed = 0, failed = 0;

  for (const request of requestQueue.values()) {
    switch (request.status) {
      case 'pending': pending++; break;
      case 'processing': processing++; break;
      case 'completed': completed++; break;
      case 'failed': failed++; break;
    }
  }

  return { pending, processing, completed, failed };
}
