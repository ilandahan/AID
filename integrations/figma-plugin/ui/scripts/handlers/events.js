/**
 * Event Handlers Module
 * Button click handlers and UI interactions
 */

import { state, $, pendingNode, setPendingNode, setAwaitingConfirmation, setJustSwitchedFrom } from '../state.js';
import { showToast } from '../utils/toast.js';
import { copyToClipboard } from '../utils/clipboard.js';
import { showPipelineProgress, clearAnalysisData, applySelection } from '../rendering/index.js';
import { generateDevMarkdown, generateDevTypeScript } from '../rendering/report.js';

/**
 * Initialize all event handlers
 */
export function initEventHandlers() {
  initTabHandlers();
  initButtonHandlers();
  initModalHandlers();
  initGotoHandler();
}

/**
 * Initialize tab switching
 */
function initTabHandlers() {
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      if (tab.classList.contains('disabled')) return;
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      tab.classList.add('active');
      const tabContent = $(tab.dataset.tab + '-tab');
      if (tabContent) {
        tabContent.classList.add('active');
      }
    });
  });
}

/**
 * Initialize button click handlers
 */
function initButtonHandlers() {
  // Run Pipeline button
  const runPipelineBtnEl = $('runPipelineBtn');
  if (runPipelineBtnEl) {
    runPipelineBtnEl.onclick = () => {
      console.log('[UI] Button: RUN_FULL_PIPELINE clicked');
      runPipelineBtnEl.classList.add('loading');
      const reviewResultsEl = $('reviewResults');
      if (reviewResultsEl) reviewResultsEl.innerHTML = '';
      showPipelineProgress();
      parent.postMessage({ pluginMessage: { type: 'RUN_FULL_PIPELINE' } }, '*');
    };
  }

  // Run Audit button
  if ($('runAuditBtn')) {
    $('runAuditBtn').onclick = () => {
      console.log('[UI] Button: RUN_AUDIT clicked');
      parent.postMessage({ pluginMessage: { type: 'RUN_AUDIT' } }, '*');
    };
  }

  // Analyze Metadata button
  if ($('analyzeBtn')) {
    $('analyzeBtn').onclick = () => {
      console.log('[UI] Button: ANALYZE_METADATA clicked');
      parent.postMessage({ pluginMessage: { type: 'ANALYZE_METADATA' } }, '*');
    };
  }

  // Generate Metadata button
  if ($('generateBtn')) {
    $('generateBtn').onclick = () => {
      console.log('[UI] Button: GENERATE_METADATA clicked');
      parent.postMessage({ pluginMessage: { type: 'GENERATE_METADATA' } }, '*');
    };
  }

  // Copy Dev Handoff buttons
  if ($('copyDevHandoffBtn')) {
    $('copyDevHandoffBtn').onclick = () => {
      const markdown = generateDevMarkdown();
      console.log('[UI] Button: COPY_DEV_MARKDOWN clicked, length:', markdown.length);
      copyToClipboard(markdown);
    };
  }

  if ($('copyDevCodeBtn')) {
    $('copyDevCodeBtn').onclick = () => {
      const typescript = generateDevTypeScript();
      console.log('[UI] Button: COPY_DEV_TYPESCRIPT clicked, length:', typescript.length);
      copyToClipboard(typescript);
    };
  }

  // Export button
  if ($('exportAIDBtn')) {
    $('exportAIDBtn').onclick = () => {
      console.log('[UI] Button: EXPORT_TO_AID clicked');
      // Get level from SERVER (single source of truth)
      // state.audit.level is set by server's audit response
      parent.postMessage({
        pluginMessage: {
          type: 'EXPORT_TO_AID',
          level: state.audit?.level || 'molecule',
          componentName: state.node?.name || 'Component'
        }
      }, '*');
    };
  }

  // Disconnect button
  if ($('disconnectBtn')) {
    $('disconnectBtn').onclick = () => {
      console.log('[UI] Button: DISCONNECT clicked');
      parent.postMessage({ pluginMessage: { type: 'DISCONNECT_MCP' } }, '*');
      showToast('Disconnecting...');
    };
  }
}

/**
 * Get metadata content for Apply modal
 */
function getMetadataContentForApply() {
  // First check state.generated (most reliable)
  if (state.generated) {
    return state.generated.formattedDescription
      || state.generated.formattedForFigma
      || JSON.stringify(state.generated, null, 2);
  }
  // Fallback to DOM element
  const generatedMetaEl = $('generatedMeta');
  const content = generatedMetaEl?.textContent;
  if (content && content !== '// Run generate to get metadata') {
    return content;
  }
  return null;
}

