/**
 * @file QueueManager.test.ts
 * @description Unit tests for QueueManager module - queue operations, processing, and listeners
 */

import { QueueManager } from '../QueueManager';

// Inline type definitions to avoid import issues
type AtomicLevel = 'atom' | 'molecule' | 'organism' | 'template' | 'page';

interface FigmaNodeInfo {
  id: string;
  name: string;
  type: string;
}

interface ComponentWorkPlan {
  classification: {
    level: AtomicLevel;
    category: string;
    confidence: number;
  };
  dependencies: Array<{
    nodeId: string;
    name: string;
    level: AtomicLevel;
  }>;
  estimatedComplexity: string;
  suggestedTasks: unknown[];
}

// Helper to create a mock FigmaNodeInfo
function mockNodeInfo(overrides: Partial<FigmaNodeInfo> = {}): FigmaNodeInfo {
  return {
    id: `node-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`,
    name: 'Test / Component',
    type: 'COMPONENT_SET',
    ...overrides,
  };
}

// Helper to create a mock ComponentWorkPlan
function mockWorkPlan(level: AtomicLevel = 'atom', dependencies: string[] = []): ComponentWorkPlan {
  return {
    classification: {
      level,
      category: 'button',
      confidence: 0.95,
    },
    dependencies: dependencies.map(nodeId => ({
      nodeId,
      name: `Dependency ${nodeId}`,
      level: 'atom' as AtomicLevel,
    })),
    estimatedComplexity: 'medium',
    suggestedTasks: [],
  };
}

