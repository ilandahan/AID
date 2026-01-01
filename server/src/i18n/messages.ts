/**
 * @file messages.ts
 * @description Internationalization messages for multilingual LTR/RTL support.
 * Supports English (LTR) and Hebrew (RTL).
 *
 * @related
 *   - ../tools/design-review.ts - Uses these messages in reports
 *   - ../../ui.html - UI displays localized messages
 */

export type Locale = 'en' | 'he';

export interface LocaleConfig {
  code: Locale;
  name: string;
  dir: 'ltr' | 'rtl';
  dateFormat: string;
}

export const locales: Record<Locale, LocaleConfig> = {
  en: {
    code: 'en',
    name: 'English',
    dir: 'ltr',
    dateFormat: 'MM/DD/YYYY'
  },
  he: {
    code: 'he',
    name: 'עברית',
    dir: 'rtl',
    dateFormat: 'DD/MM/YYYY'
  }
};

export const messages: Record<Locale, Record<string, string>> = {
  en: {
    // General
    'app.title': 'Atomic Design Extractor',
    'app.subtitle': 'Design Review & Quality Pipeline',

    // Tabs
    'tab.review': 'Review',
    'tab.audit': 'Audit',
    'tab.metadata': 'Metadata',
    'tab.report': 'Report',
    'tab.export': 'Export',

    // Selection
    'selection.empty': 'Select a component in Figma to begin',
    'selection.component': 'Component',
    'selection.variants': 'variants',

    // Scores
    'score.overall': 'Overall Score',
    'score.naming': 'Naming',
    'score.structure': 'Structure',
    'score.visual': 'Visual',
    'score.accessibility': 'Accessibility',
    'score.metadata': 'Metadata',

    // Export status
    'export.ready': 'Ready for export!',
    'export.blocked': 'Export blocked',
    'export.pointsNeeded': '{{points}} points needed',
    'export.minScore': 'Minimum score: 90',

    // Actions
    'action.runAudit': 'Run Audit',
    'action.sendToClaude': 'Send to Claude',
    'action.analyzeMetadata': 'Analyze Metadata',
    'action.generateAuto': 'Auto Generate',
    'action.copyMetadata': 'Copy Metadata',
    'action.regenerate': 'Regenerate',
    'action.exportAID': 'Export to AID',
    'action.exportJSON': 'Export JSON',
    'action.exportTS': 'Export TypeScript',

    // Issues
    'issues.title': 'Issues',
    'issues.blockers': 'Blockers',
    'issues.warnings': 'Warnings',
    'issues.suggestions': 'Suggestions',

    // Issue messages - Naming
    'issue.naming.wrongFormat': 'Component name should follow "Category / Type / Name" format',
    'issue.naming.nonSemantic': 'Layer "{{name}}" should have a semantic name',
    'issue.naming.typo': 'Possible typo: "{{found}}" should be "{{expected}}"',
    'issue.naming.notPascalCase': 'Variant property "{{name}}" should use PascalCase',

    // Issue messages - Structure
    'issue.structure.noAutoLayout': 'Component should use Auto Layout for responsive behavior',
    'issue.structure.unnecessaryWrapper': 'Unnecessary wrapper frame around component',
    'issue.structure.inconsistentHierarchy': 'Variant "{{variant}}" has different structure than others',

    // Issue messages - Visual
    'issue.visual.hardcodedColor': 'Color "{{color}}" is not from design system tokens',
    'issue.visual.inconsistentFontSize': 'Font sizes vary: {{sizes}}. Should be consistent.',
    'issue.visual.nonStandardSpacing': 'Spacing "{{value}}" is not from token scale',
    'issue.visual.inconsistentRadius': 'Border radius varies across variants',

    // Issue messages - Accessibility
    'issue.a11y.missingFocus': 'Missing Focus state for keyboard navigation',
    'issue.a11y.missingDisabled': 'Missing Disabled state',
    'issue.a11y.smallTouchTarget': 'Touch target is {{size}}px, should be at least 44x44px',
    'issue.a11y.noAriaLabel': 'Icon-only component needs ariaLabel for screen readers',
    'issue.a11y.lowContrast': 'Text contrast ratio is {{ratio}}, should be at least 4.5:1',

    // Issue messages - Metadata
    'issue.metadata.missingDescription': 'Missing component description',
    'issue.metadata.missingTags': 'Missing searchable tags',
    'issue.metadata.missingNotes': 'Missing usage notes',
    'issue.metadata.missingCategory': 'Missing component category',
    'issue.metadata.missingLevel': 'Missing atomic level (atom/molecule/organism)',
    'issue.metadata.missingVariantDesc': 'Variant "{{variant}}" is missing description',

    // Report
    'report.title': 'Component Quality Report',
    'report.generatedAt': 'Generated at',
    'report.component': 'Component',
    'report.type': 'Type',
    'report.variants': 'Variants',
    'report.categoryScores': 'Category Scores',
    'report.actionItems': 'Action Items',
    'report.suggestedMetadata': 'Suggested Metadata',
    'report.copyToFigma': 'Copy and paste this into Figma description',

    // Notifications
    'notify.auditComplete': 'Audit complete',
    'notify.analysisComplete': 'Analysis complete',
    'notify.metadataGenerated': 'Metadata generated',
    'notify.reportReady': 'Report ready',
    'notify.exportSuccess': 'Successfully exported!',
    'notify.copied': 'Copied to clipboard',
    'notify.error': 'Error',
    'notify.connecting': 'Connecting to Claude...',
    'notify.connected': 'Connected to MCP server',
    'notify.disconnected': 'Disconnected from MCP server',
  },

  he: {
    // General
    'app.title': 'מחלץ Atomic Design',
    'app.subtitle': 'סקירת עיצוב ובקרת איכות',

    // Tabs
    'tab.review': 'סקירה',
    'tab.audit': 'ביקורת',
    'tab.metadata': 'מטאדאטה',
    'tab.report': 'דוח',
    'tab.export': 'יצוא',

    // Selection
    'selection.empty': 'בחר קומפוננטה בפיגמה להתחלה',
    'selection.component': 'קומפוננטה',
    'selection.variants': 'וריאנטים',

    // Scores
    'score.overall': 'ציון כללי',
    'score.naming': 'שמות',
    'score.structure': 'מבנה',
    'score.visual': 'ויזואלי',
    'score.accessibility': 'נגישות',
    'score.metadata': 'מטאדאטה',

    // Export status
    'export.ready': 'מוכן ליצוא!',
    'export.blocked': 'יצוא חסום',
    'export.pointsNeeded': 'חסרות {{points}} נקודות',
    'export.minScore': 'ציון מינימלי: 90',

    // Actions
    'action.runAudit': 'הרץ ביקורת',
    'action.sendToClaude': 'שלח ל-Claude',
    'action.analyzeMetadata': 'נתח מטאדאטה',
    'action.generateAuto': 'ג׳נרט אוטומטי',
    'action.copyMetadata': 'העתק מטאדאטה',
    'action.regenerate': 'ג׳נרט מחדש',
    'action.exportAID': 'יצא ל-AID',
    'action.exportJSON': 'יצא JSON',
    'action.exportTS': 'יצא TypeScript',

    // Issues
    'issues.title': 'בעיות',
    'issues.blockers': 'חוסמים',
    'issues.warnings': 'אזהרות',
    'issues.suggestions': 'הצעות',

    // Issue messages - Naming
    'issue.naming.wrongFormat': 'שם הקומפוננטה צריך להיות בפורמט "Category / Type / Name"',
    'issue.naming.nonSemantic': 'לשכבה "{{name}}" צריך להיות שם סמנטי',
    'issue.naming.typo': 'שגיאת כתיב אפשרית: "{{found}}" צריך להיות "{{expected}}"',
    'issue.naming.notPascalCase': 'מאפיין וריאנט "{{name}}" צריך להיות ב-PascalCase',

    // Issue messages - Structure
    'issue.structure.noAutoLayout': 'הקומפוננטה צריכה להשתמש ב-Auto Layout לתגובתיות',
    'issue.structure.unnecessaryWrapper': 'פריים עוטף מיותר סביב הקומפוננטה',
    'issue.structure.inconsistentHierarchy': 'לוריאנט "{{variant}}" יש מבנה שונה מהאחרים',

    // Issue messages - Visual
    'issue.visual.hardcodedColor': 'הצבע "{{color}}" לא מה-design tokens',
    'issue.visual.inconsistentFontSize': 'גדלי גופן משתנים: {{sizes}}. צריך להיות אחיד.',
    'issue.visual.nonStandardSpacing': 'הריווח "{{value}}" לא מסקאלת הטוקנים',
    'issue.visual.inconsistentRadius': 'רדיוס הפינות משתנה בין הוריאנטים',

    // Issue messages - Accessibility
    'issue.a11y.missingFocus': 'חסר מצב Focus לניווט מקלדת',
    'issue.a11y.missingDisabled': 'חסר מצב Disabled',
    'issue.a11y.smallTouchTarget': 'אזור המגע הוא {{size}}px, צריך להיות לפחות 44x44px',
    'issue.a11y.noAriaLabel': 'קומפוננטה עם אייקון בלבד צריכה ariaLabel לקוראי מסך',
    'issue.a11y.lowContrast': 'יחס ניגודיות הטקסט הוא {{ratio}}, צריך להיות לפחות 4.5:1',

    // Issue messages - Metadata
    'issue.metadata.missingDescription': 'חסר תיאור לקומפוננטה',
    'issue.metadata.missingTags': 'חסרים תגיות לחיפוש',
    'issue.metadata.missingNotes': 'חסרות הערות שימוש',
    'issue.metadata.missingCategory': 'חסרה קטגוריית קומפוננטה',
    'issue.metadata.missingLevel': 'חסרה רמה אטומית (atom/molecule/organism)',
    'issue.metadata.missingVariantDesc': 'לוריאנט "{{variant}}" חסר תיאור',

    // Report
    'report.title': 'דוח איכות קומפוננטה',
    'report.generatedAt': 'נוצר ב',
    'report.component': 'קומפוננטה',
    'report.type': 'סוג',
    'report.variants': 'וריאנטים',
    'report.categoryScores': 'ציונים לפי קטגוריה',
    'report.actionItems': 'פעולות נדרשות',
    'report.suggestedMetadata': 'מטאדאטה מוצע',
    'report.copyToFigma': 'העתק והדבק בתיאור הקומפוננטה בפיגמה',

    // Notifications
    'notify.auditComplete': 'ביקורת הושלמה',
    'notify.analysisComplete': 'ניתוח הושלם',
    'notify.metadataGenerated': 'מטאדאטה נוצר',
    'notify.reportReady': 'הדוח מוכן',
    'notify.exportSuccess': 'יוצא בהצלחה!',
    'notify.copied': 'הועתק ללוח',
    'notify.error': 'שגיאה',
    'notify.connecting': 'מתחבר ל-Claude...',
    'notify.connected': 'מחובר לשרת MCP',
    'notify.disconnected': 'מנותק משרת MCP',
  }
};

/**
 * Get localized message with template variable replacement
 */
export function t(locale: Locale, key: string, vars?: Record<string, string | number>): string {
  let message = messages[locale][key] || messages['en'][key] || key;

  if (vars) {
    for (const [varKey, value] of Object.entries(vars)) {
      message = message.replace(`{{${varKey}}}`, String(value));
    }
  }

  return message;
}

/**
 * Get all messages for a locale (for client-side use)
 */
export function getMessages(locale: Locale): Record<string, string> {
  return messages[locale] || messages['en'];
}

/**
 * Detect locale from browser or system settings
 */
export function detectLocale(acceptLanguage?: string): Locale {
  if (acceptLanguage) {
    if (acceptLanguage.includes('he')) return 'he';
  }
  return 'en';
}
