/**
 * Pipeline Rendering Module
 * Handles pipeline progress and results display
 */

import { state, $ } from '../state.js';
import { t } from '../utils/i18n.js';
import { escapeHtml } from '../utils/sanitize.js';
import { MIN_EXPORT_SCORE } from '../utils/constants.js';
import { renderIssuesBySeverity } from './issues.js';
import { updateAudit } from './audit.js';
import { updateMetadata } from './metadata.js';
import { updateGenerated } from './generated.js';
import { updateReport } from './report.js';

/**
 * Update pipeline step status
 * @param {string} stepId - Step identifier (audit, metadata, generate, report)
 * @param {string} status - Status (idle, waiting, running, done, error)
 * @param {string|null} detail - Optional detail message
 */
export function updatePipelineStep(stepId, status, detail = null) {
  const step = $('step-' + stepId);
  if (!step) return;

  // Remove all status classes
  step.classList.remove('idle', 'waiting', 'running', 'done', 'error');
  step.classList.add(status);

  const statusEl = step.querySelector('.step-status');

  switch(status) {
    case 'idle':
      statusEl.innerHTML = t('pipeline.status.idle');
      break;
    case 'waiting':
      statusEl.innerHTML = t('pipeline.status.waiting');
      break;
    case 'running':
      statusEl.innerHTML = `<span class="mini-spinner"></span>${t('pipeline.status.running.' + stepId)}`;
      break;
    case 'done':
      if (detail) {
        statusEl.innerHTML = '✓ ' + detail;
      } else {
        statusEl.innerHTML = '✓ ' + t('pipeline.status.done.' + stepId);
      }
      break;
    case 'error':
      statusEl.innerHTML = '✗ ' + t('pipeline.status.error');
      break;
  }
}

/**
 * Show pipeline progress UI
 */
export function showPipelineProgress() {
  const progress = $('pipelineProgress');
  if (progress) {
    progress.style.display = 'block';
    // Reset all steps to idle
    ['audit', 'metadata', 'generate', 'report'].forEach(s => updatePipelineStep(s, 'idle'));
  }
}

/**
 * Hide pipeline progress UI
 */
export function hidePipelineProgress() {
  const progress = $('pipelineProgress');
  if (progress) progress.style.display = 'none';
}

/**
 * Update pipeline results after completion
 * @param {Object} results - Pipeline results object
 */
export function updatePipelineResults(results) {
  // Hide progress, show results
  hidePipelineProgress();

  // CRITICAL: Calculate and update state.score BEFORE calling update functions
  // This ensures updateExport() in audit/metadata/report uses the correct combined score
  const auditRawScore = results.audit?.score ?? 0;  // Raw style guide score
  const metadataRawScore = results.metadata?.completenessScore ?? results.audit?.metadataCompletenessScore ?? 0;
  const overallScore = results.report?.overallScore ?? results.audit?.combinedScore ?? 0;
  const exportReady = results.exportReady || overallScore >= MIN_EXPORT_SCORE;

  // Update state with combined score for export button BEFORE update calls
  state.score = overallScore;
  state.exportReady = exportReady;
  console.log('[UI] 📊 State score set to combined:', overallScore, 'Export ready:', exportReady);

  // NOW update all sections with pipeline results (they will use the correct state.score)
  // Pass skipScoreUpdate=true to updateAudit so it doesn't overwrite the combined score
  if (results.audit) updateAudit(results.audit, true);
  if (results.metadata) updateMetadata(results.metadata);
  if (results.generated) updateGenerated(results.generated);
  if (results.report) updateReport(results.report);

  // Show results in review tab
  const issues = results.audit?.issues || [];
  const componentName = escapeHtml(state.node?.name || results.audit?.componentName || 'Component');

  // Calculate weighted contributions for display
  const auditContribution = (auditRawScore * 0.7).toFixed(1);
  const metadataContribution = (metadataRawScore * 0.3).toFixed(1);

  // Phase summary data - showing raw scores with weighted contributions
  const phases = [
    {
      name: t('phase.audit'),
      icon: '🔍',
      status: results.audit ? 'complete' : 'pending',
      detail: results.audit ? `${auditRawScore}/100 (×70% = ${auditContribution})` : '--'
    },
    {
      name: t('phase.metadata'),
      icon: '📋',
      status: results.metadata ? 'complete' : 'pending',
      detail: results.metadata ? `${metadataRawScore}/100 (×30% = ${metadataContribution})` : '--'
    },
    {
      name: t('phase.generate'),
      icon: '✨',
      status: results.generated ? 'complete' : 'pending',
      detail: results.generated ? t('phase.ready') : '--'
    },
    {
      name: t('phase.report'),
      icon: '📊',
      status: results.report ? 'complete' : 'pending',
      detail: results.report ? `${t('phase.combined')}: ${overallScore}/100` : '--'
    }
  ];

  const resultsHtml = `
    <div class="score-card" style="margin-bottom: 16px;">
      <div class="score-value" style="font-size: 48px; color: ${exportReady ? 'var(--success)' : overallScore >= 60 ? 'var(--warning)' : 'var(--error)'};">${overallScore}</div>
      <div class="score-label">${t('score.overall')}</div>
      <div class="export-status" style="margin-top: 8px; padding: 6px 12px; border-radius: 12px; font-size: 11px; font-weight: 600; display: inline-block; ${exportReady ? 'background: #dcfce7; color: #166534;' : 'background: #fef3c7; color: #92400e;'}">
        ${exportReady ? '✅ ' + t('status.ready') : '⚠️ ' + t('status.notReady')}
      </div>
    </div>

    <div class="phases-summary" style="background: var(--gray-200); border-radius: 8px; padding: 12px; margin-bottom: 16px;">
      <div style="font-weight: 600; font-size: 11px; color: var(--gray-700); margin-bottom: 10px;">${t('phase.summary')}</div>
      ${phases.map(p => `
        <div class="phase-row" style="display: flex; align-items: center; gap: 8px; padding: 6px 0; border-bottom: 1px solid var(--gray-200);">
          <span style="font-size: 14px;">${p.icon}</span>
          <span style="flex: 1; font-size: 11px; color: var(--gray-700);">${p.name}</span>
          <span style="font-size: 10px; color: ${p.status === 'complete' ? 'var(--success)' : 'var(--gray-400)'};">${p.status === 'complete' ? '✓' : '○'}</span>
          <span style="font-size: 10px; color: var(--gray-900); min-width: 60px; text-align: right;">${p.detail}</span>
        </div>
      `).join('')}
    </div>

    <div class="issues-section">
      <div class="issues-header">${t('issues.title')} <span class="count">${issues.length}</span></div>
      ${renderIssuesBySeverity(issues, componentName)}
    </div>
  `;
  const reviewResultsEl = $('reviewResults');
  if (reviewResultsEl) {
    reviewResultsEl.innerHTML = resultsHtml;
  }

  // Hide the top selection panel since we now show component info in the results
  const reviewSelectionPanel = $('reviewSelectionPanel');
  if (reviewSelectionPanel) {
    reviewSelectionPanel.style.display = 'none';
  }
}
