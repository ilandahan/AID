# Figma Plugin Bug Fix Plan - Round 2

## Overview

This plan addresses 3 issues reported after the previous fixes:

1. **Report & Export tabs not cleared** when switching components
2. **Metadata apply validation mismatch** - 1-character difference, need manual copy fallback message
3. **Variant/property descriptions never generated** - Missing from metadata generation

---

## Issue 1: Report & Export Tabs Not Cleared on Component Switch

### Root Cause
The `clearAnalysisData()` function (lines 1385-1465) clears Audit, Metadata, and Review tabs but **does NOT clear**:

**Report Tab - Dev Handoff Section:**
- `devHandoffEmpty` - Should be shown
- `devHandoffContent` - Should be hidden
- `devHandoffButtons` - Should be hidden
- Dev Handoff level badge and content

**Export Tab:**
- `blockedState` - Should be shown initially
- `readyState` - Should be hidden initially
- `exportComponentName` - Should be reset
- `levelIcon`, `levelText`, `levelBadge` - Should be reset
- `exportDestination` - Should be reset
- `exportAIDBtn` - Should be disabled
- `blockersList` - Should be emptied
- `exportFilesList` - If exists, should be cleared

### Files to Modify
- `ui.html` - `clearAnalysisData()` function (lines 1385-1465)

### Fix Steps

1. **Add Report Tab - Dev Handoff clearing:**

   After the existing "REPORT TAB" section (around line 1436), add:
   ```javascript
   // ═══════════════════════════════════════════════════════════════
   // REPORT TAB - DEV HANDOFF
   // ═══════════════════════════════════════════════════════════════
   if ($('devHandoffEmpty')) $('devHandoffEmpty').style.display = 'block';
   if ($('devHandoffContent')) $('devHandoffContent').style.display = 'none';
   if ($('devHandoffButtons')) $('devHandoffButtons').style.display = 'none';
   if ($('devLevelBadge')) {
     $('devLevelBadge').textContent = '';
     $('devLevelBadge').style.background = '';
     $('devLevelBadge').style.color = '';
   }
   ```

2. **Expand Export Tab clearing (replace existing lines 1453-1462):**

   ```javascript
   // ═══════════════════════════════════════════════════════════════
   // EXPORT TAB
   // ═══════════════════════════════════════════════════════════════
   if ($('exportScore')) $('exportScore').textContent = '--';
   const exportStatus = $('exportScoreStatus');
   if (exportStatus) {
     exportStatus.textContent = '';
     exportStatus.style.background = '';
     exportStatus.style.color = '';
   }
   // Reset export component details
   if ($('exportComponentName')) $('exportComponentName').textContent = 'Component Name';
   if ($('levelIcon')) $('levelIcon').textContent = '🔵';
   if ($('levelText')) $('levelText').textContent = 'Atom';
   if ($('levelBadge')) {
     $('levelBadge').style.background = '#dbeafe';
     $('levelBadge').style.color = '#1e40af';
   }
   if ($('exportDestination')) $('exportDestination').textContent = 'src/design-system/atoms/';
   // Reset export states
   if ($('blockedState')) $('blockedState').style.display = 'block';
   if ($('readyState')) $('readyState').style.display = 'none';
   if ($('exportAIDBtn')) {
     $('exportAIDBtn').disabled = true;
     $('exportAIDBtn').classList.add('disabled');
   }
   if ($('blockersList')) $('blockersList').innerHTML = '';
   if ($('exportFilesList')) $('exportFilesList').innerHTML = '';
   ```

### Validation
- Select a component and run pipeline
- Export tab should show data
- Switch to a different component (approve in modal)
- Report tab Dev Handoff should show "Select a component" state
- Export tab should reset to initial empty state

---

## Issue 2: Metadata Apply Validation Mismatch

### Root Cause
Figma may modify the description when applying (e.g., trimming trailing whitespace/newlines). The current code (code.ts lines 502-521) detects this and shows a warning in console, but still sends `METADATA_APPLIED` with no indication to the user.

**Observed behavior:**
- Applied length: 276
- Expected length: 277
- 1 character difference (likely trailing newline or space)

### Files to Modify
- `code.ts` - Lines 502-521 (validation section)
- `ui.html` - `METADATA_APPLIED` handler (line 2858)

### Fix Steps

1. **Modify code.ts to send warning flag in METADATA_APPLIED message:**

   **Current (line 514):**
   ```typescript
   sendToUI({ type: 'METADATA_APPLIED' });
   ```

   **Change to:**
   ```typescript
   sendToUI({ type: 'METADATA_APPLIED', validationPassed: true });
   ```

   **And for mismatch case (line 519):**
   ```typescript
   sendToUI({ type: 'METADATA_APPLIED', validationPassed: false,
     message: 'Minor formatting difference detected. If issues persist, try copying the metadata manually.' });
   ```

