// News-image entry: draws entry.png with the pure-stdlib Python generator
// (gen.py) when python3 can run it, otherwise copies the committed
// entry.png the generator produced. Either way the same bytes land in
// /output/entry.png: the generator is deterministic.
//
// Outside the grader, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const target = join(outDir, 'entry.png');
const committed = join(root, 'entry.png');
const generator = join(root, 'gen.py');

const ran = spawnSync('python3', [generator], { stdio: 'inherit' });
if (ran.status === 0 && existsSync(committed)) {
  copyFileSync(committed, target);
} else if (existsSync(committed)) {
  // The generator could not run here (no python3, or a read-only
  // repository): the committed image is the generator's own output,
  // byte for byte, so copy it instead.
  copyFileSync(committed, target);
} else {
  throw new Error('entry.png missing and gen.py failed to run');
}
