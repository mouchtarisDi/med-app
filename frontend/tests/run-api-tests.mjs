import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const frontend = fileURLToPath(new URL('../', import.meta.url));
const output = mkdtempSync(join(tmpdir(), 'med-app-api-tests-'));

function run(args, options = {}) {
  const result = spawnSync(process.execPath, args, {
    cwd: frontend,
    stdio: 'inherit',
    ...options,
  });
  if (result.error) throw result.error;
  return result.status ?? 1;
}

try {
  writeFileSync(join(output, 'package.json'), JSON.stringify({ type: 'module' }));
  const compiled = run([
    'node_modules/typescript/bin/tsc',
    '--project', 'tsconfig.api-tests.json',
    '--outDir', output,
  ]);
  process.exitCode = compiled || run(['--test', 'tests/api.test.mjs'], {
    env: { ...process.env, API_TEST_BUILD_URL: pathToFileURL(`${output}/`).href },
  });
} finally {
  rmSync(output, { recursive: true, force: true });
}