2. **Update ui.html to handle validation warning:**

   **Replace METADATA_APPLIED handler (lines 2858-2866):**
   ```javascript
   case 'METADATA_APPLIED':
     console.log('═══════════════════════════════════════════════════════════════════');
     console.log('[UI] ✅ METADATA APPLIED TO FIGMA');
     console.log('═══════════════════════════════════════════════════════════════════');
     console.log('[UI] Component:', state.node?.name || 'Unknown');
     console.log('[UI] Fields applied:', countGeneratedFields(state.generated));
     console.log('[UI] Validation passed:', msg.validationPassed);
     console.log('───────────────────────────────────────────────────────────────────');

     if (msg.validationPassed === false) {
       // Show warning with manual copy suggestion
       showToast('⚠️ Applied with minor differences. You can copy/paste manually if needed.');
     } else {
       showToast(t('status.metadataApplied'));
     }
     break;
   ```

### Validation
- Generate metadata and apply to Figma
- If validation mismatch occurs, user should see:
  - Toast: "⚠️ Applied with minor differences. You can copy/paste manually if needed."
- Console should show validation status

---

## Issue 3: Variant & Property Descriptions Never Generated

### Root Cause
The `claudeClient.js` `parseMetadataResponse()` function (lines 98-124) does NOT extract:
- `variants` - Record of variant name to description
- `variantDescriptions` - Required by GeneratedMetadata type

The prompt (line 88) asks Claude to generate variants, but the parsing doesn't capture them.

### Files to Modify
- `server/src/utils/claudeClient.js` - `parseMetadataResponse()` function

### Fix Steps

1. **Add variant parsing to `parseMetadataResponse()` (after line 124):**

   ```javascript
   // Extract variants as key-value pairs
   metadata.variants = extractVariants(metadataSection);
   metadata.variantDescriptions = metadata.variants; // Alias for compatibility
   ```

2. **Add `extractVariants()` helper function (after line 153):**

   ```javascript
   /**
    * Extract variant descriptions as key-value pairs
    * Format: "variants:\n  VariantName: Description"
    */
   function extractVariants(text) {
     const variants = {};
     const variantSectionRegex = /variants:[\s\S]*?(?=\n\w+:|$)/i;
     const match = text.match(variantSectionRegex);

     if (match) {
       const variantText = match[0];
       // Match "  Name: Description" pattern
       const variantItemRegex = /^\s+([A-Za-z][A-Za-z0-9_-]*):\s*(.+)$/gm;
       let itemMatch;
       while ((itemMatch = variantItemRegex.exec(variantText)) !== null) {
         const name = itemMatch[1].trim();
         const description = itemMatch[2].trim();
         variants[name] = description;
       }
     }

     return variants;
   }
   ```

3. **Improve the prompt to request explicit variant format (line 88-89):**

   **Change:**
   ```javascript
   9. variants (if any)
   ```

   **To:**
   ```javascript
   9. variants - For EACH variant, provide format:
      VariantName: One-sentence description of what this variant is for
   ```

### Validation
- Select a component with multiple variants
- Run pipeline to generate metadata
- Check that `state.generated.variants` or `state.generated.variantDescriptions` is populated
- Check that formattedDescription includes variant section

---

## Implementation Order

1. **Issue 1 (Tab Clearing)** - Quick UI fix, immediately visible
2. **Issue 2 (Validation Warning)** - Plugin code + UI handler
3. **Issue 3 (Variant Descriptions)** - Server-side parsing fix

---

## Testing Checklist

After all fixes:

- [ ] Switch components - Report tab Dev Handoff resets
- [ ] Switch components - Export tab resets
- [ ] Apply metadata - Shows warning if validation mismatch
- [ ] Apply metadata - Suggests manual copy on mismatch
- [ ] Generate metadata - Variants populated in response
- [ ] Console shows no JavaScript errors

---

## Files Modified Summary

| File | Changes |
|------|---------|
| `ui.html` | Lines 1437-1465 (clearAnalysisData expansion), Lines 2858-2866 (METADATA_APPLIED handler) |
| `code.ts` | Lines 514 and 519 (add validationPassed flag to message) |
| `server/src/utils/claudeClient.js` | Lines 118-124 (add variants parsing), Lines 154+ (add extractVariants function), Line 88 (improve prompt) |

