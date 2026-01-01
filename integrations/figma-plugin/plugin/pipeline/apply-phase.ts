/**
 * @file plugin/pipeline/apply-phase.ts
 * @description Apply metadata to Figma components
 */

import { logger } from '../../Logger';
import { currentState } from '../state';
import { sendToUI, sendError } from '../ui-messaging';

// ============================================
// Prepare Description for Figma (sanitization)
// ============================================

/**
 * Prepare and sanitize the description for Figma.
 * - Strips markdown code block wrappers (```yaml, ```text, etc.)
 * - Trims leading/trailing whitespace
 * - Normalizes line endings (CRLF → LF)
 * - Removes trailing whitespace from each line
 * - Ensures no trailing newlines (Figma trims these anyway)
 *
 * @param description The raw description text
 * @returns The sanitized, Figma-ready description
 */
export function prepareFigmaDescription(description: string): string {
  if (!description) return '';

  let cleaned = description;

  // Strip markdown code block wrappers (```yaml, ```text, ```, etc.)
  // This handles cases where Claude wraps the output in code blocks
  const codeBlockPattern = /^```(?:yaml|text|markdown|md|json)?\s*\n?([\s\S]*?)\n?```$/;
  const match = cleaned.match(codeBlockPattern);
  if (match) {
    cleaned = match[1];
    logger.debug('[PLUGIN] 🧹 Stripped markdown code block wrapper from description');
  }

  return (
    cleaned
      // Normalize line endings to LF
      .replace(/\r\n/g, '\n')
      .replace(/\r/g, '\n')
      // Remove trailing whitespace from each line
      .split('\n')
      .map((line) => line.trimEnd())
      .join('\n')
      // Trim BOTH leading and trailing whitespace (Figma does this too)
      .trim()
  );
}

// ============================================
// Apply Metadata to Figma (after user approval)
// ============================================

/**
 * Apply generated metadata to the Figma component
 */
export async function applyMetadataToFigma(): Promise<void> {
  logger.debug('═══════════════════════════════════════════════════════════════════');
  logger.debug('[PLUGIN] 📝 APPLY METADATA TO FIGMA STARTED');
  logger.debug('═══════════════════════════════════════════════════════════════════');

  if (!currentState.selectedNode) {
    logger.debug('[PLUGIN] ❌ ERROR: No component selected');
    sendToUI({ type: 'METADATA_APPLY_FAILED', error: 'No component selected' });
    return;
  }

  logger.debug('[PLUGIN] 📦 Target Component:', currentState.selectedNode.name);
  logger.debug('[PLUGIN] 📦 Type:', currentState.selectedNode.type);
  logger.debug('[PLUGIN] 📦 Node ID:', currentState.selectedNode.id);

  if (!currentState.generated) {
    logger.debug('[PLUGIN] ❌ ERROR: No metadata generated yet');
    logger.debug('[PLUGIN] currentState.generated is:', currentState.generated);
    sendToUI({
      type: 'METADATA_APPLY_FAILED',
      error: 'No metadata generated yet. Please run the pipeline first.',
    });
    return;
  }

  try {
    let node = currentState.selectedNode;

    // Handle INSTANCE type - get the main component instead
    if (node.type === 'INSTANCE') {
      const instanceNode = node as InstanceNode;
      const mainComponent = instanceNode.mainComponent;

      if (!mainComponent) {
        logger.debug('[PLUGIN] ❌ ERROR: Instance has no main component');
        sendToUI({
          type: 'METADATA_APPLY_FAILED',
          error:
            'Cannot find the main component for this instance. Please select the main component directly.',
        });
        return;
      }

      logger.debug('[PLUGIN] 🔄 Instance detected - switching to main component');
      logger.debug('[PLUGIN] 📦 Main Component:', mainComponent.name);
      logger.debug('[PLUGIN] 📦 Main Component ID:', mainComponent.id);
      node = mainComponent;
      figma.notify('ℹ️ Applying to main component (instances are read-only)');
    }

    // Get the formatted description from generated metadata
    const formattedDescription =
      currentState.generated.formattedDescription ||
      currentState.generated.formattedForFigma ||
      currentState.generated.description;

    logger.debug('[PLUGIN] 📄 Content to apply:');
    logger.debug('    - Length:', formattedDescription?.length || 0, 'chars');
    logger.debug('    - Preview:', formattedDescription?.substring(0, 100) + '...');

    if (!formattedDescription) {
      logger.debug('[PLUGIN] ❌ ERROR: No description to apply');
      logger.debug(
        '[PLUGIN] Available fields in generated:',
        Object.keys(currentState.generated || {})
      );
      sendToUI({
        type: 'METADATA_APPLY_FAILED',
        error: 'No description found in generated metadata. Check console for details.',
      });
      return;
    }

    // Check if node supports description property
    if ('description' in node) {
      applyDescriptionToNode(node as ComponentNode | ComponentSetNode, formattedDescription);
    } else {
      logger.debug('[PLUGIN] ❌ ERROR: Node type does not support descriptions');
      logger.debug('[PLUGIN] Node type:', node.type);
      sendToUI({
        type: 'METADATA_APPLY_FAILED',
        error: 'This node type does not support descriptions',
      });
    }
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : 'Unknown error';
    logger.debug('[PLUGIN] ❌ EXCEPTION:', errorMsg);
    logger.debug('═══════════════════════════════════════════════════════════════════');
    sendToUI({ type: 'METADATA_APPLY_FAILED', error: errorMsg });
    sendError(`Failed to apply metadata: ${errorMsg}`);
  }
}

