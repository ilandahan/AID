/**
 * Message Handlers Module
 * Handles messages from Figma plugin
 */

import { state, $, updateMcpButtons } from '../state.js';
import { t } from '../utils/i18n.js';
import { showToast } from '../utils/toast.js';
import { countGeneratedFields, displayActualFiles } from '../utils/component.js';
import { VALID_MESSAGE_TYPES } from '../utils/constants.js';
import { updateSelection } from '../rendering/selection.js';
import { updateAudit } from '../rendering/audit.js';
import { updateMetadata } from '../rendering/metadata.js';
import { updateGenerated } from '../rendering/generated.js';
import { updateReport } from '../rendering/report.js';
import { updatePipelineStep, updatePipelineResults } from '../rendering/pipeline.js';
import { updateStatus, hideOverlay, clearOtpInputs } from './pairing.js';

/**
 * Initialize message handler
 */
export function initMessageHandler() {
  window.onmessage = (e) => {
    const msg = e.data.pluginMessage;
    if (!msg) return;

    // Validate message type to prevent processing malformed messages
    if (!msg.type || typeof msg.type !== 'string') {
      console.warn('[UI] Received message with invalid type:', msg.type);
      return;
    }

    if (!VALID_MESSAGE_TYPES.includes(msg.type)) {
      console.warn('[UI] Received unknown message type:', msg.type);
      return;
    }

    console.log('[UI] Received message:', msg.type);

    switch (msg.type) {
      case 'SELECTION_CHANGED':
        handleSelectionChanged(msg);
        break;
      case 'AUDIT_COMPLETE':
        handleAuditComplete(msg);
        break;
      case 'METADATA_ANALYZED':
        handleMetadataAnalyzed(msg);
        break;
      case 'METADATA_GENERATED':
        handleMetadataGenerated(msg);
        break;
      case 'METADATA_APPLIED':
        handleMetadataApplied(msg);
        break;
      case 'METADATA_APPLY_FAILED':
        handleMetadataApplyFailed(msg);
        break;
      case 'REPORT_READY':
        handleReportReady(msg);
        break;
      case 'PIPELINE_COMPLETE':
        handlePipelineComplete(msg);
        break;
      case 'PIPELINE_STEP':
        handlePipelineStep(msg);
        break;
      case 'MCP_CONNECTED':
        handleMcpConnected(msg);
        break;
      case 'MCP_DISCONNECTED':
        handleMcpDisconnected(msg);
        break;
      case 'AID_CONNECTED':
        handleAidConnected(msg);
        break;
      case 'AID_PAIRED':
        handleAidPaired(msg);
        break;
      case 'AID_PAIR_FAILED':
        handleAidPairFailed(msg);
        break;
      case 'EXPORT_SUCCESS':
        handleExportSuccess(msg);
        break;
      case 'CONTENT_EXPORTED':
        handleContentExported(msg);
        break;
      case 'ERROR':
        handleError(msg);
        break;
    }
  };
}

function handleSelectionChanged(msg) {
  console.log('═══════════════════════════════════════════════════════════════════');
  console.log('[UI] 🎯 COMPONENT SELECTED');
  console.log('═══════════════════════════════════════════════════════════════════');
  console.log('[UI] Name:', msg.node?.name || 'None');
  console.log('[UI] Type:', msg.node?.type || 'Unknown');
  console.log('[UI] Node ID:', msg.node?.nodeId || msg.node?.id || 'N/A');
  console.log('[UI] Variants:', msg.node?.variantCount || 0);
  console.log('[UI] Children:', msg.node?.childCount || 0);
  console.log('───────────────────────────────────────────────────────────────────');
  updateSelection(msg.node);
}

function handleAuditComplete(msg) {
  console.log('[UI] ✅ Audit complete - Score:', msg.audit?.score, 'Combined:', msg.audit?.combinedScore);
  updateAudit(msg.audit);
  showToast(t('notify.auditComplete'));
}

