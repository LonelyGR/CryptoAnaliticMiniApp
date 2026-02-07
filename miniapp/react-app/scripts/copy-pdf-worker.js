/* eslint-disable no-console */
const fs = require('fs');
const path = require('path');

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function main() {
  const projectRoot = path.resolve(__dirname, '..');
  const src = path.join(projectRoot, 'node_modules', 'pdfjs-dist', 'build', 'pdf.worker.min.mjs');
  const destDir = path.join(projectRoot, 'public');
  const dest = path.join(destDir, 'pdf.worker.min.mjs');

  try {
    if (!fs.existsSync(src)) {
      console.warn('[copy-pdf-worker] Source worker not found:', src);
      process.exit(0);
    }
    ensureDir(destDir);
    fs.copyFileSync(src, dest);
    console.log('[copy-pdf-worker] Copied:', src, '->', dest);
  } catch (e) {
    console.error('[copy-pdf-worker] Failed:', e);
    process.exit(1);
  }
}

main();

