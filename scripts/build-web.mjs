import { cp, mkdir, rm } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const projectRoot = join(dirname(fileURLToPath(import.meta.url)), '..');
const outputRoot = join(projectRoot, 'dist');

const files = [
    'index.html',
    'styles.css',
    'manifest.webmanifest',
    'sw.js',
    'apple-touch-icon.png',
    'assets'
];

await rm(outputRoot, { recursive: true, force: true });
await mkdir(outputRoot, { recursive: true });

for (const file of files) {
    await cp(join(projectRoot, file), join(outputRoot, file), { recursive: true });
}

console.log(`Built PokerGuys web assets in ${outputRoot}`);
