/**
 * Selection Rendering Module
 * Handles component selection display and switching
 */

import { state, $, hasAnalysisData, pendingNode, setPendingNode, updateMcpButtons, isAwaitingConfirmation, setAwaitingConfirmation, getJustSwitchedFrom } from '../state.js';
import { t } from '../utils/i18n.js';
import { escapeHtml } from '../utils/sanitize.js';

/**
 * Clear all analysis data from state and UI
 * Called when switching to a different component
 */
export function clearAnalysisData() {
  // Reset state
  state.audit = null;
  state.metadata = null;
  state.generated = null;
  state.score = 0;
  state.exportReady = false;

  // === Reset Audit Tab ===
  const auditScoreEl = $('auditScore');
  const scoreBarFillEl = $('scoreBarFill');
  const issuesListEl = $('issuesList');
  const issueCountEl = $('issueCount');
  const scoreStatusEl = $('scoreStatus');

  if (auditScoreEl) auditScoreEl.textContent = '--';
  if (scoreBarFillEl) {
    scoreBarFillEl.style.width = '0%';
    scoreBarFillEl.className = 'score-bar-fill';
  }
  if (issuesListEl) issuesListEl.innerHTML = '';
  if (issueCountEl) issueCountEl.textContent = '0';
  if (scoreStatusEl) {
    scoreStatusEl.textContent = t('status.loading');
    scoreStatusEl.className = 'score-status not-ready';
  }

  // === Reset Metadata Tab ===
  const metadataScoreEl = $('metadataScore');
  const metadataBarEl = $('metadataBar');
  const metadataStatusEl = $('metadataStatus');
  const metadataDetailsEl = $('metadataDetails');
  const generatedMetaEl = $('generatedMeta');
  const applyMetaBtnMeta = $('applyMetaBtnMeta');

  if (metadataScoreEl) metadataScoreEl.textContent = '--';
  if (metadataBarEl) {
    metadataBarEl.style.width = '0%';
    metadataBarEl.className = 'score-bar-fill';
  }
  if (metadataStatusEl) {
    metadataStatusEl.textContent = t('metadata.runAnalysis');
    metadataStatusEl.className = 'score-status not-ready';
  }
  if (metadataDetailsEl) {
    metadataDetailsEl.innerHTML = `<div class="empty" style="padding: 12px; color: var(--gray-500); text-align: center;">${t('metadata.selectComponent')}</div>`;
  }
  if (generatedMetaEl) generatedMetaEl.textContent = '// Run generate to get metadata';
  if (applyMetaBtnMeta) applyMetaBtnMeta.style.display = 'none';

  // === Reset Review Tab ===
  const reviewResultsEl = $('reviewResults');
  const pipelineProgressEl = $('pipelineProgress');
  const applyMetaBtn = $('applyMetaBtn');
  const reviewSelectionPanel = $('reviewSelectionPanel');

  if (reviewResultsEl) reviewResultsEl.innerHTML = '';
  if (pipelineProgressEl) pipelineProgressEl.style.display = 'none';
  if (applyMetaBtn) applyMetaBtn.style.display = 'none';
  if (reviewSelectionPanel) reviewSelectionPanel.style.display = 'block'; // Show again for new component

  // === Reset ALL unified component info panels across ALL tabs ===
  const componentInfoPanels = [
    'componentInfoPanel',          // Review tab
    'auditComponentInfoPanel',     // Audit tab
    'metadataComponentInfoPanel',  // Metadata tab
    'devComponentInfoPanel'        // Dev Info tab (will be shown when content loads)
  ];
  componentInfoPanels.forEach(panelId => {
    const panelEl = $(panelId);
    if (panelEl) panelEl.style.display = 'none';
  });

  // === Reset Dev Handoff Tab ===
  const devHandoffEmpty = $('devHandoffEmpty');
  const devHandoffContent = $('devHandoffContent');
  const devHandoffButtons = $('devHandoffButtons');

  if (devHandoffEmpty) devHandoffEmpty.style.display = 'block';
  if (devHandoffContent) devHandoffContent.style.display = 'none';
  if (devHandoffButtons) devHandoffButtons.style.display = 'none';

  console.log('[UI] 🧹 Cleared all analysis data for component switch');
}

/**
 * Update selection display based on node
 * Shows confirmation modal when switching components with existing data
 * @param {Object|null} node - Selected node or null for deselection
 */