describe('QueueManager', () => {
  let manager: QueueManager;

  beforeEach(() => {
    // Create a fresh instance for each test
    manager = new QueueManager();
  });

  describe('addToQueue', () => {
    it('should add an item to the queue', () => {
      const nodeInfo = mockNodeInfo();
      const workPlan = mockWorkPlan('atom');

      const item = manager.addToQueue(nodeInfo as any, workPlan as any);

      expect(item).toBeDefined();
      expect(item.nodeId).toBe(nodeInfo.id);
      expect(item.nodeName).toBe(nodeInfo.name);
      expect(item.status).toBe('pending');
    });

    it('should assign priority based on atomic level', () => {
      const atomNode = mockNodeInfo({ id: 'atom-node' });
      const moleculeNode = mockNodeInfo({ id: 'molecule-node' });
      const organismNode = mockNodeInfo({ id: 'organism-node' });

      const atomItem = manager.addToQueue(atomNode as any, mockWorkPlan('atom') as any);
      const moleculeItem = manager.addToQueue(moleculeNode as any, mockWorkPlan('molecule') as any);
      const organismItem = manager.addToQueue(organismNode as any, mockWorkPlan('organism') as any);

      // Atoms should have lower priority number (higher priority)
      expect(atomItem.priority).toBeLessThan(moleculeItem.priority);
      expect(moleculeItem.priority).toBeLessThan(organismItem.priority);
    });

    it('should insert items in priority order', () => {
      // Add in reverse priority order
      const pageNode = mockNodeInfo({ id: 'page', name: 'Page' });
      const atomNode = mockNodeInfo({ id: 'atom', name: 'Atom' });
      const moleculeNode = mockNodeInfo({ id: 'molecule', name: 'Molecule' });

      manager.addToQueue(pageNode as any, mockWorkPlan('page') as any);
      manager.addToQueue(atomNode as any, mockWorkPlan('atom') as any);
      manager.addToQueue(moleculeNode as any, mockWorkPlan('molecule') as any);

      const queue = manager.getQueue();

      // Should be ordered by priority: atom, molecule, page
      expect(queue.items[0].nodeName).toBe('Atom');
      expect(queue.items[1].nodeName).toBe('Molecule');
      expect(queue.items[2].nodeName).toBe('Page');
    });
  });

  describe('removeFromQueue', () => {
    it('should remove an item by ID', () => {
      const nodeInfo = mockNodeInfo();
      const item = manager.addToQueue(nodeInfo as any, mockWorkPlan() as any);

      const removed = manager.removeFromQueue(item.id);

      expect(removed).toBe(true);
      expect(manager.getItem(item.id)).toBeUndefined();
    });

    it('should return false for non-existent item', () => {
      const removed = manager.removeFromQueue('non-existent-id');
      expect(removed).toBe(false);
    });
  });

  describe('reorderItem', () => {
    it('should reorder an item to new position', () => {
      const node1 = mockNodeInfo({ id: '1', name: 'Item 1' });
      const node2 = mockNodeInfo({ id: '2', name: 'Item 2' });
      const node3 = mockNodeInfo({ id: '3', name: 'Item 3' });

      const item1 = manager.addToQueue(node1 as any, mockWorkPlan('atom') as any);
      manager.addToQueue(node2 as any, mockWorkPlan('atom') as any);
      manager.addToQueue(node3 as any, mockWorkPlan('atom') as any);

      // Move first item to the end
      const reordered = manager.reorderItem(item1.id, 2);

      expect(reordered).toBe(true);
      const queue = manager.getQueue();
      expect(queue.items[2].id).toBe(item1.id);
    });

    it('should return false for non-existent item', () => {
      const reordered = manager.reorderItem('non-existent', 0);
      expect(reordered).toBe(false);
    });
  });

  describe('clearQueue', () => {
    it('should clear all items from queue', () => {
      manager.addToQueue(mockNodeInfo() as any, mockWorkPlan() as any);
      manager.addToQueue(mockNodeInfo() as any, mockWorkPlan() as any);

      manager.clearQueue();

      const queue = manager.getQueue();
      expect(queue.items).toHaveLength(0);
      expect(queue.currentIndex).toBe(-1);
      expect(queue.isProcessing).toBe(false);
    });
  });

  describe('updateItemStatus', () => {
    it('should update item status', () => {
      const item = manager.addToQueue(mockNodeInfo() as any, mockWorkPlan() as any);

      manager.updateItemStatus(item.id, 'converting');

      const updated = manager.getItem(item.id);
      expect(updated?.status).toBe('converting');
    });

    it('should set completedAt for terminal statuses', () => {
      const item = manager.addToQueue(mockNodeInfo() as any, mockWorkPlan() as any);

      manager.updateItemStatus(item.id, 'completed');

      const updated = manager.getItem(item.id);
      expect(updated?.completedAt).toBeDefined();
    });
  });

  describe('approveWorkPlan', () => {
    it('should approve a work plan and update status', () => {
      const item = manager.addToQueue(mockNodeInfo() as any, mockWorkPlan() as any);

      const approved = manager.approveWorkPlan(item.id, 'TestUser');

      expect(approved).toBe(true);
      const updated = manager.getItem(item.id);
      expect(updated?.status).toBe('approved');
      expect(updated?.workPlan?.approvedBy).toBe('TestUser');
      expect(updated?.workPlan?.approvedAt).toBeDefined();
    });

    it('should return false for non-existent item', () => {
      const approved = manager.approveWorkPlan('non-existent');
      expect(approved).toBe(false);
    });
  });

  describe('rejectWorkPlan', () => {
    it('should reject a work plan with reason', () => {
      const item = manager.addToQueue(mockNodeInfo() as any, mockWorkPlan() as any);

      const rejected = manager.rejectWorkPlan(item.id, 'Does not meet standards');

      expect(rejected).toBe(true);
      const updated = manager.getItem(item.id);
      expect(updated?.status).toBe('failed');
      expect(updated?.error).toContain('Does not meet standards');
    });
  });

  describe('retryItem', () => {
    it('should reset a failed item to pending', () => {
      const item = manager.addToQueue(mockNodeInfo() as any, mockWorkPlan() as any);
      manager.updateItemStatus(item.id, 'failed');

      const retried = manager.retryItem(item.id);

      expect(retried).toBe(true);
      const updated = manager.getItem(item.id);
      expect(updated?.status).toBe('pending');
      expect(updated?.error).toBeUndefined();
    });

    it('should return false for non-failed items', () => {
      const item = manager.addToQueue(mockNodeInfo() as any, mockWorkPlan() as any);

      const retried = manager.retryItem(item.id);

      expect(retried).toBe(false);
    });
  });

  describe('markAsSent', () => {
    it('should mark item as completed on success', () => {
      const item = manager.addToQueue(mockNodeInfo() as any, mockWorkPlan() as any);

      manager.markAsSent(item.id, true);

      const updated = manager.getItem(item.id);
      expect(updated?.status).toBe('completed');
      expect(updated?.completedAt).toBeDefined();
    });

    it('should mark item as failed with error message on failure', () => {
      const item = manager.addToQueue(mockNodeInfo() as any, mockWorkPlan() as any);

      manager.markAsSent(item.id, false);

      const updated = manager.getItem(item.id);
      expect(updated?.status).toBe('failed');
      expect(updated?.error).toContain('Failed to send to MCP');
    });
  });

  describe('getStats', () => {
    it('should return correct statistics', () => {
      const item1 = manager.addToQueue(mockNodeInfo() as any, mockWorkPlan() as any);
      const item2 = manager.addToQueue(mockNodeInfo() as any, mockWorkPlan() as any);
      manager.addToQueue(mockNodeInfo() as any, mockWorkPlan() as any);

      manager.updateItemStatus(item1.id, 'completed');
      manager.updateItemStatus(item2.id, 'failed');
      // item3 remains pending

      const stats = manager.getStats();

      expect(stats.total).toBe(3);
      expect(stats.completed).toBe(1);
      expect(stats.failed).toBe(1);
      expect(stats.pending).toBe(1);
    });
  });

  describe('getItemsByStatus', () => {
    it('should filter items by status', () => {
      const item1 = manager.addToQueue(mockNodeInfo() as any, mockWorkPlan() as any);
      const item2 = manager.addToQueue(mockNodeInfo() as any, mockWorkPlan() as any);
      manager.addToQueue(mockNodeInfo() as any, mockWorkPlan() as any);

      manager.updateItemStatus(item1.id, 'completed');
      manager.updateItemStatus(item2.id, 'completed');

      const completed = manager.getItemsByStatus('completed');

      expect(completed).toHaveLength(2);
      expect(completed.every((i: any) => i.status === 'completed')).toBe(true);
    });
  });

  describe('getPendingItems', () => {
    it('should return pending and approved items', () => {
      const item1 = manager.addToQueue(mockNodeInfo() as any, mockWorkPlan() as any);
      const item2 = manager.addToQueue(mockNodeInfo() as any, mockWorkPlan() as any);
      const item3 = manager.addToQueue(mockNodeInfo() as any, mockWorkPlan() as any);

      manager.approveWorkPlan(item1.id);
      manager.updateItemStatus(item3.id, 'completed');

      const pending = manager.getPendingItems();

      expect(pending).toHaveLength(2);
      expect(pending.some((i: any) => i.id === item1.id)).toBe(true); // approved
      expect(pending.some((i: any) => i.id === item2.id)).toBe(true); // pending
    });
  });

  describe('listeners', () => {
    it('should notify on queue changes', () => {
      const listener = jest.fn();
      manager.onQueueChange(listener);

      manager.addToQueue(mockNodeInfo() as any, mockWorkPlan() as any);

      expect(listener).toHaveBeenCalled();
    });

    it('should allow unsubscribing from queue changes', () => {
      const listener = jest.fn();
      const unsubscribe = manager.onQueueChange(listener);

      unsubscribe();
      manager.addToQueue(mockNodeInfo() as any, mockWorkPlan() as any);

      expect(listener).not.toHaveBeenCalled();
    });

    it('should notify on specific item changes', () => {
      const item = manager.addToQueue(mockNodeInfo() as any, mockWorkPlan() as any);
      const listener = jest.fn();
      manager.onItemChange(item.id, listener);

      manager.updateItemStatus(item.id, 'converting');

      expect(listener).toHaveBeenCalledWith(expect.objectContaining({ status: 'converting' }));
    });
  });

  describe('processing control', () => {
    it('should pause and resume processing', () => {
      manager.addToQueue(mockNodeInfo() as any, mockWorkPlan() as any);

      manager.pauseProcessing();
      let queue = manager.getQueue();
      expect(queue.isPaused).toBe(true);

      manager.resumeProcessing();
      queue = manager.getQueue();
      expect(queue.isPaused).toBe(false);
    });
  });
});