/**
 * Apply description to a component node with validation
 */
function applyDescriptionToNode(
  targetNode: ComponentNode | ComponentSetNode,
  formattedDescription: string
): void {
  // STEP 1: Clear existing data
  logger.debug('───────────────────────────────────────────────────────────────────');
  logger.debug('[PLUGIN] 📋 STEP 1: Clearing existing description...');
  const existingDesc = targetNode.description;
  logger.debug('[PLUGIN]    Existing length:', existingDesc?.length || 0);

  targetNode.description = '';

  // STEP 2: Validate field is empty
  logger.debug('[PLUGIN] 📋 STEP 2: Validating field is empty...');
  const clearedDesc = targetNode.description;
  if (clearedDesc !== '') {
    logger.debug(
      '[PLUGIN] ⚠️ WARNING: Field not empty after clear:',
      clearedDesc.length,
      'chars remain'
    );
  } else {
    logger.debug('[PLUGIN]    ✓ Field is empty');
  }

  // STEP 3: Prepare and sanitize the new data
  logger.debug('[PLUGIN] 📋 STEP 3: Preparing Figma-ready description...');
  const preparedDescription = prepareFigmaDescription(formattedDescription);
  logger.debug('[PLUGIN]    Original length:', formattedDescription.length);
  logger.debug('[PLUGIN]    Prepared length:', preparedDescription.length);
  logger.debug(
    '[PLUGIN]    Chars trimmed:',
    formattedDescription.length - preparedDescription.length
  );

  // STEP 4: Apply the prepared description
  logger.debug('[PLUGIN] 📋 STEP 4: Applying prepared description to Figma...');
  targetNode.description = preparedDescription;

  // VALIDATION: Read back to verify
  logger.debug('───────────────────────────────────────────────────────────────────');
  logger.debug('[PLUGIN] 🔍 VALIDATION: Reading back from Figma...');
  const appliedDesc = targetNode.description;
  const isValid = appliedDesc === preparedDescription;
  logger.debug('[PLUGIN] 🔍 Applied length:', appliedDesc?.length || 0);
  logger.debug('[PLUGIN] 🔍 Expected length:', preparedDescription.length);
  logger.debug('[PLUGIN] 🔍 Match:', isValid ? '✅ EXACT MATCH' : '❌ MISMATCH');

  if (isValid) {
    logger.debug('[PLUGIN] ✅ SUCCESS: Metadata applied and verified!');
    logger.debug('═══════════════════════════════════════════════════════════════════');
    sendToUI({ type: 'METADATA_APPLIED', validationPassed: true });
    figma.notify('✅ Metadata applied to Figma component!');
  } else {
    // Log the difference for debugging
    logger.debug('[PLUGIN] ⚠️ Char diff:', appliedDesc?.length - preparedDescription.length);
    logger.debug('[PLUGIN] ⚠️ Applied ends with:', JSON.stringify(appliedDesc?.slice(-20)));
    logger.debug(
      '[PLUGIN] ⚠️ Expected ends with:',
      JSON.stringify(preparedDescription.slice(-20))
    );
    logger.debug('═══════════════════════════════════════════════════════════════════');
    sendToUI({
      type: 'METADATA_APPLIED',
      validationPassed: false,
      appliedLength: appliedDesc?.length || 0,
      expectedLength: preparedDescription.length,
    });
    figma.notify('⚠️ Minor formatting difference - metadata saved');
  }
}