export function updateSelection(node) {
  const panels = ['selectionPanel', 'reviewSelectionPanel'];

  // If node is null (deselection), just clear
  if (!node) {
    state.node = null;
    panels.forEach(id => {
      const el = $(id);
      if (el) el.innerHTML = `<div class="empty">${t('selection.empty')}</div>`;
    });
    const auditContentEl = $('auditContent');
    const reviewContentEl = $('reviewContent');
    if (auditContentEl) auditContentEl.style.display = 'none';
    if (reviewContentEl) reviewContentEl.style.display = 'none';
    updateMcpButtons(); // Disable buttons when no component selected
    return;
  }

  // Guard 1: If we're awaiting confirmation (modal is open), update pending node and ignore
  if (isAwaitingConfirmation) {
    // Update the pending node to the latest selection (in case user clicks around)
    if (node.nodeId !== state.node?.nodeId) {
      setPendingNode(node);
      console.log('[UI] ⏸️ Modal open - updated pending node to:', node.name);
    }
    return; // Don't process while modal is open
  }

  // Guard 2: Ignore stale events for the node we just switched away from
  const switchedFrom = getJustSwitchedFrom();
  if (switchedFrom && node.nodeId === switchedFrom.nodeId) {
    console.log('[UI] ⏭️ Ignoring stale selection event for:', node.name);
    return;
  }

  // Check if we're switching to a DIFFERENT component with existing data
  const isDifferentComponent = state.node && state.node.nodeId !== node.nodeId;
  const hasData = hasAnalysisData();

  if (isDifferentComponent && hasData) {
    // Store the pending node and show confirmation modal
    setPendingNode(node);
    setAwaitingConfirmation(true); // Mark that modal is now open
    const currentNameEl = $('currentComponentName');
    const switchModal = $('componentSwitchModal');
    if (currentNameEl) currentNameEl.textContent = state.node.name;
    if (switchModal) switchModal.style.display = 'flex';
    console.log('[UI] ⚠️ Component switch detected - showing confirmation modal');
    console.log('[UI]    Current:', state.node.name, '→ New:', node.name);
    return; // Don't update yet - wait for user confirmation
  }

  // Apply the selection (either first selection or same component re-selected)
  applySelection(node);
}

/**
 * Actually apply the selection after confirmation (or when no confirmation needed)
 * @param {Object} node - Node to apply as selection
 */
export function applySelection(node) {
  state.node = node;

  // Build component name and meta strings once
  const componentName = '📦 ' + node.name;
  const componentMeta = node.variantCount ? node.variantCount + ' variant' + (node.variantCount !== 1 ? 's' : '') : '';

  // Hide the old reviewSelectionPanel (the gray one at top)
  const reviewSelectionPanel = $('reviewSelectionPanel');
  if (reviewSelectionPanel) {
    reviewSelectionPanel.style.display = 'none';
  }

  // === Update ALL unified component info panels across ALL tabs ===
  // This ensures the same look and data in Review, Audit, Metadata, and Dev Info tabs
  const panelConfigs = [
    { panel: 'componentInfoPanel', name: 'componentInfoName', meta: 'componentInfoMeta' },       // Review tab
    { panel: 'auditComponentInfoPanel', name: 'auditComponentInfoName', meta: 'auditComponentInfoMeta' },  // Audit tab
    { panel: 'metadataComponentInfoPanel', name: 'metadataComponentInfoName', meta: 'metadataComponentInfoMeta' }, // Metadata tab
    { panel: 'devComponentInfoPanel', name: 'devComponentInfoName', meta: 'devComponentInfoMeta' }  // Dev Info tab
  ];

  panelConfigs.forEach(({ panel, name, meta }) => {
    const panelEl = $(panel);
    const nameEl = $(name);
    const metaEl = $(meta);
    if (panelEl) panelEl.style.display = 'block';
    if (nameEl) nameEl.textContent = componentName;
    if (metaEl) metaEl.textContent = componentMeta;
  });

  const auditContent = $('auditContent');
  const reviewContent = $('reviewContent');
  if (auditContent) auditContent.style.display = 'block';
  if (reviewContent) reviewContent.style.display = 'block';

  // Enable MCP-required buttons if connected
  updateMcpButtons();
}
