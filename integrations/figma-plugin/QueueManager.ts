/**
 * @file QueueManager.ts
 * @description Queue manager for component conversion with priority ordering.
 *              Uses topological sort to ensure dependencies are processed first.
 * @created 2024-12
 * @related
 *   - ./NodeAnalyzer.ts - Provides component classification for priority
 *   - ../types/index.ts - Type definitions for queue items
 *
 * @priority
 *   Components are processed in Atomic Design order:
 *   1. Atoms (priority 1) - Built first as building blocks
 *   2. Molecules (priority 2) - Composed of atoms
 *   3. Organisms (priority 3) - Complex compositions
 *   4. Templates (priority 4) - Page layouts
 *   5. Pages (priority 5) - Full page implementations
 */

import type {
  QueueItem,
  ConversionQueue,
  ConversionStatus,
  FigmaNodeInfo,
  ComponentWorkPlan,
  EnrichedComponentData,
  DesignToken,
  AtomicLevel,
} from './types';

// Priority weights for different atomic levels
const LEVEL_PRIORITY: Record<AtomicLevel, number> = {
  atom: 1,      // Highest priority - build atoms first
  molecule: 2,
  organism: 3,
  template: 4,
  page: 5,      // Lowest priority
};

export class QueueManager {
  private queue: ConversionQueue = {
    items: [],
    currentIndex: -1,
    isProcessing: false,
    isPaused: false,
  };
  
  private statusListeners: ((queue: ConversionQueue) => void)[] = [];
  private itemListeners: Map<string, ((item: QueueItem) => void)[]> = new Map();
  
  // ============================================
  // Queue Operations
  // ============================================
  
  /**
   * Add a node to the conversion queue
   */
  addToQueue(nodeInfo: FigmaNodeInfo, workPlan: ComponentWorkPlan): QueueItem {
    const item: QueueItem = {
      id: this.generateId(),
      nodeId: nodeInfo.id,
      nodeName: nodeInfo.name,
      priority: this.calculatePriority(workPlan),
      status: 'pending',
      workPlan,
      addedAt: new Date(),
    };
    
    // Insert in priority order
    const insertIndex = this.findInsertIndex(item.priority);
    this.queue.items.splice(insertIndex, 0, item);
    
    this.notifyQueueChange();
    return item;
  }
  
  /**
   * Add multiple nodes to the queue in dependency order
   */
  addBatchToQueue(
    items: Array<{ nodeInfo: FigmaNodeInfo; workPlan: ComponentWorkPlan }>
  ): QueueItem[] {
    // Sort by dependencies first, then by atomic level
    const sortedItems = this.sortByDependencies(items);
    
    return sortedItems.map(({ nodeInfo, workPlan }) => 
      this.addToQueue(nodeInfo, workPlan)
    );
  }
  
  /**
   * Remove an item from the queue
   */
  removeFromQueue(itemId: string): boolean {
    const index = this.queue.items.findIndex(item => item.id === itemId);
    if (index === -1) return false;
    
    // Don't remove if currently processing
    if (index === this.queue.currentIndex && this.queue.isProcessing) {
      return false;
    }
    
    this.queue.items.splice(index, 1);
    
    // Adjust current index if needed
    if (index < this.queue.currentIndex) {
      this.queue.currentIndex--;
    }
    
    this.notifyQueueChange();
    return true;
  }
  
  /**
   * Reorder an item in the queue
   */
  reorderItem(itemId: string, newIndex: number): boolean {
    const currentIndex = this.queue.items.findIndex(item => item.id === itemId);
    if (currentIndex === -1) return false;
    
    // Don't reorder if currently processing this item
    if (currentIndex === this.queue.currentIndex && this.queue.isProcessing) {
      return false;
    }
    
    const [item] = this.queue.items.splice(currentIndex, 1);
    const clampedIndex = Math.max(0, Math.min(newIndex, this.queue.items.length));
    this.queue.items.splice(clampedIndex, 0, item);
    
    this.notifyQueueChange();
    return true;
  }
  
  /**
   * Clear the entire queue
   */
  clearQueue(): void {
    if (this.queue.isProcessing) {
      this.queue.isPaused = true;
    }
    
    this.queue.items = [];
    this.queue.currentIndex = -1;
    this.queue.isProcessing = false;
    
    this.notifyQueueChange();
  }
  
  // ============================================
  // Queue Processing
  // ============================================
  
