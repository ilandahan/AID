/**
 * @file services/ComponentAuditor/checks/index.ts
 * @description Barrel export for all check modules
 */

export { checkNaming, checkNameFormat, checkCommonTypos, checkLayerNames, checkVariantNaming } from './naming';
export { checkStructure, checkUnnecessaryWrappers, checkVariantStructureConsistency } from './structure';
export { checkVisual, checkFontSizeConsistency, checkBorderRadiusConsistency, checkColorUsage } from './visual';
export { checkAccessibility, checkFocusState, checkDisabledState, checkTouchTargetSize } from './accessibility';
export { checkVariants, checkExpectedStates, checkVariantCombinations, checkVariantDistinction } from './variants';