function handleMetadataAnalyzed(msg) {
  console.log('[UI] 📋 Metadata analyzed - Completeness:', msg.metadata?.completenessScore + '%');
  updateMetadata(msg.metadata);
  showToast(t('notify.analysisComplete'));
}

function handleMetadataGenerated(msg) {
  console.log('[UI] ✨ Metadata generated - Has formatted:', !!msg.generated?.formattedDescription);
  updateGenerated(msg.generated);
  // Show the apply button when metadata is generated
  const applyBtnGen = $('applyMetaBtn');
  if (applyBtnGen) applyBtnGen.style.display = 'flex';
  showToast(t('notify.generated'));
}

function handleMetadataApplied(msg) {
  console.log('═══════════════════════════════════════════════════════════════════');
  console.log('[UI] ✅ METADATA SUCCESSFULLY APPLIED TO FIGMA');
  console.log('═══════════════════════════════════════════════════════════════════');
  console.log('[UI] Component:', state.node?.name || 'Unknown');
  console.log('[UI] Fields applied:', countGeneratedFields(state.generated, state.metadata));
  console.log('[UI] Validation passed:', msg.validationPassed !== false);
  console.log('───────────────────────────────────────────────────────────────────');

  // IMPORTANT: Clear state.generated after successful apply
  // This ensures re-running the pipeline shows data as "existing" not "generated"
  state.generated = null;
  console.log('[UI] 🔄 Cleared state.generated - next analysis will show applied data as existing');

  // Hide the Apply buttons since metadata is now applied
  const applyBtnApplied = $('applyMetaBtn');
  const applyBtnMetaApplied = $('applyMetaBtnMeta');
  if (applyBtnApplied) applyBtnApplied.style.display = 'none';
  if (applyBtnMetaApplied) applyBtnMetaApplied.style.display = 'none';

  // Close the approval modal if it's open
  const modal = $('metadataApprovalModal');
  if (modal) modal.style.display = 'none';

  if (msg.validationPassed === false) {
    // Show warning with manual copy suggestion
    console.warn('[UI] ⚠️ Validation mismatch - Applied:', msg.appliedLength, 'vs Expected:', msg.expectedLength);
    showToast('⚠️ Applied with slight difference. If incorrect, copy manually from Metadata tab.');
  } else {
    showToast('✅ ' + t('status.metadataApplied') + ' - Re-run to see applied data');
  }
}

function handleMetadataApplyFailed(msg) {
  console.log('═══════════════════════════════════════════════════════════════════');
  console.log('[UI] ❌ METADATA APPLICATION FAILED');
  console.log('═══════════════════════════════════════════════════════════════════');
  console.log('[UI] Error:', msg.error);
  console.log('───────────────────────────────────────────────────────────────────');
  showToast(t('status.applyFailed') + ': ' + (msg.error || ''));
}

function handleReportReady(msg) {
  console.log('[UI] Report ready, overall score:', msg.report?.overallScore);
  updateReport(msg.report);
  showToast(t('notify.reportReady'));
}

function handlePipelineComplete(msg) {
  console.log('[UI] Pipeline complete, results:', msg.results);
  const pipelineBtnComplete = $('runPipelineBtn');
  if (pipelineBtnComplete) pipelineBtnComplete.classList.remove('loading');
  updatePipelineResults(msg.results);
  showToast(t('notify.pipelineComplete'));
}

function handlePipelineStep(msg) {
  console.log('[UI] Pipeline step:', msg.step, msg.status, msg.detail);
  const { step, status, detail } = msg;
  updatePipelineStep(step, status, detail);
}

function handleMcpConnected(msg) {
  console.log('[UI] MCP connected');
  state.connected = true;

  const connDotConnect = $('connectionDot');
  if (connDotConnect) {
    connDotConnect.classList.remove('error', 'reconnecting');
    connDotConnect.classList.add('connected');
    connDotConnect.title = t('notify.connected');
  }

  // Show disconnect button when connected
  const disconnectBtn = $('disconnectBtn');
  if (disconnectBtn) {
    disconnectBtn.classList.add('show');
  }

  // Hide connection banner if showing
  const connBanner = $('connectionBanner');
  if (connBanner) {
    connBanner.classList.remove('show', 'reconnecting');
  }

  // Enable MCP-required buttons if a component is selected
  updateMcpButtons();
}