  /**
   * Start processing the queue
   */
  async startProcessing(
    processItem: (item: QueueItem) => Promise<{
      enrichedData: EnrichedComponentData;
      tokens: DesignToken[];
    }>
  ): Promise<void> {
    if (this.queue.isProcessing) return;
    
    this.queue.isProcessing = true;
    this.queue.isPaused = false;
    
    while (this.queue.currentIndex < this.queue.items.length - 1) {
      if (this.queue.isPaused) {
        this.queue.isProcessing = false;
        this.notifyQueueChange();
        return;
      }
      
      this.queue.currentIndex++;
      const item = this.queue.items[this.queue.currentIndex];
      
      if (item.status !== 'approved' && item.status !== 'pending') {
        continue; // Skip items that aren't ready
      }
      
      try {
        this.updateItemStatus(item.id, 'converting');
        item.startedAt = new Date();
        
        const result = await processItem(item);
        
        item.enrichedData = result.enrichedData;
        item.designTokens = result.tokens;
        
        this.updateItemStatus(item.id, 'sending');
        
      } catch (error) {
        item.error = error instanceof Error ? error.message : String(error);
        this.updateItemStatus(item.id, 'failed');
      }
      
      this.notifyQueueChange();
    }
    
    this.queue.isProcessing = false;
    this.notifyQueueChange();
  }
  
  /**
   * Pause queue processing
   */
  pauseProcessing(): void {
    this.queue.isPaused = true;
    this.notifyQueueChange();
  }
  
  /**
   * Resume queue processing
   */
  resumeProcessing(): void {
    this.queue.isPaused = false;
    this.notifyQueueChange();
  }
  
  /**
   * Retry a failed item
   */
  retryItem(itemId: string): boolean {
    const item = this.getItem(itemId);
    if (!item || item.status !== 'failed') return false;
    
    item.status = 'pending';
    item.error = undefined;
    item.startedAt = undefined;
    item.completedAt = undefined;
    
    this.notifyItemChange(item);
    this.notifyQueueChange();
    return true;
  }
  
  // ============================================
  // Item Status Management
  // ============================================
  
  /**
   * Update an item's status
   */
  updateItemStatus(itemId: string, status: ConversionStatus): void {
    const item = this.getItem(itemId);
    if (!item) return;
    
    item.status = status;
    
    if (status === 'completed' || status === 'failed') {
      item.completedAt = new Date();
    }
    
    this.notifyItemChange(item);
    this.notifyQueueChange();
  }
  
  /**
   * Approve a work plan
   */
  approveWorkPlan(itemId: string, approver?: string): boolean {
    const item = this.getItem(itemId);
    if (!item || !item.workPlan) return false;
    
    item.workPlan.approvedAt = new Date();
    item.workPlan.approvedBy = approver;
    item.status = 'approved';
    
    this.notifyItemChange(item);
    this.notifyQueueChange();
    return true;
  }
  
  /**
   * Reject a work plan
   */
  rejectWorkPlan(itemId: string, reason: string): boolean {
    const item = this.getItem(itemId);
    if (!item || !item.workPlan) return false;
    
    item.status = 'failed';
    item.error = `Work plan rejected: ${reason}`;
    
    this.notifyItemChange(item);
    this.notifyQueueChange();
    return true;
  }
  
  /**
   * Update enriched data for an item
   */
  updateEnrichedData(
    itemId: string, 
    updates: Partial<EnrichedComponentData>
  ): boolean {
    const item = this.getItem(itemId);
    if (!item) return false;
    
    if (item.enrichedData) {
      item.enrichedData = { ...item.enrichedData, ...updates };
    }
    
    this.notifyItemChange(item);
    return true;
  }
  
  /**
   * Mark an item as sent to MCP
   */
  markAsSent(itemId: string, success: boolean): void {
    const item = this.getItem(itemId);
    if (!item) return;
    
    item.status = success ? 'completed' : 'failed';
    item.completedAt = new Date();
    
    if (!success) {
      item.error = 'Failed to send to MCP backend';
    }
    
    this.notifyItemChange(item);
    this.notifyQueueChange();
  }
  
  // ============================================
  // Queue Queries
  // ============================================
  
  /**
   * Get an item by ID
   */
  getItem(itemId: string): QueueItem | undefined {
    return this.queue.items.find(item => item.id === itemId);
  }
  
  /**
   * Get the current queue state
   */
  getQueue(): ConversionQueue {
    return { ...this.queue };
  }
  
  /**
   * Get all pending items
   */
  getPendingItems(): QueueItem[] {
    return this.queue.items.filter(item => 
      item.status === 'pending' || item.status === 'approved'
    );
  }
  
