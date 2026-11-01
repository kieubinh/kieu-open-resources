// Render QA stills: one frame near the end of every narration beat of the chosen scenes (bundle once).
// usage: node scripts/qa_frames.mjs [--scale 0.5] [--out output/qa] [sceneIdPrefix ...]
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
let scale = 0.5, out = path.join(root, 'output/qa');
const prefixes = [];
for (let k = 0; k < args.length; k++) {
  if (args[k] === '--scale') scale = Number(args[++k]);
  else if (args[k] === '--out') out = path.resolve(args[++k]);
  else prefixes.push(args[k]);
}
fs.mkdirSync(out, {recursive: true});
const timeline = JSON.parse(fs.readFileSync(path.join(root, 'src/timeline.json'), 'utf8'));
const serveUrl = await bundle({entryPoint: path.join(root, 'src/index.ts'), publicDir: path.join(root, 'public')});
const composition = await selectComposition({serveUrl, id: 'EP03-WildcardMatching'});
let n = 0;
for (const scene of timeline.scenes) {
  if (prefixes.length && !prefixes.some((p) => scene.id.startsWith(p))) continue;
  const frames = scene.beats.length
    ? scene.beats.map((b, k) => [`b${k}`, Math.min(scene.frames - 1, b.startFrame + Math.max(10, Math.round((b.audioEndFrame - b.startFrame) * 0.85)))])
    : [['mid', Math.round(scene.frames / 2)]];
  for (const [tag, f] of frames) {
    const file = path.join(out, `${scene.id}_${tag}.png`);
    await renderStill({composition, serveUrl, output: file, frame: scene.fromFrame + f, scale});
    n++;
  }
}
console.log(`rendered ${n} stills -> ${out}`);
