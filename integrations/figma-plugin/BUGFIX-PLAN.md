# Figma Plugin Bug Fix Plan

## Overview

This plan addresses 4 issues found in the Figma plugin UI after metadata generation:

1. **Apply to Figma button not working** - says "no info to apply"
2. **Copy buttons broken** - TypeError: Cannot read properties of undefined (reading 'writeText')
3. **Score threshold mismatch** - shows score 87 but says "score 73 is below 90"
4. **Export tab UX** - should show all data even when button is disabled

---

## Issue 1: Apply to Figma Button Not Working

### Root Cause
The Apply button checks `$('generatedMeta').textContent` (line 2658-2660), but the metadata DOM element is only updated if `gen?.formattedDescription || gen?.formattedForFigma` exists (lines 2273-2278). If the generated metadata lacks these specific fields, the button sees empty/default text.

### Files to Modify
- `ui.html` - lines 2655-2686

### Fix Steps

1. **Modify the Apply button handler to check `state.generated` instead of DOM element:**

   **Before (line 2656-2668):**
   ```javascript
   $('applyMetaBtn').onclick = () => {
     const generatedMetaEl = $('generatedMeta');
     const metaContent = generatedMetaEl ? generatedMetaEl.textContent : null;
     if (metaContent && metaContent !== '// Run generate to get metadata') {
       // Opens modal
     } else {
       console.log('[UI] No metadata to apply');
     }
   };
   ```

   **After:**
   ```javascript
   $('applyMetaBtn').onclick = () => {
     // Check state.generated directly (more reliable than DOM textContent)
     if (state.generated && (state.generated.formattedDescription || state.generated.description)) {
       console.log('[UI] Opening approval modal with state.generated');
       const modalPreview = $('modalMetaPreview');
       const modal = $('metadataApprovalModal');
       const content = state.generated.formattedDescription || state.generated.formattedForFigma || JSON.stringify(state.generated, null, 2);
       if (modalPreview) modalPreview.textContent = content;
       if (modal) modal.style.display = 'flex';
     } else {
       console.log('[UI] No metadata to apply - state.generated:', state.generated);
       showToast('No generated metadata to apply. Run the pipeline first.');
     }
   };
   ```

2. **Apply the same fix to `applyMetaBtnMeta` (lines 2672-2686)**

### Validation
- Run pipeline on a component
- Click "Apply to Figma" button
- Modal should open with metadata preview
- Console should show `[UI] Opening approval modal with state.generated`

---

## Issue 2: Copy Buttons Broken (Clipboard Error)

### Root Cause
`navigator.clipboard` may be `undefined` in Figma's iframe environment. The code at lines 2636-2650 calls `navigator.clipboard.writeText()` without checking if the clipboard API exists.

### Files to Modify
- `ui.html` - lines 2636-2650 (and similar patterns throughout)

### Fix Steps

1. **Create a safe clipboard helper function (add near line 1340):**

   ```javascript
   function copyToClipboard(text) {
     if (navigator.clipboard && navigator.clipboard.writeText) {
       navigator.clipboard.writeText(text).then(() => {
         showToast('Copied to clipboard');
       }).catch(err => {
         console.error('[UI] Clipboard write failed:', err);
         fallbackCopyToClipboard(text);
       });
     } else {
       fallbackCopyToClipboard(text);
     }
   }

   function fallbackCopyToClipboard(text) {
     // Fallback using textarea + execCommand
     const textarea = document.createElement('textarea');
     textarea.value = text;
     textarea.style.position = 'fixed';
     textarea.style.left = '-9999px';
     document.body.appendChild(textarea);
     textarea.select();
     try {
       document.execCommand('copy');
       showToast('Copied to clipboard');
     } catch (err) {
       console.error('[UI] Fallback copy failed:', err);
       showToast('Copy failed - please copy manually');
     }
     document.body.removeChild(textarea);
   }
   ```

2. **Update all clipboard calls to use the helper:**

   **Line 2639 (copyDevHandoffBtn):**
   ```javascript
   // Before:
   navigator.clipboard.writeText(markdown);

   // After:
   copyToClipboard(markdown);
   ```

   **Search and replace all other instances:**
   - `copyDevTsBtn` (line ~2644)
   - Any other copy buttons

### Validation
- Open Report tab
- Click "Copy Markdown" button
- Should show "Copied to clipboard" toast (not error)
- Verify content is actually copied

