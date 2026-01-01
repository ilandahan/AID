/**
 * @file zipExporter.js
 * @description Creates ZIP files for component exports with automatic cleanup.
 *              Stores ZIPs temporarily in /tmp and deletes after download.
 * @created 2024-12-30
 */

const archiver = require('archiver');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// Temporary storage for ZIP files (works on Cloud Run's /tmp)
const TEMP_DIR = process.env.TEMP_DIR || '/tmp/aid-exports';

// Map of download tokens to file info
const pendingDownloads = new Map();

// Auto-cleanup timeout (5 minutes)
const CLEANUP_TIMEOUT_MS = 5 * 60 * 1000;

/**
 * Initialize the temp directory
 */
function initTempDir() {
  try {
    if (!fs.existsSync(TEMP_DIR)) {
      fs.mkdirSync(TEMP_DIR, { recursive: true });
      console.log(`[ZipExporter] Created temp directory: ${TEMP_DIR}`);
    }
  } catch (error) {
    console.error('[ZipExporter] Failed to create temp directory:', error);
  }
}

// Initialize on module load
initTempDir();

/**
 * Create a ZIP file from file contents
 * @param {Object} fileContents - Map of filename to content
 * @param {string} componentName - Name of the component
 * @param {string} relativePath - Relative path for the component folder
 * @returns {Promise<{token: string, filename: string, size: number}>}
 */
async function createZip(fileContents, componentName, relativePath) {
  return new Promise((resolve, reject) => {
    // Generate unique token for this download
    const token = crypto.randomBytes(16).toString('hex');
    const zipFilename = `${componentName}-${token.substring(0, 8)}.zip`;
    const zipPath = path.join(TEMP_DIR, zipFilename);

    console.log(`[ZipExporter] Creating ZIP: ${zipFilename}`);
    console.log(`[ZipExporter] Files to include:`, Object.keys(fileContents));

    // Create write stream
    const output = fs.createWriteStream(zipPath);
    const archive = archiver('zip', {
      zlib: { level: 9 } // Maximum compression
    });

    // Handle completion
    output.on('close', () => {
      const size = archive.pointer();
      console.log(`[ZipExporter] ZIP created: ${zipFilename} (${size} bytes)`);

      // Store download info
      pendingDownloads.set(token, {
        path: zipPath,
        filename: `${componentName}.zip`,
        componentName,
        relativePath,
        size,
        createdAt: Date.now()
      });

      // Schedule auto-cleanup
      setTimeout(() => {
        cleanupDownload(token);
      }, CLEANUP_TIMEOUT_MS);

      resolve({
        token,
        filename: `${componentName}.zip`,
        size,
        files: Object.keys(fileContents)
      });
    });

    // Handle errors
    archive.on('error', (err) => {
      console.error('[ZipExporter] Archive error:', err);
      reject(err);
    });

    output.on('error', (err) => {
      console.error('[ZipExporter] Output stream error:', err);
      reject(err);
    });

    // Pipe archive to file
    archive.pipe(output);

    // Extract atomic level from relativePath (format: components/{level}/{componentName})
    // e.g., "components/atoms/Button" -> level = "atoms"
    const pathParts = (relativePath || '').split('/');
    const atomicLevel = pathParts[1] || 'molecules'; // Default to molecules if not found

    // Build folder structure: {level}/{componentName}/files
    // e.g., atoms/Button/Button.tsx
    const folderPath = `${atomicLevel}/${componentName}`;

    console.log(`[ZipExporter] Creating folder structure: ${folderPath}/`);

    for (const [filename, content] of Object.entries(fileContents)) {
      // Add file inside level/component folder
      archive.append(content, { name: `${folderPath}/${filename}` });
    }

    // Add a README with installation instructions
    const readme = `# ${componentName}

Exported from Figma AID Plugin

## Atomic Level: ${atomicLevel.toUpperCase()}

## Installation

1. Copy the \`${atomicLevel}\` folder to your project's components directory:
   \`\`\`
   src/components/${atomicLevel}/${componentName}/
   \`\`\`

   Or copy just the \`${componentName}\` folder if you already have the ${atomicLevel} directory:
   \`\`\`
   src/components/${atomicLevel}/ ← paste ${componentName}/ here
   \`\`\`

2. Import the component:
   \`\`\`tsx
   import { ${componentName} } from '@/components/${atomicLevel}/${componentName}';
   \`\`\`

## Files Included

${Object.keys(fileContents).map(f => `- ${f}`).join('\n')}

---
Generated: ${new Date().toISOString()}
`;

    archive.append(readme, { name: `${folderPath}/README.md` });

    // Finalize the archive
    archive.finalize();
  });
}

/**
 * Get download info by token
 * @param {string} token - Download token
 * @returns {Object|null} Download info or null if not found
 */
function getDownloadInfo(token) {
  return pendingDownloads.get(token) || null;
}

/**
 * Get the file stream for download
 * @param {string} token - Download token
 * @returns {{stream: ReadStream, info: Object}|null}
 */
function getDownloadStream(token) {
  const info = pendingDownloads.get(token);
  if (!info) {
    return null;
  }

  if (!fs.existsSync(info.path)) {
    console.error('[ZipExporter] ZIP file not found:', info.path);
    pendingDownloads.delete(token);
    return null;
  }

  return {
    stream: fs.createReadStream(info.path),
    info
  };
}

/**
 * Clean up a download after it's been downloaded or expired
 * @param {string} token - Download token
 */
function cleanupDownload(token) {
  const info = pendingDownloads.get(token);
  if (!info) {
    return;
  }

  console.log(`[ZipExporter] Cleaning up: ${info.filename}`);

  try {
    if (fs.existsSync(info.path)) {
      fs.unlinkSync(info.path);
      console.log(`[ZipExporter] Deleted: ${info.path}`);
    }
  } catch (error) {
    console.error('[ZipExporter] Cleanup error:', error);
  }

  pendingDownloads.delete(token);
}

/**
 * Mark download as completed (triggers cleanup)
 * @param {string} token - Download token
 */
function completeDownload(token) {
  // Small delay to ensure download stream is fully flushed
  setTimeout(() => {
    cleanupDownload(token);
  }, 1000);
}

/**
 * Get statistics about pending downloads
 * @returns {Object} Stats about pending downloads
 */
function getStats() {
  return {
    pending: pendingDownloads.size,
    tempDir: TEMP_DIR,
    cleanupTimeout: CLEANUP_TIMEOUT_MS / 1000
  };
}

module.exports = {
  createZip,
  getDownloadInfo,
  getDownloadStream,
  completeDownload,
  cleanupDownload,
  getStats
};
