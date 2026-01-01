/**
 * Export Rendering Module
 * Handles export UI state and display
 */

import { state, $ } from '../state.js';
import { t } from '../utils/i18n.js';
import { escapeHtml } from '../utils/sanitize.js';
import { MIN_EXPORT_SCORE } from '../utils/constants.js';
import { getLevelDisplay, updateExportFiles } from '../utils/component.js';

/**
 * Update export tab state and display
 */
export function updateExport() {
  const score = state.score || 0;
  // MIN_EXPORT_SCORE imported from constants.js
  state.exportReady = score >= MIN_EXPORT_SCORE;

  const exportTabEl = $('exportTab');
  const blockedStateEl = $('blockedState');
  const readyStateEl = $('readyState');
  const exportAIDBtn = $('exportAIDBtn');

  // Always show export details (user can see what will be exported even if blocked)
  if (readyStateEl) readyStateEl.style.display = 'block';

  // Update component info (always visible)
  const componentName = state.node?.name || 'Component';
  const exportCompNameEl = $('exportComponentName');
  if (exportCompNameEl) exportCompNameEl.textContent = componentName;

  // Get level from SERVER response (single source of truth)
  // Classification logic is on the server - UI only displays
  const level = state.audit?.level || 'molecule';
  const levelDisplay = getLevelDisplay(level);
  const levelIconEl = $('levelIcon');
  const levelTextEl = $('levelText');
  const levelBadgeEl = $('levelBadge');
  if (levelIconEl) levelIconEl.textContent = levelDisplay.icon;
  if (levelTextEl) levelTextEl.textContent = t('export.level.' + level);
  if (levelBadgeEl) {
    levelBadgeEl.style.background = levelDisplay.color;
    levelBadgeEl.style.color = levelDisplay.textColor;
  }

  // Update score display (always visible)
  const exportScoreEl = $('exportScore');
  if (exportScoreEl) exportScoreEl.textContent = score + '/100';
  const scoreStatusEl = $('exportScoreStatus');
  if (scoreStatusEl) {
    if (score >= 90) {
      scoreStatusEl.textContent = '✅ Excellent';
      scoreStatusEl.style.background = '#dcfce7';
      scoreStatusEl.style.color = '#166534';
    } else if (score >= 80) {
      scoreStatusEl.textContent = '⚠️ Good (need 90+ to export)';
      scoreStatusEl.style.background = '#fef3c7';
      scoreStatusEl.style.color = '#92400e';
    } else {
      scoreStatusEl.textContent = '❌ Needs improvement';
      scoreStatusEl.style.background = '#fee2e2';
      scoreStatusEl.style.color = '#991b1b';
    }
  }

  // Get destination path from SERVER response (single source of truth)
  const exportDestEl = $('exportDestination');
  if (exportDestEl) exportDestEl.textContent = state.audit?.destinationPath || `src/components/molecules/${componentName}/`;

  // Update file list (always visible)
  updateExportFiles(componentName);

  if (state.exportReady) {
    // Score >= 90: Enable export
    if (exportTabEl) exportTabEl.classList.remove('disabled');
    if (blockedStateEl) blockedStateEl.style.display = 'none';
    if (exportAIDBtn) {
      exportAIDBtn.disabled = false;
      exportAIDBtn.classList.remove('disabled');
    }
  } else {
    // Score < 90: Show blocker banner but keep data visible
    if (exportTabEl) exportTabEl.classList.add('disabled');
    if (blockedStateEl) blockedStateEl.style.display = 'block';
    if (exportAIDBtn) {
      exportAIDBtn.disabled = true;
      exportAIDBtn.classList.add('disabled');
    }
    const pointsNeededEl = $('pointsNeeded');
    if (pointsNeededEl) pointsNeededEl.textContent = t('status.pointsNeeded', { points: MIN_EXPORT_SCORE - score });

    // Show blockers if available
    const blockersEl = $('blockersList');
    if (blockersEl && state.audit?.issues) {
      const criticalIssues = state.audit.issues.filter(i => i.severity === 'error');
      if (criticalIssues.length > 0) {
        blockersEl.innerHTML = criticalIssues.slice(0, 3).map(i =>
          `<div style="color: var(--error); margin-bottom: 4px;">• ${escapeHtml(i.message)}</div>`
        ).join('');
      }
    }
  }
}
