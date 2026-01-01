/**
 * Audit Rendering Module
 * Handles audit results display
 */

import { state, $ } from '../state.js';
import { t } from '../utils/i18n.js';
import { renderIssuesBySeverity } from './issues.js';
import { updateExport } from './export.js';

/**
 * Update audit display with results
 * @param {Object} audit - Audit results object
 * @param {boolean} skipScoreUpdate - If true, don't update state.score (used when pipeline has already set combined score)
 */
export function updateAudit(audit, skipScoreUpdate = false) {
  console.log('[UI] updateAudit called with:', JSON.stringify(audit).substring(0, 300));
  console.log('[UI] audit.score:', audit.score, 'audit.categories:', audit.categories);
  state.audit = audit;

  // Only update state.score if not called from pipeline (pipeline sets combined score)
  const auditScore = audit.scores?.overall || audit.score || 0;
  if (!skipScoreUpdate) {
    state.score = auditScore;
  }
  console.log('[UI] Audit score:', auditScore, 'State score:', state.score, 'Skip update:', skipScoreUpdate);

  const auditScoreEl = $('auditScore');
  const scoreBarFillEl = $('scoreBarFill');
  // Display the audit score in the audit section (not the combined score)
  if (auditScoreEl) auditScoreEl.textContent = auditScore;
  if (scoreBarFillEl) {
    scoreBarFillEl.style.width = auditScore + '%';
    scoreBarFillEl.className = 'score-bar-fill ' + (auditScore >= 80 ? 'high' : auditScore >= 60 ? 'medium' : 'low');
  }

  // Issues - grouped by severity
  const issues = audit.issues || [];

  // Update status based on actual issue count
  const scoreStatusEl = $('scoreStatus');
  if (scoreStatusEl) {
    if (issues.length === 0) {
      scoreStatusEl.textContent = t('status.ready');
      scoreStatusEl.className = 'score-status ready';
    } else {
      scoreStatusEl.textContent = t('status.issuesToFix', { count: issues.length });
      scoreStatusEl.className = 'score-status not-ready';
    }
  }
  const issueCountEl = $('issueCount');
  const issuesListEl = $('issuesList');
  if (issueCountEl) issueCountEl.textContent = issues.length;
  if (issuesListEl) issuesListEl.innerHTML = renderIssuesBySeverity(issues);

  updateExport();
}