  /**
   * Get items by status
   */
  getItemsByStatus(status: ConversionStatus): QueueItem[] {
    return this.queue.items.filter(item => item.status === status);
  }
  
  /**
   * Get queue statistics
   */
  getStats(): {
    total: number;
    pending: number;
    processing: number;
    completed: number;
    failed: number;
    averageProcessingTime: number;
  } {
    const items = this.queue.items;
    const completed = items.filter(i => i.status === 'completed');
    
    const processingTimes = completed
      .filter(i => i.startedAt && i.completedAt)
      .map(i => i.completedAt!.getTime() - i.startedAt!.getTime());
    
    const avgTime = processingTimes.length > 0
      ? processingTimes.reduce((a, b) => a + b, 0) / processingTimes.length
      : 0;
    
    return {
      total: items.length,
      pending: items.filter(i => i.status === 'pending' || i.status === 'approved').length,
      processing: items.filter(i => 
        ['analyzing', 'enriching', 'converting', 'sending'].includes(i.status)
      ).length,
      completed: completed.length,
      failed: items.filter(i => i.status === 'failed').length,
      averageProcessingTime: avgTime,
    };
  }
  
  // ============================================
  // Listeners
  // ============================================
  
  /**
   * Subscribe to queue changes
   */
  onQueueChange(callback: (queue: ConversionQueue) => void): () => void {
    this.statusListeners.push(callback);
    return () => {
      const index = this.statusListeners.indexOf(callback);
      if (index > -1) this.statusListeners.splice(index, 1);
    };
  }
  
  /**
   * Subscribe to specific item changes
   */
  onItemChange(itemId: string, callback: (item: QueueItem) => void): () => void {
    const listeners = this.itemListeners.get(itemId) || [];
    listeners.push(callback);
    this.itemListeners.set(itemId, listeners);
    
    return () => {
      const itemListeners = this.itemListeners.get(itemId);
      if (itemListeners) {
        const index = itemListeners.indexOf(callback);
        if (index > -1) itemListeners.splice(index, 1);
      }
    };
  }
  
  // ============================================
  // Private Methods
  // ============================================
  
  private generateId(): string {
    return `queue-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
  
  private calculatePriority(workPlan: ComponentWorkPlan): number {
    const levelPriority = LEVEL_PRIORITY[workPlan.classification.level];
    const dependencyPriority = workPlan.dependencies.length * 0.1;
    
    // Lower number = higher priority
    return levelPriority + dependencyPriority;
  }
  
  private findInsertIndex(priority: number): number {
    for (let i = 0; i < this.queue.items.length; i++) {
      if (this.queue.items[i].priority > priority) {
        return i;
      }
    }
    return this.queue.items.length;
  }
  
  private sortByDependencies(
    items: Array<{ nodeInfo: FigmaNodeInfo; workPlan: ComponentWorkPlan }>
  ): Array<{ nodeInfo: FigmaNodeInfo; workPlan: ComponentWorkPlan }> {
    const nodeIds = new Set(items.map(i => i.nodeInfo.id));
    const graph = new Map<string, string[]>();
    
    // Build dependency graph
    for (const item of items) {
      const deps = item.workPlan.dependencies
        .filter(d => nodeIds.has(d.nodeId))
        .map(d => d.nodeId);
      graph.set(item.nodeInfo.id, deps);
    }
    
    // Topological sort
    const sorted: typeof items = [];
    const visited = new Set<string>();
    const temp = new Set<string>();
    
    const visit = (id: string) => {
      if (temp.has(id)) return; // Cycle detected, skip
      if (visited.has(id)) return;
      
      temp.add(id);
      const deps = graph.get(id) || [];
      for (const dep of deps) {
        visit(dep);
      }
      temp.delete(id);
      visited.add(id);
      
      const item = items.find(i => i.nodeInfo.id === id);
      if (item) sorted.push(item);
    };
    
    for (const item of items) {
      visit(item.nodeInfo.id);
    }
    
    return sorted;
  }
  
  private notifyQueueChange(): void {
    const queueState = this.getQueue();
    for (const listener of this.statusListeners) {
      try {
        listener(queueState);
      } catch (e) {
        console.error('Queue listener error:', e);
      }
    }
  }
  
  private notifyItemChange(item: QueueItem): void {
    const listeners = this.itemListeners.get(item.id);
    if (listeners) {
      for (const listener of listeners) {
        try {
          listener({ ...item });
        } catch (e) {
          console.error('Item listener error:', e);
        }
      }
    }
  }
}

// Export singleton instance
export const queueManager = new QueueManager();
