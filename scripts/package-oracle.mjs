import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { cpSync, mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
execFileSync(process.execPath, [join(root, 'node_modules/vite/bin/vite.js'), 'build'], {
  cwd: root, stdio: 'inherit',
});

// Publish only assets used by the current house; retain earlier experiments locally.
const release = `shanks-studio-${new Date().toISOString().replace(/[:.]/g, '-')}`;
const output = join(root, 'tmp/oracle');
const staging = join(output, release);
mkdirSync(staging, { recursive: true });
for (const asset of ['index.html', 'assets', 'credits.html', 'models/cyber-home.glb', 'draco', 'projects']) {
  const target = join(staging, asset);
  mkdirSync(dirname(target), { recursive: true });
  cpSync(join(root, 'dist', asset), target, { recursive: true });
}
const files = [];
function inventory(directory) {
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) inventory(path);
    else files.push({ path: relative(staging, path).replaceAll('\\', '/'), bytes: statSync(path).size,
      sha256: createHash('sha256').update(readFileSync(path)).digest('hex') });
  }
}
inventory(staging);
const archive = join(output, `${release}.tar.gz`);
execFileSync('tar', ['-czf', archive, '-C', staging, '.'], { stdio: 'inherit' });
const manifest = { release, archive, archiveSha256: createHash('sha256').update(readFileSync(archive)).digest('hex'),
  totalBytes: files.reduce((sum, file) => sum + file.bytes, 0), files };
writeFileSync(join(output, `${release}.json`), JSON.stringify(manifest, null, 2) + '\n');
console.log(JSON.stringify({ release, archive, archiveSha256: manifest.archiveSha256,
  archiveBytes: statSync(archive).size, files: files.length, totalBytes: manifest.totalBytes }, null, 2));