---

## Issue 3: Score Threshold Mismatch

### Root Cause
Three different score thresholds exist:
- `ui.html` line 2375: `const MIN_EXPORT_SCORE = 70;`
- `ui.html` line 2524: `overallScore >= 90` (hardcoded, inconsistent!)
- `MCPClient.ts` line 352: `payload.qualityCertification.score < 90`

The UI shows score 87 (above 70) but the export logic uses 90, causing "score 73 is below 90" message.

### Files to Modify
- `ui.html` - lines 2375 and 2524
- Optionally: `MCPClient.ts` - line 352 (or document why it's 90)

### Fix Steps

1. **Unify to single threshold constant in ui.html:**

   **Line 2375 - Change:**
   ```javascript
   // Before:
   const MIN_EXPORT_SCORE = 70;

   // After:
   const MIN_EXPORT_SCORE = 90; // Must match MCPClient.ts threshold
   ```

2. **Fix line 2524 to use the constant:**

   **Before:**
   ```javascript
   const exportReady = results.exportReady || overallScore >= 90;
   ```

   **After:**
   ```javascript
   const exportReady = results.exportReady || overallScore >= MIN_EXPORT_SCORE;
   ```

3. **Verify MCPClient.ts line 352 uses same threshold:**
   - Currently hardcoded to 90
   - Consider extracting to shared constant or config
   - For now, document that both must stay in sync

### Validation
- Run pipeline on component with score 85
- Export button should be disabled
- Message should say "score 85 is below 90"
- Run pipeline on component with score 91
- Export button should be enabled

---

## Issue 4: Export Tab - Show All Data Even When Disabled

### Root Cause
When export is blocked (score < 90), the UI hides export data. User wants to see what WILL be exported even if they can't export yet.

### Files to Modify
- `ui.html` - `updateExport()` function (around line 2375-2500)

### Fix Steps

1. **Locate the blocked/ready state UI logic in updateExport():**

   Find where `blockedStateEl` is shown and `readyStateEl` is hidden.

2. **Always render the export preview data:**

   **Modify to show export data in BOTH states:**
   ```javascript
   // Always render the export preview (regardless of button state)
   const previewEl = $('exportPreview');
   if (previewEl) {
     previewEl.innerHTML = renderExportPreview(exportData);
     previewEl.style.display = 'block';
   }

   // Update button state (disabled or enabled)
   const exportBtn = $('exportAIDBtn');
   if (exportBtn) {
     exportBtn.disabled = !exportReady;
     exportBtn.classList.toggle('disabled', !exportReady);
   }

   // Show appropriate status message
   if (!exportReady) {
     $('exportStatus').textContent = `Score ${overallScore} is below ${MIN_EXPORT_SCORE}. Fix issues to enable export.`;
     $('exportStatus').className = 'export-status blocked';
   } else {
     $('exportStatus').textContent = 'Ready to export!';
     $('exportStatus').className = 'export-status ready';
   }
   ```

3. **Ensure blocked state doesn't hide the data sections**

### Validation
- Run pipeline on component with score 75
- Export tab should show:
  - Score 75 (with warning styling)
  - Message: "Score 75 is below 90. Fix issues to enable export."
  - DISABLED export button
  - BUT all export data visible (component info, metadata, tokens, etc.)
- Fix issues to get score 92
- Button should become enabled, all data still visible

---

## Implementation Order

1. **Issue 2 (Clipboard)** - Quick fix, unblocks testing
2. **Issue 1 (Apply Button)** - Core functionality fix
3. **Issue 3 (Score Threshold)** - Logic consistency
4. **Issue 4 (Export UX)** - UX enhancement

---

## Testing Checklist

After all fixes:

- [ ] Clipboard copy works in Report tab
- [ ] Apply button works after metadata generation
- [ ] Score threshold is consistent (90 everywhere)
- [ ] Export tab shows all data even when score < 90
- [ ] Console has no JavaScript errors
- [ ] Plugin rebuilds without TypeScript errors

---

## Files Modified Summary

| File | Changes |
|------|---------|
| `ui.html` | Lines 1340 (add clipboard helper), 2375 (threshold), 2524 (use constant), 2636-2650 (clipboard), 2655-2686 (apply button), 2400-2500 (export UX) |
| `MCPClient.ts` | Document threshold at line 352 |