function handleMcpDisconnected(msg) {
  console.log('[UI] MCP disconnected');
  state.connected = false;

  const connDotDisconnect = $('connectionDot');
  if (connDotDisconnect) {
    connDotDisconnect.classList.remove('connected', 'reconnecting');
    connDotDisconnect.classList.add('error');
    connDotDisconnect.title = t('notify.disconnected') || 'Disconnected';
  }

  // Hide disconnect button when not connected
  const disconnectBtn = $('disconnectBtn');
  if (disconnectBtn) {
    disconnectBtn.classList.remove('show');
  }

  // Show connection lost banner
  const connBanner = $('connectionBanner');
  if (connBanner) {
    connBanner.textContent = t('notify.connectionLost') || 'Connection lost. Please reconnect.';
    connBanner.classList.add('show', 'reconnecting');
  }

  // Show the MCP status card again for reconnection
  const mcpStatusCard = $('mcpStatusCard');
  if (mcpStatusCard) {
    const mcpStatusTitle = $('mcpStatusTitle');
    const mcpStatusMessage = $('mcpStatusMessage');
    if (mcpStatusTitle) mcpStatusTitle.textContent = t('mcp.disconnected') || 'Connection Lost';
    if (mcpStatusMessage) mcpStatusMessage.textContent = t('mcp.reconnect') || 'Click to reconnect...';
    mcpStatusCard.classList.add('show');
    mcpStatusCard.style.display = 'block';
  }

  // Disable MCP-required buttons
  updateMcpButtons();

  // Show toast notification
  showToast('🔌 ' + (t('notify.connectionLost') || 'Connection lost'));
}

function handleAidConnected(msg) {
  console.log('[UI] 🔗 AID Connected');

  // Update connection state
  state.connected = true;

  // Hide the MCP status card (spinner)
  const mcpStatusCard = $('mcpStatusCard');
  if (mcpStatusCard) {
    mcpStatusCard.classList.remove('show');
    mcpStatusCard.style.display = 'none';
  }

  // Show connection dot as connected
  const connDot = $('connectionDot');
  if (connDot) {
    connDot.classList.remove('error', 'reconnecting');
    connDot.classList.add('connected');
    connDot.title = t('notify.connected') || 'Connected to AI.D';
  }

  // Show disconnect button when connected
  const disconnectBtn = $('disconnectBtn');
  if (disconnectBtn) {
    disconnectBtn.classList.add('show');
  }

  // Hide connection banner if showing
  const connBanner = $('connectionBanner');
  if (connBanner) {
    connBanner.classList.remove('show', 'reconnecting');
  }

  // Enable MCP-required buttons if a component is selected
  updateMcpButtons();

  showToast('✅ Connected to AI.D');
}

/**
 * Handle successful pairing from pairWithAID()
 * This is the response from the plugin after completing the full auth flow
 */
function handleAidPaired(msg) {
  console.log('[UI] ✅ AID Paired successfully');

  // Update connection state
  state.connected = true;

  // Update pairing UI
  updateStatus('paired', t('pairing.success') || 'Connected to AI.D');
  hideOverlay();

  // Hide spinner if visible
  const mcpStatusCard = $('mcpStatusCard');
  if (mcpStatusCard) {
    mcpStatusCard.classList.remove('show');
    mcpStatusCard.style.display = 'none';
  }

  // Show connection dot as connected
  const connDot = $('connectionDot');
  if (connDot) {
    connDot.classList.remove('error', 'reconnecting');
    connDot.classList.add('connected');
    connDot.title = t('notify.connected') || 'Connected to AI.D';
  }

  // Show disconnect button when connected
  const disconnectBtn = $('disconnectBtn');
  if (disconnectBtn) {
    disconnectBtn.classList.add('show');
  }

  // Hide connection banner if showing
  const connBanner = $('connectionBanner');
  if (connBanner) {
    connBanner.classList.remove('show', 'reconnecting');
  }

  // Enable MCP-required buttons if a component is selected
  updateMcpButtons();

  showToast('✅ ' + (t('pairing.success') || 'Connected to AI.D'));
}

