/**
 * State Management Module
 * Centralized state for the Figma plugin UI
 */

// Global state object
export const state = {
  node: null,
  audit: null,
  metadata: null,
  generated: null,
  score: 0,
  exportReady: false,
  connected: false
};

/**
 * Update MCP-required buttons based on connection and selection state
 * Buttons are enabled only when BOTH connected AND component selected
 */
export function updateMcpButtons() {
  const canRun = state.connected && state.node !== null;

  // Update all mcp-required buttons
  document.querySelectorAll('.mcp-required').forEach(btn => {
    btn.disabled = !canRun;
  });

  console.log('[UI] updateMcpButtons - connected:', state.connected, 'node:', !!state.node, 'canRun:', canRun);
}

// Node waiting for user confirmation to switch
export let pendingNode = null;

export function setPendingNode(node) {
  pendingNode = node;
}

// Flag to track when confirmation modal is open
// While true, incoming SELECTION_CHANGED events update pendingNode instead of triggering new modals
export let isAwaitingConfirmation = false;

export function setAwaitingConfirmation(value) {
  isAwaitingConfirmation = value;
  console.log('[UI] isAwaitingConfirmation:', value);
}

// Node we just switched away from - used to ignore stale events
// Figma can send delayed selection events for the old node
let justSwitchedFromNode = null;
let switchedFromTimeout = null;

export function getJustSwitchedFrom() {
  return justSwitchedFromNode;
}

/**
 * Mark that we just switched away from a node
 * Stale selection events for this node will be ignored for 500ms
 */
export function setJustSwitchedFrom(node) {
  justSwitchedFromNode = node;
  console.log('[UI] justSwitchedFrom set to:', node?.name || null);

  // Clear previous timeout if exists
  if (switchedFromTimeout) {
    clearTimeout(switchedFromTimeout);
  }

  // Auto-clear after 500ms
  if (node) {
    switchedFromTimeout = setTimeout(() => {
      if (justSwitchedFromNode === node) {
        justSwitchedFromNode = null;
        console.log('[UI] justSwitchedFrom auto-cleared');
      }
    }, 500);
  }
}

// DOM helper
export const $ = (id) => document.getElementById(id);

/**
 * Check if there's meaningful analysis data that would be lost
 * This includes:
 * - Audit results (audit !== null)
 * - Metadata analysis (metadata !== null)
 * - Generated metadata (generated !== null)
 * - Export readiness status (exportReady === true)
 * - Meaningful score (score > 0)
 */
export function hasAnalysisData() {
  return (
    state.audit !== null ||
    state.metadata !== null ||
    state.generated !== null ||
    state.exportReady === true ||
    state.score > 0
  );
}

/**
 * Reset state to initial values
 */
export function resetState() {
  state.node = null;
  state.audit = null;
  state.metadata = null;
  state.generated = null;
  state.score = 0;
  state.exportReady = false;
}
