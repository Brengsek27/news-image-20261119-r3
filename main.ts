import { copyFile, mkdir, readFile } from 'node:fs/promises';
import { join } from 'node:path';

const imageUrl = new URL('./entry.png', import.meta.url);
const image = await readFile(imageUrl);

if (image.length > 1048576) {
  throw new Error(`entry.png exceeds the 1048576-byte limit (${image.length} bytes).`);
}
if (image.length < 33 || !image.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]))) {
  throw new Error('entry.png is not a valid PNG (signature missing).');
}
if (image.readUInt32BE(8) !== 13 || image.toString('ascii', 12, 16) !== 'IHDR') {
  throw new Error('entry.png is not a valid PNG (IHDR missing).');
}
if (image.readUInt32BE(16) !== 1024 || image.readUInt32BE(20) !== 1024) {
  throw new Error('entry.png must be exactly 1024×1024 pixels.');
}

const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const outputPath = join(outputDir, 'entry.png');
await mkdir(outputDir, { recursive: true });
await copyFile(imageUrl, outputPath);
console.log(`Copied ${image.length} bytes to ${outputPath}`);