/**
 * Handle failed pairing from pairWithAID()
 */
function handleAidPairFailed(msg) {
  console.log('[UI] ❌ AID Pairing failed:', msg.error);

  // Update pairing UI with error
  updateStatus('error', msg.error || t('pairing.failed') || 'Connection failed');

  // Clear OTP inputs so user can try again
  clearOtpInputs();

  showToast('❌ ' + (msg.error || t('pairing.failed') || 'Pairing failed'));
}

function handleExportSuccess(msg) {
  console.log('═══════════════════════════════════════════════════════════════════');
  console.log('[UI] ✅ EXPORT SUCCESSFUL');
  console.log('═══════════════════════════════════════════════════════════════════');
  console.log('[UI] Format:', msg.format);
  console.log('[UI] Files:', msg.files);
  console.log('[UI] Component Dir:', msg.componentDir);
  console.log('[UI] Is Cloud Export:', msg.isCloudExport);
  console.log('[UI] ZIP Base64:', msg.zipBase64 ? `present (${msg.zipBase64.length} chars)` : 'none');
  console.log('───────────────────────────────────────────────────────────────────');

  // Update the UI with actual files from server response
  if (msg.files && msg.files.length > 0) {
    displayActualFiles(msg.files, msg.componentDir);
  }

  // Handle cloud exports - show ZIP download modal
  if (msg.isCloudExport && msg.zipBase64) {
    console.log('[UI] 📦 Cloud export detected - showing download modal');
    showZipDownloadModal(msg);
  } else {
    showToast(`✅ Exported to ${msg.format || 'AID'} successfully!`);
  }
}

/**
 * Handle cloud export - create downloadable zip or individual files
 */
function handleCloudExportDownload(msg) {
  const { fileContents, componentName, relativePath, files } = msg;
  const fileCount = Object.keys(fileContents).length;

  console.log(`[UI] 📦 Preparing ${fileCount} files for download`);
  console.log('[UI] Component:', componentName);
  console.log('[UI] Relative path:', relativePath);

  // Create a combined file for easy download (all files in one text file)
  let combinedContent = `// ═══════════════════════════════════════════════════════════════════
// ${componentName} - Exported from Figma
// Path: ${relativePath}
// Files: ${files.join(', ')}
// Generated: ${new Date().toISOString()}
// ═══════════════════════════════════════════════════════════════════

`;

  // Add each file's content
  for (const [filename, content] of Object.entries(fileContents)) {
    combinedContent += `
// ─────────────────────────────────────────────────────────────────────
// FILE: ${filename}
// ─────────────────────────────────────────────────────────────────────
${content}

`;
  }

  // Copy to clipboard for easy pasting
  if (navigator.clipboard) {
    navigator.clipboard.writeText(combinedContent).then(() => {
      console.log('[UI] ✅ All files copied to clipboard');
      showToast(`✅ ${fileCount} files copied to clipboard! Paste into your project.`);
    }).catch(err => {
      console.error('[UI] Clipboard error:', err);
      // Fallback: trigger download
      triggerFileDownload(combinedContent, `${componentName}-export.txt`);
      showToast(`✅ Exported ${fileCount} files - downloading...`);
    });
  } else {
    // Fallback: trigger download
    triggerFileDownload(combinedContent, `${componentName}-export.txt`);
    showToast(`✅ Exported ${fileCount} files - downloading...`);
  }

  // Also show a modal with individual file download options
  showExportDownloadModal(fileContents, componentName, relativePath);
}

/**
 * Trigger a file download in the browser
 */
