/**
 * @file request-queue.test.ts
 * @description Comprehensive tests for the request queue relay system.
 * Tests queuing, processing, completion, timeout, and failure flows.
 *
 * @related
 *   - ./request-queue.ts - Implementation under test
 *   - ../index.ts - Server that uses this queue
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import {
  queueRequest,
  getPendingRequests,
  markProcessing,
  completeRequest,
  failRequest,
  getQueueStats,
  clearQueue,
  type QueuedRequest,
} from './request-queue.js';

// Realistic test data matching production patterns
const testComponents = [
  {
    name: 'PrimaryButton',
    type: 'COMPONENT',
    id: 'node_123:456',
    children: [
      { type: 'TEXT', characters: 'Click me' },
      { type: 'RECTANGLE', fills: [{ type: 'SOLID', color: { r: 0.2, g: 0.4, b: 0.8 } }] },
    ],
    metadata: {
      description: 'Primary call-to-action button with hover states',
      category: 'atoms',
    },
  },
  {
    name: 'NavigationHeader',
    type: 'COMPONENT',
    id: 'node_789:012',
    children: [],
    metadata: {
      description: 'Main navigation header with logo and menu items',
      category: 'organisms',
    },
    variants: [
      { name: 'Default', isDefault: true },
      { name: 'Mobile', description: 'Collapsed mobile view' },
    ],
  },
  {
    name: 'FormField_输入框',
    type: 'COMPONENT',
    id: 'node_李明_345',
    children: [],
    metadata: {
      description: 'Form input field with validation',
      category: 'molecules',
    },
  },
];

describe('Request Queue Relay', () => {
  beforeEach(() => {
    clearQueue(); // Clear state between tests
    vi.useFakeTimers();
  });

  afterEach(() => {
    clearQueue(); // Clean up
    vi.useRealTimers();
  });

  describe('queueRequest', () => {
    it('creates a pending request and returns a promise', async () => {
      const promise = queueRequest('audit', testComponents[0], 'en');

      expect(promise).toBeInstanceOf(Promise);

      const pending = getPendingRequests();
      expect(pending).toHaveLength(1);
      expect(pending[0].type).toBe('audit');
      expect(pending[0].status).toBe('pending');
      expect(pending[0].locale).toBe('en');
    });

    it('generates unique request IDs', async () => {
      const ids = new Set<string>();

      for (let i = 0; i < 10; i++) {
        queueRequest('audit', testComponents[0], 'en');
      }

      const pending = getPendingRequests();
      pending.forEach((req) => ids.add(req.id));

      expect(ids.size).toBe(10);
    });

    it('supports all request types', async () => {
      const types: Array<'audit' | 'analyze' | 'generate' | 'report' | 'pipeline' | 'export'> = [
        'audit',
        'analyze',
        'generate',
        'report',
        'pipeline',
        'export',
      ];

      for (const type of types) {
        queueRequest(type, testComponents[0], 'en');
      }

      const pending = getPendingRequests();
      const queuedTypes = pending.map((r) => r.type);

      expect(queuedTypes).toEqual(expect.arrayContaining(types));
    });

    it('stores component data correctly', async () => {
      const component = testComponents[1];
      queueRequest('pipeline', component, 'he');

      const pending = getPendingRequests();

      expect(pending[0].component).toEqual(component);
      expect(pending[0].locale).toBe('he');
    });

    it('handles unicode component names', async () => {
      const component = testComponents[2];
      queueRequest('audit', component, 'en');

      const pending = getPendingRequests();

      expect(pending[0].component.name).toBe('FormField_输入框');
    });

    it('sets createdAt timestamp', async () => {
      const now = Date.now();
      vi.setSystemTime(now);

      queueRequest('audit', testComponents[0], 'en');

      const pending = getPendingRequests();

      expect(pending[0].createdAt).toBe(now);
    });
  });

  describe('getPendingRequests', () => {
    it('returns empty array when no requests', () => {
      const pending = getPendingRequests();
      expect(pending).toEqual([]);
    });

    it('returns only pending requests, not processing ones', async () => {
      queueRequest('audit', testComponents[0], 'en');
      queueRequest('analyze', testComponents[1], 'en');

      const pending1 = getPendingRequests();
      expect(pending1).toHaveLength(2);

      // Mark one as processing
      markProcessing(pending1[0].id);

      const pending2 = getPendingRequests();
      expect(pending2).toHaveLength(1);
      expect(pending2[0].type).toBe('analyze');
    });

    it('does not return completed requests', async () => {
      queueRequest('audit', testComponents[0], 'en');

      const pending = getPendingRequests();
      const requestId = pending[0].id;

      completeRequest(requestId, { score: 95 });

      expect(getPendingRequests()).toHaveLength(0);
    });
  });

  describe('markProcessing', () => {
    it('marks pending request as processing', async () => {
      queueRequest('audit', testComponents[0], 'en');
      const pending = getPendingRequests();
      const requestId = pending[0].id;

      const success = markProcessing(requestId);

      expect(success).toBe(true);
      expect(getPendingRequests()).toHaveLength(0);
    });

    it('returns false for non-existent request', () => {
      const success = markProcessing('non_existent_request_id');
      expect(success).toBe(false);
    });

    it('returns false for already processing request', async () => {
      queueRequest('audit', testComponents[0], 'en');
      const pending = getPendingRequests();
      const requestId = pending[0].id;

      markProcessing(requestId); // First call
      const secondCall = markProcessing(requestId); // Second call

      expect(secondCall).toBe(false);
    });
  });

  describe('completeRequest', () => {
    it('resolves the waiting promise with result', async () => {
      const promise = queueRequest('audit', testComponents[0], 'en');
      const pending = getPendingRequests();
      const requestId = pending[0].id;

      const expectedResult = {
        score: 92,
        issues: [{ type: 'naming', severity: 'minor', message: 'Consider more descriptive name' }],
      };

      // Complete the request
      const success = completeRequest(requestId, expectedResult);

      expect(success).toBe(true);

      // Promise should resolve with the result
      const result = await promise;
      expect(result).toEqual(expectedResult);
    });

    it('returns false for non-existent request', () => {
      const success = completeRequest('non_existent_request_id', { result: 'test' });
      expect(success).toBe(false);
    });

    it('cleans up request after completion', async () => {
      const promise = queueRequest('audit', testComponents[0], 'en');
      const pending = getPendingRequests();
      const requestId = pending[0].id;

      completeRequest(requestId, { success: true });
      await promise;

      // Advance time to allow cleanup
      vi.advanceTimersByTime(6000);

      // Request should be gone
      const success = completeRequest(requestId, { another: 'result' });
      expect(success).toBe(false);
    });

    it('handles complex result objects', async () => {
      const promise = queueRequest('pipeline', testComponents[0], 'en');
      const pending = getPendingRequests();
      const requestId = pending[0].id;

      const complexResult = {
        audit: { score: 88, categories: { naming: 22, structure: 18, visual: 15, a11y: 20, metadata: 13 } },
        metadata: { present: ['name', 'category'], missing: ['tokens', 'variants'] },
        generated: { description: 'A button component for primary actions', category: 'atoms' },
        report: { totalScore: 88, passesThreshold: false, recommendations: ['Add metadata'] },
      };

      completeRequest(requestId, complexResult);

      const result = await promise;
      expect(result).toEqual(complexResult);
    });
  });

  describe('failRequest', () => {
    it('rejects the waiting promise with error', async () => {
      const promise = queueRequest('audit', testComponents[0], 'en');
      const pending = getPendingRequests();
      const requestId = pending[0].id;

      failRequest(requestId, 'Claude Code timeout - skill not loaded');

      await expect(promise).rejects.toThrow('Claude Code timeout - skill not loaded');
    });

    it('returns false for non-existent request', () => {
      const success = failRequest('non_existent_request_id', 'Some error');
      expect(success).toBe(false);
    });

    it('cleans up request after failure', async () => {
      const promise = queueRequest('audit', testComponents[0], 'en');
      const pending = getPendingRequests();
      const requestId = pending[0].id;

      failRequest(requestId, 'Error');

      // Catch the rejection
      await promise.catch(() => {});

      // Advance time to allow cleanup
      vi.advanceTimersByTime(6000);

      // Request should be gone
      const success = failRequest(requestId, 'Another error');
      expect(success).toBe(false);
    });
  });

  describe('timeout handling', () => {
    it('rejects promise after 60 seconds if not processed', async () => {
      const promise = queueRequest('audit', testComponents[0], 'en');

      // Advance time by 60 seconds
      vi.advanceTimersByTime(60000);

      await expect(promise).rejects.toThrow('Request timed out - Claude Code did not respond');
    });

    it('cleans up timed out request from queue', async () => {
      const promise = queueRequest('audit', testComponents[0], 'en');

      const pendingBefore = getPendingRequests();
      expect(pendingBefore).toHaveLength(1);
      const requestId = pendingBefore[0].id;

      // Advance time past timeout
      vi.advanceTimersByTime(60001);

      // Catch the rejection to prevent unhandled error
      await promise.catch(() => {});

      // Request should be removed
      const pendingAfter = getPendingRequests();
      expect(pendingAfter).toHaveLength(0);

      // Cannot complete timed out request
      const success = completeRequest(requestId, { result: 'too late' });
      expect(success).toBe(false);
    });

    it('does not timeout if completed within 60 seconds', async () => {
      const promise = queueRequest('audit', testComponents[0], 'en');
      const pending = getPendingRequests();
      const requestId = pending[0].id;

      // Complete after 59 seconds
      vi.advanceTimersByTime(59000);
      completeRequest(requestId, { score: 100 });

      // Should resolve, not reject
      const result = await promise;
      expect(result).toEqual({ score: 100 });
    });
  });

  describe('getQueueStats', () => {
    it('returns zero counts for empty queue', () => {
      const stats = getQueueStats();

      expect(stats).toEqual({
        pending: 0,
        processing: 0,
        completed: 0,
        failed: 0,
      });
    });

    it('counts pending requests correctly', async () => {
      queueRequest('audit', testComponents[0], 'en');
      queueRequest('analyze', testComponents[1], 'en');
      queueRequest('generate', testComponents[2], 'he');

      const stats = getQueueStats();

      expect(stats.pending).toBe(3);
      expect(stats.processing).toBe(0);
    });

    it('counts processing requests correctly', async () => {
      queueRequest('audit', testComponents[0], 'en');
      queueRequest('analyze', testComponents[1], 'en');

      const pending = getPendingRequests();
      markProcessing(pending[0].id);

      const stats = getQueueStats();

      expect(stats.pending).toBe(1);
      expect(stats.processing).toBe(1);
    });

    it('counts completed requests correctly', async () => {
      queueRequest('audit', testComponents[0], 'en');

      const pending = getPendingRequests();
      completeRequest(pending[0].id, { success: true });

      const stats = getQueueStats();

      expect(stats.completed).toBe(1);
    });

    it('counts failed requests correctly', async () => {
      const promise = queueRequest('audit', testComponents[0], 'en');

      const pending = getPendingRequests();
      failRequest(pending[0].id, 'Error');

      // Catch rejection
      await promise.catch(() => {});

      const stats = getQueueStats();

      expect(stats.failed).toBe(1);
    });
  });

  describe('concurrent requests', () => {
    it('handles multiple concurrent requests', async () => {
      const promises = testComponents.map((component, index) =>
        queueRequest(index % 2 === 0 ? 'audit' : 'analyze', component, 'en')
      );

      const pending = getPendingRequests();
      expect(pending).toHaveLength(3);

      // Complete all in reverse order
      for (let i = pending.length - 1; i >= 0; i--) {
        completeRequest(pending[i].id, { index: i });
      }

      const results = await Promise.all(promises);

      expect(results).toHaveLength(3);
      expect(results[0]).toEqual({ index: 0 });
      expect(results[1]).toEqual({ index: 1 });
      expect(results[2]).toEqual({ index: 2 });
    });

    it('isolates failures from other requests', async () => {
      const promise1 = queueRequest('audit', testComponents[0], 'en');
      const promise2 = queueRequest('analyze', testComponents[1], 'en');

      const pending = getPendingRequests();

      // Fail first, complete second
      failRequest(pending[0].id, 'First failed');
      completeRequest(pending[1].id, { success: true });

      await expect(promise1).rejects.toThrow('First failed');
      await expect(promise2).resolves.toEqual({ success: true });
    });
  });

  describe('request ID format', () => {
    it('generates IDs starting with req_', async () => {
      queueRequest('audit', testComponents[0], 'en');

      const pending = getPendingRequests();

      expect(pending[0].id).toMatch(/^req_/);
    });

    it('includes timestamp in ID', async () => {
      const now = 1703203200000; // Fixed timestamp
      vi.setSystemTime(now);

      queueRequest('audit', testComponents[0], 'en');

      const pending = getPendingRequests();

      expect(pending[0].id).toContain(now.toString());
    });
  });
});