describe('QueueManager Priority', () => {
  it('should use atomic design level priority correctly', () => {
    const manager = new QueueManager();

    const levels: AtomicLevel[] = ['page', 'template', 'organism', 'molecule', 'atom'];

    // Add in reverse order (page first, atom last)
    for (const level of levels) {
      const node = mockNodeInfo({ id: level, name: level });
      manager.addToQueue(node as any, mockWorkPlan(level) as any);
    }

    const queue = manager.getQueue();

    // Should be reordered to: atom, molecule, organism, template, page
    expect(queue.items[0].nodeName).toBe('atom');
    expect(queue.items[1].nodeName).toBe('molecule');
    expect(queue.items[2].nodeName).toBe('organism');
    expect(queue.items[3].nodeName).toBe('template');
    expect(queue.items[4].nodeName).toBe('page');
  });

  it('should add dependency weight to priority', () => {
    const manager = new QueueManager();

    const nodeNoDeps = mockNodeInfo({ id: 'no-deps', name: 'NoDeps' });
    const nodeWithDeps = mockNodeInfo({ id: 'with-deps', name: 'WithDeps' });

    const planNoDeps = mockWorkPlan('atom', []);
    const planWithDeps = mockWorkPlan('atom', ['dep1', 'dep2', 'dep3']);

    manager.addToQueue(nodeWithDeps as any, planWithDeps as any);
    manager.addToQueue(nodeNoDeps as any, planNoDeps as any);

    const queue = manager.getQueue();

    // Item with no dependencies should have lower priority number (higher priority)
    expect(queue.items[0].nodeName).toBe('NoDeps');
    expect(queue.items[1].nodeName).toBe('WithDeps');
  });
});