function triggerFileDownload(content, filename) {
  const blob = new Blob([content], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * Show modal with download options for exported files
 */
function showExportDownloadModal(fileContents, componentName, relativePath) {
  // Check if modal already exists, create if not
  let modal = document.getElementById('exportDownloadModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'exportDownloadModal';
    modal.className = 'modal-overlay';
    modal.innerHTML = `
      <div class="modal-content" style="max-width: 500px; max-height: 80vh; overflow: auto;">
        <h3 style="margin-bottom: 16px;">📦 Export Complete</h3>
        <p style="font-size: 12px; color: var(--gray-700); margin-bottom: 12px;">
          Your component files are ready. All files have been copied to your clipboard.
        </p>
        <div style="background: var(--gray-100); border-radius: 8px; padding: 12px; margin-bottom: 16px;">
          <div style="font-size: 11px; color: var(--gray-500); margin-bottom: 4px;">Save to:</div>
          <code style="font-size: 12px; color: var(--gray-800);" id="exportPath"></code>
        </div>
        <div style="font-size: 12px; font-weight: 600; margin-bottom: 8px;">Files included:</div>
        <div id="exportFilesList" style="background: var(--gray-900); border-radius: 8px; padding: 12px; color: #d4d4d4; font-family: monospace; font-size: 11px; max-height: 150px; overflow-y: auto; margin-bottom: 16px;"></div>
        <div class="btn-group" style="justify-content: flex-end;">
          <button class="btn btn-secondary" id="closeExportModal">
            <span>Close</span>
          </button>
          <button class="btn btn-primary" id="downloadAllFiles">
            <span>📥</span>
            <span>Download All</span>
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    // Close button handler
    document.getElementById('closeExportModal').onclick = () => {
      modal.style.display = 'none';
    };
  }

  // Populate modal content
  document.getElementById('exportPath').textContent = relativePath || 'src/components/';

  const filesList = document.getElementById('exportFilesList');
  const files = Object.keys(fileContents);
  filesList.innerHTML = files.map((f, i) => {
    const prefix = i === files.length - 1 ? '└──' : '├──';
    return `<div>${prefix} ${f}</div>`;
  }).join('');

  // Download all button handler
  document.getElementById('downloadAllFiles').onclick = () => {
    // Create combined content
    let combinedContent = `// ${componentName} Component\n// Path: ${relativePath}\n\n`;
    for (const [filename, content] of Object.entries(fileContents)) {
      combinedContent += `// === ${filename} ===\n${content}\n\n`;
    }
    triggerFileDownload(combinedContent, `${componentName}-export.txt`);
    modal.style.display = 'none';
  };

  // Show modal
  modal.style.display = 'flex';
}

/**
 * Get atomic level info (icon, color, description)
 * Supports both singular (atom) and plural (atoms) keys
 */
function getAtomicLevelInfo(level) {
  const atomInfo = {
    icon: '⚛️',
    color: '#3b82f6', // blue
    bgColor: '#dbeafe',
    label: 'Atom',
    description: 'Basic building block (buttons, inputs, labels)'
  };
  const moleculeInfo = {
    icon: '🧬',
    color: '#10b981', // green
    bgColor: '#d1fae5',
    label: 'Molecule',
    description: 'Simple component group (form fields, cards)'
  };
  const organismInfo = {
    icon: '🦠',
    color: '#8b5cf6', // purple
    bgColor: '#ede9fe',
    label: 'Organism',
    description: 'Complex UI section (headers, forms, modals)'
  };
  const templateInfo = {
    icon: '📐',
    color: '#f59e0b', // amber
    bgColor: '#fef3c7',
    label: 'Template',
    description: 'Page layout structure'
  };
  const pageInfo = {
    icon: '📄',
    color: '#ef4444', // red
    bgColor: '#fee2e2',
    label: 'Page',
    description: 'Complete page with real content'
  };

  // Support both singular and plural keys
  const levels = {
    atom: atomInfo, atoms: atomInfo,
    molecule: moleculeInfo, molecules: moleculeInfo,
    organism: organismInfo, organisms: organismInfo,
    template: templateInfo, templates: templateInfo,
    page: pageInfo, pages: pageInfo
  };

  return levels[level] || moleculeInfo;
}

/**
 * Show modal for ZIP download from cloud server
 * ZIP data is received as base64 (avoids Cloud Run instance affinity issues)
 */
function showZipDownloadModal(msg) {
  const { zipBase64, downloadFilename, downloadSize, componentName, relativePath, files } = msg;

  // Convert base64 to blob URL for download
  const byteCharacters = atob(zipBase64);
  const byteNumbers = new Array(byteCharacters.length);
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  const byteArray = new Uint8Array(byteNumbers);
  const blob = new Blob([byteArray], { type: 'application/zip' });
  const downloadUrl = URL.createObjectURL(blob);

  // Extract level from relativePath (format: components/{level}/{componentName})
  const pathParts = (relativePath || '').split('/');
  const level = pathParts[1] || 'molecules';
  const levelInfo = getAtomicLevelInfo(level);

  console.log('[UI] 📦 Preparing ZIP download modal');
  console.log('[UI] Download URL:', downloadUrl);
  console.log('[UI] Filename:', downloadFilename);
  console.log('[UI] Size:', downloadSize, 'bytes');
  console.log('[UI] Atomic Level:', level);

  // Format file size
  const formatSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  // Check if modal already exists, create if not
  let modal = document.getElementById('zipDownloadModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'zipDownloadModal';
    modal.className = 'modal-overlay';
    modal.innerHTML = `
      <div class="modal-content" style="max-width: 480px;">
        <div style="text-align: center; margin-bottom: 16px;">
          <div style="font-size: 48px; margin-bottom: 8px;">📦</div>
          <h3 style="margin: 0; font-size: 18px;">Component Ready!</h3>
        </div>

        <!-- Atomic Level Badge -->
        <div id="zipLevelBadge" style="display: flex; align-items: center; gap: 12px; padding: 12px 16px; border-radius: 8px; margin-bottom: 16px;">
          <span id="zipLevelIcon" style="font-size: 28px;"></span>
          <div style="flex: 1;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span id="zipLevelLabel" style="font-weight: 700; font-size: 14px;"></span>
              <span style="font-size: 11px; opacity: 0.7;" id="zipFileSize"></span>
            </div>
            <div id="zipLevelDesc" style="font-size: 11px; opacity: 0.8;"></div>
          </div>
        </div>

        <!-- Component Info -->
        <div style="background: var(--gray-100); border-radius: 8px; padding: 12px 16px; margin-bottom: 16px;">
          <div style="font-weight: 600; color: var(--gray-800); margin-bottom: 8px;" id="zipComponentName"></div>

          <!-- Directory Tree -->
          <div style="font-size: 11px; font-family: monospace; color: var(--gray-600); background: var(--gray-200); border-radius: 6px; padding: 10px;">
            <div style="color: var(--gray-500);">📁 src/</div>
            <div style="padding-left: 16px; color: var(--gray-500);">📁 components/</div>
            <div id="zipDirTree" style="padding-left: 32px;"></div>
          </div>
        </div>

        <div style="font-size: 12px; font-weight: 600; margin-bottom: 8px; color: var(--gray-700);">Files included:</div>
        <div id="zipFilesList" style="background: var(--gray-900); border-radius: 8px; padding: 12px; color: #10b981; font-family: monospace; font-size: 11px; max-height: 100px; overflow-y: auto; margin-bottom: 16px;"></div>

        <div style="display: flex; gap: 12px;">
          <button class="btn btn-secondary" id="closeZipModal" style="flex: 1;">
            <span>Close</span>
          </button>
          <a id="zipDownloadLink" class="btn btn-primary" style="flex: 2; text-decoration: none; display: flex; align-items: center; justify-content: center; gap: 8px;" download>
            <span>⬇️</span>
            <span>Download ZIP</span>
          </a>
        </div>

        <p style="font-size: 10px; color: var(--gray-500); text-align: center; margin-top: 12px; margin-bottom: 0;">
          Extract the ZIP and copy the folder to the path shown above
        </p>
      </div>
    `;
    document.body.appendChild(modal);

    // Close button handler
    document.getElementById('closeZipModal').onclick = () => {
      modal.style.display = 'none';
    };

    // Close on backdrop click
    modal.onclick = (e) => {
      if (e.target === modal) {
        modal.style.display = 'none';
      }
    };
  }

  // Populate level badge
  const levelBadge = document.getElementById('zipLevelBadge');
  levelBadge.style.background = levelInfo.bgColor;
  levelBadge.style.border = `2px solid ${levelInfo.color}`;

  document.getElementById('zipLevelIcon').textContent = levelInfo.icon;

  const levelLabel = document.getElementById('zipLevelLabel');
  levelLabel.textContent = levelInfo.label;
  levelLabel.style.color = levelInfo.color;

  document.getElementById('zipLevelDesc').textContent = levelInfo.description;

  // Populate modal content
  document.getElementById('zipComponentName').textContent = componentName || 'Component';
  document.getElementById('zipFileSize').textContent = formatSize(downloadSize || 0);

  // Build directory tree
  const dirTree = document.getElementById('zipDirTree');
  dirTree.innerHTML = `
    <div style="color: ${levelInfo.color}; font-weight: 600;">📁 ${level}/</div>
    <div style="padding-left: 16px; color: ${levelInfo.color};">📁 ${componentName}/ <span style="color: var(--gray-400);">← paste here</span></div>
  `;

  // Set download link with double-click prevention
  const downloadLink = document.getElementById('zipDownloadLink');
  downloadLink.href = downloadUrl;
  downloadLink.download = downloadFilename || `${componentName}.zip`;
  downloadLink.classList.remove('downloaded'); // Reset state for new downloads
  downloadLink.innerHTML = '<span>⬇️</span><span>Download ZIP</span>';

  // Prevent double-click: disable after first click
  downloadLink.onclick = (e) => {
    if (downloadLink.classList.contains('downloaded')) {
      e.preventDefault();
      showToast('⚠️ Already downloaded! Close and export again if needed.');
      return false;
    }

    // Mark as downloaded after a short delay (allow the download to start)
    setTimeout(() => {
      downloadLink.classList.add('downloaded');
      downloadLink.innerHTML = '<span>✅</span><span>Downloaded!</span>';
      downloadLink.style.opacity = '0.6';
      downloadLink.style.cursor = 'default';

      // Clean up blob URL after download starts
      setTimeout(() => {
        URL.revokeObjectURL(downloadUrl);
        console.log('[UI] 🧹 Cleaned up blob URL');
      }, 1000);
    }, 100);
  };

  // Files list
  const filesList = document.getElementById('zipFilesList');
  const fileArray = files || [];
  filesList.innerHTML = fileArray.map((f, i) => {
    const prefix = i === fileArray.length - 1 ? '└──' : '├──';
    const icon = f.endsWith('.tsx') ? '⚛️' : f.endsWith('.css') ? '🎨' : f.endsWith('.ts') ? '📘' : f.endsWith('.json') ? '📋' : '📄';
    return `<div>${prefix} ${icon} ${f}</div>`;
  }).join('') || '<div>└── (files)</div>';

  // Show modal
  modal.style.display = 'flex';

  // Show toast notification
  showToast(`✅ ${componentName || 'Component'} (${levelInfo.label}) is ready for download!`);
}

function handleContentExported(msg) {
  console.log('[UI] 📋 Content exported:', msg.format, msg.filename);
  // Copy content to clipboard if available
  if (msg.content && navigator.clipboard) {
    navigator.clipboard.writeText(msg.content).then(() => {
      showToast(`✅ ${msg.format.toUpperCase()} copied to clipboard!`);
    }).catch(() => {
      showToast(`✅ Exported as ${msg.format.toUpperCase()}`);
    });
  } else {
    showToast(`✅ Exported as ${msg.format.toUpperCase()}`);
  }
}

function handleError(msg) {
  const pipelineBtnError = $('runPipelineBtn');
  if (pipelineBtnError) pipelineBtnError.classList.remove('loading');
  // Keep progress visible to show which step failed
  showToast(t('notify.error') + ': ' + msg.message);
}