/**
 * Initialize modal handlers
 */
function initModalHandlers() {
  // Metadata approval modal - Apply button in Review tab
  if ($('applyMetaBtn')) {
    $('applyMetaBtn').onclick = () => {
      const metaContent = getMetadataContentForApply();
      console.log('[UI] Button: APPLY_TO_FIGMA clicked, has content:', !!metaContent, 'state.generated:', !!state.generated);
      if (metaContent) {
        console.log('[UI] Opening approval modal');
        const modalPreview = $('modalMetaPreview');
        const modal = $('metadataApprovalModal');
        if (modalPreview) modalPreview.textContent = metaContent;
        if (modal) modal.style.display = 'flex';
      } else {
        console.log('[UI] No metadata to apply - state.generated is null');
        showToast('No generated metadata to apply. Run the pipeline first.');
      }
    };
  }

  // Apply button in Metadata tab
  if ($('applyMetaBtnMeta')) {
    $('applyMetaBtnMeta').onclick = () => {
      const metaContent = getMetadataContentForApply();
      console.log('[UI] Button: APPLY_TO_FIGMA (from Metadata tab) clicked, has content:', !!metaContent, 'state.generated:', !!state.generated);
      if (metaContent) {
        console.log('[UI] Opening approval modal');
        const modalPreview = $('modalMetaPreview');
        const modal = $('metadataApprovalModal');
        if (modalPreview) modalPreview.textContent = metaContent;
        if (modal) modal.style.display = 'flex';
      } else {
        console.log('[UI] No metadata to apply - state.generated is null');
        showToast('No generated metadata to apply. Run the pipeline first.');
      }
    };
  }

  // Cancel apply button
  if ($('cancelApplyBtn')) {
    $('cancelApplyBtn').onclick = () => {
      console.log('[UI] Button: CANCEL_APPLY clicked');
      const modal = $('metadataApprovalModal');
      if (modal) modal.style.display = 'none';
    };
  }

  // Confirm apply button
  if ($('confirmApplyBtn')) {
    $('confirmApplyBtn').onclick = () => {
      console.log('[UI] Button: CONFIRM_APPLY clicked - sending APPLY_METADATA_TO_FIGMA');
      const modal = $('metadataApprovalModal');
      if (modal) modal.style.display = 'none';
      parent.postMessage({ pluginMessage: { type: 'APPLY_METADATA_TO_FIGMA' } }, '*');
    };
  }

  // Component switch confirmation modal - Cancel
  if ($('cancelSwitchBtn')) {
    $('cancelSwitchBtn').onclick = () => {
      console.log('[UI] Button: KEEP_CURRENT clicked - staying with current component');
      const switchModal = $('componentSwitchModal');
      if (switchModal) switchModal.style.display = 'none';
      setAwaitingConfirmation(false); // Modal is closed, allow new confirmations
      setPendingNode(null);
      // Tell Figma to re-select the current node (restore selection)
      if (state.node?.nodeId) {
        parent.postMessage({
          pluginMessage: { type: 'SELECT_NODE', nodeId: state.node.nodeId }
        }, '*');
      }
    };
  }

  // Component switch confirmation modal - Confirm
  if ($('confirmSwitchBtn')) {
    $('confirmSwitchBtn').onclick = () => {
      console.log('[UI] Button: SWITCH_COMPONENT clicked - switching to new component');
      const switchModal = $('componentSwitchModal');
      if (switchModal) switchModal.style.display = 'none';
      setAwaitingConfirmation(false); // Modal is closed, allow new confirmations
      // Mark the old node so stale events for it are ignored
      setJustSwitchedFrom(state.node);
      // Clear the old data and apply the pending selection
      clearAnalysisData();
      if (pendingNode) {
        applySelection(pendingNode);
        setPendingNode(null);
      }
    };
  }
}

/**
 * Initialize "Go to" button handler (event delegation)
 */
function initGotoHandler() {
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.goto-btn');
    if (btn) {
      const nodeId = btn.dataset.nodeId;
      if (nodeId) {
        console.log('[UI] Go to node:', nodeId);
        parent.postMessage({
          pluginMessage: { type: 'SELECT_NODE', nodeId: nodeId }
        }, '*');
      }
    }
  });
}
