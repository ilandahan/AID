/**
 * @file plugin/ui-messaging.ts
 * @description UI communication - handles messages between plugin and UI
 */

import type { PluginToUIMessage, SelectionInfo } from './types';
import { currentState, resetStateForNewSelection } from './state';

// ============================================
// UI Communication Functions
// ============================================

/**
 * Send a message to the UI
 */
export function sendToUI(message: PluginToUIMessage): void {
  figma.ui.postMessage(message);
}

/**
 * Send an error message to both UI and Figma notification
 */
export function sendError(message: string): void {
  sendToUI({ type: 'ERROR', message });
  figma.notify(message, { error: true });
}

/**
 * Send pipeline step progress to UI
 */
export function sendPipelineStep(step: string, status: string, detail?: string): void {
  sendToUI({ type: 'PIPELINE_STEP', step, status, detail });
}

// ============================================
// Selection Handling
// ============================================

/**
 * Handle selection change in Figma
 */
export function handleSelectionChange(): void {
  const selection = figma.currentPage.selection;

  if (selection.length === 0) {
    currentState.selectedNode = null;
    sendToUI({ type: 'SELECTION_CHANGED', node: null });
    return;
  }

  // Get first valid component
  const node = selection.find(
    (n) =>
      n.type === 'COMPONENT' || n.type === 'COMPONENT_SET' || n.type === 'INSTANCE'
  );

  if (!node) {
    currentState.selectedNode = null;
    sendToUI({ type: 'SELECTION_CHANGED', node: null });
    return;
  }

  currentState.selectedNode = node;

  // Reset state for new selection
  resetStateForNewSelection();

  // Build selection info
  const selectionInfo: SelectionInfo = {
    name: node.name,
    type: node.type,
    nodeId: node.id,
    hasDescription:
      'description' in node && Boolean((node as ComponentNode).description),
  };

  // Count variants if component set
  if (node.type === 'COMPONENT_SET') {
    selectionInfo.variantCount = node.children.filter(
      (c) => c.type === 'COMPONENT'
    ).length;
  }

  // Count children
  if ('children' in node) {
    selectionInfo.childCount = (node as FrameNode).children?.length || 0;
  }

  sendToUI({ type: 'SELECTION_CHANGED', node: selectionInfo });
}

// ============================================
// Node Selection (Go to Issue)
// ============================================

/**
 * Select a node by ID and scroll to it in the canvas.
 * Used by "Go to" buttons in the issues list.
 */
export function selectNodeById(nodeId: string): void {
  try {
    const node = figma.getNodeById(nodeId);
    if (!node) {
      figma.notify('❌ Node not found', { error: true });
      return;
    }

    // Check if it's a SceneNode (can be selected)
    if (!('parent' in node) || node.parent === null) {
      figma.notify('❌ Cannot select this node', { error: true });
      return;
    }

    // Set selection and scroll to it
    const sceneNode = node as SceneNode;
    figma.currentPage.selection = [sceneNode];
    figma.viewport.scrollAndZoomIntoView([sceneNode]);

    figma.notify(`🎯 Selected: ${sceneNode.name}`);
  } catch (error) {
    figma.notify('❌ Failed to select node', { error: true });
  }
}
